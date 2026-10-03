#!/usr/bin/env python3
"""Independent relocated original MAIN controls for the Stage 1 midboss."""
import argparse,hashlib,itertools,json,os,struct,subprocess
from datetime import datetime,timezone
from pathlib import Path
import unicorn
from unicorn.x86_const import UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_IP,UC_X86_REG_AX
from verify_effects import Original as Base
from probe_assets import main_assets
sha=lambda b:hashlib.sha256(b).hexdigest()

class Original(Base):
    def __init__(self,target):
        self.damage=0;self.tile_probe=False;self.setup_palette=None;self.setup_files=[];super().__init__(target)
    def hook(self,u,address,size,unused):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;sp=u.reg_read(UC_X86_REG_SP)
        if self.tile_probe and cs==0x2aaf:
            if ip==0xb92:return
            if ip==0x2209:
                u.reg_write(UC_X86_REG_SP,sp+2);u.reg_write(UC_X86_REG_IP,0x220e);return
            if ip in (0xdf8,0xdfb,0xe03):
                u.reg_write(UC_X86_REG_IP,ip+(5 if ip==0xe03 else 3));return
        def event(kind,x=0,y=0,value=0,count=0):self.events.append([kind,x,y,value&65535,count&65535])
        def ret(cleanup,far=False):
            words=struct.unpack('<HH' if far else '<H',u.mem_read(0x70000+sp,4 if far else 2))
            u.reg_write(UC_X86_REG_SP,sp+cleanup)
            if far:u.reg_write(UC_X86_REG_CS,words[1])
            u.reg_write(UC_X86_REG_IP,words[0])
        if self.setup_palette is not None:
            if (cs,ip)==(0x2000,0x2a74):
                offset,segment=struct.unpack('<HH',u.mem_read(0x70000+sp+4,4))
                name=bytes(u.mem_read(segment*16+offset,16)).split(b'\0')[0].decode('ascii')
                if name.upper()!='ST00.BMT':raise ValueError('Stage 1 setup loads a different BFNT')
                self.setup_files.append(name);u.mem_write(0x82a82,self.setup_palette);ret(8,True);return
            if (cs,ip)==(0x330e,0x858):ret(12,True);return
            if (cs,ip)==(0x33a9,0xa518):ret(6);return
        if (cs,ip)==(0x2aaf,0xb92):
            vo,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+4,6));relative=vo-72
            image=(relative%1280)//2*25+relative//1280
            event(0,x,y,image);ret(10,True);return
        if (cs,ip)==(0x330e,0x7d2):
            event(1,value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]);ret(6,True);return
        if (cs,ip)==(0x33a9,0x3fc):
            count,radius,y,x=struct.unpack('<HHhh',u.mem_read(0x70000+sp+2,8));event(2,x,y,radius,count);ret(10);return
        if cs==0x33a9 and ip in (0x69e,0x73c,0x7b3):
            x,y=self.read(0x53b4,'hh');event(3,x,y)
        if (cs,ip)==(0x2aaf,0x5ac9):
            x,y,rx,ry=self.read(0x449e,'4h');event(4,x,y,rx,ry)
            u.reg_write(UC_X86_REG_AX,self.damage&65535);ret(4,True);return
        if (cs,ip)==(0x2aaf,0x45ed):
            event(5,value=struct.unpack('<H',u.mem_read(0x70000+sp+4,2))[0]);ret(6,True);return
        if (cs,ip)==(0x33a9,0x300):
            value,y,x=struct.unpack('<Hhh',u.mem_read(0x70000+sp+2,6));event(6,x,y,value);ret(8);return
        if (cs,ip)==(0x33a9,0x84a):event(7,value=4)
        if (cs,ip)==(0x33a9,0x65c8):event(8,value=12)
        if (cs,ip)==(0x33a9,0x812):event(9,value=1)
        if cs==0x33a9 and ip in (0x94be,0x94da,0x94f6):
            t=self.template();event(10,t[2],t[3],t[7],t[8])
        super().hook(u,address,size,unused)

def record(phase=0,frame=0,sprite=136,x=3072,y=1280,hp=800,damaged=19):
    return list(struct.pack('<6hHhBBhBB',x,y,3000,1200,17,2,3100,hp,sprite,phase,frame,damaged,213))
def row(op='U',rank=1,perf=16,frame=0,scroll=16,line=100,speed=2,active=1,scrolling=1,hpbar=42,vram=97,angle=241,defeat=255,density=0,damage=0,state=None):
    return [op,rank,perf,frame,scroll,line,speed,active,scrolling,hpbar,vram,angle,defeat,density,damage,*(state or record())]
def fixtures():
    for frame,scroll,line in itertools.product((0,286,287,288,32767,-32768),(0,16,128),(0,100,399)):
        yield row(scroll=scroll,line=line,state=record(frame=frame))
    for phase,frame,sprite,damage in itertools.product((1,2),(0,7,23,24,95,96,32767),(136,139,140,146),(0,1,800)):
        yield row(damage=damage,state=record(phase,frame,sprite))
    for rank,perf,frame,density in itertools.product(range(5),(0,16,22,255),(0,7,15,32767),(0,1)):
        yield row(rank=rank,perf=perf,density=density,state=record(3,frame,146))
    for damage,hp,y,speed in itertools.product((0,1,800,65535,32768),(1,800),(4093,4094),(2,3)):
        yield row(damage=damage,speed=speed,state=record(3,7,146,y=y,hp=hp))
    for phase,frame,sprite in itertools.product((254,255,17),(0,15,31,127,32767),(4,11,255)):
        yield row(state=record(phase,frame,sprite))
    for op,frame,active in itertools.product(('A','R'),(3099,3100,3101,65535),(0,1)):
        yield row(op,frame=frame,active=active,state=record(3,99))
    for phase,frame,line,scrolling in itertools.product((0,1,2,3,254,255),(0,15,47,48,127,2048,-32768),(0,399),(0,1)):
        yield row('D',frame=65535,line=line,scrolling=scrolling,state=record(phase,frame,146))
    for x,y,angle in itertools.product((-256,0,6144,6400),(-256,0,5888,6144),(0,17,255)):
        yield row('D',defeat=angle,state=record(254,48,4,x=x,y=y))

def checkpoint(original):
    values=[original.u.mem_read(0x853b4,22).hex(),*original.read(0x46b2,'B'),*original.read(0x1ed0,'h'),*original.read(0x4256,'h'),*original.read(0x4254,'B'),*original.read(0x1ed2,'B'),*original.read(0x435a,'I'),*original.read(0x3ecc,'H'),*original.read(0xbcb9,'B'),*original.template(),original.u.mem_read(0x85a22,440*26).hex(),len(original.events),*itertools.chain.from_iterable(original.events),len(original.draws),*itertools.chain.from_iterable(original.draws)]
    return ' '.join(map(str,values))
def tile_controls(original,args,out):
    if not args.hdi:return None
    assets=main_assets(args.hdi);standard=assets['ST00.STD'];map_data=assets['ST00.MAP']
    for name in ('ST00.STD','ST00.MAP'):(out/name).write_bytes(assets[name])
    original.reset();original.tile_probe=True;original.u.mem_write(0x90000,map_data[8:]);original.u.mem_write(0x98000,standard[3:2+int.from_bytes(standard[:2],'little')])
    original.write(0x918,'H',0x9800);original.write(0x46fe,'H',0x9000)
    for i in range(32):original.write(0x93a+i*2,'H',i*320)
    original.call_args(0xfb2,cs=0x2aaf)
    order_count=standard[2];original.write(0x4276,'BBHB',0,standard[3+order_count],0,0);original.write(0x427c,'B',1)
    original.write(0x3dbe,'B',0);original.write(0x3dc4,'B',0);original.write(0x3dc0,'H',0)
    original.write(0x5380,'H',4);original.write(0x5382,'B',0)
    original.write(0x5384,'H',order_count+5)
    frames=(0,1,128,1024,3100,3387);snapshots={}
    for frame in range(max(frames)+1):
        if frame in frames:snapshots[frame]=bytes(original.u.mem_read(0x80000,65536))
        if frame<max(frames):original.call_args(0x21e6,cs=0x2aaf)
    inputs=[];expected=[]
    for frame,x,y,image in itertools.product(frames,(0,255,256,2816,6143),(-256,-1,0,1312,5888),(40,42,59)):
        original.u.mem_write(0x80000,snapshots[frame]);vo=72+2*(image//25)+1280*(image%25)
        original.call_args(0xb92,(vo,y,x),far=True,cs=0x2aaf)
        normalized=bytearray()
        for r in range(25):
            for value in original.read(0x4d40+r*64,'24H'):
                relative=value-72;image_id=(relative%1280)//2*25+relative//1280;normalized.extend(struct.pack('<H',image_id))
        expected.append(f'{original.read(0x4278,"H")[0]} {normalized.hex()}');inputs.append(f'{frame} {x} {y} {image}')
    path=out/'tile-fixtures.txt';path.write_text('\n'.join(inputs)+'\n');env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--tile-vectors',str(out/'ST00.MAP'),str(out/'ST00.STD'),str(path)]
    actual=[' '.join(line.split()) for line in subprocess.run(command,capture_output=True,text=True,check=True,env=env).stdout.splitlines()]
    if actual!=expected:
        index=next((i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b),min(len(expected),len(actual)))
        (out/'tile-mismatch.json').write_text(json.dumps(dict(case=index,input=inputs[index],expected=expected[index],actual=actual[index]),indent=2)+'\n');raise ValueError(f'original tile write differs case{index}')
    trace='\n'.join(expected)+'\n';(out/'tile-trace.txt').write_text(trace)
    return dict(cases=len(inputs),fixture_sha256=sha(path.read_bytes()),trace_sha256=sha(trace.encode()),map_sha256=sha(map_data),std_sha256=sha(standard),scope='Actual original initial-fill/scroll driver/tile setter 0AAF:0FB2/21E6/0B92, six scroll checkpoints, complete25x24 ring; EGC/GDC pixel calls intercepted.')
def setup_controls(original,args):
    if not args.hdi:return None
    assets=main_assets(args.hdi);bfnt=assets['ST00.BMT'];palette=bfnt[32:80]
    original.reset();original.tile_probe=False;original.setup_files=[]
    # The file-loader adapter supplies independently decoded B/R/G palette
    # bytes. Execute the ACTUAL stage setup after it returns, including both
    # color-zero overrides; this is not a replay of the BFNT loader itself.
    rgb=bytes(v for i in range(16) for v in (palette[i*3+1],palette[i*3+2],palette[i*3]))
    original.setup_palette=rgb;original.call_args(0xa55f,far=True)
    expected=bytearray(rgb);expected[0]=255;expected[1]=255
    observed=bytes(original.u.mem_read(0x82a82,48))
    if observed!=expected or len(original.setup_files)!=1:raise ValueError('Stage 1 palette setup disagrees')
    expected_state=struct.pack('<6hHhBBhBB',3072,5888,3072,5888,0,16,3100,800,0,0,0,0,0)
    if original.u.mem_read(0x853b4,22)!=expected_state:raise ValueError('Stage 1 initial midboss state differs')
    original.setup_palette=None
    return dict(passed=True,loaded_files=original.setup_files,bfnt_sha256=sha(bfnt),width=64,height=32,patterns=12,installed_palette_sha256=sha(observed),color_zero_rgb=list(observed[:3]),scope='Original13A9:A55F stage1_setup executes with BFNT palette adapter; CDG/BB loaders intercepted. State22 bytes and palette overrides, not complete resource loader replay.')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,required=True);p.add_argument('--exe',type=Path,required=True);p.add_argument('--runner');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--hdi',type=Path)
    args=p.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);original=Original(args.target.read_bytes());inputs=[];expected=[];counts={}
    tune=(0x9435,0x9440,0x9448,0x9453,0x9440);add=(0x94be,0x94da,0x94f6,0x94f6,0x94da)
    for i,fixture in enumerate(fixtures()):
        op,rank,perf,frame,scroll,line,speed,active,scrolling,hpbar,vram,angle,defeat,density,damage=fixture[:15];original.reset();original.damage=damage
        original.context(rank,perf,0,3072,5120);original.u.mem_write(0x853b4,bytes(fixture[15:]));original.u.mem_write(0x85a22,bytes([1 if density else 0]+[0]*25)*440)
        original.write(0x53a2,'BB4h8B',1,52,2048,1024,17,-19,46,129,42,3,6,123,128,19)
        original.write(0xbcc4,'H',tune[rank]);original.write(0xbcc2,'H',add[rank]);original.write(0xbcba,'BB',0,0);original.write(0xbcb7,'BBB',0,0,0)
        original.write(0x46b2,'B',active);original.write(0x538a,'H',frame);original.write(0x4276,'BBh',scroll,speed,line);original.write(0x427c,'B',scrolling)
        original.write(0x1ed0,'h',hpbar);original.write(0x4256,'h',vram);original.write(0x4254,'B',angle);original.write(0x1ed2,'B',defeat);original.write(0x435a,'I',0)
        if op=='U':original.call_args(0x587,far=True)
        elif op=='A':original.call_args(0x6454,far=True)
        elif op=='R':original.call_args(0x642c,far=True)
        elif op=='D':original.call_args(0x1c88,cs=0x2aaf)
        expected.append(checkpoint(original));inputs.append(' '.join(map(str,fixture)));counts[op]=counts.get(op,0)+1
    fixture_path=out/'fixtures.txt';fixture_path.write_text('\n'.join(inputs)+'\n');env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([args.runner] if args.runner else [])+[str(args.exe.resolve()),'--vectors',str(fixture_path)]
    actual=[' '.join(line.split()) for line in subprocess.run(command,capture_output=True,text=True,check=True,env=env).stdout.splitlines()]
    if len(actual)!=len(expected):raise ValueError('midboss checkpoint count differs')
    for i,(want,got) in enumerate(zip(expected,actual)):
        if want!=got:
            a,b=want.split(),got.split();different=next(j for j,(x,y) in enumerate(zip(a,b)) if x!=y) if any(x!=y for x,y in zip(a,b)) else min(len(a),len(b))
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,input=inputs[i],field=different,expected=a,actual=b),indent=2)+'\n');raise ValueError(f'midboss case{i} field{different} differs')
    trace='\n'.join(expected)+'\n';(out/'trace.txt').write_text(trace)
    tile_receipt=tile_controls(original,args,out)
    setup_receipt=setup_controls(original,args)
    receipt=dict(passed=True,counts=counts,tiles=tile_receipt,setup=setup_receipt,target_sha256=sha(original.target),native_sha256=sha(args.exe.read_bytes()),fixture_sha256=sha(fixture_path.read_bytes()),trace_sha256=sha(trace.encode()),unicorn_version=unicorn.__version__,unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),observed_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),scope='Original MAIN load2000 DS8000:13A9:0587/0522/642C/6454/6486/64DE/65B7 and0AAF:1C88/6FAA. Complete22-byte state,440x26-byte bullet pool,full scratch,HP/global angles,RNG cursor,ordered events/draws.',limits='Shot damage injected at actual hittest boundary. Tile writes,circle requests,audio,point numbers and HP pixels intercepted in midboss controls; tile ring independently executed. Original tune/add/bonus/defeat/render geometry execute. Isolated controls, not full routes, native Windows pacing or byte-exact acceptance.')
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
