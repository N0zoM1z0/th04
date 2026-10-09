#!/usr/bin/env python3
"""Continuous PMD timer comparison against original COM and pinned independent ymfm.

Clock frequency, reset FM epoch and zero CPU/bus latency are explicit adapters.
No physical board timing, PCM, frontend, whole-game or DOS exact claim follows.
All runs are CPU-only and open no audio device or backend.
"""
import argparse,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets
from verify_pmd_fm_player import PublishedView
from verify_pmd_musical_fm import mirror,PORTS
from verify_pmd_timer_player import challenges,original_row
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def operations():
    return ([('R',0),('A',1)]+[('A',17730496)]*96+[('P',4),('G',24)]+[('A',333333333)]*9
        +[('F',127),('A',1000000000),('A',1000000000),('M',0),('A',1000000000),('R',0)]
        +[('A',1000000000)]*3+[('F',-7),('A',1000000000),('H',0),('S',0),('C',72),('C',143),('A',0),('M',0),('R',0),('A',999999999)])

class Chip:
    def __init__(self,binary):
        self.p=subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);self.state=None
    def command(self,line):
        self.p.stdin.write(line+'\n');self.p.stdin.flush();reply=self.p.stdout.readline()
        if not reply:raise ValueError('independent chip stopped: '+self.p.stderr.read())
        self.state=list(map(int,reply.split()));assert len(self.state)==5;return self.state
    def close(self):
        self.p.stdin.close();code=self.p.wait(timeout=30);error=self.p.stderr.read();assert code==0 and not error,(code,error)
    def __enter__(self):return self
    def __exit__(self,kind,value,tb):
        if kind:self.p.kill();self.p.wait(timeout=30)
        else:self.close()

def produce(a,root,out,mf,files):
    profile=json.loads(a.model_profile.read_text());assert profile['revision']=='81aec25ccbb98f4873a255f7551ac4dadac59b4a'
    assert sha(a.model)==profile['binary_sha256']
    assert sha(Path(profile['command'][0]))==profile['compiler_sha256']
    assert sha(Path(profile['command'][4]))==profile['source_sha256']
    for n,h in profile['files'].items():assert sha(Path(n))==h
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as t:
        for f in files:assert sha(root/f['path'])==f['sha256'];t.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
    outputs={};cases=[];checks=0;first={};frozen=[f for f in files if f['path'].endswith('.py')]
    binaries=directory_files(a.hdi);assets=ending_assets(a.hdi);ops=operations()
    for name,data in [('MIKO.EFC',assets['MIKO.EFC'])]:p=out/name;p.write_bytes(data);outputs[name]=sha(p)
    with Chip(a.model) as chip:
      for load in (0x1000,0x2000):
        for name,(_,_,board,ext,_) in DRIVERS.items():
          songs={n:v for n,v in assets.items() if n.endswith('.'+ext)};songs.update(challenges(ext))
          for song,data in sorted(songs.items()):
            hz=4000000 if board==0 else 8000000
            d=install(binaries[name],name,load);address=d.write_resource(0xb00,assets['MIKO.EFC'])['offset'];d.write_resource(0x600,data);view=PublishedView(d,address)
            initial=out/(name+'-mirror.txt');raw=(' '.join(map(str,mirror(d,name)))+'\n').encode()
            if initial.exists():assert initial.read_bytes()==raw
            else:initial.write_bytes(raw)
            resource=out/song
            if resource.exists():assert resource.read_bytes()==data
            else:resource.write_bytes(data)
            oplist=out/('operations-'+str(board)+'.txt');raw=('Q '+str(hz)+'\n'+''.join(f'{op} {v}\n' for op,v in ops)).encode()
            if oplist.exists():assert oplist.read_bytes()==raw
            else:oplist.write_bytes(raw)
            base=PORTS[name];chip.command(f'B {board}')
            assert [d.registers.get((base,x)) for x in (0x24,0x25,0x26,0x27)]==[0,0,200,63]
            if board:chip.command('W 41 131')
            for reg,val in [(0x24,0),(0x25,0),(0x26,200),(0x27,63)]:chip.command(f'W {reg} {val}')
            irq_count=0;fraction=0;rows=0;digest=hashlib.sha256();path=out/f'{name}-{load:04x}-{song}.txt.gz'
            def feedback():
                for _,port,size,val in d.ports:
                    if port==base:d._clock_address=val
                    elif port==base+2 and getattr(d,'_clock_address',-1) in (0x24,0x25,0x26,0x27,0x29):chip.command(f'W {d._clock_address} {val}')
            with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as stream:
                def emit(flags):
                    nonlocal rows,checks
                    body=original_row(view,name,address,binaries[name])
                    if rows%257==0:assert body==original_row(d,name,address,binaries[name]);checks+=1
                    now,status,da,db,_=chip.state
                    row=[now,status,da,db,irq_count,flags]+body;raw=(' '.join(map(str,row))+'\n').encode();stream.write(raw);digest.update(raw);rows+=1
                for tick,(op,v) in enumerate(ops):
                    d.ticks=tick;d.ports=[]
                    if op in ('A','C'):
                        if op=='A':count,fraction=divmod(v*hz+fraction,1000000000)
                        else:count=v
                        end=chip.state[0]+count
                        while True:
                            next=min([end]+[t for t in chip.state[2:4] if t])
                            state=chip.command(f'A {next}')
                            if state[4]:
                                flags=state[1];irq_count+=1;d.ports=[];d.irq(flags);feedback();assert chip.state[1]==0;emit(flags);d.ports=[]
                            if next==end:break
                    else:
                        d.service({'R':0,'M':0x100,'P':0xc00|v,'S':0xd00,'G':0x300|v,'H':0x400,'F':0x200|(v&255)}[op]);feedback()
                    emit(0)
            key=name,song;raw_digest=digest.hexdigest()
            if key in first:assert first[key]==(raw_digest,rows),key
            first[key]=(raw_digest,rows)
            for p in (initial,resource,oplist,path):outputs[p.name]=sha(p)
            cases.append(dict(driver=name,board=board,song=song,load=load,hz=hz,mirror=initial.name,operations=oplist.name,reference=path.name,raw_sha256=raw_digest,rows=rows,interrupts=irq_count,end_cycle=chip.state[0],fraction=fraction))
            print(f'Original clock {name} {song} PSP{load:04x}: {irq_count} IRQs/{rows} rows PASS',flush=True)
    for f in frozen:assert sha(root/f['path'])==f['sha256']
    assert len(cases)==174
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),interrupts=sum(c['interrupts'] for c in cases),outputs=outputs,observer_service_crosschecks=checks,model_profile=profile,model_profile_sha256=sha(a.model_profile),producer_tools=frozen,producer_source_archive_sha256=sha(out/'producer-source.tar.gz'),hdi_sha256=HDI_SHA,drivers={n:dict(size=len(binaries[n]),sha256=hashlib.sha256(binaries[n]).hexdigest(),format='flat-COM',entry='PSP:0100',service='PSP:0103') for n in DRIVERS},unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))

def consume(a,root,out,mf,files):
    ref=a.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==174
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    outputs={};results=[]
    for binary in a.binary:
        binary=binary.resolve();(require_pe_x86_64 if binary.suffix=='.exe' else require_elf_x86_64)(binary);folder=out/binary.parent.name;folder.mkdir();done={}
        for c in r['cases']:
            key=c['driver'],c['song']
            if key not in done:
                target=folder/f'{c["driver"]}-{c["song"]}.txt';subprocess.run([str(binary),str(ref/c['song']),str(ref/'MIKO.EFC'),str(c['board']),str(ref/c['mirror']),str(ref/c['operations']),str(target)],check=True);done[key]=target
            expected=gzip.decompress((ref/c['reference']).read_bytes());actual=done[key].read_bytes();assert hashlib.sha256(expected).hexdigest()==c['raw_sha256']
            if actual!=expected:
                for row,(x,y) in enumerate(zip(expected.splitlines(),actual.splitlines())):
                    if x!=y:
                        aa=list(map(int,x.split()));bb=list(map(int,y.split()));diff=[(j,u,v) for j,(u,v) in enumerate(zip(aa,bb)) if u!=v];raise ValueError(f'PMD clock {binary.parent.name} {key} row{row}: {diff[:16]}, lengths{len(aa)}/{len(bb)}')
                raise ValueError('PMD clock row count differs')
        for target in done.values():
            raw=target.read_bytes();p=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(raw)
            assert gzip.decompress(p.read_bytes())==raw;target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),rows=r['rows']));print(f'Native clock {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,rows=r['rows'],outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--model',type=Path);p.add_argument('--model-profile',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference) or bool(a.reference)!=bool(a.binary) or bool(a.hdi)!=bool(a.model) or bool(a.hdi)!=bool(a.model_profile):p.error('choose original HDI with model/profile, or reference with binaries')
    if a.model:a.model=a.model.resolve()
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
