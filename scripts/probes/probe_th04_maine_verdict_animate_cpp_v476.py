#!/usr/bin/env python3
"""Fuse TH04 MAINE sub_BB81() + verdict_animate() into one natural TC86 TU.

Starts from retained v401 source, reconstructs the accepted v475 frontier,
then replaces the adjacent 0x577 + 0x51 TASM/C++ split by one TC86 owner.  No
executable, OMF, or relocation-table bytes are patched.
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
from probe_th04_maine_bb81_cpp_v475 import (  # noqa: E402
    FINAL_EXE as V475_EXE,
    FINAL_MAP as V475_MAP,
    EXPECTED_MISMATCHES as V475_MISMATCHES,
    TEMPLATE as BB81_TEMPLATE,
    TEMPLATE_SHA as BB81_TEMPLATE_SHA,
    prepare_v474,
    split_bb81_owner,
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

ANIMATE_TEMPLATE = ROOT / "config/replay/th04_maine_verdict_animate_v476.cpp.in"
ANIMATE_TEMPLATE_SHA = "9f133d7d4bf1d3cecf62a4fc00cc41409da1c2184ff260798ff3b63bb285df2f"
FINAL_EXE = "9fc54212d78f113dd2869562976860e2b9d3d0fe96e41ee5361dc19c1e0c9aeb"
FINAL_MAP = "c87f8868d18fb36e934c3a73bf3618fad2bf1dcf46e94ee204273d2ebd8cc811"
VERDICT_LOAD = 0xBB81
VERDICT_SIZE = 0x05C8
VERDICT_LINKED_SHA = "6c4abcf2cf53fdd2e4132233917546de9ff3423b460ca3f392bd8941085c531e"
VERDICT_RAW_SHA = "2d0522052c27bd5c67ae201f2cbd0e16238aa536308e83ac0167ce8ca5b86c90"
EXPECTED_RAW_DIFFS = [0x5C4, 0x5C5]
EXPECTED_MISMATCHES = 140
EXPECTED_CHANGED = list(range(274, 291))
TARGET_SITES_274_290 = [
    0xC142, 0xC13B, 0xC134, 0xC126, 0xC11C, 0xC115, 0xC104,
    0xC0DC, 0xC0D5, 0xC0CE, 0xC0BD, 0xC09E, 0xC097, 0xC08D,
    0xC082, 0xC014, 0xC00B,
]
FIRST_KIND3 = [
    0x15D, 0x14C, 0x110, 0x0DD, 0x0CC,
    0x0BB, 0x0AA, 0x099, 0x088, 0x077,
    0x066, 0x055, 0x044, 0x033, 0x022,
]
SECOND_KIND3_FUSED = [
    0x1C4, 0x1BD, 0x1B6, 0x1A8, 0x19E, 0x197, 0x186,
    0x15E, 0x157, 0x150, 0x13F, 0x120, 0x119, 0x10F, 0x104, 0x096, 0x08D,
]


def segment_bytes(path: Path, segment: str) -> bytes:
    records = parse_omf(path.read_bytes())
    groups = code_ledata(records, segment)
    if not groups:
        return b""
    end = max(row[1] for row in groups)
    out = bytearray(end)
    for start, stop, recno, _ in groups:
        out[start:stop] = records[recno - 1].data[3:]
    return bytes(out)


def kind3_by_record(path: Path) -> list[list[int]]:
    result: list[list[int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type != 0x9C:
            continue
        locs = [loc for kind, loc in fixup_locations(record.data) if kind == 3]
        if locs:
            result.append(locs)
    return result


def prepare_v475(work: Path, output: Path, label: str) -> None:
    prepare_v474(work, output, label)
    split_bb81_owner(work)
    tcc(work, output, f"v475-bb81-{label}", "th04/bb81.cpp")
    tasm(work, output, f"v475-tail-{label}", "th04_maine_01_tail_v475.asm", "m1tail75.obj")
    tasm(work, output, f"v475-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")

    rsp = work / "obj/th04/maine.@l"
    text = rsp.read_text()
    old = r"obj\th04\m1tail74.obj"
    new = r"obj\th04\bb81.obj obj\th04\m1tail75.obj"
    if text.count(old) != 1:
        raise ValueError(f"{label}: v474 tail response token drift")
    rsp.write_text(text.replace(old, new, 1))

    exe = work / "bin/th04/maine.exe"
    map_path = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
        work,
        output / f"v475-link-{label}.log",
    )
    if sha(exe) != V475_EXE or sha(map_path) != V475_MAP:
        raise ValueError(f"{label}: v475 baseline identity drift")
    image = parse_mz(exe.read_bytes())
    if digest(image.program_image) != PROGRAM_SHA:
        raise ValueError(f"{label}: v475 program-image identity drift")


def make_fused_source(work: Path) -> None:
    if sha(BB81_TEMPLATE) != BB81_TEMPLATE_SHA:
        raise ValueError("v475 BB81 template identity drift")
    if sha(ANIMATE_TEMPLATE) != ANIMATE_TEMPLATE_SHA:
        raise ValueError("v476 animate template identity drift")
    fused = BB81_TEMPLATE.read_text().rstrip() + "\n\n" + ANIMATE_TEMPLATE.read_text()
    (work / "th04/vb.cpp").write_text(fused)

    # aUde_pi stays in the v470 rest/data owner; expose a zero-byte C alias.
    rest = work / "th04_maine_rest_v470.asm"
    text = rest.read_bytes().decode("cp932")
    pos = text.index("public ", text.index("\t.data\r\n"))
    line_end = text.index("\r\n", pos)
    if "_aUde_pi" not in text[pos:line_end]:
        text = text[:line_end] + ", _aUde_pi" + text[line_end:]
    needle = "aUde_pi\t\tdb 'ude.pi',0"
    if text.count(needle) != 1:
        raise ValueError("aUde_pi rest label drift")
    text = text.replace(needle, "_aUde_pi label byte\r\n" + needle, 1)
    rest.write_bytes(text.encode("cp932"))


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
    target_verdict = target.program_image[VERDICT_LOAD:VERDICT_LOAD + VERDICT_SIZE]
    if digest(target_verdict) != VERDICT_LINKED_SHA:
        raise ValueError("target fused verdict identity drift")

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        prepare_v475(work, output, label)
        baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes())
        baseline_sites = [row.linear for row in baseline.relocations]
        if sum(a != b for a, b in zip(baseline_sites, target_sites)) != V475_MISMATCHES:
            raise ValueError(f"{label}: v475 ordered frontier drift")
        old_code = (
            segment_bytes(work / "obj/th04/bb81.obj", "MAINE_01_TEXT")
            + segment_bytes(work / "obj/th04/m1tail75.obj", "MAINE_01_TEXT")
        )
        if len(old_code) != VERDICT_SIZE:
            raise ValueError(f"{label}: v475 concatenated verdict size drift")

        make_fused_source(work)
        tcc(work, output, f"v476-verdict-fused-{label}", "th04/vb.cpp")
        tasm(work, output, f"v476-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")

        obj = work / "obj/th04/vb.obj"
        fused = segment_bytes(obj, "MAINE_01_TEXT")
        if len(fused) != VERDICT_SIZE or digest(fused) != VERDICT_RAW_SHA:
            raise ValueError(f"{label}: fused verdict raw identity drift")
        diffs = [i for i, (left, right) in enumerate(zip(fused, old_code)) if left != right]
        if diffs != EXPECTED_RAW_DIFFS:
            raise ValueError(f"{label}: fused raw differences drift: {diffs}")
        records = kind3_by_record(obj)
        if records != [FIRST_KIND3, SECOND_KIND3_FUSED]:
            raise ValueError(f"{label}: fused kind-3 order drift: {records}")

        rsp = work / "obj/th04/maine.@l"
        text = rsp.read_text()
        old = r"obj\th04\bb81.obj obj\th04\m1tail75.obj"
        new = r"obj\th04\vb.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: v475 owner pair drift")
        rsp.write_text(text.replace(old, new, 1))

        exe = work / "bin/th04/maine.exe"
        map_path = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True)
        map_path.unlink(missing_ok=True)
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work,
            output / f"v476-link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        sites = [row.linear for row in image.relocations]
        payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image or digest(image.program_image) != PROGRAM_SHA:
            raise ValueError(f"{label}: fused verdict changed linked program bytes")
        linked = image.program_image[VERDICT_LOAD:VERDICT_LOAD + VERDICT_SIZE]
        if linked != target_verdict:
            raise ValueError(f"{label}: fused verdict linked slice is not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation-site multiset drift")
        changed = [i for i, (a, b) in enumerate(zip(baseline_sites, sites)) if a != b]
        if changed != EXPECTED_CHANGED:
            raise ValueError(f"{label}: changed relocation indices drift: {changed}")
        if sites[274:291] != TARGET_SITES_274_290 or target_sites[274:291] != TARGET_SITES_274_290:
            raise ValueError(f"{label}: fused verdict target-order block drift")
        ordered = sum(a != b for a, b in zip(sites, target_sites))
        if ordered != EXPECTED_MISMATCHES:
            raise ValueError(f"{label}: v476 ordered frontier drift: {ordered}")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: v476 final identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "fused_raw_sha256": digest(fused),
            "fused_linked_sha256": digest(linked),
            "fused_size": len(fused),
            "raw_differences_vs_v475_split": diffs,
            "kind3_records": records,
            "changed_indices_vs_v475": changed,
            "target_exact_sites_274_290": sites[274:291],
            "ordered_relocation_mismatches": ordered,
            "same_index_relocations": len(sites) - ordered,
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256", "fused_raw_sha256",
        "fused_linked_sha256", "fused_size", "raw_differences_vs_v475_split",
        "kind3_records", "changed_indices_vs_v475", "target_exact_sites_274_290",
        "ordered_relocation_mismatches", "same_index_relocations",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B v476 {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE fused sub_BB81 + verdict_animate natural-C++ linked-exact relocation-order replay",
        "source_baseline": V401_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "bb81_template": str(BB81_TEMPLATE.relative_to(ROOT)),
        "animate_template": str(ANIMATE_TEMPLATE.relative_to(ROOT)),
        "animate_template_sha256": ANIMATE_TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "verdict_animate alone is 0x51 raw-CODE exact under TC86. Fusing it with the already exact sub_BB81 source into one 0x5C8 TC86 TU preserves the complete linked MAINE program image and makes target relocation indices 274..290 exact. The fused raw CODE differs from the old two-owner concatenation only at the two-byte near-call displacement from verdict_animate to same-TU sub_BB81; the split TASM owner carried a zero addend plus FIXUPP and links to identical bytes. TC86 emits the higher-address animate segment fixups before BB81's second record, reducing ordered MAINE residual 157 to 140 with the 559-site multiset unchanged."
        ),
        "limit": (
            "aUde_pi remains physically owned by the v470 rest/data object and is exposed through a zero-byte _aUde_pi alias. No executable/data address changes. This closes the adjacent verdict run but not the remaining earlier MAINE_01 producer order, SCORE_TEXT internal order, or BGIMAGE direction."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "fused_verdict_linked_exact": True,
        "ordered_relocation_mismatches": EXPECTED_MISMATCHES,
        "same_index_relocations": 559 - EXPECTED_MISMATCHES,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
