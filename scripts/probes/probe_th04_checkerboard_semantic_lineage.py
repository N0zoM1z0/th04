#!/usr/bin/env python3
"""Scan registered TH01-TH05 target images for checkerboard-like LOOP cores.

The signature permits arbitrary ES source register, repeat count, dword source
register, and DI stride. It requires the semantic architecture of a fixed-count
ES:[DI] dword store loop followed by a DI row rewind and signed backedge. DIET
artifacts are restored using only the pinned local DIET/DOSBox-X toolchain.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve()
sys.path[0:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/probes')]
from lib.pc98 import parse_mz
from lib.targets import load_target_manifest,read_verified_artifact
from probe_th04_final_blocker_crossartifact import restore_diet
CORE=re.compile(rb'\x8e([\xc0-\xc7])\xb9(..)\x66\x26\x89([\x05\x0d\x15\x1d\x25\x2d\x35\x3d])\x83\xc7(.)\xe2(.)',re.S)
EXPECTED={'th04-main':[{'offset':0x120AF,'es_modrm':0xC2,'count':6,'store_modrm':0x05,'stride':8,'loop_rel':0xF7,'rewind_hex':'81ef80007dee'}]}
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def outdir(p:Path|None)->Path:
 if p is None:
  par=PRIVATE/'reconstruction/probes'; par.mkdir(parents=True,exist_ok=True); return Path(tempfile.mkdtemp(prefix='checker-lineage-',dir=par))
 r=p.resolve()
 if r.exists() or not r.is_relative_to(PRIVATE): raise ValueError('output must be new and below .analysis')
 r.mkdir(parents=True); return r
def program(raw:bytes)->tuple[bytes,str,int]:
 if raw[:2]==b'MZ':
  mz=parse_mz(raw)
  if not mz.valid: raise ValueError('invalid MZ')
  return mz.program_image,'mz',len(mz.relocations)
 return raw,'flat',0
def scan(b:bytes)->list[dict[str,object]]:
 out=[]
 for m in CORE.finditer(b):
  tail=b[m.end():m.end()+8]
  rm=re.match(rb'(\x81\xef..|\x83\xef.)(\x7d)(.)',tail,re.S)
  if not rm: continue
  out.append({'offset':m.start(),'es_modrm':m.group(1)[0],'count':int.from_bytes(m.group(2),'little'),'store_modrm':m.group(3)[0],'stride':m.group(4)[0],'loop_rel':m.group(5)[0],'rewind_hex':rm.group(0).hex()})
 return out
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--output-dir',type=Path); a=ap.parse_args(); out=outdir(a.output_dir)
 arts=load_target_manifest(ROOT/'config/targets.toml')['artifacts']; hits={}; ids={}; restored=0
 for art in arts:
  aid=str(art['id']); raw=read_verified_artifact(ROOT,art); meta=None
  if len(raw)>=0x20 and raw[0x1c:0x20].lower()==b'diet': raw,meta=restore_diet(art,raw,out); restored+=1
  img,fmt,rel=program(raw); found=scan(img)
  if found: hits[aid]=found
  ids[aid]={'target_sha256':str(art['sha256']),'container_was_diet':meta is not None,'restored_sha256':meta['restored_sha256'] if meta else None,'program_format':fmt,'program_image_size':len(img),'program_image_sha256':sha(img),'relocation_count':rel,'semantic_core_count':len(found)}
 if len(ids)!=20 or restored!=8: raise ValueError('registered corpus/DIET partition drift')
 if hits!=EXPECTED: raise ValueError(f'checker lineage drift: {hits}')
 rec={'schema_version':1,'claim_scope':'TH04 checkerboard semantic cross-game lineage negative','registered_artifact_count':len(ids),'diet_restored_artifact_count':restored,'signature':'MOV ES,r16; MOV CX,imm16; operand-size+ES dword MOV [DI],r32; ADD DI,imm8; LOOP rel8; then SUB DI,imm and signed JNL/JGE row backedge','hits':hits,'artifacts':ids,'conclusion':'Only TH04 MAIN contains the generalized fixed-count ES:[DI] dword-store LOOP plus row-rewind architecture. No registered TH01/TH02/TH03/TH05 artifact supplies an independent semantic analogue with different count/stride/register choices.','limit':'Negative lineage evidence only; not a universal source-language proof and not authorization for target-derived inline assembly.'}
 rp=out/'receipt.json'; rp.write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':sha(rp.read_bytes()),'hits':hits},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
