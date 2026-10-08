#!/usr/bin/env python3
"""Original MAIN Continue menu versus native input, requests and reset state.

Original menu and score-reset instructions execute at two loads. Input,
ranking-save, HUD/shot-level/TRAM calls have explicit ABI adapters; no live
Game Over, actual ranking-save or pixel/timing/audio acceptance follows.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn.x86_const import *
from verify_player_lifecycle import Original as Base
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
 def event(self,kind,x=0,y=0,value=0,attr=0,data=b''):
  self.events.append(f'{kind} {x} {y} {value} {attr} '+(data.hex() if data else '-'))
 def body(self,u,address,size,unused):
  actual=u.reg_read(UC_X86_REG_CS);cs=actual+self.delta;ip=address-actual*16;sp=u.reg_read(UC_X86_REG_SP)
  def words(n,far=True):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+(4 if far else 2),n*2))
  def ret(far=True,args=0):
   values=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
   u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args)
   if far:u.reg_write(UC_X86_REG_CS,values[1])
   u.reg_write(UC_X86_REG_IP,values[0])
  pair=(cs,ip)
  if pair==(0x2aaf,0x3ca6):
   self.selected=u.reg_read(UC_X86_REG_DI);self.previous=u.reg_read(UC_X86_REG_SI)
  if pair==(0x2000,0x1b50):
   attr,off,seg,y,x=words(5);assert seg==0x8000
   raw=bytes(u.mem_read(seg*16+off,32));assert b'\0' in raw
   self.event(0,x,y,0,attr,raw.split(b'\0',1)[0]);ret(True,10);return
  if pair==(0x2000,0x1b0c):
   attr,value,y,x=words(4);self.event(0,x,y,value,attr);ret(True,8);return
  if pair==(0x330e,0x6bc):
   sample=self.initial if self.initial_reset else self.keys[self.clock]
   self.initial_reset=False;self.write(0x3974,'H',sample);ret();return
  if pair==(0x330e,0x6c4):
   self.write(0x3974,'H',self.read(0x3974,'H')[0]|self.keys[self.clock]);ret();return
  if pair==(0x330e,0xd7):
   assert words(1)==(1,);self.event(5,value=1)
   self.events.append(f'FRAME {self.clock} {u.reg_read(UC_X86_REG_DI)} {u.reg_read(UC_X86_REG_SI)}')
   self.clock+=1;assert self.clock<len(self.keys),'unconfirmed original menu fixture';ret(True,2);return
  adapters={(0x2aaf,0x81c5):(7,False),(0x2aaf,0x72f6):(8,True),
            (0x2aaf,0x43f8):(9,True),(0x2aaf,0x44b1):(10,True),(0x2aaf,0x6ba2):(11,False)}
  if pair in adapters:
   kind,far=adapters[pair];self.event(kind);ret(far);return
 def run(self,values,keys):
  stage,lives,bombs,initial=values[:4];v=values[4:]
  self.reset();self.events=['BEGIN'];self.error=None;self.clock=0;self.keys=keys
  self.initial=initial;self.initial_reset=True;self.selected=0;self.previous=1
  self.write(0x5394,'B',stage)
  for at,fmt,value in zip((0x4664,0x2396,0x4676,0xbccc),('B','h','B','H'),v[:4]):self.write(at,fmt,value)
  self.u.mem_write(0x90000,bytes(256));self.write(0xba86,'HH',0,0x9000)
  for at,value in [(0xb,v[4]),(0xc,lives),(0xd,v[5]),(0xe,bombs)]:self.u.mem_write(0x90000+at,bytes([value]))
  self.write(0x435a,'II',v[6],v[7]);self.write(0x4359,'B',v[8]);self.write(0x1a66,'BB',v[9],v[10])
  for index,at in enumerate((0x4349,0x4351,0x1ebe,0x1ec6)):self.u.mem_write(0x80000+at,bytes(v[11+index*8:19+index*8]))
  self.u.reg_write(UC_X86_REG_SI,1);self.u.reg_write(UC_X86_REG_DI,0)
  try:choice=self.call(0x3b8a,cs=0x2aaf-self.delta)
  except Exception:
   if self.error:raise RuntimeError('Continue adapter rejected') from self.error
   raise
  if self.error:raise RuntimeError('Continue adapter rejected') from self.error
  state=[self.read(0x4664,'B')[0],self.read(0x4676,'B')[0],self.read(0x2396,'h')[0],self.read(0xbccc,'H')[0],
         self.u.mem_read(0x9000b,1)[0],self.u.mem_read(0x9000d,1)[0]]
  state+=[b for at in (0x4349,0x4351,0x1ebe,0x1ec6) for b in self.u.mem_read(0x80000+at,8)]
  state+=[*self.read(0x435a,'II'),self.read(0x4359,'B')[0],self.read(0x1a66,'B')[0],self.read(0x1a67,'B')[0]]
  self.events.append('END '+' '.join(map(str,[1 if choice==0 else 2,self.selected,self.clock,self.previous,*state])))
  return self.events

def fixtures():
 profiles=[(0,[0,0x20]),(0,[0,0x2000]),(0,[0,0x1000]),
  (0,[0,1,0,0,0x20]),(0,[0,2,0,0,0x20]),(0,[0,3,0,0,0x20]),
  (0,[0,1|0x20]),(0,[0,1|0x1000|0x2000]),(0,[0,0x20|0x1000]),
  (0x20,[0x20]*33+[0,0,0x20]),(0x1000,[0x1000,0x2000,0x20,0,0,0x20]),
  (0,[0,1,2,0,0,1,0,0,0x2000]),(0,[0]*100+[0x20])]
 for stage,used,credit,profile in itertools.product((0,1,4,5,6),(0,1,2,3,4,255),(0,1,3,255),profiles):
  initial,keys=profile
  power=128;digits=[used,9,8,7,6,5,4,3]
  yield [stage,credit,2,initial,power,42,7,1280,1,0,12345,67890,137,5,1,*digits,*range(8),*range(8,16),*range(16,24)],keys
 for key in range(0x4000):
  if key%37:continue
  # A chord may remain unconfirmed, so append a released, explicit Shot.
  yield [0,3,2,0,1,-32768,0,65535,255,255,12345,67890,255,255,255,*([4]+[255]*7),*([255]*8),*([255]*8),*([255]*8)],[0,key,0,0,0x20]

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['target','exe','output-dir']:p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh output directory')
 out.mkdir(parents=True);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 cases=list(fixtures());expected=[];inputs=[]
 for load in (0x1000,0x2000):
  original=Original(a.target.read_bytes(),load);trace=[]
  for values,keys in cases:trace+=original.run(values,keys)
  if expected:assert trace==expected,'load metamorphism changed Continue menu'
  else:expected=trace
 for values,keys in cases:inputs.append(' '.join(map(str,values))+' '+','.join(map(str,keys)))
 fixture=out/'fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n')
 ref=out/'original.txt';ref.write_text('\n'.join(expected)+'\n')
 command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--gameover-menu',str(fixture)]
 result=subprocess.run(command,text=True,capture_output=True,check=True,timeout=240)
 (out/'native.txt').write_text(result.stdout);actual=result.stdout.splitlines()
 for row,(x,y) in enumerate(itertools.zip_longest(actual,expected)):
  if x!=y:
   (out/'mismatch.json').write_text(json.dumps(dict(row=row,native=x,original=y),indent=2)+'\n')
   raise ValueError(f'Continue menu differs at row{row}')
 assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,
              target_sha256=sha(original.target),executable_sha256=sha(a.exe.read_bytes()),cases=len(cases),records=len(expected),
              load_segments=[0x1000,0x2000],extent='MAIN relative0AAF:3B8A..3CEE',extent_sha256=sha(original.target[0xfe7a:0xffde]),
              fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(ref.read_bytes()),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['passed','cases','records']}))
if __name__=='__main__':main()
