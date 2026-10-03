#!/usr/bin/env python3
"""Original MAIN CPU controls for Orange foreground, explosions and circles."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX,UC_X86_REG_DX
from verify_effects import Original as Base
from verify_orange import boss
sha=lambda b:hashlib.sha256(b).hexdigest()
signed=lambda n:n if n<32768 else n-65536

class Original(Base):
    def __init__(self,target):
        self.render_draws=[];self.raw_circle=False;self.callback_error=None;super().__init__(target)
    def hook(self,u,address,size,unused):
        # Unicorn1.x can print-and-ignore Python hook exceptions. Stop the
        # CPU explicitly so an adapter rejection can never become a pass.
        try:self.hook_body(u,address,size,unused)
        except Exception as error:self.callback_error=error;u.emu_stop()
    def call_args(self,*args,**kwargs):
        self.callback_error=None
        try:super().call_args(*args,**kwargs)
        except Exception:
            if self.callback_error:raise RuntimeError('Original render hook rejected the call') from self.callback_error
            raise
        if self.callback_error:raise RuntimeError('Original render hook rejected the call') from self.callback_error
    def hook_body(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        def ret(cleanup,far=False):
            words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
            u.reg_write(UC_X86_REG_SP,sp+cleanup)
            if far:u.reg_write(UC_X86_REG_CS,words[1])
            u.reg_write(UC_X86_REG_IP,words[0])
        if cs==0x2000 and ip in (0x2f54,0x2838,0x1e2a):
            data=bytes(u.mem_read(0x70000+sp+4,10 if ip==0x2838 else 6))
            if ip==0x2838:
                planes,mask,pattern,y,x=struct.unpack('<HHHhh',data)
                if planes!=0xffc0 or mask!=0:raise ValueError('Orange white plane contract differs')
            else:pattern,y,x=struct.unpack('<Hhh',data)
            self.render_draws.append([0 if ip==0x2f54 else 1 if ip==0x2838 else 2,x,y,pattern,0])
            ret(14 if ip==0x2838 else 10,True);return
        if (cs,ip)==(0x2aaf,0x1a56):
            pattern=struct.unpack('<H',u.mem_read(0x70000+sp+2,2))[0]
            self.render_draws.append([3,signed(u.reg_read(UC_X86_REG_AX)),signed(u.reg_read(UC_X86_REG_DX)),pattern,0]);ret(4);return
        if (cs,ip)==(0x2000,0x11ec) and not self.raw_circle:
            radius,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));self.render_draws.append([4,x,y,radius,self.color]);ret(10,True);return
        if (cs,ip)==(0x2aaf,0x1666):ret(2);return
        super().hook(u,address,size,unused)

def explosion(alive=0,age=0,x=3072,y=1280,rx=8,ry=8,dx=176,dy=176,offset=0):
    return list(struct.pack('<BB6hbB',alive,age,x,y,rx,ry,dx,dy,-7,offset))
def render_row(phase=2,phase_frame=0,frame=0,damage=0,big_frame=0,e=None):
    state=boss(phase,phase_frame);state[18]=damage
    return [frame,big_frame,73,0,*state,*range(16),*(e or [*explosion(),*explosion(),*explosion()])]
def renders():
    for phase,phase_frame,frame,damage in itertools.product((0,1,2,3,4,5,253,254,255),(0,191,192,320,351,352,32767,-32768),(0,4,8,15),(0,1)):
        yield render_row(phase,phase_frame,frame,damage)
    for age,big_frame,offset in itertools.product((0,30,31,32,255),(0,1,6,7,8,14,15,32767,-32768),(0,32,224,255)):
        yield render_row(big_frame=big_frame,e=[*explosion(1,age,rx=1024,ry=2048,offset=offset),*explosion(1,age,x=32767,y=-32768,rx=32767,ry=-32768,dx=-32768,dy=32767,offset=offset),*explosion(1,age,rx=2048,ry=1024,offset=offset)])
    for x,y,large in itertools.product((-129,-128,-127,0,3072,6015,6016,6271,6272),( -129,-128,-127,0,256,1280,6015,6016),(False,True)):
        e=[*explosion(int(not large),x=x,y=y,rx=0,ry=0),*explosion(),*explosion(int(large),x=x,y=y,rx=0,ry=0)]
        yield render_row(e=e)

def circle_record(flag=1,age=0,radius=132,delta=-8):return list(struct.pack('<BB4h',flag,age,224,96,radius,delta))
def circles():
    for op,x,y,density in itertools.product(('G','S'),(-32768,-17,-16,-15,-1,0,1,32767),(-17,-16,-1,0,1,32767),(0,1,2)):
        yield [op,x,y,0,13,density,15,*circle_record(flag=0 if density!=1 else 1)]
    for op,flag,age,radius,delta in itertools.product(('U','R'),(0,1,2,255),(0,15,16,17,255),(4,132,32767,-32768),(-8,8,32767)):
        yield [op,2048,1024,0,13,2,7,*circle_record(flag,age,radius,delta)]
    for x,y,radius in itertools.product((-1,0,224,639,640),(-1,0,96,398,399,400),(0,1,4,132,332)):
        yield ['P',x,y,radius]

def compare(original,args,out,mode,rows):
    inputs=[];expected=[]
    for row in rows:
        original.reset();original.render_draws=[];original.color=0;original.raw_circle=False
        if mode=='render':
            frame,big_frame,tone,changed=row[:4]
            original.write(0x538c,'4B',frame%2,frame%4,frame%8,frame%16)
            original.u.mem_write(0x853ca,bytes(row[4:28]));original.u.mem_write(0x8bcde,bytes(row[28:44]));original.u.mem_write(0x84298,bytes(row[44:]))
            original.write(0x18d8,'h',big_frame);original.write(0x3a4,'h',tone);original.write(0x5393,'B',changed)
            original.call_args(0x6e7b,cs=0x2aaf)
            value=[original.u.mem_read(0x84298,48).hex(),*original.read(0x18d8,'h'),*original.read(0x3a4,'h'),*original.read(0x5393,'B'),*original.read(0x53dc,'B'),len(original.render_draws),*itertools.chain.from_iterable(original.render_draws)]
        elif row[0]=='P':
            _,x,y,radius=row;original.raw_circle=True;bits=bytearray(32000)
            def write(u,access,at,size,value,unused):
                if 0xa8000<=at<0xa8000+32000:
                    for byte in range(size):
                        if at-0xa8000+byte<32000:bits[at-0xa8000+byte]|=(value>>(byte*8))&255
            handle=original.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
            original.call_args(0x11ec,(radius,y,x),far=True,cs=0x2000);original.u.hook_del(handle)
            value=[bits.hex()]
        else:
            op,x,y,_,color,density,slot=row[:7];record=bytes(row[7:]);pool=bytearray()
            for i in range(16):
                e=bytearray(record);e[0]=int(density==1 or (density==2 and i%2));pool.extend(e)
            pool[slot*10:(slot+1)*10]=record;original.u.mem_write(0x89594,bytes(pool));original.write(0x4252,'B',color)
            if op in ('G','S'):original.call_args(0x1b5a if op=='G' else 0x1ba6,(y,x),far=True,cs=0x2aaf)
            elif op=='U':original.call_args(0x1bf2,cs=0x2aaf)
            elif op=='R':original.call_args(0x1c28,cs=0x2aaf)
            else:raise ValueError(op)
            value=[original.u.mem_read(0x89594,160).hex(),*original.read(0x4252,'B'),len(original.render_draws),*itertools.chain.from_iterable(d[1:] for d in original.render_draws)]
        inputs.append(' '.join(map(str,row)));expected.append(' '.join(map(str,value)))
    fixtures=out/f'{mode}-fixtures.txt';fixtures.write_text('\n'.join(inputs)+'\n');trace=out/f'{mode}-trace.txt';trace.write_text('\n'.join(expected)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),f'--{mode}-vectors',str(fixtures)]
    actual=[' '.join(line.split()) for line in subprocess.run(command,capture_output=True,text=True,check=True,env=env).stdout.splitlines()]
    for i,(a,b) in enumerate(itertools.zip_longest(expected,actual)):
        if a!=b:
            aa=a.split() if a else [];bb=b.split() if b else [];field=next((j for j,(x,y) in enumerate(zip(aa,bb)) if x!=y),min(len(aa),len(bb)))
            (out/f'{mode}-mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i],field=field,expected=aa,actual=bb),indent=2)+'\n');raise ValueError(f'{mode} case{i} field{field} differs')
    return dict(cases=len(inputs),fixture_sha256=sha(fixtures.read_bytes()),trace_sha256=sha(trace.read_bytes()))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--only',choices=('render','circle'));p.add_argument('--limit',type=int)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);original=Original(args.target.read_bytes());results={}
    for mode,rows in [('render',renders()),('circle',circles())]:
        if args.only and args.only!=mode:continue
        results[mode]=compare(original,args,out,mode,itertools.islice(rows,args.limit) if args.limit else rows)
    receipt=dict(passed=True,controls=results,target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),scope='MAIN load2000 DS8000 main01 0AAF:6E7B/2D9C/2E65 and1B5A/1BA6/1BF2/1C28. Full explosion/circle state,aging/flash clocks,ordered sprite/circle geometry; circle pixel controls execute actual original0000:11EC GRCG algorithm with default clipping.',limits='Orange sprite pixels and GRCG color hardware intercepted at draw boundaries. Circle pixels use a write-mask shadow. Host framebuffer/page/scroll/whole-route timing remain separate; no DOS exact promotion.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
