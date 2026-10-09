#!/usr/bin/env python3
"""Original MAIN third-dialogue departure at two relocated loads.

MAIN13A9:ACB3..AE86 executes. Dynamic clean, third dialogue and all-clear
children are ordered request adapters. Stop at the nonreturning end_extra
entry; do not fabricate a return into the ordinary leave/departure suffix.
This proves bounded departure fields/order, not whole MAIN or reward pixels.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_extra_handoff import Original as Base
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
 def __init__(self,target,load):
  super().__init__(target,load);self.ending=False;self.flow=[]
 def body(self,u,address,size):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs+self.delta,address-cs*16)
  if pair==(0x33a9,0xad25):self.flow.append('0 60')
  if pair==(0x2aaf,0x2bfb):self.flow.append('1 0')
  if pair==(0x33a9,0x9e06):self.flow.append('6 0')
  if pair==(0x2aaf,0xd1f):
   self.flow.append('8 0');self.ending=True;self.end_pair=pair;u.emu_stop();return
  super().body(u,address,size)
 def run(self,row):
  self.reset();self.error=None;self.ending=False;self.flow=[];self.requests=[];self.resources=[]
  frame,graze,stage_graze,tone,changed,x,y=row
  self.u.mem_write(0x90000,bytes(256));self.u.mem_write(0x90038,struct.pack('<H',graze))
  self.write(0xba86,'HH',0,0x9000);self.write(0x5394,'B',6);self.write(0x53d9,'<Bh',255,frame)
  self.write(0xbcde,'B',1);self.write(0xbcbc,'H',stage_graze)
  self.write(0x3a4,'h',tone);self.write(0x5393,'B',changed);self.write(0x4642,'hh',x,y)
  cs=0x33a9-self.delta;u=self.u
  for reg,val in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,val)
  u.mem_write(0x7e000,struct.pack('<H',0xf000));u.emu_start(cs*16+0xacb3,cs*16+0xf000,count=100000)
  if self.error:raise RuntimeError('Extra departure hook rejected') from self.error
  if self.ending:
   assert self.end_pair==(0x2aaf,0xd1f) and u.reg_read(UC_X86_REG_CS)==0x2aaf-self.delta and u.reg_read(UC_X86_REG_SP)==0xdffa
  else:assert u.reg_read(UC_X86_REG_IP)==0xf000 and u.reg_read(UC_X86_REG_SP)==0xe002
  assert self.requests==([['clean',128,256],['dialog'],['all_clear']] if frame==0 else []),self.requests
  assert not self.resources
  assert self.read(0xbcde,'B')==(1,)
  values=[*self.read(0x53da,'h'),struct.unpack('<H',u.mem_read(0x90038,2))[0],stage_graze,*self.read(0x3a4,'h'),*self.read(0x5393,'B'),*self.read(0x4642,'hh'),int(self.ending)]
  return 'E '+' '.join(map(str,values))+'|'+'|'.join(self.flow)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 target=a.target.read_bytes();assert len(target)==156258 and sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
 rows=[(frame,g,sg,tone,changed,x,y) for frame,(g,sg),(x,y),tone,changed in itertools.product((-32768,-1,0,1,415,416,417,488,32767),((0,0),(65535,2),(123,456)),((123,-456),(-32768,32767)),(-32768,100),(0,255))]
 fixture=out/'fixtures.txt';fixture.write_text('\n'.join(' '.join(map(str,row)) for row in rows)+'\n')
 native=subprocess.run([str(a.exe.resolve()),'--extra-vectors',str(fixture)],capture_output=True,text=True,check=True).stdout.splitlines();prior=None;loads=[]
 for load in (0x1000,0x2000):
  o=Original(target,load);lines=[o.run(row) for row in rows]
  assert lines==native,next(((i,w,g) for i,(w,g) in enumerate(itertools.zip_longest(lines,native)) if w!=g),None)
  assert prior is None or lines==prior;prior=lines;trace='\n'.join(lines)+'\n';(out/f'original-{load:04x}.txt').write_text(trace)
  class Rejecting(Original):
   def body(self,u,address,size):raise ValueError('injected third-departure rejection')
  try:Rejecting(target,load).run(rows[0])
  except RuntimeError as e:assert isinstance(e.__cause__,ValueError)
  else:raise ValueError('departure hook rejection swallowed')
  loads.append(dict(load=f'{load:04x}',cases=len(lines),sha256=sha(trace.encode())))
 assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
 r=dict(passed=True,source_manifest=manifest,cases=len(rows),loads=loads,target_sha256=sha(target),exe_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),callback_rejection=True,scope=__doc__,utc=datetime.now(timezone.utc).isoformat());(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('Extra departure: PASS',len(rows),'cases at1000/2000')
if __name__=='__main__':main()
