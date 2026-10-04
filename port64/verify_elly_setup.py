#!/usr/bin/env python3
"""Original retained Stage3 boss setup controls; private Elly fields retained.
File/graphics requests use the bounded verify_session adapters.
"""
import argparse,hashlib,itertools,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_IP
from verify_session import Original
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()

def setup(o,rank,marker):
    o.reset();o.error=None;o.calls=[]
    boss=bytes((marker+i*73)&255 for i in range(24))
    extra=bytes((marker+i*19)&255 for i in range(16))
    explosions=bytes((marker+i*37)&255 for i in range(48))
    o.u.mem_write(0x853ca,boss);o.u.mem_write(0x8bcde,extra);o.u.mem_write(0x84298,explosions)
    q=bytes((marker+i*11)&255 for i in range(19));orbit=marker*257-32768
    o.u.mem_write(0x846e6,q);o.write(0x46fa,'h',orbit);o.write(0x46e4,'B',marker)
    o.call_args(0xa6f6,far=True)
    if o.error:raise RuntimeError('original retained setup hook rejected') from o.error
    if o.u.mem_read(0x846e6,19)!=q or o.read(0x46fa,'h')!=(orbit,) or o.read(0x46e4,'B')!=(marker,):raise ValueError('Stage3 setup wrote private Elly globals')
    expected=' '.join((o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),o.u.mem_read(0x84298,48).hex(),*[str(v) for v in o.read(0xbcf0,'hh')+o.read(0x23ed,'B')]))
    return ' '.join(map(str,(rank,*boss,*extra,*explosions))),expected

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1];manifest,_=source_manifest(root);o=Original(a.target.read_bytes())
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            if address==0x33a90+0xa6f6:raise ValueError('injected retained setup rejection')
            super().body(u,address,size,unused)
    rejecting=Rejecting(o.target)
    try:setup(rejecting,1,77)
    except (RuntimeError,ValueError):
        if not isinstance(rejecting.error,ValueError):raise
    else:raise ValueError('original setup callback silently accepted rejection')
    pairs=[setup(o,rank,marker) for rank,marker in itertools.product((0,),range(256))]
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(row for row,_ in pairs)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve())]
    actual=subprocess.run(command+['--setup-vectors',str(fixture)],capture_output=True,text=True,check=True,env=env).stdout.splitlines()
    expected=[value for _,value in pairs]
    for i,(got,want) in enumerate(itertools.zip_longest(actual,expected)):
        if got!=want:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=pairs[i][0],expected=want,actual=got),indent=2)+'\n')
            raise ValueError(f'retained Elly setup case{i} differs')
    trace=out/'trace.txt';trace.write_text('\n'.join(expected)+'\n')
    after,_=source_manifest(root)
    if manifest!=after:raise ValueError('source changed during retained setup controls')
    receipt=dict(passed=True,callback_rejection_passed=True,retained_setup_controls=len(pairs),target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()),source_manifest_sha256=manifest,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='Original MAIN load2000 DS8000 Stage3 setup13A9:A6F6..A7B4 and boss_reset A4D1..A517; complete24-byte Boss,16 additional,48 explosion metadata,hitbox and timeout across256 retained markers; private19-byte scythe,orbit and pattern group unchanged.',limits='Stage3 setup file/BFNT/CDG/hardware consumers intercepted. Stage-common slowdown/shake/palette/invincibility reset is separately observed/integrated; player hit/death/Bomb/render and whole game excluded. No DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(passed=True,setup=len(pairs),private_globals_retained=True)))
if __name__=='__main__':main()
