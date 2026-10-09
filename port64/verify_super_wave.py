#!/usr/bin/env python3
"""Execute original SUPER_WAVE_PUT versus portable complete indexed screens.

MAIN0000:3FD0..40F3 executes at loads1000/2000. No semantic callee is
intercepted. BFNT plane staging and visible A800 GRCG shadows are adapters;
physical page/alias/scroll/pacing and the complete Gengetsu scene are separate.
Patterns have even-byte rows and at most96 lines. Zero wavelength preserves
the target DIV fault as an explicit host rejection.
"""
import argparse,gzip,hashlib,itertools,json,math,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from verify_mugetsu_graphics import Original as Base
from verify_yuuka5_pixels import Shadow,SCREEN
from verify_marisa_pixels import planes
from probe_assets import main_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def __init__(self,target,load):
        super().__init__(target,load)
        # This complete kernel has no external semantic callees. Only the
        # separately installed hardware shadows intercept its execution.
        self.u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16)
        self.u.mem_map(0,0x110000);self.u.mem_write(load*16,bytes(self.module))
    def call_args(self,*args,**kwargs):
        self.error=None;self.callback_error=None
        try:super().call_args(*args,**kwargs)
        except Exception:
            if self.callback_error:raise RuntimeError('wave hardware adapter rejected') from self.callback_error
            raise
        if self.callback_error:raise RuntimeError('wave hardware adapter rejected') from self.callback_error
def fixtures():
    names=('ST06.BB1','ST06.BB2','ST06.BB3')
    for name,image,shift,amp,phase in itertools.product(names,range(8),range(16),(1,16,32,64),(0,1,63,127,128,192,255)):
        if name=='ST06.BB3' and image>=2:continue
        if (image+shift+amp+phase)%31==0:yield [name,image,96+shift,16,80-amp,amp,phase,(image+shift)%16]
    for angle in range(256):yield ['ST06.BB2',angle%8,96+angle%16,16,16,64,angle,angle%16]
    for amp in range(256):
        if amp!=80:yield ['ST06.BB2',amp%8,31+amp%16,-15,80-amp,amp,7,amp%16]
    for x,y in itertools.product((-32768,-17,-16,-1,0,639,32767),(-32768,-15,0,399,32767)):
        yield ['ST06.BB2',0,x,y,17,63,73,(x+y)%16]
    for length,phase,amp in itertools.product((-32768,-80,-1,1,2,80,32767),(0,255,256,65535),(1,128,255)):
        yield ['ST06.BB2',phase%8,97,16,length,amp,phase,amp%16]
    for high in range(16):yield ['ST06.BB2',0,96,16,16,64+high*256,19,13]
def stage(o,row,assets):
    name,image,left,top,length,amp,phase,seed=row
    o.reset();w,height,data=planes(assets[name],image)
    o.write(0x2ac4,'H',0x9000);o.write(0x2ec4,'H',(w//8<<8)|height);o.u.mem_write(0x90000,data)
    return (phase,amp,length,0,top,left)
def expected(o,row,assets):
    args=stage(o,row,assets);shadow=Shadow(o,row[-1])
    try:o.call_args(0x3fd0,args,far=True,cs=0x2000)
    finally:shadow.close()
    return bytes(shadow.screen),shadow.writes,shadow.ports
def rejection(target,assets):
    class Rejecting(Shadow):
        def port(self,u,port,size,value,unused):
            self.o.callback_error=ValueError('injected wave hardware rejection');u.emu_stop()
    zero=[]
    for load in (0x1000,0x2000):
        o=Original(target,load);r=['ST06.BB2',0,96,16,16,64,0,13];args=stage(o,r,assets)
        table=struct.unpack('256b',o.u.mem_read(0x803e6,256))
        generated=tuple((-1 if a>=128 else 1)*min(127,int(128*math.sin((a%128 if a%128<=64 else 128-a%128)*math.pi/128))) for a in range(256))
        assert table==generated,'independent sine generation differs from target'
        shadow=Rejecting(o,13)
        try:
            try:o.call_args(0x3fd0,args,far=True,cs=0x2000)
            except RuntimeError as e:assert isinstance(e.__cause__,ValueError),'wave callback cause lost'
            else:raise ValueError('wave callback rejection swallowed')
        finally:shadow.close()
        stage(o,r,assets)
        try:o.call_args(0x3fd0,(0,64,0,0,16,96),far=True,cs=0x2000)
        except unicorn.UcError as e:assert e.errno==unicorn.UC_ERR_EXCEPTION,'zero wave produced another error';zero.append(load)
        else:raise ValueError('original zero-wave DIV did not fault')
    return zero
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','hdi','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference-dir',type=Path);a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    target=a.target.read_bytes();assert len(target)==156258 and sha(target)=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0];assets=main_assets(a.hdi);rows=list(fixtures());names=('ST06.BB1','ST06.BB2','ST06.BB3')
    for name in names:(out/name).write_bytes(assets[name])
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(' '.join(map(str,[out/r[0],*r[1:]])) for r in rows)+'\n')
    logical='\n'.join(' '.join(map(str,r)) for r in rows)+'\n'
    ref=json.loads((a.reference_dir/'receipt.json').read_text()) if a.reference_dir else None
    if ref:
        assert ref['passed'] and ref['cases']==len(rows) and ref['target_sha256']==sha(target)
        assert ref['asset_sha256']=={n:sha(assets[n]) for n in names},'wave reference assets differ'
        assert [r['input'] for r in ref['records']]==rows,'wave reference fixtures differ'
    zero=rejection(target,assets)
    check=subprocess.run([str(a.exe.resolve()),'--reject-zero',str(out/'ST06.BB2')],capture_output=True,text=True,check=True)
    assert check.stdout.strip()=='Wave zero-length rejection PASS','host zero wave accepted'
    digest=None;records=[]
    for load in (0x1000,0x2000):
        o=Original(target,load);h=hashlib.sha256()
        reference=gzip.open(a.reference_dir/f'original-{load:04x}.bin.gz','rb') if ref else None
        trace=gzip.open(out/f'original-{load:04x}.bin.gz','wb',compresslevel=1) if not ref else None
        try:
            with subprocess.Popen([str(a.exe.resolve()),'--pixel-vectors',str(fixture)],stdout=subprocess.PIPE,stderr=subprocess.PIPE) as proc:
                for i,r in enumerate(rows):
                    if ref:screen=reference.read(SCREEN);writes=ref['records'][i]['writes'];ports=ref['records'][i]['ports']
                    else:screen,writes,ports=expected(o,r,assets)
                    got=proc.stdout.read(SCREEN)
                    if len(screen)!=SCREEN or got!=screen:
                        pos=next((j for j,(x,y) in enumerate(zip(screen,got)) if x!=y),min(len(screen),len(got)))
                        (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=r,pixel=pos),indent=2)+'\n');proc.kill();raise ValueError(f'wave case{i} pixel{pos} differs')
                    assert sha(screen)==(ref['records'][i]['screen_sha256'] if ref else sha(screen)),'wave frame reference digest differs'
                    if trace:trace.write(screen)
                    h.update(got)
                    if load==0x1000:records.append(dict(input=r,screen_sha256=sha(screen),writes=writes,ports=ports))
                assert not proc.stdout.read(),'extra wave screen';error=proc.stderr.read();assert proc.wait()==0,error
                if reference:assert not reference.read(),'extra wave reference screen'
        finally:
            if trace:trace.close()
            if reference:reference.close()
        assert digest is None or digest==h.hexdigest(),'wave load invariance differs';digest=h.hexdigest()
        if ref:assert digest==ref['trace_sha256'],'wave original trace digest differs'
        print(f'Wave load{load:04x}: PASS cases{len(rows)}',flush=True)
    assert source_manifest(Path(__file__).resolve().parents[1])[0]==manifest,'source changed during wave comparison'
    receipt=dict(passed=True,cases=len(rows),loads=['1000','2000'],compared_pixels=len(rows)*SCREEN,trace_sha256=digest,
        fixture_sha256=sha(fixture.read_bytes()),logical_fixture_sha256=sha(logical.encode()),target_sha256=sha(target),hdi_sha256=sha(a.hdi.read_bytes()),
        asset_sha256={n:sha(assets[n]) for n in names},source_manifest=manifest,exe_sha256=sha(a.exe.read_bytes()),records=records,
        original_cpu_reexecuted=not bool(ref),callback_rejection_passed=True,zero_length_original_fault_loads=zero,zero_length_host_rejection=True,
        utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    if ref:receipt.update(original_producer_receipt_sha256=sha((a.reference_dir/'receipt.json').read_bytes()),original_producer_source_manifest=ref.get('source_manifest'),original_producer_candidate_sha256=ref.get('candidate_sha256'))
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Wave PASS',len(rows),digest,flush=True)
if __name__=='__main__':main()
