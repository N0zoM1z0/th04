#!/usr/bin/env python3
"""Execute original MAIN stage/all-clear bonuses against native fixed-width state."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_effects import Original as Base
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def __init__(self,target):
        self.error=None;self.bonus_events=[];self.raw=0;super().__init__(target)
    def hook(self,u,address,size,unused):
        try:self.body(u,address,size,unused)
        except Exception as e:self.error=e;u.emu_stop()
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(args):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4+args);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off)
        def event(kind,left=0,row=0,color=0,value=0,data=b''):
            self.bonus_events.append(f'{kind} {left} {row} {color} {value} '+(data.hex() if data else '-'))
        if cs==0x2000 and ip in (0x1b50,0x22f6):
            color,off,seg,row,left=struct.unpack('<5H',u.mem_read(0x70000+sp+4,10))
            text=bytearray()
            for i in range(128):
                b=u.mem_read(seg*16+off+i,1)[0]
                if not b:break
                text.append(b)
            else:raise ValueError('original bonus text exceeds128 bytes')
            event(2 if ip==0x1b50 else 1,left,row,color,data=bytes(text));ret(10);return
        if (cs,ip)==(0x2000,0x1f04):event(0,value=self.read(0x3a4,'H')[0]);ret(0);return
        if cs==0x2aaf and ip in (0x1874,0x188e):
            amount=u.mem_read(0x70000+sp+4,1)[0];event(3 if ip==0x1874 else 4,value=amount)
            return # Execute actual byte/clamp arithmetic and RETF2.
        if (cs,ip)==(0x2aaf,0x44b1):event(5);ret(0);return
        if (cs,ip)==(0x33a9,0x9b59):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp+2,4));self.raw=struct.unpack('<I',u.mem_read(seg*16+off,4))[0]
            return # Execute actual multiply/divide/modifier helper.
        super().hook(u,address,size,unused)
    def execute(self,mode,row):
        self.reset();self.error=None;self.bonus_events=[]
        stage,resource,rank,credit,continues,power,points,lives,misses,bombs_used,in_time,dream,graze,delta,bombs,perf,minimum,maximum,extends=row
        resident=bytearray(256);resident[0xb]=lives;resident[0xc]=credit;resident[0xd]=bombs;resident[0x11]=stage;resident[0x31]=misses;resident[0x32]=bombs_used
        self.u.mem_write(0x90000,bytes(resident));self.write(0xba86,'HH',0,0x9000)
        for at,value in [(0x5394,resource),(0x4348,rank),(0x4349,continues),(0x4664,power),(0x466b,points),(0x53df,in_time),(0x1a66,extends),(0x5395,perf),(0x5397,minimum),(0x5396,maximum)]:self.write(at,'B',value)
        self.write(0xbccc,'H',dream);self.write(0xbcbc,'H',graze);self.write(0x435a,'I',delta)
        try:self.call_args(0x9c31 if mode=='C' else 0x9e06,cs=0x33a9)
        except Exception:
            if self.error:raise RuntimeError('original bonus adapter rejected') from self.error
            raise
        if self.error:raise RuntimeError('original bonus adapter rejected') from self.error
        after=self.read(0x435a,'I')[0];bombs=self.u.mem_read(0x9000d,1)[0]
        state=[after,bombs,self.read(0x5395,'B')[0],self.read(0x1a66,'B')[0],self.read(0x3a4,'H')[0],self.raw,(after-delta)&0xffffffff]
        return 'S '+' '.join(map(str,state))+'|'+'|'.join(self.bonus_events)

def fixtures():
    def row(mode='C',**changes):
        c=dict(stage=0,resource=0,rank=1,credit=3,continues=0,power=17,points=31,lives=3,misses=0,bombs_used=0,in_time=1,dream=997,graze=999,delta=0xfffffff0,bombs=2,perf=16,minimum=11,maximum=24,extends=3)
        c.update(changes);return mode,list(c.values())
    # Entire modifier matrix, including unhandled values and nonboolean bonus.
    for mode,rank,credit,continues,in_time in itertools.product('CA',(0,1,2,3,4,255),(0,3,4,5,6,255),(0,1,2,3,4),(0,1,255)):
        yield row(mode,rank=rank,credit=credit,continues=continues,in_time=in_time)
    # One-variable full-width boundaries, then coupled independent edge rows.
    for mode in 'CA':
        for key,values in [('stage',(0,1,5,6,255)),('resource',(0,1,4,6,127,255)),('power',(0,1,127,128,255)),('dream',(0,1,999,1000,32767,65535)),('graze',(0,999,1000,13107,13108,32767,65535)),('points',(0,1,2,99,255)),('lives',(0,1,2,22,23,66,67,255)),('misses',(0,1,255)),('bombs_used',(0,1,255)),('bombs',(0,1,254,255)),('delta',(0,1,0xffffffff))]:
            for value in values:yield row(mode,**{key:value})
        for i in range(256):
            yield row(mode,rank=i%5,resource=i,credit=i%7,continues=i%6,power=i,points=i,lives=i,graze=i*257,dream=65535-i*257,bombs=i,perf=i,minimum=(11,127,128,255)[i%4],maximum=(24,127,128,255)[i%4])
    # Every performance threshold: points=100 means dream offsets step by100;
    # stage=0/power=0/graze=0 isolate the exact pre-modifier threshold.
    for threshold in (100000,200000,500000,800000,1200000):
        for shift in (-1,0,1):
            for perf in (0,1,11,23,24,127,128,254,255):
                yield row(power=0,graze=0,points=100,dream=threshold//100-100+shift,perf=perf,misses=255,bombs_used=255)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--limit',type=int)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);original=Original(args.target.read_bytes())
    cases=list(itertools.islice(fixtures(),args.limit) if args.limit else fixtures());inputs=[];expected=[]
    for mode,row in cases:inputs.append(mode+' '+' '.join(map(str,row)));expected.append(original.execute(mode,row))
    path=out/'fixtures.txt';path.write_text('\n'.join(inputs)+'\n');trace=out/'trace.txt';trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    cmd=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--vectors',str(path)]
    actual=subprocess.run(cmd,capture_output=True,text=True,check=True,env=env).stdout.splitlines()
    for i,(a,b) in enumerate(itertools.zip_longest(actual,expected)):
        if a!=b:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i],actual=a,expected=b),indent=2)+'\n');raise ValueError(f'bonus case{i} differs')
    receipt=dict(passed=True,cases=len(cases),ordinary=sum(m=='C' for m,_ in cases),all_clear=sum(m=='A' for m,_ in cases),target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(trace.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),scope='MAIN load2000 DS8000 main03 13A9:9C31/9E06 plus99FE/9A89/9AFF/9B59 and actual main01 0AAF:1874/188E arithmetic. Full delta/Bomb/performance/extends/tone and ordered original text/gaiji/performance/HUD calls. Independent CPU generates expected output.',limits='Palette/TRAM/HUD video consumers intercepted. No score-drain/whole-scene/route/page/pacing or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
