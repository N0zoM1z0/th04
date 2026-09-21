#!/usr/bin/env python3
"""Replay the complete TH04 OP ZUNSOFT owner as natural TC86 C++."""
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
    RUNNER,
    TARGET_RESTORED_SHA,
    V461_EXE,
    V461_MAP,
    digest,
    outdir,
    run_checked,
    segment_bytes,
)
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

PYRO_TEMPLATE = ROOT / "config/replay/th04_zunsoft_pyro_scalar_v466.cpp.in"
UPDATE_TEMPLATE = ROOT / "config/replay/th04_zunsoft_update_v464.cpp.in"
PALETTE_TEMPLATE = ROOT / "config/replay/th04_zunsoft_palette_v465.cpp.in"
ANIMATE_TEMPLATE = ROOT / "config/replay/th04_zunsoft_animate_v466.cpp.in"
PYRO_TEMPLATE_SHA = "460d4d1acfc84e6ff0fbcba8cbdbcdcfce5f13b7121f767fbda6791b8a362dfc"
UPDATE_TEMPLATE_SHA = "9e19013f5cf4e4239a271441b25df8024e28c7bfd67e144d23f44d2a1c7cad77"
PALETTE_TEMPLATE_SHA = "b2879df2405fdf493e3bdd7ff5fc8700a4bd0c5aa3d19bdd1d82f707a67963ce"
ANIMATE_TEMPLATE_SHA = "a98f781ab949a65be1ec6b5800c3b63054e6106d29a54c6bb771ec1d95eaacd0"

OWNER_LOAD = 0xBA45
OWNER_SIZE = 0x490
OWNER_SHA = "c0b9629f17aaa316af5b332cd6883e0f119f956ff2cfa64892dc067c3281c23e"
FINAL_EXE = "310ad3af095ba29067f264acbd5c88ed320d64f07bf9d315336b592fef8b5192"
FINAL_MAP = "e8a3813d4a369fadda19582237e2066680a28353e5b6acc9e23e0925be122a95"
EXPECTED_RAW_DIFFS = [0x1F, 0x8B, 0x2BF, 0x2D3, 0x303, 0x30C, 0x315, 0x31E]
EXPECTED_RAW_CANDIDATE_BYTES = [0x30, 0x30, 0x09, 0x30, 0x0E, 0x18, 0x22, 0x2C]
EXPECTED_OP_MUSIC_INDICES = list(range(271, 306))
EXPECTED_CHANGED_VS_V461 = list(range(271, 303)) + [304, 305]
EXPECTED_REMAINING = list(range(186, 194)) + list(range(403, 466))


def _check_templates() -> None:
    expected = {
        PYRO_TEMPLATE: PYRO_TEMPLATE_SHA,
        UPDATE_TEMPLATE: UPDATE_TEMPLATE_SHA,
        PALETTE_TEMPLATE: PALETTE_TEMPLATE_SHA,
        ANIMATE_TEMPLATE: ANIMATE_TEMPLATE_SHA,
    }
    for path, wanted in expected.items():
        if sha(path) != wanted:
            raise ValueError(f"template identity drift: {path.relative_to(ROOT)}")


def apply_full_cpp_source(work: Path) -> None:
    _check_templates()
    source = work / "th04/op/zunsoft.cpp"
    text = source.read_text()

    include_anchor = '#include "libs/master.lib/pc98_gfx.hpp"\n'
    if text.count(include_anchor) != 1:
        raise ValueError("zunsoft include anchor drift")
    text = text.replace(
        include_anchor,
        include_anchor
        + '#include "libs/master.lib/master.hpp"\n'
        + '#include "th03/math/polar.hpp"\n'
        + '#include "th04/snd/snd.h"\n'
        + '#include "th03/formats/pi.hpp"\n'
        + '#include "th04/hardware/bgimage.hpp"\n'
        + '#include "th04/hardware/input.h"\n',
        1,
    )

    struct_anchor = "};\n\n// Spawns [n] new explosions"
    if text.count(struct_anchor) != 1:
        raise ValueError("pyro struct anchor drift")
    text = text.replace(
        struct_anchor,
        "};\n\n"
        "extern pyro_t pyros[256];\n"
        "extern char zun00_pi[], logo[], zun02_bft[], zun04_bft[], zun01_bft[], zun03_bft[];\n\n"
        "// Spawns [n] new explosions",
        1,
    )

    pyro_decl = "void pascal zunsoft_pyro_new(screen_point_t origin, int n, char patnum_base)\n;"
    update_decl = "void zunsoft_update_and_render(void)\n;"
    palette_decl = "void zunsoft_palette_update_and_show(int tone)\n;"
    replacements = (
        (pyro_decl, PYRO_TEMPLATE.read_text().rstrip()),
        (update_decl, UPDATE_TEMPLATE.read_text().rstrip()),
        (palette_decl, PALETTE_TEMPLATE.read_text().rstrip()),
    )
    for old, new in replacements:
        if text.count(old) != 1:
            raise ValueError(f"zunsoft declaration drift: {old.splitlines()[0]}")
        text = text.replace(old, new, 1)

    data_anchor = "static const int PYRO_COUNT = 256;\n"
    if text.count(data_anchor) != 1:
        raise ValueError("zunsoft data anchor drift")
    text = text.replace(data_anchor, ANIMATE_TEMPLATE.read_text().rstrip() + "\n\n" + data_anchor, 1)
    source.write_text(text)

    # Reflect the recovered physical ownership in the source build topology:
    # OP_MUSIC_TEXT is now entirely emitted by th04/op/zunsoft.cpp.
    tup = work / "Tupfile.lua"
    build_text = tup.read_text()
    marker = 'th04:branch(MODEL_LARGE, { cflags = "-DBINARY=\'O\'" }):link("op", {'
    start = build_text.index(marker)
    end = build_text.index("\n})", start) + 3
    block = build_text[start:end]
    owner_line = '\t{ "th04_op_music_master.asm", o = "opmusicm.obj" },\n'
    if block.count(owner_line) != 1:
        raise ValueError("OP music TASM owner line drift")
    block = block.replace(owner_line, "", 1)
    tup.write_text(build_text[:start] + block + build_text[end:])


def rebuild_full_cpp_op(work: Path, output: Path, label: str) -> None:
    cpp_obj = work / "obj/th04/zunsoft.obj"
    cpp_obj.unlink(missing_ok=True)
    run_checked(
        [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-",
            "-3", "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'",
            "-nobj/th04/", "th04/zunsoft.cpp",
        ],
        work,
        output / f"compile-{label}.log",
    )
    if not cpp_obj.is_file():
        raise ValueError("TC86 did not produce obj/th04/zunsoft.obj")

    # The response file comes from the verified v461 baseline build. Removing
    # the old physical TASM owner leaves zunsoft.obj directly after op_setup.obj.
    rsp = work / "obj/th04/op.@l"
    response = rsp.read_text()
    needle = r"obj\th04\opmusicm.obj obj\th04\zunsoft.obj"
    if response.count(needle) != 1:
        raise ValueError("OP response full-owner anchor drift")
    rsp.write_text(response.replace(needle, r"obj\th04\zunsoft.obj", 1))

    exe = work / "bin/th04/op.exe"
    map_path = work / "obj/th04/op.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
        work,
        output / f"link-{label}.log",
    )
    if not exe.is_file() or not map_path.is_file():
        raise ValueError("targeted OP relink did not produce EXE/MAP")


def all_fixups(path: Path) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            result.extend(fixup_locations(record.data))
    return result


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
        raise ValueError("v228 OP target-restored identity drift")

    target = parse_mz(target_path.read_bytes())
    if not target.valid:
        raise ValueError("invalid target-restored MZ")
    target_sites = [row.linear for row in target.relocations]
    target_owner = target.program_image[OWNER_LOAD:OWNER_LOAD + OWNER_SIZE]
    if len(target_owner) != OWNER_SIZE or digest(target_owner) != OWNER_SHA:
        raise ValueError("target ZUNSOFT owner identity drift")

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        apply_v427(work)
        apply_v461(work)
        build(work, output / f"baseline-build-{label}.log")

        baseline_exe = work / "bin/th04/op.exe"
        baseline_map = work / "obj/th04/op.map"
        baseline_asm_obj = work / "obj/th04/opmusicm.obj"
        if sha(baseline_exe) != V461_EXE or sha(baseline_map) != V461_MAP:
            raise ValueError(f"{label}: v461 baseline identity drift")
        baseline = parse_mz(baseline_exe.read_bytes())
        baseline_program = baseline.program_image
        baseline_sites = [row.linear for row in baseline.relocations]
        baseline_asm_code = segment_bytes(baseline_asm_obj, "OP_MUSIC_TEXT")
        if len(baseline_asm_code) != OWNER_SIZE:
            raise ValueError(f"{label}: baseline TASM ZUNSOFT size drift")

        apply_full_cpp_source(work)
        rebuild_full_cpp_op(work, output, label)

        exe = work / "bin/th04/op.exe"
        map_path = work / "obj/th04/op.map"
        cpp_obj = work / "obj/th04/zunsoft.obj"
        image = parse_mz(exe.read_bytes())
        if not image.valid:
            raise ValueError(f"{label}: invalid candidate MZ")
        sites = [row.linear for row in image.relocations]

        if image.program_image != baseline_program:
            raise ValueError(f"{label}: full C++ owner changed linked OP program bytes")
        linked_owner = image.program_image[OWNER_LOAD:OWNER_LOAD + OWNER_SIZE]
        if linked_owner != target_owner:
            raise ValueError(f"{label}: linked 0x490 ZUNSOFT owner is not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation-site multiset drift")
        if sites[271:306] != target_sites[271:306]:
            raise ValueError(f"{label}: 35-entry OP-music relocation block is not target exact")

        ordered = sum(left != right for left, right in zip(sites, target_sites))
        if ordered != 71:
            raise ValueError(f"{label}: expected 71 ordered mismatches, got {ordered}")
        remaining = [i for i, (left, right) in enumerate(zip(sites, target_sites)) if left != right]
        if remaining != EXPECTED_REMAINING:
            raise ValueError(f"{label}: residual relocation indices drift: {remaining}")
        changed = [i for i, (left, right) in enumerate(zip(baseline_sites, sites)) if left != right]
        if changed != EXPECTED_CHANGED_VS_V461:
            raise ValueError(f"{label}: changed indices vs v461 drift: {changed}")

        cpp_code = segment_bytes(cpp_obj, "OP_MUSIC_TEXT")
        if len(cpp_code) != OWNER_SIZE:
            raise ValueError(f"{label}: full C++ OP_MUSIC_TEXT size drift: {len(cpp_code)}")
        raw_diffs = [i for i, (left, right) in enumerate(zip(cpp_code, baseline_asm_code)) if left != right]
        if raw_diffs != EXPECTED_RAW_DIFFS:
            raise ValueError(f"{label}: raw OMF CODE diff offsets drift: {raw_diffs}")
        if [cpp_code[i] for i in raw_diffs] != EXPECTED_RAW_CANDIDATE_BYTES:
            raise ValueError(f"{label}: local-addend byte values drift")
        if any(baseline_asm_code[i] != 0 for i in raw_diffs):
            raise ValueError(f"{label}: baseline raw addends are no longer external zeros")
        fixups = all_fixups(cpp_obj)
        kind1_locations = {loc for kind, loc in fixups if kind == 1}
        if not set(raw_diffs).issubset(kind1_locations):
            raise ValueError(f"{label}: raw differences are not all ordinary offset FIXUPPs")
        kind3_count = sum(kind == 3 for kind, _ in fixups)
        if kind3_count != 35:
            raise ValueError(f"{label}: expected 35 segment FIXUPPs, got {kind3_count}")

        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: final OP identity drift")

        target_payload_diffs = [
            i for i, (left, right) in enumerate(zip(image.program_image, target.program_image))
            if left != right
        ]
        if target_payload_diffs != [0xDE8B, 0xDE8C]:
            raise ValueError(f"{label}: expected only shared snd_load payload residual: {target_payload_diffs}")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "linked_owner_sha256": digest(linked_owner),
            "raw_cpp_owner_sha256": digest(cpp_code),
            "raw_asm_owner_sha256": digest(baseline_asm_code),
            "raw_omf_code_diff_offsets": raw_diffs,
            "raw_omf_candidate_addends": [cpp_code[i] for i in raw_diffs],
            "segment_fixupp_count": kind3_count,
            "op_music_relocation_indices": EXPECTED_OP_MUSIC_INDICES,
            "op_music_relocation_sites": sites[271:306],
            "ordered_relocation_mismatches": ordered,
            "remaining_mismatch_indices": remaining,
            "relocation_indices_changed_vs_v461": changed,
            "payload_mismatch_offsets_vs_target": target_payload_diffs,
        }

    if builds["a"] != builds["b"]:
        raise ValueError("A/B v466 results differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "TH04 OP complete 0x490 ZUNSOFT natural-TC86 owner replay; "
            "linked exact code and natural relocation order, no MZ relocation editing"
        ),
        "source_baseline": V402_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "templates": {
            str(PYRO_TEMPLATE.relative_to(ROOT)): PYRO_TEMPLATE_SHA,
            str(UPDATE_TEMPLATE.relative_to(ROOT)): UPDATE_TEMPLATE_SHA,
            str(PALETTE_TEMPLATE.relative_to(ROOT)): PALETTE_TEMPLATE_SHA,
            str(ANIMATE_TEMPLATE.relative_to(ROOT)): ANIMATE_TEMPLATE_SHA,
        },
        "builds": builds,
        "observed_effect": (
            "TC86 compiles all four ZUNSOFT functions into one 0x490-byte OP_MUSIC_TEXT owner whose linked bytes are target exact. "
            "The refined scalar (origin_y, origin_x, n, patnum) pyro ABI preserves the previously exact 0x84 body and naturally lets the sparse animate switch use merged 32-bit constant pushes. "
            "The animate function reaches the target ENTER 8 layout and sparse value/jump tables from ordinary C++ control flow; #pragma option -a2 supplies the target one-byte table alignment after RET. "
            "Eight raw CODE bytes differ from the former external-reference TASM owner only at ordinary kind-1 local offset FIXUPP addends, and TLINK resolves all eight to identical linked bytes. "
            "All 35 OP-music segment relocations become target-index exact without editing the MZ table, reducing the ordered OP residual from 105 to 71 while preserving the complete v461 program image and 804-site relocation multiset."
        ),
        "source_shape_caution": (
            "The 16-bit zero store used to initialize adjacent alive/age bytes is an ordinary C++ aliasing expression chosen to reproduce the compiler-observed target word store. "
            "This receipt proves a natural TC86 producer and linked semantics; it does not claim the exact historical spelling of that single source statement."
        ),
        "remaining_frontier": (
            "OP relocation order now differs only in BGIMAGE indices 186..193 and score_e/hi_view indices 403..465. "
            "The shared two-byte snd_load MOV encoding remains the only OP program-image payload residual."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": sha(receipt_path),
        "candidate_sha256": FINAL_EXE,
        "linked_owner_exact": True,
        "op_music_relocations_exact": True,
        "ordered_relocation_mismatches": 71,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
