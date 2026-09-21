#!/usr/bin/env python3
"""Replay the OP/MAINE master.lib OMF-boundary hypothesis on a frozen v214 overlay.

The input must be an unchanged v214-style ReC98-overlay build tree whose OP and
MAINE candidates match the hashes recorded by the v218 payload frontier.  The
probe copies that tree twice, changes only assembler translation-unit topology
and cross-object symbol visibility, rebuilds with the pinned toolchain, and
compares the resulting unpacked payloads.  It never inserts target bytes or
explicit alignment padding and grants no exact/source-origin credit.
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
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
TEMPLATES = {
    "th04_op_master_mid.asm": ROOT / "config/replay/th04_op_master_mid_v400.asm.in",
    "th04_op_master_tail.asm": ROOT / "config/replay/th04_op_master_tail_v400.asm.in",
    "th04_maine_master_mid.asm": ROOT / "config/replay/th04_maine_master_mid_v400.asm.in",
    "th04_maine_master_tail.asm": ROOT / "config/replay/th04_maine_master_tail_v400.asm.in",
}
BASELINE = {
    "Tupfile.lua": "abe0ec2beebfcd3b0b9e6dbf9d9891cebf70c07b322e3f390ad5628071c5ac66",
    "th04_op.asm": "262e0e998ee8ee0b28ea171b665027c2de78093196ea11e12aad26529bc5f774",
    "th04_maine_master.asm": "a10ede2f3e0d33624e570357d028748cdefe4ca24c781b22eb944f4e9944037f",
    "bin/th04/op.exe": "cb9b1c6cbd6b2c7bad6763fabd106c3cf451b1c20efef0f1fcfd3e3a47c0cdaa",
    "bin/th04/maine.exe": "7e6b78861613cdd06d72e2f8584268444642b31abcc35d686c0ed1f4cc668f70",
    "obj/th04/op.map": "7762fdd9716251b15108b970ce7cf1e261405b7fa5a989ca2fad9086c3af35f9",
    "obj/th04/maine.map": "f7c418da780e5ed97f8a02de9a6e80b082a7833ed5cbd6aa48529ef5a19c484a",
}
EXPECTED_SPLIT = {
    "op": {
        "exe": "7d3e9887f633474278e89023d315858394b12527860ca5cbc2ecdbbd082bb60d",
        "map": "5f7066ef2505ba86202851969c5b39ccad2ec4bcbea91aa2b4b94f5b5960bc95",
        "diff_bytes": 5,
        "starts": [0xBFB7, 0xBFB9, 0xDE8B, 0xFB97],
    },
    "maine": {
        "exe": "98e1a1c270837d4c154fb9cacc3176fa95ff053ab215e84d9ee72d3c212e6779",
        "map": "36170e7b9c6fde7684905a0867616f0dcc7136200c6a7ef92d09ce9280cab015",
        "diff_bytes": 3,
        "starts": [0xD1D3, 0xE933],
    },
}
EXPECTED_BASELINE = {
    "op": {"diff_bytes": 7, "starts": [0x2D59, 0x34AF, 0xBFB7, 0xBFB9, 0xDE8B, 0xFB97]},
    "maine": {"diff_bytes": 5, "starts": [0x0CBD, 0x2D11, 0xD1D3, 0xE933]},
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected one transform anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


def op_split(source: Path) -> None:
    path = source / "th04_op.asm"
    text = path.read_text()
    anchor = "include th04/th04.inc\n"
    visibility = """

; Diagnostic visibility declarations; PUBLIC adds linkage metadata only.
public ResPalSeg, pfint21_entries, pfint21_pf, pfint21_handle, parfilename
public SOUND_I, SOUND_O, ClipYB_adr, trapezoid_hmask
public Machine_State, graph_VramSeg
; Diagnostic split externs: symbols emitted by later _TEXT contributions.
extrn SUPER_PUT:far, draw_trapezoid:near
"""
    text = replace_once(text, anchor, anchor + visibility, "OP visibility")
    first = text.index("include libs/master.lib/super_put.asm\n")
    last_line = "include libs/master.lib/graph_gaiji_putc.asm\n"
    last = text.index(last_line, first) + len(last_line)
    text = text[:first] + text[last:]
    path.write_text(text)


def maine_split(source: Path) -> None:
    path = source / "th04_maine_master.asm"
    text = path.read_text()
    anchor = "group_01 group MAINE_E_TEXT, CUTSCENE_TEXT, maine_01_TEXT\n"
    visibility = r'''

; Preserve TASM's monolithic same-segment FAR-call lowering across OMF objects.
purge nopcall
nopcall macro target
if LDATA
	nop
endif
	push cs
	call near ptr target
endm

; Diagnostic split visibility for data/BSS owned by this head object.
public Machine_State, graph_VramSeg
public pfint21_entries, pfint21_pf, pfint21_handle, parfilename
public mem_AllocID, pferrno, super_patdata, super_patsize
public EPSON_NOTES, IBMADSP, IBMAFNT, EXENTRY, BACKUP_MSEG, BFNT_HEADER2
public TextVramSeg, ClipYT_seg, graph_VramWords, ClipYT, graph_VramZoom
public ClipXR, graph_VramLines, ClipYB, ClipYH, TextShown
public PaletteTone, Palettes, PaletteNote, random_seed
public mem_EndMark, mem_TopSeg, mem_TopHeap, mem_MyOwn, mem_OutSeg, mem_FirstHole, mem_Reserve
public vsync_Delay, vsync_Count1, vsync_Count2, vsync_OldMask, vsync_OldVect
public vsync_delay_count, vsync_Proc
public super_buffer, super_patnum, super_charfree, header

; Code emitted by the following object contribution but called from this head.
extrn SMEM_RELEASE:near, SMEM_WGET:near, SUPER_ENTRY_PAT:near
extrn HMEM_FREE:near, HMEM_ALLOCBYTE:near
extrn VSYNC_WAIT:near, PALETTE_SHOW:near
'''
    text = replace_once(text, anchor, anchor + visibility, "MAINE visibility")
    first = text.index("include libs/master.lib/get_machine_98.asm\n")
    last_line = "include libs/master.lib/graph_gaiji_putc.asm\n"
    last = text.index(last_line, first) + len(last_line)
    text = text[:first] + text[last:]
    path.write_text(text)


def apply_split(source: Path) -> None:
    op_split(source)
    maine_split(source)
    for name, template in TEMPLATES.items():
        (source / name).write_bytes(template.read_bytes())
    tup = source / "Tupfile.lua"
    text = tup.read_text()
    text = replace_once(
        text,
        '\t"th04_op.asm",\n',
        '\t{ "th04_op.asm", o = "op.obj" },\n'
        '\t{ "th04_op_master_mid.asm", o = "opmmid.obj" },\n'
        '\t{ "th04_op_master_tail.asm", o = "opmtail.obj" },\n',
        "OP Tupfile",
    )
    text = replace_once(
        text,
        '\t{ "th04_maine_master.asm", o = "mainem.obj" },\n',
        '\t{ "th04_maine_master.asm", o = "mainem.obj" },\n'
        '\t{ "th04_maine_master_mid.asm", o = "mainemmid.obj" },\n'
        '\t{ "th04_maine_master_tail.asm", o = "mainemtail.obj" },\n',
        "MAINE Tupfile",
    )
    tup.write_text(text)


def compare(artifact: str, source: Path) -> dict[str, object]:
    short = artifact.removeprefix("th04-")
    command = [
        sys.executable, str(ROOT / "scripts/probes/compare_diet_payloads.py"), artifact,
        "--candidate", str(source / f"bin/th04/{short}.exe"),
        "--observation-dir", str(ROOT / f".analysis/reconstruction/v218-{artifact}-diet"),
        "--map", str(source / f"obj/th04/{short}.map"),
    ]
    done = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120, check=True)
    return json.loads(done.stdout)


def validate_comparison(label: str, result: dict[str, object], expected: dict[str, object]) -> None:
    if result["payload_differing_bytes"] != expected["diff_bytes"]:
        raise ValueError(f"{label}: unexpected differing-byte count {result['payload_differing_bytes']}")
    if result["relocation_multiset_exact"] is not True:
        raise ValueError(f"{label}: relocation multiset changed")
    if result["target_payload_size"] != result["candidate_payload_size"]:
        raise ValueError(f"{label}: payload size changed")
    starts = [item["start"] for item in result["payload_mismatch_runs"]]
    if starts != expected["starts"]:
        raise ValueError(f"{label}: unexpected mismatch starts {starts}")


def build(source: Path, log: Path) -> None:
    env = os.environ.copy()
    env.update({
        "WINEPREFIX": str(ROOT / ".analysis/toolchain/wineprefix"),
        "WINEDEBUG": "-all",
        "MSDOS_PATH": r"C:\TC4\BIN",
    })
    command = [
        "wine", "cmd", "/d", "/c",
        r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%&&set PROCESSOR_ARCHITECTURE=AMD64&&set PROCESSOR_ARCHITEW6432=AMD64&&build.bat",
    ]
    done = subprocess.run(command, cwd=source, env=env, capture_output=True, text=True, timeout=600)
    log.write_text(json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr)
    if done.returncode:
        raise RuntimeError(f"build failed; see {log}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True,
                        help="unchanged v214-style overlay build tree with v218 OP/MAINE candidates")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    if not source_dir.is_dir():
        parser.error("--source-dir must exist")
    if args.output_dir is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="master-object-split-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(PRIVATE):
            parser.error("--output-dir must be new and below .analysis")
        output.mkdir(parents=True)

    for rel, expected in BASELINE.items():
        path = source_dir / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"baseline identity failed: {rel}")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tool_ids = ("active-tasm32", "active-tlink")
    toolchain = {}
    for ident in tool_ids:
        item = next(x for x in surfaces if x["id"] == ident)
        path = ROOT / item["path"]
        if sha(path) != item["sha256"]:
            raise ValueError(f"toolchain identity failed: {ident}")
        toolchain[ident] = item["sha256"]

    baseline_results = {name: compare(f"th04-{name}", source_dir) for name in ("op", "maine")}
    for name, result in baseline_results.items():
        validate_comparison(f"baseline-{name}", result, EXPECTED_BASELINE[name])

    builds: dict[str, object] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source_dir, work, symlinks=True)
        apply_split(work)
        build(work, output / f"build-{label}.log")
        results = {name: compare(f"th04-{name}", work) for name in ("op", "maine")}
        identities = {}
        for name, result in results.items():
            validate_comparison(f"{label}-{name}", result, EXPECTED_SPLIT[name])
            exe = work / f"bin/th04/{name}.exe"
            map_path = work / f"obj/th04/{name}.map"
            expected = EXPECTED_SPLIT[name]
            if sha(exe) != expected["exe"] or sha(map_path) != expected["map"]:
                raise ValueError(f"{label}-{name}: split output identity drift")
            identities[name] = {"exe_sha256": sha(exe), "map_sha256": sha(map_path), "comparison": result}
        builds[label] = identities

    for name in ("op", "maine"):
        for key in ("exe_sha256", "map_sha256"):
            if builds["a"][name][key] != builds["b"][name][key]:
                raise ValueError(f"A/B {name} {key} is not deterministic")
        left = dict(builds["a"][name]["comparison"])
        right = dict(builds["b"][name]["comparison"])
        left.pop("candidate_path", None)
        right.pop("candidate_path", None)
        if left != right:
            raise ValueError(f"A/B {name} payload Oracle is not deterministic")

    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 OP/MAINE master.lib OMF object-boundary diagnostic; no exact promotion",
        "baseline": {"identity": BASELINE, "comparisons": baseline_results},
        "templates": {str(path.relative_to(ROOT)): sha(path) for path in TEMPLATES.values()},
        "toolchain": toolchain,
        "builds": builds,
        "observed_effect": {
            "op_payload_differences": "7 -> 5; 0x2D59 and 0x34AF alignment mismatches removed",
            "maine_payload_differences": "5 -> 3; 0x0CBD and 0x2D11 alignment mismatches removed",
            "relocation_multisets": "unchanged and target-equal for both artifacts",
        },
        "limit": "Only object topology and cross-object visibility are tested. Packed-file equality, relocation order, remaining opcode/data mismatches, source origin, and authored exactness are not established.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "receipt_sha256": sha(receipt_path), "result": receipt["observed_effect"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
