#!/usr/bin/env python3
"""Extend TH04 MAINE SCORE_TEXT natural TC86 prefix through name cursor rendering."""
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
from probe_th04_maine_score_insert_cpp_v479 import V478_EXE, V478_MAP, validate_v478_source  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import EXPECTED_MISMATCHES as V478_MISMATCHES, segment_bytes  # noqa: E402
from probe_th04_master_object_split import compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_score_prefix_v481.cpp.in"
TEMPLATE_SHA = "35f25c2e26cc8d62cb6e144570779b1f0981df2b5b2c3d2820005678f12c7af2"
FINAL_EXE = "291fddb8465436b92c148e4f1d467014a7eec402644e2c1f1382dcae8b305a62"
FINAL_MAP = "b8df6759e55b9315d6882b626bb3ca5e1e0d27f06b19789f12a421e2c54bcffa"
PREFIX_SIZE = 0x035F
PREFIX_RAW_SHA = "20e21f50d69da87e08ae964f400c547fdf1df7d4d1338126d8b14766b05d6e80"
PREFIX_LINKED_SHA = "37e3e6e243f8ec56c7be9f6420d1d70dac54db46e41a4afd409ac9f95ad59e40"
TAIL_SIZE = 0x0569
RAW_DIFFS = [0x2F5, 0x2F6]
EXPECTED_KIND3 = [0x355, 0x32E, 0x319, 0x2A9, 0x295, 0x224, 0x1FB, 0x1D3]
LOCAL_TARGET_SITES = [0xC709, 0xC6E2, 0xC6CD, 0xC65D, 0xC649, 0xC5D8, 0xC5AF, 0xC587]
EXPECTED_CHANGED = list(range(311, 319))
EXPECTED_MISMATCHES = 42


def kind3_locations(path: Path) -> list[int]:
    out: list[int] = []
    for rec in parse_omf(path.read_bytes()):
        if rec.record_type == 0x9C:
            out.extend(loc for kind, loc in fixup_locations(rec.data) if kind == 3)
    return out


def split_score_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v481 template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/scp4.cpp")

    source = work / "th04_maine_score_v470.asm"
    text = source.read_bytes().decode("cp932")
    seg = "SCORE_TEXT segment byte public 'CODE' use16"
    positions=[]; off=0
    while True:
        pos=text.find(seg,off)
        if pos < 0: break
        positions.append(pos); off=pos+1
    if len(positions) != 2:
        raise ValueError(f"SCORE segment occurrence drift: {positions}")
    real=positions[1]; end_marker="SCORE_TEXT\tends"; seg_end=text.index(end_marker,real)
    common=text[:real]; body=text[real+len(seg):seg_end]
    start=body.index("sub_C711\tproc near"); tail_body=body[start:]
    replacements={
        "\t\tcall\tsub_C3B2\r\n":"\t\tcall\t@score_insert$qv\r\n",
        "\t\tcall\tsub_C506\r\n":"\t\tcall\t@SCORE_PUT$QIUC\r\n",
        "\t\tcall\tsub_C5EC\r\n":"\t\tcall\t@STAGE_PUT$QIII\r\n",
        "\t\tcall\tsub_C665\r\n":"\t\tcall\t@NAME_CURSOR_PUT$QIUCUC\r\n",
    }
    for old,new in replacements.items():
        if old not in tail_body: raise ValueError(f"call anchor drift: {old!r}")
        tail_body=tail_body.replace(old,new)
    needle="sub_CBF3\tproc near\r\n"
    if tail_body.count(needle) != 1: raise ValueError("sub_CBF3 definition drift")
    tail_body=tail_body.replace(needle,"public @SCORE_RECT_COPY$QIIII\r\n@SCORE_RECT_COPY$QIIII label near\r\n"+needle,1)

    empty=seg+"\r\nSCORE_TEXT ends"
    replacement=(seg+"\r\n"
        "\textern @score_insert$qv:near\r\n"
        "\textern @SCORE_PUT$QIUC:near\r\n"
        "\textern @STAGE_PUT$QIII:near\r\n"
        "\textern @NAME_CURSOR_PUT$QIUCUC:near\r\n"
        "SCORE_TEXT ends")
    if common.count(empty) != 1: raise ValueError("empty SCORE declaration drift")
    common=common.replace(empty,replacement,1)
    assume=("\r\n\t\tassume cs:group_01\r\n"
            "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n")
    procdesc=("\t@HISCORE_SCOREDAT_LOAD_FOR$Q10PLAYCHAR_T procdesc pascal near \\\r\n"
              "\t\tplaychar:byte\r\n"
              "\t@hiscore_scoredat_save$qv procdesc near\r\n\r\n")
    (work/"th04_maine_score_tail_v481.asm").write_bytes((common+seg+assume+procdesc+tail_body+end_marker+"\r\n\tend\r\n").encode("cp932"))


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir",type=Path,required=True)
    ap.add_argument("--target-restored",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path)
    args=ap.parse_args(); source=args.source_dir.resolve(); target_path=args.target_restored.resolve(); output=output_dir(args.output_dir)
    if sha(RUNNER) != RUNNER_SHA: raise ValueError("runner identity drift")
    validate_v478_source(source)
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA: raise ValueError("target restore drift")
    target=parse_mz(target_path.read_bytes()); target_sites=[r.linear for r in target.relocations]
    baseline=parse_mz((source/"bin/th04/maine.exe").read_bytes()); baseline_sites=[r.linear for r in baseline.relocations]
    if sum(a!=b for a,b in zip(baseline_sites,target_sites)) != V478_MISMATCHES: raise ValueError("v478 frontier drift")
    old_score=segment_bytes(source/"obj/th04/mainscv.obj","SCORE_TEXT")
    target_linked=target.program_image[0xC3B2:0xC3B2+PREFIX_SIZE]
    if digest(target_linked) != PREFIX_LINKED_SHA: raise ValueError("target linked prefix drift")

    builds={}
    for label in ("a","b"):
        work=output/label/"source"; shutil.copytree(source,work,symlinks=True)
        split_score_owner(work)
        tcc(work,output,f"v481-score-prefix-{label}","th04/scp4.cpp")
        tasm(work,output,f"v481-score-tail-{label}","th04_maine_score_tail_v481.asm","msct81.obj")
        prefix=segment_bytes(work/"obj/th04/scp4.obj","SCORE_TEXT"); tail=segment_bytes(work/"obj/th04/msct81.obj","SCORE_TEXT")
        if len(prefix)!=PREFIX_SIZE or digest(prefix)!=PREFIX_RAW_SHA: raise ValueError(f"{label}: prefix raw identity drift")
        diffs=[i for i,(a,b) in enumerate(zip(prefix,old_score[:PREFIX_SIZE])) if a!=b]
        if diffs != RAW_DIFFS: raise ValueError(f"{label}: raw difference set drift: {diffs}")
        if len(tail)!=TAIL_SIZE: raise ValueError(f"{label}: tail size drift: {len(tail)}")
        kind3=kind3_locations(work/"obj/th04/scp4.obj")
        if kind3 != EXPECTED_KIND3: raise ValueError(f"{label}: kind3 order drift: {kind3}")
        rsp=work/"obj/th04/maine.@l"; text=rsp.read_text(); old=r"obj\th04\mainscv.obj"; new=r"obj\th04\scp4.obj obj\th04\msct81.obj"
        if text.count(old)!=1: raise ValueError(f"{label}: response owner token drift")
        rsp.write_text(text.replace(old,new,1))
        exe=work/"bin/th04/maine.exe"; mp=work/"obj/th04/maine.map"; exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine",str(RUNNER),"-e","-x","tlink",r"@obj\th04\maine.@l"],work,output/f"v481-link-{label}.log")
        image=parse_mz(exe.read_bytes()); sites=[r.linear for r in image.relocations]; payload=compare("th04-maine",work)
        if image.program_image != baseline.program_image: raise ValueError(f"{label}: linked program image drift")
        linked=image.program_image[0xC3B2:0xC3B2+PREFIX_SIZE]
        if linked != target_linked: raise ValueError(f"{label}: linked prefix not target exact")
        if Counter(sites)!=Counter(target_sites): raise ValueError(f"{label}: relocation multiset drift")
        changed=[i for i,(a,b) in enumerate(zip(baseline_sites,sites)) if a!=b]
        if changed != EXPECTED_CHANGED: raise ValueError(f"{label}: changed-index drift: {changed}")
        if sites[311:319] != LOCAL_TARGET_SITES or target_sites[324:332] != LOCAL_TARGET_SITES: raise ValueError(f"{label}: local target order drift")
        ordered=sum(a!=b for a,b in zip(sites,target_sites))
        if ordered != EXPECTED_MISMATCHES: raise ValueError(f"{label}: ordered frontier drift: {ordered}")
        if sha(exe)!=FINAL_EXE or sha(mp)!=FINAL_MAP: raise ValueError(f"{label}: output identity drift")
        builds[label]={"exe_sha256":sha(exe),"map_sha256":sha(mp),"program_image_sha256":digest(image.program_image),"payload_comparison":payload,
            "prefix_raw_sha256":digest(prefix),"prefix_linked_sha256":digest(linked),"prefix_size":len(prefix),"tail_size":len(tail),"raw_differences_vs_v478":diffs,
            "prefix_kind3_locations":kind3,"changed_indices_vs_v478":changed,"local_target_sites":sites[311:319],"ordered_relocation_mismatches":ordered,"same_index_relocations":len(sites)-ordered}
    for key in ("exe_sha256","map_sha256","program_image_sha256","prefix_raw_sha256","prefix_linked_sha256","prefix_size","tail_size","raw_differences_vs_v478","prefix_kind3_locations","changed_indices_vs_v478","local_target_sites","ordered_relocation_mismatches","same_index_relocations"):
        if builds["a"][key] != builds["b"][key]: raise ValueError(f"A/B {key} differs")
    receipt={"schema_version":1,"observed_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"claim_scope":"TH04 MAINE first four SCORE_TEXT helpers natural-C++ producer replay","v478_source_exe_sha256":V478_EXE,"v478_source_map_sha256":V478_MAP,"target_restored_sha256":TARGET_RESTORED_SHA,"template":str(TEMPLATE.relative_to(ROOT)),"template_sha256":TEMPLATE_SHA,"builds":builds,
        "observed_effect":"The first four residual SCORE_TEXT helpers form one 0x35F / 863-byte natural TC86 C++ owner. All raw CODE bytes match the reconstructed TASM owner except the two-byte near-call displacement from the fourth helper to the still-later private copy helper; the split C++ object carries a zero addend plus same-segment FIXUPP, and TLINK resolves the complete linked 0x35F slice target-exact. TC86 emits eight segment FIXUPPs in target-local high-address-first order. The sites currently occupy candidate indices 311..318 but equal target indices 324..331; global residual stays 42 until higher-address SCORE helpers join the same C++ owner.",
        "limit":"The private helper names are descriptive replay names. The TASM tail provides a zero-byte near code alias for the existing sub_CBF3 address solely to bridge the source-level object split. No linked byte or address is changed."}
    rp=output/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"candidate_sha256":FINAL_EXE,"prefix_linked_exact":True,"ordered_relocation_mismatches":EXPECTED_MISMATCHES},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
