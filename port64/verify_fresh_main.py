#!/usr/bin/env python3
"""Original fresh MAIN session prefix: resident resets and local score clearing.

Execute MAIN 0AAF:0213..024F at two relocated loads with retained outgoing
resident digits and dirty graze/miss/Bomb/ES bytes. Stop before power/resource/
HUD initialization; no child adapters or fake return are used. Compare public
native MAIN construction, not complete startup, high-score loading or pixels.
"""
import argparse,hashlib,itertools,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from unicorn.x86_const import *
from verify import source_manifest
TARGET='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
sha=lambda b:hashlib.sha256(b).hexdigest()
def original(target,load,character,shot,extra,marker):
    module=bytearray(target[6144:]);at=struct.unpack_from('<H',target,24)[0]
    for n in range(1136):
        off,seg=struct.unpack_from('<HH',target,at+4*n);site=seg*16+off
        struct.pack_into('<H',module,site,(struct.unpack_from('<H',module,site)[0]+load)&65535)
    u=unicorn.Uc(unicorn.UC_ARCH_X86,unicorn.UC_MODE_16);u.mem_map(0,2*1024*1024);u.mem_write(load*16,bytes(module))
    u.mem_write(0x8ba86,struct.pack('<HH',0,0x9000));resident=bytearray([marker]*256)
    resident[0x12]=ord('0')+character;resident[0x30]=253 if extra else 254
    digits=bytes((marker+d)%10 for d in range(8));resident[0x1d:0x25]=digits;before=bytes(resident)
    u.mem_write(0x90000,before);u.mem_write(0x84349,bytes([marker]*8));u.mem_write(0x85398,bytes([marker]))
    cs=load+0xaaf
    for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
    u.emu_start(cs*16+0x213,cs*16+0x250,count=1000)
    assert (u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP))==(cs,0x250)
    expected=bytearray(before);expected[0x38:0x3a]=b'\0\0';expected[0x31:0x33]=b'\0\0';expected[0x30]=0x37
    after=bytes(u.mem_read(0x90000,256));assert after==expected
    return [struct.unpack_from('<H',after,0x38)[0],after[0x31],after[0x32],after[0x30],u.mem_read(0x85398,1)[0],*u.mem_read(0x84349,8),*after[0x1d:0x25]]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('target','exe','output-dir'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest=source_manifest(root)[0]
    target=a.target.read_bytes();assert len(target)==156258 and sha(target)==TARGET
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    native=subprocess.run([str(a.exe.resolve()),'--fresh-main-vectors'],capture_output=True,text=True,check=True).stdout
    (out/'native.txt').write_text(native);rows=[list(map(int,l.split())) for l in native.splitlines()];cases=list(itertools.product(range(2),range(2),range(2),(0,19,255)));assert len(rows)==24
    originals=[]
    for load in (0x1000,0x2000):
        result=[original(target,load,*v) for v in cases];assert result==rows
        originals.append(dict(load=f'{load:04x}',records=result))
    path=out/'original.json';path.write_text(json.dumps(originals,indent=2)+'\n');assert source_manifest(root)[0]==manifest
    receipt=dict(passed=True,cases=24,loads=['1000','2000'],source_manifest=manifest,target_sha256=TARGET,extent='MAIN 0AAF:0213..024F',extent_sha256=sha(target[6144+0xad03:6144+0xad40]),native_sha256=sha(a.exe.read_bytes()),native_trace_sha256=sha((out/'native.txt').read_bytes()),original_sha256=sha(path.read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Fresh MAIN session prefix PASS24cases at1000/2000')
if __name__=='__main__':main()
