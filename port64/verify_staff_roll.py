#!/usr/bin/env python3
"""Original CPU Staff Roll requests and independent indexed-page consumer.

The complete eight original C++ bodies and polar execute in Unicorn. File,
graphics, audio and VSync consumers are explicit adapters. The raster reference
consumes those original requests with independently unpacked CDG planes; PI
decode remains a recorded regression dependency, not original CPU PI execution.
This is not a physical PC-98 or whole-game video/audio comparison.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess

from capstone import Cs, CS_ARCH_X86, CS_MODE_16
import numpy as np
import unicorn
from unicorn.x86_const import *
from verify_cutscene import Original as Base, ending_assets, PAYLOAD_SHA
from verify_maine_join import return_to_caller
from verify import source_manifest

sha=lambda data:hashlib.sha256(data).hexdigest()
def equal_page(actual,expected,label):
    if actual!=expected:raise ValueError(label+' differs')

class Original(Base):
    def __init__(self,target,decoded,assets,load=0x2000):
        super().__init__(target,decoded,load)
        if sha(self.payload[0xaed0:0xb787])!='1bf488943682cd811d5dad81ac088c91772e87e33adbc2867d2296dc797b21f2':
            raise ValueError('Original Staff Roll body identity differs')
        self.assets=assets
        self.wait_ips={i.address for i in Cs(CS_ARCH_X86,CS_MODE_16).disasm(self.payload[0xaed0:0xb787],0xe80)
                       if i.mnemonic=='cmp' and i.op_str=='word ptr [0xefa], 2'}
        if len(self.wait_ips)!=3: raise ValueError('Staff Roll VSync boundaries differ')

    def event(self,kind,a=0,b=0,c=0,d=0,name='-'):
        self.events.append(f'{kind} {a} {b} {c} {d} {name}')

    def port(self,u,port,size,value,unused):
        if (port,size) in ((0xa4,1),(0xa6,1)):
            self.event('show' if port==0xa4 else 'access',value)
        elif (port,size,value)==(0x7c,1,0): self.event('grcg_off')
        else:
            self.error=ValueError(f'unexpected Staff Roll port {port:x}');u.emu_stop()

    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16;relative=cs-self.load
        sp=u.reg_read(UC_X86_REG_SP)
        def words(count):return struct.unpack('<'+'H'*count,u.mem_read(0x70000+sp+4,count*2))
        def string(off,seg):
            data=bytes(u.mem_read(seg*16+off,16));assert 0 in data
            return data[:data.index(0)].decode('ascii').upper()
        if cs==self.cs and ip==0xff00:
            self.done=True;u.emu_stop();return
        if relative==0xa05 and ip in self.wait_ips:
            self.event('vsync',2);self.write(0xefa,'H',2);return
        if relative==0xa05 and 0xe80<=ip<0x1737:return
        if relative==0xcc7 and 0x260<=ip<0x27a:return  # Execute original polar/SAR and original tables.
        if relative==0:
            if ip==0x19ec:self.event('tone',self.read(0x132,'h')[0]);return_to_caller(u);return
            if ip==0x11c2:self.event('copy_page',words(1)[0]);return_to_caller(u,2);return
            if ip==0x1274:self.event('pi_free');return_to_caller(u,8);return
            if ip in (0x622,0x666):self.event('fade',int(ip==0x622),words(1)[0]);return_to_caller(u,2);return
            if ip==0xc82:
                color,mode=words(2);assert (mode,color)==(0xc0,15)
                self.event('grcg_on');return_to_caller(u,4);return
        if relative==0xcc7:
            if ip in (0x9b6,0xa54,0xc5e):
                self.event({0x9b6:'snap',0xa54:'bg_free',0xc5e:'cdg_free_all'}[ip]);return_to_caller(u);return
            if ip==0xa86:
                h,w,y,x=words(4);self.event('bg_rect',x,y,w,h);return_to_caller(u,8);return
            if ip==0x6e6:
                slot,y,x=words(3);self.event('cdg_put',x,y,slot);return_to_caller(u,6);return
            if ip==0x408:
                plane,slot,y,x=words(4);self.event('plane',x,y,slot,plane);return_to_caller(u,8);return
            if ip in (0xb08,0xb0e):
                image,off,seg,slot=words(4);assert image==0
                name=string(off,seg);self.u.mem_write(self.ds*16+0x1b46+slot*16,self.assets[name][:16])
                self.event('cdg_load',slot,int(ip==0xb08),name=name);return_to_caller(u,8);return
            if ip==0xc28:self.event('cdg_free',words(1)[0]);return_to_caller(u,2);return
            if ip==0x3d6:
                fallback,measure=words(2);self.event('measure',measure,fallback);return_to_caller(u,4);return
            if ip==0x48:self.event('pi_palette');assert words(1)==(0,);return_to_caller(u,2);return
            if ip==0x6d:self.event('pi_put');assert words(3)==(0,0,0);return_to_caller(u,6);return
            if ip==0xf5:
                off,seg,slot=words(3);assert slot==0
                self.event('pi_load',name=string(off,seg));return_to_caller(u,6);return
            if ip==0x31c:self.event('bgm_control',words(1)[0]);return_to_caller(u,2);return
            if ip==0x4a2:
                mode,off,seg=words(3);self.event('bgm_load',mode,name=string(off,seg));return_to_caller(u,6);return
        raise ValueError(f'unexpected original Staff Roll consumer {relative:04X}:{ip:04X}')

    def trace(self,angle):
        self.u.mem_write(self.ds*16,self.data);self.write(0x3f97,'B',angle)
        self.events=[];self.error=None;self.done=False
        for reg,v in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),
                      (UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):
            self.u.reg_write(reg,v)
        self.u.mem_write(0x7ff00,struct.pack('<H',0xff00))
        self.u.emu_start(self.cs*16+0x13fd,0x10ffff,count=1000000)
        if self.error:raise RuntimeError('original Staff Roll adapter rejected') from self.error
        assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xff02
        return self.events+[f'END {self.read(0x3f97,"B")[0]}']

class Kernels(Original):
    """Execute original BGIMAGER, CDG_PUT_PLANE and CDG_PUT_8 instructions.

    Bank selection is fixed for these direct controls. A supplied GRCG adapter
    applies write masks to all four planar buffers; plain OR/copy instructions
    execute in the target. Deferred writeback prevents Unicorn's normal RAM
    store from overwriting the emulated GRCG result after its pre-write hook.
    """
    bases=(0xa8000,0xb0000,0xb8000,0xe0000)
    def __init__(self,*args):
        super().__init__(*args)
        self.kernel_mode=False;self.pending={}
        self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.memory_write)

    def flush(self):
        for address,value in self.pending.items():self.u.mem_write(address,bytes((value,)))
        self.pending.clear()

    def body(self,u,address):
        if not self.kernel_mode:return super().body(u,address)
        self.flush()
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
        if cs==self.entry_cs and ip==0xff00:self.done=True;u.emu_stop();return
        if cs-self.load==0xcc7 and (0x408<=ip<0x4a0 or 0x6e6<=ip<0x81a or 0xa86<=ip<0xb08):return
        raise ValueError(f'unexpected original graphics kernel {cs-self.load:04X}:{ip:04X}')

    def port(self,u,port,size,value,unused):
        if not self.kernel_mode:return super().port(u,port,size,value,unused)
        try:self.kernel_port(port,size,value)
        except Exception as error:self.error=error;u.emu_stop()

    def kernel_port(self,port,size,value):
        if size!=1:raise ValueError('unexpected kernel port size')
        if port==0x7c:self.mode=value;self.tile_index=0
        elif port==0x7e:
            self.tiles[self.tile_index]=value;self.tile_index=(self.tile_index+1)%4
        else:raise ValueError(f'unexpected graphics kernel port {port:x}')

    def memory_write(self,u,access,address,size,value,unused):
        if not self.kernel_mode:return
        try:self.kernel_write(address,size,value)
        except Exception as error:self.error=error;u.emu_stop()

    def kernel_write(self,address,size,value):
        for plane,base in enumerate(self.bases):
            if not base<=address<base+32768:continue
            for byte in range(size):
                at=address-base+byte;mask=(value>>(byte*8))&255
                if self.mode==0xc0:
                    for p in range(4):
                        old=int(self.planes[p,at]);new=(old&(~mask&255))|(self.tiles[p]&mask)
                        self.planes[p,at]=new;self.pending[self.bases[p]+at]=new
                elif self.mode==0:self.planes[plane,at]=mask
                else:raise ValueError('unsupported GRCG graphics-kernel mode')
            return

    def render(self,fixture):
        kind,name,x,y,c,d=fixture
        pattern=((np.arange(256000,dtype=np.uint32)*13+(np.arange(256000,dtype=np.uint32)//640)*7)&15).astype(np.uint8)
        source=pattern.reshape(400,640)
        seed=np.full((400,640),9,dtype=np.uint8) if kind=='bg' else source
        self.kernel_mode=False;self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
        self.planes=np.zeros((4,32768),dtype=np.uint8);self.pending={};self.mode=0;self.tile_index=0;self.tiles=[255]*4
        for plane,base in enumerate(self.bases):
            self.planes[plane,:32000]=np.packbits((seed>>plane)&1,axis=1).reshape(-1)
            self.u.mem_write(base,self.planes[plane].tobytes())
        if kind=='bg':
            for plane in range(4):self.u.mem_write(0x40000+plane*0x8000,np.packbits((source>>plane)&1,axis=1).tobytes()+bytes(768))
            self.write(0x602,'4H',0x4000,0x4800,0x5000,0x5800)
            ip=0xa86;args=(d,c,y,x)
        else:
            data=self.assets[name];size=struct.unpack_from('<H',data)[0];layout=data[11]
            header=bytearray(data[:16]);struct.pack_into('<HH',header,12,0x5800 if layout==1 else 0,0x6000)
            self.u.mem_write(self.ds*16+0x1b46,bytes(header))
            if layout==1:self.u.mem_write(0x58000,data[16:16+size])
            self.u.mem_write(0x60000,data[16+(size if layout==1 else 0):])
            if kind=='put':ip=0x6e6;args=(0,y,x)
            else:ip=0x408;args=(c,0,y,x);self.mode=0xc0
        self.entry_cs=self.load+0xcc7;self.error=None;self.done=False;self.kernel_mode=True
        for reg,v in ((UC_X86_REG_CS,self.entry_cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),
                      (UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):
            self.u.reg_write(reg,v)
        self.u.mem_write(0x7ff00,struct.pack('<'+'H'*(2+len(args)),0xff00,self.entry_cs,*args))
        self.u.emu_start(self.entry_cs*16+ip,0x10ffff,count=100000)
        if self.error:raise RuntimeError('original graphics-kernel adapter rejected') from self.error
        assert self.done and self.u.reg_read(UC_X86_REG_SP)==0xff04+2*len(args)
        self.kernel_mode=False
        bits=np.unpackbits(self.planes[:,:32000].reshape(4,400,80),axis=2)
        result=np.zeros((400,640),dtype=np.uint8)
        for plane in range(4):result|=bits[plane]*(1<<plane)
        return result.tobytes()

class Raster:
    def __init__(self,assets,pictures):
        self.assets=assets;self.pictures=pictures;self.pages=np.zeros((2,400,640),dtype=np.uint8)
        self.palette=bytes(48);self.shown=0;self.access=0;self.tone=100
        self.snapshot=None;self.slots={};self.loaded=None;self.sheets={}
        for name,data in assets.items():
            if not name.startswith('SFF') or not name.endswith('.CDG'):continue
            size,width,height,bottom,stride,count,layout=struct.unpack('<5H2B',data[:12])
            planes={0:4,1:5,2:1}[layout]
            assert count==1 and stride*4*height==size and width==stride*32
            raw=np.frombuffer(data[16:],dtype=np.uint8).reshape(planes,height,stride*4)
            self.sheets[name]=(layout,np.unpackbits(raw,axis=2)[:,::-1,:])

    def apply(self,line):
        kind,a,b,c,d,name=line.split();a,b,c,d=map(int,(a,b,c,d))
        if kind=='tone':self.tone=a
        elif kind=='access':self.access=a
        elif kind=='show':self.shown=a
        elif kind=='pi_load':self.loaded=name
        elif kind=='pi_palette':self.palette=self.pictures[self.loaded][0]
        elif kind=='pi_put':self.pages[self.access]=self.pictures[self.loaded][1]
        elif kind=='pi_free':self.loaded=None
        elif kind=='copy_page':self.pages[a]=self.pages[1-a];self.access=a
        elif kind=='snap':self.snapshot=self.pages[self.access].copy()
        elif kind=='bg_free':self.snapshot=None
        elif kind=='cdg_load':self.slots[a]=name
        elif kind=='cdg_free':del self.slots[a]
        elif kind=='cdg_free_all':self.slots.clear()
        elif kind=='bg_rect':
            # Independently replay BGIMAGER's byte/WORD geometry and TH04
            # inclusive row loop. No native Scene or Script is imported.
            start=(a//16)*16
            span=16*((a%16+c)//16+(1 if a%16 else 0))
            assert self.snapshot is not None and b>=0 and b+d<=400 and start>=0 and start+span<=640
            # The last SFF7 expansion also touches offscreen row400. Its
            # allocation tail is outside this complete visible-page claim.
            stop=min(400,b+d+1)
            self.pages[self.access,b:stop,start:start+span]=self.snapshot[b:stop,start:start+span]
        elif kind in ('cdg_put','plane'):
            layout,bits=self.sheets[self.slots[c]];height,width=bits.shape[1:]
            left=a//8*8 if kind=='cdg_put' else a
            assert left>=0 and b>=0 and left+width<=640 and b+height<=400
            dest=self.pages[self.access,b:b+height,left:left+width]
            if kind=='plane':dest[bits[d+(1 if layout==1 else 0)].astype(bool)]=15
            else:
                assert layout==1
                dest[bits[0].astype(bool)]=0
                for plane in range(4):dest|=bits[plane+1]*(1<<plane)
        elif kind=='fade':self.tone=0 if a else 100
        elif kind in ('vsync','measure'):
            # The palette transition completes before the next request;
            # checkpoints at these later boundaries see its clamped endpoint.
            pass
        elif kind not in ('bgm_control','bgm_load','grcg_on','grcg_off'):
            raise ValueError('unknown original Staff Roll raster request')

def run(exe,runner,*args):
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    return subprocess.check_output(([runner] if runner else [])+[str(exe.resolve()),*map(str,args)],env=env,text=True).splitlines()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded','hdi','exe','baseline-exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner');args=p.parse_args()
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    manifest,files=source_manifest(Path(__file__).resolve().parents[1])
    assets=ending_assets(args.hdi);asset_dir=out/'assets';asset_dir.mkdir(exist_ok=True)
    selected={k:v for k,v in assets.items() if k.startswith('SFF')}
    if len(selected)!=20:raise ValueError('Staff Roll asset set differs')
    for name,data in selected.items():(asset_dir/name).write_bytes(data)
    cases=[];trace=None
    for load in (0x1000,0x2000):
        original=Original(args.target,args.decoded,assets,load)
        for angle in (0,7,64,255):
            expected=original.trace(angle);actual=run(args.exe,args.runner,'--staff-trace',asset_dir,angle)
            (out/f'trace-{load:x}-{angle}.txt').write_text('\n'.join(expected)+'\n')
            if actual!=expected:
                (out/f'native-{load:x}-{angle}.txt').write_text('\n'.join(actual)+'\n')
                first=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),min(len(actual),len(expected)))
                raise ValueError(f'Staff Roll request {first}: native {actual[first:first+1]} / original {expected[first:first+1]}')
            cases.append(dict(load=load,angle=angle,requests=len(expected)-1,trace_sha256=sha(('\n'.join(expected)+'\n').encode())))
            if load==0x2000 and angle==0:trace=expected[:-1]
    pictures={}
    for name in ('SFF1.PI','SFF2.PI'):
        decoded=asset_dir/(name+'.raw');baseline=asset_dir/(name+'.baseline')
        run(args.exe,args.runner,'--decode',asset_dir/name,decoded)
        run(args.baseline_exe,None,'--decode',asset_dir/name,baseline)
        data=decoded.read_bytes();assert data==baseline.read_bytes()
        assert struct.unpack('<II',data[:8])==(640,400)
        packed=np.frombuffer(data[56:],dtype=np.uint8)
        indices=np.empty(256000,dtype=np.uint8);indices[0::2]=packed>>4;indices[1::2]=packed&15
        pictures[name]=(data[8:56],indices.reshape(400,640))
    # Several interior frames of every dissolve, each completed image/copy,
    # both background switches and cleanup. Keep full pages rather than crops.
    captures=[];shown_count=0
    for i,line in enumerate(trace):
        kind=line.split()[0]
        if kind=='show':shown_count+=1
        if kind in ('pi_put','copy_page','bg_free','cdg_put') or (kind=='show' and shown_count%7==0):captures.append(i)
    positions=out/'checkpoints.txt';positions.write_text(''.join(str(i)+'\n' for i in captures))
    pages=out/'pages';pages.mkdir(exist_ok=True)
    print('\n'.join(run(args.exe,args.runner,'--staff-render',asset_dir,positions,pages)))
    native_states=(pages/'states.txt').read_text().splitlines();states=[];raster=Raster(assets,pictures);records=[]
    fade_pending=None
    for i,line in enumerate(trace):
        # Original macro fades block before returning to the next request.
        if fade_pending is not None:raster.tone=fade_pending;fade_pending=None
        raster.apply(line)
        if line.startswith('fade '):fade_pending=100 if line.split()[1]=='1' else 0
        if i not in captures:continue
        kind=line.split()[0]
        states.append(f'{i} {raster.shown} {raster.access} {raster.tone} {int(raster.snapshot is not None)} {len(raster.slots)} {kind}')
        for page in (0,1):
            want=raster.pages[page].tobytes();path=pages/f'{i}-{page}.bin'
            if path.read_bytes()!=want:
                (pages/f'{i}-{page}.expected').write_bytes(want)
                raise ValueError(f'Staff Roll complete graphics page differs at request {i} page{page}')
            records.append(dict(event=i,page=page,sha256=sha(want)))
        assert (pages/f'{i}.pal').read_bytes()==raster.palette
    assert native_states==states
    # Independently execute the original pixel kernels against varied seeded
    # backgrounds, all asset plane layouts and all sub-WORD alignments used
    # by the three dissolve families. These are visible-page controls only.
    fixtures=[]
    for name in sorted(k for k in selected if k.endswith('.CDG')):
        for alignment in (0,7,15):
            for plane in range(4):fixtures.append(('plane',name,80+alignment,128,plane,0))
            if selected[name][11]==1:fixtures.append(('put',name,80+alignment,128,0,0))
    for x,y,w,h in ((31,109,322,71),(32,112,256,32),(1,1,31,0),(15,15,32,1),(16,16,32,2),(17,17,33,3),(0,304,256,96)):
        fixtures.append(('bg','-',x,y,w,h))
    fixture_file=out/'kernel-fixtures.txt';fixture_file.write_text(''.join(' '.join(map(str,r))+'\n' for r in fixtures))
    kernels_dir=out/'kernels';kernels_dir.mkdir(exist_ok=True)
    print('\n'.join(run(args.exe,args.runner,'--staff-kernels',asset_dir,fixture_file,kernels_dir)))
    original=Kernels(args.target,args.decoded,assets);kernel_records=[]
    for index,fixture in enumerate(fixtures):
        expected=original.render(fixture);path=kernels_dir/f'{index}.bin'
        if path.read_bytes()!=expected:
            (kernels_dir/f'{index}.expected').write_bytes(expected)
            raise ValueError(f'Original graphics kernel differs for {fixture}')
        kernel_records.append(dict(fixture=fixture,sha256=sha(expected)))
    # A changed complete-page byte must invalidate this comparator.
    first=pages/f'{captures[0]}-0.bin';mutated=bytearray(first.read_bytes());mutated[0]^=1
    assert sha(mutated)!=records[0]['sha256']
    try:equal_page(mutated,first.read_bytes(),'negative complete-page control')
    except ValueError:pass
    else:raise ValueError('complete-page comparator accepted its negative control')
    current,_=source_manifest(Path(__file__).resolve().parents[1]);assert current==manifest
    receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),source_manifest_sha256=manifest,
                 source_files=files,native_sha256=sha(args.exe.read_bytes()),baseline_pi_decoder_sha256=sha(args.baseline_exe.read_bytes()),
                 payload_sha256=PAYLOAD_SHA,hdi_sha256=sha(args.hdi.read_bytes()),cases=cases,pages=records,
                 checkpoints=len(captures),kernel_controls=kernel_records,negative_pixel_rejected=True,assets={k:sha(v) for k,v in selected.items()},
                 scope='Complete original CPU Staff Roll request sequence and independent request-driven CDG/background raster, strengthened by original CPU graphics-kernel controls with a GRCG adapter. PI decode is a recorded regression dependency. VSync, graphics/file consumers and inactive sound are adapters; offscreen allocation tails, physical timing/audio, whole-game, verdict and save are outside scope.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'PASS: {len(cases)} original Staff Roll request controls; {len(records)} complete pages; {len(captures)} palette/state checkpoints')

if __name__=='__main__':main()
