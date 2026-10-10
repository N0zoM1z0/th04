#!/usr/bin/env python3
"""Muted startup and physical host save/config restart through the real frontend.

Eleven settings/first-setup cases per driver run twice in separate host processes.
One authored finite STD per driver reaches ordinary Game Over, score-only MAINE
and fresh OP; it is not a natural six-stage route. Indexed/RGB and mixed PCM
comparisons here establish host consistency. Original startup control evidence
is bound separately; full independent startup pixels remain a separate gate.
"""
import argparse,hashlib,json,subprocess,sys,tarfile
from pathlib import Path
from datetime import datetime,timezone
from verify import source_manifest,require_elf_x86_64
from verify_pmd_driver import directory_files,HDI_SHA
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('hdi','font','rom','original-reference','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--binary',type=Path,action='append',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];mf,files=source_manifest(root)
    ref=json.loads((a.original_reference/'receipt.json').read_text())
    assert ref['passed'] and ref['original_cpu_reexecuted'] and ref['source_manifest']==mf
    import gzip
    assert hashlib.sha256(gzip.open(a.original_reference/'original.txt.gz','rb').read()).hexdigest()==ref['trace_sha256']
    directory_files(a.hdi);assert sha(a.hdi)==HDI_SHA
    assert sha(a.rom)=='53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8'
    frozen={q.resolve():sha(q) for q in a.binary+[a.hdi,a.font,a.rom,a.original_reference/'receipt.json']}
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    with tarfile.open(out/'source.tar.gz','w:gz') as archive:
        for f in files:assert sha(root/f['path'])==f['sha256'];archive.add(root/f['path'],arcname=f['path'])
    (out/'source-profile.json').write_text(json.dumps(dict(source_manifest=mf,files=files),indent=2)+'\n')
    runs=[];first={}
    for binary in a.binary:
        binary=binary.resolve();require_elf_x86_64(binary);host=binary.parent.name
        for profile in ('pmd','pmd86','pmdb2'):
            folder=out/(host+'-'+profile);folder.mkdir();saves=folder/'saves';saves.mkdir()
            inventories=[]
            for phase in (0,1):
                (saves/'phase.txt').write_text(str(phase)+'\n');outputs=folder/str(phase)
                command=[str(binary),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font.resolve()),
                    '--pmd-driver',profile,'--save-dir',str(saves),'--startup-checks',str(outputs),'--mute']
                if profile!='pmd':command+=['--opna-rom',str(a.rom.resolve())]
                with (folder/(str(phase)+'.log')).open('wb') as log:
                    subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
                inventory={q.relative_to(outputs).as_posix():sha(q) for q in sorted(outputs.rglob('*')) if q.is_file()}
                assert len(list(outputs.glob('*/events.txt')))==11
                assert len(list(outputs.glob('*/menu.bmp')))==11
                assert len(list(outputs.glob('*/fresh-op.bmp')))==(0 if phase else 1)
                key=(profile,phase)
                if key in first:assert inventory==first[key],key
                first[key]=inventory;inventories.append(inventory)
                runs.append(dict(binary=str(binary),binary_sha256=sha(binary),profile=profile,phase=phase,command=command,files=inventory))
                assert source_manifest(root)[0]==mf
                for q,digest in frozen.items():assert sha(q)==digest,('input changed',str(q))
            scores={q.relative_to(saves).as_posix():sha(q) for q in sorted(saves.rglob('*')) if q.is_file()}
            key=(profile,'saves')
            if key in first:assert scores==first[key],key
            first[key]=scores
            print(f'startup frontend {host}/{profile}:11 settings, actual child/fresh OP, separate-process restart PASS',flush=True)
    receipt=dict(passed=True,source_manifest=mf,source_files=len(files),source_archive_sha256=sha(out/'source.tar.gz'),
        utc=datetime.now(timezone.utc).isoformat(),runs=runs,hdi_sha256=HDI_SHA,font_sha256=sha(a.font),rom_sha256=sha(a.rom),
        original_reference_sha256=sha(a.original_reference/'receipt.json'),command=sys.argv,scope=__doc__)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
