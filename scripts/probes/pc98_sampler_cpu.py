"""Replay independently sampled bytes through unchanged original MAIN instructions."""
import hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'.analysis/reconstruction/probes/native-bgm-title-v1450/unicorn-2.1.4'),str(ROOT/'scripts/probes')]
import unicorn
from unicorn.unicorn_py3 import unicorn as library
from unicorn.x86_const import *
from compare_th04_dos_demos import relocated_module
MAIN_SHA='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
ENGINE_SHA='ddb196ec82b52e502c18e4a34478bf7b9f61c83c2ebaa95c74d8ded45a95da9c'
REGS=[UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_EBX,UC_X86_REG_ESP,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI]
SEGS=[UC_X86_REG_ES,UC_X86_REG_CS,UC_X86_REG_SS,UC_X86_REG_DS]
POINTS=[(0x6cd,7),(0x6fa,9),(0x729,8),(0x758,5),(0x771,2),(0x781,0),(0x791,3),(0x7a1,6)]
class Sampler:
 def __init__(self,load,dgroup):
  target=(ROOT/'.analysis/targets/th04/main.exe').read_bytes();assert hashlib.sha256(target).hexdigest()==MAIN_SHA
  self.engine=Path(library.uclib._name).resolve();assert unicorn.__version__=='2.1.4' and hashlib.sha256(self.engine.read_bytes()).hexdigest()==ENGINE_SHA
  self.load,self.ds=load,dgroup;self.module=relocated_module(target,load)
  self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000);self.u.mem_write(load*16,self.module)
  self.u.hook_add(unicorn.UC_HOOK_CODE,self.guarded(self.code))
  self.u.hook_add(unicorn.UC_HOOK_INTR,self.guarded(self.bios))
  self.u.hook_add(unicorn.UC_HOOK_INSN,self.guarded(self.input),None,1,0,UC_X86_INS_IN)
  self.u.hook_add(unicorn.UC_HOOK_INSN,self.guarded(self.output),None,1,0,UC_X86_INS_OUT)
 def guarded(self,fn):
  def invoke(*args):
   try:return fn(*args)
   except BaseException as error:self.error=error;self.u.emu_stop();return 0
  return invoke
 def code(self,u,address,size,data):
  cs=u.reg_read(UC_X86_REG_CS)-self.load;ip=address-(cs+self.load)*16
  assert 0<=ip<=65535
  if cs==0x130e and ip==0x7c4:self.done=True;u.emu_stop();return
  if cs==0x130e and self.at<len(POINTS) and ip==POINTS[self.at][0]:
   point=self.scalars[self.at];assert POINTS[self.at]==(point['after_offset'],point['group'])
   assert u.reg_read(UC_X86_REG_AH)==point['actual_ah']
   if self.compare:assert self.actions()==point['key_det'],('intermediate latch',self.at,self.actions(),point['key_det'])
   self.at+=1
 def bios(self,u,number,data):
  assert number==0x18 and u.reg_read(UC_X86_REG_AH)==2;u.reg_write(UC_X86_REG_AL,self.returned['shift'])
 def input(self,u,port,size,data):
  assert size==1
  if port==0x188:return 0
  assert port==0x18a and self.io_register==14;return (~self.joystick)&255
 def output(self,u,port,size,value,data):
  assert size==1
  if port==0x188:self.io_register=value
  else:assert port==0x18a and self.io_register==15 and value==128
 def actions(self):return int.from_bytes(self.u.mem_read(self.ds*16+0x3974,2),'little')
 def call(self,entry,returned,keys,scalars,operation,compare=True):
  u=self.u;self.returned=returned;self.scalars=scalars;self.at=0;self.error=None;self.done=False;self.compare=compare
  self.joystick=int.from_bytes(bytes.fromhex(returned['registers'])[:2],'little') if entry['joystick_enabled'] else 0;assert self.joystick&~63==0
  raw=bytes.fromhex(entry['registers']);segs=bytes.fromhex(entry['segments'])
  for i,reg in enumerate(REGS):u.reg_write(reg,int.from_bytes(raw[4*i:4*i+4],'little'))
  for i,reg in enumerate(SEGS):u.reg_write(reg,int.from_bytes(segs[8*i:8*i+8],'little'))
  u.reg_write(UC_X86_REG_EFLAGS,2|(int.from_bytes(raw[40:48],'little')&0x200))
  u.mem_write(0x52a,keys);u.mem_write(self.ds*16+0x39a,entry['joystick_enabled'].to_bytes(2,'little'))
  u.mem_write(entry['stack_segment']*16+entry['stack_offset'],entry['return_ip'].to_bytes(2,'little')+entry['return_cs'].to_bytes(2,'little'))
  u.emu_start((self.load+0x130e)*16+(0x6bc if operation=='R' else 0x6c4),0x10ffff,count=1000)
  if self.error:raise self.error
  assert self.done and self.at==8
  return self.actions(),bytes(u.mem_read(self.ds*16+0x3976,1))[0]
