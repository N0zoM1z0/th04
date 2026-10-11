#!/usr/bin/env python3
"""Original complete MAINE delay/black fades versus native logical admissions.

The actual VSYNC_WAIT executes. Count1 changes are explicit one-pulse consumer
stimuli; palette_show is a guarded tone observation adapter. No physical CPU,
IRQ latency, palette-port or scanout acceptance follows from this projection.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest()
PINS={0x622:(130,'19e015ce0dfae0670711db894ccddad7142328054b3495967b70cdf1529f1f4b'),
      0xcca3:(21,'0d77d41527daea4e009dcbcdbf7fb8fc956243a9cc04dfd9dc2a289468243d2b'),
      0x2206:(38,'122568ac75a194b3118dd40772ae4e55352102a549344ffb08f2b3e3c53b21d0')}
def original_case(record,load,row):
 kind,argument,direction=row;body=bytearray(record['body'])
 for at,(size,pin) in PINS.items():assert sha(body[at:at+size])==pin
 for at in record['sites']:struct.pack_into('<H',body,at,(struct.unpack_from('<H',body,at)[0]+load)&65535)
 u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);u.mem_map(0,0x110000);u.mem_write(load*16,bytes(body));ds=load+record['dg'];base=ds*16
 read=lambda at:struct.unpack('<H',u.mem_read(base+at,2))[0]
 def write(at,value):u.mem_write(base+at,struct.pack('<H',value&65535))
 write(0xefa,65535);write(0xefc,0xbeef);write(0x132,31);u.mem_write(base+0x402,b'\xfb')
 elapsed=0;polls=0;done=False;waits=0;shows=[];counter_writes=[];errors=[]
 def code(cpu,address,size,_):
  nonlocal elapsed,polls,done,waits
  try:
   relative=address-load*16
   if relative==0xff00:done=True;cpu.emu_stop()
   elif relative==0x2206:waits+=1;polls=0
   elif relative==0x2225:
    if polls:elapsed+=1;write(0xefa,read(0xefa)+1)
    polls+=1
   elif kind=='D' and relative==0xccac:
    if polls:elapsed+=1;write(0xefa,read(0xefa)+1)
    polls+=1
   elif relative==0x19ec:
    shows.append((elapsed,read(0x132)))
    sp=cpu.reg_read(UC_X86_REG_SP);ip,cs=struct.unpack('<HH',cpu.mem_read(0x70000+sp,4))
    cpu.reg_write(UC_X86_REG_SP,sp+4);cpu.reg_write(UC_X86_REG_CS,cs);cpu.reg_write(UC_X86_REG_IP,ip)
  except BaseException as error:errors.append(repr(error));cpu.emu_stop()
 def memory(cpu,access,address,size,value,_):
  if base+0xefa<=address<base+0xefe:counter_writes.append((address-base,size,value))
 u.hook_add(unicorn.UC_HOOK_CODE,code);u.hook_add(unicorn.UC_HOOK_MEM_WRITE,memory)
 segment=0xcc7 if kind=='D' else 0;entry=0x33 if kind=='D' else (0x622 if direction else 0x666)
 for reg,value in ((UC_X86_REG_CS,load+segment),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x4321),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
 u.mem_write(0x7f000,struct.pack('<HHH',0xff00,load,argument&65535));u.emu_start((load+segment)*16+entry,0x10ffff,count=40000000)
 assert done and not errors and u.reg_read(UC_X86_REG_SP)==0xf006 and u.reg_read(UC_X86_REG_BP)==0x4321,(row,load,errors)
 assert read(0xefc)==0xbeef
 assert counter_writes==([(0xefa,2,0)] if kind=='D' else []),(row,counter_writes)
 projection=''.join(f'P {tick} {tone}\n' for tick,tone in shows)+f'N {elapsed} {read(0x132)} 3\n'
 return dict(row=row,load=f'{load:04x}',elapsed=elapsed,shows=shows,wait_calls=waits,counts=[read(0xefa),read(0xefc)],counter_writes=counter_writes,projection=projection)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dos-root',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--reference',type=Path);a=p.parse_args();sys.path.insert(0,str(a.dos_root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original
 record=original('maine');args=(-65537,-65536,-1,0,1,2,100,32767,32768,65535,65536,65537)
 rows=[('D',n,0) for n in args]+[('F',n,d) for n,d in itertools.product(args,(0,1))]
 prior=None
 if a.reference:
  prior=json.loads((a.reference/'receipt.json').read_text());assert prior['passed'] and prior['original_pins']==record['pins'] and prior['rows']==[list(x) for x in rows]
  assert prior['oracle_sha256']==sha(Path(__file__).read_bytes())
  for name,pin in prior['files'].items():assert sha((a.reference/name).read_bytes())==pin,name
 controls=prior['controls'] if prior else []
 if not prior:
  for load in (0x1000,0x3333):
   for row in rows:controls.append(original_case(record,load,row))
   print('Original complete delay/fades',hex(load),len(rows),'PASS',flush=True)
 expected=''.join(x['projection'] for x in controls[:len(rows)]).encode();assert expected==''.join(x['projection'] for x in controls[len(rows):]).encode()
 a.output.mkdir(parents=True,exist_ok=False);v=a.output/'vectors.txt';v.write_text(''.join(f'{k} {n} {d}\n' for k,n,d in rows))
 run=subprocess.run([str(a.native.resolve()),'--vectors',str(v.resolve())],capture_output=True);(a.output/'native.txt').write_bytes(run.stdout);(a.output/'stderr.txt').write_bytes(run.stderr);(a.output/'expected.txt').write_bytes(expected);(a.output/'original.json').write_text(json.dumps(controls,indent=2)+'\n')
 assert run.returncode==0 and not run.stderr and run.stdout==expected,'native MAINE logical wait/palette projection differs'
 j=dict(passed=True,rows=rows,controls=controls,original_pins=record['pins'],original_cases=len(controls),code_pins=PINS,native_sha256=sha(a.native.read_bytes()),oracle_sha256=sha(Path(__file__).read_bytes()),reference_sha256=sha((a.reference/'receipt.json').read_bytes()) if prior else None,files={x.name:sha(x.read_bytes()) for x in a.output.iterdir()},scope=__doc__)
 (a.output/'receipt.json').write_text(json.dumps(j,indent=2)+'\n');print('MAINE animation PASS',len(controls),'original cases',len(rows),'native vectors',flush=True)
if __name__=='__main__':main()
