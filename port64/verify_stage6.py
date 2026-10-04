#!/usr/bin/env python3
"""Execute original Stage6 reset/setup and compare all retained actor bytes.

BFNT/CDG/BB file consumers are explicit request adapters. This probe checks
actual null callback ownership, the lone ST05.BB request, retention of the
preceding CDG/colorfill pointer, and rank defaults. GUI/physical VRAM remain
separate claims.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import unicorn
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_SP, UC_X86_REG_IP, UC_X86_REG_AX
import struct
from verify_stage3_resources import Original
from verify_dialog import Original as DialogOriginal
from probe_assets import main_assets
from verify import source_manifest

def sha(data):
    return hashlib.sha256(data).hexdigest()

def setup(original, rank, marker):
    o=original; o.reset(); o.error=None; o.resources=[]; o.calls=[]
    boss=bytes((marker+i*73)&255 for i in range(24))
    extra=bytes((marker+i*19)&255 for i in range(16))
    explosions=bytes((marker+i*37)&255 for i in range(48))
    midboss=bytes((marker+i*11)&255 for i in range(22))
    o.u.mem_write(0x853ca,boss); o.u.mem_write(0x8bcde,extra)
    o.u.mem_write(0x84298,explosions); o.u.mem_write(0x853b4,midboss)
    hpbar=marker*257-32768; angle=marker^85
    o.write(0x46b2,'B',255); o.write(0x1ed0,'h',hpbar)
    o.write(0x1ed2,'B',angle); o.write(0x4348,'B',rank)
    # A Stage5 colorfill pointer and occupied CDG16 header must survive.
    o.write(0xba8c,'H',0x3db3)
    cdg=bytes((marker+i*31)&255 for i in range(16))
    o.u.mem_write(0x80000+0x3978+16*16,cdg)
    o.call_args(0x642c,far=True); o.call_args(0xa9ec,far=True)
    if o.error: raise RuntimeError('original Stage6 adapter rejected') from o.error
    if o.resources!=[dict(name='st05.bb',image=None,slot=None)]:
        raise ValueError('Stage6 unexpectedly loads a BMT/CDG')
    if o.read(0x46bc,'3H')!=(0x11c0,0x2aaf,0x11be):
        raise ValueError('Stage6 null midboss callback ownership changed')
    if o.read(0xbcd6,'4H')!=(0x7dc9,0x79ee,0x33a9,0x712a):
        raise ValueError('Stage6 boss callback ownership changed')
    if o.read(0x432a,'2H')!=(0x11be,0x11be):
        raise ValueError('Stage6 retained a preceding stage callback')
    if o.read(0xba8c,'H')!=(0x3db3,) or bytes(o.u.mem_read(0x80000+0x3978+16*16,16))!=cdg:
        raise ValueError('Stage6 changed retained CDG/colorfill ownership')
    values=[o.u.mem_read(at,size).hex() for at,size in
            ((0x853ca,24),(0x8bcde,16),(0x84298,48),(0x853b4,22))]
    values.extend(map(str,(*o.read(0x46b2,'B'),*o.read(0x1ed0,'h'),
                          *o.read(0x1ed2,'B'),*o.read(0xbcf0,'hh'),*o.read(0x23ed,'B'))))
    fixture=' '.join(map(str,(rank,*boss,*extra,*explosions,*midboss,255,hpbar,angle)))
    return fixture,' '.join(values)

class GateOriginal(DialogOriginal):
    def body(self,u,address,size):
        cs=u.reg_read(UC_X86_REG_CS); ip=address-cs*16
        if (cs,ip) in ((0x2aaf,0xcae),(0x2aaf,0xecb)):
            self.gate_events.append('std-free' if ip==0xcae else 'map-free')
            sp=u.reg_read(UC_X86_REG_SP); ret=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0]
            u.reg_write(UC_X86_REG_SP,sp+2); u.reg_write(UC_X86_REG_IP,ret); return
        if (cs,ip)==(0x2aaf,0x2bfb): self.gate_events.append('dialog')
        super().body(u,address,size)
    def event(self,kind,a=0,b=0,c=0,d=0,name=b''):
        if kind==8: self.gate_events.append('cdg-free '+str(a))
        super().event(kind,a,b,c,d,name)

def gates(target):
    original=GateOriginal(target); records=[]
    for stage,speed,page in itertools.product(range(7),(0,1),(0,1,2)):
        original.reset(); original.gate_events=[]; original.dialog_events=[]
        original.activations=0; original.error=None
        original.write(0x4277,'B',speed); original.write(0x46fc,'B',page)
        original.write(0x5394,'B',stage); original.write(0x1868,'H',77)
        original.call_args(0x2454,cs=0x2aaf)
        if original.error: raise RuntimeError('original Stage6 gate callback rejected') from original.error
        ready=speed==0 and page==1
        wanted=(['cdg-free 31','std-free','map-free'] if stage in (5,6) else [])+['dialog'] if ready else []
        if original.gate_events!=wanted or original.activations!=int(ready) or (original.u.reg_read(UC_X86_REG_AX)&255)!=int(ready) or original.read(0x1868,'H')[0]!=77+int(not ready):
            raise ValueError('original Stage6 resource-release gate/order differs')
        records.append(dict(stage=stage,speed=speed,page=page,events=original.gate_events))
    return records

def dialogue(a,out,target):
    if not a.hdi and not a.dialog_exe: return []
    if not a.hdi or not a.dialog_exe: raise ValueError('supply both HDI and dialog consumer')
    assets=main_assets(a.hdi); original=DialogOriginal(target); records=[]
    for character,held in itertools.product(range(2),(0,1)):
        name=f'_DM{character}5.TXT'; body=assets[name]
        original.reset(); original.held=held; original.dialog_events=[]
        original.u.mem_write(0x90000,body+bytes(4)); original.write(0x428c,'HH',0,0x9000)
        original.scene(); end=original.read(0x428c,'H')[0]
        if end!=(1044 if character==0 else 910): raise ValueError('original Stage6 pre-battle scene cursor differs')
        path=out/f'{name}-{held}.txt'; path.write_bytes(body)
        command=([a.runner] if a.runner else [])+[str(a.dialog_exe.resolve()),'--trace',str(path),str(held),'1']
        env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
        actual=subprocess.run(command,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
        if actual!=original.dialog_events: raise ValueError('original Stage6 complete scene requests differ')
        frees=[line for line in actual if line.startswith('8 ')]
        if len(frees)!=31: raise ValueError('Stage6 did not release every CDG1..31')
        trace='\n'.join(actual)+'\n';(out/f'{name}-{held}-trace.txt').write_text(trace)
        records.append(dict(script=name,held=held,end_offset=end,events=len(actual),
                            script_sha256=sha(body),trace_sha256=sha(trace.encode())))
    return records

def portraits(a):
    if not a.frames: return []
    if not a.hdi: raise ValueError('portrait checks require an HDI')
    from PIL import Image
    assets=main_assets(a.hdi); faces=assets['BSS5.CD2']; sheet=assets['ST05.BB2']
    if struct.unpack_from('<3H',faces)!=(2048,128,128) or faces[10:12]!=bytes((2,1)):
        raise ValueError('Stage6 portrait geometry changed')
    at=32+struct.unpack_from('<H',sheet,28)[0]; raw=sheet[at:at+48]
    palette=[tuple((raw[i+c]>>4)*17 for c in (1,2,0)) for i in range(0,48,3)]
    records=[]
    for difficulty,character,shot,shooting in itertools.product(('normal','lunatic'),('reimu','marisa'),('a','b'),('idle','shot')):
        path=a.frames/f'{difficulty}-{character}-{shot}-{shooting}-5.bmp'
        checked=0
        with Image.open(path) as image:
            image=image.convert('RGB')
            for y in range(128):
                for x in range(128):
                    offset=(127-y)*16+x//8; mask=0x80>>(x%8)
                    if not faces[16+offset]&mask: continue
                    color=sum(1<<plane for plane in range(4) if faces[16+(plane+1)*2048+offset]&mask)
                    if image.getpixel((288+x,112+y))!=palette[color]: raise ValueError('Stage6 portrait/palette pixel differs')
                    checked+=1
        records.append(dict(image=path.name,pixels=checked,bmp_sha256=sha(path.read_bytes())))
    return records

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'): p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner'); p.add_argument('--hdi',type=Path)
    p.add_argument('--dialog-exe',type=Path); p.add_argument('--frames',type=Path); a=p.parse_args()
    out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
    o=Original(a.target.read_bytes())
    gate_records=gates(o.target);dialog_records=dialogue(a,out,o.target);portrait_records=portraits(a)
    pairs=[setup(o,rank,marker) for rank,marker in itertools.product(range(4),range(256))]
    fixture=out/'fixtures.txt'; trace=out/'trace.txt'
    fixture.write_text('\n'.join(row for row,_ in pairs)+'\n')
    expected=[value for _,value in pairs]; trace.write_text('\n'.join(expected)+'\n')
    command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--stage6-setup-vectors',str(fixture)]
    env=os.environ.copy(); env.setdefault('WINEDEBUG','-all')
    actual=subprocess.run(command,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    for i,(want,got) in enumerate(itertools.zip_longest(expected,actual)):
        if want!=got: raise ValueError(f'Stage6 setup case{i}: {got} != {want}')
    # A wrong Stage5 interval must fail even when all retained bytes agree.
    negative=list(actual); fields=negative[256].split(); damaged=bytearray.fromhex(fields[1])
    damaged[0]=160; fields[1]=damaged.hex(); negative[256]=' '.join(fields)
    if negative==expected: raise ValueError('Stage6 rank negative control failed')
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            if address==0x33a90+0xa9ec: raise ValueError('injected Stage6 setup rejection')
            super().body(u,address,size,unused)
    rejected=Rejecting(o.target)
    try: setup(rejected,1,77)
    except (RuntimeError,ValueError):
        if not isinstance(rejected.error,ValueError): raise
    else: raise ValueError('Stage6 callback rejection swallowed')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:
        raise ValueError('sources changed during Stage6 verification')
    receipt=dict(passed=True,cases=len(pairs),original_cpu_reexecuted=True,
                 gates=gate_records,dialogue=dialog_records,portrait_checks=portrait_records,
                 dialog_native_sha256=sha(a.dialog_exe.read_bytes()) if a.dialog_exe else None,
                 hdi_sha256=sha(a.hdi.read_bytes()) if a.hdi else None,
                 callback_rejection_passed=True,rank_negative_control_passed=True,
                 source_manifest_sha256=manifest,target_sha256=sha(o.target),
                 native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),
                 trace_sha256=sha(trace.read_bytes()),unicorn_version=unicorn.__version__,
                 unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
                 observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,
                 limits='MAIN load2000 DS8000;13A9:A9EC..AA87 and reset642C/A4D1. Valid ordinary rank0..3 only; Extra has separate stagex_setup. Invalid rank4 original selector reads far return CS through its unchecked stack index, while native rejects it. File loaders intercepted. No original full-route, physical PC98 or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Stage6 retained setup controls:',len(pairs),'PASS')

if __name__=='__main__': main()
