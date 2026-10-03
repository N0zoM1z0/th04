#!/usr/bin/env python3
"""Compare the native Stage 1 Orange owner with pinned, relocated MAIN CPU code."""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX
from verify_effects import Original as Base
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def __init__(self,target):
        self.damage=0;super().__init__(target)
    def hook(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def event(kind,x=0,y=0,value=0,count=0):self.events.append([kind,x,y,value&65535,count&65535])
        def ret(cleanup,far=False):
            words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
            u.reg_write(UC_X86_REG_SP,sp+cleanup)
            if far:u.reg_write(UC_X86_REG_CS,words[1])
            u.reg_write(UC_X86_REG_IP,words[0])
        if (cs,ip)==(0x330e,0x7d2):
            event(0,value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]);ret(6,True);return
        if (cs,ip)==(0x2aaf,0x5ac9):
            if self.read(0x1b5c,'B')!=(1,):raise ValueError('boss shot flag missing')
            x,y,rx,ry=self.read(0x449e,'4h');event(1,x,y,rx,ry)
            u.reg_write(UC_X86_REG_AX,self.damage&65535);ret(4,True);return
        if (cs,ip)==(0x2aaf,0x1ba6):
            y,x=struct.unpack('<hh',u.mem_read(0x70000+sp+4,4));event(2,x,y);ret(8,True);return
        if (cs,ip)==(0x33a9,0x300):
            value,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+2,6));event(3,x,y,value);ret(8);return
        if (cs,ip)==(0x33a9,0x9fa8):
            value,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+2,6));event(4,x,y,value&255);ret(8);return
        if (cs,ip)==(0x33a9,0x6486):
            maximum,hp=struct.unpack('<HH',u.mem_read(0x70000+sp+2,4));event(5,value=hp,count=maximum);ret(6);return
        if (cs,ip)==(0x2aaf,0x2bfb):event(6);ret(4,True);return
        if (cs,ip)==(0x33a9,0x9c31):event(7);ret(2);return
        if (cs,ip)==(0x330e,0x2fc):
            value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]
            if value!=0x20a:raise ValueError('unexpected boss song fade argument')
            event(8,value=10);ret(6,True);return
        if (cs,ip)==(0x330e,0xd7):
            event(10,value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]);ret(6,True);return
        if (cs,ip)==(0x33a9,0xad25):event(11,value=60)
        if (cs,ip)==(0x33a9,0xae5d):event(9)
        super().hook(u,address,size,unused)

def boss(phase=2,frame=86,mode=1,hp=2500,end_hp=1950,x=3072,y=1280,bonus=11):
    return list(struct.pack('<7hBBh4Bh',x,y,3000,1200,17,-19,hp,132,phase,frame,211,mode,241,bonus,end_hp))
def fixture(state=None,steps=1,rank=1,perf=16,frame=0,power=64,damage=0,density=0,timed_out=1,last=255,count=2):
    additional=[(i*17+9)&255 for i in range(14)]+[last,count]
    return ['S' if steps>1 else 'U',steps,rank,perf,frame,power,damage,density,timed_out,*(state or boss()),*additional]
def fixtures():
    for frame,density,damage in itertools.product((0,191,319,327,335,343,351,32767,-32768),(0,1,2),(0,256)):
        yield fixture(boss(0,frame),density=density,damage=damage)
    for frame,rank,perf,density in itertools.product((0,30,31,32767),range(5),(0,16,255),(0,1)):
        yield fixture(boss(1,frame),rank=rank,perf=perf,density=density)
    for mode,phase_frame,rank,frame in itertools.product(range(1,5),(0,15,16,69,70,72,74,85,86,87,117,118,32767),range(5),(0,1,4)):
        yield fixture(boss(frame=phase_frame,mode=mode),rank=rank,frame=frame,perf=22 if rank==3 else 16)
    for count,last in itertools.product((0,14,15,16,255),(1,2,3,4,255)):
        yield fixture(boss(mode=0),last=last,count=count)
    for phase,damage,power in itertools.product((2,3),(0,1,255,256,257,32768,65535),(0,123,124,127,128,255)):
        yield fixture(boss(phase,hp=1951,end_hp=1950),damage=damage,power=power)
    for rank,hp,x,y,frame in itertools.product(range(5),(701,700),(496,3072,5648),(752,1280,1552),(0,1,4)):
        yield fixture(boss(3,1,1,hp=hp,end_hp=450,x=x,y=y),rank=rank,frame=frame)
    for phase_frame,mode,frame,rank,density in itertools.product((96,112,127,128,129,159,160,191,192,224,240,255,256,288,304,319,320,599,600,601,1500,1501),(0,1),(0,1),range(5),(0,1)):
        yield fixture(boss(4,phase_frame,mode,hp=450,end_hp=0),rank=rank,frame=frame,density=density)
    for phase,phase_frame,hp,end_hp,damage in itertools.product((3,4),(599,600,601,1500,1501),(0,1),(0,450),(0,1,256)):
        yield fixture(boss(phase,phase_frame,1,hp=hp,end_hp=end_hp),damage=damage)
    for phase_frame,bonus,x,y,density in itertools.product((0,15,31,32767),(0,1,255),(3055,3072,3089),(1263,1280,1297),(0,1)):
        yield fixture(boss(5,phase_frame,x=x,y=y,bonus=bonus),density=density)
    for phase,phase_frame,sprite,frame in itertools.product((254,255),(0,7,11,12,63,416,488,32767),(4,11,255),range(4)):
        state=boss(phase,phase_frame);state[14]=sprite;yield fixture(state,frame=frame)
    for x,y,mode in itertools.product((-32768,-32767,32767),(32767,-32768),(1,2,3,4)):
        yield fixture(boss(frame=16,mode=mode,x=x,y=y))
    for density,mode,phase_frame in itertools.product((1,2),(1,2,3,4),(70,72,74,86,118)):
        yield fixture(boss(frame=phase_frame,mode=mode),rank=3,perf=255,density=density)
    # The deterministic whole-boss RNG does not choose aimed-cloud mode2.
    # Seed all four complete128-frame attacks instead of claiming that route
    # happened to cover it, including repeated once-tuned cloud speed updates.
    for rank,mode in itertools.product(range(5),range(1,5)):
        row=fixture(boss(frame=0,mode=mode),steps=128,rank=rank);row[0]='P';yield row
    # Long controls execute the entire invulnerable entrance, every phase,
    # mode-selection retry loop, and win/timeout transition without reset.
    for rank,damage in itertools.product(range(5),(0,19)):
        state=boss(0,0,0,x=3072,y=640);state[14]=128
        yield fixture(state,steps=5600,rank=rank,damage=damage,count=0)

def initialize(original,row):
    _,steps,rank,perf,frame,power,damage,density,timed_out=row[:9]
    original.reset();original.damage=damage;original.context(rank,perf,0,3072,5120)
    original.u.mem_write(0x853ca,bytes(row[9:33]));original.u.mem_write(0x8bcde,bytes(row[33:]))
    for address,slots,width in ((0x85a22,440,26),(0x89292,16,42),(0x853e2,96,16)):
        original.u.mem_write(address,b''.join(bytes([int(bool(density) and (density==1 or i%2))])+bytes(width-1) for i in range(slots)))
    original.write(0x9586,'6h2B',2048,1024,17,-19,1024,8,13,129)
    original.write(0x53a2,'BB4h8B',1,52,2048,1024,17,-19,46,129,42,3,6,123,128,19)
    original.write(0xbcc4,'H',(0x9435,0x9440,0x9448,0x9453,0x9440)[rank])
    original.write(0xbcc0,'H',(0x945e,0x9486,0x94a2,0x94a2,0x9486)[rank])
    original.write(0xbcc2,'H',(0x94be,0x94da,0x94f6,0x94f6,0x94da)[rank])
    original.write(0x4664,'B',power);original.write(0x4662,'B',77);original.write(0x1f38,'B',0)
    original.write(0xbcf0,'hh',384,256);original.write(0x4642,'hh',111,222);original.write(0x23ed,'B',timed_out)
    original.write(0x2a82,'3B',17,29,41);original.write(0x5393,'B',0);original.write(0x4252,'B',13);original.write(0xba8a,'B',7)
    original.write(0x426c,'H',0);original.write(0x427e,'hh',17,-19);original.write(0x5390,'H',3)
    original.write(0xbcca,'B',0);original.write(0x988,'B',1);original.write(0x435a,'I',0)
    original.write(0xbcba,'BB',0,0);original.write(0xbcb9,'B',0);original.write(0x41f4,'H',0)
    original.u.mem_write(0x84298,bytes(48))
    for at,value in ((0x4298+14,-7),(0x42a8+14,19),(0x42b8+14,61)):original.write(at,'b',value)
    original.write(0x5394,'B',0);original.write(0xba86,'HH',0,0x9000);original.u.mem_write(0x90000,bytes(256))

def checkpoint(original):
    bg=original.read(0x426c,'H')[0]
    if bg not in (0,0x768e,0x20c8):raise ValueError(f'unrecognized background {bg:04x}')
    values=[original.u.mem_read(0x853ca,24).hex(),original.u.mem_read(0x8bcde,16).hex(),*original.read(0xbcf0,'hh'),*original.read(0x4642,'hh'),*original.read(0x23ed,'B'),*original.read(0x2a82,'3B'),*original.read(0x5393,'B'),*original.read(0x4252,'B'),*original.read(0xba8a,'B'),*original.read(0x4662,'B'),(0,0x768e,0x20c8).index(bg),*original.read(0x427e,'hh'),*original.read(0x5390,'H'),*original.read(0xbcca,'B'),*original.read(0x988,'B'),*original.read(0x435a,'I'),*original.read(0x3ecc,'H'),*original.read(0xbcba,'B'),*original.read(0xbcb9,'B'),original.u.mem_read(0x853a2,18).hex(),original.u.mem_read(0x85a22,440*26).hex(),original.u.mem_read(0x89586,14).hex(),original.u.mem_read(0x89292,16*42).hex(),original.u.mem_read(0x853e2,96*16).hex(),*original.read(0x41f4,'H'),original.u.mem_read(0x84298,48).hex(),len(original.events),*itertools.chain.from_iterable(original.events)]
    if original.read(0x1b5c,'B')!=(0,):raise ValueError('boss shot flag leaked')
    return ' '.join(map(str,values))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--limit',type=int);p.add_argument('--short-only',action='store_true');p.add_argument('--patterns-only',action='store_true');p.add_argument('--native-only',action='store_true');p.add_argument('--reference-dir',type=Path)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    original=Original(args.target.read_bytes());inputs=[];expected=out/'trace.txt.gz';counts={};frames=0;sequences=[];trace_hash=hashlib.sha256()
    fixture_path=out/'fixtures.txt'
    reference=None
    if args.native_only:
        if not args.reference_dir:raise ValueError('--native-only requires --reference-dir')
        expected=args.reference_dir.resolve()/'trace.txt.gz';fixture_path=args.reference_dir.resolve()/'fixtures.txt'
        reference=json.loads((args.reference_dir/'receipt.json').read_text())
        if not reference['passed'] or reference['target_sha256']!=sha(original.target) or reference['fixture_sha256']!=sha(fixture_path.read_bytes()):raise ValueError('retained original receipt identity differs')
        counts=reference['counts'];sequences=reference['sequences']
    elif args.reference_dir:raise ValueError('--reference-dir requires --native-only')
    if not args.native_only:
        with gzip.open(expected,'wt',compresslevel=1) as trace:
            for i,row in enumerate(fixtures()):
                if args.limit and i>=args.limit:break
                if args.short_only and row[0]!='U':continue
                if args.patterns_only and row[0]!='P':continue
                initialize(original,row);inputs.append(' '.join(map(str,row)));counts[row[0]]=counts.get(row[0],0)+1
                phases=set();modes=set();finished=False
                for step in range(row[1]):
                    frame=(row[4]+step)&65535;original.events.clear()
                    original.write(0x538a,'H',frame);original.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
                    phases.add(original.read(0x53d9,'B')[0]);modes.add(original.read(0x53dd,'B')[0])
                    original.call_args(0x6013,far=True);line=checkpoint(original)+'\n';trace.write(line);trace_hash.update(line.encode());frames+=1
                    if row[0]=='S' and any(e[0]==9 for e in original.events):finished=True;break
                if row[0]=='S':
                    if not finished:raise ValueError('continuous Boss sequence missed next-stage request')
                    sequences.append(dict(rank=row[2],damage=row[6],frames=step+1,phases=sorted(phases),modes=sorted(modes)))
                    print(f'Original Orange rank={row[2]} damage={row[6]} frames={step+1} PASS return',flush=True)
        fixture_path.write_text('\n'.join(inputs)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--vectors',str(fixture_path)]
    native_hash=hashlib.sha256();frames=0
    with (out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process,gzip.open(expected,'rt') as want:
        for i,(a,b) in enumerate(itertools.zip_longest(want,process.stdout)):
            if a is None or b is None or a.split()!=b.split():
                aa=a.split() if a else [];bb=b.split() if b else []
                field=next((j for j,(x,y) in enumerate(zip(aa,bb)) if x!=y),min(len(aa),len(bb)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=i,field=field,expected=aa,actual=bb),indent=2)+'\n')
                process.terminate()
                raise ValueError(f'Orange checkpoint{i} field{field} differs')
            native_hash.update((' '.join(b.split())+'\n').encode());frames+=1
        if process.wait()!=0:raise ValueError('native Orange process failed; see native-stderr.txt')
    if reference and (native_hash.hexdigest()!=reference['trace_sha256'] or frames!=reference['frames']):raise ValueError('retained original trace identity differs')
    if not reference and native_hash.hexdigest()!=trace_hash.hexdigest():raise ValueError('trace serialization changed')
    receipt=dict(passed=True,counts=counts,frames=frames,sequences=sequences,target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=native_hash.hexdigest(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),scope='MAIN load2000 DS8000 main03 13A9:6013/5B54..6012/AB48/ABBE/AC02/AC63/ACB3/6548/21EC/226C, actual tune/add, sparks and gathers. Complete24-byte boss,16 additional bytes,440x26 bullet pool,16x42 gather pool,96x16 sparks,templates,48 explosion bytes,globals,RNG and ordered requests compared every frame before hashing. Native-only compares retained original trace; does not reexecute CPU.',limits='Injected hittest damage; circle,Hud pixels,audio,item/point allocation,post-boss dialog/stage bonus/host delay intercepted. Long sequences advance Boss only until next-stage request; pools deliberately retain occupancy, no gameplay/renderer/pacing/exact/full route claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
