#!/usr/bin/env python3
"""Cross-check TH03's homologous snd_load against the TH04 89 C3 blocker."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; PRIVATE=(ROOT/'.analysis').resolve(); sys.path[0:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/probes')]
from lib.pc98 import parse_mz
from lib.targets import find_artifact,load_target_manifest,read_verified_artifact
from replay_diet145f import check_toolchain
REST_SHA='efd858aef69a240af3a27c747a5beae150f55f0b41b8afdd1eda1760a759ecc0'; CAND_SHA='9f2e2af591645963d802489b45f9355a1e9f9b4da4b49ab0767f5be069ec204d'; MAP_SHA='d84e5b7763d6075b88decfe590c487d4ca31dab3d336a043a41c5ec387c70c2b'; BODY_SHA='5f8f4aee2edc3a11243bc57dbd716cfd3665adcdccfd63192c6bda6be516ad6c'; START=0xBF52; SIZE=0x70; MOV=0x49
def dg(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--source-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path); a=ap.parse_args(); src=a.source_dir.resolve(); out=(a.output_dir.resolve() if a.output_dir else Path(tempfile.mkdtemp(prefix='snd-th03-',dir=PRIVATE/'reconstruction/probes')))
 if not out.is_relative_to(PRIVATE) or (a.output_dir and out.exists()): raise ValueError('output must be new below .analysis')
 if a.output_dir: out.mkdir(parents=True)
 cand=src/'bin/th03/op.exe'; mp=src/'obj/th03/op.map'
 if dg(cand.read_bytes())!=CAND_SHA or dg(mp.read_bytes())!=MAP_SHA: raise ValueError('v401 TH03 candidate identity drift')
 line='0BEB:00A2 0070 C=CODE   S=SHARED         G=(none)  M=th02/snd_load.cpp ACBP=28'
 if line not in mp.read_text(encoding='cp437',errors='replace'): raise ValueError('TH03 snd_load map owner drift')
 art=find_artifact(load_target_manifest(ROOT/'config/targets.toml'),'th03-op-smoke'); packed=read_verified_artifact(ROOT,art); diet,dosbox,cfg,_,tool=check_toolchain('th04-op'); w=out/'restore'; w.mkdir(); shutil.copy2(diet,w/'DIET.EXE'); (w/'OP.EXE').write_bytes(packed)
 env=os.environ.copy(); env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',XDG_CACHE_HOME=str(w/'cache'),XDG_CONFIG_HOME=str(w/'config'),XDG_DATA_HOME=str(w/'data')); cmd=[str(dosbox),'-defaultconf','-defaultmapper','-conf',str(cfg),'-fastlaunch','-nogui','-nomenu','-exit','-time-limit','30','-c',f'mount c "{w}"','-c','c:','-c','diet.exe -ra op.exe > restore.log','-c','exit']; d=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=40); (w/'host.log').write_text(d.stdout+d.stderr); gl=w/'RESTORE.LOG'
 if d.returncode or not gl.exists() or 'Success!' not in gl.read_bytes().decode('cp437',errors='replace'): raise RuntimeError('TH03 DIET restore failed')
 raw=(w/'OP.EXE').read_bytes(); tm=parse_mz(raw); cm=parse_mz(cand.read_bytes())
 if not tm.valid or dg(raw)!=REST_SHA or len(tm.program_image)!=59770 or len(tm.relocations)!=607: raise ValueError('restored TH03 identity drift')
 tb=tm.program_image[START:START+SIZE]; cb=cm.program_image[START:START+SIZE]
 if tb!=cb or dg(tb)!=BODY_SHA or tb[MOV:MOV+2]!=b'\x8b\xd8': raise ValueError('TH03 snd_load body/handle-copy drift')
 rec={'schema_version':1,'claim_scope':'TH03 homologous snd_load cross-game negative for TH04 89 C3','th03_packed_sha256':art['sha256'],'restored_sha256':dg(raw),'candidate_sha256':CAND_SHA,'candidate_map_sha256':MAP_SHA,'load_extent':f'0x{START:X}..0x{START+SIZE-1:X}','body_sha256':BODY_SHA,'target_candidate_raw_equal':True,'handle_copy_load':hex(START+MOV),'handle_copy_hex':tb[MOV:MOV+2].hex(),'toolchain':tool,'conclusion':'TH03 joins TH02 and TH05 in using natural 8B D8 for MOV BX,AX; TH04 alone uses 89 C3 across its shared MAIN/OP/MAINE producer. This strengthens the provenance block and grants no exactness.','limit':'Cross-game negative only; it does not prove TH04 source syntax.'}; rp=out/'receipt.json'; rp.write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':dg(rp.read_bytes()),'handle_copy':rec['handle_copy_hex']},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
