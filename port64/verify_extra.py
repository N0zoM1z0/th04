#!/usr/bin/env python3
"""Original Extra setup and complete timed midboss versus native owners.

Actual MAIN13A9:AA88..AB48,0C1F..1008 and0AAF:1E5A..1EAB execute at
loads1000/2000 with explicit DS/SS adapters. File loaders, item allocation,
sound and sprite pixels are request adapters; original tune/add/RNG/polar/
activation/reset instructions execute. This is not complete Extra gameplay.
"""
import argparse,gzip,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_midboss import Original as Base,record as base_record,row
from verify import source_manifest
from probe_assets import main_assets
from verify_marisa_pixels import planes
from verify_player_render import Original as PixelOriginal
from verify_player_bomb_pixels import Shadow,SCREEN,read_exact
from verify_score import Original as ScoreOriginal
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
sha=lambda b:hashlib.sha256(b).hexdigest()

def record(*args,**kwargs):
    state=base_record(*args,**kwargs);state[12:14]=struct.pack('<H',5400);return state

class LegacyView:
    # Earlier request adapters compare canonical CS. Return words already
    # contain actual relocated CS and pass straight through on register writes.
    def __init__(self,u,delta):self.u=u;self.delta=delta
    def reg_read(self,r):return self.u.reg_read(r)+(self.delta if r==UC_X86_REG_CS else 0)
    def __getattr__(self,n):return getattr(self.u,n)

class Original(Base):
    def __init__(self,target,load=0x2000):
        self.delta=0x2000-load;self.error=None;self.resources=[]
        super().__init__(target)
        at=struct.unpack_from('<H',target,24)[0]
        if self.delta:
            for i in range(1136):
                off,seg=struct.unpack_from('<HH',target,at+i*4);site=seg*16+off
                struct.pack_into('<H',self.module,site,(struct.unpack_from('<H',self.module,site)[0]-self.delta)&65535)
            self.u.mem_write(load*16,bytes(self.module))
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as e:self.error=e;u.emu_stop()
    def body(self,u,address,size,unused):
        actual=u.reg_read(UC_X86_REG_CS);pair=(actual+self.delta,address-actual*16)
        sp=u.reg_read(UC_X86_REG_SP)
        def ret(far=False,args=0):
            data=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
            u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args)
            if far:u.reg_write(UC_X86_REG_CS,data[1])
            u.reg_write(UC_X86_REG_IP,data[0])
        if pair in ((0x330e,0x858),(0x33a9,0xa518)):
            far=pair[0]==0x330e
            args=struct.unpack('<4H',u.mem_read(0x70000+sp+(4 if far else 2),8))
            off,seg=args[1:3] if far else args[:2]
            name=bytes(u.mem_read(seg*16+off,32)).split(b'\0')[0].decode('ascii')
            self.resources.append((name,args[0] if far else None,args[3] if far else None))
            ret(far,8 if far else 4);return
        if pair==(0x33a9,0x9fa8):
            value,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+2,6))
            self.events.append([11,x,y,value,0]);ret(False,6);return
        if pair[0]==0x33a9 and pair[1] in (0x945e,0x9486,0x94a2):
            t=self.template();self.events.append([10,t[2],t[3],t[7],t[8]])
        Base.hook(self,LegacyView(u,self.delta),address+self.delta*16,size,unused)
    def call_args(self,ip,args=(),far=False,cs=0x33a9):
        cs-=self.delta;u=self.u
        for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),
                          (UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):
            u.reg_write(reg,value)
        words=(0xf000,cs,*args) if far else (0xf000,*args)
        u.mem_write(0x7e000,struct.pack('<'+'H'*len(words),*(v&65535 for v in words)))
        u.emu_start(cs*16+ip,cs*16+0xf000,count=1000000)
        if self.error:raise RuntimeError('original Extra callback rejected') from self.error
        assert u.reg_read(UC_X86_REG_IP)==0xf000 and u.reg_read(UC_X86_REG_SP)==0xe000+len(words)*2,'Extra ABI/return differs'

def setup(o,marker):
    o.reset();o.error=None;o.resources=[]
    boss=bytes((marker+i*73)&255 for i in range(24));extra=bytes((marker+i*19)&255 for i in range(16))
    exp=bytes((marker+i*37)&255 for i in range(48));mid=bytes((marker+i*11)&255 for i in range(22))
    for at,data in ((0x853ca,boss),(0x8bcde,extra),(0x84298,exp),(0x853b4,mid)):o.u.mem_write(at,data)
    hpbar=marker*257-32768;angle=marker^85
    o.write(0x46b2,'B',255);o.write(0x1ed0,'h',hpbar);o.write(0x1ed2,'B',angle)
    o.call_args(0x642c,far=True);o.call_args(0xaa88,far=True)
    assert o.resources==[('st06bk.cdg',0,16),('st06.bb',None,None)],o.resources
    assert o.read(0x46bc,'3H')==(0xebc,0x33a9-o.delta,0x1e5a),'Extra callbacks differ'
    assert o.read(0xbcd6,'4H')==(0x7e89,0x4c5b,0x33a9-o.delta,0x6ac6)
    assert o.read(0x432a,'2H')==(0x11be,0x11be) and o.read(0xba8c,'H')==(0x1658,)
    result=[bytes(o.u.mem_read(at,n)).hex() for at,n in ((0x853ca,24),(0x8bcde,16),(0x84298,48),(0x853b4,22))]
    result+=map(str,(*o.read(0x46b2,'B'),*o.read(0x1ed0,'h'),*o.read(0x1ed2,'B'),*o.read(0xbcf0,'hh'),*o.read(0x23ed,'B')))
    return ' '.join(map(str,(4,*boss,*extra,*exp,*mid,255,hpbar,angle))),' '.join(result)

def fixtures():
    clocks=(0,1,127,128,159,160,249,250,258,266,274,290,298,306,314,319,320,350,358,366,374,390,398,406,414,439,440,450,490,498,506,514,519,520,639,640,32767,-32768)
    for i,(phase,clock,density) in enumerate(itertools.product(range(8),clocks,(0,1))):
        yield row(rank=4,frame=5400+i%16,density=density,defeat=(0,255)[i%2],state=record(phase,clock,0,hp=(128,129,895,896,767,768,4096)[i%7]))
    for x,y,line,scrolling,frame in itertools.product((-257,-256,-255,0,6271,6272,6400),(-257,-256,-255,0,6400),(0,399),(0,1),(0,3,4,7,8,15)):
        yield row('D',rank=4,frame=frame,line=line,scrolling=scrolling,state=record(sprite=0,x=x,y=y))
    for op,frame,active in itertools.product(('A','R'),(5399,5400,5401,65535),(0,1)):
        yield row(op,rank=4,frame=frame,active=active,state=record(5,450,0))
    for cursor in (0,255):
        initial=list(struct.pack('<6hHhBBhBB',-256,4096,-256,4096,64,-64,5400,4096,0,0,0,0,96))
        yield row('S',rank=4,frame=5400,defeat=cursor,state=initial)+[4000]

def seed(o,f):
    op,rank,perf,frame,scroll,line,speed,active,scrolling,hpbar,vram,angle,defeat,density,damage=f[:15]
    o.reset();o.error=None;o.events=[];o.draws=[];o.damage=damage
    o.context(rank,perf,0,3072,5120);o.u.mem_write(0x853b4,bytes(f[15:37]))
    o.u.mem_write(0x85a22,bytes([int(bool(density))]+[0]*25)*440)
    o.write(0x53a2,'BB4h8B',1,52,2048,1024,17,-19,46,129,42,3,6,123,128,19)
    o.write(0xbcc4,'H',(0x9435,0x9440,0x9448,0x9453,0x9440)[rank])
    o.write(0xbcc0,'H',(0x945e,0x9486,0x94a2,0x94a2,0x9486)[rank]);o.write(0xbcc2,'H',(0x94be,0x94da,0x94f6,0x94f6,0x94da)[rank])
    o.write(0xbcba,'BB',0,0);o.write(0xbcb7,'BBB',0,0,0);o.write(0x53a0,'B',int(rank==4))
    o.write(0x46b2,'B',active);o.write(0x538a,'H',frame);o.write(0x538c,'4B',0,frame%4,frame%8,frame%16)
    o.write(0x4276,'BBh',scroll,speed,line);o.write(0x427c,'B',scrolling)
    o.write(0x1ed0,'h',hpbar);o.write(0x4256,'h',vram);o.write(0x4254,'B',angle);o.write(0x1ed2,'B',defeat)
    o.write(0x435a,'I',0);o.write(0x3ecc,'H',defeat)
    return op

def checkpoint(o):
    v=[bytes(o.u.mem_read(0x853b4,22)).hex(),*o.read(0x46b2,'B'),*o.read(0x1ed0,'h'),*o.read(0x4256,'h'),*o.read(0x4254,'B'),*o.read(0x1ed2,'B'),0,*o.read(0x3ecc,'H'),*o.read(0xbcb9,'B'),*o.template(),*o.read(0xbcb7,'B'),bytes(o.u.mem_read(0x85a22,440*26)).hex(),len(o.events),*itertools.chain.from_iterable(o.events),len(o.draws),*itertools.chain.from_iterable(o.draws)]
    return ' '.join(map(str,v))

def records(o,inputs):
    for f in inputs:
        op=seed(o,f)
        if op=='S':
            for tick in range(f[-1]):
                if not o.read(0x46b2,'B')[0]:break
                o.events=[];o.draws=[];frame=(5400+tick)&65535
                o.write(0x538a,'H',frame);o.write(0x538c,'4B',0,frame%4,frame%8,frame%16)
                o.call_args(0xebc,far=True);o.call_args(0x1e5a,cs=0x2aaf);yield checkpoint(o)
            assert not o.read(0x46b2,'B')[0],'original Extra sequence did not exit'
        else:
            if op=='U':o.call_args(0xebc,far=True)
            elif op=='D':o.call_args(0x1e5a,cs=0x2aaf)
            elif op=='A':o.call_args(0x6454,far=True)
            else:o.call_args(0x642c,far=True)
            yield checkpoint(o)

def raw_tiny(target,hdi,exe,out):
    assets=main_assets(hdi);rows=[];files={}
    # Global0..19 precede the session's tiny conversion range20..119.
    for name,images in (('MIKO.BFT',range(3)),('MARI.BFT',range(3)),('MIKOD.BFT',range(1)),('MIKO32.BFT',range(16))):
        path=out/name;path.write_bytes(assets[name]);files[name]=path
        for image,left,top in itertools.product(images,(24,25,31),(0,399)):
            rows.append((name,image,left,top,len(rows)%16))
    fixture=out/'raw-tiny-fixtures.txt'
    fixture.write_text('\n'.join(f'{files[n]} {i} {x} {y} {s}' for n,i,x,y,s in rows)+'\n')
    native=out/'raw-tiny-native.bin'
    with native.open('wb') as f:subprocess.run([str(exe.resolve()),'--raw-tiny-vectors',str(fixture)],stdout=f,check=True)
    controls=[]
    for load in (0x1000,0x2000):
        o=PixelOriginal(target,load);o.pixels=True;o.requests=[]
        with native.open('rb') as f:
            for index,(name,image,left,top,seed_value) in enumerate(rows):
                o.reset();o.error=None;o.requests=[];w,h,data=planes(assets[name],image)
                o.u.mem_write(0x90000,data);o.write(0x2ac4,'H',0x9000);o.write(0x2ec4,'H',(w//8<<8)|h)
                o.u.reg_write(UC_X86_REG_ES,0xa800);shadow=Shadow(o,seed_value)
                try:
                    o.call_args(0x1666);o.u.reg_write(UC_X86_REG_AX,left);o.u.reg_write(UC_X86_REG_DX,top)
                    o.call_args(0x1a56,(0,));want=bytes(shadow.screen)
                finally:shadow.close()
                got=read_exact(f,SCREEN)
                assert got==want,f'raw tiny case{index} differs at load{load:04x}'
                row=dict(asset=name,image=image,left=left,top=top,seed=seed_value,first_planar_byte=data[0],writes=shadow.writes,ports=shadow.ports,screen_sha256=sha(want))
                if load==0x1000:controls.append(row)
                else:assert controls[index]==row,'raw tiny changed with load'
            assert not f.read(1),'extra raw tiny pixels'
    assert controls and any(c['writes']==0 for c in controls),'missing original header-rejection control'
    # A changed pixel is rejected even when the original deliberately draws none.
    sample=bytearray(read_exact(native.open('rb'),SCREEN));sample[0]^=1
    assert sha(sample)!=controls[0]['screen_sha256'],'raw tiny comparator missed mutation'
    result=dict(cases=len(rows),compared_pixels=len(rows)*SCREEN,loads=['1000','2000'],controls=controls,
                assets={n:sha(assets[n]) for n in files},hdi_sha256=sha(hdi.read_bytes()),native_pixels_sha256=sha(native.read_bytes()),
                limits='Original raw1A56/GRCG setup; independent BFNT planar inputs and visible GRCG shadow. Global0..19 only; no complete Extra VRAM or timing claim.')
    native.unlink()
    for p in files.values():p.unlink()
    return result

def extend_order(target,exe,out):
    body=target[6144+0xaaf0+0x98:6144+0xaaf0+0x213]
    calls=[(i.address,int(i.op_str,16)&65535) for i in Cs(CS_ARCH_X86,CS_MODE_16).disasm(body,0x98)
           if i.mnemonic=='call' and i.op_str.startswith('0x')]
    assert (0x13c,0x81f5) in calls and (0x204,0x6bd4) in calls,'original gameplay render/score ordering differs'
    assert all(ip>=0x204 for ip,dest in calls if dest==0x6bd4),'score tail moved before rendering'
    values=[1,0,0,255,0,3,0,16,11,24,0,0]+[0,0,0,0,0,0,3,0]+[0]*24
    o=ScoreOriginal(target);o.seed(values)
    before=bytes(o.u.mem_read(0x85a22,440*26));wanted=o.execute('U')
    assert o.read(0xbcba,'B')[0]==20 and o.u.mem_read(0x9000b,1)[0]==4,'original score did not extend'
    assert bytes(o.u.mem_read(0x85a22,440*26))==before,'score tail rewrote already-rendered bullets'
    fixture=out/'extend-order-fixture.txt';fixture.write_text('U '+' '.join(map(str,values))+'\n')
    got=subprocess.run([str(exe.resolve()),'--vectors',str(fixture)],capture_output=True,text=True,check=True).stdout.strip()
    assert got==wanted,'extend owner differs'
    return dict(gameplay_extent='0AAF:0098..0213',extent_sha256=sha(body),calls=calls,
                render_call=[0x13c,0x81f5],score_call=[0x204,0x6bd4],score_load='2000',
                before_clear=0,after_clear=20,before_lives=3,after_lives=4,bullet_pool_unchanged=True,
                score_record=wanted,native_sha256=sha(exe.read_bytes()),
                limits='Target static order plus original score owner with explicit resident/HUD/audio adapters. Full gameplay loop not executed.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','exe','setup-exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--hdi',type=Path)
    p.add_argument('--score-exe',type=Path)
    p.add_argument('--limit',type=int);a=p.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
    target=a.target.read_bytes();inputs=list(itertools.islice(fixtures(),a.limit)) if a.limit else list(fixtures())
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(' '.join(map(str,f)) for f in inputs)+'\n')
    trace=out/'native.txt'
    with trace.open('wb') as output:subprocess.run([str(a.exe.resolve()),'--vectors',str(fixture)],stdout=output,check=True)
    setup_results=None;count=0
    for load in (0x1000,0x2000):
        o=Original(target,load)
        pairs=[setup(o,i) for i in range(256)]
        if setup_results:assert pairs==setup_results,'Extra setup load metamorphism differs'
        setup_results=pairs
        with trace.open() as native,gzip.open(out/f'original-{load:04x}.txt.gz','wt') as original:
            count=0
            for count,want in enumerate(records(o,inputs),1):
                got=' '.join(native.readline().split())
                if got!=want:
                    w,g=want.split(),got.split();at=next((i for i,(x,y) in enumerate(zip(w,g)) if x!=y),min(len(w),len(g)))
                    (out/'mismatch.json').write_text(json.dumps(dict(record=count,field=at,expected=w,actual=g),indent=2)+'\n')
                    raise ValueError(f'Extra record{count} field{at} differs at load{load:04x}')
                original.write(want+'\n')
            assert not native.read(),'extra native records'
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            cs=u.reg_read(UC_X86_REG_CS)
            if (cs+self.delta,address-cs*16)==(0x33a9,0xebc):raise ValueError('injected Extra callback rejection')
            super().body(u,address,size,unused)
    rejected=Rejecting(target);seed(rejected,inputs[0])
    try:rejected.call_args(0xebc,far=True)
    except RuntimeError:
        assert isinstance(rejected.error,ValueError),'callback rejected for another reason'
    else:raise ValueError('Extra callback rejection was swallowed')
    setup_fixture=out/'setup-fixtures.txt';setup_fixture.write_text('\n'.join(x for x,_ in setup_results)+'\n')
    got=subprocess.run([str(a.setup_exe.resolve()),'--extra-setup-vectors',str(setup_fixture)],capture_output=True,text=True,check=True).stdout.splitlines()
    assert got==[x for _,x in setup_results],'Extra retained setup differs'
    negative=got.copy();fields=negative[0].split();state=bytearray.fromhex(fields[3]);state[12:14]=struct.pack('<H',60000);fields[3]=state.hex();negative[0]=' '.join(fields)
    assert negative!=got,'Extra activation comparator missed mutation'
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
    trace_sha=sha(trace.read_bytes())
    with trace.open('rb') as source,gzip.open(out/'native.txt.gz','wb') as dest:
        for b in iter(lambda:source.read(1024*1024),b''):dest.write(b)
    trace.unlink()
    tiny=raw_tiny(target,a.hdi,a.exe,out) if a.hdi else None
    order=extend_order(target,a.score_exe,out) if a.score_exe else None
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest,'source changed during raw tiny controls'
    receipt=dict(passed=True,target_sha256=sha(target),source_manifest_sha256=manifest,native_sha256=sha(a.exe.read_bytes()),setup_native_sha256=sha(a.setup_exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=trace_sha,cases=len(inputs),records=count,setup_cases=256,loads=['1000','2000'],full_fixture_set=not bool(a.limit),negative_comparator=True,callback_rejection=True,raw_tiny=tiny,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,limits='Explicit resource/item/sound/sprite-pixel and DS/SS adapters. Entire22-byte actor/template/440x26 pool, parameter, shared cursor, ordered events and render geometry. Retained midboss-only sequences omit other actor updates; live frontend validation separate. No Mugetsu/Gengetsu/full Extra/player survival/GUI timing/audio/DOS exact claim.')
    receipt['extend_render_order']=order
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ('scope','limits','raw_tiny','extend_render_order')}))
if __name__=='__main__':main()
