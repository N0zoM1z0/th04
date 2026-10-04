#!/usr/bin/env python3
"""Independent original CPU controls for Elly's state, scythe and attacks.

Actual 13A9:7ECC..8C3D and shared aim/shot wrapper/tune/allocation/RNG/score/
explosion/gather/spark/defeat helpers execute. Damage and video/audio/item/point
consumers are bounded adapters, not whole-game or physical-hardware emulation.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX
from verify_kurumi import Original as Base
from verify_orange import initialize as base_initialize,boss as boss_bytes
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if getattr(self,'reject',False) and (cs,ip)==(0x33a9,0x8855):raise ValueError('injected Elly callback rejection')
        if (cs,ip)==(0x2aaf,0x5ac9) and self.read(0x1b5c,'B')==(0,):
            x,y,rx,ry=self.read(0x449e,'4h');self.events.append([1,x,y,rx,ry]);u.reg_write(UC_X86_REG_AX,self.damage&65535)
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off);return
        super().body(u,address,size,unused)
def scythe(mode=0,flag=0,frame=0,angle=96,speed=8,turn=-1,x=2048,y=1024):
    return list(struct.pack('<BB6hHBBb',mode,flag,x,y,1234,2345,17,-19,frame,angle,speed,turn))
def fixture(phase=3,clock=0,mode=0,steps=1,rank=1,perf=16,frame=9240,power=64,damage=0,density=0,timed_out=1,patterns=0,hp=6000,end=0,x=3072,y=1536,angle=96,orbit=0,group=0,q=None,player=(3072,5120),op=None):
    boss=boss_bytes(phase,clock,mode,hp,end,x,y,patterns);boss[14]=134;boss[20]=angle
    additional=[(i*17+9)&255 for i in range(16)]
    return [op or ('S' if steps>1 else 'U'),steps,rank,perf,frame,power,damage,density,timed_out,*boss,*additional,*(q or scythe()),orbit,group,0,*player]
def fixtures():
    # Direct scythe controls separate unsigned frame/speed arithmetic from
    # signed boss/orbit clocks, boundary precedence, turn/return and raw shots.
    for i,(mode,flag,clock,speed) in enumerate(itertools.product(range(10),(0,1,2),(0,1,55,56,63,64,79,80,31,32,65535),(0,1,4,8,9,128,255))):
        yield fixture(op='Q',q=scythe(mode,flag,clock,angle=i%256,speed=speed,turn=(-1,0,1)[i%3]),frame=i&15,damage=(0,1,257,65535)[i%4])
    for x,y,mode,turn in itertools.product((1023,1024,1025,5119,5120,5121),(511,512,513,4863,4864,4865),(2,3,4,5,6,7),(-1,0,1)):
        yield fixture(op='Q',q=scythe(mode,1,64,x=x,y=y,turn=turn),player=(x,y))
    for clock,radius,angle in itertools.product((-32768,-1,0,127,128,255,256,383,384,511,512,639,640,767,768,32767),(-32768,-1,0,8,1024,32767),(0,127,255)):
        row=fixture(op='O',orbit=clock,angle=angle);row[9+4:9+6]=list(struct.pack('<h',radius));yield row
    for phase,clock,mode,frame,damage in itertools.product((0,1,2),(0,15,16,30,31,32,33,63,64,65,32767,-32768),(0,255),(9202,9239,9240,65535),(0,257)):
        yield fixture(phase=phase,clock=clock,mode=mode,frame=frame,damage=damage,q=scythe(0))
    for mode,clock,rank,density in itertools.product(range(9),(0,1,7,8,15,16,17,31,32,33,63,64,71,72,73,79,80,81,143,144,32767,-32768),range(4),(0,1,2)):
        yield fixture(mode=mode,clock=clock,rank=rank,perf=22 if rank==3 else 16,density=density,q=scythe(1,0,16),frame=clock&15)
    for group,patterns,clock,hp,damage in itertools.product(range(6),(0,7,8,15,16,23,24,31,32,39,40,255),(0,31,32),(6000,4700,3300,2100,700,200,1),(0,19)):
        yield fixture(mode=255,clock=clock,group=group,patterns=patterns,hp=hp,damage=damage)
    for phase,clock,patterns in itertools.product((4,254,255),(0,7,15,16,31,32,63,416,488,32767,-32768),(0,1,255)):
        yield fixture(phase=phase,clock=clock,patterns=patterns,q=scythe(7,1,80))
    # Start at the actual post-dialog frame; all shared owners retain state.
    # Boss-only sequences omit ordinary pool updates and rendering consumers.
    for rank,damage in itertools.product(range(4),(0,19)):
        row=fixture(phase=0,clock=0,mode=0,steps=18000,rank=rank,damage=damage,frame=9203,hp=0,end=0,q=scythe(0,0,0),x=3072,y=1024)
        row[9+4:9+8]=list(struct.pack('<hh',3072,1024));row[9+8:9+12]=[0]*4;yield row

def initialize(o,row):
    base_initialize(o,row[:49]);o.write(0xbcf0,'hh',384,384);o.u.mem_write(0x846e6,bytes(row[49:68]));o.write(0x46fa,'h',row[68]);o.write(0x46e4,'B',row[69]);o.write(0x4669,'B',row[70]);o.write(0x464e,'hh',*row[71:73]);o.write(0x1b5c,'B',0)
def checkpoint(o):
    bg=o.read(0x426c,'H')[0];backgrounds=(0,0x76fb,0x20c8,0x777f)
    if bg not in backgrounds:raise ValueError('unknown Elly background callback')
    values=[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0xbcf0,'hh'),*o.read(0x4642,'hh'),*o.read(0x23ed,'B'),*o.read(0x2a82,'3B'),*o.read(0x5393,'B'),*o.read(0x4252,'B'),*o.read(0xba8a,'B'),*o.read(0x4662,'B'),backgrounds.index(bg),*o.read(0x427e,'hh'),*o.read(0x5390,'H'),*o.read(0xbcca,'B'),*o.read(0x988,'B'),*o.read(0x435a,'I'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,16*42).hex(),o.u.mem_read(0x853e2,96*16).hex(),*o.read(0x41f4,'H'),o.u.mem_read(0x84298,48).hex(),o.u.mem_read(0x846e6,19).hex(),*o.read(0x46fa,'h'),*o.read(0x46e4,'B'),*o.read(0x4669,'B'),len(o.events),*itertools.chain.from_iterable(o.events)]
    if o.read(0x1b5c,'B')!=(0,):raise ValueError('against-boss flag leaked')
    return ' '.join(map(str,values))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--limit',type=int);p.add_argument('--reference-dir',type=Path);a=p.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest=source_manifest(Path(__file__).resolve().parents[1])[0];counts={};sequences=[]
    if a.reference_dir:
        ref_receipt=a.reference_dir/('original-reference.json' if (a.reference_dir/'original-reference.json').exists() else 'receipt.json')
        reference=json.loads(ref_receipt.read_text());fixture_path=a.reference_dir/'fixtures.txt';expected=a.reference_dir/'trace.txt.gz'
        if not reference['passed'] or reference['target_sha256']!=sha(o.target) or reference['fixture_sha256']!=sha(fixture_path.read_bytes()):raise ValueError('reference identity differs')
        counts=reference['counts'];sequences=reference['sequences']
    else:
        reference=None;fixture_path=out/'fixtures.txt';expected=out/'trace.txt.gz';inputs=[]
        with gzip.open(expected,'wt',compresslevel=1) as trace:
            for index,row in enumerate(itertools.islice(fixtures(),a.limit) if a.limit else fixtures()):
                initialize(o,row);inputs.append(' '.join(map(str,row)));counts[row[0]]=counts.get(row[0],0)+1;phases=set();modes=set();finished=False
                for step in range(row[1]):
                    frame=(row[4]+step)&65535;o.events.clear();o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
                    phases.add(o.read(0x53d9,'B')[0]);modes.add(o.read(0x53dd,'B')[0])
                    entry={'Q':0x7ecc,'I':0x81ac,'O':0x81e3}.get(row[0],0x8855)
                    o.call_args(entry,far=row[0] in ('U','S'));trace.write(checkpoint(o)+'\n')
                    if row[0]=='S' and any(e[0]==9 for e in o.events):finished=True;break
                if row[0]=='S':
                    if not finished:raise ValueError('retained Elly sequence did not reach departure')
                    sequences.append(dict(rank=row[2],damage=row[6],frames=step+1,phases=sorted(phases),modes=sorted(modes)));print(f'Elly rank{row[2]} damage{row[6]} frames{step+1} original PASS',flush=True)
        fixture_path.write_text('\n'.join(inputs)+'\n')
        # Record target-only expectations before comparing candidate output.
        # Native mismatch cannot invalidate successful original CPU execution;
        # its separate candidate receipt must still report failure.
        original_digest=hashlib.sha256();original_records=0
        with gzip.open(expected,'rt') as trace:
            for line in trace:original_digest.update(line.encode());original_records+=1
        o.reject=True
        try:o.call_args(0x8855,far=True)
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
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,field=field,expected=ww,actual=gg),indent=2)+'\n');process.terminate();raise ValueError(f'Elly checkpoint{index} field{field} differs')
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native Elly process failed')
    if reference and (digest.hexdigest()!=reference['trace_sha256'] or records!=reference['trace_records']):raise ValueError('reference trace digest differs')
    o.reject=True
    try:o.call_args(0x8855,far=True)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('original callback rejection silently passed')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during controls')
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),callback_rejection_passed=True,counts=counts,cases=sum(counts.values()),trace_records=records,sequences=sequences,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=digest.hexdigest(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,limits='Selected original state/event controls and boss-only retained sequences. Full stage updates/render/pacing and physical hardware excluded; original shot/audio/video/item/point consumers adapted. Native player death/Bomb/audio still unported; no DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=receipt['cases'],trace_records=records)))
if __name__=='__main__':main()
