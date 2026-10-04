#!/usr/bin/env python3
"""Original MAIN CPU controls for the complete two-slot thick-laser owner.

State/copy/allocation/collision execute 13A9:22E4..243D; graphics producer
executes 0AAF:37D3..3970. Sound and ordered FAR drawing calls are adapters.
Drawing requests are compared before rasterization; physical VRAM/pacing and
full Yuuka gameplay are outside this control's scope. No DOS exact claim.
"""
import argparse, gzip, hashlib, itertools, json, os, struct, subprocess
from datetime import datetime, timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_IP, UC_X86_REG_SP, UC_X86_REG_DS, UC_X86_REG_SS, UC_X86_REG_BP, UC_X86_REG_EFLAGS, UC_X86_INS_OUT
from verify_enemy import Original as Base
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def __init__(self,target):
        self.error=None;self.reject=False;super().__init__(target)
        self.u.hook_add(unicorn.UC_HOOK_INSN,self.out,None,1,0,UC_X86_INS_OUT)
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as error:self.error=error;u.emu_stop()
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.reject and (cs,ip)==(0x33a9,0x2358):raise ValueError('injected laser callback rejection')
        def ret(args):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4+args);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off)
        if (cs,ip)==(0x330e,0x7d2):
            value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]
            self.events.append([0,0,value,0,0,0,0,0]);ret(2);return
        graphics={0x1744:4,0x1774:6,0x114c:6,0x107c:8}
        if cs==0x2000 and ip in graphics:
            count=graphics[ip];args=struct.unpack('<'+'h'*(count//2),u.mem_read(0x70000+sp+4,count))
            if ip==0x1744:
                color,mode=args;self.events.append([1,mode&65535,color&65535,0,0,0,0,0])
            elif ip==0x1774:
                bottom,top,x=args;self.events.append([2,0,0,x,top,0,bottom,0])
            elif ip==0x114c:
                radius,y,x=args;self.events.append([3,0,0,x,y,0,0,radius])
            else:
                bottom,right,top,left=args;self.events.append([4,0,0,left,top,right,bottom,0])
            ret(count);return
        super().hook(u,address,size,unused)
    def out(self,u,port,size,value,unused):
        if (port,size,value)!=(0x7c,1,0):self.error=ValueError('unexpected laser I/O');u.emu_stop();return
        self.events.append([5,0,0,0,0,0,0,0])
    def call(self,ip,args=(),far=False,cs=0x33a9):
        self.error=None
        for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,value)
        stack=[0xf000]+([cs] if far else [])+list(args)
        self.u.mem_write(0x7e000,struct.pack('<'+'H'*len(stack),*[x&65535 for x in stack]))
        self.u.emu_start(cs*16+ip,cs*16+0xf000,count=2000000)
        if self.error:raise RuntimeError('original laser adapter rejected') from self.error
        if self.u.reg_read(UC_X86_REG_IP)!=0xf000 or self.u.reg_read(UC_X86_REG_SP)!=0xe000+len(stack)*2:raise ValueError('original laser ABI/return failed')

def beam(flag=0,clock=19,radius=1,speed=6,maximum=160,line=32,hold=144,x=3072,y=1024,color=8,marker=19):
    return list(struct.pack('<BBhh4BhhhBBhhh',flag,marker&255,x,y,*[(marker+37*i)&255 for i in range(4)],clock,line,hold,color,(marker+17)&255,maximum,radius,speed))
def fixture(op='U',steps=1,slot=0,player=(3072,5120),hit=0,template=None,first=None,second=None):
    return [op,steps,slot,*player,hit,*(template or beam(flag=1,marker=201)),*(first or beam(flag=2,marker=19)),*(second or beam(marker=71))]
def fixtures():
    for marker in range(64):
        yield fixture(op='I',template=beam(flag=255,clock=-32768,radius=-123,speed=-1,marker=marker),first=beam(flag=2,marker=marker+13),second=beam(flag=127,marker=marker+31))
    for slot,marker in itertools.product(range(2),range(32)):
        yield fixture(op='P',slot=slot,template=beam(flag=marker%5,clock=-marker,radius=marker*317,marker=marker))
    for flags,scratch,hit in itertools.product(itertools.product((0,1,2,255),repeat=2),(0,1,255),(0,1,127)):
        yield fixture(op='A',template=beam(flag=scratch),first=beam(flag=flags[0]),second=beam(flag=flags[1]),hit=hit)
    radii=(-32768,-8192,-1,0,1,3,4,7,8,16,63,64,144,160,168,180,32767)
    for i,(flag,clock,radius,speed) in enumerate(itertools.product((0,1,2,3,4,5,127,128,255),(-32768,-1,0,1,31,32,143,144,32767),radii,(-32768,-1,0,1,6,32767))):
        if i%2:continue
        yield fixture(first=beam(flag=flag,clock=clock,radius=radius,speed=speed,maximum=(144,160,168,180)[i%4]),second=beam(flag=5 if i%7==0 else 0,x=-32768,y=32767,radius=32767),hit=i%3)
    # Actual inclusive hit-box edges, including wrapped intermediate widths.
    for flag,radius,dx,dy in itertools.product((1,2,3,4,255),(1,8,16,63,64,160,180,-8192),(-1,0,1),(-1,0,1)):
        narrow=(radius*4+32768)%65536-32768;narrow=min(narrow,256)
        width=(radius*16-narrow+32768)%65536-32768
        wrap=lambda n:(n+32768)%65536-32768
        for side in (-1,1):
            yield fixture(first=beam(flag=flag,clock=-1,radius=radius,speed=0),player=(wrap(3072+side*width+dx),wrap(1024+radius*8+dy)))
    # Render commands include negative radii/coordinates without silently
    # interpreting those requests as successfully rasterized visible pixels.
    for i,(flag,radius,x,y,color) in enumerate(itertools.product((0,1,2,4,5,128,255),radii,(-32768,-17,-16,-1,0,3072,32767),(-32768,-17,-16,-1,0,1024,32767),(0,8,15,255))):
        if i%7:continue
        yield fixture(op='D',first=beam(flag=flag,radius=radius,x=x,y=y,color=color),second=beam(flag=1 if i%3==0 else 2,radius=16,color=3))
    for maximum,hit in itertools.product((144,160,168,180),(0,1)):
        yield fixture(op='L',steps=640,template=beam(flag=255,clock=-19,radius=-123,speed=-1,maximum=maximum),first=beam(flag=4),second=beam(flag=255),hit=hit)
    yield fixture(op='S',steps=400,first=beam(flag=1,clock=0,radius=1,speed=6,line=32),second=beam(flag=1,clock=0,radius=1,speed=1,maximum=16,line=16,hold=24),player=(3072,5120))

def seed(o,row):
    o.reset();o.error=None;o.u.mem_write(0x842d8,bytes(row[6:]));o.write(0x464e,'hh',*row[3:5]);o.write(0x4669,'B',row[5])
def execute(o,row,frame):
    o.events=[];op=row[0]
    if op=='I':o.call(0x22e4,far=True)
    elif op=='P':o.call(0x2315,args=(0x42f0+row[2]*24,))
    elif op=='A':o.call(0x232d)
    elif op=='D':o.call(0x37d3,cs=0x2aaf)
    elif op=='L' and frame==0:o.call(0x22e4,far=True);o.call(0x232d)
    else:o.call(0x2358)
    return ' '.join(map(str,[o.u.mem_read(0x842d8,72).hex(),*o.read(0x4669,'B'),len(o.events),*itertools.chain.from_iterable(o.events)]))
def rejection(o):
    o.reject=True
    try:o.call(0x2358)
    except RuntimeError as error:
        if not isinstance(error.__cause__,ValueError):raise
    else:raise ValueError('original callback rejection was swallowed')
    finally:o.reject=False

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);a=p.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
    rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures());configured=('\n'.join(' '.join(map(str,row)) for row in rows)+'\n').encode();counts={}
    for row in rows:counts[row[0]]=counts.get(row[0],0)+1
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'original-reference.json').read_text());fixture_path=a.reference_dir/'fixtures.txt';expected=a.reference_dir/'trace.txt.gz'
        if a.limit or not ref['passed'] or ref['target_sha256']!=sha(o.target) or sha(configured)!=ref['fixture_sha256'] or sha(fixture_path.read_bytes())!=ref['fixture_sha256']:raise ValueError('original reference identity differs')
    else:
        fixture_path=out/'fixtures.txt';fixture_path.write_bytes(configured);expected=out/'trace.txt.gz';records=0;digest=hashlib.sha256()
        with gzip.open(expected,'wt',compresslevel=3) as trace:
            for row in rows:
                seed(o,row)
                for frame in range(row[1]):
                    line=execute(o,row,frame)+'\n';trace.write(line);digest.update(line.encode());records+=1
        rejection(o)
        ref=dict(passed=True,target_sha256=sha(o.target),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),trace_records=records,cases=len(rows),counts=counts,callback_rejection_passed=True,scope='Original CPU expectations, independently produced before native comparison.')
        (out/'original-reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)]
    native=hashlib.sha256();records=0
    with gzip.open(expected,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            if want is None or got is None or want.split()!=got.split():
                ww=want.split() if want else [];gg=got.split() if got else [];field=next((i for i,(x,y) in enumerate(zip(ww,gg)) if x!=y),min(len(ww),len(gg)))
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,field=field,expected=ww,actual=gg),indent=2)+'\n');process.terminate();raise ValueError(f'laser checkpoint{index} field{field} differs')
            native.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native laser process failed')
    if native.hexdigest()!=ref['trace_sha256'] or records!=ref['trace_records']:raise ValueError('original trace identity differs')
    rejection(o)
    default=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve())],env=env,capture_output=True,text=True,check=True)
    if default.stdout.strip()!='Thick laser contracts PASS':raise ValueError('native laser contracts rejected')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during laser controls')
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(configured),trace_sha256=native.hexdigest(),cases=len(rows),trace_records=records,counts=counts,callback_rejection_passed=True,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','cases','trace_records','counts')}))
if __name__=='__main__':main()
