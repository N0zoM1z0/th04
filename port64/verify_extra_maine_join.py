#!/usr/bin/env python3
"""Original outgoing Extra MAIN and MAINE caller order for live native scenes.

Original end_extra/fade16/GameExecl publication execute at two loads with
captured native outgoing state. Resource/EMS/sound/palette/VBlank/exec are
explicit adapters; execl takes a failure return solely for ABI inspection.
Decoded MAINE _main selects CONG04/14 and orders delay/register/congratulations/
verdict/fade4/OP. Child durations are native adapters; its fades/key loops are
separate retained component evidence. No original complete MAIN/child pixels,
natural survival, actual Windows, audio/timing or exact acceptance follows.
"""
import argparse,hashlib,itertools,json,struct
from pathlib import Path
from datetime import datetime,timezone
from unicorn.x86_const import *
from verify_maine_join import Main as MainBase,FIELDS,RELEASES,return_to_caller
from verify_extra import LegacyView,Original as Relocated
from verify_congratulations import Original as MaineBase,MAIN_SHA
from verify_cutscene import PACKED_SHA,PAYLOAD_SHA
from verify import source_manifest
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class MainOriginal(MainBase):
 def __init__(self,target,load):
  self.delta=0x2000-load;super().__init__(target)
  if self.delta:
   at=struct.unpack_from('<H',target,24)[0]
   for i in range(1136):
    off,seg=struct.unpack_from('<HH',target,at+4*i);site=seg*16+off
    struct.pack_into('<H',self.module,site,(struct.unpack_from('<H',self.module,site)[0]-self.delta)&65535)
   self.u.mem_write(load*16,bytes(self.module))
 call_args=Relocated.call_args
 def control(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs+self.delta,address-cs*16);view=LegacyView(u,self.delta)
  if pair[0]==0x2aaf and 0xd1f<=pair[1]<0xd45:return
  if pair==(0x330e,0x2fc):
   sp=u.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]==0x204
   assert bytes(u.mem_read(0x90030,1))==b'\xfd' and bytes(u.mem_read(0x90025,1))==bytes([self.endtype])
   self.calls.append('song-fade4');return_to_caller(view,2);return
  MainBase.control(self,view,address+self.delta*16)
 def outgoing(self,values):
  endtype,*data=values;counts=data[:7];slow,total,pending=data[7:10];digits=data[10:];assert len(digits)==8
  self.reset();self.error=None;self.calls=[];self.fade=[];self.ticks=0;self.ems=0;self.bad=False;self.endtype=endtype;self.digits=bytes(digits)
  self.expected=[253,endtype,*counts,slow,total,*digits,pending]
  self.u.mem_write(0x90000,b'\xa5'*256);self.u.mem_write(0x90025,bytes([endtype]));self.write(0xba86,'HH',0,0x9000)
  self.write(0x539e,'H',0);self.write(0x435a,'I',pending);self.u.mem_write(0x84349,self.digits)
  for (at,_),value in zip(FIELDS,counts):self.write(at,'H',value)
  self.write(0x1860,'II',slow,total);self.write(0x3a4,'h',100)
  self.call_args(0xd1f,far=True,cs=0x2aaf)
  assert self.published()==self.expected and self.ticks==273 and self.fade[-1]=='273 0'
  assert self.calls==['song-fade4']+[v[0] for v in RELEASES.values()]+['execl']
  return dict(published=self.published(),ticks=self.ticks,fade=self.fade,calls=self.calls)
class MaineOriginal(MaineBase):
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16)
  if pair==(0xa05,0x20a8):self.clock+=self.child_ticks[1]
  if pair==(0xcc7,0xf5):self.flow.extend([['tone0',self.clock],['congratulations',self.clock]])
  super().body(u,address)
  if pair==(0xcc7,0x33):self.clock+=100
  if pair==(0xa05,0x27c4):self.clock+=self.child_ticks[0]
  if pair==(0xa05,0x20a8):self.clock+=self.child_ticks[2]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('main-target','maine-target','decoded-dir','frontend-dir','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0]
 target=a.main_target.read_bytes();assert len(target)==156258 and hashlib.sha256(target).hexdigest()=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
 rows=[];first=None
 for load in (0x1000,0x2000):
  main_o=MainOriginal(target,load);group=[]
  for character,shot,paint in itertools.product(range(2),repeat=3):
   name=f'{character}-{shot}-1-{paint}';lines=(a.frontend_dir/(name+'.txt')).read_text().splitlines()
   outgoing=list(map(int,next(l for l in lines if l.startswith('outgoing_extra ')).split()[1:]));published=main_o.outgoing(outgoing)
   fade=dict(tuple(map(int,l.split()[1:])) for l in lines if l.startswith('mainfade '))
   for line in published['fade']:
    tick,tone=map(int,line.split());assert fade[tick]==tone
   flow=[list(map(int,l.split()[1:])) for l in lines if l.startswith('extra_flow ')];assert [k for k,t in flow]==list(range(10))
   assert flow[2][1]==flow[3][1]==273 and flow[4][1]==373
   m=MaineOriginal(a.maine_target,a.decoded_dir,load)
   m.child_ticks=[flow[5][1]-flow[4][1],flow[7][1]-flow[6][1],flow[8][1]-flow[7][1]];assert min(m.child_ticks)>0
   events=m.run(character,1,253,clock=False)
   labels=['delay100','register','tone0','congratulations','verdict','sound_fade4','exec_op']
   wanted=[[label,flow[i][1]-273] for label,i in zip(labels,range(3,10))];assert m.flow==wanted,(name,m.flow,wanted)
   pictures=[bytes.fromhex(l.split()[-1]).decode('ascii') for l in events if l.startswith('pi_load ')];assert pictures==[f'CONG{character}4.pi']
   group.append(dict(scene=name,outgoing=outgoing,main=published,maine_flow=m.flow,maine_events=events,child_duration_adapters=m.child_ticks))
  assert first is None or group==first;first=group;rows.append(dict(load=f'{load:04x}',cases=group))
 assert source_manifest(root)[0]==manifest
 path=out/'original.json';path.write_text(json.dumps(rows,indent=2)+'\n')
 r=dict(passed=True,source_manifest=manifest,scenes=8,loads=['1000','2000'],main_target_sha256=sha(a.main_target),maine_target_sha256=sha(a.maine_target),payload_sha256=PAYLOAD_SHA,main_body_sha256=MAIN_SHA,original_sha256=sha(path),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('Original live Extra outgoing/MAINE caller join PASS8scenes at1000/2000')
if __name__=='__main__':main()
