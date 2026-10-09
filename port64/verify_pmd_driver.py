#!/usr/bin/env python3
"""Replay the HDI's original resident PMD programs and real music while muted.

The original COM installation, interrupt dispatch, song/SE parser, measure,
volume and OPN writes execute. DOS services, board presence/readback, PIT
calibration and explicitly injected Timer A/B IRQs are guarded adapters.
This produces an independent driver reference; it does not implement native
PMD synthesis, emulate physical timing, or open an audio device.
"""
import argparse,csv,sys,struct,json,hashlib
from datetime import datetime,timezone
from verify_cutscene import Fat12,ending_assets
from verify import source_manifest
from pathlib import Path
import unicorn as U
from unicorn.x86_const import *
HDI_SHA='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
DRIVERS={
 'PMD.COM':(20379,'cbbe9bd610aedda586d8bd7f6dd13d21f037a089458a21ddda0b11a53b4b29e4',0,'M26',' /M8 /V0 /E2 /K /N /P'),
 'PMD86.COM':(28871,'34b7381d66400b89fca833e08fb30f315b9092eb3883f137538dcf18477fd77f',2,'M86',' /M8 /V0 /E2 /K /N- /P'),
 'PMDB2.COM':(25730,'dfebbfd6e82916dfc4d8d01f2fcd938e215cc16cbd5ce2f19bce37cdc3841437',1,'M86',' /M8 /V0 /E2 /K /N- /P')}
sha=lambda b:hashlib.sha256(b).hexdigest()
READ_PORTS={2,0x88,0x8a,0x8c,0x8e,0x188,0x18a,0x18c,0x18e,0x288,0x28a,0x388,0x38a,0xa460,0xa468,0xa66e}
WRITE_PORTS=READ_PORTS|{0,0x5f,0x71,0x77}

def directory_files(path):
 image=path.read_bytes()
 if sha(image)!=HDI_SHA:raise ValueError('original HDI identity differs')
 fat=Fat12(bytearray(image));at=fat.find_entry([fat.root],b'GENSO      ')
 clusters=fat.chain(struct.unpack_from('<H',image,at+26)[0]);folders=[fat.cluster_offset(c) for c in clusters];result={}
 for name in (*DRIVERS,'GAME.BAT'):
  stem,ext=name.split('.');short=stem.ljust(8).encode()+ext.encode();entry=fat.find_entry(folders,short)
  result[name]=fat.file_bytes(struct.unpack_from('<H',image,entry+26)[0],struct.unpack_from('<I',image,entry+28)[0])
 for name,(size,digest,*_) in DRIVERS.items():
  data=result[name]
  if len(data)!=size or sha(data)!=digest or data[0]!=0xe9 or data[3:8]!=b'\xeb\x11PMD':raise ValueError('driver identity/flat COM entry differs: '+name)
 return result

class Driver:
 def __init__(self,data,filename,tail,load=0x2000,calibration_interval=100):
  self.data=data;self.filename=filename.removesuffix('.COM').ljust(8).encode()+b'COM';self.calibration_interval=calibration_interval;self.load=load;self.u=U.Uc(U.UC_ARCH_X86,U.UC_MODE_16);self.u.mem_map(0,0x110000)
  self.u.mem_write(load*16+0x100,self.data);self.u.mem_write(load*16,b'\xcd\x20');self.u.mem_write((load-1)*16+3,struct.pack('<H',0x5000));self.u.mem_write(load*16+0x2c,struct.pack('<H',0x900));self.u.mem_write(0x9000,b'\0\0\x01\0C:\\GENSO\\PMD.COM\0')
  self.u.mem_write(load*16+0x80,bytes([len(tail)])+tail.encode()+b'\r')
  self.u.mem_write(0x2100,b'\xcf');self.u.mem_write(0x2200,b'\xf4')
  for n in range(256):self.u.mem_write(n*4,struct.pack('<HH',0,0x210))
  for r in (UC_X86_REG_CS,UC_X86_REG_DS,UC_X86_REG_ES,UC_X86_REG_SS):self.u.reg_write(r,load)
  self.u.reg_write(UC_X86_REG_IP,0x100);self.u.reg_write(UC_X86_REG_SP,0xff00)
  self.messages=[];self.read_ports=set();self.ports=[];self.ints=[];self.selected={};self.registers={};self.error=None;self.end=False;self.last=0;self.alloc=0x6000;self.ticks=0;self.a460=0x41;self.pic=255;self.instructions=0;self.fm_status=0
  self.u.hook_add(U.UC_HOOK_INTR,self.guarded_interrupt);self.u.hook_add(U.UC_HOOK_INSN,self.guarded_input,None,1,0,UC_X86_INS_IN);self.u.hook_add(U.UC_HOOK_INSN,self.guarded_output,None,1,0,UC_X86_INS_OUT)
  self.u.hook_add(U.UC_HOOK_CODE,self.code)
 def code(self,u,address,size,user):
  self.last=address;self.instructions+=1
  if self.instructions%self.calibration_interval==0 and (u.reg_read(UC_X86_REG_EFLAGS)&0x200) and not (self.pic&1) and self.vector(8)!=(0,0x210):
   flags=u.reg_read(UC_X86_REG_EFLAGS);ip,cs=self.vector(8);self.push(flags);self.push(self.reg(UC_X86_REG_CS));self.push(self.reg(UC_X86_REG_IP));u.reg_write(UC_X86_REG_CS,cs);u.reg_write(UC_X86_REG_IP,ip);u.reg_write(UC_X86_REG_EFLAGS,flags&~0x300)
  if address==0x2200:self.end=True;u.emu_stop()
 def guarded_input(self,u,p,size,user):
  if p not in READ_PORTS or size!=1:self.error=ValueError(f'unexpected IN {p:x}/{size}');self.end=True;u.emu_stop();return 0
  return self.input(u,p,size,user)
 def guarded_output(self,u,p,size,value,user):
  if p not in WRITE_PORTS or size!=1:self.error=ValueError(f'unexpected OUT {p:x}/{size}');self.end=True;u.emu_stop();return
  self.output(u,p,size,value,user)
 def output(self,u,p,size,v,user):
  self.ports.append([self.ticks,p,size,v])
  if p==0xa460:self.a460=v
  if p==2:self.pic=v
  if p in (0x88,0x8c,0x188,0x18c,0x288,0x28c):self.selected[p]=v
  elif p in (0x8a,0x8e,0x18a,0x18e,0x28a,0x28e):
   reg=self.selected.get(p-2,0);self.registers[(p-2,reg)]=v
   if reg==0x27:
    if v&0x10:self.fm_status&=~1
    if v&0x20:self.fm_status&=~2
 def input(self,u,p,size,user):
  self.read_ports.add(p)
  if p in (0x18c,0x18e) and not self.a460&1:return 255
  if p in (0x8a,0x8e,0x18a,0x18e,0x28a,0x28e):
   if self.selected.get(p-2,0)==255:return 1
   return self.registers.get((p-2,self.selected.get(p-2,0)),0)
  if p in (0x88,0x8c,0x188,0x18c,0x288,0x28c):return self.fm_status
  if p==0xa460:return self.a460
  return 0
 def reg(self,r):return self.u.reg_read(r)&65535
 def push(self,n):
  sp=(self.reg(UC_X86_REG_SP)-2)&65535;self.u.reg_write(UC_X86_REG_SP,sp);self.u.mem_write(self.reg(UC_X86_REG_SS)*16+sp,struct.pack('<H',n&65535))
 def vector(self,n):return struct.unpack('<HH',self.u.mem_read(n*4,4))
 def guarded_interrupt(self,u,n,user):
  try:self.interrupt(u,n,user)
  except Exception as e:self.error=e;self.end=True;u.emu_stop()
 def interrupt(self,u,n,user):
  ax=self.reg(UC_X86_REG_AX);bx=self.reg(UC_X86_REG_BX);cx=self.reg(UC_X86_REG_CX);dx=self.reg(UC_X86_REG_DX);ds=self.reg(UC_X86_REG_DS);self.ints.append([n,ax,bx,cx,dx])
  flags=u.reg_read(UC_X86_REG_EFLAGS)
  if n==0x2f and ax==0x1600:u.reg_write(UC_X86_REG_AX,0);return
  if n==0x21:
   ah=ax>>8;u.reg_write(UC_X86_REG_EFLAGS,flags&~1)
   if ah==2:return
   if ah==9:
    data=bytes(u.mem_read(ds*16+dx,min(2048,0x10000-dx)));end=data.find(b'$')
    if end<0:raise ValueError('unterminated DOS print adapter')
    self.messages.append(data[:end].hex());return
   if ah==0x30:u.reg_write(UC_X86_REG_AX,5);u.reg_write(UC_X86_REG_BX,0);return
   if ah==0x52:
    u.reg_write(UC_X86_REG_ES,0x800);u.reg_write(UC_X86_REG_BX,0x100);u.mem_write(0x8104,struct.pack('<HH',0x200,0x800));u.mem_write(0x8200,struct.pack('<HHH',65535,0,1));u.mem_write(0x8226,self.filename);u.mem_write(0x8217,struct.pack('<I',len(self.data)));return
   if ah==0x35:
    ip,cs=self.vector(ax&255);u.reg_write(UC_X86_REG_ES,cs);u.reg_write(UC_X86_REG_BX,ip);return
   if ah==0x25:u.mem_write((ax&255)*4,struct.pack('<HH',dx,ds));return
   if ah==0x48:u.reg_write(UC_X86_REG_AX,self.alloc);self.alloc+=bx+1;return
   if ah in (0x49,0x4a):return
   if ah in (0x31,0x4c):self.end=True;self.exit=ax;u.emu_stop();return
   if ah==0x2f:u.reg_write(UC_X86_REG_ES,self.load);u.reg_write(UC_X86_REG_BX,0x80);return
   raise ValueError(f'DOS {ax:04x} at {self.last:x}')
  if n in (0x60,0x64):
   ip,cs=self.vector(n);self.push(flags);self.push(self.reg(UC_X86_REG_CS));self.push(self.reg(UC_X86_REG_IP));u.reg_write(UC_X86_REG_CS,cs);u.reg_write(UC_X86_REG_IP,ip);u.reg_write(UC_X86_REG_EFLAGS,flags&~0x300);return
  raise ValueError(f'INT {n:02x}/{ax:04x} at {self.last:x}')
 def invoke(self,number,ax=0,dx=0):
  self.error=None;self.u.reg_write(UC_X86_REG_CS,0x220);self.u.reg_write(UC_X86_REG_IP,0)
  self.u.reg_write(UC_X86_REG_SS,self.load);self.u.reg_write(UC_X86_REG_SP,0xff00)
  self.u.reg_write(UC_X86_REG_AX,ax);self.u.reg_write(UC_X86_REG_DX,dx)
  self.u.reg_write(UC_X86_REG_DS,self.load)
  flags=2;ip,cs=self.vector(number);self.push(flags);self.push(0x220);self.push(0)
  self.u.reg_write(UC_X86_REG_CS,cs);self.u.reg_write(UC_X86_REG_IP,ip);self.u.reg_write(UC_X86_REG_EFLAGS,flags)
  self.run();return dict(ax=self.reg(UC_X86_REG_AX),bx=self.reg(UC_X86_REG_BX),dx=self.reg(UC_X86_REG_DX),ds=self.reg(UC_X86_REG_DS)-self.load)
 def run(self,limit=2000000):
  self.end=False;self.u.emu_start(self.reg(UC_X86_REG_CS)*16+self.reg(UC_X86_REG_IP),0x110000,count=limit)
  if self.error:raise self.error
  if not self.end:raise ValueError(f'bounded run exhausted at {self.last:x}')

 def service(self,ax):return self.invoke(0x60,ax)
 def irq(self,status):
  if status not in (0,1,2,3):raise ValueError('invalid OPN timer status')
  irq=[n for n in range(8,16) if self.vector(n)!=(0,0x210)]
  if len(irq)!=1:raise ValueError('resident FM vector ownership differs')
  self.fm_status=status;self.invoke(irq[0])
  if self.fm_status:raise ValueError('original IRQ did not clear injected timer flag')
 def write_resource(self,ax,data):
  address=self.service(ax);sizes=self.service(0x2200)
  limit=sizes['ax' if ax==0x600 else 'dx']*1024
  if len(data)>limit:raise ValueError('resource exceeds configured driver buffer')
  segment=self.load+address['ds'];offset=address['dx']
  if offset+limit>65536:raise ValueError('resident buffer crosses segment')
  self.u.mem_write(segment*16+offset,data)
  return dict(segment_relative=address['ds'],offset=offset,size=len(data),limit=limit,sha256=sha(data))
 def snapshot(self):
  return dict(measure=self.service(0x500)['ax'],volume=self.service(0x800)['ax'],status=self.service(0xa00)['ax'])


def install(data,name,load):
 driver=Driver(data,name,DRIVERS[name][4],load);driver.run()
 if driver.exit!=0x3100 or driver.vector(0x60)!=(0x103,load):raise ValueError('original resident installation did not complete')
 version=driver.service(0x900)
 if version['ax']!=0x4800+DRIVERS[name][2]:raise ValueError('original type/version differs')
 return driver

def music_case(driver,music,effects,ticks):
 driver.service(0x100);effect_address=driver.write_resource(0xb00,effects);song_address=driver.write_resource(0x600,music)
 driver.service(0);before=driver.snapshot();start=len(driver.ports)
 for _ in range(128):driver.irq(1)
 if driver.snapshot()['measure']!=before['measure']:raise ValueError('Timer A advanced song measure without Timer B')
 rows=[]
 for tick in range(ticks):
  driver.ticks=tick+1;driver.irq(3);rows.append(driver.snapshot())
 stopped=driver.service(0x100);stop=driver.snapshot()
 for _ in range(128):driver.irq(3)
 if driver.snapshot()['measure']!=stop['measure']:raise ValueError('stopped music measure advanced')
 return dict(effect_address=effect_address,song_address=song_address,before=before,states=rows,stopped=stopped,stop=stop,ports=driver.ports[start:])

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--hdi',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
 parser.add_argument('--ticks',type=int,default=384)
 args=parser.parse_args()
 if not 192<=args.ticks<=4096:raise ValueError('IRQ profile must have192..4096 Timer B ticks')
 root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root);out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
 binaries=directory_files(args.hdi);assets=ending_assets(args.hdi);outputs={};first={};cases=0
 for load in (0x1000,0x2000):
  for name in DRIVERS:
   driver=install(binaries[name],name,load);install_profile=dict(version=driver.service(0x900),vectors=[(n,ip,cs-load) for n in range(256) for ip,cs in [driver.vector(n)] if (ip,cs)!=(0,0x210)],ports=driver.ports,messages=driver.messages)
   path=out/f'{name}-{load:04x}-install.json';path.write_text(json.dumps(install_profile,indent=2)+'\n');outputs[path.name]=sha(path.read_bytes())
   songs=sorted((n,v) for n,v in assets.items() if n.endswith('.'+DRIVERS[name][3]))
   if len(songs)!=23:raise ValueError('expected all23original music resources perdriver')
   for song,data in songs:
    driver.ports=[];driver.ints=[];driver.ticks=0;record=music_case(driver,data,assets['MIKO.EFC'],args.ticks)
    key=(name,song)
    if load==0x1000:first[key]=record
    elif record!=first[key]:raise ValueError(f'relocated driver state/IO differs: {key}')
    path=out/f'{name}-{load:04x}-{song}.json';path.write_text(json.dumps(record,separators=(',',':'))+'\n');outputs[path.name]=sha(path.read_bytes());cases+=1
    print(f'PMD original load{load:04x} {name} {song}: {args.ticks}TimerB states; final measure={record["states"][-1]["measure"]}',flush=True)
 if source_manifest(root)[0]!=manifest:raise ValueError('source changed during driver replay')
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,source_files=len(files),command=sys.argv,hdi_sha256=HDI_SHA,drivers={n:dict(size=len(binaries[n]),sha256=sha(binaries[n]),tail=DRIVERS[n][4],entry='PSP:0100',isr='PSP:0103') for n in DRIVERS},music={n:dict(size=len(v),sha256=sha(v)) for n,v in assets.items() if n.endswith(('.M26','.M86','.EFC'))},cases=cases,timer_b_states=cases*args.ticks,loads=['1000','2000'],outputs=outputs,unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name).read_bytes()),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Original PMD drivers/music measure and OPN writes PASS',cases,'cases')
if __name__=='__main__':main()
