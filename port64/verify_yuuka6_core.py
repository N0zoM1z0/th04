#!/usr/bin/env python3
"""Independent MAIN CPU controls for Yuuka6 mirror, phase transition and core.

Actual MAIN13A9:7952..7ECB and its attack/animation/movement, RNG, spawn,
gather, explosion, laser and custom-entity callees execute at load2000 DS8000.
Shot damage and sound/circle/HUD/point/item consumers are explicit adapters.
Retained sequences stop on entry to big defeat: no ordinary actors, drawing,
Ending I/O, physical PC98 timing, FPS or DOS byte-exactness claim.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX
from verify_yuuka6_attacks import Original as Base,fixture as attack_fixture,seed as attack_seed,rank_dispatch
from verify_yuuka6_entities import slot,circle
from verify_orange import Original as BossAdapters
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base,BossAdapters):
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.reject and (cs,ip)==(0x33a9,0x79ee):raise ValueError('injected Yuuka6 core adapter rejection')
        if (cs,ip)==(0x2aaf,0x5ac9):
            against=self.read(0x1b5c,'B')[0]
            if against not in (0,1):raise ValueError('invalid against-boss context')
            x,y,rx,ry=self.read(0x449e,'4h');self.events.append([1,x,y,rx&65535,ry&65535])
            u.reg_write(UC_X86_REG_AX,self.damage if against else self.ordinary_damage)
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off);return
        if (cs,ip) in {(0x33a9,0x300),(0x33a9,0x6486),(0x2aaf,0x2bfb),(0x33a9,0x9c31),(0x330e,0x2fc),(0x330e,0xd7),(0x33a9,0xad25),(0x33a9,0xae5d)}:
            BossAdapters.hook(self,u,address,size,unused);return
        super().body(u,address,size,unused)

def fixture(op='U',steps=1,power=64,damage=0,ordinary=0,previous=19,mirror_damage=231,vm=0,midboss=12345,score=19,timed=1,tone=113,hp=13300,end=10600,patterns=0,sprite=128,mirror_state=0,fly=0,**kwargs):
    row=attack_fixture(op=op,steps=steps,**kwargs);raw=bytearray.fromhex(row[13])
    struct.pack_into('<h',raw,12,hp);struct.pack_into('<h',raw,22,end);raw[14]=sprite;raw[21]=patterns;raw[25]=fly;raw[34]=mirror_state;row[13]=raw.hex()
    return row+[power,damage,ordinary,previous,mirror_damage,vm,midboss,score,timed,tone]

def fixtures():
    # Ordinary mirror callback returns a WORD, but the original AL store
    # truncates it before sound/HP. Inactive states retain prior damage/scratch.
    for state,hp,damage in itertools.product((0,1,2,3,127,255),(-32768,-1,0,1,255,32767),(0,1,255,256,257,32768,65535)):
        yield fixture(op='M',mirror_state=state,hp=hp,ordinary=damage,mirror=(-32768,32767))
    for phase,end,hp,clear,kind in itertools.product((0,17,254,255),(-32768,0,7600,32767),(-32768,0,32767),(0,19,20,255),range(5)):
        yield fixture(op='N',phase=phase,hp=hp,end=end,damage=5400,clear=clear,selector=kind,clock=32767)
    clocks=(-32768,-1,0,1,15,16,31,32,47,48,63,64,79,80,95,96,111,112,127,128,129,143,144,155,156,191,192,287,288,319,320,2498,2499,2500,32767)
    for phase,clock,mode,rank in itertools.product(range(18),clocks,(0,1,2,3,255),range(5)):
        if (phase+clock+mode+rank)%13==0:
            yield fixture(phase=phase,clock=clock,mode=mode,rank=rank,perf=22 if rank==3 else 16,frame=clock&65535,points=(4,6,8,12,6)[rank],mirror_state=2 if phase in (8,12) else 0,flag=4 if phase==2 and mode==1 else 1)
    for phase,clock,damage,ordinary,power in itertools.product((2,4,7,8,11,12,14,15,16),(0,64,128,2499),(0,1,255,256,257,65535),(0,1,256,257,65535),(0,123,124,127,128,255)):
        if (phase+clock+damage+ordinary+power)%41==0:
            yield fixture(phase=phase,clock=clock,damage=damage,ordinary=ordinary,power=power,hp=10601,end=10600,mirror_state=2,score=0xffffffff)
    for phase,clock,patterns,sprite in itertools.product((2,4,8,12,14),(63,64,112,127,128),(9,10,17,18,254,255),(0,128)):
        yield fixture(phase=phase,mode=255,clock=clock,patterns=patterns,sprite=sprite,previous=1,mirror_state=2)
    for phase,clock,flag,animation in itertools.product((3,5,7,9,11,13),(0,63,64,127,128),(0,1,2,4,8),(-1,0,18,24,35)):
        if (phase+clock+flag+animation)%7==0:yield fixture(phase=phase,clock=clock,flag=flag,animation=animation,origin=(3072,1280))
    # Custom owners execute in the core tail; both shared score wrap and raw
    # contact127->1 are checked. Last-slot circle aliases remain retained.
    for phase,damage,density,hit in itertools.product((0,6,8,10,14,17),(0,100,65535),range(3),(0,127)):
        pool=[slot(flag=1 if i<2 else 0,age=56,x=2048+i*256,y=1280,speed=0,hp=1,marker=i*13+19) for i in range(31)]+[circle(flag=2,clock=15,radius=120)]
        yield fixture(phase=phase,ordinary=damage,density=density,hit=hit,pool=pool,score=0xffffffff,frame=1,player=(2048,1280),clock=31)
    for phase,clock,damage,hit in itertools.product((254,255),(0,7,11,12,31,63),(0,257),(0,127)):
        yield fixture(phase=phase,clock=clock,damage=damage,hit=hit,sprite=4)
    # Retain every boss/pool/template owner through entrance, selection retry,
    # invisible waves, dual phases, attacks and win/timeout into phase254.
    for rank,damage in itertools.product(range(4),(0,19)):
        yield fixture(op='S',steps=20000,phase=0,clock=0,mode=0,flag=1,rank=rank,damage=damage,ordinary=damage,perf=22 if rank==3 else 16,points=(4,6,8,12)[rank],previous=0,mirror_state=0,origin=(3072,1280),patterns=0)

def seed(o,row):
    if len(row)!=30:raise ValueError('Yuuka6 core fixture extent')
    attack_seed(o,row[:20]);o.damage=row[21];o.ordinary_damage=row[22]
    for at,fmt,args in ((0x46c2,'B',(row[23],)),(0x46de,'B',(row[24],)),(0x4646,'2H',(0x11c0 if row[25] else 0,0x2aaf if row[25] else 0)),(0x53c0,'h',(row[26],)),(0x435a,'I',(row[27],)),(0x23ed,'B',(row[28],)),(0x3a4,'h',(row[29],)),(0x4664,'B',(row[20],)),(0x4662,'B',(77,)),(0xbcf0,'2h',(384,768)),(0x449e,'4h',(111,222,333,444)),(0x4642,'2h',(111,222)),(0x2a82,'3B',(17,29,41)),(0x5393,'B',(0,)),(0xba8a,'B',(7,)),(0x426c,'H',(0,)),(0x427e,'2h',(17,-19)),(0x5390,'H',(3,)),(0xbcca,'B',(0,)),(0x988,'B',(1,)),(0x42c8,'h',(0,)),(0x5394,'B',(0,)),(0xba86,'2H',(0,0x9000)),(0x4357,'B',(5,))):
        o.write(at,fmt,*args)
    o.u.mem_write(0x84298,bytes(48));o.u.mem_write(0x853e2,bytes(1536));o.u.mem_write(0x90000,bytes(256))
    for at,value in ((0x4298+14,-7),(0x42a8+14,19),(0x42b8+14,61)):o.write(at,'b',value)

def execute(o,row,step):
    frame=(row[5]+step)&65535;o.events=[];o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
    op=row[0]
    if op=='M':o.call_args(0x7952);returned=o.u.reg_read(UC_X86_REG_AX)&255
    elif op=='N':o.call_args(0x799f,args=(row[21],row[2]));returned=0
    else:o.call_args(0x79ee,far=True);returned=0
    raw=bytes(o.u.mem_read(0x853ca,24))+bytes(o.u.mem_read(0x846c6,10))+bytes(o.u.mem_read(0x846db,1))
    values=[raw.hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0x4252,'B'),*o.read(0x4669,'B'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),*o.read(0xbcb7,'2B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,11440).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,672).hex(),o.u.mem_read(0x842d8,72).hex(),o.u.mem_read(0x8b204,832).hex()]
    vm=o.read(0x4646,'2H');bg=o.read(0x426c,'H')[0]
    if vm not in ((0,0),(0x11c0,0x2aaf)) or bg not in (0,0x7dc9,0x20c8):raise ValueError('unknown core dispatch token')
    values += [*o.read(0x46de,'B'),*o.read(0x46c2,'B'),int(vm==(0x11c0,0x2aaf)),*o.read(0x53c0,'h'),*o.read(0x23ed,'B'),*o.read(0x5393,'B'),*o.read(0xba8a,'B'),*o.read(0x4662,'B'),{0:0,0x7dc9:5,0x20c8:2}[bg],*o.read(0x427e,'2h'),*o.read(0x5390,'H'),*o.read(0xbcca,'B'),*o.read(0x988,'B'),*o.read(0x42c8,'h'),*o.read(0x3a4,'h'),*o.read(0x435a,'I'),*o.read(0x4642,'2h'),*o.read(0x449e,'4h'),*o.read(0x2a82,'3B'),o.u.mem_read(0x84298,48).hex(),o.u.mem_read(0x853e2,1536).hex(),*o.read(0x41f4,'H'),returned,len(o.events),*itertools.chain.from_iterable(o.events)]
    if o.read(0x1b5c,'B')!=(0,):raise ValueError('core leaked against-boss shot flag')
    return ' '.join(map(str,values))+'\n'

def same(want,got):
    if want is None or got is None or want.split()!=got.split():
        raise ValueError('Yuuka6 core complete checkpoint differs')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);a=p.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];o=Original(a.target.read_bytes());dispatch=rank_dispatch(o)
    rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures());configured=('\n'.join(' '.join(map(str,row)) for row in rows)+'\n').encode()
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'original-reference.json').read_text());fixture_path=a.reference_dir/'fixtures.txt';trace=a.reference_dir/'trace.txt.gz'
        if a.limit or not ref['passed'] or ref['target_sha256']!=sha(o.target) or ref['fixture_sha256']!=sha(configured) or sha(fixture_path.read_bytes())!=ref['fixture_sha256']:raise ValueError('core reference identity differs')
    else:
        fixture_path=out/'fixtures.txt';fixture_path.write_bytes(configured);trace=out/'trace.txt.gz';digest=hashlib.sha256();records=0;sequences=[]
        with gzip.open(trace,'wt',compresslevel=3) as target:
            for index,row in enumerate(rows):
                seed(o,row);phases=set();modes=set();finished=False
                for step in range(row[1]):
                    phases.add(o.read(0x53d9,'B')[0]);modes.add(o.read(0x53dd,'B')[0]);line=execute(o,row,step);target.write(line);digest.update(line.encode());records+=1
                    if row[0]=='S' and o.read(0x53d9,'B')==(254,):finished=True;break
                if row[0]=='S':
                    if not finished:raise ValueError('core sequence did not reach big defeat')
                    sequences.append(dict(rank=row[3],damage=row[21],frames=step+1,phases=sorted(phases),modes=sorted(modes)));print(f'Original Yuuka6 sequence rank{row[3]} damage{row[21]} frames{step+1} PASS',flush=True)
                if index and index%500==0:print(f'Original Yuuka6 core {index} fixtures PASS',flush=True)
        ref=dict(passed=True,target_sha256=sha(o.target),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),trace_records=records,cases=len(rows),sequences=sequences,source_manifest_sha256=manifest,scope=__doc__)
        (out/'original-reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    # A throwing original adapter must escape the Unicorn callback. Also
    # reject a deliberately mutated checkpoint instead of trusting green runs.
    seed(o,fixture());o.reject=True
    try:o.call_args(0x79ee,far=True)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('core adapter rejection swallowed')
    o.reject=False;env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)];count=0;digest=hashlib.sha256()
    with gzip.open(trace,'rt') as expected,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as child:
        for count,(want,got) in enumerate(itertools.zip_longest(expected,child.stdout),1):
            try:same(want,got)
            except ValueError:
                ww=want.split() if want else [];gg=got.split() if got else [];field=next((i for i,(w,g) in enumerate(zip(ww,gg)) if w!=g),min(len(ww),len(gg)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=count,field=field,expected=ww,actual=gg),indent=2)+'\n');child.terminate();raise ValueError(f'Yuuka6 core checkpoint{count} field{field} differs')
            digest.update(got.encode())
        if child.wait()!=0:raise ValueError('core native process failed')
    if count!=ref['trace_records'] or digest.hexdigest()!=ref['trace_sha256']:raise ValueError('core complete reference digest differs')
    with gzip.open(trace,'rt') as expected:first=expected.readline()
    changed=first.split();changed[0]=('1' if changed[0][0]!='1' else '0')+changed[0][1:]
    try:same(first,' '.join(changed))
    except ValueError:pass
    else:raise ValueError('one-byte core checkpoint mutation accepted')
    assert source_manifest(root)[0]==manifest
    receipt=dict(passed=True,cases=len(rows),trace_records=count,sequences=ref['sequences'],source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),fresh_rank_dispatch=dispatch,callback_rejection_passed=True,comparator_rejection_passed=True,original_cpu_reexecuted=not bool(a.reference_dir),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),trace_records=count,sequences=len(ref['sequences']))))
if __name__=='__main__':main()
