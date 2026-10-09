#!/usr/bin/env python3
"""Actual OP options/Scores/menu/MAIN join with physical saved files, muted.

Original ranking caller and file/LCG/row/fade instructions execute at two
loads using each frontend's retained initial buffers, physical file and input
samples. Original OP font/SUPER kernels independently compare sampled BMPs.
Initial native title pages, preceding PI decode, input/audio/waits/files and
CGROM/GRCG remain explicit adapters. No complete original OP loop, natural
survival/route, Windows execution, physical timing/audio or exact claim follows.
"""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
from verify_op_ranking import Original,fixtures
from verify_op_ranking_pixels import Raster
from verify_cutscene import ending_assets
from verify import source_manifest

sha=lambda b:hashlib.sha256(b).hexdigest()
def parse(line):
 w=line.split();c=list(map(int,w[:5]))+[bytes.fromhex(s) if s!='-' else b'' for s in w[5:9]]
 raw=bytes.fromhex(w[9]);c.append(list(struct.unpack('<'+'H'*(len(raw)//2),raw)));return c
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('target','decoded-dir','exe','hdi','font-bmp','pixel-reference-dir','output-dir'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--reference-dir',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);inputs=out/'inputs';inputs.mkdir()
 if a.reference_dir:
  prior=json.loads((a.reference_dir/'receipt.json').read_text());assert prior['passed']
  for f in (a.reference_dir/'inputs').iterdir():(inputs/f.name).write_bytes(f.read_bytes())
 else:
  o=Original(a.target,a.decoded_dir,0x1000);rows=fixtures(o);(inputs/'scores.SCR').write_bytes(rows[0][8]);cases=[]
  for rank in range(4):
   for scenario in (0,3,5):
    name=f'rank{rank}-input{scenario}';cases.append(f'{name} {rank}')
    keys=rows[rank*12+scenario][9];(inputs/(name+'.keys')).write_bytes(struct.pack('<'+'H'*len(keys),*keys))
  (inputs/'cases.txt').write_text('\n'.join(cases)+'\n')
 command=[str(a.exe.resolve()),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font_bmp.resolve()),'--mute','--pmd-driver','none','--save-dir',str(inputs),'--op-ranking-checks',str(out/'scenes')]
 r=subprocess.run(command,capture_output=True,timeout=180);(out/'native.txt').write_bytes(r.stdout);(out/'stderr.txt').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode()
 records=[];snapshots=0
 if a.reference_dir:
  originals=None;raster=None
 else:
  originals=[Original(a.target,a.decoded_dir,load) for load in (0x1000,0x2000)];assets=ending_assets(a.hdi);pictures={}
  for name in ('HI01.PI','OP1.PI'):
   body=(a.pixel_reference_dir/'assets'/(name+'.decoded')).read_bytes();packed=np.frombuffer(body[56:],dtype=np.uint8).reshape(400,320)
   pixels=np.empty((400,640),dtype=np.uint8);pixels[:,::2]=packed>>4;pixels[:,1::2]=packed&15;pictures[name]=(body[8:56],pixels)
  raster=Raster(a.target,a.decoded_dir,assets,pictures)
 for location in sorted((out/'scenes').iterdir()):
  observed=(location/'events.txt').read_text().splitlines()
  if originals:
   c=parse((location/'caller.txt').read_text());expected=[o.run(c) for o in originals];assert expected[0]==expected[1] and observed==expected[0],location.name
   raster.reset();initial=np.frombuffer((location/'before.idx').read_bytes(),dtype=np.uint8).reshape(400,640);raster.pages[0]=initial;raster.pages[1]=initial
   cursor=0
   for picture in sorted(location.glob('tick*.bmp'),key=lambda p:int(p.stem[4:])):
    tick=int(picture.stem[4:])
    while cursor<len(observed)-1 and int(observed[cursor].split()[1])<=tick:raster.apply(observed[cursor]);cursor+=1
    expected=raster.bytes()[512048:];actual=Image.open(picture).convert('RGB').tobytes()
    if actual!=expected:
     at=next(i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y)
     (out/'mismatch.json').write_text(json.dumps(dict(scene=location.name,tick=tick,rgb_offset=at),indent=2)+'\n');raise ValueError('ranking frontend original pixel differs')
    snapshots+=1
  else:
   ref=a.reference_dir/'scenes'/location.name
   assert (location/'events.txt').read_bytes()==(ref/'events.txt').read_bytes()
   for file in location.rglob('*'):
    if file.is_file():assert file.read_bytes()==(ref/file.relative_to(location)).read_bytes(),file
  assert (location/'before.bmp').read_bytes()==(location/'returned.bmp').read_bytes()
  assert (location/'save'/'GENSOU.SCR').read_bytes()==(inputs/'scores.SCR').read_bytes()
  records.append(dict(scene=location.name,trace_sha256=sha((location/'events.txt').read_bytes())))
 assert len(records)==12 and source_manifest(root)[0]==manifest
 outputs={f.relative_to(out/'scenes').as_posix():sha(f.read_bytes()) for f in sorted((out/'scenes').rglob('*')) if f.is_file()}
 receipt=dict(passed=True,source_manifest=manifest,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),original_cpu_reexecuted=bool(originals),original_kernel_calls=raster.kernel_calls if raster else 0,
  original_bmp_controls=snapshots,reference_dir=str(a.reference_dir) if a.reference_dir else None,cases=records,loads=['1000','2000'],muted=True,command=command,outputs=outputs,
  hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('OP ranking physical/menu/retained OP/MAIN PASS',len(records),'scenes;',snapshots,'original BMPs')
if __name__=='__main__':main()
