#!/usr/bin/env python3
"""Bounded original OP startup prefix, logo/fireworks and title at two loads.

The unchanged OP prefix decides one-time resident logo ownership and demo BGM.
Original spawn/update/polar/LCG, palette arithmetic/DAC and fades execute.
PI decode/loading, BFNT registration, page/background consumers, sound calls,
scripted input and refresh/measure readiness are explicit guarded adapters.
This control corpus does not prove physical video/audio, complete OP or routes.
"""
import argparse,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
from unicorn.x86_const import *
from verify_op_score import Original as Base,PACKED,PAYLOAD
from verify_maine_join import return_to_caller
from verify_cutscene import ending_assets
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
NAMES=('ZUN00.PI','OP1.PI',*(f'OP{i}B.PI' for i in range(6)),*(f'ZUN0{i}.BFT' for i in range(1,5)))
class Original(Base):
    def __init__(self,target,decoded,load,pictures,assets):
        super().__init__(target,decoded,load);self.pictures=pictures;self.assets=assets
    def emit(self,k,a=0,b=0,c=0,data=b''):
        self.events.append(f'{k} {self.clock} {a} {b} {c} {data.hex() if data else "-"}')
    def state(self):
        return bytes(self.u.mem_read(self.ds*16+0x2b7c,3584))+bytes(self.u.mem_read(self.ds*16+0x5c4,4))+bytes(self.u.mem_read(self.ds*16+0x1a96,48))+bytes(self.dac)+bytes((self.access,self.shown))
    def wait(self,n):
        self.emit('wait',n);self.states.append(f'STATE {self.clock} '+self.state().hex());self.clock+=n
    def port(self,u,port,size,value,unused):
        try:
            assert size==1
            if port in (0xa4,0xa6):
                assert value in (0,1)
                if port==0xa4:self.shown=value
                else:self.access=value
                self.emit('show' if port==0xa4 else 'access',value)
            elif port==0xa8:assert value<16;self.color=value
            elif port in (0xac,0xaa,0xae):assert value<16;self.dac[self.color*3+{0xac:0,0xaa:1,0xae:2}[port]]=value
            elif port==0x7c:assert value==0
            else:raise ValueError(f'unexpected startup OUT {port:x}')
        except Exception as e:self.error=e;u.emu_stop()
    def body(self,u,address):
        cs=u.reg_read(UC_X86_REG_CS);pair=(cs-self.load,address-cs*16);sp=u.reg_read(UC_X86_REG_SP)
        def words(n):return struct.unpack('<'+'H'*n,u.mem_read(0x70000+sp+4,n*2))
        def name(off,seg):
            assert seg==self.ds;data=bytes(u.mem_read(seg*16+off,40));assert b'\0' in data;return data.split(b'\0')[0]
        def ret(n=0):return_to_caller(u,n)
        if pair==(0xa74,0xce3):
            assert bytes(u.mem_read(0x90048,1))==b'\x01'
            self.emit('complete');self.states.append(f'STATE {self.clock} '+self.state().hex());self.done=True;u.emu_stop();return
        if pair==(0xa74,0xcc4):self.emit('logo_complete')
        if pair[0]==0xa74 and (0xcb6<=pair[1]<0xce3 or 0x1305<=pair[1]<0x1764 or 0x2592<=pair[1]<0x281e):
            if pair[1]==0x16e2:
                self.wait(2);self.write(0x1ac6,'H',2)
            return
        if pair[0]==0xda1 and 0x1a8<=pair[1]<0x1c4:return
        if pair[0]==0 and (0x204e<=pair[1]<0x2078 or 0x622<=pair[1]<0x6a3):return
        if pair[0]==0 and 0x1de0<=pair[1]<0x1e49:
            if pair[1]==0x1de0:self.emit('palette_show',self.read(0x586,'h')[0],data=bytes(u.mem_read(self.ds*16+0x1a96,48)))
            elif pair[1]==0x1e48:self.events.append(f'DAC {self.clock} '+bytes(self.dac).hex())
            return
        if pair==(0,0x2648):self.wait(1);ret();return
        if pair==(0xda1,0x2b):assert words(1)==(1,);self.wait(1);ret(2);return
        if pair==(0xda1,0xed):
            off,seg,slot=words(3);resource=name(off,seg).decode().upper();assert slot<6 and resource in self.pictures and slot not in self.loaded
            self.loaded[slot]=resource;self.headers[slot]=self.pictures[resource]
            self.write(0x2370+slot*4,'HH',0x4000,0x9000)
            u.mem_write(self.ds*16+0x23a0+slot*72,self.pictures[resource]);self.emit('load',slot,data=resource.lower().encode());ret(6);return
        if pair==(0xda1,0x40):
            slot=words(1)[0];assert slot in self.headers
            self.emit('palette',slot);u.mem_write(self.ds*16+0x1a96,self.headers[slot]);ret(2)
            # Replay the actual palette routine instead of scalar emulation.
            current_sp=u.reg_read(UC_X86_REG_SP);current_cs=u.reg_read(UC_X86_REG_CS);current_ip=u.reg_read(UC_X86_REG_IP)
            u.reg_write(UC_X86_REG_SP,current_sp-4);u.mem_write(0x70000+current_sp-4,struct.pack('<HH',current_ip,current_cs));u.reg_write(UC_X86_REG_CS,self.load);u.reg_write(UC_X86_REG_IP,0x1de0);return
        if pair==(0xda1,0x65):
            slot,y,x=words(3);assert slot in self.loaded and x==0 and y in (0,38)
            self.emit('picture',x,y,slot);ret(6);return
        if pair==(0,0x1618):
            off,seg,header,ds=words(4);assert (off,seg,ds)==(0x4000,0x9000,self.ds) and (header-0x2388)%72==0
            slot=(header-0x2388)//72;assert slot in self.loaded;del self.loaded[slot];self.emit('free',slot);ret(8);return
        if pair==(0,0x156c):assert words(1)==(0,);self.access=0;self.emit('copy',0);ret(2);return
        if pair in ((0xda1,0xa18),(0xda1,0xa80),(0xda1,0xab6),(0,0x1532),(0,0x2922)):
            self.emit({(0xda1,0xa18):'snap',(0xda1,0xa80):'restore',(0xda1,0xab6):'bg_free',(0,0x1532):'clear',(0,0x2922):'super_free'}[pair]);ret();return
        if pair==(0,0x2a86):
            resource=name(*words(2));index=(b'zun02.bft',b'zun04.bft',b'zun01.bft',b'zun03.bft').index(resource);blob=self.assets[resource.decode().upper()]
            assert blob[5]&128;raw=blob[32:80];palette=bytes(v for i in range(16) for v in (raw[i*3+1],raw[i*3+2],raw[i*3]))
            u.mem_write(self.ds*16+0x1a96,palette);self.emit('super_load',index,data=resource);ret(4);return
        if pair==(0,0x2b66):
            pattern,y,x=words(3);signed=lambda n:n if n<32768 else n-65536
            assert pattern<20;self.emit('sprite',signed(x),signed(y),pattern);ret(6);return
        if pair==(0xda1,0x7cc):self.write(0x2710,'H',0);self.emit('reset');ret();return
        if pair==(0xda1,0x7d4):
            assert self.clock<len(self.keys);self.write(0x2710,'H',self.keys[self.clock]);self.emit('sense',self.keys[self.clock]);ret();return
        if pair==(0xda1,0x3ba):
            mode,off,seg=words(3);resource=name(off,seg);assert mode==0x600 and resource in (b'logo',b'op');self.emit('song',mode,data=resource);ret(6);return
        if pair==(0xda1,0x264):assert words(1)[0] in (0,0x100);self.emit('command',words(1)[0]);ret(2);return
        if pair==(0xda1,0x370):
            assert words(2)==(0,2);self.emit('measure',2,0)
            if self.measure_at>=0:self.clock=max(self.clock,self.measure_at)
            ret(4);return
        if pair==(0xda1,0x8e2):assert words(1)==(15,);self.emit('se',15);ret(2);return
        if pair==(0xda1,0x91c):self.emit('se_update');ret();return
        if pair==(0,0x10d2):assert words(2)==(15,0xc0);ret(4);return
        if pair==(0,0xca4):assert words(4)==(399,79,0,0),words(4);self.emit('fill',15);ret(8);return
        raise ValueError(f'unexpected startup consumer {pair}')
    def run(self,c):
        logo,demo,seed,measure_at,keys,initial_palette=c;u=self.u;u.mem_write(self.load*16,self.module);u.mem_write(self.ds*16,self.data)
        self.write(0x1a64,'HH',0,0x9000);u.mem_write(0x90000,bytes(256));u.mem_write(0x90048,bytes((not logo,)));u.mem_write(0x9003e,bytes((demo,)))
        self.write(0x5c4,'I',seed);self.write(0x5b8,'H',0);u.mem_write(self.ds*16+0x1a96,initial_palette);u.mem_write(self.ds*16+0x2b7c,bytes(3584))
        self.events=[];self.states=[];self.clock=0;self.access=self.shown=0;self.dac=bytearray(48);self.loaded={};self.headers={};self.keys=keys;self.measure_at=measure_at;self.error=None;self.done=False
        for r,v in ((UC_X86_REG_CS,self.cs),(UC_X86_REG_DS,self.ds),(UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0),(UC_X86_REG_EFLAGS,2)):u.reg_write(r,v)
        u.emu_start(self.cs*16+0xcb6,0x10ffff,count=8000000)
        if self.error:raise RuntimeError('original startup rejected') from self.error
        assert self.done and not self.loaded and u.reg_read(UC_X86_REG_SP)==0xf000
        return self.events+self.states+[f'END {self.clock} {self.read(0x586,"h")[0]} {self.read(0x5c4,"I")[0]}']
def fixtures():
    rows=[]
    for demo in (0,1):rows.append((0,demo,1,-1,[65535]*700))
    for seed in (1,0xffffffff):
        for skip in (-1,0,17,100,338):
            keys=[0]*700
            if skip>=0:keys[skip]=0x20
            rows.append((1,0,seed,-1,keys))
    rows.append((1,1,318,23,[0]*700))
    rows=[(*c,bytes(48)) for c in rows]
    palette=bytes((i*37+19)&255 for i in range(48))
    rows.append((0,0,0xffffffff,-1,[0]*700,palette))
    rows.append((1,1,42,-1,[0xffff]*700,palette))
    return rows
def fixture(c):return ' '.join(map(str,(*c[:4],c[5].hex(),len(c[4]),*c[4])))
def prepare_assets(hdi,decoder,out):
    assets=ending_assets(hdi);folder=out/'assets';folder.mkdir();pictures={}
    for name in NAMES:
        p=folder/name;p.write_bytes(assets[name])
        if name.endswith('.PI'):
            decoded=folder/(name+'.decoded');subprocess.run([str(decoder.resolve()),'--decode',str(p.resolve()),str(decoded.resolve())],check=True,capture_output=True);pictures[name]=decoded.read_bytes()[8:56]
    return assets,pictures
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('target','decoded-dir','hdi','decoder','reference','exe'):p.add_argument('--'+name,type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    with tarfile.open(out/'source.tar.gz','w:gz') as archive:
        for f in files:
            q=root/f['path'];assert sha(q.read_bytes())==f['sha256'];archive.add(q,arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
    frozen={}
    rows=fixtures();(out/'fixtures.txt').write_text('\n'.join(map(fixture,rows))+'\n')
    if a.reference:
        r=json.loads((a.reference/'receipt.json').read_text());assert r['passed'] and r['cases']==len(rows);assert (out/'fixtures.txt').read_bytes()==(a.reference/'fixtures.txt').read_bytes()
        expected=gzip.open(a.reference/'original.txt.gz','rb').read();assert sha(expected)==r['trace_sha256']
        assert r['source_manifest']==mf and r['original_cpu_reexecuted']
        for name,digest in r['assets'].items():assert sha((a.reference/'assets'/name).read_bytes())==digest
        frozen={q.resolve():sha(q.read_bytes()) for q in [a.exe,a.reference/'receipt.json',a.reference/'original.txt.gz',*sorted((a.reference/'assets').iterdir())]}
        command=[str(a.exe.resolve()),'--trace',str(out/'fixtures.txt'),str((a.reference/'assets').resolve())]
        result=subprocess.run(command,capture_output=True);actual=result.stdout;(out/'stderr.txt').write_bytes(result.stderr)
        with gzip.open(out/'native.txt.gz','wb') as f:f.write(actual)
        if result.returncode or actual!=expected:
            x=actual.splitlines();y=expected.splitlines();at=next((i for i,(a,b) in enumerate(zip(x,y)) if a!=b),min(len(x),len(y)));(out/'mismatch.json').write_text(json.dumps(dict(line=at,actual=[v.decode() for v in x[at:at+2]],expected=[v.decode() for v in y[at:at+2]],returncode=result.returncode),indent=2));raise ValueError(f'startup differs line{at}')
        receipt=dict(passed=True,cases=len(rows),reference_receipt_sha256=sha((a.reference/'receipt.json').read_bytes()),trace_sha256=sha(expected),exe_sha256=sha(a.exe.read_bytes()),command=command)
    else:
        frozen={q.resolve():sha(q.read_bytes()) for q in [a.target,a.hdi,a.decoder,*[a.decoded_dir/n for n in ('payload.bin','receipt.json','relocations.csv')]]}
        assets,pictures=prepare_assets(a.hdi,a.decoder,out);traces=[]
        for load in (0x1000,0x2000):
            o=Original(a.target,a.decoded_dir,load,pictures,assets);lines=[]
            for i,c in enumerate(rows):lines.extend([f'CASE {i}',*o.run(c)]);print(f'original startup {load:04x}/{i} {o.clock}refreshes',flush=True)
            traces.append(('\n'.join(lines)+'\n').encode())
        assert traces[0]==traces[1]
        with gzip.open(out/'original.txt.gz','wb') as f:f.write(traces[0])
        receipt=dict(passed=True,cases=len(rows),loads=['1000','2000'],packed_sha256=PACKED,payload_sha256=PAYLOAD,trace_sha256=sha(traces[0]),original_cpu_reexecuted=True,assets={n:sha(assets[n]) for n in NAMES},decoder_sha256=sha(a.decoder.read_bytes()))
    assert source_manifest(root)[0]==mf
    for q,digest in frozen.items():assert sha(q.read_bytes())==digest,('input changed',str(q))
    receipt.update(decoded_assets={q.name:sha(q.read_bytes()) for q in sorted((a.reference/'assets' if a.reference else out/'assets').glob('*.decoded'))},engine_sha256=sha(Path(__import__('unicorn').unicorn._uc._name).read_bytes()),input_hashes={str(q):h for q,h in frozen.items()},source_archive_sha256=sha((out/'source.tar.gz').read_bytes()),command=sys.argv,engine_version=__import__('unicorn').__version__,source_manifest=mf,source_files=len(files),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__);(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('startup PASS',len(rows))
if __name__=='__main__':main()
