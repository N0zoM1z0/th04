#!/usr/bin/env python3
"""Recover TH04 MAINE SCORE_TEXT EGC rectangle copy as natural TC86 C++.

The exact low-level EGC-start helper remains assembly-owned. This replay starts
from the retained v478 MAINE source snapshot, splits only the final SCORE_TEXT
rectangle-copy function, recompiles it as C++, preserves the original one-byte
segment pad, and requires the complete linked image and relocation table to
remain byte-for-byte unchanged.
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

from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from replay_th04_scroll_driver_natural import omf_index  # noqa: E402
from probe_th04_maine_score_insert_cpp_v479 import validate_v478_source  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, TARGET_RESTORED_SHA, digest, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import output_dir, tasm, tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import FINAL_EXE as V478_EXE, EXPECTED_MISMATCHES as V478_MISMATCHES, segment_bytes  # noqa: E402
from probe_th04_master_object_split import compare, sha  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_maine_score_rect_v484.cpp.in"
TEMPLATE_SHA = "6953a64f8e91ae86635e21efb50e0bd457b78f7b73536a6555de8ad5968cfd87"
FINAL_EXE = V478_EXE
FINAL_MAP = "162d50edd4600047c1cb922a49c842a5ba40adedd091c56395bc0781b70654a3"
FUNCTION_LOAD = 0xCBF3
FUNCTION_SIZE = 0x0086
FUNCTION_RAW_SHA = "d0b6cdfac6dbbf9f4ac811380e98d216bec149b7c8536b3a8a4831bfdf9e50c4"
REFERENCE_RAW_SHA = "0ebee695c345052db9d40e8b55e0ee7c9eef50322315209cd2d7c52c849b48a9"
FUNCTION_LINKED_SHA = "86b8046d73b79655f913d1b7f62c34db3a3f6d43ffc168b9a4c855e78b7d7d2f"
RAW_DIFFS = [0x0A, 0x0B]
SCORE_HEAD_SIZE = 0x0841
PAD_SIZE = 1
EXPECTED_MISMATCHES = 42


def raw_segment_bytes(path: Path, wanted: str) -> bytes:
    """Read LEDATA even when an object has no following FIXUPP record."""
    records = parse_omf(path.read_bytes())
    names = [""]
    segments: list[str] = []
    pieces: list[tuple[int, bytes]] = []
    for record in records:
        if record.record_type == 0x96:  # LNAMES
            pos = 0
            while pos < len(record.data):
                size = record.data[pos]
                names.append(record.data[pos + 1:pos + 1 + size].decode("latin1"))
                pos += size + 1
        elif record.record_type == 0x98:  # SEGDEF
            data = record.data
            pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            name_index, pos = omf_index(data, pos)
            segments.append(names[name_index])
    for record in records:
        if record.record_type != 0xA0:  # LEDATA
            continue
        seg_index, pos = omf_index(record.data, 0)
        offset = int.from_bytes(record.data[pos:pos + 2], "little")
        payload = record.data[pos + 2:]
        if segments[seg_index - 1] == wanted:
            pieces.append((offset, payload))
    if not pieces:
        return b""
    end = max(offset + len(payload) for offset, payload in pieces)
    out = bytearray(end)
    for offset, payload in pieces:
        out[offset:offset + len(payload)] = payload
    return bytes(out)


def split_score_owner(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v484 template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/rect84.cpp")

    source = work / "th04_maine_score_v470.asm"
    text = source.read_bytes().decode("cp932")
    old_call = "\t\tcall\tsub_CBF3\r\n"
    if text.count(old_call) != 1:
        raise ValueError("score_rect_copy call anchor drift")
    text = text.replace(old_call, "\t\tcall\t@SCORE_RECT_COPY$QIIII\r\n", 1)

    seg = "SCORE_TEXT segment byte public 'CODE' use16"
    empty = seg + "\r\nSCORE_TEXT ends"
    repl = seg + "\r\n\textern @SCORE_RECT_COPY$QIIII:near\r\nSCORE_TEXT ends"
    if text.count(empty) != 1:
        raise ValueError("empty SCORE declaration drift")
    text = text.replace(empty, repl, 1)

    start_helper = "_egc_start_copy_inlined\tproc near\r\n"
    if text.count(start_helper) != 1:
        raise ValueError("EGC start helper drift")
    text = text.replace(
        start_helper,
        "public @score_egc_start_copy$qv\r\n"
        "@score_egc_start_copy$qv label near\r\n" + start_helper,
        1,
    )

    cut = text.index("sub_CBF3\tproc near")
    head = text[:cut].rstrip("\r\n") + "\r\n\r\nSCORE_TEXT\tends\r\n\tend\r\n"
    (work / "th04_maine_score_head_v484.asm").write_bytes(head.encode("cp932"))

    pad = (
        "\t.386\r\n\t.model use16 large _TEXT\r\n\r\n"
        "SCORE_TEXT segment byte public 'CODE' use16\r\n"
        "\tdb 0\r\n"
        "SCORE_TEXT ends\r\n\tend\r\n"
    )
    (work / "th04_maine_score_pad_v484.asm").write_bytes(pad.encode("ascii"))


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
        raise ValueError("runner identity drift")
    validate_v478_source(source)
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("target restore identity drift")

    baseline = parse_mz((source / "bin/th04/maine.exe").read_bytes())
    baseline_sites = [r.linear for r in baseline.relocations]
    target = parse_mz(target_path.read_bytes())
    target_sites = [r.linear for r in target.relocations]
    if sum(a != b for a, b in zip(baseline_sites, target_sites)) != V478_MISMATCHES:
        raise ValueError("v478 ordered frontier drift")

    old_score = segment_bytes(source / "obj/th04/mainscv.obj", "SCORE_TEXT")
    old_function = old_score[SCORE_HEAD_SIZE:SCORE_HEAD_SIZE + FUNCTION_SIZE]
    if len(old_function) != FUNCTION_SIZE or digest(old_function) != REFERENCE_RAW_SHA:
        raise ValueError("v478 score_rect_copy raw identity drift")
    target_function = target.program_image[FUNCTION_LOAD:FUNCTION_LOAD + FUNCTION_SIZE]
    if digest(target_function) != FUNCTION_LINKED_SHA:
        raise ValueError("target score_rect_copy linked identity drift")

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        split_score_owner(work)
        tcc(work, output, f"v484-score-rect-{label}", "th04/rect84.cpp")
        tasm(work, output, f"v484-score-head-{label}", "th04_maine_score_head_v484.asm", "msch84.obj")
        tasm(work, output, f"v484-score-pad-{label}", "th04_maine_score_pad_v484.asm", "mscp84.obj")

        cpp = segment_bytes(work / "obj/th04/rect84.obj", "SCORE_TEXT")
        head = segment_bytes(work / "obj/th04/msch84.obj", "SCORE_TEXT")
        pad = raw_segment_bytes(work / "obj/th04/mscp84.obj", "SCORE_TEXT")
        if len(cpp) != FUNCTION_SIZE or digest(cpp) != FUNCTION_RAW_SHA:
            raise ValueError(f"{label}: natural copy raw identity drift")
        raw_diffs = [i for i, (a, b) in enumerate(zip(cpp, old_function)) if a != b]
        if raw_diffs != RAW_DIFFS:
            raise ValueError(f"{label}: natural copy raw diff drift: {raw_diffs}")
        if len(head) != SCORE_HEAD_SIZE:
            raise ValueError(f"{label}: retained SCORE head size drift")
        head_diffs = [i for i, (a, b) in enumerate(zip(head, old_score[:SCORE_HEAD_SIZE])) if a != b]
        if head_diffs != [0x2F5, 0x2F6]:
            raise ValueError(f"{label}: retained SCORE head fixup-addend drift: {head_diffs}")
        if len(pad) != PAD_SIZE or pad != b"\x00":
            raise ValueError(f"{label}: SCORE pad drift")

        rsp = work / "obj/th04/maine.@l"
        text = rsp.read_text()
        old = r"obj\th04\mainscv.obj"
        new = r"obj\th04\msch84.obj obj\th04\rect84.obj obj\th04\mscp84.obj"
        if text.count(old) != 1:
            raise ValueError(f"{label}: response SCORE owner token drift")
        rsp.write_text(text.replace(old, new, 1))

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink(missing_ok=True); mp.unlink(missing_ok=True)
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"], work, output / f"v484-link-{label}.log")
        image = parse_mz(exe.read_bytes())
        sites = [r.linear for r in image.relocations]
        payload = compare("th04-maine", work)
        if image.program_image != baseline.program_image:
            raise ValueError(f"{label}: linked program image changed")
        linked = image.program_image[FUNCTION_LOAD:FUNCTION_LOAD + FUNCTION_SIZE]
        if linked != target_function:
            raise ValueError(f"{label}: linked copy helper is not target exact")
        if sites != baseline_sites or Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: relocation table changed")
        ordered = sum(a != b for a, b in zip(sites, target_sites))
        if ordered != EXPECTED_MISMATCHES:
            raise ValueError(f"{label}: ordered frontier drift: {ordered}")
        if sha(exe) != FINAL_EXE or sha(mp) != FINAL_MAP:
            raise ValueError(f"{label}: output identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(mp),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "function_raw_sha256": digest(cpp),
            "reference_raw_sha256": digest(old_function),
            "function_linked_sha256": digest(linked),
            "function_size": len(cpp),
            "raw_differences_vs_v478": raw_diffs,
            "score_head_size": len(head),
            "score_head_raw_differences_vs_v478": head_diffs,
            "score_pad_size": len(pad),
            "relocation_table_unchanged_vs_v478": True,
            "ordered_relocation_mismatches": ordered,
            "same_index_relocations": len(sites) - ordered,
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256", "function_raw_sha256",
        "reference_raw_sha256", "function_linked_sha256", "function_size",
        "raw_differences_vs_v478", "score_head_size", "score_head_raw_differences_vs_v478", "score_pad_size",
        "relocation_table_unchanged_vs_v478", "ordered_relocation_mismatches",
        "same_index_relocations",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B v484 {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE SCORE_TEXT aligned EGC rectangle-copy natural-C++ raw/linked exact replay",
        "v478_source_exe_sha256": sha(source / "bin/th04/maine.exe"),
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "builds": builds,
        "observed_effect": (
            "The final 0x86-byte SCORE_TEXT rectangle-copy function is recovered as natural TC86 C++. "
            "Its raw CODE differs from the v478 same-object TASM body only at the two-byte near-call displacement "
            "to the preceding EGC-start helper; the split C++ object carries a zero addend plus same-segment FIXUPP. "
            "TLINK resolves the function target-exact, while the complete v478 MAINE program image and all 559 relocation entries remain byte-for-byte unchanged."
        ),
        "limit": (
            "The preceding 0x43 _egc_start_copy_inlined helper remains assembly-owned in this packet. A natural C++/intrinsic translation reaches 66/67 bytes but TC86 zero-register peepholing emits XOR AX,AX where the target EGC_START_COPY_INLINED macro contains MOV AX,0. "
            "No exact claim is made for that helper."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "function_linked_exact": True,
        "function_size": FUNCTION_SIZE,
        "ordered_relocation_mismatches": EXPECTED_MISMATCHES,
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
