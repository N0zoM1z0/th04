#!/usr/bin/env python3
"""Validate maintained ZUN cfg_init codegen independently of resident link layout."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/probes"))

from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_zun_cfg_init import code  # noqa: E402
from replay_th04_zun_source_only import (  # noqa: E402
    FLAGS, PAYLOAD, PAYLOAD_SHA256, RUNNER, sha, source_closure,
)

SOURCE = "src/zun/config/cfg_init.cpp"
TARGET_START = 0xDCF
TARGET_SIZE = 0x98
TARGET_SHA256 = "8fc23f22f653db2afd65ad4cdab19776f5e9f1cdbbfa9de2dd407426fed9bfa2"
CANDIDATE_SHA256 = "4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4"
EXPECTED_FIXUPS = (
    0x93, 0x90, 0x86, 0x81, 0x7D, 0x73, 0x6A, 0x3A,
    0x37, 0x2B, 0x21, 0x19, 0x15, 0x0F, 0x06,
)
EXPECTED_LINKED_DIFFS = (
    0x15, 0x19, 0x21, 0x2B, 0x37, 0x3A, 0x6A,
    0x73, 0x7D, 0x86, 0x90, 0x93, 0x94,
)


def text_fixups(path: Path) -> list[tuple[int, int]]:
    records = parse_omf(path.read_bytes())
    groups = code_ledata(records, "_TEXT")
    result: list[tuple[int, int]] = []
    for start, _end, record_number, _segment in groups:
        index = record_number
        while index < len(records):
            record = records[index]
            if record.record_type in {0xA0, 0xA1}:
                break
            if record.record_type == 0x9C:
                result.extend((kind, start + offset) for kind, offset in fixup_locations(record.data))
            index += 1
    return result


def masked(code_bytes: bytes, fixups: list[tuple[int, int]]) -> bytes:
    result = bytearray(code_bytes)
    for kind, offset in fixups:
        if kind != 1 or offset + 2 > len(result):
            raise RuntimeError(f"unsupported cfg_init FIXUPP kind/offset: {kind}/{offset:#x}")
        result[offset:offset + 2] = b"\0\0"
    return bytes(result)


def compile_round(label: str, output: Path, inputs: tuple[str, ...]) -> dict[str, object]:
    saved = output / label
    saved.mkdir()
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    with tempfile.TemporaryDirectory(prefix=f"zun-cfg-local-{label}-", dir=output) as temporary:
        work = Path(temporary)
        (work / "obj/th04").mkdir(parents=True)
        for relative in inputs:
            source = ROOT / relative
            destination = work / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            data = (
                source.read_text(encoding="utf-8").encode("cp932")
                if relative.endswith(".cpp")
                else source.read_bytes()
            )
            destination.write_bytes(data)
            os.utime(destination, (946684800, 946684800))
        command = ["wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS, SOURCE]
        completed = subprocess.run(
            command, cwd=work, env=environment,
            capture_output=True, text=True, timeout=120,
        )
        log = saved / "compile.log"
        log.write_text(
            json.dumps(command) + f"\nexit={completed.returncode}\n"
            + completed.stdout + completed.stderr,
            encoding="utf-8",
        )
        obj = work / "obj/th04/cfg_init.obj"
        if completed.returncode or not obj.is_file():
            raise RuntimeError(f"{label}: cfg_init compile failed: {log}")
        saved_obj = saved / "cfg_init.obj"
        saved_obj.write_bytes(obj.read_bytes())
        compiled = code(saved_obj)
        (saved / "cfg_init.code").write_bytes(compiled)
        if len(compiled) != TARGET_SIZE or sha(compiled) != CANDIDATE_SHA256:
            raise RuntimeError(f"{label}: cfg_init CODE drift")
        fixups = text_fixups(saved_obj)
        if tuple(offset for kind, offset in fixups if kind == 1) != EXPECTED_FIXUPS:
            raise RuntimeError(f"{label}: cfg_init FIXUPP location drift: {fixups}")
        if any(kind != 1 for kind, _ in fixups):
            raise RuntimeError(f"{label}: unexpected cfg_init FIXUPP kind")
        return {
            "object_sha256": sha(saved_obj.read_bytes()),
            "code_sha256": sha(compiled),
            "code_size": len(compiled),
            "fixups": [[kind, offset] for kind, offset in fixups],
            "masked_code_sha256": sha(masked(compiled, fixups)),
            "log_sha256": sha(log.read_bytes()),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    payload = PAYLOAD.read_bytes()
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload identity drift")
    target = payload[TARGET_START:TARGET_START + TARGET_SIZE]
    if len(target) != TARGET_SIZE or sha(target) != TARGET_SHA256:
        raise RuntimeError("target cfg_init identity drift")

    inputs = source_closure(ROOT, (SOURCE,))
    input_hashes = {relative: sha((ROOT / relative).read_bytes()) for relative in inputs}
    output.mkdir()
    a = compile_round("a", output, inputs)
    b = compile_round("b", output, inputs)
    stable_keys = ("code_sha256", "code_size", "fixups", "masked_code_sha256")
    if any(a[key] != b[key] for key in stable_keys):
        raise RuntimeError("cold cfg_init compiler rounds disagree")

    fixups = [(int(kind), int(offset)) for kind, offset in a["fixups"]]
    candidate = (output / "a/cfg_init.code").read_bytes()
    raw_differences = [i for i, pair in enumerate(zip(target, candidate)) if pair[0] != pair[1]]
    fixup_bytes = sorted(offset + delta for _kind, offset in fixups for delta in (0, 1))
    if raw_differences != fixup_bytes:
        raise RuntimeError(
            f"cfg_init target/object differences escape FIXUPP words: {raw_differences}"
        )
    target_masked = masked(target, fixups)
    candidate_masked = masked(candidate, fixups)
    if target_masked != candidate_masked:
        raise RuntimeError("cfg_init non-FIXUPP bytes differ")

    component_output = output / "component-link"
    command = [
        sys.executable, "scripts/probes/replay_th04_zun_separate_link.py",
        "--output-dir", str(component_output),
    ]
    completed = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, timeout=600,
    )
    (output / "component-link.log").write_text(
        json.dumps(command) + f"\nexit={completed.returncode}\n"
        + completed.stdout + completed.stderr,
        encoding="utf-8",
    )
    if completed.returncode:
        raise RuntimeError("current separate resident component link failed")
    component_receipt = component_output / "receipt.json"
    if not component_receipt.is_file():
        raise RuntimeError("component link omitted receipt")

    linked = (component_output / "a/res_huma.com").read_bytes()[0x267:0x2FF]
    if len(linked) != TARGET_SIZE:
        raise RuntimeError("current linked cfg_init extent drift")
    linked_differences = [i for i, pair in enumerate(zip(target, linked)) if pair[0] != pair[1]]
    if tuple(linked_differences) != EXPECTED_LINKED_DIFFS:
        raise RuntimeError(f"current linked cfg_init difference set drift: {linked_differences}")
    if not set(linked_differences).issubset(fixup_bytes):
        raise RuntimeError("current linked cfg_init mismatch escapes standalone FIXUPP bytes")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 ZUN cfg_init function-local natural codegen and current link-context blocker",
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_cfg_sha256": TARGET_SHA256,
        "target_cfg_size": TARGET_SIZE,
        "source_input_sha256": input_hashes,
        "cold_builds": {"a": a, "b": b},
        "raw_target_object_difference_count": len(raw_differences),
        "raw_target_object_difference_offsets": raw_differences,
        "fixup_byte_offsets": fixup_bytes,
        "target_masked_sha256": sha(target_masked),
        "candidate_masked_sha256": sha(candidate_masked),
        "non_fixup_bytes_equal": target_masked == candidate_masked,
        "component_link_command": command,
        "component_link_receipt_sha256": sha(component_receipt.read_bytes()),
        "linked_cfg_sha256": sha(linked),
        "linked_raw_difference_count": len(linked_differences),
        "linked_raw_difference_offsets": linked_differences,
        "linked_differences_all_fixup_fields": set(linked_differences).issubset(fixup_bytes),
        "conclusion": (
            "Maintained cfg_init is exactly 152 bytes and every target/object raw "
            "difference is confined to the 15 two-byte OMF FIXUPP fields. After "
            "masking only those fields, all bytes are equal. The current natural "
            "resident link still differs at 13 raw bytes, all within the same FIXUPP "
            "fields because downstream symbols remain shifted by the six-byte _main blocker."
        ),
        "limit": (
            "FIXUPP-masked equality is structural diagnostic evidence only. The current "
            "artifact-local linked cfg_init is not raw equal, so cfg_init remains "
            "source-present and receives no decoded-exact or packed-file credit."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "standalone_raw_differences": len(raw_differences),
        "fixup_words": len(fixups),
        "non_fixup_bytes_equal": receipt["non_fixup_bytes_equal"],
        "linked_raw_differences": len(linked_differences),
        "linked_differences_all_fixup_fields": receipt["linked_differences_all_fixup_fields"],
    }, sort_keys=True))
    print(f"receipt: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
