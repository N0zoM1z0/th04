#!/usr/bin/env python3
"""Replay a natural MAINE master-object link order on the v401 topology candidate.

This diagnostic changes only TLINK input order among already-separated physical
master objects. It never edits relocation-table bytes. The target comparison is
the pinned DIET-restored MZ view, whose order is explicitly *not* claimed to be
the historical pre-DIET TLINK order.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, tempfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve(); sys.path[0:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/probes')]
from lib.pc98 import parse_mz
from probe_th04_master_object_split import build,compare,sha
BASE={
'Tupfile.lua':'c753fc557e97ac10872bd7a8a7a2f07200193082889fb78160edcfaf22915a8e',
'bin/th04/maine.exe':'8b4a3bb3e6985f729113967398b35cff2c9c4d32860b9034fc84b839e8862553',
'obj/th04/maine.map':'b85de8ddf0ec5ec17bc8a4554ddbee8903629877e71a45e92fd58f719f336217'}
REFERENCE_CANDIDATE_SHA='7e6b78861613cdd06d72e2f8584268444642b31abcc35d686c0ed1f4cc668f70'
NEW_EXE='9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60'; NEW_MAP='1dd895faa6c7fbfc537c2d56a95ff5ea693aa923b7f5701bb922f170dbfae4e0'
OLD='''\t{ "th04_maine_master.asm", o = "mainem.obj" },\n\t"vsorig.obj",\n\t{ "th04_maine_master_data_tail.asm", o = "mainemdata.obj" },\n\t{ "th04_maine_master_mid.asm", o = "mainemmid.obj" },\n\t{ "th04_maine_master_tail.asm", o = "mainemtail.obj" },\n'''
NEW='''\t{ "th04_maine_master.asm", o = "mainem.obj" },\n\t{ "th04_maine_master_mid.asm", o = "mainemmid.obj" },\n\t{ "th04_maine_master_tail.asm", o = "mainemtail.obj" },\n\t"vsorig.obj",\n\t{ "th04_maine_master_data_tail.asm", o = "mainemdata.obj" },\n'''
def dg(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def outdir(p:Path|None)->Path:
 if p is None:
  par=PRIVATE/'reconstruction/probes'; par.mkdir(parents=True,exist_ok=True); return Path(tempfile.mkdtemp(prefix='maine-reloc-order-',dir=par))
 r=p.resolve()
 if r.exists() or not r.is_relative_to(PRIVATE): raise ValueError('output must be new and below .analysis')
 r.mkdir(parents=True); return r
def sites(path:Path)->list[int]:
 m=parse_mz(path.read_bytes())
 if not m.valid: raise ValueError(f'invalid MZ: {path}')
 return [x.linear for x in m.relocations]
def order_metrics(c:list[int],t:list[int])->dict[str,object]:
 if Counter(c)!=Counter(t): raise ValueError('relocation multisets differ')
 dif=[i for i,(a,b) in enumerate(zip(c,t)) if a!=b]
 return {'count':len(c),'ordered_exact':not dif,'differing_indices':dif,'first_mismatch':dif[0] if dif else None,'last_mismatch':dif[-1] if dif else None,'same_index_count':sum(a==b for a,b in zip(c,t)),'mismatch_pairs':[[i,c[i],t[i]] for i in dif]}
def patch(work:Path)->None:
 p=work/'Tupfile.lua'; t=p.read_text()
 if t.count(OLD)!=1: raise ValueError('MAINE object-order anchor drift')
 p.write_text(t.replace(OLD,NEW,1))
def valid_payload(label:str,r:dict[str,object])->None:
 if r['payload_differing_bytes']!=2 or [x['start'] for x in r['payload_mismatch_runs']]!=[0xD1D3] or r['relocation_multiset_exact'] is not True or r['target_payload_size']!=r['candidate_payload_size']: raise ValueError(f'{label}: payload frontier drift')
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--source-dir',type=Path,required=True); ap.add_argument('--reference-candidate','--target-restored',dest='reference_candidate',type=Path,required=True); ap.add_argument('--output-dir',type=Path); a=ap.parse_args(); src=a.source_dir.resolve(); target=a.reference_candidate.resolve(); out=outdir(a.output_dir)
 for rel,h in BASE.items():
  p=src/rel
  if not p.is_file() or sha(p)!=h: raise ValueError(f'v401 baseline drift: {rel}')
 if not target.is_file() or sha(target)!=REFERENCE_CANDIDATE_SHA: raise ValueError('reference-candidate MZ identity drift')
 reference_sites=sites(target); baseline=order_metrics(sites(src/'bin/th04/maine.exe'),reference_sites)
 if baseline['differing_indices']!=list(range(42,55)): raise ValueError(f'baseline order drift: {baseline}')
 base_payload=compare('th04-maine',src); valid_payload('baseline',base_payload)
 builds={}
 for lab in ('a','b'):
  work=out/lab/'source'; shutil.copytree(src,work,symlinks=True); patch(work); build(work,out/f'build-{lab}.log')
  exe=work/'bin/th04/maine.exe'; mp=work/'obj/th04/maine.map'; payload=compare('th04-maine',work); valid_payload(lab,payload); metrics=order_metrics(sites(exe),reference_sites)
  if metrics['differing_indices']!=[48,49] or metrics['mismatch_pairs']!=[[48,0x2F59,0x2FE7],[49,0x2FE7,0x2F59]]: raise ValueError(f'{lab}: ordered residual drift: {metrics}')
  if sha(exe)!=NEW_EXE or sha(mp)!=NEW_MAP: raise ValueError(f'{lab}: output identity drift')
  builds[lab]={'exe_sha256':sha(exe),'map_sha256':sha(mp),'payload_comparison':payload,'relocation_order_vs_reference_candidate':metrics}
 for key in ('exe_sha256','map_sha256','relocation_order_vs_reference_candidate'):
  if builds['a'][key]!=builds['b'][key]: raise ValueError(f'A/B {key} differs')
 pa=dict(builds['a']['payload_comparison']); pb=dict(builds['b']['payload_comparison']); pa.pop('candidate_path',None); pb.pop('candidate_path',None)
 if pa!=pb: raise ValueError('A/B payload comparison differs')
 rec={'schema_version':1,'claim_scope':'TH04 MAINE natural master-object link-order diagnostic against the v231 candidate-inverse control; no target relocation-order or packed-file exactness claim','baseline_identity':BASE,'reference_candidate_sha256':REFERENCE_CANDIDATE_SHA,'baseline_relocation_order_vs_reference_candidate':baseline,'baseline_payload_comparison':base_payload,'object_order_before':['mainem.obj','vsorig.obj','mainemdata.obj','mainemmid.obj','mainemtail.obj'],'object_order_after':['mainem.obj','mainemmid.obj','mainemtail.obj','vsorig.obj','mainemdata.obj'],'builds':builds,'observed_effect':'Without editing any relocation table bytes, moving the two code-tail objects before the historical VS/data contributions reduces the v231 candidate-control ordered difference from 13 indices (42..54) to only indices 48..49 while preserving the two-byte snd_load-only payload residual and target-equal relocation multiset.','limit':'This comparison reference is the old v214 candidate recovered by DIET -RA, not a target-restored MZ. The two-entry difference is therefore only a candidate-to-candidate topology diagnostic and provides no target relocation-order acceptance claim.'}; rp=out/'receipt.json'; rp.write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':sha(rp),'baseline_mismatches':13,'reordered_mismatches':2,'candidate_sha256':NEW_EXE},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
