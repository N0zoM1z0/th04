#!/usr/bin/env python3
"""Original OP score scan/codec/recreate/Extra selection at two relocated loads.

Execute OP SCORE0A74:1E3A..205D,24A3..2556 and full character-menu
2FC8..32D0. File-byte stores and selection input/graphics/sound/resource
consumers are guarded adapters; codec/default/LCG/scan/sanitization/selection
instructions execute. Original uninitialized input_prev is supplied zero.
No physical DOS filesystem/full OP pixels/timing/audio/exact claim follows.
"""
import argparse,csv,hashlib,itertools,json,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify import source_manifest
from verify_maine_join import return_to_caller
PACKED='8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f'
PAYLOAD='13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74'
HI=0x3db2;HI2=0x3e76
sha=lambda b:hashlib.sha256(b).hexdigest()
hextext=lambda b:b.hex() if b else '-'
class Original:
 def __init__(self,target,decoded,load):
  packed=target.read_bytes();assert len(packed)==42290 and sha(packed)==PACKED
  self.payload=(decoded/'payload.bin').read_bytes();r=json.loads((decoded/'receipt.json').read_text())
  assert len(self.payload)==69028 and sha(self.payload)==PAYLOAD and r['payload_sha256']==PAYLOAD and r['packed_target_sha256']==PACKED and r['relocation_count']==804 and all(r['checks'].values())
  with (decoded/'relocations.csv').open() as f:sites=[int(v['relative_linear'],0) for v in csv.DictReader(f)]
  assert len(sites)==804
  module=bytearray(self.payload)
  for at in sites:struct.pack_into('<H',module,at,(struct.unpack_from('<H',module,at)[0]+load)&65535)
  self.load=load;self.cs=load+0xa74;self.ds=load+0xf34;self.module=bytes(module)
  self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000);self.u.mem_write(load*16,self.module)
  self.data=bytes(self.u.mem_read(self.ds*16,65536));self.u.hook_add(unicorn.UC_HOOK_CODE,self.hook)
  self.u.hook_add(unicorn.UC_HOOK_INSN,self.port,None,1,0,UC_X86_INS_OUT)
 def write(self,at,fmt,*v):self.u.mem_write(self.ds*16+at,struct.pack('<'+fmt,*v))
 def read(self,at,fmt):return struct.unpack('<'+fmt,self.u.mem_read(self.ds*16+at,struct.calcsize('<'+fmt)))
 def event(self,k,a=0,b=0,data=b''):self.events.append(f'{k} {a} {b} {hextext(data)}')
 def hook(self,u,address,size,unused):
  try:self.body(u,address)
  except Exception as e:self.error=e;u.emu_stop()
 def port(self,u,port,size,value,unused):
  if (port not in (0xa4,0xa6)) or size!=1 or value not in (0,1):self.error=ValueError('unexpected selection OUT');u.emu_stop()
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  def name(n=11):
   off,seg=words(2);return bytes(u.mem_read(seg*16+off,n)).split(b'\0')[0]
  if pair==(0xa74,0xff00):self.done=True;u.emu_stop();return
  if pair[0]==0xa74 and (0x1e3a<=pair[1]<0x205e or 0x24a3<=pair[1]<0x2557 or 0x2fc8<=pair[1]<0x32d1):return
  if pair[0]==0 and 0x204e<=pair[1]<0x2078:
   if pair[1]==0x204e:self.draws+=1
   return
  if pair==(0,0x9aa):
   assert name()==b'GENSOU.SCR';self.event('exists',int(self.present));u.reg_write(UC_X86_REG_AX,int(self.present));return_to_caller(u,4);return
  if pair in ((0,0x96a),(0,0xa7a)):
   assert name()==b'GENSOU.SCR' and not self.open;mode=2 if pair[1]==0x96a else 0
   if mode==2:self.file.clear();self.present=True
   else:assert self.present
   self.mode=mode;self.open=True;self.position=0;self.event('open',mode);return_to_caller(u,4);return
  if pair==(0,0xab6):
   origin,lo,hi=words(3);assert self.open and origin in (0,1);n=lo+(hi<<16);self.position=(self.position if origin else 0)+n;self.event('seek',n,origin);return_to_caller(u,6);return
  if pair in ((0,0x9c6),(0,0xaf8)):
   count,off,seg=words(3);assert self.open and count==196 and off in (HI,HI2) and seg==self.ds
   if pair[1]==0x9c6:
    b=bytes(self.file[self.position:self.position+count]);u.mem_write(seg*16+off,b) if b else None;self.event('read',count,len(b),b);self.position+=len(b);u.reg_write(UC_X86_REG_AX,len(b))
   else:
    assert off==HI and self.mode==2;b=bytes(u.mem_read(seg*16+off,count))
    if len(self.file)<self.position+count:self.file.extend(bytes(self.position+count-len(self.file)))
    self.file[self.position:self.position+count]=b;self.event('write',count,count,b);self.position+=count;u.reg_write(UC_X86_REG_AX,count)
   return_to_caller(u,6);return
  if pair==(0,0x95a):assert self.open;self.open=False;self.event('close');return_to_caller(u);return
  if pair==(0,0x2a86):
   self.sprite_names.append(name(32).decode('ascii'));return_to_caller(u,4);return
  if self.operation==4:
   if pair==(0xda1,0x7cc):
    assert self.poll<len(self.keys),'selection polls exceeded scripted release/press inputs';self.write(0x2710,'H',self.keys[self.poll]);self.poll+=1;return_to_caller(u);return
   if pair[0]==0xa74 and pair[1] in (0x2f72,0x2f10,0x2c62,0x2d25,0x2ab3):return_to_caller(u,2 if pair[1]==0x2d25 else 0,False);return
   if pair in ((0xda1,0x8d6),(0xda1,0x91c),(0,0x1de0)):return_to_caller(u);return
   if pair in ((0xda1,0x8e2),(0xda1,0x2b),(0,0x156c),(0,0x266e),(0,0x666)):return_to_caller(u,2);return
   if pair==(0xda1,0x65):return_to_caller(u,6);return
   if pair==(0,0x1618):return_to_caller(u,8);return
  raise ValueError(f'unexpected OP consumer {pair[0]:04x}:{pair[1]:04x}')
 def run(self,c):
  op,seed,rank,configured,extra,present,stage,first,second,flags,file,actions=c
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data);u.mem_write(0x7e000,bytes(8192));self.operation=op
  u.mem_write(self.ds*16+HI,first);u.mem_write(self.ds*16+HI2,second);u.mem_write(self.ds*16+0x3f3c,flags)
  self.write(0x3f3b,'B',rank);self.write(0x3f46,'B',extra);self.write(0x5c4,'I',seed);self.write(0x3f78,'BB',0,0)
  self.write(0x1a64,'HH',0,0x9000);resident=bytearray(256);resident[0xf]=configured;resident[0x11]=stage;u.mem_write(0x90000,bytes(resident))
  self.file=bytearray(file);self.present=bool(present);self.events=[];self.draws=0;self.open=False;self.error=None;self.done=False;self.sprite_names=[];self.poll=0
  self.keys=[]
  for action in actions:self.keys.extend([0,0,(1,2,4,8,0x20,0x1000)[action]])
  ip=(0x1e3a,0x1ff3,0x1f4c,0x24a3,0x2fc8)[op]
  for reg,v in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
  u.mem_write(0x7f000,struct.pack('<H',0xff00));u.emu_start(self.cs*16+ip,0x10ffff,count=500000)
  if self.error:raise RuntimeError('Original OP adapter rejected') from self.error
  assert self.done and not self.open and u.reg_read(UC_X86_REG_SP)==0xf002
  if op==3:assert self.sprite_names==['scnum.bft','hi_m.bft']
  elif op!=4:assert not self.sprite_names
  observed=bytes(u.mem_read(0x90000,256));allowed=bytearray(resident)
  if op==4 and (u.reg_read(UC_X86_REG_AX)&65535)==0:allowed[0x12]=48+self.read(0x3f78,'B')[0];allowed[0x19]=self.read(0x3f79,'B')[0]
  assert observed==allowed
  result=u.reg_read(UC_X86_REG_AX)&(65535 if op==4 else 255) if op in (0,1,4) else -1
  char,shot=self.read(0x3f78,'BB') if op==4 else (-1,-1)
  self.events.append(f'END {result} {self.read(0x5c4,"I")[0]} {self.draws} {int(self.present)} {self.read(0x3f3b,"B")[0]} {self.read(0x3f46,"B")[0]} {char} {shot} '+bytes(u.mem_read(self.ds*16+HI,196)).hex()+' '+bytes(u.mem_read(self.ds*16+HI2,196)).hex()+' '+bytes(u.mem_read(self.ds*16+0x3f3c,10)).hex()+' '+hextext(self.file))
  return self.events
 def encode(self,plain,seed):
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data);u.mem_write(self.ds*16+HI,bytes(plain));self.write(0x5c4,'I',seed)
  self.events=[];self.done=False;self.error=None;self.draws=0;self.operation=-1
  for reg,v in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
  u.mem_write(0x7f000,struct.pack('<H',0xff00));u.emu_start(self.cs*16+0x1ee7,0x10ffff,count=20000)
  if self.error:raise self.error
  assert self.done and self.draws==2
  return bytes(u.mem_read(self.ds*16+HI,196))
def fixtures(o):
 r=random.Random(1317);fresh=lambda n:bytes(r.randrange(256) for _ in range(n));rows=[]
 def c(op=3,seed=1,rank=0,configured=1,extra=0,present=1,stage=6,first=None,second=None,flags=None,file=b'',actions=b''):
  return [op,seed,rank,configured,extra,present,stage,first if first is not None else bytes(196),second if second is not None else bytes(196),flags if flags is not None else bytes(10),file,actions]
 baseline=b''.join(o.encode(fresh(196),n+1) for n in range(10))
 # Full first WORD checksum, low-byte-only second checksum, early return and
 # repeated second transformations during recreate.
 for marker,seed in itertools.product((0,19,255),(0,1,318,0xffffffff)):
  p=fresh(196);q=fresh(196);a=o.encode(p,seed);b=o.encode(q,seed)
  for column,byte,mask in ((0,2,1),(0,3,128),(1,2,1),(1,3,128),(0,0,128),(1,195,128)):
   x,y=bytearray(a),bytearray(b);(x if column==0 else y)[byte]^=mask;rows.append(c(0,seed,first=bytes(x),second=bytes(y)))
  rows.append(c(0,seed,first=a,second=b));rows.append(c(2,seed,first=bytes([marker])*196,second=q,file=fresh(2100)))
 for rank,seed,variant in itertools.product(range(5),(0,1,0xffffffff),range(9)):
  raw=bytearray(baseline);present=1
  if variant<4:raw[((0 if variant<2 else 5)+rank)*196+2+variant%2]^=128
  elif variant==4:raw=raw[:rank*196+83]
  elif variant==5:raw=raw[:(5+rank)*196+111]
  elif variant==6:raw=bytearray();present=0
  elif variant==7:raw=bytearray()
  else:raw+=fresh(37)
  rows.append(c(1,seed,rank,first=fresh(196),second=fresh(196),file=bytes(raw),present=present))
 for char,rank,value in itertools.product(range(2),range(5),(0,1,2,3,4,0x19,128,255)):
  parts=[]
  for n in range(10):
   plain=bytearray(196);plain[174]=value if n==char*5+rank else 0;parts.append(o.encode(plain,n+1))
  raw=b''.join(parts);rows.append(c(file=raw,configured=rank))
  bad=bytearray(raw);bad[(rank if char==0 else rank+5)*196+2]^=1;rows.append(c(file=bytes(bad),flags=fresh(10),extra=128,configured=255))
 for stop in range(5):
  # Accept prior ranks before the bad rank's rebuild; never clear those flags.
  parts=[]
  for n in range(10):
   p=bytearray(196);p[174]=(n%3)+1;parts.append(o.encode(p,318+n))
  raw=bytearray(b''.join(parts));raw[stop*196+3]^=128;rows.append(c(file=bytes(raw),configured=stop))
 for mask,stage in itertools.product(range(16),(0,6)):
  flags=bytearray(10)
  for char,shot in itertools.product(range(2),repeat=2):
   if mask&(1<<(char*2+shot)):flags[char*5+1]|=1<<shot
  for actions in (bytes([4,4]),bytes([3,4,1,4]),bytes([2,4,0,5,3,4,4]),bytes([5])):
   rows.append(c(4,flags=bytes(flags),stage=stage,actions=actions))
 for rank,mask in itertools.product((0,4),range(16)):
  flags=bytearray(10)
  for char,shot in itertools.product(range(2),repeat=2):
   if mask&(1<<(char*2+shot)):flags[char*5+rank]|=1<<shot
  rows.append(c(4,flags=bytes(flags),actions=bytes([4,4])))
 return rows,baseline
def fixture(c):return ' '.join(map(str,c[:7]))+' '+' '.join(hextext(b) for b in c[7:])+'\n'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','decoded-dir','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
 o=Original(a.target,a.decoded_dir,0x1000);rows,baseline=fixtures(o);path=out/'fixtures.txt';path.write_text(''.join(map(fixture,rows)));(out/'original-input.SCR').write_bytes(baseline)
 traces=[]
 for load in (0x1000,0x2000):
  o=Original(a.target,a.decoded_dir,load);lines=[]
  for i,c in enumerate(rows):lines.extend([f'CASE {i}',*o.run(c)])
  b=('\n'.join(lines)+'\n').encode();(out/f'original-{load:04x}.txt').write_bytes(b);traces.append(b)
 assert traces[0]==traces[1]
 result=subprocess.run([str(a.exe.resolve()),'--trace',str(path)],capture_output=True);(out/'native.txt').write_bytes(result.stdout);(out/'stderr.txt').write_bytes(result.stderr)
 if result.returncode or result.stdout!=traces[0]:
  x=result.stdout.splitlines();y=traces[0].splitlines();i=next((i for i,(a,b) in enumerate(zip(x,y)) if a!=b),min(len(x),len(y)));(out/'mismatch.json').write_text(json.dumps(dict(line=i,actual=str(x[i:i+2]),expected=str(y[i:i+2]),returncode=result.returncode),indent=2)+'\n');raise ValueError(f'OP differs line{i}')
 assert source_manifest(root)[0]==manifest
 class Rejection(Original):
  def body(self,u,address):raise ValueError('deliberate callback rejection')
 for load in (0x1000,0x2000):
  try:Rejection(a.target,a.decoded_dir,load).run(rows[0])
  except RuntimeError as error:assert isinstance(error.__cause__,ValueError) and str(error.__cause__)=='deliberate callback rejection'
  else:raise AssertionError('callback rejection swallowed')
 extents=[(0xc57a,0xad),(0xc627,0x65),(0xc68c,0xa7),(0xc733,0x6b),(0xcbe3,0xb4),(0xd708,0x309)]
 receipt=dict(passed=True,callback_rejection_passed=True,cases=len(rows),operation_counts={str(op):sum(c[0]==op for c in rows) for op in range(5)},loads=['1000','2000'],source_manifest=manifest,packed_sha256=PACKED,payload_sha256=PAYLOAD,extents=[dict(start=hex(at),size=size,sha256=sha(o.payload[at:at+size])) for at,size in extents],fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(traces[0]),exe_sha256=sha(a.exe.read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Original OP/native score scan and selection PASS',len(rows),'cases at1000/2000')
if __name__=='__main__':main()
