#!/usr/bin/env python3
"""Original OP resident probes, modes, commands, SE arbitration and load requests.

Execute original bounded functions at two relocated loads. Interrupt replies,
DOS files and beeper calls are guarded adapters. This proves the control seam,
not PMD synthesis, audible playback, physical driver residency, full startup,
native frontend integration or DOS exactness. Unsupported DS table indices and
non-8.3 input names are explicitly excluded/rejected by the host owner.
"""
import argparse,hashlib,itertools,json,random,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD
from verify_maine_join import return_to_caller
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
 def __init__(self,*args):
  super().__init__(*args);self.u.hook_add(unicorn.UC_HOOK_INTR,self.interrupt)
 def emit(self,k,a=0,b=0,name='-'):self.events.append(f'{k} {a} {b} {name}')
 def string(self,seg,off):
  b=bytes(self.u.mem_read(seg*16+off,13));assert b'\0' in b;return b.split(b'\0')[0].decode('ascii')
 def interrupt(self,u,number,unused):
  try:
   ax=u.reg_read(UC_X86_REG_AX)
   if number in (0x60,0x61):
    self.emit('int',number,ax)
    if self.operation==0:
     assert number==0x60 and ax>>8==9;u.reg_write(UC_X86_REG_AX,self.action[5])
    elif self.operation==1:u.reg_write(UC_X86_REG_AX,self.action[3])
    elif self.operation==4:assert number==0x60 and ax>>8==12;u.reg_write(UC_X86_REG_AX,0xbeef)
    elif self.operation==5:
     if ax==0x100:assert not self.open;u.reg_write(UC_X86_REG_AX,0x9876)
     else:
      assert self.open and ax==self.action[1]
      assert number==(0x61 if ax>>8==6 and self.read(0x9e1,'B')[0]==3 else 0x60)
      u.reg_write(UC_X86_REG_DS,0x8000);u.reg_write(UC_X86_REG_DX,0x4000)
    else:raise ValueError('unexpected sound driver call')
   elif number==0x21:
    bx=u.reg_read(UC_X86_REG_BX)
    if ax==0x3d00:
     assert self.operation==5 and not self.open and u.reg_read(UC_X86_REG_DS)==self.ds
     self.emit('open',name=self.string(self.ds,u.reg_read(UC_X86_REG_DX)));self.open=True;u.reg_write(UC_X86_REG_AX,0x40)
    elif ax==0x3f00:
     assert self.open and bx==0x40 and u.reg_read(UC_X86_REG_CX)==0x5000
     assert (u.reg_read(UC_X86_REG_DS),u.reg_read(UC_X86_REG_DX))==(0x8000,0x4000)
     self.emit('read',0x5000);u.mem_write(0x84000,self.file);u.reg_write(UC_X86_REG_AX,len(self.file))
    else:
     assert ax>>8==0x3e and self.open and bx==0x40 and u.reg_read(UC_X86_REG_DS)==self.ds
     self.emit('close');self.open=False;u.reg_write(UC_X86_REG_AX,0)
   else:raise ValueError(f'unexpected interrupt {number}')
  except Exception as e:self.error=e;u.emu_stop()
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16)
  if pair==(0xda1,0xff00):self.done=True;u.emu_stop();return
  if pair[0]==0xda1 and any(a<=pair[1]<b for a,b in [(0x206,0x280),(0x2d4,0x36f),(0x3ba,0x4a2),(0x8d6,0x8e1),(0x8e2,0x91b),(0x91c,0x968)]):return
  sp=u.reg_read(UC_X86_REG_SP)
  if pair==(0,0x3632):
   off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp+4,4));assert (off,seg)==(0x2700,self.ds)
   self.emit('beep_file',name=self.string(seg,off));return_to_caller(u,4);return
  if pair==(0,0x3a64):
   effect=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];assert effect<17
   self.emit('beep',effect);return_to_caller(u,2);return
  raise ValueError(f'unexpected sound consumer {pair[0]:04x}:{pair[1]:04x}')
 def invoke(self,offset,args=(),incoming=0x1357):
  u=self.u;self.done=False;self.error=None
  for reg,v in [(UC_X86_REG_CS,self.load+0xda1),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_AX,incoming),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,v)
  u.mem_write(0x7f000,struct.pack('<'+'H'*(len(args)+2),0xff00,self.load+0xda1,*args))
  u.emu_start((self.load+0xda1)*16+offset,0x10ffff,count=10000)
  if self.error:raise self.error
  assert self.done and u.reg_read(UC_X86_REG_SP)==0xf004+len(args)*2 and u.reg_read(UC_X86_REG_DS)==self.ds
  return u.reg_read(UC_X86_REG_AX)
 def run(self,number,case):
  initial,actions=case;u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data)
  bgm,se,midi,irq,playing,frame,filename=initial
  self.write(0x9e0,'BBB',se,bgm,midi);self.write(0x2638,'B',irq);self.write(0xa40,'BB',playing,frame);u.mem_write(self.ds*16+0x2700,filename)
  table=bytes(u.mem_read(self.ds*16+0x9be,34));self.events=[f'CASE {number}'];self.open=False;self.file=bytes((i*7+17)&255 for i in range(127))
  guard_at=self.ds*16+0x5000;guard=bytes((i*19+31)&255 for i in range(64));u.mem_write(guard_at,guard)
  for action in actions:
   op,a,b,c,d,e,name=action;self.operation=op;self.action=action;result=0
   if op==0:
    for interrupt,signature,matched in [(0x60,b'PMD',c),(0x61,b'MMD',d)]:
     off=0x1000+(interrupt-0x60)*0x100;u.mem_write(interrupt*4,struct.pack('<HH',off,0x9000));u.mem_write(0x90000+off,b'\xeb\x03'+(signature if matched else b'BAD'))
    result=self.invoke(0x2d4,(b,a))
   elif op==1:result=self.invoke(0x264,(a,),b)
   elif op==2:self.invoke(0x8d6)
   elif op==3:self.invoke(0x8e2,(a,))
   elif op==4:
    for _ in range(a):self.invoke(0x91c)
   elif op==5:
    u.mem_write(self.ds*16+0x6000,name);self.invoke(0x3ba,(a,0x6000,self.ds))
   else:raise ValueError('sound fixture op')
   se,bgm,midi=self.read(0x9e0,'BBB');irq=self.read(0x2638,'B')[0];playing,frame=self.read(0xa40,'BB');filename=bytes(u.mem_read(self.ds*16+0x2700,13))
   self.events.append(f'STATE {result} {bgm} {se} {midi} {irq} {playing} {frame} {filename.hex()}')
   assert bytes(u.mem_read(guard_at,64))==guard and bytes(u.mem_read(self.ds*16+0x9be,34))==table and not self.open
  return ('\n'.join(self.events)+'\n').encode()
def fixtures():
 r=random.Random(1325);rows=[]
 def initial(bgm=2,se=1,playing=255,frame=0):return [bgm,se,1,97,playing,frame,bytes(r.randrange(256) for _ in range(13))]
 def action(op,a=0,b=0,c=0,d=0,e=0,name=bytes(13)):return [op,a,b,c,d,e,name]
 for bgm,se,pmd,mmd,kind in itertools.product((0,1,2,3,4,255,65535),(0,1,2,3,255,65535),(0,1),(0,1),(0,1,2,255)):
  rows.append((initial(frame=91),[action(0,bgm,se,pmd,mmd,0x6c00|kind)]))
 for bgm,arg,ax in itertools.product((0,1,2,3,4,255),(0,0x100,0x204,0x220,0x500,0xffff),(0,0x1357,0xffff)):
  rows.append((initial(bgm),[action(1,arg,ax,0xabcd)]))
 for se,playing,frame,new in itertools.product((0,1,2,3,255),(*range(17),255),(0,1,4,16,32,80,254,255),range(17)):
  rows.append((initial(se=se,playing=playing,frame=frame),[action(3,new),action(4,1),action(4,2),action(2)]))
 for se,effect in itertools.product((1,2),range(17)):
  rows.append((initial(se=se),[action(3,effect)]+[action(4,1) for _ in range(83)]))
 for bgm,se,function,base in itertools.product(range(4),range(3),(0x600,0xb00,0x700,0x6ff),(b'op',b'MIKO',b'12345678')):
  name=base+b'\0'+bytes(r.randrange(1,256) for _ in range(12-len(base)))
  rows.append((initial(bgm,se),[action(5,function,name=name)]))
 return rows
def fixture_text(cases):
 return ''.join(' '.join(map(str,s[:6]))+' '+s[6].hex()+' '+str(len(acts))+' '+' '.join(' '.join(map(str,a[:6]))+' '+a[6].hex() for a in acts)+'\n' for s,acts in cases)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','decoded-dir','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];m,files=source_manifest(root)
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);cases=fixtures();fixture=fixture_text(cases).encode();(out/'fixtures.txt').write_bytes(fixture)
 if a.reference_dir:
  ref=json.loads((a.reference_dir/'receipt.json').read_text());assert ref['passed'] and sha(fixture)==ref['fixture_sha256'];expected=(a.reference_dir/'original.txt').read_bytes();assert sha(expected)==ref['trace_sha256']
 else:
  traces=[]
  for load in (0x1000,0x2000):
   o=Original(a.target,a.decoded_dir,load);trace=b''.join(o.run(i,c) for i,c in enumerate(cases));traces.append(trace);(out/f'original-{load:04x}.txt').write_bytes(trace)
  assert traces[0]==traces[1];expected=traces[0]
 (out/'original.txt').write_bytes(expected);result=subprocess.run([str(a.exe.resolve()),'--replay',str(out/'fixtures.txt')],capture_output=True);(out/'native.txt').write_bytes(result.stdout);(out/'stderr.txt').write_bytes(result.stderr)
 if result.returncode or result.stdout!=expected:
  x=result.stdout.splitlines();y=expected.splitlines();at=next((i for i,(z,q) in enumerate(zip(x,y)) if z!=q),min(len(x),len(y)))
  (out/'mismatch.json').write_text(json.dumps(dict(line=at,actual=str(x[at:at+3]),expected=str(y[at:at+3]),returncode=result.returncode),indent=2));raise ValueError(f'sound differs line {at}')
 assert source_manifest(root)[0]==m
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=m,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),target_sha256=PACKED,payload_sha256=PAYLOAD,cases=len(cases),trace_lines=len(expected.splitlines()),fixture_sha256=sha(fixture),trace_sha256=sha(expected),original_cpu_reexecuted=not bool(a.reference_dir),reference_receipt_sha256=sha((a.reference_dir/'receipt.json').read_bytes()) if a.reference_dir else None,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(f'sound PASS {len(cases)} cases/{receipt["trace_lines"]} records')
if __name__=='__main__':main()
