#!/usr/bin/env python3
"""Replay the v483 TH04 MAINE regist_menu() natural-C++ compiler frontier.

This is deliberately a *non-exact* compiler-shape packet. It starts from the
retained v478 MAINE source snapshot, recompiles only the natural SCORE_TEXT C++
prefix through regist_menu(), and asserts the exact remaining raw OMF CODE
differences. No link-order or packed-file credit is granted here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402
from probe_th04_maine_score_insert_cpp_v479 import validate_v478_source  # noqa: E402
from probe_th04_maine_score_producers_v468 import digest  # noqa: E402
from probe_th04_maine_segment_topology_v470 import output_dir, tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_master_object_split import sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_score_prefix_v483.cpp.in"
TEMPLATE_SHA = "c11d28528346eea99102ed298442a4f60d891a4fb8adaed158a8e8c4d76b2d1b"
PREFIX_SIZE = 0x07FE
PREFIX_RAW_SHA = "298b234aa98f9d32132d434a323af2f6715db32636ad839711cfc4d23f33e3b9"
REFERENCE_PREFIX_SHA = "ad2a2c95a992d474d97be5e096ec59f8d6ac998b135f8e66b3b85ed302ae6a86"
PREFIX_DIFFS = [0x2F5, 0x2F6, 0x7A7, 0x7A8, 0x7AA, 0x7AB]
REGIST_OFFSET = 0x0462
REGIST_SIZE = 0x039C
REGIST_RAW_SHA = "d9481b34f6872fc507a9053549ad1e05a2a0dbecbab40a5809358d5693becb02"
REFERENCE_REGIST_SHA = "e8fdf2245ad5a741ff86603daf612ecdd36625e724f34b6f2d807ed9ae943340"
REGIST_DIFFS = [0x345, 0x346, 0x348, 0x349]
EXPECTED_CANDIDATE_BYTES = bytes.fromhex("a100000bc0")
EXPECTED_REFERENCE_BYTES = bytes.fromhex("833e000000")
EXPECTED_KIND3_RECORDS = [
    [0x3F5,0x3CF,0x3A6,0x355,0x32E,0x319,0x2A9,0x295,0x224,0x1FB,0x1D3],
    [0x3E4,0x3DD,0x3D8,0x3D3,0x3C1,0x3BA,0x245,0x23B,0x22F,0x209,0x1CA,0x1C3,0x1BC,0x1B0,0x153,0x142,0x0B5,0x0AC,0x0A5,0x097,0x08D,0x086,0x075,0x058],
]
TAIL_SIZE = 0x00CA


def kind3_records(path: Path) -> list[list[int]]:
    records: list[list[int]] = []
    for rec in parse_omf(path.read_bytes()):
        if rec.record_type != 0x9C:
            continue
        locs = [loc for kind, loc in fixup_locations(rec.data) if kind == 3]
        if locs:
            records.append(locs)
    return records


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source = args.source_dir.resolve()
    output = output_dir(args.output_dir)

    validate_v478_source(source)
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v483 template identity drift")
    reference = segment_bytes(source / "obj/th04/mainscv.obj", "SCORE_TEXT")
    if len(reference) != 0x8C8:
        raise ValueError("v478 SCORE owner size drift")
    if digest(reference[:PREFIX_SIZE]) != REFERENCE_PREFIX_SHA:
        raise ValueError("v478 SCORE prefix identity drift")
    if digest(reference[REGIST_OFFSET:REGIST_OFFSET + REGIST_SIZE]) != REFERENCE_REGIST_SHA:
        raise ValueError("v478 regist_menu raw identity drift")

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        shutil.copy2(TEMPLATE, work / "th04/scp8.cpp")
        tcc(work, output, f"v483-regist-{label}", "th04/scp8.cpp")
        obj = work / "obj/th04/scp8.obj"
        prefix = segment_bytes(obj, "SCORE_TEXT")
        if len(prefix) != PREFIX_SIZE or digest(prefix) != PREFIX_RAW_SHA:
            raise ValueError(f"{label}: v483 SCORE prefix identity drift")
        prefix_diffs = [i for i, (a, b) in enumerate(zip(prefix, reference[:PREFIX_SIZE])) if a != b]
        if prefix_diffs != PREFIX_DIFFS:
            raise ValueError(f"{label}: v483 prefix difference set drift: {prefix_diffs}")

        regist = prefix[REGIST_OFFSET:REGIST_OFFSET + REGIST_SIZE]
        ref_regist = reference[REGIST_OFFSET:REGIST_OFFSET + REGIST_SIZE]
        if len(regist) != REGIST_SIZE or digest(regist) != REGIST_RAW_SHA:
            raise ValueError(f"{label}: v483 regist_menu candidate identity drift")
        regist_diffs = [i for i, (a, b) in enumerate(zip(regist, ref_regist)) if a != b]
        if regist_diffs != REGIST_DIFFS:
            raise ValueError(f"{label}: v483 regist_menu difference set drift: {regist_diffs}")
        if regist[0x345:0x34A] != EXPECTED_CANDIDATE_BYTES:
            raise ValueError(f"{label}: candidate zero-test opcode drift")
        if ref_regist[0x345:0x34A] != EXPECTED_REFERENCE_BYTES:
            raise ValueError(f"{label}: reference zero-test opcode drift")
        records = kind3_records(obj)
        if records != EXPECTED_KIND3_RECORDS:
            raise ValueError(f"{label}: v483 kind-3 record layout drift: {records}")

        builds[label] = {
            "object_sha256": sha(obj),
            "prefix_raw_sha256": digest(prefix),
            "reference_prefix_sha256": digest(reference[:PREFIX_SIZE]),
            "prefix_size": len(prefix),
            "prefix_raw_differences": prefix_diffs,
            "regist_raw_sha256": digest(regist),
            "reference_regist_sha256": digest(ref_regist),
            "regist_size": len(regist),
            "regist_equal_bytes": REGIST_SIZE - len(regist_diffs),
            "regist_raw_differences": regist_diffs,
            "candidate_zero_test_hex": regist[0x345:0x34A].hex(),
            "reference_zero_test_hex": ref_regist[0x345:0x34A].hex(),
            "kind3_records": records,
            "remaining_tasm_tail_size": len(reference) - len(prefix),
        }

    for key in (
        "prefix_raw_sha256", "reference_prefix_sha256", "prefix_size",
        "prefix_raw_differences", "regist_raw_sha256", "reference_regist_sha256",
        "regist_size", "regist_equal_bytes", "regist_raw_differences",
        "candidate_zero_test_hex", "reference_zero_test_hex", "kind3_records",
        "remaining_tasm_tail_size",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B v483 {key} differs")
    if builds["a"]["remaining_tasm_tail_size"] != TAIL_SIZE:
        raise ValueError("v483 remaining SCORE tail size drift")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE regist_menu natural-C++ compiler frontier; explicitly non-exact and no packed credit",
        "v478_source_exe_sha256": sha(source / "bin/th04/maine.exe"),
        "v478_source_map_sha256": sha(source / "obj/th04/maine.map"),
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "The natural TC86 SCORE_TEXT source now spans 0x7FE bytes through regist_menu(). "
            "The 0x39C-byte regist_menu candidate matches 920/924 raw CODE bytes. Its only remaining "
            "raw differences are offsets 0x345,0x346,0x348,0x349: candidate MOV AX,[key_det] / OR AX,AX "
            "versus reference CMP word ptr [key_det],0. The function size, ENTER 0xA frame, SI/DI allocation, "
            "nine-entry switch table, and every other instruction byte match. The full prefix has only two "
            "additional raw differences, the already-understood same-segment near-call addend at 0x2F5..0x2F6."
        ),
        "negative_surface": (
            "Bounded local experiments closed ordinary if/goto/do/while/for/tail-merge spellings, signed/unsigned/union/bitfield/volatile switch operands, "
            "meaningful and empty shadow-scope variants, whole-function -O-, -O- -y, global -Z-, local -Z-, and -O -y. "
            "None reproduces the remaining CMP-memory plus preserved-JMP combination without perturbing already-exact code."
        ),
        "limit": (
            "This receipt records a non-exact compiler frontier only. It does not grant authored-function exact credit or packed relocation-order credit. "
            "The remaining 0xCA SCORE_TEXT tail is the EGC start/copy pair and remains assembly-owned in this packet."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "prefix_size": PREFIX_SIZE,
        "regist_equal_bytes": REGIST_SIZE - len(REGIST_DIFFS),
        "regist_total_bytes": REGIST_SIZE,
        "remaining_tasm_tail_size": TAIL_SIZE,
        "exact": False,
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
