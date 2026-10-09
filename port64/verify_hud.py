#!/usr/bin/env python3
"""Bounded original MAIN HUD producers and real TRAM stores at two MZ loads.

No HUD/text return adapters: original gaiji_putca/gaiji_putsa/text_putsa execute.
Supplied resident/DS/SS/TRAM and starting fields are explicit context adapters.
This does not accept live MAIN, physical CGROM/video, host timing or DOS bytes.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
import numpy as np
from PIL import Image
from unicorn.x86_const import *
from verify_player_lifecycle import Original as Base
from verify_player_bomb_pixels import read_exact
from verify import source_manifest
from probe_assets import main_assets

sha=lambda b:hashlib.sha256(b).hexdigest()
EXTENTS=((0xaaf,0x43f8,0x44b1),(0xaaf,0x44b1,0x45ed),
         (0xaaf,0x45ed,0x4687),(0xaaf,0x4687,0x4714),(0xaaf,0x4714,0x484c),
         (0xaaf,0x6ba2,0x6bd4),(0x13a9,0x6486,0x64de),(0x13a9,0x9a89,0x9aff),
         (0,0x1b0c,0x1ba6),(0,0x22f6,0x2368))
ENTRY={'L':(0xaaf,0x43f8),'B':(0xaaf,0x44b1),'P':(0xaaf,0x4574),
       'D':(0xaaf,0x458a),'G':(0xaaf,0x45a1),'W':(0xaaf,0x45b5),
       'H':(0xaaf,0x45ed),'V':(0xaaf,0x4687),'I':(0xaaf,0x4714),
       'U':(0x13a9,0x6486),'R':(0x13a9,0x6486)}

class Original(Base):
 def __init__(self,target,load):
  super().__init__(target,load);self.requests=[];self.instructions=0;self.tram_writes=0
  self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.on_write)
 def on_write(self,u,access,address,size,value,unused):
  if 0xa0000<=address<0xa0fa0 or 0xa2000<=address<0xa2fa0:self.tram_writes+=1
 def body(self,u,address,size,unused):
  cs=u.reg_read(UC_X86_REG_CS);rel=cs-self.load;ip=address-cs*16
  if ip==0xf000:u.emu_stop();return
  if not any(rel==seg and lo<=ip<hi for seg,lo,hi in EXTENTS):
   raise ValueError(f'unexpected HUD instruction {rel:04x}:{ip:04x}')
  self.instructions+=1;sp=u.reg_read(UC_X86_REG_SP)
  if rel==0 and ip==0x1b0c:
   attr,value,row,col=struct.unpack('<4H',u.mem_read(0x70000+sp+4,8))
   self.requests.append(f'0 {col} {row} {attr} {value} -')
  if rel==0 and ip in (0x1b50,0x22f6):
   attr,off,seg,row,col=struct.unpack('<5H',u.mem_read(0x70000+sp+4,10));text=bytearray()
   for i in range(256):
    value=u.mem_read(seg*16+off+i,1)[0]
    if not value:break
    text.append(value)
   else:raise ValueError('HUD string lacks bounded terminator')
   self.requests.append(f'{1 if ip==0x1b50 else 2} {col} {row} {attr} 0 '+(text.hex() or '-'))
 def seed(self,v):
  self.reset();self.requests=[];self.error=None
  self.u.mem_write(0x90000,bytes((i*73+29)&255 for i in range(256)))
  self.write(0xba86,'HH',0,0x9000)
  for at,value in ((0xb,v[0]),(0xd,v[1]),(0x12,48+v[2])):self.u.mem_write(0x90000+at,bytes([value]))
  self.resident=bytes(self.u.mem_read(0x90000,256));self.write(0x768,'H',0xa000)
  for at,fmt,value in ((0x4348,'B',v[3]),(0x466b,'B',v[4]),(0xbccc,'H',v[5]),
                       (0xbcbc,'H',v[6]),(0x4664,'B',v[7]),(0x4665,'B',v[8]),(0x1ed0,'h',v[9])):
   self.write(at,fmt,value)
  self.u.mem_write(0x84349,bytes(v[15:23]));self.u.mem_write(0x84351,bytes(v[23:31]))
  self.u.mem_write(0x81ec6,bytes(17+i*19 for i in range(8)));self.u.mem_write(0x81ece,b'\0')
  chars=bytearray(4000);attrs=bytearray(4000)
  for i in range(2000):struct.pack_into('<H',chars,i*2,i*31&127);struct.pack_into('<H',attrs,i*2,(i*37+17)&65535)
  self.u.mem_write(0xa0000,bytes(chars));self.u.mem_write(0xa2000,bytes(attrs))
  self.u.mem_write(0xa0fa0,b'\x6d'*96);self.u.mem_write(0xa2fa0,b'\x73'*96)
 def execute(self,op,v):
  seg,ip=ENTRY[op];cs=self.load+seg;u=self.u
  args=(v[11]&65535,v[10]&65535) if op in ('U','R') else (v[13]&65535,) if op=='H' else (v[14],v[13]&65535,v[12]) if op=='V' else ()
  stack=(0xf000,*args) if op in ('U','R') else (0xf000,cs,*args)
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                    (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):
   u.reg_write(reg,value)
  u.mem_write(0x7e000,struct.pack('<'+'H'*len(stack),*stack))
  u.emu_start(cs*16+ip,cs*16+0xf000,count=200000)
  if self.error:raise RuntimeError('original HUD rejected') from self.error
  assert u.reg_read(UC_X86_REG_CS)==cs and u.reg_read(UC_X86_REG_IP)==0xf000,'original HUD instruction budget exhausted'
  assert u.reg_read(UC_X86_REG_SP)==0xe000+len(stack)*2,'original HUD ABI return differs'
  assert bytes(u.mem_read(0x90000,256))==self.resident,'HUD modified resident'
  assert bytes(u.mem_read(0xa0fa0,96))==b'\x6d'*96 and bytes(u.mem_read(0xa2fa0,96))==b'\x73'*96,'TRAM bounds changed'
  header=[self.read(0x1ed0,'h')[0],*u.mem_read(0x81ec6,8)]
  text='S '+' '.join(map(str,header))+''.join('|'+r for r in self.requests)
  tram=bytes(u.mem_read(0xa0000,4000))+bytes(u.mem_read(0xa2000,4000))
  return text,tram

def fixture(op,**kwargs):
 d=dict(lives=3,bombs=2,character=0,rank=1,points=7,dream=456,graze=789,power=1,shot=0,
        previous=17,current=1,maximum=100,row=22,bar=0,attribute=0xe1)
 d.update(kwargs)
 return op,[*d.values(),*[i for i in range(8)],*[9-i for i in range(8)]]
def fixtures():
 for value in range(256):
  yield fixture('L',lives=value);yield fixture('B',bombs=value);yield fixture('P',points=value)
 for value in (0,1,9,10,99,100,999,1000,9999,10000,6553,6554,32767,32768,65535):
  yield fixture('D',dream=value);yield fixture('G',graze=value)
 for value,shot in itertools.product(range(256),range(10)):yield fixture('W',power=value,shot=shot)
 for value,attr in itertools.product((*range(160),-1,-16,-32752,32767),(0,1,0x41,0xe1,65535)):
  yield fixture('V',bar=value,attribute=attr)
 for value in range(160):yield fixture('H',bar=value)
 for prev,cur,maximum in itertools.product((0,1,31,32,63,64,95,96,127,128),
                    (-32768,-1,0,1,2,31,32,99,100,32767),(-32768,-1,0,1,2,32,100,32767)):
  yield fixture('U',previous=prev,current=cur,maximum=maximum)
 for character,rank,lives,bombs in itertools.product(range(2),range(5),(0,1,3,7,100,129),(0,2,5,6,100,128,255)):
  yield fixture('I',character=character,rank=rank,lives=lives,bombs=bombs,power=(rank+1)*32,shot=rank,previous=128,dream=65535)
 for value in (0,9,95,96,97,255):
  op,v=fixture('I');v[15:31]=[value]*16;yield op,v
 # Subsequent calls retain the original global previous and TRAM; the native
 # producer retains its own previous instead of being reseeded from target.
 for maximum in (100,32767):
  yield fixture('U',previous=0,current=maximum,maximum=maximum)
  for tick in range(140):yield fixture('R',current=maximum,maximum=maximum)
  for current in (maximum//4,1,0,-1,maximum):
   for tick in range(8):yield fixture('R',current=current,maximum=maximum)

def rgb_from_tram(tram,font,gaiji):
 codes=np.frombuffer(tram[:4000],dtype='<u2');attrs=np.frombuffer(tram[4000:],dtype='<u2')
 dots=np.arange(256000,dtype=np.uint32)[:,None]*17+np.arange(3,dtype=np.uint32)[None,:]*73
 rgb=(dots&255).astype(np.uint8).reshape(400,640,3)
 offset=32+int.from_bytes(gaiji[28:30],'little');right=False;previous=0
 for cell,(code,attr) in enumerate(zip(map(int,codes),map(int,attrs))):
  if cell%80==0:right=False
  column=code&127;jis_cell=(code>>8)&127;custom=column in (0x56,0x57)
  standard=not custom and 1<=column<=0x5e and 0x21<=jis_cell<=0x7e
  kanji=custom or standard
  if not kanji or right and (code&0x7f7f)!=(previous&0x7f7f):right=False
  pixels=np.zeros((16,8),dtype=bool)
  if attr&1:
   if custom and code&0xff00:
    glyph=((code>>8)&127)+(column-0x56)*128
    rows=bytes(gaiji[offset+glyph*32+y*2+int(right)] for y in range(16))
    pixels=np.unpackbits(np.frombuffer(rows,dtype=np.uint8)).reshape(16,8).astype(bool)
   elif standard:
    # The independently supplied ROM bitmap is addressed by TRAM row/cell;
    # no portable Shift-JIS inverse conversion is reused here.
    left=column*16+(8 if right else 0);top=jis_cell*16
    pixels=np.asarray(font.crop((left,top,left+8,top+16)))==0
   else:
    left=(code&255)*8;pixels=np.asarray(font.crop((left,0,left+8,16)))==0
  if attr&4:pixels=~pixels
  top,left=cell//80*16,cell%80*8
  rgb[top:top+16,left:left+8][pixels]=(255 if attr&64 else 0,255 if attr&128 else 0,255 if attr&32 else 0)
  previous=code;right=kanji and bool(code&0xff00) and not right
 return rgb.tobytes()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--runner');p.add_argument('--limit',type=int)
 p.add_argument('--hdi',type=Path);p.add_argument('--font-bmp',type=Path)
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh HUD output directory')
 out.mkdir(parents=True);root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0]
 cases=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures())
 lines=[op+' '+' '.join(map(str,v)) for op,v in cases];fixture_path=out/'fixtures.txt';fixture_path.write_text('\n'.join(lines)+'\n')
 expected=[];trace=out/'original-tram.gz';counts=[]
 for load in (0x1000,0x2000):
  original=Original(a.target.read_bytes(),load)
  with gzip.open(trace,'wb',compresslevel=6) if load==0x1000 else gzip.open(trace,'rb') as stream:
   for i,(op,v) in enumerate(cases):
    if op!='R':original.seed(v)
    else:original.requests=[];original.error=None
    text,tram=original.execute(op,v)
    if load==0x1000:expected.append(text);stream.write(tram)
    else:assert expected[i]==text and read_exact(stream,8000)==tram,'HUD relocated-load metamorphism differs'
    if i and i%1000==0:print(hex(load),i,'HUD cases',flush=True)
   if load==0x2000:assert not stream.read(1)
  counts.append(dict(load=load,instructions=original.instructions,tram_writes=original.tram_writes))
 (out/'original.txt').write_text('\n'.join(expected)+'\n')
 command=([a.runner] if a.runner else [])+[str(a.exe.resolve())];env=dict(os.environ,WINEDEBUG='-all')
 actual=subprocess.run(command+['--vectors',str(fixture_path)],check=True,capture_output=True,text=True,env=env)
 (out/'native.txt').write_text(actual.stdout)
 for i,(want,got) in enumerate(itertools.zip_longest(expected,actual.stdout.splitlines())):
  if want!=got:
   (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=lines[i],original=want,native=got),indent=2)+'\n');raise ValueError(f'HUD case{i} differs')
 digest=hashlib.sha256()
 with (out/'native-stderr.txt').open('wb') as err:
  proc=subprocess.Popen(command+['--tram',str(fixture_path)],stdout=subprocess.PIPE,stderr=err,env=env)
  try:
   with gzip.open(trace,'rb') as stream:
    for i in range(len(cases)):
     want=read_exact(stream,8000);got=read_exact(proc.stdout,8000)
     if want!=got:
      at=next(j for j,(x,y) in enumerate(zip(want,got)) if x!=y) if len(got)==8000 else len(got)
      (out/'tram-mismatch.json').write_text(json.dumps(dict(case=i,input=lines[i],byte=at),indent=2)+'\n');raise ValueError(f'HUD TRAM case{i} byte{at} differs')
     digest.update(got)
    assert not stream.read(1) and not proc.stdout.read(1),'extra HUD TRAM output'
   assert proc.wait(timeout=60)==0,'native HUD TRAM failed'
  finally:
   if proc.poll() is None:proc.kill();proc.wait()
 assert source_manifest(root)[0]==manifest,'source changed during HUD control'
 pixels=None
 if a.hdi or a.font_bmp:
  assert a.hdi and a.font_bmp,'HUD pixels require both HDI and font'
  assert sha(a.hdi.read_bytes())=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd','HUD HDI differs'
  assert sha(a.font_bmp.read_bytes())=='41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6','HUD font differs'
  gaiji=main_assets(a.hdi)['GAMEFT.BFT'];font=Image.open(a.font_bmp).convert('L');gaiji_path=out/'GAMEFT.BFT';gaiji_path.write_bytes(gaiji)
  indices=[i for i,(op,v) in enumerate(cases) if op=='I' and (i%11==0 or v[0] in (100,129) and v[1] in (128,255))]
  selected=out/'pixel-fixtures.txt';selected.write_text('\n'.join(lines[i] for i in indices)+'\n')
  pixel_trace=out/'original-rgb.gz';records=[];original=Original(a.target.read_bytes(),0x1000)
  with gzip.open(pixel_trace,'wb',compresslevel=6) as stream:
   for i in indices:
    op,v=cases[i];original.seed(v);text,tram=original.execute(op,v);wire=tram+rgb_from_tram(tram,font,gaiji)
    records.append(dict(case=i,sha256=sha(wire)));stream.write(wire)
  pixel_digest=hashlib.sha256()
  with (out/'native-rgb-stderr.txt').open('wb') as err:
   proc=subprocess.Popen(command+['--rgb',str(selected),str(gaiji_path),str(a.font_bmp.resolve())],stdout=subprocess.PIPE,stderr=err,env=env)
   try:
    with gzip.open(pixel_trace,'rb') as stream:
     for record in records:
      want=read_exact(stream,776000);got=read_exact(proc.stdout,776000)
      assert sha(want)==record['sha256']
      if want!=got:
       at=next(j for j,(x,y) in enumerate(zip(want,got)) if x!=y) if len(got)==776000 else len(got)
       (out/'rgb-mismatch.json').write_text(json.dumps(dict(case=record['case'],byte=at),indent=2)+'\n');raise ValueError('HUD RGB differs')
      pixel_digest.update(got)
     assert not stream.read(1) and not proc.stdout.read(1)
    assert proc.wait(timeout=60)==0,'HUD RGB consumer failed'
   finally:
    if proc.poll() is None:proc.kill();proc.wait()
  pixels=dict(cases=len(records),bytes=len(records)*776000,sha256=pixel_digest.hexdigest(),
              trace_gzip_sha256=sha(pixel_trace.read_bytes()),gaiji_sha256=sha(gaiji),hdi_sha256=sha(a.hdi.read_bytes()),
              font_sha256=sha(a.font_bmp.read_bytes()),records=records,
              limits='Complete original TRAM; native RGB uses explicit supplied CGROM/emulator mask/transparent graphics adapter, not original hardware video or physical pixels.')
 assert source_manifest(root)[0]==manifest,'source changed during HUD pixels'
 target=a.target.read_bytes();module=target[6144:]
 receipt=dict(passed=True,cases=len(cases),counts={op:sum(x==op for x,_ in cases) for op in ENTRY},load_segments=[4096,8192],
   original_controls=counts,target_sha256=sha(target),native_sha256=sha(a.exe.read_bytes()),source_manifest_sha256=manifest,
   fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=sha((out/'original.txt').read_bytes()),tram_gzip_sha256=sha(trace.read_bytes()),
   tram_bytes=len(cases)*8000,tram_sha256=digest.hexdigest(),pixels=pixels,
   extents=[dict(segment=seg,begin=lo,end=hi,sha256=sha(module[seg*16+lo:seg*16+hi])) for seg,lo,hi in EXTENTS],
   unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
   observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
   scope='Complete ordered HUD requests, score HUD bytes, retained HP previous, resident/TRAM canaries and all8000 TRAM bytes. Original callers, count/bar/HP arithmetic and actual gaiji/SJIS stores run at two relocated loads.',
   limits='Explicit DS8000 SS7000 resident9000/TRAM A000 and isolated starting-state adapters. Undefined original table/stack inputs rejected. No complete MAIN join, pixel/CGROM/video/timing/audio, current Windows runtime, pristine provenance or DOS exact claim.')
 (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
