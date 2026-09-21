#!/usr/bin/env python3
"""Recover TH04 OP zunsoft_palette_update_and_show() as natural TC86 C++."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_master_object_split import build, sha  # noqa: E402
from probe_th04_op_music_segment_order import BASE as V402_BASE, apply_split as apply_v427  # noqa: E402
from probe_th04_op_relocation_topology_v461 import apply_v461  # noqa: E402
from probe_th04_zunsoft_pyro_cpp_v463 import (  # noqa: E402
    V461_EXE, V461_MAP, TARGET_RESTORED_SHA,
    apply_cpp_source, digest, outdir, rebuild_v463_op, segment_bytes, swap_source_order,
)
from probe_th04_zunsoft_update_cpp_v464 import apply_update_source  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_zunsoft_palette_v465.cpp.in"
TEMPLATE_SHA = "b2879df2405fdf493e3bdd7ff5fc8700a4bd0c5aa3d19bdd1d82f707a67963ce"
PALETTE_LOAD = 0xBBF4
PALETTE_OFFSET = 0x1AF
PALETTE_SIZE = 0x41
CPP_OWNER_SIZE = 0x1F0
ASM_TAIL_SIZE = 0x2A0
FINAL_EXE = "1e87ecbf564a5ef522c52fc94370ff78f2d917d084fafd249c33ebf91228819b"
FINAL_MAP = "f026e0bc299a49d9ffd376d51683085a5f8bc5182a7a73e4f3249a03d7ca62bd"
PALETTE_SHA = "08fc22f1c1142e43cb2ce54b09a86b1472f5788c1287637847f6b0e7ee90e04c"
CPP_SEGMENT_SITES = [0xBC2D, 0xBBE2, 0xBBC3, 0xBBA5, 0xBB7C, 0xBB5E, 0xBB3A, 0xBAA0, 0xBA8F]


def apply_palette_source(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v465 palette template identity drift")
    source = work / "th04/op/zunsoft.cpp"
    text = source.read_text()
    declaration = "void zunsoft_palette_update_and_show(int tone)\n;"
    if text.count(declaration) != 1:
        raise ValueError("v465 palette declaration drift")
    source.write_text(text.replace(declaration, TEMPLATE.read_text().rstrip(), 1))


def apply_asm_tail(work: Path) -> None:
    original = (work / "th04/zunsoft.asm").read_bytes()
    marker = b"public @zunsoft_animate$qv\r\n"
    if marker not in original:
        marker = b"public @zunsoft_animate$qv\n"
    if marker not in original:
        raise ValueError("v465 animate tail marker drift")
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    tail = (
        b"extern ZUNSOFT_PYRO_NEW:near" + newline
        + b"extern ZUNSOFT_UPDATE_AND_RENDER:near" + newline
        + b"extern ZUNSOFT_PALETTE_UPDATE_AND_SHOW:near" + newline
        + original[original.index(marker):]
    )
    (work / "th04_zunsoft_tail.asm").write_bytes(tail)
    wrapper = work / "th04_op_music_master.asm"
    data = wrapper.read_bytes()
    needle = b"include th04/zunsoft.asm"
    if data.count(needle) != 1:
        raise ValueError("v465 wrapper include drift")
    wrapper.write_bytes(data.replace(needle, b"include th04_zunsoft_tail.asm", 1))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source = args.source_dir.resolve()
    target_path = args.target_restored.resolve()
    output = outdir(args.output_dir)

    for rel, expected in V402_BASE.items():
        path = source / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"v402 source identity drift: {rel}")
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("v228 target-restored identity drift")
    target = parse_mz(target_path.read_bytes())
    target_sites = [r.linear for r in target.relocations]
    target_palette = target.program_image[PALETTE_LOAD:PALETTE_LOAD + PALETTE_SIZE]
    if digest(target_palette) != PALETTE_SHA:
        raise ValueError("target palette body identity drift")

    builds = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        apply_v427(work)
        apply_v461(work)
        build(work, output / f"baseline-build-{label}.log")
        baseline_exe = work / "bin/th04/op.exe"
        baseline_map = work / "obj/th04/op.map"
        if sha(baseline_exe) != V461_EXE or sha(baseline_map) != V461_MAP:
            raise ValueError(f"{label}: v461 baseline identity drift")
        baseline = parse_mz(baseline_exe.read_bytes())
        baseline_program = baseline.program_image
        baseline_sites = [r.linear for r in baseline.relocations]
        full_asm_code = segment_bytes(work / "obj/th04/opmusicm.obj", "OP_MUSIC_TEXT")

        apply_cpp_source(work)
        apply_update_source(work)
        apply_palette_source(work)
        apply_asm_tail(work)
        swap_source_order(work)
        rebuild_v463_op(work, output, label)

        exe = work / "bin/th04/op.exe"
        map_path = work / "obj/th04/op.map"
        cpp_obj = work / "obj/th04/zunsoft.obj"
        tail_obj = work / "obj/th04/opmusicm.obj"
        image = parse_mz(exe.read_bytes())
        sites = [r.linear for r in image.relocations]
        if image.program_image != baseline_program:
            raise ValueError(f"{label}: v465 changed linked OP program bytes")
        if image.program_image[PALETTE_LOAD:PALETTE_LOAD + PALETTE_SIZE] != target_palette:
            raise ValueError(f"{label}: palette linked body is not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation multiset drift")
        ordered = sum(a != b for a, b in zip(sites, target_sites))
        if ordered != 105:
            raise ValueError(f"{label}: ordered frontier drift: {ordered}")
        if sites[271:280] != CPP_SEGMENT_SITES:
            raise ValueError(f"{label}: three-function segment-fixup order drift")

        cpp_code = segment_bytes(cpp_obj, "OP_MUSIC_TEXT")
        if len(cpp_code) != CPP_OWNER_SIZE:
            raise ValueError(f"{label}: C++ owner size drift: {len(cpp_code)}")
        palette_code = cpp_code[PALETTE_OFFSET:PALETTE_OFFSET + PALETTE_SIZE]
        if palette_code != full_asm_code[PALETTE_OFFSET:PALETTE_OFFSET + PALETTE_SIZE]:
            raise ValueError(f"{label}: palette raw OMF code is not exact")
        tail_size = len(segment_bytes(tail_obj, "OP_MUSIC_TEXT"))
        if tail_size != ASM_TAIL_SIZE:
            raise ValueError(f"{label}: animate tail size drift: {tail_size}")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: v465 final identity drift")

        changed = [i for i, (a, b) in enumerate(zip(baseline_sites, sites)) if a != b]
        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "palette_linked_sha256": digest(image.program_image[PALETTE_LOAD:PALETTE_LOAD + PALETTE_SIZE]),
            "palette_raw_sha256": digest(palette_code),
            "cpp_owner_code_size": len(cpp_code),
            "asm_tail_code_size": tail_size,
            "ordered_relocation_mismatches": ordered,
            "relocation_indices_changed_vs_v461": changed,
            "cpp_owner_segment_sites": sites[271:280],
        }
    if builds["a"] != builds["b"]:
        raise ValueError("A/B v465 results differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP zunsoft_palette_update_and_show natural-C++ linked exact replay; no packed-file promotion",
        "source_baseline": V402_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "The 0x41-byte zunsoft_palette_update_and_show body is raw OMF CODE exact on the first natural TC86 C++ attempt and links at the target entry without changing any OP program byte. With v463/v464, the first 0x1F0 bytes of OP_MUSIC_TEXT are now one TC86 C++ owner and its nine segment relocations are emitted in descending code-address order. Only the final 0x2A0 zunsoft_animate body remains in TASM."
        ),
        "limit": (
            "This packet establishes the third linked-exact natural C++ function. The full 35-entry OP-music relocation block cannot close until zunsoft_animate is recovered into the same TC86 owner."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "palette_linked_exact": True,
        "palette_size": PALETTE_SIZE,
        "ordered_relocation_mismatches": 105,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
