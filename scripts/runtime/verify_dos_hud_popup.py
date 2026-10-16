"""Execute original popup/CRT/TRAM instructions with only a near-return sentinel."""
import hashlib,struct,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/runtime'))
from verify_dos_text_gaiji import original
class PopupMachine:
 def __init__(self,load):
  self.layout=original('main');self.load=load;self.ds=load+self.layout['dg'];body=bytearray(self.layout['body'])
  for site in self.layout['sites']:struct.pack_into('<H',body,site,(struct.unpack_from('<H',body,site)[0]+load)&65535)
  self.module=bytes(body);self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000);self.u.mem_write(load*16,self.module);self.u.hook_add(unicorn.UC_HOOK_CODE,self.hook);self.u.hook_add(unicorn.UC_HOOK_INTR,self.interrupt);self.visited=set();self.writes=[];self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.store,begin=0xa0000,end=0xa3fff)
 def interrupt(self,u,n,unused):raise ValueError('unexpected original interrupt %x'%n)
 def hook(self,u,address,size,unused):
  if address==(self.load+0xaaf)*16+0xf000:self.done=True;u.emu_stop();return
  if not self.load*16<=address<self.load*16+len(self.module):raise ValueError('unexpected original code %x'%address)
  self.visited.add(address-self.load*16)
 def store(self,u,access,address,size,value,unused):self.writes.append((address,size,value))
 def write(self,at,fmt,*values):self.u.mem_write(self.ds*16+at,struct.pack('<'+fmt,*values))
 def read(self,at,fmt):return struct.unpack('<'+fmt,self.u.mem_read(self.ds*16+at,struct.calcsize('<'+fmt)))
 def seed(self,kind=3,bonus=0):
  self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16+0x4688,bytes(0x1a));self.write(0x768,'H',0xa000);self.write(0x469b,'B',kind);self.write(0x469e,'H',0x67e8);self.write(0x1b64,'B',0);self.write(0x46a2,'I',bonus);self.u.mem_write(0xa0000,bytes(0x4000))
 def call(self):
  self.done=False;self.writes=[];cs=self.load+0xaaf
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_ES,0xa000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_EFLAGS,0x202)):self.u.reg_write(reg,value)
  self.u.mem_write(0x7e000,struct.pack('<H',0xf000));self.u.emu_start(cs*16+0x67e8,0x10ffff,count=1000000)
  assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xe002,'original popup return/ABI'
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_BP,0xd000),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678)):assert self.u.reg_read(reg)==value,'original popup preserved-register ABI'
  return self.snapshot()
 def snapshot(self):
  return dict(frame=self.read(0x1b64,'B')[0],length=self.read(0x4688,'h')[0],current=self.read(0x468a,'B')[0],reached=self.read(0x468b,'B')[0],shift=bytes(self.u.mem_read(self.ds*16+0x468c,9)).hex(),left=self.read(0x4696,'h')[0],dest=self.read(0x4698,'h')[0],requested=self.read(0x469b,'B')[0],callback=self.read(0x469e,'H')[0],bonus=self.read(0x46a2,'I')[0],text=bytes(self.u.mem_read(0xa0000,0x4000)).hex())
if __name__=='__main__':
 m=PopupMachine(0x1000);m.seed()
 for i in range(129):
  s=m.call()
  if i<3 or i>=127:print(i,{k:v for k,v in s.items() if k not in ('text','shift')})
 print('visited',len(m.visited))
