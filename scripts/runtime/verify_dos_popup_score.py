#!/usr/bin/env python3
"""Execute original popup and subsequent score drain with retained shared bonus."""
import struct
from unicorn.x86_const import *
from verify_dos_hud_popup import PopupMachine as PopupBase

class PopupMachine(PopupBase):
 def seed(self,kind=3,bonus=0):
  super().seed(kind,bonus)
  self.write(0x435a,'II',10000,0);self.write(0x4349,'8B',*([0]*8));self.write(0x4351,'8B',*([9]*8));self.write(0x4359,'B',0);self.write(0x1a66,'2B',0,0);self.write(0x5395,'3B',16,24,11);self.write(0xba86,'HH',0,0x9000);self.u.mem_write(0x90000,bytes(256));self.u.mem_write(0x9000b,b'\3');self.u.mem_write(self.ds*16+0x1ebe,bytes(17))
 def score(self):
  self.done=False;self.writes=[];cs=self.load+0xaaf
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_ES,0xa000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,0x202)):self.u.reg_write(reg,value)
  self.u.mem_write(0x7e000,struct.pack('<H',0xf000));self.u.emu_start(cs*16+0x6bd4,0x10ffff,count=1000000)
  assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xe002 and self.u.reg_read(UC_X86_REG_DS)==self.ds,'original score return/ABI'
  return self.snapshot()
if __name__=='__main__':
 m=PopupMachine(0x1000);m.seed(2,25000);before=m.call();after=m.score();assert before['bonus']==after['bonus']==25000;print('ORIGINAL SCORE RETAINS BONUS',after['bonus'])
