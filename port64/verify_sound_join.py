#!/usr/bin/env python3
"""Muted MAIN ordered SE frontend versus actual original MAIN controller.

MAIN 130E:07C6/07D2/080C executes at two MZ load segments. File/probe,
component emitters and process lifecycle are explicit seams. A guarded raw
0AAF:0098..0212 loop independently checks wait/page/SE/counter/score order.
Offline PIT samples use original OP library instructions as a representative
beeper Oracle; this does not claim original MAIN library/runtime equivalence,
physical refresh/audio, FM synthesis, all OP/MAINE sound, or whole-game parity.
"""
import argparse,hashlib,json,os,struct,subprocess,unicorn
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_player_lifecycle import Original as MainBase
from verify_beeper import Original as BeepOriginal
from verify_cutscene import ending_assets
from verify import source_manifest,require_elf_x86_64
sha=lambda b:hashlib.sha256(b).hexdigest()
class MainControl(MainBase):
 def __init__(self,target,load):
  super().__init__(target,load);self.requests=[];self.error=None
  self.u.hook_add(unicorn.UC_HOOK_INTR,self.interrupt)
  self.write(0x8f4,'B',2);self.write(0x914,'BB',255,0)
 def interrupt(self,u,n,unused):
  if n!=0x60:self.error=ValueError('unexpected MAIN sound INT');u.emu_stop();return
  self.requests.append(('int',u.reg_read(UC_X86_REG_AX)))
 def body(self,u,address,size,unused):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
  if pair[0]==0x130e and 0x7c6<=pair[1]<0x858:return
  if pair==(0,0x3caa):
   value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];self.requests.append(('beep',value))
   ret,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+6);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,ret);return
  raise ValueError(f'unexpected original MAIN sound {pair}')
 def invoke(self,ip,arg=None):
  self.error=None;u=self.u;cs=self.load+0x130e
  for reg,v in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,0x202)]:u.reg_write(reg,v)
  values=(0xff00,cs) if arg is None else (0xff00,cs,arg)
  u.mem_write(0x7f000,struct.pack('<'+'H'*len(values),*values));u.emu_start(cs*16+ip,cs*16+0xff00,count=10000)
  if self.error:raise self.error
  assert u.reg_read(UC_X86_REG_IP)==0xff00 and u.reg_read(UC_X86_REG_SP)==0xf000+len(values)*2
 def action(self,kind,value):
  self.requests=[]
  if kind==0:self.invoke(0x7d2,value)
  elif kind==1:self.invoke(0x80c)
  elif kind==2:self.invoke(0x7c6);self.invoke(0x7d2,value);self.invoke(0x80c)
  elif kind not in (3,4):raise ValueError('unreviewed MAIN sound action')
  return list(self.requests)
 def state(self):return self.read(0x8f4,'B')[0],*self.read(0x914,'BB')
class MainLoop(MainControl):
 def __init__(self,target,load):
  super().__init__(target,load);self.loop=False;self.events=[];self.frames=0
 def body(self,u,address,size,unused):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);ip=pair[1]
  if not self.loop or pair[0]!=0xaaf:return super().body(u,address,size,unused)
  if not 0x98<=ip<0x213:raise ValueError('raw MAIN loop left guarded extent')
  data=bytes(u.mem_read(address,size))
  if ip==0x1a3:
   self.events.append(('update',self.read(0x538a,'H')[0],self.state()));return
  if ip==0x204:
   self.events.append(('score',self.read(0x538a,'H')[0],self.state()))
   # Guarded score emitter queues an extend at its observed call boundary.
   # Actual score arithmetic and actual snd_se_play are tested separately.
   self.write(0x914,'BB',7,0);self.frames+=1
   if self.frames==2:self.write(0x5392,'B',1)
  # Other callees are named callback seams; execute the original loop body,
  # counters, page OUTs and real SE controller, never patch target bytes.
  if data[0] in (0xe8,0x9a) or (data[0]==0xff and data[1] in (0x16,0x1e)):
   u.reg_write(UC_X86_REG_IP,ip+size)
   if data[0]==0x9a and ip==0xa4:u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
   if ip==0x1ff:u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+4)
 def page(self,u,port,size,value,unused):
  assert port in (0x7c,0xa6,0xa4) and size==1
  if port in (0xa6,0xa4):self.events.append(('page',port,value))
 def run(self,start,se):
  self.loop=True;self.events=[];self.frames=0;self.write(0x538a,'H',start);self.write(0x5392,'B',0);self.write(0x8f4,'B',se);self.write(0x914,'BB',1,0)
  self.write(0xba86,'HH',0,0x9000);self.u.mem_write(0x90000,bytes(256));self.u.mem_write(0x9000b,b'\x03')
  hook=self.u.hook_add(unicorn.UC_HOOK_INSN,self.page,None,1,0,UC_X86_INS_OUT)
  self.error=None;self.call(0x98,cs=self.load+0xaaf);self.u.hook_del(hook)
  if self.error:raise self.error
  names=[e[0] for e in self.events];assert names==['page','page','update','score']*2
  pairs=[e for e in self.events if e[0] in ('update','score')]
  assert [e[1] for e in pairs]==[start,(start+1)&65535,(start+1)&65535,(start+2)&65535]
  if se==2:assert self.requests==[('beep',1),('beep',7)]
  if se==1:assert self.requests==[('int',0xc01),('int',0xc07)]
  if se==0:assert self.requests==[]
  self.loop=False;return self.events
class Pcm:
 def __init__(self,o,efs):
  self.o=o;o.begin(0);assert o.load_file(efs)==0
  self.fraction=0;self.time=0;self.reload_time=0;self.generation=o.reloads;self.next_irq=2458*48000;self.count=0;self.samples=bytearray()
 def advance(self,ns):
  n,self.fraction=divmod(self.fraction+ns*48000,1000000000)
  if self.generation!=self.o.reloads:self.generation=self.o.reloads;self.reload_time=self.time
  for _ in range(n):
   self.time+=2457600
   while self.next_irq<=self.time:
    self.o.invoke(0x381e,irq=True)
    if self.generation!=self.o.reloads:self.generation=self.o.reloads;self.reload_time=self.next_irq
    self.next_irq+=self.o.read(0x954,'H')[0]*48000
   value=0 if not self.o.gate else 8192 if (self.time-self.reload_time)%(self.o.divisor*48000)<((self.o.divisor+1)//2)*48000 else -8192
   self.samples+=struct.pack('<h',value)
  self.count+=n
 def state(self):return self.count,self.o.read(0x962,'H')[0],self.o.read(0x9b2,'H')[0],self.o.read(0x9ae,'H')[0]
def compare_control(original,actions,states,pcm=None):
 pending=0;clock=0;observed=[]
 actual={int(row.split()[0]):list(map(int,row.split()[2:])) for row in states.splitlines()}
 assert actual[0]==[2,255,0,0,0,0,0]
 for row in actions.splitlines():
  c,kind,value,name=row.split();c=int(c);value=int(value)
  if kind=='T':assert not pending;pending=value;clock=c;continue
  if kind=='E':
   if pcm and pending:pcm.advance(pending)
   pending=0;s=list(original.state());expected=actual[c]
   assert s==expected[:3],('MAIN control',c,s,expected)
   if pcm:assert list(pcm.state())==expected[3:],('OP representative beeper',c,pcm.state(),expected)
   observed.append([c,*s]);continue
  kind=int(kind)
  if kind==1:
   if pcm and pending:pcm.advance(pending)
   pending=0
  for k,v in original.action(kind,value):
   if k=='beep' and pcm:assert pcm.o.invoke(0x3a64,(v,))==0
  assert c<=clock or clock==0
 assert clock==700 and not pending;return observed

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--exe',type=Path,required=True);p.add_argument('--target',type=Path,required=True);p.add_argument('--op',type=Path,required=True);p.add_argument('--decoded',type=Path,required=True);p.add_argument('--hdi',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--reference-dir',type=Path);a=p.parse_args()
 root=a.root.resolve();manifest,files=source_manifest(root);out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
 require_elf_x86_64(a.exe);target=a.target.read_bytes();efs=ending_assets(a.hdi)['MIKO.EFS'];assert len(efs)==8284 and sha(efs)=='12045fed57d7c5a07da0047ae13c6607cbc78155cfbf5baa719fc310131de607'
 env=os.environ.copy();env['SDL_AUDIODRIVER']='dummy'
 subprocess.run([str(a.exe.resolve()),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font.resolve()),'--sound-checks',str(out/'frontend'),'--mute'],check=True,env=env,stdout=(out/'launch.log').open('wb'),stderr=subprocess.STDOUT)
 cases=sorted((out/'frontend').glob('c*-paint0'));assert len(cases)==6
 loop=[];controls=[];refs={};samples=0
 if a.reference_dir:
  reference=json.loads((a.reference_dir/'receipt.json').read_text());assert reference['passed'] and reference['original_cpu_reexecuted'] and reference['target_sha256']==sha(target) and reference['efs_sha256']==sha(efs) and reference['source_manifest']==manifest
 else:
  for load in (0x1000,0x2000):
   for start in (0,999,65535):
    for se in (0,1,2):
     loop.append({'load':load,'start':start,'se':se,'events':MainLoop(target,load).run(start,se)})
  (out/'loop.json').write_text(json.dumps(loop,indent=2)+'\n')
 for case in cases:
  actions=(case/'actions.txt').read_text();states=(case/'states.txt').read_text();wave=(case/'samples.pcm').read_bytes();name=case.name
  painted=case.with_name(name.replace('paint0','paint1'))
  for filename in ('actions.txt','states.txt','samples.pcm'):assert (case/filename).read_bytes()==(painted/filename).read_bytes(),('repaint partition',name,filename)
  if a.reference_dir:
   for filename in ('actions.txt','states.txt','samples.pcm'):assert (case/filename).read_bytes()==(a.reference_dir/'frontend'/name/filename).read_bytes()
   expect=(a.reference_dir/f'{name}.pcm').read_bytes();assert sha(expect)==reference['cases'][name]['reference_pcm_sha256']
  else:
   histories=[compare_control(MainControl(target,load),actions,states) for load in (0x1000,0x2000)];assert histories[0]==histories[1]
   pcm=Pcm(BeepOriginal(a.op,a.decoded,0x2000),efs);observed=compare_control(MainControl(target,0x2000),actions,states,pcm)
   expect=bytes(pcm.samples);(out/f'{name}.pcm').write_bytes(expect);controls.append([name,observed])
  assert wave==expect,('independent sample comparison',name);samples+=len(wave)//2
  refs[name]={'samples':len(wave)//2,'reference_pcm_sha256':sha(expect),'actions_sha256':sha(actions.encode()),'states_sha256':sha(states.encode())}
  print('MAIN sound/PIT representative/repaint PASS',name,len(wave)//2,'samples',flush=True)
 if not a.reference_dir:(out/'controls.json').write_text(json.dumps(controls)+'\n')
 assert source_manifest(root)[0]==manifest
 receipt={'passed':True,'utc':datetime.now(timezone.utc).isoformat(),'source_manifest':manifest,'source_files':len(files),'exe_sha256':sha(a.exe.read_bytes()),'target_sha256':sha(target),'hdi_sha256':sha(a.hdi.read_bytes()),'efs_sha256':sha(efs),'cases':refs,'compared_samples':samples,'original_cpu_reexecuted':not bool(a.reference_dir),'loop_cases':18 if not a.reference_dir else reference['loop_cases'],'reference_receipt_sha256':sha((a.reference_dir/'receipt.json').read_bytes()) if a.reference_dir else None,'unicorn_version':unicorn.__version__,'engine_sha256':sha(Path(unicorn.unicorn._uc._name).read_bytes()),'scope':__doc__}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('sound join PASS',samples,'samples')
if __name__=='__main__':main()
