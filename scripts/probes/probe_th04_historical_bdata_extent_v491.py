#!/usr/bin/env python3
"""Test real historical MASTER b_data.OBJ as the TH04 T-extent mechanism.

The target-derived T EOF lands at the historical 0xC6 BGM BSS boundary.  This
probe restores the independently attested b_data.OBJ as a physical linker input
while preserving its exact _DATA/_BSS position by splitting the reconstructed
master data-tail around it.  If the object boundary itself caused the larger
file-backed extent, TLINK output should change.  No product or MZ bytes are
patched.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tasm  # noqa: E402
from probe_th04_master_bgm_archive_order import ARCHIVE, ARCHIVE_SHA, RUNNER_SHA, TLIB, TLIB_SHA, run_tlib  # noqa: E402
from probe_th04_master_bgm_bss_archive import BDATA_SHA256, BDATA_SIZE, segment_table, data_records  # noqa: E402
from probe_th04_master_object_split import sha  # noqa: E402
from lib.omf import parse_omf  # noqa: E402

BASE = {
    "op": {
        "exe_sha256": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
        "map_sha256": "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee",
        "file_size": 73636,
        "load_size": 69028,
        "minalloc": 612,
        "response": "obj/th04/op.@l",
        "exe": "bin/th04/op.exe",
        "map": "obj/th04/op.map",
        "old_obj": r"obj\th04\opmdata.obj",
        "new_objs": r"obj\th04\opdp91.obj obj\th04\b_data.obj obj\th04\opds91.obj",
    },
    "maine": {
        "exe_sha256": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        "map_sha256": "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e",
        "file_size": 65998,
        "load_size": 62414,
        "minalloc": 817,
        "response": "obj/th04/maine.@l",
        "exe": "bin/th04/maine.exe",
        "map": "obj/th04/maine.map",
        "old_obj": r"obj\th04\mainemdata.obj",
        "new_objs": r"obj\th04\mndp91.obj obj\th04\b_data.obj obj\th04\mnds91.obj",
    },
}

OP_PRE = r'''\t.386
\t.model use16 large _TEXT
include ReC98.inc
public pfint21_entries, pfint21_pf, pfint21_handle, parfilename
public trapezoid_hmask, header, linebyte
include th02/snd/snd.inc
include th04/th04.inc
\t.data
include libs/master.lib/wordmask[data].asm
include libs/master.lib/mem[data].asm
include libs/master.lib/super_entry_bfnt[data].asm
include libs/master.lib/superpa[data].asm
include libs/master.lib/respal_exist[data].asm
include libs/master.lib/draw_trapezoid[data].asm
include th02/formats/pfopen[data].asm
include libs/master.lib/bgm_timerhook[data].asm
\t.data?
include libs/master.lib/vsync[bss].asm
include libs/master.lib/mem[bss].asm
include libs/master.lib/superpa[bss].asm
include libs/master.lib/super_put_rect[bss].asm
include th01/hardware/vram_planes[bss].asm
include libs/master.lib/pfint21[bss].asm
include th02/formats/pi_slots[bss].asm
include th03/formats/hfliplut[bss].asm
include th04/snd/interrupt[bss].asm
\tend
'''
OP_POST = r'''\t.386
\t.model use16 large _TEXT
include ReC98.inc
include th02/snd/snd.inc
include th04/th04.inc
\t.data
include th04/snd/se_priority[data].asm
include th04/snd/snd[data].asm
\t\tdb 0
\t.data?
include th02/snd/load[bss].asm
include th04/mem[bss].asm
include th04/hardware/input[bss].asm
public _egcrect_w
_egcrect_w\tdw ?
include th04/formats/cdg[bss].asm
\textern _resident:dword
\tend
'''
MAINE_PRE = r'''\t.386
\t.model use16 large _TEXT
include ReC98.inc
public pfint21_entries, pfint21_pf, pfint21_handle, parfilename
public header
include th02/snd/snd.inc
include th04/th04.inc
\t.data
include libs/master.lib/wordmask[data].asm
include libs/master.lib/mem[data].asm
include libs/master.lib/super_entry_bfnt[data].asm
include libs/master.lib/superpa[data].asm
include th02/formats/pfopen[data].asm
include libs/master.lib/bgm_timerhook[data].asm
\t.data?
include libs/master.lib/vsync[bss].asm
include libs/master.lib/mem[bss].asm
include libs/master.lib/superpa[bss].asm
include th01/hardware/vram_planes[bss].asm
include libs/master.lib/pfint21[bss].asm
include th02/formats/pi_slots[bss].asm
include th03/formats/hfliplut[bss].asm
include th04/snd/interrupt[bss].asm
\tend
'''
MAINE_POST = r'''\t.386
\t.model use16 large _TEXT
include ReC98.inc
include th02/snd/snd.inc
include th04/th04.inc
\t.data
include th04/snd/se_priority[data].asm
include th04/formats/cdg_put_plane[data].asm
include th04/snd/snd[data].asm
\t\tdb 0
\tend
'''


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"; parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="historical-bdata-v491-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE): raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True); return out


def extract_bdata(out: Path) -> Path:
    if sha(ARCHIVE) != ARCHIVE_SHA or sha(RUNNER) != RUNNER_SHA or sha(TLIB) != TLIB_SHA:
        raise ValueError("historical archive/tool identity drift")
    work = out / "archive"; work.mkdir(); shutil.copy2(ARCHIVE, work / "masters.lib")
    (work / "BD.RSP").write_text("*b_data\n")
    p = run_tlib(work, "masters.lib", "@BD.RSP")
    (out / "extract-b_data.log").write_text(p.stdout+p.stderr)
    obj = work / "b_data.OBJ"
    if p.returncode or not obj.is_file() or obj.stat().st_size != BDATA_SIZE or sha(obj) != BDATA_SHA256:
        raise ValueError("historical b_data extraction/identity drift")
    recs=parse_omf(obj.read_bytes()); segs=segment_table(recs); data=data_records(recs,segs)
    bss=next(x for x in segs if x['name']=='_BSS')
    if bss['length'] != 0xC6 or data['_BSS']:
        raise ValueError("historical b_data BSS structure drift")
    return obj


def prepare(work: Path, art: str, bdata: Path, output: Path, label: str) -> None:
    cfg=BASE[art]
    if sha(work/cfg['exe']) != cfg['exe_sha256'] or sha(work/cfg['map']) != cfg['map_sha256']:
        raise ValueError(f"{label}/{art}: v489 source identity drift")
    if art=='op':
        (work/'th04_op_master_data_pre_v491.asm').write_text(OP_PRE.replace('\\t','\t'))
        (work/'th04_op_master_data_post_v491.asm').write_text(OP_POST.replace('\\t','\t'))
        tasm(work,output,f'{label}-op-pre','th04_op_master_data_pre_v491.asm','opdp91.obj')
        tasm(work,output,f'{label}-op-post','th04_op_master_data_post_v491.asm','opds91.obj')
    else:
        (work/'th04_maine_master_data_pre_v491.asm').write_text(MAINE_PRE.replace('\\t','\t'))
        (work/'th04_maine_master_data_post_v491.asm').write_text(MAINE_POST.replace('\\t','\t'))
        tasm(work,output,f'{label}-maine-pre','th04_maine_master_data_pre_v491.asm','mndp91.obj')
        tasm(work,output,f'{label}-maine-post','th04_maine_master_data_post_v491.asm','mnds91.obj')
    shutil.copy2(bdata, work/'obj/th04/b_data.obj')
    rsp=work/cfg['response']; text=rsp.read_text()
    if text.count(cfg['old_obj'])!=1: raise ValueError(f"{label}/{art}: response anchor drift")
    rsp.write_text(text.replace(cfg['old_obj'],cfg['new_objs'],1))


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--op-source-dir',type=Path,required=True); ap.add_argument('--maine-source-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path)
    args=ap.parse_args(); op_source=args.op_source_dir.resolve(); maine_source=args.maine_source_dir.resolve(); out=output_dir(args.output_dir)
    bdata=extract_bdata(out)
    builds={}
    for label in ('a','b'):
        builds[label]={}
        for art,source in (('op',op_source),('maine',maine_source)):
            work=out/label/art/'source'; shutil.copytree(source,work,symlinks=True); cfg=BASE[art]
            baseline=parse_mz((work/cfg['exe']).read_bytes()); baseline_sites=[r.linear for r in baseline.relocations]
            prepare(work,art,bdata,out,label)
            exe=work/cfg['exe']; mp=work/cfg['map']; exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
            run_checked(['wine',str(RUNNER),'-e','-x','tlink',('@'+cfg['response'].replace('/','\\'))],work,out/f'link-{label}-{art}.log')
            raw=exe.read_bytes(); mz=parse_mz(raw); sites=[r.linear for r in mz.relocations]
            if sha(exe)!=cfg['exe_sha256'] or len(raw)!=cfg['file_size']:
                raise ValueError(f"{label}/{art}: historical b_data boundary changed EXE identity/extent")
            if mz.program_image != baseline.program_image or sites != baseline_sites:
                raise ValueError(f"{label}/{art}: program/relocation drift")
            if len(raw)-mz.header.header_size != cfg['load_size'] or mz.header.minimum_extra_allocation != cfg['minalloc']:
                raise ValueError(f"{label}/{art}: load/minalloc drift")
            builds[label][art]={
                'exe_sha256':sha(exe),'map_sha256':sha(mp),'file_size':len(raw),'load_image_bytes':len(raw)-mz.header.header_size,
                'minalloc':mz.header.minimum_extra_allocation,'program_image_sha256':hashlib.sha256(mz.program_image).hexdigest(),
                'relocation_count':len(sites),'relocation_table_unchanged':sites==baseline_sites,
            }
    for art in ('op','maine'):
        for key in builds['a'][art]:
            if builds['a'][art][key] != builds['b'][art][key]: raise ValueError(f'A/B {art} {key} differs')
    receipt={
        'schema_version':1,'observed_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'claim_scope':'TH04 OP/MAINE historical MASTER b_data physical-object T-extent negative replay',
        'historical_b_data_sha256':BDATA_SHA256,'historical_b_data_bss_length':0xC6,'historical_b_data_bss_has_data_records':False,
        'builds':builds,
        'observed_effect':(
            'Replacing the reconstructed inline MASTER BGM data/BSS fragments by the independently attested historical masters.lib b_data.OBJ, while splitting the surrounding master data-tail into pre/post objects so both _DATA and _BSS contribution order remain identical, produces byte-identical v489 OP and MAINE EXEs. File size, load-image extent, minalloc, program bytes, and relocation tables are unchanged. Therefore the real b_data physical library-member boundary alone does not create the target-attested T extent.'),
        'limit':(
            'This closes only the historical b_data member-boundary hypothesis. It does not exclude another historical object containing initialized data in a BSS-class segment, a different linker version, or a post-link transform. The target T extent remains unresolved.'),
    }
    rp=out/'receipt.json'; rp.write_text(json.dumps(receipt,indent=2)+'\n'); print(json.dumps({'receipt':str(rp),'receipt_sha256':sha(rp),'op_unchanged':True,'maine_unchanged':True},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
