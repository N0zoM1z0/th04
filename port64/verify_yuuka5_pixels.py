#!/usr/bin/env python3
"""Original Yuuka sprite/zoom, laser primitive and backdrop-filler pixel controls.

Execute the pinned MAIN callees. A bounded GRCG shadow translates visible
writes into a retained16-color screen; no product raster function produces
these references. Selected flat visible address wraps are included; physical page/alias/scroll
and host pacing remain separate.
"""
import argparse,hashlib,itertools,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_INS_OUT
from verify_yuuka5_render import Original as Base
from verify_marisa_pixels import planes
from probe_assets import main_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
SCREEN=640*400
class Original(Base):
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
        # These calls execute their target instructions, including zoom's
        # self-modification and downstream clipped rectangle/color calls.
        if cs==0x2000 and ip in (0x2838,0x2f54,0x31a2,0x107c,0x1774,0x1744,0x114c):return
        if cs==0x2aaf and ip==0x1508:return
        super().hook_body(u,address,size,unused)

class Shadow:
    def __init__(self,o,seed):
        self.o=o;self.mode=0;self.tiles=[0]*4;self.tile_index=0;self.writes=0;self.ports=0
        self.screen=bytearray(bytes((i*73+seed)&15 for i in range(16))*(SCREEN//16))
        self.ph=o.u.hook_add(unicorn.UC_HOOK_INSN,self.port,None,1,0,UC_X86_INS_OUT)
        self.wh=o.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.write)
    def port(self,u,port,size,value,unused):
        try:
            if size!=1:raise ValueError('unexpected GRCG port width')
            if port==0x7c:self.mode=value;self.tile_index=0
            elif port==0x7e:self.tiles[self.tile_index]=value;self.tile_index=(self.tile_index+1)%4
            else:raise ValueError('unexpected Yuuka pixel port')
            self.ports+=1
        except Exception as e:self.o.callback_error=e;u.emu_stop()
    def write(self,u,access,address,size,value,unused):
        try:
            if not 0xa8000<=address<0xa8000+32000:return
            if not self.mode&128:raise ValueError('Yuuka VRAM write outside GRCG mode')
            enabled=(~self.mode)&15
            for byte in range(size):
                at=address-0xa8000+byte
                if at>=32000:continue
                mask=(value>>(8*byte))&255
                for bit in range(8):
                    if not mask&(128>>bit) and self.mode&64:continue
                    color=sum(1<<p for p in range(4) if self.tiles[p]&(128>>bit))
                    pos=at*8+bit;self.screen[pos]=(self.screen[pos]&~enabled)|(color&enabled)
            self.writes+=1
        except Exception as e:self.o.callback_error=e;u.emu_stop()
    def close(self):self.o.u.hook_del(self.ph);self.o.u.hook_del(self.wh)

def sprites():
    for name,count in (('ST04.BB1',1),('ST04.BB2',8)):
        for image,shift,top,kind in itertools.product(range(count),range(8),(-15,0,16,367,399),(0,1)):
            yield [name,image,96+shift,top,kind,(image+shift+top)%16]
        for image,shift,top in itertools.product(range(count),(0,1,4,7),(-33,16,128,383)):
            yield [name,image,96+shift,top,10,(image+shift+top)%16]
    # Horizontal clipping for3x zoom is stage-specific; normal SUPER's
    # existing contract remains a complete visible-screen consumer.
    for name,image,left,top,kind in itertools.product(('ST04.BB1','ST04.BB2'),(0,),(-33,31,32,414,415,416),(0,16,383),(0,1,10)):
        yield [name,image,left,top,kind,(left+top)%16]

def defeat_zoom():
    # The real phase254 consumer uses MIKO32 death patterns4..11. Earlier
    # v1280 controls covered factor3 on entrance/idle sheets only; this is a
    # separate, explicit asset expansion, not a relabel of those observations.
    for image,left,top in itertools.product(range(8),(31,32,97,414),(15,16,128,383)):
        yield ['MIKO32.BFT',image,left,top,10,(image+left+top)%16]

def rasters():
    edges=(-32768,-1,0,15,16,17,31,32,33,127,128,383,384,414,415,416,639,640,32767)
    for x,y,ex,ey in itertools.product(edges,edges,edges[::3],edges[::4]):
        if (x+y+ex+ey)%71==0:yield ['R',x,y,ex,ey,15,(x+y)%16]
    for x,y,ey in itertools.product(edges,edges,edges):
        if (x+y+ey)%13==0:yield ['V',x,y,0,ey,256,(x+y)%16]
    for x,y,radius,color in itertools.product((31,32,224,415,416),(15,16,96,383,384),(0,1,8,16,64,180),(0,8,15,16,255,256)):
        if (x+y+radius+color)%7==0:yield ['D',x,y,radius,0,color,(x+y)%16]
    # The same TDW filler executes with all16 colors, overwriting the top/left
    # regions while leaving the CDG rectangle and margins untouched.
    for color,seed in itertools.product(range(16),(0,7,15)):yield ['F',0,0,0,0,color,seed]
    for color in (0,8,15,16,255,256):
        yield ['R',31,15,416,384,color,13];yield ['V',224,15,0,384,color,13]

def expected(o,row,assets):
    o.reset();o.callback_error=None;o.in_laser=False;o.raw_disc=False
    o.write(0x32c,'6h',32,383,415,16,367,383);o.write(0x338,'H',0xa850)
    shadow=Shadow(o,row[-1])
    try:
        if row[0] in assets:
            name,image,left,top,kind,seed=row;w,h,data=planes(assets[name],image)
            o.write(0x2ac4,'H',0x9000);o.write(0x2ec4,'H',(w//8<<8)|h);o.u.mem_write(0x90000,data)
            ip={0:0x2f54,1:0x2838,10:0x31a2}[kind]
            args=(0xffc0,0,0,top,left) if kind==1 else (3,0,top,left) if kind==10 else (0,top,left)
            o.call_args(ip,args,far=True,cs=0x2000)
        else:
            kind,x,y,ex,ey,color,seed=row;o.call_args(0x1744,(color,128 if kind=='F' else 192),far=True,cs=0x2000)
            if kind=='R':o.call_args(0x107c,(ey,ex,y,x),far=True,cs=0x2000)
            elif kind=='V':o.call_args(0x1774,(ey,y,x),far=True,cs=0x2000)
            elif kind=='D':o.call_args(0x114c,(ex,y,x),far=True,cs=0x2000)
            elif kind=='F':o.call_args(0x1508,cs=0x2aaf)
            else:raise ValueError('unknown raster operation')
    finally:shadow.close()
    return bytes(shadow.screen),shadow.writes,shadow.ports

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','exe','hdi','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--runner');refs=p.add_mutually_exclusive_group();refs.add_argument('--reference-dir',type=Path);refs.add_argument('--pixel-reference-dir',type=Path);p.add_argument('--only',choices=('pixel','raster'));p.add_argument('--limit',type=int);p.add_argument('--defeat-zoom-only',action='store_true')
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    o=Original(a.target.read_bytes());assets=main_assets(a.hdi);manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
    class Rejecting(Original):
        def hook_body(self,u,address,size,unused):
            if address==0x20000+0x1744:raise ValueError('injected Yuuka pixel callback rejection')
            super().hook_body(u,address,size,unused)
    bad=Rejecting(o.target)
    try:bad.call_args(0x1744,(15,192),far=True,cs=0x2000)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('Yuuka pixel callback rejection swallowed')
    files={name:out/name for name in (('MIKO32.BFT',) if a.defeat_zoom_only else ('ST04.BB1','ST04.BB2'))}
    for name,path in files.items():path.write_bytes(assets[name])
    ref=json.loads((a.reference_dir/'receipt.json').read_text()) if a.reference_dir else None
    pixel_ref=json.loads((a.pixel_reference_dir/'receipt.json').read_text()) if a.pixel_reference_dir else None
    for source in (ref,pixel_ref):
        if source and (not source['passed'] or source['target_sha256']!=sha(o.target) or source['hdi_sha256']!=sha(a.hdi.read_bytes())):raise ValueError('Yuuka pixel reference identity differs')
    controls={}
    for mode,rows in ([('pixel',defeat_zoom())] if a.defeat_zoom_only else [('pixel',sprites()),('raster',rasters())]):
        if a.only and a.only!=mode:continue
        rows=list(itertools.islice(rows,a.limit) if a.limit else rows)
        logical='\n'.join(' '.join(map(str,r)) for r in rows)+'\n'
        fixture=out/f'{mode}-fixtures.txt';fixture.write_text('\n'.join(' '.join(map(str,[str(files[r[0]])]+r[1:] if mode=='pixel' else r)) for r in rows)+'\n')
        mode_ref=pixel_ref if mode=='pixel' and pixel_ref else ref
        ref_dir=a.pixel_reference_dir if mode=='pixel' and pixel_ref else a.reference_dir
        trace=ref_dir/f'{mode}-trace.bin' if mode_ref else out/f'{mode}-trace.bin';records=[]
        if mode_ref:
            c=mode_ref['controls'][mode]
            if c['fixture_sha256']!=sha(logical.encode()) or c['cases']!=len(rows) or c['trace_sha256']!=sha(trace.read_bytes()):raise ValueError('Yuuka pixel reference fixture/trace differs')
            records=c['records']
        else:
            with trace.open('wb') as f:
                for i,row in enumerate(rows):
                    screen,writes,ports=expected(o,row,assets);f.write(screen);records.append(dict(input=row,screen_sha256=sha(screen),writes=writes,ports=ports))
                    if (i+1)%100==0:print(mode,i+1,'CPU controls produced',flush=True)
        native=out/f'native-{mode}.bin';env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
        command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),f'--{mode}-vectors',str(fixture)]
        with native.open('wb') as f:subprocess.run(command,check=True,stdout=f,env=env)
        with trace.open('rb') as want,native.open('rb') as actual:
            for i,row in enumerate(rows):
                x=want.read(SCREEN);y=actual.read(SCREEN)
                if len(x)!=SCREEN or x!=y:
                    pos=next((j for j,(q,r) in enumerate(zip(x,y)) if q!=r),min(len(x),len(y)))
                    (out/f'{mode}-mismatch.json').write_text(json.dumps(dict(case=i,input=row,first_pixel=pos,x=pos%640,y=pos//640,expected=x[pos] if pos<len(x) else None,actual=y[pos] if pos<len(y) else None),indent=2)+'\n');raise ValueError(f'Yuuka {mode} case{i} pixel{pos} differs')
            if want.read(1) or actual.read(1):raise ValueError('extra Yuuka pixel output')
        controls[mode]=dict(cases=len(rows),compared_pixels=len(rows)*SCREEN,fixture_sha256=sha(logical.encode()),trace_sha256=sha(trace.read_bytes()),native_sha256=sha(native.read_bytes()),original_cpu_reexecuted=not bool(mode_ref),reference_dir=str(ref_dir.resolve()) if mode_ref else None,reference_source_manifest_sha256=mode_ref.get('source_manifest_sha256') if mode_ref else None,reference_stage=mode_ref.get('stage','native-comparison') if mode_ref else None,records=records)
        print(mode,len(rows),'PASS',flush=True)
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during Yuuka pixel controls')
    receipt=dict(passed=True,callback_rejection_passed=True,original_cpu_reexecuted=all(c['original_cpu_reexecuted'] for c in controls.values()),source_manifest_sha256=manifest,target_sha256=sha(o.target),hdi_sha256=sha(a.hdi.read_bytes()),native_sha256=sha(a.exe.read_bytes()),controls=controls,asset_sha256={name:sha(assets[name]) for name in files},unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='Original MAIN load2000 DS8000 normal/white SUPER2F54/2838, factor3 zoom31A2 including actual color1744/rectangle107C, laser disc114C/vline1774/rectangle107C and backdrop filler0AAF1508/7578. Complete retained640x400 indexed screens.',limits='Bounded GRCG shadow at visible A800 memory; BFNT planar staging is an input adapter. Disc radii0..180, selected full-WORD rectangle/vline edges. Selected negative-X flat visible offsets included; general physical page/alias/scroll/timing and GUI battle remain separate. No DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(passed=True,controls={k:{n:c[n] for n in ('cases','compared_pixels')} for k,c in controls.items()})))
if __name__=='__main__':main()
