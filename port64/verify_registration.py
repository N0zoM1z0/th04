#!/usr/bin/env python3
"""Complete original registration control flow against the native logical menu.

Real menu, alphabet-cursor helper, score functions and LCG instructions execute.
Graphics/table/name drawing, palette waits, successful file services and sound
are explicitly guarded adapters. This controls menu selection/input/file state;
it does not prove rendered pixels, real fade clocks or host disk persistence.
"""
import argparse,hashlib,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_score_file import Original as Score,HI,text
from verify_maine_join import return_to_caller
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
MENU_SHA='7bef6c89de52462b75acb65a47dd919ce27eb38d5d920c082d73141e54cdad6b'
ALPHABET_SHA='5c20537901ef7a0188aa24a9b037a3b62a51b9ede3a930545c903c483ed095ac'
class Original(Score):
 def __init__(self,target,decoded,load):
  super().__init__(target,decoded,load)
  assert sha(self.payload[0xc814:0xcbb0])==MENU_SHA
  assert sha(self.data[0x82c:0x85f])==ALPHABET_SHA
 def event(self,name,a=0,b=0,c=0,d=0,data=b'',label=''):
  self.events.append(f'{name} {a} {b} {c} {d} {text(data)} {label or "-"}')
 def body(self,u,address):
  segment=u.reg_read(UC_X86_REG_CS)-self.load;ip=address-u.reg_read(UC_X86_REG_CS)*16
  sp=u.reg_read(UC_X86_REG_SP)
  def words(n,far=True):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+(4 if far else 2),n*2))
  def resource(off,seg):
   assert seg==self.ds;raw=bytes(u.mem_read(seg*16+off,80));return raw.split(b'\0',1)[0]
  def finish(n=0,far=True):return_to_caller(u,n,far)
  def section():return bytes(u.mem_read(self.ds*16+HI,196))
  if segment==0xa05:
   if 0x27c4<=ip<0x2b60:
    if ip==0x27d6:self.event('tone',self.read(0x132,'h')[0])
    return
   if 0x2793<=ip<0x27c4:return # Real alphabet cursor helper calls gaiji_putca.
   if ip==0x2779:
    self.event('table',words(1,False)[0],data=section());finish(2,False);return
   if ip==0x2615:
    cursor,char,place=words(3,False);self.event('name',place,char&255,cursor,data=section());finish(6,False);return
  if segment==0:
   if ip==0x19ec:finish();return
   if ip==0x1274:self.event('pi_free',0);finish(8);return
   if ip==0x11c2:self.event('copy',words(1)[0]);finish(2);return
   if ip==0x2684:
    off,seg=words(2);assert resource(off,seg)==b'scnum2.bft';self.event('bfnt',label='SCNUM2.BFT');finish(4);return
   if ip==0xfc4:
    color,glyph,y,x=words(4);self.event('gaiji',x,y,glyph,color);finish(8);return
   if ip in (0x622,0x666):self.event('fade',int(ip==0x622),words(1)[0]);finish(2);return
   if ip==0x2520:self.event('free_sprites');finish();return
   if ip==0x20fa:self.event('clear_text');finish();return
  if segment==0xcc7:
   if ip==0xf5:
    off,seg,slot=words(3);assert resource(off,seg)==b'hi01.pi';self.event('pi_load',slot,label='HI01.PI');finish(6);return
   if ip==0x48:self.event('pi_palette',words(1)[0]);finish(2);return
   if ip==0x6d:
    slot,y,x=words(3);self.event('pi_put',slot,x,y);finish(6);return
   if ip==0x58c:
    off,seg,color,y,x=words(5);assert off in (0x89e,0x8d1)
    assert resource(off,seg)==self.data[0x89e:0x8d0].split(b'\0',1)[0]
    self.event('text',x,y,color,label='non_turbo_shadow' if off==0x89e else 'non_turbo_foreground');finish(10);return
   if ip==0x31c:self.event('sound',words(1)[0]);finish(2);return
   if ip==0x4a2:
    mode,off,seg=words(3);assert mode==0x600 and resource(off,seg)==b'name'
    self.event('song',mode,label='NAME');finish(6);return
   if ip==0x81a:
    sample=self.initial if self.initial_reset else self.keys[self.clock]
    self.initial_reset=False;self.write(0x1b42,'H',sample);finish();return
   if ip==0x822:
    self.write(0x1b42,'H',self.read(0x1b42,'H')[0]|self.keys[self.clock]);finish();return
   if ip==0x33:
    assert words(1)==(1,);bp=u.reg_read(UC_X86_REG_BP)
    # Local WORDs are lock atBP-4 and alphabet row atBP-2.
    lock=struct.unpack('<H',u.mem_read(0x70000+bp-4,2))[0]
    row=struct.unpack('<h',u.mem_read(0x70000+bp-2,2))[0]
    repeat=u.mem_read(0x70000+bp-9,1)[0]
    self.events.append(f'FRAME {self.clock} {u.reg_read(UC_X86_REG_SI)} {u.reg_read(UC_X86_REG_DI)} {row} {lock} {repeat} {section().hex()}')
    self.clock+=1;assert self.clock<len(self.keys),'fixture did not confirm before inputs ended';finish(2);return
   if ip==0x20a:assert words(1)==(0,);self.event('wait',0);finish(2);return
  return super().body(u,address)
 def run_menu(self,case):
  seed,stage,rank,char,shot,turbo,end,present,initial,digits,file,keys=case
  self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
  self.u.mem_write(self.ds*16+HI,bytes(196));self.write(0x170,'I',seed)
  self.u.mem_write(self.ds*16+HI-16,bytes([0x5a])*16)
  resident=bytearray(256);resident[0xf]=rank;resident[0x11]=stage;resident[0x12]=char;resident[0x19]=shot
  resident[0x49]=turbo;resident[0x30]=end;resident[0x1d:0x25]=digits
  self.u.mem_write(0x90000,bytes(resident));self.write(0xe9e,'HH',0,0x9000)
  self.file=bytearray(file);self.present=bool(present);self.position=0;self.open=False;self.draws=0
  self.events=[];self.error=None;self.done=False;self.clock=0;self.keys=keys;self.initial=initial;self.initial_reset=True;self.font_mode=False
  for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_ES,0),
   (UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):
   self.u.reg_write(reg,value)
  self.u.mem_write(0x7f000,struct.pack('<H',0xff00))
  self.u.emu_start(self.cs*16+0x27c4,0x10ffff,count=3000000)
  if self.error:raise RuntimeError('original registration adapter rejected') from self.error
  assert self.done and not self.open and self.u.reg_read(UC_X86_REG_SP)==0xf002
  assert bytes(self.u.mem_read(0x90000,256))==resident
  assert bytes(self.u.mem_read(self.ds*16+HI-16,16))==bytes([0x5a])*16
  selected_rank=4 if stage==6 else rank;selected_char=int(char==ord('1'))
  assert self.read(0x4087,'BB')==(selected_rank,selected_char)
  place=self.read(0x4086,'B')[0];random_state=self.read(0x170,'I')[0]
  self.events.append(f'END {selected_rank} {selected_char} {place} {self.clock} {random_state} {self.draws} {int(self.present)} {bytes(self.u.mem_read(self.ds*16+HI,196)).hex()} {text(self.file)}')
  return self.events

def fixture_line(c):
 seed,stage,rank,char,shot,turbo,end,present,initial,digits,file,keys=c
 return ' '.join(map(str,(seed,stage,rank,char,shot,turbo,end,present,initial)))+' '+digits.hex()+' '+text(file)+' '+','.join(map(str,keys))
def fixtures(original):
 # File creation is executed by the attested original rather than a host cipher.
 generated=original.run((2,1,0,0,0,0,0,bytes(196),b'',bytes(8)))
 file=bytes.fromhex(generated[-1].split()[-1]);keys=[0,0,0x20,0,0,0x1000]
 result=[]
 for char in (48,49,50):
  for rank in range(5):
   for shot in (0,1):
    for turbo in (0,1):
     for end in (0,0xfd,0xfe,0xff):
      digits=bytes([0,0,0,0,0,0,1,0])
      result.append((318,5,rank,char,shot,turbo,end,1,0,digits,file,keys))
 # Missing/bad/short selected sections and all clear-mask branches.
 for rank in range(5):
  for char in (48,49):
   for data,present in ((b'',0),(b'',1),(file[:137],1),(file+bytes([0xab])*31,1)):
    result.append((0xffffffff,6,rank,char,1,0,0xfd,present,0,bytes([0,0,0,0,0,0,1,0]),data,keys))
 # Selected table clear masks are encoded by original instructions, including
 # values that exercise accumulation versus normalization.
 for cleared in (0,1,2,3,4,19,255):
  work=bytearray(196);original.run((2,1,0,0,0,0,0,bytes(work),b'',bytes(8)))
  defaults=bytearray(original.u.mem_read(original.ds*16+HI,196));defaults[174]=cleared
  encoded=original.run((0,318,0,0,0,0,1,bytes(defaults),b'',bytes(8)))[-1].split()[-2]
  modified=bytearray(file);modified[8*196:9*196]=bytes.fromhex(encoded)
  for shot in (0,1):
   for end in (0xfd,0xfe,0xff):
    result.append((1,5,3,49,shot,1,end,1,0,bytes([0,0,0,0,0,0,1,0]),bytes(modified),keys))
 # A Turbo score below the last row still saves and waits without a keyboard.
 for char in (48,49):
  result.append((1,5,1,char,0,1,0xfe,1,0,bytes(8),file,keys))
 # Navigation, commands, simultaneous chords, long holds and inherited input.
 profiles=[]
 for initial in (0,1,0x20,0x1000,0x2000):
  for chord in (1,2,4,8,15,0x20,0x2000,0x30,0x1020):
   profiles.append((initial,[0,0,chord,0,0,0x1000]))
 for chord in (1,2,4,8,0x20,0x2000,0x30):
  profiles.append((0,[0,0]+[chord]*330+[0,0,0x1000]))
 # Type eight glyphs, causing automatic keyboard selection of Enter.
 profiles.append((0,[0,0]+[v for _ in range(8) for v in (0x20,0,0)]+[0x20]))
 profiles.append((0,[0,0]+[8]*20+[4]*40+[0,0,0x1000]))
 # Navigate to space/back/right/Enter commands; keyboard is a 3x17 torus.
 for column in (13,14,15,16):
  move=[0,0,1,0,0]+[v for _ in range(17-column) for v in (4,0,0)]
  profiles.append((0,move+[0x20,0,0,0x1000]))
 for initial,keys in profiles:
  result.append((0x80000000,5,3,49,0,1,0xff,1,initial,bytes([0,0,0,0,0,0,1,0]),file,keys))
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--decoded-dir',type=Path,required=True)
 p.add_argument('--exe',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--runner',choices=('direct','wine'),default='direct')
 p.add_argument('--reference-dir',type=Path);a=p.parse_args();assert not a.output_dir.exists();a.output_dir.mkdir(parents=True)
 owner=Original(a.target,a.decoded_dir,0x1000)
 if a.reference_dir:
  proof=json.loads((a.reference_dir/'receipt.json').read_text());assert proof['passed'] and proof['menu_sha256']==MENU_SHA
  fixture_bytes=(a.reference_dir/'fixtures.txt').read_bytes();expected=(a.reference_dir/'original.txt').read_bytes()
  assert sha(fixture_bytes)==proof['fixtures_sha256'] and sha(expected)==proof['original_sha256'];cases=proof['cases']
 else:
  cases_data=fixtures(owner);cases=len(cases_data);fixture_bytes=('\n'.join(map(fixture_line,cases_data))+'\n').encode()
  original=[];other_owner=Original(a.target,a.decoded_dir,0x2000)
  for i,c in enumerate(cases_data):
   events=owner.run_menu(c);other=other_owner.run_menu(c);assert events==other
   original.extend([f'CASE {i}',*events])
   if (i+1)%32==0:print(f'Original registration controls: {i+1}/{cases}',flush=True)
  expected=('\n'.join(original)+'\n').encode()
 (a.output_dir/'fixtures.txt').write_bytes(fixture_bytes);(a.output_dir/'original.txt').write_bytes(expected)
 cmd=(['wine'] if a.runner=='wine' else [])+[str(a.exe.resolve()),'--trace',str((a.output_dir/'fixtures.txt').resolve())]
 out=subprocess.run(cmd,capture_output=True,check=True).stdout.replace(b'\r\n',b'\n');(a.output_dir/'native.txt').write_bytes(out)
 if out!=expected:
  lhs=expected.decode().splitlines();rhs=out.decode().splitlines()
  for i,(x,y) in enumerate(zip(lhs,rhs)):
   if x!=y:raise AssertionError(f'first mismatch line{i}:\noriginal {x}\nnative   {y}')
  raise AssertionError(f'trace size mismatch {len(lhs)} vs {len(rhs)}')
 mf,files=source_manifest(Path(__file__).resolve().parents[1])
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),cases=cases,load_segments=[4096,8192],menu_sha256=MENU_SHA,alphabet_sha256=ALPHABET_SHA,
  source_manifest=mf,fixtures_sha256=sha(fixture_bytes),original_sha256=sha(expected),native_sha256=sha(out),exe_sha256=sha(a.exe.read_bytes()),command=cmd,
  original_producer=not bool(a.reference_dir),scope='Logical registration menu, original score functions/LCG and input loop; successful file and graphics/sound/fade/wait adapters. No pixels, physical timing, host persistence or complete game save claim.')
 (a.output_dir/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(f'Original/native registration controls PASS: {cases} cases')
if __name__=='__main__':main()
