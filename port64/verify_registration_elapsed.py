#!/usr/bin/env python3
"""Complete original MAINE registration and score/RNG against elapsed Scene.

Pinned decompressor payload/559 relocation observations remain diagnostic
container topology. Original menu/score/RNG/fades/frame/input waits execute;
graphics, keyboard, successful file and sound have explicit ABI adapters.
Independent ideal IRQ supplies time; CPU/I/O/loader/audio costs are unmeasured.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_registration import Original as MenuOriginal
from verify_score_file import HI,text,Original as ScoreOriginal
from verify_maine_elapsed import edges,edge
from verify_maine_join import return_to_caller
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def held(profile,now):
 n=edges(now);on=n%12<3
 return 0 if profile==2 else (8 if 50<=n<390 else 0x1000 if n>=410 and on else 0) if profile==1 else (0x30 if 50<=n<160 and on else 0x1000 if n>=180 and on else 0) if profile==3 else (0x1020 if n>=60 and on else 0) if profile==4 else (0x20 if n>=50 and on else 0)

class Original(MenuOriginal):
 def __init__(self,target,decoded,load):
  super().__init__(target,decoded,load)
  # Only guarded ABI/event sites and live polling points need Python hooks.
  # All unhooked menu/score/RNG instructions execute unchanged in Unicorn.
  self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000)
  self.u.mem_write(load*16,self.module)
  points={0xa05:(0xff00,0x27d6,0x2779,0x2615),0:(0x19ec,0x1274,0x11c2,0x2684,0xfc4,0x622,0x666,0x2520,0x20fa,0x9b8,0x978,0xa88,0x8a8,0xac4,0x9d4,0xb14,0x968,0x1c5a,0x2206,0x2225),0xcc7:(0xf5,0x48,0x6d,0x58c,0x31c,0x4a2,0x81a,0x822,0x33,0x3c,0x20a)}
  for seg,ips in points.items():
   for ip in ips:
    address=(load+seg)*16+ip;self.u.hook_add(unicorn.UC_HOOK_CODE,self.code,begin=address,end=address)
  self.u.hook_add(unicorn.UC_HOOK_INSN,self.port,None,1,0,UC_X86_INS_OUT)
 def counters(self):return [self.read(at,'H')[0] for at in (0xefa,0xefc,0xf02)]
 def prefix(self,tag):return ' '.join(map(str,[tag,self.now,*self.counters()]))+' '
 def flush(self):
  while self.event_at<len(self.events):self.lines.append(self.prefix('E')+self.events[self.event_at]);self.event_at+=1
 def event(self,*args,**kwargs):
  super().event(*args,**kwargs);self.flush()
 def key(self):
  value=held(self.profile,self.now);self.lines.append(f'K {self.now} {value}');return value
 def advance(self,now):
  n=edges(now)-edges(self.now);total=self.read(0xf02,'H')[0]+n*self.inc;count=n-total//65536
  for at in (0xefa,0xefc):self.write(at,'H',(self.read(at,'H')[0]+count)&65535)
  self.write(0xf02,'H',total&65535);self.now=now
 def pulse(self,needed):
  if not needed:return
  n=((needed-1)*65536+self.read(0xf02,'H')[0])//(65536-self.inc)+1;at=edge(edges(self.now)+n-1)
  if at>self.end:self.advance(self.end);self.blocked=True;self.u.emu_stop()
  else:self.advance(at)
 def code(self,u,address,size,_):
  try:
   seg=u.reg_read(UC_X86_REG_CS)-self.load;ip=address-u.reg_read(UC_X86_REG_CS)*16;sp=u.reg_read(UC_X86_REG_SP)
   if (seg,ip)==(0,0x2206):self.polls=0
   elif (seg,ip)==(0,0x2225):
    if self.polls:self.pulse(1)
    self.polls+=1
   elif (seg,ip)==(0,0x19ec):self.lines.append(f'P {self.now} {self.read(0x132,"h")[0]}');return_to_caller(u)
   elif seg==0 and ip in (0x622,0x666):
    arg=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];assert arg==(2 if ip==0x622 else 1);self.event('fade',int(ip==0x622),arg)
   elif seg==0xcc7 and ip in (0x81a,0x822):
    value=self.key();self.write(0x1b42,'H',value if ip==0x81a else self.read(0x1b42,'H')[0]|value);return_to_caller(u)
   elif (seg,ip)==(0xcc7,0x33):
    assert struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]==1;self.polls=0
    return_ip,return_cs=struct.unpack('<HH',u.mem_read(0x70000+sp,4))
    if return_cs==self.cs:
     bp=u.reg_read(UC_X86_REG_BP);lock=struct.unpack('<H',u.mem_read(0x70000+bp-4,2))[0];row=struct.unpack('<h',u.mem_read(0x70000+bp-2,2))[0];repeat=u.mem_read(0x70000+bp-9,1)[0]
     self.lines.append(self.prefix('F')+' '.join(map(str,[u.reg_read(UC_X86_REG_SI),u.reg_read(UC_X86_REG_DI),row,lock,repeat]))+' '+bytes(u.mem_read(self.ds*16+HI,196)).hex())
   elif (seg,ip)==(0xcc7,0x3c):
    if self.polls:self.pulse(max(0,1-self.read(0xefa,'H')[0]))
    self.polls+=1
   elif (seg,ip)==(0xcc7,0x20a):
    assert struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]==0;self.event('wait',0)
   else:
    super().body(u,address);self.flush()
  except BaseException as e:self.error=e;u.emu_stop()
 def run_case(self,row):
  seed,stage,rank,char,shot,turbo,end,present,digits,file,inc,counter_seed,phase,profile,horizon,_=row
  self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data);self.u.mem_write(self.ds*16+HI,bytes(196));self.write(0x170,'I',seed)
  self.u.mem_write(self.ds*16+HI-16,bytes([0x5a])*16)
  resident=bytearray(256)
  for at,value in ((0xf,rank),(0x11,stage),(0x12,char),(0x19,shot),(0x49,turbo),(0x30,end)):resident[at]=value
  resident[0x1d:0x25]=digits;self.u.mem_write(0x90000,bytes(resident));self.write(0xe9e,'HH',0,0x9000)
  self.inc=inc;self.now=phase;self.end=phase+horizon;self.profile=profile
  n=counter_seed+edges(phase);count=n-n*inc//65536
  for at,value in ((0xefa,count),(0xefc,count),(0xf02,n*inc),(0x400,inc)):self.write(at,'H',value&65535)
  self.write(0x402,'B',251)
  self.file=bytearray(file);self.present=bool(present);self.position=0;self.open=False;self.draws=0;self.events=[];self.event_at=0;self.lines=[];self.error=None;self.done=False;self.blocked=False;self.font_mode=False
  for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_ES,0),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,value)
  self.u.mem_write(0x7f000,struct.pack('<H',0xff00));self.u.emu_start(self.cs*16+0x27c4,0x10ffff,count=4000000)
  if self.error:raise RuntimeError(('registration adapter rejected',self.now)) from self.error
  assert self.done or self.blocked
  assert bytes(self.u.mem_read(0x90000,256))==resident
  assert bytes(self.u.mem_read(self.ds*16+HI-16,16))==bytes([0x5a])*16
  selected_rank,selected_char=self.read(0x4087,'BB');place=self.read(0x4086,'B')[0]
  self.lines.append(self.prefix('STOP')+' '.join(map(str,[self.end-self.now,int(self.done),self.read(0x132,'h')[0],selected_rank,selected_char,place,self.read(0x170,'I')[0],self.draws,int(self.present)]))+' '+bytes(self.u.mem_read(self.ds*16+HI,196)).hex()+' '+text(self.file))
  return self.lines

def fixture_rows(file):
 high=bytes([0,0,0,0,0,0,1,0]);base=[(318,5,3,48,0,1,255,1,high,file),(0x80000000,5,2,49,1,0,0,1,high,file),(1,6,1,49,1,0,253,1,high,file),(0xffffffff,5,1,48,0,1,254,1,bytes(8),file)]
 rows=[(*b,inc,seed,phase,profile,horizon,0) for b,inc,seed,phase,profile,horizon in itertools.product(base,(0,13311),(0,65535),(0,1000000),range(4),(1,8000000000))]
 for present,contents in ((0,b''),(1,file[:8*196+124]),(1,file[:8*196+100]+bytes([file[8*196+100]^1])+file[8*196+101:])):
  for inc,profile in itertools.product((0,13311),(0,3)):rows.append((0xffffffff,5,3,49,1,1,255,present,high,contents,inc,65535,1000000,profile,8000000000,0))
 for b,inc in itertools.product((base[0],base[2]),(0,13311)):rows.append((*b,inc,65535,1000000,4,8000000000,0))
 return rows

def wire(row,fine=False):
 seed,stage,rank,char,shot,turbo,end,present,digits,file,inc,counter_seed,phase,profile,horizon,chunk=row
 return ' '.join(map(str,[seed,stage,rank,char,shot,turbo,end,present,digits.hex(),text(file),inc,counter_seed,phase,profile,horizon,1000000 if fine else chunk]))

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','native','output'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);decoded=a.root/'.analysis/port64/maine-ending-v1291/decoded-original';target=a.root/'.analysis/targets/th04/maine.exe';sys.path.insert(0,str(a.root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original
 record=original('maine')
 if a.reference:
  j=json.loads((a.reference/'receipt.json').read_text());assert j['passed'] and j['original']==record['pins'] and j['oracle_sha256']==sha(Path(__file__))
  for name,pin in j['files'].items():assert sha(a.reference/name)==pin
  file=bytes.fromhex(j['base_file_hex']);rows=fixture_rows(file);assert j['vectors']==[wire(x) for x in rows];wanted=(a.reference/'expected.txt').read_bytes()
 else:
  generator=ScoreOriginal(target,decoded,0x1000);generated=generator.run((2,1,0,0,0,0,0,bytes(196),b'',bytes(8)));file=bytes.fromhex(generated[-1].split()[-1]);rows=fixture_rows(file);streams=[]
  for load in (0x1000,0x3333):
   o=Original(target,decoded,load);lines=[]
   for i,row in enumerate(rows):
    lines.extend([f'CASE {i}',*o.run_case(row)])
    if i and i%64==0:print('ORIGINAL',hex(load),i,flush=True)
   raw=('\n'.join(lines)+'\n').encode();(a.output/f'original-{load:x}.txt').write_bytes(raw);streams.append(raw)
  assert streams[0]==streams[1];wanted=streams[0]
 (a.output/'expected.txt').write_bytes(wanted)
 for fine in (False,True):
  tag='fine' if fine else 'coarse';v=a.output/(tag+'-vectors.txt');v.write_text('\n'.join(wire(x,fine) for x in rows)+'\n');q=subprocess.run([str(a.native.resolve()),'--registration-elapsed',str(v)],capture_output=True);(a.output/(tag+'.txt')).write_bytes(q.stdout);(a.output/(tag+'.stderr')).write_bytes(q.stderr)
  if q.returncode or q.stderr or q.stdout!=wanted:
   at=next((i for i,(x,y) in enumerate(itertools.zip_longest(q.stdout.splitlines(),wanted.splitlines())) if x!=y),None);(a.output/'mismatch.json').write_text(json.dumps(dict(tag=tag,exit_code=q.returncode,first_row=at),indent=2)+'\n');raise AssertionError(('registration mismatch',tag,at,q.returncode))
 (a.output/'receipt.json').write_text(json.dumps(dict(passed=True,original=record['pins'],base_file_hex=file.hex(),vectors=[wire(x) for x in rows],original_cases=len(rows)*2,native_vectors=len(rows),partition_vectors=len(rows),oracle_sha256=sha(Path(__file__)),native_sha256=sha(a.native),files={str(f.relative_to(a.output)):sha(f) for f in a.output.rglob('*') if f.is_file()},scope=__doc__),indent=2)+'\n');print('REGISTRATION ELAPSED PASS',len(rows),flush=True)
if __name__=='__main__':main()
