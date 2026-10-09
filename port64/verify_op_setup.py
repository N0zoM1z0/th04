#!/usr/bin/env python3
"""Original OP setup/animations/input waits/fades at two relocated loads.

Execute0A74:0D5F..1304,0DA1:0152..01A7 and0000:0622..06A2. Original
window arithmetic, default/selection/priority, resident writes, release/press
waits and fades execute. Resource/graphics, two input samples and refresh
consumers are guarded adapters. No complete original pixels/audio/DOS exactness.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD
from verify_maine_join import return_to_caller
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def emit(self,k,a=0,b=0,c=0,d=0,data=b''):
        self.events.append(f'{k} {self.clock} {a} {b} {c} {d} {data.hex() if data else "-"}')
    def port(self,u,port,size,value,unused):
        try:
            assert port==0xa6 and size==1 and value==1
            self.emit('access',value)
        except Exception as error:self.error=error;u.emu_stop()
    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
        def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
        def string(off,seg):
            data=bytes(u.mem_read(seg*16+off,512));assert b'\0' in data;return data.split(b'\0')[0]
        def ret(n=0):return_to_caller(u,n)
        if pair==(0xa74,0xff00):self.done=True;u.emu_stop();return
        if pair[0]==0xa74 and 0xd5f<=pair[1]<0x1305:
            if pair[1] in (0x1170,0x128d):
                field=0x10 if pair[1]==0x1170 else 0x18
                self.emit('option',int(field==0x18),u.mem_read(0x90000+field,1)[0])
            return
        if pair[0]==0xda1 and 0x152<=pair[1]<0x1a8:return
        if pair[0]==0 and 0x622<=pair[1]<0x6a3:return
        if pair==(0,0x2648):self.emit('vsync');self.clock+=1;ret();return
        if pair==(0,0x1de0):self.emit('tone',self.read(0x586,'h')[0]);ret();return
        if pair==(0xda1,0x2b):
            assert words(1)==(1,);self.emit('delay',1);self.clock+=1;ret(2);return
        if pair in ((0xda1,0x7cc),(0xda1,0x7d4)):
            assert self.clock<len(self.keys),'setup input exhausted'
            sense=pair[1]==0x7d4;sample=self.keys[self.clock][int(sense)]
            self.write(0x2710,'H',(self.read(0x2710,'H')[0] if sense else 0)|sample)
            self.emit('sense' if sense else 'reset',sample);ret();return
        if pair==(0,0x2a86):
            assert string(*words(2))==b'mswin.bft';self.emit('super_load',data=b'mswin.bft');ret(4);return
        if pair==(0xda1,0xed):
            off,seg,slot=words(3);assert slot==0 and string(off,seg)==b'ms.pi' and not self.loaded
            self.loaded=True;self.write(0x2370,'HH',0x4000,0x9000);self.emit('load',data=b'ms.pi');ret(6);return
        if pair==(0xda1,0x40):assert words(1)==(0,) and self.loaded;self.emit('palette');ret(2);return
        if pair==(0xda1,0x65):assert words(3)==(0,0,0) and self.loaded;self.emit('picture');ret(6);return
        if pair==(0,0x1618):
            assert words(4)==(0x4000,0x9000,0x2388,self.ds) and self.loaded
            self.loaded=False;self.emit('free');ret(8);return
        if pair==(0,0x156c):assert words(1)==(0,);self.emit('copy',0);ret(2);return
        if pair==(0xda1,0x968):
            height,width,top,left=words(4);assert width in (160,400,448) and height in (16,32)
            self.emit('rectangle',left,top,width,height);ret(8);return
        if pair==(0,0x2d5a):
            pattern,top,left=words(3);assert pattern<9;self.emit('sprite',left,top,pattern);ret(6);return
        if pair==(0xda1,0x4a4):
            off,seg,color,top,left=words(5);assert seg==self.ds and color in (0,15)
            self.emit('text',left,top,color,self.read(0xa3c,'H')[0],string(off,seg));ret(10);return
        if pair==(0,0x2922):self.emit('super_free');ret();return
        raise ValueError(f'unexpected setup consumer {pair}')
    def run(self,effect,keys):
        u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data);u.mem_write(0x7e000,bytes(8192))
        self.write(0x1a64,'HH',0,0x9000);self.write(0xa3c,'H',effect);self.write(0x2b48,'HH',73,91)
        resident=bytes((i*73+19)&255 for i in range(256));u.mem_write(0x90000,resident)
        self.events=[];self.clock=0;self.done=False;self.loaded=False;self.error=None;self.keys=keys
        for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
        u.mem_write(0x7f000,struct.pack('<H',0xff00));u.emu_start(self.cs*16+0x128e,0x10ffff,count=5000000)
        if self.error:raise RuntimeError('original setup rejected') from self.error
        assert self.done and not self.loaded and u.reg_read(UC_X86_REG_SP)==0xf002
        actual=bytes(u.mem_read(0x90000,256));assert all(actual[i]==resident[i] for i in range(256) if i not in (0x10,0x18))
        self.events.append(f'END {self.clock} {self.read(0x586,"h")[0]} {actual[0x10]} {actual[0x18]} '+ ' '.join(map(str,self.read(0x2b48,'HH'))))
        return ('\n'.join(self.events)+'\n').encode()
def fixtures():
    cases=[]
    for effect,bgm,se in itertools.product(range(8),range(3),range(3)):
        keys=[[0,0] for _ in range(400)];at=40
        for _ in range((bgm+1)%3):keys[at]=[1,1];at+=10
        keys[at]=[0x2000,0x2000];at+=50
        for _ in range((se+2)%3):keys[at]=[2,2];at+=10
        keys[at]=[0x20,0x20];cases.append((effect,keys))
    for chord in (3,0x1000,0x10,0x1021,0x2001,0xffff):
        keys=[[0,0] for _ in range(400)];keys[40]=[chord,chord];keys[50]=[0x20,0x20];keys[110]=[0x2000,0x2000];cases.append((2,keys))
    for held in (0x20,0x2000,1,0x1000):
        keys=[[0,0] for _ in range(400)]
        for i in range(37,47):keys[i]=[held,held]
        keys[51]=[0x2000,0x2000];keys[111]=[0x20,0x20];cases.append((2,keys))
    keys=[[0,0] for _ in range(10200)];keys[10040]=[0,0x20];keys[10100]=[0,0x2000];cases.append((2,keys))
    # Reset-only and sense-only arrows test the OR latch and two clear samples.
    keys=[[0,0] for _ in range(400)];keys[40]=[1,0];keys[42]=[0,2];keys[52]=[0,0x20];keys[112]=[0x2000,0];cases.append((7,keys))
    return cases
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded-dir','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    manifest,files=source_manifest(root);out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);cases=fixtures()
    fixture=''.join(f'{effect} {len(keys)} '+' '.join(str(v) for sample in keys for v in sample)+'\n' for effect,keys in cases)
    (out/'fixtures.txt').write_text(fixture)
    if a.reference_dir:
        receipt=json.loads((a.reference_dir/'receipt.json').read_text());assert receipt['passed']
        expected=(a.reference_dir/'original.txt').read_bytes();assert sha(fixture.encode())==receipt['fixtures_sha256']
    else:
        traces=[]
        for load in (0x1000,0x2000):
            o=Original(a.target,a.decoded_dir,load);trace=b''.join(o.run(*case) for case in cases)
            (out/f'original-{load:04x}.txt').write_bytes(trace);traces.append(trace)
        assert traces[0]==traces[1];expected=traces[0]
    (out/'original.txt').write_bytes(expected)
    result=subprocess.run([str(a.exe.resolve()),'--replay',str(out/'fixtures.txt')],capture_output=True)
    (out/'native.txt').write_bytes(result.stdout);(out/'stderr.txt').write_bytes(result.stderr)
    if result.returncode or result.stdout!=expected:
        x=result.stdout.splitlines();y=expected.splitlines();at=next((i for i,(x,y) in enumerate(zip(x,y)) if x!=y),min(len(x),len(y)))
        (out/'mismatch.json').write_text(json.dumps(dict(line=at,actual=str(x[at:at+2]),expected=str(y[at:at+2]),returncode=result.returncode),indent=2))
        raise ValueError(f'setup differs line{at}')
    assert source_manifest(root)[0]==manifest
    (out/'receipt.json').write_text(json.dumps(dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),cases=len(cases),trace_lines=len(expected.splitlines()),target_sha256=PACKED,payload_sha256=PAYLOAD,fixtures_sha256=sha(fixture.encode()),trace_sha256=sha(expected),exe_sha256=sha(a.exe.read_bytes()),source_manifest=manifest,source_files=files,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),original_cpu_reexecuted=not bool(a.reference_dir),reference_receipt_sha256=sha((a.reference_dir/'receipt.json').read_bytes()) if a.reference_dir else None,scope=__doc__),indent=2)+'\n')
    print(f'setup PASS {len(cases)} cases/{len(expected.splitlines())} ordered requests at two original loads')
if __name__=='__main__':main()
