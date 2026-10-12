#!/usr/bin/env python3
"""Original complete MAINE Cutscene parser/waits against elapsed native Script.

File, graphics, font, palette I/O and keyboard calls are guarded adapters.
Original parser, black/white fades, frame_delay/input_wait and sound wait
instructions execute unchanged with ideal IRQ and explicit measure stimuli.
Escape is projected from the original key_det high-byte bit0x10 to logical
bit0x10. No CPU/I/O latency, physical keyboard/audio or full scanout claim.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_cutscene import Original as Base,ending_assets,signed
from verify_maine_elapsed import edges,edge
from verify_maine_join import return_to_caller
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Original(Base):
 def __init__(self,target,decoded,load,row,script):
  super().__init__(target,decoded,load);self.inc,self.seed,self.now,self.profile,self.mode,self.horizon,_=row;self.end=self.now+self.horizon;self.song=self.now;self.lines=[];self.fade=False;self.in_input=False;self.in_measure=False;self.blocked=False;self.state=2;self.sync_poll=False;self.measure_poll=False
  n=self.seed+edges(self.now);count=n-n*self.inc//65536
  for at,value in ((0xefa,count),(0xefc,count),(0xf02,n*self.inc),(0x400,self.inc)):self.w(at,value)
  self.write(0x402,'B',0xfb);self.write(0x5a1,'B',0 if self.mode==0 else 1)
  self.u.mem_write(self.ds*16+0x1f48,script+bytes(4));self.w(0x3f48,0x1f48);self.u.hook_add(unicorn.UC_HOOK_INTR,self.interrupt)
  assert hashlib.sha256(self.payload[0x222c:0x22ac]).hexdigest()=='dc8440641c0bc68a24377b455ec3d5f9d925370093a1b7d9c601337746b231d0'
 def r(self,at):return self.read(at,'H')[0]
 def w(self,at,value):self.write(at,'H',value&65535)
 def advance(self,now):
  n=edges(now)-edges(self.now);total=self.r(0xf02)+n*self.inc;count=n-total//65536
  self.w(0xefa,self.r(0xefa)+count);self.w(0xefc,self.r(0xefc)+count);self.w(0xf02,total);self.now=now
 def move(self,now):
  if now>self.end:self.advance(self.end);self.blocked=True;self.u.emu_stop()
  else:self.advance(now)
 def pulse(self,needed):
  if needed:
   n=((needed-1)*65536+self.r(0xf02))//(65536-self.inc)+1;self.move(edge(edges(self.now)+n-1))
 def key(self):
  at=edges(self.now)%16;value=0x10 if self.profile==3 else 0x20 if self.profile==1 and (at<5 or at>=10) or self.profile==2 and at!=6 else 0
  self.lines.append(f'K {self.now} {value}');return (value&~0x10)|((value&0x10)<<8)
 def event(self,kind,a=0,b=0,c=0,d=0,e=0,name=b''):
  if kind=='bgm_load':self.song=self.now
  self.lines.append(f'E {self.now} {kind} {a} {b} {c} {d} {e} '+(name.hex() if name else '-'))
 def interrupt(self,u,number,_):
  try:
   assert number in (0x60,0x61) and u.reg_read(UC_X86_REG_AH)==5
   if self.measure_poll:self.move(self.song+((self.now-self.song)//1000000000+1)*1000000000)
   self.measure_poll=True;u.reg_write(UC_X86_REG_AX,0 if self.mode==2 else (self.now-self.song)//1000000000)
  except BaseException as error:self.error=error;u.emu_stop()
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;rel=cs-self.load;sp=u.reg_read(UC_X86_REG_SP)
  arg=lambda:struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]
  if rel==0xa05:self.fade=False;self.in_input=False;self.in_measure=False
  if rel==0:
   if ip in (0x622,0x666,0x222c,0x226c):self.event('fade',int(ip>=0x222c),int(ip in (0x622,0x222c)),signed(arg()));self.fade=True;self.state=2;return
   if 0x622<=ip<0x6a4 or 0x222c<=ip<0x22ac:return
   if ip==0x19ec and self.fade:self.lines.append(f'P {self.now} {self.r(0x132)}');return_to_caller(u);return
   if ip==0x2206:self.sync_poll=False;return
   if 0x2206<ip<0x222c:
    if ip==0x2225:
     if self.sync_poll:self.pulse(1)
     self.sync_poll=True
    return
  if rel==0xcc7:
   if ip in (0x81a,0x822):
    value=self.key();self.w(0x1b42,value if ip==0x81a else self.r(0x1b42)|value);return_to_caller(u);return
   if ip==0x33:
    self.minimum=arg()
    if not self.in_input and not self.in_measure:self.event('delay',signed(self.minimum));self.state=2
    return
   if 0x33<ip<0x48:
    if ip==0x3c:self.pulse(max(0,self.minimum-self.r(0xefa)))
    return
   if ip==0x20a:self.event('wait',signed(arg()));self.in_input=True;self.state=3;return
   if 0x20a<ip<0x260:
    if ip==0x214:self.state=3
    elif ip==0x235:self.state=4
    return
   if ip==0x3d6:
    fallback,goal=struct.unpack('<HH',u.mem_read(0x70000+sp+4,4));self.event('measure',signed(goal),signed(fallback));self.in_measure=True;self.state=5;self.measure_poll=False;return
   if 0x3d6<ip<0x408:return
  super().body(u,address)
 def run(self):
  self.done=False;self.error=None;self.font_mode=False
  for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,value)
  self.u.mem_write(0x7ff00,struct.pack('<H',0xff00));self.u.emu_start(self.cs*16+0xdac,0x10ffff,count=3000000)
  assert not self.error and (self.done or self.blocked),(self.error,self.done,self.now)
  if self.done:assert self.u.reg_read(UC_X86_REG_SP)==0xff02
  self.lines.append(f'STOP {self.now} {self.end-self.now} {6 if self.done else self.state} {self.r(0xefa)} {self.r(0xefc)} {self.r(0xf02)} {self.r(0x132)}');return self.lines

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','native','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 target=a.root/'.analysis/targets/th04/maine.exe';decoded=a.root/'.analysis/port64/maine-ending-v1291/decoded-original';hdi=a.root/'.analysis/runtime/images/zun.hdi';assets=ending_assets(hdi)
 scripts={k:v for k,v in assets.items() if k.startswith('_ED') and k.endswith('.TXT')};scripts.update({'mixed':b'\\v0\\s3\\t17\\wi0\\wo2\\fi0\\fo1\\wm3,0\\g2\\k1\\$', 'measure':b'\\m,STAFF \r\n\\wm3,0\\$'})
 rows=[(inc,seed,0,profile,mode,120000000000,0) for inc,seed,profile,mode in itertools.product((0,13311),(0,65535),(0,1,2,3),(0,1,2))]
 reference=None
 if a.reference:
  reference=json.loads((a.reference/'receipt.json').read_text());assert reference['passed'] and reference['oracle_sha256']==sha(Path(__file__)) and reference['rows']==[list(x) for x in rows]
  for name,pin in reference['files'].items():assert sha(a.reference/name)==pin
 records=[]
 for name,body in sorted(scripts.items()):
  d=a.output/name;d.mkdir();script=d/'script.txt';script.write_bytes(body);wanted=None
  if reference:wanted=(a.reference/name/'expected.txt').read_bytes()
  else:
   controls=[]
   for load in (0x1000,0x3333):
    lines=[]
    for index,row in enumerate(rows):lines.extend([f'CASE {index}',*Original(target,decoded,load,row,body).run()])
    raw=('\n'.join(lines)+'\n').encode();(d/f'original-{load:x}.txt').write_bytes(raw);controls.append(raw)
   assert controls[0]==controls[1];wanted=controls[0]
  (d/'expected.txt').write_bytes(wanted)
  for fine in (False,True):
   v=d/('fine-vectors.txt' if fine else 'vectors.txt');v.write_text(''.join(' '.join(map(str,(*row[:-1],1000000 if fine else 0)))+'\n' for row in rows));q=subprocess.run([str(a.native.resolve()),'--cutscene-elapsed',str(script.resolve()),str(v.resolve())],capture_output=True);tag='fine' if fine else 'coarse';(d/(tag+'.txt')).write_bytes(q.stdout);(d/(tag+'.stderr')).write_bytes(q.stderr)
   assert q.returncode==0 and not q.stderr and q.stdout==wanted,(name,tag,q.returncode)
  records.append(dict(name=name,script_sha256=sha(script),rows=len(rows)));print('Cutscene elapsed',name,len(rows),'PASS',flush=True)
 receipt=dict(passed=True,rows=rows,cases=records,original_cases=len(rows)*2*len(scripts),native_vectors=len(rows)*len(scripts),partition_vectors=len(rows)*len(scripts),oracle_sha256=sha(Path(__file__)),native_sha256=sha(a.native),target_sha256=sha(target),hdi_sha256=sha(hdi),files={str(f.relative_to(a.output)):sha(f) for f in a.output.rglob('*') if f.is_file()},scope=__doc__)
 (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Cutscene elapsed PASS',receipt['original_cases'],'original',receipt['native_vectors'],'coarse/fine',flush=True)
if __name__=='__main__':main()
