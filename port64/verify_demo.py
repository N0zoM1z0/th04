#!/usr/bin/env python3
"""Original OP idle/rotation and MAIN replay/startup controls at two loads.

Execute OP0A74:0289..032D and after-menu idle0D11..0D3A; MAIN0AAF:08FE..0997,
blackout0000:0666..06A2 and the first caller through0489. Replay file/read/alloc,
CGROM/GRCG, graphics/resource/input/wait and final exec are guarded adapters.
This does not accept whole original gameplay, physical audio/timing or DOS exactness.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn.x86_const import *
from verify_player_lifecycle import Original as MainBase
from verify_main_hud_join import Original as Hud
from verify_main_score import Original as Score
from verify_op_score import Original as OpBase,PACKED
from verify_maine_join import return_to_caller
from probe_assets import main_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Replay(MainBase):
 def body(self,u,address,size,unused):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  if pair[0]==0xaaf and 0x949<=pair[1]<0x998:return
  if pair[0]==0 and 0x666<=pair[1]<0x6a3:return
  if pair==(0,0x267c):assert words(1)==(0x9200,);self.requests.append('free');return_to_caller(u,2);return
  if pair==(0,0x2462):self.ticks+=1;return_to_caller(u);return
  if pair==(0,0x1f04):self.tones.append((self.ticks,self.read(0x3a4,'H')[0]));return_to_caller(u);return
  if pair==(0xaaf,0x3d0d):
   off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp+4,4));assert bytes(u.mem_read(seg*16+off,3))==b'op\0'
   self.requests.append('exec-op');self.finished=True;u.emu_stop();return
  raise ValueError(f'unexpected demo consumer {pair}')
 def sample(self,replay,frame,keys,shift):
  self.error=None;self.finished=False;self.requests=[];self.tones=[];self.ticks=0
  self.u.mem_write(0x92000,replay);self.write(0x2a52,'HH',0,0x9200);self.write(0x538a,'H',frame)
  self.write(0x3974,'HB',keys,shift)
  cs=self.load+0xaaf
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,value)
  self.u.mem_write(0x7e000,struct.pack('<H',0xf000));self.u.emu_start(cs*16+0x949,cs*16+0xf000,count=100000)
  if self.error:raise self.error
  if self.finished:
   assert self.requests==['free','exec-op'];assert self.tones==[(1+10*i,max(0,100-i*6)) for i in range(18)]
  else:assert self.u.reg_read(UC_X86_REG_SP)==0xe002
  return f'{self.read(0x3974,"H")[0]} {self.read(0x3976,"B")[0]} {int(keys==0)} {int(self.finished)}'
class Op(OpBase):
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16)
  if self.mode=='rotation':
   if pair==(0xa74,0x32e):self.finished=True;u.emu_stop();return
   if pair[0]==0xa74 and 0x289<=pair[1]<0x32e:return
  else:
   if pair==(0xa74,0x289):self.started=True;self.finished=True;u.emu_stop();return
   if pair==(0xa74,0x912):return_to_caller(u,far=False);return
   if pair==(0xda1,0x2b):
    assert struct.unpack('<H',u.mem_read(0x70000+u.reg_read(UC_X86_REG_SP)+4,2))==(1,)
    self.finished=True;u.emu_stop();return
   if pair[0]==0xa74 and 0xd11<=pair[1]<0xd3b:return
  raise ValueError(f'unexpected OP demo {pair}')
 def run(self,mode,a,b=0,c=0):
  self.error=None;self.finished=False;self.started=False;self.mode=mode
  r=bytearray([0xa5]*256);r[0x3e]=a if mode=='rotation' else 0
  before=bytes(r);self.u.mem_write(0x90000,before);self.write(0x1a64,'HH',0,0x9000);self.write(0x2710,'H',c)
  for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_SI,a),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,value)
  self.u.mem_write(0x7e000,struct.pack('<H',0xff00));entry=0x289 if mode=='rotation' else 0xd1c if b else 0xd11
  self.u.emu_start(self.cs*16+entry,self.cs*16+0xff00,count=1000)
  if self.error:raise self.error
  assert self.finished
  if mode=='rotation':
   after=bytes(self.u.mem_read(0x90000,256));changed={0x11,0xc,0xe,0x3e,0x12,0x13,0x19,0x3c}
   assert all(after[i]==before[i] for i in range(256) if i not in changed)
   return ' '.join(str(after[i]) for i in (0x11,0xc,0xe,0x3e,0x12,0x13,0x19,0x3c))
  value=self.u.reg_read(UC_X86_REG_SI);return f'{int(self.started)} {value if value<32768 else value-65536}'
class OpFade(OpBase):
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16)
  if pair[0]==0 and 0x666<=pair[1]<0x6a3:return
  if pair==(0,0x2648):self.ticks+=1;return_to_caller(u);return
  if pair==(0,0x1de0):self.tones.append((self.ticks,self.read(0x586,'H')[0]));return_to_caller(u);return
  raise ValueError(f'unexpected OP blackout {pair}')
 def run(self):
  self.error=None;self.ticks=0;self.tones=[]
  for reg,value in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,value)
  self.u.mem_write(0x7e000,struct.pack('<HHH',0xff00,self.load,1));self.u.emu_start(self.load*16+0x666,self.load*16+0xff00,count=2000)
  if self.error:raise self.error
  assert self.u.reg_read(UC_X86_REG_SP)==0xe006
  return [f'{i} {tone}' for i,tone in self.tones]+[f'END {self.ticks}']
class Init(Hud):
 def body(self,u,address,size,unused):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  if pair==(0xaaf,0x3e0):
   r=bytearray(u.mem_read(0x90000,256));stages=[3,0,2,1];r[0x3e]=self.number;r[0x3c]=stages[self.number-1]
   r[0x13]=48+r[0x3c];r[0xe]=3;r[0x19]=int(self.number>=3);r[0x49]=0;u.mem_write(0x90000,bytes(r))
  if pair[0]==0xaaf and 0x8fe<=pair[1]<0x949:return
  if pair==(0,0x2578):assert words(1)==(8000,);u.reg_write(UC_X86_REG_AX,0x9200);return_to_caller(u,2);return
  if pair==(0,0xf14):
   off,seg=words(2);name=bytes(u.mem_read(seg*16+off,10))
   if name==f'DEMO{self.number}.REC\0'.encode():self.demo_open=True;return_to_caller(u,4);return
  if pair==(0,0xe60) and self.demo_open:
   assert words(3)==(8000,0,0x9200);u.mem_write(0x92000,self.replay);u.reg_write(UC_X86_REG_AX,8000);return_to_caller(u,6);return
  if pair==(0,0xdf4) and self.demo_open:self.demo_open=False;return_to_caller(u);return
  super().body(u,address,size,unused)
 def run(self,number,rank,seed,present,data,replay):
  self.number=number;self.demo_open=False;self.replay=replay
  fields,observation=self.initialize(int(number in (2,4)),rank,seed,present,data)
  assert not self.demo_open and bytes(self.u.mem_read(0x92000,8000))==replay
  r=bytes(self.u.mem_read(0x90000,256));prefix=[self.read(0x4348,'B')[0],self.read(0x53a0,'B')[0],self.read(0x4664,'B')[0],self.read(0x5395,'B')[0],r[0x11],r[0x13],r[0xf],r[0x49]]
  return ' '.join(map(str,prefix))+' '+fields,observation

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','op-target','op-decoded-dir','hdi','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
 target=a.target.read_bytes();assert len(target)==156258 and sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
 assert len(a.op_target.read_bytes())==42290 and sha(a.op_target.read_bytes())==PACKED
 assert sha(a.hdi.read_bytes())=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
 assets=main_assets(a.hdi);replays=[assets[f'DEMO{i}.REC'] for i in range(1,5)];private=out/'replays';private.mkdir()
 for i,b in enumerate(replays,1):assert len(b)==8000;(private/f'DEMO{i}.REC').write_bytes(b)
 cases=[(n,f,0,1) for n in range(1,5) for f in range(4000)]
 cases += list(itertools.product(range(1,5),(0,1,3995,3996,4000,65535),(1,16,32,256,4096,8192,16384,65535),(0,1,255)))
 idle=list(itertools.product((0,1,639,640,641,32767,32768,65535),(0,1),(0,1,16,32,12,65535)))
 codec=Score(target,0x1000);codec.run((2,318,0,0,0,1,0,bytes(196),b'',bytes(8)));baseline=bytes(codec.file)
 init=[]
 for number,rank,seed,variant in itertools.product(range(1,5),(0,3),(0,1,318,640),range(3)):
  data=bytearray(baseline);present=1
  if variant==1:data[(int(number in (2,4))*5+2)*196+2]^=1
  if variant==2:data=bytearray();present=0
  init.append((number,rank,seed,present,bytes(data)))
 fixture_map={'replay':cases,'idle':idle,'op':[(i,) for i in range(5)],'fade':[(1,),(10,)],'init':init};records={};details=[]
 if a.reference_dir:
  previous=json.loads((a.reference_dir/'receipt.json').read_text());assert previous['passed']
 for mode,values in fixture_map.items():
  f=out/(mode+'.txt');f.write_text(''.join(' '.join(b.hex() or '-' if isinstance(b,bytes) else str(b) for b in row)+'\n' for row in values))
  cmd=[str(a.exe.resolve()),'--'+mode,str(f)];
  if mode=='replay':cmd.append(str(private))
  if mode=='init':cmd.append(str(out/'native-saves'))
  native=subprocess.run(cmd,capture_output=True,check=True).stdout;(out/(mode+'-native.txt')).write_bytes(native)
  if a.reference_dir:expected=(a.reference_dir/(mode+'-original.txt')).read_bytes()
  else:
   answers=[]
   for load in (0x1000,0x2000):
    if mode=='replay':o=Replay(target,load);lines=[o.sample(replays[n-1],f,k,s) for n,f,k,s in values]
    elif mode in ('idle','op'):
     o=Op(a.op_target,a.op_decoded_dir,load);lines=[o.run('rotation',*row) if mode=='op' else o.run('idle',*row) for row in values]
    elif mode=='init':
     o=Init(target,load);lines=[]
     for n,r,s,p,b in values:line,detail=o.run(n,r,s,p,b,replays[n-1]);lines.append(line);details.append(dict(load=f'{load:04x}',number=n,rank=r,seed=s,present=p,**detail))
    else:
     o=Replay(target,load);o.sample(replays[0],3996,0,0)
     lines=OpFade(a.op_target,a.op_decoded_dir,load).run()+[f'{i} {tone}' for i,tone in o.tones]+[f'END {o.ticks}']
    data=('\n'.join(lines)+'\n').encode();answers.append(data)
   assert answers[0]==answers[1];expected=answers[0]
  (out/(mode+'-original.txt')).write_bytes(expected)
  if a.reference_dir:
   assert sha(expected)==previous['records'][mode]['trace_sha256'] and sha(f.read_bytes())==previous['records'][mode]['fixture_sha256']
  if native!=expected:
   index=next(i for i,(x,y) in enumerate(zip(native.splitlines(),expected.splitlines())) if x!=y)
   (out/'mismatch.json').write_text(json.dumps(dict(mode=mode,line=index,native=native.splitlines()[index].decode(),original=expected.splitlines()[index].decode()),indent=2)+'\n');raise ValueError(f'demo {mode} differs at line{index}')
  records[mode]=dict(cases=len(values),fixture_sha256=sha(f.read_bytes()),trace_sha256=sha(expected));print('demo',mode,'PASS',len(values),flush=True)
 assert source_manifest(root)[0]==manifest;(out/'startup-observations.json').write_text(json.dumps(details,indent=2)+'\n')
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,verifier_sha256=sha(Path(__file__).read_bytes()),exe_sha256=sha(a.exe.read_bytes()),main_sha256=sha(target),op_sha256=sha(a.op_target.read_bytes()),replays={f'DEMO{i}.REC':sha(b) for i,b in enumerate(replays,1)},loads=['1000','2000'],original_cpu_reexecuted=not bool(a.reference_dir),reference_dir=str(a.reference_dir) if a.reference_dir else None,records=records,scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
