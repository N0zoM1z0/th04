#!/usr/bin/env python3
"""Original MAINE branch/PI requests and full fade/key clock controls.

Original _main selects filenames and ordering. Ending/Staff/verdict/register,
initialization, PI, sound and process execution are explicit call adapters.
The fades, frame delays and keyboard loops execute original instructions.
PI pixel decoding is a retained native regression dependency, not physical VRAM.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess

from unicorn.x86_const import *
from verify_cutscene import Original as Base,ending_assets,PAYLOAD_SHA
from verify_maine_join import return_to_caller
from verify_verdict import canonical_clock
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
MAIN_SHA='9a44bbf57b6d60fa16f8a78415d969b62c6bf1c596c36fc20a779749cedd92a8'

class Original(Base):
    def __init__(self,target,decoded,load):
        super().__init__(target,decoded,load)
        assert sha(self.payload[0xa102:0xa292])==MAIN_SHA

    def event(self,*args,**kwargs):
        super().event(*args,**kwargs)
        if self.clock_mode:self.events[-1]=f'{self.clock} '+self.events[-1]

    def held(self):
        t=self.clock-self.wait_start;p=self.profile
        if p==0:return t>=8
        if p==1:return t<5 or t>=15
        if p==2:return (t<12 and t!=6) or t>=20
        if p==3:return 2<=t<6 or t>=15
        return t==8 or t>=20

    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;segment=cs-self.load
        sp=u.reg_read(UC_X86_REG_SP)
        def words(n,far=True):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+(4 if far else 2),n*2))
        if cs==self.cs and ip==0xff00:self.done=True;u.emu_stop();return
        if segment==0xa05:
            if ip==9:
                u.reg_write(UC_X86_REG_AX,0x9000 if self.config_present else 0)
                return_to_caller(u,far=False);return
            if ip in (0x6d,0x13fd,0x20a8,0x27c4):
                self.flow.append([dict(zip((0x6d,0x13fd,0x20a8,0x27c4),('ending','staff','verdict','register')))[ip],self.clock])
                # The separately CPU-controlled verdict returns after a full
                # blackout. Preserve that child-call boundary for this owner.
                if ip==0x20a8:self.write(0x132,'h',0)
                return_to_caller(u,far=False);return
            if ip==0x3a:
                off,seg=words(2,False);assert bytes(u.mem_read(seg*16+off,3))==b'op\0'
                self.flow.append(['exec_op',self.clock]);return_to_caller(u,4,False);return
            if 0xb2<=ip<=0x241:
                if ip==0x199:self.congratulations_stop=self.clock
                return
        if segment==0:
            if self.clock_mode and 0x5623<=ip<=0x5646:
                if ip==0x5623:
                    assert words(5)==(0xeca,self.ds,0x17d2,self.ds,48)
                return # Execute the original far memcpy, including its ABI.
            if self.clock_mode and 0x622<=ip<0x6a3:
                if ip in (0x622,0x666):self.event('fade',0,int(ip==0x622),words(1)[0])
                return
            if ip in (0x622,0x666):
                self.event('fade',0,int(ip==0x622),words(1)[0]);return_to_caller(u,2);return
            if ip==0x2206:self.clock+=1;return_to_caller(u);return
            if ip==0x19ec:
                tone=self.read(0x132,'h')[0]
                if tone!=self.previous_tone:self.previous_tone=tone;self.palette.append(f'PALETTE {self.clock} {tone}')
                return_to_caller(u);return
            if ip in (0xeee,0x19e0):return_to_caller(u);return
            if ip==0xf2e:return_to_caller(u,4);return
            if ip==0x1274:self.event('pi_free');return_to_caller(u,8);return
            if ip==0x11c2:self.event('copy_page',words(1)[0]);return_to_caller(u,2);return
        if segment==0xcc7:
            if self.clock_mode and 0x48<=ip<0x6d:
                # Execute the actual PI palette copy/show wrapper. Omitting
                # its palette_show loses the zero-tone observation at t0.
                if ip==0x48:self.event('pi_palette')
                return
            if ip==0x7cc:return_to_caller(u,4);return
            if ip==0x33a:return_to_caller(u,4);return
            if ip==0x31c:
                assert words(1)==(0x204,);self.flow.append(['sound_fade4',self.clock]);return_to_caller(u,2);return
            if self.clock_mode and 0x33<=ip<0x48:
                if ip==0x33:self.delay_frames=words(1)[0]
                if ip==0x3c and self.read(0xefa,'H')[0]<self.delay_frames:
                    self.clock+=1;self.write(0xefa,'H',self.read(0xefa,'H')[0]+1)
                return
            if ip==0x33:
                assert words(1)==(100,);self.flow.append(['delay100',self.clock]);return_to_caller(u,2);return
            if self.clock_mode and 0x20a<=ip<0x260:
                if ip==0x20a:self.event('wait',words(1)[0]);self.wait_start=self.clock
                return
            if ip==0x20a:self.event('wait',words(1)[0]);return_to_caller(u,2);return
            if ip in (0x81a,0x822):
                keys=0x20 if self.held() else 0
                self.write(0x1b42,'H',keys if ip==0x81a else self.read(0x1b42,'H')[0]|keys)
                return_to_caller(u);return
            if ip==0xf5:
                off,seg,slot=words(3);assert slot==0
                raw=bytes(u.mem_read(seg*16+off,32));name=raw[:raw.index(0)]
                self.event('pi_load',name=name);return_to_caller(u,6);return
            if ip==0x48:assert words(1)==(0,);self.event('pi_palette');return_to_caller(u,2);return
            if ip==0x6d:
                slot,y,x=words(3);assert slot==0
                self.event('pi_put',x,y);return_to_caller(u,6);return
        raise ValueError(f'unexpected original main control {segment:04x}:{ip:04x}')

    def run(self,character,rank,end,clock=False,profile=0,config=True):
        self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
        resident=bytearray(256);resident[0x12]=48+character;resident[0xf]=rank;resident[0x30]=end
        resident[0x11]=6 if end==253 else 5
        self.u.mem_write(0x90000,bytes(resident));self.write(0xe9e,'HH',0,0x9000)
        self.clock_mode=clock;self.profile=profile;self.config_present=config
        self.clock=0;self.wait_start=0;self.previous_tone=-1;self.palette=[];self.flow=[]
        self.congratulations_stop=None;self.events=[];self.error=None;self.done=False;self.font_mode=False
        for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),
                          (UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):
            self.u.reg_write(reg,value)
        self.u.mem_write(0x7f000,struct.pack('<HH',0xff00,self.cs))
        self.u.emu_start(self.cs*16+0xb2,0x10ffff,count=500000)
        if self.error:raise RuntimeError('original main adapter rejected') from self.error
        assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xf004
        assert bytes(self.u.mem_read(0x90000,256))==resident
        return self.events

def run(exe,runner,*arguments):
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    result=subprocess.run(([runner] if runner else [])+[str(exe.resolve()),*map(str,arguments)],capture_output=True,env=env,timeout=180)
    if result.returncode:raise RuntimeError(f'native command returned {result.returncode}: '+result.stderr.decode(errors='replace'))
    return result.stdout.replace(b'\r\n',b'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded-dir','hdi','exe','font-bmp','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--baseline-exe',type=Path);p.add_argument('--reference-dir',type=Path)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    assets=ending_assets(args.hdi);private=out/'assets';private.mkdir(exist_ok=True)
    rows=[];all_loads=[]
    for load in (0x1000,0x2000):
        original=Original(args.target,args.decoded_dir,load);lines=[];flows=[]
        for character in range(2):
            for rank in range(5):
                trace=original.run(character,rank,255);lines.extend([f'CASE {character} {rank}',*trace])
                for profile in range(5):
                    events=original.run(character,rank,255,True,profile)
                    assert original.congratulations_stop is not None
                    register=next(t for kind,t in original.flow if kind=='register')
                    assert register-original.congratulations_stop==100
                    lines.extend([f'CLOCK {character} {rank} {profile}',*events,*original.palette,f'STOP {original.congratulations_stop}'])
                if load==0x2000:
                    name=f'CONG{character}{rank}.PI';(private/name).write_bytes(assets[name])
                    rows.append(dict(index=character*5+rank,name=name))
            for rank in range(4):
                for end in (0,253,254,255):
                    events=original.run(character,rank,end)
                    flow=[kind for kind,t in original.flow]
                    if end>=254:
                        assert flow==['ending','staff','verdict','sound_fade4','delay100','register','sound_fade4','exec_op']
                        assert bool(events)==(end==255 or rank==0)
                    elif end==253:assert flow==['delay100','register','verdict','sound_fade4','exec_op']
                    else:assert flow==['delay100','register','verdict','sound_fade4','exec_op'] and not events
                    flows.append(dict(character=character,rank=rank,end=end,events=events,flow=flow))
        assert not original.run(0,0,255,config=False) and not original.flow
        encoded=('\n'.join(lines)+'\n').encode();all_loads.append(encoded)
        if load==0x2000:(out/'main-route-controls.json').write_text(json.dumps(flows,indent=2)+'\n')
    assert all_loads[0]==all_loads[1],'main/clock load metamorphism differs'
    expected=all_loads[0];(out/'original.txt').write_bytes(expected)
    actual=run(args.exe,args.runner,'--congratulations-trace');(out/'native.txt').write_bytes(actual)
    assert canonical_clock(actual)==canonical_clock(expected),'native congratulations requests/clock differ'
    pages=out/'pages';pages.mkdir(exist_ok=True)
    run(args.exe,args.runner,'--congratulations-render',private,args.font_bmp.resolve(),pages)
    states=(pages/'states.txt').read_text().splitlines();assert len(states)==10
    if args.reference_dir:
        proof=json.loads((args.reference_dir/'receipt.json').read_text());assert proof['passed']
        assert proof['main_sha256']==MAIN_SHA and proof['original_sha256']==sha(expected)
    else:
        if not args.baseline_exe:raise ValueError('retained native PI decoder baseline required')
    records=[]
    for row in rows:
        name=row['name'];index=row['index'];decoded=out/(name+'.raw')
        run(args.exe,args.runner,'--decode',private/name,decoded)
        if args.reference_dir:
            previous=(args.reference_dir/(name+'.raw')).read_bytes()
            pinned=next(r for r in proof['picture_cases'] if r['name']==name)
            assert sha(previous)==pinned['decoded_sha256']
            assert sha(assets[name])==pinned['picture_sha256']
        else:
            baseline=out/(name+'.baseline.raw');run(args.baseline_exe,None,'--decode',private/name,baseline);previous=baseline.read_bytes()
        data=decoded.read_bytes();assert data==previous and struct.unpack_from('<II',data)==(640,400) and len(data)==128056
        expected_page=bytes(v for b in data[56:] for v in (b>>4,b&15))
        hashes=[]
        for page in (0,1):
            actual_page=(pages/f'{index}-{page}.bin').read_bytes();assert actual_page==expected_page
            hashes.append(sha(actual_page))
        palette=data[8:56];assert (pages/f'{index}.pal').read_bytes()==palette
        assert states[index].split()==list(map(str,(index,0,0,100,8)))
        records.append(dict(**row,picture_sha256=sha(assets[name]),decoded_sha256=sha(data),page_sha256=hashes,palette_sha256=sha(palette)))
    mf,source=source_manifest(Path(__file__).resolve().parents[1])
    receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),main_sha256=MAIN_SHA,payload_sha256=PAYLOAD_SHA,
      original_sha256=sha(expected),native_canonical_sha256=sha(canonical_clock(actual)),clock_controls=50,
      picture_cases=records,complete_pages=20,main_branch_controls=32,missing_config_control=True,load_segments=[4096,8192],
      source_manifest=mf,source_files=source,executable_sha256=sha(args.exe.read_bytes()),font_sha256=sha(args.font_bmp.read_bytes()),
      scope='Full original _main branch/filename/PI requests plus original fade/key clocks; child Ending/Staff/verdict/register, initialization/PI/sound/exec are guarded adapters. Native congratulations20 complete pages use preceding-native PI decoder regression; no physical VRAM/audio/save/Extra game integration claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Congratulations: 32 original main branches, 50 original fade/key clocks, 20 complete pages PASS')

if __name__=='__main__':main()
