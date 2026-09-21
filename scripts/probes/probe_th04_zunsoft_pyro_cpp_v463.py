#!/usr/bin/env python3
"""Recover TH04 OP zunsoft_pyro_new() as natural TC86 C++ and relink it exact."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from probe_th04_master_object_split import build, sha  # noqa: E402
from probe_th04_op_music_segment_order import BASE as V402_BASE, apply_split as apply_v427  # noqa: E402
from probe_th04_op_relocation_topology_v461 import apply_v461  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_zunsoft_pyro_v463.cpp.in"
TEMPLATE_SHA = "e69b239621e42e6911068ec10fc9010495e83cb871752671c1c8070c8bfe70c3"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
V461_EXE = "53db8945c76daaf04124636d98e7c1d187eae252f75c21c29305edb446922301"
V461_MAP = "572b323a047b7b448822cce7179613fb91a14703f4cd0b746339b5ce19b59da2"
FINAL_EXE = "b73e54f2e2c751a9c9fec040ab7ec60dcc0beb785cbed17661df1b91f9d17235"
FINAL_MAP = "e975808eadbfe5a50e82a654b626a6f825d1aeb9c5d08010d56071583d9075cf"
TARGET_RESTORED_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
PYRO_LOAD = 0xBA45
PYRO_SIZE = 0x84


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def outdir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="zunsoft-pyro-v463-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def segment_bytes(path: Path, segment: str) -> bytes:
    records = parse_omf(path.read_bytes())
    groups = code_ledata(records, segment)
    if not groups:
        return b""
    end = max(row[1] for row in groups)
    data = bytearray(end)
    for start, stop, record_number, _ in groups:
        data[start:stop] = records[record_number - 1].data[3:]
    return bytes(data)


def apply_cpp_source(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v463 C++ template identity drift")
    source = work / "th04/op/zunsoft.cpp"
    text = source.read_text()
    include_anchor = '#include "libs/master.lib/pc98_gfx.hpp"\n'
    if text.count(include_anchor) != 1:
        raise ValueError("zunsoft include anchor drift")
    text = text.replace(
        include_anchor,
        include_anchor + '#include "libs/master.lib/master.hpp"\n',
        1,
    )
    struct_anchor = "};\n\n// Spawns [n] new explosions"
    if text.count(struct_anchor) != 1:
        raise ValueError("pyro struct anchor drift")
    text = text.replace(
        struct_anchor,
        "};\n\nextern pyro_t pyros[256];\n\n// Spawns [n] new explosions",
        1,
    )
    declaration = (
        "void pascal zunsoft_pyro_new(screen_point_t origin, int n, char patnum_base)\n;"
    )
    if text.count(declaration) != 1:
        raise ValueError("pyro declaration anchor drift")
    text = text.replace(declaration, TEMPLATE.read_text().rstrip(), 1)
    source.write_text(text)


def apply_asm_tail(work: Path) -> None:
    original = (work / "th04/zunsoft.asm").read_bytes()
    marker = b"public ZUNSOFT_UPDATE_AND_RENDER\r\n"
    if marker not in original:
        marker = b"public ZUNSOFT_UPDATE_AND_RENDER\n"
    if marker not in original:
        raise ValueError("zunsoft ASM tail marker drift")
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    tail = b"extern ZUNSOFT_PYRO_NEW:near" + newline + original[original.index(marker):]
    (work / "th04_zunsoft_tail.asm").write_bytes(tail)
    wrapper = work / "th04_op_music_master.asm"
    data = wrapper.read_bytes()
    needle = b"include th04/zunsoft.asm"
    if data.count(needle) != 1:
        raise ValueError("OP music wrapper include drift")
    wrapper.write_bytes(data.replace(needle, b"include th04_zunsoft_tail.asm", 1))


def swap_source_order(work: Path) -> None:
    tup = work / "Tupfile.lua"
    text = tup.read_text()
    old = (
        '\t{ "th04_op_music_master.asm", o = "opmusicm.obj" },\n'
        '\t"th04/zunsoft.cpp",\n'
    )
    new = (
        '\t"th04/zunsoft.cpp",\n'
        '\t{ "th04_op_music_master.asm", o = "opmusicm.obj" },\n'
    )
    if text.count(old) != 1:
        raise ValueError("v463 adjacent OP owner order drift")
    tup.write_text(text.replace(old, new, 1))


def environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN",
    )
    return env


def run_checked(command: list[str], cwd: Path, log: Path, timeout: int = 180) -> None:
    done = subprocess.run(command, cwd=cwd, env=environment(), capture_output=True, text=True, timeout=timeout)
    log.write_text(json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr)
    if done.returncode:
        raise RuntimeError(f"command failed; see {log}")


def rebuild_v463_op(work: Path, output: Path, label: str) -> None:
    # TC86 C++ owner.
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

    # TASM tail owner. TASM32 is a Windows tool, so invoke it through the same
    # Wine cmd/PATH surface used by the repository build.
    tail_obj = work / "obj/th04/opmusicm.obj"
    tail_obj.unlink(missing_ok=True)
    tasm_command = (
        r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%&&"
        r"tasm32 /m /mx /kh32768 /t /dGAME=4 th04_op_music_master.asm obj\th04\opmusicm.obj"
    )
    run_checked(
        ["wine", "cmd", "/d", "/c", tasm_command],
        work,
        output / f"assemble-{label}.log",
    )
    if not tail_obj.is_file():
        raise ValueError("TASM did not produce obj/th04/opmusicm.obj")

    # The baseline response was generated before the source-order swap. Apply
    # exactly that adjacent object swap, then relink TH04 OP only.
    rsp = work / "obj/th04/op.@l"
    text = rsp.read_text()
    old = r"obj\th04\opmusicm.obj obj\th04\zunsoft.obj"
    new = r"obj\th04\zunsoft.obj obj\th04\opmusicm.obj"
    if text.count(old) != 1:
        raise ValueError("OP response object-order anchor drift")
    rsp.write_text(text.replace(old, new, 1))
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


def relocations(path: Path) -> list[int]:
    image = parse_mz(path.read_bytes())
    if not image.valid:
        raise ValueError(f"invalid MZ: {path}")
    return [row.linear for row in image.relocations]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--target-restored", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    source = args.source_dir.resolve()
    target_path = args.target_restored.resolve()
    output = outdir(args.output_dir)

    if sha(RUNNER) != RUNNER_SHA:
        raise ValueError("MS-DOS runner identity drift")
    for rel, expected in V402_BASE.items():
        path = source / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"v402 source identity drift: {rel}")
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("v228 target-restored identity drift")
    target_mz = parse_mz(target_path.read_bytes())
    target_sites = [row.linear for row in target_mz.relocations]
    target_pyro = target_mz.program_image[PYRO_LOAD:PYRO_LOAD + PYRO_SIZE]
    if len(target_pyro) != PYRO_SIZE:
        raise ValueError("target pyro slice drift")

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
        baseline_image = parse_mz(baseline_exe.read_bytes())
        baseline_sites = [row.linear for row in baseline_image.relocations]
        baseline_program = baseline_image.program_image
        full_asm_obj = work / "obj/th04/opmusicm.obj"
        full_asm_code = segment_bytes(full_asm_obj, "OP_MUSIC_TEXT")
        if len(full_asm_code) != 0x490:
            raise ValueError(f"{label}: full ASM OP music size drift")

        apply_cpp_source(work)
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
            raise ValueError(f"{label}: replacing pyro owner changed linked program bytes")
        if image.program_image[PYRO_LOAD:PYRO_LOAD + PYRO_SIZE] != target_pyro:
            raise ValueError(f"{label}: linked natural C++ pyro body is not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation-site multiset drift")
        ordered_mismatches = sum(left != right for left, right in zip(sites, target_sites))
        if ordered_mismatches != 105:
            raise ValueError(f"{label}: ordered relocation frontier drift: {ordered_mismatches}")
        changed = [i for i, (left, right) in enumerate(zip(baseline_sites, sites)) if left != right]
        if changed != [271, 272]:
            raise ValueError(f"{label}: unexpected relocation changes vs v461: {changed}")
        if sites[271:273] != [0xBAA0, 0xBA8F]:
            raise ValueError(f"{label}: TC86 pyro far-call order drift: {sites[271:273]}")

        cpp_code = segment_bytes(cpp_obj, "OP_MUSIC_TEXT")
        if len(cpp_code) != PYRO_SIZE:
            raise ValueError(f"{label}: TC86 pyro object code is {len(cpp_code)} bytes")
        raw_diffs = [i for i, (left, right) in enumerate(zip(cpp_code, full_asm_code[:PYRO_SIZE])) if left != right]
        if raw_diffs != [0x1F]:
            raise ValueError(f"{label}: expected only local-offset fixup addend raw diff, got {raw_diffs}")
        cpp_fixups: list[tuple[int, int]] = []
        for record in parse_omf(cpp_obj.read_bytes()):
            if record.record_type == 0x9C:
                cpp_fixups.extend((kind, loc) for kind, loc in fixup_locations(record.data) if loc < PYRO_SIZE)
        if cpp_fixups != [(3, 0x59), (3, 0x48), (1, 0x1F)]:
            raise ValueError(f"{label}: TC86 pyro FIXUPP order drift: {cpp_fixups}")
        if len(segment_bytes(tail_obj, "OP_MUSIC_TEXT")) != 0x40C:
            raise ValueError(f"{label}: ASM tail size drift")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: final OP identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "pyro_linked_sha256": digest(image.program_image[PYRO_LOAD:PYRO_LOAD + PYRO_SIZE]),
            "target_pyro_sha256": digest(target_pyro),
            "cpp_pyro_raw_sha256": digest(cpp_code),
            "cpp_pyro_raw_differences_vs_asm_owner": raw_diffs,
            "cpp_pyro_fixupp_locations": [[kind, loc] for kind, loc in cpp_fixups],
            "ordered_relocation_mismatches": ordered_mismatches,
            "relocation_indices_changed_vs_v461": changed,
            "relocation_sites_271_272": sites[271:273],
            "cpp_code_size": len(cpp_code),
            "asm_tail_code_size": len(segment_bytes(tail_obj, "OP_MUSIC_TEXT")),
        }

    if builds["a"] != builds["b"]:
        raise ValueError("A/B v463 results differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP zunsoft_pyro_new natural-C++ linked exact function replay; no packed-file promotion",
        "source_baseline": V402_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "A natural TC86 C++ reconstruction of zunsoft_pyro_new links to the exact 0x84 target body at load 0xBA45. Its raw OMF code differs from the old TASM owner at only the _pyros near-offset fixup addend, which resolves to identical linked bytes. TC86 emits the two far-call segment fixups in descending code-address order (0x59 then 0x48), changing only OP relocation entries 271..272 versus v461 while preserving the entire program image and the 804-site multiset. The overall ordered mismatch remains 105 because the three remaining ASM ZUNSOFT functions still form a separate earlier FIXUPP block; this supports recovering the entire 0x490 owner as one C++ producer."
        ),
        "limit": (
            "The replay intentionally leaves the other three ZUNSOFT ASM functions in a tail object. It establishes one linked-exact natural C++ function and its producer/FIXUPP behavior, not historical source text for the remaining functions or packed-file exactness."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": sha(receipt_path),
        "candidate_sha256": FINAL_EXE,
        "pyro_linked_exact": True,
        "pyro_size": PYRO_SIZE,
        "ordered_relocation_mismatches": 105,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
