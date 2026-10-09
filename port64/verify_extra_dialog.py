#!/usr/bin/env python3
"""Original Extra script and non-EMS dialog resource boundaries at two loads.

MAIN0AAF:2A7C script,2C39 init and2CFE exit execute. Graphics/input/wait/fade,
file/sprite/CDG and sound consumers are explicit request adapters. This proves
ordered requests and retained script/counter state, not full original video,
EMS allocation, ordinary Extra survival or complete game acceptance.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn.x86_const import *
from verify_dialog import Original as Base
from verify_extra import LegacyView,Original as Relocated
from probe_assets import main_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def __init__(self,target,load):
        self.delta=0x2000-load;self.resources=[];super().__init__(target)
        if self.delta:
            at=struct.unpack_from('<H',target,24)[0]
            for i in range(1136):
                off,seg=struct.unpack_from('<HH',target,at+i*4);site=seg*16+off
                struct.pack_into('<H',self.module,site,(struct.unpack_from('<H',self.module,site)[0]-self.delta)&65535)
            self.u.mem_write(load*16,bytes(self.module))
    call_args=Relocated.call_args
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size)
        except Exception as e:self.error=e;u.emu_stop()
    def body(self,u,address,size):
        actual=u.reg_read(UC_X86_REG_CS);pair=(actual+self.delta,address-actual*16);sp=u.reg_read(UC_X86_REG_SP)
        if pair[0]==0x330e and pair[1] in (0x978,0x91c,0x858):
            count={0x978:1,0x91c:3,0x858:4}[pair[1]];words=struct.unpack('<'+'H'*count,u.mem_read(0x70000+sp+4,count*2))
            if pair[1]==0x978:self.resources.append((0,words[0],'-',0))
            else:
                off,seg,slot=words if pair[1]==0x91c else words[1:]
                name=bytes(u.mem_read(seg*16+off,32)).split(b'\0')[0].decode('ascii')
                self.resources.append((1 if pair[1]==0x91c else 2,slot,name,0 if pair[1]==0x91c else words[0]))
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4+count*2);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off);return
        Base.body(self,LegacyView(u,self.delta),address+self.delta*16,size)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','hdi','resource-exe','dialog-exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0];target=a.target.read_bytes()
    assert len(target)==156258 and sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
    assets=main_assets(a.hdi);script=assets['_DM06.TXT'];(out/'_DM06.TXT').write_bytes(script)
    rows=list(itertools.product(range(2),range(256)));fixtures=out/'resource-fixtures.txt';fixtures.write_text('\n'.join(f'{c} {n}' for c,n in rows)+'\n');first=None;scenes=[]
    for load in (0x1000,0x2000):
        o=Original(target,load);wanted=[]
        class Rejecting(Original):
            def body(self,u,address,size):raise ValueError('injected Extra dialog rejection')
        bad=Rejecting(target,load)
        try:bad.call_args(0x2cfe,cs=0x2aaf)
        except RuntimeError as e:assert isinstance(e.__cause__,ValueError)
        else:raise ValueError('Extra dialog hook rejection swallowed')
        for character,calls in rows:
            o.reset();o.error=None;o.resources=[];o.write(0x5394,'B',6);o.write(0x5398,'B',character);o.write(0x539e,'H',0);o.write(0x188a,'B',calls)
            o.call_args(0x2c39,cs=0x2aaf);o.call_args(0x2cfe,cs=0x2aaf)
            wanted.append(' '.join(map(str,[*o.read(0x188a,'B'),len(o.resources),*itertools.chain.from_iterable(o.resources)])))
        if first is None:first=wanted
        else:assert wanted==first,'Extra resource requests depend on load'
        for held in (0,1):
            o.reset();o.held=held;o.dialog_events=[];o.u.mem_write(0x90000,script+bytes(4));o.write(0x428c,'HH',0,0x9000)
            for i in range(3):o.scene()
            actual=subprocess.run([str(a.dialog_exe.resolve()),'--trace',str(out/'_DM06.TXT'),str(held),'3'],capture_output=True,text=True,check=True).stdout.splitlines()
            assert actual==o.dialog_events,'Extra script requests or retained cursor differ'
            trace='\n'.join(o.dialog_events)+'\n';(out/f'script-{load:04x}-{held}.txt').write_text(trace)
            ends=[e for e in o.dialog_events if e.startswith('END ')]
            assert [int(e.split()[1]) for e in ends]==[987,1736,1961],'Extra scene boundary differs'
            scenes.append(dict(load=f'{load:04x}',held=held,scenes=3,events=len(actual),ends=ends,trace_sha256=sha(trace.encode())))
    native=subprocess.run([str(a.resource_exe.resolve()),'--resource-vectors',str(fixtures)],capture_output=True,text=True,check=True).stdout.splitlines()
    for i,(want,got) in enumerate(itertools.zip_longest(first,native)):
        if want is None or got is None or want.split()!=got.split():
            (out/'resource-mismatch.json').write_text(json.dumps(dict(case=i,fixture=rows[i] if i<len(rows) else None,expected=want,actual=got),indent=2)+'\n');raise ValueError(f'Extra resource case{i} differs')
    trace='\n'.join(first)+'\n';(out/'resource-original.txt').write_text(trace)
    for name in ('ST06.BB1','ST06.BB2','ST06.BB3','BSS6.CD2','BSS7.CD2','BSS8.CD2','_DM06.TXT','KAO0.CD2','KAO1.CD2','BB0.CDG','BB1.CDG'):
        assert name in assets
    resources={name:dict(size=len(assets[name]),sha256=sha(assets[name])) for name in ('ST06.BB1','ST06.BB2','ST06.BB3','BSS6.CD2','BSS7.CD2','BSS8.CD2','_DM06.TXT','KAO0.CD2','KAO1.CD2','BB0.CDG','BB1.CDG')}
    assert source_manifest(root)[0]==manifest
    receipt=dict(passed=True,resource_cases=len(rows),loads=['1000','2000'],scripts=scenes,resources=resources,resource_trace_sha256=sha(trace.encode()),fixture_sha256=sha(fixtures.read_bytes()),source_manifest=manifest,target_sha256=sha(target),hdi_sha256=sha(a.hdi.read_bytes()),resource_exe_sha256=sha(a.resource_exe.read_bytes()),dialog_exe_sha256=sha(a.dialog_exe.read_bytes()),callback_rejection_passed=True,utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
