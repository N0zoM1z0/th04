#!/usr/bin/env python3
"""Original musical FM state and ordered register requests versus native owner.

All supplied M26/M86 songs execute in their unchanged HDI resident drivers.
DOS, installation/readback and explicit Timer A/B injection retain the guarded
original adapter. Compares selected six-part musical/FM state, both FM register
blocks30..B6 and primary22/28, and all ordered writes in that ownership surface.
SSG/ADPCM/hardware rhythm, FM3 extra subtracks, effects/musical handover, global
timer ACK events, synthesis, physical clocks and frontend capability are not
accepted by this profile. No audio device/backend, no DOS exact promotion.
"""
import argparse,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets
from verify_pmd_sequence import operations

PORTS={'PMD.COM':0x88,'PMD86.COM':0x188,'PMDB2.COM':0x88}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def owned(bank,address):return 48<=address<=182 or bank==0 and address in (34,40)
def mirror(d,name):return [d.registers.get((PORTS[name]+b*4,a),0) for b in range(2) for a in range(256)]

def challenges(extension):
    result={}
    for shape in range(7):
        # Constructed legal music data, never patched original executable code.
        phrase=[255,7,253,100,242,0,2,3,4,241,3,203,shape,
                191,1,1,254,3,190,3,188,4,214,2,1,189,3,255,
                254,2,196,64,179,1,181,3,3,228,2,225,3,224,8]
        if shape&1:phrase += [202,1,187,1]
        if extension=='M86':phrase += [177,131 if shape&1 else 3]
        phrase += [64,12,251,68,8,193,15,6,76,5,218,64,80,16,80,10,128]
        empty=27+len(phrase);voice=empty+1
        data=bytearray(27);data[0]=0
        for p in range(12):struct.pack_into('<H',data,1+p*2,empty-1)
        struct.pack_into('<H',data,1,26);struct.pack_into('<H',data,25,voice-1)
        data += bytes(phrase)+b'\x80'
        # ID, DT/ML, TL, AR, DR, SR, SL/RR, algorithm; a typed resource voice.
        data += bytes([7,*([1]*4),12,20,30,0,*([31]*4),*([7]*4),*([3]*4),*([15]*4),60,255])
        result[f'LFO{shape}.{extension}']=bytes(data)
    return result

def original_row(d,name):
    work=d.service(0x1000);segment=d.load+work['ds'];table=segment*16+work['dx'];address=d.service(0x600)['dx'];state=d.snapshot();memory=bytes(d.u.mem_read(table-129,144))
    row=[state['measure'],state['volume']&255,state['status'],memory[0],memory[6]]
    for pointer in struct.unpack('<11H',d.u.mem_read(table,22))[:6]:
        raw=bytes(d.u.mem_read(segment*16+pointer,0x62 if name!='PMD.COM' else 0x60))
        u16=lambda at:struct.unpack_from('<H',raw,at)[0];i16=lambda at:struct.unpack_from('<h',raw,at)[0];i8=lambda at:struct.unpack_from('<b',raw,at)[0]
        position,loop=u16(0),u16(2)
        row += [position-address if position else 0,loop-address if loop else 0,raw[4],raw[0x32],raw[0x5a],raw[0x12],raw[0x13],raw[0x5f],i16(8),raw[0x31],raw[0x3b]]
        row += [raw[5],u16(6),i16(12),i16(14),i16(16),raw[0x1c],raw[0x2e],raw[0x1d],raw[0x2f],raw[0x33],raw[0x38],raw[0x39],*raw[0x34:0x38],raw[0x3c],raw[0x55],raw[0x5e],raw[0x59],raw[0x3e],raw[0x3f],raw[0x5b],raw[0x60] if len(raw)>0x60 else 0,raw[0x40],raw[0x41],raw[0x56],raw[0x57],raw[0x58]]
        for l,shape,mask,depth_count in ((0x14,0x3a,0x3d,0x51),(0x44,0x4f,0x50,0x53)):
            value=10 if l==0x14 else 0x42;depth_step=0x1e if l==0x14 else 0x4c;depth_speed=0x1f if l==0x14 else 0x4d;initial_depth=0x20 if l==0x14 else 0x4e
            row += [i16(value),raw[l],raw[l+1],i8(l+2),raw[l+3],raw[l+4],raw[l+5],i8(l+6),raw[l+7],raw[shape],raw[mask],i8(depth_step),raw[depth_speed],raw[initial_depth],raw[depth_count],raw[depth_count+1]]
    row += [d.registers.get((PORTS[name]+bank*4,a),0) for bank in range(2) for a in range(256) if owned(bank,a)]
    selected={};writes=[];port=PORTS[name]
    for _,p,size,v in d.ports:
        if p in (port,port+4):selected[p]=v
        elif p in (port+2,port+6):
            if size!=1 or p-2 not in selected:raise ValueError('musical FM port stream lacks address')
            bank=(p-port-2)//4;a=selected[p-2]
            if owned(bank,a):writes += [bank,a,v]
    row += [len(writes)//3]+writes
    return row

def produce(args,root,out,mf,files):
    binaries=directory_files(args.hdi);assets=ending_assets(args.hdi);ops=operations(args.ticks);outputs={};cases=[];first={}
    operation=out/'operations.txt';operation.write_text(''.join(f'{op} {v}\n' for op,v in ops));outputs[operation.name]=sha(operation)
    for load in (0x1000,0x2000):
        for name,(_,_,board,extension,_) in DRIVERS.items():
            songs=challenges(extension) if args.challenge else assets
            for song,data in sorted(songs.items()):
                if not song.endswith('.'+extension):continue
                d=install(binaries[name],name,load);d.write_resource(0xb00,assets['MIKO.EFC']);d.write_resource(0x600,data)
                initial=out/(name+'-mirror.txt');initial_bytes=(' '.join(map(str,mirror(d,name)))+'\n').encode()
                if initial.exists():assert initial.read_bytes()==initial_bytes
                else:initial.write_bytes(initial_bytes)
                resource=out/song
                if resource.exists():assert resource.read_bytes()==data
                else:resource.write_bytes(data)
                d.ports=[];d.service(0);path=out/f'{name}-{load:04x}-{song}.txt.gz';raw_hash=hashlib.sha256()
                with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:
                    row=(' '.join(map(str,original_row(d,name)))+'\n').encode();f.write(row);raw_hash.update(row)
                    for tick,(op,v) in enumerate(ops):
                        d.ticks=tick;d.ports=[]
                        if op=='I':d.irq(v)
                        elif op=='F':d.service(0x200|(v&255))
                        elif op=='S':d.service(0x100)
                        else:d.service(0)
                        row=(' '.join(map(str,original_row(d,name)))+'\n').encode();f.write(row);raw_hash.update(row)
                key=(name,song);digest=raw_hash.hexdigest()
                if key in first:assert digest==first[key],key
                first[key]=digest
                for p in (initial,resource,path):outputs[p.name]=sha(p)
                cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,raw_sha256=digest,rows=len(ops)+1))
                print(f'Original musical FM {name} {song} load{load:04x}: {len(ops)+1} rows PASS',flush=True)
    if source_manifest(root)[0]!=mf:raise ValueError('source changed during original musical FM producer')
    assert len(cases)==(42 if args.challenge else 138)
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as t:
        for entry in files:t.add(root/entry['path'],arcname=entry['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
    return dict(profile='constructed-dual-lfo-gate' if args.challenge else 'all-supplied-songs',cases=cases,rows=sum(c['rows'] for c in cases),outputs=outputs,hdi_sha256=HDI_SHA,drivers={n:dict(size=len(data),sha256=hashlib.sha256(data).hexdigest(),entry='PSP:0100',service='PSP:0103',format='flat-COM') for n,data in binaries.items() if n in DRIVERS},unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))

def consume(args,root,out,mf,files):
    ref=args.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==(42 if r.get('profile')=='constructed-dual-lfo-gate' else 138)
    for n,h in r['outputs'].items():assert sha(ref/n)==h,n
    results=[];outputs={}
    for binary in args.binary:
        binary=binary.resolve();(require_pe_x86_64 if binary.suffix=='.exe' else require_elf_x86_64)(binary);directory=out/binary.parent.name;directory.mkdir();done={}
        for c in r['cases']:
            key=(c['driver'],c['song'])
            if key not in done:
                target=directory/f'{c["driver"]}-{c["song"]}.txt'
                command=[str(binary),str(ref/c['song']),str(c['board']),str(ref/c['mirror']),str(ref/'operations.txt'),str(target)]
                subprocess.run(command,check=True);done[key]=target
            target=done[key];expected=gzip.decompress((ref/c['reference']).read_bytes());actual=target.read_bytes()
            assert hashlib.sha256(expected).hexdigest()==c['raw_sha256']
            if actual!=expected:
                for i,(x,y) in enumerate(zip(expected.splitlines(),actual.splitlines())):
                    if x!=y:
                        a=list(map(int,x.split()));b=list(map(int,y.split()));diff=[(j,u,v) for j,(u,v) in enumerate(zip(a,b)) if u!=v]
                        raise ValueError(f'Musical FM {binary.parent.name} {key} row{i}: fields(expected,native)={diff[:16]}, sizes={len(a)}/{len(b)}')
                raise ValueError('musical FM row count differs')
        for key,target in done.items():
            data=target.read_bytes();path=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:f.write(data)
            assert gzip.decompress(path.read_bytes())==data;target.unlink();outputs[path.relative_to(out).as_posix()]=sha(path)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),rows=r['rows'],runs=len(done)))
        print(f'Native musical FM {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    if source_manifest(root)[0]!=mf:raise ValueError('source changed during musical FM consumer')
    return dict(runs=results,outputs=outputs,rows=r['rows'],reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--ticks',type=int,default=384);p.add_argument('--challenge',action='store_true',help='Construct legal dual-LFO/gate/slide/key-delay music for unchanged original drivers');p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if bool(args.hdi)==bool(args.reference) or bool(args.reference)!=bool(args.binary):p.error('choose original HDI or reference with binaries')
    if not 384<=args.ticks<=4096:p.error('bounded musical profile384..4096 ticks')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    r=produce(args,root,out,mf,files) if args.hdi else consume(args,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
