#!/usr/bin/env python3
"""Independent original CPU controls for Reimu's state, fixed orb pool and ten attacks.

Actual 13A9:AE87..BE5D and shared aim/shot wrapper/tune/allocation/RNG/score/
explosion/gather/spark/defeat helpers execute. Damage and video/audio/item/point
consumers are bounded adapters, not whole-game or physical-hardware emulation.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX
from verify_elly import Original as Base
from verify_orange import initialize as base_initialize,boss as boss_bytes
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if getattr(self,'reject',False) and (cs,ip)==(0x33a9,0xb91b):raise ValueError('injected Reimu callback rejection')
        if (cs,ip)==(0x2aaf,0x5ac9) and self.read(0x1b5c,'B')==(0,):
            x,y,rx,ry=self.read(0x449e,'4h');self.events.append([1,x,y,rx,ry]);u.reg_write(UC_X86_REG_AX,self.damage&65535)
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off);return
        super().body(u,address,size,unused)
def orb(flag=0,angle=96,x=2048,y=1024,ox=3000,oy=1200,vx=17,vy=-19,time=64,distance=512,speed=56,turn=4,marker=19):
    return list(struct.pack('<BB6hHhh4BBb',flag,angle,x,y,ox,oy,vx,vy,time,distance,-173,*[(marker+i*37)&255 for i in range(4)],speed,turn))
def fixture(phase=2,clock=0,mode=0,steps=1,rank=1,perf=16,frame=12808,power=64,damage=0,density=0,timed_out=1,patterns=0,hp=9100,end=7900,x=3072,y=1024,orbs=None,template=None,player=(3072,5120),op='U',offset=19,count=6,pulse=0,pattern8=0):
    b=boss_bytes(phase,clock,mode,hp,end,x,y,patterns);b[14]=128
    extra=[(i*17+9)&255 for i in range(16)]
    extra[:7]=((4,16,1,23,8,18,6),(6,12,2,23,9,16,8),(8,8,3,24,9,14,9),(12,6,4,24,10,10,10))[rank if rank<4 else 1]
    extra[10]=patterns%4
    pool=orbs if orbs is not None else [orb(marker=i*11+9) for i in range(32)]
    return [op,steps,rank,perf,frame,power,damage,density,timed_out,*b,*extra,254,144,77,*(template or orb()),*itertools.chain.from_iterable(pool),pattern8,pulse,0,*player,offset,count]
def fixtures():
    for op,density,angle,count,turn in itertools.product(('M','I'),(0,1,2),(0,127,255),(-2,1,4,12,32,33),( -128,-1,0,1,127)):
        pool=[orb(flag=int(bool(density) and (density==1 or i%2)),marker=i*11+9) for i in range(32)]
        yield fixture(op=op,orbs=pool,template=orb(angle=angle,turn=turn),offset=angle,count=count)
    for i,(flag,time,turn,distance) in enumerate(itertools.product((0,1,2,3,255),(0,1,65535),(-128,-1,0,1,127),(-32768,-1,0,1023,1024,32767))):
        pool=[orb(flag=flag,time=time,turn=turn,distance=distance,speed=i%256)]+[orb() for _ in range(31)]
        yield fixture(op='O',orbs=pool,damage=(0,1,257,65535)[i%4],player=(2048,1024))
    for x,y,vx,vy in itertools.product((-32768,-1,0,6144,6145,32767),(-32768,0,5887,5888,32767),(-32768,-64,0,64,32767),(-32768,-16,0,16,32767)):
        yield fixture(op='O',orbs=[orb(flag=2,x=x,y=y,vx=vx,vy=vy)]+[orb() for _ in range(31)],player=(x,y))
    for dx,dy in itertools.product((-193,-192,-191,191,192,193),repeat=2):
        yield fixture(op='O',orbs=[orb(flag=3)]+[orb() for _ in range(31)],player=(2048+dx,1024+dy))
    for direction,red in itertools.product((0,1,127,128,255),(0,1,63,64,65,239,240,241,254,255)):
        row=fixture(op='P',pulse=direction);row+= [red];yield row
    clocks=(-32768,-1,0,1,13,14,15,16,18,22,26,30,31,32,34,38,42,45,46,47,48,63,64,95,96,97,111,112,127,128,129,179,180,191,192,223,224,287,288,999,1000,32767)
    for phase,mode,clock,rank in itertools.product((0,1,2,3,4,5,6,7,8,9,10,11,12,254,255),(0,1,2,3,17,255),clocks,range(4)):
        if mode not in ({2:(0,1,255),4:(0,1,2,3,255),6:(0,1,255),8:(0,1,255),9:(0,1,255)}.get(phase,(0,))):continue
        yield fixture(phase=phase,mode=mode,clock=clock,rank=rank,perf=22 if rank==3 else 16,density=(clock+phase)%3)
    for phase,patterns,damage,power,timed_out in itertools.product((2,4,6,8,9),(0,8,9,10,11,12,17,18,255),(0,1,255,256,257,65535),(0,123,124,128),(0,1)):
        if (phase+patterns+damage+power+timed_out)%7:continue
        yield fixture(phase=phase,clock=48,patterns=patterns,hp=7901,end=7900,damage=damage,power=power,timed_out=timed_out)
    for rank,damage in itertools.product(range(4),(0,19)):
        row=fixture(op='S',phase=0,clock=0,mode=0,steps=18000,rank=rank,damage=damage,hp=0,end=0)
        row[9+4:9+8]=list(struct.pack('<hh',3072,1024));row[9+8:9+12]=[0]*4;yield row

def initialize(o,row):
    base_initialize(o,row[:49]);o.write(0xbcf0,'hh',384,384);o.u.mem_write(0x8bcfa,bytes(row[49:52]));o.u.mem_write(0x8bcfe,bytes(row[52:78]));o.u.mem_write(0x8b204,bytes(row[78:910]))
    o.write(0x24b6,'BB',*row[910:912]);o.write(0x4669,'B',row[912]);o.write(0x464e,'hh',*row[913:915]);o.write(0x1b5c,'B',0);o.write(0xbcb7,'BB',0,0)
    if row[0]=='P':o.write(0x2a82,'B',row[917])
def checkpoint(o):
    bg=o.read(0x426c,'H')[0];backgrounds={0:0,0x20c8:2,0x77e7:4}
    if bg not in backgrounds:raise ValueError('unknown Reimu background callback')
    values=[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0xbcf0,'hh'),*o.read(0x4642,'hh'),*o.read(0x23ed,'B'),*o.read(0x2a82,'3B'),*o.read(0x5393,'B'),*o.read(0x4252,'B'),*o.read(0xba8a,'B'),*o.read(0x4662,'B'),backgrounds[bg],*o.read(0x427e,'hh'),*o.read(0x5390,'H'),*o.read(0xbcca,'B'),*o.read(0x988,'B'),*o.read(0x435a,'I'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,16*42).hex(),o.u.mem_read(0x853e2,96*16).hex(),*o.read(0x41f4,'H'),o.u.mem_read(0x84298,48).hex(),o.u.mem_read(0x8bcfa,3).hex(),o.u.mem_read(0x8bcfe,26).hex(),o.u.mem_read(0x8b204,832).hex(),*o.read(0x24b6,'Bb'),*o.read(0x4669,'B'),*o.read(0xbcb7,'BB'),len(o.events),*itertools.chain.from_iterable(o.events)]
    if o.read(0x1b5c,'B')!=(0,):raise ValueError('against-boss flag leaked')
    return ' '.join(map(str,values))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--limit',type=int);p.add_argument('--reference-dir',type=Path);a=p.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest=source_manifest(Path(__file__).resolve().parents[1])[0];counts={};sequences=[]
    if a.reference_dir:
        if a.limit:raise ValueError("reference replay requires the complete fixture set")
        ref_receipt=a.reference_dir/('original-reference.json' if (a.reference_dir/'original-reference.json').exists() else 'receipt.json')
        reference=json.loads(ref_receipt.read_text());fixture_path=a.reference_dir/'fixtures.txt';expected=a.reference_dir/'trace.txt.gz'
        if not reference['passed'] or reference['target_sha256']!=sha(o.target) or reference['fixture_sha256']!=sha(fixture_path.read_bytes()):raise ValueError('reference identity differs')
        configured=('\n'.join(' '.join(map(str,row)) for row in fixtures())+'\n').encode()
        if sha(configured)!=reference['fixture_sha256']:raise ValueError('configured fixture set changed')
        counts=reference['counts'];sequences=reference['sequences']
    else:
        reference=None;fixture_path=out/'fixtures.txt';expected=out/'trace.txt.gz';inputs=[]
        with gzip.open(expected,'wt',compresslevel=1) as trace:
            for index,row in enumerate(itertools.islice(fixtures(),a.limit) if a.limit else fixtures()):
                initialize(o,row);inputs.append(' '.join(map(str,row)));counts[row[0]]=counts.get(row[0],0)+1;phases=set();modes=set();finished=False
                for step in range(row[1]):
                    frame=(row[4]+step)&65535;o.events.clear();o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
                    phases.add(o.read(0x53d9,'B')[0]);modes.add(o.read(0x53dd,'B')[0])
                    entry={'M':0xb0a1,'I':0xb0fc,'O':0xb163,'P':0xb8e8}.get(row[0],0xb91b)
                    o.call_args(entry,args=(row[916],row[915]) if row[0]=='I' else (),far=row[0] in ('U','S'));trace.write(checkpoint(o)+'\n')
                    if row[0]=='S' and any(e[0]==9 for e in o.events):finished=True;break
                if row[0]=='S':
                    if not finished:raise ValueError('retained Reimu sequence did not reach departure')
                    sequences.append(dict(rank=row[2],damage=row[6],frames=step+1,phases=sorted(phases),modes=sorted(modes)));print(f'Reimu rank{row[2]} damage{row[6]} frames{step+1} original PASS',flush=True)
        fixture_path.write_text('\n'.join(inputs)+'\n')
        # Record target-only expectations before comparing candidate output.
        # Native mismatch cannot invalidate successful original CPU execution;
        # its separate candidate receipt must still report failure.
        original_digest=hashlib.sha256();original_records=0
        with gzip.open(expected,'rt') as trace:
            for line in trace:original_digest.update(line.encode());original_records+=1
        o.reject=True
        try:o.call_args(0xb91b,far=True)
        except RuntimeError as e:
            if not isinstance(e.__cause__,ValueError):raise
        else:raise ValueError('original callback rejection silently passed')
        o.reject=False
        target_reference=dict(passed=True,original_cpu_completed=True,callback_rejection_passed=True,
            target_sha256=sha(o.target),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=original_digest.hexdigest(),
            trace_records=original_records,counts=counts,sequences=sequences,verifier_sha256=sha(Path(__file__).read_bytes()),
            scope='Target-only CPU expectations; no native equivalence claim. Candidate comparison receives a separate receipt.')
        (out/'original-reference.json').write_text(json.dumps(target_reference,indent=2)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)];digest=hashlib.sha256();records=0
    with gzip.open(expected,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            if want is None or got is None or want.split()!=got.split():
                ww=want.split() if want else [];gg=got.split() if got else [];field=next((i for i,(x,y) in enumerate(zip(ww,gg)) if x!=y),min(len(ww),len(gg)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,field=field,expected=ww,actual=gg),indent=2)+'\n');process.terminate();raise ValueError(f'Reimu checkpoint{index} field{field} differs')
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native Reimu process failed')
    if reference and (digest.hexdigest()!=reference['trace_sha256'] or records!=reference['trace_records']):raise ValueError('reference trace digest differs')
    o.reject=True
    try:o.call_args(0xb91b,far=True)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('original callback rejection silently passed')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during controls')
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),callback_rejection_passed=True,counts=counts,cases=sum(counts.values()),trace_records=records,sequences=sequences,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=digest.hexdigest(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,limits='Selected original state/event controls and boss-only retained sequences. Full stage updates/render/pacing and physical hardware excluded; original shot/audio/video/item/point consumers adapted. Native Reimu rendering and stage integration, player death/Bomb/audio still unported; no DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=receipt['cases'],trace_records=records)))
if __name__=='__main__':main()
