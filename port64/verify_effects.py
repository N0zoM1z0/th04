#!/usr/bin/env python3
"""Independent original MAIN CPU controls for sparks and gather circles."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import *
from verify_bullets import BulletOriginal
from probe_assets import main_assets
sha=lambda data:hashlib.sha256(data).hexdigest()

class Original(BulletOriginal):
    def hook(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if (cs,ip)==(0x33a9,0xf102):
            self.releases.append(list(u.mem_read(0x853a2,18)))
        # Execute the original effect callees instead of their old adapters.
        if (cs,ip) in ((0x33a9,0x39a),(0x33a9,0x27)):return
        if (cs,ip) in ((0x33a9,0x466),(0x2aaf,0x1672)):
            self.color=(u.reg_read(UC_X86_REG_AX)>>8)&255
            ret=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0];u.reg_write(UC_X86_REG_SP,sp+2);u.reg_write(UC_X86_REG_IP,ret);return
        if self.capture_draws and (cs,ip) in ((0x33a9,0x1008),(0x2aaf,0x1710)):
            x=u.reg_read(UC_X86_REG_AX);x=x if x<32768 else x-65536;y=u.reg_read(UC_X86_REG_DX)
            self.effect_draws.extend((x,y,self.color if cs==0x33a9 else u.reg_read(UC_X86_REG_CX)&7))
            ret=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0];u.reg_write(UC_X86_REG_SP,sp+2);u.reg_write(UC_X86_REG_IP,ret);return
        super().hook(u,address,size,unused)
    def __init__(self,target):
        self.capture_draws=False;self.effect_draws=[];self.releases=[];self.color=0;super().__init__(target)
    def call_args(self,ip,args=(),far=False,cs=0x33a9):
        for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x8000),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000),(UC_X86_REG_EFLAGS,2)):self.u.reg_write(reg,value)
        stack=[0xf000]+([cs] if far else [])+list(args)
        self.u.mem_write(0x7e000,struct.pack('<'+'H'*len(stack),*[x&65535 for x in stack]))
        self.u.emu_start(cs*16+ip,cs*16+0xf000,count=2000000)
        if self.u.reg_read(UC_X86_REG_IP)!=0xf000 or self.u.reg_read(UC_X86_REG_SP)!=0xe000+len(stack)*2:raise ValueError(f'original effect ABI/return failed {cs:04X}:{ip:04X}')

def spark(flag=0,age=0,x=2048,y=1024,vx=17,vy=-19,angle=0xab41):
    return list(struct.pack('<BB6hH',flag,age,x,y,777,888,vx,vy,angle))
def bullet(spawn=1):return list(struct.pack('<BB4h8B',spawn,52,2048,1024,17,-19,46,64,42,3,6,123,128,19))
def gather(flag=0,radius=1024,delta=32,points=8,spawn=1,x=2048,y=1024):
    return list(struct.pack('<BB6h2h2B',flag,9,x,y,777,888,17,-19,radius,points,255,2))+bullet(spawn)+list(struct.pack('<hh',666,delta))
def shape(radius=1024,points=8):return list(struct.pack('<6h2B',2048,1024,17,-19,radius,points,13,129))

def fixtures():
    for seed,high,offset in itertools.product((0,1,318,0x7fffffff,0x80000000,0xffffffff),(0,0x12,0xff),(0,0x12ff,0xffff)):
        yield ['I',seed,offset,2,7,*spark(angle=high<<8|19),2048,1024,32,8]
    for index,(op,offset,density,count,radius) in enumerate(itertools.product(('R','C'),(0,16,1504,1520),(0,1,2),(1,2,8,48,96,97,255,256,257,512),(0,32,-32768,32767))):
        yield [op,1,offset,density,7,*spark(flag=1 if density==1 else 0),2048,1024,radius,count]
    # Signed/unsigned clipping boundaries, including inclusive width/height.
    for op,x,y in itertools.product(('R','C'),(-1,0,6144,6145),(0,5888,5889,-1)):
        yield [op,1,1520,0,7,*spark(),x,y,32,2]
    yield ['R',1,0,0,7,*spark(),2048,1024,32,0]
    for flag,age,x,y,velocity in itertools.product((0,1,2,255),(0,39,40,41,255),(-65,-64,-63,6207,6208,32767),(1024,5951,5952),(0,1,-128)):
        yield ['S',1,16,0,0,*spark(flag,age,x,y,velocity,velocity),2048,1024,32,8]
    for age,x,y in itertools.product(range(8),(-64,-63,0,2048,6207),(0,1024,5951)):
        yield ['D',1,0,0,0,*spark(1,age,x,y,0,0),2048,1024,32,8]
    for op,density,radius,points in itertools.product(('G','O'),(0,1,2),(0,31,32,1024,-32768,32767),(0,8,255)):
        yield [op,density,15,*gather(0 if density!=1 else 1),*shape(radius,points),*bullet()]
    for flag,radius,delta,spawn in itertools.product((0,1,2,255),(0,31,32,33,1024,-32768,32767),(-32768,-32,0,1,32,32767),(0,1,2)):
        yield ['U',0,15,*gather(flag,radius,delta,spawn=spawn),*shape(),*bullet()]
    for points,radius,x,y in itertools.product((0,1,8,16,127,128,129,255),(-32,0,1024),(0,2048,6144),(0,1024,5888)):
        yield ['P',0,0,*gather(1,radius,32,points,x=x,y=y),*shape(),*bullet()]

def run(args,*options):
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    return subprocess.run(([args.runner] if args.runner else [])+[str(args.exe.resolve()),*map(str,options)],env=env,capture_output=True,text=True,check=True).stdout

def pixels(original,args):
    native=list(map(int,run(args,'--pixels').split()));assert len(native)==576
    cases=0
    for cel,shift,top in itertools.product(range(9),range(8),(0,1,100,394,395,396,397,398,399)):
        original.reset();original.capture_draws=False;original.u.reg_write(UC_X86_REG_ES,0xa800)
        original.u.reg_write(UC_X86_REG_AX,32+shift);original.u.reg_write(UC_X86_REG_DX,top);original.u.reg_write(UC_X86_REG_CX,cel)
        screen=bytearray(640*400)
        def write(u,access,at,size,value,unused):
            if 0xa8000<=at<0xa8000+32000:
                for byte in range(size):
                    offset=at-0xa8000+byte
                    for bit in range(8):
                        if value&(1<<(byte*8+7-bit)):screen[offset*8+bit]=1
        hook=original.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
        original.call_args(0x1710 if cel<8 else 0x1008,cs=0x2aaf if cel<8 else 0x33a9)
        original.u.hook_del(hook)
        expected=[screen[((top+y)%400)*640+32+shift+x] for y in range(8) for x in range(8)]
        if expected!=native[cel*64:(cel+1)*64]:raise ValueError(f'original glyph differs cel{cel}/shift{shift}/top{top}')
        cases+=1
    return dict(cases=cases,indexed_masks_sha256=sha(bytes(native)),scope='8 original spark cels and gather pellet, 8 alignments x9 Y/roll positions; GRCG mask shadow, not full host edge clipping.')

def joint(original,args,out):
    if not args.hdi:return []
    standard=main_assets(args.hdi)['ST00.STD'];path=out/'ST00.STD';path.write_bytes(standard)
    at=3+standard[2];at+=1+standard[at];count=standard[at];at+=1;offsets=[]
    for i in range(count):length=standard[at];at+=1;offsets.append(at-3);at+=length
    at+=1;receipts=[]
    for rank in (1,3):
        original.reset();original.capture_draws=False;original.script_offsets=offsets;original.u.mem_write(0x90000,standard[3:]);original.write(0x918,'H',0x9000)
        for i,offset in enumerate(offsets):original.write(0x3d7a+i*2,'H',offset)
        original.write(0x3dba,'HH',at-3,0x9000);original.write(0x4646,'HH',0x4341,0x33a9)
        original.write(0xbcc4,'H',0x9453 if rank==3 else 0x9440);original.write(0xbcc0,'H',0x94a2 if rank==3 else 0x9486)
        original.write(0x4662,'B',0);original.write(0x53a0,'B',1);original.write(0x3e2,'I',0x1234)
        original.write(0xbcbe,'H',250);original.call_args(0x1824,cs=0x2aaf);rows=[]
        for frame in range(1200):
            original.context(rank,22 if rank==3 else 16,16 if frame%3==0 else 0,3072,5120)
            original.write(0x538a,'H',frame);original.write(0x538c,'BB',frame%2,frame%4);original.write(0x5390,'H',1)
            original.call(0x4341,far=True);original.call_args(0x1776,cs=0x2aaf)
            original.u.mem_write(0x8b55e,bytes(68*18));original.u.mem_write(0x844a6,bytes(68*6));original.write(0x463e,'H',0)
            for i in range(32):
                record=original.u.mem_read(0x88a92+i*64,64)
                if record[0]==1:
                    x,y=struct.unpack_from('<hh',record,2)
                    original.write(0xb55e,'BB6hHBB',1,0,x,y,0,0,0,0,0,2,0)
                    original.write(0x44a6,'hhH',x,y,0xb55e);original.write(0x463e,'H',1);break
            if frame%96==0:
                original.write(0x53a2,'BB4h8B',3,52,2048,1024,0,0,27,129,42,6,6,0,0,0)
                original.call(0x9453 if rank==3 else 0x9440);original.call(0x94a2 if rank==3 else 0x9486)
            original.call(0x8e38,far=True);original.call(0x43c9,far=True);original.call_args(0x13e,far=True);original.call(0x5c23,cs=0x2aaf)
            hashes=[]
            for records in (original.normalized_pool(),original.u.mem_read(0x85a22,440*26),original.u.mem_read(0x853e2,96*16),original.u.mem_read(0x89292,16*42)):
                value=2166136261
                for byte in records:value=((value^byte)*16777619)&0xffffffff
                hashes.append(value)
            row=[frame,*hashes[:2],*original.read(0x3ecc,'H'),*original.read(0x1b5e,'HH'),*original.read(0x435a,'I'),*original.read(0x4669,'B'),*original.template(),*hashes[2:],*original.read(0x41f4,'H'),*original.read(0xbcbc,'H'),*original.read(0x4640,'B')]
            rows.append(row)
        env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
        command=([args.runner] if args.runner else [])+[str(args.bullet_exe.resolve()),'--stage-effects',str(path),str(rank),'1200']
        got=[list(map(int,row.split())) for row in subprocess.run(command,env=env,capture_output=True,text=True,check=True).stdout.splitlines()]
        if got!=rows:
            index=next((i for i,(a,b) in enumerate(zip(rows,got)) if a!=b),min(len(rows),len(got)))
            (out/'joint-mismatch.json').write_text(json.dumps(dict(rank=rank,frame=index,expected=rows[index] if index<len(rows) else None,actual=got[index] if index<len(got) else None),indent=2)+'\n');raise ValueError(f'joint effect frame differs {rank}/{index}')
        trace=out/f'joint-rank{rank}.txt';trace.write_text('\n'.join(' '.join(map(str,row)) for row in rows)+'\n')
        receipts.append(dict(rank=rank,frames=1200,std_sha256=sha(standard),trace_sha256=sha(trace.read_bytes()),scope='Controlled integration: one targeted shot-cache entry each frame and a gather producer every96 frames. Actual original spark/gather/tune/add/shot-hit callees execute; drops/HUD/audio/graphics intercepted. Not ordinary gameplay.'))
    return receipts

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--operation');p.add_argument('--limit',type=int);p.add_argument('--hdi',type=Path);p.add_argument('--bullet-exe',type=Path);p.add_argument('--joint-only',action='store_true')
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);original=Original(args.target.read_bytes());inputs=[];expected=[];counts={}
    for row in fixtures():
        if args.joint_only:break
        op=row[0]
        if args.operation and op not in args.operation:continue
        if args.limit and len(inputs)>=args.limit:break
        original.reset();original.capture_draws=op in ('D','P');original.effect_draws=[];original.events=[];original.releases=[]
        if op in ('I','R','C','S','D'):
            seed,offset,density,slot=row[1:5];record=bytearray(row[5:21]);x,y,radius,count=row[21:]
            pool=bytearray()
            for i in range(96):
                e=bytearray(record);struct.pack_into('<H',e,14,(struct.unpack_from('<H',e,14)[0]+i*19)&65535);e[0]=int(bool(density) and not(density==2 and i%2==0));pool.extend(e)
            pool[slot*16:(slot+1)*16]=record
            original.u.mem_write(0x853e2,bytes(pool));original.write(0x41f4,'H',offset);original.write(0x3e2,'I',seed)
            if op=='I':original.call_args(0x1824,cs=0x2aaf)
            if op=='R':original.call_args(0x39a,(count,radius,y,x),far=True)
            if op=='C':original.call_args(0x3fc,(count,radius,y,x))
            if op=='S':original.call_args(0x1776,cs=0x2aaf)
            if op=='D':original.call_args(0x17c2,cs=0x2aaf)
            values=original.effect_draws if op=='D' else [*original.u.mem_read(0x853e2,96*16),*original.read(0x41f4,'H'),*original.read(0x3e2,'I'),*original.read(0x3ecc,'H')]
        else:
            density,slot=row[1:3];record=bytes(row[3:45]);template=bytes(row[45:59]);shot=bytes(row[59:77]);pool=bytearray()
            for i in range(16):
                e=bytearray(record);e[0]=int(bool(density) and not(density==2 and i%2==0));pool.extend(e)
            pool[slot*42:(slot+1)*42]=record
            original.u.mem_write(0x89292,bytes(pool));original.u.mem_write(0x89586,template);original.u.mem_write(0x853a2,shot)
            original.write(0xbcc0,'H',0xf102)
            if op=='G':original.call_args(0x27)
            if op=='O':original.call_args(0x91)
            if op=='U':original.call_args(0x13e,far=True)
            if op=='P':original.call_args(0x1cc,far=True)
            values=list(original.effect_draws) if op=='P' else [*original.u.mem_read(0x89292,16*42),len(original.events)]
            if op=='U':
                # The intercepted regular wrapper sees the restored full
                # template and the UPDATED gather center, without rank tuning.
                # Parent adapter records selected fields; capture full copies
                # at the f102 call below instead of reconstructing them here.
                values=[*original.u.mem_read(0x89292,16*42),len(original.releases),*itertools.chain.from_iterable(original.releases)]
        inputs.append(' '.join(map(str,row)));expected.append(values);counts[op]=counts.get(op,0)+1
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n');actual=[list(map(int,row.split())) for row in run(args,'--vectors',fixture).splitlines()]
    if len(actual)!=len(expected):raise ValueError('effect checkpoint count differs')
    for i,(want,got) in enumerate(zip(expected,actual)):
        if want!=got:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i],expected=want,actual=got),indent=2)+'\n');raise ValueError(f'effect checkpoint{i} differs')
    trace='\n'.join(' '.join(map(str,row)) for row in expected)+'\n';(out/'vectors.txt').write_text(trace)
    if args.hdi and not args.bullet_exe:p.error('--hdi requires --bullet-exe')
    coupled=joint(original,args,out)
    glyphs=pixels(original,args)
    original.reset();original.write(0x41f4,'H',0)
    try:original.call_args(0x3fc,(0,32,1024,2048))
    except unicorn.UcError as error:
        cs=original.u.reg_read(UC_X86_REG_CS);ip=original.u.reg_read(UC_X86_REG_IP)
        if bytes(original.u.mem_read(cs*16+ip,3))!=b'\xf7\x76\x04':raise ValueError('zero-circle fault is outside DIV count') from error
        negative=dict(cs=cs,ip=ip,error=str(error),instruction='DIV word ptr [BP+4]')
    else:raise ValueError('original zero spark circle did not fault')
    receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),counts=counts,target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.encode()),glyphs=glyphs,joint_traces=coupled,joint_native_sha256=sha(args.bullet_exe.read_bytes()) if args.bullet_exe else None,hdi_sha256=sha(args.hdi.read_bytes()) if args.hdi else None,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),zero_circle_negative=negative,unicorn_version=unicorn.__version__,scope='Relocated MAIN load2000 DS8000: spark init/add/circle/update/render and gather add/only/update/render. Full packed state, LCG/ring cursor, releases and glyph controls.',limits='Isolated gather-release regular wrapper intercepted; joint controls execute it with injected shot/gather inputs. No bosses, full routes, natural timing or full host edge clipping. Zero spark circle guarded in host.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
