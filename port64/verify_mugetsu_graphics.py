#!/usr/bin/env python3
"""Independent Mugetsu foreground and shared Extra background request controls.

Original MAIN0AAF:6AC6..6BA2,2D9C,2E65 and7E89..7F1A execute at loads1000/2000.
Sprite/CDG/BB/filler/color and physical video writes are explicit request adapters.
Full explosion/flash/damage/palette state and ordered requests are compared;
this is not a pixel or ordinary Extra gameplay acceptance.
"""
import argparse,gzip,hashlib,itertools,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_orange_render import Original as RenderBase,explosion,renders
from verify_extra import LegacyView,Original as Relocated
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(RenderBase):
    def __init__(self,target,load):
        self.delta=0x2000-load;self.error=None;self.background_events=[];super().__init__(target)
        if self.delta:
            at=struct.unpack_from('<H',target,24)[0]
            for i in range(1136):
                off,seg=struct.unpack_from('<HH',target,at+i*4);site=seg*16+off
                struct.pack_into('<H',self.module,site,(struct.unpack_from('<H',self.module,site)[0]-self.delta)&65535)
            self.u.mem_write(load*16,bytes(self.module))
    call_args=Relocated.call_args
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as e:self.error=e;u.emu_stop()
    def body(self,u,address,size,unused):
        actual=u.reg_read(UC_X86_REG_CS);cs=actual+self.delta;ip=address-actual*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(n,far=False):
            words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2));u.reg_write(UC_X86_REG_SP,sp+n)
            if far:u.reg_write(UC_X86_REG_CS,words[1])
            u.reg_write(UC_X86_REG_IP,words[0])
        if (cs,ip)==(0x330e,0x5d4):
            image,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));self.background_events.append([2,x,y,image]);ret(10,True);return
        if cs==0x2aaf and ip in (0x20c8,0x2068,0x1658,0x1426):
            if ip==0x1426:
                assert self.read(0xba8e,'H')==(0x9abc,),'Extra BB segment copy differs'
                cel=struct.unpack('<H',u.mem_read(0x70000+sp+2,2))[0];self.background_events.append([3,cel,0,0]);ret(4)
            else:self.background_events.append([{0x20c8:0,0x2068:1,0x1658:4}[ip],0,0,0]);ret(2)
            return
        RenderBase.hook_body(self,LegacyView(u,self.delta),address+self.delta*16,size,unused)
def foregrounds():
    from verify_orange import boss
    def row(phase=2,clock=0,sprite=128,damage=0,flash=0,inv=0,x=3072,y=1280,e=None,big=0):
        b=boss(phase,clock,x=x,y=y);b[14]=sprite;b[18]=damage
        return [*b,*range(16),flash,inv,*(e or [*explosion(),*explosion(),*explosion()]),big,73,0]
    for phase,sprite,damage,flash,inv in itertools.product((0,1,2,6,253,254,255),(0,4,128,130,131,255),(0,1,255),(0,1,254,255),(0,1,2,31,32,255)):
        if (phase+sprite+damage+flash+inv)%7==0:yield row(phase=phase,sprite=sprite,damage=damage,flash=flash,inv=inv)
    for x,y,damage,inv in itertools.product((-32768,-17,-16,-1,0,6144,32767),(-32768,-17,-16,-1,0,5888,32767),(0,255),(0,1,32)):
        yield row(x=x,y=y,damage=damage,inv=inv)
    for r in renders():
        # Reuse prior independently bounded common explosion fixtures, preserving
        # their state/metadata; Mugetsu has its own damage flash and invincibility.
        b=r[4:28];b[14]=128
        yield [*b,*r[28:44],37,32,*r[44:92],r[1],r[2],r[3]]
def backgrounds():
    return itertools.product(range(256),(-32768,-65,-64,-63,-4,-3,-1,0,1,2,3,4,7,8,31,32,63,64,1024,32767))
def expected(o,mode,r):
    o.reset();o.error=None;o.callback_error=None;o.render_draws=[];o.background_events=[];o.raw_circle=False;o.color=0
    if mode=='foreground':
        o.u.mem_write(0x853ca,bytes(r[:24]));o.u.mem_write(0x8bcde,bytes(r[24:40]));o.write(0x46a6,'B',r[40]);o.write(0x46af,'B',r[41]);o.u.mem_write(0x84298,bytes(r[42:90]));o.write(0x18d8,'h',r[90]);o.write(0x3a4,'h',r[91]);o.write(0x5393,'B',r[92]);o.call_args(0x6ac6,cs=0x2aaf)
        return ' '.join(map(str,[o.u.mem_read(0x84298,48).hex(),*o.read(0x18d8,'h'),*o.read(0x3a4,'h'),*o.read(0x5393,'B'),*o.read(0x53dc,'B'),*o.read(0x46a6,'B'),len(o.render_draws),*itertools.chain.from_iterable(o.render_draws)]))
    phase,clock=r;o.write(0x53d9,'B',phase);o.write(0x53da,'h',clock);o.write(0xbcee,'H',0x9abc);o.write(0xba8e,'H',0x1234);o.write(0x432c,'H',0x4567);o.write(0xba8c,'H',0x1658);o.call_args(0x7e89,cs=0x2aaf)
    null=o.read(0x432c,'H')[0];assert null==(0x11be if not phase and clock<=2 else 0x4567),'Extra stage renderer mutation differs'
    assert o.read(0xba8e,'H')==((0x9abc,) if phase==1 else (0x1234,)),'Extra BB pointer ownership differs'
    events=([[5,0,0,0]] if null==0x11be else [])+o.background_events
    return ' '.join(map(str,[len(events),*itertools.chain.from_iterable(events)]))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--reference-dir',type=Path);p.add_argument('--limit',type=int);a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);target=a.target.read_bytes();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];controls={}
    assert len(target)==156258 and sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b','MAIN target identity differs'
    ref=json.loads((a.reference_dir/'receipt.json').read_text()) if a.reference_dir else None
    class Rejecting(Original):
        def body(self,u,address,size,unused):raise ValueError('injected Mugetsu graphics rejection')
    for load in (0x1000,0x2000):
        bad=Rejecting(target,load)
        try:bad.call_args(0x6ac6,cs=0x2aaf)
        except RuntimeError as e:assert isinstance(e.__cause__,ValueError)
        else:raise ValueError('Mugetsu graphics rejection swallowed')
    if ref:assert ref['passed'] and ref['target_sha256']==sha(target) and not a.limit
    for mode,rows in [('foreground',foregrounds()),('background',backgrounds())]:
        rows=list(itertools.islice(rows,a.limit) if a.limit else rows);f=out/f'{mode}-fixtures.txt';f.write_text('\n'.join(' '.join(map(str,r)) for r in rows)+'\n');want=out/f'{mode}-original.txt.gz';h=hashlib.sha256();count=0
        if ref:
            assert ref['controls'][mode]['fixture_sha256']==sha(f.read_bytes());want=a.reference_dir/f'{mode}-original.txt.gz'
        else:
            with gzip.open(want,'wt',compresslevel=1) as trace:
                first=None
                for load in (0x1000,0x2000):
                    o=Original(target,load);records=[expected(o,mode,r) for r in rows]
                    if first is None:first=records;trace.write('\n'.join(first)+'\n')
                    else:assert records==first,'Extra graphics load invariance differs'
        command=[str(a.exe.resolve()),'--'+mode+'-vectors',str(f)]
        with subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) as proc,gzip.open(want,'rt') as source:
            for count,w in enumerate(source,1):
                g=proc.stdout.readline();h.update(w.encode())
                if w.split()!=g.split():
                    (out/f'{mode}-mismatch.json').write_text(json.dumps(dict(case=count,input=rows[count-1],expected=w.split(),actual=g.split()),indent=2)+'\n');proc.kill();raise ValueError(f'Extra {mode} case{count} differs')
            assert not proc.stdout.read(),'extra native graphics records';err=proc.stderr.read();assert proc.wait()==0,err
        if ref:assert ref['controls'][mode]['trace_sha256']==h.hexdigest()
        controls[mode]=dict(cases=count,fixture_sha256=sha(f.read_bytes()),trace_sha256=h.hexdigest());print(mode,count,'PASS',flush=True)
    assert source_manifest(root)[0]==manifest
    receipt=dict(passed=True,controls=controls,loads=['1000','2000'],full_fixture_set=not bool(a.limit),original_cpu_reexecuted=not bool(ref),source_manifest=manifest,target_sha256=sha(target),exe_sha256=sha(a.exe.read_bytes()),callback_rejection_passed=True,unicorn_version=__import__('unicorn').__version__,unicorn_engine_sha256=sha(Path(__import__('unicorn').unicorn._uc._name).read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    if ref:receipt['original_producer_receipt_sha256']=sha((a.reference_dir/'receipt.json').read_bytes());receipt['original_producer_source_manifest']=ref['source_manifest']
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
