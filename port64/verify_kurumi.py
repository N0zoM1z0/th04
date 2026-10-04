#!/usr/bin/env python3
"""Selected original MAIN CPU controls for Kurumi state, attacks and spawnrays.

Actual boss helpers, tune/add, ring RNG, sparks and gathers execute. Shots return
injected damage; circle/HUD/item/point/dialog/audio/host-delay consumers are
request adapters. Retained sequences advance this owner only, not gameplay or
render. A native-only replay consumes a hash-verified original trace.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_orange import Original as Base,initialize as base_initialize,boss as boss_bytes
from verify import source_manifest
from verify_session import Original as SetupOriginal
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def __init__(self,target):
        self.callback_error=None;super().__init__(target)
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as error:self.callback_error=error;u.emu_stop()
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if (cs,ip)==(0x2aaf,0x1b5a):
            y,x=struct.unpack('<hh',u.mem_read(0x70000+sp+4,4));self.events.append([2,x,y,0,1])
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+8);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off);return
        super().hook(u,address,size,unused)
    def call_args(self,*args,**kwargs):
        self.callback_error=None
        try:super().call_args(*args,**kwargs)
        except Exception:
            if self.callback_error:raise RuntimeError('original Kurumi hook rejected') from self.callback_error
            raise
        if self.callback_error:raise RuntimeError('original Kurumi hook rejected') from self.callback_error

def ray(flag=0,x=3000,y=1200,ox=2048,oy=1024,vx=127,vy=171,marker=19):
    return list(struct.pack('<BB6h12B',flag,marker,x,y,ox,oy,vx,vy,*[(marker+i*17)&255 for i in range(12)]))
def fixture(phase=2,clock=0,mode=0,steps=1,rank=1,perf=16,frame=0,power=64,damage=0,density=0,timed_out=1,patterns=0,hp=4700,end=3300,x=3072,y=1296,angle=192,period=None,toggle=19,rays=None):
    boss=boss_bytes(phase,clock,mode,hp,end,x,y,patterns);boss[14]=0;boss[20]=angle
    additional=[(i*17+9)&255 for i in range(16)];additional[0]=period or (255,128,32,8)[rank]
    return ['S' if steps>1 else 'U',steps,rank,perf,frame,power,damage,density,timed_out,*boss,*additional,toggle,37,*itertools.chain.from_iterable(rays or [ray(marker=i*11+9) for i in range(6)])]

def fixtures():
    for clock,density,damage in itertools.product((0,1,127,128,287,288,295,296,319,320,321,32767,-32768),(0,1,2),(0,256)):
        yield fixture(phase=0,clock=clock,density=density,damage=damage)
    for clock,damage,timed in itertools.product((0,30,31,32,32767,-32768),(0,257),(0,1)):
        yield fixture(phase=1,clock=clock,damage=damage,timed_out=timed)
    for phase,mode,clock,rank in itertools.product((2,4),range(5),(0,15,16,47,48,63,64,65,79,80,95,96,97,32767,-32768),range(4)):
        yield fixture(phase=phase,clock=clock,mode=mode,rank=rank,perf=22 if rank==3 else 16)
    for phase,patterns,damage,power in itertools.product((2,4),(0,5,9,10,11,254,255),(0,1,255,256,257,65535),(0,123,124,127,128,255)):
        if (phase+patterns+damage+power)%7:continue
        yield fixture(phase=phase,clock=96,patterns=patterns,damage=damage,power=power,hp=3301,end=3300)
    for phase,clock,mode,rank,frame in itertools.product((3,5),(0,15,16,63,64,65,127,128,143,144,599,600,698,699,700,2000,2001),range(3),range(4),(0,1,57)):
        yield fixture(phase=phase,clock=clock,mode=mode,rank=rank,frame=frame,hp=2050,end=550)
    for phase,clock,damage,toggle in itertools.product((3,5,6),(15,31,599,600,699,700),(0,1,255,256,257,65535),(0,1,254,255)):
        yield fixture(phase=phase,clock=clock,mode=1,damage=damage,hp=1,end=0,toggle=toggle)
    for flag,x,y,density in itertools.product((0,1,2,255),(-1,0,1,6143,6144),(0,1,5887,5888),(0,1,2)):
        rays=[ray(flag,x,y,ox=x,oy=y)]+[ray(0,marker=i) for i in range(5)]
        yield fixture(phase=3,clock=10,mode=0,density=density,rays=rays)
    # Full/sparse allocation, boundary exits and retained byte/padding ownership.
    for mode,phase,clock,density in itertools.product((1,2,3,4),(2,4),(48,64,65,80,96),(0,1,2)):
        rays=[ray(1 if density==1 else i%2,x=0,y=0,ox=0,oy=0,marker=i*19) for i in range(6)]
        yield fixture(phase=phase,clock=clock,mode=mode,rays=rays)
    for phase,clock,sprite,frame in itertools.product((7,254,255),(0,7,11,12,63,416,488,32767,-32768),(4,11,255),range(4)):
        row=fixture(phase=phase,clock=clock,frame=frame);row[9+14]=sprite;yield row
    for phase,x,y,clock in itertools.product((5,6),(3055,3056,3088,3089),(1263,1264,1296,1297),(0,15,31,64,65)):
        yield fixture(phase=phase,x=x,y=y,clock=clock)
    for angle,phase,frame,toggle in itertools.product((0,1,127,128,129,255),(2,3,4),(56,57,114),(0,1,255)):
        yield fixture(phase=phase,clock=96,mode=1 if phase==3 else 0,angle=angle,frame=frame,toggle=toggle)
    # Retain every shared owner through actual phase2/4 attack selection,
    # ray growth/expiry, turn toggle, stack cycles, win/timeout and departure.
    for rank,damage in itertools.product(range(4),(0,19)):
        row=fixture(phase=0,steps=12000,rank=rank,damage=damage,hp=0,end=0,toggle=0);yield row

def initialize(o,row):
    base_initialize(o,row[:49]);o.write(0xbcf0,'hh',384,384);o.write(0x46b0,'BB',*row[49:51]);o.u.mem_write(0x8b204,bytes(row[51:]));o.write(0xbcb7,'BB',0,0)

def checkpoint(o):
    bg=o.read(0x426c,'H')[0]
    if bg not in (0,0x76fb,0x20c8):raise ValueError(f'unknown Kurumi background{bg:04X}')
    values=[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0xbcf0,'hh'),*o.read(0x4642,'hh'),*o.read(0x23ed,'B'),*o.read(0x2a82,'3B'),*o.read(0x5393,'B'),*o.read(0x4252,'B'),*o.read(0xba8a,'B'),*o.read(0x4662,'B'),(0,0x76fb,0x20c8).index(bg),*o.read(0x427e,'hh'),*o.read(0x5390,'H'),*o.read(0xbcca,'B'),*o.read(0x988,'B'),*o.read(0x435a,'I'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,16*42).hex(),o.u.mem_read(0x853e2,96*16).hex(),*o.read(0x41f4,'H'),o.u.mem_read(0x84298,48).hex(),o.u.mem_read(0x8b204,6*26).hex(),*o.read(0x46b0,'BB'),*o.read(0xbcb7,'BB'),len(o.events),*itertools.chain.from_iterable(o.events)]
    if o.read(0x1b5c,'B')!=(0,):raise ValueError('boss hit flag leaked')
    return ' '.join(map(str,values))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--limit',type=int);p.add_argument('--reference-dir',type=Path);p.add_argument('--short-only',action='store_true')
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest,_=source_manifest(Path(__file__).resolve().parents[1])
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    setup=SetupOriginal(o.target);setup_expected=[]
    for rank in range(4):
        setup.reset();setup.write(0x4348,'B',rank);setup.call_args(0xa623,far=True)
        if setup.error:raise RuntimeError('Stage2 setup hook rejected') from setup.error
        setup_expected.append(setup.u.mem_read(0x853ca,24).hex()+' '+' '.join(map(str,setup.read(0xbcf0,'hh')+setup.read(0xbcde,'B'))))
    setup_actual=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--setup'],capture_output=True,text=True,env=env,check=True).stdout.splitlines()
    if setup_actual!=setup_expected:raise ValueError('fresh Stage2 boss setup differs')
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            if address==0x33a90+0x56cd:raise ValueError('injected Kurumi rejection')
            super().body(u,address,size,unused)
    bad=Rejecting(o.target);initialize(bad,next(fixtures()))
    try:bad.call_args(0x56cd,far=True)
    except RuntimeError as error:
        if not isinstance(error.__cause__,ValueError):raise
    else:raise ValueError('Kurumi callback rejection swallowed')
    reference=None;counts={};records=0;sequences=[]
    if a.reference_dir:
        reference=json.loads((a.reference_dir/'receipt.json').read_text());fixture_path=a.reference_dir/'fixtures.txt';expected=a.reference_dir/'trace.txt.gz'
        if not reference['passed'] or reference['target_sha256']!=sha(o.target) or reference['fixture_sha256']!=sha(fixture_path.read_bytes()):raise ValueError('reference identity differs')
        counts=reference['counts'];sequences=reference['sequences']
    else:
        fixture_path=out/'fixtures.txt';expected=out/'trace.txt.gz';inputs=[]
        with gzip.open(expected,'wt',compresslevel=1) as trace:
            cases=(row for row in fixtures() if not a.short_only or row[0]=='U')
            for index,row in enumerate(itertools.islice(cases,a.limit) if a.limit else cases):
                initialize(o,row);inputs.append(' '.join(map(str,row)));counts[row[0]]=counts.get(row[0],0)+1;phases=set();modes=set();finished=False
                for step in range(row[1]):
                    frame=(row[4]+step)&65535;o.events.clear();o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
                    phases.add(o.read(0x53d9,'B')[0]);modes.add(o.read(0x53dd,'B')[0]);o.call_args(0x56cd,far=True);trace.write(checkpoint(o)+'\n')
                    if row[0]=='S' and any(e[0]==9 for e in o.events):finished=True;break
                if row[0]=='S':
                    if not finished:raise ValueError('retained Kurumi sequence did not reach departure')
                    sequences.append(dict(rank=row[2],damage=row[6],frames=step+1,phases=sorted(phases),modes=sorted(modes)));print(f'Kurumi rank{row[2]} damage{row[6]} frames{step+1} original PASS',flush=True)
        fixture_path.write_text('\n'.join(inputs)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)]
    digest=hashlib.sha256()
    with gzip.open(expected,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            if want is None or got is None or want.split()!=got.split():
                ww=want.split() if want else [];gg=got.split() if got else [];field=next((i for i,(x,y) in enumerate(zip(ww,gg)) if x!=y),min(len(ww),len(gg)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,field=field,expected=ww,actual=gg),indent=2)+'\n');process.terminate();raise ValueError(f'Kurumi checkpoint{index} field{field} differs')
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native Kurumi process failed')
    if reference and (digest.hexdigest()!=reference['trace_sha256'] or records!=reference['trace_records']):raise ValueError('retained original trace digest differs')
    after,_=source_manifest(Path(__file__).resolve().parents[1]);assert manifest==after
    r=dict(passed=True,callback_rejection_passed=True,fresh_setup_controls=setup_expected,counts=counts,cases=sum(counts.values()),trace_records=records,sequences=sequences,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=digest.hexdigest(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 DS8000 Kurumi13A9:4F84..5B53/update56CD and shared boss helpers, tune/add/sparks/gather/ring RNG. Complete24-byte boss,16 additional,6x26 custom ray records including retained padding,440x26 bullet/16x42 gather/96x16 spark pools,48 explosion bytes,templates/special controls/globals and ordered requests per selected update. Fresh Stage2 setup controls compare only24-byte boss,hitbox,rank period from fresh original DS; no preceding-stage metadata claim. Reference replay uses retained original trace,not new CPU update execution.',limits='Injected shot damage; circle/HUD/file/audio/item/point/dialog/bonus/delay consumers intercepted. Retained sequences advance only boss and retain pools; ordinary gameplay/render/GUI/pacing not executed. Ordinary four-rank setup only; zero stack period original DIV fault excluded and rejected natively. No DOS exact or complete original Stage2 claim.')
    (out/'receipt.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(passed=True,cases=r['cases'],trace_records=records,retained_sequences=len(sequences))))
if __name__=='__main__':main()
