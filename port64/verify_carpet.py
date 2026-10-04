#!/usr/bin/env python3
"""Original Stage4 carpet ring/lighting controls; invalidation consumers adapted."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_session import Original as Base
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if getattr(self,'reject',False) and (cs,ip)==(0x2aaf,0x3ff4):raise ValueError('injected carpet rejection')
        if cs==0x2aaf and ip in (0xee6,0x2052):
            if ip==0xee6:
                if self.read(0x4264,'HH')!=(384,2) or struct.unpack('<hh',u.mem_read(0x70000+sp+2,4))!=(3072,0):raise ValueError('carpet top invalidation request differs')
                self.top=True;cleanup=6
            else:self.all=True;cleanup=2
            off=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0];u.reg_write(UC_X86_REG_SP,sp+cleanup);u.reg_write(UC_X86_REG_IP,off);return
        super().body(u,address,size,unused)
def image_vo(n):return 72+2*(n//25)+1280*(n%25)
def image_id(n):
    v=n-72
    if v<0 or v%2 or v%1280>6:raise ValueError('invalid original tile offset')
    return (v%1280)//2*25+v//1280

def fixtures():
    for frame,cel,level,line in itertools.product((0,1,2,1663,1664,1665,1666,1667,65535),range(8),range(3),(0,399)):
        yield [frame,cel,level,1,line,1,*((i*19+7)%100 for i in range(600))]
    for frame,line,steps in ((0,0,1750),(0,399,1750),(1663,399,70),(65532,0,10)):
        yield [frame,0,0,1,line,steps,*((i*19+7)%100 for i in range(600))]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);manifest=source_manifest(Path(__file__).resolve().parents[1])[0];o=Original(a.target.read_bytes());inputs=[];expected=[]
    table=bytes(o.u.mem_read(0x8190c,144));animation=bytes(o.u.mem_read(0x8199c,192))
    # Attest the authored formulas against immutable target DATA separately
    # from the executed carpet updater. This is not candidate-derived output.
    ids=[image_id(n) for n in struct.unpack('<72H',table)]
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    tables=subprocess.run(([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--carpet-tables'],check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    if len(tables)!=2 or list(map(int,tables[0].split()))!=ids or list(map(int,tables[1].split()))!=list(animation):raise ValueError('native carpet formulas differ from target DATA')
    for row in fixtures():
        o.reset();o.error=None;o.write(0x1a5c,'h',row[1]);o.write(0x4328,'B',row[2]);o.write(0x432c,'H',0x3ff4 if row[3] else 0x11be);o.write(0x4278,'H',row[4]);o.u.mem_write(0x84700,bytes(1600))
        for y in range(25):o.u.mem_write(0x84d40+y*64,struct.pack('<24H',*(image_vo(n) for n in row[6+y*24:6+(y+1)*24])))
        inputs.append(' '.join(map(str,row)))
        for tick in range(row[5]):
            frame=(row[0]+tick)&65535;o.write(0x538a,'H',frame);o.write(0x538d,'B',frame%4);o.u.mem_write(0x84700,bytes(1600));o.top=o.all=False
            if o.read(0x432c,'H')==(0x3ff4,):o.call_args(0x3ff4,cs=0x2aaf)
            state=[*o.read(0x1a5c,'h'),*o.read(0x4328,'B'),int(o.read(0x432c,'H')==(0x3ff4,))];ring=bytearray();dirty=bytearray()
            for y in range(25):ring.extend(struct.pack('<24H',*(image_id(n) for n in o.read(0x4d40+y*64,'24H'))))
            for y in range(50):dirty.extend(o.u.mem_read(0x84700+y*32,24))
            expected.append(' '.join(map(str,(*state,ring.hex(),dirty.hex(),int(o.top),int(o.all)))))
    path=out/'fixtures.txt';path.write_text('\n'.join(inputs)+'\n');trace=out/'trace.txt';trace.write_text('\n'.join(expected)+'\n');env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--carpet-vectors',str(path)]
    actual=subprocess.run(command,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    for i,(want,got) in enumerate(itertools.zip_longest(expected,actual)):
        if not want or not got or want.split()!=got.split():
            (out/'mismatch.json').write_text(json.dumps(dict(checkpoint=i,expected=want,actual=got),indent=2)+'\n');raise ValueError(f'carpet checkpoint{i} differs')
    o.reject=True
    try:o.call_args(0x3ff4,cs=0x2aaf)
    except (ValueError,RuntimeError):
        if not isinstance(o.error,ValueError):raise
    else:raise ValueError('carpet rejection swallowed')
    assert manifest==source_manifest(Path(__file__).resolve().parents[1])[0]
    r=dict(passed=True,callback_rejection_passed=True,cases=len(inputs),trace_records=len(expected),source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(trace.read_bytes()),image_table_ids=ids,image_table_sha256=sha(table),animation_sha256=sha(animation),observed_utc=datetime.now(timezone.utc).isoformat(),unicorn_version=unicorn.__version__,scope='Actual MAIN load2000 DS8000 0AAF:3F9A..40FD carpet helper/render;25x24 tile IDs,50x24 direct dirty flags,cel/level/callback and adapted384x2 top/all invalidation requests. Retained lighting/disable/wrap sequences. DATA190C..199B image offsets/199C..1A5B animation identity.',limits='Invalidation consumers adapted; no physical page/VRAM/GRCG/frame-pacing or DOS exact claim. Native full redraw displays the ring; original dirty-page transient rows are not reproduced.')
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(inputs),records=len(expected))))
if __name__=='__main__':main()
