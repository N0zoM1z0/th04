#!/usr/bin/env python3
"""Original OP Music Room caller/animation/state at two relocated loads.

0A74:1795..1E39, polar0DA1:01A8..01C3, LCG0000:204E..2077 and
blackout0000:0666..06A2 execute original instructions. Graphics/font/blue-plane
storage, PI decoding, DOS files, input/waits and sound are guarded request
consumers here. Separate raster controls execute the original drawing kernels.
No physical timing/audio/full OP/full-game/DOS exact claim follows.
"""
import argparse,hashlib,itertools,json,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD
from verify_maine_join import return_to_caller
from verify_cutscene import ending_assets
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
hextext=lambda b:b.hex() if b else '-'
def polygon_state(o):
 return b''.join(bytes(o.u.mem_read(o.ds*16+0x39dc+i*4,4))+bytes(o.u.mem_read(o.ds*16+0x3a1c+i*4,4)) for i in range(16))+bytes(o.u.mem_read(o.ds*16+0x3a5c,32))
class Original(Base):
 def emit(self,k,a=0,b=0,c=0,d=0,data=b''):
  self.events.append(f'{k} {self.clock} {a} {b} {c} {d} {hextext(data)}')
 def port(self,u,port,size,value,unused):
  try:
   assert size==1
   if port in (0xa4,0xa6):assert value in (0,1);self.emit('show' if port==0xa4 else 'access',value)
   else:assert port==0x7c and value==0;self.emit('grcg')
  except Exception as e:self.error=e;u.emu_stop()
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  def string(off,seg,maxlen=256):
   b=bytes(u.mem_read(seg*16+off,maxlen));assert b'\0' in b;return b.split(b'\0')[0]
  def ret(n=0,far=True):return_to_caller(u,n,far)
  if pair[0]==0xa74:
   if pair[1] in (0x1828,0x1859,0x1867):
    self.emit({0x1828:'blue_snap',0x1859:'blue_free',0x1867:'blue_restore'}[pair[1]]);ret(far=False);return
   if 0x1795<=pair[1]<0x1e3a:return
   if pair[1]==0xff00:self.done=True;u.emu_stop();return
  if pair[0]==0xda1 and 0x1a8<=pair[1]<0x1c4:return
  if pair[0]==0 and 0x204e<=pair[1]<0x2078:
   if pair[1]==0x204e:self.draws+=1
   return
  if pair[0]==0 and 0x666<=pair[1]<0x6a3:
   if pair[1]==0x666:assert words(1)==(1,);self.emit('fade',1,1)
   return
  if pair==(0,0x2648):self.emit('vsync');self.clock+=1;ret();return
  if pair==(0,0x1de0):self.emit('tone',self.read(0x586,'h')[0]);ret();return
  if pair==(0xda1,0x264):self.emit('sound',words(1)[0]);ret(2);return
  if pair==(0xda1,0x3ba):
   mode,off,seg=words(3);assert mode==0x600;self.emit('song',mode,data=string(off,seg,16));ret(6);return
  if pair==(0xda1,0x7cc):
   assert self.clock<len(self.keys),'Music input fixture exhausted'
   sample=self.keys[self.clock];self.write(0x2710,'H',sample);self.emit('poll',sample);ret();return
  if pair==(0xda1,0xcce):assert words(1)==(1,);self.emit('delay',1);self.clock+=1;ret(2);return
  if pair==(0xda1,0xed):
   off,seg,slot=words(3);name=string(off,seg,16);assert slot==0 and name==b'music.pi' and self.loaded is None
   self.loaded=name;self.write(0x2370,'HH',0x4000,0x9000);self.emit('load',data=name);ret(6);return
  if pair==(0xda1,0x40):assert words(1)==(0,) and self.loaded is not None;self.emit('palette');ret(2);return
  if pair==(0xda1,0x65):assert words(3)==(0,0,0) and self.loaded is not None;self.emit('picture');ret(6);return
  if pair==(0,0x1618):assert words(4)==(0x4000,0x9000,0x2388,self.ds) and self.loaded is not None;self.loaded=None;self.emit('free');ret(8);return
  if pair==(0,0x156c):assert words(1)==(0,);self.emit('copy');ret(2);return
  if pair in ((0xda1,0xcc0),(0,0x24ee),(0,0x1532),(0xda1,0xa18),(0xda1,0xab6)):
   self.emit({(0xda1,0xcc0):'cdg_free',(0,0x24ee):'text_clear',(0,0x1532):'clear',(0xda1,0xa18):'background_snap',(0xda1,0xab6):'background_free'}[pair]);ret();return
  if pair==(0xda1,0xae8):assert words(4)==(320,320,64,320);self.emit('background_rect',320,64,320,320);ret(8);return
  if pair==(0,0x10d2):assert words(2)==(15,0xce);self.emit('grcg',0xce,15);ret(4);return
  if pair==(0,0xdc2):
   count,off,seg=words(3);assert off==0x39b4 and seg==self.ds and 3<=count<=6
   self.emit('polygon',count,data=bytes(u.mem_read(seg*16+off,(count+1)*4)));ret(6);return
  if pair==(0xda1,0x4a4):
   off,seg,color,y,x=words(5);assert seg==self.ds and color in (3,5,7)
   self.emit('text',x,y,color,self.read(0xa3c,'H')[0],string(off,seg));ret(10);return
  if pair==(0,0xa7a):
   off,seg=words(2);name=string(off,seg,16);assert name==b'_MUSIC.TXT' and not self.open
   self.open=True;self.position=0;self.emit('file',0,data=name);ret(4);return
  if pair==(0,0xab6):
   origin,lo,hi=words(3);assert self.open and origin==0 and hi==0;self.position=lo;self.emit('file',1,lo);ret(6);return
  if pair==(0,0x9c6):
   count,off,seg=words(3);assert self.open and (count,off,seg)==(800,0x3a92,self.ds)
   b=self.comments[self.position:self.position+count];assert len(b)==count;u.mem_write(seg*16+off,b)
   self.emit('file',2,count,data=b);u.reg_write(UC_X86_REG_AX,count);ret(6);return
  if pair==(0,0x95a):assert self.open;self.open=False;self.emit('file',3);ret();return
  raise ValueError(f'unexpected OP Music consumer {pair[0]:04x}:{pair[1]:04x}')
 def run(self,c):
  initialized,playing,seed,state,comments,keys=c;u=self.u
  u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data)
  self.write(0xf6e,'BB',initialized,playing);self.write(0x5c4,'I',seed)
  for i in range(16):u.mem_write(self.ds*16+0x39dc+i*4,state[i*8:i*8+4]);u.mem_write(self.ds*16+0x3a1c+i*4,state[i*8+4:i*8+8])
  u.mem_write(self.ds*16+0x3a5c,state[128:]);self.comments=comments;self.keys=keys;self.clock=0;self.draws=0;self.events=[]
  self.error=None;self.done=False;self.loaded=None;self.open=False
  for reg,v in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
  u.mem_write(0x7f000,struct.pack('<H',0xff00));u.emu_start(self.cs*16+0x1c77,0x10ffff,count=3000000)
  if self.error:raise RuntimeError('original OP Music adapter rejected') from self.error
  assert self.done and not self.open and self.loaded is None and u.reg_read(UC_X86_REG_SP)==0xf002
  self.events.append(f'END {self.clock} {self.read(0x586,"h")[0]} {self.read(0x5c4,"I")[0]} {self.draws} {self.read(0xf6e,"B")[0]} {self.read(0xf6f,"B")[0]} {self.read(0x3a7c,"B")[0]} {self.read(0x3a7d,"B")[0]} {self.read(0x3a7e,"B")[0]} {self.read(0xa3c,"H")[0]} '+polygon_state(self).hex()+' '+bytes(u.mem_read(self.ds*16+0x3a92,800)).hex())
  return self.events
def fixtures(comments):
 r=random.Random(1321);rows=[]
 for playing,scenario in itertools.product((0,1,20,21),range(8)):
  keys=[0]*150;keys[80:90]=[0x1000]*10
  if scenario==0:keys[1:7]=[0x1000]*6 # release on entry must precede controls
  if scenario in (1,2,3):keys[3:8]=[(1,2,3)[scenario-1]]*5
  if scenario==4:keys[3:8]=[1]*5;keys[10:16]=[0x20]*6
  if scenario==5:keys[3:8]=[2]*5;keys[10:16]=[0x2000]*6
  if scenario==6:keys[4]=0x1020 # play, then old cancel sample after ten refreshes
  if scenario==7:keys[4]=0x1003 # both arrows then cancel
  initialized=scenario%2;state=b''.join(struct.pack('<4h',(-1,0,638,639)[i%4],(7950,-1600,0,6300)[i%4],(-3,-1,1,4)[i%4],32+(i%4)*16) for i in range(16))+bytes(r.randrange(256) for _ in range(32))
  rows.append((initialized,playing,(0,1,318,0xffffffff)[scenario%4],state,comments,keys))
 return rows
def fixture(c):return ' '.join(map(str,c[:3]))+' '+' '.join(hextext(b) for b in c[3:5])+' '+struct.pack('<'+'H'*len(c[5]),*c[5]).hex()+'\n'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','hdi','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0]
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);o=Original(a.target,a.decoded_dir,0x1000)
 if a.reference_dir:
  ref=a.reference_dir;previous=json.loads((ref/'receipt.json').read_text());assert previous['passed']
  path=out/'fixtures.txt';path.write_bytes((ref/'fixtures.txt').read_bytes());expected=(ref/'original-1000.txt').read_bytes()
  assert sha(expected)==previous['trace_sha256'] and sha(path.read_bytes())==previous['fixture_sha256'];count=previous['cases']
 else:
  rows=fixtures(ending_assets(a.hdi)['_MUSIC.TXT']);count=len(rows);path=out/'fixtures.txt';path.write_text(''.join(map(fixture,rows)));traces=[]
  for load in (0x1000,0x2000):
   o=Original(a.target,a.decoded_dir,load);lines=[]
   for i,c in enumerate(rows):
    try:lines.extend([f'CASE {i}',*o.run(c)])
    except Exception:
     (out/'failed-case.json').write_text(json.dumps(dict(index=i,load=hex(load),clock=o.clock,last_events=o.events[-20:]),indent=2)+'\n');raise
   trace=('\n'.join(lines)+'\n').encode();(out/f'original-{load:04x}.txt').write_bytes(trace);traces.append(trace)
   print(f'OP Music original load{load:04x}: {count} cases',flush=True)
  assert traces[0]==traces[1];expected=traces[0]
 result=subprocess.run([str(a.exe.resolve()),'--trace',str(path)],capture_output=True);(out/'native.txt').write_bytes(result.stdout);(out/'stderr.txt').write_bytes(result.stderr)
 if result.returncode or result.stdout!=expected:
  x=result.stdout.splitlines();y=expected.splitlines();i=next((i for i,(a,b) in enumerate(zip(x,y)) if a!=b),min(len(x),len(y)))
  (out/'mismatch.json').write_text(json.dumps(dict(line=i,actual=str(x[i:i+2]),expected=str(y[i:i+2]),returncode=result.returncode),indent=2)+'\n');raise ValueError(f'OP Music differs line{i}')
 assert source_manifest(root)[0]==manifest
 receipt=dict(passed=True,cases=count,loads=['1000','2000'],original_cpu_reexecuted=not bool(a.reference_dir),reference_dir=str(a.reference_dir) if a.reference_dir else None,
  source_manifest=manifest,packed_sha256=PACKED,payload_sha256=PAYLOAD,fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(expected),exe_sha256=sha(a.exe.read_bytes()),
  extents=[dict(segment='0A74',start='1795',end='1E3A',sha256=sha(o.payload[0xbed5:0xc57a]))],
  muted=True,scope=__doc__,utc=datetime.now(timezone.utc).isoformat())
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(f'OP Music PASS: {count} cases')
if __name__=='__main__':main()
