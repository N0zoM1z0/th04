#!/usr/bin/env python3
"""Original simultaneous FM music/effect state, masks and ordered requests.

Unchanged drivers execute supplied and constructed music with MIKO.EFC.
DOS/board/explicit Timer A/B IRQs remain adapters. Compares all selected
six-part musical FM fields,42 effect fields,272 owned FM mirrors and all
ordered owned writes. Musical SSG/FM3 extra tracks/ADPCM/rhythm, synthesis,
physical timers, frontend capability and complete natural routes remain
outside this owner. No audio device/backend or historical exact promotion.
"""
import argparse,gzip,hashlib,json,subprocess,sys,tarfile,struct
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets
from verify_pmd_musical_fm import original_row as music_row,mirror
from verify_pmd_fm import original_row as effect_row
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def operations():
    result=[('R',0)]+[('I',3)]*64
    for e in range(17):
        result += [('P',e)]+[('I',2)]*8+[('I',0)]*4+[('I',1)]*256+[('I',3)]*128
        result += [('P',e)]+[('I',3)]*8+[('P',(e+1)%17)]+[('I',3)]*16+[('S',0)]+[('I',3)]*32
        result += [('P',e),('M',0)]+[('I',3)]*64+[('R',0)]+[('I',3)]*64
    result += [('F',4)]+[('I',1)]*64+[('F',-7)]+[('I',3)]*64
    return result

def challenges(extension):
    result={}
    for variant in range(3):
        programs=[]
        for p in range(6 if extension=='M86' else 3):
            length=64 if variant==0 else 12
            phrase=[255,7,253,100,254,2,242,0,2,3,4,241,3,191,0,2,254,3,190,3]
            if variant==2:phrase += [181,3,4,228,6,225,3,224,8]
            phrase += [64+p,length,251,68+p,length,255,8,15,8,69+p,length,218,64,80,16,76,12,128]
            programs.append(bytes(phrase))
        data=bytearray(27);offset=27
        for p,program in enumerate(programs):struct.pack_into('<H',data,1+2*p,offset-1);offset+=len(program)
        for p in range(len(programs),12):struct.pack_into('<H',data,1+2*p,offset-1)
        struct.pack_into('<H',data,25,offset)
        for program in programs:data+=program
        data+=b'\x80'
        for id,algo in ((7,60),(8,56)):
            data+=bytes([id,*([1]*4),12,20,30,0,*([31]*4),*([7]*4),*([3]*4),*([15]*4),algo])
        data+=b'\xff';result[f'SHARE{variant}.{extension}']=bytes(data)
    return result

class PublishedView:
    """Read original globals exposed by500/800/A00 at attested table offsets.

    Periodic full service observations compare the entire selected row. This
    never replaces original IRQ execution or derives state from native code.
    """
    def __init__(self,d,address):
        self.driver=d;self.work=d.service(0x1000);self.resource=d.service(0x600)
        self.table=(d.load+self.work['ds'])*16+self.work['dx']
    def __getattr__(self,name):return getattr(self.driver,name)
    def service(self,code):
        if code==0x1000:return self.work
        if code==0x600:return self.resource
        return self.driver.service(code)
    def snapshot(self):
        u=self.driver.u;at=self.table
        return dict(measure=struct.unpack('<H',u.mem_read(at-57,2))[0],volume=u.mem_read(at-127,1)[0],status=(u.mem_read(at-131,1)[0]<<8)|u.mem_read(at-130,1)[0])

def original_row(d,name,address):
    m=music_row(d,name);e=effect_row(d,name,address)
    return m[:709]+e[:42]+m[709:]

def produce(args,root,out,mf,files):
    # Preserve the starting hypothesis separately from the executing Oracle.
    # Native C++ may advance while immutable Python producer tools keep running.
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as t:
        for f in files:
            assert sha(root/f['path'])==f['sha256'];t.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
    producer_tools=[f for f in files if f['path'].endswith('.py')]
    binaries=directory_files(args.hdi);assets=ending_assets(args.hdi);ops=operations();outputs={};cases=[];first={};observer_checks=0
    for p,data in [(out/'MIKO.EFC',assets['MIKO.EFC']),(out/'operations.txt',''.join(f'{o} {v}\n' for o,v in ops).encode())]:p.write_bytes(data);outputs[p.name]=sha(p)
    for load in (0x1000,0x2000):
        for name,(_,_,board,ext,_) in DRIVERS.items():
            songs={n:assets[n+'.'+ext] for n in ('LOGO','OP','ST05B','STAFF')};songs={n+'.'+ext:v for n,v in songs.items()};songs.update(challenges(ext))
            for song,data in sorted(songs.items()):
                d=install(binaries[name],name,load);address=d.write_resource(0xb00,assets['MIKO.EFC'])['offset'];d.write_resource(0x600,data);view=PublishedView(d,address)
                initial=out/(name+'-mirror.txt');raw=(' '.join(map(str,mirror(d,name)))+'\n').encode()
                if initial.exists():assert initial.read_bytes()==raw
                else:initial.write_bytes(raw)
                resource=out/song
                if resource.exists():assert resource.read_bytes()==data
                else:resource.write_bytes(data)
                path=out/f'{name}-{load:04x}-{song}.txt.gz';raw_hash=hashlib.sha256()
                with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:
                    for tick,(op,v) in enumerate(ops):
                        d.ticks=tick;d.ports=[]
                        if op=='R':d.service(0)
                        elif op=='M':d.service(0x100)
                        elif op=='P':d.service(0xc00|v)
                        elif op=='S':d.service(0xd00)
                        elif op=='F':d.service(0x200|(v&255))
                        else:d.irq(v)
                        row=original_row(view,name,address)
                        if op!='I' or tick%257==0:
                            assert row==original_row(d,name,address),(name,song,load,tick,'published observer differs');observer_checks+=1
                        raw=(' '.join(map(str,row))+'\n').encode();f.write(raw);raw_hash.update(raw)
                key=(name,song);digest=raw_hash.hexdigest()
                if key in first:assert digest==first[key],key
                first[key]=digest
                for p in (initial,resource,path):outputs[p.name]=sha(p)
                cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,raw_sha256=digest,rows=len(ops)))
                print(f'Original FM music/effects {name} {song} PSP{load:04x}: {len(ops)} rows PASS',flush=True)
    for f in producer_tools:assert sha(root/f['path'])==f['sha256'],f['path']
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),outputs=outputs,observer_service_crosschecks=observer_checks,producer_tools=producer_tools,producer_source_archive_sha256=sha(out/'producer-source.tar.gz'),hdi_sha256=HDI_SHA,drivers={n:dict(size=len(binaries[n]),sha256=hashlib.sha256(binaries[n]).hexdigest(),entry='PSP:0100',service='PSP:0103',format='flat-COM') for n in DRIVERS},unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))

def consume(args,root,out,mf,files):
    ref=args.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==42
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    outputs={};results=[]
    for binary in args.binary:
        binary=binary.resolve();(require_pe_x86_64 if binary.suffix=='.exe' else require_elf_x86_64)(binary);directory=out/binary.parent.name;directory.mkdir();done={}
        for c in r['cases']:
            key=(c['driver'],c['song'])
            if key not in done:
                target=directory/f'{c["driver"]}-{c["song"]}.txt'
                command=[str(binary),str(ref/c['song']),str(ref/'MIKO.EFC'),str(c['board']),str(ref/c['mirror']),str(ref/'operations.txt'),str(target)]
                subprocess.run(command,check=True);done[key]=target
            expect=gzip.decompress((ref/c['reference']).read_bytes());actual=done[key].read_bytes();assert hashlib.sha256(expect).hexdigest()==c['raw_sha256']
            if actual!=expect:
                for i,(x,y) in enumerate(zip(expect.splitlines(),actual.splitlines())):
                    if x!=y:
                        a=list(map(int,x.split()));b=list(map(int,y.split()));diff=[(j,u,v) for j,(u,v) in enumerate(zip(a,b)) if u!=v]
                        raise ValueError(f'FM player {binary.parent.name} {key} row{i}: fields(expected,native)={diff[:18]}, sizes={len(a)}/{len(b)}')
                raise ValueError('FM player trace length differs')
        for target in done.values():
            raw=target.read_bytes();p=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(raw)
            assert gzip.decompress(p.read_bytes())==raw;target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),rows=r['rows']))
        print(f'Native FM player {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,outputs=outputs,rows=r['rows'],reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference) or bool(a.reference)!=bool(a.binary):p.error('choose original HDI or reference plus binaries')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
