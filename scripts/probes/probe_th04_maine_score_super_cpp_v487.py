#!/usr/bin/env python3
"""Recover the historical TH04 MAINE SCORE_TEXT physical TC86 producer.

The accepted v486 source closes every SCORE executable byte but not packed
relocation order. This replay restores the larger physical producer by compiling
score_d + score_hi + the full v486 SCORE body as one grouped SCORE_TEXT TC86 TU.
The preceding 0x269 code shifts TC86 LEDATA/FIXUPP batching naturally; no OMF or
MZ relocation bytes are edited.
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

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from inspect_dialog_fixup_order import code_ledata, omf_index  # noqa: E402
from probe_th04_maine_score_full_cpp_v486 import (  # noqa: E402
    TEMPLATE as SCORE_TEMPLATE,
    TEMPLATE_SHA as SCORE_TEMPLATE_SHA,
    add_score_aliases,
)
from probe_th04_maine_score_insert_cpp_v479 import validate_v478_source  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import EXPECTED_MISMATCHES as V478_MISMATCHES, segment_bytes  # noqa: E402
from probe_th04_master_object_split import compare, sha  # noqa: E402
from probe_th04_maine_score_rect_cpp_v484 import raw_segment_bytes  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_score_super_v487.cpp.in"
TEMPLATE_SHA = "9082aff7bbc7a39ed84d05b124343ca110df4d3000d629df1ebe14f43ca1faff"
FINAL_EXE = "b8aa92ccea28a435a17e6bd9bab39507b851cbaa6ece281552daa553efbd411f"
FINAL_MAP = "f4581d687d59e880962cee121a1edbb5246e248fff82b851319ac2522210455a"
SCORE_LOAD = 0xC149
SCORE_CODE_SIZE = 0x0B30
SCORE_RAW_SHA = "d8180ee4acb342cefe168337bb6dff4986b6bac625a4c614128c1b9430cec693"
SCORE_LINKED_SHA = "a7ccdd75806f46444a768186f6661ba31c69bd7bdb3163229428488860db24a0"
PAD_SIZE = 1
EXPECTED_MISMATCHES = 8
EXPECTED_SAME = 551
EXPECTED_REMAINING = list(range(80, 88))
EXPECTED_BGIMAGE_CANDIDATE = [0xD6ED,0xD6E4,0xD6DB,0xD6D2,0xD656,0xD64B,0xD640,0xD635]
EXPECTED_BGIMAGE_TARGET = [0xD635,0xD640,0xD64B,0xD656,0xD6D2,0xD6DB,0xD6E4,0xD6ED]
EXPECTED_RAW_DIFFS_VS_SPLIT = [0x153,0x154,0x1B8,0x1B9,0x237,0x238]
EXPECTED_KIND3_RECORDS = [
    [0x262,0x257,0x24B,0x232,0x226,0x20F,0x203,0x1EF,0x1D9,0x1B3,0x1AE,0x1A2,0x18F,0x179,0x16C,0x15C,0x14E,0x13B,0x82,0x7A],
    [0x3BC,0x3AB,0x31E,0x315,0x30E,0x300,0x2F6,0x2EF,0x2DE,0x2C1,0x25E,0x238,0x20F,0x1BE,0x197,0x182,0x112,0xFE,0x8D,0x64,0x3C],
    [0x329,0x250,0x249,0x244,0x23F,0x22D,0x226,0xB1,0xA7,0x9B,0x75,0x36,0x2F,0x28,0x1C],
]


def score_bytes_by_seg_index(path: Path) -> bytes:
    records = parse_omf(path.read_bytes())
    names = [""]
    segs: list[str] = []
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                n = record.data[pos]
                names.append(record.data[pos+1:pos+1+n].decode("latin1"))
                pos += n + 1
        elif record.record_type == 0x98:
            data = record.data
            pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            name_i, pos = omf_index(data, pos)
            segs.append(names[name_i])
    chunks: dict[int, list[tuple[int, bytes]]] = {}
    for record in records:
        if record.record_type != 0xA0:
            continue
        seg_i, pos = omf_index(record.data, 0)
        offset = int.from_bytes(record.data[pos:pos+2], "little")
        chunks.setdefault(seg_i, []).append((offset, record.data[pos+2:]))
    score_indices = [i for i in chunks if segs[i-1] == "SCORE_TEXT"]
    if len(score_indices) != 1:
        raise ValueError(f"expected one SCORE_TEXT SEGDEF with data, got {score_indices}")
    rows = chunks[score_indices[0]]
    end = max(offset + len(data) for offset, data in rows)
    out = bytearray(end)
    for offset, data in rows:
        out[offset:offset+len(data)] = data
    return bytes(out)


def kind3_records(path: Path) -> list[list[int]]:
    records = parse_omf(path.read_bytes())
    names = [""]
    segs: list[str] = []
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                n = record.data[pos]
                names.append(record.data[pos+1:pos+1+n].decode("latin1"))
                pos += n + 1
        elif record.record_type == 0x98:
            data = record.data; pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            name_i, pos = omf_index(data, pos); segs.append(names[name_i])
    result: list[list[int]] = []
    last_seg: int | None = None
    for record in records:
        if record.record_type == 0xA0:
            last_seg, _ = omf_index(record.data, 0)
        elif record.record_type == 0x9C and last_seg is not None and segs[last_seg-1] == "SCORE_TEXT":
            locs = [loc for kind, loc in fixup_locations(record.data) if kind == 3]
            if locs:
                result.append(locs)
    return result


def compile_hygiene(work: Path) -> None:
    for rel, guard in (
        ("th04/formats/scoredat/scoredat.hpp", "V487_SCOREDAT_HPP_GUARD"),
        ("th04/gaiji/gaiji.h", "V487_GAIJI_H_GUARD"),
    ):
        path = work / rel
        text = path.read_text()
        if not text.startswith("#ifndef " + guard):
            path.write_text(f"#ifndef {guard}\n#define {guard}\n" + text + "\n#endif\n")
    for rel in (
        "th04/formats/scoredat/decode.cpp",
        "th04/formats/scoredat/encode.cpp",
        "th04/formats/scoredat/recreate.cpp",
    ):
        path = work / rel
        text = path.read_text()
        needle = "#pragma option -zCSCORE_TEXT\n"
        if text.count(needle) == 1:
            path.write_text(text.replace(needle, "", 1))
        elif text.count(needle) != 0:
            raise ValueError(f"{rel}: SCORE pragma count drift")

    # The top-level v487 template establishes one grouped SCORE_TEXT SEGDEF.
    # Remove the v486 per-function reopen/reset pragmas so all later code stays
    # in that same physical segment contribution.
    path = work / "th04/score86.cpp"
    text = path.read_text()
    text = text.replace("#pragma codeseg SCORE_TEXT score_01\n", "")
    text = text.replace("#pragma codeseg\n", "")
    path.write_text(text)


def add_pad(work: Path) -> None:
    pad = (
        "\t.386\r\n\t.model use16 large _TEXT\r\n\r\n"
        "SCORE_TEXT segment byte public 'CODE' use16\r\n"
        "\tdb 0\r\n"
        "SCORE_TEXT ends\r\n\tend\r\n"
    )
    (work / "th04_maine_score_pad_v487.asm").write_bytes(pad.encode("ascii"))


def rewrite_response(work: Path) -> None:
    rsp = work / "obj/th04/maine.@l"
    tokens = rsp.read_text().split()
    score_d = r"obj\th04\score_d.obj"
    score_hi = r"obj\th04\score_hi.obj"
    mainscv = r"obj\th04\mainscv.obj"
    for token in (score_d, score_hi, mainscv):
        if tokens.count(token) != 1:
            raise ValueError(f"response token drift for {token}: {tokens.count(token)}")
    tokens.remove(score_d)
    index = tokens.index(score_hi)
    if tokens[index:index+2] != [score_hi, mainscv]:
        raise ValueError("score_hi/mainscv adjacency drift")
    tokens[index:index+2] = [r"obj\th04\scoreall.obj", r"obj\th04\mscp87.obj"]
    rsp.write_text(" ".join(tokens) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source = args.source_dir.resolve(); target_path = args.target_restored.resolve(); output = output_dir(args.output_dir)

    if sha(RUNNER) != RUNNER_SHA:
        raise ValueError("runner identity drift")
    validate_v478_source(source)
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("target restore identity drift")
    if sha(SCORE_TEMPLATE) != SCORE_TEMPLATE_SHA:
        raise ValueError("v486 SCORE template identity drift")
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v487 super-TU template identity drift")

    baseline = parse_mz((source / "bin/th04/maine.exe").read_bytes())
    baseline_sites = [r.linear for r in baseline.relocations]
    target = parse_mz(target_path.read_bytes()); target_sites = [r.linear for r in target.relocations]
    if sum(a != b for a, b in zip(baseline_sites, target_sites)) != V478_MISMATCHES:
        raise ValueError("v478 ordered frontier drift")
    target_score = target.program_image[SCORE_LOAD:SCORE_LOAD+SCORE_CODE_SIZE]
    if digest(target_score) != SCORE_LINKED_SHA:
        raise ValueError("target complete SCORE identity drift")

    # Separate-object raw reference for same-TU addend diagnosis.
    split_raw = (
        segment_bytes(source / "obj/th04/score_d.obj", "SCORE_TEXT")
        + segment_bytes(source / "obj/th04/score_hi.obj", "SCORE_TEXT")
        + score_bytes_by_seg_index(source / "obj/th04/mainscv.obj")[:0]  # placeholder; replaced below per work after copying v486 source
    )

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        shutil.copy2(SCORE_TEMPLATE, work / "th04/score86.cpp")
        shutil.copy2(TEMPLATE, work / "th04/scoreall.cpp")
        compile_hygiene(work)
        add_score_aliases(work)
        add_pad(work)
        tcc(work, output, f"v487-scoreall-{label}", "th04/scoreall.cpp")
        tasm(work, output, f"v487-rest-{label}", "th04_maine_rest_v470.asm", "mainerest.obj")
        tasm(work, output, f"v487-pad-{label}", "th04_maine_score_pad_v487.asm", "mscp87.obj")

        obj = work / "obj/th04/scoreall.obj"
        code = score_bytes_by_seg_index(obj)
        pad = raw_segment_bytes(work / "obj/th04/mscp87.obj", "SCORE_TEXT")
        if len(code) != SCORE_CODE_SIZE or digest(code) != SCORE_RAW_SHA:
            raise ValueError(f"{label}: super-TU SCORE raw identity drift")
        if pad != b"\x00":
            raise ValueError(f"{label}: SCORE pad drift")
        records = kind3_records(obj)
        if records != EXPECTED_KIND3_RECORDS:
            raise ValueError(f"{label}: super-TU FIXUPP topology drift: {records}")

        # Compare the first 0x269 bytes against the previously split score_d + score_hi
        # producer. Six raw bytes are expected to differ only because same-TU local
        # offset references no longer need external OMF addends.
        split_prefix = (
            segment_bytes(source / "obj/th04/score_d.obj", "SCORE_TEXT")
            + segment_bytes(source / "obj/th04/score_hi.obj", "SCORE_TEXT")
        )
        prefix_diffs = [i for i,(a,b) in enumerate(zip(code[:len(split_prefix)], split_prefix)) if a != b]
        if prefix_diffs != EXPECTED_RAW_DIFFS_VS_SPLIT:
            raise ValueError(f"{label}: super-TU prefix addend drift: {prefix_diffs}")

        rewrite_response(work)
        exe = work / "bin/th04/maine.exe"; mp = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"], work, output / f"v487-link-{label}.log")
        image = parse_mz(exe.read_bytes()); sites = [r.linear for r in image.relocations]; payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image:
            raise ValueError(f"{label}: super-TU changed linked program bytes")
        linked_score = image.program_image[SCORE_LOAD:SCORE_LOAD+SCORE_CODE_SIZE]
        if linked_score != target_score:
            raise ValueError(f"{label}: linked complete SCORE slice is not target exact")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation multiset drift")
        if sites[291:347] != target_sites[291:347]:
            raise ValueError(f"{label}: SCORE relocation block is not target-index exact")
        ordered = sum(a != b for a,b in zip(sites,target_sites))
        remaining = [i for i,(a,b) in enumerate(zip(sites,target_sites)) if a != b]
        if ordered != EXPECTED_MISMATCHES or remaining != EXPECTED_REMAINING:
            raise ValueError(f"{label}: v487 frontier drift: {ordered}, {remaining}")
        if sites[80:88] != EXPECTED_BGIMAGE_CANDIDATE or target_sites[80:88] != EXPECTED_BGIMAGE_TARGET:
            raise ValueError(f"{label}: remaining BGIMAGE block drift")
        if sha(exe) != FINAL_EXE or sha(mp) != FINAL_MAP:
            raise ValueError(f"{label}: output identity drift")

        builds[label] = {
            "exe_sha256": sha(exe), "map_sha256": sha(mp), "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload, "score_raw_sha256": digest(code), "score_linked_sha256": digest(linked_score),
            "score_code_size": len(code), "score_pad_size": len(pad), "prefix_raw_differences_vs_split": prefix_diffs,
            "kind3_records": records, "score_relocations_target_index_exact": True,
            "ordered_relocation_mismatches": ordered, "same_index_relocations": len(sites)-ordered,
            "remaining_mismatch_indices": remaining, "remaining_bgimage_candidate_sites": sites[80:88],
            "remaining_bgimage_target_sites": target_sites[80:88],
        }

    for key in (
        "exe_sha256","map_sha256","program_image_sha256","score_raw_sha256","score_linked_sha256","score_code_size",
        "score_pad_size","prefix_raw_differences_vs_split","kind3_records","score_relocations_target_index_exact",
        "ordered_relocation_mismatches","same_index_relocations","remaining_mismatch_indices",
        "remaining_bgimage_candidate_sites","remaining_bgimage_target_sites",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE historical SCORE_TEXT physical TC86 producer and packed relocation-order closure",
        "v478_source_exe_sha256": sha(source / "bin/th04/maine.exe"),
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "score_source_template": str(SCORE_TEMPLATE.relative_to(ROOT)),
        "score_source_template_sha256": SCORE_TEMPLATE_SHA,
        "super_tu_template": str(TEMPLATE.relative_to(ROOT)),
        "super_tu_template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "Compiling score_d + score_hi + the complete v486 SCORE body in one grouped SCORE_TEXT TC86 translation unit restores the target physical producer. The preceding 0x269 bytes shift TC86 LEDATA/FIXUPP batching to 0x000..0x3FF, 0x400..0x7FC, and 0x7FD..0xB2F. A single top-level #pragma codeseg SCORE_TEXT score_01 keeps the combined SEGDEF in SCORE_01, preserving group-relative local offset fixups needed by regist_menu's switch table. Linked program bytes remain byte-identical to v478, the 559-site relocation multiset remains exact, and every SCORE relocation at target indices 291..346 becomes target-index exact. Ordered MAINE residual falls 42 to 8."
        ),
        "remaining": (
            "The only remaining MAINE ordered relocation differences are indices 80..87, the shared BGIMAGE eight-entry reverse. The shared snd_load 2-byte payload encoding remains an independent program-byte residual and is unchanged by this packet."
        ),
        "limit": (
            "Temporary include guards and duplicate same-segment pragma suppression are compile-scaffold hygiene for testing the larger historical TU with the maintained ReC98 source tree; no function body, OMF record, MZ relocation, or target byte is patched."
        ),
    }
    rp = output / "receipt.json"; rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp), "receipt_sha256": sha(rp), "candidate_sha256": FINAL_EXE,
        "score_relocations_target_index_exact": True, "ordered_relocation_mismatches": EXPECTED_MISMATCHES,
        "same_index_relocations": EXPECTED_SAME,
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
