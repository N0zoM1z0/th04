#!/usr/bin/env python3
"""Muted config-enabled menus, live/exit saves, fresh OP and process restart.

The independent OP component receipt guards raw file operations/widths.
This verifier checks actual native menu transitions and physical storage;
it does not execute whole original OP/setup/gameplay or audio backends.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('exe','hdi','font-bmp','original-dir','scores-file','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
 original=json.loads((a.original_dir/'receipt.json').read_text());assert original['passed'] and original['original_cpu_reexecuted']
 assert sha((a.original_dir/'original.txt').read_bytes())==original['trace_sha256']
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);inputs=out/'inputs';inputs.mkdir()
 (inputs/'scores.SCR').write_bytes(a.scores_file.read_bytes());seed=bytes.fromhex('010302020101a5127e0a')
 for rank in range(4):
  for kind in range(2):
   name=f'r{rank}-k{kind}';n=rank*2+kind;data=seed
   if n==1:continue
   if n==2:data=seed[:-1]+b'\0'
   elif n==3:data=seed[:7]
   elif n==5:data=bytes.fromhex('ff030201010100000009')
   elif n==7:data=bytes.fromhex('0103020201ff00000008')
   (inputs/(name+'.cfg')).write_bytes(data)
 commands=[]
 for phase in (0,1):
  (inputs/'phase.txt').write_text(str(phase)+'\n')
  command=[str(a.exe.resolve()),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font_bmp.resolve()),'--mute','--save-dir',str(inputs),'--configuration-checks',str(out/f'phase{phase}')];commands.append(command)
  r=subprocess.run(command,capture_output=True,timeout=180);(out/f'phase{phase}-stdout.txt').write_bytes(r.stdout);(out/f'phase{phase}-stderr.txt').write_bytes(r.stderr);r.check_returncode()
  assert sum(line.startswith('CONFIG rank=') for line in r.stdout.decode().splitlines())==8
 for rank in range(4):
  for kind in range(2):
   name=f'r{rank}-k{kind}';directory=out/'phase0'/name
   o=bytes((rank,6-rank,rank%3,rank%3,(3-rank)%3,int(rank%2==0)))
   live=(directory/'live.cfg').read_bytes();before=(directory/'before.cfg').read_bytes()
   assert live==o+before[6:9]+bytes([sum(o)&255])
   final=bytearray(o);final[3]=(rank+kind)%3;expected=bytes(final)+bytes(3)+bytes([sum(final)&255])
   assert (directory/'exit.cfg').read_bytes()==expected
   assert (out/'phase1'/name/'restarted.cfg').read_bytes()==expected
   assert (inputs/name/'MIKO.CFG').read_bytes()==expected
 for n in range(4):assert (out/'phase0'/f'failed{n}'/'rejected.txt').read_text()==f'failed={n} program=op main=0 muted=1\n'
 extra=bytes.fromhex('030600000200a5127e0b')
 assert (out/'phase0/extra/live.cfg').read_bytes()==extra
 assert (out/'phase0/extra/save/MIKO.CFG').read_bytes()==extra
 outputs={str(f.relative_to(out)):sha(f.read_bytes()) for phase in ('phase0','phase1') for f in sorted((out/phase).rglob('*')) if f.is_file()}
 if a.reference_dir:
  previous=json.loads((a.reference_dir/'receipt.json').read_text());assert previous['passed'] and previous['outputs']==outputs
 assert source_manifest(root)[0]==manifest
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),original_receipt_sha256=sha((a.original_dir/'receipt.json').read_bytes()),hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),scores_sha256=sha(a.scores_file.read_bytes()),muted=True,process_launches=2,menu_cases=16,extra_entry=1,failed_writes=4,outputs=outputs,commands=commands,reference_dir=str(a.reference_dir) if a.reference_dir else None,scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('configuration frontend PASS16 menu cases,2 process launches,4 failed writers')
if __name__=='__main__':main()
