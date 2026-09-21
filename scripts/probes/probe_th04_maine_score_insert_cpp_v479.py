#!/usr/bin/env python3
"""Recover TH04 MAINE SCORE_TEXT score insertion helper as natural TC86 C++.

This targeted replay starts from the retained v478 source snapshot, whose
EXE/MAP and SCORE owner identities are checked first. It then performs two
independent source copies, recompiles only the new C++ prefix and TASM tail,
and relinks MAINE. No executable, OMF, or relocation bytes are patched.
"""
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
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked,
)
from probe_th04_maine_segment_topology_v470 import output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import (  # noqa: E402
    FINAL_EXE as V478_EXE,
    FINAL_MAP as V478_MAP,
    EXPECTED_MISMATCHES as V478_MISMATCHES,
    segment_bytes,
)
from probe_th04_master_object_split import compare, sha  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_score_insert_v479.cpp.in"
TEMPLATE_SHA = "22595fcb2b887a0196fdb7fd7f2428bc30d1ea2d441310d5874b2039c7a5041d"
FINAL_EXE = V478_EXE
FINAL_MAP = "8bef805e5d3d83081860375d50b5120d978da1486aa632741d14b51f1dc21a2a"
FUNCTION_LOAD = 0xC3B2
FUNCTION_SIZE = 0x0154
FUNCTION_RAW_SHA = "978e0eb303d2875ed00983f0ea3fc9d48136949afbcd677190a7447eeba2d09c"
FUNCTION_LINKED_SHA = "ed7880a5a1cd7aa721c2a95bafb819da15768fd660cf6dd96dbccc9fdc30c093"
SCORE_OWNER_SIZE = 0x08C8
SCORE_TAIL_SIZE = 0x0774
EXPECTED_MISMATCHES = 42


def validate_v478_source(source: Path) -> None:
    exe = source / "bin/th04/maine.exe"
    mp = source / "obj/th04/maine.map"
    score = source / "obj/th04/mainscv.obj"
    if not exe.is_file() or sha(exe) != V478_EXE:
        raise ValueError("v478 source EXE identity drift")
    if not mp.is_file() or sha(mp) != V478_MAP:
        raise ValueError("v478 source MAP identity drift")
    raw = segment_bytes(score, "SCORE_TEXT")
    if len(raw) != SCORE_OWNER_SIZE or digest(raw[:FUNCTION_SIZE]) != FUNCTION_RAW_SHA:
        raise ValueError("v478 SCORE owner identity drift")
    rsp = (source / "obj/th04/maine.@l").read_text()
    if rsp.count(r"obj\th04\mainscv.obj") != 1:
        raise ValueError("v478 response SCORE owner token drift")


def split_score_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v479 score template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/scins.cpp")

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
    start = body.index("sub_C506\tproc near")
    tail_body = body[start:]
    old_call = "\t\tcall\tsub_C3B2\r\n"
    if tail_body.count(old_call) != 1:
        raise ValueError("score insertion call anchor drift")
    tail_body = tail_body.replace(old_call, "\t\tcall\t@score_insert$qv\r\n", 1)

    empty = seg + "\r\nSCORE_TEXT ends"
    replacement = seg + "\r\n\textern @score_insert$qv:near\r\nSCORE_TEXT ends"
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
    (work / "th04_maine_score_tail_v479.asm").write_bytes(tail.encode("cp932"))


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
    target_function = target.program_image[FUNCTION_LOAD:FUNCTION_LOAD + FUNCTION_SIZE]
    if digest(target_function) != FUNCTION_LINKED_SHA:
        raise ValueError("target function identity drift")

    baseline = parse_mz((source / "bin/th04/maine.exe").read_bytes())
    baseline_sites = [r.linear for r in baseline.relocations]
    if sum(a != b for a,b in zip(baseline_sites,target_sites)) != V478_MISMATCHES:
        raise ValueError("v478 ordered frontier drift")
    old_score = segment_bytes(source / "obj/th04/mainscv.obj", "SCORE_TEXT")

    builds = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        split_score_owner(work)
        tcc(work, output, f"v479-score-insert-{label}", "th04/scins.cpp")
        tasm(work, output, f"v479-score-tail-{label}", "th04_maine_score_tail_v479.asm", "msct79.obj")
        cpp = segment_bytes(work / "obj/th04/scins.obj", "SCORE_TEXT")
        tail = segment_bytes(work / "obj/th04/msct79.obj", "SCORE_TEXT")
        if len(cpp) != FUNCTION_SIZE or digest(cpp) != FUNCTION_RAW_SHA or cpp != old_score[:FUNCTION_SIZE]:
            raise ValueError(f"{label}: natural score insertion raw CODE is not exact")
        if len(tail) != SCORE_TAIL_SIZE:
            raise ValueError(f"{label}: score tail size drift: {len(tail)}")

        rsp = work / "obj/th04/maine.@l"
        text = rsp.read_text(); old = r"obj\th04\mainscv.obj"; new = r"obj\th04\scins.obj obj\th04\msct79.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: response owner token drift")
        rsp.write_text(text.replace(old, new, 1))
        exe = work / "bin/th04/maine.exe"; mp = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"], work, output / f"v479-link-{label}.log")
        image = parse_mz(exe.read_bytes()); sites = [r.linear for r in image.relocations]; payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image:
            raise ValueError(f"{label}: replacement changed linked program bytes")
        linked = image.program_image[FUNCTION_LOAD:FUNCTION_LOAD + FUNCTION_SIZE]
        if linked != target_function:
            raise ValueError(f"{label}: linked function is not target exact")
        if sites != baseline_sites or Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: replacement changed relocation table")
        ordered = sum(a != b for a,b in zip(sites,target_sites))
        if ordered != EXPECTED_MISMATCHES:
            raise ValueError(f"{label}: residual drift: {ordered}")
        if sha(exe) != FINAL_EXE or sha(mp) != FINAL_MAP:
            raise ValueError(f"{label}: output identity drift")
        builds[label] = {
            "exe_sha256": sha(exe), "map_sha256": sha(mp), "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload, "function_raw_sha256": digest(cpp), "function_linked_sha256": digest(linked),
            "function_size": len(cpp), "tail_size": len(tail), "relocation_table_unchanged_vs_v478": True,
            "ordered_relocation_mismatches": ordered, "same_index_relocations": len(sites)-ordered,
        }
    for key in ("exe_sha256","map_sha256","program_image_sha256","function_raw_sha256","function_linked_sha256","function_size","tail_size","relocation_table_unchanged_vs_v478","ordered_relocation_mismatches","same_index_relocations"):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B {key} differs")
    receipt = {
        "schema_version": 1, "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE SCORE_TEXT score insertion helper natural-C++ raw/linked exact replay",
        "v478_source_exe_sha256": V478_EXE, "v478_source_map_sha256": V478_MAP,
        "target_restored_sha256": TARGET_RESTORED_SHA, "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA, "builds": builds,
        "observed_effect": "A direct TC86 C++ reconstruction of the leading 0x154-byte SCORE_TEXT score-insertion helper is raw CODE exact and linked target-exact. Splitting only that function from the retained v478 TASM SCORE owner preserves the complete MAINE program image and every one of the 559 relocation entries byte-for-byte, so the ordered residual remains 42. This is positive natural-C++ producer evidence for the remaining SCORE_TEXT owner even though the helper itself contributes only data-offset fixups.",
        "limit": "The helper's historical symbol name is not target-attested; score_insert is a descriptive replay name. The tail calls it through a source-level near external only to preserve the original call boundary. No executable, data, or relocation byte is patched."
    }
    rp=output/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"candidate_sha256":FINAL_EXE,"function_linked_exact":True,"ordered_relocation_mismatches":EXPECTED_MISMATCHES},sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
