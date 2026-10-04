#!/usr/bin/env python3
"""Original Stage4 resource/setup controls and independent native NPC pixels.

File/VRAM consumers are request adapters. Assets independently decoded from the
legal HDI check the native character-dependent portrait/palette composition.
"""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
import unicorn
from verify_stage3_resources import Original
from probe_assets import main_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','hdi','frames','exe','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
    assets=main_assets(a.hdi);o=Original(a.target.read_bytes());setups=[];inputs=[];expected=[]
    for name,geometry in [('ST03.BFT',(32,32,0,27)),('ST03.BMT',(64,64,0,7)),
            ('ST03.BBT',(64,64,0,11)),('ST03B.BBT',(32,32,0,7)),
            ('ST03B21.BBT',(64,64,0,7)),('ST03B22.BBT',(32,32,0,3))]:
        body=assets[name]
        if body[:5]!=b'BFNT\x1a' or struct.unpack_from('<4H',body,8)!=geometry:raise ValueError('Stage4 BFNT geometry changed: '+name)
    if assets['ST03.MPN'][4]!=88 or len(assets['ST03.BB'])!=2048:raise ValueError('Stage4 map/transition geometry changed')
    for character,rank in itertools.product(range(2),range(4)):
        o.reset();o.error=None;o.resources=[];o.write(0x5398,'B',character);o.write(0x4348,'B',rank)
        o.call_args(0x642c,far=True);o.call_args(0xa7b5,far=True)
        wanted=[dict(name='st03.bmt',image=None,slot=None),dict(name='st03bk.cdg' if character else 'st03bk2.cdg',image=0,slot=16),dict(name='st03.bb',image=None,slot=None)]
        if o.resources!=wanted:raise ValueError('Stage4 original loader requests differ')
        if o.read(0x46bc,'3H')!=(0x1824,0x33a9,0x2316):raise ValueError('Stage4 callback ownership differs')
        setups.append(dict(character=character,rank=rank,requests=list(o.resources)))
        for marker in range(0,256,8):
            o.reset();o.error=None;o.resources=[];actor=bytes((marker+i*73)&255 for i in range(22))
            hpbar,angle=marker*257-32768,marker^85;o.u.mem_write(0x853b4,actor)
            o.write(0x46b2,'B',255);o.write(0x1ed0,'h',hpbar);o.write(0x1ed2,'B',angle)
            o.write(0x5398,'B',character);o.write(0x4348,'B',rank)
            o.write(0x4286,'3B',marker,marker^170,marker^85);o.write(0x185e,'B',marker^255)
            o.call_args(0x642c,far=True);o.call_args(0xa7b5,far=True)
            if o.read(0x4286,'3B')!=(marker,marker^170,marker^85) or o.read(0x185e,'B')!=(marker^255,):raise ValueError('Stage4 setup reset private state')
            inputs.append(' '.join(map(str,(rank,*actor,255,hpbar,angle))))
            expected.append(' '.join((o.u.mem_read(0x853b4,22).hex(),str(o.read(0x46b2,'B')[0]),str(o.read(0x1ed0,'h')[0]),str(o.read(0x1ed2,'B')[0]))))
    fixture=a.output.parent/'setup-fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n')
    trace=a.output.parent/'setup-trace.txt';trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--setup-vectors',str(fixture.resolve())]
    got=subprocess.run(command,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    for i,(want,actual) in enumerate(itertools.zip_longest(expected,got)):
        if not want or not actual or want.split()!=actual.split():raise ValueError(f'Stage4 retained setup case{i} differs')
    checks=[]
    for rank,character,shooting in itertools.product(('normal','lunatic'),('reimu','marisa'),('shot','idle')):
        faces=assets['KAO3.CD2' if character=='reimu' else 'KAO2.CD2']
        if struct.unpack_from('<3H',faces)!=(2048,128,128) or faces[10:12]!=bytes((4 if character=='reimu' else 3,1)):raise ValueError('Stage4 NPC portrait geometry changed')
        bmt=assets['ST03B22.BBT' if character=='reimu' else 'ST03B.BBT'];start=32+struct.unpack_from('<H',bmt,28)[0]
        raw=bmt[start:start+48];palette=[tuple((raw[i+c]>>4)*17 for c in (1,2,0)) for i in range(0,48,3)]
        path=a.frames/f'{rank}-{character}-{shooting}-10.bmp';checked=0;used=set()
        with Image.open(path) as image:
            image=image.convert('RGB')
            for y in range(128):
                for x in range(128):
                    offset=(127-y)*16+x//8;mask=0x80>>(x%8)
                    if not faces[16+offset]&mask:continue
                    color=sum(1<<plane for plane in range(4) if faces[16+(plane+1)*2048+offset]&mask)
                    if image.getpixel((288+x,112+y))!=palette[color]:raise ValueError(f'Stage4 NPC asset/palette pixel differs: {path.name} {x},{y}')
                    checked+=1;used.add(color)
        checks.append(dict(image=path.name,opaque_pixels=checked,palette_indices=sorted(used),bmp_sha256=sha(path.read_bytes())))
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            if address==0x33a90+0xa7b5:raise ValueError('injected Stage4 setup rejection')
            super().body(u,address,size,unused)
    rejected=Rejecting(o.target)
    try:rejected.call_args(0xa7b5,far=True)
    except (RuntimeError,ValueError):
        if not isinstance(rejected.error,ValueError):raise
    else:raise ValueError('Stage4 setup rejection swallowed')
    assert manifest==source_manifest(Path(__file__).resolve().parents[1])[0]
    names=('ST03.BFT','ST03.BMT','ST03.MPN','ST03.MAP','ST03.STD','ST03BK.CDG','ST03BK2.CDG','ST03.BB','KAO2.CD2','KAO3.CD2','_DM03.TXT','_DM13.TXT','ST03.BBT','ST03B.BBT','ST03B21.BBT','ST03B22.BBT')
    r=dict(passed=True,callback_rejection_passed=True,original_setups=setups,retained_midboss_setup_controls=len(inputs),portrait_checks=checks,
        target_sha256=sha(o.target),hdi_sha256=sha(a.hdi.read_bytes()),native_sha256=sha(a.exe.read_bytes()),source_manifest_sha256=manifest,
        fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()),asset_sha256={n:sha(assets[n]) for n in names},
        unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),
        scope='Actual MAIN load2000 DS8000 13A9:A7B5..A931 loader requests across2characters/4ordinary ranks;256 retained22byte midboss setup controls including active/sharedHP/angle and4private-state retention. Independent character-dependent archive NPC0/palette pixels across8native routes.',
        limits='BFNT/CDG/BB file/VRAM consumers intercepted; NPC battle not implemented. Independent native asset composition, not complete original VRAM, physical hardware, GUI pacing or DOS exactness.')
    a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print('Stage4 resources, retained setup and independent NPC pixels: PASS')
if __name__=='__main__':main()
