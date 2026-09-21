#!/usr/bin/env python3
"""Recover the first TH04 MAINE verdict owner as one natural TC86 C++ TU.

Starting from retained v401 source, this replay reconstructs the accepted v473
frontier, then fuses the already-linked-exact graph3 / B81D / skill / fraction
/ B9 helpers into one TC86 MAINE_01_TEXT producer.  No executable, object, or
relocation-table bytes are patched.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_fraction_cpp_v473 import (  # noqa: E402
    FINAL_EXE as V473_EXE,
    FINAL_MAP as V473_MAP,
    V472_MISMATCHES as V473_MISMATCHES,
    prepare_v472,
    split_fraction_owner,
)
from probe_th04_maine_master_relocation_order import BASE as V401_BASE  # noqa: E402
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER,
    RUNNER_SHA,
    TARGET_RESTORED_SHA,
    digest,
    run_checked,
)
from probe_th04_maine_segment_topology_v470 import (  # noqa: E402
    PROGRAM_SHA,
    output_dir,
    tasm,
    tcc,
)
from probe_th04_master_object_split import compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_verdict_v474.cpp.in"
TEMPLATE_SHA = "9b21fbe19efc67d6b96ae918d49394aff834a65bada742063e4ac91b77811360"
FINAL_EXE = "9436f51a66156cfda240296ae43972669ec76a952f04276c597081c992324c6a"
FINAL_MAP = "2bfad457813561e365c3c9ef56f5c590eeb36e079865caa45623b0a601761488"
GRAPH_LOAD = 0x1737
OWNER_SIZE = 0x03FA
TAIL_SIZE = 0x05C8
EXPECTED_MISMATCHES = 170
EXPECTED_CHANGED = [251, 252, 253, 256, 257, 258]
EXPECTED_TARGET_SITES = [
    0xBB70, 0xBB1B, 0xB9EA, 0xB973,
    0xB963, 0xB881, 0xB86C, 0xB816,
]
EXPECTED_KIND3 = [0x3E7, 0x392, 0x261, 0x1EA, 0x1DA, 0x0F8, 0x0E3, 0x08D]


def segment_bytes(path: Path, segment: str) -> bytes:
    records = parse_omf(path.read_bytes())
    groups = code_ledata(records, segment)
    if not groups:
        return b""
    end = max(row[1] for row in groups)
    data = bytearray(end)
    for start, stop, recno, _ in groups:
        data[start:stop] = records[recno - 1].data[3:]
    return bytes(data)


def object_fixups(path: Path) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            result.extend(fixup_locations(record.data))
    return result


def prepare_v473(work: Path, output: Path, label: str) -> None:
    prepare_v472(work, output, label)
    split_fraction_owner(work)
    tasm(work, output, f"v473-tail-{label}", "th04_maine_01_tail_v473.asm", "m1tail73.obj")
    tasm(work, output, f"v473-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")
    tcc(work, output, f"v473-fraction-{label}", "th04/fr.cpp")

    rsp = work / "obj/th04/maine.@l"
    text = rsp.read_text()
    old = r"obj\th04\m1tail.obj"
    new = r"obj\th04\fr.obj obj\th04\m1tail73.obj"
    if text.count(old) != 1:
        raise ValueError(f"{label}: v472 tail response token drift")
    rsp.write_text(text.replace(old, new, 1))

    exe = work / "bin/th04/maine.exe"
    map_path = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
        work,
        output / f"v473-link-{label}.log",
    )
    if sha(exe) != V473_EXE or sha(map_path) != V473_MAP:
        raise ValueError(f"{label}: v473 baseline identity drift")
    if digest(parse_mz(exe.read_bytes()).program_image) != PROGRAM_SHA:
        raise ValueError(f"{label}: v473 program-image identity drift")


def split_verdict_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v474 verdict template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/gv.cpp")

    # The remaining TASM starts at sub_BB81; B9 body + switch table are now
    # generated naturally in the TC86 owner.
    source = work / "th04_maine_01_tail_v473.asm"
    text = source.read_bytes().decode("cp932")
    seg = "maine_01_TEXT segment byte public 'CODE' use16"
    positions: list[int] = []
    off = 0
    while True:
        pos = text.find(seg, off)
        if pos < 0:
            break
        positions.append(pos)
        off = pos + 1
    if len(positions) != 2:
        raise ValueError(f"v473 tail segment occurrence drift: {positions}")
    real = positions[1]
    end_marker = "maine_01_TEXT ends"
    seg_end = text.index(end_marker, real)
    common = text[:real]
    body = text[real + len(seg):seg_end]
    start = body.index("sub_BB81\tproc near")
    tail_body = body[start:]

    # Source-level cross-owner calls now target normal TC86 C++ PUBLIC names.
    common = common.replace(
        "\textern sub_B81D:near\r\n",
        "\textern @sub_B81D$qv:near\r\n",
    )
    if "\textern @sub_B9F2$qv:near\r\n" not in common:
        text_end = common.index("_TEXT ends\r\n") + len("_TEXT ends\r\n")
        common = (
            common[:text_end]
            + "\r\n\textern @sub_B9F2$qv:near\r\n"
            + common[text_end:]
        )
    tail_body = tail_body.replace(
        "\t\tcall\tsub_B81D\r\n",
        "\t\tcall\t@sub_B81D$qv\r\n",
    )
    tail_body = tail_body.replace(
        "\t\tcall\tsub_B9F2\r\n",
        "\t\tcall\t@sub_B9F2$qv\r\n",
    )
    assume = (
        "\r\n\t\tassume cs:group_01\r\n"
        "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n"
    )
    tail = common + seg + assume + tail_body + end_marker + "\r\n\tend\r\n"
    (work / "th04_maine_01_tail_v474.asm").write_bytes(tail.encode("cp932"))

    # The strings already live in the rest/data owner.  Expose their exact
    # addresses to TC86 using zero-byte C-linkage aliases.
    rest = work / "th04_maine_rest_v470.asm"
    data = rest.read_bytes().decode("cp932")
    pos = data.index("public ", data.index("\t.data\r\n"))
    line_end = data.index("\r\n", pos)
    for alias in ("_aU_", "_aBu_0"):
        if alias not in data[pos:line_end]:
            data = data[:line_end] + ", " + alias + data[line_end:]
            line_end = data.index("\r\n", pos)
    for needle, alias in (
        ("aU_\t\tdb '点',0", "_aU_"),
        ("aBu_0\t\tdb '％',0", "_aBu_0"),
    ):
        if data.count(needle) != 1:
            raise ValueError(f"v474 rest data label drift: {needle}")
        if f"{alias} label byte" not in data:
            data = data.replace(needle, f"{alias} label byte\r\n" + needle, 1)
    rest.write_bytes(data.encode("cp932"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source = args.source_dir.resolve()
    target_path = args.target_restored.resolve()
    output = output_dir(args.output_dir)

    if sha(RUNNER) != RUNNER_SHA:
        raise ValueError("MS-DOS runner identity drift")
    for rel, expected in V401_BASE.items():
        path = source / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"v401 source identity drift: {rel}")
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("v228 MAINE target-restored identity drift")
    target = parse_mz(target_path.read_bytes())
    target_sites = [row.linear for row in target.relocations]
    target_owner = target.program_image[GRAPH_LOAD:GRAPH_LOAD + OWNER_SIZE]

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        prepare_v473(work, output, label)
        baseline_exe = work / "bin/th04/maine.exe"
        baseline = parse_mz(baseline_exe.read_bytes())
        baseline_sites = [row.linear for row in baseline.relocations]
        if sum(a != b for a, b in zip(baseline_sites, target_sites)) != V473_MISMATCHES:
            raise ValueError(f"{label}: v473 ordered frontier drift")

        split_verdict_owner(work)
        tcc(work, output, f"v474-verdict-{label}", "th04/gv.cpp")
        tasm(work, output, f"v474-tail-{label}", "th04_maine_01_tail_v474.asm", "m1tail74.obj")
        tasm(work, output, f"v474-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")

        owner = segment_bytes(work / "obj/th04/gv.obj", "MAINE_01_TEXT")
        tail = segment_bytes(work / "obj/th04/m1tail74.obj", "MAINE_01_TEXT")
        groups = code_ledata(parse_omf((work / "obj/th04/gv.obj").read_bytes()), "MAINE_01_TEXT")
        if len(groups) != 1 or groups[0][0] != 0 or groups[0][1] != OWNER_SIZE:
            raise ValueError(f"{label}: verdict owner is not one MAINE_01 LEDATA: {groups}")
        if len(owner) != OWNER_SIZE or len(tail) != TAIL_SIZE:
            raise ValueError(f"{label}: verdict/tail size drift")
        fixes = object_fixups(work / "obj/th04/gv.obj")
        kind3 = [loc for kind, loc in fixes if kind == 3]
        if kind3 != EXPECTED_KIND3:
            raise ValueError(f"{label}: verdict kind-3 FIXUPP order drift: {kind3}")

        rsp = work / "obj/th04/maine.@l"
        text = rsp.read_text()
        old = (
            r"obj\th04\g3.obj obj\th04\m1mid.obj obj\th04\sk.obj "
            r"obj\th04\fr.obj obj\th04\m1tail73.obj"
        )
        new = r"obj\th04\gv.obj obj\th04\m1tail74.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: v473 verdict-owner response sequence drift")
        rsp.write_text(text.replace(old, new, 1))

        exe = work / "bin/th04/maine.exe"
        map_path = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True)
        map_path.unlink(missing_ok=True)
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work,
            output / f"v474-link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        sites = [row.linear for row in image.relocations]
        payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image or digest(image.program_image) != PROGRAM_SHA:
            raise ValueError(f"{label}: verdict fusion changed linked program bytes")
        if image.program_image[GRAPH_LOAD:GRAPH_LOAD + OWNER_SIZE] != target_owner:
            raise ValueError(f"{label}: linked verdict owner is not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: target relocation-site multiset drift")
        ordered = sum(a != b for a, b in zip(sites, target_sites))
        if ordered != EXPECTED_MISMATCHES:
            raise ValueError(f"{label}: v474 ordered mismatch drift: {ordered}")
        changed = [i for i, (a, b) in enumerate(zip(baseline_sites, sites)) if a != b]
        if changed != EXPECTED_CHANGED:
            raise ValueError(f"{label}: v474 changed-index set drift: {changed}")
        if sites[251:259] != EXPECTED_TARGET_SITES or target_sites[251:259] != EXPECTED_TARGET_SITES:
            raise ValueError(f"{label}: verdict relocation block is not target-index exact")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: v474 final identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "owner_code_sha256": digest(owner),
            "owner_size": len(owner),
            "owner_single_ledata": True,
            "owner_fixupp_count": len(fixes),
            "owner_kind3_locations": kind3,
            "tail_size": len(tail),
            "changed_indices_vs_v473": changed,
            "target_exact_indices": [251, 258],
            "target_exact_sites": sites[251:259],
            "ordered_relocation_mismatches": ordered,
            "same_index_relocations": len(sites) - ordered,
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256", "owner_code_sha256",
        "owner_size", "owner_single_ledata", "owner_fixupp_count", "owner_kind3_locations",
        "tail_size", "changed_indices_vs_v473", "target_exact_sites",
        "ordered_relocation_mismatches", "same_index_relocations",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B v474 {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE graph3+verdict natural-C++ TU linked-exact / relocation-order replay",
        "source_baseline": V401_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "Putting graph_3_digit_put, sub_B81D, skill_apply_and_graph_percentage_put, graph_fraction_of_million_put, and sub_B9F2 in one TC86 TU produces one 0x3FA MAINE_01_TEXT LEDATA/FIXUPP owner. The complete linked MAINE program image remains byte-identical to v473. The compiler emits the eight target-relevant segment fixups as one high-address-first stream, making relocation indices 251..258 target-index exact and reducing the ordered residual from 176 to 170 while preserving the 559-site multiset. The one-byte B9 switch-table pad appears naturally from #pragma option -a2 at the combined owner offset; no padding or relocation bytes are inserted manually."
        ),
        "limit": (
            "The replay uses zero-byte C-linkage aliases for existing rest-owner strings and source-level symbol adapters for private near helpers only. Those adapters alter no linked code/data address. Remaining MAINE_01 residuals begin in the preceding TASM prefix and following sub_BB81 verdict tail; further progress requires recovering those natural producer boundaries rather than reordering the MZ table."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "verdict_owner_linked_exact": True,
        "ordered_relocation_mismatches": EXPECTED_MISMATCHES,
        "same_index_relocations": 559 - EXPECTED_MISMATCHES,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
