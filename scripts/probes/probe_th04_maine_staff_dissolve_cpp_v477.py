#!/usr/bin/env python3
"""Recover the first four TH04 MAINE staff-roll helpers as one TC86 C++ TU."""
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

from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_master_relocation_order import BASE as V401_BASE  # noqa: E402
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked,
)
from probe_th04_maine_segment_topology_v470 import PROGRAM_SHA, output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_verdict_animate_cpp_v476 import (  # noqa: E402
    FINAL_EXE as V476_EXE,
    FINAL_MAP as V476_MAP,
    EXPECTED_MISMATCHES as V476_MISMATCHES,
    make_fused_source,
    prepare_v475,
    segment_bytes,
)
from probe_th04_master_object_split import compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from lib.omf import parse_omf  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_staff_dissolve_v477.cpp.in"
TEMPLATE_SHA = "6188ca8add86b1068fd5501386700835849a85008803726b8cb2c182459297a7"
D4_SIZE = 0x3C1
D4_RAW_SHA = "1cbbcaa3153f1df6222707cc52fa1b56bb2fd81a2bec984615c3e3e4a38ff4f5"
FINAL_EXE = "dad219be755c32c27f9bb2db4563d64e2c2b1b390b5caeddff8d711756b9130b"
FINAL_MAP = "a4fa9483717816a9efe2977801b3c5a47e5404956e1aefa43bd4d049289e9030"
EXPECTED_MISMATCHES = 98
EXPECTED_CHANGED = list(range(152, 173)) + list(range(174, 195))
KIND3 = [
    0x3B8, 0x37B, 0x368, 0x359, 0x34C, 0x339, 0x323, 0x30F, 0x2FC,
    0x2ED, 0x2E0, 0x2CD, 0x2B7, 0x29C, 0x28E, 0x264, 0x251, 0x242,
    0x235, 0x222, 0x20C, 0x1F8, 0x1E5, 0x1D6, 0x1C9, 0x1B6, 0x1A0,
    0x185, 0x177, 0x145, 0x132, 0x11A, 0x0FF, 0x0EC, 0x0D4, 0x0B9,
    0x0A6, 0x08E, 0x073, 0x060, 0x048, 0x028, 0x01A,
]


def prepare_v476(work: Path, output: Path, label: str) -> None:
    prepare_v475(work, output, label)
    make_fused_source(work)
    tcc(work, output, f"v476-verdict-{label}", "th04/vb.cpp")
    tasm(work, output, f"v476-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")
    rsp = work / "obj/th04/maine.@l"
    text = rsp.read_text()
    old = r"obj\th04\bb81.obj obj\th04\m1tail75.obj"
    if text.count(old) != 1:
        raise ValueError(f"{label}: v475 verdict pair drift")
    rsp.write_text(text.replace(old, r"obj\th04\vb.obj", 1))
    exe = work / "bin/th04/maine.exe"
    map_path = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True); map_path.unlink(missing_ok=True)
    run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"], work, output / f"v476-link-{label}.log")
    if sha(exe) != V476_EXE or sha(map_path) != V476_MAP:
        raise ValueError(f"{label}: v476 baseline identity drift")
    image = parse_mz(exe.read_bytes())
    if digest(image.program_image) != PROGRAM_SHA:
        raise ValueError(f"{label}: v476 program image drift")


def split_staff_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v477 template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/d4.cpp")
    source = work / "th04_maine_01_pre_v471.asm"
    text = source.read_bytes().decode("cp932")
    seg = "maine_01_TEXT segment byte public 'CODE' use16"
    positions = []
    off = 0
    while True:
        pos = text.find(seg, off)
        if pos < 0: break
        positions.append(pos); off = pos + 1
    if len(positions) != 2:
        raise ValueError(f"MAINE_01 segment occurrence drift: {positions}")
    real = positions[1]
    end_marker = "maine_01_TEXT ends"
    seg_end = text.index(end_marker, real)
    common = text[:real]
    body = text[real + len(seg):seg_end]
    start = body.index("sub_AED0\tproc near")
    end = body.index("sub_B25B\tendp", start) + len("sub_B25B\tendp")
    tail_body = body[end:]
    symbols = {
        "sub_B25B": "@STAFFROLL_BGIMAGE_EXPAND_PUT$QIIIII",
        "sub_AED0": "@STAFFROLL_DISSOLVE_RADIAL_PUT$QIII",
        "sub_B02D": "@STAFFROLL_DISSOLVE_DIAGONAL_PUT$QIII",
        "sub_B144": "@STAFFROLL_DISSOLVE_AXIS_PUT$QIII",
    }
    for old, new in symbols.items():
        tail_body = tail_body.replace(old, new)
    for old in symbols:
        if old in tail_body:
            raise ValueError(f"old cross-object symbol remains: {old}")
    assume = (
        "\r\n\t\tassume cs:group_01\r\n"
        "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n"
    )
    tail = common + seg + assume + tail_body + end_marker + "\r\n\tend\r\n"
    text_end = tail.index("_TEXT ends\r\n") + len("_TEXT ends\r\n")
    externs = "\r\n" + "".join(f"\textern {name}:near\r\n" for name in symbols.values())
    tail = tail[:text_end] + externs + tail[text_end:]
    (work / "th04_maine_01_after_d4_v477.asm").write_bytes(tail.encode("cp932"))


def kind3_locations(path: Path) -> list[int]:
    out = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            out.extend(loc for kind, loc in fixup_locations(record.data) if kind == 3)
    return out


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
    target = parse_mz(target_path.read_bytes()); target_sites = [r.linear for r in target.relocations]

    builds = {}
    for label in ("a", "b"):
        work = output / label / "source"; shutil.copytree(source, work, symlinks=True)
        prepare_v476(work, output, label)
        baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes()); baseline_sites = [r.linear for r in baseline.relocations]
        if sum(a != b for a, b in zip(baseline_sites, target_sites)) != V476_MISMATCHES:
            raise ValueError(f"{label}: v476 order frontier drift")
        old_pre = segment_bytes(work / "obj/th04/m1pre.obj", "MAINE_01_TEXT")
        if len(old_pre) != 0x8B7: raise ValueError(f"{label}: v476 pre owner size drift")

        split_staff_owner(work)
        tcc(work, output, f"v477-d4-{label}", "th04/d4.cpp")
        tasm(work, output, f"v477-tail-{label}", "th04_maine_01_after_d4_v477.asm", "m1after4.obj")
        d4 = segment_bytes(work / "obj/th04/d4.obj", "MAINE_01_TEXT")
        tail = segment_bytes(work / "obj/th04/m1after4.obj", "MAINE_01_TEXT")
        if len(d4) != D4_SIZE or digest(d4) != D4_RAW_SHA or d4 != old_pre[:D4_SIZE]:
            raise ValueError(f"{label}: d4 raw CODE is not exact")
        if len(d4) + len(tail) != len(old_pre): raise ValueError(f"{label}: split size drift")
        fixes = kind3_locations(work / "obj/th04/d4.obj")
        if fixes != KIND3: raise ValueError(f"{label}: d4 FIXUPP order drift")
        rsp = work / "obj/th04/maine.@l"; text = rsp.read_text(); old = r"obj\th04\m1pre.obj"; new = r"obj\th04\d4.obj obj\th04\m1after4.obj"
        if text.count(old) != 1: raise ValueError(f"{label}: m1pre token drift")
        rsp.write_text(text.replace(old, new, 1))
        exe = work / "bin/th04/maine.exe"; map_path = work / "obj/th04/maine.map"; exe.unlink(missing_ok=True); map_path.unlink(missing_ok=True)
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"], work, output / f"v477-link-{label}.log")
        image = parse_mz(exe.read_bytes()); sites = [r.linear for r in image.relocations]; payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image or digest(image.program_image) != PROGRAM_SHA: raise ValueError(f"{label}: linked image changed")
        if Counter(sites) != Counter(target_sites): raise ValueError(f"{label}: relocation multiset drift")
        changed = [i for i,(a,b) in enumerate(zip(baseline_sites,sites)) if a != b]
        if changed != EXPECTED_CHANGED: raise ValueError(f"{label}: changed indices drift: {changed}")
        if sites[152:195] != target_sites[152:195]: raise ValueError(f"{label}: target slice 152..194 not exact")
        ordered = sum(a != b for a,b in zip(sites,target_sites))
        if ordered != EXPECTED_MISMATCHES: raise ValueError(f"{label}: residual drift: {ordered}")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP: raise ValueError(f"{label}: output identity drift")
        builds[label] = {
            "exe_sha256": sha(exe), "map_sha256": sha(map_path), "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload, "d4_raw_sha256": digest(d4), "d4_size": len(d4), "tail_size": len(tail),
            "kind3_locations": fixes, "changed_indices_vs_v476": changed, "target_exact_sites_152_194": sites[152:195],
            "ordered_relocation_mismatches": ordered, "same_index_relocations": len(sites)-ordered,
        }
    for key in ("exe_sha256","map_sha256","program_image_sha256","d4_raw_sha256","d4_size","tail_size","kind3_locations","changed_indices_vs_v476","target_exact_sites_152_194","ordered_relocation_mismatches","same_index_relocations"):
        if builds["a"][key] != builds["b"][key]: raise ValueError(f"A/B {key} differs")
    receipt = {
        "schema_version": 1, "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE first four staff-roll helpers natural-C++ raw/linked exact relocation-order replay",
        "source_baseline": V401_BASE, "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)), "template_sha256": TEMPLATE_SHA, "builds": builds,
        "observed_effect": "The first four MAINE_01 staff-roll helpers compile as one 0x3C1 TC86 C++ owner whose raw CODE is byte-exact. Linked program bytes remain unchanged. TC86 emits one high-address-first segment FIXUPP stream: the one sub_B25B site, then the reversed sub_B144, sub_B02D, and sub_AED0 runs. Target relocation indices 152..194 become exact and MAINE ordered residual falls 140 to 98 with the 559-site multiset unchanged.",
        "limit": "The TASM remainder only redirects four existing near/public symbol references across the new source-level object boundary. Remaining MAINE_01 staffroll producer order, SCORE_TEXT internal order, and BGIMAGE direction are unresolved."
    }
    rp = output / "receipt.json"; rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(rp), "receipt_sha256": sha(rp), "candidate_sha256": FINAL_EXE, "ordered_relocation_mismatches": EXPECTED_MISMATCHES, "same_index_relocations": 559-EXPECTED_MISMATCHES}, sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
