#!/usr/bin/env python3
"""Prove that TH04/TH05 use ZUN-modified MASTER code, not masters.lib verbatim.

The official/archive GRAPH_GAIJI_PUTC/PUTS objects retain the master.lib ADC
5680h bug.  Independently restored TH04 and TH05 OP/MAINE targets contain ADD
at the corresponding functions.  This packet establishes archive-version
mismatch only; it does not infer the contents of ZUN's historical b_data object.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_master_bgm_archive_order import ARCHIVE, ARCHIVE_SHA, RUNNER, RUNNER_SHA, TLIB, TLIB_SHA, run_tlib  # noqa: E402

EXPECTED_ARCHIVE = {
    "grpgjput": {
        "obj_sha256": "fa85d77b90daea85910f921fcf465415b300db41846f9e5a67fade40de2a529d",
        "code_size": 148,
        "code_sha256": "80fed19f84cd2a71daedaa05580f302d3da57b9f7f2cc6c1146189c9db466088",
        "site_offset": 0x10,
        "site_bytes": "81d58056",  # ADC BP,5680h
        "public": "GRAPH_GAIJI_PUTC",
    },
    "grpgputs": {
        "obj_sha256": "9643b6a564c37cfcedcc72797dce7a1b7400f42aaf07272bf1074807092c7e89",
        "code_size": 168,
        "code_sha256": "64421f86f84908f25140e33c06ac2f59cdcae88be19555d7438e65f8cc9930e3",
        "site_offset": 0x4E,
        "site_bytes": "158056",  # ADC AX,5680h
        "public": "GRAPH_GAIJI_PUTS",
    },
}

EXPECTED_TARGETS = {
    "th04-op": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
    "th04-maine": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
    "th05-op": "1caaa7f804146838e8771ae69487005f1ccd70cc8369dcb62e8adaf6addad71c",
    "th05-maine": "247a7b90bb912562999da15267fe6e98fa72c8cccdbab3f1a88eee37c82fc9a4",
}

TARGET_SITES = {
    "GRAPH_GAIJI_PUTC": (0x10, bytes.fromhex("81c58056")),  # ADD BP,5680h
    "GRAPH_GAIJI_PUTS": (0x4F, bytes.fromhex("058056")),    # ADD AX,5680h
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"; parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="zun-master-patch-v493-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE): raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True); return out


def public_load(map_path: Path, symbol: str) -> int:
    text = map_path.read_text(encoding="cp437", errors="replace")
    matches = re.findall(rf"^\s*([0-9A-F]{{4}}):([0-9A-F]{{4}})\s+(?:idle\s+)?{re.escape(symbol)}\s*$", text, re.M)
    vals = sorted({int(a,16)*16 + int(b,16) for a,b in matches})
    if len(vals) != 1: raise ValueError(f"{map_path}: {symbol} ambiguity {vals}")
    return vals[0]


def extract_archive(output: Path) -> dict[str, object]:
    for p,h in ((ARCHIVE,ARCHIVE_SHA),(RUNNER,RUNNER_SHA),(TLIB,TLIB_SHA)):
        if not p.is_file() or sha(p) != h: raise ValueError(f"identity drift: {p}")
    work=output/"archive"; work.mkdir(); shutil.copy2(ARCHIVE,work/"masters.lib")
    listing=run_tlib(work,"masters.lib,masters.lst"); (output/"list.log").write_text(listing.stdout+listing.stderr)
    if listing.returncode: raise RuntimeError("TLIB listing failed")
    lt=(work/"masters.lst").read_bytes().decode("cp437",errors="replace")
    result={}
    for module,spec in EXPECTED_ARCHIVE.items():
        if module not in lt or spec["public"] not in lt: raise ValueError(f"archive listing missing {module}/{spec['public']}")
        rsp=work/f"{module}.rsp"; rsp.write_text(f"*{module}\n")
        p=run_tlib(work,"masters.lib",f"@{rsp.name}"); (output/f"extract-{module}.log").write_text(p.stdout+p.stderr)
        obj=work/f"{module}.OBJ"
        if p.returncode or not obj.is_file() or sha(obj)!=spec["obj_sha256"]: raise ValueError(f"archive object drift: {module}")
        recs=parse_omf(obj.read_bytes()); groups=code_ledata(recs,"_TEXT")
        code=bytearray(max(e for s,e,n,f in groups))
        for s,e,n,f in groups: code[s:e]=recs[n-1].data[3:]
        b=bytes(code); off=spec["site_offset"]; wanted=bytes.fromhex(spec["site_bytes"])
        if len(b)!=spec["code_size"] or hashlib.sha256(b).hexdigest()!=spec["code_sha256"] or b[off:off+len(wanted)]!=wanted:
            raise ValueError(f"archive code/opcode drift: {module}")
        result[module]={"object_sha256":sha(obj),"code_size":len(b),"code_sha256":hashlib.sha256(b).hexdigest(),"public":spec["public"],"adc_site_offset":off,"adc_bytes":wanted.hex()}
    return result


def inspect_target(label: str, exe: Path, map_path: Path) -> dict[str, object]:
    if sha(exe)!=EXPECTED_TARGETS[label]: raise ValueError(f"{label}: target identity drift")
    mz=parse_mz(exe.read_bytes())
    if not mz.valid: raise ValueError(f"{label}: invalid MZ")
    funcs={}
    for sym,(off,wanted) in TARGET_SITES.items():
        start=public_load(map_path,sym); got=mz.program_image[start+off:start+off+len(wanted)]
        if got!=wanted: raise ValueError(f"{label}: {sym} is not ZUN ADD variant: {got.hex()}")
        funcs[sym]={"load":start,"site_offset":off,"add_bytes":got.hex()}
    return {"sha256":sha(exe),"functions":funcs}


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--th04-op-restored",type=Path,required=True); ap.add_argument("--th04-maine-restored",type=Path,required=True)
    ap.add_argument("--th05-op-restored",type=Path,required=True); ap.add_argument("--th05-maine-restored",type=Path,required=True)
    ap.add_argument("--th04-op-map",type=Path,required=True); ap.add_argument("--th04-maine-map",type=Path,required=True)
    ap.add_argument("--th05-op-map",type=Path,required=True); ap.add_argument("--th05-maine-map",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path)
    args=ap.parse_args(); out=output_dir(args.output_dir)
    archive=extract_archive(out)
    targets={
        "th04-op":inspect_target("th04-op",args.th04_op_restored.resolve(),args.th04_op_map.resolve()),
        "th04-maine":inspect_target("th04-maine",args.th04_maine_restored.resolve(),args.th04_maine_map.resolve()),
        "th05-op":inspect_target("th05-op",args.th05_op_restored.resolve(),args.th05_op_map.resolve()),
        "th05-maine":inspect_target("th05-maine",args.th05_maine_restored.resolve(),args.th05_maine_map.resolve()),
    }
    receipt={
        "schema_version":1,"observed_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope":"TH04/TH05 ZUN-modified MASTER.LIB provenance: gaiji ADD fix versus official/archive ADC objects",
        "archive_sha256":ARCHIVE_SHA,"archive_objects":archive,"targets":targets,
        "observed_effect":(
            "The pinned generic masters.lib contains grpgjput/grpgputs objects with the official master.lib ADC 5680h bug. Independently restored TH04 OP, TH04 MAINE, TH05 OP, and TH05 MAINE targets all contain ADD at the corresponding GRAPH_GAIJI_PUTC/PUTS sites. Therefore ZUN's TH04/TH05 build did not link these MASTER routines verbatim from the pinned generic archive; a game-specific modified MASTER source/object set is target-attested."),
        "limit":(
            "This proves MASTER archive/version divergence but does not prove that ZUN's BGM b_data object used initialized BSS or emitted LEDATA. It weakens the generic b_data.OBJ as a negative provenance constraint for v492 but does not by itself promote the explicit-zero BGM replay template to historical source."),
    }
    rp=out/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"archive_adc":True,"four_targets_add":True},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
