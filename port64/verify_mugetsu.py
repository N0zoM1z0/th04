#!/usr/bin/env python3
"""Independent original Mugetsu core/transition/pattern controls at two loads.

Actual MAIN13A9:459F..4F5E, shared hit/explosion/bonus/gather/RNG/tune/add
execute. Shot damage and downstream circle/HUD/item/point/sound are request
adapters. Retained sequences advance only the boss until the Gengetsu dialog
gate; they omit ordinary gameplay and rendering. No full Extra acceptance.
"""
import argparse,gzip,hashlib,itertools,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_kurumi import Original as Base
from verify_orange import initialize as base_initialize,boss as boss_bytes
from verify_extra import LegacyView,Original as Relocated
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
TRANSITIONS=(0x462b,0x469a,0x478e)
ATTACKS=(0x4884,0x48fa,0x49ce,0x4a1c,0x4ac6,0x4b54,0x4bc5)
class Original(Base):
    def __init__(self,target,load=0x2000):
        self.delta=0x2000-load;self.error=None;super().__init__(target)
        if self.delta:
            at=struct.unpack_from('<H',target,24)[0]
            for i in range(1136):
                off,seg=struct.unpack_from('<HH',target,at+i*4);site=seg*16+off
                struct.pack_into('<H',self.module,site,(struct.unpack_from('<H',self.module,site)[0]-self.delta)&65535)
            self.u.mem_write(load*16,bytes(self.module))
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as e:self.error=e;u.emu_stop()
    def body(self,u,address,size,unused):
        Base.body(self,LegacyView(u,self.delta),address+self.delta*16,size,unused)
    call_args=Relocated.call_args

def fixture(op='U',steps=1,phase=2,clock=0,mode=0,frame=0,damage=0,density=0,
            sprite=128,hp=9400,end=3700,cycle=0,transition=0,inv=0,bombing=0,
            anchor=(3072,1280),selector=0,power=64):
    s=boss_bytes(phase,clock,mode,hp,end,3072,1280,2);s[14]=sprite
    return [op,steps,4,16,frame,power,damage,density,1,*s,*[(i*17+9)&255 for i in range(16)],
            *anchor,113,cycle,37,inv,transition,0,12345,100,bombing,selector]
def fixtures():
    clocks=(-32768,-1,0,1,15,16,17,23,24,25,26,28,30,31,32,33,34,35,36,38,40,42,44,46,47,48,49,63,64,65,127,128,129,143,144,145,191,192,193,2999,3000,3999,4000,32767)
    for trans,clock,sprite,frame in itertools.product(range(3),clocks,(0,23,24,128),(0,1)):
        yield fixture('T',transition=trans,clock=clock,sprite=sprite,frame=frame)
    for attack,trans,clock in itertools.product(range(7),range(3),clocks):
        yield fixture('P',selector=attack,transition=trans,clock=clock,frame=clock&65535)
    for phase,clock,damage in itertools.product((0,1,3,4,5,6,7,254),clocks,(0,19,256)):
        yield fixture(phase=phase,clock=clock,damage=damage,frame=clock&65535,sprite=4 if phase==254 else 128)
    for mode,clock,cycle,damage in itertools.product((0,1,2,3,4,5,6,7,255),(0,16,17,24,25,48,64,128,144),(0,31,32,35,36,255),(0,19)):
        if (mode+clock+cycle+damage)%5==0:yield fixture(mode=mode,clock=clock,cycle=cycle,damage=damage,hp=3701,frame=1)
    for inv,bombing,sprite,damage in itertools.product((0,1,2,31,32,255),(0,1),(0,128,130,131,255),(0,255,256,65535)):
        yield fixture(phase=6,clock=3999,inv=inv,bombing=bombing,sprite=sprite,damage=damage)
    for attack,density in itertools.product(range(7),(1,2)):
        yield fixture('A',steps=192,selector=attack,density=density,transition=2)
    for damage in (0,19):yield fixture('S',steps=12000,phase=0,damage=damage)

def initialize(o,row):
    base_initialize(o,row[:49]);o.error=None;o.write(0xbcf0,'hh',384,768)
    x,y,offset,cycle,flash,inv,trans,vm,mid,tone,bombing,selector=row[49:]
    o.write(0x46aa,'hhBB',x,y,cycle,inv);o.write(0x46a6,'B',flash);o.write(0x1eb2,'h',offset)
    o.write(0x46a8,'H',TRANSITIONS[trans]);o.write(0x4646,'HH',*((0x11c0,0x2aaf-o.delta) if vm else (0x4567,0x1234)))
    o.write(0x53c0,'h',mid);o.write(0x3a4,'h',tone);o.write(0x4368,'B',bombing);o.write(0xbcb7,'BB',0,0);o.write(0x53a0,'B',1)
    o.write(0x5394,'B',6)
def checkpoint(o,returned):
    bg=o.read(0x426c,'H')[0];background={0:0,0x7e89:4,0x20c8:2}
    assert bg in background,f'unknown Mugetsu background{bg:04x}'
    vm=o.read(0x4646,'HH');assert vm in ((0x11c0,0x2aaf-o.delta),(0x4567,0x1234))
    private=struct.pack('<3h4B',*o.read(0x46aa,'hh'),*o.read(0x1eb2,'h'),*o.read(0x46ae,'B'),*o.read(0x46a6,'B'),*o.read(0x46af,'B'),TRANSITIONS.index(o.read(0x46a8,'H')[0]))
    values=[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0xbcf0,'hh'),*o.read(0x4642,'hh'),*o.read(0x23ed,'B'),*o.read(0x2a82,'3B'),*o.read(0x5393,'B'),*o.read(0x4252,'B'),*o.read(0xba8a,'B'),*o.read(0x4662,'B'),background[bg],*o.read(0x427e,'hh'),*o.read(0x5390,'H'),*o.read(0xbcca,'B'),*o.read(0x988,'B'),*o.read(0x435a,'I'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,16*42).hex(),o.u.mem_read(0x853e2,96*16).hex(),*o.read(0x41f4,'H'),o.u.mem_read(0x84298,48).hex(),private.hex(),*o.read(0x3a4,'h'),int(vm==(0x11c0,0x2aaf-o.delta)),*o.read(0x53c0,'h'),*o.read(0xbcb7,'BB'),returned,len(o.events),*itertools.chain.from_iterable(o.events)]
    assert o.read(0x1b5c,'B')==(0,),'boss hit flag leaked'
    return ' '.join(map(str,values))
def records(o,rows):
    for row in rows:
        initialize(o,row)
        for tick in range(row[1]):
            frame=(row[4]+tick)&65535;o.events=[];o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16);returned=0
            if row[0]=='T':o.call_args(TRANSITIONS[row[55]]);returned=o.u.reg_read(UC_X86_REG_AX)&255
            elif row[0] in ('P','A'):o.call_args(ATTACKS[row[-1]])
            else:o.call_args(0x4c5b,far=True)
            yield checkpoint(o,returned)
            if row[0]=='S' and o.read(0x53d9,'B')[0]==255:break
            if row[0]=='A':o.write(0x53da,'h',((o.read(0x53da,'h')[0]+1+32768)%65536)-32768)
        if row[0]=='S':assert o.read(0x53d9,'B')[0]==255,'Mugetsu sequence missed Gengetsu gate'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--limit',type=int);p.add_argument('--reference-dir',type=Path);a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0];target=a.target.read_bytes()
    assert len(target)==156258 and sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b','MAIN target identity differs'
    rows=list(itertools.islice(fixtures(),a.limit)) if a.limit else list(fixtures());fixture=out/'fixtures.txt';fixture.write_text('\n'.join(' '.join(map(str,r)) for r in rows)+'\n')
    ref=json.loads((a.reference_dir/'receipt.json').read_text()) if a.reference_dir else None
    if ref:
        assert ref['passed'] and ref['full_fixture_set'] and ref['target_sha256']==sha(target) and not a.limit
        assert ref['fixture_sha256']==sha(fixture.read_bytes()),'Mugetsu retained fixtures differ'
    class Rejecting(Original):
        def body(self,u,address,size,unused):raise ValueError('injected Mugetsu hook rejection')
    for load in (0x1000,0x2000):
        bad=Rejecting(target,load)
        try:bad.call_args(0x4c5b,far=True)
        except RuntimeError as e:assert isinstance(e.__cause__,ValueError),'Mugetsu callback cause lost'
        else:raise ValueError('Mugetsu callback rejection swallowed')
    count=0;digest=None
    for load in (0x1000,0x2000):
        h=hashlib.sha256();o=Original(target,load) if not ref else None;trace_path=out/f'original-{load:04x}.txt.gz';source=gzip.open(a.reference_dir/f'original-{load:04x}.txt.gz','rt') if ref else None
        trace=gzip.open(trace_path,'wt',compresslevel=1) if not ref else None
        proc=subprocess.Popen([str(a.exe.resolve()),'--vectors',str(fixture)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        native=gzip.open(out/'native.txt.gz','wt',compresslevel=1) if load==0x1000 else None
        try:
            wants=source if ref else records(o,rows)
            for count,want in enumerate(wants,1):
                want=' '.join(want.split());raw=proc.stdout.readline();got=' '.join(raw.split());line=want+'\n';h.update(raw.encode())
                if got!=want:
                    x,y=want.split(),got.split();field=next((i for i,(v,w) in enumerate(zip(x,y)) if v!=w),min(len(x),len(y)))
                    (out/'mismatch.json').write_text(json.dumps(dict(record=count,field=field,expected=x,actual=y),indent=2)+'\n');raise ValueError(f'Mugetsu record{count} field{field} differs at load{load:04x}')
                if trace:trace.write(line)
                if native:native.write(raw)
            assert not proc.stdout.read(),'extra Mugetsu native records';err=proc.stderr.read();assert proc.wait()==0,err
        finally:
            if proc.poll() is None:proc.kill();proc.wait()
            if source:source.close()
            if trace:trace.close()
            if native:native.close()
        assert digest is None or digest==h.hexdigest(),'Mugetsu load invariance differs'
        digest=h.hexdigest()
        if ref:assert digest==ref['trace_sha256'] and count==ref['records'],'Mugetsu original reference digest differs'
        print(f'Mugetsu load{load:04x}: PASS records{count}',flush=True)
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
    receipt=dict(passed=True,cases=len(rows),records=count,loads=['1000','2000'],full_fixture_set=not bool(a.limit),original_cpu_reexecuted=not bool(ref),callback_rejection_passed=True,source_manifest=manifest,target_sha256=sha(target),exe_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=digest,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    if ref:receipt['original_producer_receipt_sha256']=sha((a.reference_dir/'receipt.json').read_bytes());receipt['original_producer_source_manifest']=ref['source_manifest']
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
