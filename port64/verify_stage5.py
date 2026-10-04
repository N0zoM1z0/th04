#!/usr/bin/env python3
"""Independent original CPU Stage5 setup, star requests and plane-OR controls.

Request adapters bound file operations and tile invalidation. Pixel controls
execute the original CDG producer against ordinary flat visible VRAM storage;
physical PC-98 page/alias/pacing behavior is a separate claim.
"""
import argparse, hashlib, itertools, json, os, struct, subprocess
from datetime import datetime, timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_IP, UC_X86_REG_SP
from verify_stage3_resources import Original as Base
from probe_assets import main_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def __init__(self,target):
        self.star_draws=[];self.invalidations=[];self.capture_stars=True
        super().__init__(target)
    def call_args(self,*args,**kwargs):
        super().call_args(*args,**kwargs)
        if self.error:raise RuntimeError('Stage5 original callback rejected') from self.error
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.capture_stars and (cs,ip)==(0x330e,0x63a):
            dst,plane,slot,top,left=struct.unpack('<HHHhh',u.mem_read(0x70000+sp+4,10))
            if (dst,plane,slot)!=(0xe000,0,17):raise ValueError('Star plane request ownership differs')
            self.star_draws.append((left,top));off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4))
            u.reg_write(UC_X86_REG_SP,sp+14);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off);return
        if (cs,ip)==(0x2aaf,0xee6):
            x,y=struct.unpack('<hh',u.mem_read(0x70000+sp+2,4));width,height=self.read(0x4264,'hh')
            self.invalidations.append((x,y,width,height));off=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0]
            u.reg_write(UC_X86_REG_SP,sp+6);u.reg_write(UC_X86_REG_IP,off);return
        super().body(u,address,size,unused)


def native(exe,runner,option,path,binary=False):
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([runner] if runner else [])+[str(exe.resolve()),option,str(path.resolve())]
    return subprocess.run(command,check=True,capture_output=True,text=not binary,env=env).stdout

def check_lines(expected,got,label):
    for i,(want,actual) in enumerate(itertools.zip_longest(expected,got.splitlines())):
        if want!=actual:raise ValueError(f'{label} case {i}: {actual} != {want}')

def setup(o,rank,marker):
    o.reset();o.error=None;o.resources=[];o.calls=[]
    boss=bytes((marker+i*73)&255 for i in range(24));extra=bytes((marker+i*19)&255 for i in range(16));ex=bytes((marker+i*37)&255 for i in range(48));mid=bytes((marker+i*11)&255 for i in range(22))
    o.u.mem_write(0x853ca,boss);o.u.mem_write(0x8bcde,extra);o.u.mem_write(0x84298,ex);o.u.mem_write(0x853b4,mid)
    hpbar=marker*257-32768;angle=marker^85
    o.write(0x46b2,'B',1);o.write(0x1ed0,'h',hpbar);o.write(0x1ed2,'B',angle);o.write(0x4348,'B',rank)
    o.call_args(0x642c,far=True);o.call_args(0xa932,far=True)
    wanted=[dict(name='st04bk.cdg',image=0,slot=16),dict(name='st04.bb',image=None,slot=None),dict(name='st04.cdg',image=0,slot=17)]
    if o.resources!=wanted:raise ValueError('Stage5 resource request differs')
    if o.read(0x46bc,'3H')!=(0x11c0,0x2aaf,0x11be) or o.read(0xbcd6,'4H')!=(0x7874,0x2b80,0x33a9,0x3db3) or o.read(0x432a,'2H')!=(0x4169,0x40fe):raise ValueError('Stage5 callback ownership differs')
    values=[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),o.u.mem_read(0x84298,48).hex(),o.u.mem_read(0x853b4,22).hex()]
    values.extend(map(str,(*o.read(0x46b2,'B'),*o.read(0x1ed0,'h'),*o.read(0x1ed2,'B'),*o.read(0xbcf0,'hh'),*o.read(0x23ed,'B'),*o.read(0xbcf4,'3h'))))
    return ' '.join(map(str,(rank,*boss,*extra,*ex,*mid,1,hpbar,angle))),' '.join(values)


def star(o,row):
    phase,line,scrolling,*centers=row;o.reset();o.error=None;o.star_draws=[];o.invalidations=[]
    o.write(0x53d9,'B',phase);o.write(0x4278,'h',line);o.write(0x427c,'B',scrolling);o.write(0xbcf4,'3h',*centers)
    o.call_args(0x40fe,cs=0x2aaf);o.call_args(0x4169,cs=0x2aaf)
    values=[*o.read(0xbcf4,'3h'),len(o.star_draws),*[n for d in o.star_draws for n in d],*[n for r in o.invalidations for n in r]]
    return ' '.join(map(str,values))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','hdi','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--frames',type=Path);p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0];assets=main_assets(a.hdi);o=Original(a.target.read_bytes())
    pairs=[setup(o,rank,marker) for rank,marker in itertools.product(range(4),range(256))]
    setup_path=out/'setup-fixtures.txt';setup_path.write_text('\n'.join(row for row,_ in pairs)+'\n')
    setup_trace='\n'.join(want for _,want in pairs)+'\n';(out/'setup-trace.txt').write_text(setup_trace)
    check_lines((want for _,want in pairs),native(a.exe,a.runner,'--setup-vectors',setup_path),'setup')
    boundary=(-32768,-32767,-1,0,1,15,16,383,384,6335,6336,6399,6400,6401,32703,32704,32767)
    rows=[(phase,line,scrolling,y,((y+2133+32768)%65536)-32768,((y-3071+32768)%65536)-32768) for phase,line,scrolling,y in itertools.product((0,1,2,253,254,255),(0,1,39,320,399),(0,1),boundary)]
    centers=[5120,640,3040]
    for frame in range(800):
        rows.append((0,(400-frame)%400,1,*centers));centers=[(v+64)%6400 for v in centers]
    expected=[star(o,row) for row in rows];star_path=out/'star-fixtures.txt';star_path.write_text('\n'.join(' '.join(map(str,row)) for row in rows)+'\n');(out/'star-trace.txt').write_text('\n'.join(expected)+'\n')
    check_lines(expected,native(a.exe,a.runner,'--star-vectors',star_path),'stars')
    cdg=assets['ST04.CDG'];cdg_path=out/'ST04.CDG';cdg_path.write_bytes(cdg)
    if len(cdg)!=3856 or struct.unpack_from('<5H',cdg)!=(960,96,80,6320,3) or cdg[10:12]!=b'\1\0':raise ValueError('Star CDG geometry changed')
    pixel_rows=list(itertools.product((0,8,48,176,304,544),(0,1,79,319,320,321,399),(0,1,399),(0,1,7,15)))
    expected_pixels=bytearray();o.capture_stars=False
    for left,top,display,seed in pixel_rows:
        o.reset();o.error=None;o.u.mem_write(0x50000,cdg[16:]);header=bytearray(cdg[:16]);struct.pack_into('<H',header,14,0x5000);o.u.mem_write(0x80000+0x3978+17*16,bytes(header))
        physical=bytearray(32000)
        # Frame indices retain a deterministic four-bit background. Only its
        # I plane is stored here; the CPU's actual OR writes preserve that plane.
        for y in range(400):
            screen=(y+400-display)%400
            for x in range(640):
                if ((screen*640+x)*73+seed)&8:physical[y*80+x//8]|=0x80>>(x%8)
        o.u.mem_write(0xe0000,bytes(physical));o.call_args(0x63a,args=(0xe000,0,17,top,left),far=True,cs=0x330e)
        raw=o.u.mem_read(0xe0000,32000)
        for screen in range(400):
            physical_y=(screen+display)%400;expected_pixels.extend(raw[physical_y*80:(physical_y+1)*80])
    pixel_path=out/'pixel-fixtures.txt';pixel_path.write_text('\n'.join(f'{cdg_path} '+ ' '.join(map(str,row)) for row in pixel_rows)+'\n')
    (out/'pixel-trace.bin').write_bytes(expected_pixels)
    got=native(a.exe,a.runner,'--pixel-vectors',pixel_path,True)
    if got!=expected_pixels:raise ValueError('Stage5 original OR pixels differ')
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            if address==0x33a90+0xa932:raise ValueError('injected Stage5 setup rejection')
            super().body(u,address,size,unused)
    bad=Rejecting(o.target)
    try:setup(bad,1,77)
    except (RuntimeError,ValueError):
        if not isinstance(bad.error,ValueError):raise
    else:raise ValueError('Original callback rejection swallowed')
    portrait_checks=[]
    if a.frames:
        from PIL import Image
        faces=assets['BSS4.CD2'];bmt=assets['ST04.BB2']
        if struct.unpack_from('<3H',faces)!=(2048,128,128) or faces[10:12]!=b'\4\1':raise ValueError('Stage5 portrait geometry changed')
        at=32+struct.unpack_from('<H',bmt,28)[0];raw=bmt[at:at+48]
        palette=[tuple((raw[i+c]>>4)*17 for c in (1,2,0)) for i in range(0,48,3)]
        for rank,character,shot,shooting in itertools.product(('normal','lunatic'),('reimu','marisa'),('a','b'),('idle','shot')):
            path=a.frames/f'{rank}-{character}-{shot}-{shooting}-5.bmp';checked=0
            with Image.open(path) as image:
                image=image.convert('RGB')
                for y in range(128):
                    for x in range(128):
                        offset=(127-y)*16+x//8;mask=0x80>>(x%8)
                        if not faces[16+offset]&mask:continue
                        color=sum(1<<plane for plane in range(4) if faces[16+(plane+1)*2048+offset]&mask)
                        if image.getpixel((288+x,112+y))!=palette[color]:raise ValueError(f'Stage5 portrait/palette differs {path.name} {x},{y}')
                        checked+=1
            portrait_checks.append(dict(image=path.name,opaque_pixels=checked,bmp_sha256=sha(path.read_bytes())))
    assert manifest==source_manifest(Path(__file__).resolve().parents[1])[0]
    names=('ST04.BFT','ST04.CDG','ST04BK.CDG','ST04.BB','ST04.BB1','ST04.BB2','ST04.MPN','ST04.MAP','ST04.STD','BSS4.CD2','_DM04.TXT','_DM14.TXT')
    receipt=dict(passed=True,setup_cases=len(pairs),star_cases=len(rows),pixel_cases=len(pixel_rows),pixel_bytes=len(expected_pixels),portrait_checks=portrait_checks,callback_rejection_passed=True,target_sha256=sha(o.target),hdi_sha256=sha(a.hdi.read_bytes()),native_sha256=sha(a.exe.read_bytes()),source_manifest_sha256=manifest,asset_sha256={n:sha(assets[n]) for n in names},files_sha256={p.name:sha(p.read_bytes()) for p in (setup_path,out/'setup-trace.txt',star_path,out/'star-trace.txt',pixel_path,out/'pixel-trace.bin')},unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 DS8000 setup13A9:A932..A9EB plus actual midboss_reset; Stage5 stars0AAF:40FE..4168/4169..419D and scroll1120..1147; original rolling OR-plane producer130E:063A..06BB. Ordinary ranks, retained raw actor metadata, signed WORD edge requests, 800 trajectory checkpoints and bounded visible plane placements.',limits='File and tile invalidation consumers adapted. Flat visible E000 storage, not complete physical PC98 alias/page/VRAM/pacing or whole gameplay equality. Pixel requests use well-formed CDG and ordinary placements. No DOS exact promotion.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','setup_cases','star_cases','pixel_cases','pixel_bytes')}))
if __name__=='__main__':main()
