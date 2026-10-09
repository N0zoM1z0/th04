#!/usr/bin/env python3
"""Original Gengetsu foreground at two loads versus maintained ordered draws.

MAIN0AAF:846F..85FC, common explosion state and full laser render producer
execute. Sprite/wave/zoom/color/geometry and common explosion video disable
are adapters; no whole-scene pixel or complete Extra acceptance.
"""
import argparse,gzip,hashlib,itertools,json,struct,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path.cwd()/'port64'))
from verify_mugetsu_graphics import Original as Base
from verify import source_manifest
from verify_orange_render import explosion,renders
from verify_orange import boss
from verify_lasers import beam
from unicorn.x86_const import *
import unicorn
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference-dir',type=Path);a=p.parse_args()
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0]
    target=a.target.read_bytes()
    ref=json.loads((a.reference_dir/'receipt.json').read_text()) if a.reference_dir else None
    if ref:assert ref['passed'] and ref['target_sha256']==sha(target) and ref['cases']==3458
    assert sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
    def row(phase=2,clock=0,mode=0,sprite=130,damage=0,angle=73,frame=0,amp=0,adjacent=37,flash=255,inv=32,x=3072,y=1280,e=None,big=0,lasers=None):
        b=boss(phase,clock,mode,x=x,y=y);b[14]=sprite;b[18]=damage;b[20]=angle
        positions=(-32768,-17,-16,-15,-1,0,1,15,16,17,3072,6144,32767,-32000,32000,4096)
        columns=list(itertools.chain.from_iterable(struct.pack('<2Bhh20B',i*11+9&255,i*17+19&255,pos,32000-i*117,*[(i*19+j*7+3)&255 for j in range(20)]) for i,pos in enumerate(positions)))
        return [frame,big,73,0,*b,*range(16),amp,adjacent,flash,inv,*(e or [*explosion(),*explosion(),*explosion()]),*columns,*itertools.chain.from_iterable(lasers or [beam(flag=1),beam(),beam()])]
    rows=[]
    for phase,sprite,damage,amp,flash,inv in itertools.product((0,2,5,253,254,255),(0,4,31,128,130,255),(0,1,255),(0,1,64,80,128,255),(0,1,254,255),(0,1,2,31,32,255)):
        if (phase+sprite+damage+amp+flash+inv)%17==0:rows.append(row(phase=phase,sprite=sprite,damage=damage,amp=amp,flash=flash,inv=inv))
    for angle,amp in itertools.product(range(256),(0,1,64,255)):
        rows.append(row(angle=angle,amp=amp,adjacent=angle))
    for phase,mode,clock,frame in itertools.product((4,5,6),(0,1,2),(-32768,-1,31,32,33,95,96,97,32767),(0,1)):
        rows.append(row(phase=phase,mode=mode,clock=clock,frame=frame))
    for x,y,amp,inv in itertools.product((-32768,-17,-16,-1,0,6144,32767),(-32768,-17,-16,-1,0,5888,32767),(0,64),(0,32)):
        rows.append(row(x=x,y=y,amp=amp,inv=inv))
    for flag,radius,color in itertools.product((0,1,2,4,5,128,255),(-32768,-1,0,1,8,16,180,32767),(0,8,15,255)):
        rows.append(row(lasers=[beam(flag=1),beam(flag=flag,radius=radius,color=color),beam(flag=1,x=3200,marker=73)]))
    for r in renders():rows.append(row(e=r[44:92],big=r[1]))
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(' '.join(map(str,r)) for r in rows)+'\n')
    class Original(Base):
        def __init__(self,target,load):
            super().__init__(target,load);self.columns_started=False;self.in_laser=False
            self.u.hook_add(unicorn.UC_HOOK_INSN,self.out,None,1,0,UC_X86_INS_OUT)
        def out(self,u,port,size,value,unused):
            try:
                assert (port,size,value)==(0x7c,1,0),'unexpected foreground port'
                # Shared explosion RMW disable is a hardware adapter, as in the
                # accepted Orange/Yuuka request vocabulary. Retain the laser's
                # explicit final disable request separately.
                if not self.in_laser:return
                self.render_draws.append([9,0,0,0,0,0,0,0,0,0,0])
            except Exception as e:self.error=e;u.emu_stop()
        def body(self,u,address,size,unused):
            actual=u.reg_read(UC_X86_REG_CS);cs=actual+self.delta;ip=address-actual*16;sp=u.reg_read(UC_X86_REG_SP)
            if (cs,ip)==(0x2aaf,0x37d3):self.in_laser=True
            if (cs,ip)==(0x2aaf,0x3970):self.in_laser=False
            def ret(n,far=True):
                words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2));u.reg_write(UC_X86_REG_SP,sp+n)
                if far:u.reg_write(UC_X86_REG_CS,words[1])
                u.reg_write(UC_X86_REG_IP,words[0])
            if cs==0x2000:
                if ip==0x3fd0:
                    angle,amp,length,pat,y,x=struct.unpack('<HHhHhh',u.mem_read(0x70000+sp+4,12));self.render_draws.append([11,x,y,pat,0,0,0,0,length,amp,angle]);ret(16);return
                if ip==0x31a2:
                    zoom,pat,y,x=struct.unpack('<HHhh',u.mem_read(0x70000+sp+4,8));self.render_draws.append([10,x,y,pat,0,0,0,zoom,0,0,0]);ret(12);return
                if ip==0x1744:
                    color,mode=struct.unpack('<HH',u.mem_read(0x70000+sp+4,4));self.color=color;self.render_draws.append([5,0,0,0,color,0,0,mode,0,0,0]);ret(8);return
                if ip==0x1774:
                    bottom,top,x=struct.unpack('<3h',u.mem_read(0x70000+sp+4,6));self.render_draws.append([8,x,top,0,self.color,0,bottom,0,0,0,0]);ret(10);return
                if ip==0x114c:
                    radius,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));self.render_draws.append([6,x,y,radius,self.color,0,0,0,0,0,0]);ret(10);return
                if ip==0x107c:
                    bottom,right,top,left=struct.unpack('<4h',u.mem_read(0x70000+sp+4,8));self.render_draws.append([7,left,top,0,self.color,right,bottom,0,0,0,0]);ret(12);return
            if (cs,ip)==(0x2aaf,0x1666) and struct.unpack('<H',u.mem_read(0x70000+sp,2))[0]==0x85bb:
                self.columns_started=True;ret(2,False);return
            if (cs,ip)==(0x2aaf,0x1672) and self.columns_started:
                self.color=(u.reg_read(UC_X86_REG_AX)>>8)&255;self.render_draws.append([5,0,0,0,self.color,0,0,192,0,0,0]);ret(2,False);return
            super().body(u,address,size,unused)
    def expected(o,r):
        o.reset();o.error=None;o.callback_error=None;o.render_draws=[];o.color=0;o.columns_started=False;o.in_laser=False
        frame,big,tone,changed=r[:4];o.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
        o.u.mem_write(0x853ca,bytes(r[4:28]));o.u.mem_write(0x8bcde,bytes(r[28:44]));o.write(0x24b8,'2B',*r[44:46]);o.write(0xbd18,'B',r[46]);o.write(0x46af,'B',r[47]);o.u.mem_write(0x84298,bytes(r[48:96]));o.u.mem_write(0x8b204,bytes(r[96:512]));o.u.mem_write(0x842d8,bytes(r[512:584]));o.write(0x18d8,'h',big);o.write(0x3a4,'h',tone);o.write(0x5393,'B',changed)
        o.call_args(0x846f,cs=0x2aaf)
        assert bytes(o.u.mem_read(0x8b204,416))==bytes(r[96:512]),'columns mutated during render'
        assert bytes(o.u.mem_read(0x842d8,72))==bytes(r[512:584]),'lasers mutated during render'
        assert o.read(0x24b8,'2B')==tuple(r[44:46]),'wave amplitude word mutated'
        draws=[d+[0]*6 if len(d)==5 else d for d in o.render_draws];assert all(len(d)==11 for d in draws)
        return ' '.join(map(str,[bytes(o.u.mem_read(0x84298,48)).hex(),*o.read(0x18d8,'h'),*o.read(0x3a4,'h'),*o.read(0x5393,'B'),*o.read(0x53dc,'B'),*o.read(0x53de,'B'),*o.read(0xbd18,'B'),len(draws),*itertools.chain.from_iterable(draws)]))
    class Rejecting(Original):
        def body(self,u,address,size,unused):raise ValueError('injected Gengetsu foreground rejection')
    for load in (0x1000,0x2000):
        bad=Rejecting(target,load)
        try:bad.call_args(0x846f,cs=0x2aaf)
        except RuntimeError as e:assert isinstance(e.__cause__,ValueError)
        else:raise ValueError('foreground hook rejection swallowed')
    if ref:assert ref['fixture_sha256']==sha(fixture.read_bytes()),'foreground fixtures differ'
    digest=None
    for load in (0x1000,0x2000):
        o=Original(target,load);h=hashlib.sha256()
        reference=gzip.open(a.reference_dir/f'original-{load:04x}.txt.gz','rt') if ref else None
        trace=gzip.open(out/f'original-{load:04x}.txt.gz','wt',compresslevel=1) if not ref else None
        try:
            with subprocess.Popen([str(a.exe.resolve()),'--foreground-vectors',str(fixture)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) as proc:
                for i,r in enumerate(rows):
                    want=reference.readline().rstrip('\n') if ref else expected(o,r)
                    got=' '.join(proc.stdout.readline().split())
                    if not want or want!=got:
                        (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=r,expected=want.split(),actual=got.split()),indent=2)+'\n');proc.kill();raise ValueError(f'Gengetsu foreground case{i} differs')
                    if trace:trace.write(want+'\n')
                    h.update((want+'\n').encode())
                assert not proc.stdout.read(),'extra foreground record';error=proc.stderr.read();assert proc.wait()==0,error
                if reference:assert not reference.read(),'extra original foreground record'
        finally:
            if reference:reference.close()
            if trace:trace.close()
        if ref:assert h.hexdigest()==ref['trace_sha256'],'foreground reference digest differs'
        assert digest is None or digest==h.hexdigest(),'foreground load differs';digest=h.hexdigest();print(f'Gengetsu foreground load{load:04x} PASS cases{len(rows)}',flush=True)
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest,'source changed during foreground comparison'
    receipt=dict(passed=True,cases=len(rows),loads=['1000','2000'],trace_sha256=digest,fixture_sha256=sha(fixture.read_bytes()),target_sha256=sha(target),source_manifest=manifest,exe_sha256=sha(a.exe.read_bytes()),original_cpu_reexecuted=not bool(ref),callback_rejection_passed=True,utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    if ref:receipt.update(original_producer_receipt_sha256=sha((a.reference_dir/'receipt.json').read_bytes()),original_producer_source_manifest=ref.get('source_manifest'),original_producer_candidate_sha256=ref.get('candidate_sha256'))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
