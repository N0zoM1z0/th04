#!/usr/bin/env python3
"""Original CPU controls for Stage4 Marisa, four bits and ten attacks.

Actual13A9:2F8A..422E and shared shot wrapper/tune/allocation/RNG/score/
explosion/gather/spark/defeat helpers execute. Damage/audio/video/item/point
consumers are bounded adapters. Native bytes are intentionally nonexact.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX
from verify_reimu import Original as Base
from verify_orange import initialize as base_initialize,boss as boss_bytes
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
ATTACKS={0:0x340d,1:0x34d1,2:0x35e9,3:0x36ed,4:0x38a5,5:0x3a01,6:0x3c0e,7:0x3dfe,10:0x336f,11:0x3d83}
class Original(Base):
    def body(self,u,address,size,unused):
        if getattr(self,'reject',False) and address==0x33a90+0x3f64:raise ValueError('injected Marisa callback rejection')
        super().body(u,address,size,unused)
def bit(flag=0,angle=96,x=2048,y=1024,pattern=136,distance=512,speed=32,hp=400,damage=173,turn=2,marker=19):
    return list(struct.pack('<BB3h8B4hBb',flag,angle,x,y,pattern,*[(marker+i*37)&255 for i in range(8)],distance,speed,hp,damage,marker&255,turn))
def fixture(phase=2,clock=0,mode=0,steps=1,rank=1,perf=16,frame=12808,power=64,damage=0,density=0,timed_out=1,patterns=0,hp=6000,end=0,x=3072,y=1024,pool=None,player=(3072,5120),op='U',alive=0,variant=0,turn=2,callback=0x3494,prev=10,previous_alive=0,cycle=1,pulse=0,tick=0,mark=64,duration=96):
    b=boss_bytes(phase,clock,mode,hp,end,x,y,patterns);b[14]=128
    extra=[(i*17+9)&255 for i in range(16)];extra[13]=tick;extra[14]=32;extra[15]=mark
    pool=pool if pool is not None else [bit(marker=i*11+9) for i in range(32)]
    return [op,steps,rank,perf,frame,power,damage,density,timed_out,*b,*extra,prev,previous_alive,pulse,turn&255,alive,cycle,variant,0,callback,*[111+i*17 for i in range(8)],220,400,280,450,*itertools.chain.from_iterable(pool),*player,duration]
def fixtures():
    for turn,angle in itertools.product((0,1,127,128,255),(0,127,255)):
        row=fixture(op='I',turn=turn);row[66:70]=[0,-1,32767,-32768];yield row
    for i,(flag,turn,distance,speed,damage) in enumerate(itertools.product((0,1,2,3,127,128,158,159,160,254,255),(-128,-1,0,1,127),(-32768,-1,0,63,64,1023,1024,32767),(-32,0,32),(0,257,65535))):
        if i%13:continue
        pool=[bit(flag=flag,turn=turn,distance=distance,speed=speed,hp=(0,1,257,32767)[i%4])]+[bit(marker=j*11+9) for j in range(1,32)]
        yield fixture(op='O',pool=pool,damage=damage,player=(2048,1024),density=i%3)
    for dx,dy in itertools.product((-193,-192,-191,191,192,193),repeat=2):
        yield fixture(op='O',pool=[bit(flag=3,distance=0,speed=0)]+[bit() for _ in range(31)],player=(3072+dx,1024+dy))
    for flag,callback,alive,turn,density in itertools.product((0,1,3,127,128,255),(0x3494,0x35d1),range(5),(-128,-1,0,127),(0,1,2)):
        pool=[bit(flag=flag,angle=i*64,turn=turn,x=2048+i*512,y=1024+i*256) for i in range(4)]+[bit() for _ in range(28)]
        yield fixture(op='F',pool=pool,alive=alive,callback=callback,density=density)
    for mode,clock in itertools.product((0,1,6,7,255),(-32768,-1,0,16,30,32,34,36,43,44,47,60,63,64,65,32767)):
        yield fixture(op='E',mode=mode,clock=clock)
    for clock,x,y in itertools.product((-32768,-1,0,1,31,32,33,64,65,32767),(-32768,1791,1792,3072,4352,4353,32767),(-32768,1279,1280,1792,2304,2305,32767)):
        yield fixture(op='M',clock=clock,x=x,y=y)
    for tick,duration,x,y in itertools.product((0,1,63,64,95,96,127,254,255),(-32768,-1,0,1,11,14,64,96,32767),(0,3072,32767),(0,1792,32767)):
        if tick==0 and duration==14 and ((3072-x)==-32768 or (1792-y)==-32768):continue
        yield fixture(op='Y',tick=tick,duration=duration,x=x,y=y)
    for alive,damage,hp,clock in itertools.product((0,1,4,127,255),(0,1,255,256,257,65535),(-32768,0,1,6000),(-1,32767)):
        yield fixture(op='H',alive=alive,damage=damage,hp=hp,clock=clock)
    clocks=(-32768,-1,0,16,30,32,34,36,44,63,64,65,68,96,97,128,129,160,161,192,193,224,225,256,257,384,385,32767)
    for mode,clock,rank,alive in itertools.product(ATTACKS,clocks,range(4),(0,1,4)):
        pool=[bit(flag=int(i<alive),angle=i*64,x=2048+i*512,y=1024+i*256) for i in range(4)]+[bit() for _ in range(28)]
        yield fixture(op='A',mode=mode,clock=clock,rank=rank,perf=22 if rank==3 else 16,alive=alive,pool=pool,callback=0x35d1 if mode in (2,4,5,6) else 0x3494,mark=64,density=(clock+mode)%3,variant=rank%3)
    for phase,clock,rank,alive,damage in itertools.product((0,1,2,3,254,255),(0,15,16,31,32,63,64,95,96,97,127,128,416,488,32767),range(4),(0,4),(0,257)):
        yield fixture(phase=phase,clock=clock,mode=255 if phase==2 else 0,rank=rank,alive=alive,damage=damage)
    for hp,variant,power,damage in itertools.product((4501,4500,2501,2500,1001,1000,1,0),range(4),(0,123,124,128),(0,19)):
        yield fixture(mode=17,clock=65,hp=hp,variant=variant,power=power,damage=damage)
    # Whole-owner attack sequences stop on the first completed pattern.
    # Full boss controls below continue through retained mode choice.
    for mode,rank,alive in itertools.product(ATTACKS,range(4),(0,4)):
        pool=[bit(flag=int(i<alive),angle=i*64,x=2048+i*512,y=1024+i*256) for i in range(4)]+[bit() for _ in range(28)]
        yield fixture(op='P',steps=420,mode=mode,clock=0,rank=rank,alive=alive,pool=pool,callback=0x35d1 if mode in (2,4,5,6) else 0x3494)
    for rank,damage in itertools.product(range(4),(0,19)):
        row=fixture(op='S',phase=0,clock=0,mode=0,steps=18000,rank=rank,damage=damage,hp=0,end=0,mark=0,callback=0)
        row[13:17]=list(struct.pack('<hh',3072,1024));row[17:21]=[0]*4;yield row

def initialize(o,row):
    base_initialize(o,row[:49]);o.write(0xbcf0,'hh',384,384);o.u.mem_write(0x8432e,bytes(row[49:56]));o.write(0x4669,'B',row[56]);o.write(0x4336,'H',row[57]);o.write(0x4338,'8h',*row[58:66]);o.write(0x1a5e,'4h',*row[66:70]);o.u.mem_write(0x8b204,bytes(row[70:902]));o.write(0x464e,'hh',*row[902:904]);o.write(0x1b5c,'B',0);o.write(0xbcb7,'BB',0,0)
def checkpoint(o,result=0):
    bg=o.read(0x426c,'H')[0];backgrounds={0:0,0x20c8:2,0x77e7:4}
    if bg not in backgrounds:raise ValueError('unknown Marisa background callback')
    private=bytes(o.u.mem_read(0x8432e,7))+bytes(o.u.mem_read(0x84669,1))+bytes(o.u.mem_read(0x84336,18))+bytes(o.u.mem_read(0x81a5e,8))
    values=[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0xbcf0,'hh'),*o.read(0x4642,'hh'),*o.read(0x23ed,'B'),*o.read(0x2a82,'3B'),*o.read(0x5393,'B'),*o.read(0x4252,'B'),*o.read(0xba8a,'B'),*o.read(0x4662,'B'),backgrounds[bg],*o.read(0x427e,'hh'),*o.read(0x5390,'H'),*o.read(0xbcca,'B'),*o.read(0x988,'B'),*o.read(0x435a,'I'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,16*42).hex(),o.u.mem_read(0x853e2,96*16).hex(),*o.read(0x41f4,'H'),o.u.mem_read(0x84298,48).hex(),private.hex(),o.u.mem_read(0x8b204,832).hex(),*o.read(0xbcb7,'BB'),result,len(o.events),*itertools.chain.from_iterable(o.events)]
    if o.read(0x1b5c,'B')!=(0,):raise ValueError('against-boss flag leaked')
    return ' '.join(map(str,values))
def original_divide_failures(target):
    records=[]
    for duration,x,y in ((12,3072,1024),(13,3072,1024),(10,-29696,1024),(10,3072,-30976)):
        # A faulted Unicorn instance is discarded. Its pending exception state
        # cannot serve as the starting state of the next independent control.
        o=Original(target);initialize(o,fixture(op='Y',duration=duration,x=x,y=y,tick=0))
        try:o.call_args(0x30f5,args=(duration,))
        except unicorn.UcError as error:
            if error.errno!=unicorn.UC_ERR_EXCEPTION:raise
        else:raise ValueError('original flystep divide failure was swallowed')
        ip=o.u.reg_read(UC_X86_REG_IP)
        if ip not in (0x3117,0x3130) or o.read(0xbceb,'B')!=(0,):raise ValueError('unexpected original divide failure or writes')
        velocity=o.read(0x53d2,'hh')
        if velocity!=((0,-19) if ip==0x3130 else (17,-19)):raise ValueError('original sequential flystep writes differ')
        records.append(dict(duration=duration,x=x,y=y,ip=ip,velocity=velocity,tick=0))
    return records

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--limit',type=int);p.add_argument('--reference-dir',type=Path);a=p.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest=source_manifest(Path(__file__).resolve().parents[1])[0];counts={};sequences=[];divide_failures=original_divide_failures(o.target)
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
                    entry={'I':0x3175,'O':0x31da,'F':0x3347,'E':0x2f8a,'M':0x3059,'Y':0x30f5,'H':0x3f2c}.get(row[0],0x3f64)
                    if row[0]=='A':entry=ATTACKS[row[28]]
                    o.call_args(entry,args=(row[904],) if row[0]=='Y' else (),far=row[0] in ('U','S','P'))
                    result=o.u.reg_read(UC_X86_REG_AX)&255 if row[0] in ('E','Y','H') else 0
                    trace.write(checkpoint(o,result)+'\n')
                    if row[0]=='P' and o.read(0x53dd,'B')==(255,):finished=True;break
                    if row[0]=='S' and any(e[0]==9 for e in o.events):finished=True;break
                if row[0]=='P' and not finished:raise ValueError('Marisa attack sequence missed completion')
                if row[0]=='S':
                    if not finished:raise ValueError('retained Marisa sequence did not reach departure')
                    sequences.append(dict(rank=row[2],damage=row[6],frames=step+1,phases=sorted(phases),modes=sorted(modes)));print(f'Marisa rank{row[2]} damage{row[6]} frames{step+1} original PASS',flush=True)
        fixture_path.write_text('\n'.join(inputs)+'\n')
        # Record target-only expectations before comparing candidate output.
        # Native mismatch cannot invalidate successful original CPU execution;
        # its separate candidate receipt must still report failure.
        original_digest=hashlib.sha256();original_records=0
        with gzip.open(expected,'rt') as trace:
            for line in trace:original_digest.update(line.encode());original_records+=1
        o.reject=True
        try:o.call_args(0x3f64,far=True)
        except RuntimeError as e:
            if not isinstance(e.__cause__,ValueError):raise
        else:raise ValueError('original callback rejection silently passed')
        o.reject=False
        target_reference=dict(passed=True,original_cpu_completed=True,callback_rejection_passed=True,
            target_sha256=sha(o.target),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=original_digest.hexdigest(),
            trace_records=original_records,counts=counts,sequences=sequences,verifier_sha256=sha(Path(__file__).read_bytes()),
            scope='Target-only CPU expectations; no native equivalence claim. Candidate comparison receives a separate receipt.')
        (out/'original-reference.json').write_text(json.dumps(target_reference,indent=2)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)]
    # Default contracts check the independently observed pre-IDIV writes and
    # unknown callback rejection before the large state/event comparison.
    result=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve())],capture_output=True,text=True,check=True,env=env)
    if result.stdout.strip()!='Stage 4 Marisa core contracts PASS':raise ValueError('native Marisa failure controls rejected')
    digest=hashlib.sha256();records=0
    with gzip.open(expected,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            if want is None or got is None or want.split()!=got.split():
                ww=want.split() if want else [];gg=got.split() if got else [];field=next((i for i,(x,y) in enumerate(zip(ww,gg)) if x!=y),min(len(ww),len(gg)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,field=field,expected=ww,actual=gg),indent=2)+'\n');process.terminate();raise ValueError(f'Marisa checkpoint{index} field{field} differs')
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native Marisa process failed')
    if reference and (digest.hexdigest()!=reference['trace_sha256'] or records!=reference['trace_records']):raise ValueError('reference trace digest differs')
    o.reject=True
    try:o.call_args(0x3f64,far=True)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('original callback rejection silently passed')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during controls')
    receipt=dict(passed=True,divide_failures=divide_failures,original_cpu_reexecuted=not bool(a.reference_dir),callback_rejection_passed=True,counts=counts,cases=sum(counts.values()),trace_records=records,sequences=sequences,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=digest.hexdigest(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,limits='Selected original state/event controls and boss-only retained sequences. Full stage updates/render/pacing and physical hardware excluded; original shot/audio/video/item/point consumers adapted. Rendering and stage integration have separate foreground/pixel/natural-route controls; player death/Bomb/audio still unported; no DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=receipt['cases'],trace_records=records)))
if __name__=='__main__':main()
