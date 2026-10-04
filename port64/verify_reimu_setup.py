#!/usr/bin/env python3
"""Original retained Stage4 Reimu setup controls, with bounded file/video adapters."""
import argparse,hashlib,itertools,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from verify_session import Original
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
def setup(o,rank,marker):
    o.reset();o.error=None;o.calls=[];o.write(0x4348,'B',rank);o.write(0x5398,'B',1)
    boss=bytes((marker+i*73)&255 for i in range(24));extra=bytes((marker+i*19)&255 for i in range(16));ex=bytes((marker+i*37)&255 for i in range(48))
    private=bytes((marker+i*11)&255 for i in range(3));template=bytes((marker+i*29)&255 for i in range(26));pool=bytes((marker+i*7)&255 for i in range(832))
    o.u.mem_write(0x853ca,boss);o.u.mem_write(0x8bcde,extra);o.u.mem_write(0x84298,ex)
    o.u.mem_write(0x8bcfa,private);o.u.mem_write(0x8bcfe,template);o.u.mem_write(0x8b204,pool);o.write(0x24b6,'BB',marker,marker^170)
    o.call_args(0xa7b5,far=True)
    if o.error:raise RuntimeError('original retained Reimu setup rejected') from o.error
    if o.u.mem_read(0x8bcfa,3)!=private or o.u.mem_read(0x8bcfe,26)!=template or o.u.mem_read(0x8b204,832)!=pool or o.read(0x24b6,'BB')!=(marker,marker^170):raise ValueError('Stage4 setup wrote private Reimu state')
    if o.read(0xbcd8,'HHH')!=(0xb91b,0x33a9,0x83a3,):raise ValueError('Reimu callbacks differ')
    want=' '.join((o.u.mem_read(0x853ca,24).hex(),o.u.mem_read(0x8bcde,16).hex(),o.u.mem_read(0x84298,48).hex(),*[str(v) for v in o.read(0xbcf0,'hh')+o.read(0x23ed,'B')]))
    return ' '.join(map(str,[rank,*boss,*extra,*ex])),want

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0];o=Original(a.target.read_bytes())
    class Rejecting(Original):
        def body(self,u,address,size,unused):
            if address==0x33a90+0xa7b5:raise ValueError('injected Reimu setup rejection')
            super().body(u,address,size,unused)
    bad=Rejecting(o.target)
    try:setup(bad,1,77)
    except (RuntimeError,ValueError):
        if not isinstance(bad.error,ValueError):raise
    else:raise ValueError('original setup rejection swallowed')
    pairs=[setup(o,rank,marker) for rank,marker in itertools.product(range(4),range(256))]
    path=out/'fixtures.txt';path.write_text('\n'.join(row for row,_ in pairs)+'\n');trace=out/'trace.txt';trace.write_text('\n'.join(want for _,want in pairs)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--setup-vectors',str(path)]
    got=subprocess.run(command,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    for i,(want,actual) in enumerate(itertools.zip_longest((want for _,want in pairs),got)):
        if want!=actual:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=pairs[i][0],expected=want,actual=actual),indent=2)+'\n');raise ValueError(f'Reimu setup case{i} differs')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during setup controls')
    r=dict(passed=True,callback_rejection_passed=True,cases=len(pairs),target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(trace.read_bytes()),source_manifest_sha256=manifest,observed_utc=datetime.now(timezone.utc).isoformat(),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),scope='Original MAIN load2000 DS8000 Stage4 setup13A9:A7B5..A931 for Marisa player/Reimu Boss. Four ranks256retained markers: complete BOSS24/additional16/explosions48/hitbox/timeout; private3/template26/pool832/initialized2 bytes retained; update/foreground pointers checked.',limits='File/video consumers adapted. Native helper assumes first encounter fresh MAIN private state; common stage initialization resets pool separately. Not complete stage integration/render/player death/Bomb/audio/full route or DOS exact.')
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(pairs))))
if __name__=='__main__':main()
