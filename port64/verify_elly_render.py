#!/usr/bin/env python3
"""Original Elly foreground/backdrop CPU controls with bounded draw adapters."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_orange_render import Original as Base,explosion,renders as explosion_rows,signed
from verify_elly import scythe
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
        if (cs,ip)==(0x2aaf,0xee6):
            x,y=struct.unpack('<hh',u.mem_read(0x70000+sp+2,4))
            if self.read(0x4264,'HH')!=(64,64):raise ValueError('Elly invalidation dimensions differ')
            self.background_events.append([5,x,y,64]);ret(6);return
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

def render_row(phase=3,frame=0,sprite=134,damage=0,x=3072,y=1536,q=None,e=None,big_frame=0):
    b=boss(phase,0,x=x,y=y);b[14]=sprite;b[18]=damage
    return [frame,big_frame,73,0,*b,*range(16),*(e or [*explosion(),*explosion(),*explosion()]),*(q or scythe())]
def render_rows():
    for phase,sprite,frame,damage in itertools.product((0,1,2,3,4,253,254,255),(0,4,134,141,255),range(16),(0,1)):
        yield render_row(phase=phase,sprite=sprite,frame=frame,damage=damage)
    for phase,flag,x,y,frame in itertools.product((0,3,254,255),(0,1,2,255),(-32768,-1,0,1,6143,6144,32767),(-32768,-1,0,1,5887,5888,32767),(0,1,6,7)):
        yield render_row(phase=phase,x=x,y=y,frame=frame,q=scythe(flag=flag,x=x,y=y))
    for row in explosion_rows():yield row+scythe()

def compare(o,a,out,mode,rows):
    inputs=[];expected=[]
    for row in rows:
        o.reset();o.render_draws=[];o.background_events=[];o.raw_line=False;o.color=0
        if mode=='render':
            frame,clock,tone,changed=row[:4];o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
            o.u.mem_write(0x853ca,bytes(row[4:28]));o.u.mem_write(0x8bcde,bytes(row[28:44]));o.u.mem_write(0x84298,bytes(row[44:92]));o.u.mem_write(0x846e6,bytes(row[92:]))
            o.write(0x18d8,'h',clock);o.write(0x3a4,'h',tone);o.write(0x5393,'B',changed);o.call_args(0x7322,cs=0x2aaf)
            draws=[d if len(d)==7 else d+[0,0] for d in o.render_draws]
            value=[o.u.mem_read(0x84298,48).hex(),*o.read(0x18d8,'h'),*o.read(0x3a4,'h'),*o.read(0x5393,'B'),*o.read(0x53dc,'B'),o.u.mem_read(0x846e6,19).hex(),len(draws),*itertools.chain.from_iterable(draws)]
            assert bytes(o.u.mem_read(0x853ca,24))==bytes(row[4:28]) and bytes(o.u.mem_read(0x8bcde,16))==bytes(row[28:44])
        elif mode=='background':
            phase,clock,flag=row;o.write(0x46e7,'B',flag);o.write(0x53ce,'hh',1234,-2345);o.write(0x46ec,'hh',-3456,4567);o.write(0x53d9,'B',phase);o.write(0x53da,'h',clock);o.write(0xbcee,'H',0x9abc);o.write(0xba8e,'H',0x1234)
            o.call_args(0x777f,cs=0x2aaf);value=[len(o.background_events),*itertools.chain.from_iterable(o.background_events)]
            if phase!=2:assert o.read(0xba8e,'H')==(0x1234,)
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
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--only',choices=('render','background'));p.add_argument('--limit',type=int)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest,_=source_manifest(Path(__file__).resolve().parents[1])
    class Rejecting(Original):
        def hook_body(self,u,address,size,unused):
            if address==0x2aaf0+0x7322:raise ValueError('injected Elly foreground rejection')
            super().hook_body(u,address,size,unused)
    bad=Rejecting(o.target)
    try:bad.call_args(0x7322,cs=0x2aaf)
    except RuntimeError as error:
        if not isinstance(error.__cause__,ValueError):raise
    else:raise ValueError('foreground hook rejection swallowed')
    modes=[('render',render_rows()),('background',itertools.product(range(256),(-32768,-1,0,1,2,3,31,32,319,320,32767),(0,1,2,255)))];results={}
    for mode,rows in modes:
        if a.only and a.only!=mode:continue
        results[mode]=compare(o,a,out,mode,itertools.islice(rows,a.limit) if a.limit else rows)
    assert manifest==source_manifest(Path(__file__).resolve().parents[1])[0]
    r=dict(passed=True,callback_rejection_passed=True,controls=results,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 DS8000 Elly foreground0AAF:7322..73DA/backdrop777F..77E6/invalidation7757..777E/shared explosions2D9C/2E65. Ordered sprite/explosion requests and complete explosion/scythe state/flash clocks; BOSS/additional bytes retained. BB pointer copy and64x64 previous-position invalidations asserted.',limits='Sprite/CDG/tile/color hardware consumers adapted. No physical GRCG color/page/scroll/VRAM,whole-route,timing or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(passed=True,controls=results)))
if __name__=='__main__':main()
