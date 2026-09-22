#!/usr/bin/env python3
"""Recover the historical TH04 OP score_db + score_e + hi_view TC86 producer."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_master_object_split import sha  # noqa: E402
from probe_th04_zunsoft_pyro_cpp_v463 import RUNNER, digest  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_op_score_group_v488.cpp.in"
TEMPLATE_SHA = "7789531bbc2d529beb7354915b87e2877585a270b2108ed00fc8c375d52e7bfd"
RUNNER_SHA = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
BASE_EXE = "310ad3af095ba29067f264acbd5c88ed320d64f07bf9d315336b592fef8b5192"
BASE_MAP = "e8a3813d4a369fadda19582237e2066680a28353e5b6acc9e23e0925be122a95"
BASE_PROGRAM = "7e4cb7aa24782700d6db85c4cd39622d7b23e3a62d9da325b92089e9b8f1b948"
TARGET_RESTORED_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
FINAL_EXE = "d1e64a65e06844831264ad9691710007e629e63599639e73d1ca0a180d5a29d8"
FINAL_MAP = "3f48d379d567cce4be13c68e9f053dffd8712a941ea4f32f9296df85bab3fe07"
RAW_SIZE = 0x071D
RAW_SHA = "1792cb712472c9bebb41e53da7720535202722a9f17ec347d84d99ea558e08b5"
LEDATA_EXTENTS = [(0x000, 0x3FE), (0x3FE, 0x71D)]
KIND3_COUNTS = [25, 38]
EXPECTED_CHANGED = list(range(403, 466))
EXPECTED_REMAINING = list(range(186, 194))
EXPECTED_MISMATCHES = 8


def outdir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"; parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-score-group-v488-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def env() -> dict[str, str]:
    e = os.environ.copy()
    e.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"), WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN")
    return e


def run_checked(cmd: list[str], cwd: Path, log: Path, timeout: int = 180) -> None:
    p = subprocess.run(cmd, cwd=cwd, env=env(), capture_output=True, text=True, timeout=timeout)
    log.write_text(json.dumps(cmd)+f"\nexit={p.returncode}\n"+p.stdout+"\n"+p.stderr)
    if p.returncode:
        raise RuntimeError(f"command failed; see {log}")


def segment_bytes(path: Path, seg: str) -> tuple[bytes, list[tuple[int,int,int,int]]]:
    recs = parse_omf(path.read_bytes()); groups = code_ledata(recs, seg)
    if not groups: return b"", []
    out = bytearray(max(e for s,e,n,f in groups))
    for s,e,n,f in groups: out[s:e] = recs[n-1].data[3:]
    return bytes(out), groups


def apply_scaffold(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA: raise ValueError("template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/scall.cpp")
    h = work / "th04/formats/scoredat/scoredat.hpp"; s = h.read_text()
    h.write_text("#ifndef V488_SCOREDAT_HPP_GUARD\n#define V488_SCOREDAT_HPP_GUARD\n"+s+"\n#endif\n")
    for rel, needle in (
        ("th04/hiscore/view.cpp", "#pragma option -zPop_01\n"),
        ("th04/formats/scoredat/recreate.cpp", "#pragma option -zCSCORE_TEXT\n\n"),
        ("th04/formats/scoredat/encode.cpp", "#pragma option -zCSCORE_TEXT\n\n"),
    ):
        p = work / rel; t = p.read_text()
        if t.count(needle) != 1: raise ValueError(f"pragma anchor drift: {rel}")
        p.write_text(t.replace(needle, "", 1))


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir",type=Path,required=True); ap.add_argument("--target-restored",type=Path,required=True); ap.add_argument("--output-dir",type=Path)
    args=ap.parse_args(); source=args.source_dir.resolve(); target_path=args.target_restored.resolve(); output=outdir(args.output_dir)
    if sha(RUNNER) != RUNNER_SHA: raise ValueError("runner drift")
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA: raise ValueError("target drift")
    base_exe=source/"bin/th04/op.exe"; base_map=source/"obj/th04/op.map"
    if sha(base_exe)!=BASE_EXE or sha(base_map)!=BASE_MAP: raise ValueError("v466 source identity drift")
    baseline=parse_mz(base_exe.read_bytes()); base_sites=[r.linear for r in baseline.relocations]
    if digest(baseline.program_image)!=BASE_PROGRAM: raise ValueError("v466 program image drift")
    target=parse_mz(target_path.read_bytes()); target_sites=[r.linear for r in target.relocations]
    if sum(a!=b for a,b in zip(base_sites,target_sites)) != 71: raise ValueError("v466 frontier drift")
    if len(base_sites)!=804 or Counter(base_sites)!=Counter(target_sites): raise ValueError("baseline relocation multiset drift")

    builds={}
    for label in ("a","b"):
        work=output/label/"source"; shutil.copytree(source,work,symlinks=True); apply_scaffold(work)
        obj=work/"obj/th04/scall.obj"; obj.unlink(missing_ok=True)
        run_checked(["wine",str(RUNNER),"-e","-x","tcc","-c","-I.","-O","-b-","-3","-Z","-d","-DGAME=4","-ml","-DBINARY='O'","-nobj/th04/","th04/scall.cpp"],work,output/f"compile-{label}.log")
        code,groups=segment_bytes(obj,"SCORE_TEXT")
        if len(code)!=RAW_SIZE or digest(code)!=RAW_SHA: raise ValueError(f"{label}: raw owner drift")
        extents=[(s,e) for s,e,n,f in groups]
        if extents!=LEDATA_EXTENTS: raise ValueError(f"{label}: LEDATA extent drift: {extents}")
        kind3=[]
        for rec in parse_omf(obj.read_bytes()):
            if rec.record_type==0x9C:
                xs=[loc for kind,loc in fixup_locations(rec.data) if kind==3]
                if xs: kind3.append(xs)
        if [len(x) for x in kind3] != KIND3_COUNTS: raise ValueError(f"{label}: kind3 record counts drift")
        if kind3[0][-2:] != [0xD7,0xCF]: raise ValueError(f"{label}: score_e tail fixups drift")

        rsp=work/"obj/th04/op.@l"; text=rsp.read_text(); old=r"obj\th04\score_db.obj obj\th04\score_e.obj obj\th04\hi_view.obj"
        if text.count(old)!=1: raise ValueError(f"{label}: response score-group anchor drift")
        rsp.write_text(text.replace(old,r"obj\th04\scall.obj",1))
        exe=work/"bin/th04/op.exe"; mp=work/"obj/th04/op.map"; exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine",str(RUNNER),"-e","-x","tlink",r"@obj\th04\op.@l"],work,output/f"link-{label}.log")
        image=parse_mz(exe.read_bytes()); sites=[r.linear for r in image.relocations]
        if image.program_image != baseline.program_image: raise ValueError(f"{label}: linked program image drift")
        if Counter(sites)!=Counter(target_sites): raise ValueError(f"{label}: relocation multiset drift")
        changed=[i for i,(a,b) in enumerate(zip(base_sites,sites)) if a!=b]
        if changed!=EXPECTED_CHANGED: raise ValueError(f"{label}: changed-index drift")
        if sites[403:466] != target_sites[403:466]: raise ValueError(f"{label}: score/hi block not target exact")
        remaining=[i for i,(a,b) in enumerate(zip(sites,target_sites)) if a!=b]
        if remaining!=EXPECTED_REMAINING: raise ValueError(f"{label}: remaining frontier drift: {remaining}")
        if sha(exe)!=FINAL_EXE or sha(mp)!=FINAL_MAP: raise ValueError(f"{label}: output identity drift")
        builds[label]={"exe_sha256":sha(exe),"map_sha256":sha(mp),"program_image_sha256":digest(image.program_image),"raw_owner_sha256":digest(code),"raw_owner_size":len(code),"ledata_extents":extents,"kind3_record_counts":[len(x) for x in kind3],"first_record_score_e_tail":kind3[0][-2:],"changed_indices_vs_v466":changed,"score_hi_target_exact_indices":[403,465],"remaining_mismatch_indices":remaining,"ordered_relocation_mismatches":len(remaining),"same_index_relocations":len(sites)-len(remaining)}
    for key in builds["a"]:
        if builds["a"][key]!=builds["b"][key]: raise ValueError(f"A/B {key} differs")
    receipt={"schema_version":1,"observed_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"claim_scope":"TH04 OP historical score_db+score_e+hi_view physical TC86 producer replay","v466_source_exe_sha256":BASE_EXE,"v466_source_map_sha256":BASE_MAP,"target_restored_sha256":TARGET_RESTORED_SHA,"template":str(TEMPLATE.relative_to(ROOT)),"template_sha256":TEMPLATE_SHA,"builds":builds,"observed_effect":"Compiling score_db (0xAD), score_e (0x65), and hi_view (0x60B) as one TC86 SCORE_TEXT translation unit shifts natural LEDATA batching to 0x3FE/0x31F. The first kind-3 FIXUPP record contains 23 hi_view segment sites followed by score_e's two sites, and the second record contains the remaining 38 hi_view sites. Replacing the three v466 objects by this one producer preserves every linked program byte and the 804-site relocation multiset, makes target indices 403..465 exact, and reduces OP ordered residual 71 to 8. Only BGIMAGE indices 186..193 remain.","limit":"The temporary include guard and duplicate code-segment pragma suppression are compile-scaffold hygiene only; no function body is changed. This packet recovers physical OMF/TU topology, not new authored function text."}
    rp=output/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"candidate_sha256":FINAL_EXE,"ordered_relocation_mismatches":EXPECTED_MISMATCHES,"same_index_relocations":804-EXPECTED_MISMATCHES},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
