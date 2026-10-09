#!/usr/bin/env python3
"""Original Mugetsu-to-Gengetsu second-dialog return at two relocated loads.

MAIN13A9:ACB3..AE0A and A4D1..A517 execute; dialog, BB/CDG and clean
consumers are request adapters. All boss fields, pools, shared wave/Bomb state,
column padding and laser bytes compare with native prepare_after_dialog.
This is the handoff component, not original full MAIN or complete Extra.
"""
import sys,struct,hashlib,json,itertools
from pathlib import Path
from verify_extra_dialog import Original as Base
from unicorn.x86_const import *
class Original(Base):
 def __init__(self,target,load):
  self.requests=[];super().__init__(target,load)
 def body(self,u,address,size):
  actual=u.reg_read(UC_X86_REG_CS);pair=(actual+self.delta,address-actual*16);sp=u.reg_read(UC_X86_REG_SP)
  def ret(far,args=0):
   words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2));u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args)
   if far:u.reg_write(UC_X86_REG_CS,words[1])
   u.reg_write(UC_X86_REG_IP,words[0])
  if pair==(0x2000,0x2b4e):
   end,start=struct.unpack('<HH',u.mem_read(0x70000+sp+4,4));self.requests.append(['clean',start,end]);ret(True,4);return
  if pair==(0x2aaf,0x2bfb):self.requests.append(['dialog']);ret(True);return
  if pair==(0x33a9,0xa544):self.requests.append(['bb_free']);ret(True);return
  if pair==(0x33a9,0xa518):
   off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp+2,4));self.requests.append(['bb_load',bytes(u.mem_read(seg*16+off,32)).split(b'\0')[0].decode()]);ret(False,4);return
  if pair==(0x33a9,0x9e06):self.requests.append(['all_clear']);ret(False);return
  if pair==(0x2aaf,0xd1f):self.requests.append(['end_extra']);ret(True);return
  if pair[0]==0x330e and pair[1] in (0x978,0x858):
   self.requests.append(['cdg_free',struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]] if pair[1]==0x978 else ['cdg_load'])
  super().body(u,address,size)

import argparse,subprocess
from datetime import datetime,timezone
from verify_gengetsu import initialize,checkpoint,fixture
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixtures():
 for marker in range(256):
  row=fixture('D',phase=255,clock=0,mode=marker,amplitude=marker,inv=marker,damage=0,sprite=marker,hp=marker*257-32768,end=32767-marker*127)
  row[9:33]=[(marker+i*73)&255 for i in range(24)];row[24]=255;row[25:27]=[0,0]
  row[33]=0
  yield row

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0]
 target=a.target.read_bytes();assert len(target)==156258 and sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
 rows=list(fixtures());path=out/'fixtures.txt';path.write_text('\n'.join(' '.join(map(str,row)) for row in rows)+'\n')
 native=subprocess.run([str(a.exe.resolve()),'--vectors',str(path)],capture_output=True,text=True,check=True).stdout.splitlines();first=None;controls=[]
 class Rejecting(Original):
  def body(self,u,address,size):raise ValueError('injected Extra handoff rejection')
 for load in (0x1000,0x2000):
  bad=Rejecting(target,load)
  try:bad.call_args(0xacb3)
  except RuntimeError as e:assert isinstance(e.__cause__,ValueError)
  else:raise ValueError('handoff callback rejection swallowed')
  o=Original(target,load);expected=[]
  for i,row in enumerate(rows):
   initialize(o,row);o.write(0x4298,'B',17);o.write(0x42a8,'B',31);o.events=[];o.resources=[];o.requests=[];o.call_args(0xacb3)
   line=checkpoint(o,0,row[51]);expected.append(line)
   assert line.split()==native[i].split(),f'handoff case{i} load{load:04x} differs'
   assert o.requests==[['clean',128,256],['dialog'],['cdg_free',16],['bb_free'],['cdg_load'],['bb_load','st06b.bb']],o.requests
   assert o.resources==[(0,16,'-',0),(2,16,'st06bk2.cdg',0)],o.resources
   callbacks=o.read(0x4268,'H')+o.read(0xbcd0,'3H')
   assert callbacks==(0x7e89,0xc7da,load+0x13a9,0x846f)
  assert first is None or expected==first,'handoff depends on load';first=expected
  trace='\n'.join(expected)+'\n';(out/f'original-{load:04x}.txt').write_text(trace)
  controls.append(dict(load=f'{load:04x}',cases=len(expected),trace_sha256=sha(trace.encode())))
 assert source_manifest(root)[0]==manifest
 r=dict(passed=True,cases=len(rows),loads=controls,source_manifest=manifest,target_sha256=sha(target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(path.read_bytes()),callback_rejection_passed=True,utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('Extra handoff: PASS256cases at loads1000/2000')
if __name__=='__main__':main()
