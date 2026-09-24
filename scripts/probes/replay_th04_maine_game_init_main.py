#!/usr/bin/env python3
"""Cold-compile maintained MAINE game_init_main and verify TLINK same-segment call optimization."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import describe_omf, parse_omf
from lib.pc98 import parse_mz
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from probe_th04_maine_segment_topology_v470 import tcc
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_scroll_driver_natural import fixup_locations
from replay_th04_shared_delay_measure import link_relevant_omf_sha
from replay_th04_zun_source_only import source_closure

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/shared/core/game_init_main.cpp"

TARGET_SHA = "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533"
BASE_EXE_SHA = "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c"
BASE_MAP_SHA = "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e"
BASE_WRAPPER_SHA = "6a82b4086cdd59252b618c5ac8fd9a585f4f3e01bd86296ceb0dbf1857e1cf3e"
BASE_OBJECT_SHA = "cbf7132c806eb541d49c6a4efc8b08cdbb00c5e986b40a9caa43c694fde9ca5a"
BASE_LINK_OMF_SHA = "4b8c373afdeab9563f3592b5a92358a7110967c7c6b07f1ef155f6fc12e652ec"
BASE_CODE_SHA = "2a94edb08551dcb5ba1d390672e54f33604d1cb51fed97735cdac21c230e8fb0"
STANDALONE_CODE_SHA = "e3faaf7c275e1ad6bb0742b68c9e473873d958406d30ff2f1970bc1d2ca87447"
STANDALONE_FIXUPS = [(3,67),(3,59),(3,50),(3,45),(3,40),(3,35),(3,30),(1,25),(3,8),(1,5)]
RELOCATIONS = 559

START = 0xD43C
SIZE = 0x4D
NEXT = START + SIZE
PRODUCER_SIZE = 0x4E
TARGET_FUNCTION_SHA = "71bcdbd68d5d111fa0fbb90d8196b5ebaffda59eddd1e9ef071db0239fa86133"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha_file(path: Path) -> str:
    return sha(path.read_bytes())

def object_fixups(obj: Path) -> list[tuple[int,int]]:
    return [item for rec in parse_omf(obj.read_bytes()) if rec.record_type == 0x9C
            for item in fixup_locations(rec.data)]

def map_contribution(path: Path) -> tuple[int,int,str]:
    pat = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=SHARED\b.*\bM=th04/initmain\.cpp(?:\s|$)", re.I)
    matches=[]
    for line in path.read_text(encoding="cp437").splitlines():
        m=pat.search(line)
        if m:
            matches.append((int(m[1],16)*16+int(m[2],16),int(m[3],16),line.strip()))
    if len(matches)!=1:
        raise RuntimeError(f"expected one initmain MAP contribution: {matches}")
    return matches[0]

def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body)!=SIZE or sha(body)!=TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE game_init_main target identity drift")
    p=ROOT/".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    rows=[r for r in csv.DictReader(p.open(newline="",encoding="utf-8"))
          if int(r["entry_linear"],0)==0x10000+START]
    if len(rows)!=1:
        raise RuntimeError("MAINE game_init_main Ghidra entry count drift")
    r=rows[0]
    if (int(r["entry_segment"],0)!=0x1CC7 or int(r["entry_offset"],0)!=0x07CC
        or int(r["body_min_linear"],0)!=0x10000+START
        or int(r["body_max_linear"],0)!=0x10000+NEXT-1
        or int(r["body_addresses"])!=SIZE or int(r["body_span"])!=SIZE
        or r["contiguous"]!="true" or r["body_range_count"]!="1"
        or int(r["caller_count"])!=1 or int(r["callee_count"])!=8):
        raise RuntimeError(f"MAINE game_init_main Ghidra extent drift: {r!r}")
    required=(
        "0CC7:07CC       game_init_main(const unsigned char far*)",
        "0E53:1B40       _mem_assign_paras",
        "0000:22E0       MEM_ASSIGN_DOS",
        "0E53:016A       _bbufsiz",
        "0000:2110       VSYNC_START",
        "0000:087C       EGC_START",
        "0000:113A       GRAPH_400LINE",
        "0000:2B6E       JS_START",
        "0000:2916       PFSTART",
        "0000:33D0       BGM_INIT",
    )
    if any(x not in map_text for x in required):
        raise RuntimeError("MAINE game_init_main MAP target drift")
    if (body[:3]!=bytes.fromhex("55 8b ec")
        or body[3:7]!=bytes.fromhex("ff 36 40 1b")
        or body[12:23]!=bytes.fromhex("0b c0 74 07 b8 01 00 5d ca 04 00")
        or body[23:29]!=bytes.fromhex("c7 06 6a 01 00 10")
        or body[29:34]!=bytes.fromhex("90 0e e8 1c f8")
        or body[54:58]!=bytes.fromhex("66 ff 76 06")
        or body[71:]!=bytes.fromhex("33 c0 5d ca 04 00")):
        raise RuntimeError("MAINE game_init_main target topology drift")
    return {
        "segment_identity":"1CC7","segment_offset":"07CC",
        "payload_offset":hex(START),"size":SIZE,"target_sha256":sha(body),
        "caller_count":1,"callee_count":8,
        "same_segment_call":"vram_planes_set via TLINK NOP/PUSH CS/CALL rel16",
        "terminal":"RETF 4",
    }

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    output=args.output_dir.resolve()
    private=(ROOT/".analysis/reconstruction/probes").resolve()
    if output.exists() or output==private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run([sys.executable,"scripts/preflight.py"],cwd=ROOT,check=True,
                   capture_output=True,text=True)
    for path,expected in (
        (TARGET,TARGET_SHA),
        (SNAPSHOT/"bin/th04/maine.exe",BASE_EXE_SHA),
        (SNAPSHOT/"obj/th04/maine.map",BASE_MAP_SHA),
        (SNAPSHOT/"th04/initmain.cpp",BASE_WRAPPER_SHA),
        (SNAPSHOT/"obj/th04/initmain.obj",BASE_OBJECT_SHA),
    ):
        if sha_file(path)!=expected:
            raise RuntimeError(f"pinned input identity drift: {path}")
    if sha_file(RUNNER)!=RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")

    base_obj=SNAPSHOT/"obj/th04/initmain.obj"
    base_code=segment_bytes(base_obj,"SHARED")
    if len(base_code)!=PRODUCER_SIZE or sha(base_code)!=BASE_CODE_SHA:
        raise RuntimeError("baseline initmain SHARED contribution drift")
    if link_relevant_omf_sha(base_obj)!=BASE_LINK_OMF_SHA:
        raise RuntimeError("baseline initmain OMF drift")

    target=parse_mz(TARGET.read_bytes())
    baseline=parse_mz((SNAPSHOT/"bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations)!=RELOCATIONS:
        raise RuntimeError("invalid MAINE target/baseline")
    sites=[x.linear for x in target.relocations]
    if [x.linear for x in baseline.relocations]!=sites:
        raise RuntimeError("MAINE baseline relocation order drift")

    body=target.program_image[START:NEXT]
    producer=target.program_image[START:START+PRODUCER_SIZE]
    if baseline.program_image[START:NEXT]!=body or baseline.program_image[START:START+PRODUCER_SIZE]!=producer:
        raise RuntimeError("v489 game_init_main baseline differs from target")
    map_text=(SNAPSHOT/"obj/th04/maine.map").read_text(encoding="cp437")
    bound=target_boundary(body,map_text)
    mstart,msize,mline=map_contribution(SNAPSHOT/"obj/th04/maine.map")
    if (mstart,msize)!=(START,PRODUCER_SIZE):
        raise RuntimeError(f"baseline initmain MAP contribution drift: {mline}")

    closure=source_closure(ROOT,("src/shared/core/game_init_main.cpp",))
    source_hashes={name:sha_file(ROOT/name) for name in closure}
    output.mkdir(parents=True)
    builds={}
    for label in ("a","b"):
        work=output/label/"maine/source"
        work.parent.mkdir(parents=True)
        compact=copy_compact_snapshot(SNAPSHOT,work,"maine")
        for rel in closure:
            dst=work/rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/rel,dst)

        objdir=work/"obj/th04"
        before={p.name for p in objdir.glob("*.obj")}
        tcc(work,output,f"game-init-main-standalone-{label}","src/shared/core/game_init_main.cpp")
        standalone=[p for p in objdir.glob("*.obj") if p.name not in before]
        if len(standalone)!=1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj=standalone[0]
        local_desc=describe_omf(local_obj.read_bytes())
        local_code=segment_bytes(local_obj,"SHARED")
        local_fixups=object_fixups(local_obj)
        if (not local_desc["valid"]
            or "TC86 Borland C++ 4.02" not in local_desc["translator_comments"]
            or len(local_code)!=SIZE or sha(local_code)!=STANDALONE_CODE_SHA
            or local_fixups!=STANDALONE_FIXUPS):
            raise RuntimeError(f"{label}: standalone game_init_main codegen drift")
        masked_target=bytearray(body)
        masked_local=bytearray(local_code)
        for kind,off in STANDALONE_FIXUPS:
            width=2 if kind==1 else 4
            masked_target[off:off+width]=b"\0"*width
            masked_local[off:off+width]=b"\0"*width
        diffs=[i for i,(a,b) in enumerate(zip(masked_target,masked_local)) if a!=b]
        if diffs!=[29] or masked_target[29]!=0x90 or masked_local[29]!=0x9A:
            raise RuntimeError(f"{label}: non-fixup delta no longer isolates TLINK call optimization: {diffs}")

        wrapper=work/"th04/initmain.cpp"
        if sha_file(wrapper)!=BASE_WRAPPER_SHA:
            raise RuntimeError(f"{label}: initmain wrapper drift")
        wrapper.write_text('#include "src/shared/core/game_init_main.cpp"\n#pragma codestring "\\x00"\n')
        wrapper_sha=sha_file(wrapper)
        group_obj=work/"obj/th04/initmain.obj"
        group_obj.unlink()
        tcc(work,output,f"game-init-main-group-{label}","th04/initmain.cpp")
        group_desc=describe_omf(group_obj.read_bytes())
        group_code=segment_bytes(group_obj,"SHARED")
        if (not group_desc["valid"]
            or "TC86 Borland C++ 4.02" not in group_desc["translator_comments"]
            or group_code!=base_code
            or link_relevant_omf_sha(group_obj)!=BASE_LINK_OMF_SHA):
            raise RuntimeError(f"{label}: grouped initmain.obj drift")

        exe=work/"bin/th04/maine.exe"
        mp=work/"obj/th04/maine.map"
        exe.unlink(); mp.unlink()
        run_checked(["wine",str(RUNNER),"-e","-x","tlink",r"@obj\th04\maine.@l"],
                    work,output/f"link-{label}.log")
        image=parse_mz(exe.read_bytes())
        linked=image.program_image[START:NEXT]
        linked_producer=image.program_image[START:START+PRODUCER_SIZE]
        map_start,map_size,map_line=map_contribution(mp)
        if (not image.valid or sha_file(exe)!=BASE_EXE_SHA or sha_file(mp)!=BASE_MAP_SHA
            or [x.linear for x in image.relocations]!=sites
            or image.program_image!=baseline.program_image
            or linked!=body or linked_producer!=producer
            or (map_start,map_size)!=(START,PRODUCER_SIZE)):
            raise RuntimeError(f"{label}: linked MAINE game_init_main/layout drift")

        builds[label]={
            "compact_snapshot":compact,
            "patched_wrapper_sha256":wrapper_sha,
            "standalone_object_sha256":sha_file(local_obj),
            "standalone_link_relevant_omf_sha256":link_relevant_omf_sha(local_obj),
            "standalone_code_sha256":sha(local_code),
            "standalone_fixup_sites":[list(x) for x in local_fixups],
            "standalone_masked_difference_offsets":diffs,
            "group_object_sha256":sha_file(group_obj),
            "group_link_relevant_omf_sha256":link_relevant_omf_sha(group_obj),
            "group_code_sha256":sha(group_code),
            "linked_exe_sha256":sha_file(exe),
            "linked_map_sha256":sha_file(mp),
            "linked_program_sha256":sha(image.program_image),
            "linked_function_sha256":sha(linked),
            "linked_producer_sha256":sha(linked_producer),
            "raw_function_difference_count":0,
            "raw_producer_difference_count":0,
            "ordered_relocations":len(sites),
            "map_contribution":map_line,
            "tlink_same_segment_far_call_optimized":linked[29:34]==bytes.fromhex("90 0e e8 1c f8"),
        }

    stable=(
        "patched_wrapper_sha256","standalone_link_relevant_omf_sha256",
        "standalone_code_sha256","standalone_fixup_sites",
        "standalone_masked_difference_offsets","group_link_relevant_omf_sha256",
        "group_code_sha256","linked_exe_sha256","linked_map_sha256",
        "linked_program_sha256","linked_function_sha256","linked_producer_sha256",
        "raw_function_difference_count","raw_producer_difference_count",
        "ordered_relocations","map_contribution","tlink_same_segment_far_call_optimized",
    )
    if any(builds["a"][k]!=builds["b"][k] for k in stable):
        raise RuntimeError("independent MAINE game_init_main cold rounds differ")
    if any(sha_file(ROOT/name)!=digest for name,digest in source_hashes.items()):
        raise RuntimeError("maintained game_init_main source changed during replay")

    receipt={
        "schema_version":1,
        "observed_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact":"th04-maine",
        "source_sha256":source_hashes,
        "boundary":bound,
        "producer":{
            "segment":"SHARED","payload_offset":hex(START),"size":PRODUCER_SIZE,
            "function_size":SIZE,"padding_size":PRODUCER_SIZE-SIZE,
            "target_linked_sha256":sha(producer),
        },
        "builds":builds,
        "limit":"Decoded 77-byte game_init_main only; the 78th owner byte is linker/source padding. No packed-file or whole-MAINE exactness.",
    }
    path=output/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({
        "receipt":str(path),
        "function_sha256":builds["a"]["linked_function_sha256"],
        "producer_sha256":builds["a"]["linked_producer_sha256"],
        "relocations":builds["a"]["ordered_relocations"],
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
