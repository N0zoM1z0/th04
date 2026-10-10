#!/usr/bin/env python3
"""Verify frontend PCM transport with explicit fake devices; never open audio.

All nine BGM/SE settings on three driver profiles check mixed-PCM identity,
nonresident mono, mute admission, repaint invariance and scene ownership.
The existing seeded registration child remains a declared component fixture.
This is host transport/control evidence, not audible hardware validation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from verify import source_manifest,require_elf_x86_64

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def inventory(folder):return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('hdi','font','rom','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--binary',type=Path,action='append',required=True)
    parser.add_argument('--baseline-binary',type=Path)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    mf,files=source_manifest(root);out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    hdi,font,rom=[p.resolve() for p in (args.hdi,args.font,args.rom)]
    assert sha(hdi)=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(font)=='41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    assert sha(rom)=='53afd0fa9c62eda3e2be939e23f3adf48a2af8ad37bb1640261726c5d5adeba8'
    binaries=[p.resolve() for p in args.binary];baseline=args.baseline_binary.resolve() if args.baseline_binary else None
    frozen={str(p):sha(p) for p in [hdi,font,rom]+binaries+([baseline] if baseline else [])}
    runs=[];negative=[];first={}
    for index,binary in enumerate(([baseline] if baseline else [])+binaries):
        require_elf_x86_64(binary);label='baseline' if binary==baseline else str(index)+'-'+binary.parent.name
        for profile in ('pmd','pmd86','pmdb2'):
            folder=out/(label+'-'+profile)
            command=[str(binary),'--hdi',str(hdi),'--font-bmp',str(font),'--pmd-driver',profile,'--resident-sound-checks',str(folder)]
            if profile!='pmd':command+=['--opna-rom',str(rom)]
            command+=['--mute'] if binary==baseline else (['--mute','--audio'] if profile=='pmd86' else ['--audio','--mute'])
            with (out/(label+'-'+profile+'.log')).open('wb') as log:
                subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=300,check=True)
            contents=inventory(folder);assert len(contents)==65
            if profile in first:assert contents==first[profile],(label,profile,'old/other-host corpus differs')
            first[profile]=contents
            runs.append(dict(binary=str(binary),binary_sha256=sha(binary),profile=profile,command=command,files=contents,
                fake_transport=binary!=baseline,scope='ordinary OP/Music Room/MAIN plus declared registration child'))
            for p,digest in frozen.items():assert sha(Path(p))==digest
            print(label,profile,'65 complete files PASS',flush=True)
        if binary==baseline:continue
        for name,flags in [('headless',['--resident-sound-checks']),('interactive-diagnostic',['--title','--sound-checks'])]:
            folder=out/(label+'-reject-'+name);command=[str(binary),'--hdi',str(hdi),'--audio']+flags+[str(folder)]
            result=subprocess.run(command,capture_output=True,timeout=30)
            assert result.returncode!=0 and not folder.exists() and b'--audio requires an interactive --title' in result.stderr
            log=out/(label+'-reject-'+name+'.stderr.txt');log.write_bytes(result.stderr)
            negative.append(dict(command=command,exit_code=result.returncode,stderr_sha256=sha(log),output_created=False))
    assert source_manifest(root)[0]==mf
    for p,digest in frozen.items():assert sha(Path(p))==digest
    (out/'receipt.json').write_text(json.dumps(dict(passed=True,source_manifest=mf,source_files=len(files),
        inputs=frozen,runs=runs,negative=negative,command=sys.argv,scope=__doc__),indent=2)+'\n')
if __name__=='__main__':main()
