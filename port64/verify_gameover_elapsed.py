#!/usr/bin/env python3
"""Complete original MAIN Game Over/Continue, frame/input waits and fade4.

Legal MZ relocations and DGROUP are retained at loads1000/3333. Keyboard,
TRAM/palette, ranking/HUD/sound and final dispatch are guarded ABI seams.
Ideal IRQ timing is independent of host partitions; CPU/I/O/loader/audio
latency and physical display are outside this bounded instruction control.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys,ast
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_maine_elapsed import edges,edge
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Original:
 def __init__(self,record,load,row):
  self.stage,self.used,self.inc,self.seed,self.now,self.profile,self.horizon,_=row;self.end=self.now+self.horizon;self.load=load;self.dg=load+record['dg'];self.base=self.dg*16;self.lines=[];self.errors=[];self.route=-1;self.stopped=False;self.blocked=False;self.saves=0;self.poll=False
  body=bytearray(record['body'])
  for at in record['sites']:struct.pack_into('<H',body,at,(struct.unpack_from('<H',body,at)[0]+load)&65535)
  self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000);self.u.mem_write(load*16,bytes(body));self.u.hook_add(unicorn.UC_HOOK_CODE,self.code)
  n=self.seed+edges(self.now);count=n-n*self.inc//65536
  for at,value in ((0x2ab2,count),(0x2ab4,count),(0x2aba,n*self.inc),(0x772,self.inc),(0x3a4,100)):self.w(at,'H',value&65535)
  self.w(0x774,'B',251);self.w(0x5394,'B',self.stage);self.w(0x4664,'B',128);self.w(0x2396,'h',42);self.w(0x4676,'B',7);self.w(0xbccc,'H',1280)
  self.w(0xba86,'HH',0,0x9000);self.u.mem_write(0x90000,bytes(256))
  for at,value in [(0xb,1),(0xc,3),(0xd,0),(0xe,2),(0x30,255)]:self.u.mem_write(0x90000+at,bytes([value]))
  self.w(0x435a,'II',12345,67890);self.w(0x4359,'B',137);self.w(0x1a66,'BB',5,1)
  for at,raw in [(0x4349,[self.used,9,8,7,6,5,4,3]),(0x4351,range(8)),(0x1ebe,range(8,16)),(0x1ec6,range(16,24))]:self.u.mem_write(self.base+at,bytes(raw))
 def r(self,at,fmt='H'):return struct.unpack('<'+fmt,self.u.mem_read(self.base+at,struct.calcsize('<'+fmt)))[0]
 def w(self,at,fmt,*values):self.u.mem_write(self.base+at,struct.pack('<'+fmt,*values))
 def event(self,kind,x=0,y=0,value=0,attr=0,data=b''):
  self.lines.append(f'E {self.now} {self.r(0x2ab2)} {self.r(0x2ab4)} {self.r(0x2aba)} {kind} {x} {y} {value} {attr} '+(data.hex() if data else '-'))
 def keys(self):
  n=edges(self.now);on=n%16<5 or n%16>=10
  value=0 if self.profile==3 else (0x20 if n<140 else 0x1000 if n>=180 and on else 0) if self.profile==2 else (0x1000 if self.profile==1 else 0x20) if on else 0
  self.lines.append(f'K {self.now} {value}');return value
 def advance(self,now):
  n=edges(now)-edges(self.now);total=self.r(0x2aba)+n*self.inc;count=n-total//65536
  for at in (0x2ab2,0x2ab4):self.w(at,'H',(self.r(at)+count)&65535)
  self.w(0x2aba,'H',total&65535);self.now=now
 def pulse(self):
  n=self.r(0x2aba)//(65536-self.inc)+1;now=edge(edges(self.now)+n-1)
  if now>self.end:self.advance(self.end);self.blocked=True;self.u.emu_stop()
  else:self.advance(now)
 def ret(self,far=True,args=0):
  u=self.u;sp=u.reg_read(UC_X86_REG_SP);raw=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2));u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args)
  if far:u.reg_write(UC_X86_REG_CS,raw[1])
  u.reg_write(UC_X86_REG_IP,raw[0])
 def words(self,n):return struct.unpack('<'+'H'*n,self.u.mem_read(0x70000+self.u.reg_read(UC_X86_REG_SP)+4,n*2))
 def code(self,u,address,size,_):
  try:
   at=address-self.load*16
   if at==0x1b50:
    attr,off,seg,y,x=self.words(5);assert seg==self.dg;raw=bytes(u.mem_read(seg*16+off,32));assert b'\0' in raw;self.event(0,x,y,0,attr,raw.split(b'\0',1)[0]);self.ret(True,10)
   elif at==0x1b0c:
    attr,value,y,x=self.words(4);self.event(0,x,y,value,attr);self.ret(True,8)
   elif at==0x1379c:self.w(0x3974,'H',self.keys());self.ret()
   elif at==0x137a4:self.w(0x3974,'H',self.r(0x3974)|self.keys());self.ret()
   elif at==0x131b7:assert self.words(1)==(1,);self.event(5,value=1)
   elif at==0x131c0:
    if self.r(0x2ab2)<1:self.pulse()
   elif at==0x13213:assert self.words(1)==(0,);self.event(6)
   elif at==0x2462:self.poll=False
   elif at==0x2481:
    if self.poll:self.pulse()
    self.poll=True
   elif at==0x1f04:self.event(4,value=self.r(0x3a4));self.ret()
   elif at==0x666:assert self.words(1)==(4,);self.event(13,value=4)
   elif at==0xe65d:assert u.mem_read(0x90030,1)==b'\0';self.event(16)
   elif at==0x133dc:assert self.words(1)==(0x204,);self.event(12,value=4);self.ret(True,2)
   elif at==0x22f6:
    attr,off,seg,y,x=self.words(5);raw=bytes(u.mem_read(seg*16+off,3));assert raw==b'  \0';self.event(1,x,y,0,attr,raw[:2]);self.ret(True,10)
   elif at in (0x10d4b,0x10d77):self.event(2 if at==0x10d4b else 3);self.ret(False)
   elif at==0xe7fd:
    off,seg=self.words(2);assert bytes(u.mem_read(seg*16+off,6))==b'maine\0';self.event(14);self.route=1;self.stopped=True;u.emu_stop()
   elif at==0xb7e4:self.event(15);self.route=2;self.stopped=True;u.emu_stop()
   elif at==0x19af0:self.route=0;self.stopped=True;u.emu_stop()
   elif at in (0x12cb5,0x11de6,0xeee8,0xefa1,0x11692):
    kind,far={0x12cb5:(7,False),0x11de6:(8,True),0xeee8:(9,True),0xefa1:(10,True),0x11692:(11,False)}[at];self.event(kind)
    if kind==7:self.saves+=1
    self.ret(far)
  except BaseException as error:self.errors.append(repr(error));u.emu_stop()
 def run(self):
  u=self.u;cs=self.load+0xaaf
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.dg),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
  u.mem_write(0x7e000,struct.pack('<H',0xf000));u.emu_start(cs*16+0x3a51,0x10ffff,count=3000000);assert not self.errors and (self.stopped or self.blocked),(self.errors,self.now)
  state=[self.r(0x3a4),self.r(0x4664,'B'),self.r(0x4676,'B'),u.mem_read(0x9000b,1)[0],u.mem_read(0x9000d,1)[0],self.r(0x4349,'B'),self.r(0x2ab2),self.r(0x2ab4),self.r(0x2aba),self.saves]
  self.lines.append('STOP '+' '.join(map(str,[self.now,self.end-self.now,self.route,*state])));return self.lines

def fixtures():
 rows=[(0,used,inc,seed,phase,profile,horizon,0) for used,inc,seed,phase,profile,horizon in itertools.product((0,3,255),(0,13311),(0,65535),(0,1000000),range(4),(1,8000000000))]
 rows.extend((stage,0,inc,seed,phase,profile,8000000000,0) for stage,profile in ((4,1),(5,0),(6,0)) for inc,seed,phase in itertools.product((0,13311),(0,65535),(0,1000000)))
 return rows

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','native','output'):p.add_argument('--'+name,type=Path,required=True)
 g=p.add_mutually_exclusive_group();g.add_argument('--reference',type=Path);g.add_argument('--original-reference',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original
 record=original('main');rows=fixtures()
 pins=[(0xe461,893,'16277ea55192dd47018f2800b04ecb68eda39f6af6451751d2b609095bff2f93'),(0x622,130,'c4597fe984067e57ad982e693ed768a83e95d76465666c0db5d5eb0ae834fa3e'),(0x131b7,21,'3c79ff0bb4e74ee6e2aa9ac688bf1b849c015acd31c7d7ff135b2ca455b7c26f'),(0x13213,84,'1b83b9ea53e48c9b11eee06513595bea74021b2efced2da1045eb98c81be70f0')]
 for at,n,pin in pins:assert hashlib.sha256(record['body'][at:at+n]).hexdigest()==pin
 if a.original_reference:
  j=json.loads((a.original_reference/'original-controls.json').read_text());classpin=hashlib.sha256(ast.dump(next(x for x in ast.parse(Path(__file__).read_text()).body if isinstance(x,ast.ClassDef) and x.name=='Original'),include_attributes=False).encode()).hexdigest()
  assert j['passed'] and j['original_controls_passed'] and not j['native_acceptance'] and j['original']==record['pins'] and j['rows']==[list(x) for x in rows] and j['original_class_sha256']==classpin and j['edge_reader_sha256']==sha(Path(__file__).parent/'verify_maine_elapsed.py')
  for name,pin in j['files'].items():assert sha(a.original_reference/name)==pin
  wanted=(a.original_reference/'expected.txt').read_bytes()
 elif a.reference:
  j=json.loads((a.reference/'receipt.json').read_text());assert j['passed'] and j['original']==record['pins'] and j['rows']==[list(x) for x in rows] and j['oracle_sha256']==sha(Path(__file__))
  for name,pin in j['files'].items():assert sha(a.reference/name)==pin
  wanted=(a.reference/'expected.txt').read_bytes()
 else:
  controls=[]
  for load in (0x1000,0x3333):
   lines=[]
   for index,row in enumerate(rows):lines.extend([f'CASE {index}',*Original(record,load,row).run()])
   raw=('\n'.join(lines)+'\n').encode();(a.output/f'original-{load:x}.txt').write_bytes(raw);controls.append(raw);print('ORIGINAL',hex(load),len(rows),flush=True)
  assert controls[0]==controls[1];wanted=controls[0]
 (a.output/'expected.txt').write_bytes(wanted)
 for fine in (False,True):
  tag='fine' if fine else 'coarse';v=a.output/(tag+'-vectors.txt');v.write_text(''.join(' '.join(map(str,(*row[:-1],1000000 if fine else 0)))+'\n' for row in rows));q=subprocess.run([str(a.native.resolve()),'--gameover-elapsed',str(v)],capture_output=True);(a.output/(tag+'.txt')).write_bytes(q.stdout);(a.output/(tag+'.stderr')).write_bytes(q.stderr)
  if q.returncode or q.stderr or q.stdout!=wanted:
   first=next((i for i,(x,y) in enumerate(itertools.zip_longest(q.stdout.splitlines(),wanted.splitlines())) if x!=y),None);(a.output/'mismatch.json').write_text(json.dumps(dict(tag=tag,exit_code=q.returncode,first_row=first),indent=2)+'\n');raise AssertionError(('Game Over elapsed mismatch',tag,first,q.returncode))
 (a.output/'receipt.json').write_text(json.dumps(dict(passed=True,original=record['pins'],rows=rows,original_cases=len(rows)*2,native_vectors=len(rows),partition_vectors=len(rows),oracle_sha256=sha(Path(__file__)),native_sha256=sha(a.native),files={str(f.relative_to(a.output)):sha(f) for f in a.output.rglob('*') if f.is_file()},scope=__doc__),indent=2)+'\n');print('GAME OVER ELAPSED PASS',len(rows),flush=True)
if __name__=='__main__':main()
