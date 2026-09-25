#!/usr/bin/env python3
"""Cold-replay maintained natural C++ for MAINE pic_put_both_masked."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf
from lib.pc98 import parse_mz
from compact_op_maine_snapshot import copy_compact_snapshot
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from probe_th04_maine_segment_topology_v470 import tcc
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from replay_th04_zun_source_only import source_closure
import replay_th04_maine_score_insert as prior
import replay_th04_maine_script_op as base

SOURCE = ROOT / "src/maine/cutscene/pic_put_both_masked.inl"
START = 0xA37F
SIZE = 0x12F
NEXT = START + SIZE
PRODUCER_START = 0xA292
PRODUCER_SIZE = 0xC3E
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "4a4a69256ba51a5efeabbe21da3f34663be99fee67b9c57b8587f96cb2eaa673"
RAW_CALLER = 0xACBC
RAW_CALL = b"\xE8\xC0\xF6"


def sha(data: bytes) -> str:
    return prior.sha(data)


def validate_target(program: bytes, body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE pic_put_both_masked target identity drift")
    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = [r for r in csv.DictReader(stream) if int(r["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("MAINE pic_put_both_masked Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x032F
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 0
        or int(row["callee_count"]) != 4
    ):
        raise RuntimeError(f"MAINE pic_put_both_masked Ghidra extent drift: {row!r}")
    if "0A05:032F idle  pic_put_both_masked(int,int,int,int)" not in map_text:
        raise RuntimeError("MAINE pic_put_both_masked MAP entry drift")
    if "0A05:045E idle  box_bg_allocate_and_snap()" not in map_text:
        raise RuntimeError("MAINE following box background MAP entry drift")
    if program[RAW_CALLER:RAW_CALLER + len(RAW_CALL)] != RAW_CALL:
        raise RuntimeError("MAINE raw script_op caller drift")
    rel = int.from_bytes(RAW_CALL[1:], "little", signed=True)
    if RAW_CALLER + 3 + rel != START:
        raise RuntimeError("MAINE raw caller no longer targets pic_put_both_masked")
    if not body.startswith(b"\xC8\x08\x00\x00\x56\x57") or body[-6:] != b"\x5F\x5E\xC9\xC2\x08\x00":
        raise RuntimeError("MAINE pic_put_both_masked prologue/epilogue drift")
    return {
        "segment_identity": "1A05",
        "segment_offset": "032F",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_caller_count": 0,
        "ghidra_callee_count": 4,
        "raw_caller_payload_offset": hex(RAW_CALLER),
        "raw_caller_target": hex(START),
        "terminal": "pop di; pop si; leave; ret 8",
        "next_function": "1A05:045E box_bg_allocate_and_snap",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th03/cutscene/cutscene.cpp"
    if prior.sha_file(upstream) != base.BASE_CUTSCENE_SOURCE_SHA:
        raise RuntimeError("pinned v489 cutscene translation unit drift")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/maine/cutscene", work / "src/maine/cutscene", dirs_exist_ok=True)
    data = upstream.read_bytes()
    anchor = b"void pascal near pic_put_both_masked(\n\tscreen_x_t left, vram_y_t top, int quarter, int mask_id\n)\n{"
    if data.count(anchor) != 2:
        raise RuntimeError("pic_put_both_masked candidate branch count drift")
    start = data.rindex(anchor)
    end_anchor = b"\n}\n\n#define box_bg_snap_func"
    end_marker = data.index(end_anchor, start)
    if data.find(end_anchor, end_marker + 1) >= 0:
        raise RuntimeError("pic_put_both_masked end anchor is not unique")
    end = end_marker + 2
    upstream.write_bytes(
        data[:start] + b'#include "src/maine/cutscene/pic_put_both_masked.inl"' + data[end:]
    )
    return prior.sha_file(upstream)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   capture_output=True, text=True, check=True)
    if prior.sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (prior.TARGET, prior.TARGET_SHA),
        (prior.SNAPSHOT / "bin/th04/maine.exe", prior.BASE_EXE_SHA),
        (prior.SNAPSHOT / "obj/th04/maine.map", prior.BASE_MAP_SHA),
        (prior.SNAPSHOT / "th03/cutscene/cutscene.cpp", base.BASE_CUTSCENE_SOURCE_SHA),
        (prior.SNAPSHOT / "obj/th04/cutscene.obj", base.BASE_CUTSCENE_OBJECT_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    closure = source_closure(ROOT, ("src/maine/cutscene/pic_put_both_masked.inl",))
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}
    target = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")

    body = target.program_image[START:NEXT]
    target_producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    boundary = validate_target(target.program_image, body, map_text)
    if baseline.program_image[START:NEXT] != body:
        raise RuntimeError("v489 pic_put_both_masked bytes differ from target")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != target_producer:
        raise RuntimeError("v489 CUTSCENE_TEXT producer differs from target")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 ordered relocations differ from target")

    base_object = prior.SNAPSHOT / "obj/th04/cutscene.obj"
    base_omf = describe_omf(base_object.read_bytes())
    base_code = segment_bytes(base_object, "CUTSCENE_TEXT")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != base.BASE_CUTSCENE_CODE_SHA
    ):
        raise RuntimeError("pinned v489 CUTSCENE_TEXT object drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        patched_source_sha = overlay_source(work)

        group_obj = work / "obj/th04/cutscene.obj"
        group_obj.unlink()
        tcc(work, output, f"v691-pic-put-both-masked-group-{label}", "th04/cutscene.cpp")
        omf = describe_omf(group_obj.read_bytes())
        code = segment_bytes(group_obj, "CUTSCENE_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained pic_put_both_masked changed grouped CUTSCENE_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or prior.sha_file(exe) != prior.BASE_EXE_SHA
            or prior.sha_file(mp) != prior.BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked != body
            or linked_producer != target_producer
        ):
            raise RuntimeError(f"{label}: cold MAINE pic_put_both_masked link/layout drift")
        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "group_omf_sha256": prior.sha_file(group_obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked),
            "linked_producer_sha256": sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable = lambda d: {k: v for k, v in d.items() if k != "group_omf_sha256"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent MAINE pic_put_both_masked cold rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained pic_put_both_masked source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed pic_put_both_masked and maintained natural-C++ cold replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "baseline_exe_sha256": prior.BASE_EXE_SHA,
        "baseline_map_sha256": prior.BASE_MAP_SHA,
        "baseline_cutscene_object_sha256": base.BASE_CUTSCENE_OBJECT_SHA,
        "baseline_cutscene_code_sha256": base.BASE_CUTSCENE_CODE_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": prior.sha_file(Path(__file__).resolve()),
        "boundary": boundary,
        "producer": {
            "segment": "CUTSCENE_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(target_producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "limit": (
            "Decoded 303-byte function only; no packed-file or whole-MAINE exactness. "
            "The surrounding v489 tree remains replay scaffold."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": prior.sha_file(receipt_path),
        "function_sha256": TARGET_FUNCTION_SHA,
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
