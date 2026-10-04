#!/usr/bin/env python3
"""Original MAIN CPU controls for Stage5 Yuuka movement, seven attacks and core.

Actual boss/shared helpers, random ring, tune/add, sparks/gather and lasers run.
Injected shot damage and downstream circle/HUD/item/point/dialog/audio requests
are adapters. Boss-only retained sequences do not advance ordinary actors or
render. FAR VM callback identity is a symbolic null/retained dispatch token.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_AX
from verify_kurumi import Original as Base
from verify_orange import initialize as base_initialize,boss as boss_bytes
from verify_lasers import beam
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
ATTACKS=(0x2507,0x2615,0x2747,0x2813,0x287d,0x28f9,0x2aad)
class Original(Base):
    def __init__(self,target):
        self.reject=False;super().__init__(target)
    def body(self,u,address,size,unused):
        if self.reject and address==0x33a90+0x2b80:raise ValueError('injected Yuuka adapter rejection')
        super().body(u,address,size,unused)

def fixture(op='U',steps=1,phase=2,clock=0,mode=0,rank=1,perf=16,frame=0,power=64,damage=0,density=0,timed_out=1,patterns=0,hp=9000,end=7900,x=3072,y=1024,move=0,sweep=2560,step=1,acc=0,tone=100,vm=0,midboss=12345,palette=113,selector=0,player=(3072,5120),hit=0,lasers=None):
    state=boss_bytes(phase,clock,mode,hp,end,x,y,patterns);state[14]=144
    additional=[(i*17+9)&255 for i in range(16)];additional[0]=(144,160,168,180,160)[rank]
    ls=lasers or [beam(flag=1,clock=0,radius=1,speed=1,marker=201),beam(flag=0,marker=19),beam(flag=0,marker=71)]
    return [op,steps,rank,perf,frame,power,damage,density,timed_out,*state,*additional,sweep,step,acc,tone,move,vm,midboss,palette,*itertools.chain.from_iterable(ls),hit,*player,selector]

def fixtures():
    for phase,clock,damage in itertools.product((0,1),(0,1,7,15,30,31,32,63,64,127,128,129,32767,-32768),(0,256,257)):
        yield fixture(phase=phase,clock=clock,damage=damage,move=2)
    for clock,vm,midboss,palette in itertools.product((-1,0,1,128),(0,1),(-32768,0,32767),(-32768,0,100,32767)):
        yield fixture(phase=0,clock=clock,vm=vm,midboss=midboss,palette=palette)
    # Isolated transition state machine: pre-increment and nonzero centered
    # argument semantics; wrapped SUB precedes signed IDIV64.
    for move,clock,center,x,y in itertools.product((0,1,2,3,4,255),(-32768,-1,0,7,8,31,32,63,64,32767),(0,1,65535),(-32768,3072,32767),(-32768,1280,32767)):
        yield fixture(op='M',move=move,clock=clock,selector=center,x=x,y=y)
    clocks=(-32768,-1,0,1,3,5,7,15,16,17,31,32,39,40,41,42,44,47,48,49,50,52,55,56,60,63,64,68,72,76,79,80,82,84,95,96,111,127,128,129,139,140,159,160,161,169,170,191,192,255,256,287,288,499,500,999,1000,32767)
    for attack,rank,clock in itertools.product(range(7),range(5),clocks):
        yield fixture(op='P',selector=attack,rank=rank,perf=22 if rank==3 else 16,clock=clock,frame=clock&65535)
    for attack,density,clock,acc,step in itertools.product(range(7),(1,2),(1,15,17,48,64,96,128,160,192,256),(0,15,16,255),(1,255)):
        if (attack+clock+acc+step)%5:continue
        yield fixture(op='P',selector=attack,density=density,clock=clock,acc=acc,step=step,frame=1,rank=3,perf=255)
    for phase,mode,move,clock in itertools.product((2,5,8,11,14),(0,1,2,254,255),(0,1,2,3,255),(0,1,7,15,31,32,63,64,128,140,170,288)):
        if (phase+mode+move+clock)%3:continue
        yield fixture(phase=phase,mode=mode,move=move,clock=clock,rank=3,perf=22)
    for phase,clock,move in itertools.product((3,6,9,12,15),(0,6,7,30,31,62,63,32767,-32768),(0,1,2,3,255)):
        yield fixture(phase=phase,clock=clock,move=move)
    for phase,clock,damage,power in itertools.product((2,5,8,11,14,4,7,10,17),(0,17,31,64,287,498,499,500,998,999,1000),(0,1,255,256,257,65535),(0,123,124,127,128,255)):
        if (phase+clock+damage+power)%11:continue
        yield fixture(phase=phase,clock=clock,damage=damage,power=power,hp=7901,patterns=0)
    for phase,patterns,mode in itertools.product((2,5,8,11,14),(3,4,5,254,255),(2,254,255)):
        yield fixture(phase=phase,patterns=patterns,mode=mode)
    for phase,clock,frame,tone,density in itertools.product((13,16),(16,40,42,48,96,127,128,159,160,161,192,255,256,286,287,288),range(2),(0,99,100,101,254,255),range(3)):
        if (clock+tone+density)%3:continue
        yield fixture(phase=phase,clock=clock,frame=frame,tone=tone,density=density)
    for phase,clock,patterns,frame in itertools.product((17,18,19,254,255),(0,7,11,12,15,16,31,32,63,416,488,998,999,1000,32767,-32768),(0,1,255),range(4)):
        yield fixture(phase=phase,clock=clock,patterns=patterns,frame=frame,hp=1,end=0)
    # Laser tail runs even at entry/centered motion, and is absent in default
    # defeat dispatch. Preserve latch and all unused beam/scratch bytes.
    for phase,flag,clock,hit in itertools.product((0,3,13,16,17,18,254,255),(1,2,3,4,255),(0,31,32,143,144),(0,1,127)):
        ls=[beam(flag=1,clock=0,radius=1,speed=1),beam(flag=flag,clock=clock),beam(flag=2,clock=31,x=3200)]
        yield fixture(phase=phase,clock=64,lasers=ls,hit=hit)
    for attack,x,y in itertools.product(range(7),(-32768,-1,32767),(-32768,32767)):
        yield fixture(op='P',selector=attack,clock=1,x=x,y=y,player=(32767,-32768))
    # Both producers alias MAIN's player-hit BYTE. A new contact writes1 even
    # when the incoming latch is a retained noncanonical value (127).
    for hit,attack,clock in itertools.product((0,1,127),range(7),(7,15,32,64,128,192)):
        yield fixture(op='P',selector=attack,clock=clock,player=(2048,1024),hit=hit)
    for phase,mode in ((2,0),(2,1),(4,0),(11,0),(11,1),(13,0),(16,0),(17,0)):
        yield fixture(phase=phase,mode=mode,clock=15,player=(3072,1280))
    for rank,attack in itertools.product(range(5),range(7)):
        yield fixture(op='A',steps=(141,289,501,171,129,289,1001)[attack],rank=rank,selector=attack)
    for rank,damage in itertools.product(range(4),(0,19)):
        yield fixture(op='S',steps=12000,phase=0,clock=0,rank=rank,damage=damage,hp=0,end=0,x=3072,y=1280,sweep=0,step=0,acc=0,tone=0,move=0)

def initialize(o,row):
    if len(row)!=133:raise ValueError('Yuuka fixture size')
    base_initialize(o,row[:49]);o.write(0xbcf0,'hh',416,416)
    o.write(0x4322,'h4B',*row[49:54]);o.write(0x4646,'HH',*( (0x11c0,0x2aaf) if row[54] else (0x4567,0x1234)))
    o.write(0x53c0,'h',row[55]);o.write(0x3a4,'h',row[56]);o.u.mem_write(0x842d8,bytes(row[57:129]));o.write(0x4669,'B',row[129]);o.write(0x464e,'hh',*row[130:132]);o.write(0xbcb7,'BB',0,0)

def execute(o,row,step):
    frame=(row[4]+step)&65535;o.events.clear();o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
    if row[0]=='M':
        o.call_args(0x243e,args=(row[132],));returned=o.u.reg_read(UC_X86_REG_AX)&255
        if returned not in (0,1):raise ValueError('invalid original move return')
        return returned
    if row[0] in ('P','A'):o.call_args(ATTACKS[row[132]])
    else:o.call_args(0x2b80,far=True)
    return 0

def checkpoint(o,returned):
    bg=o.read(0x426c,'H')[0];background={0:0,0x7874:5,0x20c8:2}
    if bg not in background:raise ValueError(f'unknown Yuuka background{bg:04X}')
    vm=o.read(0x4646,'HH')
    if vm not in ((0x11c0,0x2aaf),(0x4567,0x1234)):raise ValueError('unknown VM token')
    values=[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0xbcf0,'hh'),*o.read(0x4642,'hh'),*o.read(0x23ed,'B'),*o.read(0x2a82,'3B'),*o.read(0x5393,'B'),*o.read(0x4252,'B'),*o.read(0xba8a,'B'),*o.read(0x4662,'B'),background[bg],*o.read(0x427e,'hh'),*o.read(0x5390,'H'),*o.read(0xbcca,'B'),*o.read(0x988,'B'),*o.read(0x435a,'I'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,16*42).hex(),o.u.mem_read(0x853e2,96*16).hex(),*o.read(0x41f4,'H'),o.u.mem_read(0x84298,48).hex(),o.u.mem_read(0x84322,6).hex(),*o.read(0x3a4,'h'),int(vm==(0x11c0,0x2aaf)),*o.read(0x53c0,'h'),o.u.mem_read(0x842d8,72).hex(),*o.read(0x4669,'B'),*o.read(0xbcb7,'BB'),returned,len(o.events),*itertools.chain.from_iterable(o.events)]
    if o.read(0x1b5c,'B')!=(0,):raise ValueError('boss hit flag leaked')
    return ' '.join(map(str,values))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--limit',type=int);p.add_argument('--reference-dir',type=Path);p.add_argument('--short-only',action='store_true')
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest,_=source_manifest(Path(__file__).resolve().parents[1]);env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    o.reject=True;initialize(o,fixture())
    try:o.call_args(0x2b80,far=True)
    except RuntimeError as error:
        if not isinstance(error.__cause__,ValueError):raise
    else:raise ValueError('callback rejection swallowed')
    o.reject=False;reference=None;counts={};records=0;sequences=[]
    if a.reference_dir:
        reference=json.loads((a.reference_dir/'receipt.json').read_text());fixture_path=a.reference_dir/'fixtures.txt';expected=a.reference_dir/'trace.txt.gz'
        if not reference['passed'] or reference['target_sha256']!=sha(o.target) or reference['fixture_sha256']!=sha(fixture_path.read_bytes()):raise ValueError('reference identity differs')
        counts=reference['counts'];sequences=reference['sequences']
    else:
        fixture_path=out/'fixtures.txt';expected=out/'trace.txt.gz';inputs=[]
        with gzip.open(expected,'wt',compresslevel=1) as trace:
            cases=(row for row in fixtures() if not a.short_only or row[0] not in ('S','A'))
            for index,row in enumerate(itertools.islice(cases,a.limit) if a.limit else cases):
                initialize(o,row);inputs.append(' '.join(map(str,row)));counts[row[0]]=counts.get(row[0],0)+1;phases=set();modes=set();finished=False
                for step in range(row[1]):
                    phases.add(o.read(0x53d9,'B')[0]);modes.add(o.read(0x53dd,'B')[0]);returned=execute(o,row,step);trace.write(checkpoint(o,returned)+'\n')
                    if row[0]=='S' and any(e[0]==9 for e in o.events):finished=True;break
                    if row[0]=='A':o.write(0x53da,'h',(o.read(0x53da,'h')[0]+1+32768)%65536-32768)
                if row[0]=='S':
                    if not finished:raise ValueError('retained Yuuka sequence did not reach departure')
                    sequences.append(dict(rank=row[2],damage=row[6],frames=step+1,phases=sorted(phases),modes=sorted(modes)));print(f'Yuuka rank{row[2]} damage{row[6]} frames{step+1} original PASS',flush=True)
        fixture_path.write_text('\n'.join(inputs)+'\n')
    command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)]
    digest=hashlib.sha256()
    with gzip.open(expected,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            if want is None or got is None or want.split()!=got.split():
                ww=want.split() if want else [];gg=got.split() if got else [];field=next((i for i,(x,y) in enumerate(zip(ww,gg)) if x!=y),min(len(ww),len(gg)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,field=field,expected=ww,actual=gg),indent=2)+'\n');process.terminate();raise ValueError(f'Yuuka checkpoint{index} field{field} differs')
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native Yuuka process failed')
    if reference and (digest.hexdigest()!=reference['trace_sha256'] or records!=reference['trace_records']):raise ValueError('retained original trace digest differs')
    after,_=source_manifest(Path(__file__).resolve().parents[1]);assert manifest==after
    r=dict(passed=True,original_cpu_reexecuted=not bool(reference),callback_rejection_passed=True,counts=counts,cases=sum(counts.values()),trace_records=records,sequences=sequences,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=digest.hexdigest(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 DS8000 Yuuka13A9:243E..2F89; seven actual helpers/core and shared boss/tune/add/gather/ring/laser callees including aliased spawn/laser contact latch. Complete boss/additional/private bytes, full440x26 bullets/16x42 gathers/96x16 sparks/48 explosions/72 lasers, templates/latches/WORD palette/VM dispatch token and ordered requests at every checkpoint.',limits='Injected shot damage and downstream circle/HUD/item/point/dialog/audio/delay consumers; ordinary actor updates/render/gameplay/pacing not run. VM token is null/retained classification, not host FAR pointer equality. No GUI Stage5 completion, wholegame or DOS exact claim. Reference mode replays retained independent CPU trace, not freshly executed updates.')
    (out/'receipt.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(passed=True,cases=r['cases'],trace_records=records,retained_sequences=len(sequences))))
if __name__=='__main__':main()
