#!/usr/bin/env python3
"""Compare complete MAINE verdict requests/state with original CPU execution.

The original arithmetic, five switches, BCD formatting and LCG execute without
numeric adapters. Graphics, file I/O, palette and wait consumers are explicit
adapters; this does not establish physical graphics, audio or GUI integration.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import struct
import subprocess

from unicorn.x86_const import *
from verify_cutscene import Original as Base, ending_assets, PAYLOAD_SHA
from verify_maine_join import return_to_caller
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
BODY_SHA='b2eb0681b9cf45b3d58ff8af3007fb568f432140ed31fbc58e8bf6f335c49595'

class Original(Base):
    def __init__(self,target,decoded,commentary,load):
        super().__init__(target,decoded,load)
        if sha(self.payload[0xb787:0xc149])!=BODY_SHA:
            raise ValueError('verdict body extent differs')
        if self.payload[0xe530+0x71a]!=0 or self.payload[0xe530+0x743]!=0:
            raise ValueError('percentage/fixed-digit initialized bytes differ')
        self.commentary=commentary

    def event(self,kind,a=0,b=0,c=0,d=0,e=0,name=b''):
        self.events.append(f'{kind} {a} {b} {c} {d} {e} '+(name.hex() if name else '-'))

    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;relative=cs-self.load
        sp=u.reg_read(UC_X86_REG_SP)
        def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
        def cstring(off,seg):
            raw=bytes(u.mem_read(seg*16+off,128))
            if 0 not in raw:raise ValueError('unterminated verdict consumer string')
            return raw[:raw.index(0)]
        if cs==self.cs and ip==0xff00:
            self.done=True;u.emu_stop();return
        if relative==0xa05 and 0x1737<=ip<0x20f9:
            if ip==0x208e:
                bp=u.reg_read(UC_X86_REG_BP)
                self.cap=struct.unpack('<I',u.mem_read(0x70000+bp-4,4))[0]
            return
        if relative==0 and 0x1c5a<=ip<0x1c84:
            return  # Full original TC4J irand; no host numeric model here.
        if relative==0:
            if ip==0x36b6:
                color,off,seg,step,y,x=words(6)
                self.event('gaiji',x,y,step,color,name=cstring(off,seg));return_to_caller(u,12);return
            if ip==0x19ec:self.event('tone',self.read(0x132,'h')[0]);return_to_caller(u);return
            if ip==0x1274:self.event('pi_free');return_to_caller(u,8);return
            if ip==0x11c2:self.event('copy_page',words(1)[0]);return_to_caller(u,2);return
            if ip in (0x622,0x666):
                self.event('fade',0,int(ip==0x622),words(1)[0]);return_to_caller(u,2);return
            if ip==0xa88:
                off,seg=words(2);assert cstring(off,seg)==b'_ude.txt'
                assert not self.file_open
                self.file_open=True;self.file_position=0;self.line=0
                self.event('file_open',name=cstring(off,seg));return_to_caller(u,4);return
            if ip==0xac4:
                origin,lo,hi=words(3);assert self.file_open and origin==0
                self.file_position=lo+(hi<<16);self.line=self.file_position//30
                self.event('file_seek',self.file_position);return_to_caller(u,6);return
            if ip==0x9d4:
                count,off,seg=words(3);assert self.file_open and count==30
                data=self.commentary[self.file_position:self.file_position+count];assert len(data)==count
                u.mem_write(seg*16+off,data);u.reg_write(UC_X86_REG_AX,count)
                self.event('file_read',count,name=data);return_to_caller(u,6);return
            if ip==0x968:
                assert self.file_open;self.file_open=False
                self.event('file_close');return_to_caller(u);return
        if relative==0xcc7:
            if ip==0x58c:
                off,seg,color,y,x=words(5)
                self.event('text',x,y,color,self.read(0x5fc,'H')[0],name=cstring(off,seg))
                return_to_caller(u,10);return
            if ip in (0x33,0x20a):
                self.event('delay' if ip==0x33 else 'wait',words(1)[0]);return_to_caller(u,2);return
            if ip==0xf5:
                off,seg,slot=words(3);assert slot==0
                self.event('pi_load',name=cstring(off,seg));return_to_caller(u,6);return
            if ip==0x48:assert words(1)==(0,);self.event('pi_palette');return_to_caller(u,2);return
            if ip==0x6d:
                slot,y,x=words(3);assert slot==0
                self.event('pi_put',x,y);return_to_caller(u,6);return
        raise ValueError(f'unexpected verdict consumer {relative:04x}:{ip:04x}')

    def run(self,v):
        self.u.mem_write(self.load*16,self.module)
        self.u.mem_write(self.ds*16,self.data)
        resident=bytearray(256)
        resident[0xf],resident[0x11],resident[0x30]=v[:3]
        resident[0xc],resident[0xe],resident[0x49]=v[3:6]
        struct.pack_into('<H',resident,0x38,v[6])
        struct.pack_into('<I',resident,0x14,v[7])
        for at,n in zip((0x26,0x28,0x2a,0x2c,0x2e,0x34,0x36),v[8:15]):struct.pack_into('<H',resident,at,n)
        struct.pack_into('<II',resident,0x40,*v[15:17])
        resident[0x31],resident[0x32]=v[17:19]
        resident[0x1d:0x25]=bytes(v[21:])
        self.u.mem_write(0x90000,bytes(resident));self.resident_before=bytes(resident)
        self.write(0xe9e,'HH',0,0x9000);self.write(0x3f9e,'I',v[19]);self.write(0x71a,'B',v[20])
        self.write(0x3f9c,'B',0xa5);self.write(0x170,'I',1)
        self.events=[];self.error=None;self.done=False;self.line=-1;self.file_open=False;self.cap=None
        self.font_mode=False
        for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_ES,0),
                          (UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0),
                          (UC_X86_REG_EFLAGS,2)):
            self.u.reg_write(reg,value)
        self.u.mem_write(0x7ff00,struct.pack('<H',0xff00))
        self.u.emu_start(self.cs*16+0x20a8,0x10ffff,count=100000)
        if self.error:raise RuntimeError('original verdict adapter rejected') from self.error
        if not self.done or self.u.reg_read(UC_X86_REG_SP)!=0xff02 or self.file_open:
            raise ValueError('original verdict did not return with its near ABI/file lifetime')
        after=bytes(self.u.mem_read(0x90000,256))
        assert after[:0x26]==resident[:0x26] and after[0x28:]==resident[0x28:]
        skill=self.read(0x3f9e,'I')[0];seed=self.read(0x170,'I')[0]
        std=struct.unpack_from('<H',after,0x26)[0]
        rank=self.read(0x3fa2,'B')[0]
        flags=(self.read(0x3f9c,'B')[0],self.read(0x743,'B')[0],self.read(0x71a,'B')[0],self.read(0x5fc,'H')[0])
        self.events.append('END '+' '.join(map(str,(skill,self.cap,seed,std,rank,self.line,*flags))))
        return self.events

class ClockOriginal(Original):
    """Execute original fades, counter waits and both keyboard wait loops."""
    def held(self):
        t=self.clock;p=self.profile
        if p==0:return t>=160
        if p==1:return t<150 or t>=160
        if p==2:return t<150 or 151<=t<170 or t>=180
        if p==3:return 134<=t<146 or t>=180
        return t==150 or t>=200

    def event(self,*args,**kwargs):
        super().event(*args,**kwargs)
        self.events[-1]=str(self.clock)+' '+self.events[-1]

    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;relative=cs-self.load
        sp=u.reg_read(UC_X86_REG_SP)
        def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
        if relative==0:
            if 0x622<=ip<0x6a3:
                if ip in (0x622,0x666):self.event('fade',0,int(ip==0x622),words(1)[0])
                return
            if ip==0x2206:
                self.clock+=1;return_to_caller(u);return
            if ip==0x19ec:
                tone=self.read(0x132,'h')[0]
                caller=struct.unpack('<HH',u.mem_read(0x70000+sp,4))[1]-self.load
                if caller==0xa05:self.event('tone',tone)
                if tone!=self.previous_tone:
                    self.previous_tone=tone;self.palette.append(f'PALETTE {self.clock} {tone}')
                return_to_caller(u);return
        if relative==0xcc7:
            if 0x33<=ip<0x48:
                if ip==0x33:
                    self.delay_frames=words(1)[0]
                    caller=struct.unpack('<HH',u.mem_read(0x70000+sp,4))[1]-self.load
                    if caller==0xa05:self.event('delay',self.delay_frames)
                if ip==0x3c and self.read(0xefa,'H')[0]<self.delay_frames:
                    self.clock+=1;self.write(0xefa,'H',self.read(0xefa,'H')[0]+1)
                return
            if 0x20a<=ip<0x260:
                if ip==0x20a:self.event('wait',words(1)[0])
                return
            if ip in (0x81a,0x822):
                keys=0x20 if self.held() else 0
                self.write(0x1b42,'H',keys if ip==0x81a else self.read(0x1b42,'H')[0]|keys)
                return_to_caller(u);return
        super().body(u,address)

    def run_clock(self,visible,profile):
        v=[1,5,255,3,2,1,0,0,0,0,0,0,0,0,0,0 if visible else 500,1000,0,0,0,0,*([0]*8)]
        self.clock=0;self.profile=profile;self.previous_tone=-1;self.palette=[]
        events=self.run(v)[:-1]
        return [f'CLOCK {visible} {profile}',*events,*self.palette,f'STOP {self.clock}']

def canonical_clock(data):
    groups=[];current=[]
    for line in data.decode().splitlines():
        if line.startswith('CLOCK '):
            if current:groups.append(current)
            current=[line]
        else:current.append(line)
    if current:groups.append(current)
    normalized=[]
    for group in groups:
        normalized.extend([line for line in group if not line.startswith(('PALETTE ','STOP '))])
        normalized.extend([line for line in group if line.startswith('PALETTE ')])
        normalized.extend([line for line in group if line.startswith('STOP ')])
    return ('\n'.join(normalized)+'\n').encode()

def fixtures():
    # Every legal difficulty/life/bomb/end/turbo choice; completion/std mutation,
    # slow boundary, incomplete run, wrapped helper inputs and BCD bonus branches.
    base=[1,5,255,3,2,1,500,0x12345678,35000,400,300,250,125,700,600,100,100000,3,8,0,0,8,7,6,5,4,3,2,1]
    result=[]
    for rank,lives,bombs,end,turbo in itertools.product(range(5),range(1,7),range(3),(0,254,255),range(2)):
        v=base.copy();v[0]=min(rank,3);v[1]=6 if rank==4 else 5
        v[2]=253 if rank==4 and end==255 else end
        v[3:6]=lives,bombs,turbo;result.append(v)
    for at,values in ((6,(0,1,32767,32768,65535)),(8,(0,1,12000,44000,65535)),
                      (9,(0,1,299,300,301,65535)),(10,(0,1,300,400,65535)),
                      (11,(0,1,124,125,126,65535)),(12,(0,1,125,250,65535)),
                      (13,(0,1,599,600,601,65535)),(14,(0,1,600,700,65535)),
                      (15,(0,49999,50000,50001,655350,655360,4294967295)),
                      (16,(0,1,200,655350,655360,655370,4294967295)),
                      (17,(0,14,15,16,255)),(18,(0,29,30,31,255)),
                      (19,(0,0x7fffffff,0x80000000,0xffffffff)),(20,(0,1))):
        for n in values:
            v=base.copy();v[at]=n;result.append(v)
    for high,next_digit in itertools.product(range(10),range(10)):
        v=base.copy();v[27],v[28]=next_digit,high;result.append(v)
    # Deliberate DWORD wrap and gaiji NUL boundary, not ordinary-game fixtures.
    for total,share in ((1,96),(1,352),(0,0),(0,65535),(65535,65535),(1,65535)):
        for subtract in (0,1):
            v=base.copy();v[13:15]=total,share;v[20]=subtract;result.append(v)
    # Construct assessments at every commentary interval and its neighboring
    # edge. The target still decides the outcome and line independently.
    for desired in (0,1,*range(50000,1050000,50000),1049999,1050000,1199999,
                    1200000,1349999,1350000,1499999,1500000,1700000):
        v=base.copy();v[0:6]=3,6,253,1,0,1;v[6]=1500;v[8]=12000
        v[9:15]=1,1,1,1,1,1;v[15:19]=0,1000,0,0;v[21:]=[0]*8
        v[19]=((desired-550000)*5-5000000)&0xffffffff
        result.append(v)
    rng=random.Random(1294)
    for _ in range(160):
        v=base.copy();v[0]=rng.randrange(4);v[1]=rng.randrange(7);v[2]=rng.choice((0,253,254,255))
        v[3]=rng.randrange(1,7);v[4]=rng.randrange(4);v[5]=rng.randrange(2)
        for at in (6,8,9,10,11,12,13,14):v[at]=rng.randrange(65536)
        for at in (7,15,16,19):v[at]=rng.randrange(1<<32)
        v[17:19]=rng.randrange(256),rng.randrange(256);v[20]=rng.randrange(2)
        v[21:]=[rng.randrange(10) for _ in range(8)];result.append(v)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',type=Path,required=True);p.add_argument('--decoded-dir',type=Path,required=True)
    p.add_argument('--hdi',type=Path,required=True);p.add_argument('--exe',type=Path,required=True)
    p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--reference-dir',type=Path)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    text=ending_assets(args.hdi)['_UDE.TXT'];assert len(text)==780
    (out/'_UDE.TXT').write_bytes(text)
    cases=fixtures();fixture=''.join(' '.join(map(str,v))+'\n' for v in cases)
    (out/'fixtures.txt').write_text(fixture)
    if args.reference_dir:
        Original(args.target,args.decoded_dir,text,0x2000) # Re-attest retained reference's private inputs.
        reference=args.reference_dir.resolve();receipt=json.loads((reference/'receipt.json').read_text())
        assert receipt['passed'] and receipt['body_sha256']==BODY_SHA and receipt['payload_sha256']==PAYLOAD_SHA
        assert receipt['fixture_sha256']==sha(fixture.encode()) and receipt['commentary_sha256']==sha(text)
        expected=(reference/'original.txt').read_bytes();assert sha(expected)==receipt['original_sha256']
        loads=receipt['load_segments']
    else:
        all_loads=[];loads=[0x1000,0x2000]
        for load in loads:
            original=Original(args.target,args.decoded_dir,text,load)
            lines=[]
            for index,v in enumerate(cases):
                lines.append(f'CASE {index}');lines.extend(original.run(v))
            all_loads.append(('\n'.join(lines)+'\n').encode())
        assert all_loads[0]==all_loads[1],'load metamorphism changed verdict state/requests'
        expected=all_loads[0]
    (out/'original.txt').write_bytes(expected)
    env=os.environ.copy();env['WINEDEBUG']='-all'
    cmd=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--verdict-trace',str(out/'fixtures.txt'),str(out/'_UDE.TXT')]
    proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=120)
    (out/'native.txt').write_bytes(proc.stdout);(out/'native-stderr.txt').write_bytes(proc.stderr)
    actual=proc.stdout.replace(b'\r\n',b'\n')
    if proc.returncode or actual!=expected:
        a=actual.splitlines();e=expected.splitlines()
        first=next((i for i,(x,y) in enumerate(zip(a,e)) if x!=y),min(len(a),len(e)))
        (out/'mismatch.json').write_text(json.dumps({'line':first,'actual':str(a[first:first+3]),'expected':str(e[first:first+3]),'returncode':proc.returncode},indent=2)+'\n')
        raise ValueError(f'original/native verdict differs at line {first}')
    if args.reference_dir:
        expected_clock=(reference/'clock-original.txt').read_bytes()
        assert sha(expected_clock)==receipt['clock_original_sha256']
    else:
        traces=[]
        for load in loads:
            original=ClockOriginal(args.target,args.decoded_dir,text,load)
            lines=[]
            for visible,profile in itertools.product(range(2),range(5)):
                lines.extend(original.run_clock(visible,profile))
            traces.append(('\n'.join(lines)+'\n').encode())
        assert traces[0]==traces[1],'load metamorphism changed clock/input/palette'
        expected_clock=traces[0]
    (out/'clock-original.txt').write_bytes(expected_clock)
    clock_cmd=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--verdict-clock',str(out/'_UDE.TXT')]
    clock=subprocess.run(clock_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,timeout=120)
    (out/'clock-native.txt').write_bytes(clock.stdout);(out/'clock-stderr.txt').write_bytes(clock.stderr)
    actual_clock=canonical_clock(clock.stdout.replace(b'\r\n',b'\n'))
    if clock.returncode or actual_clock!=expected_clock:
        a=actual_clock.splitlines();e=expected_clock.splitlines()
        first=next((i for i,(x,y) in enumerate(zip(a,e)) if x!=y),min(len(a),len(e)))
        (out/'clock-mismatch.json').write_text(json.dumps({'line':first,'actual':str(a[first:first+3]),'expected':str(e[first:first+3])},indent=2)+'\n')
        raise ValueError(f'original/native clock differs at line {first}')
    mf,source=source_manifest(Path(__file__).resolve().parents[1])
    ends=[line.split() for line in expected.decode().splitlines() if line.startswith('END ')]
    covered=sorted({int(v[6]) for v in ends})
    assert covered==list(range(-1,26)),'verdict controls omitted a commentary interval'
    receipt={'passed':True,'utc':datetime.now(timezone.utc).isoformat(),'cases':len(cases),
        'load_segments':loads,'body_extent':'MAINE recovered 0A05:1737..20F8 (tables included)',
        'body_sha256':BODY_SHA,'payload_sha256':PAYLOAD_SHA,'commentary_sha256':sha(text),
        'fixture_sha256':sha(fixture.encode()),'original_sha256':sha(expected),'native_sha256':sha(actual),
        'executable_sha256':sha(args.exe.read_bytes()),'source_manifest':mf,'source_files':source,
        'clock_cases':10,'clock_original_sha256':sha(expected_clock),'clock_native_sha256':sha(actual_clock),
        'commentary_lines':covered,
        'command':cmd,'reference_dir':str(args.reference_dir) if args.reference_dir else None,
        'scope':'Full verdict C++/LCG CPU and consumer requests/state; full original fades, counter and keyboard wait loops with VSync/keyboard/palette adapters. No original pixels, physical timing/audio, GUI integration or DOS exact promotion.'}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'Original/native verdict: {len(cases)} cases, 10 clock/key controls; loads={loads}; state/requests/palette ticks PASS')

if __name__=='__main__':main()
