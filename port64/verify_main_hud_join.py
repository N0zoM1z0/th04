#!/usr/bin/env python3
"""Original first-stage caller, selected score loading, RNG initialization and HUD.

Execute MAIN 0AAF:03E0 through the return of stage_runtime_init at0489 at two
loads, including gameplay_session_init, real score codec/file byte store, all
353 runtime RNG draws, shot-level and full HUD/text stores. Stop at the explicit
caller prefix boundary; this is not a complete MAIN startup or physical DOS I/O.
BB/resource loading, palette application, clipping and tile invalidation are guarded adapters.
Native uses public ordinary MAIN construction and a fresh physical HostStore,
including writer-close and independent reopen. Short physical host files use
the documented host missing-file policy; raw target short reads remain separate.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_main_score import Original as Score
from verify_hud import EXTENTS as HUD_EXTENTS
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
EXTENTS=(*HUD_EXTENTS,(0,0x2266,0x22f6),(0xaaf,0x0213,0x03d5),
         (0xaaf,0x03e0,0x0489),(0xaaf,0x06e0,0x07ae),(0xaaf,0x43c0,0x43f8),
         (0xaaf,0x73db,0x74a6),(0xaaf,0x185e,0x1874),(0xaaf,0x593a,0x5954),
         (0xaaf,0x1168,0x1180),(0xaaf,0x1824,0x1842),(0xaaf,0x72f6,0x7322),
         (0xaaf,0x54b4,0x54c4),(0xaaf,0x11c2,0x11cd),(0xaaf,0x625b,0x6287),
         (0x13a9,0x9f8b,0x9fa8),(0x13a9,0x0486,0x04a0),(0x13a9,0x22e4,0x2315))

class Original(Score):
 def body(self,u,address,size,unused):
  cs=u.reg_read(UC_X86_REG_CS);rel=cs-self.load;ip=address-cs*16
  if (rel,ip)==(0xaaf,0x0489):self.finished=True;u.emu_stop();return
  if (rel,ip) in ((0xaaf,0x030f),(0xaaf,0x0785),(0xaaf,0x0790)):
   self.order.append((ip,self.rng_draws))
  if any(rel==s and lo<=ip<hi for s,lo,hi in EXTENTS):return
  adapters={(0xaaf,0x6a61):(False,()),(0xaaf,0x7534):(False,()),(0xaaf,0x203e):(False,()),
            (0,0x219c):(True,(0xd5,0x8000)),(0,0x1f04):(True,()),
            (0,0x144a):(True,(0x17f,0x19f,0x10,0x20))}
  if (rel,ip) in adapters:
   far,args=adapters[rel,ip];sp=u.reg_read(UC_X86_REG_SP);distance=4 if far else 2
   if args:assert struct.unpack('<'+'H'*len(args),u.mem_read(0x70000+sp+distance,len(args)*2))==args
   self.adapters.append((rel,ip,args))
   ret=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,distance))
   u.reg_write(UC_X86_REG_SP,sp+distance+len(args)*2);u.reg_write(UC_X86_REG_IP,ret[0])
   if far:u.reg_write(UC_X86_REG_CS,ret[1])
   return
  super().body(u,address,size,unused)
 def initialize(self,character,rank,seed,present,data):
  self.reset();self.error=None;self.finished=False;self.order=[];self.adapters=[]
  self.rng_draws=0;self.events=[];self.file=bytearray(data);self.open=False;self.position=0
  self.present=bool(present);self.write(0x3e2,'I',seed);self.write(0x768,'H',0xa000)
  # BIOS stores the last row index, not the row count: 24 selects 25 rows.
  self.u.mem_write(0x712,bytes([24]));self.u.mem_write(0xa0000,bytes(4000));self.u.mem_write(0xa2000,bytes(4000))
  resident=bytearray(256);resident[0xc]=3;resident[0xe]=2;resident[0xf]=rank if rank<4 else 1
  resident[0x11]=6 if rank==4 else 0;resident[0x12]=48+character;resident[0x13]=48+resident[0x11]
  resident[0x49]=1;self.u.mem_write(0x90000,bytes(resident));self.write(0xba86,'HH',0,0x9000)
  cs=self.load+0xaaf
  for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                    (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EAX,0),(UC_X86_REG_EFLAGS,2)):
   self.u.reg_write(reg,value)
  self.u.mem_write(0x7e000,struct.pack('<H',0xf000))
  self.u.emu_start(cs*16+0x3e0,cs*16+0xf000,count=500000)
  if self.error:raise RuntimeError('original MAIN caller rejected') from self.error
  assert self.finished and self.u.reg_read(UC_X86_REG_SP)==0xdffc and not self.open
  assert self.order[0]==(0x30f,0) and self.order[1][0]==0x785 and self.order[2]==(0x790,self.order[1][1]+257)
  assert self.rng_draws==self.order[1][1]+353
  tram=bytes(self.u.mem_read(0xa0000,4000))+bytes(self.u.mem_read(0xa2000,4000))
  angles=b''.join(bytes(self.u.mem_read(0x853e2+i*16+14,2)) for i in range(96))
  # One recreate writer closes once after writing the ten sections; selected
  # successful load closes once but performs no physical native commit.
  commits=1 if self.order[1][1] else 0
  fields=[str(self.read(0x3e2,'I')[0]),str(self.read(0x3ecc,'H')[0]),str(self.read(0xbcce,'B')[0]),
          str(self.read(0x1ed0,'h')[0]),bytes(self.u.mem_read(0x84349,8)).hex(),bytes(self.u.mem_read(0x84351,8)).hex(),
          bytes(self.u.mem_read(0x83dcc,256)).hex(),angles.hex(),tram.hex(),bytes(self.file).hex() or '-',str(commits)]
  return ' '.join(fields),dict(order=self.order,rng_draws=self.rng_draws,adapters=self.adapters,io=self.events)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh MAIN HUD output directory')
 out.mkdir(parents=True);root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
 target=a.target.read_bytes();assert sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
 codec=Score(target,0x1000);codec.run((2,318,0,0,0,1,0,bytes(196),b'',bytes(8)));baseline=bytes(codec.file)
 cases=[]
 for character,rank,seed,variant in itertools.product(range(2),range(5),(0,1,318),range(5)):
  data=bytearray(baseline);present=1;offset=(character*5+rank)*196
  if variant==0:data+=b'preserved-tail'
  elif variant==1:data[offset+2]^=1
  elif variant==2:data[offset+3]^=128
  elif variant==3:data=bytearray();present=0
  elif variant==4:data=data[:997]
  cases.append((character,rank,seed,present,bytes(data)))
 fixture=out/'fixtures.txt';fixture.write_text(''.join(f'{c} {r} {s} {p} {b.hex() or "-"}\n' for c,r,s,p,b in cases))
 expected=[];observations=[]
 for load in (0x1000,0x2000):
  original=Original(target,load);lines=[];current=[]
  for index,(c,r,s,p,b) in enumerate(cases):
   # Physical host policy rejects incomplete ten-section files as missing.
   line,observation=original.initialize(c,r,s,p and len(b)>=1960,b)
   lines.append(line);current.append(observation)
   if index%50==49:print(f'load{load:04x} {index+1} caller/HUD cases',flush=True)
  if expected:assert expected==lines and observations==current,'MAIN caller load metamorphism differs'
  else:expected=lines;observations=current
 ref=out/'original.txt';ref.write_text('\n'.join(expected)+'\n')
 command=[str(a.exe.resolve()),'--main-hud-join',str(fixture),str(out/'physical')]
 result=subprocess.run(command,capture_output=True,check=True,timeout=240);(out/'native.txt').write_bytes(result.stdout)
 for index,(x,y) in enumerate(itertools.zip_longest(expected,result.stdout.decode().splitlines())):
  if x!=y:
   (out/'mismatch.json').write_text(json.dumps(dict(case=index,original=x,native=y),indent=2)+'\n');raise ValueError(f'MAIN caller/HUD case{index} differs')
 assert source_manifest(root)[0]==manifest
 (out/'source-manifest.json').write_text(json.dumps(dict(sha256=manifest,files=files),indent=2)+'\n')
 (out/'observations.json').write_text(json.dumps(observations,indent=2)+'\n')
 receipt=dict(passed=True,cases=len(cases),load_segments=[4096,8192],source_manifest=manifest,
              target_sha256=sha(target),exe_sha256=sha(a.exe.read_bytes()),trace_sha256=sha(ref.read_bytes()),
              fixture_sha256=sha(fixture.read_bytes()),command=command,observed_utc=datetime.now(timezone.utc).isoformat(),
              extents={f'{s:04x}:{lo:04x}..{hi:04x}':sha(target[6144+s*16+lo:6144+s*16+hi]) for s,lo,hi in EXTENTS},scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','cases','trace_sha256')}))
if __name__=='__main__':main()
