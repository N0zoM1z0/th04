#!/usr/bin/env python3
"""Original OP convex DDA/font kernels and complete Music Room displays.

0000:0DC2..0FD9,1D76..1DAA,3264..3335 and0DA1:04A4..05FD execute
at loads1000/2000. Full-screen clipping/GRCG, supplied CGROM, preceding PI
decode, saved planes/pages and scalar palette composition are explicit adapters.
No physical hardware/timing/audio, complete OP or full-game claim follows.
"""
import argparse,gzip,hashlib,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image
import unicorn
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD
from verify_cutscene import Original as FontAdapter,ending_assets
from verify_registration_render import Sprite as GrcgAdapter
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
SIZE=512000+48+768000
class Polygon(Base):
 def __init__(self,*args):super().__init__(*args);self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.shadow)
 port=GrcgAdapter.port
 shadow=GrcgAdapter.shadow
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
  if cs==self.load and (0xdc2<=ip<0xfda or 0x1d76<=ip<0x1dab or 0x3264<=ip<0x3336):return
  if cs==self.cs and ip==0xff00:self.done=True;u.emu_stop();return
  raise ValueError(f'unexpected polygon instruction {cs-self.load:04x}:{ip:04x}')
 def render(self,raw,n,background):
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data)
  self.write(0x50e,'6h',0,639,639,0,0,399);self.write(0x51a,'HH',0xa800,399*80);self.write(0x898,'H',0xffff)
  u.mem_write(self.ds*16+0x6000,raw);u.mem_write(0xa8000,bytes(32000));self.screen=bytearray(background)
  self.mode=0xce;self.tiles=[255]*4;self.tile_at=0;self.writes=0;self.error=None;self.done=False
  for r,v in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(r,v)
  u.mem_write(0x7f000,struct.pack('<5H',0xff00,self.cs,n,0x6000,self.ds));u.emu_start(self.load*16+0xdc2,0x10ffff,count=500000)
  if self.error:raise RuntimeError('OP polygon kernel rejected') from self.error
  assert self.done and u.reg_read(UC_X86_REG_SP)==0xf00a
  return bytes(self.screen)
class Fonts(Base):
 def __init__(self,*args):
  super().__init__(*args);self.u.hook_add(unicorn.UC_HOOK_INSN,self.input_port,None,1,0,UC_X86_INS_IN);self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.font_write)
 port=FontAdapter.port
 input_port=FontAdapter.input_port
 font_write=FontAdapter.font_write
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
  if cs==self.load+0xda1 and 0x4a4<=ip<0x5fe:return
  if cs==self.cs and ip==0xff00:self.done=True;u.emu_stop();return
  raise ValueError(f'unexpected OP font instruction {cs-self.load:04x}:{ip:04x}')
 def render(self,raw,x,y,effect):
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data);self.write(0x570,'H',0xa800);self.write(0xa3c,'HH',effect,16)
  u.mem_write(self.ds*16+0x6000,raw+b'\0');u.mem_write(0xa8000,bytes(32000))
  self.font_mode=True;self.font_rom=self.rom;self.font_color=15;self.font_pixels=bytearray(256000)
  self.font_cell=0;self.font_column=0;self.font_row=0;self.error=None;self.done=False
  for r,v in ((UC_X86_REG_CS,self.load+0xda1),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(r,v)
  u.mem_write(0x7f000,struct.pack('<7H',0xff00,self.cs,0x6000,self.ds,15,y,x));u.emu_start((self.load+0xda1)*16+0x4a4,0x10ffff,count=300000)
  if self.error:raise RuntimeError('OP Music font kernel rejected') from self.error
  assert self.done and u.reg_read(UC_X86_REG_SP)==0xf00e
  return bytes(self.font_pixels)
 def rom(self,cell,column,selector):
  if column in (0x56,0x57):
   glyph=cell+(column-0x56)*128;at=32+int.from_bytes(self.gaiji[28:30],'little')+glyph*32+(selector&15)*2
   return self.gaiji[at+(0 if selector&0x20 else 1)]
  # FREECG98's cell layout is independently supplied, as in prior MAINE fonts.
  if column in (9,10):x=(cell+(128 if column==10 else 0))*8;y=selector&15
  else:x=column*16+(0 if selector&0x20 else 8);y=cell*16+(selector&15)
  return sum((128>>bit) if self.font.getpixel((x+bit,y))==0 else 0 for bit in range(8))
class Raster:
 def __init__(self,target,decoded,assets,pictures,font):
  self.fonts=[Fonts(target,decoded,load) for load in (0x1000,0x2000)]
  for f in self.fonts:f.gaiji=assets['GAMEFT.BFT'];f.font=Image.open(font).convert('L')
  self.polygons=[Polygon(target,decoded,load) for load in (0x1000,0x2000)];self.pictures=pictures;self.font_cache={};self.polygon_cache={};self.calls=0
 def reset(self):
  self.pages=np.empty((2,400,640),dtype=np.uint8);self.pages[0].fill(1);self.pages[1].fill(2)
  self.access=0;self.shown=0;self.tone=0;self.palette=bytes(48);self.loaded=None;self.blue=None;self.background=None
 def apply(self,line):
  w=line.split();kind=w[0];tick,a,b,c,d=map(int,w[1:6]);raw=bytes.fromhex(w[6]) if w[6]!='-' else b''
  if kind=='access':self.access=a
  elif kind=='show':self.shown=a
  elif kind=='tone':self.tone=a
  elif kind=='clear':self.pages[self.access].fill(0)
  elif kind=='load':assert self.loaded is None;self.loaded=raw.decode().upper()
  elif kind=='free':assert self.loaded;self.loaded=None
  elif kind=='palette':assert self.loaded;self.palette=self.pictures[self.loaded][0]
  elif kind=='picture':assert self.loaded;self.pages[self.access]=self.pictures[self.loaded][1]
  elif kind=='copy':self.access=a;self.pages[a]=self.pages[1-a]
  elif kind=='blue_snap':self.blue=self.pages[self.access]&1
  elif kind=='blue_restore':assert self.blue is not None;self.pages[self.access]=(self.pages[self.access]&14)|self.blue
  elif kind=='blue_free':self.blue=None
  elif kind=='background_snap':self.background=self.pages[self.access].copy()
  elif kind=='background_rect':assert self.background is not None;self.pages[self.access,b:b+d,a:a+c]=self.background[b:b+d,a:a+c]
  elif kind=='background_free':self.background=None
  elif kind=='text':
   key=(raw,a,b,d)
   if key not in self.font_cache:
    masks=[f.render(raw,a,b,d) for f in self.fonts];assert masks[0]==masks[1];self.calls+=2
    self.font_cache[key]=np.frombuffer(masks[0],dtype=np.uint8).reshape(400,640)!=0
   self.pages[self.access][self.font_cache[key]]=c&15
  elif kind=='polygon':
   if raw not in self.polygon_cache:
    masks=[p.render(raw,a,bytes(256000)) for p in self.polygons];assert masks[0]==masks[1];self.calls+=2
    self.polygon_cache[raw]=np.frombuffer(masks[0],dtype=np.uint8).reshape(400,640)
   self.pages[self.access]|=self.polygon_cache[raw]
 def bytes(self):
  palette=(np.frombuffer(self.palette,dtype=np.uint8).reshape(16,3).astype(np.uint16)>>4)*self.tone//100*17
  return self.pages.tobytes()+self.palette+palette.astype(np.uint8)[self.pages[self.shown]].tobytes()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','exe','hdi','font-bmp','reference-dir','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--pixel-reference-dir',type=Path);p.add_argument('--geometry',action='store_true');a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
 if a.geometry:
  geometry(a,out,manifest);return
 assets=ending_assets(a.hdi);private=out/'assets';private.mkdir();pictures={}
 for name in ('MUSIC.PI','GAMEFT.BFT'):(private/name).write_bytes(assets[name])
 decoder=a.exe.parent/'th04-port64-cutscene-contracts';path=private/'MUSIC.PI.decoded';subprocess.run([str(decoder.resolve()),'--decode',str(private/'MUSIC.PI'),str(path)],check=True)
 body=path.read_bytes();assert struct.unpack_from('<II',body)==(640,400) and len(body)==128056
 packed=np.frombuffer(body[56:],dtype=np.uint8).reshape(400,320);pixels=np.empty((400,640),dtype=np.uint8);pixels[:,::2]=packed>>4;pixels[:,1::2]=packed&15;pictures['MUSIC.PI']=(body[8:56],pixels)
 selected=[0,1,4,6,24];lines=(a.reference_dir/'fixtures.txt').read_text().splitlines();fixtures=out/'fixtures.txt';fixtures.write_text('\n'.join(lines[i] for i in selected)+'\n')
 native=out/'native.bin';r=subprocess.run([str(a.exe.resolve()),'--pixels',str(fixtures),str(private),str(a.font_bmp.resolve()),str(native)],capture_output=True,timeout=180)
 (out/'native.txt').write_bytes(r.stdout);(out/'stderr.txt').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode()
 if a.pixel_reference_dir:
  previous=json.loads((a.pixel_reference_dir/'receipt.json').read_text());assert previous['passed'] and previous['fixture_sha256']==sha(fixtures.read_bytes())
  expected_path=a.pixel_reference_dir/'native.bin.gz';expected=gzip.open(expected_path,'rb');snapshots=previous['snapshots'];calls=0
  with native.open('rb') as f:
   for i in range(snapshots):assert f.read(SIZE)==expected.read(SIZE),f'current pixel reference mismatch {i}'
   assert not f.read(1) and not expected.read(1)
  expected.close();display_sha=sha(native.read_bytes())
  assert display_sha==previous['display_sha256']
 else:
  trace=(a.reference_dir/'original-1000.txt').read_text().splitlines();cases=[]
  for line in trace:
   if line.startswith('CASE '):cases.append([])
   else:cases[-1].append(line)
  raster=Raster(a.target,a.decoded_dir,assets,pictures,a.font_bmp);digest=hashlib.sha256();snapshots=0
  with native.open('rb') as f:
   for index in selected:
    raster.reset();lines=cases[index];last=int(lines[-1].split()[1]);cursor=0
    for tick in range(last+1):
     while cursor<len(lines)-1 and int(lines[cursor].split()[1])==tick:raster.apply(lines[cursor]);cursor+=1
     expected=raster.bytes();actual=f.read(SIZE)
     if actual!=expected:
      at=next((i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y),min(len(actual),len(expected)))
      (out/'mismatch.json').write_text(json.dumps(dict(case=index,tick=tick,snapshot=snapshots,offset=at,actual=actual[at:at+16].hex(),expected=expected[at:at+16].hex()),indent=2)+'\n');raise ValueError('OP Music complete display differs')
     digest.update(expected);snapshots+=1
    assert cursor==len(lines)-1;print(f'OP Music complete displays case{index} total{snapshots}',flush=True)
   assert not f.read(1)
  display_sha=digest.hexdigest();calls=raster.calls
 compressed=out/'native.bin.gz'
 with native.open('rb') as f,compressed.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=6) as g:
  for chunk in iter(lambda:f.read(1024*1024),b''):g.write(chunk)
 digest=hashlib.sha256()
 with gzip.open(compressed,'rb') as g:
  for chunk in iter(lambda:g.read(1024*1024),b''):digest.update(chunk)
 assert digest.hexdigest()==display_sha;allocated=native.stat().st_blocks*512;native.unlink()
 assert source_manifest(root)[0]==manifest
 receipt=dict(passed=True,source_manifest=manifest,selected=selected,snapshots=snapshots,snapshot_size=SIZE,compared_bytes=snapshots*SIZE,original_kernel_calls=calls,
  original_cpu_reexecuted=not bool(a.pixel_reference_dir),loads=['1000','2000'],packed_sha256=PACKED,payload_sha256=PAYLOAD,
  assets={n:sha(assets[n]) for n in ('MUSIC.PI','_MUSIC.TXT','GAMEFT.BFT')},hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),
  fixture_sha256=sha(fixtures.read_bytes()),trace_sha256=sha(r.stdout),display_sha256=display_sha,exe_sha256=sha(a.exe.read_bytes()),
  reclaimed_allocated_bytes=allocated-compressed.stat().st_blocks*512,utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('OP Music pixels PASS',snapshots)
def geometry(a,out,manifest):
 kernels=[Polygon(a.target,a.decoded_dir,load) for load in (0x1000,0x2000)];shapes=[]
 for line in (a.reference_dir/'original-1000.txt').read_text().splitlines():
  if line.startswith('polygon '):
   w=line.split();n=int(w[2]);raw=bytes.fromhex(w[6]);points=list(struct.iter_unpack('<hh',raw))[:-1]
   if points not in shapes:shapes.append(points)
   if len(shapes)==160:break
 shapes += [[(10,10),(50,10),(30,40)],[(30,40),(10,10),(50,10)],[(10,10),(30,40),(50,10)],
  [(-40,-30),(80,-30),(80,40),(-40,40)],[(600,390),(680,390),(680,460),(600,460)],
  [(-120,80),(-40,80),(-40,160),(-120,160)],[(80,-80),(160,-80),(120,-10)],
  [(10,0),(80,0),(60,40),(30,40)],[(30,40),(10,0),(80,0),(60,40)],
  [(-20,-10),(40,20),(-20,50)],[(400,-30),(420,0),(460,20),(400,50),(340,20),(380,0)]]
 fixture=out/'geometry.txt';fixture.write_text(''.join(str(len(points))+' '+' '.join(str(v) for p in points for v in p)+'\n' for points in shapes))
 native=out/'native.bin';subprocess.run([str(a.exe.resolve()),'--fill',str(fixture),str(native)],check=True)
 background=bytes(((i*13+i//640)%16)&14 for i in range(256000));digest=hashlib.sha256()
 with native.open('rb') as f:
  for index,points in enumerate(shapes):
   raw=b''.join(struct.pack('<hh',*p) for p in points+[points[0]]);original=[p.render(raw,len(points),background) for p in kernels];assert original[0]==original[1]
   actual=f.read(256000)
   if actual!=original[0]:
    at=next(i for i,(x,y) in enumerate(zip(actual,original[0])) if x!=y)
    (out/'mismatch.json').write_text(json.dumps(dict(case=index,points=points,offset=at,x=at%640,y=at//640,actual=actual[at],expected=original[0][at]),indent=2)+'\n');raise ValueError('OP polygon geometry differs')
   digest.update(actual)
  assert not f.read(1)
 compressed=out/'native.bin.gz'
 with native.open('rb') as f,compressed.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=6) as g:
  for chunk in iter(lambda:f.read(1024*1024),b''):g.write(chunk)
 with gzip.open(compressed,'rb') as f:assert sha(f.read())==digest.hexdigest()
 reclaimed=native.stat().st_blocks*512-compressed.stat().st_blocks*512;native.unlink()
 receipt=dict(passed=True,cases=len(shapes),original_kernel_calls=len(shapes)*2,loads=['1000','2000'],source_manifest=manifest,
  fixture_sha256=sha(fixture.read_bytes()),display_sha256=digest.hexdigest(),exe_sha256=sha(a.exe.read_bytes()),reclaimed_allocated_bytes=reclaimed,
  extents=[dict(segment='0000',start=f'{start:04X}',end=f'{end:04X}',sha256=sha(kernels[0].payload[start:end])) for start,end in ((0xdc2,0xfda),(0x1d76,0x1dab),(0x3264,0x3336))],
  scope='Original convex DDA, half rounding, clipping and B-plane writes with dirty other planes; full-screen clip/GRCG adapters.',utc=datetime.now(timezone.utc).isoformat())
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('OP Music geometry PASS',len(shapes))
if __name__=='__main__':main()
