#!/usr/bin/env python3
"""Independent original MAIN CPU controls for enter/leave and blocked departure."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_score import Original as Base
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
POINTERS={0:0x11be,1:0x62b3,2:0x6349,3:0x6446}
class Original(Base):
    def __init__(self,target):
        self.events=[];self.pause_dialog=False;self.paused=False;super().__init__(target)
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(args):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4+args);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off)
        if (cs,ip) in ((0x2000,0x1b0c),(0x2000,0x229e)):
            attr,value,row,left=struct.unpack('<4H',u.mem_read(0x70000+sp+4,8));self.events.append(f'{int(ip==0x1b0c)} {left} {row} {value} {attr}');ret(8);return
        if (cs,ip)==(0x33a9,0xad25):self.events.append('0 60')
        if (cs,ip)==(0x2aaf,0x2bfb):
            self.events.append('1 0')
            if self.pause_dialog:self.paused=True;u.emu_stop();return
            ret(0);return
        if (cs,ip)==(0x33a9,0x9c31):
            self.events.append('2 0');off=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0];u.reg_write(UC_X86_REG_SP,sp+2);u.reg_write(UC_X86_REG_IP,off);return
        if (cs,ip)==(0x330e,0x2fc):
            arg=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]
            if arg!=0x20a:raise ValueError('unexpected departure fade')
            self.events.append('3 10');ret(2);return
        if (cs,ip)==(0x33a9,0xae5d):self.events.append('4 0')
        if (cs,ip)==(0x330e,0xd7):
            arg=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];self.events.append(f'5 {arg}');ret(2);return
        super().body(u,address,size,unused)
    def seed_overlay(self,time,mode):
        self.reset();self.u.mem_write(0x90000,bytes(256));self.write(0xba86,'HH',0,0x9000);self.write(0x1b62,'B',time);self.write(0x469c,'H',POINTERS[mode])
    def overlay(self):
        self.events=[];mode={v:k for k,v in POINTERS.items()}[self.read(0x469c,'H')[0]]
        if mode not in (1,2):raise ValueError('overlay callback outside enter/leave ownership')
        self.call_args(POINTERS[mode],cs=0x2aaf)
        if self.error:raise RuntimeError('original overlay callback rejected') from self.error
        mode={v:k for k,v in POINTERS.items()}[self.read(0x469c,'H')[0]]
        return f'O {self.read(0x1b62,"B")[0]} {mode}'+('|'+'|'.join(self.events) if self.events else '')
    def seed_departure(self,v,reset=True):
        frame,graze,stage_graze,stage,ascii,quit,tone,changed,x,y,time,mode=v
        if reset:self.seed_overlay(time,mode)
        else:self.write(0x1b62,'B',time);self.write(0x469c,'H',POINTERS[mode])
        self.paused=False;self.pause_dialog=False;self.error=None
        self.write(0x53d9,'<Bh',255,frame);self.write(0x5394,'B',0);self.write(0xbcbc,'H',stage_graze)
        self.u.mem_write(0x90038,struct.pack('<H',graze));self.u.mem_write(0x90011,bytes([stage]));self.u.mem_write(0x90013,bytes([ascii]))
        self.write(0x5392,'B',quit);self.write(0x3a4,'h',tone);self.write(0x5393,'B',changed);self.write(0x4642,'hh',x,y)
    def departure(self,op='N'):
        self.events=[];self.error=None
        if op=='B':
            if not self.paused:raise ValueError('original was not blocked')
        elif op=='C':
            if not self.paused:raise ValueError('original was not blocked')
            # Continue the original machine context after the intercepted far
            # dialog call, preserving its actual caller stack and registers.
            u=self.u;sp=u.reg_read(UC_X86_REG_SP);off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off);self.paused=False
            u.emu_start(seg*16+off,0x33a90+0xf000,count=2000000)
            if u.reg_read(UC_X86_REG_IP)!=0xf000 or u.reg_read(UC_X86_REG_SP)!=0xe002:raise ValueError('original resumed departure ABI failed')
        elif op=='P':
            u=self.u;self.pause_dialog=True
            for reg,value in ((UC_X86_REG_CS,0x33a9),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
            u.mem_write(0x7e000,struct.pack('<H',0xf000));u.emu_start(0x33a90+0xacb3,0x33a90+0xf000,count=2000000)
            if not self.paused:raise ValueError('original did not reach dialog interception')
        else:self.call_args(0xacb3,cs=0x33a9)
        if self.error:raise RuntimeError('original departure callback rejected') from self.error
        mode={v:k for k,v in POINTERS.items()}[self.read(0x469c,'H')[0]]
        v=[self.read(0x53da,'h')[0],struct.unpack('<H',self.u.mem_read(0x90038,2))[0],self.read(0xbcbc,'H')[0],self.u.mem_read(0x90011,1)[0],self.u.mem_read(0x90013,1)[0],self.read(0x5392,'B')[0],self.read(0x3a4,'h')[0],self.read(0x5393,'B')[0],*self.read(0x4642,'hh'),int(self.paused),self.read(0x1b62,'B')[0],mode]
        return 'D '+' '.join(map(str,v))+('|'+'|'.join(self.events) if self.events else '')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);original=Original(a.target.read_bytes());manifest,_=source_manifest(Path(__file__).resolve().parents[1]);inputs=[];expected=[];counts=dict(overlay=0,departure=0,blocked=0,joint=0)
    class RejectingOriginal(Original):
        def body(self,u,address,size,unused):
            if address==0x2aaf0+0x6349:raise ValueError('injected original transition rejection')
            super().body(u,address,size,unused)
    rejected=RejectingOriginal(original.target);rejected.seed_overlay(72,2)
    try:rejected.overlay()
    except (ValueError,RuntimeError):
        if not isinstance(rejected.error,ValueError):raise
    else:raise ValueError('original callback error silently passed')
    def overlay(op):inputs.append(op);expected.append(original.overlay());counts['overlay']+=1
    def departure(op):inputs.append(op);expected.append(original.departure(op[0]));counts['blocked' if op[0] in 'PBC' else 'departure']+=1
    for mode,time in itertools.product((1,2),range(256)):
        original.seed_overlay(time,mode);overlay(f'O {time} {mode}')
    for mode,time in ((1,0),(1,63),(2,72),(2,255)):
        original.seed_overlay(time,mode);overlay(f'O {time} {mode}')
        while original.read(0x469c,'H')[0] in (POINTERS[1],POINTERS[2]):overlay('R')
    for frame,stage,ascii,graze,stage_graze,time,mode in itertools.product((0,1,415,416,417,487,488,489,32767,-32768),(0,255),(48,255),(0,65535),(0,2,65535),(0,72),(0,1,3)):
        values=[frame,graze,stage_graze,stage,ascii,91,100,0,123,-456,time,mode]
        original.seed_departure(values);departure('D '+' '.join(map(str,values)))
    values=[0,65535,2,0,48,0,100,0,123,-456,72,3];original.seed_departure(values);departure('P '+' '.join(map(str,values)))
    for _ in range(9):departure('B')
    departure('C')
    for _ in range(489):departure('N')
    # Compose the actual departure, owned leave callback and score routines.
    # Ordinary Stage1 carries large pending score; there is no final/Extra
    # forced flush in this control. Titles/audio/dialog/bonus remain adapters.
    for pending in (1,20000000,2000000000):
        values=[pending,0,0,0,0,3,0,16,11,24,0,0]+[0]*32
        original.seed(values);original.seed_departure([0,0,0,0,48,0,100,0,123,-456,72,0],reset=False)
        for tick in range(489):
            inputs.append('J '+str(pending) if not tick else 'K');counts['joint']+=1
            expected.append(original.departure())
            mode={v:k for k,v in POINTERS.items()}[original.read(0x469c,'H')[0]]
            expected.append(original.overlay() if mode==2 else f'O {original.read(0x1b62,"B")[0]} {mode}')
            expected.append(original.execute('U'))
        if pending>=20000000 and not original.read(0x435a,'I')[0]:raise ValueError('original ordinary departure unexpectedly drained all pending score')
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n');trace=out/'trace.txt';trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');cmd=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--vectors',str(fixture)];actual=subprocess.run(cmd,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    for i,(x,y) in enumerate(itertools.zip_longest(actual,expected)):
        if x!=y:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i] if i<len(inputs) else None,expected=y,actual=x),indent=2)+'\n');raise ValueError(f'transition case{i} differs')
    if source_manifest(Path(__file__).resolve().parents[1])[0]!=manifest:raise ValueError('source changed during transition oracle')
    r=dict(passed=True,callback_rejection_passed=True,cases=len(inputs),trace_records=len(expected),counts=counts,target_sha256=sha(original.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()),source_manifest_sha256=manifest,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),scope='MAIN load2000 DS8000 main01 0AAF:62B3/6349/6287 and main03 13A9:ACB3..AE86 ordinary Stage1 departure. Full callback-byte/state, ordered text/gaiji/tone/dialog/bonus/audio/next-stage/delay requests. Original retained machine context pauses at dialog then resumes from its actual far-call return. Three489-tick joint original departure/leave/score sequences preserve pending score across next-stage request.',limits='TRAM/font/audio/dialog/bonus rendering intercepted. Stage2 resources, final/Extra Ending branches, whole gameplay/video/pacing and DOS exactness not claimed.')
    (out/'receipt.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
