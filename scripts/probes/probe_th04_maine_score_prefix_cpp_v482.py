#!/usr/bin/env python3
"""Extend TH04 MAINE SCORE_TEXT natural TC86 prefix through row/cursor helpers."""
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
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_score_prefix_v482.cpp.in"
TEMPLATE_SHA = "832dd1eeaf057efeb01e8438677ad80ba642919c2e045c0ee5d1469a45b9b3ed"
FINAL_EXE = "2dac1a8a1cf6ee10d41946c82933112e496cd19f3df354fed11cbc49e50f597b"
FINAL_MAP = "a3cc85e0d705a96c539f71ba0803d062bf035f9b886004eb2d6c5604ea869c64"
PREFIX_SIZE = 0x0462
PREFIX_RAW_SHA = "836b450754b7c9a7db562235d2858e77afe7c369594db3614749dde81afd81da"
PREFIX_LINKED_SHA = "11bc4d06b392a9ce4ad9b71f791e3f6ff5ca859f041f68c15809718773b7e49a"
TAIL_SIZE = 0x0466
RAW_DIFFS = [0x2F5, 0x2F6]
EXPECTED_KIND3 = [0x3F5,0x3CF,0x3A6,0x355,0x32E,0x319,0x2A9,0x295,0x224,0x1FB,0x1D3,0x58]
EXPECTED_CHANGED = [311,312,313,314,315,317,318,319,320,321]
EXPECTED_MISMATCHES = 43
PREFIX_SITES = [0xC7A9,0xC783,0xC75A,0xC709,0xC6E2,0xC6CD,0xC65D,0xC649,0xC5D8,0xC5AF,0xC587,0xC80C]
TARGET_INDICES = [321,322,323,324,325,326,327,328,329,330,331,320]


def kind3_locations(path: Path) -> list[int]:
    out=[]
    for rec in parse_omf(path.read_bytes()):
        if rec.record_type == 0x9C:
            out.extend(loc for kind,loc in fixup_locations(rec.data) if kind==3)
    return out


def split_score_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA: raise ValueError("v482 template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/scp7.cpp")
    text=(work/"th04_maine_score_v470.asm").read_bytes().decode("cp932")
    seg="SCORE_TEXT segment byte public 'CODE' use16"; pos=[]; off=0
    while True:
        i=text.find(seg,off)
        if i<0: break
        pos.append(i); off=i+1
    if len(pos)!=2: raise ValueError(f"SCORE segment occurrence drift: {pos}")
    real=pos[1]; end_marker="SCORE_TEXT\tends"; seg_end=text.index(end_marker,real)
    common=text[:real]; body=text[real+len(seg):seg_end]
    start=body.index("@regist_menu$qv proc near"); tail_body=body[start:]
    repls={
        "\t\tcall\tsub_C3B2\r\n":"\t\tcall\t@score_insert$qv\r\n",
        "\t\tcall\tsub_C7C9\r\n":"\t\tcall\t@PLACES_PUT$QUC\r\n",
        "\t\tcall\tsub_C7E3\r\n":"\t\tcall\t@ALPHABET_CURSOR_PUT$QIII\r\n",
        "\t\tcall\tsub_C665\r\n":"\t\tcall\t@NAME_CURSOR_PUT$QIUCUC\r\n",
    }
    for old,new in repls.items():
        if old not in tail_body: raise ValueError(f"call anchor drift: {old!r}")
        tail_body=tail_body.replace(old,new)
    needle="sub_CBF3\tproc near\r\n"
    if tail_body.count(needle)!=1: raise ValueError("copy helper drift")
    tail_body=tail_body.replace(needle,"public @SCORE_RECT_COPY$QIIII\r\n@SCORE_RECT_COPY$QIIII label near\r\n"+needle,1)
    empty=seg+"\r\nSCORE_TEXT ends"
    ext=(seg+"\r\n"
         "\textern @score_insert$qv:near\r\n"
         "\textern @PLACES_PUT$QUC:near\r\n"
         "\textern @ALPHABET_CURSOR_PUT$QIII:near\r\n"
         "\textern @NAME_CURSOR_PUT$QIUCUC:near\r\n"
         "SCORE_TEXT ends")
    if common.count(empty)!=1: raise ValueError("empty SCORE declaration drift")
    common=common.replace(empty,ext,1)
    assume=("\r\n\t\tassume cs:group_01\r\n\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n")
    procdesc=("\t@HISCORE_SCOREDAT_LOAD_FOR$Q10PLAYCHAR_T procdesc pascal near \\\r\n\t\tplaychar:byte\r\n"
              "\t@hiscore_scoredat_save$qv procdesc near\r\n\r\ninclude th02/hiscore/regist.inc\r\n\r\npublic @regist_menu$qv\r\n")
    tail_body=tail_body.replace("@regist_menu$qv proc near",procdesc+"@regist_menu$qv proc near",1)
    (work/"th04_maine_score_tail_v482.asm").write_bytes((common+seg+assume+tail_body+end_marker+"\r\n\tend\r\n").encode("cp932"))


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir",type=Path,required=True); ap.add_argument("--target-restored",type=Path,required=True); ap.add_argument("--output-dir",type=Path)
    args=ap.parse_args(); source=args.source_dir.resolve(); target_path=args.target_restored.resolve(); output=output_dir(args.output_dir)
    if sha(RUNNER)!=RUNNER_SHA: raise ValueError("runner drift")
    validate_v478_source(source)
    if not target_path.is_file() or sha(target_path)!=TARGET_RESTORED_SHA: raise ValueError("target drift")
    target=parse_mz(target_path.read_bytes()); target_sites=[r.linear for r in target.relocations]
    baseline=parse_mz((source/"bin/th04/maine.exe").read_bytes()); baseline_sites=[r.linear for r in baseline.relocations]
    if sum(a!=b for a,b in zip(baseline_sites,target_sites))!=V478_MISMATCHES: raise ValueError("v478 frontier drift")
    old=segment_bytes(source/"obj/th04/mainscv.obj","SCORE_TEXT")
    target_linked=target.program_image[0xC3B2:0xC3B2+PREFIX_SIZE]
    if digest(target_linked)!=PREFIX_LINKED_SHA: raise ValueError("target linked prefix drift")
    builds={}
    for label in ("a","b"):
        work=output/label/"source"; shutil.copytree(source,work,symlinks=True); split_score_owner(work)
        tcc(work,output,f"v482-prefix-{label}","th04/scp7.cpp"); tasm(work,output,f"v482-tail-{label}","th04_maine_score_tail_v482.asm","msct82.obj")
        prefix=segment_bytes(work/"obj/th04/scp7.obj","SCORE_TEXT"); tail=segment_bytes(work/"obj/th04/msct82.obj","SCORE_TEXT")
        if len(prefix)!=PREFIX_SIZE or digest(prefix)!=PREFIX_RAW_SHA: raise ValueError(f"{label}: prefix identity drift")
        diffs=[i for i,(a,b) in enumerate(zip(prefix,old[:PREFIX_SIZE])) if a!=b]
        if diffs!=RAW_DIFFS: raise ValueError(f"{label}: raw diff drift: {diffs}")
        if len(tail)!=TAIL_SIZE: raise ValueError(f"{label}: tail size drift")
        kind3=kind3_locations(work/"obj/th04/scp7.obj")
        if kind3!=EXPECTED_KIND3: raise ValueError(f"{label}: kind3 drift: {kind3}")
        rsp=work/"obj/th04/maine.@l"; text=rsp.read_text(); oldtok=r"obj\th04\mainscv.obj"; newtok=r"obj\th04\scp7.obj obj\th04\msct82.obj"
        if text.count(oldtok)!=1: raise ValueError(f"{label}: response token drift")
        rsp.write_text(text.replace(oldtok,newtok,1))
        exe=work/"bin/th04/maine.exe"; mp=work/"obj/th04/maine.map"; exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine",str(RUNNER),"-e","-x","tlink",r"@obj\th04\maine.@l"],work,output/f"v482-link-{label}.log")
        image=parse_mz(exe.read_bytes()); sites=[r.linear for r in image.relocations]; payload=compare("th04-maine",work)
        if image.program_image!=baseline.program_image: raise ValueError(f"{label}: program image drift")
        linked=image.program_image[0xC3B2:0xC3B2+PREFIX_SIZE]
        if linked!=target_linked: raise ValueError(f"{label}: linked prefix not target exact")
        if Counter(sites)!=Counter(target_sites): raise ValueError(f"{label}: multiset drift")
        changed=[i for i,(a,b) in enumerate(zip(baseline_sites,sites)) if a!=b]
        if changed!=EXPECTED_CHANGED: raise ValueError(f"{label}: changed-index drift: {changed}")
        ordered=sum(a!=b for a,b in zip(sites,target_sites))
        if ordered!=EXPECTED_MISMATCHES: raise ValueError(f"{label}: residual drift: {ordered}")
        if sha(exe)!=FINAL_EXE or sha(mp)!=FINAL_MAP: raise ValueError(f"{label}: output identity drift")
        # Source-owner sites must map to the expected target positions even while the tail is separate.
        cand_sites=sites[311:323]
        if cand_sites!=PREFIX_SITES: raise ValueError(f"{label}: prefix site sequence drift")
        if [target_sites[i] for i in TARGET_INDICES]!=PREFIX_SITES: raise ValueError(f"{label}: target-local projection drift")
        builds[label]={"exe_sha256":sha(exe),"map_sha256":sha(mp),"program_image_sha256":digest(image.program_image),"payload_comparison":payload,
            "prefix_raw_sha256":digest(prefix),"prefix_linked_sha256":digest(linked),"prefix_size":len(prefix),"tail_size":len(tail),"raw_differences_vs_v478":diffs,
            "prefix_kind3_locations":kind3,"changed_indices_vs_v478":changed,"prefix_sites":cand_sites,"target_indices_for_prefix_sites":TARGET_INDICES,
            "ordered_relocation_mismatches":ordered,"same_index_relocations":len(sites)-ordered}
    for key in ("exe_sha256","map_sha256","program_image_sha256","prefix_raw_sha256","prefix_linked_sha256","prefix_size","tail_size","raw_differences_vs_v478","prefix_kind3_locations","changed_indices_vs_v478","prefix_sites","target_indices_for_prefix_sites","ordered_relocation_mismatches","same_index_relocations"):
        if builds["a"][key]!=builds["b"][key]: raise ValueError(f"A/B {key} differs")
    receipt={"schema_version":1,"observed_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"claim_scope":"TH04 MAINE first seven SCORE_TEXT helpers natural-C++ producer checkpoint","v478_source_exe_sha256":sha(source/"bin/th04/maine.exe"),"target_restored_sha256":TARGET_RESTORED_SHA,"template":str(TEMPLATE.relative_to(ROOT)),"template_sha256":TEMPLATE_SHA,"builds":builds,
        "observed_effect":"The v481 SCORE_TEXT C++ prefix is extended by three more adjacent helpers: place_row_put (0xB8), places_put (0x1A), and alphabet_cursor_put (0x31). All three are raw CODE exact, growing the natural TC86 prefix to 0x462 bytes. The complete linked MAINE program image remains byte-identical and the 559-site relocation multiset remains exact. The partial split temporarily raises ordered mismatch 42 to 43 because the higher-address regist_menu/EGC TASM tail is still a later object; nevertheless all 12 C++ prefix segment sites map exactly to target-local indices 320..331, exposing the final one-TU ordering mechanism.",
        "limit":"This is a producer checkpoint, not packed-frontier promotion. The replay deliberately does not claim the temporary 43-entry split as an improvement. Continue by recovering regist_menu and the EGC tail into the same TC86 SCORE_TEXT owner; do not permute MZ entries."}
    rp=output/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"candidate_sha256":FINAL_EXE,"prefix_linked_exact":True,"ordered_relocation_mismatches":EXPECTED_MISMATCHES},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
