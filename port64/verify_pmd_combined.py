#!/usr/bin/env python3
"""Original combined musical FM/SSG and both effect owners.

Compares the union of retained FM and SSG state with every owned chronological
write, keeping banks and duplicates. Only resource/work pointers are relative.
Unchanged original COMs execute supplied and independently authored music.
No synthesis, physical clock, ADPCM/rhythm/FM3extras, frontend/fullroute or DOS
exact acceptance; this CPU-only verifier opens no audio device/backend.
"""
import argparse,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets
from verify_pmd_fm_player import PublishedView,original_row as fm_row,challenges as fm_challenges
from verify_pmd_musical_ssg import original_row as ssg_row,challenges as ssg_challenges
from verify_pmd_musical_fm import mirror,PORTS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def operations():
    result=[('R',0)]+[('I',3)]*64
    for e in range(17):
        result += [('P',e),('G',(e*7)%40)]+[('I',2)]*8+[('I',0)]*4+[('I',1)]*128+[('I',3)]*64
        result += [('G',11),('G',0),('P',e)]+[('I',3)]*8+[('P',(e+1)%17),('H',0)]+[('I',3)]*16+[('S',0)]+[('I',3)]*16
        result += [('G',12),('P',e),('M',0)]+[('I',3)]*32+[('R',0)]+[('I',3)]*32+[('H',0)]
    for e in range(40):
        result += [('H',0),('G',e)]+[('I',3)]*32+[('M',0),('R',0)]+[('I',3)]*8
    result += [('F',4)]+[('I',1)]*64+[('F',-7)]+[('I',3)]*64+[('H',0),('S',0),('M',0)]
    return result

def challenges(extension):
    result={};fm=fm_challenges(extension)['SHARE2.'+extension];sg=ssg_challenges(extension)
    pointer=lambda data,p:struct.unpack_from('<H',data,1+2*p)[0]+1
    voice=struct.unpack_from('<H',fm,25)[0]+1;fm_count=6 if extension=='M86' else 3
    for variant in range(7):
        parts={}
        for p in range(fm_count):
            start=pointer(fm,p);end=pointer(fm,p+1)
            prefix=[203,variant,188,(variant+2)%7,202,1,187,1,183,3,183,130]
            if extension=='M86':prefix += [177,3]
            parts[p]=bytes(prefix)+fm[start:end]
        data=sg[f'SSG{variant}.{extension}']
        for p in range(6,9):
            start=pointer(data,p);end=pointer(data,p+1) if p<8 else struct.unpack_from('<H',data,25)[0]+1
            parts[p]=data[start:end]
        parts[10]=bytes([0,128]);out=bytearray(27)
        for p in range(11):
            if p not in parts:continue
            struct.pack_into('<H',out,1+2*p,len(out)-1);out+=parts[p]
        empty=len(out);out+=b'\x80'
        for p in range(11):
            if p not in parts:struct.pack_into('<H',out,1+2*p,empty-1)
        table=len(out);struct.pack_into('<H',out,23,table-1);out+=struct.pack('<H',table+1)
        effect=11 if variant&1 else 0;mask=1<<effect;out+=bytes([128|(mask>>8),mask&255,8,255])
        struct.pack_into('<H',out,25,len(out)-1);out+=fm[voice:];result[f'MIX{variant}.{extension}']=bytes(out)
    return result

def original_row(d,name,address,binary):
    row=fm_row(d,name,address)[:751]+ssg_row(d,name,binary)[:322 if name=='PMD.COM' else 328]
    ports={PORTS[name]:0,PORTS[name]+4:1};selected={};writes=[]
    for _,port,size,value in d.ports:
        if port in ports:selected[ports[port]]=value
        elif port-2 in ports:
            bank=ports[port-2];a=selected.get(bank)
            if a is not None and ((48<=a<=182) or (bank==0 and (a in (34,40) or a<14))):
                if size!=1:raise ValueError('combined non-byte write')
                writes += [bank,a,value]
    return row+[len(writes)//3]+writes

def produce(args,root,out,mf,files):
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as t:
        for f in files:assert sha(root/f['path'])==f['sha256'];t.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n');frozen=[f for f in files if f['path'].endswith('.py')]
    binaries=directory_files(args.hdi);assets=ending_assets(args.hdi);ops=operations();outputs={};cases=[];first={};checks=0
    for p,data in [(out/'MIKO.EFC',assets['MIKO.EFC']),(out/'operations.txt',''.join(f'{op} {v}\n' for op,v in ops).encode())]:p.write_bytes(data);outputs[p.name]=sha(p)
    for load in (0x1000,0x2000):
        for name,(_,_,board,ext,_) in DRIVERS.items():
            songs={n+'.'+ext:assets[n+'.'+ext] for n in ('LOGO','OP','ST05B','STAFF')};songs.update(challenges(ext))
            for song,data in sorted(songs.items()):
                d=install(binaries[name],name,load);address=d.write_resource(0xb00,assets['MIKO.EFC'])['offset'];d.write_resource(0x600,data);view=PublishedView(d,address)
                initial=out/(name+'-mirror.txt');raw=(' '.join(map(str,mirror(d,name)))+'\n').encode()
                if initial.exists():assert initial.read_bytes()==raw
                else:initial.write_bytes(raw)
                resource=out/song
                if resource.exists():assert resource.read_bytes()==data
                else:resource.write_bytes(data)
                path=out/f'{name}-{load:04x}-{song}.txt.gz';digest=hashlib.sha256()
                with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:
                    for tick,(op,v) in enumerate(ops):
                        d.ticks=tick;d.ports=[]
                        if op=='I':d.irq(v)
                        else:d.service({'R':0,'M':0x100,'P':0xc00|v,'S':0xd00,'G':0x300|v,'H':0x400,'F':0x200|(v&255)}[op])
                        row=original_row(view,name,address,binaries[name])
                        if op!='I' or tick%257==0:assert row==original_row(d,name,address,binaries[name]);checks+=1
                        raw=(' '.join(map(str,row))+'\n').encode();f.write(raw);digest.update(raw)
                key=name,song;raw_digest=digest.hexdigest()
                if key in first:assert first[key]==raw_digest,key
                first[key]=raw_digest
                for p in (initial,resource,path):outputs[p.name]=sha(p)
                cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,raw_sha256=raw_digest,rows=len(ops)));print(f'Original combined {name} {song} PSP{load:04x}: {len(ops)} rows PASS',flush=True)
    for f in frozen:assert sha(root/f['path'])==f['sha256']
    assert len(cases)==66
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),outputs=outputs,observer_service_crosschecks=checks,producer_tools=frozen,producer_source_archive_sha256=sha(out/'producer-source.tar.gz'),hdi_sha256=HDI_SHA,drivers={n:dict(size=len(binaries[n]),sha256=hashlib.sha256(binaries[n]).hexdigest(),entry='PSP:0100',service='PSP:0103',format='flat-COM') for n in DRIVERS},unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))

def consume(args,root,out,mf,files):
    ref=args.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==66
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
                        a=list(map(int,x.split()));b=list(map(int,y.split()));diff=[(j,u,v) for j,(u,v) in enumerate(zip(a,b)) if u!=v];raise ValueError(f'Combined {binary.parent.name} {key} row{row}: {diff[:16]}, lengths{len(a)}/{len(b)}')
                raise ValueError('combined length differs')
        for target in done.values():
            raw=target.read_bytes();p=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(raw)
            assert gzip.decompress(p.read_bytes())==raw;target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),rows=r['rows']));print(f'Native combined {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,rows=r['rows'],outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference) or bool(a.reference)!=bool(a.binary):p.error('choose original HDI or reference with binaries')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
