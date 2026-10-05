#!/usr/bin/env python3
"""Compare complete verdict pages using original requests/full-string kernels.

The original graph_putsa_fx and graph_gaiji_puts execute their full string,
cursor, font-weight and write loops. CGROM/GRCG are explicit adapters; UDE.PI
decoding is independently regressed against the preceding native executable.
This is not physical PC-98 video or audio capture.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess

import numpy as np
from PIL import Image
from unicorn.x86_const import *
from verify_cutscene import Original as FontBase,ending_assets,PAYLOAD_SHA
from verify_verdict import Original,fixtures
from verify_cutscene_pixels import Raster
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()

class FontOriginal(FontBase):
    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);relative=cs-self.load;ip=address-cs*16
        if self.font_mode and relative==0 and 0x36b6<=ip<0x375f:return
        super().body(u,address)

    def string(self,kind,text,x,y,color,weight,step,rom):
        self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
        self.u.mem_write(0xa8000,bytes(32000));self.u.mem_write(self.ds*16+0x4000,text+b'\0')
        self.write(0x5fc,'H',weight)
        self.font_mode=True;self.font_rows=None;self.font_row=0;self.font_rom=rom
        self.font_cell=0;self.font_column=0;self.font_color=color;self.font_pixels=bytearray(640*400)
        self.error=None;self.done=False
        segment=0xcc7 if kind=='text' else 0
        ip=0x58c if kind=='text' else 0x36b6
        for reg,value in ((UC_X86_REG_CS,self.load+segment),(UC_X86_REG_DS,self.ds),
                          (UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):
            self.u.reg_write(reg,value)
        args=(0x4000,self.ds,color,y,x) if kind=='text' else (color,0x4000,self.ds,step,y,x)
        stack=(0xff00,self.cs,*args)
        self.u.mem_write(0x7f000,struct.pack('<'+'H'*len(stack),*stack))
        self.u.emu_start((self.load+segment)*16+ip,0x10ffff,count=250000)
        self.font_mode=False
        if self.error:raise RuntimeError('original full-string kernel rejected') from self.error
        if not self.done or self.u.reg_read(UC_X86_REG_SP)!=0xf000+len(stack)*2:
            raise ValueError('original full-string FAR Pascal ABI differs')
        return bytes(self.font_pixels)

def run(exe,runner,*arguments):
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    proc=subprocess.run(([runner] if runner else [])+[str(exe.resolve()),*map(str,arguments)],capture_output=True,env=env,timeout=180)
    if proc.returncode:raise RuntimeError(proc.stderr.decode(errors='replace'))
    return proc.stdout.decode().replace('\r\n','\n')

def selected_cases(original):
    cases=fixtures();chosen=set();lines=set();ranks=set()
    traces={}
    for index,v in enumerate(cases):
        trace=original.run(v);end=trace[-1].split();line=int(end[6]);rank=int(end[5])
        if line not in lines or rank not in ranks:
            chosen.add(index);lines.add(line);ranks.add(rank)
        # Include frame truncation, wrapped gaiji/NUL and nonstandard ratios.
        if any(v[n]>60000 for n in (6,9,10,11,12,13,14)) or v[20]:
            if len(chosen)<80:chosen.add(index)
        if index in chosen:traces[index]=trace
    assert lines==set(range(-1,26)) and ranks==set(range(5))
    return [(index,cases[index],traces[index]) for index in sorted(chosen)]

class VerdictRaster:
    """Independent indexed consumer with two relocated original font kernels."""
    def __init__(self,target,decoded,font_path,gaiji,picture_bytes):
        self.gaiji=gaiji;self.decoded=picture_bytes
        self.first=FontOriginal(target,decoded,0x2000);self.second=FontOriginal(target,decoded,0x1000)
        self.lookup=Raster(self.first,Image.open(font_path).convert('L'),gaiji,{},(None,None))
        self.kernels={}
        packed=np.frombuffer(picture_bytes[56:],dtype=np.uint8);self.picture=np.empty((400,640),dtype=np.uint8)
        self.picture[:,::2]=(packed>>4).reshape(400,320);self.picture[:,1::2]=(packed&15).reshape(400,320)

    def rom(self,cell,column,selector):
        if column in (0x56,0x57):
            character=cell+(column-0x56)*128
            at=32+int.from_bytes(self.gaiji[28:30],'little')+character*32+(selector&15)*2
            return self.gaiji[at+(0 if selector&0x20 else 1)]
        return self.lookup.rom(cell,column,selector)

    def render(self,trace):
        canvas=np.empty((2,400,640),dtype=np.uint8);canvas[0].fill(3);canvas[1].fill(9)
        access=0;shown=1;tone=0;palette=bytes(48);loaded=False;count=0
        for line in trace:
            if line.startswith('END '):break
            w=line.split();kind=w[0];a,b,c,d,e=map(int,w[1:6]);raw=bytes.fromhex(w[6]) if w[6]!='-' else b''
            count+=1
            if kind=='access':access=a
            elif kind=='show':shown=a
            elif kind=='pi_load':loaded=True
            elif kind=='pi_palette':assert loaded;palette=self.decoded[8:56]
            elif kind=='pi_put':assert loaded;canvas[access]=self.picture
            elif kind=='pi_free':loaded=False
            elif kind=='copy_page':access=a;canvas[access]=canvas[1-access]
            elif kind=='tone':tone=a
            elif kind=='fade':tone=100 if b else 0
            elif kind in ('text','gaiji'):
                color=c if kind=='text' else d;weight=d if kind=='text' else 0;step=16 if kind=='text' else c
                key=(kind,raw,a,b,weight,step)
                if key not in self.kernels:
                    footprint=self.first.string(kind,raw,a,b,15,weight,step,self.rom)
                    relocated=self.second.string(kind,raw,a,b,15,weight,step,self.rom)
                    if footprint!=relocated:raise ValueError('original full-string kernel load metamorphism differs')
                    self.kernels[key]=np.frombuffer(footprint,dtype=np.uint8).reshape(400,640)!=0
                canvas[access][self.kernels[key]]=color&15
            elif kind=='wait':break
        return canvas,palette,[shown,access,tone,count]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded-dir','hdi','font-bmp','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--baseline-exe',type=Path);p.add_argument('--reference-dir',type=Path);p.add_argument('--runner')
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    assets=ending_assets(args.hdi);private=out/'assets';private.mkdir(exist_ok=True)
    for name in ('UDE.PI','GAMEFT.BFT','_UDE.TXT'):(private/name).write_bytes(assets[name])
    original=Original(args.target,args.decoded_dir,assets['_UDE.TXT'],0x2000)
    if args.reference_dir:
        ref=args.reference_dir.resolve();proof=json.loads((ref/'receipt.json').read_text());assert proof['passed']
        assert proof['payload_sha256']==PAYLOAD_SHA and proof['font_sha256']==sha(args.font_bmp.read_bytes()) and proof['gaiji_sha256']==sha(assets['GAMEFT.BFT'])
        choices=proof['cases'];fixture=(ref/'fixtures.txt').read_bytes();assert sha(fixture)==proof['fixture_sha256']
        (out/'fixtures.txt').write_bytes(fixture)
        decoded=(ref/'UDE.raw').read_bytes();assert sha(decoded)==proof['pi_decoder']['decoded_sha256']
        trace_bytes=(ref/'original-requests.json').read_bytes();assert sha(trace_bytes)==proof['original_requests_sha256']
        traces=json.loads(trace_bytes)
        vectors=[list(map(int,line.split())) for line in fixture.decode().splitlines()]
        assert len(choices)==len(vectors)==len(traces)
        for vector,trace in zip(vectors,traces):assert original.run(vector)==trace
    else:
        if not args.baseline_exe:raise ValueError('PI decoder regression baseline required')
        chosen=selected_cases(original);choices=[{'original_case':i} for i,_,_ in chosen]
        fixture=''.join(' '.join(map(str,v))+'\n' for _,v,_ in chosen).encode()
        (out/'fixtures.txt').write_bytes(fixture)
        traces=[t for _,_,t in chosen]
        run(args.baseline_exe,None,'--decode',private/'UDE.PI',out/'UDE-baseline.raw')
        decoded=(out/'UDE-baseline.raw').read_bytes()
    run(args.exe,args.runner,'--decode',private/'UDE.PI',out/'UDE.raw')
    if (out/'UDE.raw').read_bytes()!=decoded:raise ValueError('UDE.PI decoder regression differs')
    assert struct.unpack_from('<II',decoded)==(640,400) and len(decoded)==128056
    (out/'original-requests.json').write_text(json.dumps(traces)+'\n')
    pages=out/'pages';pages.mkdir(exist_ok=True)
    stdout=run(args.exe,args.runner,'--verdict-render',private,args.font_bmp.resolve(),out/'fixtures.txt',pages)
    (out/'stdout.txt').write_text(stdout)
    states={int(l.split()[0]):list(map(int,l.split()[1:])) for l in (pages/'states.txt').read_text().splitlines()}
    assert len(states)==len(choices)
    gaiji=assets['GAMEFT.BFT'];raster=VerdictRaster(args.target,args.decoded_dir,args.font_bmp,gaiji,decoded)
    records=[]
    for index,(choice,trace) in enumerate(zip(choices,traces)):
        canvas,palette,state=raster.render(trace)
        if states[index]!=state:raise ValueError('verdict page/tone/request state differs')
        if (pages/f'{index}.pal').read_bytes()!=palette:raise ValueError('verdict palette differs')
        hashes=[]
        for page in (0,1):
            actual=(pages/f'{index}-{page}.bin').read_bytes();expected=canvas[page].tobytes()
            if actual!=expected:
                at=next(i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b)
                raise ValueError(f'verdict case{index} page{page} differs at {at%640},{at//640}')
            hashes.append(sha(expected))
        records.append({**choice,'page_sha256':hashes,'palette_sha256':sha(palette),'state':states[index],
                        'end':trace[-1]})
    mf,source=source_manifest(Path(__file__).resolve().parents[1])
    receipt={'passed':True,'utc':datetime.now(timezone.utc).isoformat(),'cases':records,'complete_pages':len(records)*2,
      'full_string_kernels':len(raster.kernels),'kernel_loads':[0x1000,0x2000],'fixture_sha256':sha(fixture),
      'original_requests_sha256':sha((out/'original-requests.json').read_bytes()),'payload_sha256':PAYLOAD_SHA,
      'font_sha256':sha(args.font_bmp.read_bytes()),'gaiji_sha256':sha(gaiji),'source_manifest':mf,'source_files':source,
      'executable_sha256':sha(args.exe.read_bytes()),'pi_decoder':{'baseline_sha256':sha(args.baseline_exe.read_bytes()) if args.baseline_exe else None,'decoded_sha256':sha(decoded)},
      'scope':'Original full verdict requests and full-string graph_putsa_fx/graph_gaiji_puts kernels with supplied CGROM and GRCG write adapters. PI decode is preceding-native regression; complete indexed pages/palette/state, not physical video/audio.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'Verdict original full-string graphics: {len(records)} cases, {len(raster.kernels)} kernels, {len(records)*2} pages PASS')

if __name__=='__main__':main()
