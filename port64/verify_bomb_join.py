#!/usr/bin/env python3
"""Live MAIN Bomb dispatch/palette versus two-load original render instructions.

Actual OP selection, finite STD contact and held X drive normal Bomb, deathbomb
and rejected late deathbomb routes. Original 0AAF:571A executes lifecycle and
actual character/star/RNG/circle instructions. Captured native pre-Bomb state,
ring, physical page, resource handles, sound and graph_scrollup are explicit
adapters. Selected frames execute original BB/fill/CDG/mono hardware kernels;
this validates the joined Bomb layer, not independent complete MAIN rendering,
physical timing, audio, or full-game routes. All launches remain muted.
"""
import argparse,gzip,hashlib,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_player_bomb_pixels import Original,Shadow,stage_assets,read_exact,SCREEN
from verify_player_lifecycle import OFFSETS,RESIDENT,BG
from probe_assets import main_assets
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
LIFE=('inv hit miss respawn radius angle misses used quit bombing frame disabled clear pull scroll bg circle tone changed '
      'p0 p1 p2 b0 b1 b2').split()

class Joined(Original):
 def body(self,u,address,size,unused):
  actual=u.reg_read(UC_X86_REG_CS);pair=(actual+self.delta,address-actual*16)
  if pair==(0x2000,0x1d50):
   sp=u.reg_read(UC_X86_REG_SP)
   self.scrolls.append(struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0])
   ip,cs=struct.unpack('<HH',u.mem_read(0x70000+sp,4))
   u.reg_write(UC_X86_REG_SP,sp+6);u.reg_write(UC_X86_REG_CS,cs);u.reg_write(UC_X86_REG_IP,ip)
  elif pair==(0x2aaf,0x553a) and not self.pixels:
   # Only non-pixel snapshots adapt the already independently tested BB callee.
   sp=u.reg_read(UC_X86_REG_SP);ip=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0]
   u.reg_write(UC_X86_REG_SP,sp+4);u.reg_write(UC_X86_REG_IP,ip)
  else:super().body(u,address,size,unused)
 def seed_join(self,row,assets,pixels):
  self.reset();self.error=None;self.events=[];self.scrolls=[];self.color=0;self.pixels=pixels
  for name,value in zip(LIFE,row['before']):
   if name in OFFSETS:at,fmt=OFFSETS[name];self.write(at,fmt,value)
   elif name in RESIDENT:self.u.mem_write(0x60000+RESIDENT[name],bytes([value]))
   elif name=='bg':self.write(0x426a,'H',BG[value])
  self.write(0xba86,'HH',0,0x6000);self.write(0x426c,'H',BG[1])
  self.write(0x436c,'H',0x555d if not row['character'] else 0x5623)
  self.write(0x538a,'H',row['stage']);self.write(0x538d,'B',row['stage']%4)
  self.write(0x4278,'H',row['line']);self.write(0x3ecc,'H',row['cursor'])
  self.u.mem_write(0x83dcc,row['ring']);self.u.mem_write(0x84370,row['stars']);self.u.mem_write(0x89594,row['circles'])
  stage_assets(self,assets,row['character'])
 def life(self):
  result=[]
  for name in LIFE:
   if name in OFFSETS:at,fmt=OFFSETS[name];value=self.read(at,fmt)[0]
   elif name in RESIDENT:value=self.u.mem_read(0x60000+RESIDENT[name],1)[0]
   else:value=BG.index(self.read(0x426a,'H')[0])
   result.append(value)
  return result

def rows(path):
 result=[]
 for text in path.read_text().splitlines():
  a=text.split();n=len(LIFE)
  assert len(a)==7+n*2+1+5
  result.append(dict(name=a[0],character=int(a[1]),frame=int(a[2]),stage=int(a[3]),line=int(a[4]),
   cursor=int(a[5]),retained=bool(int(a[6])),before=list(map(int,a[7:7+n])),after=list(map(int,a[7+n:7+2*n])),new_cursor=int(a[7+2*n]),
   **{k:bytes.fromhex(v) for k,v in zip(('ring','stars','circles','new_stars','new_circles'),a[8+2*n:])}))
 return result

def palette(assets,life):
 b=assets['ST00.BMT'];at=32+struct.unpack_from('<H',b,28)[0]
 colors=[x for i in range(16) for x in (b[at+i*3+1],b[at+i*3+2],b[at+i*3])]
 colors[0]=colors[1]=255;colors[42:45]=life[19:22];tone=life[17]
 # Preserve the existing native full-redraw RGB convention at neutral100.
 # Original hardware palette nibble expansion remains an explicit adapter.
 if tone!=100:
  colors=[((v>>4)*tone//100 if tone<=100 else 15-(15-(v>>4))*(200-tone)//100)*16 for v in colors]
 return colors

def compare(target,hdi,scenes,stream,out):
 assets=main_assets(hdi);frames=rows(scenes/'frames.txt');snapshots=[]
 for text in (scenes/'snapshots.txt').read_text().splitlines():
  a=text.split();snapshots.append(dict(name=a[0],frame=int(a[1]),line=int(a[2]),page=int(a[3]),palette=list(map(int,a[4:]))))
 lookup={(s['name'],s['frame']):i for i,s in enumerate(snapshots)}
 records=[];first_load=[];digest=hashlib.sha256()
 for load in (0x1000,0x2000):
  o=Joined(target.read_bytes(),load);current=[];image_digest=hashlib.sha256()
  with gzip.open(stream,'rb') as captures:
   for index,row in enumerate(frames):
    selected=(row['name'],row['frame']) in lookup
    o.seed_join(row,assets,selected);shadow=None;data=None;snapshot=None
    if selected:
     before=read_exact(captures,SCREEN);after=read_exact(captures,SCREEN)
     final=read_exact(captures,SCREEN);rgb=read_exact(captures,SCREEN*3)
     assert len(rgb)==SCREEN*3,'short live Bomb capture'
     snapshot=snapshots[lookup[row['name'],row['frame']]]
     shadow=Shadow(o,0);shadow.screen=bytearray(before)
    try:o.call_args(0x571a)
    finally:
     if shadow:shadow.close()
    actual=o.life()
    assert actual==row['after'],f"Bomb state differs {row['name']} frame{row['frame']}: {actual} / {row['after']}"
    assert bytes(o.u.mem_read(0x84370,288))==row['new_stars'],'joined Bomb stars differ'
    assert bytes(o.u.mem_read(0x89594,160))==row['new_circles'],'joined Bomb circles differ'
    assert row['retained']==(49<=row['frame']<=176),'Bomb background owner boundary differs'
    expected_scroll=[0] if row['frame']==48 else [row['line']] if row['frame']==177 else []
    assert o.scrolls==expected_scroll,'Bomb explicit display scroll differs'
    cursor=o.read(0x3ecc,'H')[0]
    assert cursor==row['new_cursor'],'joined Bomb shared RNG cursor differs'
    entry=dict(name=row['name'],frame=row['frame'],life=actual,cursor=cursor,scrolls=o.scrolls,
               stars=sha(row['new_stars']),circles=sha(row['new_circles']))
    if selected:
     if bytes(shadow.screen)!=after:
      at=next(i for i,(x,y) in enumerate(zip(shadow.screen,after)) if x!=y)
      raise ValueError(f"joined Bomb pixels differ {row['name']} frame{row['frame']} at{at%640},{at//640}: {shadow.screen[at]}/{after[at]}")
     expected_palette=palette(assets,actual)
     assert snapshot['palette']==expected_palette,'joined shared palette differs'
     # Final foreground page is a native composition input here. Independently
     # check every displayed RGB byte against its physical indices and palette.
     colors=[bytes((v>>4)*17 for v in expected_palette[i:i+3]) for i in range(0,48,3)]
     expected_rgb=b''.join(colors[final[((y+snapshot['line'])%400)*640+x]] for y in range(400) for x in range(640))
     assert rgb==expected_rgb,'joined full indexed/RGB conversion differs'
     image_digest.update(after);image_digest.update(rgb)
     entry.update(pixels=sha(after),rgb=sha(rgb),ports=shadow.ports,writes=shadow.writes)
    current.append(entry)
    if (index+1)%227==0:print(hex(load),row['name'],'227 original Bomb frames',flush=True)
   assert not captures.read(1),'extra joined Bomb captures'
  if first_load:assert first_load==current and digest.hexdigest()==image_digest.hexdigest(),'Bomb load metamorphism differs'
  else:first_load=current;digest=image_digest
 (out/'original.json').write_text(json.dumps(first_load,indent=2)+'\n')
 return dict(frames=len(frames),scenes=12,screens=len(snapshots),original_sha256=sha((out/'original.json').read_bytes()),
             pixels_rgb_sha256=digest.hexdigest(),original_loads=[4096,8192],assets={n:sha(assets[n]) for n in ('BB0.BB','BB1.BB','BB0.CDG','BB1.CDG','MIKO16.BFT','ST00.BMT')})

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','hdi','exe','font','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path)
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh Bomb join output directory')
 out.mkdir(parents=True);root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)
 scenes=out/'scenes';stream=out/'native.gz'
 command=[str(a.exe.resolve()),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font.resolve()),'--bomb-checks',str(scenes),'--mute']
 with (out/'stderr.txt').open('wb') as err:
  process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=err)
  try:
   with gzip.open(stream,'wb',compresslevel=6) as f:
    while True:
     data=process.stdout.read(1024*1024)
     if not data:break
     f.write(data)
   assert process.wait(timeout=120)==0,'native Bomb frontend rejected: '+(out/'stderr.txt').read_text()
  finally:
   if process.poll() is None:process.kill();process.wait()
 details=compare(a.target,a.hdi,scenes,stream,out)
 if a.reference_dir:
  reference=json.loads((a.reference_dir/'receipt.json').read_text())
  assert reference['passed'] and reference['target']==sha(a.target.read_bytes()) and reference['hdi']==sha(a.hdi.read_bytes())
  for file in ('frames.txt','snapshots.txt','trace.txt','finite.std'):
   assert (scenes/file).read_bytes()==(a.reference_dir/'scenes'/file).read_bytes(),'host Bomb journal differs '+file
  with gzip.open(stream,'rb') as x,gzip.open(a.reference_dir/'native.gz','rb') as y:
   while True:
    b=x.read(1024*1024);c=y.read(1024*1024);assert b==c,'host complete Bomb captures differ'
    if not b:break
  assert (out/'original.json').read_bytes()==(a.reference_dir/'original.json').read_bytes(),'host original Bomb results differ'
 assert source_manifest(root)==manifest,'source changed during Bomb join'
 (out/'source-manifest.json').write_text(json.dumps(dict(sha256=manifest[0],files=manifest[1]),indent=2)+'\n')
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest[0],
  target=sha(a.target.read_bytes()),hdi=sha(a.hdi.read_bytes()),font=sha(a.font.read_bytes()),exe=sha(a.exe.read_bytes()),
  captures_gzip_sha256=sha(stream.read_bytes()),command=command,scope=__doc__,**details)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(details))
if __name__=='__main__':main()
