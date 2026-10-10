#!/usr/bin/env python3
"""All supplied TH04 music reaches two global loops or natural score end.

Original stock COM/boot options execute at PSP1000/2000. Full configured
FM/SSG/rhythm/FM3 state and ordered requests compare, while every raw port and
ADPCM-track note count is independently inventoried. IRQ3, DOS/board and absent
third-party residents remain declared adapters. No physical chip/video, audible
device, whole natural game route or historical exactness claim follows.
"""
import argparse,csv,gzip,hashlib,json,struct,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
import unicorn
from verify import source_manifest,require_elf_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_cutscene import ending_assets,Fat12
from verify_pmd_fm3 import target_profile,original_row
from verify_pmd_fm_player import PublishedView
from verify_pmd_musical_fm import PORTS,mirror
from scripts.probes.probe_th04_pf_archive import ARCHIVES,parse_archive
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def archive(root,out,mf,files):
    with tarfile.open(out/'source.tar.gz','w:gz') as t:
        for f in files:
            p=root/f['path'];assert sha(p)==f['sha256'];t.add(p,arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
def inventory(hdi,binaries,assets):
    image=hdi.read_bytes();assert hashlib.sha256(image).hexdigest()==HDI_SHA
    fat=Fat12(bytearray(image));entry=fat.find_entry([fat.root],b'GENSO      ')
    folders=[fat.cluster_offset(c) for c in fat.chain(struct.unpack_from('<H',image,entry+26)[0])];loose={};archives={}
    for start in folders:
        for at in range(start,start+fat.cluster_bytes,32):
            if image[at]==0:break
            if image[at] in (0xe5,0x2e) or image[at+11]&0x18:continue
            name=image[at:at+8].decode('cp932').strip()+'.'+image[at+8:at+11].decode('cp932').strip()
            body=fat.file_bytes(struct.unpack_from('<H',image,at+26)[0],struct.unpack_from('<I',image,at+28)[0])
            loose[name]=dict(size=len(body),sha256=hashlib.sha256(body).hexdigest())
    for name,spec in ARCHIVES.items():
        at=fat.find_entry(folders,spec['fat_name']);body=fat.file_bytes(struct.unpack_from('<H',image,at+26)[0],struct.unpack_from('<I',image,at+28)[0])
        assert hashlib.sha256(body).hexdigest()==spec['sha256'];entries=parse_archive(body,name,spec)[1]
        archives[name]={n:dict(size=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in entries.items()}
    return dict(hdi_sha256=HDI_SHA,loose=loose,archives=archives,game_bat_sha256=hashlib.sha256(binaries['GAME.BAT']).hexdigest(),driver_profiles={n:dict(size=len(binaries[n]),sha256=hashlib.sha256(binaries[n]).hexdigest(),format='flat-COM',entry='PSP:0100',tail=DRIVERS[n][4]) for n in DRIVERS},music={n:dict(size=len(b),sha256=hashlib.sha256(b).hexdigest(),part9=struct.unpack_from('<H',b,19)[0]+1) for n,b in assets.items() if n.endswith(('.M26','.M86'))})
def produce(a,root,out,mf,files):
    before=sha(a.hdi);assert before==HDI_SHA;binaries=directory_files(a.hdi);assets=ending_assets(a.hdi);anchors=target_profile(binaries)
    inv=inventory(a.hdi,binaries,assets);assert len(inv['music'])==46
    (out/'inventory.json').write_text(json.dumps(inv,indent=2,ensure_ascii=False)+'\n');(out/'GAME.BAT').write_bytes(binaries['GAME.BAT'])
    for n,b in assets.items():
        if n.endswith(('.M26','.M86')) or n=='MIKO.EFC':(out/n).write_bytes(b)
    cases=[];first={};observer_checks=0
    for load in ((0x1000,) if a.first_load_only else (0x1000,0x2000)):
        for name,(_,_,board,ext,_) in DRIVERS.items():
            for song in sorted(n for n in assets if n.endswith('.'+ext)):
                d=install(binaries[name],name,load);address=d.write_resource(0xb00,assets['MIKO.EFC'])['offset'];d.write_resource(0x600,assets[song]);view=PublishedView(d,address)
                initial=out/(name+'-mirror.txt');raw=(' '.join(map(str,mirror(d,name)))+'\n').encode()
                if initial.exists():assert initial.read_bytes()==raw
                else:initial.write_bytes(raw)
                label=name+'-'+f'{load:04x}'+'-'+song;path=out/(label+'.txt.gz');operations=[];digest=hashlib.sha256();count=0;port_counts={};other_writes={};adpcm_max=0;pps_requests=0;position=None
                table=view.table;segment=(d.load+view.work['ds'])*16;part9=anchors[name]['primary_parts'][9];base=PORTS[name]
                with gzip.open(path,'wb',compresslevel=1) as trace,gzip.open(out/(label+'-ports.jsonl.gz'),'wb',compresslevel=1) as ports:
                    def emit(op,value):
                        nonlocal count,observer_checks,adpcm_max,pps_requests,position
                        operations.append((op,value));row=original_row(view,name,address,binaries[name],anchors)
                        if op!='I' or count%257==0:
                            assert row==original_row(d,name,address,binaries[name],anchors);observer_checks+=1
                        raw=(' '.join(map(str,row))+'\n').encode();trace.write(raw);digest.update(raw)
                        memory=bytes(d.u.mem_read(segment+part9,96 if not board else 98));adpcm_max=max(adpcm_max,memory[90]);position=struct.unpack_from('<H',memory)[0]
                        selected={};unknown=[]
                        for t,p,size,v in d.ports:
                            assert size==1;port_counts[str(p)]=port_counts.get(str(p),0)+1
                            if p in (base,base+4):selected[p]=v
                            elif p in (base+2,base+6):
                                assert p-2 in selected;bank=(p-base-2)//4;reg=selected[p-2]
                                if bank==1 and reg<=16:unknown.append([bank,reg,v]);key=f'{bank}:{reg}';other_writes[key]=other_writes.get(key,0)+1
                        pps_requests+=sum(n==0x64 for n,*_ in d.ints);d.ints=[]
                        ports.write((json.dumps(dict(row=count,ports=d.ports,part9_note_counter=memory[90],part9_position=position-address if position else 0,unowned_sample_writes=unknown),separators=(',',':'))+'\n').encode());count+=1
                    d.ports=[];d.ints=[];d.service(0);emit('R',0)
                    for tick in range(1,65537):
                        d.ticks=tick;d.ports=[];d.irq(3);emit('I',3);loop=view.snapshot()['status']&255
                        if loop==255 or loop>=2:break
                    else:raise ValueError(f'{name}/{song}: no score end/two loops in65536IRQs')
                    terminal=dict(ticks=tick,loop=loop,measure=view.snapshot()['measure'])
                    for _ in range(64):d.ports=[];d.irq(3);emit('I',3)
                    d.ports=[];d.service(0x100);emit('M',0)
                    for _ in range(8):d.ports=[];d.irq(3);emit('I',3)
                ops=out/(label+'-operations.txt');ops.write_text(''.join(f'{o} {v}\n' for o,v in operations))
                record=dict(driver=name,board=board,song=song,load=load,mirror=initial.name,reference=path.name,ports=label+'-ports.jsonl.gz',operations=ops.name,rows=count,raw_sha256=digest.hexdigest(),terminal=terminal,part9_max_note_counter=adpcm_max,pps_requests=pps_requests,raw_port_counts=port_counts,secondary_sample_writes=other_writes)
                key=name,song
                if key in first:assert first[key]==(record['raw_sha256'],record['terminal'],record['part9_max_note_counter'],record['pps_requests'],record['secondary_sample_writes'])
                first[key]=(record['raw_sha256'],record['terminal'],record['part9_max_note_counter'],record['pps_requests'],record['secondary_sample_writes']);cases.append(record)
                (out/'progress.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n');print(name,song,f'PSP{load:04x}',terminal,'rows',count,'sample-notes',adpcm_max,'PPS',pps_requests,flush=True)
    assert sha(a.hdi)==before
    # Keep the starting hypothesis archive; candidate C++ may advance while
    # independent producer tools remain frozen.
    for f in files:
        if f['path'].endswith(('.py','.ps1')):assert sha(root/f['path'])==f['sha256']
    return dict(cases=cases,rows=sum(c['rows'] for c in cases),observer_service_crosschecks=observer_checks,outputs={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name not in ('progress.json','source.tar.gz','source-profile.json')},hdi_sha256=HDI_SHA,loads=['1000'] if a.first_load_only else ['1000','2000'])
def consume(a,root,out,mf,files):
    ref=a.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==138 and r['loads']==['1000','2000']
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    product=json.loads(a.product_profile.read_text());binary=a.binary.resolve();require_elf_x86_64(binary);assert any(x.get(binary.name)==sha(binary) for x in product['products'].values())
    frozen={binary:sha(binary),a.product_profile.resolve():sha(a.product_profile),ref/'receipt.json':sha(ref/'receipt.json')};done={};records=[]
    for c in r['cases']:
        key=c['driver'],c['song']
        if key not in done:
            output=out/(c['driver']+'-'+c['song']+'.txt.gz');command=[str(binary),str(ref/c['song']),str(ref/'MIKO.EFC'),str(c['board']),str(ref/c['mirror']),str(ref/c['operations']),'/dev/stdout'];digest=hashlib.sha256();rows=0
            with (out/(c['driver']+'-'+c['song']+'-stderr.txt')).open('wb') as error:
                child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=error)
                try:
                    with gzip.open(ref/c['reference'],'rb') as expected,gzip.open(output,'wb',compresslevel=1) as actual:
                        for want in expected:
                            got=child.stdout.readline();actual.write(got)
                            if got!=want:
                                x=want.split();y=got.split();columns=[(i,p.decode(),q.decode()) for i,(p,q) in enumerate(zip(x,y)) if p!=q];(out/'mismatch.json').write_text(json.dumps(dict(case=c,row=rows,columns=columns,expected_columns=len(x),actual_columns=len(y)),indent=2)+'\n');raise ValueError(f'{key} row{rows} differs')
                            digest.update(got);rows+=1
                        assert not child.stdout.read(1) and child.wait(timeout=30)==0
                finally:
                    if child.poll() is None:child.kill();child.wait()
            assert rows==c['rows'] and digest.hexdigest()==c['raw_sha256'];done[key]=dict(rows=rows,raw_sha256=digest.hexdigest(),command=command,output=output.name)
        assert done[key]['raw_sha256']==c['raw_sha256'] and done[key]['rows']==c['rows'];records.append(dict(driver=c['driver'],song=c['song'],load=c['load'],**done[key]));print('native full song',key,c['load'],c['rows'],flush=True)
    for p,h in frozen.items():assert sha(p)==h
    assert source_manifest(root)[0]==mf
    return dict(cases=records,rows=sum(x['rows'] for x in records),product_producer_manifest=product['product_producer_manifest'],product_profile_sha256=sha(a.product_profile),exe_sha256=sha(binary),reference_receipt_sha256=sha(ref/'receipt.json'),reference_producer_manifest=r['source_manifest'])
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('hdi','reference','binary','product-profile'):p.add_argument('--'+n,type=Path)
    p.add_argument('--first-load-only',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if bool(a.hdi)==bool(a.reference):p.error('choose original HDI or reference')
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);archive(root,out,mf,files)
    r=produce(a,root,out,mf,files) if a.hdi else consume(a,root,out,mf,files)
    r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),source_archive_sha256=sha(out/'source.tar.gz'),engine_version=unicorn.__version__,engine_sha256=sha(Path(unicorn.unicorn._uc._name)),command=sys.argv,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('full supplied music corpus PASS',len(r['cases']),r['rows'],flush=True)
if __name__=='__main__':main()
