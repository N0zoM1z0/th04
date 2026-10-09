#!/usr/bin/env python3
"""Original hardware rhythm joins FM/SSG music and both effect owners.

All supplied songs and six authored fixtures per format retain complete
prior configured FM/SSG state, five fade globals, rhythm track/global state,
primary16..31 mirrors and every chronological write in the owned union.
Only work/resource pointers become relative. FM3/PPS/ADPCM, waveform synthesis,
physical clocks/frontend/fullroutes and DOS exact remain separate.
No audio device/backend opens. Original producer tools freeze while running.
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
from verify_pmd_commands import original_row as command_row
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def operations():
    result=[('R',0)]+[('I',3)]*32+[('P',4),('G',24)]+[('I',1)]*8+[('I',0)]*4+[('I',2)]*8+[('I',3)]*256
    result += [('H',0),('S',0)]+[('I',3)]*32+[('F',127)]+[('I',1)]*24+[('I',0),('I',1),('I',2)]
    result += [('M',0),('R',0)]+[('I',3)]*256+[('G',11),('P',7),('M',0)]+[('I',1)]*32+[('R',0)]+[('I',3)]*256
    result += [('H',0),('S',0),('F',-7)]+[('I',1)]*64+[('M',0)]
    return result

def resource(extension,parts,patterns):
    seed=mixed_challenges(extension)['MIX0.'+extension];voice=struct.unpack_from('<H',seed,25)[0]+1;data=bytearray(27)
    for p in range(11):
        struct.pack_into('<H',data,1+2*p,len(data)-1)
        if p in parts:data+=parts[p]
        elif p<3 or (extension=='M86' and p<6):data+=bytes([255,7,253,80,64+p,64,15,8,128])
        elif 6<=p<=8:data+=bytes([253,8,240,0,254,1,1,64,64,15,8,128])
        else:data+=b'\x80'
    table=len(data);struct.pack_into('<H',data,23,table-1);data+=bytes(2*len(patterns))
    for n,pattern in enumerate(patterns):struct.pack_into('<H',data,table+2*n,len(data)-1);data+=pattern
    struct.pack_into('<H',data,25,len(data)-1);data+=seed[voice:];return bytes(data)

def challenges(extension):
    patterns=[bytes([128|((1<<i)>>8),(1<<i)&255,2,0,1,255]) for i in range(14)];result={}
    result['RHYMACRO.'+extension]=resource(extension,{10:bytes([246,*range(14),128])},patterns)
    result['RHYMASK.'+extension]=resource(extension,{10:bytes([192,1,*range(14),192,0,*range(14),128])},patterns)
    result['RHYFADE.'+extension]=resource(extension,{0:bytes([255,7,64,2,210,127,65,64,128]),10:bytes([246,*range(14),128])},patterns)
    for part,label in ((0,'FM'),(6,'SSG'),(10,'TRACK')):
        program=([255,7] if part==0 else [240,0,254,1,1] if part==6 else [])
        separator=[0] if part==10 else [64,1]
        def add(values):program.extend(values);program.extend(separator)
        for value in range(256):add([235,value])
        for index in range(8):
            add([234,(index<<5)|27])
            for pan in range(4):add([233,(index<<5)|pan])
            for delta in (0,1,127,128,255):add([229,index,delta])
        for gain in (0,127,255):
            add([192,249,gain])
            for value in (0,1,48,63,128,255):add([232,value])
            for delta in (0,1,63,127,128,255):add([230,delta])
        for delta in (1,127,128,255,0):add([192,248,delta])
        add([239,24,90]);program += [128]
        result['RHY'+label+'.'+extension]=resource(extension,{part:bytes(program)},[bytes([0,1,255])])
    assert len(result)==6;return result

def original_row(d,name,address,binary):
    row=command_row(d,name,address,binary);at=1078 if name=='PMD.COM' else 1084;work=d.service(0x1000);segment=(d.load+work['ds'])*16;table=segment+work['dx'];pointer=struct.unpack('<11H',d.u.mem_read(table,22))[10];raw=bytes(d.u.mem_read(segment+pointer,96));u16=lambda p:struct.unpack_from('<H',raw,p)[0]
    music_address=d.service(0x600)['dx']
    extra=[u16(0)-music_address if u16(0) else 0,u16(2)-music_address if u16(2) else 0,raw[4],raw[50],raw[90],raw[18],raw[19],raw[95],struct.unpack_from('<h',raw,8)[0],raw[49],raw[59]]
    byte=lambda offset:d.u.mem_read(table+offset,1)[0]
    extra += [byte(-134),byte(-45),byte(-140),byte(-85),byte(-102),byte(-95),struct.unpack('<H',d.u.mem_read(table-94,2))[0]]
    extra += list(d.u.mem_read(table-101,6))+list(d.u.mem_read(table-26,12))
    extra += mirror(d,name)[16:32]
    ports={PORTS[name]:0,PORTS[name]+4:1};selected={};writes=[]
    for _,port,size,value in d.ports:
        if port in ports:selected[ports[port]]=value
        elif port-2 in ports:
            bank=ports[port-2];register=selected.get(bank)
            if register is not None and (48<=register<=182 or (bank==0 and (register in (34,40) or register<14 or 16<=register<32))):writes += [bank,register,value]
    assert len(extra)==52
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
                cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,raw_sha256=raw_digest,rows=len(ops)));print(f'Original PMD rhythm {name} {song} PSP{load:04x}: {len(ops)} rows PASS',flush=True)
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
                        a=list(map(int,x.split()));b=list(map(int,y.split()));diff=[(j,u,v) for j,(u,v) in enumerate(zip(a,b)) if u!=v];raise ValueError(f'PMD rhythm {binary.parent.name} {key} row{row}: {diff[:16]}, lengths{len(a)}/{len(b)}')
                raise ValueError('PMD rhythm length differs')
        for target in done.values():
            raw=target.read_bytes();p=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(raw)
            assert gzip.decompress(p.read_bytes())==raw;target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),rows=r['rows']));print(f'Native PMD rhythm {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,rows=r['rows'],outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference) or bool(a.reference)!=bool(a.binary):p.error('choose original HDI or reference with binaries')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
