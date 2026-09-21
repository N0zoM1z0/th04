#!/usr/bin/env python3
"""Recover the complete TH04 MAINE staff-roll MAINE_01 owner as TC86 C++."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_master_relocation_order import BASE as V401_BASE  # noqa: E402
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked,
)
from probe_th04_maine_segment_topology_v470 import PROGRAM_SHA, output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_staff_dissolve_cpp_v477 import (  # noqa: E402
    FINAL_EXE as V477_EXE,
    FINAL_MAP as V477_MAP,
    EXPECTED_MISMATCHES as V477_MISMATCHES,
    prepare_v476,
    split_staff_owner,
    segment_bytes,
)
from probe_th04_master_object_split import compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_staff_full_v478.cpp.in"
TEMPLATE_SHA = "ddd3c9f94720b92dc8e8c14ebb21e673e5e5bc8e98d9e1d4b48f5e54164f4334"
STAFF_SIZE = 0x8B7
STAFF_RAW_SHA = "d30e94167ce85eb5e38ecf6f9dce4f634a9088b7a3f8a9fcb238d5697a0da4d4"
FINAL_EXE = "45aa099ecb29aee883c29ea37c7ad8493ed1871e8b3694a19b63b8e28c331989"
FINAL_MAP = "4be00e3e72042ef0a2ee38a223f63dea39fbf763cd19232b7321adb416200ccc"
EXPECTED_MISMATCHES = 42
EXPECTED_CHANGED = list(range(195, 251))
STAFF_NAMES = [
    "aSff1_pi", "aStaff", "aSff1_cdg", "aSff1b_cdg", "aSff2_cdg", "aSff2b_cdg",
    "aSff3_cdg", "aSff3b_cdg", "aSff2_pi", "aSff4_cdg", "aSff4b_cdg",
    "aSff5_cdg", "aSff5b_cdg", "aSff8_cdg", "aSff8b_cdg", "aSff9_cdg",
    "aSff9b_cdg", "aSff6_cdg", "aSff6b_cdg", "aSff7_cdg", "aSff7b_cdg",
]
KIND3_RECORDS = [
    [0x3B8,0x37B,0x368,0x359,0x34C,0x339,0x323,0x30F,0x2FC,0x2ED,0x2E0,0x2CD,0x2B7,0x29C,0x28E,0x264,0x251,0x242,0x235,0x222,0x20C,0x1F8,0x1E5,0x1D6,0x1C9,0x1B6,0x1A0,0x185,0x177,0x145,0x132,0x11A,0x0FF,0x0EC,0x0D4,0x0B9,0x0A6,0x08E,0x073,0x060,0x048,0x028,0x01A],
    [0x3F1,0x3E6,0x3D9,0x3AF,0x3A4,0x397,0x376,0x36B,0x35E,0x351,0x336,0x32B,0x31E,0x311,0x30A,0x305,0x2FE,0x2F0,0x2E6,0x2DF,0x2CE,0x2C9,0x2AD,0x299,0x28E,0x281,0x246,0x23B,0x22E,0x20D,0x202,0x1F5,0x1E8,0x1E1,0x1DA,0x1CE,0x1C6,0x1C1,0x1BA,0x1AC,0x1A2,0x19B,0x18A,0x176,0x0D5,0x047],
    [0x0BB,0x0B4,0x0AF,0x0AA,0x091,0x084,0x062,0x03A,0x02F,0x022],
]


def kind3_records(path: Path) -> list[list[int]]:
    out: list[list[int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type != 0x9C:
            continue
        locs = [loc for kind, loc in fixup_locations(record.data) if kind == 3]
        if locs:
            out.append(locs)
    return out


def prepare_v477(work: Path, output: Path, label: str) -> None:
    prepare_v476(work, output, label)
    split_staff_owner(work)
    tcc(work, output, f"v477-d4-{label}", "th04/d4.cpp")
    tasm(work, output, f"v477-tail-{label}", "th04_maine_01_after_d4_v477.asm", "m1after4.obj")
    rsp = work / "obj/th04/maine.@l"
    text = rsp.read_text()
    old = r"obj\th04\m1pre.obj"
    new = r"obj\th04\d4.obj obj\th04\m1after4.obj"
    if text.count(old) != 1:
        raise ValueError(f"{label}: v476 m1pre token drift")
    rsp.write_text(text.replace(old, new, 1))
    exe = work / "bin/th04/maine.exe"; mp = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
    run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"], work, output / f"v477-link-{label}.log")
    if sha(exe) != V477_EXE or sha(mp) != V477_MAP:
        raise ValueError(f"{label}: v477 baseline identity drift")
    image = parse_mz(exe.read_bytes())
    if digest(image.program_image) != PROGRAM_SHA:
        raise ValueError(f"{label}: v477 program image drift")


def add_staff_aliases(work: Path) -> None:
    rest = work / "th04_maine_rest_v470.asm"
    text = rest.read_bytes().decode("cp932")
    pos = text.index("public ", text.index("\t.data\r\n"))
    line_end = text.index("\r\n", pos)
    base_line = text[pos:line_end]
    alias_line = "public " + ", ".join("_" + name for name in STAFF_NAMES)
    text = text[:line_end] + "\r\n" + alias_line + text[line_end:]
    for name in STAFF_NAMES:
        needle = name + "\t"
        idx = text.find(needle)
        if idx < 0:
            raise ValueError(f"missing staff data label {name}")
        line_start = text.rfind("\n", 0, idx) + 1
        alias = "_" + name + " label byte\r\n"
        text = text[:line_start] + alias + text[line_start:]
    rest.write_bytes(text.encode("cp932"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source = args.source_dir.resolve(); target_path = args.target_restored.resolve(); output = output_dir(args.output_dir)
    if sha(RUNNER) != RUNNER_SHA: raise ValueError("runner drift")
    for rel, expected in V401_BASE.items():
        if not (source / rel).is_file() or sha(source / rel) != expected:
            raise ValueError(f"v401 source drift: {rel}")
    if sha(target_path) != TARGET_RESTORED_SHA: raise ValueError("target restore drift")
    if sha(TEMPLATE) != TEMPLATE_SHA: raise ValueError("v478 template identity drift")
    target = parse_mz(target_path.read_bytes()); target_sites = [r.linear for r in target.relocations]

    builds = {}
    for label in ("a", "b"):
        work = output / label / "source"; shutil.copytree(source, work, symlinks=True)
        prepare_v477(work, output, label)
        baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes()); baseline_sites = [r.linear for r in baseline.relocations]
        if sum(a != b for a,b in zip(baseline_sites,target_sites)) != V477_MISMATCHES:
            raise ValueError(f"{label}: v477 frontier drift")
        old_pre = segment_bytes(work / "obj/th04/m1pre.obj", "MAINE_01_TEXT")
        if len(old_pre) != STAFF_SIZE or digest(old_pre) != STAFF_RAW_SHA:
            raise ValueError(f"{label}: original staff owner identity drift")

        shutil.copy2(TEMPLATE, work / "th04/staffall.cpp")
        add_staff_aliases(work)
        tcc(work, output, f"v478-staffall-{label}", "th04/staffall.cpp")
        tasm(work, output, f"v478-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")
        obj = work / "obj/th04/staffall.obj"
        code = segment_bytes(obj, "MAINE_01_TEXT")
        if len(code) != STAFF_SIZE or digest(code) != STAFF_RAW_SHA or code != old_pre:
            raise ValueError(f"{label}: complete staff C++ raw CODE is not exact")
        records = kind3_records(obj)
        if records != KIND3_RECORDS:
            raise ValueError(f"{label}: staff kind-3 record order drift")

        rsp = work / "obj/th04/maine.@l"; text = rsp.read_text()
        old = r"obj\th04\d4.obj obj\th04\m1after4.obj"
        if text.count(old) != 1: raise ValueError(f"{label}: v477 split owner pair drift")
        rsp.write_text(text.replace(old, r"obj\th04\staffall.obj", 1))
        exe = work / "bin/th04/maine.exe"; mp = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"], work, output / f"v478-link-{label}.log")
        image = parse_mz(exe.read_bytes()); sites = [r.linear for r in image.relocations]; payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image or digest(image.program_image) != PROGRAM_SHA:
            raise ValueError(f"{label}: complete staff replacement changed linked bytes")
        if Counter(sites) != Counter(target_sites): raise ValueError(f"{label}: relocation multiset drift")
        changed = [i for i,(a,b) in enumerate(zip(baseline_sites,sites)) if a != b]
        if changed != EXPECTED_CHANGED: raise ValueError(f"{label}: changed index set drift: {changed}")
        if sites[195:251] != target_sites[195:251]: raise ValueError(f"{label}: target slice 195..250 not exact")
        ordered = sum(a != b for a,b in zip(sites,target_sites))
        if ordered != EXPECTED_MISMATCHES: raise ValueError(f"{label}: residual drift: {ordered}")
        if sha(exe) != FINAL_EXE or sha(mp) != FINAL_MAP: raise ValueError(f"{label}: output identity drift")
        builds[label] = {
            "exe_sha256": sha(exe), "map_sha256": sha(mp), "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload, "staff_raw_sha256": digest(code), "staff_size": len(code),
            "kind3_records": records, "changed_indices_vs_v477": changed, "target_exact_sites_195_250": sites[195:251],
            "ordered_relocation_mismatches": ordered, "same_index_relocations": len(sites)-ordered,
        }
    for key in ("exe_sha256","map_sha256","program_image_sha256","staff_raw_sha256","staff_size","kind3_records","changed_indices_vs_v477","target_exact_sites_195_250","ordered_relocation_mismatches","same_index_relocations"):
        if builds["a"][key] != builds["b"][key]: raise ValueError(f"A/B {key} differs")
    receipt = {
        "schema_version": 1, "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE complete staff-roll MAINE_01 owner natural-C++ raw/linked exact relocation-order replay",
        "source_baseline": V401_BASE, "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)), "template_sha256": TEMPLATE_SHA, "builds": builds,
        "observed_effect": "All eight staff-roll MAINE_01 functions compile as one 0x8B7 TC86 C++ owner whose raw CODE is byte-exact to the reconstructed TASM owner. The complete linked program image remains unchanged. TC86 naturally interleaves the three segment-FIXUPP records so target relocation indices 195..250 become exact; ordered MAINE residual falls 98 to 42 with the 559-site multiset unchanged. MAINE_01 internal relocation order is now fully closed.",
        "limit": "Existing staff filename bytes remain physically owned by the v470 rest/data object and are exposed via zero-byte C aliases. Remaining MAINE relocation residual is SCORE_TEXT internal order (34) plus shared BGIMAGE direction (8)."
    }
    rp=output/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"candidate_sha256":FINAL_EXE,"ordered_relocation_mismatches":EXPECTED_MISMATCHES,"same_index_relocations":559-EXPECTED_MISMATCHES},sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
