#!/usr/bin/env python3
"""Independent original Yuuka6 normal, red-plane, white and death-zoom pixels.

MAIN0000:2F54/2838/31A2 execute at load2000 DS8000. Real BFNT sheets are
staged as alpha/four-plane input; an independent GRCG shadow retains complete
640x400 indexed screens. No physical VRAM alias/page/pacing or whole-battle
claim. Ordered multi-sprite frames test plane retention across overlaps.
"""
import argparse,gzip,hashlib,itertools,json,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from verify_yuuka5_pixels import Original,Shadow,SCREEN
from verify_marisa_pixels import planes
from probe_assets import main_assets
from verify import source_manifest
sha=lambda data:hashlib.sha256(data).hexdigest()
NAMES=tuple('ST05.BB'+str(n) for n in (1,2,3,4,5,6,7,9))+('MIKO32.BFT',)
COUNTS=(8,6,8,8,8,8,8,8)

def fixtures():
    yield [7,0]
    for name,count in zip(NAMES,COUNTS):
        for image,shift,kind in itertools.product(range(count),range(8),(0,1,11)):
            yield [(image+shift)%16,1,name,image,96+shift,128,kind]
        for image,top,kind in itertools.product(range(count),(-15,383,399),(0,1,11)):
            yield [(image+top)%16,1,name,image,96+(image%8),top,kind]
    for name,image in (('ST05.BB1',0),('ST05.BB9',4),('MIKO32.BFT',4)):
        for x,y,kind in itertools.product((-32768,-17,-16,-1,31,415,639,32767),(-32768,-1,0,15,383,399,32767),(0,1,11)):
            if (x+y+kind)%7==0:yield [(x+y)%16,1,name,image,x,y,kind]
    for image,x,y in itertools.product(range(4,12),(31,32,97,414),(15,16,128,383)):
        yield [(image+x+y)%16,1,'MIKO32.BFT',image,x,y,10]
    # Two body halves and mirror halves retain one screen. Mix red/normal
    # parity, overlapping bodies, auxiliary sprites and a white custom cross.
    for parity,shift,mirror in itertools.product(range(4),range(8),(96,120,144)):
        body=11 if not parity&1 else 0;other=11 if not parity&2 else 0
        yield [13,6,'ST05.BB9',shift%4,120,152,0,
               'ST05.BB1',0,96+shift,128,body,'ST05.BB1',1,144+shift,128,body,
               'ST05.BB1',0,mirror+shift,128,other,'ST05.BB1',1,mirror+48+shift,128,other,
               'ST05.BB9',4,120+shift,152,1]
    # Full prior sprite then red mask at identical coordinates proves that
    # red tint merges destination bits instead of replacing by color2.
    for name,count in zip(NAMES,COUNTS):
        for image in range(count):yield [5,2,name,image,100,128,0,name,image,100,128,11]

def expected(o,row,assets):
    o.reset();o.callback_error=None;o.in_laser=False;o.raw_disc=False
    o.write(0x32c,'6h',32,383,415,16,367,383);o.write(0x338,'H',0xa850)
    shadow=Shadow(o,row[0])
    try:
        for index in range(row[1]):
            name,image,x,y,kind=row[2+index*5:7+index*5];w,h,data=planes(assets[name],image)
            o.write(0x2ac4,'H',0x9000);o.write(0x2ec4,'H',(w//8<<8)|h);o.u.mem_write(0x90000,data)
            ip={0:0x2f54,1:0x2838,11:0x2838,10:0x31a2}[kind]
            args=(0xffcd if kind==11 else 0xffc0,0,0,y,x) if kind in (1,11) else (3,0,y,x) if kind==10 else (0,y,x)
            o.call_args(ip,args,far=True,cs=0x2000)
    finally:shadow.close()
    return bytes(shadow.screen),shadow.writes,shadow.ports

def rejection(target):
    class Rejecting(Original):
        def hook_body(self,u,address,size,unused):
            if address==0x20000+0x2838:raise ValueError('injected red-plane callback rejection')
            super().hook_body(u,address,size,unused)
    bad=Rejecting(target)
    try:bad.call_args(0x2838,(0xffcd,0,0,128,96),far=True,cs=0x2000)
    except RuntimeError as error:
        if not isinstance(error.__cause__,ValueError):raise
    else:raise ValueError('red-plane callback rejection swallowed')

def same(wanted,got):
    if wanted!=got:raise ValueError('Yuuka6 foreground pixels differ')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('target','hdi','exe','output-dir'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--reference-dir',type=Path);parser.add_argument('--runner');parser.add_argument('--limit',type=int)
    args=parser.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    original=Original(args.target.read_bytes());assets=main_assets(args.hdi);manifest=source_manifest(Path(__file__).resolve().parents[1])[0];rejection(original.target)
    rows=list(itertools.islice(fixtures(),args.limit) if args.limit else fixtures());configured=('\n'.join(' '.join(map(str,row)) for row in rows)+'\n').encode()
    asset_hashes={name:sha(assets[name]) for name in NAMES}
    if args.reference_dir:
        ref=json.loads((args.reference_dir/'original-reference.json').read_text());trace=args.reference_dir/'pixel-trace.bin.gz'
        if args.limit or not ref['passed'] or ref['target_sha256']!=sha(original.target) or ref['hdi_sha256']!=sha(args.hdi.read_bytes()) or ref['asset_sha256']!=asset_hashes or ref['fixture_sha256']!=sha(configured) or ref['cases']!=len(rows):raise ValueError('Yuuka6 pixel reference identity differs')
    else:
        trace=out/'pixel-trace.bin.gz';digest=hashlib.sha256();records=[]
        with gzip.open(trace,'wb',compresslevel=3) as file:
            for index,row in enumerate(rows):
                screen,writes,ports=expected(original,row,assets);file.write(screen);digest.update(screen);records.append(dict(screen_sha256=sha(screen),writes=writes,ports=ports))
                if (index+1)%250==0:print('Original Yuuka6 pixels',index+1,'PASS',flush=True)
        # A target-only pair falsifies replacement by pure red. Check only
        # opaque source pixels, independently decoded by the BFNT probe.
        pair=[expected(original,[5,1,'ST05.BB1',0,96,128,kind],assets)[0] for kind in (11,1)]
        occupied=[i for i,(r,w) in enumerate(zip(*pair)) if w==15 and r==7 and ((i*73+5)&15)==5]
        if not occupied:raise ValueError('red-plane retention control found no distinguishing pixels')
        try:same(pair[0],pair[1])
        except ValueError:pass
        else:raise ValueError('red/white perturbation accepted')
        ref=dict(passed=True,target_sha256=sha(original.target),hdi_sha256=sha(args.hdi.read_bytes()),asset_sha256=asset_hashes,source_manifest_sha256=manifest,fixture_sha256=sha(configured),cases=len(rows),pixel_bytes=len(rows)*SCREEN,pixel_trace_sha256=digest.hexdigest(),records=records,red_retains_destination_control=dict(seed=5,red_color=7,white_color=15,distinguishing_pixels=len(occupied),first_pixel=occupied[0],red_sha256=sha(pair[0]),white_sha256=sha(pair[1])),scope=__doc__)
        (out/'original-reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    fixture=out/'fixtures.txt';fixture.write_bytes(configured)
    for name in NAMES:(out/name).write_bytes(assets[name])
    # Native asset bytes and fixture are attested independently of its parser.
    if sha(fixture.read_bytes())!=ref['fixture_sha256']:raise ValueError('fixture write differs')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--pixels',str(fixture)];digest=hashlib.sha256();pbytes=0
    with gzip.open(trace,'rb') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,env=env) as process:
        while True:
            w=wanted.read(65536);g=process.stdout.read(len(w) if w else 1)
            try:same(w,g)
            except ValueError:
                position=next((i for i,(a,b) in enumerate(zip(w,g)) if a!=b),min(len(w),len(g)))
                (out/'mismatch.json').write_text(json.dumps(dict(byte_offset=pbytes+position,screen=(pbytes+position)//SCREEN,pixel=(pbytes+position)%SCREEN,expected=w[position] if position<len(w) else None,actual=g[position] if position<len(g) else None),indent=2)+'\n');process.terminate();raise
            if not w:break
            digest.update(g);pbytes+=len(g)
        if process.wait()!=0:raise ValueError('Yuuka6 pixel consumer failed')
    if pbytes!=ref['pixel_bytes'] or digest.hexdigest()!=ref['pixel_trace_sha256']:raise ValueError('Yuuka6 pixel reference hash/extent differs')
    try:same(b'\x00',b'\x01')
    except ValueError:pass
    else:raise ValueError('pixel byte perturbation accepted')
    default=subprocess.run(command[:-2],capture_output=True,text=True,check=True,env=env).stdout.strip()
    if default!='Stage 6 Yuuka foreground contracts PASS':raise ValueError('Yuuka6 foreground contract failed')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during Yuuka6 pixel controls')
    receipt=dict(ref,original_source_manifest_sha256=ref['source_manifest_sha256'],source_manifest_sha256=manifest,original_cpu_reexecuted=not bool(args.reference_dir),native_sha256=sha(args.exe.read_bytes()),callback_rejection_passed=True,one_byte_rejection_passed=True,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),limits='Actual kernel pixel controls with BFNT planar input adapter and visible-memory GRCG shadow. Selected WORD flat offsets and stage-clipped factor3. Multi-draw screen controls do not execute ordinary core/render dispatcher. No physical VRAM alias/page/palette timing, full battle or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),pixel_bytes=pbytes)))
if __name__=='__main__':main()
