#!/usr/bin/env python3
"""Diagnose natural-C++ codegen for MAINE egc_start_copy without exact credit."""

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

SOURCE = ROOT / "src/maine/cutscene/egc_start_copy.cpp"
BODY = ROOT / "src/maine/cutscene/egc_start_copy.inl"
DEPENDENCIES = (
    "src/shared/hardware/graphics.hpp",
    "src/shared/platform/abi.hpp",
    "src/shared/platform/pc98.hpp",
    "src/shared/platform/x86.hpp",
    "src/shared/platform/types.hpp",
)
START = 0xA2D6
SIZE = 0x34
TARGET_SHA = "1f0b71efadc4a80c8acced8ae69c7d527b00a34c8b107d5addb885bc36ee8825"
NATURAL_SIZE = 0x33
NATURAL_CODE_SHA = "d27c574dcd96bf6ac2736477ef0b3fbbec42794cee766419ac73fe5142353e75"
NATURAL_FIXUPS = [(3, 4)]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def copy_inputs(work: Path) -> None:
    copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
    for rel in (
        "src/maine/cutscene/egc_start_copy.cpp",
        "src/maine/cutscene/egc_start_copy.inl",
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
    tcc(work, output, label, "src/maine/cutscene/egc_start_copy.cpp")
    objects = [p for p in (work / "obj/th04").glob("*.obj") if p.name not in before]
    if len(objects) != 1:
        raise RuntimeError(f"{label}: expected one standalone object")
    return code_and_fixups(objects[0])


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_SHA:
        raise RuntimeError("MAINE egc_start_copy target identity drift")
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("MAINE egc_start_copy Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x0286
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + START + SIZE - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 3
        or int(row["callee_count"]) != 1
    ):
        raise RuntimeError(f"MAINE egc_start_copy Ghidra extent drift: {row!r}")
    required = (
        "0A05:0286 idle  egc_start_copy()",
        "0000:0846       EGC_ON",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE egc_start_copy MAP target drift")
    expected_tail = bytes.fromhex(
        "b8 f0 ff ba a0 04 ef "
        "b8 ff 00 ba a2 04 ef "
        "b8 00 31 ba a4 04 ef "
        "b8 ff ff ba a8 04 ef "
        "b8 00 00 ba ac 04 ef "
        "b8 0f 00 ba ae 04 ef 5d c3"
    )
    if (
        body[:3] != bytes.fromhex("55 8b ec")
        or body[3] != 0x9A
        or int.from_bytes(body[4:6], "little") != 0x0846
        or int.from_bytes(body[6:8], "little") != 0x0000
        or body[8:] != expected_tail
    ):
        raise RuntimeError("MAINE egc_start_copy instruction topology drift")
    return {
        "segment_identity": "1A05",
        "segment_offset": "0286",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 3,
        "callee_count": 1,
        "egc_on": "0000:0846",
        "word_port_writes": [
            ["0x04A0", "0xFFF0"],
            ["0x04A2", "0x00FF"],
            ["0x04A4", "0x3100"],
            ["0x04A8", "0xFFFF"],
            ["0x04AC", "0x0000"],
            ["0x04AE", "0x000F"],
        ],
        "load_order": "AX=value then DX=port",
        "terminal": "RET",
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
        "src/maine/cutscene/egc_start_copy.cpp": sha(SOURCE.read_bytes()),
        "src/maine/cutscene/egc_start_copy.inl": sha(BODY.read_bytes()),
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
            len(code) != NATURAL_SIZE
            or sha(code) != NATURAL_CODE_SHA
            or fixups != NATURAL_FIXUPS
        ):
            raise RuntimeError(f"{label}: natural egc_start_copy codegen drift")
        codes.append(code)
        rounds.append({
            "label": label,
            "code_size": len(code),
            "code_sha256": sha(code),
            "fixups": [list(x) for x in fixups],
        })
    if codes[0] != codes[1]:
        raise RuntimeError("natural egc_start_copy cold codegen differs")

    # Mask the one ordinary FAR-call relocation and compare the actual
    # instruction streams. The target is one byte longer because TC86 uses
    # XOR AX,AX for ordinary outport(..., 0), and every port write also loads
    # DX before AX while the target consistently uses the reverse order.
    target_masked = bytearray(target)
    candidate_masked = bytearray(codes[0])
    target_masked[4:8] = b"\0" * 4
    candidate_masked[4:8] = b"\0" * 4
    if target_masked[:8] != candidate_masked[:8]:
        raise RuntimeError("egc_start_copy prologue/call masking drift")
    if target_masked[8:] == candidate_masked[8:]:
        raise RuntimeError("egc_start_copy unexpectedly became exact")

    decomp = ROOT / "_reference/ReC98/decomp.hpp"
    decomp_text = decomp.read_text(encoding="utf-8", errors="replace")
    if "#define outport2(port, val) _asm" not in decomp_text:
        raise RuntimeError("historical decomp outport2 provenance drift")

    if {
        "src/maine/cutscene/egc_start_copy.cpp": sha(SOURCE.read_bytes()),
        "src/maine/cutscene/egc_start_copy.inl": sha(BODY.read_bytes()),
        **{rel: sha((ROOT / rel).read_bytes()) for rel in DEPENDENCIES},
    } != source_hashes:
        raise RuntimeError("maintained egc_start_copy source changed during probe")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-maine",
        "function": "egc_start_copy",
        "boundary": boundary,
        "source_sha256": source_hashes,
        "natural": {
            "rounds": rounds,
            "target_size": SIZE,
            "candidate_size": NATURAL_SIZE,
            "size_delta_from_target": NATURAL_SIZE - SIZE,
            "mismatch": (
                "Ordinary outport() emits DX=port before AX=value for all six "
                "word writes; target emits AX=value before DX=port. For the zero "
                "value, ordinary outport() also selects XOR AX,AX instead of MOV AX,0."
            ),
        },
        "exploration": {
            "variants_tested": ["direct", "local temporary", "register temporary", "const locals"],
            "variant_sizes": {"direct": 51, "local temporary": 65, "register temporary": 65, "const locals": 82},
            "all_exact": False,
        },
        "historical_helper_provenance": {
            "path": "_reference/ReC98/decomp.hpp",
            "sha256": sha(decomp.read_bytes()),
            "finding": "outport2 is explicitly an _asm helper in a file labeled for decompilation support.",
            "compiled": False,
            "source_credit": False,
        },
        "limit": (
            "Diagnostic codegen evidence only. No inline assembly, pseudo-register "
            "forcing, or historical decompilation helper is accepted as authored "
            "source; the function remains source-present and nonexact."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "target_size": SIZE,
        "natural_size": NATURAL_SIZE,
        "natural_sha256": NATURAL_CODE_SHA,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
