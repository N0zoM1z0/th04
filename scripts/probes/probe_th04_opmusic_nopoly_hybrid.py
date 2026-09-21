#!/usr/bin/env python3
"""Replay the cross-game-corroborated TH04 OP nopoly_B_put copy core."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve()
sys.path[0:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/probes')]
from lib.pc98 import parse_mz
from lib.omf import normalize_dependency_timestamps
from lib.targets import find_artifact,load_target_manifest,read_verified_artifact
from probe_th04_master_object_split import build,compare,sha
from probe_tc4_mov_bx_ax_encoding import code_bytes
from replay_diet145f import check_toolchain
FRAGMENT=ROOT/'config/replay/th04_op_music_nopoly_core_v402.inl'
OLD='\t__memcpy__(MK_FP(_ES, 0), MK_FP(_DS, 0), PLANE_SIZE);\n'
BASE={
'Tupfile.lua':'c753fc557e97ac10872bd7a8a7a2f07200193082889fb78160edcfaf22915a8e',
'th02/op/m_music.cpp':'85440d4778240ef183a90134db9969111fef1d24681e8abea5c538242509643f',
'bin/th04/op.exe':'3000d2c113cc4a7eb4d2f79cdb9c5cebbec1d7180e699525dafe86fbb8af3d5a',
'obj/th04/op.map':'08ab21543cc5e7c58e29a566538011aab3514adb5d3193216df7e44d671b0cf3'}
REST={
'th03-op':(63866,'efd858aef69a240af3a27c747a5beae150f55f0b41b8afdd1eda1760a759ecc0',59770,607,0xA5FB),
'th05-op':(80906,'1caaa7f804146838e8771ae69487005f1ccd70cc8369dcb62e8adaf6addad71c',75786,952,0xBFFB)}
TH04_PAY='13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74'; TH04_MOTIF=0xBFAC
MOTIF=re.compile(rb'\x1e\xb8\x00\xa8\x8e\xc0\xa1..\x8e\xd8(?:\x31\xff\x31\xf6|\x33\xff\x33\xf6)\xb9\x80\x3e\xf3\xa5\x1f')
HYBRID_EXE='5a7af3868e28e2bc46268d413f8f7e78213603431b3c1acc3e4f85f4d8cb95eb'; MAP_SHA=BASE['obj/th04/op.map']
def dg(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def outdir(p:Path)->Path:
 p=p.resolve()
 if not p.is_relative_to(PRIVATE) or p.exists(): raise ValueError('output must be new below .analysis')
 p.mkdir(parents=True); return p
def body(payload:bytes,m:int)->tuple[str,str]:
 b=bytearray(payload[m-5:m+25])
 if len(b)!=30 or b[:12]!=bytes.fromhex('55 8b ec 56 57 1e b8 00 a8 8e c0 a1') or b[14:16]!=b'\x8e\xd8' or b[20:]!=bytes.fromhex('b9 80 3e f3 a5 1f 5f 5e 5d c3'): raise ValueError('nopoly body shape drift')
 x=bytes(b[16:20]).hex(); b[12:14]=b'\0\0'; return x,dg(bytes(b))
def restore(aid:str,out:Path)->dict:
 manifest_id=aid+'-smoke'; art=find_artifact(load_target_manifest(ROOT/'config/targets.toml'),manifest_id); packed=read_verified_artifact(ROOT,art); exp=REST[aid]
 diet,dosbox,cfg,_,tool=check_toolchain('th04-op'); w=out/aid; w.mkdir(); shutil.copy2(diet,w/'DIET.EXE'); (w/'OP.EXE').write_bytes(packed)
 env=os.environ.copy(); env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',XDG_CACHE_HOME=str(w/'cache'),XDG_CONFIG_HOME=str(w/'config'),XDG_DATA_HOME=str(w/'data'))
 cmd=[str(dosbox),'-defaultconf','-defaultmapper','-conf',str(cfg),'-fastlaunch','-nogui','-nomenu','-exit','-time-limit','30','-c',f'mount c "{w}"','-c','c:','-c','diet.exe -ra op.exe > restore.log','-c','exit']
 d=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=40); (w/'host.log').write_text(d.stdout+d.stderr); gl=w/'RESTORE.LOG'; gt=gl.read_bytes().decode('cp437',errors='replace') if gl.exists() else ''
 if d.returncode or 'Success!' not in gt: raise RuntimeError(f'{aid}: DIET restore failed')
 raw=(w/'OP.EXE').read_bytes(); mz=parse_mz(raw)
 if not mz.valid or (len(raw),dg(raw),len(mz.program_image),len(mz.relocations))!=exp[:4]: raise ValueError(f'{aid}: restored identity drift')
 hits=list(MOTIF.finditer(mz.program_image));
 if len(hits)!=1 or hits[0].start()!=exp[4]: raise ValueError(f'{aid}: motif drift')
 x,n=body(mz.program_image,hits[0].start())
 if x!='31ff31f6': raise ValueError(f'{aid}: xor direction drift')
 return {'packed_sha256':art['sha256'],'restored_sha256':dg(raw),'payload_size':len(mz.program_image),'relocation_count':len(mz.relocations),'motif_offset':hex(exp[4]),'xor_hex':x,'normalized_body_sha256':n,'toolchain':tool,'restore_log_sha256':dg(gl.read_bytes())}
def th04_target()->dict:
 p=(ROOT/'.analysis/reconstruction/v218-th04-op-diet/payload.bin').read_bytes()
 if dg(p)!=TH04_PAY: raise ValueError('TH04 OP payload identity drift')
 h=list(MOTIF.finditer(p))
 if len(h)!=1 or h[0].start()!=TH04_MOTIF: raise ValueError('TH04 motif drift')
 x,n=body(p,TH04_MOTIF)
 if x!='31ff31f6': raise ValueError('TH04 xor direction drift')
 return {'payload_sha256':dg(p),'payload_size':len(p),'motif_offset':hex(TH04_MOTIF),'xor_hex':x,'normalized_body_sha256':n}
def controls(out:Path)->dict:
 surfaces=tomllib.loads((ROOT/'config/toolchain.toml').read_text())['surfaces']; t=next(x for x in surfaces if x['id']=='active-tcc')
 if sha(ROOT/t['path'])!=t['sha256']: raise ValueError('TCC identity drift')
 runner=ROOT/'_reference/ReC98/bin/msdos.exe'; env=os.environ.copy(); env.update(WINEPREFIX=str(ROOT/'.analysis/toolchain/wineprefix'),WINEDEBUG='-all',MSDOS_PATH=r'C:\TC4\BIN;C:\TASM50\BIN')
 variants={'assign_zero':'_DI = 0; _SI = 0;','xor_self':'_DI ^= _DI; _SI ^= _SI;','integrated_asm':'asm { xor di, di; xor si, si; }'}
 expected={'assign_zero':'565733ff33f65f5ec3','xor_self':'565733ff33f65f5ec3','integrated_asm':'565731ff31f65f5ec3'}; got={}
 for name,stmt in variants.items():
  w=out/f'compiler-{name}'; w.mkdir(); s=w/'p.cpp'; s.write_text('#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n#include <dos.h>\nvoid near probe(void) { '+stmt+' }\n#pragma option -k.\n')
  cmd=['wine',str(runner),'-e','-x','tcc','-c','-ml','-O','-b-','-3','-Z','-d',f'-I{ROOT / "_reference/ReC98"}','p.cpp']; d=subprocess.run(cmd,cwd=w,env=env,capture_output=True,text=True,timeout=120); (w/'compile.log').write_text(d.stdout+d.stderr); o=w/'p.obj'
  if d.returncode or not o.is_file(): raise RuntimeError(f'{name}: compile failed')
  c=code_bytes(o)
  if c.hex()!=expected[name]: raise ValueError(f'{name}: opcode selection drift')
  got[name]={'source_sha256':dg(s.read_bytes()),'object_sha256':dg(o.read_bytes()),'code_hex':c.hex(),'code_sha256':dg(c)}
 return {'tcc_sha256':t['sha256'],'runner_sha256':dg(runner.read_bytes()),'variants':got}
def valid(label:str,r:dict,diff:int,starts:list[int])->None:
 if r['payload_differing_bytes']!=diff or [x['start'] for x in r['payload_mismatch_runs']]!=starts or r['relocation_multiset_exact'] is not True or r['target_payload_size']!=r['candidate_payload_size']: raise ValueError(f'{label}: payload Oracle drift')
def patch(w:Path)->None:
 p=w/'th02/op/m_music.cpp'; t=p.read_text()
 if t.count(OLD)!=1: raise ValueError('memcpy anchor drift')
 p.write_text(t.replace(OLD,FRAGMENT.read_text(),1))
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--source-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path); a=ap.parse_args(); src=a.source_dir.resolve()
 if not src.is_dir(): ap.error('--source-dir must exist')
 out=outdir(a.output_dir) if a.output_dir else Path(tempfile.mkdtemp(prefix='opmusic-v402-',dir=PRIVATE/'reconstruction/probes'))
 for rel,h in BASE.items():
  if not (src/rel).is_file() or sha(src/rel)!=h: raise ValueError(f'v401 baseline drift: {rel}')
 baseline=compare('th04-op',src); valid('baseline',baseline,4,[0xBFB7,0xBFB9,0xDE8B])
 targets={'th03-op':restore('th03-op',out),'th04-op':th04_target(),'th05-op':restore('th05-op',out)}
 if len({x['normalized_body_sha256'] for x in targets.values()})!=1: raise ValueError('cross-game bodies differ')
 cc=controls(out); builds={}
 for lab in ('a','b'):
  w=out/lab/'source'; shutil.copytree(src,w,symlinks=True); patch(w); build(w,out/f'build-{lab}.log'); r=compare('th04-op',w); valid(lab,r,2,[0xDE8B]); exe=w/'bin/th04/op.exe'; mp=w/'obj/th04/op.map'; obj=w/'obj/th04/op_music.obj'
  if sha(exe)!=HYBRID_EXE or sha(mp)!=MAP_SHA: raise ValueError(f'{lab}: linked identity drift')
  raw=obj.read_bytes(); builds[lab]={'exe_sha256':sha(exe),'map_sha256':sha(mp),'op_music_object_sha256':dg(raw),'op_music_object_normalized_sha256':dg(normalize_dependency_timestamps(raw)),'comparison':r}
 if builds['a']['exe_sha256']!=builds['b']['exe_sha256'] or builds['a']['op_music_object_normalized_sha256']!=builds['b']['op_music_object_normalized_sha256']: raise ValueError('A/B normalized identity differs')
 la=dict(builds['a']['comparison']); lb=dict(builds['b']['comparison']); la.pop('candidate_path',None); lb.pop('candidate_path',None)
 if la!=lb: raise ValueError('A/B payload Oracle differs')
 rec={'schema_version':1,'claim_scope':'TH04 OP nopoly_B_put cross-game producer and hybrid decoded-payload diagnostic; no packed-file or authored exact promotion','baseline':{'identity':BASE,'comparison':baseline},'fragment_path':str(FRAGMENT.relative_to(ROOT)),'fragment_sha256':sha(FRAGMENT),'cross_game_targets':targets,'compiler_controls':cc,'builds':builds,'observed_effect':'TH03/TH04/TH05 independently preserve the same 30-byte nopoly_B_put architecture modulo the linked nopoly_B word. Natural TC4J emits 33 FF / 33 F6 while its integrated assembler emits target 31 FF / 31 F6. Replacing only the corroborated irreducible copy core reduces TH04 OP payload mismatch from four bytes to the two-byte shared snd_load residual.','limit':'Replay input only. No OP authored-source/function exactness or packed-file exactness credit; original unpacked relocation order remains separate.'}; rp=out/'receipt.json'; rp.write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':sha(rp),'candidate_op_sha256':builds['a']['exe_sha256'],'remaining_payload_differences':2},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
