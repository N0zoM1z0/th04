#!/usr/bin/env python3
"""Compare native popup fields and complete TRAM with unmodified original code."""
from __future__ import annotations
import argparse,gzip,hashlib,json,os,subprocess,sys
from pathlib import Path
from verify import source_manifest,require_elf_x86_64

def sha(data):return hashlib.sha256(data).hexdigest()
def configured():
    rows=[]
    for kind in range(4):
        for bonus in ((0,9,1234567,0xffffffff) if kind==2 else (0,)):
            rows.append(('S',kind,bonus));rows.extend(('U',) for _ in range(130))
    for before,after in ((a,b) for a in range(4) for b in range(4) if a!=b):
        for at in (63,64):
            rows.append(('S',before,0));rows.extend(('U',) for _ in range(at));rows.append(('Q',after,1234567 if after==2 else 0));rows.extend(('U',) for _ in range(132))
    for at in (0,1,6,7,14,65,127,128):
        rows.append(('S',0,0));rows.extend(('U',) for _ in range(at));rows.append(('Q',3,0));rows.extend(('U',) for _ in range(132))
    for bonus in (1,9,25000,0xffffffff):
        rows.append(('S',2,bonus));rows.append(('R',));rows.extend(('U',) for _ in range(20));rows.append(('R',));rows.extend(('U',) for _ in range(130))
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('dos-root','exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1];dos=a.dos_root.resolve();sys.path.insert(0,str(dos/'scripts/runtime'))
    from verify_dos_popup_score import PopupMachine
    manifest,sources=source_manifest(root);require_elf_x86_64(a.exe);out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);rows=configured();plan='\n'.join(' '.join(map(str,row)) for row in rows)+'\n';(out/'vectors.txt').write_text(plan)
    with (out/'vectors.txt').open('rb') as source,(out/'native.txt').open('wb') as destination:
        run=subprocess.run([str(a.exe.resolve()),'--vectors'],stdin=source,stdout=destination,stderr=subprocess.PIPE,env=dict(os.environ,UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'),timeout=120)
    (out/'stderr.txt').write_bytes(run.stderr);run.check_returncode();profiles=[]
    for load in (0x1000,0x3333):
        machine=PopupMachine(load);bad=[];different=0
        with (out/'native.txt').open() as native,gzip.open(out/('original-%04x.jsonl.gz'%load),'wt',compresslevel=1) as transcript:
            for index,op in enumerate(rows):
                if op[0]=='S':machine.seed(op[1],op[2])
                elif op[0]=='Q':machine.write(0x469b,'B',op[1]);machine.write(0x469e,'H',0x67e8);machine.write(0x46a2,'I',op[2])
                expected=machine.score() if op[0]=='R' else (machine.call() if machine.read(0x469e,'H')[0]==0x67e8 else machine.snapshot())
                columns=native.readline().split();assert len(columns)==11,'popup native record extent'
                keys=('frame','length','current','reached','left','dest','requested','callback','bonus');actual={k:int(v) for k,v in zip(keys,columns[:9])};actual.update(shift=columns[9],text=columns[10]);assert len(bytes.fromhex(actual['text']))==16384 and len(bytes.fromhex(actual['shift']))==9
                changed={k:dict(original=expected[k] if not isinstance(expected[k],str) else sha(bytes.fromhex(expected[k])),native=actual[k] if not isinstance(actual[k],str) else sha(bytes.fromhex(actual[k]))) for k in expected if expected[k]!=actual[k]}
                if changed:
                    different+=1
                    if len(bad)<8:bad.append(dict(index=index,operation=op,fields=changed))
                transcript.write(json.dumps(dict(index=index,input=op,original=expected,native_sha256=sha(json.dumps(actual,sort_keys=True).encode())),separators=(',',':'))+'\n')
            assert not native.read(1),'popup native trailing rows'
        profiles.append(dict(load=load,rows=len(rows),differing_rows=different,differences=bad,visited_original_instructions=len(machine.visited)))
    raw=out/'native.txt'
    raw_digest=hashlib.sha256()
    with raw.open('rb') as source,gzip.open(out/'native.txt.gz','wb',compresslevel=1) as destination:
        while block:=source.read(1024*1024):raw_digest.update(block);destination.write(block)
    with gzip.open(out/'native.txt.gz','rb') as source:
        digest=hashlib.sha256()
        while block:=source.read(1024*1024):digest.update(block)
    assert digest.digest()==raw_digest.digest();raw.unlink();assert source_manifest(root)[0]==manifest
    result=dict(passed=all(not row['differing_rows'] for row in profiles),profiles=profiles,source_manifest=manifest,source_files=sources,executable_sha256=sha(a.exe.read_bytes()),dos_sources={str(path):sha(path.read_bytes()) for path in (dos/'scripts/runtime/verify_dos_popup_score.py',dos/'scripts/runtime/verify_dos_hud_popup.py',dos/'scripts/runtime/verify_dos_text_gaiji.py',dos/'scripts/runtime/verify_dos_vsync_lifecycle.py',dos/'scripts/lib/pc98.py')},files={path.name:sha(path.read_bytes()) for path in out.iterdir()},scope='Original full popup/points,CRT and text/gaiji instructions execute without call adapters; a near-return sentinel ends the component call. Compare all popup fields and complete16KiB TRAM at two load segments over all four labels,128-frame expiry,64-frame replacement boundaries and bonus values and actual following score-drain return boundaries. Not natural UI input, complete picture, scan timing or exact promotion.')
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=result['passed'],profiles=profiles)));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
