#!/usr/bin/env python3
"""Selected original MAIN controls for Kurumi foreground, backdrop and ray masks.

Sprite/CDG/tile requests are adapters. Shared original explosions execute.
Ray mask controls execute original GRCG line with the default screen clip and
capture CPU write masks, not physical GRCG color/VRAM/page behavior.
"""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_orange_render import Original as Base,explosion,renders as explosion_rows,signed
from verify_kurumi import ray
from verify_orange import boss
from verify import source_manifest
sha=lambda data:hashlib.sha256(data).hexdigest()
class Original(Base):
    def __init__(self,target):
        self.raw_line=False;self.background_events=[];super().__init__(target)
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(cleanup,far=False):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+cleanup)
            if far:u.reg_write(UC_X86_REG_CS,seg)
            u.reg_write(UC_X86_REG_IP,off)
        if (cs,ip)==(0x2000,0x1562) and not self.raw_line:
            ey,ex,y,x=struct.unpack('<4h',u.mem_read(0x70000+sp+4,8))
            self.render_draws.append([5,x,y,0,self.color,ex,ey]);ret(12,True);return
        if (cs,ip)==(0x2aaf,0x7667):
            color,y,x=struct.unpack('<3h',u.mem_read(0x70000+sp+2,6));self.background_events.append([2,x,y,color]);ret(8);return
        if cs==0x2aaf and ip in (0x20c8,0x2068,0x14a4,0x10b4):
            kind={0x20c8:0,0x2068:1,0x14a4:3,0x10b4:4}[ip]
            if ip==0x14a4:
                if self.read(0xba8e,'H')!=(0x9abc,):raise ValueError('background BB pointer was not copied')
                cel=struct.unpack('<h',u.mem_read(0x70000+sp+2,2))[0]
            else:cel=0
            self.background_events.append([kind,cel,0,0]);ret(4 if ip==0x14a4 else 2);return
        super().hook_body(u,address,size,unused)

def render_row(phase=2,clock=0,frame=0,sprite=0,damage=0,x=3072,y=1296,rays=None,e=None,big_frame=0):
    b=boss(phase,clock,x=x,y=y);b[14]=sprite;b[18]=damage
    return [frame,big_frame,73,0,*b,*range(16),*(e or [*explosion(),*explosion(),*explosion()]),*itertools.chain.from_iterable(rays or [ray(marker=i*11) for i in range(6)])]
def render_rows():
    for phase,clock,frame,damage in itertools.product((0,1,2,3,4,5,6,253,254,255),(0,128,129,319,320,321,32767,-32768),range(16),(0,1)):
        yield render_row(phase,clock,frame,damage=damage)
    for phase,sprite,frame,damage in itertools.product((0,1,2,254,255),(0,4,6,8,9,10,12,255),range(16),(0,255)):
        yield render_row(phase=phase,sprite=sprite,frame=frame,damage=damage)
    for phase,flag,x,y in itertools.product((0,1,2,6,253,254,255),(0,1,2,255),(-32768,-17,-16,-15,-1,0,1,15,16,17,32767),(-17,-16,-15,-1,0,1,17,32767)):
        rays=[ray(flag,x,y,ox=-x if x!=-32768 else 32767,oy=-y,marker=i*17) for i in range(6)]
        yield render_row(phase=phase,x=x,y=y,rays=rays)
    for row in explosion_rows():
        # Reuse independently selected shared-explosion boundary fixtures.
        yield row+[v for r in [ray(marker=i*13) for i in range(6)] for v in r]

def line_rows():
    for x,y,ex,ey in itertools.product((0,7,8,15,16,32,639),(0,16,399),(0,31,32,639),(0,17,399)):
        yield [x,y,ex,ey]
    for dx,dy,reverse in itertools.product((0,1,2,3,7,15,16,17,31,32,63,127,255),(0,1,2,3,7,15,16,17,31,63,127,255),(0,1)):
        a=[32,128,32+dx,128+dy];yield a[2:]+a[:2] if reverse else a
    for dx,dy in itertools.product((1,3,7,15,31,63,127,255),(1,3,7,15,31,63,127)):
        yield [32,256,32+dx,256-dy]

def compare(o,a,out,mode,rows):
    inputs=[];expected=[]
    for row in rows:
        o.reset();o.render_draws=[];o.background_events=[];o.raw_line=False;o.color=0
        if mode=='render':
            frame,clock,tone,changed=row[:4];o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
            o.u.mem_write(0x853ca,bytes(row[4:28]));o.u.mem_write(0x8bcde,bytes(row[28:44]));o.u.mem_write(0x84298,bytes(row[44:92]));o.u.mem_write(0x8b204,bytes(row[92:]))
            o.write(0x18d8,'h',clock);o.write(0x3a4,'h',tone);o.write(0x5393,'B',changed);o.call_args(0x6ca3,cs=0x2aaf)
            draws=[d if len(d)==7 else d+[0,0] for d in o.render_draws]
            value=[o.u.mem_read(0x84298,48).hex(),*o.read(0x18d8,'h'),*o.read(0x3a4,'h'),*o.read(0x5393,'B'),*o.read(0x53dc,'B'),o.u.mem_read(0x8b204,156).hex(),len(draws),*itertools.chain.from_iterable(draws)]
            assert bytes(o.u.mem_read(0x853ca,24))==bytes(row[4:28]) and bytes(o.u.mem_read(0x8bcde,16))==bytes(row[28:44])
        elif mode=='background':
            phase,clock=row;o.write(0x53d9,'B',phase);o.write(0x53da,'h',clock);o.write(0xbcee,'H',0x9abc);o.write(0xba8e,'H',0x1234)
            o.call_args(0x76fb,cs=0x2aaf);value=[len(o.background_events),*itertools.chain.from_iterable(o.background_events)]
            if phase!=1:assert o.read(0xba8e,'H')==(0x1234,)
        else:
            o.raw_line=True;bits=bytearray(32000)
            def write(u,access,at,size,value,unused):
                for index in range(size):
                    offset=at-0xa8000+index
                    if 0<=offset<32000:bits[offset]|=(value>>(index*8))&255
            hook=o.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
            x,y,ex,ey=row;o.call_args(0x1562,(ey,ex,y,x),far=True,cs=0x2000);o.u.hook_del(hook);value=[bits.hex()]
        inputs.append(' '.join(map(str,row)));expected.append(' '.join(map(str,value)))
    path=out/f'{mode}-fixtures.txt';path.write_text('\n'.join(inputs)+'\n');trace=out/f'{mode}-trace.txt';trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--'+mode+'-vectors',str(path)]
    lines=subprocess.run(command,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    for index,(want,got) in enumerate(itertools.zip_longest(expected,lines)):
        if want is None or got is None or want.split()!=got.split():
            ww=want.split() if want else [];gg=got.split() if got else [];field=next((i for i,(x,y) in enumerate(zip(ww,gg)) if x!=y),min(len(ww),len(gg)))
            (out/f'{mode}-mismatch.json').write_text(json.dumps(dict(case=index,input=inputs[index],field=field,expected=ww,actual=gg),indent=2)+'\n');raise ValueError(f'{mode} case{index} field{field} differs')
    return dict(cases=len(inputs),fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(trace.read_bytes()))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--only',choices=('render','background','line'));p.add_argument('--limit',type=int)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest,_=source_manifest(Path(__file__).resolve().parents[1])
    class Rejecting(Original):
        def hook_body(self,u,address,size,unused):
            if address==0x2aaf0+0x6ca3:raise ValueError('injected Kurumi foreground rejection')
            super().hook_body(u,address,size,unused)
    bad=Rejecting(o.target)
    try:bad.call_args(0x6ca3,cs=0x2aaf)
    except RuntimeError as error:
        if not isinstance(error.__cause__,ValueError):raise
    else:raise ValueError('foreground hook rejection swallowed')
    modes=[('render',render_rows()),('background',itertools.product(range(256),(-32768,-1,0,1,2,3,31,32,319,320,32767))),('line',line_rows())];results={}
    for mode,rows in modes:
        if a.only and a.only!=mode:continue
        results[mode]=compare(o,a,out,mode,itertools.islice(rows,a.limit) if a.limit else rows)
    assert manifest==source_manifest(Path(__file__).resolve().parents[1])[0]
    r=dict(passed=True,callback_rejection_passed=True,controls=results,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 DS8000 Kurumi foreground0AAF:6CA3..6E7A/backdrop76FB..7756/shared explosions2D9C/2E65. Sprite/ray/circle geometry and complete explosion/ray state/flash clocks; BOSS/additional bytes retain unchanged. Background consumers intercepted at request boundaries; BB pointer copy asserted. Ray pixel mask controls execute0000:1562 with actual fixed-point algorithm and default clip,in-screen endpoints only.',limits='Sprite/CDG pixels,color hardware and tile consumers intercepted. Line pixels are CPU-write-mask shadow,no physicalGRCG color/page/scroll/VRAM/fullroute/timing equivalence. No generalized line clipping or DOS exact claim; Kurumi GUI battle is separate.')
    (out/'receipt.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(passed=True,controls=results)))
if __name__=='__main__':main()
