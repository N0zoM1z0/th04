#!/usr/bin/env python3
"""Actual muted OP idle -> recorded demos -> fresh OP -> ordinary MAIN.

Both characters/shots and all four original replays run with ordinary hit
consumption. Original callback/idle/startup receipts independently guard input,
terminal callbacks and initial RNG; GNU/UB frontend files compare each other.
This does not reexecute complete original gameplay or establish original full
pixels, physical timing/audio, config persistence or current Windows acceptance.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from verify import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('exe','hdi','font-bmp','original-dir','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--scores-file',type=Path);p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
 original=json.loads((a.original_dir/'receipt.json').read_text());assert original['passed']
 for mode,v in original['records'].items():assert sha((a.original_dir/(mode+'-original.txt')).read_bytes())==v['trace_sha256']
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);inputs=out/'inputs';inputs.mkdir()
 if a.reference_dir:
  previous=json.loads((a.reference_dir/'receipt.json').read_text());assert previous['passed'];scores=(a.reference_dir/'inputs/scores.SCR').read_bytes()
 else:
  assert a.scores_file is not None;scores=a.scores_file.read_bytes()
 (inputs/'scores.SCR').write_bytes(scores)
 command=[str(a.exe.resolve()),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font_bmp.resolve()),'--mute','--save-dir',str(inputs),'--demo-checks',str(out/'scenes')]
 r=subprocess.run(command,capture_output=True,timeout=300);(out/'stdout.log').write_bytes(r.stdout);(out/'stderr.log').write_bytes(r.stderr);r.check_returncode()
 initial=(a.original_dir/'init-original.txt').read_text().splitlines();rngs={int(line.split()[8]) for line in initial};assert len(rngs)==1;expected_rng=rngs.pop()
 replays=[(a.original_dir/'replays'/f'DEMO{i}.REC').read_bytes() for i in range(1,5)]
 for i,b in enumerate(replays,1):assert sha(b)==original['replays'][f'DEMO{i}.REC']
 checked=0
 for rank in (0,3):
  for abort in (0,1):
   name=f'rank{rank}-abort{abort}';path=out/'scenes'/name/'events.txt';lines=path.read_text().splitlines();starts=returns=0
   for line in lines:
    w=line.split()
    if w[0]=='START':
     n,stage,rng,resident=map(int,w[1:]);assert n==starts+1 and stage==[3,0,2,1][n-1] and rng==expected_rng;starts+=1
    elif w[0]=='FRAME':
     n,frame,keys,shift,replaced,finished=map(int,w[1:7]);replay=replays[n-1]
     if abort and frame==120:assert (keys,shift,replaced,finished)==([1,32,4096,16384][n-1],0,0,1)
     else:assert (keys,shift,replaced,finished)==(replay[frame],replay[frame+4000],1,int(frame>=3996))
     checked+=1
    elif w[0]=='RETURN':
     n,refreshes,generation,frames,rng=map(int,w[1:]);assert n==returns+1 and frames==(120 if abort else 3996)
     assert refreshes==frames+1+171 and rng==1;returns+=1
    else:raise ValueError('unknown demo frontend event')
   assert starts==returns==4
 outputs={str(f.relative_to(out/'scenes')):sha(f.read_bytes()) for f in sorted((out/'scenes').rglob('*')) if f.is_file()}
 if a.reference_dir:assert outputs==previous['outputs'],'current demo frontend differs from retained reference'
 assert source_manifest(root)[0]==manifest
 receipt=dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_manifest=manifest,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),original_receipt_sha256=sha((a.original_dir/'receipt.json').read_bytes()),physical_scores_sha256=sha(scores),visits=16,full_recorded_demos=8,early_abort_demos=8,callback_controls=checked,outputs=outputs,files=len(outputs),bmps=sum(n.endswith('.bmp') for n in outputs),muted=True,command=command,reference_dir=str(a.reference_dir) if a.reference_dir else None,scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('demo frontend PASS16 visits',checked,'callback observations',receipt['bmps'],'BMPs')
if __name__=='__main__':main()
