#!/usr/bin/env python3
"""Original musical SSG state/envelopes/effect sharing and ordered requests.

Unchanged original COM drivers execute supplied and constructed resources.
Compares globals, all96/98 musical work bytes with two resource pointers made
relative, built-in effect state, all14SSGmirrors and every owned ordered write.
Native FM/SSG share one sequence, random stream and Timer A baseline. Synthesis,
physical clocks, ADPCM/rhythm/FM3extras/frontend capability/fullroutes remain
outside this owner. No audio device/backend or DOS exact promotion.
"""
import argparse,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets
from verify_pmd_musical_fm import mirror,PORTS
from verify_pmd_fm_player import PublishedView
from verify_pmd_sequence import operations
from verify_pmd_ssg import original_state,sharing_song
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def challenges(extension):
    result={}
    for variant in range(7):
        programs=[]
        for p in range(3):
            phrase=[253,10,254,2,242,0,2,3,4,241,3,203,variant,191,1,1,254,3,190,3,188,(variant+3)%7,214,2,1,189,3,255,196,64,179,1]
            phrase += [240,3,254,2,1] if variant<3 else [205,24,20,17,67,2]
            if variant&1:phrase += [202,1,187,1,201,1]
            if variant&2:phrase += [204,1]
            if extension=='M86':phrase += [177,3]
            phrase += [238,5+p,237,63,183,3,183,130,64+p,12,251,68+p,8,193,15,6,76,5,208,255,218,64,80,16,80,10,128]
            programs.append(bytes(phrase))
        data=bytearray(27);data+=b'\x80';offset=len(data)
        for p in range(12):struct.pack_into('<H',data,1+2*p,26)
        for p,program in enumerate(programs):struct.pack_into('<H',data,13+2*p,offset-1);data+=program;offset+=len(program)
        struct.pack_into('<H',data,25,len(data)-1);data+=b'\xff';result[f'SSG{variant}.{extension}']=bytes(data)
    for label,effect,rest in [('drum-note',0,False),('effect-note',11,False),('drum-rest',1,True)]:
        data=bytearray(sharing_song(effect,rest))
        # Append a channel-C phrase; all offsets are resource-owned. The old
        # bounded rhythm/table data stays at its original directory positions.
        stream=[240,0,254,2,1,180]+[0]*16
        stream += [239,6,17,238,5,237,63]
        stream += [79 if rest else 64,2,79 if rest else 65,2,218,66,70,4,67,2,128]
        struct.pack_into('<H',data,17,len(data)-1);data+=bytes(stream)
        result[f'{label}.{extension}']=bytes(data)
    return result

def original_row(d,name,binary):
    work=d.service(0x1000);segment=d.load+work['ds'];table=segment*16+work['dx'];address=d.service(0x600)['dx'];state=d.snapshot();u=d.u
    get=lambda offset:u.mem_read(table+offset,1)[0]
    row=[state['measure'],state['volume']&255,state['status'],get(-129),get(-123),get(-136),get(-47),get(-121),get(-120)]
    for pointer in struct.unpack('<11H',u.mem_read(table,22))[6:9]:
        raw=bytearray(u.mem_read(segment*16+pointer,96 if name=='PMD.COM' else 98))
        for at in (0,2):
            ptr=struct.unpack_from('<H',raw,at)[0];struct.pack_into('<H',raw,at,ptr-address if ptr else 0)
        row+=raw
    row+=original_state(d,name,binary)[:11];row += [d.registers.get((PORTS[name],a),0) for a in range(14)]
    writes=[];selected=None
    for _,port,size,value in d.ports:
        if port==PORTS[name]:selected=value
        elif port==PORTS[name]+2 and selected is not None and selected<14:
            if size!=1:raise ValueError('SSG musical non-byte I/O')
            writes += [selected,value]
    row += [len(writes)//2]+writes;return row

def produce(a,root,out,mf,files):
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as t:
        for f in files:assert sha(root/f['path'])==f['sha256'];t.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n');frozen=[f for f in files if f['path'].endswith('.py')]
    binaries=directory_files(a.hdi);assets=ending_assets(a.hdi);ops=operations(a.ticks);operation=out/'operations.txt';operation.write_text(''.join(f'{op} {v}\n' for op,v in ops));outputs={operation.name:sha(operation)};cases=[];first={};checks=0
    for load in (0x1000,0x2000):
        for name,(_,_,board,extension,_) in DRIVERS.items():
            songs=challenges(extension) if a.challenge else assets
            for song,data in sorted(songs.items()):
                if not song.endswith('.'+extension):continue
                d=install(binaries[name],name,load);d.write_resource(0xb00,assets['MIKO.EFC']);d.write_resource(0x600,data);view=PublishedView(d,0)
                initial=out/(name+'-mirror.txt');raw=(' '.join(map(str,mirror(d,name)))+'\n').encode()
                if initial.exists():assert initial.read_bytes()==raw
                else:initial.write_bytes(raw)
                resource=out/song
                if resource.exists():assert resource.read_bytes()==data
                else:resource.write_bytes(data)
                d.ports=[];d.service(0);path=out/f'{name}-{load:04x}-{song}.txt.gz';digest=hashlib.sha256()
                with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:
                    row=original_row(view,name,binaries[name]);assert row==original_row(d,name,binaries[name]);checks+=1;raw=(' '.join(map(str,row))+'\n').encode();f.write(raw);digest.update(raw)
                    for tick,(op,v) in enumerate(ops):
                        d.ticks=tick;d.ports=[]
                        if op=='I':d.irq(v)
                        elif op=='F':d.service(0x200|(v&255))
                        elif op=='S':d.service(0x100)
                        else:d.service(0)
                        row=original_row(view,name,binaries[name])
                        if op!='I' or tick%257==0:assert row==original_row(d,name,binaries[name]);checks+=1
                        raw=(' '.join(map(str,row))+'\n').encode();f.write(raw);digest.update(raw)
                key=(name,song);raw_digest=digest.hexdigest()
                if key in first:assert first[key]==raw_digest,key
                first[key]=raw_digest
                for p in (initial,resource,path):outputs[p.name]=sha(p)
                cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,raw_sha256=raw_digest,rows=len(ops)+1))
                print(f'Original musical SSG {name} {song} PSP{load:04x}: {len(ops)+1} rows PASS',flush=True)
    for f in frozen:assert sha(root/f['path'])==f['sha256']
    assert len(cases)==(60 if a.challenge else 138)
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),outputs=outputs,observer_service_crosschecks=checks,producer_tools=frozen,producer_source_archive_sha256=sha(out/'producer-source.tar.gz'),hdi_sha256=HDI_SHA,drivers={n:dict(size=len(binaries[n]),sha256=hashlib.sha256(binaries[n]).hexdigest(),format='flat-COM',entry='PSP:0100',service='PSP:0103') for n in DRIVERS},unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))

def consume(a,root,out,mf,files):
    ref=a.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases']) in (42,60,138)
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    results=[];outputs={}
    for binary in a.binary:
        binary=binary.resolve();(require_pe_x86_64 if binary.suffix=='.exe' else require_elf_x86_64)(binary);folder=out/binary.parent.name;folder.mkdir();done={}
        for c in r['cases']:
            key=c['driver'],c['song']
            if key not in done:
                target=folder/f'{c["driver"]}-{c["song"]}.txt';subprocess.run([str(binary),str(ref/c['song']),str(c['board']),str(ref/c['mirror']),str(ref/'operations.txt'),str(target)],check=True);done[key]=target
            expected=gzip.decompress((ref/c['reference']).read_bytes());actual=done[key].read_bytes();assert hashlib.sha256(expected).hexdigest()==c['raw_sha256']
            if actual!=expected:
                for i,(x,y) in enumerate(zip(expected.splitlines(),actual.splitlines())):
                    if x!=y:
                        v=list(map(int,x.split()));w=list(map(int,y.split()));diff=[(j,p,q) for j,(p,q) in enumerate(zip(v,w)) if p!=q];raise ValueError(f'Musical SSG {binary.parent.name} {key} row{i}: fields(expected,native)={diff[:16]}, sizes={len(v)}/{len(w)}')
                raise ValueError('SSG musical trace length differs')
        for target in done.values():
            raw=target.read_bytes();p=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(raw)
            assert gzip.decompress(p.read_bytes())==raw;target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),rows=r['rows']));print(f'Native musical SSG {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,rows=r['rows'],outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--challenge',action='store_true');p.add_argument('--ticks',type=int,default=384);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference) or bool(a.reference)!=bool(a.binary):p.error('choose original HDI or reference with binaries')
    if not 384<=a.ticks<=4096:p.error('bounded SSG musical384..4096ticks')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
