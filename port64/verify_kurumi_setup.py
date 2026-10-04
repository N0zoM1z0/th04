#!/usr/bin/env python3
"""Original CPU controls for retained Stage2 boss setup and invincibility tick.

Executes original boss_reset/Stage2 setup. File/graphics requests use the same
bounded adapters as verify_session. Player controls stop immediately after the
invincibility decrement, before hit/death/Bomb consumers.
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
    o.write(0x4348,'B',rank);o.call_args(0xa623,far=True)
    if o.error:raise RuntimeError('original retained setup hook rejected') from o.error
    expected=' '.join((o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),o.u.mem_read(0x84298,48).hex(),*[str(v) for v in o.read(0xbcf0,'hh')+o.read(0x23ed,'B')]))
    return ' '.join(map(str,(rank,*boss,*extra,*explosions))),expected

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1];manifest,_=source_manifest(root);o=Original(a.target.read_bytes())
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            if address==0x33a90+0xa623:raise ValueError('injected retained setup rejection')
            super().body(u,address,size,unused)
    rejecting=Rejecting(o.target)
    try:setup(rejecting,1,77)
    except (RuntimeError,ValueError):
        if not isinstance(rejecting.error,ValueError):raise
    else:raise ValueError('original setup callback silently accepted rejection')
    pairs=[setup(o,rank,marker) for rank,marker in itertools.product(range(4),range(256))]
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(row for row,_ in pairs)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve())]
    actual=subprocess.run(command+['--setup-vectors',str(fixture)],capture_output=True,text=True,check=True,env=env).stdout.splitlines()
    expected=[value for _,value in pairs]
    for i,(got,want) in enumerate(itertools.zip_longest(actual,expected)):
        if got!=want:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=pairs[i][0],expected=want,actual=got),indent=2)+'\n')
            raise ValueError(f'retained Kurumi setup case{i} differs')
    ticks=[]
    for value in range(256):
        o.reset();o.error=None;o.write(0x4662,'B',value)
        o.u.reg_write(UC_X86_REG_CS,0x2aaf);o.u.reg_write(UC_X86_REG_IP,0x5fd4)
        o.u.emu_start(0x2aaf0+0x5fd4,0x2aaf0+0x5fdf,count=8)
        if o.error:raise RuntimeError('player countdown hook rejected') from o.error
        if o.u.reg_read(UC_X86_REG_IP)!=0x5fdf:raise ValueError('player countdown left bounded prefix')
        ticks.append(str(o.read(0x4662,'B')[0]))
    native_ticks=subprocess.run(command+['--invincibility-vectors'],capture_output=True,text=True,check=True,env=env).stdout.splitlines()
    if ticks!=native_ticks:raise ValueError('player invincibility byte tick differs')
    trace=out/'trace.txt';trace.write_text('\n'.join(expected+ticks)+'\n')
    after,_=source_manifest(root)
    if manifest!=after:raise ValueError('source changed during retained setup controls')
    receipt=dict(passed=True,callback_rejection_passed=True,retained_setup_controls=len(pairs),invincibility_controls=len(ticks),target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()),source_manifest_sha256=manifest,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope='Original MAIN load2000 DS8000 Stage2 setup13A9:A623..A6F5 and boss_reset A4D1..A517; complete24-byte Boss,16 additional,48 explosion metadata,hitbox and timeout across four ranks and256 retained markers. Original player_update0AAF:5FD4..5FDE byte decrement only.',limits='Stage2 setup file/BFNT/CDG/hardware consumers intercepted. Stage-common slowdown/shake/palette/invincibility reset is separately observed/integrated; player hit/death/Bomb/render and whole game excluded. No DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(passed=True,setup=len(pairs),ticks=len(ticks))))
if __name__=='__main__':main()
