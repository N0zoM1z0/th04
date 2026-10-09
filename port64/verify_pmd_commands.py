#!/usr/bin/env python3
"""Original D4/D3 musical effect commands and D2/fade request boundaries.

Retains the whole configured combined FM/SSG state and chronological write
union, plus fade speed, musical fade marker, deferred request, playing and
fade-stop policy. Unchanged original COMs run independently authored music;
only work/resource pointers become relative. Synthesis, physical clocks,
PPS/FM3extras/ADPCM/rhythm, frontend/fullroutes and DOS exact remain separate.
No audio device/backend opens. Producer Python freezes during execution.
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
from verify_pmd_musical_fm import mirror
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def operations():
    result=[('R',0)]+[('I',3)]*32+[('P',4),('G',24)]+[('I',1)]*8+[('I',0)]*4+[('I',2)]*8+[('I',3)]*256
    result += [('H',0),('S',0)]+[('I',3)]*32+[('F',127)]+[('I',1)]*24+[('I',0),('I',1),('I',2)]
    result += [('M',0),('R',0)]+[('I',3)]*256+[('G',11),('P',7),('M',0)]+[('I',1)]*32+[('R',0)]+[('I',3)]*256
    result += [('H',0),('S',0),('F',-7)]+[('I',1)]*64+[('M',0)]
    return result

def resource(extension,part,program):
    seed=mixed_challenges(extension)['MIX0.'+extension];voice=struct.unpack_from('<H',seed,25)[0]+1;data=bytearray(27)
    for p in range(11):
        struct.pack_into('<H',data,1+2*p,len(data)-1)
        if p==part:data+=program
        elif p<3 or (extension=='M86' and p<6):data+=bytes([255,7,253,100,64+p,64,15,8,128])
        elif 6<=p<=8:data+=bytes([253,10,240,0,254,1,1,64,64,15,8,128])
        else:data+=b'\x80'
    table=len(data);struct.pack_into('<H',data,23,table-1);data+=struct.pack('<H',table+1)+b'\x80'
    struct.pack_into('<H',data,25,len(data)-1);data+=seed[voice:];return bytes(data)

def challenges(extension):
    result={}
    for part in (0,2,5,6,8):
        for masked in (False,True):
            program=([255,7,253,100] if part<6 else [253,10,240,0,254,1,1])+[64,2]
            if masked:program += [192,1,210,0]
            for effect in range(1,40):program += [212,effect,65,2,212,0,66,2]
            for effect in range(1,17):program += [211,effect,64,2,211,0,67,2]
            if masked:program += [192,0,212,11,64,2,211,4,65,2,212,0,211,0,66,2]
            program += [128];name=f'CMD{part}'+('MASK' if masked else '')+'.'+extension
            result[name]=resource(extension,part,bytes(program))
    for label,part,speed,masked in [('ZERO',0,0,False),('CARRY',0,127,False),('BOUNDARY',0,85,False),('BACK',0,249,False),('MASK',0,127,True),('SSG',6,127,False),('SSGMASK',6,127,True)]:
        program=[255,7,64,2] if part<6 else [240,0,254,1,1,64,2]
        if masked:program += [192,1]
        program += [210,speed,65,64,128];result['FADE'+label+'.'+extension]=resource(extension,part,bytes(program))
    assert len(result)==17;return result

def original_row(d,name,address,binary):
    row=combined_row(d,name,address,binary);at=1073 if name=='PMD.COM' else 1079
    work=d.service(0x1000);table=(d.load+work['ds'])*16+work['dx']
    # Independent target anchors: request PSP3185/4050/3C59; the common
    # -220 guess reads last Timer A on26/B2 and is a recorded rejected view.
    offsets=(-128,-61,-220 if name=='PMD86.COM' else -219,-88,-86)
    extra=[d.u.mem_read(table+offset,1)[0] for offset in offsets]
    return row[:at]+extra+row[at:]

def produce(args,root,out,mf,files):
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as t:
        for f in files:assert sha(root/f['path'])==f['sha256'];t.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n');frozen=[f for f in files if f['path'].endswith('.py')]
    binaries=directory_files(args.hdi);assets=ending_assets(args.hdi);ops=operations();outputs={};cases=[];first={};checks=0
    for p,data in [(out/'MIKO.EFC',assets['MIKO.EFC']),(out/'operations.txt',''.join(f'{op} {v}\n' for op,v in ops).encode())]:p.write_bytes(data);outputs[p.name]=sha(p)
    for load in (0x1000,0x2000):
        for name,(_,_,board,ext,_) in DRIVERS.items():
            for song,data in sorted(challenges(ext).items()):
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
                cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,raw_sha256=raw_digest,rows=len(ops)));print(f'Original PMD commands {name} {song} PSP{load:04x}: {len(ops)} rows PASS',flush=True)
    for f in frozen:assert sha(root/f['path'])==f['sha256']
    assert len(cases)==102
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),outputs=outputs,observer_service_crosschecks=checks,producer_tools=frozen,producer_source_archive_sha256=sha(out/'producer-source.tar.gz'),hdi_sha256=HDI_SHA,drivers={n:dict(size=len(binaries[n]),sha256=hashlib.sha256(binaries[n]).hexdigest(),entry='PSP:0100',service='PSP:0103',format='flat-COM') for n in DRIVERS},unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))

def consume(args,root,out,mf,files):
    ref=args.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==102
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
                        a=list(map(int,x.split()));b=list(map(int,y.split()));diff=[(j,u,v) for j,(u,v) in enumerate(zip(a,b)) if u!=v];raise ValueError(f'PMD commands {binary.parent.name} {key} row{row}: {diff[:16]}, lengths{len(a)}/{len(b)}')
                raise ValueError('PMD commands length differs')
        for target in done.values():
            raw=target.read_bytes();p=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(raw)
            assert gzip.decompress(p.read_bytes())==raw;target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),rows=r['rows']));print(f'Native PMD commands {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,rows=r['rows'],outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference) or bool(a.reference)!=bool(a.binary):p.error('choose original HDI or reference with binaries')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
