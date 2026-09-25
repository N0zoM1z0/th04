#!/usr/bin/env python3
"""Cold-compile maintained OP cfg_load and relink OP_MAIN_TEXT."""

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

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import describe_omf, parse_omf
from lib.pc98 import parse_mz
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_op_help_put import tcc_op, loose_segment_bytes
from replay_th04_scroll_driver_natural import fixup_locations
from replay_th04_shared_delay_measure import link_relevant_omf_sha
from replay_th04_zun_source_only import source_closure
import replay_th04_op_cfg_save_exit as base

SNAPSHOT = base.SNAPSHOT
TARGET = base.TARGET
SOURCE = ROOT / "src/op/config/cfg_load.cpp"
BODY = ROOT / "src/op/config/cfg_load.inl"

TARGET_SHA = base.TARGET_SHA
BASE_EXE_SHA = base.BASE_EXE_SHA
BASE_MAP_SHA = base.BASE_MAP_SHA
BASE_CFG_SOURCE_SHA = base.BASE_CFG_SOURCE_SHA
BASE_OP_MAIN_SOURCE_SHA = base.BASE_OP_MAIN_SOURCE_SHA
BASE_OBJECT_SHA = base.BASE_OBJECT_SHA
BASE_LINK_OMF_SHA = base.BASE_LINK_OMF_SHA
BASE_CODE_SHA = base.BASE_CODE_SHA
RELOCATIONS = base.RELOCATIONS

START = 0xA74C
SIZE = 0xA4
NEXT = START + SIZE
PRODUCER_START = base.PRODUCER_START
PRODUCER_SIZE = base.PRODUCER_SIZE
TARGET_FUNCTION_SHA = "007b031558b792b510a709526d9171b323daeba7b98532aed3023a8f85c1ff87"
TARGET_PRODUCER_SHA = base.TARGET_PRODUCER_SHA
STANDALONE_CODE_SHA = "8e3cf9e413b580dafa6b28fb8b6956161b5d0db81a319650fef6e634c2a77bf1"
STANDALONE_FIXUPS = [
    (1, 148), (1, 132), (1, 116), (1, 107), (1, 47),
    (1, 41), (1, 37), (3, 26), (3, 21), (3, 9), (1, 6),
]


def sha(data: bytes) -> str:
    return base.sha(data)


def sha_file(path: Path) -> str:
    return base.sha_file(path)


def object_fixups(obj: Path) -> list[tuple[int, int]]:
    return [
        item
        for rec in parse_omf(obj.read_bytes())
        if rec.record_type == 0x9C
        for item in fixup_locations(rec.data)
    ]


def target_boundary(body: bytes, target_program: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP cfg_load target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP cfg_load Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x000C
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 3
    ):
        raise RuntimeError(f"OP cfg_load Ghidra extent drift: {row!r}")

    far_calls = ((8, 0x0A7A), (20, 0x09C6), (25, 0x095A))
    if (
        body[:8] != bytes.fromhex("c8 0c 00 00 1e 68 08 01")
        or any(
            body[off] != 0x9A
            or int.from_bytes(body[off + 1:off + 3], "little") != target_off
            or int.from_bytes(body[off + 3:off + 5], "little") != 0
            for off, target_off in far_calls
        )
        or body[13:20] != bytes.fromhex("16 8d 46 f6 50 6a 0a")
        or body[30:45] != bytes.fromhex(
            "8b 46 fc 89 46 f4 a3 66 1a c7 06 64 1a 00 00"
        )
        or body[-2:] != bytes.fromhex("c9 c3")
    ):
        raise RuntimeError("OP cfg_load instruction/operand topology drift")

    required = (
        "0A74:000C idle  cfg_load()",
        "0000:0A7A       FILE_ROPEN",
        "0000:09C6       FILE_READ",
        "0000:095A       FILE_CLOSE",
        "0F34:1A64       _resident",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP cfg_load MAP target drift")
    if target_program[0xF340 + 0x0108:0xF340 + 0x0111] != b"MIKO.CFG\0":
        raise RuntimeError("OP cfg_load filename target drift")

    return {
        "segment_identity": "1A74",
        "segment_offset": "000C",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 1,
        "callee_count": 3,
        "stack_cfg_size": 10,
        "filename": "DS:0108 MIKO.CFG",
        "resident_pointer": "0F34:1A64",
        "resident_field_offsets": ["0x0F", "0x3A", "0x3B", "0x10", "0x18", "0x49"],
        "lives_valid_range": "1..6; default 3",
        "bombs_max": 2,
        "bgm_mode_count": 3,
        "se_mode_count": 3,
        "terminal": "RET",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/formats/cfg.cpp"
    if sha_file(upstream) != BASE_CFG_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP cfg source drift")
    dst = work / "src/op/config"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)

    data = upstream.read_bytes()
    start_marker = b"void near cfg_load(void)\n"
    end_marker = b"\n}\n\nvoid near cfg_save(void)\n"
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise RuntimeError("cfg_load replacement anchors drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start) + 2
    upstream.write_bytes(
        data[:start] + b'#include "src/op/config/cfg_load.inl"\n' + data[end:]
    )
    return sha_file(upstream)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/formats/cfg.cpp", BASE_CFG_SOURCE_SHA),
        (SNAPSHOT / "th04/op_main.cpp", BASE_OP_MAIN_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_main.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    base_obj = SNAPSHOT / "obj/th04/op_main.obj"
    base_code = segment_bytes(base_obj, "OP_MAIN_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_CODE_SHA:
        raise RuntimeError("baseline OP_MAIN_TEXT contribution drift")
    if link_relevant_omf_sha(base_obj) != BASE_LINK_OMF_SHA:
        raise RuntimeError("baseline op_main.obj OMF drift")

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid OP target/baseline")
    sites = [x.linear for x in target.relocations]
    if [x.linear for x in baseline.relocations] != sites:
        raise RuntimeError("OP baseline relocation order drift")

    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target OP_MAIN_TEXT producer identity drift")
    if (
        baseline.program_image[START:NEXT] != body
        or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer
    ):
        raise RuntimeError("v489 OP_MAIN_TEXT differs from target")
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    bound = target_boundary(body, target.program_image, map_text)
    mstart, msize, mline = base.base.map_contribution(SNAPSHOT / "obj/th04/op.map")
    if (mstart, msize) != (PRODUCER_START, PRODUCER_SIZE):
        raise RuntimeError(f"baseline OP_MAIN_TEXT MAP contribution drift: {mline}")

    closure = source_closure(ROOT, ("src/op/config/cfg_load.cpp",))
    source_hashes = {name: sha_file(ROOT / name) for name in closure}
    output.mkdir(parents=True)
    builds = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        for rel in closure:
            dst = work / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)

        before = {p.name for p in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"cfg-save-standalone-{label}", "src/op/config/cfg_load.cpp")
        standalone = [p for p in (work / "obj/th04").glob("*.obj") if p.name not in before]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_desc = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_MAIN_TEXT")
        local_fixups = object_fixups(local_obj)
        masked_target = bytearray(body)
        masked_local = bytearray(local_code)
        for kind, off in STANDALONE_FIXUPS:
            width = 2 if kind == 1 else 4
            masked_target[off:off + width] = b"\0" * width
            masked_local[off:off + width] = b"\0" * width
        if (
            not local_desc["valid"]
            or "TC86 Borland C++ 4.02" not in local_desc["translator_comments"]
            or len(local_code) != SIZE
            or sha(local_code) != STANDALONE_CODE_SHA
            or local_fixups != STANDALONE_FIXUPS
            or bytes(masked_local) != bytes(masked_target)
        ):
            raise RuntimeError(f"{label}: standalone cfg_load codegen drift")

        patched_cfg_sha = overlay_source(work)
        op_main = work / "th04/op_main.cpp"
        if sha_file(op_main) != BASE_OP_MAIN_SOURCE_SHA:
            raise RuntimeError(f"{label}: pinned op_main.cpp drift")
        group_obj = work / "obj/th04/op_main.obj"
        group_obj.unlink()
        tcc_op(work, output, f"cfg-save-group-{label}", "th04/op_main.cpp")
        group_desc = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_MAIN_TEXT")
        if (
            not group_desc["valid"]
            or "TC86 Borland C++ 4.02" not in group_desc["translator_comments"]
            or group_code != base_code
            or link_relevant_omf_sha(group_obj) != BASE_LINK_OMF_SHA
        ):
            raise RuntimeError(f"{label}: grouped op_main.obj drift")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked_body = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        map_start, map_size, map_line = base.base.map_contribution(mp)
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [x.linear for x in image.relocations] != sites
            or image.program_image != baseline.program_image
            or linked_body != body
            or linked_producer != producer
            or (map_start, map_size) != (PRODUCER_START, PRODUCER_SIZE)
        ):
            raise RuntimeError(f"{label}: linked OP cfg_load/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_cfg_source_sha256": patched_cfg_sha,
            "standalone_object_sha256": sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": sha(local_code),
            "standalone_fixup_sites": [list(x) for x in local_fixups],
            "group_object_sha256": sha_file(group_obj),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": sha(group_code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked_body),
            "linked_producer_sha256": sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(sites),
            "map_contribution": map_line,
        }

    stable = (
        "patched_cfg_source_sha256", "standalone_link_relevant_omf_sha256",
        "standalone_code_sha256", "standalone_fixup_sites",
        "group_link_relevant_omf_sha256", "group_code_sha256",
        "linked_exe_sha256", "linked_map_sha256", "linked_program_sha256",
        "linked_function_sha256", "linked_producer_sha256",
        "raw_function_difference_count", "raw_producer_difference_count",
        "ordered_relocations", "map_contribution",
    )
    if any(builds["a"][k] != builds["b"][k] for k in stable):
        raise RuntimeError("independent OP cfg_load cold rounds differ")
    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained cfg_load source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "source_sha256": source_hashes,
        "boundary": bound,
        "producer": {
            "segment": "OP_MAIN_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "limit": "Decoded 164-byte cfg_load only; no packed-file or whole-OP exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "function_sha256": builds["a"]["linked_function_sha256"],
        "producer_sha256": builds["a"]["linked_producer_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
