#!/usr/bin/env python3
"""Original Bomb BB/fill/CDG/mono kernels versus retained indexed native screens.

Execute original graphics instructions at two loads. Independent BFNT input
decoding and an explicit GRCG/direct-plane write shadow supply visible pixels;
physical pages/scroll registers, display timing, audio and live MAIN are outside
this component claim. Captures are compressed; replay uses fresh directories.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_player_bomb import Original,fixture,sha
from verify_marisa_pixels import planes
from probe_assets import main_assets
from verify import source_manifest

SCREEN=640*400
class Shadow:
 def __init__(self,original,seed):
  self.o=original;self.mode=0;self.tiles=[0]*4;self.index=0;self.writes=0;self.ports=0
  self.screen=bytearray(bytes((i*73+seed)&15 for i in range(16))*(SCREEN//16))
  self.ph=original.u.hook_add(unicorn.UC_HOOK_INSN,self.port,None,1,0,UC_X86_INS_OUT)
  self.wh=original.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.write)
 def port(self,u,port,size,value,unused):
  try:
   if size!=1 or port not in (0x7c,0x7e):raise ValueError('unexpected Bomb GRCG port')
   if port==0x7c:self.mode=value;self.index=0
   else:self.tiles[self.index]=value;self.index=(self.index+1)%4
   self.ports+=1
  except Exception as e:self.o.error=e;u.emu_stop()
 def write(self,u,access,address,size,value,unused):
  try:
   if self.mode&128:
    if not 0xa8000<=address<0xa8000+32000:return
    enabled=(~self.mode)&15
    for byte in range(size):
     at=address-0xa8000+byte
     if at>=32000:continue
     mask=(value>>(byte*8))&255
     for bit in range(8):
      if self.mode&64 and not mask&(128>>bit):continue
      color=sum(1<<p for p in range(4) if self.tiles[p]&(128>>bit))
      pos=at*8+bit;self.screen[pos]=(self.screen[pos]&~enabled)|(color&enabled)
   else:
    plane=next((p for p,base in enumerate((0xa8000,0xb0000,0xb8000,0xe0000)) if base<=address<base+32000),None)
    if plane is None:return
    base=(0xa8000,0xb0000,0xb8000,0xe0000)[plane];enabled=1<<plane
    for byte in range(size):
     at=address-base+byte
     if at>=32000:continue
     mask=(value>>(byte*8))&255
     for bit in range(8):
      pos=at*8+bit;self.screen[pos]=(self.screen[pos]&~enabled)|(enabled if mask&(128>>bit) else 0)
   self.writes+=1
  except Exception as e:self.o.error=e;u.emu_stop()
 def close(self):self.o.u.hook_del(self.ph);self.o.u.hook_del(self.wh)

def fixtures():
 for character,cel,line in itertools.product(range(2),range(16),(0,1,15,16,383,384,399)):
  yield ['T',character,cel,line,(cel+line)%16]
 for character,frame,mod4 in itertools.product(range(2),(48,49,80,81,84,119,120,160,161,175),(0,1)):
  yield ['F',*fixture(character=character,frame=frame,mod4=mod4,variant=frame%14,cursor=255),frame%16]
 for character,variant in itertools.product(range(2),range(14)):
  yield ['S',*fixture(character=character,frame=49,variant=variant,cursor=255),variant%16]
 for character in range(2):
  yield ['L',*fixture(character=character,steps=128,frame=48,stage=65520,cursor=255),7]

def stage_assets(o,assets,character):
 cdg=assets[f'BB{character}.CDG'];header=bytearray(cdg[:16]);struct.pack_into('<H',header,14,0x9000)
 o.u.mem_write(0x83978,bytes(header));o.u.mem_write(0x90000,cdg[16:])
 _,_,data=planes(assets['MIKO16.BFT'],92);o.u.mem_write(0x9e000,data[:32]);o.write(0x2bb4,'H',0x9e00)
 o.u.mem_write(0x9f000,assets[f'BB{character}.BB']);o.write(0x436e,'H',0x9f00);o.write(0x5398,'B',character)

def original_screens(o,row,assets):
 op=row[0]
 if op=='T':
  _,character,cel,line,seed=row;o.reset();o.error=None;stage_assets(o,assets,character);o.write(0x4278,'H',line)
 else:
  character=row[1];seed=row[-1];o.seed_bomb(row[1:-1]);stage_assets(o,assets,character)
 o.pixels=True;shadow=Shadow(o,seed)
 try:
  if op=='S':
   # The bounded star-only entry inherits its caller's RMW/color state.
   # Execute the original caller setup rather than treating mono stores as
   # direct blue-plane writes with GRCG disabled.
   o.call_args(0x1666);o.u.reg_write(UC_X86_REG_AX,(14 if not character else 8)<<8);o.call_args(0x1672)
  if op=='T':o.call_args(0x553a,(cel,));yield bytes(shadow.screen),shadow.writes,shadow.ports
  else:
   for step in range(row[2]):
    o.execute(op,character);yield bytes(shadow.screen),shadow.writes,shadow.ports
    if op=='L':o.next_frame()
 finally:shadow.close()

def read_exact(stream,size):
 result=bytearray()
 while len(result)<size:
  chunk=stream.read(size-len(result))
  if not chunk:break
  result.extend(chunk)
 return bytes(result)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','hdi','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);p.add_argument('--runner')
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh Bomb pixel output directory')
 out.mkdir(parents=True);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 assets=main_assets(a.hdi);names=['BB0.BB','BB1.BB','BB0.CDG','BB1.CDG','MIKO16.BFT']
 for name in names:(out/name).write_bytes(assets[name])
 rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures());text='\n'.join(' '.join(map(str,row)) for row in rows)+'\n'
 fixture_path=out/'fixtures.txt';fixture_path.write_text(text);records=[];reference=None;raw=hashlib.sha256()
 if a.reference_dir:
  reference=json.loads((a.reference_dir/'receipt.json').read_text())
  assert reference['passed'] and reference['target_sha256']==sha(a.target.read_bytes()) and reference['hdi_sha256']==sha(a.hdi.read_bytes()) and reference['fixture_sha256']==sha(text.encode())
  trace=a.reference_dir/'original.gz';assert sha(trace.read_bytes())==reference['trace_gzip_sha256'];records=reference['records']
 else:
  trace=out/'original.gz'
  for load in (0x1000,0x2000):
   o=Original(a.target.read_bytes(),load);current=[];digest=hashlib.sha256()
   with gzip.open(trace,'wb',compresslevel=6) if load==0x1000 else gzip.open(trace,'rb') as f:
    for index,row in enumerate(rows):
     for step,(screen,writes,ports) in enumerate(original_screens(o,row,assets)):
      digest.update(screen);current.append(dict(case=index,step=step,sha256=sha(screen),writes=writes,ports=ports))
      if load==0x1000:f.write(screen)
      else:assert read_exact(f,SCREEN)==screen,'Bomb pixel load metamorphism differs'
     if (index+1)%32==0:print(hex(load),index+1,'original pixel cases',flush=True)
    if load==0x2000:assert not f.read(1),'extra original pixel reference'
   if records:assert records==current and raw.hexdigest()==digest.hexdigest(),'Bomb pixel load events differ'
   else:records=current;raw=digest
 stderr=out/'native-stderr.txt';native=out/'native.gz';env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
 command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--bomb-pixels',str(fixture_path)]
 actual_digest=hashlib.sha256()
 with stderr.open('wb') as err:
  process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=err,env=env)
  try:
   with gzip.open(trace,'rb') as wanted,gzip.open(native,'wb',compresslevel=6) as got:
    for index,record in enumerate(records):
     x=read_exact(wanted,SCREEN);y=read_exact(process.stdout,SCREEN)
     if len(x)!=SCREEN or x!=y or sha(x)!=record['sha256']:
      at=next((i for i,(q,r) in enumerate(zip(x,y)) if q!=r),min(len(x),len(y)))
      (out/'mismatch.json').write_text(json.dumps(dict(record=index,input=rows[record['case']],pixel=at,x=at%640,y=at//640,original=x[at] if at<len(x) else None,native=y[at] if at<len(y) else None),indent=2)+'\n')
      raise ValueError(f'Bomb pixel record{index} at{at} differs')
     actual_digest.update(y);got.write(y)
    assert not wanted.read(1) and not process.stdout.read(1),'extra Bomb pixels'
   assert process.wait(timeout=240)==0,'native Bomb pixel consumer failed'
  finally:
   if process.poll() is None:process.kill();process.wait()
 assert manifest==source_manifest(Path(__file__).resolve().parents[1])[0],'source changed during Bomb pixels'
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,
  target_sha256=sha(a.target.read_bytes()),hdi_sha256=sha(a.hdi.read_bytes()),fixture_sha256=sha(text.encode()),
  executable_sha256=sha(a.exe.read_bytes()),trace_raw_sha256=actual_digest.hexdigest(),trace_gzip_sha256=sha(trace.read_bytes()),
  native_gzip_sha256=sha(native.read_bytes()),cases=len(rows),screens=len(records),compared_pixels=len(records)*SCREEN,
  records=records,asset_sha256={name:sha(assets[name]) for name in names},load_segments=[4096,8192],
  original_cpu_reexecuted=not bool(reference),reference_dir=str(a.reference_dir) if reference else None,
  unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','cases','screens','compared_pixels')}))
if __name__=='__main__':main()
