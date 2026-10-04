#!/usr/bin/env python3
"""Original MAIN Yuuka6 background state, checkerboard and mono pixel controls.

MAIN0AAF:7901/7937/7971/7DC9, checker7586 and mono152A; load2000 DS8000.
State controls execute actual RNG, atan/vector, clipping and checker kernels;
mode/color/fill/entrance/mono drawing are explicit ordered request adapters.
Pixel controls execute actual checker/mono with a bounded16-color GRCG shadow.
No physical PC98 page/alias/interrupt/frame pacing or whole-battle claim.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX,UC_X86_REG_CX,UC_X86_REG_ES,UC_X86_INS_OUT
from verify_orange_render import Original as Base
from verify_yuuka5_pixels import Shadow
from verify_marisa_pixels import planes
from probe_assets import main_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
CLIPS=(0,0x7901,0x7937)
class Original(Base):
    def __init__(self,target):
        self.background=[];self.in_checker=False;self.pixel_mode=False;self.reject=False;super().__init__(target)
        self.u.hook_add(unicorn.UC_HOOK_INSN,self.out,None,1,0,UC_X86_INS_OUT)
    def out(self,u,port,size,value,unused):
        try:
            if self.pixel_mode:return
            if self.in_checker:
                if port!=0x7e or size!=1:raise ValueError('unexpected checker OUT')
                return
            if (port,size,value)!=(0x7c,1,0):raise ValueError('unexpected background disable OUT')
            self.background.append([6,0,0,0])
        except Exception as e:self.callback_error=e;u.emu_stop()
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.reject and (cs,ip)==(0x2aaf,0x7971):raise ValueError('injected background callback rejection')
        if cs==0x2aaf:
            if self.pixel_mode and ip in (0x1666,0x166c,0x1672,0x152a):return
            def ret(cleanup):
                off=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0];u.reg_write(UC_X86_REG_SP,sp+cleanup);u.reg_write(UC_X86_REG_IP,off)
            if ip==0x7586:
                self.in_checker=True
                if not self.pixel_mode:self.background.append([3,0,0,0])
            if ip==0x7633:self.in_checker=False
            if ip in (0x1666,0x166c):self.background.append([0,0,0,192 if ip==0x1666 else 128]);ret(2);return
            if ip==0x1672:self.background.append([1,0,0,(u.reg_read(UC_X86_REG_AX)>>8)&255]);ret(2);return
            if ip==0x756a:self.background.append([2,0,0,0]);ret(2);return
            if ip==0x1426:
                cel=struct.unpack('<H',u.mem_read(0x70000+sp+2,2))[0];self.background.append([4,0,0,cel]);ret(4);return
            if ip==0x152a:
                pattern=struct.unpack('<H',u.mem_read(0x70000+sp+2,2))[0];signed=lambda n:n if n<32768 else n-65536
                self.background.append([5,signed(u.reg_read(UC_X86_REG_CX)),signed(u.reg_read(UC_X86_REG_AX)),pattern]);ret(4);return
        super().hook_body(u,address,size,unused)

def shape(x=3072,y=2944,angle=96,speed=16):return struct.pack('<hhBB',x,y,angle,speed)
def fixture(op='U',steps=1,phase=2,clock=0,state=0,fade=0,latch=0,pattern=120,speed=16,clip=2,cursor=0,first=None,board=None):
    pool=[first or shape()]+[shape((i*119)%6144,(i*137)%5888,i*17%256,(i*19)%256) for i in range(1,56)]+[shape(-12345,23456,129,255)]
    return [op,steps,phase,clock,state,fade,latch,pattern,speed,clip,cursor,17,29,41,0,0x9abc,0x1234,b''.join(pool).hex(),(board or struct.pack('<3H2B',0xaf30,1200,2480,4,2)).hex()]

def fixtures():
    for index,(state,fade,phase,clip,latch) in enumerate(itertools.product((*range(18),255),(0,1,126,127,128,129,252,253,254,255),(0,2,3,4,5,7,8,9,10,11,12,13,14,15,17,253,254,255),(1,2),(0,1))):
        if index%11==0:yield fixture(state=state,fade=fade,phase=phase,clip=clip,latch=latch,cursor=255)
    for phase,fade,clip in itertools.product((2,7,15,254),range(256),(1,2)):
        if (phase+fade+clip)%7==0:yield fixture(state=(phase+fade)%18,fade=fade,phase=phase,clip=clip,latch=fade%2,pattern=65535,cursor=255)
    xs=(-32768,-129,-128,-127,0,6271,6272,6273,32767);ys=(-32768,-129,-128,-127,0,6143,6144,6145,32767)
    for index,(x,y,clip,speed,flyout) in enumerate(itertools.product(xs,ys,(1,2),(0,1,127,255),(0,16,256,65535))):
        if index%5==0:yield fixture(op='C',clip=clip,speed=flyout,first=shape(x,y,255,speed))
    for phase,clock in itertools.product(range(256),(-32768,-65,-4,-3,-1,0,1,2,3,31,32,32767)):
        if phase<2 or (phase+clock)%23==0:yield fixture(op='B',phase=phase,clock=clock,cursor=255)
    # Caller-driven retained render sequence, not a full boss update/game route.
    for cursor in (0,255):yield fixture(op='S',steps=1571,cursor=cursor,clip=0,latch=0)
    for state,phase in ((0,2),(4,4),(6,6),(8,8),(10,10),(12,12),(14,14),(16,16),(17,255)):
        yield fixture(state=state,phase=phase,steps=40,fade=252)

def seed(o,row):
    o.reset();o.pixel_mode=False;o.in_checker=False;o.background=[]
    o.write(0x53d9,'B',row[2]);o.write(0x53da,'h',row[3]);o.write(0xba90,'2B',row[4],row[5]);o.write(0x1f02,'B',row[6]);o.write(0xbbe8,'3H',row[7],row[8],CLIPS[row[9]]);o.write(0x3ecc,'H',row[10]);o.write(0x2a82,'3B',*row[11:14]);o.write(0x5393,'B',row[14]);o.write(0xbcee,'H',row[15]);o.write(0xba8e,'H',row[16]);o.u.mem_write(0x8ba92,bytes.fromhex(row[17]));o.u.mem_write(0x81efa,bytes.fromhex(row[18]))

def sequence(step):
    if step<3:return 0,step
    if step<35:return 1,step-3
    if step<291:return 2,step-35
    phases=(3,5,7,9,11,13,15,254);return phases[min(7,(step-291)//160)],(step-291)%160

def execute(o,row,step):
    o.background=[];o.in_checker=False
    if row[0]=='C':o.call_args(CLIPS[row[9]],(0xba92,),cs=0x2aaf)
    elif row[0]=='U':o.call_args(0x7971,cs=0x2aaf)
    else:
        phase,clock=sequence(step) if row[0]=='S' else (row[2],(row[3]+step+32768)%65536-32768)
        o.write(0x53d9,'B',phase);o.write(0x53da,'h',clock);o.call_args(0x7dc9,cs=0x2aaf)
    pointer=o.read(0xbbec,'H')[0]
    if pointer not in CLIPS:raise ValueError('unattested clip pointer')
    values=[o.u.mem_read(0x8ba92,342).hex(),o.u.mem_read(0x81efa,8).hex(),*o.read(0xba90,'2B'),*o.read(0x1f02,'B'),*o.read(0xbbe8,'2H'),CLIPS.index(pointer),*o.read(0x3ecc,'H'),*o.read(0x2a82,'3B'),*o.read(0x5393,'B'),*o.read(0xba8e,'H'),*o.read(0xbcee,'H'),len(o.background),*itertools.chain.from_iterable(o.background)]
    return ' '.join(map(str,values))+'\n'

def pixel_rows(assets):
    yield ['K',32,7,struct.pack('<3H2B',0xaf30,1200,2480,4,2).hex()]
    for passes,dark in itertools.product((1,2,3),(4,8)):
        yield ['K',8,13,struct.pack('<3H2B',0xaf6c,320,2480,dark,passes).hex()]
    for image,shift in itertools.product(range(92,100),range(8)):
        w,h,data=planes(assets['MIKO16.BFT'],image);assert (w,h)==(16,16)
        yield ['M',96+shift,128,8+(image%2),(image+shift)%16,data[:32].hex()]
    for x,y,color in itertools.product((-32768,-17,-16,-1,0,31,32,415,639,32767),(-32768,-1,0,15,383,399,32767),(0,9,15,255)):
        if (x+y+color)%7==0:
            data=bytes((i*73+19)&255 for i in range(32));yield ['M',x,y,color,7,data.hex()]

def pixels(o,row):
    o.reset();o.pixel_mode=True;o.in_checker=False;o.u.reg_write(UC_X86_REG_ES,0xa800);shadow=Shadow(o,row[2] if row[0]=='K' else row[4])
    try:
        if row[0]=='K':
            o.u.mem_write(0x81efa,bytes.fromhex(row[3]));o.call_args(0x166c,cs=0x2aaf)
            for step in range(row[1]):o.call_args(0x7586,cs=0x2aaf);yield bytes(o.u.mem_read(0x81efa,8))+bytes(shadow.screen)
        else:
            _,x,y,color,seed,raw=row;o.write(0x2ac4,'H',0x9000);o.u.mem_write(0x90000,bytes.fromhex(raw));o.call_args(0x1666,cs=0x2aaf);o.u.reg_write(UC_X86_REG_AX,(color&255)<<8);o.call_args(0x1672,cs=0x2aaf);o.u.reg_write(UC_X86_REG_AX,y&65535);o.u.reg_write(UC_X86_REG_CX,x&65535);o.call_args(0x152a,(0,),cs=0x2aaf);yield bytes(shadow.screen)
    finally:shadow.close();o.pixel_mode=False

def rejection(o):
    o.reset();o.reject=True
    try:o.call_args(0x7971,cs=0x2aaf)
    except RuntimeError as e:
        if not isinstance(e.__cause__,ValueError):raise
    else:raise ValueError('background callback rejection swallowed')
    finally:o.reject=False

def same(want,got):
    if want!=got:raise ValueError('background original/native data differs')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','hdi','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);o=Original(a.target.read_bytes());assets=main_assets(a.hdi);manifest=source_manifest(Path(__file__).resolve().parents[1])[0];rejection(o)
    rows=list(itertools.islice(fixtures(),a.limit) if a.limit else fixtures());pixrows=list(itertools.islice(pixel_rows(assets),a.limit) if a.limit else pixel_rows(assets));configured=('\n'.join(' '.join(map(str,r)) for r in rows)+'\n').encode();pixconfigured=('\n'.join(' '.join(map(str,r)) for r in pixrows)+'\n').encode()
    if a.reference_dir:
        ref=json.loads((a.reference_dir/'original-reference.json').read_text());fixture=a.reference_dir/'fixtures.txt';pixfixture=a.reference_dir/'pixel-fixtures.txt';trace=a.reference_dir/'trace.txt.gz';pixtrace=a.reference_dir/'pixel-trace.bin.gz'
        if a.limit or not ref['passed'] or ref['target_sha256']!=sha(o.target) or ref['hdi_sha256']!=sha(a.hdi.read_bytes()) or sha(configured)!=ref['fixture_sha256'] or sha(pixconfigured)!=ref['pixel_fixture_sha256'] or sha(fixture.read_bytes())!=ref['fixture_sha256'] or sha(pixfixture.read_bytes())!=ref['pixel_fixture_sha256']:raise ValueError('background reference identity differs')
    else:
        fixture=out/'fixtures.txt';fixture.write_bytes(configured);pixfixture=out/'pixel-fixtures.txt';pixfixture.write_bytes(pixconfigured);trace=out/'trace.txt.gz';pixtrace=out/'pixel-trace.bin.gz';digest=hashlib.sha256();records=0
        with gzip.open(trace,'wt',compresslevel=3) as f:
            for index,r in enumerate(rows):
                seed(o,r)
                for step in range(r[1]):line=execute(o,r,step);f.write(line);digest.update(line.encode());records+=1
                if index and index%500==0:print('Original background',index,'fixtures PASS',flush=True)
        pdigest=hashlib.sha256();pbytes=0;precords=0
        with gzip.open(pixtrace,'wb',compresslevel=3) as f:
            for r in pixrows:
                for data in pixels(o,r):f.write(data);pdigest.update(data);pbytes+=len(data);precords+=1
        ref=dict(passed=True,target_sha256=sha(o.target),hdi_sha256=sha(a.hdi.read_bytes()),asset_sha256=sha(assets['MIKO16.BFT']),source_manifest_sha256=manifest,fixture_sha256=sha(configured),pixel_fixture_sha256=sha(pixconfigured),trace_sha256=digest.hexdigest(),trace_records=records,cases=len(rows),pixel_cases=len(pixrows),pixel_records=precords,pixel_bytes=pbytes,pixel_trace_sha256=pdigest.hexdigest(),scope=__doc__)
        (out/'original-reference.json').write_text(json.dumps(ref,indent=2)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');prefix=([a.runner] if a.runner else [])+[str(a.exe.resolve())];digest=hashlib.sha256();records=0
    with gzip.open(trace,'rt') as wanted,(out/'native-state-stderr.txt').open('w') as errors,subprocess.Popen(prefix+['--vectors',str(fixture)],stdout=subprocess.PIPE,stderr=errors,text=True,env=env) as process:
        for i,(w,g) in enumerate(itertools.zip_longest(wanted,process.stdout)):
            ww=' '.join((w or '').split())+'\n';gg=' '.join((g or '').split())+'\n'
            try:same(ww,gg)
            except ValueError:(out/'mismatch.json').write_text(json.dumps(dict(record=i,expected=w,actual=g),indent=2)+'\n');process.terminate();raise
            digest.update(gg.encode());records+=1
        if process.wait()!=0:raise ValueError('background native state consumer failed')
    if digest.hexdigest()!=ref['trace_sha256'] or records!=ref['trace_records']:raise ValueError('background trace hash/extent differs')
    pdigest=hashlib.sha256();pbytes=0
    with gzip.open(pixtrace,'rb') as wanted,(out/'native-pixel-stderr.txt').open('w') as errors,subprocess.Popen(prefix+['--pixels',str(pixfixture)],stdout=subprocess.PIPE,stderr=errors,env=env) as process:
        while True:
            w=wanted.read(65536);g=process.stdout.read(len(w) if w else 1)
            try:same(w,g)
            except ValueError:(out/'pixel-mismatch.json').write_text(json.dumps(dict(offset=pbytes,expected_sha256=sha(w),actual_sha256=sha(g)))+'\n');process.terminate();raise
            if not w:break
            pdigest.update(g);pbytes+=len(g)
        if process.wait()!=0:raise ValueError('background native pixel consumer failed')
    if pdigest.hexdigest()!=ref['pixel_trace_sha256'] or pbytes!=ref['pixel_bytes']:raise ValueError('background pixels hash/extent differs')
    try:same(b'\x00',b'\x01')
    except ValueError:pass
    else:raise ValueError('pixel byte perturbation accepted')
    output=subprocess.run(prefix,capture_output=True,text=True,check=True,env=env).stdout.strip()
    if output!='Stage 6 Yuuka background contracts PASS':raise ValueError('background contracts failed')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during background controls')
    receipt=dict(ref,original_source_manifest_sha256=ref['source_manifest_sha256'],original_cpu_reexecuted=not bool(a.reference_dir),source_manifest_sha256=manifest,native_sha256=sha(a.exe.read_bytes()),callback_rejection_passed=True,one_byte_rejection_passed=True,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),limits='Pixel shadow preserves flat visible writes and seeded colors, not physical VRAM aliases/pages. State controls adapt fill/BB/mono calls; retained sequences are caller-driven background ownership, not ordinary core/combat or complete game. Atan INT16_MIN displacement and malformed checker segments outsideA850..AF6C explicitly excluded/rejected. No DOS exact promotion.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('passed','cases','trace_records','pixel_cases','pixel_records','pixel_bytes')}))
if __name__=='__main__':main()
