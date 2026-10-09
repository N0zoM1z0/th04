#!/usr/bin/env python3
"""Original MAIN score cipher/load/Continue insertion/selected-write controls.

Complete MAIN score instructions and TC4J LCG execute at two loads. File
wrappers have guarded byte-store adapters. Whole section/file bytes, ordered
I/O, RNG, Continue place and resident/digit guards are compared. No physical
DOS I/O or live host persistence/Continue acceptance follows.
"""
import argparse,hashlib,itertools,json,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_player_lifecycle import Original as Base
from verify_score_file import encode_fixture
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
HI=0xbbee
ENTRY=(0x18fa,0x18ba,0x7f1a,0x7fc7,0x802e,0x81c5,0x81d7)

class Original(Base):
 def body(self,u,address,size,unused):
  actual=u.reg_read(UC_X86_REG_CS);cs=actual+self.delta;ip=address-actual*16
  sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  def ret(args=0):
   off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4+args)
   u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off)
  def event(kind,a=0,b=0,data=b''):self.events.append(f'{kind} {a} {b} '+(data.hex() if data else '-'))
  def name():
   off,seg=words(2);assert bytes(u.mem_read(seg*16+off,11))==b'GENSOU.SCR\0'
  if cs==0x2aaf and (0x18ba<=ip<0x1939 or 0x7f1a<=ip<0x81f5):return
  if cs==0x2000 and 0x2172<=ip<0x219c:
   if ip==0x2172:self.rng_draws+=1
   return
  if cs==0x2000 and 0x45aa<=ip<0x45cb:return
  if cs==0x2aaf and ip==0xf000:return
  assert cs==0x2000,f'unexpected score CS {cs:04x}:{ip:04x}'
  if ip==0xe44:
   name();event('exists',int(self.present));u.reg_write(UC_X86_REG_AX,int(self.present));ret(4);return
  if ip in (0xe04,0xf14,0xd34):
   name();assert not self.open
   mode={0xf14:0,0xd34:1,0xe04:2}[ip]
   if mode==2:self.file.clear();self.present=True
   else:assert self.present
   self.open=True;self.mode=mode;self.position=len(self.file) if mode==1 else 0;event('open',mode);ret(4);return
  if ip==0xf50:
   origin,lo,hi=words(3);assert self.open and origin in (0,1)
   value=lo+(hi<<16);self.position=(self.position if origin else 0)+value;event('seek',value,origin);ret(6);return
  if ip in (0xe60,0xfa0):
   count,off,seg=words(3);assert self.open and (off,seg,count)==(HI,0x8000,196)
   if ip==0xe60:
    data=bytes(self.file[self.position:self.position+count])
    if data:u.mem_write(seg*16+off,data)
    event('read',count,len(data),data);self.position+=len(data);u.reg_write(UC_X86_REG_AX,len(data))
   else:
    assert self.mode in (1,2);data=bytes(u.mem_read(seg*16+off,count))
    if len(self.file)<self.position+count:self.file.extend(bytes(self.position+count-len(self.file)))
    self.file[self.position:self.position+count]=data;event('write',count,count,data);self.position+=count
    u.reg_write(UC_X86_REG_AX,count)
   ret(6);return
  if ip==0xdf4:assert self.open;self.open=False;event('close');ret();return
  raise ValueError(f'unexpected score adapter {cs:04x}:{ip:04x}')
 def run(self,case):
  op,seed,char,rank,stage,turbo,present,work,file,digits=case
  self.reset();self.error=None;self.u.mem_write(0x80000+HI,work);self.write(0x3e2,'I',seed)
  self.write(0x4348,'B',rank);self.write(0xbcb2,'B',0xa5);self.write(0x5394,'B',stage);self.write(0x53a0,'B',turbo)
  self.u.mem_write(0x84349,digits);self.u.mem_write(0x80000+HI-16,bytes([0x5a])*16)
  resident=bytearray(256);resident[0x12]=(0x30+char)&255
  self.u.mem_write(0x90000,bytes(resident));self.write(0xba86,'HH',0,0x9000)
  self.file=bytearray(file);self.present=bool(present);self.open=False;self.position=0;self.rng_draws=0;self.events=[]
  cs=0x2aaf-self.delta
  for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                    (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)]:self.u.reg_write(reg,value)
  self.u.mem_write(0x7e000,struct.pack('<HH',0xf000,HI))
  try:self.u.emu_start(cs*16+ENTRY[op],cs*16+0xf000,count=500000)
  except Exception:
   if self.error:raise RuntimeError('MAIN score adapter rejected') from self.error
   raise
  if self.error:raise RuntimeError('MAIN score adapter rejected') from self.error
  assert self.u.reg_read(UC_X86_REG_IP)==0xf000 and self.u.reg_read(UC_X86_REG_SP)==0xe000+(4 if op<2 else 2)
  assert not self.open and bytes(self.u.mem_read(0x90000,256))==resident
  assert bytes(self.u.mem_read(0x84349,8))==digits
  assert bytes(self.u.mem_read(0x80000+HI-16,16))==bytes([0x5a])*16
  result=self.u.reg_read(UC_X86_REG_AX)&255 if op==1 else -1
  place=self.read(0xbcb2,'B')[0];buffer=bytes(self.u.mem_read(0x80000+HI,196));state=self.read(0x3e2,'I')[0]
  if op==6:self.events.append('HS '+bytes(self.u.mem_read(0x84351,8)).hex())
  self.events.append(f'END {result} {place} {state} {self.rng_draws} {int(self.present)} {buffer.hex()} '+(self.file.hex() if self.file else '-'))
  return self.events

def fixtures(original):
 r=random.Random(1302);fresh=lambda n:bytes(r.randrange(256) for _ in range(n));cases=[]
 def c(op,work,seed=1,char=0,rank=0,stage=0,turbo=1,present=0,file=b'',digits=bytes(8)):
  return(op,seed,char,rank,stage,turbo,present,work,file,digits)
 samples=[bytes(196),bytes([255])*196,bytes(range(196)),fresh(196),fresh(196)]
 seeds=(0,1,318,0x7fffffff,0x80000000,0xffffffff,0x12345678)
 for seed,work in itertools.product(seeds,samples):
  q=c(0,work,seed);cases.append(q);original.run(q);encoded=bytes(original.u.mem_read(0x80000+HI,196))
  cases.append(c(1,encoded,seed))
  for at in (0,1,2,3,4,195):
   edited=bytearray(encoded);edited[at]^=1;cases.append(c(1,bytes(edited),seed))
  cases.append(c(2,work,seed,present=1,file=fresh(2111)))
 original.run(c(2,fresh(196),seed=0x31415926));baseline=bytes(original.file)
 for char,rank,variant in itertools.product((0,1,2,255),range(5),range(7)):
  data=bytearray(baseline);present=1;off=((char==1)*5+rank)*196
  if variant==1:data[off+2]^=1
  if variant==2:data[off+3]^=128
  if variant==3:data=data[:off+101]
  if variant==4:data=bytearray();present=0
  if variant==5:data=bytearray()
  if variant==6:data+=fresh(83)
  cases.append(c(3,fresh(196),seeds[rank],char,rank,present=present,file=bytes(data)))
 for char,rank in itertools.product((0,1),range(5)):
  original.run(c(3,bytes(196),char=char,rank=rank,present=1,file=baseline));table=bytes(original.u.mem_read(0x80000+HI,196))
  for seed in seeds:cases.append(c(4,table,seed,char,rank,present=1,file=baseline+fresh(33)))
  for row,delta,stage,turbo in itertools.product(range(10),(-1,0,1),(0,5,6,255),(0,1)):
   ds=[b-0xa0 for b in table[94+row*8:102+row*8]];numeric=sum(v*10**i for i,v in enumerate(ds))+delta
   digits=bytes((numeric//10**i)%10 for i in range(8))
   cases.append(c(5,fresh(196),char=char,rank=rank,stage=stage,turbo=turbo,present=1,file=baseline+fresh(17),digits=digits))
 for char,rank,turbo in itertools.product((0,1),range(5),(0,1)):
  for variant in range(3):
   data=bytearray(baseline);present=1
   if variant==0:data[((char*5)+rank)*196+2]^=1
   if variant==1:data=bytearray();present=0
   if variant==2:data=data[:997]
   cases.append(c(5,fresh(196),0xffffffff,char,rank,6,turbo,present,bytes(data),bytes([255]*8)))
 # Real hiscore_load wrapper, not just its selected-section load helper.
 # Preserve all existing codec/Continue controls and their trace protocol.
 cases.extend((6,*q[1:]) for q in list(cases) if q[0]==3)
 for seed,work in itertools.product(seeds,samples):cases.append(c(6,work,seed))
 for char,rank,value in itertools.product((0,1),range(5),(0,95,96,159,160,169,170,255)):
  plain=bytearray(196);plain[94:102]=bytes([value])*8
  original.run(c(0,bytes(plain),seed=0x31415926));encoded=bytes(original.u.mem_read(0x80000+HI,196))
  data=bytearray(baseline);data[(char*5+rank)*196:(char*5+rank+1)*196]=encoded
  cases.append(c(6,fresh(196),seeds[rank],char,rank,present=1,file=bytes(data)+fresh(13)))
 return cases

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['target','exe','output-dir']:p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh output directory')
 out.mkdir(parents=True);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 cases=fixtures(Original(a.target.read_bytes(),0x1000));expected=[]
 for load in (0x1000,0x2000):
  original=Original(a.target.read_bytes(),load);lines=[]
  for index,case in enumerate(cases):lines.extend([f'CASE {index}',*original.run(case)])
  if expected:assert expected==lines,'MAIN score load metamorphism differs'
  else:expected=lines
 fixture=out/'fixtures.txt';fixture.write_text(''.join(map(encode_fixture,cases)))
 ref=out/'original.txt';ref.write_text('\n'.join(expected)+'\n')
 result=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--main-trace',str(fixture)],
                       text=True,capture_output=True,check=True,timeout=240)
 (out/'native.txt').write_text(result.stdout)
 for row,(x,y) in enumerate(itertools.zip_longest(result.stdout.splitlines(),expected)):
  if x!=y:
   (out/'mismatch.json').write_text(json.dumps(dict(row=row,native=x,original=y),indent=2)+'\n')
   raise ValueError(f'MAIN score differs at row {row}')
 assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,
              target_sha256=sha(original.target),executable_sha256=sha(a.exe.read_bytes()),cases=len(cases),records=len(expected),
              load_segments=[0x1000,0x2000],extent='MAIN relative0AAF:18BA..1939 and 7F1A..81F5',
              extents_sha256={name:sha(original.target[6144+lo:6144+hi]) for name,lo,hi in
                [('cipher',0xc3aa,0xc429),('load-save-continue-hiscore',0x12a0a,0x12ce5),('lcg',0x2172,0x219c)]},
              fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(ref.read_bytes()),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['passed','cases','records']}))
if __name__=='__main__':main()
