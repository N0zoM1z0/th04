#!/usr/bin/env python3
"""Recover first three TH04 MAINE SCORE_TEXT helpers as one natural TC86 owner."""
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
from probe_th04_maine_score_insert_cpp_v479 import (  # noqa: E402
    V478_EXE, V478_MAP, validate_v478_source,
)
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked,
)
from probe_th04_maine_segment_topology_v470 import output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import EXPECTED_MISMATCHES as V478_MISMATCHES, segment_bytes  # noqa: E402
from probe_th04_master_object_split import compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_score_prefix_v480.cpp.in"
TEMPLATE_SHA = "31a1b8f0a69e2dfa93634561a5db61e829a16fbb68f3df45fb4b14d2d1e19b85"
FINAL_EXE = "0cc4b8adc623a1d5cc510ba703545d3851641ed4536ef75e7e95e30fde479a16"
FINAL_MAP = "281a978ffdbb101041109fce6db06ba3b42cc49e35137911d8fb0275f237f70b"
PREFIX_SIZE = 0x02B3
PREFIX_RAW_SHA = "33c15523010ce54850087504a918a1b0a681ba5009470fdc3ffb0b450c006b1b"
TAIL_SIZE = 0x0615
EXPECTED_MISMATCHES = 42
EXPECTED_CHANGED = [311, 312, 314, 315]
LOCAL_TARGET_SITES = [0xC65D, 0xC649, 0xC5D8, 0xC5AF, 0xC587]
EXPECTED_KIND3 = [0x2A9, 0x295, 0x224, 0x1FB, 0x1D3]


def kind3_locations(path: Path) -> list[int]:
    out: list[int] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            out.extend(loc for kind, loc in fixup_locations(record.data) if kind == 3)
    return out


def split_score_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v480 score prefix template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/scp3.cpp")

    source = work / "th04_maine_score_v470.asm"
    text = source.read_bytes().decode("cp932")
    seg = "SCORE_TEXT segment byte public 'CODE' use16"
    positions: list[int] = []
    off = 0
    while True:
        pos = text.find(seg, off)
        if pos < 0:
            break
        positions.append(pos)
        off = pos + 1
    if len(positions) != 2:
        raise ValueError(f"SCORE segment occurrence drift: {positions}")
    real = positions[1]
    end_marker = "SCORE_TEXT\tends"
    seg_end = text.index(end_marker, real)
    common = text[:real]
    body = text[real + len(seg):seg_end]
    start = body.index("sub_C665\tproc near")
    tail_body = body[start:]
    replacements = {
        "\t\tcall\tsub_C3B2\r\n": "\t\tcall\t@score_insert$qv\r\n",
        "\t\tcall\tsub_C506\r\n": "\t\tcall\t@SCORE_PUT$QIUC\r\n",
        "\t\tcall\tsub_C5EC\r\n": "\t\tcall\t@STAGE_PUT$QIII\r\n",
    }
    for old, new in replacements.items():
        if old not in tail_body:
            raise ValueError(f"score tail call anchor drift: {old!r}")
        tail_body = tail_body.replace(old, new)

    empty = seg + "\r\nSCORE_TEXT ends"
    replacement = (
        seg + "\r\n"
        "\textern @score_insert$qv:near\r\n"
        "\textern @SCORE_PUT$QIUC:near\r\n"
        "\textern @STAGE_PUT$QIII:near\r\n"
        "SCORE_TEXT ends"
    )
    if common.count(empty) != 1:
        raise ValueError("empty SCORE declaration drift")
    common = common.replace(empty, replacement, 1)
    assume = (
        "\r\n\t\tassume cs:group_01\r\n"
        "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n"
    )
    procdesc = (
        "\t@HISCORE_SCOREDAT_LOAD_FOR$Q10PLAYCHAR_T procdesc pascal near \\\r\n"
        "\t\tplaychar:byte\r\n"
        "\t@hiscore_scoredat_save$qv procdesc near\r\n\r\n"
    )
    tail = common + seg + assume + procdesc + tail_body + end_marker + "\r\n\tend\r\n"
    (work / "th04_maine_score_tail_v480.asm").write_bytes(tail.encode("cp932"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source = args.source_dir.resolve(); target_path = args.target_restored.resolve(); output = output_dir(args.output_dir)

    if sha(RUNNER) != RUNNER_SHA:
        raise ValueError("runner identity drift")
    validate_v478_source(source)
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("target restore identity drift")
    target = parse_mz(target_path.read_bytes()); target_sites = [r.linear for r in target.relocations]
    baseline = parse_mz((source / "bin/th04/maine.exe").read_bytes()); baseline_sites = [r.linear for r in baseline.relocations]
    if sum(a != b for a,b in zip(baseline_sites,target_sites)) != V478_MISMATCHES:
        raise ValueError("v478 ordered frontier drift")
    old_score = segment_bytes(source / "obj/th04/mainscv.obj", "SCORE_TEXT")
    if len(old_score) != 0x8C8 or digest(old_score[:PREFIX_SIZE]) != PREFIX_RAW_SHA:
        raise ValueError("v478 SCORE prefix identity drift")

    builds = {}
    for label in ("a", "b"):
        work = output / label / "source"; shutil.copytree(source, work, symlinks=True)
        split_score_owner(work)
        tcc(work, output, f"v480-score-prefix-{label}", "th04/scp3.cpp")
        tasm(work, output, f"v480-score-tail-{label}", "th04_maine_score_tail_v480.asm", "msct80.obj")
        prefix = segment_bytes(work / "obj/th04/scp3.obj", "SCORE_TEXT")
        tail = segment_bytes(work / "obj/th04/msct80.obj", "SCORE_TEXT")
        if len(prefix) != PREFIX_SIZE or digest(prefix) != PREFIX_RAW_SHA or prefix != old_score[:PREFIX_SIZE]:
            raise ValueError(f"{label}: natural SCORE prefix is not raw exact")
        if len(tail) != TAIL_SIZE:
            raise ValueError(f"{label}: SCORE tail size drift: {len(tail)}")
        kind3 = kind3_locations(work / "obj/th04/scp3.obj")
        if kind3 != EXPECTED_KIND3:
            raise ValueError(f"{label}: SCORE prefix kind-3 order drift: {kind3}")

        rsp = work / "obj/th04/maine.@l"; text = rsp.read_text()
        old = r"obj\th04\mainscv.obj"; new = r"obj\th04\scp3.obj obj\th04\msct80.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: SCORE owner response token drift")
        rsp.write_text(text.replace(old, new, 1))
        exe = work / "bin/th04/maine.exe"; mp = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"], work, output / f"v480-link-{label}.log")
        image = parse_mz(exe.read_bytes()); sites = [r.linear for r in image.relocations]; payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image:
            raise ValueError(f"{label}: SCORE prefix replacement changed linked program bytes")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation multiset drift")
        changed = [i for i,(a,b) in enumerate(zip(baseline_sites,sites)) if a != b]
        if changed != EXPECTED_CHANGED:
            raise ValueError(f"{label}: changed relocation indices drift: {changed}")
        if sites[311:316] != LOCAL_TARGET_SITES or target_sites[327:332] != LOCAL_TARGET_SITES:
            raise ValueError(f"{label}: natural local SCORE order drift")
        ordered = sum(a != b for a,b in zip(sites,target_sites))
        if ordered != EXPECTED_MISMATCHES:
            raise ValueError(f"{label}: ordered frontier drift: {ordered}")
        if sha(exe) != FINAL_EXE or sha(mp) != FINAL_MAP:
            raise ValueError(f"{label}: final identity drift")
        builds[label] = {
            "exe_sha256": sha(exe), "map_sha256": sha(mp), "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload, "prefix_raw_sha256": digest(prefix), "prefix_size": len(prefix),
            "tail_size": len(tail), "prefix_kind3_locations": kind3, "changed_indices_vs_v478": changed,
            "local_target_sites": sites[311:316], "ordered_relocation_mismatches": ordered,
            "same_index_relocations": len(sites)-ordered,
        }
    for key in ("exe_sha256","map_sha256","program_image_sha256","prefix_raw_sha256","prefix_size","tail_size","prefix_kind3_locations","changed_indices_vs_v478","local_target_sites","ordered_relocation_mismatches","same_index_relocations"):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B {key} differs")
    receipt = {
        "schema_version": 1, "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE first three SCORE_TEXT helpers natural-C++ raw/linked exact producer replay",
        "v478_source_exe_sha256": V478_EXE, "v478_source_map_sha256": V478_MAP,
        "target_restored_sha256": TARGET_RESTORED_SHA, "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA, "builds": builds,
        "observed_effect": "The leading SCORE_TEXT score-insertion, score renderer, and stage renderer helpers form one 0x2B3 / 691-byte raw-exact TC86 C++ owner. Replacing the TASM prefix preserves the complete MAINE program image and relocation-site multiset. TC86 naturally emits the five segment FIXUPPs in target-local high-address-first order: stage_put's two sites followed by score_put's three sites. Because higher-address SCORE helpers are still in the following TASM owner, these five sites remain at indices 311..315 rather than their target positions 327..331 and the global ordered residual stays 42. This establishes the correct natural producer direction for the growing SCORE_TEXT TU.",
        "limit": "The private helper names score_insert, score_put, and stage_put are descriptive replay names where target symbols are absent. Same-segment near externs bridge calls from the remaining TASM tail without changing linked bytes. Full SCORE relocation closure requires continuing the same TC86 owner through the higher-address helpers."
    }
    rp=output/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"candidate_sha256":FINAL_EXE,"score_prefix_raw_exact":True,"ordered_relocation_mismatches":EXPECTED_MISMATCHES},sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
