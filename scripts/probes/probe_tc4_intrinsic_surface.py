#!/usr/bin/env python3
"""Probe hidden TC4J intrinsic/string-op surfaces relevant to final MAIN blockers."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve(); sys.path.insert(0,str(ROOT/'scripts/probes'))
from probe_tc4_mov_bx_ax_encoding import code_bytes
BASE=('-c','-ml','-O','-b-','-3','-Z','-d')
REJECT=('-z','-z-','-Oa','-Oa-','-OW','-Ow')
INTR={
'memcpy':('#include <string.h>','char a[32],b[32]; void near probe(void){ memcpy(a,b,32); }'),
'memset':('#include <string.h>','char a[32]; void near probe(void){ memset(a,0,32); }'),
'strlen':('#include <string.h>','char a[32]; unsigned near probe(void){ return strlen(a); }'),
'memcmp':('#include <string.h>','char a[32],b[32]; int near probe(void){ return memcmp(a,b,32); }'),
'strcpy':('#include <string.h>','char a[32],b[32]; void near probe(void){ strcpy(a,b); }'),
'strncpy':('#include <string.h>','char a[32],b[32]; void near probe(void){ strncpy(a,b,24); }'),
'strcat':('#include <string.h>','char a[32],b[32]; void near probe(void){ strcat(a,b); }')}
def dg(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--output-dir',type=Path); a=ap.parse_args(); out=a.output_dir.resolve() if a.output_dir else Path(tempfile.mkdtemp(prefix='tc4-intrinsic-',dir=PRIVATE/'reconstruction/probes'))
 if a.output_dir:
  if out.exists() or not out.is_relative_to(PRIVATE): ap.error('output must be new below .analysis')
  out.mkdir(parents=True)
 surf=tomllib.loads((ROOT/'config/toolchain.toml').read_text())['surfaces']; t=next(x for x in surf if x['id']=='active-tcc'); tcc=ROOT/t['path']
 if dg(tcc.read_bytes())!=t['sha256']: raise ValueError('TCC identity drift')
 runner=ROOT/'_reference/ReC98/bin/msdos.exe'; env=os.environ.copy(); env.update(WINEPREFIX=str(ROOT/'.analysis/toolchain/wineprefix'),WINEDEBUG='-all',MSDOS_PATH=r'C:\TC4\BIN;C:\TASM50\BIN')
 rejected={}
 for opt in REJECT:
  w=out/('opt-'+opt.replace('-','x')); w.mkdir(); (w/'p.cpp').write_text('#include <dos.h>\nvoid near probe(void){ _BX=_AX; }\n'); d=subprocess.run(['wine',str(runner),'-e','-x','tcc',*BASE,opt,f'-I{ROOT / "_reference/ReC98"}','p.cpp'],cwd=w,env=env,capture_output=True,text=True,timeout=90); log=(d.stdout+d.stderr).strip(); rejected[opt]={'exit_code':d.returncode,'object_present':(w/'p.obj').exists(),'log_tail':log[-180:]}
  if d.returncode==0 or (w/'p.obj').exists() or 'Incorrect command line option' not in log: raise ValueError(f'{opt}: expected hard rejection')
 intrinsic={}
 for name,(inc,body) in INTR.items():
  w=out/name; w.mkdir(); s=w/'p.cpp'; s.write_text(inc+'\n#pragma intrinsic '+name+'\n'+body+'\n'); d=subprocess.run(['wine',str(runner),'-e','-x','tcc',*BASE,f'-I{ROOT / "_reference/ReC98"}','p.cpp'],cwd=w,env=env,capture_output=True,text=True,timeout=90); o=w/'p.obj'
  if d.returncode or not o.is_file(): raise RuntimeError(f'{name}: compile failed')
  c=code_bytes(o); cp=w/'p.code'; cp.write_bytes(c); dis=subprocess.check_output(['ndisasm','-b16',str(cp)],text=True); (w/'p.ndis').write_text(dis); low=dis.lower(); intrinsic[name]={'source_sha256':dg(s.read_bytes()),'object_sha256':dg(o.read_bytes()),'code_size':len(c),'code_sha256':dg(c),'code_hex':c.hex(),'has_lodsb':any('lodsb' in x for x in low.splitlines()),'has_loop':any(x.split()[-2:-1]==['loop'] for x in low.splitlines()),'string_ops':[op for op in ('rep movsw','rep stosw','repne scasb','repe cmpsb','rep movsb','rep stosb') if op in low]}
 if any(x['has_lodsb'] or x['has_loop'] for x in intrinsic.values()): raise ValueError('tested intrinsic unexpectedly emitted LODSB/LOOP')
 rec={'schema_version':1,'claim_scope':'pinned TC4J hidden intrinsic/string-op surface for final TH04 MAIN blockers','tcc_sha256':t['sha256'],'runner_sha256':dg(runner.read_bytes()),'base_flags':list(BASE),'rejected_options':rejected,'intrinsics':intrinsic,'conclusion':'Pinned TCC rejects tested BCC-only -z/-Oa/-OW controls but accepts #pragma intrinsic. Tested memcpy/memset/strlen/memcmp/strcpy/strncpy/strcat inline into REP MOVS/STOS/SCAS/CMPS families; none emits LODSB or x86 LOOP. These contiguous primitives do not preserve the strided memory semantics of the carpet/checkerboard blockers.','limit':'Bounded compiler negative only; does not prove no other TC4J source form can emit LODSB/LOOP.'}; rp=out/'receipt.json'; rp.write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':dg(rp.read_bytes()),'intrinsics':list(INTR)},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
