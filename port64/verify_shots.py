#!/usr/bin/env python3
"""Compare four native player-shot routes and lifecycle/hit state with original MAIN CPU."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_MEM_READ
from unicorn.x86_const import (UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_SS,
    UC_X86_REG_SP, UC_X86_REG_BP, UC_X86_REG_IP, UC_X86_REG_EFLAGS, UC_X86_REG_AX)


def fixtures():
    def checkpoint(operation='F', character=0, route=0, level=0, time=18, cycle=0,
                   target=0, pool=0, laser_time=0, laser_ring=0):
        entities=[]
        for i in range(68):
            flag=1 if pool==2 or (pool==1 and i%3==0) else 0
            entities.append([flag,i*3%256,320+i,400+i,-i,i,i-33,33-i,28+i%8,i%16,173])
        return dict(operation=operation,character=character,route=route,level=level,
            target_present=bool(target),target=(512 if target==1 else 5632,512),
            player=(3072,5200),options=(3105,5167),center=(3072,2400),radius=(1024,640),
            context=(0,0,1,0),time=time,cycle=cycle,spark=255,laser_time=laser_time,
            laser_style=4,laser_ring=laser_ring,laser_motion=(3039,5233,3006,5266,11,-17),
            old_options=(3039,5233),score=0xfffffff0,entities=entities,cache=[])
    for character,route,level,time,cycle,pool in itertools.product(
            range(2),range(2),range(10),(18,12,6),(0,1,2,255),range(3)):
        for target in (range(3) if character==0 and route==0 and level>=2 else (0,)):
            yield checkpoint(character=character,route=route,level=level,time=time,
                             cycle=cycle,target=target,pool=pool)
    for level,time,cycle in itertools.product(range(2,10),(0,32,47,48,64),(0,3,4,7,255)):
        yield checkpoint(character=1,level=level,laser_time=time,laser_ring=cycle)
    for time,pressed in itertools.product(range(256),range(2)):
        yield checkpoint('T',time=time,target=pressed)
    for iteration in range(64):
        c=checkpoint('U',laser_time=iteration)
        for i,e in enumerate(c['entities']):
            e[0]=(i+iteration)%21;e[1]=255
            e[2:4]=[(-129,-128,-127,0,6271,6272,32767,-32768)[i%8],
                    (-129,-128,-127,0,6015,6016,32767,-32768)[(i+iteration)%8]]
            e[6:8]=[(iteration-32)*6,(32-iteration)*6];e[8]=65535
        yield c
    for bombing,boss,mod2,mod4,count,phase in itertools.product(
            range(2),range(2),range(2),range(4),(0,1,2,8,68),(0,1,3,255)):
        for operation in ('H','D'):
            c=checkpoint(operation,laser_time=64)
            c['context']=(bombing,boss,mod2,mod4);c['spark']=phase
            for i,e in enumerate(c['entities']):
                e[0]=1;e[2:4]=[3072+(i%4-2)*384,2400+(i%3-1)*640]
                e[6:8]=[(i-32)*7,(32-i)*9];e[9]=255
            c['cache']=[(*c['entities'][i][2:4],i) for i in range(count)]
            yield c


def input_row(c):
    values=[c['character'],c['route'],c['level'],int(c['target_present']),*c['target'],
        *c['player'],*c['options'],*c['center'],*c['radius'],*c['context'],c['time'],
        c['cycle'],c['spark'],c['laser_time'],c['laser_style'],c['laser_ring'],
        *c['laser_motion'],*c['old_options'],c['score']]
    values+=list(itertools.chain.from_iterable(c['entities']))
    values += [len(c['cache']),*itertools.chain.from_iterable(c['cache'])]
    return c['operation']+' '+' '.join(map(str,values))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    sha=lambda b:hashlib.sha256(b).hexdigest()
    target=args.target.read_bytes()
    if len(target)!=156258 or sha(target)!='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b':
        raise ValueError('MAIN identity mismatch')
    if struct.unpack_from('<H',target,8)[0]*16!=6144 or struct.unpack_from('<H',target,6)[0]!=1136:
        raise ValueError('MAIN header mismatch')
    module=bytearray(target[6144:]);table=struct.unpack_from('<H',target,24)[0]
    for i in range(1136):
        off,seg=struct.unpack_from('<HH',target,table+i*4);at=seg*16+off
        struct.pack_into('<H',module,at,(struct.unpack_from('<H',module,at)[0]+0x2000)&65535)
    root=Path(__file__).resolve().parents[1]
    entries={r['tasm_proc']:int(r['payload_offset'],0)-0xaaf0
        for r in csv.DictReader((root/'config/th04_function_boundaries.csv').open())
        if r['artifact']=='th04-main' and r['tasm_proc'].startswith('shot_')}
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x110000);u.mem_write(0x20000,bytes(module))
    ds=0x80000;cs=0x2aaf
    def write(at,fmt,*v):u.mem_write(ds+at,struct.pack(fmt,*v))
    def read(at,fmt):return struct.unpack(fmt,u.mem_read(ds+at,struct.calcsize(fmt)))
    sparks=[]
    fired=[0]
    def hook(engine,address,size,unused):
        if address==cs*16+0x60c0:
            # Scope is the trigger decision, stopping before the indirect
            # producer and SE call. Producer bodies are exercised separately.
            fired[0]+=1;engine.reg_write(UC_X86_REG_IP,0x60d7)
        if address==0x33a9*16+0x39a:
            sp=engine.reg_read(UC_X86_REG_SP);ret_ip,ret_cs,count,radius,y,x=struct.unpack(
                '<HHHHhh',engine.mem_read(0x70000+sp,12))
            if count!=1 or radius!=128:raise ValueError('unexpected original spark request')
            sparks.append((x,y));engine.reg_write(UC_X86_REG_SP,sp+12)
            engine.reg_write(UC_X86_REG_CS,ret_cs);engine.reg_write(UC_X86_REG_IP,ret_ip)
    u.hook_add(UC_HOOK_CODE,hook)
    cases=list(fixtures());fixture=out/'fixtures.txt'
    fixture.write_text('\n'.join(map(input_row,cases))+'\n')
    expected=[];counts={}
    for index,c in enumerate(cases):
        u.mem_write(ds,bytes(65536));u.mem_write(ds,bytes(module[0x21340:]))
        write(0x3dcc,'256B',*reversed([(i*73+19)&255 for i in range(256)]));write(0x3ecc,'H',0)
        write(0x4666,'B',c['time']);write(0x4362,'B',c['cycle']);write(0x4640,'B',c['spark'])
        write(0x42c8,'H',c['laser_time']);write(0x42ca,'B',c['laser_style']);write(0x18da,'B',c['laser_ring'])
        write(0x42cc,'6h',*c['laser_motion']);write(0x466c,'2h',*c['old_options'])
        write(0x464e,'2h',*c['player']);write(0x4642,'2h',*(c['target'] if c['target_present'] else (0,-15984)))
        write(0x435a,'I',c['score'])
        for i,e in enumerate(c['entities']):write(0xb55e+i*18,'BB6hHBB',*e)
        write(0x463e,'H',len(c['cache']))
        for i,(x,y,slot) in enumerate(c['cache']):write(0x44a6+i*6,'hhH',x,y,0xb55e+slot*18)
        operation=c['operation'];counts[operation]=counts.get(operation,0)+1;sparks.clear()
        if operation=='F':
            char='reimu' if not c['character'] else 'marisa';level=c['level']
            symbol=f'shot_{char}_'+('' if level<2 else ('b_' if c['route'] else 'a_'))+f'l{level}'
            ip=entries[symbol]
        elif operation=='U':ip=0x59c6;write(0x466c,'2h',*c['options'])
        elif operation=='T':ip=0x6092;write(0x3974,'B',0x20 if c['target_present'] else 0)
        else:
            ip=0x5ac9;write(0x449e,'4h',*c['center'],*c['radius'])
            bomb,boss,mod2,mod4=c['context']
            write(0x4368,'B',bomb);write(0x1b5c,'B',boss);write(0x538c,'BB',mod2,mod4)
        for repeat in range(2 if operation=='D' else 1):
            sparks.clear()
            fired[0]=0
            for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):
                u.reg_write(reg,value)
            far=operation in ('H','D')
            u.mem_write(0x7e000,struct.pack('<HH',0xf000,cs))
            stop=0x60d7 if operation=='T' else 0xf000
            u.emu_start(cs*16+ip,cs*16+stop,count=20000)
            if u.reg_read(UC_X86_REG_IP)!=stop or u.reg_read(UC_X86_REG_SP)!=0xe000+(0 if operation=='T' else (4 if far else 2)):
                raise ValueError(f'original shot return failed at case {index}')
        values=[]
        for i in range(68):values.extend(read(0xb55e+i*18,'BB6hHBB'))
        count=read(0x463e,'H')[0];values.append(count)
        for i in range(count):
            x,y,ptr=read(0x44a6+i*6,'hhH');values.extend((x,y,(ptr-0xb55e)//18))
        for at,fmt in [(0x4666,'B'),(0x4362,'B'),(0x4640,'B'),(0x42c8,'H'),(0x42ca,'B'),
                       (0x18da,'B'),(0x42cc,'6h'),(0x466c,'2h'),(0x435a,'I'),(0x3ecc,'H')]:
            values.extend(read(at,fmt))
        values.extend((fired[0] if operation=='T' else (u.reg_read(UC_X86_REG_AX) if operation in ('H','D') else 0),len(sparks)))
        values.extend(itertools.chain.from_iterable(sparks));expected.append(values)
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--vectors',str(fixture)]
    result=subprocess.run(command,text=True,capture_output=True,check=True,env=env)
    actual=[list(map(int,row.split())) for row in result.stdout.splitlines()]
    if len(actual)!=len(expected):raise ValueError('native shot vector count mismatch')
    for index,(want,got) in enumerate(zip(expected,actual)):
        if want!=got:
            mismatch={'case':index,'input':input_row(cases[index]),'expected':want,'actual':got}
            (out/'mismatch.json').write_text(json.dumps(mismatch,indent=2)+'\n')
            first=next((i for i,(x,y) in enumerate(zip(want,got)) if x!=y),min(len(want),len(got)))
            raise ValueError(f'shot mismatch case {index} field {first}: {want[first:first+4]} != {got[first:first+4]}')
    normalized='\n'.join(' '.join(map(str,v)) for v in expected)+'\n'
    (out/'vectors.txt').write_text(normalized)
    # Independent negative control for the capacity guard. DOS counts only
    # occupied slots: a final-slot success followed by another request reads
    # beyond the true pool. Observe it in disposable memory, never product.
    u.mem_write(ds+0xb55e,bytes(18*80))
    for i in range(67):write(0xb55e+i*18,'B',1)
    overrun=[]
    def read_hook(engine,access,address,size,value,unused):
        if size==1 and address>=ds+0xb55e+18*68 and (address-ds-0xb55e)%18==0:
            overrun.append(address-ds)
    handle=u.hook_add(UC_HOOK_MEM_READ,read_hook,begin=ds+0xb55e+18*68,end=ds+0xb55e+18*80-1)
    for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
        (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
    u.mem_write(0x7e000,struct.pack('<H',0xf000))
    u.emu_start(cs*16+entries['shot_marisa_b_l9'],cs*16+0xf000,count=20000)
    u.hook_del(handle)
    if not overrun or u.reg_read(UC_X86_REG_IP)!=0xf000:
        raise ValueError('original allocator overrun negative control failed')
    receipt=dict(schema_version=1,passed=True,observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
        target_sha256=sha(target),native_sha256=sha(args.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),
        vectors_sha256=sha(normalized.encode()),cases=counts,command=command,
        allocator_negative_control=dict(original_outside_pool_flag_reads=[f'{at:04X}' for at in overrun],
            first_invalid_slot=68,host_behavior='Stops at real capacity; separately covered by shot contracts.'),
        target_scope='MAIN.EXE main_01 relative 0AAF; relocated at 2000; isolated DS 8000 copied from initialized DGROUP',
        unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
        limits='Software shot producers/update/hit state only; spark calls recorded and intercepted (no spark RNG), sound/render/timing/enemy integration excluded. Invalid original allocator overrun excluded; portable capacity guard separately tested.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(passed=True,cases=counts,receipt=str(out/'receipt.json'))))


if __name__=='__main__':main()
