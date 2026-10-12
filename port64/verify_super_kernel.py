#!/usr/bin/env python3
"""Actual MAINE SUPER reads, GRCG ports and writes against portable byte kernel.

Seeded pattern segments and geometry are explicit memory-provider controls,
including zero counts and WORD SI/DI wrap. The complete original self-modifying
body executes through its final RETF6, whose guarded stack return adapts a
recorded Unicorn mixed-return failure. No clipping, low-memory contents, physical GRCG bus mapping,
CPU cost, full-game or byte-exact acceptance is inferred from these streams.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
EVENT=struct.Struct('<BHHH')

class Original:
 def __init__(self,record,load):
  self.load=load;self.ds=load+record['dg'];module=bytearray(record['body'])
  for at in record['sites']:struct.pack_into('<H',module,at,(struct.unpack_from('<H',module,at)[0]+load)&65535)
  self.module=bytes(module);self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000)
  assert record['body'][0x284b:0x284e]==bytes((0xca,6,0))
  self.u.hook_add(unicorn.UC_HOOK_CODE,self.end,begin=load*16+0x284b,end=load*16+0x284b)
  self.u.hook_add(unicorn.UC_HOOK_MEM_READ,self.read)
  self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.write)
  self.u.hook_add(unicorn.UC_HOOK_INSN,self.port,None,1,0,UC_X86_INS_OUT)
 def event(self,kind,address,size,value):self.output.write(EVENT.pack(ord(kind),address,size,value))
 def end(self,u,address,size,_):
  try:
   sp=u.reg_read(UC_X86_REG_SP)
   assert u.reg_read(UC_X86_REG_CS)==self.load and u.reg_read(UC_X86_REG_SS)==0x7000
   assert bytes(u.mem_read(address,3))==bytes((0xca,6,0))
   assert struct.unpack('<HH',u.mem_read(0x70000+sp,4))==(0xff00,self.load+0xa05)
   u.reg_write(UC_X86_REG_SP,sp+10);self.done=True;u.emu_stop()
  except BaseException as error:self.error=error;u.emu_stop()
 def read(self,u,access,address,size,value,_):
  try:
   ip=u.reg_read(UC_X86_REG_EIP)-self.load*16
   if ip not in (0x2850,0x2878,0x288a,0x28a0,0x28b0,0x28c2,0x28d6,0x28e6):return
   assert size in (1,2) and 0<=address-0x90000<=65535
   value=int.from_bytes(u.mem_read(address,size),'little');self.event('R',address-0x90000,size,value)
  except BaseException as error:self.error=error;u.emu_stop()
 def write(self,u,access,address,size,value,_):
  try:
   ip=u.reg_read(UC_X86_REG_EIP)-self.load*16
   if ip not in (0x285b,0x2862,0x2883,0x2891,0x28ab,0x28bb,0x28c9,0x28e1,0x28f1,0x28f8):return
   assert size in (1,2) and 0<=address-0xa8000<=65535
   self.event('W',address-0xa8000,size,value&((1<<(8*size))-1))
  except BaseException as error:self.error=error;u.emu_stop()
 def port(self,u,port,size,value,_):
  try:
   assert port in (0x7c,0x7e) and size==1;self.event('P',port,size,value)
  except BaseException as error:self.error=error;u.emu_stop()
 def run(self,row,output,index):
  left,top,size,seed=row;self.output=output;self.done=False;self.error=None
  self.u.mem_write(self.load*16,self.module)
  # FF60 models the actual raw-zero registration request, but geometry and
  # the source segment are controlled providers, not measured startup RAM.
  self.u.mem_write(self.ds*16+0xdcc,struct.pack('<H',0x9000));self.u.mem_write(self.ds*16+0x11cc,struct.pack('<H',size))
  self.u.mem_write(0x90000,bytes((at*73+(at>>8)*11+seed)&255 for at in range(65537)))
  self.u.mem_write(0xa8000,bytes(65537))
  for reg,value in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):
   self.u.reg_write(reg,value)
  self.u.mem_write(0x7f000,struct.pack('<5H',0xff00,self.load+0xa05,0xff60,top,left));self.event('C',index,0,0)
  self.u.emu_start(self.load*16+0x275e,0x10ffff,count=12000000)
  if self.error:raise RuntimeError(('SUPER callback rejected',index,row)) from self.error
  assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xf00a,(index,row)

def vectors():
 rows=[(160+odd*8+shift,96,(width<<8)|height,(width*17+height*3+shift)&255) for odd,shift,width,height in itertools.product(range(2),range(8),(0,1,2,3,4,5,31),(1,2))]
 rows.extend((left,96,(width<<8)|2,19) for left,width in itertools.product((160,168),(127,128,129,159,160,255)))
 rows.extend((left,96,width<<8,7) for left,width in itertools.product((160,168),(0,1,2)))
 rows.extend(((65535,65535,0x0302,1),(65528,819,0x0202,3),(0,65535,0x0302,5),(172,819,0x0210,0)))
 return rows

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','native','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 sys.path.insert(0,str(a.root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original
 record=original('maine');rows=vectors();fixture=a.output/'vectors.txt';fixture.write_text(''.join(' '.join(map(str,row))+'\n' for row in rows));wanted=a.output/'original.bin'
 if a.reference:
  proof=json.loads((a.reference/'receipt.json').read_text());assert proof['passed'] and proof['original']==record['pins'] and proof['oracle_sha256']==sha(Path(__file__))
  for name,pin in proof['files'].items():assert sha(a.reference/name)==pin
  assert fixture.read_bytes()==(a.reference/'vectors.txt').read_bytes();wanted.write_bytes((a.reference/'original.bin').read_bytes())
 else:
  for load in (0x1000,0x3333):
   out=a.output/f'original-{load:x}.bin';o=Original(record,load)
   with out.open('xb') as stream:
    for index,row in enumerate(rows):
     o.run(row,stream,index)
     if index%32==0:print('ORIGINAL',hex(load),index,flush=True)
   if load==0x1000:wanted.write_bytes(out.read_bytes())
   else:assert sha(out)==sha(wanted),'load metamorphism differs'
 native=a.output/'native.bin';q=subprocess.run([str(a.native.resolve()),'--super-kernel',str(fixture),str(native)],capture_output=True);(a.output/'stderr.txt').write_bytes(q.stderr)
 assert q.returncode==0 and not q.stderr,(q.returncode,q.stderr)
 if sha(native)!=sha(wanted):
  with wanted.open('rb') as x,native.open('rb') as y:
   index=0;case=0
   while True:
    want=x.read(EVENT.size);got=y.read(EVENT.size)
    if want and want[0]==ord('C'):case=EVENT.unpack(want)[1]
    if want!=got:raise AssertionError(('SUPER event mismatch',case,index,EVENT.unpack(want) if len(want)==EVENT.size else want,EVENT.unpack(got) if len(got)==EVENT.size else got))
    if not want:break
    index+=1
 j=dict(passed=True,original=record['pins'],loads=[4096,13107],original_controls=len(rows)*2,native_controls=len(rows),source_segment=0x9000,oracle_sha256=sha(Path(__file__)),native_sha256=sha(a.native),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name)),extent_sha256=hashlib.sha256(record['body'][0x275e:0x2910]).hexdigest(),events=wanted.stat().st_size//EVENT.size,files={str(f.relative_to(a.output)):sha(f) for f in a.output.rglob('*') if f.is_file()},scope=__doc__)
 (a.output/'receipt.json').write_text(json.dumps(j,indent=2)+'\n');print('SUPER KERNEL PASS',len(rows),j['events'],flush=True)
if __name__=='__main__':main()
