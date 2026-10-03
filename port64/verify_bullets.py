#!/usr/bin/env python3
"""Compare native enemy bullet tuning/spawn/update against relocated original MAIN CPU."""
import argparse
from datetime import datetime,timezone
import hashlib,itertools,json,os,struct,subprocess
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_ES
from verify_enemy import Original
from probe_assets import main_assets

sha=lambda b:hashlib.sha256(b).hexdigest()
GROUPS=(0,1,26,27,28,29,38,44,45,46,47,48,64,65)

class BulletOriginal(Original):
    def hook(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if (cs,ip)==(0x2aaf,0x45a1):
            ret,seg=struct.unpack('<HH',u.mem_read(0x70000+sp,4));u.reg_write(UC_X86_REG_SP,sp+4)
            u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_IP,ret);return
        if cs==0x33a9 and ip==0x31a:
            ret,value,y,x=struct.unpack('<HHhh',u.mem_read(0x70000+sp,8))
            self.events.append([1,x,y,value,0]);u.reg_write(UC_X86_REG_SP,sp+8)
            u.reg_write(UC_X86_REG_IP,ret);return
        if cs==0x33a9 and ip==0x27:
            ret=struct.unpack('<H',u.mem_read(0x70000+sp,2))[0]
            t=self.template();self.events.append([3,t[2],t[3],1024,8,*t])
            u.reg_write(UC_X86_REG_SP,sp+2);u.reg_write(UC_X86_REG_IP,ret);return
        before=len(self.events);super().hook(u,address,size,unused)
        if len(self.events)>before and self.events[-1][0]==4:
            _,x,y,radius,count=self.events[-1];self.events[-1]=[0,x,y,radius,count]

    def template(self):return list(self.read(0x53a2,'BB4h8B'))


def seed(flag=1):
    e=bytearray(26);e[0]=flag;e[1]=255
    struct.pack_into('<6h',e,2,3072,1800,3000,1700,-19,128)
    e[14:24]=bytes((46,123,42,64,0,2,128,42,32,30));struct.pack_into('<H',e,24,52)
    return e


def fixtures():
    for group,rank,perf,count,delta in itertools.product(GROUPS,range(5),(0,4,6,10,16,20,24,34,127,255),(0,1,2,3,5,6,48,127,255),(0,6,255)):
        yield ('T',[rank,perf,3072,5120,0,0,0,250],[1,52,2048,1024,17,-19,group,129,42,count,delta,123,128,19],None)
    # Descending allocation, all groups/ranks, byte speed edges, clouds,
    # sparse/full/final-slot pools, clear/zap suppression and fixed speeds.
    for index,(group,rank,spawn,speed,density,fixed) in enumerate(itertools.product(GROUPS,range(5),(1,2,4,5),(7,42,128,255),(0,1,2,3),(False,True))):
        context=[rank,22 if rank==3 else 16,3072,5120,index%2,0,0,250]
        t=[spawn,76 if index%2 else 52,2048,1024,17,-19,group,129,speed,6,6,123,128,19]
        e=seed(0 if density!=1 else 1);slot=239 if spawn==1 else 439
        yield ('A',context,t,[0,0,3,17,0,1,density,slot,*e,0,int(fixed)])
    # Special producers and template clipping/clear-time boundaries.
    for index,(spawn,special,clear,zap,x,y) in enumerate(itertools.product((1,2,3,4,5),(False,True),(0,1,17,18,255),(0,1),(-129,-128,-127,2048,6271,6272),(1024,5120))):
        t=[spawn,52,x,y,17,-19,46,64,42,3,6,123,131,19]
        yield ('A',[1,16,3072,5120,0,0,0,250],t,[clear,zap,3,17,0,1,0,239,*seed(0),int(special),0])
    # Every special motion: unsigned speed/counter and signed angle deltas,
    # corner double-bounces, gravity parity, deceleration multiplication.
    for index,(special,speed,x,y,mod2) in enumerate(itertools.product(range(128,137),(0,1,2,31,32,255),(-1,0,3072,6144),(0,1800,5888),(0,1))):
        e=seed();e[16]=speed;e[19]=1;e[20]=special;e[22]=255;e[23]=129
        struct.pack_into('<hh',e,2,x,y)
        yield ('U',[1,16,3072,5120,mod2,1,0,250],[1,52,2048,1024,0,0,46,64,42,3,6,0,128,0],[0,0,2,17,0,1,0,239,*e])
    for index,(slot,flag,phase,movement,clear,zap,invincibility) in enumerate(itertools.product((0,439),(0,1,2),(0,1,2,3,4,19,20,255),(0,2,4,19,20),(0,1,18,255),(0,1,16),(0,1))):
        e=seed(flag);e[18]=phase;e[19]=movement
        struct.pack_into('<hh',e,2,3072,5120);struct.pack_into('<hh',e,10,0,0)
        yield ('U',[index%5,16,3072,5120,index%2,invincibility,index%2,250],[1,52,2048,1024,0,0,46,64,42,3,6,0,128,0],[clear,zap,2,17,999 if index%3==0 else 0,1,0,slot,*e])
    # Complete-pool count policy and zap polynomial/cap/ordered rewards.
    for rank,mod2,turbo,zap in itertools.product(range(5),(0,1),(0,1),(0,1,15,16,255)):
        yield ('U',[rank,22,3072,5120,mod2,1,turbo,250],[1,52,2048,1024,0,0,46,64,42,3,6,0,128,0],[0,zap,2,17,0,1,1,239,*seed()])


def joint_control(original,args,out):
    if not args.hdi:return []
    standard=main_assets(args.hdi)['ST00.STD'];path=out/'ST00.STD';path.write_bytes(standard)
    at=3+standard[2];at+=1+standard[at];count=standard[at];at+=1;offsets=[]
    for i in range(count):length=standard[at];at+=1;offsets.append(at-3);at+=length
    at+=1;receipts=[]
    for rank in (1,3):
        original.reset();original.script_offsets=offsets;original.u.mem_write(0x90000,standard[3:]);original.write(0x918,'H',0x9000)
        for i,off in enumerate(offsets):original.write(0x3d7a+i*2,'H',off)
        original.write(0x3dba,'HH',at-3,0x9000);original.write(0x4646,'HH',0x4341,0x33a9)
        original.write(0xbcc4,'H',0x9453 if rank==3 else 0x9440);original.write(0xbcc0,'H',0x94a2 if rank==3 else 0x9486)
        original.write(0x4662,'B',1);original.write(0x53a0,'B',1);rows=[]
        for frame in range(1200):
            original.events.clear();original.context(rank,22 if rank==3 else 16,16 if frame%3==0 else 0,3072,5120)
            original.write(0x538a,'H',frame);original.write(0x538c,'BB',frame%2,frame%4);original.write(0x5390,'H',1)
            original.call(0x4341,far=True);original.call(0x8e38,far=True);original.call(0x43c9,far=True);original.call(0x5c23,cs=0x2aaf)
            hashes=[]
            for records in (original.normalized_pool(),original.u.mem_read(0x85a22,440*26)):
                digest=2166136261
                for byte in records:digest=((digest^byte)*16777619)&0xffffffff
                hashes.append(digest)
            row=[frame,*hashes,*original.read(0x3ecc,'H'),*original.read(0x1b5e,'HH'),*original.read(0x435a,'I'),*original.read(0x4669,'B'),*original.template()]
            rows.append(row)
        env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
        command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--stage',str(path),str(rank),'1200']
        got=[list(map(int,line.split())) for line in subprocess.run(command,capture_output=True,text=True,check=True,env=env).stdout.splitlines()]
        if got!=rows:
            index=next((i for i,(x,y) in enumerate(zip(rows,got)) if x!=y),min(len(rows),len(got)))
            (out/'joint-mismatch.json').write_text(json.dumps(dict(rank=rank,frame=index,expected=rows[index],actual=got[index]),indent=2)+'\n')
            raise ValueError(f'joint original STD/enemy/bullet frame differs: {rank}/{index}')
        trace=out/f'joint-rank{rank}.txt';trace.write_text('\n'.join(' '.join(map(str,row)) for row in rows)+'\n')
        receipts.append(dict(rank=rank,frames=1200,std_sha256=sha(standard),trace_sha256=sha(trace.read_bytes())))
    return receipts


def pellet_control(original,args,out):
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--pellet-pixels']
    native=list(map(int,subprocess.run(command,capture_output=True,text=True,check=True,env=env).stdout.split()))
    if len(native)!=64:raise ValueError('pellet must have 64 indexed pixels')
    cases=0
    for shift,top in itertools.product(range(8),(0,1,100,394,395,396,397,398,399)):
        original.reset();original.write(0xbcc6,'H',1);original.write(0x86d2,'hh',32+shift,top)
        original.u.reg_write(UC_X86_REG_ES,0xa800);pixels=bytearray(640*400);color=[15]
        def write(u,access,at,size,value,unused):
            if 0xa8000<=at<0xa8000+32000:
                for byte in range(size):
                    offset=at-0xa8000+byte
                    for bit in range(8):
                        if value & (1<<(byte*8+7-bit)):pixels[offset*8+bit]=color[0]
        handle=original.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,write)
        original.call(0x1eac,cs=0x2aaf);color[0]=9;original.call(0x1f3e,cs=0x2aaf)
        original.u.hook_del(handle)
        expected=[pixels[((top+y)%400)*640+32+shift+x] for y in range(8) for x in range(8)]
        if expected!=native:raise ValueError(f'original pellet pixels differ at shift {shift}/top {top}')
        cases+=1
    return dict(cases=cases,pixels=64,pixels_sha256=sha(bytes(native)),scope='Original main_01 0AAF:1EAC/1F3E with GRCG write-mask shadow, 8 alignments and 9 Y/roll positions. Glyph pixels, not host edge clipping.')


def empty_ring_control(original):
    rows=[]
    for group in (38,44):
        original.reset();original.context(1,16,0,3072,5120)
        original.write(0x53a2,'BB4h8B',1,52,2048,1024,0,0,group,0,42,0,0,0,0,0)
        try:original.call(0x9486)
        except unicorn.UcError as error:
            cs=original.u.reg_read(UC_X86_REG_CS);ip=original.u.reg_read(UC_X86_REG_IP)
            if cs!=0x33a9 or bytes(original.u.mem_read(cs*16+ip,2))!=b'\xf7\xfb':raise ValueError('empty-ring control failed outside IDIV BX') from error
            rows.append(dict(group=group,cs=cs,ip=ip,error=str(error),instruction='IDIV BX'))
        else:raise ValueError('original count-zero ring did not raise CPU exception')
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True)
    p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--hdi',type=Path);p.add_argument('--joint-only',action='store_true');p.add_argument('--limit',type=int);p.add_argument('--operation',choices=('T','A','U'))
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    original=BulletOriginal(args.target.read_bytes());inputs=[];expected=[];counts={}
    tune_entry=(0x9435,0x9440,0x9448,0x9453,0x9440)
    for index,(op,c,t,extra) in enumerate(fixtures()):
        if args.joint_only:break
        if args.operation and op!=args.operation:continue
        if args.limit and len(inputs)>=args.limit:break
        original.reset();original.context(c[0],c[1],0,c[2],c[3]);original.write(0x538c,'B',c[4])
        original.write(0x4662,'B',c[5]);original.write(0x53a0,'B',c[6]);original.write(0xbcbe,'H',c[7])
        original.write(0x53a2,'BB4h8B',*t);counts[op]=counts.get(op,0)+1
        if op=='T':original.call(tune_entry[c[0]])
        else:
            clear,zap,parameter,angle,graze,slowdown,density,slot=extra[:8];e=bytes(extra[8:34])
            pool=bytearray(440*26)
            for i in range(440):
                if density and (density!=3 or i%2):pool[i*26:(i+1)*26]=e;pool[i*26]=1
            pool[slot*26:(slot+1)*26]=e
            original.u.mem_write(0x85a22,bytes(pool));original.write(0xbcba,'B',clear);original.write(0xbcb9,'B',zap)
            original.write(0xbcb8,'B',angle);original.write(0xbcb7,'B',parameter)
            original.write(0xbcbc,'H',graze);original.write(0x5390,'H',slowdown)
            if op=='A':
                special,fixed=extra[34:36];original.write(0x1f38,'B',fixed)
                entries=(0x94be,0x94da,0x94f6) if special else (0x945e,0x9486,0x94a2)
                # Wrapper selection is rank-dependent; all preserve speed.
                ip=entries[0 if c[0]==0 else (2 if c[0] in (2,3) else 1)]
                original.call(ip)
            else:
                try:original.call(0x8e38,far=True)
                except Exception:
                    (out/'cpu-failure.json').write_text(json.dumps(dict(case=index,context=c,template=t,extra=extra,cs=original.u.reg_read(UC_X86_REG_CS),ip=original.u.reg_read(UC_X86_REG_IP)),indent=2)+'\n')
                    raise
        values=original.template()
        if op!='T':
            digest=2166136261
            for byte in original.u.mem_read(0x85a22,440*26):digest=((digest^byte)*16777619)&0xffffffff
            if op=='U' and original.read(0x46a2,'I')[0]:original.events.append([2,0,0,0,0])
            values.extend([digest,*original.read(0x3ecc,'H'),*original.read(0x435a,'I'),*original.read(0xbcbc,'H'),*original.read(0x5390,'H'),
                *original.read(0xbcba,'B'),*original.read(0xbcb9,'B'),*original.read(0x46a2,'I'),*original.read(0x4669,'B'),len(original.events)])
            values.extend(itertools.chain.from_iterable(original.events))
        expected.append(values)
        inputs.append(' '.join(map(str,[op,*c,*t,*(extra or [])])))
    fixture=out/'fixtures.txt';fixture.write_text('\n'.join(inputs)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all');command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--vectors',str(fixture)]
    result=subprocess.run(command,capture_output=True,text=True,check=True,env=env)
    actual=[list(map(int,row.split())) for row in result.stdout.splitlines()]
    if len(actual)!=len(expected):raise ValueError('bullet checkpoint count differs')
    for index,(want,got) in enumerate(zip(expected,actual)):
        if want!=got:
            (out/'mismatch.json').write_text(json.dumps(dict(case=index,input=inputs[index],expected=want,actual=got),indent=2)+'\n')
            raise ValueError(f'bullet checkpoint {index} differs: see mismatch.json')
    trace='\n'.join(' '.join(map(str,row)) for row in expected)+'\n';(out/'vectors.txt').write_text(trace)
    joint=joint_control(original,args,out)
    pellet=pellet_control(original,args,out);empty_rings=empty_ring_control(original)
    receipt=dict(passed=True,joint_traces=joint,pellet_pixels=pellet,empty_ring_negative=empty_rings,observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),counts=counts,
        target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),fixture_sha256=sha(fixture.read_bytes()),trace_sha256=sha(trace.encode()),
        unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
        scope='MAIN.EXE main_03 13A9 tune/wrappers/group/motion/update, load2000 DS8000. 440 packed 26-byte records checked by FNV32 with template/scalars and ordered events.',
        limits='Spark, HUD graze, point-number and gather callees intercepted. Graphics, spark RNG, gather lifecycle, full routes and natural timing excluded. Empty rings use existing native DOS guard rather than original IDIV.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
