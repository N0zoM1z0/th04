#!/usr/bin/env python3
"""Compare original and linked DOS text Gaiji memory writes and far-call state."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.x86_const import (
    UC_X86_REG_BP, UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES,
    UC_X86_REG_DI, UC_X86_REG_SI, UC_X86_REG_SP, UC_X86_REG_SS, UC_X86_REG_EFLAGS,
)
from verify_dos_vsync_lifecycle import original

ROOT=Path(__file__).resolve().parents[2]
START,END=0x80000,0xe0000
SEED=bytes(range(256))*((END-START)//256)
sha=lambda b:hashlib.sha256(b).hexdigest()


def configured():
    rows=[('putca',20,10,c,((c*257)^0xe1)&65535,0xa000)
          for c in range(256)]
    edges=((0,0),(79,0),(80,0),(79,24),(80,24),(2047,0),(2048,0),
           (28671,0),(28672,0),(32767,0),(65535,0),(20,32768),(20,65535))
    rows += [('putca',x,y,c,attr,0xa000) for (x,y),c,attr in itertools.product(
        edges,(0,127,128,255,65535),(0,0xe1,0xffff))]
    rows += [('putsa',x,y,text,attr,0xa000) for x,y,text,attr in itertools.product(
        (0,79,80,2047,28671,32767,65535),(0,24,65535),
        ('017f80ff','010002','-'),(0,0xe1,0xffff))]
    rows += [('putca',20,1,c,0xe1,base) for c,base in itertools.product(
        (0,127,128,255),(0x9000,0xa100))]
    rows += [('putsa',79,1,'017f80ff',0xffff,base) for base in (0x9000,0xa100)]
    for length,x in itertools.product((2047,2048,2049,16383,16384,16385,32768),(0,32767)):
        text=bytes((i%255)+1 for i in range(length)).hex()
        rows.append(('putsa',x,0,text,0xe1,0xa000))
    return rows


def candidate(exe,mp,predecessor=False):
    import re,sys
    sys.path.insert(0,str(ROOT/'scripts'))
    from lib.pc98 import parse_mz
    raw=exe.read_bytes();assert parse_mz(raw).valid
    body=raw[int.from_bytes(raw[8:10],'little')*16:]
    sites=[]
    for i in range(int.from_bytes(raw[6:8],'little')):
        off,seg=struct.unpack_from('<HH',raw,int.from_bytes(raw[24:26],'little')+4*i)
        assert seg*16+off+1<len(body);sites.append(seg*16+off)
    text=mp.read_text()
    def public(name):
        hits=set(re.findall(r'(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?'+name+r'\s*$',text))
        assert len(hits)==1,(name,hits)
        return tuple(int(n,16) for n in hits.pop())
    if predecessor:
        assert not re.search(r'\s_TextVramSeg\s*$',text,re.M)
        dg,_=public('_vsync_Count1');textseg=None
    else:
        dg,textseg=public('_TextVramSeg')
    return dict(body=body,sites=sites,dg=dg,textseg=textseg,putca=public('GAIJI_PUTCA'),
                putsa=public('GAIJI_PUTSA'),pins=dict(executable=sha(raw),map=sha(mp.read_bytes()),payload=sha(body)))


class Machine:
    def __init__(self,layout,load):
        self.layout=layout;self.load=load
        body=bytearray(layout['body'])
        for at in layout['sites']:
            struct.pack_into('<H',body,at,(struct.unpack_from('<H',body,at)[0]+load)&65535)
        self.body=bytes(body);self.cpu=Uc(UC_ARCH_X86,UC_MODE_16)
        self.cpu.mem_map(0,0x100000)
        self.cpu.hook_add(UC_HOOK_CODE,self.finish,None,0x6f000,0x6f000)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,None,START,END-1)

    def finish(self,cpu,address,size,unused):
        self.done=True;cpu.emu_stop()

    def write(self,cpu,access,address,size,value,unused):
        assert START<=address and address+size<=END and size==2,(address,size)
        self.writes.extend(struct.pack('<IHI',address,size,value))

    def run(self,row,interrupt):
        kind,x,y,text,attr,base=row;cpu=self.cpu
        cpu.mem_write(self.load*16,self.body)
        ds=self.load+self.layout['dg']
        if self.layout['textseg'] is not None:
            cpu.mem_write(ds*16+self.layout['textseg'],struct.pack('<H',base))
        raw=bytes.fromhex(text) if kind=='putsa' and text!='-' else b''
        assert len(raw)<0xb000
        cpu.mem_write(ds*16+0x5000,raw+b'\0')
        cpu.mem_write(START,SEED)
        self.writes=bytearray();self.done=False
        cs,ip=self.layout[kind]
        for reg,value in ((UC_X86_REG_CS,self.load+cs),(UC_X86_REG_DS,ds),
                          (UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),
                          (UC_X86_REG_BP,0xabcd),(UC_X86_REG_SI,0x1234),
                          (UC_X86_REG_DI,0x5678),(UC_X86_REG_ES,0x6789),
                          (UC_X86_REG_EFLAGS,2|(interrupt<<9))):cpu.reg_write(reg,value)
        args=(attr,text,y,x) if kind=='putca' else (attr,0x5000,ds,y,x)
        stack=(0,0x6f00,*(n&65535 for n in args))
        cpu.mem_write(0x7f000,struct.pack('<'+'H'*len(stack),*stack))
        cpu.emu_start((self.load+cs)*16+ip,0xfffff,count=100000000)
        assert self.done and cpu.reg_read(UC_X86_REG_SP)==0xf000+len(stack)*2
        for reg,value in ((UC_X86_REG_BP,0xabcd),(UC_X86_REG_SI,0x1234),
                          (UC_X86_REG_DI,0x5678),(UC_X86_REG_DS,ds)):
            assert cpu.reg_read(reg)==value,(reg,cpu.reg_read(reg),value)
        assert bool(cpu.reg_read(UC_X86_REG_EFLAGS)&0x200)==bool(interrupt)
        return bytes(cpu.mem_read(START,END-START)),bytes(self.writes),cpu.reg_read(UC_X86_REG_ES)


def main():
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--artifact',choices=('main','maine'),required=True)
    p.add_argument('--exe',type=Path,required=True);p.add_argument('--map',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--diagnostic',action='store_true')
    p.add_argument('--predecessor-fixed-base',action='store_true',help='compare the recorded old candidate with no TextVramSeg public')
    p.add_argument('--limit',type=int)
    args=p.parse_args();reference=original(args.artifact)
    putca,putsa,textseg={'main':(0x1b0c,0x1b50,0x768),'maine':(0xfc4,0x1008,0x3f6)}[args.artifact]
    reference.update(putca=(0,putca),putsa=(0,putsa),textseg=textseg)
    assert not args.predecessor_fixed_base or args.diagnostic
    current=candidate(args.exe,args.map,args.predecessor_fixed_base);rows=configured()
    if args.limit:rows=rows[:args.limit]
    args.output.mkdir(parents=True,exist_ok=False);controls=[];diffs=[]
    for load in (0x1000,0x3333):
        target=Machine(reference,load);product=Machine(current,load)
        with gzip.open(args.output/f'transcripts-{load:04x}.bin.gz','wb',compresslevel=1) as stream:
            for index,row in enumerate(rows):
                expected=target.run(row,index&1);actual=product.run(row,index&1);equal=expected==actual
                if not equal:
                    d=dict(load=f'{load:04x}',index=index,input=row,memory_bytes=sum(a!=b for a,b in zip(expected[0],actual[0])),writes_equal=expected[1]==actual[1],es_equal=expected[2]==actual[2]);diffs.append(d)
                    assert args.diagnostic,d
                for result in (expected,actual):
                    for data in result[:2]:stream.write(struct.pack('<I',len(data))+data)
                controls.append(dict(load=f'{load:04x}',input=row,equal=equal,original=[sha(x) for x in expected[:2]],candidate=[sha(x) for x in actual[:2]],original_es=expected[2],candidate_es=actual[2]))
        print(args.artifact,f'{load:04x}',len(rows),'checked',flush=True)
    receipt=dict(passed=not diffs,diagnostic=args.diagnostic,artifact=args.artifact,
        original=reference['pins'],candidate=current['pins'],controls=controls,differences=diffs,
        original_entries=dict(putca=[0,putca],putsa=[0,putsa]),candidate_entries={k:list(current[k]) for k in ('putca','putsa')},
        source_sha256=sha((ROOT/'src/shared/hardware/gaiji_text.cpp').read_bytes()),producer_sha256=sha(Path(__file__).read_bytes()),
        files={p.name:sha(p.read_bytes()) for p in args.output.iterdir()})
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('DOS text Gaiji',args.artifact,len(controls),'PASS' if not diffs else f'{len(diffs)} differences',flush=True)


if __name__=='__main__':main()
