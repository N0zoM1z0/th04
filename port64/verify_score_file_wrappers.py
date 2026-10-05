"""Original file append/read wrappers; only successful DOS INT21 is adapted."""
from pathlib import Path
import sys,json,struct,hashlib,argparse
import unicorn
from unicorn.x86_const import *
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'port64'))
from verify_cutscene import Original as Base
sha=lambda b:hashlib.sha256(b).hexdigest()
class Wrapper(Base):
 def __init__(self,target,decoded,load):
  super().__init__(target,decoded,load)
  self.u.hook_add(unicorn.UC_HOOK_INTR,self.dos)
 def dos(self,u,number,unused):
  try:
   assert number==0x21;ax=u.reg_read(UC_X86_REG_AX)
   if ax==0x3d02:
    address=u.reg_read(UC_X86_REG_DS)*16+u.reg_read(UC_X86_REG_DX)
    assert bytes(u.mem_read(address,11))==b'GENSOU.SCR\0';u.reg_write(UC_X86_REG_AX,7)
   elif ax==0x4202:
    assert u.reg_read(UC_X86_REG_BX)==7 and u.reg_read(UC_X86_REG_CX)==u.reg_read(UC_X86_REG_DX)==0
    self.position=len(self.file);u.reg_write(UC_X86_REG_AX,self.position&65535);u.reg_write(UC_X86_REG_DX,self.position>>16)
   elif ax>>8==0x3f:
    assert u.reg_read(UC_X86_REG_BX)==7;count=u.reg_read(UC_X86_REG_CX)
    data=self.file[self.position:self.position+count];address=u.reg_read(UC_X86_REG_DS)*16+u.reg_read(UC_X86_REG_DX)
    if data:u.mem_write(address,data)
    self.position+=len(data);u.reg_write(UC_X86_REG_AX,len(data))
   else:raise ValueError(f'unexpected DOS function{ax:04x}')
   u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)&~1)
  except BaseException as e:self.error=e;u.emu_stop()
 def body(self,u,address):
  seg=u.reg_read(UC_X86_REG_CS)-self.load;ip=address-u.reg_read(UC_X86_REG_CS)*16
  if seg==0xa05 and ip==0xff00:self.done=True;u.emu_stop();return
  if seg==0 and (0x79a<=ip<0x7b1 or 0x8a8<=ip<0x8fa or 0x9d4<=ip<0xa88):return
  raise ValueError(f'unexpected wrapper instruction{seg:04x}:{ip:04x}')
 def run(self,append,size,buffer_size=0):
  self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
  self.done=False;self.error=None;self.font_mode=False;self.position=0;self.file=bytes((i*79)&255 for i in range(size))
  self.write(0xee,'H',0xffff if append else 7);self.write(0xec,'H',buffer_size)
  self.write(0xeb6,'HH',0x200,0x8000);self.write(0xeba,'I',0);self.write(0xebe,'HHHH',0,0,0,0)
  self.u.mem_write(self.ds*16+0x3fc2,bytes([0xa5])*196)
  for reg,v in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_ES,0),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,v)
  args=(0x880,self.ds) if append else (196,0x3fc2,self.ds)
  self.u.mem_write(0x7f000,struct.pack('<'+'H'*(2+len(args)),0xff00,self.cs,*args))
  self.u.emu_start(self.load*16+(0x8a8 if append else 0x9d4),0x10ffff,count=100000)
  if self.error:raise RuntimeError('original wrapper failed') from self.error
  assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xf004+len(args)*2
  if append:
   assert self.u.reg_read(UC_X86_REG_AX)==1 and self.read(0xee,'H')[0]==7 and self.read(0xeba,'I')[0]==size
   return dict(kind='append',size=size,position=size)
  count=min(196,size);actual=bytes(self.u.mem_read(self.ds*16+0x3fc2,196))
  assert actual==self.file[:count]+bytes([0xa5])*(196-count) and self.u.reg_read(UC_X86_REG_AX)==count
  assert not buffer_size or not self.read(0xec0,'H')[0] or self.read(0xeba,'I')[0]+self.read(0xebe,'H')[0]==count
  if not buffer_size:assert self.read(0xeba,'I')[0]==count
  return dict(kind='read',size=size,buffer_size=buffer_size,returned=count,buffer_sha256=sha(actual),buffer_position=self.read(0xeba,'I')[0],buffer_cursor=self.read(0xebe,'H')[0],buffer_valid=self.read(0xec0,'H')[0])
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 args=p.parse_args()
 rows=[]
 for load in (0x1000,0x2000):
  w=Wrapper(args.target,args.decoded_dir,load);result=[]
  for size in (0,1960,65535,65536,196000):result.append(w.run(True,size))
  for buffer in (0,64):
   for size in (0,1,137,196,541):result.append(w.run(False,size,buffer))
  rows.append(result)
 assert rows[0]==rows[1]
 out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
 receipt=dict(passed=True,controls=rows[0],load_segments=[4096,8192],append_extent='0000:08A8..08F9',read_extent='0000:09D4..0A87',append_sha256=sha(w.payload[0x8a8:0x8fa]),read_sha256=sha(w.payload[0x9d4:0xa88]),scope='Full original file wrappers and DOSAXDX helper, success-only INT21 adapter. Both direct and buffered reads leave unread HI bytes intact;append stores actual DWORD EOF position. No physical DOS filesystem/error behavior claim.')
 (out/'wrapper-controls.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Original append/direct-buffered read wrappers:',len(rows[0]),'controls at two loads PASS')

if __name__=='__main__':main()
