#!/usr/bin/env python3
"""Compare TC4J integrated-assembler and TASM encodings for carpet residuals.

This is a producer-mechanism fingerprint only. It intentionally does not place
these instructions in maintained product source and grants no exactness or
original-assembly provenance by itself.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve(); sys.path.insert(0,str(ROOT/'scripts/probes'))
from probe_tc4_mov_bx_ax_encoding import code_bytes
FLAGS=('-c','-ml','-O','-b-','-3','-Z','-d')
INTEGRATED_INNER=bytes.fromhex('1e07f7e389c601dbf7e389c331d2ac89d7d1e789d7b90200e2fe')
TASM_BODY=bytes.fromhex('1e07f7e38bf003dbf7e38bd833d2ac8bfad1e78bfab90200e2fec3')
TARGET_CHUNKS={
 'ds_bridge':'1e07','first_mul_si':'f7e389c6','scale_mul':'01dbf7e3','bx_dx':'89c331d2',
 'lodsb':'ac','tile_index_shl':'89d7d1e7','dirty_index_move':'89d7','loop_opcode':'e2'}

def dg(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def outdir(p:Path|None)->Path:
 if p is None:
  d=PRIVATE/'reconstruction/probes'; d.mkdir(parents=True,exist_ok=True); return Path(tempfile.mkdtemp(prefix='carpet-asm-fingerprint-',dir=d))
 p=p.resolve()
 if p.exists() or not p.is_relative_to(PRIVATE): raise ValueError('output must be new below .analysis')
 p.mkdir(parents=True); return p

def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--output-dir',type=Path); a=ap.parse_args(); out=outdir(a.output_dir)
 surfaces=tomllib.loads((ROOT/'config/toolchain.toml').read_text())['surfaces']; by={x['id']:x for x in surfaces}
 tcc=ROOT/by['active-tcc']['path']; tasm=ROOT/by['active-tasm32']['path']; runner=ROOT/by['msdos-player-p0281']['path']
 for key,path in [('active-tcc',tcc),('active-tasm32',tasm),('msdos-player-p0281',runner)]:
  if dg(path.read_bytes())!=by[key]['sha256']: raise ValueError(f'{key} identity drift')
 env=os.environ.copy(); env.update(WINEPREFIX=str(ROOT/'.analysis/toolchain/wineprefix'),WINEDEBUG='-all',MSDOS_PATH=r'C:\TC4\BIN;C:\TASM50\BIN')
 cpp=out/'p.cpp'; cpp.write_text('''#pragma option -zCPROBE_TEXT -zPmain_01 -k-\nvoid near probe(void) {\nasm {\n push ds\n pop es\n mul bx\n mov si, ax\n add bx, bx\n mul bx\n mov bx, ax\n xor dx, dx\n lodsb\n mov di, dx\n shl di, 1\n mov di, dx\n mov cx, 2\nagain:\n loop again\n}\n}\n#pragma option -k.\n''')
 cmd=['wine',str(runner),'-e','-x','tcc',*FLAGS,f'-I{ROOT / "_reference/ReC98"}',cpp.name]
 d=subprocess.run(cmd,cwd=out,env=env,capture_output=True,text=True,timeout=120); (out/'integrated.log').write_text(d.stdout+d.stderr); obj=out/'p.obj'
 if d.returncode or not obj.is_file(): raise RuntimeError('integrated assembler compile failed')
 ic=code_bytes(obj); (out/'integrated.code').write_bytes(ic)
 if INTEGRATED_INNER not in ic: raise ValueError(f'integrated fingerprint drift: {ic.hex()}')
 asm=out/'external.asm'; asm.write_text('''.386\n.model use16 large\n_TEXT segment word public 'CODE' use16\nassume cs:_TEXT\npublic PROBE\nPROBE proc near\n push ds\n pop es\n mul bx\n mov si, ax\n add bx, bx\n mul bx\n mov bx, ax\n xor dx, dx\n lodsb\n mov di, dx\n shl di, 1\n mov di, dx\n mov cx, 2\nagain:\n loop again\n ret\nPROBE endp\n_TEXT ends\nend\n''')
 d=subprocess.run(['wine',str(tasm),'/m','/mx','/kh32768','/t','external.asm,external.obj'],cwd=out,env=env,capture_output=True,text=True,timeout=120); (out/'external.log').write_text(d.stdout+d.stderr); to=out/'external.obj'
 if d.returncode or not to.is_file(): raise RuntimeError('external TASM compile failed')
 tc=code_bytes(to); (out/'external.code').write_bytes(tc)
 if tc!=TASM_BODY: raise ValueError(f'TASM fingerprint drift: {tc.hex()}')
 integrated_hex=INTEGRATED_INNER.hex(); tasm_hex=TASM_BODY[:-1].hex()
 direction_sensitive={
  'mov_si_ax':{'target':'89c6','integrated':'89c6','tasm':'8bf0'},
  'add_bx_bx':{'target':'01db','integrated':'01db','tasm':'03db'},
  'mov_bx_ax':{'target':'89c3','integrated':'89c3','tasm':'8bd8'},
  'xor_dx_dx':{'target':'31d2','integrated':'31d2','tasm':'33d2'},
  'mov_di_dx_1':{'target':'89d7','integrated':'89d7','tasm':'8bfa'},
  'mov_di_dx_2':{'target':'89d7','integrated':'89d7','tasm':'8bfa'},
 }
 if any(v['integrated']!=v['target'] or v['tasm']==v['target'] for v in direction_sensitive.values()): raise ValueError('direction-sensitive classification drift')
 fixed={'push_ds_pop_es':'1e07','mul_bx':'f7e3','lodsb':'ac','shl_di_1':'d1e7','loop_opcode':'e2'}
 rec={'schema_version':1,'claim_scope':'TH04 carpet 23-byte residual TC4J integrated-assembler encoding fingerprint; no source/exact promotion','inputs':{'tcc_sha256':by['active-tcc']['sha256'],'tasm32_sha256':by['active-tasm32']['sha256'],'runner_sha256':by['msdos-player-p0281']['sha256'],'flags':list(FLAGS)},'target_residual_chunks':TARGET_CHUNKS,'integrated':{'source_sha256':dg(cpp.read_bytes()),'object_sha256':dg(obj.read_bytes()),'code_sha256':dg(ic),'code_hex':ic.hex(),'inner_hex':integrated_hex},'external_tasm':{'source_sha256':dg(asm.read_bytes()),'object_sha256':dg(to.read_bytes()),'code_sha256':dg(tc),'code_hex':tc.hex(),'body_without_ret_hex':tasm_hex},'direction_sensitive':direction_sensitive,'fixed_opcode_forms':fixed,'conclusion':'For every direction-sensitive register operation still blocked in carpet_lighting_put_new, TC4J integrated assembly selects the target 89/01/31 ModR/M direction while external TASM selects the non-target 8B/03/33 synonym. Both assemblers agree on fixed-opcode MUL BX, LODSB, SHL DI,1, PUSH DS/POP ES, and LOOP. Thus the entire 23-byte residual is consistent with one TC4J integrated-assembler encoding fingerprint, but this is mechanism evidence only.','limit':'The probe does not establish that the historical TH04 carpet source used inline assembly and does not authorize copying target-derived assembly into product source. Independent origin/provenance is still required by repository policy.'}; rp=out/'receipt.json'; rp.write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':dg(rp.read_bytes()),'integrated_inner':integrated_hex,'tasm_body':tasm_hex},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
