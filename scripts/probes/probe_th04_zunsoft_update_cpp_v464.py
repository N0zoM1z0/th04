#!/usr/bin/env python3
"""Recover TH04 OP zunsoft_update_and_render() as natural TC86 C++ and relink it exact."""
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

from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_master_object_split import build, sha  # noqa: E402
from probe_th04_op_music_segment_order import BASE as V402_BASE, apply_split as apply_v427  # noqa: E402
from probe_th04_op_relocation_topology_v461 import apply_v461  # noqa: E402
from probe_th04_zunsoft_pyro_cpp_v463 import (  # noqa: E402
    V461_EXE,
    V461_MAP,
    TARGET_RESTORED_SHA,
    PYRO_LOAD,
    PYRO_SIZE,
    apply_cpp_source,
    digest,
    outdir,
    rebuild_v463_op,
    segment_bytes,
    swap_source_order,
)
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_zunsoft_update_v464.cpp.in"
TEMPLATE_SHA = "9e19013f5cf4e4239a271441b25df8024e28c7bfd67e144d23f44d2a1c7cad77"
UPDATE_LOAD = 0xBAC9
UPDATE_OFFSET = 0x84
UPDATE_SIZE = 0x12B
CPP_OWNER_SIZE = 0x1AF
ASM_TAIL_SIZE = 0x2E1
FINAL_EXE = "6668546c64d9f00e61338fea93df401ce3a65485a8a94fb805cc943a717599e2"
FINAL_MAP = "65e596ca2f0914ecf3468cd1549fb808aeffe89c97a8621a0da3d74ff1144447"
UPDATE_SHA = "a2ecb4e9a3c07ff4bb8cf81f539d642a0622b871ce2c456d25a91793e1d5b6b7"
EXPECTED_CHANGED = list(range(271, 279))
EXPECTED_CPP_SEGMENT_SITES = [0xBBE2, 0xBBC3, 0xBBA5, 0xBB7C, 0xBB5E, 0xBB3A, 0xBAA0, 0xBA8F]
EXPECTED_UPDATE_FIXUPS = [
    (3, 0x19B),
    (3, 0x17C),
    (1, 0x179),
    (3, 0x15E),
    (1, 0x15B),
    (3, 0x135),
    (1, 0x132),
    (3, 0x117),
    (1, 0x114),
    (3, 0x0F3),
    (1, 0x08B),
]


def apply_update_source(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v464 update template identity drift")
    source = work / "th04/op/zunsoft.cpp"
    text = source.read_text()
    anchor = '#include "libs/master.lib/master.hpp"\n'
    if text.count(anchor) != 1:
        raise ValueError("v464 include anchor drift")
    text = text.replace(
        anchor,
        anchor + '#include "th03/math/polar.hpp"\n#include "th02/snd/snd.h"\n',
        1,
    )
    declaration = "void zunsoft_update_and_render(void)\n;"
    if text.count(declaration) != 1:
        raise ValueError("v464 update declaration drift")
    source.write_text(text.replace(declaration, TEMPLATE.read_text().rstrip(), 1))


def apply_asm_tail(work: Path) -> None:
    original = (work / "th04/zunsoft.asm").read_bytes()
    marker = b"public ZUNSOFT_PALETTE_UPDATE_AND_SHOW\r\n"
    if marker not in original:
        marker = b"public ZUNSOFT_PALETTE_UPDATE_AND_SHOW\n"
    if marker not in original:
        raise ValueError("v464 ASM tail marker drift")
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    tail = (
        b"extern ZUNSOFT_PYRO_NEW:near" + newline
        + b"extern ZUNSOFT_UPDATE_AND_RENDER:near" + newline
        + original[original.index(marker):]
    )
    (work / "th04_zunsoft_tail.asm").write_bytes(tail)
    wrapper = work / "th04_op_music_master.asm"
    data = wrapper.read_bytes()
    needle = b"include th04/zunsoft.asm"
    if data.count(needle) != 1:
        raise ValueError("v464 wrapper include drift")
    wrapper.write_bytes(data.replace(needle, b"include th04_zunsoft_tail.asm", 1))


def relocations(path: Path) -> list[int]:
    image = parse_mz(path.read_bytes())
    if not image.valid:
        raise ValueError(f"invalid MZ: {path}")
    return [row.linear for row in image.relocations]


def update_fixups(path: Path) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            found.extend(
                (kind, loc)
                for kind, loc in fixup_locations(record.data)
                if UPDATE_OFFSET <= loc < UPDATE_OFFSET + UPDATE_SIZE
            )
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--target-restored", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
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
    target_sites = [row.linear for row in target.relocations]
    target_pyro = target.program_image[PYRO_LOAD:PYRO_LOAD + PYRO_SIZE]
    target_update = target.program_image[UPDATE_LOAD:UPDATE_LOAD + UPDATE_SIZE]
    if digest(target_update) != UPDATE_SHA:
        raise ValueError("target update body identity drift")

    builds: dict[str, dict[str, object]] = {}
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
        baseline_sites = [row.linear for row in baseline.relocations]
        full_asm_code = segment_bytes(work / "obj/th04/opmusicm.obj", "OP_MUSIC_TEXT")
        if len(full_asm_code) != 0x490:
            raise ValueError(f"{label}: full ASM OP music size drift")

        apply_cpp_source(work)
        apply_update_source(work)
        apply_asm_tail(work)
        swap_source_order(work)
        rebuild_v463_op(work, output, label)

        exe = work / "bin/th04/op.exe"
        map_path = work / "obj/th04/op.map"
        cpp_obj = work / "obj/th04/zunsoft.obj"
        tail_obj = work / "obj/th04/opmusicm.obj"
        image = parse_mz(exe.read_bytes())
        sites = [row.linear for row in image.relocations]
        if image.program_image != baseline_program:
            raise ValueError(f"{label}: v464 changed linked OP program bytes")
        if image.program_image[PYRO_LOAD:PYRO_LOAD + PYRO_SIZE] != target_pyro:
            raise ValueError(f"{label}: pyro linked body drift")
        if image.program_image[UPDATE_LOAD:UPDATE_LOAD + UPDATE_SIZE] != target_update:
            raise ValueError(f"{label}: update linked body is not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation-site multiset drift")
        ordered = sum(left != right for left, right in zip(sites, target_sites))
        if ordered != 105:
            raise ValueError(f"{label}: ordered relocation frontier drift: {ordered}")
        changed = [i for i, (left, right) in enumerate(zip(baseline_sites, sites)) if left != right]
        if changed != EXPECTED_CHANGED:
            raise ValueError(f"{label}: unexpected relocation changes vs v461: {changed}")
        if sites[271:279] != EXPECTED_CPP_SEGMENT_SITES:
            raise ValueError(f"{label}: first-two-function segment-fixup order drift")

        cpp_code = segment_bytes(cpp_obj, "OP_MUSIC_TEXT")
        if len(cpp_code) != CPP_OWNER_SIZE:
            raise ValueError(f"{label}: TC86 first-two-function code size drift")
        update_code = cpp_code[UPDATE_OFFSET:UPDATE_OFFSET + UPDATE_SIZE]
        raw_diffs = [
            i for i, (left, right) in enumerate(zip(update_code, full_asm_code[UPDATE_OFFSET:UPDATE_OFFSET + UPDATE_SIZE]))
            if left != right
        ]
        if raw_diffs != [0x07]:
            raise ValueError(f"{label}: expected only _pyros offset-fixup addend raw diff: {raw_diffs}")
        fixups = update_fixups(cpp_obj)
        if fixups != EXPECTED_UPDATE_FIXUPS:
            raise ValueError(f"{label}: update FIXUPP order drift: {fixups}")
        tail_size = len(segment_bytes(tail_obj, "OP_MUSIC_TEXT"))
        if tail_size != ASM_TAIL_SIZE:
            raise ValueError(f"{label}: v464 ASM tail size drift: {tail_size}")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: v464 final OP identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "update_linked_sha256": digest(image.program_image[UPDATE_LOAD:UPDATE_LOAD + UPDATE_SIZE]),
            "target_update_sha256": UPDATE_SHA,
            "update_raw_sha256": digest(update_code),
            "update_raw_differences_vs_asm_owner": raw_diffs,
            "update_fixupp_locations": [[kind, loc] for kind, loc in fixups],
            "cpp_owner_code_size": len(cpp_code),
            "asm_tail_code_size": tail_size,
            "ordered_relocation_mismatches": ordered,
            "relocation_indices_changed_vs_v461": changed,
            "cpp_owner_segment_sites": sites[271:279],
        }

    if builds["a"] != builds["b"]:
        raise ValueError("A/B v464 results differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP zunsoft_update_and_render natural-C++ linked exact function replay; no packed-file promotion",
        "source_baseline": V402_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "A natural TC86 C++ reconstruction of zunsoft_update_and_render links to the exact 0x12B target body at load 0xBAC9 while preserving the whole v461 OP program image. The raw C++ function differs from the old TASM owner at only its local _pyros near-offset fixup addend. With the v463 pyro function in the same TC86 owner, the compiler emits all eight segment relocations from the first two functions in descending code-address order, exactly the local direction required by the target OP-music reversal. Overall R remains 105 only because the remaining two ZUNSOFT functions are still a separate TASM tail."
        ),
        "limit": (
            "This packet establishes the second linked-exact natural C++ function and strengthens the one-TC86-TU producer hypothesis. It does not establish source text for the final two ZUNSOFT functions or packed-file exactness."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": sha(receipt_path),
        "candidate_sha256": FINAL_EXE,
        "update_linked_exact": True,
        "update_size": UPDATE_SIZE,
        "ordered_relocation_mismatches": 105,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
