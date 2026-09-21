#!/usr/bin/env python3
"""Bound TASM32 5.0 option/version-emulation effects on TH04 FIXUPP order.

The real OP music producer supplies a target-relevant pair of multi-site kind-3
FIXUPP records. Two tiny symbolic fixtures separately cover ordered segment
fixups and far-call fixups without depending on modern ReC98 macro syntax.
No target bytes or relocation tables are edited.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, tomllib
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve(); sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/probes')]
from lib.omf import parse_omf
from replay_th04_scroll_driver_natural import fixup_locations,omf_index
TASM_SHA='ba50fe547863b96242d98cff54cdf95ab268a8682395afad172eedbfc46c5b26'
REAL_OBJ_SHA='0e1f644354036bea04bdb4138d6b83c915e9c93473c39eafe4d574d03c3056e7'
REAL_CODE_SHA='f427b565d2e036f8a4b90887f1f3ea896664bbde48164a170ffbfc62617c79ef'
REAL_GROUPS=[[0x4A,0x5B,0xF5,0x119,0x137,0x160,0x17E,0x19D,0x1E8,0x20B,0x21C,0x223,0x22D,0x23B,0x242,0x247,0x252,0x25D,0x2C7,0x2CE,0x2F4,0x2FF,0x308,0x311,0x31A,0x323,0x338,0x342,0x3D3,0x3DB],[0x43A,0x43F,0x44F,0x454,0x459]]
REAL_VARIANTS={'baseline':([],REAL_OBJ_SHA),'m1':(['/m1'],REAL_OBJ_SHA),'m2':(['/m2'],REAL_OBJ_SHA),'m3':(['/m3'],REAL_OBJ_SHA),'m5':(['/m5'],REAL_OBJ_SHA),'q':(['/q'],'f86089a2238600204c850171cf8ac4329b852e830af95b7dbb4f9611a751f0b7'),'a':(['/a'],'17b6b441a6674324dd0870bdd725ca7737f8fc60997d38ce26dd4cf2fc1e1332'),'s':(['/s'],REAL_OBJ_SHA),'os':(['/os'],REAL_OBJ_SHA),'o':(['/o'],REAL_OBJ_SHA),'oi':(['/oi'],'9e8a233170efc4a9f0b8c020a570f33be36560c440e48334e284d4da95f5bddc'),'uT500':(['/uT500'],REAL_OBJ_SHA)}
VERSION_IDS=['T100','T101','T200','T250','T300','T310','T320','T400','T410','T500','M400','M500','M510','M520']
SEGMENT_FIXTURE=ROOT/'config/replay/th04_bgimage_fixup_direction_v233.asm.in'
SEGMENT_FIXTURE_SHA='90129f58a781ee197ab3c6436386a9482484d58e2fc50101e7d9c9b26dd3f2a8'
FAR_FIXTURE="""SHARED SEGMENT PARA PUBLIC 'CODE'\nASSUME CS:SHARED\nEXTRN F1:FAR,F2:FAR,F3:FAR,F4:FAR,F5:FAR,F6:FAR,F7:FAR,F8:FAR\nPUBLIC PROBE\nPROBE PROC NEAR\n CALL F1\n CALL F2\n CALL F3\n CALL F4\n CALL F5\n CALL F6\n CALL F7\n CALL F8\n RET\nPROBE ENDP\nSHARED ENDS\nEND\n"""
def sha(b):return hashlib.sha256(b).hexdigest()
def outdir(p):
 if p is None:q=PRIVATE/'reconstruction/probes';q.mkdir(parents=True,exist_ok=True);return Path(tempfile.mkdtemp(prefix='tasm5-fixupp-',dir=q))
 q=p.resolve();
 if q.exists() or not q.is_relative_to(PRIVATE):raise ValueError('output must be new and below .analysis')
 q.mkdir(parents=True);return q
def run(work,source,obj,extra,log,game=False):
 env=os.environ.copy();env.update(WINEPREFIX=str(ROOT/'.analysis/toolchain/wineprefix'),WINEDEBUG='-all')
 args=['/m','/mx','/kh32768','/t'] + (['/dGAME=4'] if game else [])
 if extra and extra[0].startswith('/m') and extra[0]!='/mx':args=[x for x in args if x!='/m']
 args+=extra; cmd=['wine',r'C:\TASM50\BIN\TASM32.EXE',*args,source,obj]
 p=subprocess.run(cmd,cwd=work,env=env,capture_output=True,text=True,timeout=120);log.write_text(json.dumps(cmd)+f'\nexit={p.returncode}\n'+p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(f'TASM failed: {log}')
def omf_sig(path,segment=None):
 rec=parse_omf(path.read_bytes()); names=[''];segs=[];groups=[];code=bytearray()
 for r in rec:
  if r.record_type==0x96:
   p=0
   while p<len(r.data):n=r.data[p];names.append(r.data[p+1:p+1+n].decode('latin1'));p+=n+1
  elif r.record_type==0x98:
   d=r.data;p=1+(3 if d[0]>>5==0 else 2);ni,p=omf_index(d,p);segs.append(names[ni])
 for i,r in enumerate(rec):
  if r.record_type==0x9c and segment is None:groups.append(fixup_locations(r.data))
  if r.record_type!=0xA0 or segment is None:continue
  si,p=omf_index(r.data,0);off=int.from_bytes(r.data[p:p+2],'little');payload=r.data[p+2:]
  if segs[si-1]!=segment:continue
  if len(code)<off+len(payload):code.extend(b'\0'*(off+len(payload)-len(code)))
  code[off:off+len(payload)]=payload;j=i+1
  while j<len(rec) and rec[j].record_type==0x9c:
   k3=[off+loc+2 for kind,loc in fixup_locations(rec[j].data) if kind==3]
   if k3:groups.append(k3)
   j+=1
 return {'object_sha256':sha(path.read_bytes()),'code_sha256':sha(code) if segment else None,'groups':groups}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--output-dir',type=Path);a=ap.parse_args();src=a.source_dir.resolve();out=outdir(a.output_dir)
 tasm=ROOT/'.analysis/toolchain/installed/tasm50/bin/TASM32.EXE'
 if sha(tasm.read_bytes())!=TASM_SHA:raise ValueError('TASM identity drift')
 if sha(SEGMENT_FIXTURE.read_bytes())!=SEGMENT_FIXTURE_SHA:raise ValueError('segment fixture drift')
 real={}; temp=out/'real';temp.mkdir()
 for name,(extra,objsha) in REAL_VARIANTS.items():
  host=temp/f'{name}.obj';run(src,'th04_op_music_master.asm',fr'{temp.relative_to(src) if temp.is_relative_to(src) else ""}',extra,out/f'{name}.log') if False else None
  # Assemble to a source-tree-local temporary path so DOS TASM accepts it.
  local=src/'v453_tmp';local.mkdir(exist_ok=True);dest=local/f'{name}.obj';dest.unlink(missing_ok=True);run(src,'th04_op_music_master.asm',fr'v453_tmp\{name}.obj',extra,out/f'real-{name}.log',game=True);s=omf_sig(dest,'OP_MUSIC_TEXT');shutil.copy2(dest,host);dest.unlink()
  if s['object_sha256']!=objsha or s['code_sha256']!=REAL_CODE_SHA or s['groups']!=REAL_GROUPS:raise ValueError(f'real variant drift: {name}')
  real[name]=s
 (src/'v453_tmp').rmdir()
 fixtures=out/'fixtures';fixtures.mkdir();shutil.copy2(SEGMENT_FIXTURE,fixtures/'segment.asm');(fixtures/'far.asm').write_text(FAR_FIXTURE)
 version={}
 segment_base_sha=None; far_current_sha=None; far_old_sha=None
 old_modes={'T100','T101','M400','M500','M510','M520'}
 for vid in ['BASE',*VERSION_IDS]:
  extra=[] if vid=='BASE' else [f'/u{vid}'];row={}
  for kind,fn in [('segment','segment.asm'),('far','far.asm')]:
   dest=fixtures/f'{kind}-{vid}.obj';run(fixtures,fn,dest.name,extra,out/f'{kind}-{vid}.log');row[kind]=omf_sig(dest)
  segfix=[(k,o) for group in row['segment']['groups'] for k,o in group]
  if segfix!=[(2,o) for o in range(0,16,2)]:raise ValueError(f'{vid}: segment fixup drift: {segfix}')
  segment_base_sha=segment_base_sha or row['segment']['object_sha256']
  if row['segment']['object_sha256']!=segment_base_sha:raise ValueError(f'{vid}: segment object differs')
  farfix=[(k,o) for group in row['far']['groups'] for k,o in group];loc=[o for k,o in farfix]
  if loc!=sorted(loc):raise ValueError(f'{vid}: far FIXUPP is not ascending')
  if vid in old_modes:
   if not all(k==3 for k,o in farfix):raise ValueError(f'{vid}: old/MASM far kind drift')
   far_old_sha=far_old_sha or row['far']['object_sha256']
   if row['far']['object_sha256']!=far_old_sha:raise ValueError(f'{vid}: old/MASM object class drift')
  else:
   if not all(k==1 for k,o in farfix):raise ValueError(f'{vid}: current far kind drift')
   far_current_sha=far_current_sha or row['far']['object_sha256']
   if row['far']['object_sha256']!=far_current_sha:raise ValueError(f'{vid}: current object class drift')
  version[vid]=row
 rec={'schema_version':1,'observed_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'claim_scope':'active TASM32 5.0 option/version-emulation FIXUPP-order surface; no source/exact promotion','tasm_sha256':TASM_SHA,'real_op_music_variants':real,'version_ids':VERSION_IDS,'version_fixtures':version,'conclusion':'On the real OP music assembler source, multipass limits, /q, segment-order /a-/s, standard/overlay/IBM OMF modes, and /uT500 preserve the two target-relevant kind-3 FIXUPP groups in the same ascending/current order. On minimal symbolic fixtures, every legal TASM/MASM version-emulation ID T100..T500/M400..M520 preserves ascending FIXUPP LOCAT order. Older/MASM modes can change FAR CALL encoding/fixup kind, but never reverse emission order. Active TASM5 compatibility modes therefore do not explain the v448 per-record reversals.','limit':'This closes only the pinned TASM32 5.0 option/version-emulation surface. It does not prove the historical TH04 producer was TASM or rule out another assembler binary/source organization.'};rp=out/'receipt.json';rp.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({'receipt':str(rp),'receipt_sha256':sha(rp.read_bytes()),'real_variants':len(real),'version_ids':len(VERSION_IDS),'all_fixupp_directions':'ascending'},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
