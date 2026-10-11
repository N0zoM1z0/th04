#!/usr/bin/env python3
"""Original MAINE fade/delay/input functions against shared elapsed Animation.

Original instructions execute unchanged. Counter changes use independently
computed ideal IRQ stimuli; palette-show and keyboard calls are guarded
observation adapters. Physical CPU/I-O latency is not inferred.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest()
HZ=2631575;H=106;V=440;R=407
PINS={0x622:(130,'19e015ce0dfae0670711db894ccddad7142328054b3495967b70cdf1529f1f4b'),0xcca3:(21,'0d77d41527daea4e009dcbcdbf7fb8fc956243a9cc04dfd9dc2a289468243d2b'),0xce7a:(86,'3a73aea1528421db6658b8419aa06f4313b6341b968ffd9c1a043db8ed6964cf'),0x2206:(38,'122568ac75a194b3118dd40772ae4e55352102a549344ffb08f2b3e3c53b21d0')}
def edge(n):return ((n*V+R)*H*1000000000+HZ-1)//HZ
def edges(now):return max(0,(now*HZ-R*H*1000000000)//(V*H*1000000000)+1)
def held(profile,now):
 n=edges(now)%16
 return 0x20 if (n<5 or n>=10) and profile==1 or profile==2 and n!=6 else 0
class Original:
 def __init__(self,record,load,row):
  inc,seed,phase,speed,delay,budget,profile,horizon,chunk=row;self.inc=inc;self.profile=profile;self.now=phase;self.end=phase+horizon;self.lines=[];self.blocked=False;self.stage=1;self.polls=0;self.done=False;self.errors=[];self.op=''
  body=bytearray(record['body'])
  for at,(size,pin) in PINS.items():assert sha(body[at:at+size])==pin
  for at in record['sites']:struct.pack_into('<H',body,at,(struct.unpack_from('<H',body,at)[0]+load)&65535)
  self.load=load;self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000);self.u.mem_write(load*16,bytes(body));self.base=(load+record['dg'])*16
  n=seed+edges(phase);count=n-(n*inc)//65536
  for at,value in ((0xefa,count),(0xefc,count),(0xf02,n*inc),(0x400,inc),(0x132,31)):self.write(at,value)
  self.u.mem_write(self.base+0x402,b'\xfb');self.u.hook_add(unicorn.UC_HOOK_CODE,self.code)
 def read(self,at):return struct.unpack('<H',self.u.mem_read(self.base+at,2))[0]
 def write(self,at,value):self.u.mem_write(self.base+at,struct.pack('<H',value&65535))
 def advance(self,now):
  n=edges(now)-edges(self.now);total=self.read(0xf02)+n*self.inc;count=n-total//65536
  self.write(0xefa,self.read(0xefa)+count);self.write(0xefc,self.read(0xefc)+count);self.write(0xf02,total);self.now=now
 def pulse(self,needed):
  if not needed:return
  n=((needed-1)*65536+self.read(0xf02))//(65536-self.inc)+1;at=edge(edges(self.now)+n-1)
  if at>self.end:self.advance(self.end);self.blocked=True;self.u.emu_stop()
  else:self.advance(at)
 def return_far(self):
  u=self.u;sp=u.reg_read(UC_X86_REG_SP);ip,cs=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4);u.reg_write(UC_X86_REG_CS,cs);u.reg_write(UC_X86_REG_IP,ip)
 def code(self,u,address,size,_):
  try:
   at=address-self.load*16
   if at==0x60000-self.load*16:self.done=True;u.emu_stop();return
   if at==0xcca3:
    sp=u.reg_read(UC_X86_REG_SP);self.minimum=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];self.polls=0
   elif at==0xccac:
    if self.polls:self.pulse(max(0,self.minimum-self.read(0xefa)))
    self.polls+=1
   elif at==0x2206:self.polls=0
   elif at==0x2225:
    if self.polls:self.pulse(1)
    self.polls+=1
   elif at==0x19ec:
    self.lines.append(f'P {self.now} {self.read(0x132)}');self.return_far()
   elif at in (0xd48a,0xd492): # 0CC7:081A input_reset_sense / :0822 input_sense
    value=held(self.profile,self.now);self.lines.append(f'K {self.now} {value}')
    self.write(0x1b42,value if at==0xd48a else self.read(0x1b42)|value);self.return_far()
   elif at==0xce84:self.stage=2 # release loop 0CC7:0214
   elif at==0xcea5:self.stage=3 # press loop 0CC7:0235
  except BaseException as e:self.errors.append(repr(e));u.emu_stop()
 def call(self,kind,argument,direction=0):
  self.op=kind;self.stage=1;self.done=False
  if kind=='F':seg=0;off=0x622 if direction else 0x666;event=(8,0,direction,argument)
  elif kind=='D':seg=0xcc7;off=0x33;event=(15,argument,0,0)
  else:seg=0xcc7;off=0x20a;event=(16,argument,0,0)
  self.lines.append(' '.join(map(str,('E',self.now,*event))))
  u=self.u
  for reg,value in ((UC_X86_REG_CS,self.load+seg),(UC_X86_REG_DS,self.base//16),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x4321),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
  u.mem_write(0x7f000,struct.pack('<HHH',0,0x6000,argument&65535));u.emu_start((self.load+seg)*16+off,0x10ffff,count=2000000)
  assert not self.errors and (self.done or self.blocked),(kind,self.errors,self.now)
  if self.done:assert u.reg_read(UC_X86_REG_SP)==0xf006 and u.reg_read(UC_X86_REG_BP)==0x4321
 def run(self,row):
  inc,seed,phase,speed,delay,budget,profile,horizon,chunk=row
  for kind,arg,dir in (('F',speed,1),('D',delay,0),('W',budget,0),('F',0,0)):
   self.call(kind,arg,dir)
   if self.blocked:break
  if not self.blocked:self.lines.append(f'E {self.now} 9 99 0 0')
  self.lines.append(f'STOP {self.now} {self.end-self.now} {self.stage if self.blocked else 4} {self.read(0xefa)} {self.read(0xefc)} {self.read(0xf02)}')
  return self.lines
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--reference',type=Path);a=p.parse_args();sys.path.insert(0,str(a.root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original
 record=original('maine');rows=[(inc,seed,0,speed,delay,budget,profile,2000000000,0) for inc,seed,speed,delay,budget,profile in itertools.product((0,13311),(0,65535),(0,2),(0,1),(-1,0,1,3,9999,32768),(0,1,2))];expected=[]
 if a.reference:
  j=json.loads((a.reference/'receipt.json').read_text());assert j['passed'] and j['original']==record['pins'] and j['rows']==[list(r) for r in rows] and j['oracle_sha256']==sha(Path(__file__).read_bytes())
  for name,pin in j['files'].items():assert sha((a.reference/name).read_bytes())==pin
  wanted=(a.reference/'expected.txt').read_bytes()
 else:
  for load in (0x1000,0x3333):
   lines=[]
   for i,row in enumerate(rows):lines.extend([f'CASE {i}',*Original(record,load,row).run(row)])
   expected.append(('\n'.join(lines)+'\n').encode());print('Original MAINE elapsed',hex(load),len(rows),'PASS',flush=True)
  assert expected[0]==expected[1];wanted=expected[0]
 a.output.mkdir(parents=True,exist_ok=False);v=a.output/'vectors.txt';v.write_text(''.join(' '.join(map(str,row))+'\n' for row in rows));run=subprocess.run([str(a.native.resolve()),'--vectors',str(v.resolve())],capture_output=True)
 (a.output/'native.txt').write_bytes(run.stdout);(a.output/'expected.txt').write_bytes(wanted);(a.output/'stderr.txt').write_bytes(run.stderr)
 assert run.returncode==0 and not run.stderr and run.stdout==wanted,'native/original elapsed trace differs'
 fine=a.output/'fine-vectors.txt';fine.write_text(''.join(' '.join(map(str,(*row[:-1],1000000)))+'\n' for row in rows));split=subprocess.run([str(a.native.resolve()),'--vectors',str(fine.resolve())],capture_output=True);(a.output/'fine-native.txt').write_bytes(split.stdout);assert split.returncode==0 and not split.stderr and split.stdout==wanted,'elapsed partition changes trace'
 receipt=dict(passed=True,original=record['pins'],rows=rows,original_cases=len(rows)*2,native_vectors=len(rows),partition_vectors=len(rows),native_sha256=sha(a.native.read_bytes()),oracle_sha256=sha(Path(__file__).read_bytes()),files={q.name:sha(q.read_bytes()) for q in a.output.iterdir()},scope=__doc__)
 (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('MAINE elapsed PASS',len(rows)*2,'original cases',len(rows),'coarse/fine vectors',flush=True)
if __name__=='__main__':main()
