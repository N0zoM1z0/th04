"""Execute original title/CRT/text/BB instructions with a GRCG hardware adapter.

No callee is replaced. Only the caller's near-return sentinel ends execution.
The adapter records actual OUT instructions and applies RMW masks from actual
VRAM stores to four complete 32 KiB planes. CPU-visible VRAM is never read by
these routines; an unexpected read or unsupported hardware operation fails.
"""
import hashlib,struct
import unicorn
from unicorn.x86_const import *
from verify_dos_hud_popup import PopupMachine

# Original MAIN0AAF:6A61 loads TXT.BB[0:2048] + TXT2.BB[0:1024].
# Derived through the hash-pinned MAIN PAR decoder, not a synthetic mask.
BB_SHA256='00d1f591a385dbe5f8ac92d2c73cabc863e93d4a012d8291a901bc1316af804e'

def guarded(callback):
    # Pinned Unicorn 1.x ctypes callbacks swallow Python exceptions. Stop the
    # CPU first and rethrow after emu_start, so invalid hardware cannot pass.
    def run(self,u,*args):
        try:return callback(self,u,*args)
        except Exception as error:self.fault=error;u.emu_stop();return 0
    return run

def graphics_seed():
    return [bytearray((plane*31+offset*17+offset//80)&255 for offset in range(32768)) for plane in range(4)]

class TitlesMachine(PopupMachine):
    def __init__(self,load,bb):
        super().__init__(load)
        if len(bb)!=3072 or hashlib.sha256(bb).hexdigest()!=BB_SHA256:raise ValueError('TXT.BB + TXT2.BB identity/extent')
        self.bb=bb;self.mode=0;self.tile=[0]*4;self.tile_at=0;self.ports=[];self.draws=[]
        self.u.hook_add(unicorn.UC_HOOK_INSN,self.output,None,1,0,UC_X86_INS_OUT)
        self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.graphics_write,begin=0xa8000,end=0xaffff)
        self.u.hook_add(unicorn.UC_HOOK_MEM_READ,self.graphics_read,begin=0xa8000,end=0xaffff)
    @guarded
    def hook(self,u,address,size,unused):
        if not 0<=address-u.reg_read(UC_X86_REG_CS)*16<=65535:
            raise ValueError('title engine produced an invalid16-bit CS:IP')
        super().hook(u,address,size,unused)
        if address==(self.load+0xaaf)*16+0x15aa:
            self.draws.append((u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX),u.reg_read(UC_X86_REG_CX),sum((self.tile[i]&1)<<i for i in range(4))))
    @guarded
    def interrupt(self,u,number,unused):raise ValueError(('unexpected title interrupt',number))
    @guarded
    def output(self,u,port,size,value,unused):
        if size!=1 or port not in (0x7c,0x7e):raise ValueError(('unexpected title OUT',port,size,value))
        self.ports.append((port,value))
        if port==0x7c:
            if value not in (0,0xc0):raise ValueError(('unsupported GRCG mode',value))
            self.mode=value;self.tile_at=0
        else:
            if self.mode!=0xc0 or value not in (0,255):raise ValueError('unexpected GRCG tile')
            self.tile[self.tile_at%4]=value;self.tile_at+=1
    @guarded
    def graphics_read(self,u,access,address,size,value,unused):
        raise ValueError(('unexpected CPU VRAM read',address,size))
    @guarded
    def graphics_write(self,u,access,address,size,value,unused):
        if self.mode!=0xc0 or not self.tile_at or self.tile_at%4 or size!=4 or address+size>0xb0000:raise ValueError('unexpected title VRAM write')
        offset=address-0xa8000
        for i,mask in enumerate(value.to_bytes(size,'little')):
            for plane in range(4):
                before=self.planes[plane][offset+i]
                self.planes[plane][offset+i]=(before&(~mask&255))|(self.tile[plane]&mask)
    def seed(self,stage=0,character=0,bgm=0,scroll=0,active=0):
        self.u.mem_write(self.load*16,self.module);self.write(0x768,'H',0xa000)
        self.write(0x1b63,'B',0);self.write(0x1bb6,'B',0)
        self.u.mem_write(self.ds*16+0x4680,bytes(8));self.write(0x469a,'B',bgm)
        self.write(0x469c,'H',0x6446);self.write(0x46a0,'B',0)
        self.write(0x5394,'B',stage);self.write(0x5398,'B',character)
        self.write(0x4278,'h',scroll);self.write(0x427c,'B',active)
        self.write(0x1b66,'H',0x8000);self.u.mem_write(0x80000,self.bb)
        self.u.mem_write(0xa0000,bytes(range(256))*64);self.planes=graphics_seed()
        self.mode=0;self.tile_at=0;self.ports=[];self.draws=[]
    def call(self,callback=None):
        self.done=False;self.fault=None;self.writes=[];self.ports=[];self.draws=[];cs=self.load+0xaaf
        ip=self.read(0x469c,'H')[0] if callback is None else callback
        for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_ES,0xa000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_EFLAGS,0x202)):self.u.reg_write(reg,value)
        self.u.mem_write(0x7e000,struct.pack('<H',0xf000));self.u.emu_start(cs*16+ip,0x10ffff,count=1000000)
        if self.fault:raise self.fault
        if not self.done or self.u.reg_read(UC_X86_REG_SP)!=0xe002:raise ValueError('original title return ABI')
        for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_BP,0xd000),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678)):
            if self.u.reg_read(reg)!=value:raise ValueError(('original title preserved register',reg))
        if self.mode:raise ValueError('title left GRCG enabled')
        return self.snapshot()
    def snapshot(self):
        return dict(titles=self.read(0x46a0,'B')[0],boss=self.read(0x1b63,'B')[0],sprite=self.read(0x1bb6,'B')[0],stage_id=self.read(0x4684,'B')[0],bgm_id=self.read(0x469a,'B')[0],lengths=[self.read(at,'h')[0] for at in (0x4680,0x4682,0x4686)],callback=self.read(0x469c,'H')[0],text=bytes(self.u.mem_read(0xa0000,0x4000)),graphics=b''.join(self.planes),draws=self.draws,ports=self.ports)
