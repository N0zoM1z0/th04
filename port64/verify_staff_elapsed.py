#!/usr/bin/env python3
"""Full original Staff Roll instructions with ideal IRQ/measure stimuli.

Graphics/file calls remain guarded request adapters. Original fade, counted
wait and sound-wait instructions execute unchanged. No physical CPU/I/O/audio
latency or original full scanout claim.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_staff_roll import Original as StaffOriginal
from verify_cutscene import ending_assets
from verify_maine_join import return_to_caller
from verify_maine_elapsed import edges,edge
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Original(StaffOriginal):
 def __init__(self,target,decoded,assets,load,row):
  super().__init__(target,decoded,assets,load);self.inc,self.seed,self.now,self.mode,self.horizon,_=row;self.end=self.now+self.horizon;self.song=self.now;self.lines=[];self.blocked=False;self.fade=False;self.wait_pc=None;self.sync_poll=False;self.measure_poll=False
  n=self.seed+edges(self.now);count=n-n*self.inc//65536
  for at,value in ((0xefa,count),(0xefc,count),(0xf02,n*self.inc),(0x400,self.inc)):self.w(at,value)
  self.write(0x402,'B',0xfb);self.write(0x5a1,'B',0 if not self.mode else 1);self.u.hook_add(unicorn.UC_HOOK_INTR,self.interrupt)
  pins={0x622:(130,'19e015ce0dfae0670711db894ccddad7142328054b3495967b70cdf1529f1f4b'),0xcca3:(21,'0d77d41527daea4e009dcbcdbf7fb8fc956243a9cc04dfd9dc2a289468243d2b'),0xd046:(50,'a66b7ca45082a6bab45fb4ba26a9364c39c6d9fa5b85046536dcc5448fafadd8')}
  for at,(length,pin) in pins.items():assert hashlib.sha256(self.payload[at:at+length]).hexdigest()==pin
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
 def event(self,kind,a=0,b=0,c=0,d=0,name='-'):
  if kind=='bgm_load':self.song=self.now
  self.lines.append(f'E {self.now} {kind} {a} {b} {c} {d} {name}')
 def interrupt(self,u,number,_):
  try:
   assert number in (0x60,0x61) and u.reg_read(UC_X86_REG_AH)==5
   if self.measure_poll:self.move(self.song+((self.now-self.song)//1000000000+1)*1000000000)
   self.measure_poll=True;u.reg_write(UC_X86_REG_AX,0 if self.mode==2 else (self.now-self.song)//1000000000)
  except BaseException as error:self.error=error;u.emu_stop()
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;relative=cs-self.load;sp=u.reg_read(UC_X86_REG_SP)
  if relative==0xa05:
   self.fade=False
   if ip in self.wait_ips:
    if self.wait_pc!=ip:self.event('vsync',2);self.wait_pc=ip
    if self.r(0xefa)<2:self.pulse(2-self.r(0xefa))
    return
   if self.wait_pc is not None and ip==self.wait_pc+7:self.wait_pc=None
  if relative==0:
   if ip in (0x622,0x666):
    speed=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];self.event('fade',int(ip==0x622),speed);self.fade=True;return
   if 0x622<=ip<0x6a4:return
   if ip==0x19ec and self.fade:
    self.lines.append(f'P {self.now} {self.r(0x132)}');return_to_caller(u);return
   if ip==0x2206:self.sync_poll=False;return
   if 0x2206<ip<0x222c:
    if ip==0x2225:
     if self.sync_poll:self.pulse(1)
     self.sync_poll=True
    return
  if relative==0xcc7:
   if ip==0x33:self.minimum=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];return
   if 0x33<ip<0x48:
    if ip==0x3c:self.pulse(max(0,self.minimum-self.r(0xefa)))
    return
   if ip==0x3d6:
    fallback,goal=struct.unpack('<HH',u.mem_read(0x70000+sp+4,4));self.event('measure',goal,fallback);self.measure_poll=False;return
   if 0x3d6<ip<0x408:return
  super().body(u,address)
 def run(self):
  self.done=False;self.error=None
  for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,value)
  self.u.mem_write(0x7ff00,struct.pack('<H',0xff00));self.u.emu_start(self.cs*16+0x13fd,0x10ffff,count=2000000)
  assert not self.error and (self.done or self.blocked),(self.error,self.done,self.now)
  if self.done:assert self.u.reg_read(UC_X86_REG_SP)==0xff02
  count=sum(line.startswith('E ') for line in self.lines);status=3 if self.done else 2
  self.lines.append(f'STOP {self.now} {self.end-self.now} {status} {self.r(0xefa)} {self.r(0xefc)} {self.r(0xf02)} {count} {self.r(0x132)}');return self.lines

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','native','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 target=a.root/'.analysis/targets/th04/maine.exe';decoded=a.root/'.analysis/port64/maine-ending-v1291/decoded-original';hdi=a.root/'.analysis/runtime/images/zun.hdi';assets=ending_assets(hdi);folder=a.output/'assets';folder.mkdir()
 for name,raw in assets.items():
  if name.startswith('SFF'):(folder/name).write_bytes(raw)
 rows=[(*row,180000000000,0) for row in itertools.product((0,13311),(0,65535),(0,1000000),(0,1,2))];controls=[];wanted=None
 if a.reference:
  j=json.loads((a.reference/'receipt.json').read_text());assert j['passed'] and j['oracle_sha256']==sha(Path(__file__)) and j['rows']==[list(row) for row in rows]
  for name,pin in j['files'].items():assert sha(a.reference/name)==pin
  wanted=(a.reference/'expected.txt').read_bytes()
 else:
  for load in (0x1000,0x3333):
   lines=[]
   for index,row in enumerate(rows):lines.extend([f'CASE {index}',*Original(target,decoded,assets,load,row).run()])
   raw=('\n'.join(lines)+'\n').encode();(a.output/f'original-{load:x}.txt').write_bytes(raw);controls.append(raw);print('Original Staff elapsed',hex(load),len(rows),flush=True)
  assert controls[0]==controls[1];wanted=controls[0]
 (a.output/'expected.txt').write_bytes(wanted)
 for fine in (False,True):
  vectors=a.output/('fine-vectors.txt' if fine else 'vectors.txt');vectors.write_text(''.join(' '.join(map(str,(*row[:-1],1000000 if fine else 0)))+'\n' for row in rows))
  q=subprocess.run([str(a.native.resolve()),'--staff-elapsed',str(folder.resolve()),str(vectors.resolve())],capture_output=True);name='fine-native.txt' if fine else 'native.txt';(a.output/name).write_bytes(q.stdout);(a.output/(name+'.stderr')).write_bytes(q.stderr);assert q.returncode==0 and not q.stderr and q.stdout==wanted,('Staff elapsed difference',fine,q.returncode)
 receipt=dict(passed=True,rows=rows,original_cases=len(rows)*2,native_vectors=len(rows),partition_vectors=len(rows),native_sha256=sha(a.native),oracle_sha256=sha(Path(__file__)),target_sha256=sha(target),hdi_sha256=sha(hdi),files={str(f.relative_to(a.output)):sha(f) for f in a.output.rglob('*') if f.is_file()},scope=__doc__)
 (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Staff elapsed PASS',len(rows)*2,'original',len(rows),'coarse/fine vectors',flush=True)
if __name__=='__main__':main()
