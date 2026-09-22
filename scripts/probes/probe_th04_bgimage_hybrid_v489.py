#!/usr/bin/env python3
"""Promote TH04 OP/MAINE BGIMAGE using cross-game-corroborated hybrid C++.

The maintained source keeps allocation/free and loop semantics in C++, and uses
symbolic low-level statements only for the independently TH05-corroborated
segment-stack/REP MOVSD producer and the even SHARED alignment. TC86 assembly
output is assembled by pinned TASM32, matching the target FIXUPP direction.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_master_object_split import sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from roundtrip_diet_target import check_toolchain, run_guest  # noqa: E402

SOURCE = ROOT / "src/shared/hardware/bgimage.cpp"
HEADER = ROOT / "src/shared/hardware/bgimage.hpp"
HMEM = ROOT / "src/shared/memory/hmem.hpp"
SOURCE_SHA = "537039ea684587ab7446c1b82932f4be1f7294ff599f0e6460e3b3e7808eaaf5"
CODE_SIZE = 0xD0
CODE_SHA = "efb4f7170ae577f5f18df689baffeeaad9fb34db3766d01ebdb25209d1f8f554"
ALL_FIXUPS = [0x04,0x0D,0x12,0x18,0x1D,0x23,0x28,0x2E,0x33,0x3D,0x44,0x4B,0x52,0x72,0x79,0x80,0x87,0xA0,0xA7,0xAA,0xB0,0xB3,0xB9,0xBC,0xC2,0xC5,0xCB]
SEG_FIXUPS = [0x0D,0x18,0x23,0x2E,0xAA,0xB3,0xBC,0xC5]
BG_RELOC_REL = [0x0F,0x1A,0x25,0x30,0xAC,0xB5,0xBE,0xC7]
CROSSGAME_MASK = [
  0x04,0x05,0x0D,0x0E,0x12,0x13,0x18,0x19,0x1D,0x1E,0x23,0x24,0x28,0x29,0x2E,0x2F,0x33,0x34,
  0x3D,0x3E,0x44,0x45,0x4B,0x4C,0x52,0x53,0x72,0x73,0x79,0x7A,0x80,0x81,0x87,0x88,0xA0,0xA1,
  0xA7,0xA8,0xAA,0xAB,0xB0,0xB1,0xB3,0xB4,0xB9,0xBA,0xBC,0xBD,0xC2,0xC3,0xC5,0xC6,0xCB,0xCC,
]
CROSSGAME_NORM_SHA = "de718574f65aaa539ef0d56da3ef4c7ee1f9d498418aa11d780e368cb05390d9"
BASE = {
 "op": {
   "exe":"d1e64a65e06844831264ad9691710007e629e63599639e73d1ca0a180d5a29d8",
   "map":"3f48d379d567cce4be13c68e9f053dffd8712a941ea4f32f9296df85bab3fe07",
   "program":"7e4cb7aa24782700d6db85c4cd39622d7b23e3a62d9da325b92089e9b8f1b948",
   "target":"40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
   "load":0xE428, "changed":list(range(186,194)), "reloc_count":804,
 },
 "maine": {
   "exe":"b8aa92ccea28a435a17e6bd9bab39507b851cbaa6ece281552daa553efbd411f",
   "map":"f4581d687d59e880962cee121a1edbb5246e248fff82b851319ac2522210455a",
   "program":"0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1",
   "target":"6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
   "load":0xD626, "changed":list(range(80,88)), "reloc_count":559,
 },
}
FINAL = {
 "op":{"exe":"c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274","map":"65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"},
 "maine":{"exe":"d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c","map":"014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e"},
}
TH05 = {"op": {"id":"th05-op-smoke","load":0xD688,"name":"OP.EXE"}, "maine":{"id":"th05-maine-smoke","load":0xEB6C,"name":"MAINE.EXE"}}


def digest(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def outdir(path: Path | None) -> Path:
 if path is None:
  root=PRIVATE/"reconstruction/probes"; root.mkdir(parents=True,exist_ok=True)
  return Path(tempfile.mkdtemp(prefix="bgimage-current-",dir=root))
 out=path.resolve()
 if out.exists() or not out.is_relative_to(PRIVATE): raise ValueError("output must be new and below .analysis")
 out.mkdir(parents=True); return out

def object_code(path: Path) -> tuple[bytes,list[tuple[int,int]]]:
 recs=parse_omf(path.read_bytes()); groups=code_ledata(recs,"SHARED")
 out=bytearray(max(e for s,e,n,f in groups))
 for s,e,n,f in groups: out[s:e]=recs[n-1].data[3:]
 fix=[(k,o) for r in recs if r.record_type==0x9C for k,o in fixup_locations(r.data)]
 return bytes(out),fix

def normalize_crossgame(data: bytes) -> bytes:
 if len(data)!=CODE_SIZE: raise ValueError("cross-game BGIMAGE size drift")
 out=bytearray(data)
 for i in CROSSGAME_MASK: out[i]=0
 return bytes(out)

def apply_product_source(work: Path) -> None:
 if sha(SOURCE)!=SOURCE_SHA: raise ValueError("maintained BGIMAGE source identity drift")
 for src in (HEADER,HMEM):
  dst=work/src.relative_to(ROOT); dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
 dst=work/"src/shared/hardware/bgimage.cpp"; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(SOURCE,dst)
 shutil.copy2(SOURCE,work/"th04/bgimage.cpp")

def compile_bgimage(work: Path, output: Path, label: str) -> dict[str,object]:
 apply_product_source(work)
 obj=work/"obj/th04/bgimage.obj"; asm=work/"obj/th04/bgimage.asm"; obj.unlink(missing_ok=True); asm.unlink(missing_ok=True)
 env=os.environ.copy(); env.update(WINEPREFIX=str(ROOT/".analysis/toolchain/wineprefix"),WINEDEBUG="-all",MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
 import subprocess
 cmd=["wine",str(RUNNER),"-e","-x","tcc","-B","-c","-I.","-O","-b-","-3","-Z","-d","-DGAME=4","-ml","-nobj/th04/","th04/bgimage.cpp"]
 p=subprocess.run(cmd,cwd=work,env=env,capture_output=True,text=True,timeout=180)
 (output/f"compile-{label}.log").write_text(json.dumps(cmd)+f"\nexit={p.returncode}\n"+p.stdout+"\n"+p.stderr)
 if not asm.is_file() or "Unable to execute command 'tasm.exe'" not in (p.stdout+p.stderr): raise ValueError(f"{label}: TCC -B generation surface drift")
 text=asm.read_text(errors="replace").lower()
 if text.count("rep movsd")!=2 or "even" not in text or "db\t243" in text or "codestring" in text or "__emit__" in text: raise ValueError(f"{label}: generated ASM symbolic-surface drift")
 run_checked(["wine","cmd","/d","/c",r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%&&tasm32 /m /mx /kh32768 /t /dGAME=4 obj\th04\bgimage.asm obj\th04\bgimage.obj"],work,output/f"assemble-{label}.log")
 code,fix=object_code(obj)
 if len(code)!=CODE_SIZE or digest(code)!=CODE_SHA or code[0x9D]!=0x90: raise ValueError(f"{label}: BGIMAGE CODE drift")
 if [o for k,o in fix]!=ALL_FIXUPS or [o for k,o in fix if k==3]!=SEG_FIXUPS: raise ValueError(f"{label}: BGIMAGE FIXUPP order drift")
 return {"object_sha256":sha(obj),"code_sha256":digest(code),"code_size":len(code),"all_fixup_locations":[o for k,o in fix],"segment_fixup_locations":[o for k,o in fix if k==3],"generated_asm_sha256":sha(asm)}

def crossgame(output: Path, th04_op_target: Path) -> dict[str,object]:
 manifest=tomllib.loads((ROOT/"config/targets.toml").read_text()); items={x["id"]:x for x in manifest["artifacts"]}
 binary,dosbox,config,options,toolchain=check_toolchain("th04-op")
 th04=parse_mz(th04_op_target.read_bytes()); ref=th04.program_image[BASE["op"]["load"]:BASE["op"]["load"]+CODE_SIZE]
 if digest(normalize_crossgame(ref))!=CROSSGAME_NORM_SHA: raise ValueError("TH04 cross-game reference drift")
 rel=[r.linear-BASE["op"]["load"] for r in th04.relocations if BASE["op"]["load"]<=r.linear<BASE["op"]["load"]+CODE_SIZE]
 if rel!=BG_RELOC_REL: raise ValueError("TH04 BGIMAGE relocation skeleton drift")
 result={"normalized_sha256":CROSSGAME_NORM_SHA,"masked_offsets":CROSSGAME_MASK,"th04_relative_relocations":rel,"th05":{}}
 for art,cfg in TH05.items():
  item=items[cfg["id"]]; packed=(ROOT/item["private_path"]).read_bytes()
  if len(packed)!=item["size"] or digest(packed)!=item["sha256"]: raise ValueError(f"{art}: TH05 target identity drift")
  work=output/f"crossgame-th05-{art}"; work.mkdir(); shutil.copy2(binary,work/"DIET.EXE"); (work/cfg["name"]).write_bytes(packed)
  command=run_guest(work,dosbox,config,f"diet.exe -ra {cfg['name'].lower()}","RESTORE.LOG")
  restored=(work/cfg["name"]).read_bytes(); (work/"restored.bin").write_bytes(restored); mz=parse_mz(restored)
  if not mz.valid: raise ValueError(f"{art}: restored TH05 MZ invalid")
  sl=mz.program_image[cfg["load"]:cfg["load"]+CODE_SIZE]
  if digest(normalize_crossgame(sl))!=CROSSGAME_NORM_SHA: raise ValueError(f"{art}: cross-game BGIMAGE architecture drift")
  rel=[r.linear-cfg["load"] for r in mz.relocations if cfg["load"]<=r.linear<cfg["load"]+CODE_SIZE]
  if rel!=BG_RELOC_REL: raise ValueError(f"{art}: cross-game BGIMAGE relocations drift")
  result["th05"][art]={"packed_sha256":item["sha256"],"restored_sha256":digest(restored),"load":cfg["load"],"slice_sha256":digest(sl),"normalized_sha256":digest(normalize_crossgame(sl)),"relative_relocations":rel,"restore_command":command}
 return result

def main() -> int:
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--op-source-dir",type=Path,required=True); ap.add_argument("--maine-source-dir",type=Path,required=True); ap.add_argument("--op-target-restored",type=Path,required=True); ap.add_argument("--maine-target-restored",type=Path,required=True); ap.add_argument("--output-dir",type=Path)
 ap.add_argument("--current-snapshot",action="store_true",help="revalidate retained v489 final source snapshots without the superseded v487/v488 inputs")
 args=ap.parse_args(); output=outdir(args.output_dir)
 if sha(RUNNER)!=RUNNER_SHA: raise ValueError("runner identity drift")
 sources={"op":args.op_source_dir.resolve(),"maine":args.maine_source_dir.resolve()}; targets={"op":args.op_target_restored.resolve(),"maine":args.maine_target_restored.resolve()}
 baseline={}; target_mz={}
 for art in ("op","maine"):
  exe=sources[art]/f"bin/th04/{art}.exe"; mp=sources[art]/f"obj/th04/{art}.map"
  expected=FINAL[art] if args.current_snapshot else BASE[art]
  if sha(exe)!=expected["exe"] or sha(mp)!=expected["map"]: raise ValueError(f"{art}: baseline identity drift")
  baseline[art]=parse_mz(exe.read_bytes()); target_mz[art]=parse_mz(targets[art].read_bytes())
  if sha(targets[art])!=BASE[art]["target"] or digest(baseline[art].program_image)!=BASE[art]["program"]: raise ValueError(f"{art}: target/program identity drift")
  bs=[r.linear for r in baseline[art].relocations]; ts=[r.linear for r in target_mz[art].relocations]
  expected_diffs=0 if args.current_snapshot else 8
  if len(bs)!=BASE[art]["reloc_count"] or Counter(bs)!=Counter(ts) or sum(a!=b for a,b in zip(bs,ts))!=expected_diffs: raise ValueError(f"{art}: baseline relocation frontier drift")
 provenance=crossgame(output,targets["op"])
 builds={}
 for label in ("a","b"):
  works={}
  for art in ("op","maine"):
   w=output/label/art/"source"; shutil.copytree(sources[art],w,symlinks=True); works[art]=w
  objinfo=compile_bgimage(works["op"],output,f"{label}-bgimage")
  shutil.copy2(works["op"]/"obj/th04/bgimage.obj",works["maine"]/"obj/th04/bgimage.obj")
  arts={}
  for art in ("op","maine"):
   w=works[art]; exe=w/f"bin/th04/{art}.exe"; mp=w/f"obj/th04/{art}.map"; exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
   run_checked(["wine",str(RUNNER),"-e","-x","tlink",fr"@obj\th04\{art}.@l"],w,output/f"link-{label}-{art}.log")
   mz=parse_mz(exe.read_bytes()); sites=[r.linear for r in mz.relocations]; ts=[r.linear for r in target_mz[art].relocations]; bs=[r.linear for r in baseline[art].relocations]
   if mz.program_image!=baseline[art].program_image: raise ValueError(f"{label}/{art}: linked program image drift")
   if sites!=ts or Counter(sites)!=Counter(ts): raise ValueError(f"{label}/{art}: relocation table is not target exact")
   changed=[i for i,(a,b) in enumerate(zip(bs,sites)) if a!=b]
   expected_changed=[] if args.current_snapshot else BASE[art]["changed"]
   if changed!=expected_changed: raise ValueError(f"{label}/{art}: changed-index drift")
   if sum(a!=b for a,b in zip(mz.program_image,target_mz[art].program_image))!=2: raise ValueError(f"{label}/{art}: target payload residual drift")
   if sha(exe)!=FINAL[art]["exe"] or sha(mp)!=FINAL[art]["map"]: raise ValueError(f"{label}/{art}: final EXE/MAP identity drift")
   arts[art]={"exe_sha256":sha(exe),"map_sha256":sha(mp),"program_image_sha256":digest(mz.program_image),"relocation_count":len(sites),"ordered_relocation_mismatches":0,"same_index_relocations":len(sites),"changed_indices_vs_baseline":changed,"target_program_differing_bytes":2}
  builds[label]={"object":objinfo,"artifacts":arts}
 for art in ("op","maine"):
  if builds["a"]["artifacts"][art]!=builds["b"]["artifacts"][art]: raise ValueError(f"A/B {art} differs")
 for key in ("code_sha256","code_size","all_fixup_locations","segment_fixup_locations"):
  if builds["a"]["object"][key]!=builds["b"]["object"][key]: raise ValueError(f"A/B object {key} differs")
 receipt={"schema_version":1,"observed_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"claim_scope":"TH04 OP/MAINE BGIMAGE hybrid authored C++ exact producer and cross-game provenance replay","replay_mode":"current-final-snapshot" if args.current_snapshot else "historical-v488-v487-transition","source_sha256":sha(SOURCE),"header_sha256":sha(HEADER),"hmem_header_sha256":sha(HMEM),"producer":"TC86 -B generated symbolic ASM -> pinned TASM32 5.0","crossgame":provenance,"builds":builds,"observed_effect":("Recompiling maintained BGIMAGE from the retained v489 final snapshots preserves both target-index-exact relocation tables and the complete program images." if args.current_snapshot else "Replacing BGIMAGE in the historical v488/v487 snapshots makes both full MZ relocation tables target-index exact without changing their program images.")+" The only remaining target-restored program-image difference in each artifact is the shared two-byte snd_load encoding.","limit":"The hybrid source uses symbolic low-level DS/ES stack operations, REP MOVSD, and an EVEN directive only where pure C++/intrinsic probes are compiler-negative and independent TH05 targets corroborate the same architecture. No emitted opcodes, codestrings, object patches, FIXUPP edits, or MZ relocation permutation are used."}
 rp=output/"receipt.json"; rp.write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps({"receipt":str(rp),"receipt_sha256":sha(rp),"op_mismatches":0,"maine_mismatches":0,"source_sha256":sha(SOURCE)},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
