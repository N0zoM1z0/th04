#!/usr/bin/env python3
"""Original resident timer writes join complete FM/SSG/effect/rhythm ownership.

Compare primary 24..27 mirrors and the complete chronological owned union,
including acknowledge before parsing, final tempo commit and start/restart.
Original COM executes at two PSPs; IRQ flags remain explicit adapters. No
physical clock, waveform, frontend, whole-game or DOS exact claim follows.
All runs remain muted and open no audio device/backend.
"""
import argparse,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets
from verify_pmd_fm_player import PublishedView
from verify_pmd_combined import original_row as combined_row,challenges as mixed_challenges
from verify_pmd_musical_fm import mirror,PORTS
from verify_pmd_rhythm import original_row as rhythm_row,resource
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def operations():
    r=[('R',0),('I',0),('I',1),('I',2),('I',3)]+[('I',3)]*128
    r += [('P',4),('G',24)]+[('I',0),('I',1),('I',2),('I',3)]*16
    r += [('F',127)]+[('I',1)]*24+[('I',0),('I',2),('I',3),('M',0)]
    r += [('I',0),('I',1),('I',2),('I',3)]*8+[('R',0)]+[('I',3)]*128
    r += [('H',0),('S',0),('F',-7)]+[('I',1)]*64+[('M',0),('R',0),('I',0),('I',2)]
    return r

def challenges(extension):
    result={};program=[]
    for value in (0,1,18,64,128,200,249,250):program += [252,value,64,1]
    for mode in (255,254,253):
        for value in (0,1,18,127,128,200,255):program += [252,mode,value,64,1]
    for part,label in [(0,'FM'),(6,'SSG')]:
        prefix=[255,7] if part==0 else [240,0,254,1,1]
        result['TIM'+label+'.'+extension]=resource(extension,{part:bytes(prefix+program+[128])},[bytes([0,1,255])])
    rhythm=[]
    for value in (1,18,128,200,249,250):rhythm += [252,value,0]
    result['TIMRHY.'+extension]=resource(extension,{10:bytes(rhythm+[128])},[bytes([0,1,255])])
    result['TIMORDER.'+extension]=resource(extension,{0:bytes([255,7,252,111,64,1,252,112,64,1,128]),3:bytes([255,7,252,151,64,1,252,152,64,1,128]),6:bytes([240,0,254,1,1,252,181,64,1,252,182,64,1,128])},[bytes([0,1,255])])
    result['TIMSAME.'+extension]=resource(extension,{0:bytes([255,7,252,200,252,200,64,1,252,200,64,1,128])},[bytes([0,1,255])])
    result['TIMFADE.'+extension]=resource(extension,{0:bytes([255,7,252,134,64,1,210,127,64,64,128])},[bytes([0,1,255])])
    assert len(result)==6;return result

def original_row(d,name,address,binary):
    row=rhythm_row(d,name,address,binary);at=1130 if name=='PMD.COM' else 1136
    extra=mirror(d,name)[0x24:0x28]
    ports={PORTS[name]:0,PORTS[name]+4:1};selected={};writes=[]
    for _,port,size,value in d.ports:
        if port in ports:selected[ports[port]]=value
        elif port-2 in ports:
            bank=ports[port-2];register=selected.get(bank)
            if register is not None and (48<=register<=182 or (bank==0 and (register in (34,40) or register<14 or 16<=register<32 or 0x24<=register<=0x27))):writes += [bank,register,value]
    return row[:at]+extra+[len(writes)//3]+writes

def produce(args,root,out,mf,files):
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as t:
        for f in files:assert sha(root/f['path'])==f['sha256'];t.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n');frozen=[f for f in files if f['path'].endswith('.py')]
    binaries=directory_files(args.hdi);assets=ending_assets(args.hdi);ops=operations();outputs={};cases=[];first={};checks=0
    for p,data in [(out/'MIKO.EFC',assets['MIKO.EFC']),(out/'operations.txt',''.join(f'{op} {v}\n' for op,v in ops).encode())]:p.write_bytes(data);outputs[p.name]=sha(p)
    for load in (0x1000,0x2000):
        for name,(_,_,board,ext,_) in DRIVERS.items():
            songs={n:v for n,v in assets.items() if n.endswith('.'+ext)};songs.update(challenges(ext))
            for song,data in sorted(songs.items()):
                d=install(binaries[name],name,load);address=d.write_resource(0xb00,assets['MIKO.EFC'])['offset'];d.write_resource(0x600,data);view=PublishedView(d,address)
                initial=out/(name+'-mirror.txt');raw=(' '.join(map(str,mirror(d,name)))+'\n').encode()
                if initial.exists():assert initial.read_bytes()==raw
                else:initial.write_bytes(raw)
                resource_file=out/song
                if resource_file.exists():assert resource_file.read_bytes()==data
                else:resource_file.write_bytes(data)
                path=out/f'{name}-{load:04x}-{song}.txt.gz';digest=hashlib.sha256()
                with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as stream:
                    for tick,(op,v) in enumerate(ops):
                        d.ticks=tick;d.ports=[]
                        if op=='I':d.irq(v)
                        else:d.service({'R':0,'M':0x100,'P':0xc00|v,'S':0xd00,'G':0x300|v,'H':0x400,'F':0x200|(v&255)}[op])
                        row=original_row(view,name,address,binaries[name])
                        if op!='I' or tick%257==0:assert row==original_row(d,name,address,binaries[name]);checks+=1
                        raw=(' '.join(map(str,row))+'\n').encode();stream.write(raw);digest.update(raw)
                key=name,song;raw_digest=digest.hexdigest()
                if key in first:assert first[key]==raw_digest,key
                first[key]=raw_digest
                for p in (initial,resource_file,path):outputs[p.name]=sha(p)
                cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,raw_sha256=raw_digest,rows=len(ops)));print(f'Original PMD timer player {name} {song} PSP{load:04x}: {len(ops)} rows PASS',flush=True)
    for f in frozen:assert sha(root/f['path'])==f['sha256']
    assert len(cases)==174
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),outputs=outputs,observer_service_crosschecks=checks,producer_tools=frozen,producer_source_archive_sha256=sha(out/'producer-source.tar.gz'),hdi_sha256=HDI_SHA,drivers={n:dict(size=len(binaries[n]),sha256=hashlib.sha256(binaries[n]).hexdigest(),entry='PSP:0100',service='PSP:0103',format='flat-COM') for n in DRIVERS},unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))

def consume(args,root,out,mf,files):
    ref=args.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==174
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    outputs={};results=[]
    for binary in args.binary:
        binary=binary.resolve();(require_pe_x86_64 if binary.suffix=='.exe' else require_elf_x86_64)(binary);folder=out/binary.parent.name;folder.mkdir();done={}
        for c in r['cases']:
            key=c['driver'],c['song']
            if key not in done:
                target=folder/f'{c["driver"]}-{c["song"]}.txt';subprocess.run([str(binary),str(ref/c['song']),str(ref/'MIKO.EFC'),str(c['board']),str(ref/c['mirror']),str(ref/'operations.txt'),str(target)],check=True);done[key]=target
            expected=gzip.decompress((ref/c['reference']).read_bytes());actual=done[key].read_bytes();assert hashlib.sha256(expected).hexdigest()==c['raw_sha256']
            if actual!=expected:
                for row,(x,y) in enumerate(zip(expected.splitlines(),actual.splitlines())):
                    if x!=y:
                        a=list(map(int,x.split()));b=list(map(int,y.split()));diff=[(j,u,v) for j,(u,v) in enumerate(zip(a,b)) if u!=v];raise ValueError(f'PMD timer player {binary.parent.name} {key} row{row}: {diff[:16]}, lengths{len(a)}/{len(b)}')
                raise ValueError('PMD timer player length differs')
        for target in done.values():
            raw=target.read_bytes();p=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(raw)
            assert gzip.decompress(p.read_bytes())==raw;target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),rows=r['rows']));print(f'Native PMD timer player {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,rows=r['rows'],outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference) or bool(a.reference)!=bool(a.binary):p.error('choose original HDI or reference with binaries')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
