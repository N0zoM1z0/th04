#!/usr/bin/env python3
"""Project target-constrained packed relocation order onto current OMF FIXUPP records."""
from __future__ import annotations
import argparse, hashlib, json, sys, tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve(); sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/probes')]
from analyze_diet_relocation_owners import map_contributions
from lib.omf import describe_omf,parse_omf
from lib.pc98 import parse_mz
from replay_th04_scroll_driver_natural import fixup_locations,omf_index
EXPECTED={
 'th04-op':{
  'exe':'78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd','map':'cd2e0a35b1d1262dca398db0302ab68243179cf18edfac2e1ec0810acf2ef334','target':'40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d',
  'objects':{
   'th04/bgimage.cpp':('obj/th04/bgimage.obj','e6b51ddee67e1c0b7dd67ee431ea2a71b03886f1610dbfc1a3bda0addb176297','TC86 Borland C++ 4.02',8,[[33,8]],[[33,8]],{33:'reverse'}),
   'th04/hi_view.cpp':('obj/th04/hi_view.obj','e508835bcb046fad636484d6f59f2e75d043abb10caf77c8b5d30f69f6e9890c','TC86 Borland C++ 4.02',61,[[74,32],[76,29]],[[74,23],[76,29],[74,9]],{74:'rotate_left_9',76:'exact'}),
   'th04_op_master_data_tail.asm':('obj/th04/opmdata.obj','16784662a8912439cbe055d3656e6338dd336ed11040e2166e336ed8244e2d35','Turbo Assembler  Version 5.0',4,[[154,4]],[[154,4]],{154:'reverse'}),
   'th04_op_music_master.asm':('obj/th04/opmusicm.obj','0e1f644354036bea04bdb4138d6b83c915e9c93473c39eafe4d574d03c3056e7','Turbo Assembler  Version 5.0',35,[[64,30],[66,5]],[[64,30],[66,5]],{64:'reverse',66:'reverse'}),}},
 'th04-maine':{
  'exe':'9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60','map':'1dd895faa6c7fbfc537c2d56a95ff5ea693aa923b7f5701bb922f170dbfae4e0','target':'6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533',
  'objects':{
   'th04/bgimage.cpp':('obj/th04/bgimage.obj','e6b51ddee67e1c0b7dd67ee431ea2a71b03886f1610dbfc1a3bda0addb176297','TC86 Borland C++ 4.02',8,[[33,8]],[[33,8]],{33:'reverse'}),
   'th04_maine.asm':('obj/th04/maine.obj','f4f3358c8da054e59ac7ca278cae7dc4bb25fe1567d8f5478beafe57cd6126f2','Turbo Assembler  Version 5.0',175,[[128,43],[130,44],[132,18],[134,17],[136,17],[138,10],[140,22],[142,4]],[[128,43],[132,2],[130,44],[132,10],[134,2],[132,6],[134,15],[136,17],[140,11],[138,10],[142,4],[140,11]],{128:'other',130:'other',132:'other',134:'other',136:'other',138:'reverse',140:'other',142:'reverse'}),
   'th04_maine_master_data_tail.asm':('obj/th04/mainemdata.obj','061fe40749de44f9bb43c7ded1c36f8a467837c4d1950cf2a10c49794a017499','Turbo Assembler  Version 5.0',4,[[111,4]],[[111,4]],{111:'reverse'}),}}}
def sha(b): return hashlib.sha256(b).hexdigest()
def outdir(p):
 if p is None:
  q=PRIVATE/'reconstruction/probes';q.mkdir(parents=True,exist_ok=True);return Path(tempfile.mkdtemp(prefix='packed-fixupp-',dir=q))
 q=p.resolve()
 if q.exists() or not q.is_relative_to(PRIVATE): raise ValueError('output must be new and below .analysis')
 q.mkdir(parents=True);return q
def omf_fixups(path):
 rec=parse_omf(path.read_bytes());names=[''];segs=[];out=defaultdict(list)
 for r in rec:
  if r.record_type==0x96:
   p=0
   while p<len(r.data): n=r.data[p];names.append(r.data[p+1:p+1+n].decode('latin1'));p+=n+1
  elif r.record_type==0x98:
   d=r.data;p=1+(3 if d[0]>>5==0 else 2);ni,p=omf_index(d,p);segs.append(names[ni])
 for i,r in enumerate(rec):
  if r.record_type!=0xA0: continue
  si,p=omf_index(r.data,0);base=int.from_bytes(r.data[p:p+2],'little');j=i+1
  while j<len(rec) and rec[j].record_type==0x9c:
   for kind,loc in fixup_locations(rec[j].data):
    if kind==3: out[segs[si-1]].append((base+loc+2,j+1,base+loc))
   j+=1
 return out
def runs(xs):
 out=[]
 for x in xs:
  if not out or out[-1][0]!=x: out.append([x,1])
  else: out[-1][1]+=1
 return out
def relation(a,b):
 if a==b:return 'exact'
 if a[::-1]==b:return 'reverse'
 for k in range(1,len(a)):
  if a[k:]+a[:k]==b:return f'rotate_left_{k}'
 return 'other'
def index_runs(a,b):
 pos={v:i for i,v in enumerate(a)};seq=[pos[v] for v in b];out=[];i=0
 while i<len(seq):
  d=(seq[i+1]-seq[i]) if i+1<len(seq) and abs(seq[i+1]-seq[i])==1 else 0;j=i+1
  while d and j<len(seq) and seq[j]-seq[j-1]==d:j+=1
  out.append([seq[i],seq[j-1],j-i,d]);i=j
 return out
def inspect(artifact,src,target_path):
 e=EXPECTED[artifact];stem=artifact.removeprefix('th04-');ep=src/f'bin/th04/{stem}.exe';mp=src/f'obj/th04/{stem}.map';eb=ep.read_bytes();mb=mp.read_bytes();tb=target_path.read_bytes()
 if (sha(eb),sha(mb),sha(tb))!=(e['exe'],e['map'],e['target']): raise ValueError(f'{artifact}: input identity drift')
 cm=parse_mz(eb);tm=parse_mz(tb);cs=[r.linear for r in cm.relocations];ts=[r.linear for r in tm.relocations];con=map_contributions(mb);owner={};row={}
 for s in cs:
  m=[x for x in con if x['start']<=s<x['end']]
  if len(m)!=1:raise ValueError(f'{artifact}: ambiguous MAP owner {s:#x}')
  owner[s]=str(m[0]['module']);row[s]=m[0]
 result={}
 for mod,(rel,objsha,translator,count,cr,tr,rels) in e['objects'].items():
  op=src/rel;ob=op.read_bytes();desc=describe_omf(ob)
  if sha(ob)!=objsha or desc['translator_comments']!=[translator]:raise ValueError(f'{artifact}/{mod}: OMF identity drift')
  lookup=defaultdict(list)
  for seg,items in omf_fixups(op).items():
   for local,rec,locat in items: lookup[(seg,local)].append((rec,locat))
  def annotate(seq):
   out=[]
   for s in seq:
    if owner[s]!=mod:continue
    r=row[s];seg=str(r['segment']);local=s-int(r['start']);m=lookup[(seg,local)]
    if len(m)!=1:raise ValueError(f'{artifact}/{mod}: OMF match drift at {s:#x}')
    out.append({'site':s,'segment':seg,'local':local,'record':m[0][0],'locat':m[0][1]})
   return out
  a,b=annotate(cs),annotate(ts)
  if len(a)!=count or len(b)!=count:raise ValueError(f'{artifact}/{mod}: relocation count drift')
  ar,br=runs([x['record'] for x in a]),runs([x['record'] for x in b])
  if ar!=cr or br!=tr:raise ValueError(f'{artifact}/{mod}: record-run drift')
  per={}
  for rec in sorted(set(x['record'] for x in a)):
   left=[x['local'] for x in a if x['record']==rec];right=[x['local'] for x in b if x['record']==rec];obs=relation(left,right)
   if obs!=rels[rec]:raise ValueError(f'{artifact}/{mod}/{rec}: relation {obs}')
   per[str(rec)]={'count':len(left),'relation':obs,'target_as_current_index_runs':index_runs(left,right)}
  result[mod]={'object_path':rel,'object_sha256':objsha,'translator':translator,'relocations':count,'current_record_runs':ar,'target_record_runs':br,'per_record':per}
 return {'candidate_sha256':e['exe'],'map_sha256':e['map'],'target_restored_sha256':e['target'],'objects':result}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--op-source-dir',type=Path,required=True);p.add_argument('--op-target-restored',type=Path,required=True);p.add_argument('--maine-source-dir',type=Path,required=True);p.add_argument('--maine-target-restored',type=Path,required=True);p.add_argument('--output-dir',type=Path);a=p.parse_args();out=outdir(a.output_dir)
 arts={'th04-op':inspect('th04-op',a.op_source_dir.resolve(),a.op_target_restored.resolve()),'th04-maine':inspect('th04-maine',a.maine_source_dir.resolve(),a.maine_target_restored.resolve())}
 rec={'schema_version':1,'observed_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'claim_scope':'candidate-MAP projection of target-constrained relocation order onto current OMF kind-3 FIXUPP records; no historical target-source ownership claim','artifacts':arts,'conclusion':'The packed order residual is heterogeneous. Current TASM5 master DATA and both OP music FIXUPP records require exact within-record reversal; current TC4J BGIMAGE also projects as one reversed record. OP hi_view instead keeps record 76 exact while record 74 rotates left by nine, yielding target runs 74x23,76x29,74x9. MAINE monolithic TASM mixes record interleaving with some exact record reversals. This separates producer FIXUPP-direction hypotheses from historical TU/object-ownership hypotheses.','limit':'Candidate MAP names and current OMF records are projection aids only. Historical target OMF files are unavailable; no MZ or object bytes are edited and no source/exact credit follows.'}
 rp=out/'receipt.json';rp.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({'receipt':str(rp),'receipt_sha256':sha(rp.read_bytes()),'hi_view_target_runs':arts['th04-op']['objects']['th04/hi_view.cpp']['target_record_runs'],'op_music_relations':{k:v['relation'] for k,v in arts['th04-op']['objects']['th04_op_music_master.asm']['per_record'].items()}},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
