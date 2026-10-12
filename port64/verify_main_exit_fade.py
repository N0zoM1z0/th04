#!/usr/bin/env python3
"""Three original MAIN exits and blackout16 against actual Ending/Extra owners.

Original complete exits, fade and IRQ-owned wait execute unchanged. Sound
command and nonreturning execl entry are guarded boundaries, with ideal IRQ
stimuli and explicit resident storage. Native release-order checks include
publication and fresh MAINE. CPU, I/O, loader/audio latency is not inferred.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_maine_elapsed import edges,edge
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Original:
 def __init__(self,record,load,row):
  self.kind,self.inc,self.seed,self.now,self.horizon,_=row;self.end=self.now+self.horizon;self.load=load;self.blocked=False;self.done=False;self.lines=[];self.errors=[];self.poll=False;self.record=record
  body=bytearray(record['body'])
  for at in record['sites']:struct.pack_into('<H',body,at,(struct.unpack_from('<H',body,at)[0]+load)&65535)
  self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000);self.u.mem_write(load*16,bytes(body));self.base=(load+record['dg'])*16
  n=self.seed+edges(self.now);count=n-n*self.inc//65536
  for at,value in ((0x2ab2,count),(0x2ab4,count),(0x2aba,n*self.inc),(0x772,self.inc),(0x3a4,100)):self.w(at,value)
  self.u.mem_write(self.base+0x774,b'\xfb');self.u.mem_write(self.base+0xba86,struct.pack('<HH',0x100,0x5000));self.u.mem_write(0x50125,b'7');self.u.hook_add(unicorn.UC_HOOK_CODE,self.code)
 def r(self,at):return struct.unpack('<H',self.u.mem_read(self.base+at,2))[0]
 def w(self,at,value):self.u.mem_write(self.base+at,struct.pack('<H',value&65535))
 def advance(self,now):
  n=edges(now)-edges(self.now);total=self.r(0x2aba)+n*self.inc;count=n-total//65536
  self.w(0x2ab2,self.r(0x2ab2)+count);self.w(0x2ab4,self.r(0x2ab4)+count);self.w(0x2aba,total);self.now=now
 def pulse(self):
  n=self.r(0x2aba)//(65536-self.inc)+1;now=edge(edges(self.now)+n-1)
  if now>self.end:self.advance(self.end);self.blocked=True;self.u.emu_stop()
  else:self.advance(now)
 def far_return(self,args=0):
  u=self.u;sp=u.reg_read(UC_X86_REG_SP);ip,cs=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4+args);u.reg_write(UC_X86_REG_CS,cs);u.reg_write(UC_X86_REG_IP,ip)
 def code(self,u,address,size,_):
  try:
   at=address-self.load*16
   if at==0x1f04:self.lines.append(f'P {self.now} {self.r(0x3a4)}');self.far_return()
   elif at==0x2462:self.poll=False
   elif at==0x2481:
    if self.poll:self.pulse()
    self.poll=True
   elif at==0x133dc:
    sp=u.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]==0x204;self.far_return(2)
   elif at==0xe7fd:
    marker=self.u.mem_read(0x50130,1)[0];assert marker==(255,254,253)[self.kind]
    if self.kind<2:assert self.u.mem_read(0x50125,1)[0]==ord('0')+self.kind
    else:assert self.u.mem_read(0x50125,1)[0]==ord('7')
    self.lines.append(f'X {self.now} {self.r(0x2ab2)} {self.r(0x2ab4)} {self.r(0x2aba)}');self.done=True;u.emu_stop()
  except BaseException as error:self.errors.append(repr(error));u.emu_stop()
 def run(self):
  u=self.u;entry=(0xb7b9,0xb7e4,0xb80f)[self.kind]
  for reg,value in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.base//16),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x4321),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
  u.mem_write(0x7f000,struct.pack('<HH',0xff00,self.load));u.emu_start(self.load*16+entry,0x10ffff,count=2000000)
  assert not self.errors and (self.done or self.blocked),(self.errors,self.done,self.now)
  if not self.done:self.lines.append(f'BLOCK {self.now} {self.r(0x2ab2)} {self.r(0x2ab4)} {self.r(0x2aba)} {self.r(0x3a4)}')
  self.lines.append(f'END {int(self.done)}');return self.lines

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','native','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original
 record=original('main');body=bytes(record['body']);extents=[(0xb7b9,124,'0cc7e7f846ffba45efc6d49668da80370b4b12acc1752b20daa14f3d045afcbb'),(0x622,130,'c4597fe984067e57ad982e693ed768a83e95d76465666c0db5d5eb0ae834fa3e')]
 for at,size,pin in extents:assert hashlib.sha256(body[at:at+size]).hexdigest()==pin
 rows=[(kind,inc,seed,phase,horizon,0) for kind,inc,seed,phase,horizon in itertools.product((0,1,2),(0,13311),(0,65535),(0,1000000),(1,4840000000,6100000000))];wanted=None
 if a.reference:
  j=json.loads((a.reference/'receipt.json').read_text());assert j['passed'] and j['oracle_sha256']==sha(Path(__file__)) and j['original']==record['pins'] and j['rows']==[list(x) for x in rows]
  for name,pin in j['files'].items():assert sha(a.reference/name)==pin
  wanted=(a.reference/'expected.txt').read_bytes()
 else:
  controls=[]
  for load in (0x1000,0x3333):
   lines=[]
   for index,row in enumerate(rows):lines.extend([f'CASE {index}',*Original(record,load,row).run()])
   raw=('\n'.join(lines)+'\n').encode();(a.output/f'original-{load:x}.txt').write_bytes(raw);controls.append(raw);print('Original MAIN exit',hex(load),len(rows),flush=True)
  assert controls[0]==controls[1];wanted=controls[0]
 (a.output/'expected.txt').write_bytes(wanted)
 for fine in (False,True):
  v=a.output/('fine-vectors.txt' if fine else 'vectors.txt');v.write_text(''.join(' '.join(map(str,(*row[:-1],1000000 if fine else 0)))+'\n' for row in rows));tag='fine' if fine else 'coarse';folder=a.output/('save-'+tag);folder.mkdir();q=subprocess.run([str(a.native.resolve()),'--main-exit-fade',str(folder.resolve()),str(v.resolve())],capture_output=True);(a.output/(tag+'.txt')).write_bytes(q.stdout);(a.output/(tag+'.stderr')).write_bytes(q.stderr);assert q.returncode==0 and not q.stderr and q.stdout==wanted,('MAIN fade difference',tag,q.returncode)
 receipt=dict(passed=True,original=record['pins'],rows=rows,original_cases=len(rows)*2,native_vectors=len(rows),partition_vectors=len(rows),oracle_sha256=sha(Path(__file__)),native_sha256=sha(a.native),files={str(f.relative_to(a.output)):sha(f) for f in a.output.rglob('*') if f.is_file()},scope=__doc__)
 (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('MAIN exit fade PASS',len(rows)*2,'original',len(rows),'coarse/fine',flush=True)
if __name__=='__main__':main()
