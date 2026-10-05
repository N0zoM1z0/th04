#!/usr/bin/env python3
"""Original MAINE registration drawing helpers, SUPER, fonts and raw TRAM.

Two load segments execute the actual table/name/rectangle/text-RAM bodies.
Supplied CGROM, GRCG/EGC shadow, BFNT planar staging and preceding PI decode
are explicit adapters. RGB composition is pinned emulator-source corroboration,
not a capture of physical video; scene clocks, sound and host saves are absent.
"""
import argparse,hashlib,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
import unicorn
from unicorn.x86_const import *
from verify_cutscene import Original as Base,ending_assets,PAYLOAD_SHA
from verify_verdict_pixels import FontOriginal,VerdictRaster
from verify_reimu_pixels import planes
from verify_maine_join import return_to_caller
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
SIZE=512000+48+8000+768000
class Sprite(Base):
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
  if cs==self.load and 0x275e<=ip<0x2910:return
  if cs==self.cs and ip==0xff00:self.done=True;u.emu_stop();return
  raise ValueError(f'unexpected SUPER instruction {cs-self.load:04x}:{ip:04x}')
 def port(self,u,port,size,value,unused):
  try:
   assert size==1
   if port==0x7c:self.mode=value;self.tile_at=0
   elif port==0x7e:self.tiles[self.tile_at]=value;self.tile_at=(self.tile_at+1)%4
   else:raise ValueError('unexpected SUPER port')
  except Exception as e:self.error=e;u.emu_stop()
 def shadow(self,u,access,address,size,value,unused):
  if not 0xa8000<=address<0xa8000+32000:return
  try:
   assert self.mode&0x80
   enabled=(~self.mode)&15
   for byte in range(size):
    at=address-0xa8000+byte;assert at<32000
    mask=(value>>(byte*8))&255
    for bit in range(8):
     if self.mode&0x40 and not mask&(128>>bit):continue
     color=sum(1<<p for p in range(4) if self.tiles[p]&(128>>bit))
     pos=at*8+bit;self.screen[pos]=(self.screen[pos]&~enabled)|(color&enabled)
   self.writes+=1
  except Exception as e:self.error=e;u.emu_stop()
 def __init__(self,*args):
  super().__init__(*args);self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.shadow)
 def render(self,bft,image,x,y,background):
  self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
  w,h,blob=planes(bft,image);assert (w,h)==(16,16)
  self.write(0xf0c+image*2,'H',0x9000);self.write(0x130c+image*2,'H',0x210)
  self.u.mem_write(0x90000,blob);self.u.mem_write(0xa8000,bytes(32000))
  self.screen=bytearray(background);self.tiles=[0]*4;self.tile_at=0;self.mode=0;self.writes=0
  self.error=None;self.done=False;self.font_mode=False
  for r,v in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(r,v)
  self.u.mem_write(0x7f000,struct.pack('<5H',0xff00,self.cs,image,y,x))
  self.u.emu_start(self.load*16+0x275e,0x10ffff,count=100000)
  if self.error:raise RuntimeError('original SUPER shadow rejected') from self.error
  assert self.done and self.writes and self.u.reg_read(UC_X86_REG_SP)==0xf00a and self.mode==0
  return bytes(self.screen)

class Fonts(FontOriginal):
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
  if self.font_mode and cs==self.load and 0x3760<=ip<0x37f3:return
  super().body(u,address)
 def single(self,glyph,x,y,rom):
  self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
  self.write(0x11c,'H',0xa800);self.u.mem_write(0xa8000,bytes(32000))
  self.font_mode=True;self.font_rows=None;self.font_rom=rom;self.font_row=0;self.font_cell=0;self.font_column=0
  self.font_color=15;self.font_pixels=bytearray(256000);self.error=None;self.done=False
  for r,v in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(r,v)
  self.u.mem_write(0x7f000,struct.pack('<6H',0xff00,self.cs,15,glyph,y,x))
  self.u.emu_start(self.load*16+0x3760,0x10ffff,count=100000);self.font_mode=False
  if self.error:raise RuntimeError('original graph gaiji rejected') from self.error
  assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xf00c
  return bytes(self.font_pixels)

class Drawing(Base):
 def __init__(self,target,decoded,load,font,bft,gaiji,picture):
  super().__init__(target,decoded,load)
  self.fonts=Fonts(target,decoded,load);self.super=Sprite(target,decoded,load)
  self.lookup=VerdictRaster(target,decoded,font,gaiji,picture)
  self.bft=bft;self.gaiji=gaiji;self.picture=picture;self.font_image=Image.open(font).convert('L')
  self.cache={};self.sprite_cache={};self.commands=0;self.rect_reads=0;self.rect_writes=0
  self.u.hook_add(unicorn.UC_HOOK_MEM_READ,self.vram_read)
  self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.vram_write)
 def reset(self,char,place,weight):
  self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
  self.write(0x3f6,'H',0xa000);self.write(0x170c,'HH',0,0xa800)
  self.write(0x4086,'B',place);self.write(0x4088,'B',char);self.write(0x5fc,'H',weight)
  self.u.mem_write(0xa0000,bytes(0x3000));self.pages=np.repeat(self.lookup.picture[None,:,:],2,axis=0).copy()
  self.page=0;self.rect=False;self.ports=[];self.latch=None;self.error=None;self.done=False
 def call(self,ip,args,segment=0xa05,far=False):
  self.error=None;self.done=False;self.font_mode=False
  for r,v in ((UC_X86_REG_CS,self.load+segment),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(r,v)
  stack=(0xff00,self.cs,*args) if far else (0xff00,*args)
  self.u.mem_write(0x7f000,struct.pack('<'+'H'*len(stack),*stack))
  self.u.emu_start((self.load+segment)*16+ip,0x10ffff,count=500000)
  if self.error:raise RuntimeError('original registration drawing rejected') from self.error
  assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xf000+len(stack)*2
  self.commands+=1
 def mask(self,kind,raw,x,y,weight=0,step=16):
  key=(kind,raw,x,y,weight,step)
  if key not in self.cache:
   if kind=='single':result=self.fonts.single(raw[0],x,y,self.lookup.rom)
   else:result=self.fonts.string(kind,raw,x,y,15,weight,step,self.lookup.rom)
   self.cache[key]=np.frombuffer(result,dtype=np.uint8).reshape(400,640)!=0
  return self.cache[key]
 def numeral(self,image,x,y):
  key=(image,x,y)
  if key not in self.sprite_cache:
   zero=self.super.render(self.bft,image,x,y,bytes(256000));pixels=np.frombuffer(zero,dtype=np.uint8).reshape(400,640)
   background=bytes((i*73+5)&15 for i in range(16))*16000
   actual=self.super.render(self.bft,image,x,y,background)
   expected=np.frombuffer(background,dtype=np.uint8).copy().reshape(400,640);expected[pixels!=0]=pixels[pixels!=0]
   assert actual==expected.tobytes(),'SUPER transparency/metamorphic background differs'
   self.sprite_cache[key]=pixels
  pixels=self.sprite_cache[key];self.pages[self.page][pixels!=0]=pixels[pixels!=0]
 def vram_read(self,u,access,address,size,value,unused):
  if not self.rect or not 0xa8000<=address<0xa8000+32000:return
  try:
   assert self.page==1 and size==2;at=(address-0xa8000)*8
   self.latch=(address,self.pages[1].reshape(-1)[at:at+16].copy());self.rect_reads+=1
  except Exception as e:self.error=e;u.emu_stop()
 def vram_write(self,u,access,address,size,value,unused):
  if not self.rect or not 0xa8000<=address<0xa8000+32000:return
  try:
   assert self.page==0 and size==2 and self.latch[0]==address
   at=(address-0xa8000)*8;self.pages[0].reshape(-1)[at:at+16]=self.latch[1];self.latch=None;self.rect_writes+=1
  except Exception as e:self.error=e;u.emu_stop()
 def port(self,u,port,size,value,unused):
  try:
   assert self.rect,'hardware output outside original rectangle'
   if port==0xa6:assert size==1 and value in (0,1);self.page=value
   else:
    assert (port,size,value) in ((0x7c,1,0),(0x6a,1,7),(0x6a,1,5),(0x7c,1,128),(0x6a,1,6),(0x4a0,2,0xfff0),(0x4a2,2,0xff),(0x4a4,2,0x3100),(0x4a8,2,0xffff),(0x4ac,2,0),(0x4ae,2,15))
    self.ports.append((port,size,value))
  except Exception as e:self.error=e;u.emu_stop()
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);rel=cs-self.load;ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  if cs==self.cs and ip==0xff00:self.done=True;u.emu_stop();return
  if rel==0xa05 and (0x24b6<=ip<0x2793 or 0x2b60<=ip<0x2c29):
   if ip==0x2ba3:self.rect=True;self.ports=[]
   return
  if rel==0:
   if ip in (0x1004,0x105b):
    # This mixed hooked/real FAR return after REP STOSW reports an
    # inconsistent CS:IP (negative receipt retains the failure). Guard
    # the actual RETF immediate, then apply only its stack/return ABI. All
    # preceding character/attribute stores still execute original code.
    argc=8 if ip==0x1004 else 10
    assert self.payload[ip:ip+3]==bytes((0xca,argc,0))
    return_to_caller(u,argc);return
   if 0xfc4<=ip<0x105e:return # Actual character + attribute RAM stores.
   if ip==0x85c:
    assert self.rect and self.page==0 and self.latch is None
    assert self.ports==[(0x7c,1,0),(0x6a,1,7),(0x6a,1,5),(0x7c,1,128),(0x6a,1,6),(0x4a0,2,0xfff0),(0x4a2,2,0xff),(0x4a4,2,0x3100),(0x4a8,2,0xffff),(0x4ac,2,0),(0x4ae,2,15)]
    self.rect=False;return_to_caller(u);return
   if ip==0x275e:
    image,y,x=words(3);self.numeral(image,x,y);return_to_caller(u,6);return
   if ip==0x3760:
    color,glyph,y,x=words(4);self.pages[self.page][self.mask('single',bytes([glyph]),x,y)]=color&15;return_to_caller(u,8);return
   if ip==0x36b6:
    color,off,seg,step,y,x=words(6);data=bytes(u.mem_read(seg*16+off,196));assert 0 in data;data=data.split(b'\0',1)[0]
    self.pages[self.page][self.mask('gaiji',data,x,y,step=step)]=color&15;return_to_caller(u,12);return
  raise ValueError(f'unexpected drawing consumer {rel:04x}:{ip:04x}')
 def command(self,line):
  w=line.split();kind=w[0]
  if kind=='CASE':self.reset(*map(int,w[1:]));return
  if kind in ('table','name'):
   section=bytes.fromhex(w[-1]);assert len(section)==196;self.u.mem_write(self.ds*16+0x3fc2,section)
   if kind=='table':self.call(0x2779,(int(w[1]),))
   else:self.call(0x2615,(int(w[3]),int(w[2]),int(w[1])))
  elif kind=='gaiji':x,y,glyph,attr=map(int,w[1:]);self.call(0xfc4,(attr,glyph,y,x),0,True)
  elif kind=='sprite':x,y,image=map(int,w[1:]);self.numeral(image,x,y)
  elif kind=='rect':x,y,width,height=map(int,w[1:]);self.call(0x2ba3,(height,width,y,x))
  elif kind=='clear_text':self.u.mem_write(0xa0000,bytes(0x3000)) # Console clear is an adapter.
  elif kind=='text':
   x,y,color=map(int,w[1:]);message=self.data[0x89e:0x8d0].split(b'\0',1)[0]
   self.pages[self.page][self.mask('text',message,x,y,self.read(0x5fc,'H')[0])]=color
  else:raise ValueError('unexpected render command')
 def capture(self,tone):
  codes=np.frombuffer(bytes(self.u.mem_read(0xa0000,4000)),dtype='<u2');attrs=np.frombuffer(bytes(self.u.mem_read(0xa2000,4000)),dtype='<u2')
  tram=codes.tobytes()+attrs.tobytes();palette=self.picture[8:56]
  colors=(np.frombuffer(palette,dtype=np.uint8).reshape(16,3).astype(np.uint16)>>4)*tone//100*17
  rgb=colors[self.pages[0]].astype(np.uint8)
  # Independent pinned DOSBox-X video policy: fullwidth gaiji's custom-bank
  # right half must match the previous code; attributes belong to each cell.
  base=32+int.from_bytes(self.gaiji[28:30],'little');right=False;previous=0
  for cell,(code,attr) in enumerate(zip(map(int,codes),map(int,attrs))):
   if cell%80==0:right=False
   col=code&127
   if col not in (0x56,0x57):right=False;continue
   if right and (code&0x7f7f)!=(previous&0x7f7f):right=False
   glyph=((code>>8)&127)+(col-0x56)*128
   for y in range(16):
    if not attr&1:mask=0
    elif code&0xff00:mask=self.gaiji[base+glyph*32+y*2+int(right)]
    else:
     # ANK CGROM from supplied FREECG98, independent of native Font mapping.
     mask=self.lookup.lookup.rom(code&127,9+(code>>7),y)
    if attr&4:mask^=255
    for x in range(8):
     if mask&(128>>x):rgb[cell//80*16+y,cell%80*8+x]=(255 if attr&64 else 0,255 if attr&128 else 0,255 if attr&32 else 0)
   previous=code;right=bool(code&0xff00) and not right
  return self.pages.tobytes()+palette+tram+rgb.tobytes()

def section(n):
 b=bytearray(196)
 for p in range(10):
  b[4+p*9:12+p*9]=bytes(1+(n+p*8+i)%255 for i in range(8))
  b[94+p*8:102+p*8]=bytes(0xa0+(n+p+i)%10 for i in range(8))
  b[101+p*8]=0xa0+(10+n+p)%20;b[176+p]=(n+p*25)%256
 return b

def fixtures(menu_reference=None):
 lines=[]
 def add(*a):lines.append(' '.join(map(str,a)))
 for char in range(2):
  for place in (*range(10),255):
   add('CASE',char,place,0);add('table',1-char,section(5).hex());add('table',char,section(17).hex());add('SNAP',100)
   if place!=255:
    b=section(17);b[4+place*9]=0xc4;add('name',place,char,0,b.hex())
    b[11+place*9]=2;add('name',place,char,7,b.hex());add('SNAP',43)
    add('clear_text');add('SNAP',0)
 for attr in (0xe1,0x85,0x41,0x45):
  for first in (0,128):
   add('CASE',0,255,0)
   for i in range(128):add('gaiji',(i%32)*2,3+i//32,first+i,attr)
   # Pair-spill and independently replaced/overlapping half-cell codes.
   add('gaiji',79,10,0xe6,attr);add('gaiji',5,3,0xc4,attr);add('SNAP',0)
 for shift in range(8):
  add('CASE',0,255,0)
  for pattern in range(20):add('sprite',96+shift+pattern%10*32,20+pattern//10*32,pattern)
  add('SNAP',100)
 for weight in range(4):
  add('CASE',1,255,weight);add('text',124,196,9);add('text',120,192,2);add('SNAP',100)
 for shift in range(8):
  add('CASE',0,255,0);add('table',0,section(1).hex());add('rect',16+shift,98,129,16);add('SNAP',100)
 # Original full menu requests supply natural sections, eight-letter edits,
 # keyboard wrap/repeat, Escape and non-Turbo paths. No host cipher creates them.
 if menu_reference:
  proof=json.loads((menu_reference/'receipt.json').read_text());assert proof['passed'] and proof['cases']==382 and proof['load_segments']==[4096,8192]
  raw=(menu_reference/'original.txt').read_bytes();assert sha(raw)==proof['original_sha256']
  vectors=(menu_reference/'fixtures.txt').read_bytes();assert sha(vectors)==proof['fixtures_sha256']
  groups=raw.decode().split('CASE ')[1:];assert len(groups)==382
  for index in (0,4,8,44,80,88,239,316,371,372,373,374,378,379,380,381):
   trace=groups[index].splitlines()[1:];end=trace[-1].split();add('CASE',int(end[2]),int(end[3]),0)
   captured=False;names=0
   for line in trace:
    w=line.split();kind=w[0]
    if kind=='table':add('table',w[1],w[5])
    elif kind=='name':
     add('name',*w[1:4],w[5]);names+=1
     if names<=8:add('SNAP',100)
    elif kind=='gaiji':add('gaiji',*w[1:5])
    elif kind=='text':add('text',*w[1:4])
    elif kind=='FRAME' and not captured:add('SNAP',100);captured=True
    elif kind=='clear_text':add('SNAP',100);add('clear_text');add('SNAP',0)
 # A zero stage glyph is legal for putc, despite being a string terminator.
 add('CASE',0,255,0);add('table',0,section(0).hex());add('SNAP',100)
 return lines

def run(exe,runner,fixture,assets,font,message,out):
 env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
 subprocess.run(([runner] if runner else [])+[str(exe.resolve()),'--render',str(fixture),str(assets/'HI01.PI'),str(assets/'SCNUM2.BFT'),str(assets/'GAMEFT.BFT'),str(font.resolve()),message,str(out)],check=True,env=env)

def compare(expected,actual,records,out):
 with expected.open('rb') as want,actual.open('rb') as got:
  for index,r in enumerate(records):
   a=want.read(SIZE);b=got.read(SIZE)
   if a!=b:
    pos=next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)))
    report=dict(snapshot=index,record=r,first_byte=pos,expected=a[pos] if pos<len(a) else None,actual=b[pos] if pos<len(b) else None)
    (out/'mismatch.json').write_text(json.dumps(report,indent=2)+'\n');raise ValueError(f'registration snapshot{index} byte{pos} differs')
  assert not want.read(1) and not got.read(1)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','hdi','font-bmp','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--menu-reference',type=Path);p.add_argument('--baseline-exe',type=Path);p.add_argument('--runner');p.add_argument('--reference-dir',type=Path)
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh output directory; completed captures can share storage')
 out.mkdir(parents=True)
 manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
 assets=ending_assets(a.hdi);private=out/'assets';private.mkdir(exist_ok=True)
 for name in ('HI01.PI','SCNUM2.BFT','GAMEFT.BFT'):(private/name).write_bytes(assets[name])
 base=Base(a.target,a.decoded_dir);message=base.data[0x89e:0x8d0].split(b'\0',1)[0].hex()
 if a.reference_dir:
  ref=a.reference_dir.resolve();proof=json.loads((ref/'receipt.json').read_text());assert proof['passed']
  for name,key in [('fixtures.txt','fixture_sha256'),('original.bin','original_sha256'),('HI01.raw','pi_raw_sha256')]:assert sha((ref/name).read_bytes())==proof[key]
  assert proof['payload_sha256']==PAYLOAD_SHA and proof['font_sha256']==sha(a.font_bmp.read_bytes())
  assert proof['assets']=={n:sha(assets[n]) for n in ('HI01.PI','SCNUM2.BFT','GAMEFT.BFT')} and proof['message_hex']==message
  lines=(ref/'fixtures.txt').read_text().splitlines();records=proof['snapshots'];original=ref/'original.bin';picture=(ref/'HI01.raw').read_bytes()
 else:
  assert a.baseline_exe,'preceding PI decoder executable required'
  subprocess.run([str(a.baseline_exe.resolve()),'--decode',str(private/'HI01.PI'),str(out/'HI01.raw')],check=True)
  picture=(out/'HI01.raw').read_bytes();assert len(picture)==128056 and struct.unpack_from('<II',picture)==(640,400)
  lines=fixtures(a.menu_reference);drawings=[Drawing(a.target,a.decoded_dir,load,a.font_bmp,assets['SCNUM2.BFT'],assets['GAMEFT.BFT'],picture) for load in (0x1000,0x2000)]
  records=[];original=out/'original.bin'
  with original.open('wb') as f:
   for index,line in enumerate(lines):
    if line.startswith('SNAP'):
     tone=int(line.split()[1]);snapshots=[d.capture(tone) for d in drawings];assert snapshots[0]==snapshots[1],'drawing load metamorphism differs'
     f.write(snapshots[0]);records.append(dict(command_index=index,tone=tone,sha256=sha(snapshots[0])))
     print(f'Original snapshot {len(records)} PASS',flush=True)
    else:
     for d in drawings:d.command(line)
  proof=dict(original_calls=[d.commands for d in drawings],original_sprite_sites=[len(d.sprite_cache) for d in drawings],original_font_sites=[len(d.cache) for d in drawings],rectangle_reads=[d.rect_reads for d in drawings],rectangle_writes=[d.rect_writes for d in drawings])
 fixture=out/'fixtures.txt';fixture.write_text('\n'.join(lines)+'\n');(out/'HI01.raw').write_bytes(picture)
 native=out/'native.bin';run(a.exe,a.runner,fixture,private,a.font_bmp,message,native);compare(original,native,records,out)
 assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
 source_root=a.target.resolve().parents[3]
 compositor=source_root/'.analysis/runtime/emulators/dosbox-x-199aa35f'
 corroboration={p:sha((compositor/p).read_bytes()) for p in ('src/hardware/vga_draw.cpp','src/hardware/vga.cpp','include/pc98_cg.h')}
 extents={f'{segment:04x}:{start:04x}..{end:04x}':sha(base.payload[segment*16+start:segment*16+end]) for segment,start,end in ((0xa05,0x24b6,0x2793),(0xa05,0x2b60,0x2c29),(0,0xfc4,0x105e),(0,0x275e,0x2910),(0,0x36b6,0x37f3))}
 receipt=dict(passed=True,emulator_source_corroboration=corroboration,extents=extents,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,payload_sha256=PAYLOAD_SHA,target_sha256=sha(a.target.read_bytes()),hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),assets={n:sha(assets[n]) for n in ('HI01.PI','SCNUM2.BFT','GAMEFT.BFT')},exe_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),original_sha256=sha(original.read_bytes()),native_sha256=sha(native.read_bytes()),pi_raw_sha256=sha(picture),snapshots=records,load_segments=[4096,8192],original_controls=proof.get('original_controls',proof),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),message_hex=message,limits='Graphics consumer only. GRCG/EGC/CGROM and BFNT staging are adapters; PI uses preceding decoder regression; raw TRAM uses original stores; RGB composition is pinned emulator-source corroboration. Console clear is an adapter. Text-RAM RETF immediates use guarded ABI returns after original stores (mixed Unicorn FAR return negative retained). No scene fade/wait clock, sound, host persistence, GUI integration, physical video or DOS exactness claim.')
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,snapshots=len(records),compared_bytes=len(records)*SIZE)))
if __name__=='__main__':main()
