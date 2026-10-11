#!/usr/bin/env python3
"""Original WORD consumers/IRQ recurrence and independent big-integer clock vectors.

Consumer word changes and IRQ injections are explicit stimuli. Bulk arithmetic
and ideal raster deadlines do not measure CPU/ISR or physical scanout latency.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest()
ENTRIES={'main':(0x130e,0xd7,'3c79ff0bb4e74ee6e2aa9ac688bf1b849c015acd31c7d7ff135b2ca455b7c26f'),
 'op':(0xda1,0x2b,'1683f148a8bda60e6dbbe69510b3d79544e84057d6b7721facfaed4820f134aa'),
 'maine':(0xcc7,0x33,'0d77d41527daea4e009dcbcdbf7fb8fc956243a9cc04dfd9dc2a289468243d2b')}
HZ=2631575;H=106;V=440;R=407
def consumer(record,artifact,load,argument,owned):
 seg,off,pin=ENTRIES[artifact];at=seg*16+off;image=bytearray(record['body']);assert sha(image[at:at+21])==pin
 for site in record['sites']:struct.pack_into('<H',image,site,(struct.unpack_from('<H',image,site)[0]+load)&65535)
 u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);u.mem_map(0,0x110000);u.mem_write(load*16,bytes(image));base=(load+record['dg'])*16
 for address,value in ((record['count1'],65535),(record['count2'],0xbeef)):u.mem_write(base+address,struct.pack('<H',value))
 u.mem_write(base+record['owner'],bytes([owned]));minimum=argument&65535;signals=[0] if not minimum else [0,0,minimum-1,minimum];reads=[];writes=[];done=False;errors=[]
 def code(cpu,address,size,_):
  nonlocal done
  try:
   if address==0x60000:done=True;cpu.emu_stop()
   elif address==load*16+at+9:
    index=len(reads);value=signals[index] if owned or not minimum else 0
    cpu.mem_write(base+record['count1'],struct.pack('<H',value));reads.append(value)
  except BaseException as e:errors.append(repr(e));cpu.emu_stop()
 def memory(cpu,access,address,size,value,_):
  if base+record['count1']<=address<base+record['count2']+2:writes.append((address-base,size,value))
 u.hook_add(unicorn.UC_HOOK_CODE,code);u.hook_add(unicorn.UC_HOOK_MEM_WRITE,memory)
 for reg,value in ((UC_X86_REG_CS,load+seg),(UC_X86_REG_DS,load+record['dg']),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x4321),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
 u.mem_write(0x7f000,struct.pack('<HHH',0,0x6000,minimum));u.emu_start(load*16+at,0x10ffff,count=1000)
 assert not errors and writes==[(record['count1'],2,0)] and struct.unpack('<H',u.mem_read(base+record['count2'],2))[0]==0xbeef
 expected_return=bool(owned or not minimum);assert done==expected_return
 if done:assert reads==signals and u.reg_read(UC_X86_REG_SP)==0xf006 and u.reg_read(UC_X86_REG_BP)==0x4321
 else:assert reads and not any(reads)
 return dict(artifact=artifact,load=f'{load:04x}',entry=f'{seg:04x}:{off:04x}',argument=argument,minimum=minimum,owner=owned,returned=done,reads=reads,writes=writes,count2=0xbeef,code_sha256=pin)
def arithmetic(one,two,acc,inc,n):
 total=acc+n*inc;counted=n-total//65536
 return (one+counted)&65535,(two+counted)&65535,total&65535,counted
def edge(epoch,index,adjust):return epoch+((index*V+R)*H*1000000000+HZ-1)//HZ+adjust
def edges(phase,adjust):return max(0,((phase-adjust)*HZ-R*H*1000000000)//(V*H*1000000000)+1)
def expected(row):
 mode,active,inc,*args=row
 if mode=='B':
  pre,n=args;b1,b2,acc,_=arithmetic(0,0,0,inc,pre);a1,a2,next_acc,count=arithmetic(b1,b2,acc,inc,n) if active else (b1,b2,acc,0)
  return [b1,b2,acc,a1,a2,next_acc,count,active]
 epoch,phase,adjust,pre,argument=args;elapsed=edges(phase,adjust);b1,b2,acc,_=arithmetic(0,0,0,inc,pre+elapsed);minimum=argument&65535;now=epoch+phase;prefix=[b1,b2,acc,0,b2,acc,now,minimum,int(minimum==0)]
 if not active and minimum:return prefix+['BLOCKED']
 pulses=0 if not minimum else ((minimum-1)*65536+acc)//(65536-inc)+1;finish=now if not pulses else edge(epoch,elapsed+pulses-1,adjust);a1,a2,last,_=arithmetic(0,b2,acc,inc,pulses)
 return prefix+[finish-now,finish,a1,a2,last,1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--reference',type=Path);a=p.parse_args();sys.path.insert(0,str(a.root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original;from verify_dos_vsync_wait import original_wait,execute
 records={artifact:original(artifact) for artifact in ENTRIES};pins={k:v['pins'] for k,v in records.items()};args=(-65537,-65536,-1,0,1,2,100,32767,32768,65535,65536,65537);controls=[];irqs=[]
 if a.reference:
  prior=json.loads((a.reference/'receipt.json').read_text());assert prior['passed'] and prior['original_pins']==pins and prior['oracle_sha256']==sha(Path(__file__).read_bytes())
  for name,pin in prior['files'].items():assert sha((a.reference/name).read_bytes())==pin,name
  controls=prior['consumer_controls'];irqs=prior['irq_controls']
 else:
  for artifact,record in records.items():
   for load,arg,owner in itertools.product((0x1000,0x3333),args,(0,251)):controls.append(consumer(record,artifact,load,arg,owner))
   for load,initial,irq in itertools.product((0x1000,0x3333),(0,65535),((0,0),(13311,60000),(65535,3))):
    observed=execute(original_wait(artifact),load,251,initial,0,irq);irqs.append(dict(artifact=artifact,load=f'{load:04x}',initial=initial,irq=irq,observed=observed))
   print('Original consumers/ISR',artifact,'PASS',flush=True)
 maximum=(1<<64)-1;rows=[('B',active,inc,pre,n) for active,inc,pre,n in itertools.product((0,1),(0,1,13311,65535),(0,1,65535,65536,maximum),(0,1,65535,65536,4294901760,maximum-1,maximum))]
 rows += [('D',active,inc,epoch,phase,adjust,pre,arg) for active,inc,epoch,phase,adjust,pre,arg in itertools.product((0,1),(0,13311,65535),(0,1000000000000),(0,edge(0,0,0),1000000000),(0,40000000),(0,65535),args)]
 a.output.mkdir(parents=True,exist_ok=False);v=a.output/'vectors.txt';v.write_text(''.join(' '.join(map(str,row))+'\n' for row in rows));wanted=''.join(' '.join(map(str,expected(row)))+'\n' for row in rows).encode();run=subprocess.run([str(a.native.resolve()),'--vectors',str(v.resolve())],capture_output=True)
 (a.output/'native.txt').write_bytes(run.stdout);(a.output/'expected.txt').write_bytes(wanted);(a.output/'stderr.txt').write_bytes(run.stderr);assert run.returncode==0 and not run.stderr and run.stdout==wanted,'counter/delay big-integer projection differs'
 (a.output/'original.json').write_text(json.dumps(dict(consumers=controls,irqs=irqs),indent=2)+'\n')
 j=dict(passed=True,original_pins=pins,consumer_controls=controls,irq_controls=irqs,native_vectors=len(rows),bulk_vectors=sum(row[0]=='B' for row in rows),delay_vectors=sum(row[0]=='D' for row in rows),native_sha256=sha(a.native.read_bytes()),oracle_sha256=sha(Path(__file__).read_bytes()),files={x.name:sha(x.read_bytes()) for x in a.output.iterdir()},scope=__doc__)
 (a.output/'receipt.json').write_text(json.dumps(j,indent=2)+'\n');print('COUNTER/DELAY PASS',len(controls),'original consumers',len(irqs),'real ISR controls',len(rows),'big-integer vectors',flush=True)
if __name__=='__main__':main()
