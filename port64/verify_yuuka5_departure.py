#!/usr/bin/env python3
"""Original MAIN Stage5 bad-dialog/Ending branch, before normal clear bonus.

The CPU executes the real predicate, filename mutation and end_game_bad
resident writes. File I/O, dialogue, sound and palette callees are explicit
adapters; GameExecl is the nonreturning observation boundary. The native
comparison covers the predicate; full native Easy routes separately guard
blocking dialogue and absence of normal bonus/Stage6 publication.
"""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_transition import Original as Base
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Original(Base):
    def body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def far_return(args):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4+args);u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,off)
        if (cs,ip)==(0x2aaf,0x23a3):
            off,seg=struct.unpack('<HH',u.mem_read(0x70000+sp+2,4));name=bytes(u.mem_read(seg*16+off,32)).split(b'\0')[0].decode('ascii')
            self.events.append('load '+name)
            ret=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0];u.reg_write(UC_X86_REG_SP,sp+6);u.reg_write(UC_X86_REG_IP,ret);return
        if (cs,ip)==(0x330e,0x2fc):
            arg=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]
            if arg==0x204:self.events.append('bad-sound-fade4');far_return(2);return
        if (cs,ip)==(0x2000,0x666):
            arg=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0];self.events.append('blackout '+str(arg));far_return(2);return
        if (cs,ip)==(0x2aaf,0x3d0d):
            self.transferred=True;self.events.append('GameExecl');u.emu_stop();return
        super().body(u,address,size,unused)
    def branch(self,stage,rank,continues,character):
        self.seed_departure([0,65535,2,stage,48+stage,0,100,0,123,-456,72,0])
        self.write(0x5394,'B',stage);self.write(0x4348,'BB',rank,continues);self.u.mem_write(0x90012,bytes([48+character]));self.events=[];self.transferred=False;self.error=None
        u=self.u
        for reg,value in ((UC_X86_REG_CS,0x33a9),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
        u.mem_write(0x7e000,struct.pack('<H',0xf000));u.emu_start(0x33a90+0xacb3,0x33a90+0xf000,count=2000000)
        if self.error:raise RuntimeError('original bad-ending callback rejected') from self.error
        if not self.transferred and (u.reg_read(UC_X86_REG_IP)!=0xf000 or u.reg_read(UC_X86_REG_SP)!=0xe002):raise ValueError('ordinary departure ABI failed')
        result=dict(stage=stage,rank=rank,continues=continues,character=character,bad=self.transferred,events=self.events,graze=struct.unpack('<H',u.mem_read(0x90038,2))[0],sequence=u.mem_read(0x90030,1)[0],ending_ascii=u.mem_read(0x90025,1)[0],clock=self.read(0x53da,'h')[0])
        if result['graze']!=1:raise ValueError('departure graze wrap differs')
        if self.transferred:
            if result['sequence']!=254 or result['ending_ascii']!=49 or result['clock']!=0 or self.events!=['0 60','load _DM'+str(character)+'4B.txt','1 0','bad-sound-fade4','blackout 16','GameExecl']:raise ValueError('bad Ending actual filename/order/publication differs')
        elif self.events!=['0 60','1 0','2 0'] or result['clock']!=1:raise ValueError('normal departure branch/order differs')
        return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');a=p.parse_args();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    manifest=source_manifest(Path(__file__).resolve().parents[1])[0];o=Original(a.target.read_bytes());rows=list(itertools.product((0,3,4),range(4),(0,1,127,255),range(2)))
    records=[o.branch(*r) for r in rows];fixture=out/'fixtures.txt';fixture.write_text('\n'.join(' '.join(map(str,r[:3])) for r in rows)+'\n')
    expected=['B '+str(int(r['bad'])) for r in records];trace=out/'trace.txt';trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([a.runner] if a.runner else [])+[str(a.exe.resolve()),'--ending-vectors',str(fixture)];actual=subprocess.run(command,check=True,capture_output=True,text=True,env=env).stdout.splitlines()
    if actual!=expected:raise ValueError('native bad-ending predicate differs')
    # The oracle must reject a one-variable incorrect rank decision.
    mutated=list(actual);mutated[rows.index((4,0,0,0))]='B 0'
    if mutated==expected:raise ValueError('bad-ending negative control failed')
    if manifest!=source_manifest(Path(__file__).resolve().parents[1])[0]:raise ValueError('source changed during departure controls')
    receipt=dict(passed=True,cases=len(rows),original_cpu_reexecuted=True,predicate_negative_control_passed=True,source_manifest_sha256=manifest,target_sha256=sha(o.target),native_sha256=sha(a.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.read_bytes()),records=records,unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,limits='Original MAIN load2000 DS8000;13A9:ACB3/AD4D..AD71;0AAF:2411..242D/0CF4..0D1E. Native predicate only; native Continue/death/MAINE rendering not implemented. No original full-route or DOS exact claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Yuuka5 bad-dialog/Ending controls:',len(rows),'PASS')
if __name__=='__main__':main()
