#!/usr/bin/env python3
"""Original MAIN pause/menu/input waits against portable elapsed pause.

Legal MZ relocations at loads1000/3333. Graphics and keyboard are guarded ABI
consumers; original pause and complete input_wait/frame_delay/VSYNC_WAIT
execute unchanged. Busy reset-sense loops sample immediately then at explicit
counted IRQ observation edges. This is a cadence adapter, not CPU poll latency,
physical hardware, full gameplay or byte-exact acceptance.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
from unicorn.x86_const import *
from verify_gameover_elapsed import Original as Base
from verify_maine_elapsed import edges
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def held(profile,now):
 n=edges(now)
 if profile==0:return 0x1000
 if n<3:return 0x1000
 if 6<=n<9:return {1:0x20,2:2,3:0x4000,4:0x1000,5:0x4023,6:4,7:4}[profile]
 if 14<=n<17:return 0x20 if profile==2 else 0x2000 if profile==6 else 0x1023 if profile==7 else 0
 return 0
class Original(Base):
 def __init__(self,record,load,row):
  initial,inc,seed,phase,profile,horizon,chunk=row
  super().__init__(record,load,(0,0,inc,seed,phase,profile,horizon,chunk));self.w(0x3974,'H',initial);self.busy=False;self.done=False;self.selected=0
 def prefix(self,tag):return f'{tag} {self.now} {self.r(0x2ab2)} {self.r(0x2ab4)} {self.r(0x2aba)} '
 def keys(self):
  value=held(self.profile,self.now);self.lines.append(f'K {self.now} {value}');return value
 def code(self,u,address,size,_):
  try:
   at=address-self.load*16;sp=u.reg_read(UC_X86_REG_SP)
   if at==0x1a9f0:
    self.done=True;u.emu_stop()
   elif at==0xb3eb:self.selected=u.reg_read(UC_X86_REG_SI)
   elif at in (0x1b50,0x22f6):
    attr,off,seg,row,col=self.words(5);assert seg==self.dg and col==26 and row in (12,14,15)
    raw=bytes(u.mem_read(seg*16+off,32));assert b'\0' in raw;raw=raw.split(b'\0',1)[0]
    self.lines.append(self.prefix('E')+f'{0 if at==0x1b50 else 1} {row} {attr} '+(raw.hex() if raw else '-'));self.ret(True,10)
   elif at==0x1379c:
    ret_ip,ret_cs=struct.unpack('<HH',u.mem_read(0x70000+sp,4));busy=ret_cs==self.load+0xaaf and ret_ip in (0x7ec,0x8bc)
    if busy and self.busy:self.pulse()
    if self.blocked:return
    self.busy=busy;self.w(0x3974,'H',self.keys());self.ret()
   elif at==0x137a4:self.w(0x3974,'H',self.r(0x3974)|self.keys());self.ret()
   elif at==0x13213:
    assert self.words(1)==(0,);self.lines.append(self.prefix('E')+'2 0 0 -');self.busy=False
   elif at==0x131c0:
    if self.r(0x2ab2)<1:self.pulse()
   elif at==0x2462:self.poll=False
   elif at==0x2481:
    if self.poll:self.pulse()
    self.poll=True
  except BaseException as error:self.errors.append(repr(error));u.emu_stop()
 def run(self):
  u=self.u;cs=self.load+0xaaf
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.dg),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
  u.mem_write(0x7e000,struct.pack('<H',0xff00));u.emu_start(cs*16+0x7df,0x10ffff,count=3000000)
  assert not self.errors and (self.done or self.blocked),(self.errors,self.now)
  result=0 if not self.done else 2 if u.reg_read(UC_X86_REG_AX) else 1
  self.lines.append(self.prefix('STOP')+f'{self.end-self.now} {result} {self.selected if self.done else u.reg_read(UC_X86_REG_SI)} {self.r(0x3974)}');return self.lines

def fixtures():return [(initial,inc,seed,phase,profile,horizon,0) for initial,inc,seed,phase,profile,horizon in itertools.product((0,0x1000),(0,13311),(0,65535),(0,1000000),range(8),(1,1000000000,2000000000))]
def wire(row,fine=False):return ' '.join(map(str,(*row[:-1],1000000 if fine else 0)))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','native','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original
 record=original('main');rows=fixtures();pin=hashlib.sha256(record['body'][0xb2cf:0xb3ee]).hexdigest()
 if a.reference:
  j=json.loads((a.reference/'receipt.json').read_text());assert j['passed'] and j['original']==record['pins'] and j['oracle_sha256']==sha(Path(__file__)) and j['extent_sha256']==pin
  for name,digest in j['files'].items():assert sha(a.reference/name)==digest
  wanted=(a.reference/'expected.txt').read_bytes()
 else:
  wanted=None
  for load in (0x1000,0x3333):
   lines=[]
   for index,row in enumerate(rows):
    lines.extend([f'CASE {index}',*Original(record,load,row).run()])
    if index%64==0:print('ORIGINAL',hex(load),index,flush=True)
   raw=('\n'.join(lines)+'\n').encode();(a.output/f'original-{load:x}.txt').write_bytes(raw)
   if wanted is None:wanted=raw
   else:assert wanted==raw,'load metamorphism differs'
 (a.output/'expected.txt').write_bytes(wanted)
 for fine in (False,True):
  tag='fine' if fine else 'coarse';fixture=a.output/(tag+'-vectors.txt');fixture.write_text('\n'.join(wire(row,fine) for row in rows)+'\n');q=subprocess.run([str(a.native.resolve()),'--pause-elapsed',str(fixture)],capture_output=True);(a.output/(tag+'.txt')).write_bytes(q.stdout);(a.output/(tag+'.stderr')).write_bytes(q.stderr)
  if q.returncode or q.stderr or q.stdout!=wanted:
   at=next((i for i,(x,y) in enumerate(itertools.zip_longest(q.stdout.splitlines(),wanted.splitlines())) if x!=y),None);(a.output/'mismatch.json').write_text(json.dumps(dict(tag=tag,first_line=at,exit_code=q.returncode),indent=2)+'\n');raise AssertionError(('pause mismatch',tag,at,q.returncode))
 (a.output/'receipt.json').write_text(json.dumps(dict(passed=True,original=record['pins'],extent='MAIN DEMO_TEXT 0AAF:07DF..08FD load0B2CF..0B3ED',extent_sha256=pin,oracle_sha256=sha(Path(__file__)),native_sha256=sha(a.native),original_controls=len(rows)*2,native_vectors=len(rows),partition_vectors=len(rows),files={str(f.relative_to(a.output)):sha(f) for f in a.output.rglob('*') if f.is_file()},scope=__doc__),indent=2)+'\n');print('MAIN PAUSE PASS',len(rows),flush=True)
if __name__=='__main__':main()
