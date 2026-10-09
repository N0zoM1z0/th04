#!/usr/bin/env python3
"""OP ranking caller, both-column rows and fades at two relocated loads.

Original SCORE0A74:205E..24A2, score codecs/LCG and0000:0622..06A2
execute. PI decode, CGROM/graphics, input samples, VBlank/frame waits,
audio requests and DOS files are guarded consumers. This does not accept
physical timing/audio, a full OP loop, complete game routes or DOS exactness.
"""
import argparse,hashlib,itertools,json,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD,HI,HI2
from verify_maine_join import return_to_caller
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
hextext=lambda b:b.hex() if b else '-'
class Original(Base):
 def event(self,k,a=0,b=0,data=b''):
  # File adapters inherited from the original score reader execute in their
  # real call order, mixed with render/input requests at the current clock.
  self.emit('file',('exists','open','seek','read','write','close').index(k),a,b,0,data)
 def emit(self,k,a=0,b=0,c=0,d=0,data=b''):
  self.events.append(f'{k} {self.clock} {a} {b} {c} {d} {hextext(data)}')
 def port(self,u,port,size,value,unused):
  try:
   assert port==0xa6 and size==1 and value in (0,1)
   self.emit('access',value)
  except Exception as e:self.error=e;u.emu_stop()
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  def string(off,seg,maxlen=256):
   b=bytes(u.mem_read(seg*16+off,maxlen));assert b'\0' in b;return b.split(b'\0')[0]
  def ret(n=0):return_to_caller(u,n)
  if pair[0]==0xa74 and 0x205e<=pair[1]<0x24a3:return
  if pair[0]==0 and 0x622<=pair[1]<0x6a3:
   if pair[1] in (0x622,0x666):assert words(1)==(1,);self.emit('fade',int(pair[1]==0x666),1)
   return
  if pair==(0,0x2648):self.emit('vsync');self.clock+=1;ret();return
  if pair==(0,0x1de0):self.emit('tone',self.read(0x586,'h')[0]);ret();return
  if pair==(0xda1,0x264):self.emit('sound',words(1)[0]);ret(2);return
  if pair==(0xda1,0x3ba):
   mode,off,seg=words(3);name=string(off,seg,16);assert mode==0x600 and seg==self.ds and name in (b'name',b'op')
   self.emit('song',mode,data=name);ret(6);return
  if pair==(0xda1,0x7cc):
   assert self.clock<len(self.keys),'ranking keyboard fixture exhausted'
   sample=self.keys[self.clock];self.write(0x2710,'H',sample);self.emit('poll',sample);ret();return
  if pair==(0xda1,0x2b):
   assert words(1)==(1,);self.emit('delay',1);self.clock+=1;ret(2);return
  if pair==(0xda1,0xed):
   off,seg,slot=words(3);name=string(off,seg,16);assert slot==0 and seg==self.ds and name in (b'hi01.pi',b'op1.pi') and self.loaded is None
   self.loaded=name;self.write(0x2370,'HH',0x4000,0x9000);self.emit('load',data=name);ret(6);return
  if pair==(0xda1,0x40):assert words(1)==(0,) and self.loaded is not None;self.emit('palette');ret(2);return
  if pair==(0xda1,0x65):assert words(3)==(0,0,0) and self.loaded is not None;self.emit('picture');ret(6);return
  if pair==(0,0x1618):
   assert words(4)==(0x4000,0x9000,0x2388,self.ds) and self.loaded is not None
   self.loaded=None;self.emit('free');ret(8);return
  if pair==(0,0x156c):assert words(1)==(0,);self.emit('copy',0);ret(2);return
  if pair==(0,0x3d8a):
   color,off,seg,step,y,x=words(6);assert seg==self.ds and step==16 and color in (2,7,14)
   name=string(off,seg);self.emit('name',x,y,step,color,name);ret(12);return
  if pair==(0,0x3e34):
   color,glyph,y,x=words(4);assert color in (7,14) and glyph<256;self.emit('gaiji',x,y,glyph,color);ret(8);return
  if pair==(0,0x2d5a):
   image,y,x=words(3);signed=image-65536 if image>=32768 else image
   self.emit('sprite',x,y,signed);ret(6);return
  super().body(u,address)
 def run(self,c):
  configured,rank,extra,present,seed,first,second,flags,file,keys=c
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data);u.mem_write(0x7e000,bytes(8192));self.operation=5
  u.mem_write(self.ds*16+HI,first);u.mem_write(self.ds*16+HI2,second);u.mem_write(self.ds*16+0x3f3c,flags)
  self.write(0x3f3b,'B',rank);self.write(0x3f46,'B',extra);self.write(0x5c4,'I',seed);self.write(0x1a64,'HH',0,0x9000)
  resident=bytearray((i*73+19)&255 for i in range(256));resident[15]=configured;u.mem_write(0x90000,bytes(resident))
  self.keys=keys;self.clock=0;self.file=bytearray(file);self.present=bool(present);self.events=[];self.draws=0;self.open=False
  self.error=None;self.done=False;self.sprite_names=[];self.loaded=None
  for reg,v in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
  u.mem_write(0x7f000,struct.pack('<H',0xff00));u.emu_start(self.cs*16+0x2354,0x10ffff,count=2000000)
  if self.error:raise RuntimeError('original OP ranking adapter rejected') from self.error
  assert self.done and not self.open and self.loaded is None and u.reg_read(UC_X86_REG_SP)==0xf002 and bytes(u.mem_read(0x90000,256))==resident
  self.events.append(f'END {self.clock} {self.read(0x586,"h")[0]} {self.read(0x5c4,"I")[0]} {self.draws} {int(self.present)} {self.read(0x3f3b,"B")[0]} {self.read(0x3f46,"B")[0]} '+bytes(u.mem_read(self.ds*16+HI,196)).hex()+' '+bytes(u.mem_read(self.ds*16+HI2,196)).hex()+' '+flags.hex()+' '+hextext(self.file))
  return self.events
def fixtures(o):
 r=random.Random(1320);parts=[]
 for section in range(10):
  row=bytearray(196);row[174]=section%4
  for place in range(10):
   n=4+place*9;size=(section+place)%9;row[n:n+size]=bytes(r.randrange(0x80,256) for _ in range(size));row[n+size]=0
   row[94+place*8:102+place*8]=bytes([0xa0+(section+place+i)%10 for i in range(7)]+[0xa0+(section*17+place)%96])
   row[176+place]=(0,1,0xe9,0xff)[(section+place)%4]
  parts.append(o.encode(row,section*977+1))
 file=b''.join(parts);rows=[]
 for configured,scenario in itertools.product(range(5),range(12)):
  keys=[0]*500;exitkey=(0x20,0x1000,0x2000)[scenario%3]
  if scenario<3:keys[36:91]=[exitkey]*55
  else:
   arrows=(4,8,12,4,8,12,4,8,12)[scenario-3];keys[36:125]=[arrows]*89;keys[125:173]=[exitkey]*48
   if scenario in (6,7,8):keys[36]=arrows|exitkey
   if scenario in (9,10,11):keys[40:74]=[0x10]*34 # Bomb/up/down do not exit.
  rows.append([configured,255,128,1,(0,1,318,0xffffffff)[scenario%4],bytes(196),bytes(196),bytes(range(10)),file,keys])
 # Missing/bad file recovery uses the existing OP buffers, ten real encoded
 # writes and original repeated second transformations. Keep render requests
 # raw even when they name undefined pattern indices; no pixel claim follows.
 for configured,seed,variant in itertools.product(range(5),(0,1,318),range(5)):
  keys=[0]*160;keys[36:80]=[0x20]*44;raw=bytearray(file);present=1
  # Supply a defined zero-key second buffer for recovery cases. Arbitrary
  # ciphertext can leave a name unterminated across DS globals after repeated
  # recreation decodes; the native consumer explicitly rejects that surface.
  raw[(configured+5)*196:(configured+6)*196]=bytes(196)
  if variant==0:raw.clear();present=0
  elif variant==1:raw.clear()
  elif variant==2:raw[configured*196+3]^=128
  elif variant==3:raw[(configured+5)*196+2]^=1
  else:raw=raw[:(configured+5)*196+127]
  # NUL at every ninth byte guarantees a bounded original name even after
  # failure transformations, while nonzero padding tests retained state.
  first=bytearray(196);second=bytearray(196)
  rows.append([configured,4,3,present,seed,bytes(first),bytes(second),bytes([3]*10),bytes(raw),keys])
 return rows
def fixture(c):return ' '.join(map(str,c[:5]))+' '+' '.join(hextext(b) for b in c[5:9])+' '+struct.pack('<'+'H'*len(c[9]),*c[9]).hex()+'\n'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0]
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
 o=Original(a.target,a.decoded_dir,0x1000)
 if a.reference_dir:
  ref=a.reference_dir;previous=json.loads((ref/'receipt.json').read_text());assert previous['passed']
  path=out/'fixtures.txt';path.write_bytes((ref/'fixtures.txt').read_bytes());expected=(ref/'original-1000.txt').read_bytes()
  assert sha(expected)==previous['trace_sha256'] and sha(path.read_bytes())==previous['fixture_sha256'];count=previous['cases']
 else:
  rows=fixtures(o);count=len(rows);path=out/'fixtures.txt';path.write_text(''.join(map(fixture,rows)));traces=[]
  for load in (0x1000,0x2000):
   o=Original(a.target,a.decoded_dir,load);lines=[]
   for i,c in enumerate(rows):
    try:lines.extend([f'CASE {i}',*o.run(c)])
    except Exception:
     (out/'failed-case.json').write_text(json.dumps(dict(index=i,load=hex(load),clock=o.clock,last_events=o.events[-20:]),indent=2)+'\n');raise
    if i%10==0:print(f'OP ranking original load{load:04x} case{i}/{len(rows)}',flush=True)
   trace=('\n'.join(lines)+'\n').encode();(out/f'original-{load:04x}.txt').write_bytes(trace);traces.append(trace)
  assert traces[0]==traces[1];expected=traces[0]
 result=subprocess.run([str(a.exe.resolve()),'--trace',str(path)],capture_output=True);(out/'native.txt').write_bytes(result.stdout);(out/'stderr.txt').write_bytes(result.stderr)
 if result.returncode or result.stdout!=expected:
  x=result.stdout.splitlines();y=expected.splitlines();i=next((i for i,(a,b) in enumerate(zip(x,y)) if a!=b),min(len(x),len(y)))
  (out/'mismatch.json').write_text(json.dumps(dict(line=i,actual=str(x[i:i+2]),expected=str(y[i:i+2]),returncode=result.returncode),indent=2)+'\n');raise ValueError(f'OP ranking differs line{i}')
 assert source_manifest(root)[0]==manifest
 receipt=dict(passed=True,cases=count,loads=['1000','2000'],original_cpu_reexecuted=not bool(a.reference_dir),reference_dir=str(a.reference_dir) if a.reference_dir else None,
  source_manifest=manifest,packed_sha256=PACKED,payload_sha256=PAYLOAD,fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(expected),exe_sha256=sha(a.exe.read_bytes()),
  extents=[dict(segment='0A74',start='205E',end='24A3',sha256=sha(o.payload[0xc79e:0xcbe3])),dict(segment='0000',start='0622',end='06A3',sha256=sha(o.payload[0x622:0x6a3]))],
  utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Original OP ranking/native PASS',count,'cases')
if __name__=='__main__':main()
