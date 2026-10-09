#!/usr/bin/env python3
"""FM3 subtracks, slot/voice ownership, detunes, two LFOs and effect release.

Original pinned flat COM executes at two PSPs. Compare every prior TimerPlayer
field and ordered write, plus nine shared FM3 globals and 72 fields per extra
track. FM26 reuses D-F; PMD86/PMDB2 append three tracks. Constructed resources
exercise CF/C6/C7/C8, zero pointers, masks, effects and restart. Explicit
IRQ/board/file adapters remain; no natural route, physical chip or exact claim.
CPU-only, muted; no audio device/backend is opened.
"""
import argparse,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets
from verify_pmd_timer_player import original_row as timer_row
from verify_pmd_fm_player import PublishedView
from verify_pmd_musical_fm import mirror
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

# PSP-relative observed work-table bases, attested against each pinned COM.
TABLES={'PMD.COM':0x3260,'PMD86.COM':0x412c,'PMDB2.COM':0x3d34}
FM_TABLES={'PMD.COM':0x0ae2,'PMD86.COM':0x1666,'PMDB2.COM':0x1268}
HANDLERS={'PMD.COM':(0x0fde,0x11d6,0x10ad,0x10dd),
          'PMD86.COM':(0x1b78,0x1d70,0x1c47,0x1c81),
          'PMDB2.COM':(0x177a,0x1972,0x1849,0x1883)}

def target_profile(binaries):
    result={}
    for name,binary in binaries.items():
        if name not in DRIVERS:continue
        size=96 if name=='PMD.COM' else 98;table=TABLES[name]
        parts=list(struct.unpack_from('<11H',binary,table-256))
        assert parts==[table+(24 if size==96 else 30)+size*n for n in range(11)]
        handlers=tuple(struct.unpack_from('<H',binary,FM_TABLES[name]-256+2*(255-op))[0] for op in (198,207,199,200))
        assert handlers==HANDLERS[name]
        result[name]=dict(size=len(binary),sha256=hashlib.sha256(binary).hexdigest(),entry='PSP:0100',service='PSP:0103',format='flat-COM',work_table=table,primary_parts=parts,fm_dispatch_table=FM_TABLES[name],handlers=handlers)
    assert len(result)==3
    return result

def resource(programs,extra=()):
 data=bytearray(27);positions={}
 for p in range(11):
  positions[p]=len(data);struct.pack_into('<H',data,1+2*p,len(data)-1);data+=programs.get(p,b'\x80')
 struct.pack_into('<H',data,23,len(data)-1);data+=b'\0\0'
 extra_positions=[]
 for program in extra:extra_positions.append(len(data));data+=program
 for p,program in programs.items():
  if b'\xc6\xfe\xff\xfd\xff\xfc\xff' in program:
   marker=b'\xc6\xfe\xff\xfd\xff\xfc\xff';search=0
   while True:
    found=program.find(marker,search)
    if found<0:break
    at=positions[p]+found+1
    for n in range(3):struct.pack_into('<H',data,at+n*2,extra_positions[n]-1 if n<len(extra_positions) and extra[n] else 0)
    search=found+len(marker)
 struct.pack_into('<H',data,25,len(data)-1)
 for id,algorithm in ((0,60),(7,60),(8,56)):
  data+=bytes([id,*([1]*4),12,20,30,0,*([31]*4),*([7]*4),*([3]*4),*([15]*4),algorithm])
 data+=b'\xff';assert struct.unpack_from('<H',data,1)[0]==26;assert len(data)<8192;return bytes(data)

def fixtures():
 result={};prefix=[255,7,253,100]
 slots=prefix[:]
 for value in range(256):slots += [207,value,182,value,184,143,value,64,1]
 result['SLOTS2']=resource({2:bytes(slots+[128])})
 det=prefix+[207,240]
 for selector in range(16):
  for value in (0,1,127,128,32767,32768,65535,618):det += [200,selector,value&255,value>>8,64,1,199,selector,255,255,65,1]
 result['DETUNE2']=resource({2:bytes(det+[200,15,0,0,64,4,128])})
 lfo=prefix+[207,240,242,0,1,2,3,191,0,2,255,4]
 for mask in range(16):lfo += [197,mask,186,15-mask,241,1,190,1,64,4,241,0,190,0,64,1]
 result['DUALLFO2']=resource({2:bytes(lfo+[128])})
 marker=[198,254,255,253,255,252,255]
 extensions=[bytes([207,slot|carrier,255,7,253,80+n*4,246,64+n,3,251,68+n,3,184,143,1,182,129,128]) for n,(slot,carrier) in enumerate(((32,2),(64,4),(128,8)))]
 result['SUB3']=resource({2:bytes(prefix+[207,17]+marker+[246,64,4,255,8,68,4,128])},extensions)
 result['SUBREMASK']=resource({2:bytes(prefix+[207,17]+marker+[64,16,192,1]+marker+[64,8,192,0,200,15,1,0,64,16,200,15,0,0,64,8,128])},extensions)
 result['ZEROPOINTER']=resource({2:bytes(prefix+[207,17]+marker+[64,4,198,0,0,0,0,0,0,64,16,128])},extensions)
 result['C6FROM0']=resource({0:bytes(prefix+marker+[64,8,128]),2:bytes(prefix+[207,17,246,64,4,128])},extensions)
 result['IGNORE5']=resource({5:bytes(prefix+[200,15,255,127,199,15,1,0,207,0,64,4,207,240,64,4,128])})
 return result

def corners():
    prefix=[255,7,253,100]
    lfo=prefix+[242,0,1,2,3,191,0,1,253,5,241,1,190,1]
    for slots in (16,32,64,96,128,160,224,240):
        lfo += [207,slots,197,3,186,12,200,15,255,127,64,4,
                197,12,186,3,199,15,1,0,70,4]
    result={'PARTLFO':resource({2:bytes(lfo+[128])})}
    marker=[198,254,255,253,255,252,255]
    extensions=[]
    for n in range(3):
        select=2<<n
        extensions.append(bytes([207,32<<n,255,7,242,0,1,2,3,197,3,
            241,1,200,select,255,127,199,select,1,0,64+n,4,
            200,select,1,0,65+n,4,128]))
    result['SUBDETUNE']=resource({2:bytes(prefix+[207,17]+marker+[64,16,128])},extensions)
    return result

def part_fields(raw,address):
 u16=lambda a:struct.unpack_from('<H',raw,a)[0];i16=lambda a:struct.unpack_from('<h',raw,a)[0];i8=lambda a:struct.unpack_from('<b',raw,a)[0]
 position,loop=u16(0),u16(2)
 row=[position-address if position else 0,loop-address if loop else 0,raw[4],raw[0x32],raw[0x5a],raw[0x12],raw[0x13],raw[0x5f],i16(8),raw[0x31],raw[0x3b]]
 row += [raw[5],u16(6),i16(12),i16(14),i16(16),raw[0x1c],raw[0x2e],raw[0x1d],raw[0x2f],raw[0x33],raw[0x38],raw[0x39],*raw[0x34:0x38],raw[0x3c],raw[0x55],raw[0x5e],raw[0x59],raw[0x3e],raw[0x3f],raw[0x5b],raw[0x60] if len(raw)>0x60 else 0,raw[0x40],raw[0x41],raw[0x56],raw[0x57],raw[0x58]]
 for l,shape,mask,depth_count in ((0x14,0x3a,0x3d,0x51),(0x44,0x4f,0x50,0x53)):
  value=10 if l==0x14 else 0x42;depth_step=0x1e if l==0x14 else 0x4c;depth_speed=0x1f if l==0x14 else 0x4d;initial_depth=0x20 if l==0x14 else 0x4e
  row += [i16(value),raw[l],raw[l+1],i8(l+2),raw[l+3],raw[l+4],raw[l+5],i8(l+6),raw[l+7],raw[shape],raw[mask],i8(depth_step),raw[depth_speed],raw[initial_depth],raw[depth_count],raw[depth_count+1]]
 assert len(row)==72;return row

def original_row(d,name,address,binary,anchors):
 r=timer_row(d,name,address,binary);at=1134 if name=='PMD.COM' else 1140;w=d.service(0x1000);segment=(d.load+w['ds'])*16;table=w['dx'];size=96 if name=='PMD.COM' else 98
 detune=struct.unpack('<4h',d.u.mem_read(segment+table-76,8));delta=1 if name=='PMD86.COM' else 0
 glob=[*detune,d.u.mem_read(segment+table-218-delta,1)[0],d.u.mem_read(segment+table-217-delta,1)[0],d.u.mem_read(segment+table-205-delta,1)[0],d.u.mem_read(segment+table-14,1)[0],d.u.mem_read(segment+table-13,1)[0]]
 extra=anchors[name]['primary_parts'][3:6] if name=='PMD.COM' else [anchors[name]['primary_parts'][10]+size*(n+1) for n in range(3)]
 music_address=d.service(0x600)['dx']
 for p in extra:glob += part_fields(bytes(d.u.mem_read(segment+p,size)),music_address)
 assert len(glob)==225;return r[:at]+glob+r[at:]
def operations():
    return [('R',0)]+[('I',3)]*320+[('P',4)]+[('I',3)]*96+[('S',0)]+[('I',1)]*32+[('F',4)]+[('I',3)]*64+[('M',0)]+[('I',3)]*8+[('R',0)]+[('I',3)]*320

def produce(args,root,out,mf,files):
    binaries=directory_files(args.hdi);assets=ending_assets(args.hdi);anchors=target_profile(binaries);ops=operations()
    outputs={};cases=[];first={};checks=0
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as archive:
        for f in files:
            assert sha(root/f['path'])==f['sha256'];archive.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
    for p,data in ((out/'operations.txt',''.join(f'{op} {v}\n' for op,v in ops).encode()),(out/'MIKO.EFC',assets['MIKO.EFC'])):
        p.write_bytes(data);outputs[p.name]=sha(p)
    for load in (0x1000,0x2000):
        for name,(_,_,board,ext,_) in DRIVERS.items():
            for label,data in (corners() if args.corners else fixtures()).items():
                song=label+'.'+ext;resource_file=out/song
                if resource_file.exists():assert resource_file.read_bytes()==data
                else:resource_file.write_bytes(data)
                d=install(binaries[name],name,load);address=d.write_resource(0xb00,assets['MIKO.EFC'])['offset'];d.write_resource(0x600,data);view=PublishedView(d,address)
                initial=out/(name+'-mirror.txt');raw=(' '.join(map(str,mirror(d,name)))+'\n').encode()
                if initial.exists():assert initial.read_bytes()==raw
                else:initial.write_bytes(raw)
                path=out/f'{name}-{load:04x}-{song}.txt.gz';digest=hashlib.sha256()
                with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as stream:
                    for tick,(op,v) in enumerate(ops):
                        d.ticks=tick;d.ports=[]
                        if op=='I':d.irq(v)
                        else:d.service({'R':0,'M':0x100,'P':0xc00|v,'S':0xd00,'F':0x200|(v&255)}[op])
                        r=original_row(view,name,address,binaries[name],anchors)
                        if op!='I' or tick%257==0:assert r==original_row(d,name,address,binaries[name],anchors);checks+=1
                        raw=(' '.join(map(str,r))+'\n').encode();stream.write(raw);digest.update(raw)
                key=name,song;h=digest.hexdigest()
                if key in first:assert first[key]==h,key
                first[key]=h
                for p in (resource_file,initial,path):outputs[p.name]=sha(p)
                cases.append(dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,raw_sha256=h,rows=len(ops)))
                print(f'Original FM3 {name} {song} PSP{load:04x}: {len(ops)} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),outputs=outputs,observer_service_crosschecks=checks,producer_source_archive_sha256=sha(out/'producer-source.tar.gz'),hdi_sha256=HDI_SHA,drivers=anchors,unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)))

def consume(args,root,out,mf,files):
    ref=args.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases']) in (48,12)
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
                        a=list(map(int,x.split()));b=list(map(int,y.split()));diff=[(j,u,v) for j,(u,v) in enumerate(zip(a,b)) if u!=v];raise ValueError(f'PMD FM3 {binary.parent.name} {key} row{row}: {diff[:16]}, lengths{len(a)}/{len(b)}')
                raise ValueError('PMD FM3 length differs')
        for target in done.values():
            raw=target.read_bytes();p=target.with_suffix('.txt.gz')
            with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(raw)
            assert gzip.decompress(p.read_bytes())==raw;target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),rows=r['rows']));print(f'Native PMD FM3 {binary.parent.name}: {r["rows"]} rows PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,rows=r['rows'],outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--corners',action='store_true');p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference) or bool(a.reference)!=bool(a.binary):p.error('choose original HDI or reference with binaries')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
