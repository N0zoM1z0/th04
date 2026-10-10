#!/usr/bin/env python3
"""Replay ordinary key-only routes through the maintained executable entry.

The public --natural-route-checks entry observes gameplay to choose keys.
It does not change actors, lives, hits,
score, stage or clear state. Legal six-life/two-bomb settings are initial
physical configuration. Extra requires a same-run Normal-earned score file.
This verifies logical routes and host consistency. --render paints each
startup and route refresh. Physical input/timing, full original routes,
remaining rank/shot/Continue cases and GUI delivery remain separate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from verify import source_manifest, require_elf_x86_64

ROOT=Path(__file__).resolve().parents[1]
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',choices=('linux','ubsan'),required=True)
    for name in ('binary','product-profile','source-profile','hdi','font','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--reference',type=Path)
    parser.add_argument('--extra',action='store_true')
    parser.add_argument('--render',action='store_true')
    a=parser.parse_args()
    profile=json.loads(a.product_profile.read_text())
    source=json.loads(a.source_profile.read_text())
    manifest,files=source_manifest(ROOT)
    assert manifest==source['source_manifest']==profile['source_manifest']
    assert source['files']==files and profile['source_files']==len(files)
    helper=ROOT/'port64/natural_route_probe.inl'
    binary=a.binary.resolve();require_elf_x86_64(binary)
    assert binary.name=='th04-port64'
    assert sha(binary)==profile['products'][a.host][binary.name]
    assert sha(a.hdi)=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(a.font)=='41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    pinned={p.resolve():sha(p) for p in (binary,a.product_profile,a.source_profile,a.hdi,a.font,helper,Path(__file__))}
    if a.reference:
        reference=json.loads((a.reference/'receipt.json').read_text())
        assert reference['passed']
        pinned[(a.reference/'receipt.json').resolve()]=sha(a.reference/'receipt.json')
        for case in reference['cases']:
            for name,digest in case['files'].items():
                path=(a.reference/case['name']/name).resolve()
                assert sha(path)==digest,path
                pinned[path]=digest
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    # Archive all maintained inputs; no rewritten frontend or private hook.
    with tarfile.open(out/'source.tar.gz','w:gz') as archive:
        for f in files:
            assert sha(ROOT/f['path'])==f['sha256']
            archive.add(ROOT/f['path'],arcname=f['path'])
    def guard() -> None:
        assert source_manifest(ROOT)[0]==manifest
        for p,h in pinned.items():assert sha(p)==h,p
    cases=[('easy-reimu',0,0,False),('normal-reimu',1,0,False),('normal-marisa',1,1,False)]
    if a.extra:cases.append(('extra-reimu',1,0,True))
    records=[]
    for name,rank,character,extra in cases:
        save=out/(name+'-saves');save.mkdir()
        if extra:
            for n in ('GENSOU.SCR','MIKO.CFG'):shutil.copyfile(out/'normal-reimu-saves'/n,save/n)
        initial={p.name:sha(p) for p in save.iterdir() if p.is_file()}
        plan=save/'route-plan.txt';plan.write_text(f'{rank} {character} 200000 {int(a.render)} 0 {int(extra)}\n')
        folder=out/name
        command=[str(binary),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font.resolve()),'--pmd-driver','pmd','--save-dir',str(save),'--natural-route-checks',str(folder),'--mute']
        guard()
        with (out/(name+'.log')).open('wb') as log:
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
        words=(folder/'result.txt').read_text().split()
        result={words[i]:int(words[i+1]) for i in range(0,len(words),2)}
        captures={p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}
        saves={n:sha(save/n) for n in ('GENSOU.SCR','MIKO.CFG')}
        clear=bool(result['fresh_op'] and not result['gameover_visits'] and result['registration_visits'] and (result['extra_visits'] if extra else result['ending_visits']))
        record=dict(name=name,result=result,natural_clear=clear,files=captures,saves=saves,initial_saves=initial,plan_sha256=sha(plan),command=command)
        if a.reference:
            expected=next(c for c in reference['cases'] if c['name']==name)
            assert record['result']==expected['result'] and saves==expected['saves'],name
            added={'startup-inputs.txt','menu-inputs.txt','startup-menu.bmp'}
            assert set(captures)-set(expected['files'])==added-set(expected['files']),name
            assert {n:captures[n] for n in expected['files']}==expected['files'],name
        (out/(name+'-receipt.json')).write_text(json.dumps(record,indent=2)+'\n')
        records.append(record);guard()
        print('ordinary key-only route',a.host,name,result,'natural clear',clear,flush=True)
    assert all(c['natural_clear'] for c in records),'Uncleared attempt retained;no aggregate acceptance.'
    receipt=dict(passed=True,host=a.host,cases=records,source_manifest=manifest,product_producer_manifest=profile['source_manifest'],source_profile_sha256=sha(a.source_profile),product_profile_sha256=sha(a.product_profile),binary_sha256=sha(binary),reference_receipt_sha256=sha(a.reference/'receipt.json') if a.reference else None,source_archive_sha256=sha(out/'source.tar.gz'),scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':
    main()
