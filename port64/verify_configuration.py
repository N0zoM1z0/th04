#!/usr/bin/env python3
"""Original OP configuration load/live-save/exit-save and physical host storage.

OP0A74:000C..01B0 and the original far structure-copy helper execute at
loads1000/2000. Guarded DOS-file consumers preserve request order and bytes.
Host checksum/rank/bool/short-file repair is an explicit native policy.
RankFF now requests the independently checked OP setup; the defined host
checksum does not reproduce ZUN's uninitialized missing-file checksum.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import struct
import subprocess
from datetime import datetime, timezone
from unicorn.x86_const import *
from verify_op_score import Original as Base, PACKED, PAYLOAD
from verify_maine_join import return_to_caller
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
hextext=lambda b:b.hex() if b else '-'
FIELDS=(15,58,59,16,24,73)
class Original(Base):
    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16)
        sp=u.reg_read(UC_X86_REG_SP)
        def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
        def ret(n=0):return_to_caller(u,n)
        if pair==(0xa74,0xff00):self.done=True;u.emu_stop();return
        if pair[0]==0xa74 and 0xc<=pair[1]<0x1b1:return
        if pair[0]==0 and 0x4202<=pair[1]<0x421c:return # execute actual F_SCOPY
        if pair in ((0,0x89a),(0,0xa7a)):
            off,seg=words(2);name=bytes(u.mem_read(seg*16+off,16)).split(b'\0')[0]
            assert name==b'MIKO.CFG' and not self.open
            self.open=True;self.mode=int(pair[1]==0x89a)
            self.position=len(self.file) if self.mode else 0
            self.events.append(f'0 {self.mode} 0 -');u.reg_write(UC_X86_REG_AX,1);ret(4);return
        if pair==(0,0xab6):
            origin,lo,hi=words(3);assert self.open and origin==0
            self.position=lo+(hi<<16);assert self.position in (0,9)
            self.events.append(f'1 {self.position} 0 -');ret(6);return
        if pair in ((0,0x9c6),(0,0xaf8)):
            count,off,seg=words(3);assert self.open and seg==0x7000 and count in (1,6,10)
            if pair[1]==0x9c6:
                assert self.mode==0 and count==10
                data=bytes(self.file[self.position:self.position+count]);assert len(data)==10
                u.mem_write(seg*16+off,data);kind=2
            else:
                assert self.mode==1
                data=bytes(u.mem_read(seg*16+off,count));kind=3
                if len(self.file)<self.position+count:self.file.extend(bytes(self.position+count-len(self.file)))
                self.file[self.position:self.position+count]=data
            self.events.append(f'{kind} {count} {len(data)} {hextext(data)}')
            self.position+=len(data);u.reg_write(UC_X86_REG_AX,len(data));ret(6);return
        if pair==(0,0x95a):
            assert self.open;self.open=False;self.events.append('4 0 0 -');ret();return
        raise ValueError(f'unexpected original configuration control {pair}')
    def run(self,operation,file,options):
        u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data)
        u.mem_write(0x7e000,bytes(8192));self.write(0x1a64,'HH',0,0x9000)
        resident=bytearray((i*73+19)&255 for i in range(256))
        for field,value in zip(FIELDS,options):resident[field]=value
        u.mem_write(0x90000,bytes(resident));self.file=bytearray(file);self.events=[]
        self.open=False;self.mode=0;self.position=0;self.done=False;self.error=None
        for reg,value in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
        u.mem_write(0x7f000,struct.pack('<H',0xff00));u.emu_start(self.cs*16+(0xc,0xb0,0x133)[operation],0x10ffff,count=10000)
        if self.error:raise RuntimeError('original configuration adapter rejected') from self.error
        assert self.done and not self.open and u.reg_read(UC_X86_REG_SP)==0xf002
        actual=bytes(u.mem_read(0x90000,256));allowed=bytearray(resident)
        if operation==0:
            for field in FIELDS:allowed[field]=actual[field]
        assert actual==allowed,'configuration changed unrelated resident fields'
        loaded=bytes(actual[field] for field in FIELDS)
        return '\n'.join(['STATE '+loaded.hex()+' '+hextext(self.file)]+self.events)+'\n'

def fixtures():
    default=bytes([1,3,2,2,1,1]);record=default+b'\0\x90\x53'+bytes([sum(default)])
    rows=[]
    for field,value in itertools.product(range(6),range(256)):
        data=bytearray(record);data[field]=value
        rows.append((0,bytes(data),default))
    r=random.Random(1323)
    for operation in (0,1,2):
        for size in (10,11,29):
            for _ in range(64):
                data=bytearray(r.randrange(256) for _ in range(size));data[6:8]=b'\0\x90'
                options=bytes(r.randrange(256) for _ in range(6));rows.append((operation,bytes(data),options))
    return rows

def physical(exe,out):
    valid=bytes.fromhex('030600020200a5127e0d') # six-byte sum13, opaque metadata
    cases={'valid':valid,'missing':b'','short':valid[:7],'checksum':valid[:-1]+b'\0','rank':bytes.fromhex('07030202010100000010'),'bool':bytes.fromhex('0103020201020000000b'),
           'ranges':bytes.fromhex('0000ff030401c1237707')}
    # Generate checksums independently of native production, including wraps.
    raw=bytearray(cases['ranges']);raw[9]=sum(raw[:6])&255;cases['ranges']=bytes(raw)
    outputs={};wanted='000401010200'
    for name,data in cases.items():
        directory=out/name;directory.mkdir()
        if name!='missing':(directory/'MIKO.CFG').write_bytes(data)
        command=[str(exe.resolve()),'--host',str(directory),wanted]
        r=subprocess.run(command,capture_output=True);(directory/'stdout.txt').write_bytes(r.stdout);(directory/'stderr.txt').write_bytes(r.stderr);r.check_returncode()
        expected=bytes.fromhex(wanted)+bytes(3)+bytes([sum(bytes.fromhex(wanted))])
        assert (directory/'MIKO.CFG').read_bytes()==expected
        lines=r.stdout.decode().splitlines();loaded=lines[0].split()[1]
        assert loaded==({'valid':'030600020200','ranges':'000302000001'}.get(name,'010302010101')),(name,loaded)
        # Live save must preserve opaque bytes, while exit clears them.
        first_state=next(line for line in lines if line.startswith('STATE '))
        metadata=data[6:9] if name in ('valid','ranges') else bytes(3)
        assert first_state.split()[2]==(bytes.fromhex(wanted)+metadata+expected[-1:]).hex()
        assert not list(directory.glob('.config-pending-*'))
        outputs[name]=dict(stdout_sha256=sha(r.stdout),file_sha256=sha(expected))
    blocked=out/'blocked';blocked.mkdir();(blocked/'MIKO.CFG').mkdir()
    r=subprocess.run([str(exe.resolve()),'--host',str(blocked),wanted],capture_output=True)
    (blocked/'stdout.txt').write_bytes(r.stdout);(blocked/'stderr.txt').write_bytes(r.stderr)
    assert r.returncode!=0 and (blocked/'MIKO.CFG').is_dir() and not list(blocked.glob('.config-pending-*'))
    return outputs

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded-dir','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    manifest,files=source_manifest(root);out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    rows=fixtures();fixture=''.join(f'{op} {hextext(file)} {options.hex()}\n' for op,file,options in rows)
    (out/'fixtures.txt').write_text(fixture)
    if a.reference_dir:
        previous=json.loads((a.reference_dir/'receipt.json').read_text());assert previous['passed']
        expected=(a.reference_dir/'original.txt').read_bytes()
        assert sha(expected)==previous['trace_sha256'] and sha(fixture.encode())==previous['fixture_sha256']
        Original(a.target,a.decoded_dir,0x1000) # re-attest, no semantic CPU rerun
    else:
        answers=[]
        for load in (0x1000,0x2000):
            original=Original(a.target,a.decoded_dir,load)
            answer=''.join(original.run(*row) for row in rows).encode();answers.append(answer)
            (out/f'original-{load:04x}.txt').write_bytes(answer)
        assert answers[0]==answers[1];expected=answers[0]
    (out/'original.txt').write_bytes(expected)
    command=[str(a.exe.resolve()),'--replay',str(out/'fixtures.txt')]
    r=subprocess.run(command,capture_output=True);(out/'native.txt').write_bytes(r.stdout);(out/'stderr.txt').write_bytes(r.stderr);r.check_returncode()
    if r.stdout!=expected:
        index=next(i for i,(x,y) in enumerate(zip(r.stdout.splitlines(),expected.splitlines())) if x!=y)
        (out/'mismatch.json').write_text(json.dumps(dict(line=index,native=r.stdout.splitlines()[index].decode(),original=expected.splitlines()[index].decode()),indent=2)+'\n')
        raise ValueError('configuration differs at line'+str(index))
    host=physical(a.exe,out);assert source_manifest(root)[0]==manifest
    receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),target_sha256=PACKED,payload_sha256=PAYLOAD,
                 original_cpu_reexecuted=not bool(a.reference_dir),reference_dir=str(a.reference_dir) if a.reference_dir else None,cases=len(rows),loads=['1000','2000'],fixture_sha256=sha(fixture.encode()),trace_sha256=sha(expected),host_cases=host,host_failed_read=1,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('configuration PASS',len(rows),'original cases;7 physical load/save/reopen controls;1 failed read')
if __name__=='__main__':main()
