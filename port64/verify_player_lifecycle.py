#!/usr/bin/env python3
"""Original MAIN player/miss/Bomb CPU producers versus native state and requests.

Movement, clamp, point-motion, trigger branches and performance-lower execute
original instructions. Fire/items/HUD/sound/game-over/character graphics have
explicit ABI adapters. This is a component claim, not live death/Bomb gameplay.
"""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_enemy import Original as Base
from verify import source_manifest

FIELDS=('inv hit miss respawn radius angle misses used quit bombing frame disabled clear pull scroll bg circle tone changed '
        'p0 p1 p2 b0 b1 b2 ox oy px py power overflow dream dream_score lives bombs perf minimum credit scroll_line '
        'x y prev_x prev_y vx vy old_input shot_time laser_time keys shift gameover').split()
OFFSETS={
 'inv':(0x4662,'B'),'hit':(0x4669,'B'),'miss':(0x466a,'B'),'respawn':(0x4663,'B'),
 'radius':(0x467a,'H'),'angle':(0x4679,'B'),'quit':(0x5392,'B'),
 'bombing':(0x4368,'B'),'frame':(0x4369,'B'),'disabled':(0xbcca,'B'),
 'clear':(0xbcba,'B'),'pull':(0x23a0,'B'),'scroll':(0x427c,'B'),'circle':(0x4252,'B'),
 'tone':(0x3a4,'H'),'changed':(0x5393,'B'),
 'ox':(0x466c,'h'),'oy':(0x466e,'h'),'px':(0x4670,'h'),'py':(0x4672,'h'),
 'power':(0x4664,'B'),'overflow':(0x2396,'h'),'dream':(0x4676,'B'),'dream_score':(0xbccc,'H'),
 'perf':(0x5395,'B'),'minimum':(0x5397,'B'),'scroll_line':(0x4278,'H'),
 'x':(0x464e,'h'),'y':(0x4650,'h'),'prev_x':(0x4652,'h'),'prev_y':(0x4654,'h'),
 'vx':(0x4656,'h'),'vy':(0x4658,'h'),'old_input':(0x464c,'H'),
 'shot_time':(0x4666,'B'),'laser_time':(0x42c8,'H'),'keys':(0x3974,'H'),'shift':(0x3976,'B')}
for i in range(3):OFFSETS['p'+str(i)]=(0x2aac+i,'B');OFFSETS['b'+str(i)]=(0x4496+i,'B')
RESIDENT={'misses':0x31,'used':0x32,'lives':0xb,'bombs':0xd,'credit':0xe}
BG=[0xe020,0xe021,0x11be]
sha=lambda data:hashlib.sha256(data).hexdigest()

class Original(Base):
 def __init__(self,target,load=0x2000):
  self.error=None;self.requests=[];self.gameover=1;self.load=load;self.delta=0x2000-load
  super().__init__(target)
  if self.delta:
   # Relocate the same pinned module at a second load; code offsets and the
   # explicit DS/SS/resident adapters retain their identities.
   at=struct.unpack_from('<H',target,24)[0]
   for i in range(1136):
    off,seg=struct.unpack_from('<HH',target,at+i*4);site=seg*16+off
    struct.pack_into('<H',self.module,site,(struct.unpack_from('<H',self.module,site)[0]-self.delta)&65535)
   self.u.mem_write(load*16,bytes(self.module))
 def hook(self,u,address,size,unused):
  try:self.body(u,address,size,unused)
  except Exception as error:self.error=error;u.emu_stop()
 def body(self,u,address,size,unused):
  actual_cs=u.reg_read(UC_X86_REG_CS);cs=actual_cs+self.delta
  ip=address-actual_cs*16;sp=u.reg_read(UC_X86_REG_SP)
  def ret(far=False,args=0):
   data=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
   u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args)
   if far:u.reg_write(UC_X86_REG_CS,data[1])
   u.reg_write(UC_X86_REG_IP,data[0])
  pair=(cs,ip)
  kinds={(0x2aaf,0xe000):(0,False),(0x33a9,0xa03e):(1,True),
         (0x2aaf,0x458a):(2,True),(0x2aaf,0x72f6):(3,True),
         (0x2aaf,0x43f8):(6,True),(0x2aaf,0x44b1):(7,True),
         (0x2aaf,0xe002):(10,False)}
  if pair in kinds:
   kind,far=kinds[pair];self.requests.append(f'{kind} 0');ret(far);return
  if pair==(0x330e,0x7d2):
   self.requests.append('4 '+str(struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]));ret(True,2);return
  if pair==(0x2aaf,0x188e):
   self.requests.append('5 '+str(u.mem_read(0x70000+sp+4,1)[0]));return # actual lower runs
  if pair==(0x2aaf,0x3a51):
   self.requests.append('8 0');u.reg_write(UC_X86_REG_AX,self.gameover);ret();return
  if pair==(0x2aaf,0x553a):
   self.requests.append('9 '+str(struct.unpack('<H',u.mem_read(0x70000+sp+2,2))[0]));ret(False,2);return
  if pair==(0x2000,0x1d50):
   self.requests.append('11 '+str(struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]));ret(True,2);return
 def seed(self,values):
  assert len(values)==51
  self.reset();self.error=None;self.requests=[]
  d=dict(zip(FIELDS,values));self.gameover=d['gameover']
  for name,(at,fmt) in OFFSETS.items():self.write(at,fmt,d[name])
  self.u.mem_write(0x90000,bytes(256));self.write(0xba86,'HH',0,0x9000)
  for name,at in RESIDENT.items():self.u.mem_write(0x90000+at,bytes([d[name]]))
  self.write(0x426a,'H',BG[d['bg']]);self.write(0x426c,'H',BG[1])
  self.write(0x449a,'H',0xe000);self.write(0x436a,'H',0x54c4);self.write(0x436c,'H',0xe002)
 def execute(self,op):
  self.requests=[];self.error=None
  try:self.call({'U':0x5fcf,'M':0x5e98,'B':0x54c4,'R':0x571a}[op],cs=0x2aaf-self.delta)
  except Exception:
   if self.error:raise RuntimeError('original lifecycle adapter rejected') from self.error
   raise
  if self.error:raise RuntimeError('original lifecycle adapter rejected') from self.error
  values=[]
  for name in FIELDS[:-3]:
   if name in OFFSETS:at,fmt=OFFSETS[name];value=self.read(at,fmt)[0]
   elif name in RESIDENT:value=self.u.mem_read(0x90000+RESIDENT[name],1)[0]
   elif name=='bg':value=BG.index(self.read(0x426a,'H')[0])
   else:raise ValueError('unmapped state '+name)
   values.append(value)
  return 'S '+' '.join(map(str,values))+''.join('|'+x for x in self.requests)

def fixture(**kwargs):
 d=dict.fromkeys(FIELDS,0)
 d.update(inv=64,scroll=1,circle=13,tone=100,p0=16,p1=32,p2=48,b0=64,b1=80,b2=96,
          ox=17,oy=23,px=31,py=43,power=128,overflow=42,dream=7,dream_score=1280,
          lives=3,bombs=2,perf=16,minimum=11,credit=2,scroll_line=399,
          x=3072,y=5120,prev_x=3040,prev_y=5136,vx=17,vy=-19,gameover=1)
 d.update(kwargs)
 return [d[k] for k in FIELDS]

def fixtures():
 for inv,hit,laser,keys in itertools.product((0,1,2,64,192,255),(0,1,127,255),(0,32,33,34,65535),(0,0x10,0x20,0x30)):
  yield 'U',fixture(inv=inv,hit=hit,laser_time=laser,keys=keys)
 for miss,respawn,keys,shift in itertools.product((0,1,2,3,4,31,32,33,39,40,41,255),(0,1,2,71,72),(0,0x10,0x20,0x30,5,10),(0,1)):
  yield 'U',fixture(miss=miss,respawn=respawn,keys=keys,shift=shift)
 for power,dream,perf,lives in itertools.product((0,1,3,4,63,64,65,128,255),range(8),(0,3,4,11,16,21,22,34,127,128,255),(0,1,2,3,255)):
  yield 'M',fixture(miss=33,power=power,dream=dream,perf=perf,lives=lives,misses=255)
 for miss,lives,angle,radius in itertools.product((0,1,2,3,4,5,31,32,33,34,255),(0,1,2,255),(0,248,255),(0,65500,65535)):
  yield 'M',fixture(miss=miss,lives=lives,angle=angle,radius=radius)
 for bombing,disabled,bombs,miss in itertools.product((0,1,127,255),(0,1,255),(0,1,2,255),(0,1,32,33,40,255)):
  yield 'B',fixture(bombing=bombing,disabled=disabled,bombs=bombs,miss=miss,hit=1,respawn=71,used=255,bg=2)
 for frame,bombing,bg in itertools.product(range(256),(0,1,255),range(3)):
  yield 'R',fixture(frame=frame,bombing=bombing,bg=bg,pull=1,scroll=0,circle=255,tone=65535,changed=255)
 for shot_time,keys,x,y,old_input in itertools.product((0,1,2,6,7,12,13,18,19,255),(0,1,4,5,10,15,0x20),(-32768,128,3072,6016,32767),(0,128,5632,32767),(0,4,8)):
  # Sample enough movement/trigger combinations without exploding the matrix.
  if (shot_time+keys+x+y+old_input)%47==0:
   yield 'U',fixture(shot_time=shot_time,keys=keys,x=x,y=y,old_input=old_input)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['target','exe','output-dir']:p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--runner');p.add_argument('--limit',type=int)
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh output directory')
 out.mkdir(parents=True);before=source_manifest(Path(__file__).resolve().parents[1])[0]
 inputs=[];expected=[];loads=[]
 cases=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures())
 for load in (0x1000,0x2000):
  original=Original(a.target.read_bytes(),load);load_inputs=[];load_expected=[]
  for op,values in cases:
   original.seed(values);load_inputs.append(op+' '+' '.join(map(str,values)));load_expected.append(original.execute(op))
  isolated=len(load_inputs)
  if not a.limit:
   # Each side retains ITS OWN preceding state, never target-seeded native
   # state. Include full miss/respawn, deathbomb and Bomb cleanup sequences.
   for bombs,lives in itertools.product((0,1),(1,3)):
    values=fixture(inv=0,hit=1,bombs=bombs,lives=lives,keys=0x10 if bombs else 0)
    original.seed(values);load_inputs.append('U '+' '.join(map(str,values)));load_expected.append(original.execute('U'))
    for tick in range(260):
     original.write(0x3974,'H',0);load_inputs.append('N 0 0');load_expected.append(original.execute('U'))
     load_inputs.append('T');load_expected.append(original.execute('R'))
  if inputs:assert inputs==load_inputs and expected==load_expected,'load metamorphism changed lifecycle'
  else:inputs,expected=load_inputs,load_expected
  loads.append(load)
 fixture_path=out/'fixtures.txt';fixture_path.write_text('\n'.join(inputs)+'\n')
 trace=out/'original.txt';trace.write_text('\n'.join(expected)+'\n')
 env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
 command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)]
 result=subprocess.run(command,text=True,capture_output=True,env=env,check=True,timeout=240)
 actual=result.stdout.splitlines();(out/'native.txt').write_text(result.stdout)
 for i,(left,right) in enumerate(itertools.zip_longest(actual,expected)):
  if left!=right:
   (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i],native=left,original=right),indent=2)+'\n')
   raise ValueError(f'lifecycle differential failed at case{i}')
 after=source_manifest(Path(__file__).resolve().parents[1])[0]
 assert before==after,'source changed during Oracle'
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest=after,
              target_sha256=sha(original.target),executable_sha256=sha(a.exe.read_bytes()),
              fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=sha(trace.read_bytes()),
              isolated=isolated,records=len(inputs),load_segments=loads,data_segment='8000',
              extents={name:sha(a.target.read_bytes()[6144+lo:6144+hi]) for name,lo,hi in
                       [('0AAF:54C4..553A',0xffb4,0x1002a),('0AAF:571A..581D',0x1020a,0x1030d),
                        ('0AAF:5E98..610D',0x10988,0x10bfd)]},
              unicorn_version=unicorn.__version__,scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({k:receipt[k] for k in ['passed','isolated','records','source_manifest']}))
if __name__=='__main__':main()
