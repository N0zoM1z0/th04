#!/usr/bin/env python3
"""Independent original MAIN CPU controls for score drain, HUD bytes and extends."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_effects import Original as Base
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def __init__(self,target):
        self.error=None;self.score_events=[];super().__init__(target)
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as error:self.error=error;u.emu_stop()
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(args):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4+args);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off)
        if (cs,ip)==(0x2000,0x1b50):
            attr,off,seg,row,left=struct.unpack('<5H',u.mem_read(0x70000+sp+4,10));data=bytearray()
            for i in range(9):
                b=u.mem_read(seg*16+off+i,1)[0]
                if not b:break
                data.append(b)
            else:raise ValueError('score HUD string lacks terminator')
            self.score_events.append(f'0 {left} {row} {attr} '+(data.hex() if data else '-'));ret(10);return
        if (cs,ip)==(0x2aaf,0x1874):
            self.score_events.append(f'1 0 0 {u.mem_read(0x70000+sp+4,1)[0]} -');return # actual wrapped raise executes
        if (cs,ip)==(0x2aaf,0x43f8):self.score_events.append('2 0 0 0 -');ret(0);return
        if (cs,ip)==(0x330e,0x7d2):
            value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];self.score_events.append(f'3 0 0 {value} -');ret(2);return
        super().hook(u,address,size,unused)
    def seed(self,values):
        self.reset();self.error=None;self.score_events=[]
        delta,frame,shown,unused,extends,lives,clear,perf,minimum,maximum,popup,callback=values[:12]
        self.write(0x435a,'II',delta,frame);self.write(0x1a67,'B',shown);self.write(0x4359,'B',unused);self.write(0x1a66,'B',extends)
        self.u.mem_write(0x90000,bytes(256));self.u.mem_write(0x9000b,bytes([lives]));self.write(0xba86,'HH',0,0x9000)
        self.write(0xbcba,'B',clear);self.write(0x5395,'3B',perf,maximum,minimum)
        self.write(0x469b,'B',popup);self.write(0x469e,'H',0x67e8 if callback else 0x7777)
        for at,data in zip((0x4349,0x4351,0x1ebe,0x1ec6),(values[12:20],values[20:28],values[28:36],values[36:44])):self.u.mem_write(0x80000+at,bytes(data))
        self.u.mem_write(0x81ece,b'\0')
    def execute(self,op):
        self.score_events=[];self.error=None
        try:self.call_args({'U':0x6bd4,'E':0x4316,'H':0x6ba2}[op],cs=0x2aaf)
        except Exception:
            if self.error:raise RuntimeError('original score adapter rejected') from self.error
            raise
        if self.error:raise RuntimeError('original score adapter rejected') from self.error
        header=[*self.read(0x435a,'II'),self.read(0x1a67,'B')[0],self.read(0x4359,'B')[0],self.read(0x1a66,'B')[0],self.u.mem_read(0x9000b,1)[0],self.read(0xbcba,'B')[0],self.read(0x5395,'B')[0],self.read(0x5397,'B')[0],self.read(0x5396,'B')[0],self.read(0x469b,'B')[0],int(self.read(0x469e,'H')[0]==0x67e8)]
        data=[b for at in (0x4349,0x4351,0x1ebe,0x1ec6) for b in self.u.mem_read(0x80000+at,8)]
        return 'S '+' '.join(map(str,header+data))+('|'+'|'.join(self.score_events) if self.score_events else '')

def fixtures():
    def row(op='U',delta=12345,frame=0,shown=0,unused=137,extends=0,lives=3,clear=0,perf=16,minimum=11,maximum=24,popup=4,callback=0,digits=None,hiscore=None,temp=None,hud=None):
        return op,[delta,frame,shown,unused,extends,lives,clear,perf,minimum,maximum,popup,callback,*((digits or [7,9,9,9,9,2,0,0])),*((hiscore or [7,9,9,9,9,2,0,0])),*((temp or [23,17,5,11,71,0,0,43])),*((hud or list(range(8))))]
    for delta,frame,shown in itertools.product((0,1,2,31,32,33,65535,65536,195551,195552,195553,0x7fffffff,0x80000000,0xffffffff),(0,1,6110,6111,6112,65535,65536,0xffff0000,0xffffffff),(0,1,255)):
        yield row(delta=delta,frame=frame,shown=shown)
    for i in range(256):
        # AAA sees genuine byte-add AF and can produce a two-byte carry in
        # nondecimal controls. Highest byte and gaiji NUL termination vary.
        digits=[i]*8;temp=[(i*73+19)&255]*8;hiscore=[(i+17)&255]*8
        yield row(delta=i*773+1,frame=i*257,digits=digits,temp=temp,hiscore=hiscore,shown=i%3,extends=5)
        yield row('H',digits=digits,hiscore=hiscore)
    for index,high,millions,extends,lives,clear,perf in itertools.product(range(5),(0,1,2,3,9,10,255),(0,1,2,3,4,5,7,8,9,255),(0,1,2,3,4,5,10),(0,99,100,255),(0,19,20,255),(0,24,254,255)):
        if (index+high+millions+extends+lives+clear+perf)%97:continue
        digits=[7,0,0,0,0,index,millions,high]
        yield row('E',digits=digits,extends=extends,lives=lives,clear=clear,perf=perf)
    for position,offset,shown in itertools.product(range(8),(-1,0,1),(0,1)):
        digits=[5]*8;hiscore=digits.copy();hiscore[position]+=offset
        yield row(delta=1,digits=digits,hiscore=hiscore,shown=shown,extends=10)
    for high in (0,9,10,95,96,97,255):
        yield row(delta=1,digits=[3,9,9,9,9,9,9,high],hiscore=[0]*8,extends=10,temp=[0]*8)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--limit',type=int)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);original=Original(args.target.read_bytes())
    manifest_before,_=source_manifest(Path(__file__).resolve().parents[1])
    class RejectingOriginal(Original):
        def body(self,u,address,size,unused):
            if address-u.reg_read(UC_X86_REG_CS)*16==0x6bd4:
                raise ValueError('injected callback rejection')
            super().body(u,address,size,unused)
    rejected=RejectingOriginal(original.target);rejected.seed(next(fixtures())[1])
    try:rejected.execute('U')
    except RuntimeError as error:
        if not isinstance(error.__cause__,ValueError):raise
    else:raise ValueError('CPU callback rejection silently accepted')
    cases=list(itertools.islice(fixtures(),args.limit) if args.limit else fixtures());expected=[];inputs=[]
    for op,values in cases:
        original.seed(values);inputs.append(op+' '+' '.join(map(str,values)));expected.append(original.execute(op))
    sequences=0;sequence_steps=0
    if not args.limit:
        # Original retained memory drives the sequence; the native executable
        # retains its own state between R commands, rather than reseeding from
        # each target result. Inject later awards before original U calls.
        for initial in (1,33,200000,999999,3000000):
            values=[initial,0,0,137,0,3,0,16,11,24,4,0]+[7]+[0]*7+[0]*24
            original.seed(values);inputs.append('U '+' '.join(map(str,values)));expected.append(original.execute('U'));sequences+=1
            for tick in range(10000):
                award=12345 if tick in (2,17,64) else 0
                pending=original.read(0x435a,'I')[0]
                if not pending and tick>64:break
                original.write(0x435a,'I',(pending+award)&0xffffffff)
                inputs.append('R '+str(award));expected.append(original.execute('U'));sequence_steps+=1
            else:raise ValueError('original score sequence failed to drain')
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n');trace=out/'trace.txt';trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--vectors',str(fixture)]
    actual=subprocess.run(command,capture_output=True,text=True,check=True,env=env).stdout.splitlines()
    for i,(a,b) in enumerate(itertools.zip_longest(actual,expected)):
        if a!=b:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i],expected=b,actual=a),indent=2)+'\n');raise ValueError(f'score case{i} differs')
    manifest_after,_=source_manifest(Path(__file__).resolve().parents[1])
    if manifest_before!=manifest_after:raise ValueError('source changed during score oracle')
    counts={k:sum(op==k for op,_ in cases) for k in 'UEH'}
    receipt=dict(passed=True,source_manifest_sha256=manifest_after,callback_rejection_passed=True,cases=len(inputs),isolated_cases=len(cases),counts=counts,sequences=sequences,retained_state_steps=sequence_steps,target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),scope='MAIN load2000 DS8000 main01 0AAF:6BD4/6BA2/4316 and actual1874 byte raise. Complete8-byte score/hiscore/temp/HUD, delta/frame dwords, flags, extends/lives/clear/performance/popup selector and ordered gaiji/performance/HUD/audio requests.',limits='TRAM/lives-HUD/audio consumers intercepted; popup callback recorded by identity. No persisted score data, complete scene/frame pacing/DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
