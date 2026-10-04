#!/usr/bin/env python3
"""Pinned original CPU controls for ordinary stage actor reset and Stage2 seed."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_score import Original as Base
from verify import source_manifest
from probe_assets import main_assets
sha=lambda b:hashlib.sha256(b).hexdigest()
CLEAR=((0xb55e,0x132),(0x8a92,0x200),(0x53e2,0x180),(0x5a22,0xb2c),(0xb204,0xd0),(0x9594,0x28),(0xaf34,0xa0),(0x9634,0x640),(0x9292,0xa8))
class Original(Base):
    def __init__(self,target):
        self.clears=[];self.calls=[];self.random_calls=0;super().__init__(target)
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(args=0,far=False):
            off=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0]
            if far:u.reg_write(UC_X86_REG_CS,struct.unpack('<H',u.mem_read(0x70000+sp+2,2))[0])
            u.reg_write(UC_X86_REG_SP,sp+(4 if far else 2)+args);u.reg_write(UC_X86_REG_IP,off)
        if (cs,ip)==(0x2000,0x2172):self.random_calls+=1 # Execute actual process LCG.
        if (cs,ip)==(0x2aaf,0x185e):
            count,dest=struct.unpack('<HH',u.mem_read(0x70000+sp+2,4));self.clears.append((dest,count)) # Execute actual REP STOSD.
        adapters={(0x2000,0x144a):(8,True), # Clipping/hardware.
                  (0x2aaf,0x72f6):(0,True), # Selected firing callback; firing owner uses power directly.
                  (0x33a9,0x486):(0,False), # Item splash graphics pool.
                  (0x2aaf,0x54b4):(0,False), # Bomb lifecycle absent from native actor slice.
                  (0x33a9,0x22e4):(0,True), # Thick laser owner.
                  (0x2aaf,0x11c2):(0,False), # Point popup owner.
                  (0x2aaf,0x4714):(0,True), # Remaining HUD.
                  (0x2aaf,0x203e):(0,False), # Tile hardware invalidation.
                  (0x2000,0x2a74):(4,True), # BFNT request.
                  (0x330e,0x858):(8,True), # Backdrop CDG request.
                  (0x33a9,0xa518):(4,False)} # Boss .BB request.
        if (cs,ip) in adapters:
            self.calls.append((cs,ip));ret(*adapters[cs,ip]);return
        super().body(u,address,size,unused)
    def actors(self,seed,marker,pending,clear,offset,repeats=1):
        self.reset();self.error=None;self.clears=[];self.calls=[];self.random_calls=0
        for at,count in CLEAR:self.u.mem_write(0x80000+at,bytes([255])*count*4)
        for at,fmt,values in ((0x3e2,'<I',[seed]),(0x464e,'<6h',[123,-456,123,-456,-64,0]),(0x4666,'B',[marker]),(0x4362,'B',[marker]),(0x4640,'B',[marker]),(0x42c8,'<H',[marker*257]),(0x42ca,'B',[marker%5]),(0xbcba,'B',[clear]),(0xbcb9,'B',[marker]),(0xbcbc,'<H',[65535]),(0x4252,'B',[marker]),(0x9586,'<4h',[123,-456,123,-456]),(0x41f4,'<H',[offset]),(0x4664,'B',[marker]),(0x466b,'B',[marker]),(0x4676,'B',[marker]),(0xbccc,'<H',[65535]),(0x435a,'<I',[pending]),(0x5395,'B',[marker])):self.write(at,fmt,*values)
        self.u.mem_write(0x84349,bytes([marker])*8);self.u.mem_write(0x84351,bytes([(marker+1)&255])*8);self.u.mem_write(0x81ece,b'\0')
        for stage in range(repeats):
            self.u.reg_write(UC_X86_REG_EAX,0);self.call_args(0x6e0,cs=0x2aaf)
        if self.error:raise RuntimeError('original actor reset adapter rejected') from self.error
        if self.clears!=list(CLEAR)*repeats or self.random_calls!=353*repeats:raise ValueError('original stage clear/random ownership changed')
        # Complete raw target clear extents must now be zero except the96
        # freshly generated spark angle low bytes. This is independent of the
        # selected portable checkpoint below; absent custom/popup consumers
        # are not counted as native implementations.
        for at,count in CLEAR:
            data=bytearray(self.u.mem_read(0x80000+at,count*4))
            if at==0x53e2:
                for i in range(96):data[i*16+14]=0
            if any(data):raise ValueError(f'original stage clear left bytes at{at:04X}')
        values=[]
        for at,fmt in ((0x464e,'<6h'),(0x4666,'B'),(0x42c8,'<H'),(0x42ca,'B'),(0x4362,'B'),(0x4640,'B'),(0xbcba,'B'),(0xbcbc,'<H'),(0xbcb9,'B'),(0x4252,'B'),(0x9586,'<6h2B'),(0x41f4,'<H'),(0x3e2,'<I'),(0xbcce,'B'),(0x4664,'B'),(0x466b,'B'),(0x4676,'B'),(0xbccc,'<H'),(0x435a,'<I'),(0x435a,'<I'),(0x5395,'B')):values.extend(self.read(at,fmt))
        for at in (0x4349,0x4351,0x1ec6):values.extend(self.u.mem_read(0x80000+at,8))
        for i in range(96):values.extend(self.read(0x53e2+i*16+14,'<H'))
        ring=self.u.mem_read(0x83dcc,256)
        for i in range(256):values.append(ring[i]+((255 if i==255 else ring[i+1])<<8))
        if self.read(0x3ecc,'<H')[0]!=0:raise ValueError('stage ring cursor not reset')
        values.append(0)
        return ' '.join(map(str,values))
    def midboss(self,marker):
        self.reset();self.error=None;self.calls=[]
        self.write(0x53b4,'<6hHhBBhBB',123,-456,123,-456,17,-19,99,17,19,marker,marker*257 if marker<128 else marker*257-65536,marker,marker^55);self.write(0x46b2,'B',1)
        self.call_args(0x642c,far=True);self.call_args(0xa623,far=True)
        if self.error:raise RuntimeError('original Stage2 setup adapter rejected') from self.error
        values=list(self.read(0x53b4,'<6hHhBBhBB'))+[self.read(0x46b2,'B')[0]]
        return ' '.join(map(str,values))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--limit',type=int);p.add_argument('--hdi',type=Path)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);original=Original(a.target.read_bytes());manifest,_=source_manifest(Path(__file__).resolve().parents[1]);inputs=[];expected=[]
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            if address==0x2aaf0+0x6e0:raise ValueError('injected stage actor rejection')
            super().body(u,address,size,unused)
    rejected=Rejecting(original.target)
    try:rejected.actors(318,255,12345,20,0x12ff)
    except (RuntimeError,ValueError):
        if not isinstance(rejected.error,ValueError):raise
    else:raise ValueError('original callback rejection silently passed')
    cases=itertools.product((0,318,0x80000000,0xffffffff),(0,1,95,96,97,255),(1,17011721,0xffffffff),(0,20,255),(0,0x12ff,0xffff))
    for row in itertools.islice(cases,a.limit) if a.limit else cases:
        inputs.append('R '+' '.join(map(str,row)));expected.append(original.actors(*row))
    for seed,marker in itertools.product((0,318,0x80000000,0xffffffff),(0,1,95,96,97,255)):
        row=(seed,marker,17011721,20,0x12ff);inputs.append('Q '+' '.join(map(str,row)));expected.append(original.actors(*row,repeats=2))
    reset_cases=len(inputs)
    for marker in range(256):inputs.append('M '+str(marker));expected.append(original.midboss(marker))
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n');trace=out/'trace.txt';trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');actual=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture)],capture_output=True,text=True,check=True,env=env).stdout.splitlines()
    for i,(got,want) in enumerate(itertools.zip_longest(actual,expected)):
        if got!=want:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i],expected=want,actual=got),indent=2)+'\n');raise ValueError(f'stage session case{i} differs')
    live=None
    if a.hdi:
        assets=main_assets(a.hdi);names=('ST00.STD','ST00.MAP','ST01.STD','ST01.MAP')
        for name in names:(out/name).write_bytes(assets[name])
        command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--stage2-actors',*[str(out/name) for name in names]]
        text=subprocess.run(command,capture_output=True,text=True,check=True,env=env).stdout
        if len(text.splitlines())!=4 or text.count('boundary=midboss2_pending')!=4:raise ValueError('missing natural Stage2 actor routes')
        (out/'stage2-actors.txt').write_text(text)
        live=dict(routes=4,stage2_frames=10400,output_sha256=sha(text.encode()),output=text.splitlines(),asset_sha256={name:sha(assets[name]) for name in names},scope='Native integration continues actual Stage1 state after ordinary departure, rejects invalid STD before mutation, preserves awards/process generation, consumes353 next LCG draws, resets actors, loads real Stage2 STD/MAP and stops before its2600 midboss callback. Full original CPU gameplay/resources/render/GUI not claimed.')
    after,_=source_manifest(Path(__file__).resolve().parents[1]);assert manifest==after
    receipt=dict(passed=True,callback_rejection_passed=True,cases=len(inputs),actor_reset_cases=reset_cases,retained_double_resets=24,midboss_seed_cases=256,native_integration=live,source_manifest_sha256=after,target_sha256=sha(original.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='MAIN load2000 CS2AAF DS8000 stage_runtime06E0/stage_state73DB, actual resetShots593A/ring1168/items33A9:9F8B/sparks1824/LCG2000:2172/HUD6BA2; selected actor/persistent-score/gather metadata, all96 spark angles and256 ring samples,353 retained process draws; Stage2 midboss-reset642C/setupA623 owned22-byte seed and active flag. Original complete9 raw clear extents checked independently.',limits='Original EAX upper word initialized0 at REP STOSD entry. Hardware/shot-level/Bomb/splashes/thicklaser/pointnums/remainingHUD adapters intercepted; custom/popup clears checked only in original. Not full stage session/resource/video or midboss2/Kurumi behavior, no DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
