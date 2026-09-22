#!/usr/bin/env python3
"""Probe TC4J inline-expansion effects on the TH04 checkerboard counted loop.

Compiler-mechanism evidence only. No inline assembly, __emit__, target bytes,
or product-source changes are used.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile, tomllib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PRIVATE=(ROOT/".analysis").resolve()
sys.path[0:0]=[str(ROOT/"scripts"),str(ROOT/"scripts/probes")]
from lib.omf import parse_omf  # noqa: E402

def omf_index(data: bytes, pos: int) -> tuple[int, int]:
    first=data[pos]
    if first < 0x80:
        return first,pos+1
    return ((first & 0x7F) << 8) | data[pos+1], pos+2

def code_bytes(path: Path) -> bytes:
    # CPROBE_TEXT is deliberately the first SEGDEF. Ignore helper COMDAT/other
    # LEDATA: the target question is the actual probe body after inline expansion.
    chunks=[]
    for record in parse_omf(path.read_bytes()):
        if record.record_type != 0xA0:
            continue
        seg,pos=omf_index(record.data,0)
        off=int.from_bytes(record.data[pos:pos+2],"little"); pos+=2
        if seg == 1:
            chunks.append((off,record.data[pos:]))
    if not chunks:
        raise ValueError("no CPROBE_TEXT LEDATA")
    size=max(o+len(b) for o,b in chunks)
    out=bytearray(size)
    for o,b in chunks:
        out[o:o+len(b)]=b
    return bytes(out)

FLAGS=("-c","-ml","-O","-b-","-3","-Z","-d")
PREFIX="#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n#include <dos.h>\n"
SUFFIX="\n#pragma option -k.\n"
BODY="_ES=_DX; *reinterpret_cast<unsigned long __es *>(_DI)=_EAX; _DI+=8;"
SOURCES={
 "baseline": f"void near probe(void){{ _CX=6; do{{ {BODY} }}while(--_CX); }}",
 "inline_whole": f"inline void put6(void){{ _CX=6; do{{ {BODY} }}while(--_CX); }} void near probe(void){{ put6(); }}",
 "inline_body": f"inline void put1(void){{ {BODY} }} void near probe(void){{ _CX=6; do{{ put1(); }}while(--_CX); }}",
 "inline_count_arg": f"inline void putn(unsigned n){{ _CX=n; do{{ {BODY} }}while(--_CX); }} void near probe(void){{ putn(6); }}",
 "inline_local_count": f"inline void putn(unsigned n){{ do{{ {BODY} }}while(--n); }} void near probe(void){{ putn(6); }}",
 "inline_goto": f"inline void put6(void){{ _CX=6; L: {BODY} if(--_CX) goto L; }} void near probe(void){{ put6(); }}",
}

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def outdir(p:Path|None)->Path:
    if p is None:
        parent=PRIVATE/"reconstruction/probes"; parent.mkdir(parents=True,exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-checker-inline-v502-",dir=parent))
    o=p.resolve()
    if o.exists() or not o.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    o.mkdir(parents=True); return o

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--output-dir",type=Path)
    args=ap.parse_args(); out=outdir(args.output_dir)
    surfaces=tomllib.loads((ROOT/"config/toolchain.toml").read_text())["surfaces"]
    tcc=next(x for x in surfaces if x["id"]=="active-tcc")
    if sha((ROOT/tcc["path"]).read_bytes())!=tcc["sha256"]: raise ValueError("TCC identity drift")
    runner=ROOT/"_reference/ReC98/bin/msdos.exe"
    env=os.environ.copy(); env.update(WINEPREFIX=str(ROOT/".analysis/toolchain/wineprefix"),WINEDEBUG="-all",MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    results={}
    for name,body in SOURCES.items():
        w=out/name; w.mkdir(); src=w/"p.cpp"; src.write_text(PREFIX+body+SUFFIX)
        cmd=["wine",str(runner),"-e","-x","tcc",*FLAGS,f"-I{ROOT/'_reference/ReC98'}","p.cpp"]
        done=subprocess.run(cmd,cwd=w,env=env,capture_output=True,text=True,timeout=120)
        (w/"compile.log").write_text(done.stdout+done.stderr)
        obj=w/"p.obj"
        if done.returncode or not obj.is_file(): raise RuntimeError(f"{name}: compile failed\n{done.stdout}{done.stderr}")
        code=code_bytes(obj); (w/"p.code").write_bytes(code)
        dis=subprocess.run(["ndisasm","-b16",str(w/"p.code")],check=True,capture_output=True,text=True).stdout
        (w/"p.ndis").write_text(dis)
        results[name]={
          "source_sha256":sha(src.read_bytes()),"code_sha256":sha(code),"code_hex":code.hex(),
          "code_size":len(code),
          "has_loop":any(" loop " in (" "+x.lower()+" ") for x in dis.splitlines()),
          "has_call":any(" call " in (" "+x.lower()+" ") for x in dis.splitlines()),
          "disassembly":dis.splitlines(),
        }
    receipt={
      "schema_version":1,
      "claim_scope":"TC4J inline-expansion checkerboard counted-loop surface",
      "tcc_sha256":tcc["sha256"],"runner_sha256":sha(runner.read_bytes()),
      "probe_sha256":sha(Path(__file__).read_bytes()),"flags":list(FLAGS),
      "results":results,
      "loop_hits":[k for k,v in results.items() if v["has_loop"]],
      "call_hits":[k for k,v in results.items() if v["has_call"]],
      "limit":"Compiler mechanism evidence only; no source or exactness credit.",
    }
    rp=out/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp.read_bytes()),"loop_hits":receipt["loop_hits"],"call_hits":receipt["call_hits"],"summary":{k:{"size":v["code_size"],"sha":v["code_sha256"],"loop":v["has_loop"],"call":v["has_call"]} for k,v in results.items()}},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
