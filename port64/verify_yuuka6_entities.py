#!/usr/bin/env python3
"""Original MAIN controls for Yuuka6 cross/circle allocation, update and drawing.

MAIN13A9:65F7..6932 and MAIN0AAF:7054..7129, load2000 DS8000.
Actual vector/atan/polar, spark allocation, RNG, tune and bullet spawn execute.
Ordinary-shot WORD damage, item/audio and graphics consumers are explicit
request adapters. Compare832 custom bytes, complete440-bullet/96-spark pools,
templates, shared globals, RNG and ordered events/draws. Sequences advance
these owners only; no whole battle, physical video, frame pacing or exact claim.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX,UC_X86_INS_OUT,UC_X86_REG_DS,UC_X86_REG_SS,UC_X86_REG_BP,UC_X86_REG_EFLAGS
from verify_effects import Original as Base
from verify_orange import boss
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def __init__(self,target):
        self.error=None;self.reject=False;self.entity_draws=[];self.damage=0;super().__init__(target)
        self.u.hook_add(unicorn.UC_HOOK_INSN,self.out,None,1,0,UC_X86_INS_OUT)
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as e:self.error=e;u.emu_stop()
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.reject and (cs,ip)==(0x33a9,0x6680):raise ValueError('injected entity hook rejection')
        def ret(args,far=False):
            words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
            u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args)
            if far:u.reg_write(UC_X86_REG_CS,words[1])
            u.reg_write(UC_X86_REG_IP,words[0])
        if (cs,ip)==(0x330e,0x7d2):
            value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];self.events.append([0,0,0,value,0]);ret(2,True);return
        if (cs,ip)==(0x2aaf,0x5ac9):
            if self.read(0x1b5c,'B')!=(0,):raise ValueError('entity inherited against-boss shot flag')
            x,y,rx,ry=self.read(0x449e,'4h');self.events.append([1,x,y,rx&65535,ry&65535]);u.reg_write(UC_X86_REG_AX,self.damage);ret(0,True);return
        if (cs,ip)==(0x33a9,0x9fa8):
            item,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+2,6));self.events.append([4,x,y,item&255,0]);ret(6);return
        if cs==0x2000 and ip in (0x2f54,0x2838):
            if ip==0x2838:
                planes,mask,pattern,y,x=struct.unpack('<HHHhh',u.mem_read(0x70000+sp+4,10))
                if planes!=0xffc0 or mask!=0:raise ValueError('entity white plane contract differs')
            else:pattern,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6))
            self.entity_draws.append([int(ip==0x2838),x,y,pattern]);ret(10 if ip==0x2838 else 6,True);return
        if (cs,ip)==(0x2aaf,0x1666):self.entity_draws.append([2,0,0,0xc0]);ret(0);return
        if (cs,ip)==(0x2aaf,0x1672):self.entity_draws.append([3,0,0,(u.reg_read(UC_X86_REG_AX)>>8)&255]);ret(0);return
        if cs==0x2000 and ip in (0x114c,0x11ec):
            radius,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));self.entity_draws.append([4 if ip==0x114c else 5,x,y,radius]);ret(6,True);return
        super().hook(u,address,size,unused)
    def out(self,u,port,size,value,unused):
        if (port,size,value)!=(0x7c,1,0):self.error=ValueError('unexpected entity graphics OUT');u.emu_stop();return
        self.entity_draws.append([6,0,0,0])
    def call_args(self,*args,**kwargs):
        self.error=None
        try:super().call_args(*args,**kwargs)
        except Exception:
            if self.error:raise RuntimeError('original entity adapter rejected') from self.error
            raise
        if self.error:raise RuntimeError('original entity adapter rejected') from self.error

def slot(flag=0,angle=64,x=2048,y=1024,age=0,hp=100,damage=17,speed=16,marker=19,radius=77,distance=-123):
    return struct.pack('<BBhh4BhhH4hBB',flag,angle,x,y,*[(marker+37*i)&255 for i in range(4)],17,-19,age,radius,distance,hp,damage,speed,(marker+71)&255)
def circle(flag=0,clock=0,radius=8,distance=80,color=8,x=224,y=336):
    return slot(flag,x=x,y=y,age=clock,radius=radius,distance=distance,speed=color,marker=201)
def fixture(op='U',steps=1,rank=1,perf=16,frame=0,damage=0,density=0,hit=127,score=19,ring=0,cursor=0,angle=64,speed=16,boss_origin=(3072,1280),player=(3072,5120),clear=0,zap=0,pool=None,cross=None,sc=None):
    records=list(pool) if pool is not None else [slot(marker=i*13+19) for i in range(31)]+[circle()]
    if cross is not None:records[0]=cross
    if sc is not None:records[31]=sc
    scratch=struct.pack('<BB4h8B',2,52,2048,1024,17,-19,46,129,42,3,6,123,128,19)
    return [op,steps,rank,perf,frame,damage,density,hit,score,ring,cursor,angle,speed,*boss_origin,*player,clear,zap,b''.join(records).hex(),scratch.hex()]

def fixtures():
    for free,angle,speed in itertools.product(range(33),(0,64,128,255),(0,1,16,127,128,255)):
        pool=[slot(flag=0 if i==free else 2,marker=i*13+19) for i in range(32)]
        yield fixture(op='A',pool=pool,angle=angle,speed=speed,boss_origin=(-32768,32767))
    yield fixture(op='A',steps=33)
    for x,y,flag in itertools.product((-32768,-17,-16,-1,0,1,32767),(-32768,-1,0,32767),(0,1,2,255)):
        yield fixture(op='G',player=(x,y),sc=circle(flag=flag,clock=65535,radius=-32768,color=255))
    for index,(angle,speed,age) in enumerate(itertools.product(range(256),(0,1,16,128,255),(0,1,55,56,65535))):
        if index%11==0:yield fixture(cross=slot(flag=1,angle=angle,speed=speed,age=age))
    # Signed wrap/offscreen edges skip atan's existing INT16_MIN domain.
    edges=(-32768,-257,-256,-255,-1,0,6143,6144,6399,6400,32767)
    for index,(x,y,hp,damage) in enumerate(itertools.product(edges,edges,(-32768,0,1,99,100,32767),(0,1,100,32768,65535))):
        if index%19==0:yield fixture(cross=slot(flag=1,x=x,y=y,speed=0,age=56,hp=hp),damage=damage,score=0xffffffff,cursor=255,ring=1520)
    for dx,dy,hit in itertools.product((-193,-192,-191,191,192,193),(-193,-192,-191,191,192,193),(0,127)):
        yield fixture(cross=slot(flag=1,speed=0,age=56),player=(2048+dx,1024+dy),hit=hit)
    for damage,density,cursor,ring in itertools.product((0,1,100,65535),(0,1,2),(0,205,255),(0,1504,1520)):
        yield fixture(cross=slot(flag=1,age=56,hp=1),damage=damage,density=density,cursor=cursor,ring=ring)
    # Simultaneous31 alive entries, score wrapping and a saturated spark pool.
    for density,damage in itertools.product((0,1,2),(0,100)):
        yield fixture(pool=[slot(flag=1,age=56,x=1024+i*80,y=1024,marker=i*13) for i in range(31)]+[circle()],density=density,damage=damage,score=0xffffffff,ring=1520,cursor=255)
    for clock in range(256):yield fixture(sc=circle(flag=2,clock=clock,radius=120),frame=clock)
    clocks=(0,7,8,9,15,16,17,31,32,33,103,104,105,159,160,175,176,65535)
    for clock,rank,density,frame in itertools.product(clocks,range(5),(0,1,2),(0,65535)):
        yield fixture(sc=circle(flag=2,clock=clock,radius=120),frame=frame,rank=rank,perf=255 if rank==3 else 16,density=density,cursor=255)
    for flag,radius,clock in itertools.product((0,1,2,3,255),(-32768,-1,0,8,128,129,32767),(0,8,16,32,104,160,175,176,65535)):
        yield fixture(sc=circle(flag=flag,clock=clock,radius=radius,distance=32767),frame=65535)
    for clear,zap,clock in itertools.product((0,1,17,18,255),(0,1,255),(16,32,48,64)):
        yield fixture(sc=circle(flag=2,clock=clock,radius=120),clear=clear,zap=zap)
    # All raw flag BYTEs, retained age/damage and negative/offscreen positions.
    for flag,age,damage in itertools.product(range(256),(0,1,7,65535),(0,257)):
        yield fixture(op='R',cross=slot(flag=flag,age=age,damage=damage))
    for index,(flag,x,y,damage) in enumerate(itertools.product((0,1,16,47,48,255),edges,edges,(0,1,257))):
        if index%7==0:yield fixture(op='R',cross=slot(flag=flag,x=x,y=y,damage=damage,age=65535))
    for flag,radius,distance,color,point in itertools.product((0,1,2,3,255),(-32768,0,8,128,32767),(-32768,80,32767),(0,15,255),((-32768,32767),(224,336),(32767,-32768))):
        yield fixture(op='R',sc=circle(flag=flag,radius=radius,distance=distance,color=color,x=point[0],y=point[1]))
    for rank,damage,density in itertools.product((1,3),(0,2),(0,1,2)):
        yield fixture(op='L',steps=224,cross=slot(flag=1,speed=16),damage=damage,rank=rank,perf=22 if rank==3 else 16,density=density,cursor=255,ring=1520)
    for flag in (2,15,16,47,48,255):yield fixture(op='R',steps=40,cross=slot(flag=flag))

def seed(o,row):
    if len(row)!=21:raise ValueError('entity fixture extent')
    o.reset();o.damage=row[5];o.context(row[2],row[3],0,row[15],row[16]);o.events=[];o.entity_draws=[]
    o.u.mem_write(0x8b204,bytes.fromhex(row[19]));o.u.mem_write(0x853a2,bytes.fromhex(row[20]));assert len(bytes.fromhex(row[19]))==832
    before=bytes(boss(x=row[13],y=row[14]));o.u.mem_write(0x853ca,before);o.write(0x449e,'4h',111,222,333,444)
    o.write(0x4669,'B',row[7]);o.write(0x435a,'I',row[8]);o.write(0x41f4,'H',row[9]);o.write(0x3ecc,'H',row[10])
    o.write(0xbcba,'B',row[17]);o.write(0xbcb9,'B',row[18]);o.write(0xbcb7,'BB',0,0);o.write(0x1b5c,'B',0)
    o.write(0xbcc4,'H',(0x9435,0x9440,0x9448,0x9453,0x9440)[row[2]]);o.write(0xbcc0,'H',(0x945e,0x9486,0x94a2,0x94a2,0x9486)[row[2]])
    density=row[6];o.u.mem_write(0x85a22,b''.join(bytes([int(density==1 or (density==2 and i%2))])+bytes(25) for i in range(440)))
    o.u.mem_write(0x853e2,b''.join(struct.pack('<BB6hH',int(density==1 or (density==2 and i%2)),37,900,1200,777,888,17,-19,(i*257+0xab13)&65535) for i in range(96)))
    return before

def execute(o,row,step,before):
    frame=(row[4]+step)&65535;o.events=[];o.entity_draws=[];o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
    op=row[0]
    if op=='A':o.call_args(0x65f7,args=(row[12],row[11]))
    elif op=='G':o.call_args(0x6641)
    elif op=='R':o.call_args(0x7054,cs=0x2aaf)
    else:
        if op=='L' and step==0:o.call_args(0x6641)
        o.call_args(0x6680)
        if op=='L':o.call_args(0x7054,cs=0x2aaf)
    if o.u.mem_read(0x853ca,24)!=before or o.read(0x1b5c,'B')!=(0,):raise ValueError('entities wrote unrelated BOSS/against-boss flag')
    values=[o.u.mem_read(0x8b204,832).hex(),*o.read(0x449e,'4h'),*o.read(0x4669,'B'),*o.read(0x435a,'I'),*o.read(0x3ecc,'H'),*o.read(0x41f4,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),*o.read(0xbcb7,'2B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x853e2,96*16).hex(),len(o.events),*itertools.chain.from_iterable(o.events),len(o.entity_draws),*itertools.chain.from_iterable(o.entity_draws)]
    return ' '.join(map(str,values))+'\n'

def rank_dispatch(o):
    # Execute only the actual five-way gameplay_session_init switch tail,
    # MAIN0AAF:0312..03D1, stopping before its epilogue. Earlier file/score/
    # resident initialization is deliberately outside this bounded control.
    controls=[]
    for rank in range(5):
        o.reset();o.error=None;o.write(0x4348,'B',rank)
        o.write(0xbcc0,'H',0xdead);o.write(0xbcc4,'H',0xbeef)
        for reg,value in ((UC_X86_REG_CS,0x2aaf),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):
            o.u.reg_write(reg,value)
        o.u.emu_start(0x2aaf0+0x312,0x2aaf0+0x3d2,count=1000)
        if o.error:raise RuntimeError('original rank-dispatch rejected') from o.error
        if o.u.reg_read(UC_X86_REG_CS)!=0x2aaf or o.u.reg_read(UC_X86_REG_IP)!=0x3d2 or o.u.reg_read(UC_X86_REG_SP)!=0xe000:raise ValueError('original rank-switch boundary differs')
        actual=(*o.read(0xbcc0,'H'),*o.read(0xbcc4,'H'))
        expected=((0x945e,0x9435),(0x9486,0x9440),(0x94a2,0x9448),(0x94a2,0x9453),(0x9486,0x9440))[rank]
        if actual!=expected:raise ValueError('entity rank context differs from original switch')
        controls.append(dict(rank=rank,add=actual[0],tune=actual[1]))
    return controls

def rejection(o):
    o.reject=True
    try:o.call_args(0x6680)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('entity callback rejection swallowed')
    finally:o.reject=False

def same(want,got):
    if want.split()!=got.split():raise ValueError('entity original/native checkpoint differs')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes())
    dispatch=rank_dispatch(o);rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures());configured=('\n'.join(' '.join(map(str,row)) for row in rows)+'\n').encode();counts={}
    for row in rows:counts[row[0]]=counts.get(row[0],0)+1
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'original-reference.json').read_text());fixture_path=a.reference_dir/'fixtures.txt';expected=a.reference_dir/'trace.txt.gz'
        if a.limit or not ref['passed'] or ref['target_sha256']!=sha(o.target) or sha(configured)!=ref['fixture_sha256'] or sha(fixture_path.read_bytes())!=ref['fixture_sha256']:raise ValueError('entity reference identity mismatch')
    else:
        fixture_path=out/'fixtures.txt';fixture_path.write_bytes(configured);expected=out/'trace.txt.gz';digest=hashlib.sha256();records=0
        with gzip.open(expected,'wt',compresslevel=3) as trace:
            for index,row in enumerate(rows):
                before=seed(o,row)
                for step in range(row[1]):line=execute(o,row,step,before);trace.write(line);digest.update(line.encode());records+=1
                if index and index%500==0:print(f'Original Yuuka6 entities {index} fixtures PASS',flush=True)
        rejection(o)
        ref=dict(passed=True,target_sha256=sha(o.target),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),trace_records=records,cases=len(rows),counts=counts,callback_rejection_passed=True,scope='Independent original CPU expectations before native comparison; graphics/audio/item and ordinary-shot damage are explicit adapters.')
        (out/'original-reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)];digest=hashlib.sha256();records=0
    with gzip.open(expected,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            try:same(want or '',got or '')
            except ValueError:
                ww=(want or '').split();gg=(got or '').split();field=next((i for i,(x,y) in enumerate(zip(ww,gg)) if x!=y),min(len(ww),len(gg)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,field=field,expected=want,actual=got),indent=2)+'\n');process.terminate();raise
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native entity reference consumer failed')
    if digest.hexdigest()!=ref['trace_sha256'] or records!=ref['trace_records']:raise ValueError('entity reference trace identity mismatch')
    rejection(o)
    try:same('abcd 1','abce 1')
    except ValueError:pass
    else:raise ValueError('one-variable entity byte mutation accepted')
    result=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve())],capture_output=True,text=True,env=env,check=True)
    if result.stdout.strip()!='Stage 6 Yuuka entity contracts PASS':raise ValueError('entity contracts failed')
    if manifest!=source_manifest(root)[0]:raise ValueError('source changed during entity controls')
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),cases=len(rows),trace_records=records,counts=counts,fresh_rank_dispatch=dispatch,callback_rejection_passed=True,one_variable_rejection_passed=True,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,limits='Ordinary against-boss flag starts0. Existing atan domain excludes INT16_MIN displacement; signed extreme motion edges use age>=56. Drawing requests only: actual sprite/circle pixels, physical page/alias/pacing and ordinary battle integration remain separate.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','cases','trace_records','counts')}))
if __name__=='__main__':main()
