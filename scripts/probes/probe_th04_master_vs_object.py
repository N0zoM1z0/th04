#!/usr/bin/env python3
"""Replay the TH04 MASTER.LIB VS.OBJ data-owner hypothesis on v400 topology.

The probe starts from the hash-pinned v400 OP/MAINE object-topology candidate,
extracts VS.OBJ from the independent historical masters.lib support archive,
splits the surrounding DATA/BSS contributions without adding padding bytes,
and links the historical library object between the head and tail contributions.
It also assembles the same maintained vs[data]/vs[bss] source with the pinned
TASM 5.0 control to preserve the producer-version differential. No target byte
is copied into source or an object, and no authored-source exactness is granted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from probe_th04_master_object_split import build, compare, sha

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
ARCHIVE = ROOT / "_reference/ReC98/bin/masters.lib"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
TLIB = ROOT / ".analysis/toolchain/wineprefix/drive_c/TC4/BIN/TLIB.EXE"
TASM = ROOT / ".analysis/toolchain/wineprefix/drive_c/TASM50/bin/TASM32.EXE"
TEMPLATES = {
    "th04_op_master_data_tail.asm": ROOT / "config/replay/th04_op_master_data_tail_v401.asm.in",
    "th04_maine_master_data_tail.asm": ROOT / "config/replay/th04_maine_master_data_tail_v401.asm.in",
}

BASELINE = {
    "Tupfile.lua": "009c7d5595fc2c15d0420cb759171f9196043179d6a68468f958c7cfcd5ffe8a",
    "th04_op.asm": "678fbd95c31c02f81dd557cbd688c7607919bedfbf0780d0755c666cae23173a",
    "th04_op_master_mid.asm": "7bf1bc2d5532727862f68599ee79de925e889027c47a5ff4e2d6917478974e35",
    "th04_op_master_tail.asm": "d1c47b1086a26ff9b9fca8686bcbd73b86d405a5a4f4c1874e3939f94ab3931b",
    "th04_maine_master.asm": "e34c8dececf505f325b4c8b2f7365c2661a03ef29341f764bd60f61ee45cf1d5",
    "th04_maine_master_mid.asm": "1e4df0e810dfcf16c234cef439cd307e7d0bf0d5af343294b5cfed8cab461a0d",
    "th04_maine_master_tail.asm": "986e1447afb01310bf7e7a4f19aea5fd586f6971b3cb27dadf9f82639ae169d3",
    "bin/th04/op.exe": "7d3e9887f633474278e89023d315858394b12527860ca5cbc2ecdbbd082bb60d",
    "bin/th04/maine.exe": "98e1a1c270837d4c154fb9cacc3176fa95ff053ab215e84d9ee72d3c212e6779",
    "obj/th04/op.map": "5f7066ef2505ba86202851969c5b39ccad2ec4bcbea91aa2b4b94f5b5960bc95",
    "obj/th04/maine.map": "36170e7b9c6fde7684905a0867616f0dcc7136200c6a7ef92d09ce9280cab015",
}
ARCHIVE_SHA = "6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6"
TLIB_SHA = "2d65d72b8800f7f3d4716218ed508bdd198e73b5f96f4830c1e14d1bb56546e2"
TASM_SHA = "ba50fe547863b96242d98cff54cdf95ab268a8682395afad172eedbfc46c5b26"
VS_OBJ_SHA = "3bb280d22f01581b08c4fed605f09c198f54cde8b9b6767a4fef5a09953a8318"
EXPECTED = {
    "op": {
        "baseline_diff": 5,
        "baseline_starts": [0xBFB7, 0xBFB9, 0xDE8B, 0xFB97],
        "split_diff": 4,
        "split_starts": [0xBFB7, 0xBFB9, 0xDE8B],
        "exe": "3000d2c113cc4a7eb4d2f79cdb9c5cebbec1d7180e699525dafe86fbb8af3d5a",
        "map": "08ab21543cc5e7c58e29a566538011aab3514adb5d3193216df7e44d671b0cf3",
    },
    "maine": {
        "baseline_diff": 3,
        "baseline_starts": [0xD1D3, 0xE933],
        "split_diff": 2,
        "split_starts": [0xD1D3],
        "exe": "8b4a3bb3e6985f729113967398b35cff2c9c4d32860b9034fc84b839e8862553",
        "map": "b85de8ddf0ec5ec17bc8a4554ddbee8903629877e71a45e92fd58f719f336217",
    },
}


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected one anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


def extract_vs(output: Path) -> Path:
    if sha(ARCHIVE) != ARCHIVE_SHA:
        raise ValueError("masters.lib identity failed")
    if sha(TLIB) != TLIB_SHA:
        raise ValueError("TLIB identity failed")
    extract = output / "archive-extract"
    extract.mkdir()
    shutil.copy2(ARCHIVE, extract / "masters.lib")
    (extract / "EXTRACT.RSP").write_text("*vs\n")
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"), WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN")
    done = subprocess.run(
        ["wine", str(RUNNER), "-e", "-x", "tlib", "masters.lib", "@EXTRACT.RSP"],
        cwd=extract, env=env, capture_output=True, text=True, timeout=120,
    )
    (extract / "tlib.log").write_text(done.stdout + done.stderr)
    if done.returncode:
        raise RuntimeError("TLIB extraction failed")
    vs = extract / "vs.OBJ"
    if not vs.is_file() or sha(vs) != VS_OBJ_SHA:
        raise ValueError("historical VS.OBJ identity failed")
    data = vs.read_bytes()
    # The historical object independently preserves the eight-byte VS _DATA
    # contribution, including its TASM-3-era trailing 0x90 alignment byte.
    if bytes.fromhex("0000000000000090") not in data:
        raise ValueError("historical VS.OBJ no longer contains the expected VS data contribution")
    return vs


def split_head(path: Path) -> None:
    text = path.read_text()
    data_marker = "\n\t.data\n\n"
    bss_marker = "\n\t.data?\n\n"
    ds = text.index(data_marker)
    bs = text.index(bss_marker, ds)
    end = text.rfind("\n\tend")
    if end < bs:
        end = text.rfind("\n\t\tend")
    if end < bs:
        raise ValueError(f"{path.name}: end anchor missing")
    data = text[ds + len(data_marker):bs]
    bss = text[bs + len(bss_marker):end]
    vs_data = "include libs/master.lib/vs[data].asm\n"
    vs_bss = "include libs/master.lib/vs[bss].asm\n"
    if data.count(vs_data) != 1 or bss.count(vs_bss) != 1:
        raise ValueError(f"{path.name}: VS ownership anchors changed")
    head_data = data[:data.index(vs_data)]
    head_bss = bss[:bss.index(vs_bss)]
    path.write_text(text[:ds] + data_marker + head_data + bss_marker + head_bss + text[end:])


def apply_op(work: Path) -> None:
    path = work / "th04_op.asm"
    text = path.read_text()
    old = '''; Diagnostic visibility declarations; PUBLIC adds linkage metadata only.\npublic ResPalSeg, pfint21_entries, pfint21_pf, pfint21_handle, parfilename\npublic SOUND_I, SOUND_O, ClipYB_adr, trapezoid_hmask\npublic Machine_State, graph_VramSeg\n'''
    new = '''; Diagnostic visibility declarations; PUBLIC adds linkage metadata only.\npublic SOUND_I, SOUND_O, ClipYB_adr, ResPalSeg\npublic Machine_State, graph_VramSeg\n; Data/BSS now owned by historical VS.OBJ or the following data-tail object.\nextrn pfint21_entries:word, pfint21_pf:word, pfint21_handle:word\nextrn parfilename:byte, trapezoid_hmask:word\nextrn mem_AllocID:word, mem_EndMark:word, mem_TopSeg:word, mem_TopHeap:word\nextrn mem_MyOwn:word, mem_OutSeg:word, mem_FirstHole:word, mem_Reserve:word\nextrn vsync_Delay:word, vsync_Count1:word, vsync_Count2:word, vsync_OldMask:byte\nextrn vsync_OldVect:dword, vsync_delay_count:word, vsync_Proc:dword\nextrn super_buffer:word, super_patnum:word, super_charfree:word\nextrn super_patsize:word, super_patdata:word\nextrn header:BFNT_HEADER, linebyte:word\nextrn _pi_buffers:dword, _pi_headers:PiHeader:6, _key_det:word\n; These two includes contain declarations/types only and allocate no bytes.\ninclude th04/zunsoft[data].asm\ninclude th04/zunsoft[bss].asm\n'''
    path.write_text(replace_once(text, old, new, "OP visibility"))
    split_head(path)
    (work / "th04_op_master_data_tail.asm").write_bytes(TEMPLATES["th04_op_master_data_tail.asm"].read_bytes())


def apply_maine(work: Path) -> None:
    path = work / "th04_maine_master.asm"
    text = path.read_text()
    text = replace_once(text, "public pfint21_entries, pfint21_pf, pfint21_handle, parfilename\n",
                        "extrn pfint21_entries:word, pfint21_pf:word, pfint21_handle:word, parfilename:byte\n", "MAINE pfint")
    text = replace_once(text, "public mem_AllocID, pferrno, super_patdata, super_patsize\n",
                        "public pferrno\nextrn mem_AllocID:word, super_patdata:word, super_patsize:word\n", "MAINE mem")
    text = replace_once(text, "public mem_EndMark, mem_TopSeg, mem_TopHeap, mem_MyOwn, mem_OutSeg, mem_FirstHole, mem_Reserve\n",
                        "extrn mem_EndMark:word, mem_TopSeg:word, mem_TopHeap:word, mem_MyOwn:word\nextrn mem_OutSeg:word, mem_FirstHole:word, mem_Reserve:word\n", "MAINE mem bss")
    text = replace_once(text, "public vsync_Delay, vsync_Count1, vsync_Count2, vsync_OldMask, vsync_OldVect\n",
                        "extrn vsync_Delay:word, vsync_Count1:word, vsync_Count2:word, vsync_OldMask:byte\nextrn vsync_OldVect:dword\n", "MAINE VS")
    text = replace_once(text, "public vsync_delay_count, vsync_Proc\n",
                        "extrn vsync_delay_count:word, vsync_Proc:dword\n", "MAINE vsync")
    text = replace_once(text, "public super_buffer, super_patnum, super_charfree, header\n",
                        "extrn super_buffer:word, super_patnum:word, super_charfree:word\nextrn header:BFNT_HEADER\n", "MAINE super")
    path.write_text(text)
    split_head(path)
    (work / "th04_maine_master_data_tail.asm").write_bytes(TEMPLATES["th04_maine_master_data_tail.asm"].read_bytes())


def apply_tup(work: Path) -> None:
    path = work / "Tupfile.lua"
    text = path.read_text()
    text = replace_once(
        text,
        '\t{ "th04_op.asm", o = "op.obj" },\n\t{ "th04_op_master_mid.asm", o = "opmmid.obj" },\n',
        '\t{ "th04_op.asm", o = "op.obj" },\n\t"vsorig.obj",\n\t{ "th04_op_master_data_tail.asm", o = "opmdata.obj" },\n\t{ "th04_op_master_mid.asm", o = "opmmid.obj" },\n',
        "OP link order",
    )
    text = replace_once(
        text,
        '\t{ "th04_maine_master.asm", o = "mainem.obj" },\n\t{ "th04_maine_master_mid.asm", o = "mainemmid.obj" },\n',
        '\t{ "th04_maine_master.asm", o = "mainem.obj" },\n\t"vsorig.obj",\n\t{ "th04_maine_master_data_tail.asm", o = "mainemdata.obj" },\n\t{ "th04_maine_master_mid.asm", o = "mainemmid.obj" },\n',
        "MAINE link order",
    )
    path.write_text(text)


def compile_tasm5_control(work: Path, output: Path) -> dict[str, str]:
    if sha(TASM) != TASM_SHA:
        raise ValueError("TASM32 identity failed")
    source = work / "VSCTRL.ASM"
    obj = work / "VSCTRL.OBJ"
    source.write_text('''.386\n.model use16 large\ninclude ReC98.inc\n_TEXT segment word public 'CODE' use16\n_TEXT ends\n.data\ninclude libs/master.lib/vs[data].asm\n.data?\ninclude libs/master.lib/vs[bss].asm\nend\n''')
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"), WINEDEBUG="-all")
    done = subprocess.run(["wine", str(TASM), "/m", "/mx", "/kh32768", "/t", "VSCTRL.ASM,VSCTRL.OBJ"], cwd=work, env=env, capture_output=True, text=True, timeout=120)
    (output / "tasm5-control.log").write_text(done.stdout + done.stderr)
    if done.returncode or not obj.is_file():
        raise RuntimeError("TASM5 VS control failed")
    data = obj.read_bytes()
    if bytes.fromhex("0000000000000000") not in data:
        raise ValueError("TASM5 VS control no longer contains zero-filled VS data")
    return {"source_sha256": sha(source), "object_sha256": sha(obj)}


def validate_result(label: str, result: dict[str, object], diff: int, starts: list[int]) -> None:
    if result["payload_differing_bytes"] != diff:
        raise ValueError(f"{label}: unexpected differing-byte count")
    if [item["start"] for item in result["payload_mismatch_runs"]] != starts:
        raise ValueError(f"{label}: mismatch starts changed")
    if result["relocation_multiset_exact"] is not True:
        raise ValueError(f"{label}: relocation multiset changed")
    if result["target_payload_size"] != result["candidate_payload_size"]:
        raise ValueError(f"{label}: payload length changed")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source_dir = args.source_dir.resolve()
    if not source_dir.is_dir():
        ap.error("--source-dir must exist")
    if args.output_dir is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="master-vs-object-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(PRIVATE):
            ap.error("--output-dir must be new and below .analysis")
        output.mkdir(parents=True)

    for rel, expected in BASELINE.items():
        path = source_dir / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"v400 baseline identity failed: {rel}")
    baseline = {name: compare(f"th04-{name}", source_dir) for name in ("op", "maine")}
    for name, result in baseline.items():
        validate_result(f"baseline-{name}", result, EXPECTED[name]["baseline_diff"], EXPECTED[name]["baseline_starts"])

    vs = extract_vs(output)
    builds = {}
    control = None
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source_dir, work, symlinks=True)
        shutil.copy2(vs, work / "vsorig.obj")
        apply_op(work)
        apply_maine(work)
        apply_tup(work)
        if label == "a":
            control = compile_tasm5_control(work, output)
        build(work, output / f"build-{label}.log")
        results = {name: compare(f"th04-{name}", work) for name in ("op", "maine")}
        identities = {}
        for name, result in results.items():
            expected = EXPECTED[name]
            validate_result(f"{label}-{name}", result, expected["split_diff"], expected["split_starts"])
            exe = work / f"bin/th04/{name}.exe"
            map_path = work / f"obj/th04/{name}.map"
            if sha(exe) != expected["exe"] or sha(map_path) != expected["map"]:
                raise ValueError(f"{label}-{name}: output identity drift")
            identities[name] = {"exe_sha256": sha(exe), "map_sha256": sha(map_path), "comparison": result}
        builds[label] = identities

    for name in ("op", "maine"):
        for key in ("exe_sha256", "map_sha256"):
            if builds["a"][name][key] != builds["b"][name][key]:
                raise ValueError(f"A/B {name} {key} differs")
        left = dict(builds["a"][name]["comparison"]); left.pop("candidate_path", None)
        right = dict(builds["b"][name]["comparison"]); right.pop("candidate_path", None)
        if left != right:
            raise ValueError(f"A/B {name} payload Oracle differs")

    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 OP/MAINE historical MASTER.LIB VS.OBJ physical ownership; no authored exact promotion",
        "baseline": {"identity": BASELINE, "comparisons": baseline},
        "masters_lib_sha256": ARCHIVE_SHA,
        "tlib_sha256": TLIB_SHA,
        "historical_vs_obj_sha256": VS_OBJ_SHA,
        "historical_vs_data_tail": "90",
        "tasm5_control": control,
        "templates": {str(path.relative_to(ROOT)): sha(path) for path in TEMPLATES.values()},
        "builds": builds,
        "observed_effect": {
            "op_payload_differences": "5 -> 4; DATA mismatch at 0xFB97 removed",
            "maine_payload_differences": "3 -> 2; DATA mismatch at 0xE933 removed",
            "relocation_multisets": "unchanged and target-equal for both artifacts",
        },
        "limit": "This establishes library-object physical ownership for the two DATA bytes in the diagnostic unpacked payload. It does not make OP/MAINE packed files exact, does not promote library bytes into authored progress, and does not resolve the remaining op_music or snd_load instruction encodings.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "receipt_sha256": sha(receipt_path), "result": receipt["observed_effect"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
