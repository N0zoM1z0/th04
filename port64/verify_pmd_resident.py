#!/usr/bin/env python3
"""Original OP sound controls coupled to original resident COM services.

The two original CPU engines share typed service/resource adapters, not a
physical DOS address space. Fresh controls use a declared process-local seed;
actual OP/MAIN/MAINE startup is not executed here. PMD stays installed across
generations. Original chip timing uses pinned ymfm and the v1341 epoch/zero
CPU-latency convention. PCM uses an independent host renderer sharing ymfm
arithmetic. SE2 requests/state are compared, but mixed beeper PCM is excluded
from this waveform Oracle. No sound device, physical timing or exact claim.
"""
import argparse,gzip,hashlib,itertools,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from unicorn.x86_const import *
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_sound_control import Original as Controls,PACKED,PAYLOAD
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_pmd_clock import Chip
from verify_pmd_musical_fm import PORTS,mirror
from verify_cutscene import ending_assets
from verify_pmd_pcm import compressed

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def operations(bgm,se):
    return ([('T',0,1,bgm,se),('L',0x600,'logo'),('K',0)]
        +[('A',17730496)]*8+[('K',0x500),('T',1,2,bgm,se),('L',0x600,'st00'),('K',0),('E',4),('U',1),('A',1000000000),('E',7),('U',1),('A',1000000000),('Z',),('T',2,3,bgm,se),('L',0x600,'end1'),('K',0)]
        +[('A',1000000000)]*4+[('K',0x204)]+[('A',1000000000)]*2
        +[('T',0,4,bgm,se),('L',0x600,'name'),('K',0),('A',999999999),('K',0x800),('K',0xa00),('K',0x100),('A',17730496),('K',0x500)])

class Coupled(Controls):
    def __init__(self,target,decoded,load,driver,chip,assets,hz):
        super().__init__(target,decoded,load)
        self.driver=driver;self.chip=chip;self.assets=assets;self.hz=hz
        self.program=3;self.generation=0;self.open=False;self.destination=None
        self.trace=[];self.timed=[];self.fraction=0;self.interrupts=0
    def emit(self,k,a=0,b=0,name='-'):
        self.trace.append(f'REQUEST {self.program} {self.generation} {k} {a} {b} {name}')
    def feedback(self):
        d=self.driver;base=PORTS[self.name]
        for _,port,size,value in d.ports:
            assert size==1
            if port in (base,base+4):d._resident_selected[port]=value
            elif port in (base+2,base+6):
                address=d._resident_selected[port-2];bank=(port-base-2)//4
                self.timed.append((self.chip.state[0],bank,address,value))
                if bank==0 and address in (0x24,0x25,0x26,0x27,0x29):self.chip.command(f'W {address} {value}')
        d.ports=[]
    def service(self,ax):
        result=self.driver.service(ax);self.feedback();return result
    def interrupt(self,u,number,unused):
        try:
            ax=u.reg_read(UC_X86_REG_AX)
            if number==0x60:
                self.emit('int',number,ax);result=self.service(ax);u.reg_write(UC_X86_REG_AX,result['ax'])
                if ax in (0x600,0xb00):
                    assert self.open
                    self.destination=(self.driver.load+result['ds'])*16+result['dx']
                    u.reg_write(UC_X86_REG_DS,0x8000);u.reg_write(UC_X86_REG_DX,0x4000)
            elif number==0x21:
                if ax==0x3d00:
                    assert not self.open and u.reg_read(UC_X86_REG_DS)==self.ds
                    name=self.string(self.ds,u.reg_read(UC_X86_REG_DX));self.emit('open',name=name)
                    self.file=self.assets[name.upper()];self.open=True;self.destination=None
                    u.reg_write(UC_X86_REG_AX,0x40)
                elif ax==0x3f00:
                    assert self.open and self.destination is not None and u.reg_read(UC_X86_REG_BX)==0x40 and u.reg_read(UC_X86_REG_CX)==0x5000
                    assert (u.reg_read(UC_X86_REG_DS),u.reg_read(UC_X86_REG_DX))==(0x8000,0x4000)
                    self.emit('read',0x5000);u.mem_write(0x84000,self.file)
                    self.driver.u.mem_write(self.destination,self.file);u.reg_write(UC_X86_REG_AX,len(self.file))
                else:
                    assert ax>>8==0x3e and self.open and u.reg_read(UC_X86_REG_BX)==0x40
                    self.emit('close');self.open=False;self.destination=None;u.reg_write(UC_X86_REG_AX,0)
            else:raise ValueError(f'unsupported coupled interrupt {number:02x}/{ax:04x}')
        except Exception as error:self.error=error;u.emu_stop()
    def enter(self,p,g,bgm,se):
        assert not self.open
        self.program=p;self.generation=g
        self.u.mem_write(self.load*16,self.module);self.u.mem_write(self.ds*16,self.data)
        self.write(0x9e0,'BBB',0,0,0);self.write(0x2638,'B',0x60);self.write(0xa40,'BB',255,0);self.u.mem_write(self.ds*16+0x2700,bytes(13))
        for interrupt,signature in [(0x60,b'PMD'),(0x61,b'BAD')]:
            off=0x1000+(interrupt-0x60)*0x100
            self.u.mem_write(interrupt*4,struct.pack('<HH',off,0x9000));self.u.mem_write(0x90000+off,b'\xeb\x03'+signature)
        self.invoke(0x2d4,(se,bgm))
        if p!=2:self.load_resource(0xb00,'miko')
    def load_resource(self,function,name):
        self.u.mem_write(self.ds*16+0x6000,name.encode()+bytes(13-len(name)))
        self.invoke(0x3ba,(function,0x6000,self.ds));assert not self.open
    def advance(self,ns):
        count,self.fraction=divmod(ns*self.hz+self.fraction,1000000000);end=self.chip.state[0]+count
        while True:
            next=min([end]+[t for t in self.chip.state[2:4] if t])
            state=self.chip.command(f'A {next}')
            if state[4]:
                self.interrupts+=1;self.driver.irq(state[1]);self.feedback();assert self.chip.state[1]==0
            if next==end:break
    def state(self,reply):
        se,bgm,midi=self.read(0x9e0,'BBB');irq=self.read(0x2638,'B')[0];playing,frame=self.read(0xa40,'BB')
        filename=bytes(self.u.mem_read(self.ds*16+0x2700,13)).hex()
        clock=self.chip.state[0];frames=clock*48000//self.hz
        values=[clock,self.fraction,frames]+[self.service(v)['ax'] for v in (0x500,0x800,0xa00)]+mirror(self.driver,self.name)
        self.trace.append(f'STATE {self.program} {self.generation} {reply} {bgm} {se} {midi} {irq} {playing} {frame} {filename} '+' '.join(map(str,values)))
    def run_operations(self,ops):
        for op,*values in ops:
            reply=0
            if op=='T':self.enter(*values)
            elif op=='L':self.load_resource(*values)
            elif op=='K':reply=self.invoke(0x264,(values[0],),0x1357)
            elif op=='A':self.advance(values[0])
            elif op=='E':self.invoke(0x8e2,(values[0],))
            elif op=='U':
                for _ in range(values[0]):self.invoke(0x91c)
            elif op=='Z':self.invoke(0x8d6)
            else:raise ValueError('resident operation')
            self.state(reply)

def archive(root,out,mf,files):
    with tarfile.open(out/'source.tar.gz','w:gz') as t:
        for f in files:assert sha(root/f['path'])==f['sha256'];t.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')

def produce(a,root,out,mf,files):
    mp=json.loads(a.model_profile.read_text());assert sha(a.model)==mp['binary_sha256'] and sha(Path(mp['command'][0]))==mp['compiler_sha256'] and sha(Path(mp['command'][4]))==mp['source_sha256']
    for n,h in mp['files'].items():assert sha(Path(n))==h
    rp=json.loads(a.renderer_profile.read_text());assert sha(a.renderer)==rp['binary_sha256'] and sha(Path(rp['source_path']))==rp['source_sha256'] and sha(Path(rp['command'][0]))==rp['compiler_sha256']
    for n,h in rp['external_inputs'].items():assert sha(Path(n))==h
    rom=json.loads(a.rom_profile.read_text());assert rom['passed'] and rom['size']==8192 and sha(a.rom)==rom['sha256']
    binaries=directory_files(a.hdi);assets=ending_assets(a.hdi);outputs={};cases=[];first={}
    archive(root,out,mf,files)
    for n,data in assets.items():
        if n.endswith(('.M26','.M86','.EFC','.EFS')):p=out/n;p.write_bytes(data);outputs[n]=sha(p)
    rom_path=out/'ym2608_adpcm_rom.bin';rom_path.write_bytes(a.rom.read_bytes());outputs[rom_path.name]=sha(rom_path)
    with Chip(a.model) as chip:
      for load in (0x1000,0x2000):
       for name,(_,_,board,ext,_) in DRIVERS.items():
        hz=4000000 if board==0 else 8000000
        for bgm,se in itertools.product(range(4),range(3)):
            d=install(binaries[name],name,load);chip.command(f'B {board}')
            if board:chip.command('W 41 131')
            for reg,val in [(0x24,0),(0x25,0),(0x26,200),(0x27,63)]:chip.command(f'W {reg} {val}')
            o=Coupled(a.target,a.decoded,load,d,chip,assets,hz);o.name=name;d._resident_selected={}
            for _,port,size,val in d.ports:
                base=PORTS[name]
                if port in (base,base+4):d._resident_selected[port]=val
                elif port in (base+2,base+6):
                    bank=(port-base-2)//4;address=d._resident_selected[port-2]
                    o.trace.append(f'INSTALL {bank} {address} {val}');o.timed.append((0,bank,address,val))
            d.ports=[];ops=operations(bgm,se);o.run_operations(ops)
            key=f'{name}-{bgm}-{se}';trace=('\n'.join(o.trace)+'\n').encode();events=''.join(' '.join(map(str,v))+'\n' for v in o.timed).encode()
            if key not in first:
                opfile=out/(key+'-operations.txt');opfile.write_text(f'Q {hz}\n'+''.join(' '.join(map(str,v))+'\n' for v in ops));outputs[opfile.name]=sha(opfile)
                target=out/(key+'.txt.gz');compressed(target,trace);outputs[target.name]=sha(target)
                first[key]=dict(reference=target.name,raw_sha256=hashlib.sha256(trace).hexdigest(),rows=len(o.trace),operations=opfile.name,end_cycle=chip.state[0],frames=chip.state[0]*48000//hz,interrupts=o.interrupts,pcm_compared=se!=2)
                ep=out/(key+'-events.txt');ep.write_bytes(events)
                if se!=2:
                    pcm=out/(key+'.pcm');subprocess.run([str(a.renderer),str(board),str(hz),str(a.rom),str(ep),str(chip.state[0]),str(pcm)],check=True)
                    raw=pcm.read_bytes();assert len(raw)==4*first[key]['frames'];p=pcm.with_suffix('.pcm.gz');compressed(p,raw);pcm.unlink();outputs[p.name]=sha(p)
                    first[key].update(pcm=p.name,pcm_sha256=hashlib.sha256(raw).hexdigest())
                p=ep.with_suffix('.txt.gz');compressed(p,events);ep.unlink();outputs[p.name]=sha(p);first[key]['events_sha256']=hashlib.sha256(events).hexdigest()
            else:assert first[key]['raw_sha256']==hashlib.sha256(trace).hexdigest() and first[key]['events_sha256']==hashlib.sha256(events).hexdigest()
            cases.append(dict(driver=name,board=board,load=load,bgm=bgm,se=se,hz=hz,**first[key]));print(f'Original resident {key} PSP{load:04x}: {len(o.trace)} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf and len(cases)==72
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),pcm_frames=sum(c['frames'] for c in cases if c['pcm_compared']),outputs=outputs,model_profile=mp,renderer_profile=rp,rom_profile=rom,hdi_sha256=HDI_SHA,target_sha256=PACKED,payload_sha256=PAYLOAD,drivers={n:dict(size=len(binaries[n]),sha256=hashlib.sha256(binaries[n]).hexdigest(),format='flat-COM',entry='PSP:0100',service='PSP:0103') for n in DRIVERS},unicorn_version=unicorn.__version__,engine_sha256=sha(Path(unicorn.unicorn._uc._name)),chip_independence=False,typed_buffer_bridge=True)

def consume(a,root,out,mf,files):
    ref=a.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==72
    frozen={binary.resolve():sha(binary) for binary in a.binary}
    reference_sha=sha(ref/'receipt.json')
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    archive(root,out,mf,files);outputs={};runs=[]
    for binary in a.binary:
        binary=binary.resolve();(require_pe_x86_64 if binary.suffix=='.exe' else require_elf_x86_64)(binary);folder=out/binary.parent.name;folder.mkdir();done={}
        for c in r['cases']:
            key=c['driver'],c['bgm'],c['se']
            if key not in done:
                name=f'{c["driver"]}-{c["bgm"]}-{c["se"]}';trace=folder/(name+'.txt');pcm=folder/(name+'.pcm')
                subprocess.run([str(binary),str(ref/'MIKO.EFC'),str(c['board']),str(ref/'ym2608_adpcm_rom.bin'),str(ref/c['operations']),str(trace),str(pcm)],check=True);done[key]=(trace,pcm)
            expected=gzip.decompress((ref/c['reference']).read_bytes());actual=done[key][0].read_bytes();assert hashlib.sha256(expected).hexdigest()==c['raw_sha256']
            if actual!=expected:
                x=actual.splitlines();y=expected.splitlines();at=next((i for i,(u,v) in enumerate(zip(x,y)) if u!=v),min(len(x),len(y)))
                (folder/'mismatch.json').write_text(json.dumps(dict(case=key,row=at,expected=str(y[at:at+1]),actual=str(x[at:at+1])),indent=2));raise ValueError(f'resident {key} row{at} differs')
            raw=done[key][1].read_bytes();assert len(raw)==4*c['frames']
            if c['pcm_compared']:
                expected=gzip.decompress((ref/c['pcm']).read_bytes());assert hashlib.sha256(expected).hexdigest()==c['pcm_sha256']
                if raw!=expected:
                    at=next((i for i in range(0,min(len(raw),len(expected)),4) if raw[i:i+4]!=expected[i:i+4]),min(len(raw),len(expected)))
                    raise ValueError(f'resident PCM {key} frame{at//4}: {expected[at:at+4].hex()}/{raw[at:at+4].hex()}')
        for pair in done.values():
            for p in pair:
                target=p.with_suffix(p.suffix+'.gz');compressed(target,p.read_bytes());p.unlink();outputs[target.relative_to(out).as_posix()]=sha(target)
        runs.append(dict(binary=str(binary),binary_sha256=sha(binary),unique_runs=len(done),rows=r['rows'],pcm_frames=r['pcm_frames']));print(f'Native resident {binary.parent.name}: {r["rows"]} rows/{r["pcm_frames"]} compared PCM frames PASS',flush=True)
        for path,digest in frozen.items():assert sha(path)==digest,('binary changed during resident run',str(path))
    assert source_manifest(root)[0]==mf
    assert sha(ref/'receipt.json')==reference_sha
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    return dict(runs=runs,outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'],chip_independence=False,typed_buffer_bridge=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('hdi','target','decoded','model','model-profile','renderer','renderer-profile','rom','rom-profile','reference'):p.add_argument('--'+name,type=Path)
    p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    producer=bool(a.hdi)
    if producer==bool(a.reference) or bool(a.reference)!=bool(a.binary) or any(producer!=bool(getattr(a,n)) for n in ('target','decoded','model','model_profile','renderer','renderer_profile','rom','rom_profile')):p.error('choose original inputs/profiles or reference and native binaries')
    if producer:a.model=a.model.resolve();a.renderer=a.renderer.resolve()
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    r=produce(a,root,out,mf,files) if producer else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),source_archive_sha256=sha(out/'source.tar.gz'),command=sys.argv,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
