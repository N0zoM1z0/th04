#!/usr/bin/env python3
"""Independent MAIN CPU controls for Yuuka5 foreground/backdrop and filled discs.

Body/explosion geometry and laser graphics calls are request adapters. Disc
controls execute original114C/14DC under actual stage clipping and capture the
complete visible write mask. Physical hardware/page/scroll/pacing is separate.
"""
import argparse,hashlib,itertools,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_orange_render import Original as Base,explosion,renders as explosion_rows
from verify_orange import boss
from verify_lasers import beam
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def __init__(self,target):
        self.background_events=[];self.in_laser=False;self.raw_disc=False;super().__init__(target)
        from unicorn.x86_const import UC_X86_INS_OUT
        self.u.hook_add(unicorn.UC_HOOK_INSN,self.out,None,1,0,UC_X86_INS_OUT)
    def out(self,u,port,size,value,unused):
        if self.in_laser:
            if (port,size,value)!=(0x7c,1,0):self.callback_error=ValueError('unexpected laser disable port');u.emu_stop();return
            self.render_draws.append([9,0,0,0,0,0,0,0])
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(bytes_count,far=True):
            words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2));u.reg_write(UC_X86_REG_SP,sp+bytes_count)
            if far:u.reg_write(UC_X86_REG_CS,words[1])
            u.reg_write(UC_X86_REG_IP,words[0])
        if (cs,ip)==(0x2aaf,0x37d3):self.in_laser=True
        if (cs,ip)==(0x2aaf,0x3f7b):self.in_laser=False
        if cs==0x2000:
            if ip==0x31a2:
                zoom,pattern,y,x=struct.unpack('<HHhh',u.mem_read(0x70000+sp+4,8));self.render_draws.append([10,x,y,pattern,0,0,0,zoom]);ret(12);return
            if ip==0x114c and not self.raw_disc:
                radius,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));self.render_draws.append([6,x,y,radius,self.color,0,0,0]);ret(10);return
            if ip==0x1744:
                color,mode=struct.unpack('<HH',u.mem_read(0x70000+sp+4,4));self.color=color;self.render_draws.append([5,0,0,0,color,0,0,mode]);ret(8);return
            if ip==0x1774:
                bottom,top,x=struct.unpack('<3h',u.mem_read(0x70000+sp+4,6));self.render_draws.append([8,x,top,0,self.color,0,bottom,0]);ret(10);return
            if ip==0x107c:
                bottom,right,top,left=struct.unpack('<4h',u.mem_read(0x70000+sp+4,8));self.render_draws.append([7,left,top,0,self.color,right,bottom,0]);ret(12);return
        if (cs,ip)==(0x330e,0x5d4):
            image,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));self.background_events.append([2,x,y,image]);ret(10);return
        if cs==0x2aaf and ip in (0x20c8,0x2068,0x1426,0x1508):
            if ip==0x1426:
                if self.read(0xba8e,'H')!=(0x9abc,):raise ValueError('Yuuka BB pointer not copied')
                cel=struct.unpack('<H',u.mem_read(0x70000+sp+2,2))[0];self.background_events.append([3,cel,0,0]);ret(4,False)
            else:
                self.background_events.append([{0x20c8:0,0x2068:1,0x1508:4}[ip],0,0,0]);ret(2,False)
            return
        super().hook_body(u,address,size,unused)

def row(phase=2,clock=0,frame=0,damage=0,move=0,x=3072,y=1024,e=None,lasers=None):
    b=boss(phase,clock,x=x,y=y);b[18]=damage
    return [frame,0,73,0,*b,*range(16),*(e or [*explosion(),*explosion(),*explosion()]),21,37,73,129,173,move,*itertools.chain.from_iterable(lasers or [beam(flag=1),beam(),beam()]),127]

def renders():
    for phase,move,clock,frame,damage in itertools.product((0,1,2,3,13,17,18,253,254,255),(0,1,2,3,4,255),(-32768,-1,0,1,7,8,31,32,63,64,32767),(0,3,4,7,8,11,12,15),(0,1,255)):
        if (phase+move+clock+frame+damage)%7:continue
        yield row(phase=phase,move=move,clock=clock,frame=frame,damage=damage)
    for flag,phase,radius,outline in itertools.product((0,1,2,4,128,255),(0,2,254,255),(-32768,-1,0,1,8,16,64,180,32767),(0,8,15,255)):
        yield row(phase=phase,lasers=[beam(flag=1),beam(flag=flag,radius=radius,color=outline),beam(flag=1,x=3200,marker=73)])
    for x,y,move,damage in itertools.product((-32768,-17,-16,-1,0,6144,32767),(-32768,-17,-16,-1,0,5888,32767),range(4),(0,255)):
        yield row(x=x,y=y,move=move,clock=7,damage=damage)
    for r in explosion_rows():yield r+[21,37,73,129,173,0]+list(itertools.chain.from_iterable([beam(flag=1),beam(),beam()]))+[127]

def checkpoint(o):
    draws=[d+[0,0,0] if len(d)==5 else d for d in o.render_draws]
    return ' '.join(map(str,[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),o.u.mem_read(0x84298,48).hex(),o.u.mem_read(0x84322,6).hex(),o.u.mem_read(0x842d8,72).hex(),*o.read(0x4669,'B'),*o.read(0x18d8,'h'),*o.read(0x3a4,'h'),*o.read(0x5393,'B'),len(draws),*itertools.chain.from_iterable(draws)]))
def expected(o,mode,r):
    o.reset();o.callback_error=None;o.render_draws=[];o.background_events=[];o.color=0;o.in_laser=False;o.raw_disc=False
    if mode=='render':
        if len(r)!=171:raise ValueError('invalid Yuuka render fixture size')
        frame,clock,tone,changed=r[:4];o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
        for at,sl in [(0x853ca,r[4:28]),(0x8bcde,r[28:44]),(0x84298,r[44:92]),(0x84322,r[92:98]),(0x842d8,r[98:170])]:o.u.mem_write(at,bytes(sl))
        o.write(0x4669,'B',r[170]);o.write(0x18d8,'h',clock);o.write(0x3a4,'h',tone);o.write(0x5393,'B',changed);o.call_args(0x3db3,cs=0x2aaf);return checkpoint(o)
    if mode=='background':
        phase,clock=r;o.write(0x53d9,'B',phase);o.write(0x53da,'h',clock);o.write(0xbcee,'H',0x9abc);o.write(0xba8e,'H',0x1234);o.write(0xba8c,'H',0x1508);o.call_args(0x7874,cs=0x2aaf)
        if o.read(0xba8e,'H')!=((0x9abc,) if phase==1 else (0x1234,)):raise ValueError('unexpected Yuuka BB pointer ownership')
        return ' '.join(map(str,[len(o.background_events),*itertools.chain.from_iterable(o.background_events)]))
    o.raw_disc=True;x,y,radius=r;o.write(0x32c,'6h',32,383,415,16,367,383);o.write(0x338,'H',0xa850);bits=bytearray(32000)
    def write(u,access,address,size,value,unused):
        for byte in range(size):
            at=address-0xa8000+byte
            if 0<=at<32000:bits[at]|=(value>>(8*byte))&255
    handle=o.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
    try:o.call_args(0x114c,(radius,y,x),far=True,cs=0x2000)
    finally:o.u.hook_del(handle)
    return bits.hex()

def discs():
    for x,y,radius in itertools.product((-32,0,31,32,33,128,224,414,415,416,639),(0,15,16,17,128,200,382,383,384,399),(0,1,3,4,7,8,15,16,31,32,64,80,96,144,160,168,180)):
        if (x+y+radius)%5==0:yield (x,y,radius)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--only',choices=('render','background','disc'));p.add_argument('--limit',type=int)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest=source_manifest(Path(__file__).resolve().parents[1])[0];controls={};ref=json.loads((a.reference_dir/'receipt.json').read_text()) if a.reference_dir else None
    if ref and (not ref['passed'] or ref['target_sha256']!=sha(o.target)):raise ValueError('Yuuka reference identity differs')
    class Rejecting(Original):
        def hook_body(self,u,address,size,unused):
            if address==0x2aaf0+0x3db3:raise ValueError('injected Yuuka foreground rejection')
            super().hook_body(u,address,size,unused)
    bad=Rejecting(o.target)
    try:bad.call_args(0x3db3,cs=0x2aaf)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('Yuuka callback rejection swallowed')
    for mode,rows in [('render',renders()),('background',itertools.product(range(256),(-32768,-65,-64,-63,-4,-3,-1,0,1,2,3,4,7,8,31,32,63,64,1024,32767))),('disc',discs())]:
        if a.only and mode!=a.only:continue
        rows=list(itertools.islice(rows,a.limit) if a.limit else rows);configured='\n'.join(' '.join(map(str,r)) for r in rows)+'\n';fixture=out/f'{mode}-fixtures.txt';fixture.write_text(configured)
        if ref:
            trace=a.reference_dir/f'{mode}-trace.txt';wanted=trace.read_text().splitlines();c=ref['controls'][mode]
            if sha(configured.encode())!=c['fixture_sha256'] or sha(trace.read_bytes())!=c['trace_sha256'] or len(wanted)!=c['cases']:raise ValueError('Yuuka reference fixture/trace differs')
        else:
            wanted=[expected(o,mode,r) for r in rows];trace=out/f'{mode}-trace.txt';trace.write_text('\n'.join(wanted)+'\n')
        env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),f'--{mode}-vectors',str(fixture)]
        got=subprocess.run(command,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
        for i,(want,actual) in enumerate(itertools.zip_longest(wanted,got)):
            if want is None or actual is None or want.split()!=actual.split():
                (out/f'{mode}-mismatch.json').write_text(json.dumps(dict(case=i,input=rows[i] if i<len(rows) else None,expected=want,actual=actual),indent=2)+'\n');raise ValueError(f'Yuuka {mode} case{i} differs')
        controls[mode]=dict(cases=len(rows),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()));print(mode,len(rows),'PASS',flush=True)
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during Yuuka graphics controls')
    r=dict(passed=True,original_cpu_reexecuted=not bool(ref),callback_rejection_passed=True,controls=controls,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 DS8000 Yuuka foreground0AAF:3DB3..3F7E/backdrop7874..7900, common explosions and thicklaser draw37D3. Full retained boss/additional/private/explosion/laser metadata and ordered geometry/zoom/color requests. Disc114C/14DC executes with actual stage32..415/16..383 clipping and visible write-mask comparison.',limits='Body mode/disable and shared explosion hardware controls are not collected; visible requests plus laser controls are compared. Sprite/CDG/BB/filler/HUD/frame pacing/physical hardware are separate; disc pixels are a bounded write mask. No GUI battle/full-stage or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,controls=controls)))
if __name__=='__main__':main()
