#!/usr/bin/env python3
"""Selected original MAIN CPU state/event/draw controls for the Stage4 midboss."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_midboss2 import Original as Base, seed as base_seed
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
        if self.reject_callback and (cs,ip)==(0x33a9,0x1824):raise ValueError('rejected Stage4 callback control')
        if (cs,ip)==(0x33a9,0x1824):self.events.append([3,*self.read(0x53b4,'hh'),0,0])
        #9512 sets fixed-speed mode, then calls the existing regular wrapper.
        #Base records that inner request; recording both would count one shot
        #twice. Original pool/template execution is unchanged by this observer.
        if (cs,ip)==(0x33a9,0x19a8):self.events.append([8,0,0,12,0])
        super().body(u,address,size,unused)

def record(phase=1,frame=0,sprite=0,x=3072,y=1024,hp=1200,damage=19,start=2800):
    return list(struct.pack('<6hHhBBhBB',x,y,3000,1200,17,0,start,hp,sprite,phase,frame,damage,213))
def row(op='U',rank=1,perf=16,frame=2800,line=100,scrolling=1,active=1,hpbar=42,pattern=0,unused_state=1,done=0,density=0,damage=0,zap=0,clear=0,px=3072,py=5120,cursor=0,gather_density=0,state=None,aim=255):
    return [op,rank,perf,frame,line,scrolling,active,hpbar,pattern,unused_state,done,density,damage,zap,clear,px,py,cursor,gather_density,*(state or record()),255,aim]
def fixtures():
    for clock,damage in itertools.product((0,46,47,48,32767,-32768),(0,1,1200)):yield row(damage=damage,state=record(0,clock,y=-512))
    clocks=(0,1,2,7,8,15,16,23,24,25,26,31,32,63,119,120,121,127,128,135,136,137,143,144,151,152,159,160,32767,-32768)
    for i,(pattern,clock,rank,perf) in enumerate(itertools.product((0,1,2,3,17,255),clocks,range(5),(4,16,24))):
        yield row(rank=rank,perf=perf,pattern=pattern,unused_state=i%256,aim=i%256,density=i%2,cursor=255 if i%3==0 else 0,state=record(frame=clock,x=(3071,3072,3073)[i%3]))
    for damage,hp,done,start,x,y in itertools.product((0,1,1200,65535,32768),(1,1200),(0,7,8),(2800,5600),(0,3072,6144),(1024,5888)):
        yield row(pattern=17,done=done,damage=damage,state=record(frame=7,hp=hp,x=x,y=y,start=start))
    for clock,done,x in itertools.product((0,1,2,63,32767,-32768),(0,7,8,255),(-513,-512,-1,0,1,767,768,769,2879,2880,5375,5376,5377,6143,6144,6655,6656,6657)):
        yield row(pattern=255,done=done,state=record(frame=clock,x=x))
    for phase,clock,sprite,start in itertools.product((2,3,17,254,255),(0,15,31,127,32767,-32768),(4,11,255),(2800,5600)):
        yield row(state=record(phase,clock,sprite,start=start))
    for phase,sprite,x,y,clock,scrolling in itertools.product((0,1,2,3,254,255),(0,3,4),(-1,0,1,3071,3072,3073,6143,6144),(-1,0,1,5887,5888),(0,15,16,47,48,-32768),(0,1)):
        yield row('D',line=399,scrolling=scrolling,state=record(phase,clock,sprite,x=x,y=y))
    for op,frame,active in itertools.product(('A','R'),(2799,2800,2801,65535),(0,1)):yield row(op,frame=frame,active=active,state=record(frame=99))
    for rank,damage,cursor,start in itertools.product((1,3),(0,10),(0,255),(2800,5600)):
        x,vx=(2304,64) if start==2800 else (3840,-64)
        state=list(struct.pack('<6hHhBBhBB',x,-512,x,-512,vx,32,start,1200,0,0,0,0,0))
        yield row('S',rank=rank,perf=22 if rank==3 else 16,damage=damage,cursor=cursor,state=state)+[2800]

def seed(o,fixture):
    op=base_seed(o,fixture[:41])
    o.write(0x4286,'<3B',fixture[8],fixture[10],fixture[9]);o.write(0x1ed2,'B',fixture[41]);o.write(0x185e,'B',fixture[42])
    return op

def checkpoint(o):
    values=[o.u.mem_read(0x853b4,22).hex(),*o.read(0x46b2,'<B'),*o.read(0x1ed0,'<h'),*o.read(0x4286,'B'),*o.read(0x4288,'B'),*o.read(0x4287,'B'),*o.read(0x185e,'B'),*o.read(0x1ed2,'B'),*o.read(0x435a,'<I'),*o.read(0x3ecc,'<H'),*o.read(0xbcb9,'<B'),*o.template(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89292,16*42).hex(),*o.read(0x9586,'<6h2B'),len(o.events),*itertools.chain.from_iterable(o.events),len(o.draws),*itertools.chain.from_iterable(o.draws)]
    return ' '.join(map(str,values))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--limit',type=int);p.add_argument('--reference-dir',type=Path)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);manifest,_=source_manifest(Path(__file__).resolve().parents[1]);o=Original(a.target.read_bytes());inputs=[];expected=[];counts={}
    if a.reference_dir:
        if a.limit:raise ValueError('reference replay requires the complete fixture set')
        reference=a.reference_dir.resolve();r=json.loads((reference/'receipt.json').read_text())
        inputs=[' '.join(map(str,fixture)) for fixture in fixtures()]
        fixture_bytes=('\n'.join(inputs)+'\n').encode()
        if not r['passed'] or r['target_sha256']!=sha(o.target):raise ValueError('invalid original reference identity')
        if r['fixture_sha256']!=sha(fixture_bytes) or (reference/'fixtures.txt').read_bytes()!=fixture_bytes:raise ValueError('reference fixture set changed')
        trace_bytes=(reference/'trace.txt').read_bytes()
        if sha(trace_bytes)!=r['trace_sha256']:raise ValueError('reference trace digest changed')
        expected=trace_bytes.decode().splitlines();counts=r['counts']
        if len(expected)!=r['trace_records'] or len(inputs)!=r['cases']:raise ValueError('reference record count changed')
    else:
        for fixture in fixtures():
            if a.limit and len(inputs)>=a.limit:break
            op=seed(o,fixture)
            inputs.append(' '.join(map(str,fixture)));counts[op]=counts.get(op,0)+1
            if op=='S':
                for tick in range(fixture[43]):
                    if not o.read(0x46b2,'<B')[0]:break
                    o.events.clear();o.draws.clear();frame=(fixture[3]+tick)&65535
                    o.write(0x538a,'<H',frame);o.write(0x538c,'<4B',frame%2,frame%4,frame%8,frame%16)
                    o.call_args(0x1824,far=True);o.call_args(0x2316,cs=0x2aaf);expected.append(checkpoint(o))
                if o.read(0x46b2,'<B')[0]:raise ValueError('retained original sequence did not finish')
            else:
                if op=='U':o.call_args(0x1824,far=True)
                elif op=='D':o.call_args(0x2316,cs=0x2aaf)
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
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i] if i<len(inputs) else "retained sequence",field=different,expected=x,actual=y),indent=2)+'\n');raise ValueError(f'Stage4 midboss case{i} field{different} differs')
    if len(got)!=len(expected):raise ValueError('extra Stage4 midboss checkpoints')
    o.reject_callback=True
    try:o.call_args(0x1824,far=True)
    except ValueError as e:assert str(e)=='rejected Stage4 callback control'
    else:raise ValueError('original callback rejection was swallowed')
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
    trace='\n'.join(expected)+'\n';(out/'trace.txt').write_text(trace)
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),reference_receipt_sha256=sha((a.reference_dir/'receipt.json').read_bytes()) if a.reference_dir else None,counts=counts,cases=len(inputs),trace_records=len(expected),retained_sequences=counts.get("S",0),callback_rejection_passed=True,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(trace.encode()),source_manifest_sha256=manifest,observed_utc=datetime.now(timezone.utc).isoformat(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),scope='MAIN load2000 DS8000; actual13A9:14E8..1ABE patterns/dispatcher, original tune/regular/fixed add/bonus/LCG/hit/HP/activation/reset and0AAF:2316 render/shared6FAA defeat. Complete22-byte actor,4private bytes,440bullets/16gathers/templates and ordered events/draw geometry; first-encounter rearm5600 and second termination.',limits='Hit damage injected; spark/point/HP/audio/video consumers adapted. Midboss-only retained update/render sequences omit other actor updates. No original full-stage VRAM,physical hardware,GUI pacing or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
