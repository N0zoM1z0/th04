#!/usr/bin/env python3
"""Muted physical first-setup startup, selections, exit and separate restart.

Requires the independent original setup request receipt; frontend assets and
host files are actual native owners. No complete original OP/game/audio claim.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('exe','hdi','font-bmp','original-dir','scores-file','output-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
    original=json.loads((a.original_dir/'receipt.json').read_text());assert original['passed'] and original['original_cpu_reexecuted']
    assert sha((a.original_dir/'original.txt').read_bytes())==original['trace_sha256']
    assert sha(a.hdi.read_bytes())=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(a.font_bmp.read_bytes())=='41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);inputs=out/'inputs';inputs.mkdir();(inputs/'scores.SCR').write_bytes(a.scores_file.read_bytes())
    # Original six defaults, with a deliberately defined host checksum. The
    # invalid startup forms must request setup, while a valid rankFF survives.
    pending=bytes.fromhex('ff030201010100000007')
    for bgm in range(3):
        for se in range(3):
            name=f'b{bgm}-s{se}';n=bgm*3+se
            if n==0:continue
            data=pending
            if n==1:data=pending[:7]
            elif n==2:data=pending[:-1]+b'\0'
            elif n==3:data=bytes.fromhex('07030202010100000010')
            elif n==4:data=bytes.fromhex('0103020201ff00000008')
            else:data=pending[:6]+bytes.fromhex('a5127e')+pending[-1:]+b'\x42\x17'
            (inputs/(name+'.cfg')).write_bytes(data)
    commands=[]
    for phase in (0,1):
        (inputs/'phase.txt').write_text(str(phase)+'\n')
        command=[str(a.exe.resolve()),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font_bmp.resolve()),'--mute','--pmd-driver','none','--save-dir',str(inputs),'--setup-checks',str(out/f'phase{phase}')];commands.append(command)
        result=subprocess.run(command,capture_output=True,timeout=180);(out/f'phase{phase}-stdout.txt').write_bytes(result.stdout);(out/f'phase{phase}-stderr.txt').write_bytes(result.stderr);result.check_returncode()
        assert sum(line.startswith('SETUP bgm=') for line in result.stdout.decode().splitlines())==9
    for bgm in range(3):
        for se in range(3):
            name=f'b{bgm}-s{se}';before=(out/'phase0'/name/'before.cfg').read_bytes();assert before[0]==255
            options=bytes((1,3,2,bgm,se,1));expected=options+bytes(3)+bytes([sum(options)&255])+before[10:]
            for path in (out/'phase0'/name/'exit.cfg',out/'phase1'/name/'restarted.cfg',inputs/name/'MIKO.CFG'):assert path.read_bytes()==expected,path
    assert (out/'phase0/interrupted/exit.cfg').read_bytes()==bytes.fromhex('0103020201010000000a')
    assert (out/'phase0/failed/rejected.txt').read_bytes()==b'program=op setup=1 main=0 muted=1\n'
    assert (out/'phase0/fresh-op/exit.cfg').read_bytes()==bytes.fromhex('0103020102010000000a')
    outputs={str(f.relative_to(out)):sha(f.read_bytes()) for phase in ('phase0','phase1') for f in sorted((out/phase).rglob('*')) if f.is_file()}
    if a.reference_dir:
        previous=json.loads((a.reference_dir/'receipt.json').read_text());assert previous['passed'] and previous['outputs']==outputs
    assert source_manifest(root)[0]==manifest
    (out/'receipt.json').write_text(json.dumps(dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),original_receipt_sha256=sha((a.original_dir/'receipt.json').read_bytes()),hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),scores_sha256=sha(a.scores_file.read_bytes()),muted=True,process_launches=2,selections=9,interrupted_restart=1,failed_writes=1,fresh_op_setup=1,outputs=outputs,commands=commands,scope=__doc__),indent=2)+'\n')
    print('setup frontend PASS9 selections/two processes/interrupted restart/failed writer')
if __name__=='__main__':main()
