#!/usr/bin/env python3
"""Recover the complete TH04 MAINE SCORE_TEXT CODE body as one TC86 C++ TU.

This is a producer checkpoint, not packed-order promotion. It starts from the
retained v478 source snapshot, compiles the complete 0x8C7 SCORE_TEXT code body
from natural C++, keeps the original one-byte segment pad separate, exposes
existing SCORE strings through zero-byte C aliases, and relinks MAINE twice.
No executable, OMF, or relocation-table byte is patched.
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

from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_insert_cpp_v479 import validate_v478_source  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import EXPECTED_MISMATCHES as V478_MISMATCHES, segment_bytes  # noqa: E402
from probe_th04_master_object_split import compare, sha  # noqa: E402
from probe_th04_maine_score_rect_cpp_v484 import raw_segment_bytes  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_score_full_v486.cpp.in"
TEMPLATE_SHA = "3a855e207a2bc0d814ea9c94dc1c230a611c2876182eb661613c452f2696dc7a"
FINAL_EXE = "eba75be94f3e43776b5206a10ab3b9818eefc0308d9d87b7c148eca8f6b83397"
FINAL_MAP = "57286cfe662899fd1889c3caca5d7e0cb38f89072fc40d462ad3ad3a6b01eaac"
SCORE_LOAD = 0xC3B2
SCORE_CODE_SIZE = 0x08C7
SCORE_RAW_SHA = "99b6809c3ccac9d8f4257609132ec19fd0625fe12be0a95b54b1e6b5df718f17"
SCORE_LINKED_SHA = "491222d0f3c105e253ea4d6daf8546ec338b35ff9ad617abf76020bd60c2bda3"
PAD_SIZE = 1
EXPECTED_MISMATCHES = 44
EXPECTED_SAME = 515
EXPECTED_REMAINING = list(range(80, 88)) + list(range(311, 347))
EXPECTED_KIND3_RECORDS = [
    [0x3F5,0x3CF,0x3A6,0x355,0x32E,0x319,0x2A9,0x295,0x224,0x1FB,0x1D3],
    [0x3E4,0x3DD,0x3D8,0x3D3,0x3C1,0x3BA,0x245,0x23B,0x22F,0x209,0x1CA,0x1C3,0x1BC,0x1B0,0x153,0x142,0x0B5,0x0AC,0x0A5,0x097,0x08D,0x086,0x075,0x058],
    [0x0BD],
]
EXPECTED_SCORE_OFFSETS = [
    0x3F7,0x3D1,0x3A8,0x357,0x330,0x31B,0x2AB,0x297,0x226,0x1FD,0x1D5,
    0x7E6,0x7DF,0x7DA,0x7D5,0x7C3,0x7BC,0x647,0x63D,0x631,0x60B,0x5CC,0x5C5,0x5BE,0x5B2,
    0x555,0x544,0x4B7,0x4AE,0x4A7,0x499,0x48F,0x488,0x477,0x45A,
    0x8BF,
]
TARGET_SCORE_OFFSETS = [
    0x555,0x544,0x4B7,0x4AE,0x4A7,0x499,0x48F,0x488,0x477,0x45A,
    0x3F7,0x3D1,0x3A8,0x357,0x330,0x31B,0x2AB,0x297,0x226,0x1FD,0x1D5,
    0x8BF,
    0x7E6,0x7DF,0x7DA,0x7D5,0x7C3,0x7BC,0x647,0x63D,0x631,0x60B,0x5CC,0x5C5,0x5BE,0x5B2,
]
ALIASES = [
    ("aHi01_pi", "_aHi01_pi"),
    ("aScnum2_bft", "_aScnum2_bft"),
    ("aGxgnbGvbGhvVGv", "_aGxgnbGvbGhvVGv"),
    ("aGxgnbGvbGhvV_1", "_aGxgnbGvbGhvV_1"),
    ("aName", "_aName"),
]


def kind3_records(path: Path) -> list[list[int]]:
    out: list[list[int]] = []
    for rec in parse_omf(path.read_bytes()):
        if rec.record_type != 0x9C:
            continue
        locs = [loc for kind,loc in fixup_locations(rec.data) if kind == 3]
        if locs:
            out.append(locs)
    return out


def add_score_aliases(work: Path) -> None:
    path = work / "th04_maine_rest_v470.asm"
    text = path.read_bytes().decode("cp932")
    lines = text.split("\r\n")
    public_i = next(i for i,line in enumerate(lines) if line.startswith("public aSff1_pi"))
    for _, alias in ALIASES:
        if alias not in lines[public_i].split(", "):
            lines[public_i] += ", " + alias
    for original, alias in ALIASES:
        matches = [i for i,line in enumerate(lines) if line.startswith(original) and ("\tdb " in line or "\t\tdb " in line)]
        if len(matches) != 1:
            raise ValueError(f"SCORE data label drift for {original}: {matches}")
        i = matches[0]
        if i == 0 or lines[i-1] != f"{alias} label byte":
            lines.insert(i, f"{alias} label byte")
    path.write_bytes("\r\n".join(lines).encode("cp932"))


def add_pad(work: Path) -> None:
    pad = (
        "\t.386\r\n\t.model use16 large _TEXT\r\n\r\n"
        "SCORE_TEXT segment byte public 'CODE' use16\r\n"
        "\tdb 0\r\n"
        "SCORE_TEXT ends\r\n\tend\r\n"
    )
    (work / "th04_maine_score_pad_v486.asm").write_bytes(pad.encode("ascii"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source=args.source_dir.resolve(); target_path=args.target_restored.resolve(); output=output_dir(args.output_dir)
    if sha(RUNNER) != RUNNER_SHA:
        raise ValueError("runner identity drift")
    validate_v478_source(source)
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("target restore identity drift")
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v486 template identity drift")

    baseline=parse_mz((source/"bin/th04/maine.exe").read_bytes()); baseline_sites=[r.linear for r in baseline.relocations]
    target=parse_mz(target_path.read_bytes()); target_sites=[r.linear for r in target.relocations]
    if sum(a!=b for a,b in zip(baseline_sites,target_sites)) != V478_MISMATCHES:
        raise ValueError("v478 ordered frontier drift")
    target_score=target.program_image[SCORE_LOAD:SCORE_LOAD+SCORE_CODE_SIZE]
    if digest(target_score) != SCORE_LINKED_SHA:
        raise ValueError("target SCORE linked identity drift")
    target_score_sites=[x for x in target_sites if SCORE_LOAD <= x < SCORE_LOAD+SCORE_CODE_SIZE]
    if [x-SCORE_LOAD for x in target_score_sites] != TARGET_SCORE_OFFSETS:
        raise ValueError("target SCORE relocation projection drift")

    builds={}
    for label in ("a","b"):
        work=output/label/"source"; shutil.copytree(source,work,symlinks=True)
        shutil.copy2(TEMPLATE,work/"th04/score86.cpp")
        add_score_aliases(work); add_pad(work)
        tcc(work,output,f"v486-score-{label}","th04/score86.cpp")
        tasm(work,output,f"v486-rest-{label}","th04_maine_rest_v470.asm","mainerest.obj")
        tasm(work,output,f"v486-pad-{label}","th04_maine_score_pad_v486.asm","mscp86.obj")

        obj=work/"obj/th04/score86.obj"; code=segment_bytes(obj,"SCORE_TEXT")
        pad=raw_segment_bytes(work/"obj/th04/mscp86.obj","SCORE_TEXT")
        if len(code)!=SCORE_CODE_SIZE or digest(code)!=SCORE_RAW_SHA:
            raise ValueError(f"{label}: full SCORE raw CODE identity drift")
        if pad != b"\x00":
            raise ValueError(f"{label}: SCORE pad drift")
        records=kind3_records(obj)
        if records != EXPECTED_KIND3_RECORDS:
            raise ValueError(f"{label}: SCORE FIXUPP record topology drift: {records}")

        rsp=work/"obj/th04/maine.@l"; text=rsp.read_text(); old=r"obj\th04\mainscv.obj"; new=r"obj\th04\score86.obj obj\th04\mscp86.obj"
        if text.count(old)!=1:
            raise ValueError(f"{label}: SCORE response token drift")
        rsp.write_text(text.replace(old,new,1))
        exe=work/"bin/th04/maine.exe"; mp=work/"obj/th04/maine.map"; exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine",str(RUNNER),"-e","-x","tlink",r"@obj\th04\maine.@l"],work,output/f"v486-link-{label}.log")
        image=parse_mz(exe.read_bytes()); sites=[r.linear for r in image.relocations]; payload=compare("th04-maine",work)
        if image.program_image != baseline.program_image:
            raise ValueError(f"{label}: full SCORE replacement changed linked program bytes")
        linked=image.program_image[SCORE_LOAD:SCORE_LOAD+SCORE_CODE_SIZE]
        if linked != target_score:
            raise ValueError(f"{label}: linked SCORE code not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation multiset drift")
        score_sites=[x for x in sites if SCORE_LOAD <= x < SCORE_LOAD+SCORE_CODE_SIZE]
        score_offsets=[x-SCORE_LOAD for x in score_sites]
        if score_offsets != EXPECTED_SCORE_OFFSETS:
            raise ValueError(f"{label}: candidate SCORE relocation order drift: {score_offsets}")
        ordered=sum(a!=b for a,b in zip(sites,target_sites)); remaining=[i for i,(a,b) in enumerate(zip(sites,target_sites)) if a!=b]
        if ordered != EXPECTED_MISMATCHES or remaining != EXPECTED_REMAINING:
            raise ValueError(f"{label}: v486 packed frontier drift: {ordered}, {remaining}")
        if sha(exe)!=FINAL_EXE or sha(mp)!=FINAL_MAP:
            raise ValueError(f"{label}: output identity drift")
        builds[label]={
            "exe_sha256":sha(exe),"map_sha256":sha(mp),"program_image_sha256":digest(image.program_image),"payload_comparison":payload,
            "score_raw_sha256":digest(code),"score_linked_sha256":digest(linked),"score_code_size":len(code),"score_pad_size":len(pad),
            "kind3_records":records,"score_relocation_offsets":score_offsets,"target_score_relocation_offsets":TARGET_SCORE_OFFSETS,
            "ordered_relocation_mismatches":ordered,"same_index_relocations":len(sites)-ordered,"remaining_mismatch_indices":remaining,
        }
    for key in ("exe_sha256","map_sha256","program_image_sha256","score_raw_sha256","score_linked_sha256","score_code_size","score_pad_size","kind3_records","score_relocation_offsets","target_score_relocation_offsets","ordered_relocation_mismatches","same_index_relocations","remaining_mismatch_indices"):
        if builds["a"][key]!=builds["b"][key]:
            raise ValueError(f"A/B {key} differs")
    receipt={
        "schema_version":1,"observed_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope":"TH04 MAINE complete SCORE_TEXT natural-C++ code producer; explicitly no packed-order credit",
        "v478_source_exe_sha256":sha(source/"bin/th04/maine.exe"),"target_restored_sha256":TARGET_RESTORED_SHA,
        "template":str(TEMPLATE.relative_to(ROOT)),"template_sha256":TEMPLATE_SHA,"builds":builds,
        "observed_effect":(
            "All 0x8C7 bytes of MAINE SCORE_TEXT executable code, from the registration score insertion helper through regist_menu and the EGC rectangle-copy tail, now compile byte-for-byte from one TC86 C++ translation unit. optimization_barrier() supplies the target regist_menu CMP/JZ/JMP shape and keep_0(0) supplies the target EGC MOV AX,0 form; both are repository-supported compiler-shape mechanisms, with keep_0 independently used by TH05 for the same EGC register. The linked program image remains byte-identical and the 559-site relocation multiset remains exact."
        ),
        "record_frontier":(
            "The full C++ object emits three target-relevant kind-3 FIXUPP records. Its SCORE relocation order is R1(11), R2-prefix(14), R2-suffix(10), R3(1), while the packed target requires R2-suffix(10), R1(11), R3(1), R2-prefix(14). Consequently the temporary full-owner link has 44 ordered mismatches (36 SCORE + 8 BGIMAGE), compared with v478's 42. Response-position and -y metadata probes leave the 36-site relative SCORE order unchanged."
        ),
        "limit":"This packet grants source/compiler producer evidence only. It deliberately does not promote packed relocation order or exactness; historical OMF/library record topology remains unresolved. No relocation entry is patched or permuted.",
    }
    rp=output/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"score_raw_exact":True,"score_linked_exact":True,"ordered_relocation_mismatches":EXPECTED_MISMATCHES,"packed_credit":False},sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
