#!/usr/bin/env python3
"""Independent original-CPU controls for native STD waves and enemy bytecode/pool."""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
from unicorn.x86_const import (UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_SS,
    UC_X86_REG_SP, UC_X86_REG_BP, UC_X86_REG_IP, UC_X86_REG_EFLAGS, UC_X86_REG_AX)
from probe_assets import main_assets


sha=lambda b:hashlib.sha256(b).hexdigest()


class Original:
    def __init__(self,target):
        self.target=target
        if len(target)!=156258 or sha(target)!='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b':
            raise ValueError('MAIN identity mismatch')
        if struct.unpack_from('<H',target,8)[0]*16!=6144 or struct.unpack_from('<H',target,6)[0]!=1136:
            raise ValueError('MAIN header mismatch')
        self.module=bytearray(target[6144:]);at=struct.unpack_from('<H',target,24)[0]
        for i in range(1136):
            off,seg=struct.unpack_from('<HH',target,at+i*4);site=seg*16+off
            struct.pack_into('<H',self.module,site,(struct.unpack_from('<H',self.module,site)[0]+0x2000)&65535)
        self.u=Uc(UC_ARCH_X86,UC_MODE_16);self.u.mem_map(0,0x110000)
        self.u.mem_write(0x20000,bytes(self.module));self.events=[];self.draws=[];self.script_offsets=[];self.schedule_only=False
        self.u.hook_add(UC_HOOK_CODE,self.hook)
        self.reset()

    def reset(self):
        self.u.mem_write(0x80000,bytes(65536));self.u.mem_write(0x80000,bytes(self.module[0x21340:]))
        self.write(0x3dcc,'256B',*reversed([(i*73+19)&255 for i in range(256)]))
        self.write(0x3ecc,'H',0);self.write(0xbcc4,'H',0xf101);self.write(0xbcc0,'H',0xf102)
        self.events.clear()
        self.draws.clear()

    def write(self,at,fmt,*values):self.u.mem_write(0x80000+at,struct.pack(fmt,*values))
    def read(self,at,fmt):return struct.unpack(fmt,self.u.mem_read(0x80000+at,struct.calcsize(fmt)))

    def hook(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.schedule_only and cs==0x33a9 and ip==0x4263:
            ret,item,y,x,script=struct.unpack('<HHhhH',u.mem_read(0x70000+sp,10))
            self.events.append([script,x,y,item&255]);u.reg_write(UC_X86_REG_SP,sp+10);u.reg_write(UC_X86_REG_IP,ret)
            return
        if cs==0x33a9 and ip in (0xf101,0xf102,0x9fa8):
            ret=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0]
            if ip==0xf102:
                b=u.mem_read(0x853a2,18);x,y=struct.unpack_from('<hh',b,2)
                self.events.append([0,b[0],b[1],x,y,b[10],b[11],b[12],b[13],b[14]])
            if ip==0x9fa8:
                item,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+2,6))
                self.events.append([3,x,y,item&255])
            u.reg_write(UC_X86_REG_SP,sp+(8 if ip==0x9fa8 else 2));u.reg_write(UC_X86_REG_IP,ret)
        elif (cs,ip) in ((0x330e,0x7d2),(0x2aaf,0xb92),(0x33a9,0x39a)):
            ret_ip,ret_cs=struct.unpack('<HH',u.mem_read(0x70000+sp,4))
            if cs==0x330e:
                value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]
                self.events.append([1,value&255]);cleanup=6
            elif cs==0x2aaf:
                value,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6))
                self.events.append([2,x,y,value&255]);cleanup=10
            else:
                count,radius,y,x=struct.unpack('<HHhh',u.mem_read(0x70000+sp+4,8))
                self.events.append([4,x,y,radius,count]);cleanup=12
            u.reg_write(UC_X86_REG_SP,sp+cleanup);u.reg_write(UC_X86_REG_CS,ret_cs);u.reg_write(UC_X86_REG_IP,ret_ip)
        elif cs==0x2000 and ip in (0x2d3e,0x2b78):
            ret_ip,ret_cs=struct.unpack('<HH',u.mem_read(0x70000+sp,4))
            white=ip==0x2b78;skip=4 if white else 0
            pattern,y,x=struct.unpack('<HHh',u.mem_read(0x70000+sp+4+skip,6))
            self.draws.append([x,y,pattern,int(white)])
            u.reg_write(UC_X86_REG_SP,sp+10+skip);u.reg_write(UC_X86_REG_CS,ret_cs);u.reg_write(UC_X86_REG_IP,ret_ip)

    def context(self,rank,performance,scroll,x,y):
        self.write(0x4348,'B',rank);self.write(0x5395,'B',performance)
        self.write(0x427a,'h',scroll);self.write(0x464e,'hh',x,y)

    def call(self,ip,far=False,cs=0x33a9):
        u=self.u
        for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
            (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
        u.mem_write(0x7e000,struct.pack('<HH',0xf000,cs))
        u.emu_start(cs*16+ip,cs*16+0xf000,count=200000)
        if u.reg_read(UC_X86_REG_IP)!=0xf000 or u.reg_read(UC_X86_REG_SP)!=0xe000+(4 if far else 2):
            raise ValueError(f'original enemy call failed at {ip:04X}')
        return u.reg_read(UC_X86_REG_AX)&255

    def normalized_pool(self):
        records=bytearray(self.u.mem_read(0x88a92,32*64))
        ids={off:i for i,off in enumerate(self.script_offsets)}
        ids[0]=65535
        for i in range(32):
            ptr=struct.unpack_from('<H',records,i*64+22)[0]
            if ptr not in ids:raise ValueError('original enemy references unknown script')
            struct.pack_into('<H',records,i*64+22,ids[ptr])
        return records


def instruction(op,variant):
    d=(0,1,254,255)[variant];angle=(0,64,129,255)[variant]
    operands={0:[],1:[angle,24,d],2:[d],3:[24,d],4:[angle,24,129,d],5:[angle,24,129,255,128,d],
        6:[d],7:[24,129,255,d],8:[24,129,128,d],9:[angle,24],10:[129],11:[d],12:[128],13:[d],14:[255,128,d],
        16:[12,0xff,0xff,0xff,0x7f],17:[],18:[angle,24],19:[angle,24],20:[24],32:[],
        33:[2,0x80,0xff,0x81,0xff,0x2e,angle,42,52,3],34:[2],35:[0x80,0xff,0x81,0xff],
        36:[angle],37:[129],38:[42],39:[255],40:[0x2e],41:[3],42:[52],43:[],44:[d],45:[],46:[],48:[16],
        128:[0,3],129:[0,3],130:[],131:[],132:[],133:[4,4],134:[3],135:[12],136:[],137:[],
        138:[0x80,0xff,0x81,0xff],139:[0x80,0xff,0x81,0xff],140:[],141:[],142:[255],143:[2]}
    return [op,*operands[op]]


def vm_fixtures():
    opcodes=list(range(15))+list(range(16,21))+list(range(32,47))+[48]+list(range(128,144))
    def record(phase,variant):
        b=bytearray((i*37+19)&255 for i in range(64))
        b[0]=1;b[1]=255;struct.pack_into('<6h',b,2,3072,1800,3040,1768,17,-19)
        struct.pack_into('<HHHHH',b,16,23,0x1234,250,0,0)
        b[26]=phase;b[27]=variant;struct.pack_into('<h',b,28,24)
        b[30]=(0,64,129,255)[variant];b[31]=129;b[32]=b[33]=0
        return b
    for op,rank,phase,variant in itertools.product(opcodes,range(5),(0,1,254,255),range(4)):
        yield [rank,(4,16,34,255)[variant],(0,16,128,-16)[variant],3072,5120,65530],record(phase,variant),instruction(op,variant)+[6,0,0]
    for rank,performance,interval in itertools.product(range(5),range(256),(0,16,128,255)):
        yield [rank,performance,0,3072,5120,0],record(0,0),[44,interval,6,0,0]
    for axis,edge,velocity,phase in itertools.product((0,1),(-257,-256,-255,6143,6144,6399,6400,6655,6656,32767,-32768),(-128,0,128),(0,1)):
        b=record(phase,0);b[32]=b[33]=1
        struct.pack_into('<h',b,2+axis*2,edge);struct.pack_into('<h',b,10+axis*2,velocity)
        # Scroll movement preserves X only on subsequent instruction frames.
        yield [1,16,velocity,3072,5120,65535],b,[11,1,0]
    # True backward/absolute loops re-execute a previous immediate operation.
    for op in (128,129):
        b=record(0,0);struct.pack_into('<h',b,24,2)
        yield [1,16,0,3072,5120,0],b,[37,9,op,0 if op==128 else 2,3,6,0,0]


def run_host(args,*options):
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),*map(str,options)]
    rows=subprocess.run(command,env=env,capture_output=True,text=True,check=True).stdout.strip().splitlines()
    return [' '.join(row.split()) for row in rows]


def pool_controls(original,args,out):
    inputs=[];expected=[]
    variants=itertools.product((0,1,2,3,128,159,160,255),(-32768,-2,-1,0,1,10,32767),(0,1,24,255),(False,True),(False,True))
    for index,(flag,hp,damage,collision,bomb) in enumerate(variants):
        original.reset();original.context(1,16,0,3072,1800 if collision else 5120)
        entity=bytearray(64);entity[0]=flag;entity[1]=index&255
        struct.pack_into('<6h',entity,2,3072,1800,3072,1800,-19,128)
        entity[14]=12;struct.pack_into('<h',entity,16,hp);struct.pack_into('<H',entity,20,65530)
        entity[35]=255;entity[37]=4;entity[38]=4;entity[40]=entity[42]=1
        # Native handle 0, original script pointer 0100 in ES9000.
        target_entity=bytearray(entity);struct.pack_into('<H',target_entity,22,0x100)
        original.u.mem_write(0x88a92,bytes(target_entity));original.write(0x918,'H',0x9000)
        original.u.mem_write(0x90100,bytes([6,30,0]))
        original.write(0x538c,'BB',index%2,index%4);original.write(0x4368,'B',int(bomb))
        original.write(0x4640,'B',index%4);laser=64 if index%3==0 else 0
        original.write(0x42c8,'H',laser);original.write(0x42cc,'hh',3072,5120)
        original.write(0x463e,'H',2)
        for i in range(2):
            original.write(0xb55e+i*18,'BB6hHBB',1,0,3072,1800,0,0,-19,-128,0,damage,0)
            original.write(0x44a6+i*6,'hhH',3072,1800,0xb55e+i*18)
        original.call(0x43c9,far=True);original.draws.clear();original.call(0x5c23,cs=0x2aaf)
        result=bytearray(original.u.mem_read(0x88a92,64));struct.pack_into('<H',result,22,0)
        values=[*result,*original.read(0x1b5e,'HH'),*original.read(0x435a,'I'),
                *original.read(0x4669,'B'),*original.read(0x4642,'hh')]
        for i in range(2):
            record=original.u.mem_read(0x8b55e+i*18,18)
            values.extend((record[0],struct.unpack_from('<H',record,14)[0],*struct.unpack_from('<hh',record,10)))
        values.extend((*original.read(0x4640,'B'),len(original.events),*itertools.chain.from_iterable(original.events)))
        expected.append(values)
        context=[1,16,0,3072,1800 if collision else 5120,int(bomb),index%2,index%4]
        inputs.append(' '.join(map(str,[*context,*entity,damage,index%4,laser])))
    fixture=out/'pool-fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n')
    actual=[list(map(int,row.split())) for row in run_host(args,'--pool-vectors',fixture)]
    if len(actual)!=len(expected):raise ValueError('enemy pool vector count differs')
    for index,(want,got) in enumerate(zip(expected,actual)):
        if want!=got:
            (out/'pool-mismatch.json').write_text(json.dumps(dict(case=index,input=inputs[index],expected=want,actual=got),indent=2)+'\n')
            raise ValueError(f'enemy hit/lifecycle case {index} differs')
    trace=out/'pool-vectors.txt';trace.write_text('\n'.join(' '.join(map(str,row)) for row in expected)+'\n')
    return dict(cases=len(expected),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',type=Path,required=True);p.add_argument('--hdi',type=Path,required=True)
    p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--vm-only',action='store_true')
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    original=Original(args.target.read_bytes());cases=list(vm_fixtures());inputs=[];expected=[]
    for index,(context,entity,script) in enumerate(cases):
        original.reset();original.context(*context[:5]);original.write(0x1b5e,'H',context[5])
        target_entity=bytearray(entity);struct.pack_into('<H',target_entity,22,0x100)
        original.u.mem_write(0x88a92,bytes(target_entity));original.write(0x464a,'H',0x8a92)
        original.write(0x918,'H',0x9000);original.u.mem_write(0x90100,bytes(script))
        try:returned=original.call(0x1b4d)
        except Exception:
            (out/'cpu-failure.json').write_text(json.dumps(dict(case=index,context=context,entity=list(entity),
                script=script,cs=original.u.reg_read(UC_X86_REG_CS),ip=original.u.reg_read(UC_X86_REG_IP)),indent=2)+'\n')
            raise
        result=bytearray(original.u.mem_read(0x88a92,64));struct.pack_into('<H',result,22,0)
        values=[*result,*original.read(0x1b5e,'H'),*original.read(0x3ecc,'H'),returned,len(original.events)]
        values.extend(itertools.chain.from_iterable(original.events));expected.append(values)
        inputs.append(' '.join(map(str,[*context,*entity,len(script),*script])))
    fixture=out/'vm-fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n')
    actual=[list(map(int,row.split())) for row in run_host(args,'--vm-vectors',fixture)]
    if len(actual)!=len(expected):raise ValueError('VM vector count mismatch')
    for index,(want,got) in enumerate(zip(expected,actual)):
        if want!=got:
            (out/'vm-mismatch.json').write_text(json.dumps(dict(case=index,input=inputs[index],expected=want,actual=got),indent=2)+'\n')
            first=next((i for i,(x,y) in enumerate(zip(want,got)) if x!=y),min(len(want),len(got)))
            raise ValueError(f'VM case {index} field {first}: {want[first:first+5]} != {got[first:first+5]}')
    vectors='\n'.join(' '.join(map(str,row)) for row in expected)+'\n'
    (out/'vm-vectors.txt').write_text(vectors)
    pool_receipt=pool_controls(original,args,out)
    stage_receipts=[];schedules=[]
    if not args.vm_only:
        assets=main_assets(args.hdi)
        for stage in range(7):
            path=out/f'ST0{stage}.STD';standard=assets[path.name];path.write_bytes(standard)
            original.reset();original.schedule_only=True
            at=3+standard[2];at+=1+standard[at];count=standard[at];at+=1;layout=[count]
            for i in range(count):
                length=standard[at];at+=1;layout.extend((at-3,length));at+=length
            at+=1;original.u.mem_write(0x90000,standard[3:]);original.write(0x3dba,'HH',at-3,0x9000)
            original.write(0x4646,'HH',0x4341,0x33a9);rows=[' '.join(map(str,layout))];wave=0;spawn_count=0
            while original.read(0x4646,'H')[0]==0x4341:
                frame=struct.unpack('<H',original.u.mem_read(0x90000+original.read(0x3dba,'H')[0],2))[0]
                original.write(0x538a,'H',frame);original.write(0x46b2,'B',int(wave%3==1));original.events.clear()
                original.call(0x4341,far=True);wave+=1;spawn_count+=len(original.events)
                row=[frame,*original.read(0x3dba,'H'),int(original.read(0x4646,'H')[0]!=0x4341),len(original.events)]
                row.extend(itertools.chain.from_iterable(original.events));rows.append(' '.join(map(str,row)))
                if wave>65536:raise ValueError('original STD wave schedule did not stop')
            got=run_host(args,'--schedule',path)
            if got!=rows:raise ValueError(f'ST0{stage} native schedule differs from original CPU')
            trace=out/f'schedule-stage{stage}.txt';trace.write_text('\n'.join(rows)+'\n')
            schedules.append(dict(stage=stage,waves=wave,emitted=spawn_count,trace_sha256=sha(trace.read_bytes()),std_sha256=sha(standard)))
        original.schedule_only=False
        standard=assets['ST00.STD'];at=3+standard[2];at+=1+standard[at];count=standard[at];at+=1
        offsets=[]
        for i in range(count):length=standard[at];at+=1;offsets.append(at-3);at+=length
        at+=1;wave_start=at-3
        for rank,frames in ((1,6200),(3,3200),(0,3200)):
            original.reset();original.script_offsets=offsets
            original.u.mem_write(0x90000,standard[3:]);original.write(0x918,'H',0x9000)
            for i,off in enumerate(offsets):original.write(0x3d7a+i*2,'H',off)
            original.write(0x3dba,'HH',wave_start,0x9000);original.write(0x4646,'HH',0x4341,0x33a9)
            rows=[]
            for frame in range(frames):
                original.events.clear();original.context(rank,22 if rank==3 else 16,16 if frame%3==0 else 0,3072,5120)
                original.write(0x538a,'H',frame);original.write(0x538c,'BB',frame%2,frame%4)
                original.write(0x46b2,'B',int(2000<=frame<2400))
                if original.read(0x4646,'H')[0]==0x4341:original.call(0x4341,far=True)
                original.call(0x43c9,far=True)
                original.draws.clear();original.call(0x5c23,cs=0x2aaf)
                digest=2166136261
                for byte in original.normalized_pool():digest=((digest^byte)*16777619)&0xffffffff
                pointer=original.read(0x3dba,'H')[0];stopped=original.read(0x4646,'H')[0]!=0x4341
                row=[frame,pointer,int(stopped),digest,*original.read(0x3ecc,'H'),*original.read(0x1b5e,'HH'),
                    *original.read(0x435a,'I'),*original.read(0x4669,'B'),*original.read(0x4642,'hh'),len(original.events)]
                row.extend(itertools.chain.from_iterable(original.events));rows.append(' '.join(map(str,row)))
                row.extend([len(original.draws),*itertools.chain.from_iterable(original.draws)])
                rows[-1]=' '.join(map(str,row))
            got=run_host(args,'--stage-trace',out/'ST00.STD',rank,frames)
            if got!=rows:
                first=next((i for i,(a,b) in enumerate(zip(rows,got)) if a!=b),min(len(rows),len(got)))
                (out/f'stage-mismatch-rank{rank}.json').write_text(json.dumps(dict(frame=first,expected=rows[first],actual=got[first]),indent=2)+'\n')
                raise ValueError(f'original scheduled enemy pool differs at rank {rank}, frame {first}')
            path=out/f'stage-rank{rank}.txt';path.write_text('\n'.join(rows)+'\n')
            stage_receipts.append(dict(stage=0,rank=rank,frames=frames,trace_sha256=sha(path.read_bytes())))
    receipt=dict(schema_version=1,passed=True,observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),
        target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),
        vm_vectors_sha256=sha(vectors.encode()),vm_cases=len(cases),vm_valid_opcodes=52,pool_controls=pool_receipt,stage_traces=stage_receipts,schedules=schedules,
        unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
        scope='MAIN.EXE main_03 13A9:1B4D VM; 1ABF/1B02/1B1A helpers; 4263 add; 4341 STD; 43C9 pool; main_01 0AAF:5C23 renderer; load 2000 DS8000 ES9000.',
        limits='Bullet tune/add, sound, tile-ring, drop and spark callees intercepted; ordered requests recorded. Enemy renderer state and normalized graphics requests compared; no bullet/spark RNG, graphics pixels, natural Windows pacing or complete route claim. Malformed bytecode rejected by host instead of original undefined paths.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(passed=True,vm_cases=len(cases),stage_frames=sum(r['frames'] for r in stage_receipts),receipt=str(out/'receipt.json'))))


if __name__=='__main__':main()
