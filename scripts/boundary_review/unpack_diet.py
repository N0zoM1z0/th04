#!/usr/bin/env python3
"""Deterministically unpack a pinned TH04 DIET target into private analysis output.

This is a target-observation tool, not a reconstruction shortcut.  It emulates the
compressed target's own real-mode decompressor at two load segments, records every
executed ``add es:[bx],bp`` relocation, stops before the transfer to the original
entry point, reverses those relocations, and requires both runs to agree byte for
byte.  No unpacked game bytes are written outside ignored ``.analysis/``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
import struct
import sys
import tomllib
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.pc98 import parse_mz
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact


ROOT = Path(__file__).resolve().parents[2]
TARGET_CONFIG = ROOT / "config" / "targets.toml"
REVIEW_CONFIG = ROOT / "config" / "th04_boundary_review.toml"
DIET_MARKER_OFFSET = 0x1C
RELOCATION_OPCODE = b"\x26\x01\x2f"  # add word ptr es:[bx],bp
DEFAULT_LOAD_SEGMENTS = (0x1000, 0x2000)
REQUIRED_UNICORN_VERSION = "1.0.2"


class DietError(ValueError):
    """A fail-closed DIET observation error."""


@dataclass(frozen=True)
class RelocationObservation:
    index: int
    es: int
    bx: int
    relative_segment: int
    relative_linear: int


@dataclass(frozen=True)
class EmulationResult:
    load_segment: int
    relocated_payload: bytes
    relocations: tuple[RelocationObservation, ...]
    final_cs: int
    final_ip: int
    final_ss: int
    final_sp: int
    instruction_count: int
    dos_version_calls: int


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to((ROOT / ".analysis").resolve())
    except ValueError as error:
        raise DietError("DIET output must stay below ignored .analysis") from error
    return resolved


def load_policy(artifact_id: str) -> dict[str, object]:
    parsed = tomllib.loads(REVIEW_CONFIG.read_text(encoding="utf-8"))
    if parsed.get("schema_version") != 1:
        raise DietError("unsupported th04_boundary_review.toml schema")
    matches = [
        row for row in parsed.get("diet_artifacts", [])
        if row.get("artifact") == artifact_id
    ]
    if len(matches) != 1:
        raise DietError(f"expected one DIET policy for {artifact_id}, got {len(matches)}")
    return matches[0]


def normalize_payload(
    relocated: bytes,
    relocations: tuple[RelocationObservation, ...],
    load_segment: int,
) -> bytes:
    """Reverse the target stub's observed MZ relocation additions."""
    result = bytearray(relocated)
    for relocation in relocations:
        offset = relocation.relative_linear
        if offset < 0 or offset + 2 > len(result):
            raise DietError(
                f"relocation {relocation.index} escapes payload: 0x{offset:x}"
            )
        value = struct.unpack_from("<H", result, offset)[0]
        struct.pack_into("<H", result, offset, (value - load_segment) & 0xFFFF)
    return bytes(result)


def _unicorn_imports() -> tuple[object, object]:
    try:
        import unicorn
        import unicorn.x86_const
    except ImportError as error:
        raise DietError(
            "Unicorn is required; install the pinned host dependency documented in "
            "docs/RE_WORKFLOW.md"
        ) from error
    if getattr(unicorn, "__version__", None) != REQUIRED_UNICORN_VERSION:
        raise DietError(
            f"Unicorn {REQUIRED_UNICORN_VERSION} is required; got "
            f"{getattr(unicorn, '__version__', 'unknown')}"
        )
    return unicorn, unicorn.x86_const


def emulate_once(
    target: bytes,
    *,
    payload_size: int,
    original_format: str,
    expected_entry_cs: int | None,
    expected_entry_ip: int,
    load_segment: int,
    max_instructions: int,
    code_hook: Callable[[int, bytes], None] | None = None,
) -> EmulationResult:
    unicorn, x86 = _unicorn_imports()
    image = parse_mz(target)
    if target[DIET_MARKER_OFFSET:DIET_MARKER_OFFSET + 4].lower() != b"diet":
        raise DietError("target lacks the expected DIET marker at file offset 0x1c")
    if not 0x100 <= load_segment <= 0x7000:
        raise DietError("load segment must be in the safe range 0x0100..0x7000")
    if payload_size <= 0:
        raise DietError("payload size must be positive")

    psp_segment = load_segment - 0x10
    load_physical = load_segment << 4
    memory_size = 0x200000
    uc = unicorn.Uc(unicorn.UC_ARCH_X86, unicorn.UC_MODE_16)
    uc.mem_map(0, memory_size)
    uc.mem_write(load_physical, image.program_image)
    # Minimal deterministic PSP state used by the stub/DOS allocation convention.
    uc.mem_write(psp_segment << 4, b"\xcd\x20")
    uc.mem_write((psp_segment << 4) + 2, struct.pack("<H", 0x9000))

    uc.reg_write(
        x86.UC_X86_REG_CS,
        (load_segment + image.header.initial_relative_cs) & 0xFFFF,
    )
    uc.reg_write(x86.UC_X86_REG_IP, image.header.initial_ip)
    uc.reg_write(
        x86.UC_X86_REG_SS,
        (load_segment + image.header.initial_relative_ss) & 0xFFFF,
    )
    uc.reg_write(x86.UC_X86_REG_SP, image.header.initial_sp)
    uc.reg_write(x86.UC_X86_REG_DS, psp_segment)
    uc.reg_write(x86.UC_X86_REG_ES, psp_segment)

    relocations: list[RelocationObservation] = []
    state: dict[str, object] = {
        "instructions": 0,
        "dos_version_calls": 0,
        "final": None,
        "error": None,
    }

    if original_format == "mz":
        assert expected_entry_cs is not None
        expected_transfer = (
            (load_segment + expected_entry_cs) & 0xFFFF,
            expected_entry_ip,
        )
    elif original_format == "com":
        expected_transfer = (psp_segment, expected_entry_ip)
    else:
        raise DietError(f"unsupported original format {original_format!r}")

    def on_code(machine: object, address: int, size: int, user_data: object) -> None:
        del user_data
        state["instructions"] = int(state["instructions"]) + 1
        if int(state["instructions"]) > max_instructions:
            state["error"] = f"instruction limit exceeded ({max_instructions})"
            machine.emu_stop()
            return
        raw = bytes(machine.mem_read(address, max(size, 5)))
        if code_hook is not None:
            code_hook(address, raw[:size])
        if raw.startswith(RELOCATION_OPCODE):
            es = int(machine.reg_read(x86.UC_X86_REG_ES)) & 0xFFFF
            bx = int(machine.reg_read(x86.UC_X86_REG_BX)) & 0xFFFF
            relative_segment = (es - load_segment) & 0xFFFF
            relative_linear = (es << 4) + bx - load_physical
            relocations.append(RelocationObservation(
                len(relocations), es, bx, relative_segment, relative_linear
            ))
        if raw[0] == 0xEA:
            ip, cs = struct.unpack_from("<HH", raw, 1)
            if (cs, ip) == expected_transfer:
                state["final"] = (cs, ip)
                machine.emu_stop()

    def on_interrupt(machine: object, interrupt: int, user_data: object) -> None:
        del user_data
        ah = (int(machine.reg_read(x86.UC_X86_REG_AX)) >> 8) & 0xFF
        if interrupt == 0x21 and ah == 0x30:
            # DOS 5.00.  The decompressor uses this only to gate DOS-era behavior.
            machine.reg_write(x86.UC_X86_REG_AX, 0x0005)
            machine.reg_write(x86.UC_X86_REG_BX, 0)
            machine.reg_write(x86.UC_X86_REG_CX, 0)
            state["dos_version_calls"] = int(state["dos_version_calls"]) + 1
            return
        state["error"] = f"unexpected interrupt 0x{interrupt:02x}/AH=0x{ah:02x}"
        machine.emu_stop()

    uc.hook_add(unicorn.UC_HOOK_CODE, on_code)
    uc.hook_add(unicorn.UC_HOOK_INTR, on_interrupt)
    entry = (
        (load_segment + image.header.initial_relative_cs) << 4
    ) + image.header.initial_ip
    try:
        uc.emu_start(entry, memory_size - 1, count=max_instructions + 1)
    except unicorn.UcError as error:
        raise DietError(f"DIET emulation failed at load segment 0x{load_segment:04x}: {error}") from error
    if state["error"]:
        raise DietError(str(state["error"]))
    if state["final"] is None:
        raise DietError("decompressor did not reach the configured original entry transfer")
    relocated_payload = bytes(uc.mem_read(load_physical, payload_size))
    return EmulationResult(
        load_segment=load_segment,
        relocated_payload=relocated_payload,
        relocations=tuple(relocations),
        final_cs=int(state["final"][0]),
        final_ip=int(state["final"][1]),
        final_ss=int(uc.reg_read(x86.UC_X86_REG_SS)) & 0xFFFF,
        final_sp=int(uc.reg_read(x86.UC_X86_REG_SP)) & 0xFFFF,
        instruction_count=int(state["instructions"]),
        dos_version_calls=int(state["dos_version_calls"]),
    )


def relocation_identity(result: EmulationResult) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (item.relative_segment, item.bx, item.relative_linear)
        for item in result.relocations
    )


def observe(
    target: bytes,
    policy: dict[str, object],
    load_segments: tuple[int, ...],
    max_instructions: int,
) -> tuple[bytes, tuple[RelocationObservation, ...], list[EmulationResult]]:
    if len(set(load_segments)) < 2:
        raise DietError("at least two distinct load segments are required")
    original_format = str(policy["original_format"])
    expected_entry_cs = (
        int(policy["entry_cs"]) if "entry_cs" in policy else None
    )
    results = [
        emulate_once(
            target,
            payload_size=int(policy["payload_size"]),
            original_format=original_format,
            expected_entry_cs=expected_entry_cs,
            expected_entry_ip=int(policy["entry_ip"]),
            load_segment=segment,
            max_instructions=max_instructions,
        )
        for segment in load_segments
    ]
    normalized = [
        normalize_payload(item.relocated_payload, item.relocations, item.load_segment)
        for item in results
    ]
    reference_relocations = relocation_identity(results[0])
    for result, payload in zip(results[1:], normalized[1:]):
        if relocation_identity(result) != reference_relocations:
            raise DietError(
                f"relocation stream changes at load segment 0x{result.load_segment:04x}"
            )
        if payload != normalized[0]:
            raise DietError(
                f"unrelocated payload changes at load segment 0x{result.load_segment:04x}"
            )
    expected_count = int(policy["relocation_count"])
    if len(results[0].relocations) != expected_count:
        raise DietError(
            f"relocation count mismatch: observed {len(results[0].relocations)}, "
            f"expected {expected_count}"
        )
    if original_format == "mz":
        expected_ss = int(policy["initial_ss"])
        expected_sp = int(policy["initial_sp"])
        for result in results:
            if (result.final_ss - result.load_segment) & 0xFFFF != expected_ss:
                raise DietError("original SS differs from configured topology")
            if result.final_sp != expected_sp:
                raise DietError("original SP differs from configured topology")
    return normalized[0], results[0].relocations, results


def write_outputs(
    output: Path,
    artifact: dict[str, object],
    target: bytes,
    policy: dict[str, object],
    payload: bytes,
    relocations: tuple[RelocationObservation, ...],
    results: list[EmulationResult],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "payload.bin").write_bytes(payload)
    with (output / "relocations.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow([
            "index", "relative_segment", "offset", "relative_linear",
            "observed_es_first_run",
        ])
        for item in relocations:
            writer.writerow([
                item.index, f"0x{item.relative_segment:04x}", f"0x{item.bx:04x}",
                f"0x{item.relative_linear:x}", f"0x{item.es:04x}",
            ])
    receipt = {
        "schema_version": 1,
        "artifact": artifact["id"],
        "packed_target_sha256": sha256(target),
        "packed_target_size": len(target),
        "diet_marker_file_offset": DIET_MARKER_OFFSET,
        "policy": policy,
        "method": {
            "emulator": "Unicorn x86 16-bit real mode",
            "unicorn_version": REQUIRED_UNICORN_VERSION,
            "dos_interrupts": ["INT 21h/AH=30h -> DOS 5.00"],
            "stop": "before target-observed far transfer to original entry",
            "relocation_instruction": RELOCATION_OPCODE.hex(),
            "normalization": "subtract each run's load segment at every observed relocation",
        },
        "runs": [
            {
                "load_segment": f"0x{item.load_segment:04x}",
                "instruction_count": item.instruction_count,
                "dos_version_calls": item.dos_version_calls,
                "relocation_count": len(item.relocations),
                "relocated_payload_sha256": sha256(item.relocated_payload),
                "final_cs": f"0x{item.final_cs:04x}",
                "final_ip": f"0x{item.final_ip:04x}",
                "final_ss": f"0x{item.final_ss:04x}",
                "final_sp": f"0x{item.final_sp:04x}",
            }
            for item in results
        ],
        "checks": {
            "manifest_target_identity": sha256(target) == artifact["sha256"],
            "distinct_load_segments": len({item.load_segment for item in results}) == len(results),
            "relocation_stream_load_invariant": True,
            "unrelocated_payload_load_invariant": True,
            "configured_relocation_count": len(relocations) == int(policy["relocation_count"]),
            "configured_payload_size": len(payload) == int(policy["payload_size"]),
        },
        "payload_size": len(payload),
        "payload_sha256": sha256(payload),
        "relocation_count": len(relocations),
    }
    (output / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_id", choices=("th04-op", "th04-maine", "th04-zun"))
    parser.add_argument(
        "--output-dir", type=Path,
        help="ignored output directory (default: .analysis/reconstruction/boundary-review/ARTIFACT)",
    )
    parser.add_argument(
        "--load-segment", action="append", type=lambda value: int(value, 0),
        dest="load_segments", help="repeat at least twice (default: 0x1000 and 0x2000)",
    )
    parser.add_argument("--max-instructions", type=int, default=20_000_000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.max_instructions <= 0:
            raise DietError("max instructions must be positive")
        manifest = load_target_manifest(TARGET_CONFIG)
        artifact = find_artifact(manifest, args.artifact_id)
        target = read_verified_artifact(ROOT, artifact)
        policy = load_policy(args.artifact_id)
        load_segments = tuple(args.load_segments or DEFAULT_LOAD_SEGMENTS)
        output = private_output(
            args.output_dir
            or ROOT / ".analysis" / "reconstruction" / "boundary-review" / args.artifact_id
        )
        payload, relocations, results = observe(
            target, policy, load_segments, args.max_instructions
        )
        write_outputs(output, artifact, target, policy, payload, relocations, results)
        print(
            f"{args.artifact_id}: {len(payload)} unrelocated bytes, "
            f"{len(relocations)} relocations, sha256={sha256(payload)}"
        )
        print(f"private output: {output}")
        return 0
    except (DietError, KeyError, OSError, struct.error, tomllib.TOMLDecodeError) as error:
        print(f"error: DIET observation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
