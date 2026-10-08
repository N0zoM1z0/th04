#!/usr/bin/env python3
"""Original MAIN Game Over owner, fades, delays and key-wait CPU controls.

Game Over, cell fades, frame-delay/key loops and palette fade execute original
instructions at two loads. Keyboard sampling, vsync, TRAM, palette hardware,
ranking-save, HUD, song fade and process execution are explicit ABI adapters.
This accepts ordered component requests/refreshes; it does not accept pixels,
physical timing/audio, live MAIN suspension, or actual Continue score writes.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn.x86_const import *
from verify_gameover import Original as MenuOriginal
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(MenuOriginal):
 def event(self,*args,**kwargs):
  super().event(*args,**kwargs);self.events[-1]=f'{self.clock} '+self.events[-1]
 def body(self,u,address,size,unused):
  actual=u.reg_read(UC_X86_REG_CS);pair=(actual+self.delta,address-actual*16)
  sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  def ret(far=True,args=0):
   raw=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
   u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args)
   if far:u.reg_write(UC_X86_REG_CS,raw[1])
   u.reg_write(UC_X86_REG_IP,raw[0])
  if pair==(0x330e,0xd7):
   assert words(1)==(1,);self.event(5,value=1);return
  if pair==(0x330e,0xe0):
   bp=u.reg_read(UC_X86_REG_BP);frames=struct.unpack('<H',u.mem_read(0x70000+bp+6,2))[0]
   counter=self.read(0x2ab2,'H')[0]
   if counter<frames:
    self.clock+=1;assert self.clock<len(self.keys),'Game Over fixture exhausted'
    self.write(0x2ab2,'H',counter+1)
   return
  if pair==(0x330e,0x133):assert words(1)==(0,);self.event(6);return
  if pair==(0x2000,0x2462):
   self.clock+=1;assert self.clock<len(self.keys),'palette fixture exhausted';ret();return
  if pair==(0x2000,0x1f04):self.event(4,value=self.read(0x3a4,'H')[0]);ret();return
  if pair==(0x2000,0x666):assert words(1)==(4,);self.event(13,value=4);return
  if pair==(0x2aaf,0x3b6d):
   assert u.mem_read(0x90030,1)==b'\0';self.event(16);return
  if pair==(0x330e,0x2fc):assert words(1)==(0x204,);self.event(12,value=4);ret(True,2);return
  if pair==(0x2000,0x22f6):
   attr,off,seg,y,x=words(5);raw=bytes(u.mem_read(seg*16+off,3));assert raw==b'  \0'
   self.event(1,x,y,0,attr,raw[:2]);ret(True,10);return
  if pair in ((0x2aaf,0x625b),(0x2aaf,0x6287)):
   self.event(2 if pair[1]==0x625b else 3);ret(False);return
  if pair==(0x2aaf,0x3d0d):
   off,seg=words(2);assert bytes(u.mem_read(seg*16+off,6))==b'maine\0'
   self.event(14);self.route=1;self.stopped=True;u.emu_stop();return
  if pair==(0x2aaf,0xcf4):
   self.event(15);self.route=2;self.stopped=True;u.emu_stop();return
  super().body(u,address,size,unused)
 def run_scene(self,values,keys):
  stage,lives,bombs,initial=values[:4];v=values[4:]
  self.reset();self.events=['BEGIN'];self.error=None;self.clock=0;self.keys=[initial,*keys]
  self.initial=initial;self.initial_reset=False;self.selected=0;self.previous=1;self.stopped=False;self.route=0
  self.write(0x5394,'B',stage);self.write(0x3a4,'H',100)
  for at,fmt,value in zip((0x4664,0x2396,0x4676,0xbccc),('B','h','B','H'),v[:4]):self.write(at,fmt,value)
  self.u.mem_write(0x90000,bytes(256));self.write(0xba86,'HH',0,0x9000)
  for at,value in [(0xb,v[4]),(0xc,lives),(0xd,v[5]),(0xe,bombs),(0x30,255)]:self.u.mem_write(0x90000+at,bytes([value]))
  self.write(0x435a,'II',v[6],v[7]);self.write(0x4359,'B',v[8]);self.write(0x1a66,'BB',v[9],v[10])
  for index,at in enumerate((0x4349,0x4351,0x1ebe,0x1ec6)):self.u.mem_write(0x80000+at,bytes(v[11+index*8:19+index*8]))
  cs=0x2aaf-self.delta
  for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                    (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)]:self.u.reg_write(reg,value)
  self.u.mem_write(0x7e000,struct.pack('<HH',0xf000,cs))
  try:self.u.emu_start(cs*16+0x3a51,cs*16+0xf000,count=3000000)
  except Exception:
   if self.error:raise RuntimeError('Game Over scene adapter rejected') from self.error
   raise
  if self.error:raise RuntimeError('Game Over scene adapter rejected') from self.error
  if not self.stopped:assert self.u.reg_read(UC_X86_REG_IP)==0xf000 and self.u.reg_read(UC_X86_REG_SP)==0xe002
  state=[self.read(0x3a4,'H')[0],self.read(0x4664,'B')[0],self.read(0x4676,'B')[0],
         self.u.mem_read(0x9000b,1)[0],self.u.mem_read(0x9000d,1)[0],self.read(0x4349,'B')[0]]
  self.events.append('END '+' '.join(map(str,[self.route,self.clock,*state])))
  return self.events

def fixtures():
 for stage,used,profile in itertools.product((0,4,5,6),(0,2,3,255),range(4)):
  def held(clock):
   t=clock-95
   if profile==0:return 0x20 if 2<=t<6 or t>=9 else 0
   if profile==1:return 0x20 if t<7 or 16<=t<20 or t>=23 else 0
   if profile==2:return 0x20 if 301<=t<305 or t>=308 else 0
   return 0x20 if 2<=t<6 else (0x1000 if t>=9 else 0)
  initial=held(0);keys=[held(t) for t in range(1,650)]
  yield [stage,3,2,initial,128,42,7,1280,1,0,12345,67890,137,5,1,
         used,9,8,7,6,5,4,3,*range(8),*range(8,16),*range(16,24)],keys

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['target','exe','output-dir']:p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh output directory')
 out.mkdir(parents=True);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 cases=list(fixtures());expected=[]
 for load in (0x1000,0x2000):
  original=Original(a.target.read_bytes(),load);trace=[]
  for values,keys in cases:trace+=original.run_scene(values,keys)
  if expected:assert trace==expected,'load metamorphism changed Game Over'
  else:expected=trace
 fixture=out/'fixtures.txt';fixture.write_text('\n'.join(' '.join(map(str,v))+' '+','.join(map(str,k)) for v,k in cases)+'\n')
 ref=out/'original.txt';ref.write_text('\n'.join(expected)+'\n')
 result=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--gameover-scene',str(fixture)],
                       text=True,capture_output=True,check=True,timeout=240)
 (out/'native.txt').write_text(result.stdout)
 for row,(x,y) in enumerate(itertools.zip_longest(result.stdout.splitlines(),expected)):
  if x!=y:
   (out/'mismatch.json').write_text(json.dumps(dict(row=row,native=x,original=y),indent=2)+'\n')
   raise ValueError(f'Game Over scene differs at row {row}')
 assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,
              target_sha256=sha(original.target),executable_sha256=sha(a.exe.read_bytes()),cases=len(cases),records=len(expected),
              load_segments=[0x1000,0x2000],extent='MAIN relative0AAF:3971..3CEE and relative0000:0666..06A3',
              extents_sha256={name:sha(original.target[6144+lo:6144+hi]) for name,lo,hi in
                [('gameover',0xe461,0xe7de),('palette-blackout',0x666,0x6a3),('key-wait',0x13213,0x13267)]},
              fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(ref.read_bytes()),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['passed','cases','records']}))
if __name__=='__main__':main()
