#!/usr/bin/env python3
"""Independent original OP font/SUPER kernels consume original ranking traces.

OP0000:2D5A..2F0B and3D8A..3EC4 execute at two relocated loads. BFNT
planar staging, supplied GAMEFT CGROM, GRCG write shadow, preceding PI decode
and scalar palette composition are explicit adapters. Complete pages/palette/
RGB are compared at EVERY refresh of six caller fixtures. No physical PC-98
video/timing/audio, whole OP loop or complete-game claim follows.
"""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import unicorn
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD
from verify_op_ranking import fixture,hextext
from verify_cutscene import Original as FontAdapter,ending_assets
from verify_registration_render import Sprite as GrcgAdapter
from verify_reimu_pixels import planes
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
SIZE=512000+48+768000
class Fonts(Base):
 def __init__(self,*args):
  super().__init__(*args);self.u.hook_add(unicorn.UC_HOOK_INSN,self.input_port,None,1,0,UC_X86_INS_IN);self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.font_write)
 port=FontAdapter.port
 input_port=FontAdapter.input_port
 font_write=FontAdapter.font_write
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
  if cs==self.load and 0x3d8a<=ip<0x3ec5:return
  if cs==self.cs and ip==0xff00:self.done=True;u.emu_stop();return
  raise ValueError('unexpected OP font instruction')
 def render(self,raw,x,y,single=False):
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data);self.write(0x570,'H',0xa800)
  u.mem_write(self.ds*16+0x6000,raw+b'\0');u.mem_write(0xa8000,bytes(32000))
  self.font_mode=True;self.font_rom=self.rom;self.font_color=15;self.font_pixels=bytearray(256000)
  self.font_cell=0;self.font_column=0;self.font_row=0;self.error=None;self.done=False
  args=(15,raw[0],y,x) if single else (15,0x6000,self.ds,16,y,x)
  stack=(0xff00,self.cs,*args)
  for r,v in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(r,v)
  u.mem_write(0x7f000,struct.pack('<'+'H'*len(stack),*stack));u.emu_start(self.load*16+(0x3e34 if single else 0x3d8a),0x10ffff,count=300000)
  if self.error:raise RuntimeError('OP font kernel rejected') from self.error
  assert self.done and u.reg_read(UC_X86_REG_SP)==0xf000+len(stack)*2
  return bytes(self.font_pixels)
 def rom(self,cell,column,selector):
  assert column in (0x56,0x57);glyph=cell+(column-0x56)*128
  at=32+int.from_bytes(self.gaiji[28:30],'little')+glyph*32+(selector&15)*2
  return self.gaiji[at+(0 if selector&0x20 else 1)]
class Sprites(Base):
 def __init__(self,*args):super().__init__(*args);self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.shadow)
 port=GrcgAdapter.port
 shadow=GrcgAdapter.shadow
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
  if cs==self.load and 0x2d5a<=ip<0x2f0c:return
  if cs==self.cs and ip==0xff00:self.done=True;u.emu_stop();return
  raise ValueError('unexpected OP SUPER instruction')
 def render(self,blob,image,x,y,background):
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data);w,h,pattern=planes(blob,image)
  assert h==16 and w in (16,64);self.write(0x1ad8+image*2,'H',0x9000);self.write(0x1ed8+image*2,'H',(w//8<<8)|h)
  u.mem_write(0x90000,pattern);u.mem_write(0xa8000,bytes(32000));self.screen=bytearray(background)
  self.mode=0;self.tile_at=0;self.tiles=[0]*4;self.writes=0;self.error=None;self.done=False
  for r,v in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(r,v)
  u.mem_write(0x7f000,struct.pack('<5H',0xff00,self.cs,image,y,x));u.emu_start(self.load*16+0x2d5a,0x10ffff,count=300000)
  if self.error:raise RuntimeError('OP SUPER kernel rejected') from self.error
  assert self.done and self.writes and self.mode==0 and u.reg_read(UC_X86_REG_SP)==0xf00a
  return bytes(self.screen)
class Raster:
 def __init__(self,target,decoded,assets,pictures):
  self.fonts=[Fonts(target,decoded,load) for load in (0x1000,0x2000)]
  for f in self.fonts:f.gaiji=assets['GAMEFT.BFT']
  self.sprites=[Sprites(target,decoded,load) for load in (0x1000,0x2000)]
  self.assets=assets;self.pictures=pictures;self.font_cache={};self.sprite_cache={};self.kernel_calls=0
 def reset(self):
  self.pages=np.empty((2,400,640),dtype=np.uint8);self.pages[0].fill(1);self.pages[1].fill(2)
  self.access=0;self.tone=100;self.palette=self.pictures['OP1.PI'][0];self.loaded=None
 def apply(self,line):
  w=line.split();kind=w[0];tick,a,b,c,d=map(int,w[1:6]);raw=bytes.fromhex(w[6]) if w[6]!='-' else b''
  if kind=='access':self.access=a
  elif kind=='tone':self.tone=a
  elif kind=='fade':self.tone=100 if a else 0
  elif kind=='load':assert self.loaded is None;self.loaded=raw.decode().upper()
  elif kind=='free':assert self.loaded;self.loaded=None
  elif kind=='palette':assert self.loaded;self.palette=self.pictures[self.loaded][0]
  elif kind=='picture':assert self.loaded;self.pages[self.access]=self.pictures[self.loaded][1]
  elif kind=='copy':self.access=a;self.pages[a]=self.pages[1-a]
  elif kind in ('name','gaiji'):
   if kind=='gaiji':raw=bytes([c]);color=d
   else:color=d
   key=(kind,raw,a,b)
   if key not in self.font_cache:
    masks=[f.render(raw,a,b,kind=='gaiji') for f in self.fonts];assert masks[0]==masks[1]
    self.font_cache[key]=np.frombuffer(masks[0],dtype=np.uint8).reshape(400,640)!=0;self.kernel_calls+=2
   self.pages[self.access][self.font_cache[key]]=color&15
  elif kind=='sprite':
   assert 0<=c<20;blob=self.assets['SCNUM.BFT' if c<10 else 'HI_M.BFT'];image=c if c<10 else c-10;key=(c,a,b)
   if key not in self.sprite_cache:
    zero=[s.render(blob,image,a,b,bytes(256000)) for s in self.sprites];assert zero[0]==zero[1]
    pixels=np.frombuffer(zero[0],dtype=np.uint8).reshape(400,640)
    bg=np.arange(256000,dtype=np.uint8).reshape(400,640)&15;expected=bg.copy();expected[pixels!=0]=pixels[pixels!=0]
    for s in self.sprites:assert s.render(blob,image,a,b,bg.tobytes())==expected.tobytes()
    self.sprite_cache[key]=pixels.copy();self.kernel_calls+=4
   pixels=self.sprite_cache[key];self.pages[self.access][pixels!=0]=pixels[pixels!=0]
 def bytes(self):
  palette=(np.frombuffer(self.palette,dtype=np.uint8).reshape(16,3).astype(np.uint16)>>4)*self.tone//100*17
  return self.pages.tobytes()+self.palette+palette.astype(np.uint8)[self.pages[0]].tobytes()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','exe','hdi','font-bmp','reference-dir','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
 assets=ending_assets(a.hdi);private=out/'assets';private.mkdir();pictures={}
 for name in ('HI01.PI','OP1.PI','SCNUM.BFT','HI_M.BFT','GAMEFT.BFT'):(private/name).write_bytes(assets[name])
 decoder=a.exe.parent/'th04-port64-cutscene-contracts'
 for name in ('HI01.PI','OP1.PI'):
  path=private/(name+'.decoded');subprocess.run([str(decoder.resolve()),'--decode',str(private/name),str(path)],check=True)
  body=path.read_bytes();assert struct.unpack_from('<II',body)==(640,400) and len(body)==128056
  packed=np.frombuffer(body[56:],dtype=np.uint8).reshape(400,320);pixels=np.empty((400,640),dtype=np.uint8);pixels[:,::2]=packed>>4;pixels[:,1::2]=packed&15
  pictures[name]=(body[8:56],pixels)
 lines=(a.reference_dir/'fixtures.txt').read_text().splitlines();selected=[0,12,24,36,48,5];fixtures_path=out/'fixtures.txt';fixtures_path.write_text('\n'.join(lines[i] for i in selected)+'\n')
 native=out/'native.bin';r=subprocess.run([str(a.exe.resolve()),'--pixels',str(fixtures_path),str(private),str(a.font_bmp.resolve()),str(native)],capture_output=True,timeout=180)
 (out/'native.txt').write_bytes(r.stdout);(out/'stderr.txt').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode()
 trace=(a.reference_dir/'original-1000.txt').read_text().splitlines();cases=[]
 for line in trace:
  if line.startswith('CASE '):cases.append([])
  else:cases[-1].append(line)
 raster=Raster(a.target,a.decoded_dir,assets,pictures);expected_hash=hashlib.sha256();snapshots=0;records=[]
 with native.open('rb') as f:
  for index in selected:
   raster.reset();lines=cases[index];last=int(lines[-1].split()[1]);cursor=0
   for tick in range(last+1):
    while cursor<len(lines)-1 and int(lines[cursor].split()[1])==tick:raster.apply(lines[cursor]);cursor+=1
    expected=raster.bytes();actual=f.read(SIZE)
    if actual!=expected:
     at=next((i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y),min(len(actual),len(expected)))
     (out/'mismatch.json').write_text(json.dumps(dict(case=index,tick=tick,stream_snapshot=snapshots,offset=at,actual=actual[at:at+16].hex(),expected=expected[at:at+16].hex()),indent=2)+'\n');raise ValueError('OP ranking complete display differs')
    expected_hash.update(expected);snapshots+=1
   assert cursor==len(lines)-1;records.append(dict(case=index,snapshots=last+1))
  assert not f.read(1)
 assert source_manifest(root)[0]==manifest
 receipt=dict(passed=True,source_manifest=manifest,cases=records,snapshots=snapshots,snapshot_size=SIZE,compared_bytes=snapshots*SIZE,original_kernel_calls=raster.kernel_calls,
  loads=['1000','2000'],packed_sha256=PACKED,payload_sha256=PAYLOAD,assets={n:sha(assets[n]) for n in ('HI01.PI','OP1.PI','SCNUM.BFT','HI_M.BFT','GAMEFT.BFT')},
  hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),trace_sha256=sha(r.stdout),display_sha256=expected_hash.hexdigest(),exe_sha256=sha(a.exe.read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('OP ranking original font/SUPER complete displays PASS',snapshots)
if __name__=='__main__':main()
