#!/usr/bin/env python3
"""Original Gengetsu full core/pattern/wave/column/laser state controls at two loads.

MAIN13A9:BE5E..CC5B and shared laser/hit/RNG/tune/add/gather/explosion/score
execute. Shot damage and circle/HUD/item/point/sound consumers are adapters.
Retained sequences omit gameplay and foreground rendering. Complete pools and
column padding compare; phase255 is the post-dialog gate, not full Extra.
"""
import argparse,gzip,hashlib,itertools,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_mugetsu import Original
from verify_orange import initialize as base_initialize,boss as boss_bytes
from verify_lasers import beam
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
ATTACKS=(0xc01a,0xc067,0xc0f6,0xc1b6,0xc2a0,0xc36e,0xc3da,0xc44f,0xc5c0,0xc626,0xc705,0xc7ab)
OPERATIONS=dict(G=0xbe73,W=0xbeea,B=0xbf35,T=0xbfa3,H=0xc772)
def fixture(op='U',steps=1,phase=2,clock=0,mode=0,frame=0,damage=0,density=0,
            sprite=128,hp=18700,end=14700,patterns=0,amplitude=0,inv=0,bombing=0,
            target=3072,selector=0,power=64,player=(3072,5120),beams=0,x=3072,y=1280):
    s=boss_bytes(phase,clock,mode,hp,end,x,y,patterns);s[14]=sprite
    return [op,steps,4,16,frame,power,damage,density,1,*s,*[(i*17+9)&255 for i in range(16)],
            target,amplitude,37,inv,100,bombing,selector,*player,beams]
def fixtures():
    clocks=(-32768,-1,0,1,7,8,9,15,16,31,32,33,47,48,49,50,51,52,63,64,65,79,80,81,127,128,129,143,144,145,1499,1500,2999,3000,3001,4999,5000,32767)
    for op,clock,sprite,frame in itertools.product(('G','T'),clocks,(0,31,32,128),(0,1)):
        yield fixture(op,clock=clock,sprite=sprite,frame=frame)
    for op,clock,x,target,amplitude in itertools.product(('W','B'),(0,1,32,33,63,64,65,127,128,129),(-32768,0,3072,3088,32767),(-32768,3072,32767),(0,63,255)):
        if (clock+x+target+amplitude)%7==0:yield fixture(op,clock=clock,x=x,target=target,amplitude=amplitude)
    for inv,amplitude,sprite,damage in itertools.product((0,1,31,32,255),(0,1,64,255),(0,31,128,255),(0,19,255,256,65535)):
        yield fixture('H',inv=inv,amplitude=amplitude,sprite=sprite,damage=damage,hp=14701)
    for attack,clock,frame in itertools.product(range(12),clocks,(0,1,8)):
        yield fixture('P',selector=attack,clock=clock,frame=frame)
    for phase,clock,damage in itertools.product((0,1,6,7,8,9,254),clocks,(0,19,256)):
        yield fixture(phase=phase,clock=clock,damage=damage,frame=clock&65535,sprite=4 if phase==254 else 128)
    for phase,mode,clock,patterns,damage in itertools.product((2,3,4,5),(0,1,255),(0,1,32,64,80,128,144),(0,17,18,21,22,255),(0,19)):
        if (phase+mode+clock+patterns+damage)%4==0:yield fixture(phase=phase,mode=mode,clock=clock,patterns=patterns,damage=damage,hp=14701,frame=clock&65535)
    for phase,bombing,inv,amplitude,sprite,damage in itertools.product((0,8),(0,1),(0,1,31,32,255),(0,1,64,255),(0,128,255),(0,255,256)):
        if (phase+bombing+inv+amplitude+sprite+damage)%5==0:yield fixture(phase=phase,bombing=bombing,inv=inv,amplitude=amplitude,sprite=sprite,damage=damage,clock=4999)
    for attack,density,beams in itertools.product(range(12),(0,1,2),(0,1,2)):
        yield fixture('A',steps=160,selector=attack,density=density,beams=beams,clock=1)
    for phase,player,beams in itertools.product((2,3,4,5),((-32768,32767),(0,0),(6144,5120)),range(3)):
        yield fixture(phase=phase,mode=255,clock=1,patterns=1,player=player,beams=beams)
    for damage in (0,19):yield fixture('S',steps=30000,phase=0,damage=damage)
def initialize(o,row):
    base_initialize(o,row[:49]);o.error=None;o.write(0xbcf0,'hh',384,768)
    target,amplitude,flash,inv,tone,bombing,selector,x,y,density=row[49:]
    o.context(4,16,0,x,y);o.write(0xbd18,'B',flash);o.write(0x24b8,'B',amplitude);o.write(0xbd1a,'h',target);o.write(0x46af,'B',inv)
    o.write(0x3a4,'h',tone);o.write(0x4368,'B',bombing);o.write(0xbcb7,'BB',0,0);o.write(0x5394,'B',6);o.write(0x5390,'H',3)
    columns=b''.join(struct.pack('<2Bhh20B',i*11+9&255,i*17+19&255,-32000+i*113,32000-i*117,*[(i*19+j*7+3)&255 for j in range(20)]) for i in range(16));o.u.mem_write(0x8b204,columns)
    scratch=beam(flag=1,clock=0,radius=1,speed=1,maximum=64,line=32,hold=48,x=2048,y=1024,marker=201)
    first=beam(flag=1 if density==1 else 3 if density==2 else 0,clock=31 if density==2 else 19,radius=16 if density==2 else 1,marker=19)
    second=beam(flag=1 if density==1 else 0,marker=71);o.u.mem_write(0x842d8,bytes(scratch+first+second));o.write(0x4669,'B',0)
def checkpoint(o,returned,flash):
    # The shared prefix is read independently from actual DS; exclude the
    # Mugetsu-private suffix without initializing its callbacks or state.
    bg=o.read(0x426c,'H')[0];assert bg in (0,0x7e89,0x20c8)
    values=[o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),*o.read(0xbcf0,'hh'),*o.read(0x4642,'hh'),*o.read(0x23ed,'B'),*o.read(0x2a82,'3B'),*o.read(0x5393,'B'),*o.read(0x4252,'B'),*o.read(0xba8a,'B'),*o.read(0x4662,'B'),{0:0,0x7e89:4,0x20c8:2}[bg],*o.read(0x427e,'hh'),*o.read(0x5390,'H'),*o.read(0xbcca,'B'),*o.read(0x988,'B'),*o.read(0x435a,'I'),*o.read(0x3ecc,'H'),*o.read(0xbcba,'B'),*o.read(0xbcb9,'B'),o.u.mem_read(0x853a2,18).hex(),o.u.mem_read(0x85a22,440*26).hex(),o.u.mem_read(0x89586,14).hex(),o.u.mem_read(0x89292,16*42).hex(),o.u.mem_read(0x853e2,96*16).hex(),*o.read(0x41f4,'H'),o.u.mem_read(0x84298,48).hex(),struct.pack('<hBBB',*o.read(0xbd1a,'h'),*o.read(0x24b8,'B'),*o.read(0xbd18,'B'),*o.read(0x46af,'B')).hex(),o.u.mem_read(0x8b204,16*26).hex(),o.u.mem_read(0x842d8,72).hex(),*o.read(0x4669,'B'),*o.read(0x3a4,'h'),*o.read(0x18d8,'h'),*o.read(0xbcb7,'BB'),returned,len(o.events),*itertools.chain.from_iterable(o.events)]
    assert o.read(0x1b5c,'B')==(0,),'Gengetsu hit flag leaked'
    return ' '.join(map(str,values))
def records(o,rows):
    for row in rows:
        initialize(o,row)
        for tick in range(row[1]):
            frame=(row[4]+tick)&65535;o.events=[];o.write(0x538a,'H',frame);o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16);returned=0
            if row[0] in OPERATIONS:
                o.call_args(OPERATIONS[row[0]]);returned=o.u.reg_read(UC_X86_REG_AX)&255 if row[0] in ('W','B','T','H') else 0
            elif row[0] in ('P','A'):o.call_args(ATTACKS[row[55]])
            else:o.call_args(0xc7da,far=True)
            yield checkpoint(o,returned,row[51])
            if row[0]=='S' and o.read(0x53d9,'B')[0]==255:break
            if row[0]=='A':o.write(0x53da,'h',((o.read(0x53da,'h')[0]+1+32768)%65536)-32768)
        if row[0]=='S':assert o.read(0x53d9,'B')[0]==255,'Gengetsu sequence missed post-dialog gate'
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
        assert ref['fixture_sha256']==sha(fixture.read_bytes()),'Gengetsu retained fixtures differ'
    class Rejecting(Original):
        def body(self,u,address,size,unused):raise ValueError('injected Gengetsu hook rejection')
    for load in (0x1000,0x2000):
        bad=Rejecting(target,load)
        try:bad.call_args(0xc7da,far=True)
        except RuntimeError as e:assert isinstance(e.__cause__,ValueError),'Gengetsu callback cause lost'
        else:raise ValueError('Gengetsu callback rejection swallowed')
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
                    (out/'mismatch.json').write_text(json.dumps(dict(record=count,field=field,expected=x,actual=y),indent=2)+'\n');raise ValueError(f'Gengetsu record{count} field{field} differs at load{load:04x}')
                if trace:trace.write(line)
                if native:native.write(raw)
            assert not proc.stdout.read(),'extra Gengetsu native records';err=proc.stderr.read();assert proc.wait()==0,err
        finally:
            if proc.poll() is None:proc.kill();proc.wait()
            if source:source.close()
            if trace:trace.close()
            if native:native.close()
        assert digest is None or digest==h.hexdigest(),'Gengetsu load invariance differs'
        digest=h.hexdigest()
        if ref:assert digest==ref['trace_sha256'] and count==ref['records'],'Gengetsu original reference digest differs'
        print(f'Gengetsu load{load:04x}: PASS records{count}',flush=True)
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest
    receipt=dict(passed=True,cases=len(rows),records=count,loads=['1000','2000'],full_fixture_set=not bool(a.limit),original_cpu_reexecuted=not bool(ref),callback_rejection_passed=True,source_manifest=manifest,target_sha256=sha(target),exe_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=digest,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    if ref:receipt['original_producer_receipt_sha256']=sha((a.reference_dir/'receipt.json').read_bytes());receipt['original_producer_source_manifest']=ref['source_manifest']
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
