#!/usr/bin/env python3
"""Compare native STD/MAP scroll state with the original MAIN CPU through termination."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess

import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_BP, UC_X86_REG_IP, UC_X86_REG_EFLAGS
from probe_assets import main_assets


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,required=True)
    parser.add_argument('--hdi',type=Path,required=True)
    parser.add_argument('--exe',type=Path,required=True)
    parser.add_argument('--runner')
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    data=args.target.read_bytes()
    sha=lambda data:hashlib.sha256(data).hexdigest()
    if len(data)!=156258 or sha(data)!='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b':
        raise ValueError('MAIN identity mismatch')
    if struct.unpack_from('<H',data,8)[0]*16!=6144 or struct.unpack_from('<H',data,6)[0]!=1136:
        raise ValueError('MAIN MZ header mismatch')
    assets=main_assets(args.hdi)
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    for name in ['ST00.MAP','ST00.STD']: (out/name).write_bytes(assets[name])
    module=data[6144:]
    u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x110000);u.mem_write(0x20000,module)
    cs=0x2aaf;ds=0x80000
    def byte(at,value):u.mem_write(ds+at,bytes([value]))
    def word(at,value):u.mem_write(ds+at,struct.pack('<H',value))
    def readbyte(at):return u.mem_read(ds+at,1)[0]
    def readword(at):return struct.unpack('<H',u.mem_read(ds+at,2))[0]
    mp=assets['ST00.MAP'][8:]; std=assets['ST00.STD']; order_count=std[2]
    order=std[3:3+order_count];speed_count=std[3+order_count]
    u.mem_write(0x90000,mp);u.mem_write(0x98000,std[3:2+int.from_bytes(std[:2],'little')])
    word(0x918,0x9800);word(0x46fe,0x9000)
    for i in range(32):word(0x93a+i*2,i*320)
    # Execute the original 75-byte tiles_fill_initial owner as well. FS
    # supplies STD order and ES owns the 25x32 ring while DS reads MAP.
    for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
    u.mem_write(0x7e000,struct.pack('<H',0xf000))
    u.emu_start(cs*16+0xfb2,cs*16+0xf000,count=10000)
    if u.reg_read(UC_X86_REG_IP)!=0xf000 or u.reg_read(UC_X86_REG_SP)!=0xe002:raise ValueError('original initial tile fill failed')
    byte(0x4276,0);byte(0x4277,speed_count);word(0x4278,0);byte(0x427c,1)
    byte(0x3dbe,0);byte(0x3dc4,0);word(0x3dc0,0)
    word(0x5380,4);byte(0x5382,0);word(0x5384,order_count+5)
    display=[0]
    def graphics_hook(engine,address,size,unused):
        ip=address-cs*16
        if ip==0x2209:
            sp=engine.reg_read(UC_X86_REG_SP)
            display[0]=struct.unpack('<H',engine.mem_read(0x70000+sp,2))[0]
            engine.reg_write(UC_X86_REG_SP,sp+2);engine.reg_write(UC_X86_REG_IP,0x220e)
        elif ip in (0xdf8,0xdfb,0xe03):
            # EGC setup, pixel copier and EGC off are outside this state oracle.
            engine.reg_write(UC_X86_REG_IP,ip+(5 if ip==0xe03 else 3))
    u.hook_add(UC_HOOK_CODE,graphics_hook)
    expected=[];stopped=0
    for frame in range(20000):
        normalized=bytearray()
        for row in range(25):
            for offset in struct.unpack('<24H',u.mem_read(ds+0x4d40+row*64,48)):
                relative=offset-72;image=(relative%1280)//2*25+relative//1280
                normalized+=struct.pack('<H',image)
        hash=2166136261
        for value in normalized:hash=((hash^value)*16777619)&0xffffffff
        expected.append(f'{frame} {readword(0x4278)} {display[0]} {readbyte(0x4277)} {readword(0x5380)} {readbyte(0x5382)} {hash}')
        if readbyte(0x4277)==0:
            stopped+=1
            if stopped==64:break
        for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
        u.mem_write(0x7e000,struct.pack('<H',0xf000))
        u.emu_start(cs*16+0x21e6,cs*16+0xf000,count=2000)
        if u.reg_read(UC_X86_REG_IP)!=0xf000 or u.reg_read(UC_X86_REG_SP)!=0xe002:raise ValueError('original scroll return failed')
    else:raise ValueError('original STD did not terminate')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--background-trace',str(out/'ST00.MAP'),str(out/'ST00.STD')]
    result=subprocess.run(command,capture_output=True,text=True,check=True,env=env)
    actual=result.stdout.strip().splitlines()
    if actual!=expected:
        for index,(x,y) in enumerate(zip(expected,actual)):
            if x!=y:raise ValueError(f'frame {index}: target={x}, native={y}')
        raise ValueError(f'scroll trace length mismatch: {len(expected)}, {len(actual)}')
    pixel_results = {}
    for name in ['ST00.MPN','ST10.MPN']:
        tile_data=assets[name]; count=tile_data[4]+1
        (out/name).write_bytes(tile_data)
        word(0x345c,0x9000); word(0x345e,count-1)
        u.mem_write(0x90000,tile_data[54:54+count*128])
        expected_pixels=bytearray()
        for image in range(count):
            for reg,val in [(UC_X86_REG_CS,0x2000),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
            u.mem_write(0x7e000,struct.pack('<6H',0xf000,0x2000,image,0,0,0))
            u.emu_start(0x23680,0x2f000,count=1000)
            if u.reg_read(UC_X86_REG_IP)!=0xf000 or u.reg_read(UC_X86_REG_SP)!=0xe00c:raise ValueError('original MPN far return failed')
            planes=[u.mem_read(seg*16,80*16) for seg in (0xa800,0xb000,0xb800,0xe000)]
            for y in range(16):
                for x in range(16):
                    expected_pixels.append(sum(((plane[y*80+x//8]>>(7-x%8))&1)<<bit for bit,plane in enumerate(planes)))
        pixels_path=out/(name+'.pixels')
        command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--tile-pixels',str(out/name),str(pixels_path)]
        subprocess.run(command,capture_output=True,check=True,env=env)
        if pixels_path.read_bytes()!=expected_pixels:raise ValueError(f'{name}: MPN pixels differ from original CPU renderer')
        pixel_results[name]={'images':count,'pixels':len(expected_pixels),'pixels_sha256':sha(expected_pixels),'asset_sha256':sha(tile_data)}
    receipt={'passed':True,'observed_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),'frames':len(expected),'mpn_pixels':pixel_results,
        'target_sha256':sha(data),'unicorn_version':unicorn.__version__,'unicorn_engine_sha256':sha(Path(unicorn.unicorn._uc._name).read_bytes()),'native_sha256':sha(args.exe.read_bytes()),'trace_sha256':sha(('\n'.join(expected)+'\n').encode()),
        'asset_sha256':{name:sha(assets[name]) for name in ['ST00.MAP','ST00.STD']},
        'entry':{'load_segment':'2000','group':'main_01 0AAF','driver_offset':'21E6','driver_load_offset':'CCD6','helper_offset':'0D45','helper_load_offset':'B835','initial_fill_offset':'0FB2','initial_fill_load_offset':'BAA2'},
        'limits':'Original CPU initial fill and driver/helper state, complete 25x24 ring, native MAP decoding and STD through termination plus 64 stopped frames. All 128 original MPN renderer calls separately agree on 32768 indexed pixels. Scroll EGC copies and graphics calls are intercepted, not a full PC-98 video or gameplay replay.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))


if __name__=='__main__':main()
