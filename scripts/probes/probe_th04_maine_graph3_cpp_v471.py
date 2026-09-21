#!/usr/bin/env python3
"""Recover TH04 MAINE graph_3_digit_put() as natural TC86 C++.

The v470 packet established a byte-stable source-level MAINE_01_TEXT owner.
This replay splits that owner at the existing graph_3_digit_put() function
boundary into TASM prefix / TC86 C++ function / TASM suffix contributions.
Only the compiler-generated C++ public spelling is exposed across the new
object boundary; no linked code, OMF record, or MZ relocation byte is patched.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_master_relocation_order import (  # noqa: E402
    BASE as V401_BASE,
    NEW_EXE as V425_EXE,
    NEW_MAP as V425_MAP,
    patch as apply_v425,
)
from probe_th04_maine_score_producers_v468 import (  # noqa: E402
    RUNNER,
    RUNNER_SHA,
    TARGET_RESTORED_SHA,
    apply_producer_sources,
    digest,
    run_checked,
)
from probe_th04_maine_segment_topology_v470 import (  # noqa: E402
    FINAL_EXE as V470_EXE,
    FINAL_MAP as V470_MAP,
    PROGRAM_SHA,
    EXPECTED_ORDERED_MISMATCHES,
    apply_target_owner_order,
    generate_split_sources,
    output_dir,
    tasm,
    tcc,
)
from probe_th04_master_object_split import build, compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_graph3_v471.cpp.in"
TEMPLATE_SHA = "1d89385905a3cbb6db2f80b099205e18422ca841cd59f5cb2b6d748d814d453d"
FINAL_MAP = "d15028081d0104843c53802d17c95747b6c7741bdc500ee94af93911e1eda720"
GRAPH_LOAD = 0x1737
GRAPH_LOCAL_OFFSET = 0x08B7
GRAPH_SIZE = 0x0096
GRAPH_LINKED_SHA = "7149fdd7c6a73eca991d4fb22d3d25f50640228cc368fe64d10ad6ed8a07a85e"
GRAPH_RAW_SHA = "05578d60d4e8b2ca86099ee54ac504e626074bb06b32248f8bb833b7770474a0"
GRAPH_FIXUPS = [(3, 0x8D), (1, 0x59), (1, 0x24)]
PREFIX_SIZE = 0x08B7
SUFFIX_SIZE = 0x092C
BASE_MAINE01_SIZE = 0x1279


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


def prepare_v470(work: Path, output: Path, label: str) -> None:
    apply_v425(work)
    build(work, output / f"v425-build-{label}.log")
    if sha(work / "bin/th04/maine.exe") != V425_EXE or sha(work / "obj/th04/maine.map") != V425_MAP:
        raise ValueError(f"{label}: v425 baseline identity drift")

    apply_producer_sources(work)
    generate_split_sources(work)
    for asm, obj in (
        ("th04_maine_01_v470.asm", "maine01v.obj"),
        ("th04_maine_score_v470.asm", "mainscv.obj"),
        ("th04_maine_rest_v470.asm", "mainerest.obj"),
        ("th04_maine_master_data_tail.asm", "mainemdata.obj"),
    ):
        tasm(work, output, f"v470-{Path(asm).stem}-{label}", asm, obj)
    for cpp in ("th04/sndlext.cpp", "th04/score_hi.cpp"):
        tcc(work, output, f"v470-{Path(cpp).stem}-{label}", cpp)
    apply_target_owner_order(work)
    exe = work / "bin/th04/maine.exe"
    map_path = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
        work,
        output / f"v470-link-{label}.log",
    )
    if sha(exe) != V470_EXE or sha(map_path) != V470_MAP:
        raise ValueError(f"{label}: v470 baseline identity drift")


def split_graph_owner(work: Path) -> None:
    source = work / "th04_maine_01_v470.asm"
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
        raise ValueError(f"MAINE_01 segment occurrence drift: {positions}")
    real = positions[1]
    end_marker = "maine_01_TEXT ends"
    seg_end = text.index(end_marker, real)
    common = text[:real]
    body = text[real + len(seg):seg_end]
    graph_start = body.index("public @GRAPH_3_DIGIT_PUT$QIIU")
    graph_end = body.index("@graph_3_digit_put$qiiu\tendp", graph_start)
    graph_end += len("@graph_3_digit_put$qiiu\tendp")
    prefix_body = body[:graph_start]
    suffix_body = body[graph_end:]

    prefix = common + seg + prefix_body + end_marker + "\r\n\tend\r\n"
    assume = (
        "\r\n\t\tassume cs:group_01\r\n"
        "\t\tassume es:nothing, ss:nothing, ds:_DATA, fs:nothing, gs:nothing\r\n"
    )
    suffix = common + seg + assume + suffix_body + end_marker + "\r\n\tend\r\n"
    # The maintained C++ shell uses uint16_t, which TC86 naturally exports as
    # ...$QIIUI.  The reconstructed TASM scaffold used ...$QIIU; this symbol
    # spelling is not executable data.  Adapt only the source-level interface.
    suffix = suffix.replace("@graph_3_digit_put$qiiu", "@graph_3_digit_put$qiiui")
    text_end = suffix.index("_TEXT ends\r\n") + len("_TEXT ends\r\n")
    suffix = (
        suffix[:text_end]
        + "\r\n\textern @GRAPH_3_DIGIT_PUT$QIIUI:near\r\n"
        + suffix[text_end:]
    )
    (work / "th04_maine_01_pre_v471.asm").write_bytes(prefix.encode("cp932"))
    (work / "th04_maine_01_post_v471.asm").write_bytes(suffix.encode("cp932"))

    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("graph3 template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/g3.cpp")


def graph_fixups(path: Path) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            found.extend(fixup_locations(record.data))
    return found


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
        raise ValueError("v228 target-restored identity drift")
    target = parse_mz(target_path.read_bytes())
    target_sites = [row.linear for row in target.relocations]
    target_graph = target.program_image[GRAPH_LOAD:GRAPH_LOAD + GRAPH_SIZE]
    if digest(target_graph) != GRAPH_LINKED_SHA:
        raise ValueError("target graph3 identity drift")

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        prepare_v470(work, output, label)
        baseline = parse_mz((work / "bin/th04/maine.exe").read_bytes())
        baseline_sites = [row.linear for row in baseline.relocations]
        baseline_owner = segment_bytes(work / "obj/th04/maine01v.obj", "MAINE_01_TEXT")
        if len(baseline_owner) != BASE_MAINE01_SIZE:
            raise ValueError(f"{label}: v470 MAINE_01 size drift")
        old_graph = baseline_owner[GRAPH_LOCAL_OFFSET:GRAPH_LOCAL_OFFSET + GRAPH_SIZE]

        split_graph_owner(work)
        tasm(work, output, f"graph3-pre-{label}", "th04_maine_01_pre_v471.asm", "m1pre.obj")
        tasm(work, output, f"graph3-post-{label}", "th04_maine_01_post_v471.asm", "m1post.obj")
        tcc(work, output, f"graph3-cpp-{label}", "th04/g3.cpp")

        prefix = segment_bytes(work / "obj/th04/m1pre.obj", "MAINE_01_TEXT")
        graph = segment_bytes(work / "obj/th04/g3.obj", "MAINE_01_TEXT")
        suffix = segment_bytes(work / "obj/th04/m1post.obj", "MAINE_01_TEXT")
        if (len(prefix), len(graph), len(suffix)) != (PREFIX_SIZE, GRAPH_SIZE, SUFFIX_SIZE):
            raise ValueError(f"{label}: split owner sizes drift")
        if len(prefix) + len(graph) + len(suffix) != BASE_MAINE01_SIZE:
            raise ValueError(f"{label}: split owner total size drift")
        if digest(graph) != GRAPH_RAW_SHA:
            raise ValueError(f"{label}: natural graph3 raw CODE drift")
        raw_diffs = [i for i, (left, right) in enumerate(zip(graph, old_graph)) if left != right]
        if raw_diffs:
            raise ValueError(f"{label}: graph3 raw CODE is not exact: {raw_diffs}")
        fixups = graph_fixups(work / "obj/th04/g3.obj")
        if fixups != GRAPH_FIXUPS:
            raise ValueError(f"{label}: graph3 FIXUPP order drift: {fixups}")

        rsp = work / "obj/th04/maine.@l"
        text = rsp.read_text()
        old = r"obj\th04\maine01v.obj"
        new = r"obj\th04\m1pre.obj obj\th04\g3.obj obj\th04\m1post.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: v470 MAINE_01 response token drift")
        rsp.write_text(text.replace(old, new, 1))
        exe = work / "bin/th04/maine.exe"
        map_path = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True)
        map_path.unlink(missing_ok=True)
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work,
            output / f"graph3-link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        sites = [row.linear for row in image.relocations]
        payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image or digest(image.program_image) != PROGRAM_SHA:
            raise ValueError(f"{label}: graph3 owner replacement changed linked program bytes")
        if sites != baseline_sites:
            raise ValueError(f"{label}: graph3 replacement changed relocation table")
        ordered = sum(left != right for left, right in zip(sites, target_sites))
        if ordered != EXPECTED_ORDERED_MISMATCHES:
            raise ValueError(f"{label}: graph3 changed v470 relocation frontier: {ordered}")
        linked_graph = image.program_image[GRAPH_LOAD:GRAPH_LOAD + GRAPH_SIZE]
        if linked_graph != target_graph:
            raise ValueError(f"{label}: linked graph3 body is not target exact")
        if sha(exe) != V470_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: v471 final identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "ordered_relocation_mismatches": ordered,
            "relocation_table_unchanged_vs_v470": sites == baseline_sites,
            "graph_load": GRAPH_LOAD,
            "graph_size": GRAPH_SIZE,
            "graph_linked_sha256": digest(linked_graph),
            "graph_raw_sha256": digest(graph),
            "graph_raw_differences_vs_tasm_owner": raw_diffs,
            "graph_fixupp_locations": [[kind, loc] for kind, loc in fixups],
            "prefix_size": len(prefix),
            "suffix_size": len(suffix),
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256",
        "ordered_relocation_mismatches", "relocation_table_unchanged_vs_v470",
        "graph_linked_sha256", "graph_raw_sha256",
        "graph_raw_differences_vs_tasm_owner", "graph_fixupp_locations",
        "prefix_size", "suffix_size",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B v471 {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE graph_3_digit_put natural-C++ linked-exact function replay",
        "source_baseline": V401_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "Natural TC86 C++ emits a 0x96-byte graph_3_digit_put body that is 150/150 raw CODE exact against the already-source-split v470 MAINE_01 owner. Splitting that owner at this function boundary into TASM prefix + C++ body + TASM suffix and preserving the near-call ABI keeps the entire linked MAINE program image and all 559 relocation entries byte-for-byte unchanged. The linked 150-byte function is target exact."
        ),
        "limit": (
            "TC86 naturally mangles the maintained uint16_t signature as @GRAPH_3_DIGIT_PUT$QIIUI, while the reconstructed TASM scaffold used @GRAPH_3_DIGIT_PUT$QIIU. The replay adapts only this source-level symbolic interface in the suffix; symbol names are not executable target bytes. This function has only one segment relocation, so recovering it does not by itself reduce the v470 178-entry ordered relocation residual."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": V470_EXE,
        "graph_linked_exact": True,
        "graph_size": GRAPH_SIZE,
        "ordered_relocation_mismatches": EXPECTED_ORDERED_MISMATCHES,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
