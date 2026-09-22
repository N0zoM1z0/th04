#!/usr/bin/env python3
"""Replay the 2014 ReC98 Reduction #172 BGM-BSS binary-preserving form.

The exact template is taken from ReC98 commit 509d3b31, whose commit message
explicitly says that initializing the BSS data to zero instead of the `?` in
the original source avoids MZ header size changes.  This is repository-history
provenance for a reconstruction/build representation, not a claim about ZUN's
original source spelling.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
REC98 = ROOT / "_reference/ReC98"
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tasm  # noqa: E402
from probe_th04_master_object_split import sha  # noqa: E402

COMMIT = "509d3b31b9197711b65062108e12fe5a52a767e9"
PATH_IN_COMMIT = "libs/master.lib/bgm[bss].asm"
TEMPLATE = ROOT / "config/replay/th04_bgm_bss_reduction172_v494.asm.in"
TEMPLATE_SHA = "c6c7e07f7b9ac47397f5a2101ae077dc6e422c81cfbfa125149800b17eb12b31"
MESSAGE_NEEDLE = "Initializing the BSS data to 0 instead of the ? in the original source file\navoids size changes in the MZ header."

SPECS = {
    "op": {
        "base_exe": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
        "base_map": "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee",
        "final_exe": "994f80821d2918f0071e28f6e82d6ed660eac1d8473a532fd70fb743008f87ee",
        "final_map": "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee",
        "file_size": 76864, "load_size": 72256, "minalloc": 410, "relocs": 804,
        "diffs": [0xDE8B, 0xDE8C],
        "data_source": "th04_op_master_data_tail.asm", "data_object": "opmdata.obj",
        "exe": "bin/th04/op.exe", "map": "obj/th04/op.map", "response": "obj/th04/op.@l",
        "target_sha": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
    },
    "maine": {
        "base_exe": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        "base_map": "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e",
        "final_exe": "27c17df711ed08f4c4bcada9b4ba699914d08cb164cd1444c36f1994527bab8a",
        "final_map": "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e",
        "file_size": 69218, "load_size": 65634, "minalloc": 615, "relocs": 559,
        "diffs": [0xD1D3, 0xD1D4],
        "data_source": "th04_maine_master_data_tail.asm", "data_object": "mainemdata.obj",
        "exe": "bin/th04/maine.exe", "map": "obj/th04/maine.map", "response": "obj/th04/maine.@l",
        "target_sha": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"; parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="bgm-reduction172-v494-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE): raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True); return out


def git_bytes(args: list[str]) -> bytes:
    return subprocess.check_output(["git", "-C", str(REC98), *args])


def validate_history() -> dict[str, object]:
    if sha(TEMPLATE) != TEMPLATE_SHA: raise ValueError("v494 template identity drift")
    blob = git_bytes(["show", f"{COMMIT}:{PATH_IN_COMMIT}"])
    if digest(blob) != TEMPLATE_SHA or blob != TEMPLATE.read_bytes():
        raise ValueError("Reduction #172 source blob identity drift")
    msg = git_bytes(["show", "-s", "--format=%B", COMMIT]).decode("utf-8", errors="replace").strip()
    if MESSAGE_NEEDLE not in msg:
        raise ValueError("Reduction #172 provenance message drift")
    text = blob.decode("cp932")
    required = ["timerorg\tdd\t?", "part\t\tSPART\tPMAX dup(<0>)", "esound\t\tSESOUND\tSMAX dup(<0>)"]
    if any(x not in text for x in required): raise ValueError("Reduction #172 source spelling drift")
    return {"commit": COMMIT, "blob_sha256": digest(blob), "message": msg, "required_spellings": required}


def build_one(source: Path, art: str, target_path: Path, output: Path, label: str) -> dict[str, object]:
    spec=SPECS[art]; work=output/label/art/"source"; shutil.copytree(source,work,symlinks=True)
    exe=work/spec["exe"]; mp=work/spec["map"]
    if sha(exe)!=spec["base_exe"] or sha(mp)!=spec["base_map"]: raise ValueError(f"{label}/{art}: v489 baseline drift")
    base=parse_mz(exe.read_bytes()); base_sites=[r.linear for r in base.relocations]
    shutil.copy2(TEMPLATE, work/"libs/master.lib/bgm[bss].asm")
    tasm(work,output,f"{label}-{art}-reduction172",spec["data_source"],spec["data_object"])
    exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
    rsp="@"+spec["response"].replace("/","\\")
    run_checked(["wine",str(RUNNER),"-e","-x","tlink",rsp],work,output/f"link-{label}-{art}.log")
    raw=exe.read_bytes(); mz=parse_mz(raw); sites=[r.linear for r in mz.relocations]
    target_raw=target_path.read_bytes(); target=parse_mz(target_raw); target_sites=[r.linear for r in target.relocations]
    if sha(target_path)!=spec["target_sha"]: raise ValueError(f"{label}/{art}: target identity drift")
    if sha(exe)!=spec["final_exe"] or sha(mp)!=spec["final_map"]: raise ValueError(f"{label}/{art}: v494 output identity drift")
    if len(raw)!=spec["file_size"] or len(mz.program_image)!=spec["load_size"] or mz.header.minimum_extra_allocation!=spec["minalloc"]:
        raise ValueError(f"{label}/{art}: T/minalloc drift")
    if mz.program_image[:len(base.program_image)] != base.program_image: raise ValueError(f"{label}/{art}: baseline program prefix changed")
    extra=mz.program_image[len(base.program_image):]
    if any(extra): raise ValueError(f"{label}/{art}: file-backed extension not all zero")
    if sites!=base_sites or sites!=target_sites or len(sites)!=spec["relocs"]: raise ValueError(f"{label}/{art}: relocation drift")
    diffs=[i for i,(a,b) in enumerate(zip(mz.program_image,target.program_image)) if a!=b]
    if diffs!=spec["diffs"]: raise ValueError(f"{label}/{art}: remaining P frontier drift: {diffs}")
    return {
        "exe_sha256":sha(exe),"map_sha256":sha(mp),"file_size":len(raw),"load_image_bytes":len(mz.program_image),
        "minalloc":mz.header.minimum_extra_allocation,"program_prefix_unchanged":True,
        "zero_tail_bytes":len(extra),"zero_tail_sha256":digest(extra),"relocation_count":len(sites),
        "relocation_table_target_exact":sites==target_sites,"remaining_program_diff_offsets":[hex(x) for x in diffs],
    }


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--op-source-dir",type=Path,required=True); ap.add_argument("--maine-source-dir",type=Path,required=True)
    ap.add_argument("--op-target-restored",type=Path,required=True); ap.add_argument("--maine-target-restored",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path)
    args=ap.parse_args(); out=output_dir(args.output_dir); history=validate_history()
    builds={}
    for label in ("a","b"):
        builds[label]={
            "op":build_one(args.op_source_dir.resolve(),"op",args.op_target_restored.resolve(),out,label),
            "maine":build_one(args.maine_source_dir.resolve(),"maine",args.maine_target_restored.resolve(),out,label),
        }
    if builds["a"]!=builds["b"]: raise ValueError("A/B v494 results differ")
    receipt={
        "schema_version":1,"observed_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope":"TH04 OP/MAINE Reduction #172 repository-history-attested BGM BSS file-backing replay; no ZUN-source promotion",
        "history":history,"builds":builds,
        "observed_effect":(
            "The exact BGM BSS source blob from ReC98 Reduction #172 (2014) retains timerorg as uninitialized `dd ?` and initializes only part/esound with `dup(<0>)`. Its commit message explicitly records that this was done instead of the `?` in the original source to avoid MZ header size changes. Substituting that unmodified historical blob into isolated v489 OP/MAINE source copies reproduces exactly the same v492 EXEs, T extents, minalloc values, unchanged program prefixes, and target-exact relocation tables. Only the known snd_load two-byte program encoding remains versus target-restored MZs."),
        "limit":(
            "This is strong repository-history provenance for a binary-preserving reconstruction/build representation, not evidence that ZUN's original source used zero initialization. The historical commit explicitly says the original source used `?`. The mechanism may compensate for a lost original object/segment/post-link condition. Do not promote it as authored ZUN source without further evidence."),
    }
    rp=out/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"history_attested":True,"same_as_v492":True},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
