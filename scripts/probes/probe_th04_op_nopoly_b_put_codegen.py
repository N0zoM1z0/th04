#!/usr/bin/env python3
"""Diagnose natural-C++ codegen for OP nopoly_B_put without exact credit."""

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

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import parse_omf
from lib.pc98 import parse_mz
from replay_th04_op_help_put import SNAPSHOT, tcc_op, loose_segment_bytes
from replay_th04_scroll_driver_natural import fixup_locations
from replay_th04_zun_source_only import source_closure

TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/op/music/nopoly_put.cpp"
BODY = ROOT / "src/op/music/nopoly_put.inl"

START = 0xBFA7
SIZE = 0x1E
TARGET_SHA = "f9af3bf25fe94b1ca89ef5ad9bdacd77a87cfc401450a378a12428ea1f409083"
NATURAL_SHA = "e4f9fc0ead018e7bf3ffe49ece3c288a9d7523560bc3eb215ff14e82b668b78e"
NATURAL_FIXUPS = [(1, 6)]
REFERENCE = ROOT / "_reference/ReC98/th02/op/m_music.cpp"
REFERENCE_SHA = "85440d4778240ef183a90134db9969111fef1d24681e8abea5c538242509643f"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def object_fixups(obj: Path) -> list[tuple[int, int]]:
    return [
        item
        for rec in parse_omf(obj.read_bytes())
        if rec.record_type == 0x9C
        for item in fixup_locations(rec.data)
    ]


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_SHA:
        raise RuntimeError("OP nopoly_B_put target identity drift")
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP nopoly_B_put Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x1867
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + START + SIZE - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 2
        or int(row["callee_count"]) != 0
    ):
        raise RuntimeError(f"OP nopoly_B_put Ghidra extent drift: {row!r}")
    if body != bytes.fromhex(
        "55 8b ec 56 57 1e b8 00 a8 8e c0 a1 80 3a 8e d8 "
        "31 ff 31 f6 b9 80 3e f3 a5 1f 5f 5e 5d c3"
    ):
        raise RuntimeError("OP nopoly_B_put instruction topology drift")
    required = (
        "0A74:1867 idle  nopoly_b_put()",
        "0F34:3A80 idle  _nopoly_B",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP nopoly_B_put MAP target drift")
    return {
        "segment_identity": "1A74",
        "segment_offset": "1867",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 2,
        "callee_count": 0,
        "destination_segment": "0xA800",
        "source_segment_pointer": "0F34:3A80 _nopoly_B",
        "word_count": "0x3E80",
        "copy_instruction": "REP MOVSW",
        "target_setup_order": [
            "PUSH DS",
            "AX=0xA800",
            "ES=AX",
            "AX=[nopoly_B]",
            "DS=AX",
            "DI=0",
            "SI=0",
            "CX=0x3E80",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        ap.error("output must be a new direct child of .analysis/reconstruction/probes")
    output.mkdir(parents=True)

    target_mz = parse_mz(TARGET.read_bytes())
    body = target_mz.program_image[START:START + SIZE]
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    bound = target_boundary(body, map_text)

    closure = source_closure(ROOT, ("src/op/music/nopoly_put.cpp",))
    source_hashes = {name: sha_file(ROOT / name) for name in closure}
    builds = []
    codes = []
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        copy_compact_snapshot(SNAPSHOT, work, "op")
        for rel in closure:
            dst = work / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)
        before = {p.name for p in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"nopoly-put-{label}", "src/op/music/nopoly_put.cpp")
        objects = [p for p in (work / "obj/th04").glob("*.obj") if p.name not in before]
        if len(objects) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        obj = objects[0]
        code = loose_segment_bytes(obj, "OP_MUSIC_TEXT")
        fx = object_fixups(obj)
        if len(code) != SIZE or sha(code) != NATURAL_SHA or fx != NATURAL_FIXUPS:
            raise RuntimeError(f"{label}: natural nopoly_B_put codegen drift")
        codes.append(code)
        builds.append({
            "label": label,
            "code_size": len(code),
            "code_sha256": sha(code),
            "fixups": [list(x) for x in fx],
        })
    if codes[0] != codes[1]:
        raise RuntimeError("natural nopoly_B_put cold codegen differs")

    expected_natural = bytes.fromhex(
        "55 8b ec 56 57 a1 00 00 33 f6 ba 00 a8 33 ff b9 "
        "80 3e 8e c2 1e 8e d8 f3 a5 1f 5f 5e 5d c3"
    )
    if codes[0] != expected_natural:
        raise RuntimeError("natural nopoly_B_put instruction order drift")
    if codes[0] == body:
        raise RuntimeError("nopoly_B_put unexpectedly became exact")

    if sha_file(REFERENCE) != REFERENCE_SHA:
        raise RuntimeError("cross-game reference identity drift")
    ref = REFERENCE.read_text(encoding="shift_jis", errors="replace")
    for marker in (
        "void near nopoly_B_put(void)",
        "asm { push ds; }",
        "_ES = SEG_PLANE_B;",
        "_DS = _AX;",
        "__memcpy__(MK_FP(_ES, 0), MK_FP(_DS, 0), PLANE_SIZE);",
    ):
        if marker not in ref:
            raise RuntimeError(f"cross-game reference marker drift: {marker}")

    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained nopoly_B_put source changed during probe")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "function": "nopoly_B_put",
        "boundary": bound,
        "source_sha256": source_hashes,
        "natural": {
            "rounds": builds,
            "target_size": SIZE,
            "candidate_size": SIZE,
            "candidate_sha256": NATURAL_SHA,
            "mismatch": (
                "Intrinsic memcpy emits the same 30-byte REP MOVSW strategy, but "
                "TC86 evaluates the source segment before loading the destination "
                "segment and places PUSH DS immediately before DS=source. The "
                "target loads ES=0xA800 first and saves DS earlier."
            ),
        },
        "exploration": {
            "variants_tested": [
                "dword loop",
                "far word loop",
                "memcpy",
                "_fmemcpy",
                "movedata",
                "intrinsic memcpy with locals",
                "intrinsic memcpy direct",
                "MK_FP intrinsic memcpy",
            ],
            "notable_sizes": {
                "dword loop": 38,
                "far word loop": 60,
                "memcpy/_fmemcpy call": 44,
                "movedata call": 29,
                "intrinsic memcpy with locals": 44,
                "intrinsic memcpy direct": 30,
            },
            "all_exact": False,
        },
        "reference_provenance": {
            "path": "_reference/ReC98/th02/op/m_music.cpp",
            "sha256": REFERENCE_SHA,
            "finding": (
                "The cross-game candidate forces ES/DS pseudoregister order and routes "
                "the copy through __memcpy__(), a decompilation helper surface. "
                "It is reference evidence only."
            ),
            "compiled": False,
            "source_credit": False,
        },
        "limit": (
            "Diagnostic codegen evidence only. Pseudoregister forcing or inline "
            "assembly is not accepted as authored source; the function remains "
            "source-present and nonexact."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "target_sha256": TARGET_SHA,
        "natural_sha256": NATURAL_SHA,
        "size": SIZE,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
