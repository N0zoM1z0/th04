#!/usr/bin/env python3
"""Original Reimu foreground and shared NPC backdrop controls; draw consumers adapted."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_orange_render import Original as Base,explosion,renders as explosion_rows
from verify_reimu import orb
from verify_orange import boss
from verify import source_manifest
sha=lambda data:hashlib.sha256(data).hexdigest()
class Original(Base):
    def __init__(self,target):
        self.background_events=[];super().__init__(target)
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(cleanup,far=False):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+cleanup)
            if far:u.reg_write(UC_X86_REG_CS,seg)
            u.reg_write(UC_X86_REG_IP,off)
        if (cs,ip)==(0x2000,0x2838):
            planes,mask,pattern,y,x=struct.unpack('<HHHhh',u.mem_read(0x70000+sp+4,10))
            if planes not in (0xffc0,0xffc6) or mask!=0:raise ValueError('Reimu partial-plane contract differs')
            self.render_draws.append([6 if planes==0xffc6 else 1,x,y,pattern,9 if planes==0xffc6 else 0]);ret(14,True);return
        if (cs,ip)==(0x2000,0x2d3e):
            pattern,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));self.render_draws.append([7,x,y,pattern,0]);ret(10,True);return
        if (cs,ip)==(0x330e,0x5d4):
            image,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));self.background_events.append([2,x,y,image]);ret(10,True);return
        if cs==0x2aaf and ip in (0x20c8,0x2068,0x1426,0x13ea):
            kind={0x20c8:0,0x2068:1,0x1426:3,0x13ea:4}[ip]
            if ip==0x1426:
                if self.read(0xba8e,'H')!=(0x9abc,):raise ValueError('NPC BB pointer not copied')
                cel=struct.unpack('<h',u.mem_read(0x70000+sp+2,2))[0]
            elif ip==0x13ea:
                if self.color!=1:raise ValueError('NPC filler color differs')
                cel=self.color
            else:cel=0
            self.background_events.append([kind,cel,0,0]);ret(4 if ip==0x1426 else 2);return
        super().hook_body(u,address,size,unused)

def render_row(phase=2,frame=0,sprite=136,damage=0,x=3072,y=1024,trail=1,q=None,e=None):
    b=boss(phase,0,x=x,y=y);b[14]=sprite;b[18]=damage
    return [frame,0,73,0,*b,*range(16),*(e or [*explosion(),*explosion(),*explosion()]),254,144,trail,*orb(),*itertools.chain.from_iterable(q or [orb(flag=int(i%3!=0),x=256+i*171,y=-257+i*207) for i in range(32)])]
def render_rows():
    for phase,sprite,frame,damage,trail in itertools.product((0,1,2,12,253,254,255),(0,4,128,136,139,255),range(16),(0,1,255),(0,1,255)):
        yield render_row(phase=phase,sprite=sprite,frame=frame,damage=damage,trail=trail)
    for phase,flag,x,y,frame in itertools.product((0,2,254,255),(0,1,2,255),(-32768,-17,-16,-1,0,6144,32767),(-32768,-257,-256,-255,-1,0,5888,6399,6400,32767),(0,7)):
        yield render_row(phase=phase,x=x,y=y,frame=frame,q=[orb(flag=flag,x=x,y=y)]+[orb() for _ in range(31)])
    for row in explosion_rows():yield row+[254,144,1,*orb(),*itertools.chain.from_iterable(orb() for _ in range(32))]

def compare(o,a,out,mode,rows):
    inputs=[];expected=[]
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'receipt.json').read_text());configured=('\n'.join(' '.join(map(str,row)) for row in rows)+'\n').encode()
        fixture=a.reference_dir/f'{mode}-fixtures.txt';trace=a.reference_dir/f'{mode}-trace.txt';control=ref['controls'][mode]
        if not ref['passed'] or ref['target_sha256']!=sha(o.target) or control['fixture_sha256']!=sha(fixture.read_bytes()) or control['trace_sha256']!=sha(trace.read_bytes()) or sha(configured)!=control['fixture_sha256']:
            raise ValueError('render reference identity/configuration differs')
        inputs=fixture.read_text().splitlines();expected=trace.read_text().splitlines()
        if len(inputs)!=control['cases'] or len(expected)!=control['cases']:raise ValueError('reference control count differs')
    else:
        for row in rows:
            o.reset();o.render_draws=[];o.background_events=[];o.color=0
            if mode=='render':
                frame,clock,tone,changed=row[:4];o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
                o.u.mem_write(0x853ca,bytes(row[4:28]));o.u.mem_write(0x8bcde,bytes(row[28:44]));o.u.mem_write(0x84298,bytes(row[44:92]));o.u.mem_write(0x8bcfa,bytes(row[92:95]));o.u.mem_write(0x8bcfe,bytes(row[95:121]));o.u.mem_write(0x8b204,bytes(row[121:]))
                o.write(0x18d8,'h',clock);o.write(0x3a4,'h',tone);o.write(0x5393,'B',changed);o.call_args(0x83a3,cs=0x2aaf)
                value=[o.u.mem_read(0x84298,48).hex(),*o.read(0x18d8,'h'),*o.read(0x3a4,'h'),*o.read(0x5393,'B'),*o.read(0x53dc,'B'),o.u.mem_read(0x8bcfa,3).hex(),o.u.mem_read(0x8bcfe,26).hex(),o.u.mem_read(0x8b204,832).hex(),len(o.render_draws),*itertools.chain.from_iterable(o.render_draws)]
                b=bytearray(row[4:28]);b[18]=0 if b[15]<254 else b[18]
                if o.u.mem_read(0x853ca,24)!=bytes(b) or o.u.mem_read(0x8bcde,16)!=bytes(row[28:44]):raise ValueError('foreground wrote unrelated BOSS bytes')
            else:
                phase,clock=row;o.write(0x53d9,'B',phase);o.write(0x53da,'h',clock);o.write(0xbcee,'H',0x9abc);o.write(0xba8e,'H',0x1234);o.write(0xba8c,'H',0x13ea)
                o.call_args(0x77e7,cs=0x2aaf);value=[len(o.background_events),*itertools.chain.from_iterable(o.background_events)]
                if phase!=1 and o.read(0xba8e,'H')!=(0x1234,):raise ValueError('unexpected NPC BB copy')
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
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--only',choices=('render','background'));p.add_argument('--limit',type=int);a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    o=Original(a.target.read_bytes());manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
    class Rejecting(Original):
        def hook_body(self,u,address,size,unused):
            if address==0x2aaf0+0x83a3:raise ValueError('injected Reimu foreground rejection')
            super().hook_body(u,address,size,unused)
    bad=Rejecting(o.target)
    try:bad.call_args(0x83a3,cs=0x2aaf)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('foreground callback rejection swallowed')
    if a.reference_dir and a.limit:raise ValueError('reference replay requires the complete fixture set')
    results={}
    for mode,rows in [('render',render_rows()),('background',itertools.product(range(256),(-32768,-65,-64,-63,-8,-7,-1,0,1,2,3,7,8,55,56,63,64,65,119,120,127,128,32767)))]:
        if a.only and a.only!=mode:continue
        results[mode]=compare(o,a,out,mode,itertools.islice(rows,a.limit) if a.limit else rows)
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during render controls')
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),reference_receipt_sha256=sha((a.reference_dir/"receipt.json").read_bytes()) if a.reference_dir else None,callback_rejection_passed=True,controls=results,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 DS8000 foreground0AAF:8347..846E, shared NPC backdrop77E7..7873 and picture7667..768D. Full ordered sprite/explosion requests, damage consumption, retained template/pool/private state, signed clock and BB pointer controls.',limits='Sprite/CDG/tile/filler hardware consumers adapted. Pixel composition, GUI integration and hardware/page/scroll/timing are separate; no DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,controls=results)))
if __name__=='__main__':main()
