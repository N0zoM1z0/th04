#!/usr/bin/env python3
"""CPU-only PMD PCM integration against independent original register timelines.

Chip arithmetic shares the pinned BSD3 ymfm implementation; this is not an
independent waveform-accuracy Oracle. Original COM/parser/timer producer and
standalone host/mix/resampling adapter are independent of the native consumer.
No audio device/backend, frontend, physical analogue or full-route claim.
"""
import argparse,gzip,hashlib,json,subprocess,sys,tarfile,struct
from pathlib import Path
from datetime import datetime,timezone
import unicorn as U
from verify import source_manifest,require_elf_x86_64,require_pe_x86_64
from verify_pmd_driver import directory_files,install,DRIVERS,HDI_SHA
from verify_pmd_musical_fm import PORTS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def compressed(path,raw):
    with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as stream:stream.write(raw)
    assert gzip.decompress(path.read_bytes())==raw

def produce(a,root,out,mf,files):
    ref=a.clock_reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==174
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    rp=json.loads(a.renderer_profile.read_text());assert sha(a.renderer)==rp['binary_sha256'];assert sha(Path(rp['source_path']))==rp['source_sha256'];assert sha(Path(rp['command'][0]))==rp['compiler_sha256']
    for n,h in rp['external_inputs'].items():assert sha(Path(n))==h
    rom=json.loads(a.rom_profile.read_text());assert rom['passed'] and rom['size']==8192 and sha(a.rom)==rom['sha256']
    assert hashlib.sha1(a.rom.read_bytes()).hexdigest()=='50b6c3e288eaa12ad275d4f323267bb72b0445df'
    with tarfile.open(out/'producer-source.tar.gz','w:gz') as t:
        for f in files:assert sha(root/f['path'])==f['sha256'];t.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
    outputs={};cases=[];first={};frozen=[f for f in files if f['path'].endswith('.py')]
    binaries=directory_files(a.hdi);initial={};initial_cases=[]
    for load in (0x1000,0x2000):
      for name,(_,_,board,ext,_) in DRIVERS.items():
        d=install(binaries[name],name,load);base=PORTS[name];selected={};writes=[]
        for _,port,size,value in d.ports:
            if port in (base,base+4):selected[(port-base)//4]=value
            elif port in (base+2,base+6):
                bank=(port-base-2)//4;address=selected.get(bank);assert address is not None
                assert not(bank==0 and address in (0x2d,0x2e,0x2f)),"default prescaler setup required"
                writes.append((bank,address,value))
        raw=''.join(f'{b} {a} {v}\n' for b,a,v in writes).encode();path=out/(name+'-installation.txt')
        if name in initial:assert initial[name]==raw
        else:initial[name]=raw;path.write_bytes(raw);outputs[path.name]=sha(path)
        initial_cases.append(dict(driver=name,load=load,writes=len(writes),raw_sha256=hashlib.sha256(raw).hexdigest(),installation=path.name))
    for c in r['cases']:
        for name in ('MIKO.EFC',c['song'],c['mirror'],c['operations']):
            path=out/name;raw=(ref/name).read_bytes()
            if path.exists():assert path.read_bytes()==raw
            else:path.write_bytes(raw);outputs[name]=sha(path)
        name=c['driver']+'-'+c['song'];events=[]
        for b,adr,v in (map(int,line.split()) for line in initial[c['driver']].decode().splitlines()):events.append((0,b,adr,v))
        raw=gzip.decompress((ref/c['reference']).read_bytes());assert hashlib.sha256(raw).hexdigest()==c['raw_sha256'];assert len(raw.splitlines())==c['rows']
        at=1140 if c['board']==0 else 1146
        for line in raw.splitlines():
            row=list(map(int,line.split()));count=row[at];values=row[at+1:];assert len(values)==count*3
            events.extend((row[0],*values[i:i+3]) for i in range(0,len(values),3))
        event_bytes=''.join(' '.join(map(str,e))+'\n' for e in events).encode();event_sha=hashlib.sha256(event_bytes).hexdigest()
        if name not in first:
            p=out/(name+'-events.txt');p.write_bytes(event_bytes);pcm=out/(name+'.pcm');command=[str(a.renderer),str(c['board']),str(c['hz']),str(a.rom),str(p),str(c['end_cycle']),str(pcm)];subprocess.run(command,check=True)
            data=pcm.read_bytes();assert len(data)==4*(c['end_cycle']*48000//c['hz']);target=pcm.with_suffix('.pcm.gz');compressed(target,data);pcm.unlink();events_gz=p.with_suffix('.txt.gz');compressed(events_gz,event_bytes);p.unlink();outputs[target.name]=sha(target);outputs[events_gz.name]=sha(events_gz)
            first[name]=dict(reference=target.name,raw_sha256=hashlib.sha256(data).hexdigest(),event_sha256=event_sha,frames=len(data)//4,events=len(events),events_file=events_gz.name,renderer_command=command)
        else:assert first[name]['event_sha256']==event_sha
        cases.append(dict(driver=c['driver'],board=c['board'],song=c['song'],load=c['load'],mirror=c['mirror'],operations=c['operations'],installation=c['driver']+'-installation.txt',hz=c['hz'],end_cycle=c['end_cycle'],clock_reference=c['reference'],clock_raw_sha256=c['raw_sha256'],**first[name]));print(f'Original PCM {name} PSP{c["load"]:04x}: {first[name]["frames"]}frames PASS',flush=True)
    rom_path=out/'ym2608_adpcm_rom.bin';rom_path.write_bytes(a.rom.read_bytes());outputs[rom_path.name]=sha(rom_path)
    for f in frozen:assert sha(root/f['path'])==f['sha256']
    assert len(first)==87 and len(cases)==174
    return dict(cases=cases,frames=sum(c['frames'] for c in cases),unique_frames=sum(c['frames'] for c in first.values()),unique_renderings=len(first),outputs=outputs,initial_observations=initial_cases,renderer_profile=rp,renderer_profile_sha256=sha(a.renderer_profile),rom_profile=rom,rom_profile_sha256=sha(a.rom_profile),clock_receipt_sha256=sha(ref/'receipt.json'),clock_producer_manifest=r['source_manifest'],producer_source_archive_sha256=sha(out/'producer-source.tar.gz'),hdi_sha256=HDI_SHA,drivers={n:dict(size=len(v),sha256=hashlib.sha256(v).hexdigest(),format='flat-COM',entry='PSP:0100',service='PSP:0103') for n,v in binaries.items() if n in DRIVERS},unicorn_version=U.__version__,engine_sha256=sha(Path(U.unicorn._uc._name)),chip_independence=False,host_adapter_independence=True)

def consume(a,root,out,mf,files):
    ref=a.reference.resolve();r=json.loads((ref/'receipt.json').read_text());assert r['passed'] and len(r['cases'])==174 and r['unique_renderings']==87
    for n,h in r['outputs'].items():assert sha(ref/n)==h
    outputs={};results=[]
    for binary in a.binary:
        binary=binary.resolve();(require_pe_x86_64 if binary.suffix=='.exe' else require_elf_x86_64)(binary);folder=out/binary.parent.name;folder.mkdir();done={}
        for c in r['cases']:
            key=c['driver'],c['song']
            if key not in done:
                target=folder/f'{c["driver"]}-{c["song"]}.pcm';command=[str(binary),str(ref/c['song']),str(ref/'MIKO.EFC'),str(c['board']),str(ref/c['mirror']),str(ref/c['operations']),str(ref/'ym2608_adpcm_rom.bin'),str(ref/c['installation']),str(target)];subprocess.run(command,check=True);done[key]=target
            expected=gzip.decompress((ref/c['reference']).read_bytes());actual=done[key].read_bytes();assert hashlib.sha256(expected).hexdigest()==c['raw_sha256']
            if actual!=expected:
                upto=min(len(expected),len(actual));offset=next((i for i in range(0,upto,4) if actual[i:i+4]!=expected[i:i+4]),upto)
                raise ValueError(f'PCM {binary.parent.name} {key} frame{offset//4}: {expected[offset:offset+4].hex()}/{actual[offset:offset+4].hex()}, sizes{len(expected)}/{len(actual)}')
        for target in done.values():
            p=target.with_suffix('.pcm.gz');compressed(p,target.read_bytes());target.unlink();outputs[p.relative_to(out).as_posix()]=sha(p)
        results.append(dict(binary=str(binary),binary_sha256=sha(binary),runs=len(done),frames=r['frames'],unique_frames=r['unique_frames']));print(f'Native PCM {binary.parent.name}: {r["frames"]}frames PASS',flush=True)
    assert source_manifest(root)[0]==mf
    return dict(runs=results,frames=r['frames'],outputs=outputs,reference_receipt_sha256=sha(ref/'receipt.json'),reference_source_manifest=r['source_manifest'],chip_independence=False,host_adapter_independence=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hdi',type=Path);p.add_argument('--clock-reference',type=Path);p.add_argument('--renderer',type=Path);p.add_argument('--renderer-profile',type=Path);p.add_argument('--rom',type=Path);p.add_argument('--rom-profile',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--binary',type=Path,action='append',default=[]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    producer=bool(a.hdi)
    if producer==bool(a.reference) or bool(a.reference)!=bool(a.binary) or any(producer!=bool(getattr(a,n)) for n in ('clock_reference','renderer','renderer_profile','rom','rom_profile')):p.error('choose original HDI with clock reference, renderer/profile and ROM/profile, or reference with binaries')
    if a.renderer:a.renderer=a.renderer.resolve()
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root);out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);r=produce(a,root,out,mf,files) if producer else consume(a,root,out,mf,files);r.update(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),command=sys.argv,scope=__doc__);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
