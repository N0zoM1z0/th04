#!/usr/bin/env python3
"""Physical OP saved-score startup/restart, selection and writer-close join.

Original decoded OP codec/scan/selection instructions generate fixtures and
expected state at two relocated loads. Native Linux opens physical files,
repairs missing/bad/host-short input, starts actual MAIN/Extra resources, and
restarts a separate FrontEnd. Six explicitly seeded registration child scenes
save clear bits before blackout/fresh OP and then start Extra without an unlock
adapter. All ten saved sections independently decode under original OP.
Host incomplete-file rejection is explicit policy. Original file/input/render
consumers remain adapters; no natural survival, whole-scene pixels/audio/timing,
Windows runtime, pristine provenance or DOS byte-exact acceptance follows.
"""
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
from verify import source_manifest,require_elf_x86_64
from verify_op_score import Original,PACKED,PAYLOAD
sha=lambda b:hashlib.sha256(b).hexdigest()
def case(op=3,raw=b'',present=True,flags=bytes(10),stage=6,actions=b''):
 return [op,1,0,1,0,int(present),stage,bytes(196),bytes(196),flags,raw,actions]
def end(lines):return lines[-1].split()[1:]
def prepare(o):
 default=end(o.run(case(2,present=False)))[-1];raw=bytes.fromhex(default)
 plain=bytes.fromhex(end(o.run([0,1,0,1,0,1,6,raw[:196],raw[5*196:6*196],bytes(10),b'',b'']))[8])
 def file(flags):
  parts=[]
  for i in range(10):
   p=bytearray(plain);p[174]=flags[i];parts.append(o.encode(p,318+i))
  return b''.join(parts)
 zero=file(bytes(10));fixtures={}
 for mask in range(16):
  flags=bytearray(10)
  for c in range(2):flags[c*5+1]=(mask>>(c*2))&3
  fixtures[f'normal-mask{mask:02d}']=file(flags)
 for rank in (0,2,3,4):
  for mask in (1,8):
   flags=bytearray(10)
   for c in range(2):flags[c*5+rank]=(mask>>(c*2))&3
   fixtures[f'rank{rank}-mask{mask:02d}']=file(flags)
 for value in (4,19,128,255):
  flags=bytearray(10);flags[1]=value;flags[6]=1
  fixtures[f'invalid{value}']=file(flags)
 for rank in (0,3):
  bad=bytearray(fixtures['normal-mask15']);bad[rank*196+3]^=128;fixtures[f'bad-first-rank{rank}']=bytes(bad)
 bad=bytearray(zero);bad[6*196+2]^=1;fixtures['bad-second']=bytes(bad)
 fixtures['host-short']=zero[:103];fixtures['trailing']=zero+b'host trailing bytes';fixtures['missing']=None
 return fixtures,zero
def expected(o,raw,present=None,configured=1):
 if present is None:present=raw is not None and len(raw)>=1960
 c=case(raw=raw or b'',present=present);c[3]=configured;scan=end(o.run(c))
 flags=bytes.fromhex(scan[10]);extra=int(scan[5])!=0
 chosen=end(o.run(case(4,flags=flags,stage=6,actions=bytes([4,4]))))
 available=''.join(str(v) for v in o.read(0x3f82,'BBBB'))
 if not extra:chosen=end(o.run(case(4,flags=flags,stage=0,actions=bytes([4,4]))))
 read=' '.join([scan[1],scan[4],scan[5],scan[10],scan[8],scan[9],available])+'\n'
 selection=f'{chosen[6]} {chosen[7]} {6 if extra else 0}\n'
 return read,selection,bytes.fromhex(scan[-1])
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('target','decoded-dir','exe','hdi','font-bmp','output-dir'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();root=Path(__file__).resolve().parents[1];manifest,files=source_manifest(root)
 out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False);inputs=out/'original-inputs';inputs.mkdir()
 original=Original(a.target,a.decoded_dir,0x1000);fixtures,zero=prepare(original)
 (inputs/'cases.txt').write_text('\n'.join(fixtures)+'\n');(inputs/'zero.SCR').write_bytes(zero)
 for name,raw in fixtures.items():
  if raw is not None:(inputs/(name+'.SCR')).write_bytes(raw)
 command=[str(a.exe.resolve()),'--hdi',str(a.hdi.resolve()),'--font-bmp',str(a.font_bmp.resolve()),'--mute','--pmd-driver','none','--save-dir',str(inputs),'--op-score-checks',str(out/'scenes')]
 result=subprocess.run(command,capture_output=True,timeout=180);(out/'native.txt').write_bytes(result.stdout);(out/'stderr.txt').write_bytes(result.stderr)
 assert result.returncode==0,result.stderr.decode(errors='replace')
 assert sum(s.startswith('OP_SCORE ') for s in result.stdout.decode().splitlines())==len(fixtures)
 assert sum(s.startswith('OP_SCORE_REGISTRATION ') for s in result.stdout.decode().splitlines())==6
 rows=[]
 for load in (0x1000,0x2000):
  o=Original(a.target,a.decoded_dir,load);observed=[]
  for name,raw in fixtures.items():
   location=out/'scenes'/name;read,selection,saved=expected(o,raw)
   assert (location/'read.txt').read_text()==read,(load,name,'read')
   assert (location/'selection.txt').read_text()==selection,(load,name,'selection')
   assert (location/'save'/'GENSOU.SCR').read_bytes()==saved,(load,name,'physical repair')
   restart_read,_,_=expected(o,saved);assert (location/'restart'/'read.txt').read_text()==restart_read,(name,'restart')
   assert (location/'restart'/'selection.txt').read_text()=='0 0 0\n',name
   observed.append(dict(scene=name,read=read,selection=selection,restarted_read=restart_read,saved_sha256=sha(saved)))
  for location in sorted((out/'scenes').glob('registration-*')):
   saved=(location/'save'/'GENSOU.SCR').read_bytes();rank=int(location.name[-1]);read,selection,_=expected(o,saved,configured=rank)
   for base in (location,location/'restart'):
    observed_read=read if base==location else expected(o,saved)[0]
    assert (base/'read.txt').read_text()==observed_read,(load,location.name,'saved read')
    assert (base/'selection.txt').read_text()==selection,(load,location.name,'saved Extra')
   for rank in range(5):
    c=case(1,raw=saved);c[2]=rank;assert int(end(o.run(c))[0])==0,(location.name,rank,'ten sections')
   observed.append(dict(scene=location.name,read=read,selection=selection,saved_sha256=sha(saved),sections=10))
  rows.append(observed)
 assert rows[0]==rows[1];(out/'original.json').write_text(json.dumps(rows[0],indent=2)+'\n')
 require_elf_x86_64(a.exe);assert source_manifest(root)[0]==manifest
 outputs={f.relative_to(out/'scenes').as_posix():sha(f.read_bytes()) for f in sorted((out/'scenes').rglob('*')) if f.is_file()}
 receipt=dict(passed=True,source_manifest=manifest,source_files=len(files),exe_sha256=sha(a.exe.read_bytes()),packed_sha256=PACKED,payload_sha256=PAYLOAD,hdi_sha256=sha(a.hdi.read_bytes()),font_sha256=sha(a.font_bmp.read_bytes()),loads=['1000','2000'],physical_startup_restart_cases=len(fixtures),registration_close_cases=6,muted=True,command=command,outputs=outputs,utc=datetime.now(timezone.utc).isoformat(),scope=__doc__)
 (out/'source-manifest.json').write_text(json.dumps(dict(sha256=manifest,files=files),indent=2)+'\n');(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(f'PASS{len(fixtures)} physical OP startup/restart/selection and6 registration-close/fresh OP/Extra cases at two original loads; muted')
if __name__=='__main__':main()
