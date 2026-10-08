#!/usr/bin/env python3
"""Original MAIN character Bomb/star instructions versus complete native state.

Both load segments execute actual RNG, polar motion and growing-circle bodies.
Fill/CDG/mono, sound and GRCG are explicit request/hardware adapters here;
the separate pixel control executes their original graphics kernels.
No live MAIN, physical timing/audio or DOS exactness acceptance follows.
"""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_player_lifecycle import Original as Base
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
 def __init__(self,target,load=0x2000):
  self.color=0;self.events=[];self.pixels=False
  super().__init__(target,load)
  self.u.hook_add(unicorn.UC_HOOK_INSN,self.port,None,1,0,UC_X86_INS_OUT)
 def port(self,u,port,size,value,unused):
  if size!=1 or port not in (0x7c,0x7e):
   self.error=ValueError('unexpected Bomb hardware port');u.emu_stop()
 def body(self,u,address,size,unused):
  actual=u.reg_read(UC_X86_REG_CS);pair=(actual+self.delta,address-actual*16)
  sp=u.reg_read(UC_X86_REG_SP)
  def args(n,far=False):return struct.unpack('<'+'h'*n,u.mem_read(0x70000+sp+(4 if far else 2),n*2))
  def ret(far=False,words=0):
   values=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
   u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+words*2)
   if far:u.reg_write(UC_X86_REG_CS,values[1])
   u.reg_write(UC_X86_REG_IP,values[0])
  if pair==(0x2aaf,0x1672):self.color=(u.reg_read(UC_X86_REG_AX)>>8)&15
  if pair==(0x2aaf,0x751a):
   self.events.append((0,0,0,self.color))
   if not self.pixels:ret()
  elif pair==(0x330e,0x5d4):
   slot,y,x=args(3,True);self.events.append((1,x,y,slot))
   if not self.pixels:ret(True,3)
  elif pair==(0x2aaf,0x1b5a):
   y,x=args(2,True);self.events.append((2,x,y,0)) # execute actual pool allocation
  elif pair==(0x330e,0x7d2):
   self.events.append((3,0,0,args(1,True)[0]));ret(True,1)
  elif pair==(0x2aaf,0x152a):
   assert args(1)[0]==120,'unexpected Bomb mono pattern'
   signed=lambda x:x-65536 if x&32768 else x
   self.events.append((4,signed(u.reg_read(UC_X86_REG_CX)),signed(u.reg_read(UC_X86_REG_AX)),self.color))
   if not self.pixels:ret(False,1)
 def seed_bomb(self,row):
  character,steps,frame,stage,mod4,cursor,tone,changed,color,stars,circles=row
  self.reset();self.error=None;self.events=[];self.color=14 if character==0 else 8
  for at,fmt,value in [(0x4369,'B',frame),(0x538a,'H',stage),(0x538d,'B',mod4),(0x3ecc,'H',cursor),
                        (0x3a4,'H',tone),(0x5393,'B',changed),(0x4252,'B',color)]:self.write(at,fmt,value)
  self.u.mem_write(0x84370,bytes.fromhex(stars));self.u.mem_write(0x89594,bytes.fromhex(circles))
 def call_args(self,ip,args=(),far=False,cs=0x2aaf):
  cs-=self.delta;u=self.u
  for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                    (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
  stack=(0xf000,cs,*args) if far else (0xf000,*args)
  u.mem_write(0x7e000,struct.pack('<'+'H'*len(stack),*(x&65535 for x in stack)))
  try:u.emu_start(cs*16+ip,cs*16+0xf000,count=500000)
  except Exception:
   if self.error:raise RuntimeError('Bomb callback rejected') from self.error
   raise
  if self.error:raise RuntimeError('Bomb callback rejected') from self.error
  assert u.reg_read(UC_X86_REG_IP)==0xf000 and u.reg_read(UC_X86_REG_SP)==0xe000+len(stack)*2,'Bomb return failed'
 def execute(self,op,character):
  self.events=[]
  self.call_args(0x581d if op=='S' else 0x555d if not character else 0x5623,(character,) if op=='S' else ())
  values=[self.read(at,fmt)[0] for at,fmt in [(0x3a4,'H'),(0x5393,'B'),(0x4252,'B'),(0x3ecc,'H')]]
  return 'STATE '+' '.join(map(str,values))+' '+bytes(self.u.mem_read(0x84370,288)).hex()+' '+bytes(self.u.mem_read(0x89594,160)).hex()+' '+str(len(self.events))+''.join(' '+' '.join(map(str,event)) for event in self.events)
 def next_frame(self):
  frame=(self.read(0x4369,'B')[0]+1)&255;stage=(self.read(0x538a,'H')[0]+1)&65535
  self.write(0x4369,'B',frame);self.write(0x538a,'H',stage);self.write(0x538d,'B',stage%4)

def stars(variant):
 edges=(-32768,-129,-128,-127,0,2047,2048,4096,4097,6143,6144,6271,6272,32767)
 return b''.join(struct.pack('<hhBB',edges[(i+variant)%len(edges)],edges[(i*3+variant)%len(edges)],(i*17+variant)&255,(i*73+variant)&255) for i in range(48)).hex()
def circles(variant):
 return b''.join(struct.pack('<BBhhhh',0 if (i+variant)%3==0 else 1,(i*13)&255,i*7-51,i*11-37,i*9-65,i*5-33) for i in range(16)).hex()
def fixture(character=0,steps=1,frame=48,stage=123,mod4=0,cursor=0,variant=0):
 return [character,steps,frame,stage,mod4,cursor,65535,255,13,stars(variant),circles(variant)]
def fixtures():
 for character,frame,mod4 in itertools.product(range(2),range(256),(0,1)):
  yield 'F',fixture(character=character,frame=frame,mod4=mod4,cursor=(frame*19)&255,variant=frame%14)
 for character,frame,mod4,cursor in itertools.product(range(2),(48,49,80,81,84,119,120,160,161,175,255),(0,3),(0,1,254,255)):
  yield 'F',fixture(character=character,frame=frame,mod4=mod4,cursor=cursor,stage=65535,variant=cursor%14)
 for character,variant in itertools.product(range(2),range(14)):
  yield 'S',fixture(character=character,frame=49,variant=variant,cursor=255)
 for character,cursor in itertools.product(range(2),(0,1,254,255)):
  yield 'L',fixture(character=character,steps=128,frame=48,stage=65520,cursor=cursor)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for n in ('target','exe','output-dir'):parser.add_argument('--'+n,type=Path,required=True)
 parser.add_argument('--runner');parser.add_argument('--reference-dir',type=Path);parser.add_argument('--limit',type=int)
 a=parser.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh Bomb output directory')
 out.mkdir(parents=True);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures())
 inputs='\n'.join(op+' '+' '.join(map(str,row)) for op,row in rows)+'\n'
 fixture_path=out/'fixtures.txt';fixture_path.write_text(inputs);reference=None
 if a.reference_dir:
  reference=json.loads((a.reference_dir/'receipt.json').read_text())
  assert reference['passed'] and reference['target_sha256']==sha(a.target.read_bytes()) and reference['fixture_sha256']==sha(inputs.encode())
  trace=a.reference_dir/'original.txt';assert sha(trace.read_bytes())==reference['trace_sha256']
  expected=trace.read_text().splitlines()
 else:
  expected=[]
  for load in (0x1000,0x2000):
   original=Original(a.target.read_bytes(),load);current=[]
   for index,(op,row) in enumerate(rows):
    original.seed_bomb(row)
    for step in range(row[1]):
     current.append(original.execute(op,row[0]))
     if op=='L':original.next_frame()
    if (index+1)%256==0:print(hex(load),index+1,'original cases',flush=True)
   if expected:assert expected==current,'Bomb load metamorphism differs'
   else:expected=current
  trace=out/'original.txt';trace.write_text('\n'.join(expected)+'\n')
 command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--bomb-vectors',str(fixture_path)]
 env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
 result=subprocess.run(command,text=True,capture_output=True,check=True,env=env,timeout=240)
 (out/'native.txt').write_text(result.stdout)
 for i,(x,y) in enumerate(itertools.zip_longest(expected,result.stdout.splitlines())):
  if x!=y:
   (out/'mismatch.json').write_text(json.dumps(dict(record=i,original=x,native=y),indent=2)+'\n');raise ValueError(f'Bomb record{i} differs')
 assert manifest==source_manifest(Path(__file__).resolve().parents[1])[0],'source changed during Bomb Oracle'
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,
  target_sha256=sha(a.target.read_bytes()),executable_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(inputs.encode()),
  trace_sha256=sha(trace.read_bytes()),native_sha256=sha(result.stdout.encode()),cases=len(rows),records=len(expected),
  load_segments=[4096,8192],data_segment='8000',original_cpu_reexecuted=not bool(reference),reference_dir=str(a.reference_dir) if reference else None,
  unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
  extents={f'0AAF:{lo:04X}..{hi:04X}':sha(a.target.read_bytes()[6144+0xaaf0+lo:6144+0xaaf0+hi]) for lo,hi in [(0x555d,0x5623),(0x5623,0x571a),(0x581d,0x593a)]},scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','cases','records','source_manifest')}))
if __name__=='__main__':main()
