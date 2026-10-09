#!/usr/bin/env python3
"""Actual options/Music Room/revisit/menu/ordinary MAIN with original controls.

Music Room caller and animation instructions execute at two relocated loads;
actual font/convex DDA kernels compare sampled complete BMPs. The original
parent suffix0A74:087A..0905 independently checks menu resource requests and
Game selection. Native initial pages, preceding PI decode, graphics storage,
files/input/waits and sound remain explicit adapters. No physical audio/timing,
whole OP loop, natural full route, current Windows or exact claim follows.
"""
import argparse,hashlib,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image
from unicorn.x86_const import *
from verify_op_music import Original
from verify_op_music_pixels import Raster
from verify_cutscene import ending_assets
from verify_maine_join import return_to_caller
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
def parse(line):
 w=line.split();c=list(map(int,w[:3]))+[bytes.fromhex(s) if s!='-' else b'' for s in w[3:5]]
 raw=bytes.fromhex(w[5]);c.append(list(struct.unpack('<'+'H'*(len(raw)//2),raw)));return c
class Parent(Original):
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
  if pair[0]==0xa74 and 0x87a<=pair[1]<0x906:return
  if pair==(0xa74,0x2557):self.emit('main_cdg_load');return_to_caller(u,far=False);return
  if pair==(0xda1,0xed):
   off,seg,slot=struct.unpack('<3H',u.mem_read(0x70000+sp+4,6));name=bytes(u.mem_read(seg*16+off,16)).split(b'\0')[0]
   assert name==b'op1.pi' and slot==0;self.loaded=name;self.write(0x2370,'HH',0x4000,0x9000);self.emit('load',data=name);return_to_caller(u,6);return
  super().body(u,address)
 def restore(self):
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data);self.write(0x9b,'B',3);self.write(0x106,'B',1);self.write(0x1a68,'B',1);self.write(0x5c4,'I',0x87654321)
  self.clock=0;self.events=[];self.loaded=None;self.error=None;self.done=False
  for reg,v in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
  # This suffix begins after main_update_and_render's PUSH BP/MOV BP,SP/PUSH SI.
  # Supply its live frame, rather than a fresh function-entry stack.
  u.reg_write(UC_X86_REG_SP,0xeffc);u.reg_write(UC_X86_REG_BP,0xeffe)
  u.mem_write(0x7effc,struct.pack('<3H',0,0,0xff00));u.emu_start(self.cs*16+0x87a,0x10ffff,count=20000)
  if self.error:raise self.error
  assert self.done and self.loaded is None and u.reg_read(UC_X86_REG_SP)==0xf002
  assert (self.read(0x9b,'B')[0],self.read(0x106,'B')[0],self.read(0x1a68,'B')[0])==(0,0,0) and self.read(0x5c4,'I')[0]==0x87654321
  result=[]
  for line in self.events:
   w=line.split();kind=w[0]
   if kind=='load':result.append('load '+bytes.fromhex(w[6]).decode())
   elif kind in ('tone','access','copy'):result.append(kind+' '+w[2])
   else:result.append(kind)
  return result
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','exe','hdi','font-bmp','pixel-reference-dir','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--scores-file',type=Path);p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);inputs=out/'inputs';inputs.mkdir()
 if a.reference_dir:
  previous=json.loads((a.reference_dir/'receipt.json').read_text());assert previous['passed']
  for f in (a.reference_dir/'inputs').iterdir():(inputs/f.name).write_bytes(f.read_bytes())
 else:
  assert a.scores_file and a.scores_file.is_file();(inputs/'scores.SCR').write_bytes(a.scores_file.read_bytes());cases=[]
  for rank in (0,3):
   for scenario in range(3):
    keys=[0]*120
    if scenario==0:keys[3:8]=[2]*5;keys[10:16]=[0x20]*6;keys[55:62]=[0x1000]*7
    elif scenario==1:keys[3:8]=[1]*5;keys[10:16]=[0x20]*6
    else:keys[4]=0x1020
    name=f'rank{rank}-input{scenario}';cases.append(f'{name} {rank}');(inputs/(name+'.keys')).write_bytes(struct.pack('<'+'H'*len(keys),*keys))
  (inputs/'cases.txt').write_text('\n'.join(cases)+'\n')
 command=[str(a.exe.resolve()),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font_bmp.resolve()),'--mute','--pmd-driver','none','--save-dir',str(inputs),'--op-music-checks',str(out/'scenes')]
 r=subprocess.run(command,capture_output=True,timeout=180);(out/'native.txt').write_bytes(r.stdout);(out/'stderr.txt').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode()
 if a.reference_dir:originals=None;raster=None;parent=None
 else:
  originals=[Original(a.target,a.decoded_dir,load) for load in (0x1000,0x2000)];parents=[Parent(a.target,a.decoded_dir,load) for load in (0x1000,0x2000)]
  results=[o.restore() for o in parents];assert results[0]==results[1];parent=results[0];(out/'original-parent.json').write_text(json.dumps(parent,indent=2)+'\n')
  assets=ending_assets(a.hdi);body=(a.pixel_reference_dir/'assets'/'MUSIC.PI.decoded').read_bytes();packed=np.frombuffer(body[56:],dtype=np.uint8).reshape(400,320);pixels=np.empty((400,640),dtype=np.uint8);pixels[:,::2]=packed>>4;pixels[:,1::2]=packed&15
  raster=Raster(a.target,a.decoded_dir,assets,{'MUSIC.PI':(body[8:56],pixels)},a.font_bmp)
 records=[];snapshots=0
 for location in sorted((out/'scenes').iterdir()):
  for visit in sorted(location.glob('visit*')):
   observed=(visit/'events.txt').read_text().splitlines()
   if originals:
    c=parse((visit/'caller.txt').read_text());expected=[o.run(c) for o in originals];assert expected[0]==expected[1] and observed==expected[0],visit
    assert (visit/'parent.txt').read_text().splitlines()==parent,visit
    (visit/'original.txt').write_text('\n'.join(expected[0])+'\n');raster.reset();cursor=0
    for picture in sorted(visit.glob('tick*.bmp'),key=lambda p:int(p.stem[4:])):
     tick=int(picture.stem[4:])
     while cursor<len(observed)-1 and int(observed[cursor].split()[1])<=tick:raster.apply(observed[cursor]);cursor+=1
     expected=raster.bytes()[512048:];actual=Image.open(picture).convert('RGB').tobytes()
     if actual!=expected:
      at=next(i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y)
      (out/'mismatch.json').write_text(json.dumps(dict(scene=location.name,visit=visit.name,tick=tick,rgb_offset=at),indent=2)+'\n');raise ValueError('Music frontend original pixels differ')
     snapshots+=1
   else:
    ref=a.reference_dir/'scenes'/location.name/visit.name
    for file in visit.rglob('*'):
     if file.is_file():assert file.read_bytes()==(ref/file.relative_to(visit)).read_bytes(),file
   records.append(dict(scene=location.name,visit=visit.name,trace_sha256=sha((visit/'events.txt').read_bytes())))
  assert (location/'save'/'GENSOU.SCR').read_bytes()==(inputs/'scores.SCR').read_bytes()
  if a.reference_dir:
   ref=a.reference_dir/'scenes'/location.name
   assert (location/'save'/'GENSOU.SCR').read_bytes()==(ref/'save'/'GENSOU.SCR').read_bytes()
 assert len(records)==12 and source_manifest(root)[0]==manifest
 outputs={f.relative_to(out/'scenes').as_posix():sha(f.read_bytes()) for f in sorted((out/'scenes').rglob('*')) if f.is_file() and f.name!='original.txt'}
 receipt=dict(passed=True,source_manifest=manifest,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),original_cpu_reexecuted=bool(originals),original_kernel_calls=raster.calls if raster else 0,
  original_bmp_controls=snapshots,reference_dir=str(a.reference_dir) if a.reference_dir else None,cases=records,loads=['1000','2000'],muted=True,command=command,outputs=outputs,
  hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),scores_sha256=sha((inputs/'scores.SCR').read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('OP Music/menu/revisit/ordinary MAIN PASS',len(records),'visits;',snapshots,'original BMPs')
if __name__=='__main__':main()
