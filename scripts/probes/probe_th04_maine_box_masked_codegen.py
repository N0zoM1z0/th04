#!/usr/bin/env python3
"""Diagnose natural-C++ codegen for MAINE box_1_to_0_masked without exact credit."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
import replay_th04_maine_score_insert as prior  # noqa: E402

SOURCE = ROOT / "src/maine/cutscene/box_1_to_0_masked.cpp"
BODY = ROOT / "src/maine/cutscene/box_1_to_0_masked.inl"
DEPENDENCIES = (
    "src/shared/hardware/graphics.hpp",
    "src/shared/platform/abi.hpp",
    "src/shared/platform/pc98.hpp",
    "src/shared/platform/x86.hpp",
    "src/shared/platform/types.hpp",
)
START = 0xA78F
SIZE = 0x86
TARGET_SHA = "1a7ddf9c97c9fa1cb40368133d5b01e41cb359a40b516854d8754aea6735d012"
NATURAL_CODE_SHA = "e6beef20b6a886875bfb81436a27f46f8b6f704718989ddd19d6940400d1eb4a"
NATURAL_FIXUPS = [(1, 99), (1, 84), (1, 49)]
MUL_CODE_SHA = "b0738a04e17c13b820cc0f6ff78b85389620cbe47d986e54b33b90001b55f7a6"
MUL_SIZE = 0x7F
MUL_FIXUPS = [(1, 92), (1, 77), (1, 49)]
LOAD_ORDER_DIFFS = [
    11, 12, 13, 14, 15, 16,
    18, 19, 20, 21, 22, 23,
    25, 26, 27, 28, 29, 30,
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def copy_inputs(work: Path) -> None:
    copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
    for rel in (
        "src/maine/cutscene/box_1_to_0_masked.cpp",
        "src/maine/cutscene/box_1_to_0_masked.inl",
        *DEPENDENCIES,
    ):
        dst = work / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)


def code_and_fixups(obj: Path) -> tuple[bytes, list[tuple[int, int]]]:
    code = segment_bytes(obj, "CUTSCENE_TEXT")
    fixups = [
        item
        for record in parse_omf(obj.read_bytes())
        if record.record_type == 0x9C
        for item in fixup_locations(record.data)
    ]
    return code, fixups


def compile_one(work: Path, output: Path, label: str) -> tuple[bytes, list[tuple[int, int]]]:
    before = {p.name for p in (work / "obj/th04").glob("*.obj")}
    tcc(work, output, label, "src/maine/cutscene/box_1_to_0_masked.cpp")
    objects = [p for p in (work / "obj/th04").glob("*.obj") if p.name not in before]
    if len(objects) != 1:
        raise RuntimeError(f"{label}: expected one standalone object")
    return code_and_fixups(objects[0])


def mask(data: bytes, fixups: list[tuple[int, int]]) -> bytes:
    out = bytearray(data)
    for kind, offset in fixups:
        width = 2 if kind == 1 else 4
        out[offset:offset + width] = b"\0" * width
    return bytes(out)


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_SHA:
        raise RuntimeError("MAINE box_1_to_0_masked target identity drift")
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("MAINE box_1_to_0_masked Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x073F
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + START + SIZE - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 0
    ):
        raise RuntimeError(f"MAINE box_1_to_0_masked Ghidra extent drift: {row!r}")
    required = (
        "0A05:073F idle  box_1_to_0_masked(box_mask_t)",
        "0E53:062C       _BOX_MASKS",
        "0E53:170C       _VRAM_PLANE_B",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE box_1_to_0_masked MAP target drift")
    return {
        "segment_identity": "1A05",
        "segment_offset": "073F",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 1,
        "callee_count": 0,
        "box_masks": "0E53:062C",
        "vram_plane_b": "0E53:170C",
        "rows": [320, 384],
        "width_pixels": 480,
        "terminal": "RET 2",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output must be a new direct child of .analysis/reconstruction/probes")
    output.mkdir(parents=True)

    target_mz = parse_mz(prior.TARGET.read_bytes())
    target = target_mz.program_image[START:START + SIZE]
    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    boundary = target_boundary(target, map_text)

    source_hashes = {
        "src/maine/cutscene/box_1_to_0_masked.cpp": sha(SOURCE.read_bytes()),
        "src/maine/cutscene/box_1_to_0_masked.inl": sha(BODY.read_bytes()),
        **{rel: sha((ROOT / rel).read_bytes()) for rel in DEPENDENCIES},
    }

    rounds = []
    codes = []
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        copy_inputs(work)
        code, fixups = compile_one(work, output, f"natural-{label}")
        if (
            len(code) != SIZE
            or sha(code) != NATURAL_CODE_SHA
            or fixups != NATURAL_FIXUPS
        ):
            raise RuntimeError(f"{label}: natural codegen drift")
        codes.append(code)
        rounds.append({
            "label": label,
            "code_size": len(code),
            "code_sha256": sha(code),
            "fixups": [list(x) for x in fixups],
        })
    if codes[0] != codes[1]:
        raise RuntimeError("natural cold codegen differs")

    target_masked = mask(target, NATURAL_FIXUPS)
    natural_masked = mask(codes[0], NATURAL_FIXUPS)
    differences = [
        i for i, pair in enumerate(zip(target_masked, natural_masked))
        if pair[0] != pair[1]
    ]
    if differences != LOAD_ORDER_DIFFS:
        raise RuntimeError(f"natural mismatch is no longer isolated to EGC load order: {differences}")

    # Diagnostic-only arithmetic control. This uses the equally natural y*ROW_SIZE
    # spelling and proves that the seven-byte size gap in the first experiment
    # comes solely from TC86 selecting IMUL instead of the planar shift formula.
    mul_work = output / "mul-diagnostic/maine/source"
    mul_work.parent.mkdir(parents=True)
    copy_inputs(mul_work)
    mul_body = mul_work / "src/maine/cutscene/box_1_to_0_masked.inl"
    text = mul_body.read_text()
    old = "((y << 6) + (y << 4) + (BOX_LEFT / BYTE_DOTS))"
    new = "((y * ROW_SIZE) + (BOX_LEFT / BYTE_DOTS))"
    if text.count(old) != 1:
        raise RuntimeError("multiplication diagnostic source anchor drift")
    mul_body.write_text(text.replace(old, new, 1))
    mul_code, mul_fixups = compile_one(mul_work, output, "mul-diagnostic")
    if len(mul_code) != MUL_SIZE or sha(mul_code) != MUL_CODE_SHA or mul_fixups != MUL_FIXUPS:
        raise RuntimeError("multiplication diagnostic drift")

    decomp = ROOT / "_reference/ReC98/decomp.hpp"
    decomp_text = decomp.read_text(encoding="utf-8", errors="replace")
    if "#define outport2(port, val) _asm" not in decomp_text:
        raise RuntimeError("historical decomp outport2 provenance drift")

    if {
        "src/maine/cutscene/box_1_to_0_masked.cpp": sha(SOURCE.read_bytes()),
        "src/maine/cutscene/box_1_to_0_masked.inl": sha(BODY.read_bytes()),
        **{rel: sha((ROOT / rel).read_bytes()) for rel in DEPENDENCIES},
    } != source_hashes:
        raise RuntimeError("maintained natural source changed during probe")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-maine",
        "function": "box_1_to_0_masked",
        "boundary": boundary,
        "source_sha256": source_hashes,
        "natural": {
            "rounds": rounds,
            "target_size": SIZE,
            "masked_difference_count": len(differences),
            "masked_difference_offsets": differences,
            "mismatch": (
                "TC86 ordinary outport() loads DX=port before AX=value for the first "
                "three EGC setup writes; target loads AX=value before DX=port."
            ),
        },
        "multiplication_diagnostic": {
            "code_size": len(mul_code),
            "code_sha256": sha(mul_code),
            "fixups": [list(x) for x in mul_fixups],
            "size_delta_from_target": len(mul_code) - SIZE,
            "source_credit": False,
        },
        "historical_helper_provenance": {
            "path": "_reference/ReC98/decomp.hpp",
            "sha256": sha(decomp.read_bytes()),
            "finding": "outport2 is explicitly an _asm helper in a file labeled for decompilation support.",
            "compiled": False,
            "source_credit": False,
        },
        "limit": (
            "Diagnostic codegen evidence only. No inline assembly or historical "
            "decompilation helper is accepted as authored source, so this function "
            "remains source-present and nonexact."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "target_size": SIZE,
        "natural_size": len(codes[0]),
        "masked_difference_count": len(differences),
        "mul_size": len(mul_code),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
