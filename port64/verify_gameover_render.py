#!/usr/bin/env python3
"""Original MAIN TRAM stores versus native Game Over text and complete RGB.

Actual gaiji/ANK and playfield wipe/black instructions execute at two loads.
Frozen indexed graphics/palette and supplied CGROM are explicit adapters. RGB
composition follows pinned emulator video policy, not physical video. Optional
attested scene requests retain the preceding two-load clock control's scope.
Captures are compressed and every replay requires a fresh output directory.
"""
import argparse,gzip,hashlib,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image
import unicorn
from unicorn.x86_const import *
from verify_player_lifecycle import Original as Base
from verify_cutscene_pixels import Raster
from verify_player_bomb_pixels import read_exact
from probe_assets import main_assets
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
SIZE=256000+8000+768000
EXTENTS=((0,0x1b0c,0x1ba6),(0,0x229e,0x2368),(0xaaf,0x625b,0x62b3))

class Original(Base):
 def __init__(self,target,load,font,gaiji):
  super().__init__(target,load)
  self.gaiji=gaiji;self.rom=Raster(None,Image.open(font).convert('L'),gaiji,{},(None,None)).rom
  self.masks={};self.calls=0;self.writes=0
  self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.tram_write)
 def tram_write(self,u,access,address,size,value,unused):
  if 0xa0000<=address<0xa0fa0 or 0xa2000<=address<0xa2fa0:self.writes+=1
 def body(self,u,address,size,unused):
  actual=u.reg_read(UC_X86_REG_CS);rel=actual-self.load;ip=address-actual*16
  if ip==0xf000:u.emu_stop();return
  if any(rel==segment and lo<=ip<hi for segment,lo,hi in EXTENTS):return
  raise ValueError(f'unexpected Game Over text instruction {rel:04x}:{ip:04x}')
 def call(self,segment,ip,args=(),far=False):
  cs=self.load+segment;u=self.u;self.error=None
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                    (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):
   u.reg_write(reg,value)
  stack=(0xf000,cs,*args) if far else (0xf000,*args)
  u.mem_write(0x7e000,struct.pack('<'+'H'*len(stack),*stack))
  u.emu_start(cs*16+ip,cs*16+0xf000,count=200000)
  if self.error:raise RuntimeError('original Game Over TRAM rejected') from self.error
  assert u.reg_read(UC_X86_REG_CS)==cs and u.reg_read(UC_X86_REG_IP)==0xf000
  assert u.reg_read(UC_X86_REG_SP)==0xe000+len(stack)*2,'text ABI did not return'
  self.calls+=1
 def command(self,line):
  w=line.split();op=w[0]
  if op=='CASE':
   seed=int(w[1]);self.reset();self.write(0x768,'H',0xa000)
   codes=np.zeros((2000,2),dtype=np.uint8);codes[:,0]=(np.arange(2000)*31+seed)&127
   attrs=np.zeros((2000,2),dtype=np.uint8);attrs[:,0]=np.array([0,1,0xe1,0x85,0x41,0x45])[(np.arange(2000)+seed)%6]
   self.u.mem_write(0xa0000,codes.tobytes());self.u.mem_write(0xa2000,attrs.tobytes())
   self.indices=((np.arange(256000)*73+seed)&15).astype(np.uint8).reshape(400,640)
   self.palette=(((np.arange(48)*29+seed)&15)<<4).astype(np.uint8).reshape(16,3)
  elif op in ('W','B'):self.call(0xaaf,0x625b if op=='W' else 0x6287)
  else:
   assert op in ('G','A');x,y,value,attr=map(int,w[1:5]);raw=bytes.fromhex(w[5]) if w[5]!='-' else b''
   assert 0<=x<80 and 0<=y<25 and 0<=attr<=65535
   if op=='G' and not raw:self.call(0,0x1b0c,(attr,value,y,x),True)
   else:
    assert len(raw)<256 and (op!='A' or all(c<128 for c in raw))
    self.u.mem_write(0x8f000,raw+b'\0')
    self.call(0,0x1b50 if op=='G' else 0x22f6,(attr,0xf000,0x8000,y,x),True)
 def capture(self,tone):
  assert 0<=tone<=200
  tram=bytes(self.u.mem_read(0xa0000,4000))+bytes(self.u.mem_read(0xa2000,4000))
  codes=np.frombuffer(tram[:4000],dtype='<u2');attrs=np.frombuffer(tram[4000:],dtype='<u2')
  base=self.palette.astype(np.int32)>>4
  colors=(base*tone//100 if tone<=100 else 15-(15-base)*(200-tone)//100)*17
  rgb=colors[self.indices].astype(np.uint8);right=False;previous=0;offset=32+int.from_bytes(self.gaiji[28:30],'little')
  for cell,(code,attr) in enumerate(zip(map(int,codes),map(int,attrs))):
   if cell%80==0:right=False
   column=code&127;custom=column in (0x56,0x57)
   if not custom or right and (code&0x7f7f)!=(previous&0x7f7f):right=False
   key=(code,bool(right),attr&5)
   if key not in self.masks:
    rows=bytes(16)
    if attr&1:
     if custom and code&0xff00:
      glyph=((code>>8)&127)+(column-0x56)*128
      rows=bytes(self.gaiji[offset+glyph*32+y*2+int(right)] for y in range(16))
     else:rows=bytes(self.rom(code&127,9+((code>>7)&1),y) for y in range(16))
    pixels=np.unpackbits(np.frombuffer(rows,dtype=np.uint8)).reshape(16,8).astype(bool)
    self.masks[key]=~pixels if attr&4 else pixels
   top,left=cell//80*16,cell%80*8
   rgb[top:top+16,left:left+8][self.masks[key]]=(255 if attr&64 else 0,255 if attr&128 else 0,255 if attr&32 else 0)
   previous=code;right=custom and bool(code&0xff00) and not right
  return self.indices.tobytes()+tram+rgb.tobytes()

def fixtures(scene_reference=None):
 lines=[]
 def add(*v):lines.append(' '.join(map(str,v)))
 for seed in (0,7):
  add('CASE',seed)
  for tone in (0,1,43,50,100,150,200):add('SNAP',tone)
  for op in ('W','B'):
   add(op);add('SNAP',0);add('SNAP',100)
 for attr in (0,1,0xe1,0x85,0x41,0x45,0x81,0xffff):
  add('CASE',attr&15)
  for i in range(256):add('G',i%32*2,2+i//32,i,attr,'-')
  add('G',79,11,0xe6,attr,'-');add('G',5,2,0xc4,attr,'-');add('SNAP',50)
  for y in range(2):add('A',4,13+y,0,attr,bytes(range(1+y*64,min(65+y*64,128))).hex())
  add('A',79,20,0,attr,b' AB\0CD'.hex());add('SNAP',0);add('SNAP',200)
 if scene_reference:
  proof=json.loads((scene_reference/'receipt.json').read_text());assert proof['passed'] and proof['cases']==64 and proof['load_segments']==[4096,8192]
  raw=(scene_reference/'original.txt').read_bytes();assert sha(raw)==proof['trace_sha256']
  assert sha((scene_reference/'fixtures.txt').read_bytes())==proof['fixture_sha256']
  manifest=json.loads((scene_reference.parent/'source-manifest.json').read_text());assert manifest['sha256']==proof['source_manifest']
  root=Path(__file__).resolve().parents[1]
  for name in ('port64/gameover.cpp','port64/gameover.hpp','port64/verify_gameover.py','port64/verify_gameover_scene.py'):
   row=next(v for v in manifest['files'] if v['path']==name);assert sha((root/name).read_bytes())==row['sha256'],'scene dependency changed'
  groups=raw.decode().split('BEGIN\n')[1:];assert len(groups)==64
  for case in (0,1,2,3,8,16,48):
   add('CASE',case%16);tone=100;previous=-1
   for line in groups[case].splitlines():
    w=line.split()
    if w[0]=='END':break
    clock,kind,x,y,value,attr=map(int,w[:6])
    if clock!=previous:
     if previous>=0 and (previous%16==0 or previous in (31,32,36,67,68,94,95,96,100,101)):add('SNAP',tone)
     previous=clock
    if kind in (0,1):add('G' if kind==0 else 'A',x,y,value,attr,w[6])
    elif kind in (2,3):add('W' if kind==2 else 'B')
    elif kind==4:tone=value
   add('SNAP',tone)
 return lines

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','hdi','font-bmp','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--scene-reference',type=Path);p.add_argument('--reference-dir',type=Path);p.add_argument('--runner')
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh Game Over graphics output directory')
 out.mkdir(parents=True);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 assets=main_assets(a.hdi);gaiji=assets['GAMEFT.BFT'];(out/'GAMEFT.BFT').write_bytes(gaiji);(out/'FREECG98.bmp').write_bytes(a.font_bmp.read_bytes())
 lines=fixtures(a.scene_reference);fixture=out/'fixtures.txt';fixture.write_text('\n'.join(lines)+'\n');records=[]
 if a.reference_dir:
  proof=json.loads((a.reference_dir/'receipt.json').read_text());assert proof['passed']
  for key,expected in [('target_sha256',sha(a.target.read_bytes())),('hdi_sha256',sha(a.hdi.read_bytes())),('font_sha256',sha(a.font_bmp.read_bytes())),('fixture_sha256',sha(fixture.read_bytes()))]:assert proof[key]==expected
  trace=a.reference_dir/'original.gz';assert sha(trace.read_bytes())==proof['trace_gzip_sha256'];records=proof['records'];counts=proof['original_controls']
 else:
  trace=out/'original.gz';counts=[]
  for load in (0x1000,0x2000):
   original=Original(a.target.read_bytes(),load,a.font_bmp,gaiji);current=[]
   with gzip.open(trace,'wb',compresslevel=6) if load==0x1000 else gzip.open(trace,'rb') as stream:
    for index,line in enumerate(lines):
     if line.startswith('SNAP'):
      wire=original.capture(int(line.split()[1]));current.append(dict(command_index=index,sha256=sha(wire)))
      if load==0x1000:stream.write(wire)
      else:assert read_exact(stream,SIZE)==wire,'TRAM load metamorphism differs'
      if len(current)%16==0:print(hex(load),len(current),'original snapshots',flush=True)
     else:original.command(line)
    if load==0x2000:assert not stream.read(1),'extra original snapshots'
   counts.append(dict(load=load,calls=original.calls,tram_writes=original.writes))
   if records:assert records==current
   else:records=current
 digest=hashlib.sha256();command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--gameover-render',str(fixture)]
 with (out/'native-stderr.txt').open('wb') as err:
  process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=err,env=dict(os.environ,WINEDEBUG='-all'))
  try:
   with gzip.open(trace,'rb') as wanted,gzip.open(out/'native.gz','wb',compresslevel=6) as got:
    for index,record in enumerate(records):
     x=read_exact(wanted,SIZE);y=read_exact(process.stdout,SIZE)
     if len(x)!=SIZE or x!=y or sha(x)!=record['sha256']:
      at=next((i for i,(q,r) in enumerate(zip(x,y)) if q!=r),min(len(x),len(y)))
      (out/'mismatch.json').write_text(json.dumps(dict(record=index,command_index=record['command_index'],byte=at,original=x[at] if at<len(x) else None,native=y[at] if at<len(y) else None),indent=2)+'\n')
      raise ValueError(f'Game Over render record{index} byte{at} differs')
     digest.update(y);got.write(y)
    assert not wanted.read(1) and not process.stdout.read(1),'extra native snapshots'
   assert process.wait(timeout=120)==0,'native Game Over renderer failed'
  finally:
   if process.poll() is None:process.kill();process.wait()
 assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest,'source changed during graphics control'
 root=a.target.resolve().parents[3];emulator=root/'.analysis/runtime/emulators/dosbox-x-199aa35f'
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,
  target_sha256=sha(a.target.read_bytes()),hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),
  executable_sha256=sha(a.exe.read_bytes()),asset_sha256={'GAMEFT.BFT':sha(gaiji),'FREECG98.bmp':sha(a.font_bmp.read_bytes())},
  fixture_sha256=sha(fixture.read_bytes()),trace_raw_sha256=digest.hexdigest(),trace_gzip_sha256=sha(trace.read_bytes()),native_gzip_sha256=sha((out/'native.gz').read_bytes()),
  snapshots=len(records),compared_bytes=len(records)*SIZE,records=records,original_controls=counts,load_segments=[4096,8192],original_cpu_reexecuted=not bool(a.reference_dir),
  scene_reference_receipt_sha256=sha((a.scene_reference/'receipt.json').read_bytes()) if a.scene_reference else None,
  reference_dir=str(a.reference_dir) if a.reference_dir else None,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
  extents={f'{s:04x}:{lo:04x}..{hi:04x}':sha(a.target.read_bytes()[6144+s*16+lo:6144+s*16+hi]) for s,lo,hi in EXTENTS},
  emulator_source_corroboration={n:sha((emulator/n).read_bytes()) for n in ('src/hardware/vga_draw.cpp','src/hardware/vga.cpp','include/pc98_cg.h')},scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','snapshots','compared_bytes')}))
if __name__=='__main__':main()
