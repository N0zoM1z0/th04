#!/usr/bin/env python3
"""Selected original MAIN CPU state/event/draw controls for the Stage2 midboss."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_midboss import Original as Base
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def __init__(self,target):
        self.reject_callback=False;self.error=None
        super().__init__(target)
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as e:self.error=e;u.emu_stop()
    def call_args(self,*args,**kwargs):
        self.error=None
        try:super().call_args(*args,**kwargs)
        except Exception:
            if self.error:raise self.error
            raise
        if self.error:raise self.error
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def event(kind,x=0,y=0,value=0,count=0):self.events.append([kind,x,y,value&65535,count&65535])
        if self.reject_callback and (cs,ip)==(0x33a9,0x126d):raise ValueError('rejected Stage2 callback control')
        if (cs,ip)==(0x33a9,0x126d):event(3,*self.read(0x53b4,'<hh'))
        if cs==0x33a9 and ip in (0x945e,0x9486,0x94a2):
            t=self.template();event(10,t[2],t[3],t[7],t[8])
        if (cs,ip)==(0x33a9,0x64de):event(9,value=1)
        if (cs,ip)==(0x33a9,0x144a):event(8,value=12)
        if (cs,ip)==(0x33a9,0x91):
            g=self.read(0x9586,'<6h2B');event(12,g[0],g[1],g[6],g[5])
        if (cs,ip)==(0x33a9,0x9fa8):
            item,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+2,6));event(11,x,y,item)
            ret=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0];u.reg_write(UC_X86_REG_SP,sp+8);u.reg_write(UC_X86_REG_IP,ret);return
        super().hook(u,address,size,unused)

def record(phase=1,frame=0,sprite=0,x=3072,y=1024,hp=750,damage=19):
    return list(struct.pack('<6hHhBBhBB',x,y,3000,1200,17,0,2600,hp,sprite,phase,frame,damage,213))
def row(op='U',rank=1,perf=16,frame=2600,line=100,scrolling=1,active=1,hpbar=42,pattern=0,direction=1,done=0,density=0,damage=0,zap=0,clear=0,px=3072,py=5120,cursor=0,gather_density=0,state=None):
    return [op,rank,perf,frame,line,scrolling,active,hpbar,pattern,direction,done,density,damage,zap,clear,px,py,cursor,gather_density,*(state or record())]
def fixtures():
    for phase_frame,damage in itertools.product((0,94,95,96,32767,-32768),(0,1,750)):
        yield row(damage=damage,state=record(0,phase_frame,y=-512))
    frames=(0,1,3,7,8,15,23,24,31,47,48,49,50,51,52,63,64,65,32767,-32768)
    for i,(pattern,phase_frame,rank,perf) in enumerate(itertools.product((0,1,2,3,17,255),frames,range(5),(4,16,24))):
        yield row(rank=rank,perf=perf,pattern=pattern,direction=i%3,density=i%2,cursor=255 if i%3==0 else 0,state=record(frame=phase_frame))
    for damage,hp,done,cursor in itertools.product((1,750,65535,32768),(1,750),(0,4,16,17,18),(0,255)):
        yield row(pattern=17,done=done,damage=damage,cursor=cursor,state=record(frame=7,hp=hp))
    for frame,direction,done,cursor,density in itertools.product((0,47,49,51),(0,1,2,255),(0,16,17,255),(0,1,255),(0,1)):
        yield row(pattern=255,direction=direction,done=done,cursor=cursor,gather_density=density,state=record(frame=frame))
    for i,(phase,frame,y) in enumerate(itertools.product((2,3,17,255),(0,15,31,32767,-32768),(-16,0,1,16,1024))):
        yield row(frame=i%16,state=record(phase,frame,y=y))
    for rank,pattern,zap,clear in itertools.product(range(5),range(4),(0,1),(0,17,18,255)):
        yield row(rank=rank,pattern=pattern,zap=zap,clear=clear,state=record(frame=7))
    for phase,sprite,y,frame,line,scrolling in itertools.product((0,1,2,3,255),range(3),(-16,0,1,16,255,256,5888),range(16),(0,399),(0,1)):
        yield row('D',frame=frame,line=line,scrolling=scrolling,state=record(phase,sprite=sprite,y=y))
    for op,frame,active in itertools.product(('A','R'),(2599,2600,2601,65535),(0,1)):
        yield row(op,frame=frame,active=active,state=record(frame=99))
    for rank,damage in itertools.product((1,3),(0,10)):
        state=list(struct.pack('<6hHhBBhBB',3072,-512,3072,-512,0,16,2600,750,0,0,0,0,0))
        yield row('S',rank=rank,perf=22 if rank==3 else 16,damage=damage,cursor=255,state=state)+[2200]

def seed(o,fixture):
    op,rank,perf,frame,line,scrolling,active,hpbar,pattern,direction,done,density,damage,zap,clear,px,py,cursor,gd=fixture[:19]
    o.reset();o.damage=damage;o.context(rank,perf,0,px,py)
    o.u.mem_write(0x853b4,bytes(fixture[19:41]));o.u.mem_write(0x85a22,bytes([int(bool(density))]+[0]*25)*440)
    o.u.mem_write(0x89292,bytes([int(bool(gd))]+[0]*41)*16)
    o.write(0x9586,'<6h2B',2048,1024,17,-19,1024,8,9,2)
    o.write(0x53a2,'<BB4h8B',1,52,2048,1024,17,-19,46,129,42,3,6,123,128,19)
    o.write(0x4272,'<3B',pattern,direction,done);o.write(0x538a,'<H',frame)
    o.write(0x538c,'<4B',frame%2,frame%4,frame%8,frame%16)
    o.write(0x46b2,'<B',active);o.write(0x4278,'<h',line);o.write(0x427c,'<B',scrolling)
    o.write(0x1ed0,'<h',hpbar);o.write(0x435a,'<I',0);o.write(0x3ecc,'<H',cursor)
    o.write(0xbcb9,'<2B',zap,clear);o.write(0xbcb7,'<B',0);o.write(0x1f38,'<B',0)
    o.write(0xbcc4,'<H',(0x9435,0x9440,0x9448,0x9453,0x9440)[rank])
    o.write(0xbcc0,'<H',(0x945e,0x9486,0x94a2,0x94a2,0x9486)[rank])
    o.write(0xbcc2,'<H',(0x94be,0x94da,0x94f6,0x94f6,0x94da)[rank])
    return op

def checkpoint(o):
    values=[o.u.mem_read(0x853b4,22).hex(),*o.read(0x46b2,'<B'),*o.read(0x1ed0,'<h'),*o.read(0x4272,'<3B'),*o.read(0x435a,'<I'),*o.read(0x3ecc,'<H'),*o.read(0xbcb9,'<B'),*o.template(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89292,16*42).hex(),*o.read(0x9586,'<6h2B'),len(o.events),*itertools.chain.from_iterable(o.events),len(o.draws),*itertools.chain.from_iterable(o.draws)]
    return ' '.join(map(str,values))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--limit',type=int)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);manifest,_=source_manifest(Path(__file__).resolve().parents[1]);o=Original(a.target.read_bytes());inputs=[];expected=[];counts={}
    for fixture in fixtures():
        if a.limit and len(inputs)>=a.limit:break
        op=seed(o,fixture)
        inputs.append(' '.join(map(str,fixture)));counts[op]=counts.get(op,0)+1
        if op=='S':
            for tick in range(fixture[41]):
                if not o.read(0x46b2,'<B')[0]:break
                o.events.clear();o.draws.clear();frame=(fixture[3]+tick)&65535
                o.write(0x538a,'<H',frame);o.write(0x538c,'<4B',frame%2,frame%4,frame%8,frame%16)
                o.call_args(0x126d,far=True);o.call_args(0x214a,cs=0x2aaf);expected.append(checkpoint(o))
            if o.read(0x46b2,'<B')[0]:raise ValueError('retained original sequence did not finish')
        else:
            if op=='U':o.call_args(0x126d,far=True)
            elif op=='D':o.call_args(0x214a,cs=0x2aaf)
            elif op=='A':o.call_args(0x6454,far=True)
            else:o.call_args(0x642c,far=True)
            expected.append(checkpoint(o))
    path=out/'fixtures.txt';path.write_text('\n'.join(inputs)+'\n');env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    cmd=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(path)]
    got=[' '.join(line.split()) for line in subprocess.run(cmd,env=env,capture_output=True,text=True,check=True).stdout.splitlines()]
    for i,want in enumerate(expected):
        actual=got[i] if i<len(got) else ''
        if want!=actual:
            x,y=want.split(),actual.split();different=next((j for j,(v,w) in enumerate(zip(x,y)) if v!=w),min(len(x),len(y)))
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i] if i<len(inputs) else "retained sequence",field=different,expected=x,actual=y),indent=2)+'\n');raise ValueError(f'Stage2 midboss case{i} field{different} differs')
    if len(got)!=len(expected):raise ValueError('extra Stage2 midboss checkpoints')
    o.reject_callback=True
    try:o.call_args(0x126d,far=True)
    except ValueError as e:assert str(e)=='rejected Stage2 callback control'
    else:raise ValueError('original callback rejection was swallowed')
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
    trace='\n'.join(expected)+'\n';(out/'trace.txt').write_text(trace)
    receipt=dict(passed=True,counts=counts,cases=len(inputs),trace_records=len(expected),retained_sequences=counts.get("S",0),callback_rejection_passed=True,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(trace.encode()),source_manifest_sha256=manifest,observed_utc=datetime.now(timezone.utc).isoformat(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),scope='MAIN load2000 DS8000; actual13A9:1062..14D3 patterns/dispatcher,original tune/regular-special add,gather3stack/only,scorebonus/LCG/hittest wrapper/HP/activation/reset and0AAF:214A render. Complete22-byte state,3 private bytes,440 bullet records,16 gather records/full templates,ordered requests/draw geometry.',limits='Shot damage injected at actual collision boundary. Spark requests,point popups,Bomb requests,HP pixels and audio/video consumers intercepted. Invalid sprite>2 undefined-register target state excluded. Selected controls and retained midboss-only update/render sequences (other actor updates omitted), not whole Stage2 resources/gameplay/FPS/DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
