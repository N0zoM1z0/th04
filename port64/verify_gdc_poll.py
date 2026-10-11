#!/usr/bin/env python3
"""Original VSYNC_WAIT dispatch/clear behavior and ideal native wait deadlines.

Counter values/GDC status are explicit consumer stimuli, not physical IRQ
latency measurements. Native raster/cadence checks use independent integer
arithmetic. No original opcode or original return is substituted.
"""
import argparse,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest()
CODE_SHA='989ba1d57373892c48f460097161f08d5391388535059d007327fda0f4e45b20'
HZ=2631575;H=106;V=440;R=407
def edge(epoch,index,adjust=0):return epoch+((index*V+R)*H*1000000000+HZ-1)//HZ+adjust
def edges(epoch,now,adjust=0):
    t=now-epoch-adjust
    return max(0,(t*HZ-R*H*1000000000)//(V*H*1000000000)+1)
def expected(row):
    epoch,phase,adjust,owned,inc,seed,steps=row;now=epoch+phase
    def count(pulses,acc):return pulses-(acc+pulses*inc)//65536
    one=two=count(seed,0)&65535;acc=seed*inc&65535
    if owned:
        pulses=edges(epoch,now,adjust);delta=count(pulses,acc);one=(one+delta)&65535;two=(two+delta)&65535;acc=(acc+pulses*inc)&65535
    result=[]
    for _ in range(steps):
        if owned:
            pulses=acc//(65536-inc)+1;at=edge(epoch,edges(epoch,now,adjust)+pulses-1,adjust)
            one=(one+1)&65535;two=(two+1)&65535;acc=(acc+pulses*inc)&65535
        else:at=edge(epoch,edges(epoch,now))
        result.append((at,at-now,one,two,acc,owned));now=at
    return result
def original_case(record,load,owner,initial,signals):
    body=bytearray(record['body']);assert sha(body[0x2648:0x266e])==CODE_SHA
    for at in record['sites']:struct.pack_into('<H',body,at,(struct.unpack_from('<H',body,at)[0]+load)&65535)
    cpu=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);cpu.mem_map(0,0x110000);cpu.mem_write(load*16,bytes(body));ds=load+record['dg'];base=ds*16
    cpu.mem_write(base+record['owner'],bytes([owner]));cpu.mem_write(base+record['count1'],struct.pack('<H',initial));cpu.mem_write(base+record['count2'],struct.pack('<H',0xbeef))
    reads=[];writes=[];done=False
    def code(u,address,size,_):
        nonlocal done
        if address==load*16+0xff00:done=True;u.emu_stop()
        elif owner and address==load*16+0x2667:
            assert len(reads)<len(signals),'counter stimulus exhausted'
            value=signals[len(reads)];cpu.mem_write(base+record['count1'],struct.pack('<H',value));reads.append(value)
    def port(u,port,size,_):
        assert not owner and port==0xa0 and size==1 and len(reads)<len(signals)
        value=signals[len(reads)];reads.append(value);return value
    def write(u,access,address,size,value,_):
        if base+record['count1']<=address<base+record['count2']+2:writes.append((address-base,size,value))
    cpu.hook_add(unicorn.UC_HOOK_CODE,code);cpu.hook_add(unicorn.UC_HOOK_INSN,port,None,1,0,UC_X86_INS_IN);cpu.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
    for reg,value in [(UC_X86_REG_CS,load),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0xabcd),(UC_X86_REG_EFLAGS,2)]:cpu.reg_write(reg,value)
    cpu.mem_write(0x7f000,struct.pack('<HH',0xff00,load));cpu.emu_start(load*16+0x2648,0x10ffff,count=1000)
    assert done and reads==signals and not writes and cpu.reg_read(UC_X86_REG_SP)==0xf004 and cpu.reg_read(UC_X86_REG_BP)==0xabcd
    one,two=struct.unpack('<HH',cpu.mem_read(base+record['count1'],4));assert two==0xbeef and one==(signals[-1] if owner else initial)
    return dict(load=f'{load:04x}',owner=owner,initial=initial,signals=signals,reads=reads,counts=[one,two],counter_writes=writes,sp=cpu.reg_read(UC_X86_REG_SP))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.root/'scripts/runtime'));from verify_dos_vsync_lifecycle import original
    record=original('op');controls=[]
    for load,owner,initial in itertools.product((0x1000,0x3333),(0,1,251,255),(0,4,100,65535)):
        if owner:signals=[initial,initial,0 if initial else 1]
        else:signals=[0x61,0x20,0x01,0x40,0x21]
        controls.append(original_case(record,load,owner,initial,signals))
    rows=list(itertools.product((0,1000000000000),(0,edge(0,0)-1,edge(0,0),edge(0,0)+1),(0,100,40000000),(0,1),(0,13311,65535),(0,4,65535),(3,)))
    a.output.mkdir(parents=True,exist_ok=False);fixture=a.output/'vectors.txt';fixture.write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))
    result=subprocess.run([str(a.native.resolve()),'--vectors',str(fixture.resolve())],capture_output=True,check=True);assert not result.stderr;wanted=''.join(' '.join(map(str,line))+'\n' for row in rows for line in expected(row)).encode();assert result.stdout==wanted,'native deadline/counter stream differs'
    (a.output/'native.txt').write_bytes(result.stdout);(a.output/'expected.txt').write_bytes(wanted);(a.output/'original.json').write_text(json.dumps(controls,indent=2)+'\n')
    source=Path(__file__).resolve().parent
    receipt=dict(passed=True,original=record['pins'],entry='0000:2648',extent_size=38,code_sha256=CODE_SHA,original_cases=len(controls),native_vectors=len(rows),native_waits=len(rows)*3,native_sha256=sha(a.native.read_bytes()),source={name:sha((source/name).read_bytes()) for name in ['pc98_vsync.hpp','op_startup.hpp','op_startup.cpp','gdc_poll_contracts.cpp','verify_gdc_poll.py','CMakeLists.txt']},files={q.name:sha(q.read_bytes()) for q in a.output.iterdir()},scope='Original dispatch/no counter clear at two relocated loads; explicit Count1/status stimuli. Independent ideal raster/cadence/native wrap deadline checks, not measured physical CPU/poll/ISR timing.')
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('GDC/owned wait PASS',len(controls),'original controls',len(rows),'native vectors',len(rows)*3,'waits',flush=True)
if __name__=='__main__':main()
