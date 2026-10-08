#!/usr/bin/env python3
"""Original MAIN player-render instructions and rolling kernels versus native.

MAIN relative0AAF:610D..625B and actual polar/scroll helpers execute at two
loads. Request-only graphics ABI adapters are distinct from full original
kernel execution. BFNT planar/tiny staging and visible GRCG/direct-plane
shadow are explicit input/hardware adapters. No physical display timing,
audio, complete ordinary route, or DOS exact acceptance follows.
"""
import argparse,gzip,hashlib,itertools,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
import unicorn
from verify_player_bomb import Original as Base,sha
from verify_player_bomb_pixels import Shadow,read_exact,SCREEN
from verify_marisa_pixels import planes
from probe_assets import main_assets
from verify import source_manifest

class Original(Base):
 def body(self,u,address,size,unused):
  actual=u.reg_read(UC_X86_REG_CS);pair=(actual+self.delta,address-actual*16)
  sp=u.reg_read(UC_X86_REG_SP)
  def ret(far,words):
   values=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
   u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+words*2)
   if far:u.reg_write(UC_X86_REG_CS,values[1])
   u.reg_write(UC_X86_REG_IP,values[0])
  if pair in ((0x2000,0x2d3e),(0x2000,0x2b78)):
   white=pair[1]==0x2b78
   if white:
    color,plane,pattern,y,x=struct.unpack('<HHHhh',u.mem_read(0x70000+sp+4,10))
    assert color==0xffc0 and plane==0,'unexpected white-player ABI'
   else:pattern,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6))
   self.requests.append([int(white),x,y,pattern])
   if not self.pixels:ret(True,5 if white else 3)
  elif pair==(0x2aaf,0x1a56):
   pattern=struct.unpack('<H',u.mem_read(0x70000+sp+2,2))[0]
   signed=lambda n:n-65536 if n&32768 else n
   self.requests.append([2,signed(u.reg_read(UC_X86_REG_AX)),signed(u.reg_read(UC_X86_REG_DX)),pattern])
   if not self.pixels:ret(False,1)
 def render(self,row,pixels=False):
  self.reset();self.error=None;self.requests=[];self.pixels=pixels
  character,x,y,vx,miss,inv,radius,angle,ox,oy,level,pattern,mod4,scroll,line,seed=row
  for at,fmt,value in [(0x464e,'h',x),(0x4650,'h',y),(0x4656,'h',vx),(0x466a,'B',miss),
      (0x4662,'B',inv),(0x467a,'H',radius),(0x4679,'B',angle),(0x466c,'h',ox),(0x466e,'h',oy),
      (0x4665,'B',level),(0x4674,'H',pattern),(0x538d,'B',mod4),(0x427c,'B',scroll),(0x4278,'H',line)]:self.write(at,fmt,value)
  self.u.reg_write(UC_X86_REG_ES,0xa800)
  if pixels:stage_assets(self,self.assets,character)
  shadow=Shadow(self,seed) if pixels else None
  try:
   self.call_args(0x610d)
   requests='D '+str(len(self.requests))+''.join(' '+' '.join(map(str,d)) for d in self.requests)
   return (requests,bytes(shadow.screen),shadow.writes,shadow.ports) if pixels else requests
  finally:
   if shadow:shadow.close()

def stage_assets(o,assets,character):
 for pattern in range(4):
  blob=assets['MIKOD.BFT'] if pattern==3 else assets['MIKO.BFT' if character==0 else 'MARI.BFT']
  w,h,data=planes(blob,0 if pattern==3 else pattern);segment=0x9000+pattern*0x100
  o.u.mem_write(segment*16,data);o.write(0x2ac4+pattern*2,'H',segment);o.write(0x2ec4+pattern*2,'H',(w//8<<8)|h)
 # Independent input adapter for the tiny color-mask format consumed by1A56.
 # Header80/color, sixteen two-byte MSB-first rows; zero word terminates.
 for pattern in (38,39):
  w,h,data=planes(assets['MIKO16.BFT'],pattern-28);assert (w,h)==(16,16)
  masks=[]
  for color in range(15,0,-1):
   mask=bytearray(32)
   for y in range(16):
    for x in range(16):
     at=y*2+x//8;bit=128>>(x&7)
     value=sum(1<<p for p in range(4) if data[(p+1)*32+at]&bit)
     if value==color:mask[at]|=bit
   if any(mask):masks.append(bytes((0x80,color))+bytes(mask))
  assert len(masks)<=4,'option exceeds original tiny converter color budget'
  segment=0x9400+(pattern-38)*0x100;o.u.mem_write(segment*16,b''.join(masks)+bytes(2));o.write(0x2ac4+pattern*2,'H',segment)

def fixture(character=0,x=3072,y=5120,vx=0,miss=0,inv=192,radius=257,angle=37,
            ox=3072,oy=5120,level=2,pattern=None,mod4=0,scroll=1,line=399,seed=7):
 return [character,x,y,vx,miss,inv,radius,angle,ox,oy,level,38+character if pattern is None else pattern,mod4,scroll,line,seed]

def state_fixtures():
 for vx,miss,inv,level,mod4,scroll,line in itertools.product((-32768,-1,0,1,32767),(0,1,2,32,33,255),(0,1,192,255),(0,1,2,255),range(4),(0,1),(0,399)):
  if (vx+miss+inv+level+mod4+scroll+line)%37==0:yield fixture(vx=vx,miss=miss,inv=inv,level=level,mod4=mod4,scroll=scroll,line=line)
 for angle,radius,edge in itertools.product(range(256),(0,1,257,32767,32768,65535),range(4)):
  x,y=((-129,-128),(-128,-129),(6271,6015),(6272,6016))[edge]
  yield fixture(x=x,y=y,miss=2,radius=radius,angle=angle)
 for x,y,ox,oy,line in itertools.product((-32768,-129,-128,-1,0,32767),(-32768,-129,32767),(-32768,32767),(-32768,32767),(0,399,65535)):
  yield fixture(x=x,y=y,ox=ox,oy=oy,line=line)

def pixel_fixtures():
 for character,vx,mod4,shift,line in itertools.product(range(2),(-1,0,1),(0,1),range(8),(0,399)):
  yield fixture(character=character,vx=vx,mod4=mod4,x=(192+shift)*16,ox=(192+shift)*16,line=line,seed=shift)
 for character,angle,radius,x,y in itertools.product(range(2),(0,37,64,129,255),(0,1,257,1023,32768,65535),(-128,3072,6271),(-128,5120,6015)):
  if (character+angle+radius+x+y)%11==0:yield fixture(character=character,x=x,y=y,miss=2,radius=radius,angle=angle,seed=angle%16)
 for character,miss,scroll in itertools.product(range(2),(0,1,32,33),(0,1)):
  yield fixture(character=character,miss=miss,scroll=scroll)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','hdi','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int)
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use fresh player-render output directory')
 out.mkdir(parents=True);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 assets=main_assets(a.hdi);names=('MIKO.BFT','MARI.BFT','MIKOD.BFT','MIKO16.BFT')
 for name in names:(out/name).write_bytes(assets[name])
 states=list(state_fixtures());pixels=list(pixel_fixtures())
 if a.limit:states=states[:a.limit];pixels=pixels[:a.limit]
 texts=['\n'.join(' '.join(map(str,row)) for row in rows)+'\n' for rows in (states,pixels)]
 for name,text in zip(('state-fixtures.txt','pixel-fixtures.txt'),texts):(out/name).write_text(text)
 reference=None;records=[]
 if a.reference_dir:
  reference=json.loads((a.reference_dir/'receipt.json').read_text())
  assert reference['passed'] and reference['target_sha256']==sha(a.target.read_bytes()) and reference['hdi_sha256']==sha(a.hdi.read_bytes()) and reference['fixture_sha256']==list(map(lambda x:sha(x.encode()),texts))
  expected=(a.reference_dir/'original.txt').read_text().splitlines();trace=a.reference_dir/'original.gz';records=reference['records']
  assert sha((a.reference_dir/'original.txt').read_bytes())==reference['state_sha256'] and sha(trace.read_bytes())==reference['trace_gzip_sha256']
 else:
  expected=[];trace=out/'original.gz'
  for load in (0x1000,0x2000):
   original=Original(a.target.read_bytes(),load);original.assets=assets
   current=[original.render(row) for row in states]
   if expected:assert expected==current,'player requests changed with load'
   else:expected=current
   current_records=[]
   with gzip.open(trace,'wb',compresslevel=6) if load==0x1000 else gzip.open(trace,'rb') as f:
    for i,row in enumerate(pixels):
     request,screen,writes,ports=original.render(row,True)
     assert request==original.render(row),'pixel kernel execution changed caller requests'
     current_records.append(dict(case=i,sha256=sha(screen),writes=writes,ports=ports,requests=request))
     if load==0x1000:f.write(screen)
     else:assert read_exact(f,SCREEN)==screen,'player pixels changed with load'
     if (i+1)%64==0:print(hex(load),i+1,'player pixel cases',flush=True)
    if load==0x2000:assert not f.read(1)
   if records:assert records==current_records,'player kernel events changed with load'
   else:records=current_records
  (out/'original.txt').write_text('\n'.join(expected)+'\n')
 command=[str(a.exe.resolve()),'--player-render-vectors',str(out/'state-fixtures.txt')]
 result=subprocess.run(command,check=True,capture_output=True,text=True,timeout=120)
 (out/'native.txt').write_text(result.stdout)
 for i,(want,got) in enumerate(itertools.zip_longest(expected,result.stdout.splitlines())):
  if want!=got:
   (out/'mismatch.json').write_text(json.dumps(dict(case=i,row=states[i],original=want,native=got),indent=2)+'\n');raise ValueError(f'player request case{i} differs')
 digest=hashlib.sha256();native=out/'native.gz'
 with (out/'native-stderr.txt').open('wb') as err:
  process=subprocess.Popen([str(a.exe.resolve()),'--player-render-pixels',str(out/'pixel-fixtures.txt')],stdout=subprocess.PIPE,stderr=err)
  try:
   with gzip.open(trace,'rb') as wanted,gzip.open(native,'wb',compresslevel=6) as got:
    for i,record in enumerate(records):
     x=read_exact(wanted,SCREEN);y=read_exact(process.stdout,SCREEN)
     if len(y)!=SCREEN or x!=y or sha(x)!=record['sha256']:
      at=next((j for j,(v,w) in enumerate(zip(x,y)) if v!=w),min(len(x),len(y)))
      (out/'mismatch.json').write_text(json.dumps(dict(case=i,row=pixels[i],pixel=at,x=at%640,y=at//640,original=x[at] if at<len(x) else None,native=y[at] if at<len(y) else None),indent=2)+'\n');raise ValueError(f'player pixel case{i} differs at{at}')
     digest.update(y);got.write(y)
    assert not wanted.read(1) and not process.stdout.read(1),'extra player pixels'
   assert process.wait(timeout=120)==0,'player pixel consumer failed'
  finally:
   if process.poll() is None:process.kill();process.wait()
 assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest,'source changed during player-render controls'
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,
  target_sha256=sha(a.target.read_bytes()),hdi_sha256=sha(a.hdi.read_bytes()),executable_sha256=sha(a.exe.read_bytes()),
  fixture_sha256=[sha(text.encode()) for text in texts],state_sha256=sha(result.stdout.encode()),
  state_cases=len(states),pixel_cases=len(pixels),screens=len(records),compared_pixels=len(records)*SCREEN,
  trace_raw_sha256=digest.hexdigest(),trace_gzip_sha256=sha(trace.read_bytes()),native_gzip_sha256=sha(native.read_bytes()),
  asset_sha256={name:sha(assets[name]) for name in names},records=records,load_segments=[4096,8192],
  original_cpu_reexecuted=not bool(reference),reference_dir=str(a.reference_dir) if reference else None,
  unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','state_cases','pixel_cases','compared_pixels')}))
if __name__=='__main__':main()
