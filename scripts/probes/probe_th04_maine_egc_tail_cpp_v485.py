#!/usr/bin/env python3
"""Recover TH04 MAINE SCORE_TEXT EGC start + rectangle copy as one natural TC86 tail."""
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
from probe_th04_maine_score_insert_cpp_v479 import validate_v478_source  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import FINAL_EXE as V478_EXE, EXPECTED_MISMATCHES as V478_MISMATCHES, segment_bytes  # noqa: E402
from probe_th04_master_object_split import compare, sha  # noqa: E402
from probe_th04_maine_score_rect_cpp_v484 import raw_segment_bytes  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_egc_tail_v485.cpp.in"
TEMPLATE_SHA = "c840baaaed7b5073fcd9506061976d978f81421f77917f848c52ae56ccc52e63"
FINAL_EXE = V478_EXE
FINAL_MAP = "5c882d63dfe20686e566a9fd3def7b4a4c5b914d4d1108b3dfd227c0da00c682"
TAIL_LOAD = 0xCBB0
TAIL_SIZE = 0x00C9
TAIL_RAW_SHA = "6b55b254101a12f91c53798f8e8838896de7b12b7591b4d9368f3bdd5a0d314d"
TAIL_LINKED_SHA = "c97000dbc25f0ea6e58724b0f3b32739ec66e5bb9d181b687433c4a0b8b988b9"
SCORE_HEAD_SIZE = 0x07FE
PAD_SIZE = 1
HEAD_RAW_DIFFS = [0x2F5, 0x2F6]
EXPECTED_MISMATCHES = 42


def split_score_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v485 template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/egct85.cpp")

    source = work / "th04_maine_score_v470.asm"
    text = source.read_bytes().decode("cp932")
    old_call = "\t\tcall\tsub_CBF3\r\n"
    if text.count(old_call) != 1:
        raise ValueError("score_rect_copy call anchor drift")
    text = text.replace(old_call, "\t\tcall\t@SCORE_RECT_COPY$QIIII\r\n", 1)

    seg = "SCORE_TEXT segment byte public 'CODE' use16"
    empty = seg + "\r\nSCORE_TEXT ends"
    repl = seg + "\r\n\textern @SCORE_RECT_COPY$QIIII:near\r\nSCORE_TEXT ends"
    if text.count(empty) != 1:
        raise ValueError("empty SCORE declaration drift")
    text = text.replace(empty, repl, 1)

    cut = text.index("_egc_start_copy_inlined\tproc near")
    head = text[:cut].rstrip("\r\n") + "\r\n\r\nSCORE_TEXT\tends\r\n\tend\r\n"
    (work / "th04_maine_score_head_v485.asm").write_bytes(head.encode("cp932"))

    pad = (
        "\t.386\r\n\t.model use16 large _TEXT\r\n\r\n"
        "SCORE_TEXT segment byte public 'CODE' use16\r\n"
        "\tdb 0\r\n"
        "SCORE_TEXT ends\r\n\tend\r\n"
    )
    (work / "th04_maine_score_pad_v485.asm").write_bytes(pad.encode("ascii"))


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

    baseline = parse_mz((source / "bin/th04/maine.exe").read_bytes())
    baseline_sites = [r.linear for r in baseline.relocations]
    target = parse_mz(target_path.read_bytes()); target_sites = [r.linear for r in target.relocations]
    if sum(a != b for a,b in zip(baseline_sites,target_sites)) != V478_MISMATCHES:
        raise ValueError("v478 ordered frontier drift")
    old_score = segment_bytes(source / "obj/th04/mainscv.obj", "SCORE_TEXT")
    old_head = old_score[:SCORE_HEAD_SIZE]
    old_tail = old_score[SCORE_HEAD_SIZE:SCORE_HEAD_SIZE + TAIL_SIZE]
    if len(old_tail) != TAIL_SIZE or digest(old_tail) != TAIL_RAW_SHA:
        raise ValueError("v478 EGC tail raw identity drift")
    target_tail = target.program_image[TAIL_LOAD:TAIL_LOAD + TAIL_SIZE]
    if digest(target_tail) != TAIL_LINKED_SHA:
        raise ValueError("target EGC tail linked identity drift")

    builds = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        split_score_owner(work)
        tcc(work, output, f"v485-egc-tail-{label}", "th04/egct85.cpp")
        tasm(work, output, f"v485-score-head-{label}", "th04_maine_score_head_v485.asm", "msch85.obj")
        tasm(work, output, f"v485-score-pad-{label}", "th04_maine_score_pad_v485.asm", "mscp85.obj")

        cpp = segment_bytes(work / "obj/th04/egct85.obj", "SCORE_TEXT")
        head = segment_bytes(work / "obj/th04/msch85.obj", "SCORE_TEXT")
        pad = raw_segment_bytes(work / "obj/th04/mscp85.obj", "SCORE_TEXT")
        if len(cpp) != TAIL_SIZE or digest(cpp) != TAIL_RAW_SHA or cpp != old_tail:
            raise ValueError(f"{label}: natural EGC tail raw CODE is not exact")
        if len(head) != SCORE_HEAD_SIZE:
            raise ValueError(f"{label}: SCORE head size drift")
        head_diffs = [i for i,(a,b) in enumerate(zip(head,old_head)) if a != b]
        if head_diffs != HEAD_RAW_DIFFS:
            raise ValueError(f"{label}: SCORE head fixup-addend drift: {head_diffs}")
        if pad != b"\x00":
            raise ValueError(f"{label}: SCORE pad drift")

        rsp = work / "obj/th04/maine.@l"; text = rsp.read_text()
        old = r"obj\th04\mainscv.obj"
        new = r"obj\th04\msch85.obj obj\th04\egct85.obj obj\th04\mscp85.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: response SCORE token drift")
        rsp.write_text(text.replace(old,new,1))

        exe = work / "bin/th04/maine.exe"; mp = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine",str(RUNNER),"-e","-x","tlink",r"@obj\th04\maine.@l"], work, output / f"v485-link-{label}.log")
        image = parse_mz(exe.read_bytes()); sites = [r.linear for r in image.relocations]; payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image:
            raise ValueError(f"{label}: program image changed")
        linked = image.program_image[TAIL_LOAD:TAIL_LOAD + TAIL_SIZE]
        if linked != target_tail:
            raise ValueError(f"{label}: linked EGC tail is not target exact")
        if sites != baseline_sites or Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation table changed")
        ordered = sum(a != b for a,b in zip(sites,target_sites))
        if ordered != EXPECTED_MISMATCHES:
            raise ValueError(f"{label}: ordered frontier drift: {ordered}")
        if sha(exe) != FINAL_EXE or sha(mp) != FINAL_MAP:
            raise ValueError(f"{label}: output identity drift")

        builds[label] = {
            "exe_sha256": sha(exe), "map_sha256": sha(mp), "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload, "tail_raw_sha256": digest(cpp), "tail_linked_sha256": digest(linked),
            "tail_size": len(cpp), "score_head_size": len(head), "score_head_raw_differences_vs_v478": head_diffs,
            "score_pad_size": len(pad), "relocation_table_unchanged_vs_v478": True,
            "ordered_relocation_mismatches": ordered, "same_index_relocations": len(sites)-ordered,
        }

    for key in ("exe_sha256","map_sha256","program_image_sha256","tail_raw_sha256","tail_linked_sha256","tail_size","score_head_size","score_head_raw_differences_vs_v478","score_pad_size","relocation_table_unchanged_vs_v478","ordered_relocation_mismatches","same_index_relocations"):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B {key} differs")

    receipt = {
        "schema_version": 1, "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE SCORE_TEXT complete EGC tail natural-C++ raw/linked exact replay",
        "v478_source_exe_sha256": sha(source / "bin/th04/maine.exe"), "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)), "template_sha256": TEMPLATE_SHA, "builds": builds,
        "observed_effect": (
            "The final 0xC9 bytes of SCORE_TEXT code are recovered as one natural TC86 C++ TU: the 0x43 EGC-start helper and the 0x86 rectangle-copy helper. Cross-game TH05 source independently supplies decomp.hpp::keep_0(0) for the EGC address-register zero write, preventing TC86 from shrinking MOV AX,0 to XOR AX,AX. The fused tail is raw CODE byte-exact, linked target-exact, and preserves the complete v478 MAINE program image and all 559 relocation entries byte-for-byte."
        ),
        "limit": (
            "The one-byte SCORE segment pad remains an explicit assembly contribution. The higher-address regist_menu C++ frontier still differs at one four-byte zero-test peephole and is not credited as exact."
        ),
    }
    rp = output / "receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"candidate_sha256":FINAL_EXE,"tail_raw_exact":True,"tail_linked_exact":True,"ordered_relocation_mismatches":EXPECTED_MISMATCHES},sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
