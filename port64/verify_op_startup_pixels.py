#!/usr/bin/env python3
"""Original OP clipped SUPER instructions and actual DAC consume startup requests.

All fifteen control fixtures capture both640x400indexed pages/rawRGB/DAC/shown
RGB at EVERY refresh. Original caller and clipped SUPER execute at two loads;
PI decode/page/background/BFNT staging/input/measure/sound remain explicit
adapters. RGB uses the existing four-bit DAC expansion, not physical video.
Streams are losslessly compressed without retaining raw multigigabyte files.
"""
import argparse,gzip,hashlib,json,os,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import unicorn
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD
from verify_op_startup import Original as Control,fixtures,fixture,prepare_assets,NAMES
from verify_registration_render import Sprite as Grcg
from verify_reimu_pixels import planes
from verify import source_manifest,require_elf_x86_64
SIZE=512000+48+48+768000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Caller(Control):
    def emit(self,kind,a=0,b=0,c=0,data=b''):
        super().emit(kind,a,b,c,data)
        # Observe the raw software palette while DAC may still retain an older
        # publication. The measure call follows the original45-component clear.
        if kind in ('measure','super_load'):
            self.events.append(f'RAW {self.clock} '+bytes(self.u.mem_read(self.ds*16+0x1a96,48)).hex())
class Sprite(Base):
    def __init__(self,*args):
        super().__init__(*args);self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE,self.shadow)
    port=Grcg.port
    def shadow(self,u,access,address,size,value,unused):
        if 0xa8000<=address<0xb0000 and address+size>0xa8000+32000:
            self.error=ValueError('clipped kernel wrote below visible VRAM');u.emu_stop();return
        Grcg.shadow(self,u,access,address,size,value,unused)
    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);ip=address-cs*16
        # 2B60 is the shared early-return tail preceding this entry.
        if cs==self.load and 0x2b60<=ip<0x2f0c:return
        if cs==self.cs and ip==0xff00:self.done=True;u.emu_stop();return
        raise ValueError(f'unexpected clipped SUPER {cs-self.load:04x}:{ip:04x}')
    def render(self,blob,image,x,y,background):
        u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data)
        width,height,pattern=planes(blob,image);assert (width,height) in ((16,16),(32,32))
        self.write(0x1ad8+image*2,'H',0x9000);self.write(0x1ed8+image*2,'H',(width//8<<8)|height)
        self.write(0x50e,'7H',0,639,639,0,399,399,0xa800)
        u.mem_write(0x90000,pattern);u.mem_write(0xa8000,bytes(32000));self.screen=bytearray(background)
        self.mode=0;self.tile_at=0;self.tiles=[0]*4;self.writes=0;self.error=None;self.done=False
        for r,v in ((UC_X86_REG_CS,self.load),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(r,v)
        u.mem_write(0x7f000,struct.pack('<5H',0xff00,self.cs,image,y&65535,x&65535))
        u.emu_start(self.load*16+0x2b66,0x10ffff,count=300000)
        if self.error:raise RuntimeError('original clipped SUPER rejected') from self.error
        assert self.done and self.mode==0 and u.reg_read(UC_X86_REG_SP)==0xf00a
        return bytes(self.screen)
class Raster:
    def __init__(self,target,decoded,assets,pictures):
        self.sprites=[Sprite(target,decoded,load) for load in (0x1000,0x2000)]
        self.assets=assets;self.pictures=pictures;self.cache={};self.calls=0
        self.background_control=(np.arange(256000,dtype=np.uint32)*73+5).astype(np.uint8)&15
    def reset(self,initial):
        self.pages=np.zeros((2,400,640),dtype=np.uint8);self.access=self.shown=0
        self.raw=initial;self.dac=bytes(48);self.loaded={};self.headers={};self.bank=[];self.background=None
    def apply(self,line):
        words=line.split();kind=words[0]
        if kind in ('RAW','DAC'):
            data=bytes.fromhex(words[2]);assert len(data)==48
            if kind=='RAW':self.raw=data
            else:self.dac=data
            return
        tick,a,b,c=map(int,words[1:5]);data=bytes.fromhex(words[5]) if words[5]!='-' else b''
        if kind=='access':self.access=a
        elif kind=='show':self.shown=a
        elif kind=='load':self.loaded[a]=data.decode().upper();self.headers[a]=self.loaded[a]
        elif kind=='free':del self.loaded[a] # The PI palette header remains.
        elif kind=='palette':self.raw=self.pictures[self.headers[a]][0]
        elif kind=='palette_show':assert len(data)==48;self.raw=data
        elif kind=='picture':
            pixels=self.pictures[self.loaded[c]][1];height,width=pixels.shape
            assert a==0 and b in (0,38) and width==640
            # The title's108-row slices overwrite only their destination band.
            for row in range(height):self.pages[self.access,(b+row)%400,:]=pixels[row]
        elif kind=='copy':self.access=a;self.pages[a]=self.pages[1-a]
        elif kind=='clear':self.pages[self.access].fill(0)
        elif kind=='fill':self.pages[self.access].fill(a)
        elif kind=='snap':self.background=self.pages[self.access].copy()
        elif kind=='restore':assert self.background is not None;self.pages[self.access]=self.background
        elif kind=='bg_free':self.background=None
        elif kind=='super_load':
            name=data.decode().upper();blob=self.assets[name];first,last=struct.unpack_from('<2H',blob,12)
            self.bank.extend((name,i) for i in range(last-first+1))
        elif kind=='super_free':self.bank=[]
        elif kind=='sprite':
            name,image=self.bank[c];key=(name,image,a,b)
            if key not in self.cache:
                zero=[s.render(self.assets[name],image,a,b,bytes(256000)) for s in self.sprites];assert zero[0]==zero[1]
                pixels=np.frombuffer(zero[0],dtype=np.uint8);positions=np.flatnonzero(pixels).astype(np.int32);colors=pixels[positions].copy()
                expected=self.background_control.copy();expected[positions]=colors
                for s in self.sprites:assert s.render(self.assets[name],image,a,b,self.background_control.tobytes())==expected.tobytes()
                self.calls+=4;self.cache[key]=(positions,colors)
            positions,colors=self.cache[key];self.pages[self.access].reshape(-1)[positions]=colors
        elif kind not in ('song','command','measure','reset','sense','wait','se','se_update','logo_complete','complete'):
            raise ValueError('unhandled startup raster event '+kind)
    def bytes(self):
        rgb=np.frombuffer(self.dac,dtype=np.uint8).reshape(16,3)*17
        return self.pages.tobytes()+self.raw+self.dac+rgb[self.pages[self.shown]].tobytes()
def archive_sources(root,out,mf,files):
    with tarfile.open(out/'source.tar.gz','w:gz') as archive:
        for f in files:
            p=root/f['path'];assert sha(p)==f['sha256'];archive.add(p,arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
def controls(lines):
    cases=[];current=None
    for line in lines:
        if line.startswith('CASE '):current=[];cases.append(current)
        elif line.startswith('END '):current.append(line)
        elif not line.startswith('STATE '):current.append(line)
    return cases
def check_inputs(frozen):
    for p,h in frozen.items():assert sha(p)==h,('input changed',str(p))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded-dir','hdi','decoder','control-reference','reference','exe','product-profile'):
        p.add_argument('--'+name,type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);archive_sources(root,out,mf,files)
    rows=fixtures();fixture_path=out/'fixtures.txt';fixture_path.write_text('\n'.join(map(fixture,rows))+'\n')
    if a.reference:
        reference=a.reference.resolve();r=json.loads((reference/'receipt.json').read_text());assert r['passed'] and r['cases']==len(rows)
        assert fixture_path.read_bytes()==(reference/'fixtures.txt').read_bytes()
        assert a.product_profile is not None,'Name the immutable executable producer profile'
        product=json.loads(a.product_profile.read_text());binary_sha=sha(a.exe)
        assert any(host.get(a.exe.name)==binary_sha for host in product['products'].values()),'Executable not bound by producer profile'
        frozen={q:sha(q) for q in [a.exe.resolve(),a.product_profile.resolve(),reference/'receipt.json',reference/'fixtures.txt',reference/'frames.bin.gz',*sorted((reference/'assets').iterdir())]}
        for n,h in r['assets'].items():assert sha(reference/'assets'/n)==h
        require_elf_x86_64(a.exe);command=[str(a.exe.resolve()),'--frames',str(fixture_path),str(reference/'assets')]
        digest=hashlib.sha256();count=0
        with (out/'stderr.txt').open('wb') as stderr:
            child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=stderr)
            try:
                with gzip.open(reference/'frames.bin.gz','rb') as expected,gzip.open(out/'frames.bin.gz','wb',compresslevel=1) as actual:
                    while True:
                        want=expected.read(SIZE)
                        if not want:break
                        assert len(want)==SIZE
                        got=bytearray()
                        while len(got)<SIZE:
                            chunk=child.stdout.read(SIZE-len(got))
                            if not chunk:break
                            got.extend(chunk)
                        actual.write(got)
                        if got!=want:
                            at=next((i for i,(x,y) in enumerate(zip(want,got)) if x!=y),min(len(want),len(got)))
                            (out/'mismatch.json').write_text(json.dumps(dict(frame=count,offset=at,expected=want[at] if at<len(want) else None,actual=got[at] if at<len(got) else None),indent=2)+'\n')
                            raise ValueError(f'startup frame{count} differs at byte{at}')
                        digest.update(got);count+=1
                    assert not child.stdout.read(1) and child.wait(timeout=30)==0
            finally:
                if child.poll() is None:child.kill();child.wait()
        assert count==r['frames'] and digest.hexdigest()==r['frames_sha256'];check_inputs(frozen)
        receipt=dict(passed=True,cases=len(rows),frames=count,frames_sha256=digest.hexdigest(),exe_sha256=sha(a.exe),command=command,reference_receipt_sha256=sha(reference/'receipt.json'),reference_producer_manifest=r['source_manifest'],product_producer_manifest=product['product_producer_manifest'],product_profile_sha256=sha(a.product_profile))
    else:
        ref=a.control_reference.resolve();old=json.loads((ref/'receipt.json').read_text());assert old['passed'] and old['cases']==len(rows)
        previous=gzip.open(ref/'original.txt.gz','rb').read();assert hashlib.sha256(previous).hexdigest()==old['trace_sha256']
        assert fixture_path.read_bytes()==(ref/'fixtures.txt').read_bytes()
        frozen={q.resolve():sha(q) for q in [a.target,a.hdi,a.decoder,ref/'receipt.json',ref/'fixtures.txt',ref/'original.txt.gz',*[a.decoded_dir/n for n in ('payload.bin','receipt.json','relocations.csv')]]}
        assets,palettes=prepare_assets(a.hdi,a.decoder,out);traces=[]
        for load in (0x1000,0x2000):
            caller=Caller(a.target,a.decoded_dir,load,palettes,assets);lines=[]
            for i,c in enumerate(rows):
                lines.extend([f'CASE {i}',*caller.run(c)]);print(f'original startup pixel caller {load:04x}/{i}',flush=True)
            trace=('\n'.join(lines)+'\n').encode();canonical=('\n'.join(line for line in lines if not line.startswith('RAW '))+'\n').encode();assert canonical==previous
            traces.append(trace)
        assert traces[0]==traces[1]
        with gzip.open(out/'control.txt.gz','wb',compresslevel=1) as f:f.write(traces[0])
        pictures={}
        for q in (out/'assets').glob('*.decoded'):
            body=q.read_bytes();width,height=struct.unpack_from('<II',body);assert width==640 and height in (108,400) and len(body)==56+width*height//2
            packed=np.frombuffer(body[56:],dtype=np.uint8).reshape(height,width//2);pixels=np.empty((height,width),dtype=np.uint8);pixels[:,::2]=packed>>4;pixels[:,1::2]=packed&15
            pictures[q.name[:-8]]=(body[8:56],pixels)
        raster=Raster(a.target,a.decoded_dir,assets,pictures);digest=hashlib.sha256();frames=0;case_records=[]
        control_cases=controls(traces[0].decode().splitlines());assert len(control_cases)==len(rows)
        state_cases=[]
        for line in traces[0].decode().splitlines():
            if line.startswith('CASE '):state_cases.append({})
            elif line.startswith('STATE '):
                _,tick,hex_state=line.split();state_cases[-1][int(tick)]=bytes.fromhex(hex_state)
        checked_states=0
        with gzip.open(out/'frames.bin.gz','wb',compresslevel=1) as stream:
            for index,(c,events) in enumerate(zip(rows,control_cases)):
                end=int(events[-1].split()[1]);pending={}
                for line in events[:-1]:pending.setdefault(int(line.split()[1]),[]).append(line)
                raster.reset(c[5]);case_digest=hashlib.sha256()
                for tick in range(end+1):
                    for line in pending.get(tick,[]):raster.apply(line)
                    if tick in state_cases[index]:
                        s=state_cases[index][tick];assert len(s)==3686
                        assert raster.raw==s[3588:3636] and raster.dac==s[3636:3684]
                        assert bytes((raster.access,raster.shown))==s[3684:]
                        checked_states+=1
                    raw=raster.bytes();assert len(raw)==SIZE;stream.write(raw);digest.update(raw);case_digest.update(raw);frames+=1
                case_records.append(dict(case=index,last_tick=end,frames=end+1,sha256=case_digest.hexdigest()));print(f'original pixels {index}/{end+1}frames kernels={raster.calls}',flush=True)
        check_inputs(frozen)
        receipt=dict(passed=True,cases=len(rows),frames=frames,frame_bytes=SIZE,frames_sha256=digest.hexdigest(),loads=['1000','2000'],kernel_calls=raster.calls,unique_stencils=len(raster.cache),checked_original_palette_page_states=checked_states,case_records=case_records,
            packed_sha256=PACKED,payload_sha256=PAYLOAD,control_receipt_sha256=sha(ref/'receipt.json'),control_producer_manifest=old['source_manifest'],assets={q.name:sha(q) for q in sorted((out/'assets').iterdir())},decoder_sha256=sha(a.decoder),input_hashes={str(q):h for q,h in frozen.items()})
    assert source_manifest(root)[0]==mf
    receipt.update(source_manifest=mf,source_files=len(files),source_archive_sha256=sha(out/'source.tar.gz'),utc=datetime.now(timezone.utc).isoformat(),engine_version=unicorn.__version__,engine_sha256=sha(Path(unicorn.unicorn._uc._name)),scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('startup pixels PASS',receipt['frames'],flush=True)
if __name__=='__main__':main()
