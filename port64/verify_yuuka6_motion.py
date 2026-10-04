#!/usr/bin/env python3
"""Original MAIN CPU controls for Yuuka6's eight animations/four motion helpers.

MAIN13A9:6933..6E76 plus actual vector/polar callees, load2000 DS8000.
No file, graphics, shot, audio or timing consumer is invoked in this batch.
Full boss24/animation10/mirror-state1 bytes and BYTE returns are compared.
Retained sequences advance only these helpers with an explicit caller clock
increment; they are not a complete battle, graphical route or FPS claim.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_AX,UC_X86_REG_CS
from verify_kurumi import Original as Base
from verify_orange import boss
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
ANIMATIONS=(0x6aad,0x6b1c,0x6b8c,0x6bf6,0x6c55,0x6d2c,0x6da1,0x6e17)
class Original(Base):
    def __init__(self,target):
        self.reject=False;self.memory_error=None;super().__init__(target)
        self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.memory_write)
    def body(self,u,address,size,unused):
        if self.reject and address==0x33a90+ANIMATIONS[0]:raise ValueError('injected Yuuka6 hook rejection')
        super().body(u,address,size,unused)
    def memory_write(self,u,access,address,size,value,unused):
        if address<0x80000 or address>=0x90000:return
        allowed=((0x853ca,0x853e2),(0x846c6,0x846d0),(0x846db,0x846dc))
        if not any(lo<=address and address+size<=hi for lo,hi in allowed):
            self.memory_error=ValueError(f'unowned Yuuka6 DS write {address:05X}/{size}')
            u.emu_stop()
    def call_args(self,*args,**kwargs):
        self.memory_error=None
        try:super().call_args(*args,**kwargs)
        except Exception:
            if self.memory_error:raise RuntimeError('Yuuka6 memory owner rejected') from self.memory_error
            raise
        if self.memory_error:raise RuntimeError('Yuuka6 memory owner rejected') from self.memory_error

def fixture(op='A',steps=1,selector=0,clock=0,animation=0,flag=1,path=0,aux=123,mirror=127,patterns=19,x=3072,y=1280,vx=17,vy=-19,angle=241,sprite=189,destination=(3072,1280)):
    raw=bytearray(boss(frame=clock,x=x,y=y,bonus=patterns));struct.pack_into('<hh',raw,8,vx,vy);raw[14]=sprite;raw[20]=angle
    raw+=struct.pack('<4Bh2hB',flag,path,aux,231,animation,-12345,23456,mirror)
    return [op,steps,selector,*destination,*raw]

def fixtures():
    clocks=(-32768,-32767,-2,-1,*range(49),32766,32767)
    for selector,clock,flag,sprite in itertools.product(range(8),clocks,(0,1,2,3,4,8,255),(0,128,255)):
        yield fixture(selector=selector,animation=clock,flag=flag,sprite=sprite)
    for clock,animation,flag,mirror,destination in itertools.product((-32768,-1,0,1,35,36,63,64,65,127,128,129,32767),(0,28,35,32767),(0,1,8),(0,1,2,255),((-32768,32767),(3072,1280),(32767,-32768))):
        yield fixture(op='M',clock=clock,animation=animation,flag=flag,mirror=mirror,destination=destination,patterns=255)
    # Every BYTE pattern residue, including 255 -> 0 on completion, and both
    # legitimate flight tables. Center residue calls the real animation owner.
    for patterns,path,clock in itertools.product(range(256),range(2),(-1,0,1,111,112,128)):
        yield fixture(op='F',patterns=patterns,path=path,clock=clock,flag=0,animation=35,x=32767,y=-32768,vx=32767,vy=-32768)
    for index,(angle,x,vx) in enumerate(itertools.product(range(256),(-32768,-1,767,768,769,3072,5375,5376,5377,32767),(-32768,-32,0,32,32767))):
        if index%3==0:yield fixture(op='W',clock=2,angle=angle,x=x,vx=vx)
    for x,angle,vx in itertools.product((-32768,767,768,5375,5376,32767),(0,1,255),(-32768,0,32767)):
        yield fixture(op='W',clock=1,angle=angle,x=x,vx=vx)
    for x,flag,animation,aux in itertools.product((-32768,-1,*range(3055,3105),32767),(0,1,8,255),(0,35,32767),(0,1,255)):
        yield fixture(op='C',x=x,flag=flag,animation=animation,aux=aux)
    for selector,flag in itertools.product(range(8),(0,1,255)):
        yield fixture(steps=96,selector=selector,animation=0,flag=flag)
    for path in range(2):
        yield fixture(op='F',steps=1438,path=path,clock=1,patterns=0,animation=0,flag=1,vx=0,vy=0)
    for flag,mirror in itertools.product((0,1,8),(0,1,255)):
        yield fixture(op='M',steps=260,clock=0,animation=0,flag=flag,mirror=mirror,patterns=254,destination=(768,1280))
    for x in (768,3072,5376):yield fixture(op='W',steps=1024,clock=1,x=x)
    for x,flag in itertools.product((0,3071,3072,3087,3088,6144),(0,1)):
        yield fixture(op='C',steps=420,x=x,flag=flag,animation=0)

def seed(o,row):
    if len(row)!=40:raise ValueError('Yuuka6 fixture size')
    o.reset();o.u.mem_write(0x853ca,bytes(row[5:29]));o.u.mem_write(0x846c6,bytes(row[29:39]));o.write(0x46db,'B',row[39])
    if o.read(0x1ed4,'10B')!=(0x60,0,0x70,0xe0,0x80,0x20,0x70,0x90,0xf0,0x10):raise ValueError('original flight table identity')

def execute(o,row):
    op=row[0]
    if op=='A':o.call_args(ANIMATIONS[row[2]])
    elif op=='M':o.call_args(0x69a9,args=(row[4],row[3]))
    elif op=='F':o.call_args(0x6933)
    elif op=='W':o.call_args(0x6a18)
    elif op=='C':o.call_args(0x6a73)
    else:raise ValueError('unknown original Yuuka6 operation')
    returned=0 if op=='W' else o.u.reg_read(UC_X86_REG_AX)&255
    if returned not in (0,1):raise ValueError('invalid original BYTE return')
    raw=bytes(o.u.mem_read(0x853ca,24))+bytes(o.u.mem_read(0x846c6,10))+bytes(o.u.mem_read(0x846db,1))
    return f'{returned} {raw.hex()}\n'

def same(want,got):
    if want.split()!=got.split():raise ValueError('Yuuka6 original/native checkpoint differs')

def rejection(o):
    o.reject=True
    try:o.call_args(ANIMATIONS[0])
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('original callback rejection swallowed')
    finally:o.reject=False

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    o=Original(a.target.read_bytes());rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures())
    configured=('\n'.join(' '.join(map(str,row)) for row in rows)+'\n').encode();counts={}
    for row in rows:counts[row[0]]=counts.get(row[0],0)+1
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'original-reference.json').read_text());fixture_path=a.reference_dir/'fixtures.txt';expected=a.reference_dir/'trace.txt.gz'
        if a.limit or not ref['passed'] or ref['target_sha256']!=sha(o.target) or sha(configured)!=ref['fixture_sha256'] or sha(fixture_path.read_bytes())!=ref['fixture_sha256']:raise ValueError('reference identity mismatch')
    else:
        fixture_path=out/'fixtures.txt';fixture_path.write_bytes(configured);expected=out/'trace.txt.gz';records=0;digest=hashlib.sha256()
        with gzip.open(expected,'wt',compresslevel=3) as trace:
            for index,row in enumerate(rows):
                seed(o,row)
                for step in range(row[1]):
                    line=execute(o,row);trace.write(line);digest.update(line.encode());records+=1
                    if row[0] not in ('A','C'):
                        clock=o.read(0x53da,'h')[0];o.write(0x53da,'h',(clock+1+32768)%65536-32768)
                if index and index%5000==0:print(f'Original Yuuka6 {index} fixtures PASS',flush=True)
        rejection(o)
        ref=dict(passed=True,target_sha256=sha(o.target),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),trace_records=records,cases=len(rows),counts=counts,callback_rejection_passed=True,scope='Independent original CPU producer before native comparison; valid paths0/1, one caller clock increment after each motion helper except center.')
        (out/'original-reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture_path)];env=os.environ.copy();env.setdefault('WINEDEBUG','-all');digest=hashlib.sha256();records=0
    with gzip.open(expected,'rt') as wanted,(out/'native-stderr.txt').open('w') as errors,subprocess.Popen(command,stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for index,(want,got) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            try:same(want or '',got or '')
            except ValueError:
                (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=index,expected=want,actual=got),indent=2)+'\n');process.terminate();raise
            digest.update((' '.join(got.split())+'\n').encode());records+=1
        if process.wait()!=0:raise ValueError('native Yuuka6 consumer failed')
    if digest.hexdigest()!=ref['trace_sha256'] or records!=ref['trace_records']:raise ValueError('reference trace identity mismatch')
    rejection(o)
    try:same('0 1234','1 1234')
    except ValueError:pass
    else:raise ValueError('one-variable return mutation accepted')
    default=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve())],capture_output=True,text=True,env=env,check=True)
    if default.stdout.strip()!='Stage 6 Yuuka movement contracts PASS':raise ValueError('Yuuka6 contracts failed')
    if manifest!=source_manifest(root)[0]:raise ValueError('source changed during controls')
    receipt=dict(passed=True,original_cpu_reexecuted=not bool(a.reference_dir),source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(configured),trace_sha256=digest.hexdigest(),cases=len(rows),trace_records=records,counts=counts,callback_rejection_passed=True,one_variable_rejection_passed=True,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','cases','trace_records','counts')}))
if __name__=='__main__':main()
