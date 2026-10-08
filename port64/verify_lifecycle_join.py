#!/usr/bin/env python3
"""Native MAIN lifecycle/Continue integration invariants and real host files.

Explicit player checkpoints, not natural routes or a joined original CPU run.
The retained original player/menu/file producers are separate differential gates.
"""
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from verify import source_manifest

sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('exe','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();out=a.output_dir.resolve()
 if out.exists():raise ValueError('use a fresh output directory')
 out.mkdir(parents=True);root=Path(__file__).resolve().parents[1]
 manifest,files=source_manifest(root)
 result=subprocess.run([str(a.exe.resolve()),'--lifecycle-join',str(out/'scenes')],
                       capture_output=True,text=True,check=True,timeout=60)
 (out/'trace.txt').write_text(result.stdout)
 outputs={str(path.relative_to(out/'scenes')):sha(path.read_bytes())
          for path in sorted((out/'scenes').rglob('*')) if path.is_file()}
 assert set(outputs)=={'continued/GENSOU.SCR','ranked/GENSOU.SCR','failed'}
 assert source_manifest(root)[0]==manifest
 receipt=dict(passed=True,observed_utc=datetime.now(timezone.utc).isoformat(),
              executable_sha256=sha(a.exe.read_bytes()),source_manifest=manifest,source_files=len(files),
              trace_sha256=sha((out/'trace.txt').read_bytes()),outputs=outputs,
              scope='Explicit native player checkpoints; real MAIN suffix, Game Over clocks, Continue writer-close, ten sections, restart and failed-write invariants. No natural route, original joined-CPU, frontend graphics, physical timing or audio acceptance.')
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('PASS native MAIN lifecycle/Continue integration and three host-file outputs')
if __name__=='__main__':main()
