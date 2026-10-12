#!/usr/bin/env python3
"""Execute original MAINE numeral rows and SUPER WORD lookup addresses.

SUPER is stopped after its two actual DGROUP reads, before graphics. Row
calls use a guarded far-return adapter to record requests. No low-memory
pixels, physical timing, pristine provenance or byte-exact claim.
"""
import argparse, hashlib, itertools, json, struct, subprocess, sys
from pathlib import Path
import unicorn
from unicorn.x86_const import *
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

class Original:
    def __init__(self, record, load):
        self.load = load
        self.ds = load + record['dg']
        self.cs = load + 0xa05
        image = bytearray(record['body'])
        for at in record['sites']:
            struct.pack_into('<H', image, at, (struct.unpack_from('<H', image, at)[0] + load) & 65535)
        self.u = unicorn.Uc(unicorn.UC_ARCH_X86, unicorn.UC_MODE_16)
        self.u.mem_map(0, 0x110000)
        self.u.mem_write(load * 16, bytes(image))
        self.mode = ''
        self.u.hook_add(unicorn.UC_HOOK_CODE, self.code, begin=load*16+0x275e, end=load*16+0x275e)
        self.u.hook_add(unicorn.UC_HOOK_CODE, self.code, begin=load*16+0x2804, end=load*16+0x2804)
        self.u.hook_add(unicorn.UC_HOOK_CODE, self.code, begin=self.cs*16+0xff00, end=self.cs*16+0xff00)
        self.u.hook_add(unicorn.UC_HOOK_MEM_READ, self.read)
    def read(self, u, access, address, size, value, unused):
        if self.mode == 'slot' and u.reg_read(UC_X86_REG_EIP)-self.load*16 in (0x2769, 0x2800):
            assert size == 2
            self.addresses.append(address-self.ds*16)
    def code(self, u, address, size, unused):
        try:
            self.body(u, address)
        except BaseException as error:
            self.error=error;u.emu_stop()
    def body(self, u, address):
        if address == self.cs*16+0xff00:
            self.done=True; u.emu_stop()
        elif self.mode == 'slot' and address == self.load*16+0x2804:
            assert len(self.addresses)==2
            self.done=True;u.emu_stop()
        elif self.mode == 'row':
            assert address == self.load*16+0x275e
            sp=u.reg_read(UC_X86_REG_SP)
            ip,cs,pattern,top,left=struct.unpack('<5H',u.mem_read(0x70000+sp,10))
            self.requests.append((left,top,pattern))
            u.reg_write(UC_X86_REG_SP,sp+10)
            u.reg_write(UC_X86_REG_CS,cs);u.reg_write(UC_X86_REG_IP,ip)
    def reset(self, cs, stack):
        self.done=False;self.error=None
        for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):
            self.u.reg_write(reg,value)
        self.u.mem_write(0x7f000,struct.pack('<'+'H'*len(stack),*stack))
    def slot(self, pattern):
        self.mode='slot';self.addresses=[]
        self.reset(self.load,(0xff00,self.cs,pattern,96,172))
        self.u.emu_start(self.load*16+0x275e,0x10ffff,count=200)
        if self.error:raise RuntimeError("original callback rejected") from self.error
        assert self.done
        dimensions,pointer=self.addresses
        assert 0<=dimensions<65536 and 0<=pointer<65536
        return pattern,pointer,dimensions
    def row(self, place, char, selected, digits):
        self.mode='row';self.requests=[]
        self.u.mem_write(self.ds*16+0x4086,bytes([place if selected else 255]))
        self.u.mem_write(self.ds*16+0x4088,bytes([char]))
        self.u.mem_write(self.ds*16+0x4020+place*8,bytes(digits))
        self.reset(self.cs,(0xff00,char,place))
        self.u.emu_start(self.cs*16+0x24b6,0x10ffff,count=1000)
        if self.error:raise RuntimeError("original callback rejected") from self.error
        assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xf006
        return self.requests

def vectors():
    for position,value,char,selected in itertools.product(range(8),range(256),range(2),range(2)):
        digits=[0xa0+(i*3)%10 for i in range(8)];digits[position]=value
        yield (0 if (position+value)%2==0 else 9,char,selected,digits)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('root','native','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.root/'scripts/runtime'))
    from verify_dos_vsync_lifecycle import original
    record=original('maine');rows=list(vectors())
    inputs=''.join(' '.join(map(str,[place,char,selected,*digits]))+'\n' for place,char,selected,digits in rows)
    (a.output/'vectors.txt').write_text(inputs)
    if a.reference:
        receipt=json.loads((a.reference/'receipt.json').read_text())
        assert receipt['passed'] and receipt['original']==record['pins'] and receipt['oracle_sha256']==sha(Path(__file__))
        for name,pin in receipt['files'].items():assert sha(a.reference/name)==pin
        assert (a.reference/'vectors.txt').read_text()==inputs
        for name in ('slots.txt','rows.txt'):(a.output/name).write_bytes((a.reference/name).read_bytes())
    else:
        previous=None
        for load in (0x1000,0x3333):
            o=Original(record,load);slots=[]
            for pattern in range(65536):
                slots.append(o.slot(pattern))
                if pattern%8192==0:print('SUPER',hex(load),pattern,flush=True)
            lines=[]
            for i,(place,char,selected,digits) in enumerate(rows):
                lines.append(f'CASE {i}')
                for left,top,pattern in o.row(place,char,selected,digits):
                    _,pointer,dimensions=slots[pattern]
                    lines.append(f'{left} {top} {pattern} {pointer} {dimensions}')
            data=(''.join(' '.join(map(str,row))+'\n' for row in slots).encode(),('\n'.join(lines)+'\n').encode())
            if previous is not None:assert data==previous,'load metamorphism differs'
            else:
                for name,raw in zip(('slots.txt','rows.txt'),data):(a.output/name).write_bytes(raw)
            previous=data;print('ORIGINAL PASS',hex(load),len(rows),flush=True)
    for name,args in (('slots',['--slot-addresses']),('rows',['--numeral-requests',str(a.output/'vectors.txt')])):
        q=subprocess.run([str(a.native.resolve()),*args],capture_output=True)
        (a.output/(name+'-native.txt')).write_bytes(q.stdout);(a.output/(name+'-stderr.txt')).write_bytes(q.stderr)
        wanted=(a.output/(name+'.txt')).read_bytes()
        if q.returncode or q.stderr or q.stdout!=wanted:
            at=next((i for i,(x,y) in enumerate(itertools.zip_longest(q.stdout.splitlines(),wanted.splitlines())) if x!=y),None)
            raise AssertionError((name,q.returncode,at))
    extents={name:hashlib.sha256(record['body'][start:start+length]).hexdigest() for name,start,length in (('MAINE 0A05:24B6..2599',0xc506,0xe4),('MAINE 0000:275E..290F',0x275e,0x1b2))}
    (a.output/'receipt.json').write_text(json.dumps(dict(passed=True,original=record['pins'],extents=extents,loads=[4096,13107],original_slot_controls=131072,original_row_controls=len(rows)*2,native_slot_controls=65536,native_row_controls=len(rows),oracle_sha256=sha(Path(__file__)),native_sha256=sha(a.native),files={str(f.relative_to(a.output)):sha(f) for f in a.output.rglob('*') if f.is_file()},scope=__doc__),indent=2)+'\n')
    print('NUMERAL SLOT PASS',len(rows),65536,flush=True)
if __name__=='__main__':main()
