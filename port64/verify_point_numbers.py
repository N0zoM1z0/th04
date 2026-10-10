#!/usr/bin/env python3
"""Original MAIN point-number rings, lifecycle, requests and full indexed pixels.

Execute the pinned add/digits/update/render/put/scroll bodies at two loads.
DS/SS and supplied pool/list/scroll inputs are explicit component adapters.
The renderer inherits GRCG RMW from its original foreground caller; the
independent hardware shadow observes actual stores/ports. Full scanout,
dirty-page invalidation and complete gameplay parity are outside this claim.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
from datetime import datetime, timezone

import unicorn
from unicorn.x86_const import *
from verify_player_bomb_pixels import Shadow, read_exact, SCREEN
from verify import source_manifest

sha=lambda data:hashlib.sha256(data).hexdigest()
POOL=0x9634


def pointers(data,to_guest):
    result=bytearray(data)
    for at in [6402,*range(6404,7206,2)]:
        value=struct.unpack_from('<H',result,at)[0]
        if value:
            if to_guest:
                if not 1<=value<=400:raise ValueError('portable list index')
                value=POOL+(value-1)*16
            else:
                if value<POOL or value>=POOL+6400 or (value-POOL)%16:raise ValueError('original list ownership')
                value=(value-POOL)//16+1
        struct.pack_into('<H',result,at,value)
    return bytes(result)


class Original:
    def __init__(self,target,load):
        if len(target)!=156258 or sha(target)!='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b':
            raise ValueError('original MAIN identity')
        self.target=target;self.load=load;self.error=None
        self.module=bytearray(target[6144:])
        if struct.unpack_from('<HH',target,6)!=(1136,384):raise ValueError('original MAIN header')
        at=struct.unpack_from('<H',target,24)[0]
        for i in range(1136):
            off,seg=struct.unpack_from('<HH',target,at+i*4);site=seg*16+off
            struct.pack_into('<H',self.module,site,(struct.unpack_from('<H',self.module,site)[0]+load)&65535)
        self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);self.u.mem_map(0,0x110000)
        self.u.hook_add(unicorn.UC_HOOK_CODE,self.code)
        self.reset()

    def reset(self):
        self.u.mem_write(self.load*16,bytes(self.module))
        self.u.mem_write(0x80000,bytes(65536))
        self.u.mem_write(0x80000,bytes(self.module[0x21340:]))
        self.requests=[];self.shadow=None;self.error=None

    def code(self,u,address,size,unused):
        if address==(self.load+0x0aaf)*16+0x130e:
            signed=lambda v:v-65536 if v>=32768 else v
            color=sum((self.shadow.tiles[p]&1)<<p for p in range(4))
            self.requests.extend([signed(u.reg_read(UC_X86_REG_DX)),u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_CX),color])

    def write(self,at,fmt,*values):self.u.mem_write(0x80000+at,struct.pack(fmt,*values))

    def seed(self,data):
        self.reset();data=pointers(data,True)
        self.u.mem_write(0x80000+POOL,data[:6400]);self.u.mem_write(0x83ece,data[6400:6402])
        self.u.mem_write(0x841f2,data[6402:6404]);self.u.mem_write(0x83ed0,data[6404:7206])
        self.u.mem_write(0x84254,data[7206:7210])

    def snapshot(self):
        data=bytes(self.u.mem_read(0x80000+POOL,6400))+bytes(self.u.mem_read(0x83ece,2))+bytes(self.u.mem_read(0x841f2,2))+bytes(self.u.mem_read(0x83ed0,802))+bytes(self.u.mem_read(0x84254,4))
        return pointers(data,False)

    def call(self,segment,ip,args=(),budget=200000):
        cs=self.load+segment
        for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                          (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_ES,0xa800),(UC_X86_REG_EFLAGS,2)):
            self.u.reg_write(reg,value)
        words=(0xf000,*args);self.u.mem_write(0x7e000,struct.pack('<'+'H'*len(words),*[v&65535 for v in words]))
        self.u.emu_start(cs*16+ip,cs*16+0xf000,count=budget)
        if self.error:raise self.error
        if self.u.reg_read(UC_X86_REG_IP)!=0xf000 or self.u.reg_read(UC_X86_REG_SP)!=0xe000+len(words)*2:
            raise ValueError('original point-number bounded return/ABI')

    def execute(self,row):
        op,data,x,y,points,yellow,times,scroll,line,seed=row
        self.seed(data);self.write(0x988,'B',times);self.write(0x427c,'B',scroll);self.write(0x4278,'H',line)
        if op=='I':self.call(0xaaf,0x11c2)
        elif op=='A':self.call(0x13a9,0x300 if yellow else 0x31a,(points,y,x))
        elif op=='U':self.call(0xaaf,0x1204)
        elif op=='R':
            self.shadow=Shadow(self,seed);self.shadow.mode=0xc0
            try:
                self.call(0xaaf,0x1274)
                screen=bytes(self.shadow.screen);writes=self.shadow.writes;ports=self.shadow.ports
            finally:self.shadow.close()
        result=self.snapshot().hex()+' '+str(len(self.requests)//4)
        if self.requests:result+=' '+' '.join(map(str,self.requests))
        return result,(screen,writes,ports) if op=='R' else None


def entity(flag=1,age=0,x=3072,y=1024,number=5120,times=0):
    decimal=[number%10,(number//10)%10,(number//100)%10,number//1000]
    return struct.pack('<BBhhh4BHBB',flag,age,x,y,777,*decimal,0xa123,times,0x5a)


def snapshot(records=(),white=0,yellow=0,alive=(),first=0):
    pool=bytearray(6400)
    for index,record in records:pool[index*16:(index+1)*16]=record
    entries=list(alive)+[0]*(401-len(alive))
    return bytes(pool)+struct.pack('<BBH401H4B',white,yellow,first,*entries,19,71,113,223)


def fixtures(target):
    def row(op,data,x=3072,y=1024,points=5120,yellow=0,times=0,scroll=1,line=399,seed=7):
        return [op,data,x,y,points,yellow,times,scroll,line,seed]
    dense=[(i,entity(flag=i%4,age=(i*19)&255,x=16*(i%384),y=16*(i%368),number=1+i,times=i%2)) for i in range(400)]
    full=snapshot(dense,white=199,yellow=198,alive=range(1,401),first=201)
    yield row('I',full)
    for color,cursor,number,times in itertools.product(range(2),(0,1,198,199),(0,1,9,10,999,9999,10000,65535),range(2)):
        yield row('A',snapshot(dense,white=cursor,yellow=cursor,alive=range(1,401),first=201),points=number,yellow=color,times=times,x=-32768 if number%2 else 32767,y=-1234)
    for flag,age,y in itertools.product((0,1,2,255),(0,23,24,35,36,37,255),(-32768,-65,-64,-63,0,32767)):
        records=dense.copy();records[199]=(199,entity(flag=flag,age=age,y=y))
        records[200]=(200,entity(flag=flag,age=age,y=y))
        yield row('U',snapshot(records,white=17,yellow=71,alive=range(1,401),first=201))
    # Every numeral, multiplier, bit alignment and lower-edge roll is exposed
    # on a nonzero patterned background, with both colors and scroll states.
    for number,shift,top in itertools.product((1,12,23,34,45,56,67,78,89,90,100,9999,10000,11000),range(8),(0,392,393,399)):
        color=(number+shift+top)&1;index=200 if color else 0
        y=(top-12)*16
        yield row('R',snapshot([(index,entity(x=(20+shift)*16,y=y,number=number,times=shift&1))],alive=(index+1,),first=index+1 if color else 0),scroll=0,seed=shift)
    for line,scroll in itertools.product((0,1,399),range(2)):
        records=[(0,entity(x=2048,y=1024,number=10)),(199,entity(x=2048,y=1024,number=3456,times=1)),
                 (200,entity(x=2048,y=1024,number=89,times=1)),(399,entity(x=2048,y=1024,number=1))]
        yield row('R',snapshot(records,alive=(1,200,201,400),first=201),line=line,scroll=scroll)
    # Retained alive pointers may reference overwritten or remove-marked
    # entries: the renderer follows its list, not an invented flag scan.
    yield row('R',snapshot([(0,entity(flag=2,number=9)),(200,entity(flag=0,number=123))],alive=(1,201),first=201))
    data=snapshot([(0,entity(number=5120)),(200,entity(number=5120,times=1))],alive=(1,201),first=201)
    o=Original(target,0x2000)
    for frame in range(39):
        trial=row('U',data);yield trial;state,_=o.execute(trial);data=bytes.fromhex(state.split()[0])
        trial=row('R',data,line=frame%400);yield trial;state,_=o.execute(trial);data=bytes.fromhex(state.split()[0])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--limit',type=int);args=parser.parse_args();out=args.output_dir.resolve()
    if out.exists():raise ValueError('fresh point-number output directory required')
    out.mkdir(parents=True);root=Path(__file__).resolve().parents[1]
    manifest,files=source_manifest(root);rows=list(fixtures(args.target.read_bytes()));rows=rows[:args.limit] if args.limit else rows
    text='\n'.join(' '.join([r[0],r[1].hex(),*map(str,r[2:])]) for r in rows)+'\n'
    path=out/'fixtures.txt';path.write_text(text);counts={op:sum(r[0]==op for r in rows) for op in 'IAUR'}
    expected=[];records=[];trace=out/'original-pixels.gz'
    for load in (0x1000,0x2000):
        original=Original(args.target.read_bytes(),load);current=[];local=[]
        with gzip.open(trace,'wb',compresslevel=6) if load==0x1000 else gzip.open(trace,'rb') as stream:
            for index,row in enumerate(rows):
                result,pixels=original.execute(row);current.append(result)
                if pixels:
                    screen,writes,ports=pixels;local.append(dict(case=index,sha256=sha(screen),writes=writes,ports=ports))
                    if load==0x1000:stream.write(screen)
                    elif read_exact(stream,SCREEN)!=screen:raise ValueError('point-number pixels changed with load')
                if (index+1)%200==0:print(f'load {load:04X}: {index+1}/{len(rows)} point-number controls',flush=True)
            if load==0x2000 and stream.read(1):raise ValueError('original pixel EOF')
        if load==0x1000:expected=current;records=local
        elif expected!=current or records!=local:raise ValueError('point-number state/request/writes changed with load')
    (out/'original.txt').write_text('\n'.join(expected)+'\n')
    command=[str(args.exe.resolve()),'--vectors',str(path),str(args.target.resolve()),str(out/'native-pixels.bin')]
    env=os.environ.copy();env['SDL_AUDIODRIVER']='dummy';env['SDL_VIDEODRIVER']='dummy'
    result=subprocess.run(command,env=env,capture_output=True,text=True)
    (out/'native.stderr').write_text(result.stderr);(out/'native.txt').write_text(result.stdout)
    if result.returncode:raise ValueError('native point-number control failed: '+result.stderr)
    actual=result.stdout.splitlines()
    if actual!=expected:
        at=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),min(len(actual),len(expected)))
        (out/'mismatch.json').write_text(json.dumps(dict(case=at,expected=expected[at] if at<len(expected) else None,actual=actual[at] if at<len(actual) else None),indent=2)+'\n')
        raise ValueError(f'complete point-number state/request mismatch {at}')
    with gzip.open(trace,'rb') as a,(out/'native-pixels.bin').open('rb') as b:
        for record in records:
            original=read_exact(a,SCREEN);native=read_exact(b,SCREEN)
            if len(original)!=SCREEN or original!=native:raise ValueError(f'complete point-number indexed pixels differ case {record["case"]}')
        if a.read(1) or b.read(1):raise ValueError('point-number pixel EOF mismatch')
    if source_manifest(root)[0]!=manifest:raise ValueError('point-number sources changed during comparison')
    receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),target_sha256=sha(args.target.read_bytes()),
        executable_sha256=sha(args.exe.read_bytes()),source_manifest_sha256=manifest,source_files=files,
        cases=counts,total_cases=len(rows),loads=[0x1000,0x2000],pixel_frames=len(records),records=records,
        fixture_sha256=sha(path.read_bytes()),original_state_sha256=sha((out/'original.txt').read_bytes()),
        native_state_sha256=sha((out/'native.txt').read_bytes()),pixel_gzip_sha256=sha(trace.read_bytes()),
        command=command,accepts_exact=False,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('passed','cases','total_cases','pixel_frames')}))


if __name__=='__main__':main()
