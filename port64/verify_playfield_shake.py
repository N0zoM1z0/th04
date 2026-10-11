#!/usr/bin/env python3
"""Compare original MAIN shake state/EGC requests with the native owner.

Actual target CPU executes 0AAF:2246..2315 and its tile invalidator.
The four EGC hardware consumers are adapted to record their complete call ABI;
this does not accept physical EGC pixels or complete native pictures.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,os,struct,subprocess
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP
from verify_score import Original as Base
from verify import source_manifest

sha=lambda data:hashlib.sha256(data).hexdigest()
class Original(Base):
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if cs==0x2000 and ip in (0xa22,0xb24,0xc34,0x91c):
            if getattr(self,'reject',False):raise ValueError('injected shake EGC rejection')
            count,bottom,right,top,left=struct.unpack('<5H',u.mem_read(0x70000+sp+4,10))
            if (left,top,right,bottom)!=(32,0,415,399):raise ValueError('shake EGC rectangle ABI')
            if ip in (0xa22,0xb24):self.draw_x=(-1 if ip==0xa22 else 1)*count
            else:self.draw_y=(-1 if ip==0xc34 else 1)*count
            off,segment=struct.unpack('<HH',u.mem_read(0x70000+sp,4))
            u.reg_write(UC_X86_REG_CS,segment);u.reg_write(UC_X86_REG_IP,off);u.reg_write(UC_X86_REG_SP,sp+14);return
        if (cs,ip)==(0x2aaf,0x2052):self.invalidated=True # Execute actual invalidator.
        super().body(u,address,size,unused)

    def execute(self,row):
        self.reset();self.error=None;self.draw_x=self.draw_y=0;self.invalidated=False
        x,y,time,redraw,mod2,mod4=row
        self.write(0x427e,'hhh',x,y,time);self.write(0x185c,'B',redraw&255)
        self.write(0x538c,'BB',mod2,mod4)
        self.call_args(0x2246,cs=0x2aaf)
        if self.error:raise RuntimeError('original shake adapter rejected') from self.error
        return [*self.read(0x427e,'hhh'),*self.read(0x185c,'b'),self.draw_x,self.draw_y,int(self.invalidated)]

def fixtures():
    yield from itertools.product((-4,0,4),(-4,0,4),(-1,0,1,12),(-128,-1,0,1,2,127),(0,1,255),(0,1,2,3,255))
    for timer in (-32768,32767):
        for mod2,mod4 in itertools.product((0,1),range(4)):yield (0,0,timer,0,mod2,mod4)
    for x,y in itertools.product((-32768,32767),(0,-2,2)):yield (x,y,0,0,0,0)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('target','exe','output-dir'):p.add_argument('--'+key,required=True,type=Path)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    target=args.target.read_bytes()
    if len(target)!=156258 or sha(target)!='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b':raise ValueError('shake target identity')
    manifest,sources=source_manifest(Path(__file__).resolve().parents[1]);original=Original(target)
    rows=list(fixtures());expected=[original.execute(row) for row in rows]
    fixture=out/'fixture.txt';fixture.write_text(''.join(' '.join(map(str,row))+'\n' for row in rows))
    trace=out/'native.txt';command=[str(args.exe.resolve()),str(fixture),str(trace)]
    subprocess.run(command,check=True);actual=[list(map(int,line.split())) for line in trace.read_text().splitlines()]
    if actual!=expected:raise ValueError('complete shake CPU state/EGC request comparison')
    subprocess.run([str(args.exe.resolve())],check=True)
    original.reject=True
    try:original.execute((0,0,12,0,0,0))
    except (RuntimeError,ValueError):
        if not isinstance(original.error,ValueError):raise
    else:raise ValueError('shake rejection swallowed')
    snapshot=out/'executed-source/native'
    for row in sources:
        source=Path(__file__).resolve().parents[1]/row['path'];destination=snapshot/row['path'];destination.parent.mkdir(parents=True,exist_ok=True)
        data=source.read_bytes();destination.write_bytes(data)
        if sha(data)!=row['sha256']:raise ValueError('shake source drift')
    report=dict(passed=True,accepts_exact=False,cases=len(rows),target_sha256=sha(target),owner_sha256=sha(target[0xe536:0xe606]),
        native_program_sha256=sha(args.exe.read_bytes()),source_manifest_sha256=manifest,source_files=sources,
        fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()),command=command,unicorn_version=unicorn.__version__,
        callback_rejection_passed=True,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))

if __name__=='__main__':main()
