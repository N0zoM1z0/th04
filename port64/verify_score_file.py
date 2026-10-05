#!/usr/bin/env python3
"""Original MAINE score cipher, recreate/load/save and ranking controls.

Complete recovered instructions compute cipher/checksum, rank, defaults and
LCG. Successful file wrappers are guarded byte-store adapters; no portable
algorithm creates the original reference and no physical DOS I/O is claimed.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import random
import unicorn
import struct
import subprocess

from unicorn.x86_const import *
from verify_cutscene import Original as Base,PACKED_SHA,PAYLOAD_SHA
from verify_maine_join import return_to_caller
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
HI=0x3fc2
EXTENTS=(
 (0xc149,0x58,'decode','31ea6a61abea7712e7ddd2ef8d9ee446b5947b514611252cba2d70c3930aff99'),
 (0xc1a1,0x65,'encode','c5c56e733842e6ba9b2d0448109939b2e04c8536b8495057425c4e787437c497'),
 (0xc206,0xa7,'recreate','7bc9464f7f09359087fb329a0c829021a834415aba27383f717d38cd1ba98094'),
 (0xc2ad,0x67,'load','612c01bcd337e251022f22034b5f2d374f81309ff3621a4ce1757e21928c36a5'),
 (0xc316,0x9c,'save','657805c7c6b0773da7bdcd1e6813507c1c3305fb75dd8ee695c3b6b75d9992b6'),
 (0xc3b2,0x154,'insert','ed7880a5a1cd7aa721c2a95bafb819da15768fd660cf6dd96dbccc9fdc30c093'),
)
ENTRY=(0x2151,0x20f9,0x21b6,0x225d,0x22c6,0x2362)

def text(data):return data.hex() if data else '-'
class Original(Base):
 def __init__(self,target,decoded,load):
  super().__init__(target,decoded,load)
  for start,size,name,digest in EXTENTS:
   assert sha(self.payload[start:start+size])==digest,name+' extent differs'
  self.owner_sha=sha(self.payload[0xc149:0xc506])
 def body(self,u,address):
  segment=u.reg_read(UC_X86_REG_CS)-self.load;ip=address-u.reg_read(UC_X86_REG_CS)*16
  sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  def name():
   off,seg=words(2);raw=bytes(u.mem_read(seg*16+off,11));assert raw==b'GENSOU.SCR\0'
  def event(kind,a=0,b=0,data=b''):self.events.append(f'{kind} {a} {b} {text(data)}')
  if segment==0xa05 and ip==0xff00:self.done=True;u.emu_stop();return
  if segment==0xa05 and 0x20f9<=ip<0x24b6:return
  if segment==0 and 0x1c5a<=ip<0x1c84:
   if ip==0x1c5a:self.draws+=1
   return # Execute full original TC4J process-local RNG.
  if segment==0:
   if ip==0x9b8:
    name();event('exists',int(self.present));u.reg_write(UC_X86_REG_AX,int(self.present));return_to_caller(u,4);return
   if ip in (0x978,0xa88,0x8a8):
    name();assert not self.open
    mode={0xa88:0,0x8a8:1,0x978:2}[ip]
    if mode==2:self.file.clear();self.present=True
    else:assert self.present
    self.open=True;self.mode=mode;self.position=0;event('open',mode)
    return_to_caller(u,4);return
   if ip==0xac4:
    origin,lo,hi=words(3);assert self.open and origin in (0,1)
    value=lo+(hi<<16);self.position=(self.position if origin else 0)+value
    event('seek',value,origin);return_to_caller(u,6);return
   if ip in (0x9d4,0xb14):
    count,off,seg=words(3);assert self.open and (off,seg,count)==(HI,self.ds,196)
    if ip==0x9d4:
     data=bytes(self.file[self.position:self.position+count]);u.mem_write(seg*16+off,data) if data else None
     event('read',count,len(data),data);self.position+=len(data);u.reg_write(UC_X86_REG_AX,len(data))
    else:
     assert self.mode in (1,2);data=bytes(u.mem_read(seg*16+off,count))
     if len(self.file)<self.position+count:self.file.extend(bytes(self.position+count-len(self.file)))
     self.file[self.position:self.position+count]=data;event('write',count,count,data);self.position+=count
     u.reg_write(UC_X86_REG_AX,count)
    return_to_caller(u,6);return
   if ip==0x968:
    assert self.open;self.open=False;event('close');return_to_caller(u);return
  raise ValueError(f'unexpected score consumer {segment:04x}:{ip:04x}')
 def run(self,case):
  operation,seed,character,rank,stage,end,present,work,file,digits=case
  self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
  self.u.mem_write(self.ds*16+HI,work);self.write(0x170,'I',seed)
  self.write(0x4086,'BBB',0xa5,rank,character);self.u.mem_write(self.ds*16+HI-16,bytes([0x5a])*16)
  resident=bytearray(256);resident[0x11]=stage;resident[0x30]=end;resident[0x1d:0x25]=digits
  self.u.mem_write(0x90000,bytes(resident));self.write(0xe9e,'HH',0,0x9000)
  self.file=bytearray(file);self.present=bool(present);self.position=0;self.open=False;self.draws=0
  self.events=[];self.error=None;self.done=False;self.font_mode=False
  for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_ES,0),
   (UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):
   self.u.reg_write(reg,value)
  self.u.mem_write(0x7f000,struct.pack('<HH',0xff00,character))
  self.u.emu_start(self.cs*16+ENTRY[operation],0x10ffff,count=200000)
  if self.error:raise RuntimeError('original score adapter rejected') from self.error
  assert self.done and not self.open and self.u.reg_read(UC_X86_REG_SP)==0xf000+(4 if operation==3 else 2)
  assert bytes(self.u.mem_read(0x90000,256))==resident
  assert bytes(self.u.mem_read(self.ds*16+HI-16,16))==bytes([0x5a])*16
  result=self.u.reg_read(UC_X86_REG_AX)&255 if operation in (1,3) else -1
  place=self.read(0x4086,'B')[0]
  if operation!=5:assert place==0xa5
  assert self.read(0x4087,'BB')==(rank,character)
  buffer=bytes(self.u.mem_read(self.ds*16+HI,196));random_state=self.read(0x170,'I')[0]
  assert self.draws==({0:2,1:0,2:20,3:20 if result else 0,4:22,5:0}[operation])
  self.events.append(f'END {result} {place} {random_state} {self.draws} {int(self.present)} {buffer.hex()} {text(self.file)}')
  return self.events

def fixtures(original):
 r=random.Random(1297);fresh=lambda n:bytes(r.randrange(256) for _ in range(n));cases=[]
 def case(op,work,seed=1,character=0,rank=0,stage=5,end=255,present=0,file=b'',digits=bytes(8)):
  return (op,seed,character,rank,stage,end,present,work,file,digits)
 seeds=(0,1,318,0x7fffffff,0x80000000,0xffffffff,0x12345678)
 samples=[bytes(196),bytes([255])*196,bytes(range(196)),fresh(196),fresh(196)]
 for seed in seeds:
  for work in samples:
   c=case(0,work,seed);cases.append(c);original.run(c)
   encoded=bytes(original.u.mem_read(original.ds*16+HI,196));cases.append(case(1,encoded,seed))
   for index,value in ((2,1),(3,128),(0,128),(1,1),(4,1),(195,128)):
    changed=bytearray(encoded);changed[index]^=value;cases.append(case(1,bytes(changed),seed))
 for seed in seeds:
  for work in samples[:4]:cases.append(case(2,work,seed,present=1,file=fresh(2111)))
 # Obtain independent whole-file input from original recreation, not native
 # score code. Preserve the decoded work's reserved bytes in each scenario.
 original.run(case(2,fresh(196),0x31415926))
 baseline=bytes(original.file)
 for character in (0,1,2,255):
  for rank in range(5):
   for variant in range(7):
    raw=bytearray(baseline);present=1
    if variant==1:raw[(int(bool(character))*5+rank)*196+2]^=1
    if variant==2:raw[(int(bool(character))*5+rank)*196+3]^=128
    if variant==3:raw=raw[:(int(bool(character))*5+rank)*196+101]
    if variant==4:raw=bytearray();present=0
    if variant==5:raw=bytearray()
    if variant==6:raw+=fresh(83)
    c=case(3,fresh(196),seeds[rank],character,rank,present=present,file=bytes(raw));cases.append(c)
   original.run(case(3,bytes(196),1,character,rank,present=1,file=baseline))
   decoded=bytes(original.u.mem_read(original.ds*16+HI,196))
   for seed in (0,1,0xffffffff):
    edit=bytearray(decoded);edit[4:12]=b'ABCDEFGH';edit[174]=3
    cases.append(case(4,bytes(edit),seed,character,rank,present=1,file=baseline+fresh(33)))
 # Save ignores decode's checksum return for nonselected sections. Corrupt
 # them independently, and shorten the file so read leaves HI's suffix/stale
 # contents. This distinguishes re-keying from an accidental recreate/clear.
 for character in (0,1):
  for rank in range(5):
   original.run(case(3,bytes(196),1,character,rank,present=1,file=baseline))
   decoded=bytes(original.u.mem_read(original.ds*16+HI,196))
   other=((character*5+rank+1)%10)*196
   for seed in (0,0xffffffff):
    for variant in range(4):
     raw=bytearray(baseline)
     if variant==0:raw[other+2]^=1
     if variant==1:raw[other+4]^=128
     if variant==2:raw=raw[:1080]
     if variant==3:raw=raw[:196]
     cases.append(case(4,decoded,seed,character,rank,present=1,file=bytes(raw)))
 # Target produces the default ranking. Exercise ties above/below EVERY row,
 # all end-sequence/stage markers and malformed BYTE values/row terminators.
 original.run(case(2,bytes(196)));table=bytes(original.u.mem_read(original.ds*16+HI,196))
 for row in range(10):
  score=[b-0xa0 for b in table[94+row*8:102+row*8]]
  for delta in (-1,0,1):
   numeric=sum(v*10**i for i,v in enumerate(score))+delta
   digits=bytes((numeric//10**i)%10 for i in range(8))
   work=bytearray(table)
   for place in range(10):work[4+place*9+8]=200+place
   for stage in (0,5,6,255):
    for end in (0,252,253,254,255):cases.append(case(5,bytes(work),stage=stage,end=end,digits=digits))
 for _ in range(100):cases.append(case(5,fresh(196),stage=r.randrange(256),end=r.randrange(256),digits=fresh(8)))
 return cases

def encode_fixture(c):
 op,seed,char,rank,stage,end,present,work,file,digits=c
 return ' '.join(map(str,(op,seed,char,rank,stage,end,present)))+' '+work.hex()+' '+text(file)+' '+digits.hex()+'\n'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--runner');p.add_argument('--reference-dir',type=Path)
 args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
 if args.reference_dir:
  reference=args.reference_dir;proof=json.loads((reference/'receipt.json').read_text());assert proof['passed'] and proof['payload_sha256']==PAYLOAD_SHA
  fixture=(reference/'fixtures.txt').read_bytes();expected=(reference/'original.txt').read_bytes()
  assert sha(fixture)==proof['fixture_sha256'] and sha(expected)==proof['original_sha256']
  cases=proof['cases'];owner_sha=proof['owner_sha256'];counts=proof['operation_counts'];loads=proof['load_segments']
  # The attested target remains required even for a retained producer consumer.
  original=Original(args.target,args.decoded_dir,0x2000);assert original.owner_sha==owner_sha
 else:
  original=Original(args.target,args.decoded_dir,0x1000);cases=fixtures(original);fixture=''.join(map(encode_fixture,cases)).encode()
  owner_sha=original.owner_sha;traces=[];loads=[4096,8192]
  for load in loads:
   original=Original(args.target,args.decoded_dir,load);lines=[]
   for index,c in enumerate(cases):lines.extend([f'CASE {index}',*original.run(c)])
   traces.append(('\n'.join(lines)+'\n').encode())
  assert traces[0]==traces[1],'score producer differs across load segments'
  expected=traces[0];counts={str(op):sum(c[0]==op for c in cases) for op in range(6)};cases=len(cases)
 (out/'fixtures.txt').write_bytes(fixture);(out/'original.txt').write_bytes(expected)
 env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
 cmd=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--trace',str(out/'fixtures.txt')]
 r=subprocess.run(cmd,capture_output=True,env=env,timeout=180)
 actual=r.stdout.replace(b'\r\n',b'\n');(out/'native.txt').write_bytes(actual);(out/'stderr.txt').write_bytes(r.stderr)
 if r.returncode or actual!=expected:
  a=actual.splitlines();e=expected.splitlines();first=next((i for i,(x,y) in enumerate(zip(a,e)) if x!=y),min(len(a),len(e)))
  (out/'mismatch.json').write_text(json.dumps(dict(line=first,actual=str(a[first:first+2]),expected=str(e[first:first+2]),returncode=r.returncode),indent=2)+'\n')
  raise ValueError(f'original/native score differs at line{first}')
 mf,source=source_manifest(Path(__file__).resolve().parents[1])
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),cases=cases,operation_counts=counts,load_segments=loads,
  payload_sha256=PAYLOAD_SHA,packed_sha256=PACKED_SHA,owner_sha256=owner_sha,fixture_sha256=sha(fixture),original_sha256=sha(expected),
  executable_sha256=sha(args.exe.read_bytes()),source_manifest=mf,source_files=source,command=cmd,
  scope='Complete original score cipher/default/load/save/insertion and original LCG;successful file wrappers are guarded byte-store adapters. Full work/file bytes,operations,RNG,rank,resident guards and load metamorphism. No physical DOS filesystem,registration UI,host persistence or packed-file exactness claim.')
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Original/native score file:',cases,'complete controls PASS')
if __name__=='__main__':main()
