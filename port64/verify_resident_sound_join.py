#!/usr/bin/env python3
"""Muted actual frontend resident audio and real Ending/Staff measure consumers.

All nine BGM/SE settings use three explicit original-driver profiles. Ordinary
OP/Music Room/MAIN controls and a separate seeded registration child exercise
resource/config/score boundaries. An authored legal Ending script isolates live
measure waits; the first Staff wait uses original resources. Frontend mixed PCM
and displays are host-consistency evidence, not an independent waveform or
complete-route Oracle. Independent service/FM PCM evidence is separately bound.
"""
import argparse,hashlib,json,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
from verify import source_manifest,require_elf_x86_64
from verify_pmd_driver import directory_files,HDI_SHA
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('hdi','font','rom','original-reference','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--binary',type=Path,action='append',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root)
    frozen={p.resolve():sha(p) for p in a.binary+[a.hdi,a.font,a.rom,a.original_reference/'receipt.json']}
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    directory_files(a.hdi);assert sha(a.rom)=='53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8'
    ref=json.loads((a.original_reference/'receipt.json').read_text());assert ref['passed'] and len(ref['cases'])==72
    for n,h in ref['outputs'].items():assert sha(a.original_reference/n)==h
    with tarfile.open(out/'source.tar.gz','w:gz') as archive:
        for f in files:assert sha(root/f['path'])==f['sha256'];archive.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
    results=[];first={}
    for binary in a.binary:
        binary=binary.resolve();require_elf_x86_64(binary);host=binary.parent.name
        for profile in ('pmd','pmd86','pmdb2'):
            folder=out/(host+'-'+profile)
            command=[str(binary),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font.resolve()),'--pmd-driver',profile,'--resident-sound-checks',str(folder),'--mute']
            if profile!='pmd':command+=['--opna-rom',str(a.rom.resolve())]
            with (out/(host+'-'+profile+'.log')).open('wb') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            inventory={f.relative_to(folder).as_posix():sha(f) for f in sorted(folder.rglob('*')) if f.is_file()}
            assert len(inventory)==65 and len(list(folder.glob('*/mixed.pcm')))==9 and len(list(folder.glob('*/fresh-op.bmp')))==9
            inactive=list(map(int,(folder/'measure-off.txt').read_text().split()))
            active=list(map(int,(folder/'measure-active.txt').read_text().split()))
            assert len(inactive)==3 and inactive[0:2]==[500,0]
            assert len(active)==3 and 0<active[0]<500 and active[1]>=3 and active[2]>inactive[2]
            if profile in first:assert inventory==first[profile],profile
            first[profile]=inventory
            results.append(dict(binary=str(binary),binary_sha256=sha(binary),profile=profile,command=command,files=inventory,scenarios=9,pcm_frames=sum(f.stat().st_size//4 for f in folder.glob('*/mixed.pcm'))))
            for path,digest in frozen.items():assert sha(path)==digest,('input changed during frontend run',str(path))
            print(f'Frontend resident {host}/{profile}:9scenes/{len(inventory)}files PASS',flush=True)
    assert source_manifest(root)[0]==mf
    for path,digest in frozen.items():assert sha(path)==digest,('input changed during frontend run',str(path))
    receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=mf,source_files=len(files),source_archive_sha256=sha(out/'source.tar.gz'),runs=results,hdi_sha256=HDI_SHA,font_sha256=sha(a.font),rom_sha256=sha(a.rom),original_reference_sha256=sha(a.original_reference/'receipt.json'),command=sys.argv,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
