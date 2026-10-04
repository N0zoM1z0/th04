#!/usr/bin/env python3
"""Independent original MAIN controls for Yuuka6 gathering and twelve attacks.

MAIN13A9:6E77..7951, load2000 DS8000. Actual animation, vector/atan,
shared RNG/tune/spawn/gather, safety-circle/cross and laser allocation execute.
Circles/audio are ordered request adapters. Complete35 boss/animation bytes,
additional16, templates/full pools/hit latch/RNG and events are compared.
Retained sequences advance helpers and caller clock only, not ordinary actors,
battle dispatcher, pixels, physical PC98 pacing or DOS exactness.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_IP,UC_X86_REG_SP,UC_X86_REG_DS,UC_X86_REG_SS,UC_X86_REG_BP,UC_X86_REG_EFLAGS
from verify_yuuka6_entities import Original as Base,slot,circle
from verify_orange import boss
from verify_lasers import beam
from verify_effects import gather,shape
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
GATHERS=(0x6e77,0x6f25,0x6f3a,0x6fb5,0x7055)
ATTACKS=(0x70cd,0x7155,0x723c,0x72df,0x734b,0x73ff,0x7518,0x7609,0x7721,0x779b,0x77f2,0x7883)
class Original(Base):
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.reject and (cs,ip)==(0x33a9,ATTACKS[0]):raise ValueError('injected Yuuka6 attack hook rejection')
        if (cs,ip)==(0x2aaf,0x1ba6):
            off,seg,y,x=struct.unpack('<HHhh',u.mem_read(0x70000+sp,8));self.events.append([2,x,y,0,0]);u.reg_write(UC_X86_REG_SP,sp+8);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off);return
        super().body(u,address,size,unused)

def rank_dispatch(o):
    # The special producer uses BCC2, in addition to regular BCC0 and tune
    # BCC4. Execute the actual switch tail rather than guessing from rank.
    controls=[]
    for rank in range(5):
        o.reset();o.error=None;o.write(0x4348,'B',rank);o.write(0xbcc0,'3H',0xdead,0xbeef,0xcafe)
        for reg,value in ((UC_X86_REG_CS,0x2aaf),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):
            o.u.reg_write(reg,value)
        o.u.emu_start(0x2aaf0+0x312,0x2aaf0+0x3d2,count=1000)
        if o.error:raise RuntimeError('attack rank switch rejected') from o.error
        if o.u.reg_read(UC_X86_REG_IP)!=0x3d2 or o.u.reg_read(UC_X86_REG_CS)!=0x2aaf or o.u.reg_read(UC_X86_REG_SP)!=0xe000:raise ValueError('rank switch boundary differs')
        actual=o.read(0xbcc0,'3H')
        expected=((0x945e,0x94be,0x9435),(0x9486,0x94da,0x9440),(0x94a2,0x94f6,0x9448),(0x94a2,0x94f6,0x9453),(0x9486,0x94da,0x9440))[rank]
        if actual!=expected:raise ValueError('original attack callbacks differ')
        controls.append(dict(rank=rank,regular=actual[0],special=actual[1],tune=actual[2]))
    return controls

def fixture(op='A',steps=1,selector=0,rank=1,perf=16,frame=0,density=0,cursor=0,hit=127,clear=0,zap=0,clock=0,animation=0,flag=1,phase=2,angle=241,mode=19,origin=(3072,1280),mirror=(4096,1280),player=(3072,5120),range_byte=2,points=8,spawn=2,bullet_count=8,shape_radius=1024,shape_delta=129,pool=None,laser_flags=(0,0)):
    raw=bytearray(boss(phase=phase,frame=clock,x=origin[0],y=origin[1],mode=mode));raw[20]=angle
    raw+=struct.pack('<4Bh2hB',flag,0,123,231,animation,*mirror,127)
    additional=bytearray((i*17+9)&255 for i in range(16));additional[0]=160;additional[1]=points;additional[15]=range_byte
    template=struct.pack('<BB4h8B',spawn,52,2048,1024,17,-19,46,129,42,bullet_count,6,123,128,19)
    sh=bytearray(shape(shape_radius,8));sh[-1]=shape_delta
    gathers=b''.join(bytes(gather(flag=int(density==1 or (density==2 and i%2)),spawn=2)) for i in range(16))
    lasers=b''.join(bytes(q) for q in (beam(flag=1,clock=0,radius=1,speed=1,marker=201),beam(flag=laser_flags[0],marker=19),beam(flag=laser_flags[1],marker=71)))
    custom=b''.join(pool or [slot(flag=int(density==1 or (density==2 and i%2)),marker=i*13+19) for i in range(31)]+[circle(flag=0)])
    return [op,steps,selector,rank,perf,frame,density,cursor,hit,clear,zap,*player,raw.hex(),additional.hex(),template.hex(),sh.hex(),gathers.hex(),lasers.hex(),custom.hex()]

def fixtures():
    # Every meaningful gather clock plus no-op/wrap clocks; templates and
    # occupied slots retain their bytes and angle direction between calls.
    for selector,clock,density in itertools.product(range(5),(-32768,-1,0,15,16,17,18,19,20,31,32,33,34,35,36,47,48,49,50,51,52,63,64,65,32767),range(3)):
        yield fixture(op='G',selector=selector,clock=clock,density=density,origin=(-32768,32767),mirror=(32767,-32768))
    clocks=(-32768,-1,0,1,15,16,18,20,31,32,34,36,47,48,49,50,52,63,64,65,79,80,81,95,96,111,112,113,127,128,129,135,136,143,144,145,149,150,155,156,191,192,193,287,288,289,32767)
    for selector,rank,clock in itertools.product(range(12),range(5),clocks):
        yield fixture(selector=selector,rank=rank,perf=22 if rank==3 else 16,clock=clock,frame=clock&65535,points=(4,6,8,12,6)[rank])
    # All animation clocks around terminal cels and raw sprite flag modes.
    for selector,flag,animation,clock in itertools.product((0,1,2,3,5,6,7,11),(0,1,2,4,8,255),(-32768,-1,0,18,24,28,35,38,39,32767),(32,48,64,80,128,192,288)):
        if (selector+flag+animation+clock)%7==0:yield fixture(selector=selector,flag=flag,animation=animation,clock=clock,frame=clock&65535)
    for selector,density,clock,frame,perf,cursor in itertools.product(range(12),range(3),(48,64,80,112,128,144,192,288),(0,1,4,8,15,16,65535),(0,16,255),(0,255)):
        if (selector+clock+frame+perf+cursor)%17==0:yield fixture(selector=selector,density=density,clock=clock,frame=frame,rank=3,perf=perf,cursor=cursor,flag=4 if selector==1 else 1)
    for selector,clock,clear,zap in itertools.product(range(12),(48,64,80,112,144),(0,1,17,18,255),(0,1,255)):
        if (selector+clock+clear+zap)%5==0:yield fixture(selector=selector,clock=clock,frame=clock&65535,clear=clear,zap=zap,cursor=255,flag=4 if selector==1 else 1)
    # Raw BYTE arithmetic and signed clock quotients, including nonzero
    # RNG divisor edges. A zero range divisor has a separate rejecting probe.
    for range_byte in (1,2,127,128,255):
        for clock in (64,80,128):yield fixture(selector=6,clock=clock,frame=0,range_byte=range_byte)
    for angle,rank in itertools.product(range(256),range(5)):
        if angle%7==0:yield fixture(selector=7,clock=112,frame=1,angle=angle,rank=rank)
    for spawn,angle,delta,clock in itertools.product((1,2),(0,127,128,255),(0,1,128,255),(-32768,-1,0,4,16,28,32767)):
        yield fixture(selector=10,clock=clock,spawn=spawn,angle=angle,shape_delta=delta,frame=65535)
    for selector,clock,origin,player,hit in itertools.product(range(12),(48,64,112),((3072,5120),(3071,5119),(-17,-1),(6143,5887)),((3072,5120),(3071,5119)),(0,127)):
        if (selector+clock+hit)%7==0:yield fixture(selector=selector,clock=clock,frame=0,origin=origin,player=player,flag=4 if selector==1 else 1,hit=hit)
    for flags in itertools.product((0,1,2,255),repeat=2):
        yield fixture(selector=5,clock=64,frame=0,laser_flags=flags)
    # No original actor/render advancement: pools fill and stay occupied.
    # Attack helpers own their clock resets; caller increments once afterward.
    for selector,rank,density in itertools.product(range(12),(0,1,3),range(3)):
        yield fixture(op='L',steps=320,selector=selector,rank=rank,perf=22 if rank==3 else 16,density=density,flag=2 if selector==1 else 1,points=(4,6,8,12,6)[rank],phase=6 if selector==4 else 2,cursor=255)

def seed(o,row):
    if len(row)!=20:raise ValueError('Yuuka6 attack fixture extent')
    o.reset();o.context(row[3],row[4],0,row[11],row[12]);o.events=[];o.entity_draws=[]
    raw=bytes.fromhex(row[13]);o.u.mem_write(0x853ca,raw[:24]);o.u.mem_write(0x846c6,raw[24:34]);o.u.mem_write(0x846db,raw[34:])
    for at,value in ((0xbcde,row[14]),(0x53a2,row[15]),(0x9586,row[16]),(0x9292,row[17]),(0x42d8,row[18]),(0xb204,row[19])):o.u.mem_write(0x80000+at,bytes.fromhex(value))
    o.write(0x4669,'B',row[8]);o.write(0x3ecc,'H',row[7]);o.write(0x4252,'B',13);o.write(0xbcba,'B',row[9]);o.write(0xbcb9,'B',row[10]);o.write(0xbcb7,'2B',0,0);o.write(0x1b5c,'B',0)
    o.write(0xbcc2,'H',(0x94be,0x94da,0x94f6,0x94f6,0x94da)[row[3]])
    o.write(0xbcc0,'H',(0x945e,0x9486,0x94a2,0x94a2,0x9486)[row[3]]);o.write(0xbcc4,'H',(0x9435,0x9440,0x9448,0x9453,0x9440)[row[3]])
    o.u.mem_write(0x85a22,b''.join(bytes([int(row[6]==1 or (row[6]==2 and i%2))])+bytes(25) for i in range(440)))
    return bytes(o.u.mem_read(0x853e2,96*16)),o.read(0x41f4,'H')

def execute(o,row,step,untouched):
    frame=(row[5]+step)&65535;o.events=[];o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
    o.call_args((GATHERS if row[0]=='G' else ATTACKS)[row[2]])
    if o.read(0x1b5c,'B')!=(0,) or bytes(o.u.mem_read(0x853e2,96*16))!=untouched[0] or o.read(0x41f4,'H')!=untouched[1]:raise ValueError('attack touched unrelated shot/spark ownership')
    raw=bytes(o.u.mem_read(0x853ca,24))+bytes(o.u.mem_read(0x846c6,10))+bytes(o.u.mem_read(0x846db,1))
    values=[raw.hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0x4252,'B'),*o.read(0x4669,'B'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),*o.read(0xbcb7,'2B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,16*42).hex(),o.u.mem_read(0x842d8,72).hex(),o.u.mem_read(0x8b204,832).hex(),len(o.events),*itertools.chain.from_iterable(o.events)]
    if row[0]=='L':o.write(0x53da,'h',(o.read(0x53da,'h')[0]+1+32768)%65536-32768)
    return ' '.join(map(str,values))+'\n'

def rejection(o):
    o.reject=True
    try:o.call_args(ATTACKS[0])
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('attack callback rejection swallowed')
    finally:o.reject=False

def same(want,got):
    if want.split()!=got.split():raise ValueError('Yuuka6 attack original/native checkpoint differs')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes())
    dispatch=rank_dispatch(o);rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures());configured=('\n'.join(' '.join(map(str,row)) for row in rows)+'\n').encode();counts={}
    for row in rows:counts[row[0]]=counts.get(row[0],0)+1
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'original-reference.json').read_text());fixture_path=a.reference_dir/'fixtures.txt';expected=a.reference_dir/'trace.txt.gz'
        if a.limit or not ref['passed'] or ref['target_sha256']!=sha(o.target) or sha(configured)!=ref['fixture_sha256'] or sha(fixture_path.read_bytes())!=ref['fixture_sha256']:raise ValueError('Yuuka6 attack reference identity mismatch')
    else:
        fixture_path=out/'fixtures.txt';fixture_path.write_bytes(configured);expected=out/'trace.txt.gz';digest=hashlib.sha256();records=0
        with gzip.open(expected,'wt',compresslevel=3) as trace:
            for index,row in enumerate(rows):
                before=seed(o,row)
                for step in range(row[1]):line=execute(o,row,step,before);trace.write(line);digest.update(line.encode());records+=1
                if index and index%500==0:print(f'Original Yuuka6 attacks {index} fixtures PASS',flush=True)
        rejection(o)
        ref=dict(passed=True,target_sha256=sha(o.target),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),trace_records=records,cases=len(rows),counts=counts,callback_rejection_passed=True,scope='Independent original CPU expectations before native comparison; circle/audio consumers are explicit request adapters; other listed owners execute.')
        (out/'original-reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)];digest=hashlib.sha256();records=0
    with gzip.open(expected,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            try:same(want or '',got or '')
            except ValueError:
                ww=(want or '').split();gg=(got or '').split();field=next((i for i,(x,y) in enumerate(zip(ww,gg)) if x!=y),min(len(ww),len(gg)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,field=field,expected=want,actual=got),indent=2)+'\n');process.terminate();raise
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native Yuuka6 attack reference consumer failed')
    if digest.hexdigest()!=ref['trace_sha256'] or records!=ref['trace_records']:raise ValueError('Yuuka6 attack reference trace identity mismatch')
    rejection(o)
    try:same('abcd 1','abce 1')
    except ValueError:pass
    else:raise ValueError('one-variable attack byte mutation accepted')
    result=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve())],capture_output=True,text=True,env=env,check=True)
    if result.stdout.strip()!='Stage 6 Yuuka attack contracts PASS':raise ValueError('Yuuka6 attack contracts failed')
    if manifest!=source_manifest(root)[0]:raise ValueError('source changed during attack controls')
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),cases=len(rows),trace_records=records,counts=counts,fresh_rank_dispatch=dispatch,callback_rejection_passed=True,one_variable_rejection_passed=True,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,limits='Original helper/callee controls only. Circle/audio requests adapted; retained sequences advance helper/caller clocks without actor/pool updates. Existing atan INT16_MIN domain and original zero ring divisor remain separate; no whole battle, pixels, physical timing or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','cases','trace_records','counts')}))
if __name__=='__main__':main()
