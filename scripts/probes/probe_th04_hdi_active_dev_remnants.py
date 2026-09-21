#!/usr/bin/env python3
"""Audit active files/archives in pinned HDI for TH04 development remnants.

This complements v413-v416, which cover deleted/free/slack space. It reads only
the already supplied hash-attested HDI, walks active FAT12 directories, and
inspects active LZH member tables. No bytes are promoted as source or target.
"""
from __future__ import annotations
import argparse, hashlib, json, math, struct, sys, tempfile, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve(); sys.path[0:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/probes')]
from lib.pc98 import parse_fat_boot_sector
from probe_th04_hdi_deleted_builds import parse_directory, parse_lzh_level01
PARTITION_OFFSET=38912
DEV_EXT={'C','CPP','H','HPP','ASM','OBJ','MAP','PRJ','MAK','LST','SYM','LIB','BAK'}
TRIAL_NAMES={'GEN_TS1.EXE','MAIN.EXE','OP.EXE','MAINE.EXE','ZUN.COM'}
EXPECTED_ENTRY_COUNT=170; EXPECTED_FILE_COUNT=164; EXPECTED_DIR_COUNT=6
EXPECTED_LZH={'GENSO/CANBE.LZH':['PMDPPZ.COM','GAMECB.BAT'],'GENSO/OMAKE2.LZH':['','MUSIC.TXT','HUU1_86.M','HUU5B_86.M','YUME1_86.M','YUNE9_86.M','YUMEED86.M','GEN4_86.M','GEN4_26.M','GEN4B_86.M','GEN4B_26.M','GEN5_86.M','GEN5_26.M','GEN6B_86.M','GEN6B_26.M']}
def dg(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def outdir(p:Path|None)->Path:
 if p is None:
  d=PRIVATE/'reconstruction/probes'; d.mkdir(parents=True,exist_ok=True); return Path(tempfile.mkdtemp(prefix='hdi-active-dev-',dir=d))
 p=p.resolve()
 if p.exists() or not p.is_relative_to(PRIVATE): raise ValueError('output must be new below .analysis')
 p.mkdir(parents=True); return p

def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--output-dir',type=Path); a=ap.parse_args(); out=outdir(a.output_dir)
 rt=tomllib.loads((ROOT/'config/runtime.toml').read_text()); row=rt['image']; img=(ROOT/row['path']).read_bytes()
 if len(img)!=row['size'] or dg(img)!=row['sha256']: raise ValueError('HDI identity drift')
 boot=parse_fat_boot_sector(img,PARTITION_OFFSET); bps=boot.bytes_per_sector; spc=boot.sectors_per_cluster; cs=bps*spc
 root_sectors=math.ceil((boot.root_entries*32)/bps); fat0=PARTITION_OFFSET+boot.reserved_sectors*bps; root_off=PARTITION_OFFSET+(boot.reserved_sectors+boot.fat_count*boot.fat_sectors)*bps; root_size=boot.root_entries*32; data_off=root_off+root_size; fat=img[fat0:fat0+boot.fat_sectors*bps]
 def f12(c:int)->int:
  o=c+c//2; v=fat[o]|(fat[o+1]<<8); return ((v>>4)&0xfff) if c&1 else (v&0xfff)
 def coff(c:int)->int:return data_off+(c-2)*cs
 def chain(c:int)->list[int]:
  out=[]; seen=set()
  while 2<=c<0xff8 and c not in seen:
   seen.add(c); out.append(c); c=f12(c)
  return out
 def read(c:int)->bytes:return b''.join(img[coff(x):coff(x)+cs] for x in chain(c))
 entries=[]
 def walk(raw:bytes,owner:str)->None:
  for r in parse_directory(raw,owner):
   if r['deleted'] or r['name'] in ('.','..'): continue
   path=(owner+'/'+str(r['name'])) if owner else str(r['name']); rr=dict(r); rr['path']=path; entries.append(rr)
   if r['is_directory'] and int(r['start_cluster'])>=2: walk(read(int(r['start_cluster'])),path)
 walk(img[root_off:root_off+root_size],'')
 files=[r for r in entries if not r['is_directory']]; dirs=[r for r in entries if r['is_directory']]
 if (len(entries),len(files),len(dirs))!=(EXPECTED_ENTRY_COUNT,EXPECTED_FILE_COUNT,EXPECTED_DIR_COUNT): raise ValueError('active inventory count drift')
 dev=[]; active_trial=[]; archives={}
 for r in files:
  name=str(r['name']); up=name.upper(); ext=up.rsplit('.',1)[1] if '.' in up else ''
  if ext in DEV_EXT: dev.append(r['path'])
  if up in TRIAL_NAMES and not str(r['path']).startswith('GENSO/'):
   active_trial.append(r['path'])
  if up.endswith('.LZH'):
   raw=read(int(r['start_cluster']))[:int(r['size'])]; members,end=parse_lzh_level01(raw,0); names=[str(m['name']) for m in members]; archives[str(r['path'])]={'sha256':dg(raw),'size':len(raw),'member_names':names,'member_count':len(names),'terminator_offset':end}
   if names!=EXPECTED_LZH.get(str(r['path'])): raise ValueError(f'active LZH inventory drift: {r["path"]}')
   for m in names:
    u=m.upper(); e=u.rsplit('.',1)[1] if '.' in u else ''
    if e in DEV_EXT or u in TRIAL_NAMES: dev.append(str(r['path'])+'::'+m)
 if dev: raise ValueError(f'development/trial artifacts unexpectedly present: {dev}')
 # The active GENSO release executables are expected, but no trial-named GEN_TS1 exists.
 gen_ts=[r['path'] for r in files if str(r['name']).upper()=='GEN_TS1.EXE']
 if gen_ts: raise ValueError('active GEN_TS1 unexpectedly present')
 rec={'schema_version':1,'claim_scope':'pinned HDI active-file and active-archive TH04 development-remnant provenance search','image_sha256':dg(img),'active_entry_count':len(entries),'active_file_count':len(files),'active_directory_count':len(dirs),'development_extension_hits':dev,'active_gen_ts1_hits':gen_ts,'active_lzh':archives,'conclusion':'The active FAT12 filesystem contains no C/C++/ASM/object/map/project/build remnants and no GEN_TS1 trial executable. The only active LZH archives are GENSO/CANBE.LZH (PMD compatibility) and GENSO/OMAKE2.LZH (music/text data); neither contains TH04 executables or development files.','limit':'This covers active directory-visible files and active LZH member tables only. Deleted/free/slack space is covered separately by v413-v416. Negative provenance only; no exactness credit.'}; rp=out/'receipt.json'; rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':dg(rp.read_bytes()),'files':len(files),'dirs':len(dirs),'archives':list(archives)},ensure_ascii=False,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
