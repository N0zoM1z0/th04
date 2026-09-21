#!/usr/bin/env python3
"""Probe remaining natural TC4J LODSB and DS->ES setup source surfaces.

This is bounded compiler evidence for TH04 carpet_lighting_put_new(). It does
not alter product source and grants no exactness or inline-assembly provenance.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve(); sys.path.insert(0,str(ROOT/'scripts/probes'))
from probe_tc4_mov_bx_ax_encoding import code_bytes
BASE=('-c','-ml','-O','-b-','-3','-Z','-d')

def dg(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--output-dir',type=Path); a=ap.parse_args()
 out=a.output_dir.resolve() if a.output_dir else Path(tempfile.mkdtemp(prefix='tc4-lodsb-seg-',dir=PRIVATE/'reconstruction/probes'))
 if a.output_dir:
  if out.exists() or not out.is_relative_to(PRIVATE): ap.error('output must be new below .analysis')
  out.mkdir(parents=True)
 surf=tomllib.loads((ROOT/'config/toolchain.toml').read_text())['surfaces']; t=next(x for x in surf if x['id']=='active-tcc'); tcc=ROOT/t['path']
 if dg(tcc.read_bytes())!=t['sha256']: raise ValueError('TCC identity drift')
 runner=ROOT/'_reference/ReC98/bin/msdos.exe'; env=os.environ.copy(); env.update(WINEPREFIX=str(ROOT/'.analysis/toolchain/wineprefix'),WINEDEBUG='-all',MSDOS_PATH=r'C:\TC4\BIN;C:\TASM50\BIN')
 variants={
  'si_postinc_cast':('#include <dos.h>','void near probe(void){ _AL = *((unsigned char near *)_SI++); }'),
  'si_postinc_reinterpret':('#include <dos.h>','void near probe(void){ _AL = *reinterpret_cast<unsigned char near *>(_SI++); }'),
  'si_load_then_inc':('#include <dos.h>','void near probe(void){ _AL = *reinterpret_cast<unsigned char near *>(_SI); _SI++; }'),
  'register_ptr':('#include <dos.h>','void near probe(void){ register unsigned char near *p = reinterpret_cast<unsigned char near *>(_SI); _AL = *p++; _SI = reinterpret_cast<unsigned int>(p); }'),
  'movedata_call':('#include <dos.h>\n#include <mem.h>','void near probe(void){ movedata(_DS, _SI, _ES, _DI, _CX); }'),
  'movedata_intrinsic':('#include <dos.h>\n#include <mem.h>\n#pragma intrinsic movedata','void near probe(void){ movedata(_DS, _SI, _ES, _DI, _CX); }'),
  'near_memcpy_scalar_before':('#include <dos.h>\n#include <string.h>\n#pragma intrinsic memcpy\nchar a[32], b[32];','void near probe(void){ _BX = 0x1234; memcpy(a,b,32); }'),
 }
 results={}
 for name,(inc,body) in variants.items():
  w=out/name; w.mkdir(); s=w/'p.cpp'; s.write_text('#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n'+inc+'\n'+body+'\n#pragma option -k.\n')
  cmd=['wine',str(runner),'-e','-x','tcc',*BASE,f'-I{ROOT / "_reference/ReC98"}','p.cpp']; d=subprocess.run(cmd,cwd=w,env=env,capture_output=True,text=True,timeout=120); log=(d.stdout+d.stderr); (w/'compile.log').write_text(log); o=w/'p.obj'
  if d.returncode or not o.is_file(): raise RuntimeError(f'{name}: compile failed: {log}')
  c=code_bytes(o); (w/'p.code').write_bytes(c); dis=subprocess.check_output(['ndisasm','-b16',str(w/'p.code')],text=True); (w/'p.ndis').write_text(dis)
  results[name]={'source_sha256':dg(s.read_bytes()),'object_sha256':dg(o.read_bytes()),'code_hex':c.hex(),'code_sha256':dg(c),'has_lodsb':'lodsb' in dis.lower(),'has_push_ds_pop_es':b'\x1e\x07' in c,'compiler_log':log.strip()[-240:]}
 for n in ('si_postinc_cast','si_postinc_reinterpret','si_load_then_inc','register_ptr'):
  if results[n]['has_lodsb']: raise ValueError(f'{n}: unexpected LODSB')
 if results['movedata_call']['has_lodsb'] or results['movedata_call']['has_push_ds_pop_es']:
  raise ValueError('movedata call unexpectedly became local LODSB/DS->ES intrinsic')
 if 'Ill-formed pragma' not in results['movedata_intrinsic']['compiler_log']:
  raise ValueError('movedata intrinsic pragma acceptance changed')
 if not results['near_memcpy_scalar_before']['has_push_ds_pop_es']:
  raise ValueError('near memcpy no longer emits DS->ES setup')
 code=bytes.fromhex(results['near_memcpy_scalar_before']['code_hex'])
 if code.find(b'\xbb\x34\x12')<0 or code.find(b'\x1e\x07')<code.find(b'\xbb\x34\x12'):
  raise ValueError('near memcpy DS->ES setup unexpectedly hoisted ahead of scalar source')
 rec={'schema_version':1,'claim_scope':'TC4J post-increment LODSB and DS->ES intrinsic placement surface for TH04 carpet','tcc_sha256':t['sha256'],'runner_sha256':dg(runner.read_bytes()),'base_flags':list(BASE),'results':results,'conclusion':'Fixed-SI post-increment source forms remain MOV AL,[SI]; INC SI rather than LODSB. movedata stays a far runtime call and is not accepted by #pragma intrinsic. Near-array intrinsic memcpy can naturally emit PUSH DS; POP ES, but placement follows the source copy site rather than being hoisted over preceding scalar work. Therefore carpet entry 1E 07 is compiler-reachable only in a real string-intrinsic context; no semantically matching natural carpet source is demonstrated.','limit':'Bounded compiler evidence only. It does not prove historical source language and does not authorize inert/fake memcpy or target-derived inline assembly.'}; rp=out/'receipt.json'; rp.write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':dg(rp.read_bytes())},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
