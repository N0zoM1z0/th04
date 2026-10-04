#!/usr/bin/env python3
"""Original SUPER1PLANE/rolling CPU pixel controls using a bounded GRCG write shadow."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_INS_OUT
from verify_marisa_render import Original as Base
from probe_assets import main_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS)
        if cs==0x2000 and address-cs*16 in (0x2838,0x2d3e,0x2b78,0x2f54):return
        super().hook_body(u,address,size,unused)

def planes(blob,image):
    w,h,first,last=struct.unpack_from('<4H',blob,8);stride=w*h//8
    at=32+struct.unpack_from('<H',blob,28)[0]+(48 if blob[5]&128 else 0)
    pixels=blob[at+image*w*h//2:at+(image+1)*w*h//2]
    if len(pixels)!=w*h//2 or image>last-first:raise ValueError('short BFNT pixel fixture')
    result=bytearray(stride*5)
    for y in range(h):
        for x in range(w):
            v=pixels[y*w//2+x//2];color=(v&15) if x&1 else v>>4
            dest=y*(w//8)+x//8;bit=128>>(x&7)
            if color:result[dest]|=bit
            for p in range(4):
                if color&(1<<p):result[(p+1)*stride+dest]|=bit
    return w,h,bytes(result)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','hdi','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--limit',type=int);a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    o=Original(a.target.read_bytes());manifest=source_manifest(Path(__file__).resolve().parents[1])[0];assets=main_assets(a.hdi)
    files={name:out/name for name in ('ST03B21.BBT','ST03B22.BBT')}
    for name,path in files.items():path.write_bytes(assets[name])
    # kind0/1 are body normal/white;7/8 are bit rolling normal/white.
    rows=list(itertools.product(('ST03B21.BBT',),range(8),range(8),(-15,-1,0,20,320,367,399),(0,1)))+list(itertools.product(('ST03B22.BBT',),range(4),range(8),(-15,-1,0,367,368,383,399),(7,8)))
    rows=rows[:a.limit] if a.limit else rows;inputs=[];trace=out/'pixel-trace.bin';records=[]
    with trace.open('wb') as result:
        for index,(name,image,shift,top,kind) in enumerate(rows):
            left=96+shift;seed=index%16;o.reset();o.callback_error=None
            w,h,data=planes(assets[name],image);o.write(0x2ac4,'H',0x9000);o.write(0x2ec4,'H',(w//8<<8)|h);o.u.mem_write(0x90000,data)
            screen=bytearray(bytes((i*73+seed)&15 for i in range(16))*(640*400//16));mode=[0];tiles=[0,0,0,0];tile_index=[0];writes=[0]
            def port(u,port,size,value,unused):
                try:
                    if size!=1:raise ValueError('unexpected GRCG port width')
                    if port==0x7c:mode[0]=value;tile_index[0]=0
                    elif port==0x7e:tiles[tile_index[0]]=value;tile_index[0]=(tile_index[0]+1)%4
                    else:raise ValueError('unexpected pixel port')
                except Exception as error:o.callback_error=error;u.emu_stop()
            def write(u,access,address,size,value,unused):
                try:
                    if not 0xa8000<=address<0xa8000+32000:return
                    if not mode[0]&0x80:raise ValueError('VRAM write outside GRCG mode')
                    enabled=(~mode[0])&15
                    for byte in range(size):
                        at=address-0xa8000+byte
                        if at>=32000:continue
                        mask=(value>>(byte*8))&255
                        for bit in range(8):
                            if not mask&(128>>bit) and mode[0]&0x40:continue
                            color=sum(1<<p for p in range(4) if tiles[p]&(128>>bit))
                            pos=at*8+bit;screen[pos]=(screen[pos]&~enabled)|(color&enabled)
                    writes[0]+=1
                except Exception as error:o.callback_error=error;u.emu_stop()
            ph=o.u.hook_add(unicorn.UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);wh=o.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
            try:o.call_args({0:0x2f54,1:0x2838,7:0x2d3e,8:0x2b78}[kind],args=(0xffc0,0,0,top,left) if kind in (1,8) else (0,top,left),far=True,cs=0x2000)
            finally:o.u.hook_del(ph);o.u.hook_del(wh)
            if not writes[0]:raise ValueError('original pixel control produced no writes')
            inputs.append(f'{files[name]} {image} {left} {top} {kind} {seed}');result.write(screen)
            records.append(dict(asset=name,image=image,left=left,top=top,kind=kind,seed=seed,screen_sha256=sha(screen)))
    path=out/'pixel-fixtures.txt';path.write_text('\n'.join(inputs)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--pixel-vectors',str(path)]
    native=out/'native-pixels.bin'
    with native.open('wb') as f:subprocess.run(command,check=True,stdout=f,env=env)
    with trace.open('rb') as expected,native.open('rb') as actual:
        for index,row in enumerate(records):
            want=expected.read(640*400);got=actual.read(640*400)
            if want!=got:
                pos=next((i for i,(x,y) in enumerate(zip(want,got)) if x!=y),min(len(want),len(got)))
                (out/'mismatch.json').write_text(json.dumps(dict(case=index,control=row,first_pixel=pos,x=pos%640,y=pos//640,expected=want[pos] if pos<len(want) else None,actual=got[pos] if pos<len(got) else None),indent=2)+'\n');raise ValueError(f'pixel case{index} at{pos} differs')
        if actual.read(1) or expected.read(1):raise ValueError('extra pixel output')
    if source_manifest(Path(__file__).resolve().parents[1])[0]!=manifest:raise ValueError('source changed during pixel controls')
    r=dict(passed=True,cases=len(rows),compared_pixels=len(rows)*640*400,source_manifest_sha256=manifest,target_sha256=sha(o.target),hdi_sha256=sha(a.hdi.read_bytes()),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(trace.read_bytes()),native_pixels_sha256=sha(native.read_bytes()),controls=records,assets={name:sha(assets[name]) for name in files},observed_utc=datetime.now(timezone.utc).isoformat(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),scope='Original0000:2F54/2838 body normal/white and2D3E/2B78 rolling bit normal/white execute against all8Marisa64x64/fourbit32x32 BFNT assets, eight X alignments, retained16-color backgrounds and seven signed top/bottom positions. Complete640x400 indexed buffers compared.',limits='GRCG output ports and visible A800:0000..7CFF writes use a software shadow; physical page/scroll/VRAM aliasing outside visible plane, timing and invalid extreme coordinates excluded. Original asset planar staging is a bounded input adapter. No DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),compared_pixels=r['compared_pixels'])))
if __name__=='__main__':main()
