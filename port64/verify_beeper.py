#!/usr/bin/env python3
"""Original OP EFS parser/play/tempo/PC-98 IRQ and offline digital PIT adapter.

Execute original 0000:3632..3771,3A64..3B25,3B40..3B6D,381E..38CC,
34B0..34DE at two loads. Files/allocation, initial hardware state, IRQ spacing
and PCM sampling are explicit adapters. TH04 beeper SE only; no library beeper
music, physical analogue/audio device, PMD/FM, full frontend or exact claim.
Host rejects segment/capacity overflow rather than reading unrelated DS.
"""
import argparse,hashlib,itertools,json,random,struct,subprocess,unicorn
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD
from verify_maine_join import return_to_caller
from verify_cutscene import ending_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
 def body(self,u,address):
  cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;pair=(cs-self.load,ip);sp=u.reg_read(UC_X86_REG_SP)
  if pair==(0,0xff00):self.done=True;u.emu_stop();return
  if pair[0]==0 and any(a<=ip<b for a,b in [(0x3632,0x3772),(0x3a64,0x3b26),(0x3b40,0x3b6e),(0x381e,0x38cd),(0x34b0,0x34df)]):return
  def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
  def ret(n=0):return_to_caller(u,n)
  if pair==(0,0xbb4):
   assert words(2)==(0x6000,self.ds) and not self.open
   self.open=self.file is not None;u.reg_write(UC_X86_REG_AX,0x40 if self.open else 0xfffe);ret(4);return
  if pair==(0,0x7fc):
   origin,lo,hi,handle=words(4);assert self.open and handle==0x40 and lo==hi==0 and origin in (0,2)
   u.reg_write(UC_X86_REG_AX,len(self.file) if origin==2 else 0);u.reg_write(UC_X86_REG_DX,0);ret(8);return
  if pair==(0,0x248e):
   assert self.open and words(1)==(len(self.file),);u.reg_write(UC_X86_REG_AX,0x9000);u.reg_write(UC_X86_REG_CX,0)
   u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)&~1);ret(2);return
  if pair==(0,0x7e2):
   assert self.open and words(4)==(len(self.file),0,0x9000,0x40)
   if self.file:u.mem_write(0x90000,self.file)
   u.reg_write(UC_X86_REG_AX,len(self.file));ret(8);return
  if pair==(0,0xb9e):assert self.open and words(1)==(0x40,);self.open=False;ret(2);return
  if pair==(0,0x2478):assert not self.open and words(1)==(0x9000,);ret(2);return
  raise ValueError(f'unexpected beeper consumer {pair[0]:04x}:{pair[1]:04x}')
 def port(self,u,port,size,value,unused):
  try:
   assert size==1 and port in (0x71,0x37,0x3fdb,0)
   self.events.append(f'OUT {port} {value}')
   if port==0x37:assert value in (6,7);self.gate=value==6
   if port==0x3fdb:
    if self.low is None:self.low=value
    else:self.divisor=self.low+(value<<8);self.low=None;self.reloads+=1
  except Exception as e:self.error=e;u.emu_stop()
 def begin(self,clock8,enabled=1,phase=0):
  u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data)
  self.write(0x584,'H',0);u.mem_write(0x501,bytes([128 if clock8 else 0]));self.write(0x958,'H',0)
  self.write(0x954,'HH',1996 if clock8 else 2458,120);self.write(0x962,'H',phase)
  self.write(0x9ae,'HHHHHHI',0,0,0,1,enabled,1,(1996 if clock8 else 2458)*120)
  for n in range(16):
   self.write(0x2680+n*8,'HHHH',0,0,0,0x8000+n*0x100);u.mem_write((0x8000+n*0x100)*16,bytes(528));u.mem_write((0x8000+n*0x100)*16+528,b'GUARD')
  self.clock8=clock8;self.events=[];self.low=None;self.gate=False;self.divisor=998 if clock8 else 1229;self.reloads=0;self.open=False
  u.mem_write(self.ds*16+0x6000,b'MIKO.EFS\0');self.guard=bytes((i*23+41)&255 for i in range(64));u.mem_write(self.ds*16+0x7000,self.guard)
 def invoke(self,ip,args=(),irq=False):
  u=self.u;self.done=False;self.error=None
  values=[(UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_AX,0x1357),(UC_X86_REG_EFLAGS,0x202)]
  for reg,v in values:u.reg_write(reg,v)
  stack=(0xff00,self.load,0x202) if irq else (0xff00,self.load,*args)
  u.mem_write(0x7f000,struct.pack('<'+'H'*len(stack),*stack));u.emu_start(self.load*16+ip,0x10ffff,count=2000000)
  if self.error:raise self.error
  assert self.done and u.reg_read(UC_X86_REG_SP)==0xf000+len(stack)*2 and u.reg_read(UC_X86_REG_DS)==self.ds and self.low is None
  assert bytes(u.mem_read(self.ds*16+0x7000,64))==self.guard
  for n in range(16):assert bytes(u.mem_read((0x8000+n*0x100)*16+528,5))==b'GUARD'
  ax=u.reg_read(UC_X86_REG_AX);return ax-65536 if ax>=32768 else ax
 def load_file(self,data):self.file=data;return self.invoke(0x3632,(0x6000,self.ds))
 def effect_data(self):return b''.join(bytes(self.u.mem_read((0x8000+n*0x100)*16,514)) for n in range(16))
 def snapshot(self,result=0):
  count,selected=self.read(0x9b0,'HH');active=self.read(0x9ae,'H')[0];phase=self.read(0x962,'H')[0];div,tempo=self.read(0x954,'HH');enabled=self.read(0x9b6,'H')[0]
  cursors=[self.read(0x2680+n*8,'H')[0] for n in range(16)]
  return 'STATE '+' '.join(map(str,[result,count,selected,active,phase,tempo,div,enabled,int(self.gate),self.divisor,self.reloads,*cursors]))
 def run(self,n,case):
  clock8,enabled,phase,actions=case;self.begin(clock8,enabled,phase);self.events=[f'CASE {n}']
  for op,value,data in actions:
   result=0
   if op==0:result=self.load_file(data);self.events.append('DATA '+self.effect_data().hex())
   elif op==1:result=self.invoke(0x3a64,(value,))
   elif op==2:
    for _ in range(value):self.invoke(0x381e,irq=True);self.events.append(self.snapshot())
   elif op==3:result=self.invoke(0x3b40,(value,))
   elif op==4:self.write(0x9b6,'H',value)
   else:raise ValueError('beeper action')
   if op!=2:self.events.append(self.snapshot(result))
  assert not self.open;return ('\n'.join(self.events)+'\n').encode()
def fixtures(efs):
 rows=[]
 def load(data):return (0,0,data)
 def action(op,n):return (op,n,b'')
 variants=[b'',b'; comment123\n',b'440 0',b'440 0 ',b'440',b'0 ',b'65536 0 ',b'65537 0 ',b'999999999999999 0 ',b'440;comment123\n0 ',b'440 ;comment123\n0 ',b'440\xff0 ',b'440 0 880 0 ',b'440 0 880 ',b'1 '*255+b'0 ',b'1 '*256+b'0 ',b'1 '*257+b'0 ',b'0 '*16+b'440 ',efs]
 for clock8,data in itertools.product((0,1),variants):rows.append((clock8,1,0,[load(data),action(1,1),action(2,25)]))
 r=random.Random(1326)
 for clock8 in (0,1):
  for _ in range(50):
   data=bytes(r.choice(b'0123456789 ;\r\n\t:ABC') for _ in range(r.randrange(1,300)))
   rows.append((clock8,1,0,[load(data),load(b'440 0 '),action(1,1),action(2,31)]))
 for clock8,effect in itertools.product((0,1),range(1,16)):
  rows.append((clock8,1,0,[load(efs),action(1,effect),action(2,1320)]))
 for clock8,enabled,phase in itertools.product((0,1),(0,1,2),(0,3,4,19,20,65532,65535)):
  rows.append((clock8,enabled,phase,[load(b'1 30 31 37 38 440 65535 0 '),action(1,1),action(2,55),action(4,1),action(1,1),action(2,55)]))
 for clock8,value in itertools.product((0,1),(0,29,30,31,60,119,120,121,239,240,241,32767,32768,65535)):
  rows.append((clock8,1,0,[load(b'440 0 '),action(3,value),action(1,1),action(2,25)]))
 for clock8,effect in itertools.product((0,1),(0,16,17,32767,32768,65535)):
  rows.append((clock8,1,0,[load(efs),action(1,effect),action(2,25)]))
 for clock8 in (0,1):
  rows.append((clock8,1,0,[load(b'440 0 '),action(1,1),action(2,5),load(b'880 0 '),action(1,2),action(2,25),load(None)]))
  rows.append((clock8,1,0,[load(efs),load(efs),load(None),action(1,16),action(2,1320)]))
 return rows
def fixture_text(cases):return ''.join(f'{c} {e} {p} {len(actions)} '+' '.join(f'{op} {v} '+('!' if data is None else data.hex() or '-') for op,v,data in actions)+'\n' for c,e,p,actions in cases)
def pcm_reference(o,efs,clock8,effect,rate=48000,count=144000):
 o.begin(clock8);assert o.load_file(efs)==0;assert o.invoke(0x3a64,(effect,))==0
 generation=o.reloads;time=0;reload_time=0;next_irq=(1996 if clock8 else 2458)*rate;clock=1996800 if clock8 else 2457600;out=bytearray()
 for _ in range(count):
  time+=clock
  while next_irq<=time:
   o.invoke(0x381e,irq=True)
   if generation!=o.reloads:generation=o.reloads;reload_time=next_irq
   next_irq+=o.read(0x954,'H')[0]*rate
  value=0 if not o.gate else 8192 if (time-reload_time)%(o.divisor*rate)<((o.divisor+1)//2)*rate else -8192
  out+=struct.pack('<h',value)
 return bytes(out)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','decoded-dir','exe','hdi','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);efs=ending_assets(a.hdi)['MIKO.EFS'];assert len(efs)==8284 and sha(efs)=='12045fed57d7c5a07da0047ae13c6607cbc78155cfbf5baa719fc310131de607';(out/'MIKO.EFS').write_bytes(efs)
 cases=fixtures(efs);fixture=fixture_text(cases).encode();(out/'fixtures.txt').write_bytes(fixture)
 # Even reference consumers must attest the supplied packed/decoded inputs.
 Original(a.target,a.decoded_dir,0x1000)
 if a.reference_dir:
  previous=json.loads((a.reference_dir/'receipt.json').read_text());assert previous['passed'] and previous['original_cpu_reexecuted'] and previous['target_sha256']==PACKED and previous['payload_sha256']==PAYLOAD and previous['efs_sha256']==sha(efs) and sha(fixture)==previous['fixture_sha256'];expected=(a.reference_dir/'original.txt').read_bytes();assert sha(expected)==previous['trace_sha256']
 else:
  traces=[]
  for load in (0x1000,0x2000):
   o=Original(a.target,a.decoded_dir,load);trace=b''.join(o.run(i,c) for i,c in enumerate(cases));traces.append(trace);(out/f'original-{load:04x}.txt').write_bytes(trace)
   print(f'original load{load:04x}: {len(cases)} cases complete',flush=True)
  assert traces[0]==traces[1];expected=traces[0]
 (out/'original.txt').write_bytes(expected);r=subprocess.run([str(a.exe.resolve()),'--replay',str(out/'fixtures.txt')],capture_output=True);(out/'native.txt').write_bytes(r.stdout);(out/'stderr.txt').write_bytes(r.stderr)
 if r.returncode or r.stdout!=expected:
  x=r.stdout.splitlines();y=expected.splitlines();at=next((i for i,(a,b) in enumerate(zip(x,y)) if a!=b),min(len(x),len(y)));(out/'mismatch.json').write_text(json.dumps(dict(line=at,actual=str(x[at:at+2]),expected=str(y[at:at+2]),returncode=r.returncode),indent=2));raise ValueError(f'beeper differs line{at}')
 pcm={};samples=0
 for clock8,effect in itertools.product((0,1),range(1,16)):
  name=f'c{clock8}-e{effect}.pcm';path=out/name
  if a.reference_dir:wave=(a.reference_dir/name).read_bytes();assert sha(wave)==previous['pcm'][name]
  else:
   waves=[pcm_reference(Original(a.target,a.decoded_dir,load),efs,clock8,effect) for load in (0x1000,0x2000)];assert waves[0]==waves[1];wave=waves[0]
  path.write_bytes(wave)
  for block in (144000,137):
   command=[str(a.exe.resolve()),'--pcm',str(clock8),'48000','144000',str(out/'MIKO.EFS'),str(effect),str(block)];r=subprocess.run(command,capture_output=True);assert r.returncode==0 and r.stdout==wave,(name,block,r.stderr[:100]);samples+=144000
  pcm[name]=sha(wave)
  print(f'offline PCM {name} agrees in both block partitions',flush=True)
 assert source_manifest(root)[0]==manifest
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),target_sha256=PACKED,payload_sha256=PAYLOAD,efs_sha256=sha(efs),hdi_sha256=sha(a.hdi.read_bytes()),cases=len(cases),trace_lines=len(expected.splitlines()),fixture_sha256=sha(fixture),trace_sha256=sha(expected),original_cpu_reexecuted=not bool(a.reference_dir),pcm=pcm,compared_samples=samples,reference_receipt_sha256=sha((a.reference_dir/'receipt.json').read_bytes()) if a.reference_dir else None,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('beeper PASS',len(cases),'cases',receipt['trace_lines'],'records',samples,'offline samples')
if __name__=='__main__':main()
