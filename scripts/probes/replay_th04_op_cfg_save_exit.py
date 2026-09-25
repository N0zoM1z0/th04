#!/usr/bin/env python3
"""Cold-compile maintained OP cfg_save_exit and relink OP_MAIN_TEXT."""

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
import replay_th04_op_start_game as base

SNAPSHOT = base.SNAPSHOT
TARGET = base.TARGET
SOURCE = ROOT / "src/op/config/cfg_save_exit.cpp"
BODY = ROOT / "src/op/config/cfg_save_exit.inl"

TARGET_SHA = base.TARGET_SHA
BASE_EXE_SHA = base.BASE_EXE_SHA
BASE_MAP_SHA = base.BASE_MAP_SHA
BASE_CFG_SOURCE_SHA = "006bd62a3049e529ec6073dbc13531ac92b04987773e7825001ddf355e0bd69c"
BASE_OP_MAIN_SOURCE_SHA = base.BASE_OP_MAIN_SOURCE_SHA
BASE_OBJECT_SHA = base.BASE_OBJECT_SHA
BASE_LINK_OMF_SHA = base.BASE_LINK_OMF_SHA
BASE_CODE_SHA = base.BASE_CODE_SHA
RELOCATIONS = base.RELOCATIONS

START = 0xA873
SIZE = 0x7E
NEXT = START + SIZE
PRODUCER_START = base.PRODUCER_START
PRODUCER_SIZE = base.PRODUCER_SIZE
TARGET_FUNCTION_SHA = "c491e94f797e59d1e3d2717001b19aad62a9b598cf9c6bd9d910daacedfb5438"
TARGET_PRODUCER_SHA = base.TARGET_PRODUCER_SHA
STANDALONE_CODE_SHA = "ed56c3796b01b477498f8580b75d5e4b43f2cf64021e7d93d3c2e383b2d7483a"
STANDALONE_FIXUPS = [
    (3, 120), (3, 115), (1, 42), (3, 36),
    (3, 26), (1, 23), (3, 17), (1, 11),
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
        raise RuntimeError("OP cfg_save_exit target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP cfg_save_exit Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x0133
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 5
    ):
        raise RuntimeError(f"OP cfg_save_exit Ghidra extent drift: {row!r}")

    if (
        body[:4] != bytes.fromhex("c8 0a 00 00")
        or body[4:17] != bytes.fromhex(
            "8d 46 f6 16 50 1e 68 91 00 b9 0a 00 9a"
        )
        or int.from_bytes(body[17:19], "little") != 0x4202
        or int.from_bytes(body[19:21], "little") != 0x0000
        or body[21:26] != bytes.fromhex("1e 68 08 01 9a")
        or int.from_bytes(body[26:28], "little") != 0x089A
        or int.from_bytes(body[28:30], "little") != 0x0000
        or body[30:36] != bytes.fromhex("66 6a 00 6a 00 9a")
        or int.from_bytes(body[36:38], "little") != 0x0AB6
        or int.from_bytes(body[38:40], "little") != 0x0000
        or body[40:44] != bytes.fromhex("c4 1e 64 1a")
        or body[44:86] != bytes.fromhex(
            "26 8a 47 0f 88 46 f6 "
            "26 8a 47 3a 88 46 f7 "
            "26 8a 47 3b 88 46 f8 "
            "26 8a 47 10 88 46 f9 "
            "26 8a 47 18 88 46 fa "
            "26 8a 47 49 88 46 fb"
        )
        or body[86:107] != bytes.fromhex(
            "8a 46 f6 02 46 f7 02 46 f8 02 46 f9 02 46 fa 02 46 fb 88 46 ff"
        )
        or body[107:111] != bytes.fromhex("16 8d 46 f6")
        or body[111:115] != bytes.fromhex("50 6a 0a 9a")
        or int.from_bytes(body[115:117], "little") != 0x0AF8
        or int.from_bytes(body[117:119], "little") != 0x0000
        or body[119] != 0x9A
        or int.from_bytes(body[120:122], "little") != 0x095A
        or int.from_bytes(body[122:124], "little") != 0x0000
        or body[-2:] != bytes.fromhex("c9 c3")
    ):
        raise RuntimeError("OP cfg_save_exit instruction/operand topology drift")

    required = (
        "0A74:0133 idle  cfg_save_exit()",
        "0000:4202       F_SCOPY@",
        "0000:089A       FILE_APPEND",
        "0000:0AB6       FILE_SEEK",
        "0000:0AF8       FILE_WRITE",
        "0000:095A       FILE_CLOSE",
        "0F34:1A64       _resident",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP cfg_save_exit MAP target drift")

    if target_program[0xF340 + 0x0091:0xF340 + 0x009B] != b"\0" * 10:
        raise RuntimeError("OP cfg_save_exit zero-template target drift")
    if target_program[0xF340 + 0x0108:0xF340 + 0x0111] != b"MIKO.CFG\0":
        raise RuntimeError("OP cfg_save_exit filename target drift")

    return {
        "segment_identity": "1A74",
        "segment_offset": "0133",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 1,
        "callee_count": 5,
        "stack_cfg_size": 10,
        "zero_template": "DS:0091, 10 bytes",
        "filename": "DS:0108 MIKO.CFG",
        "resident_pointer": "0F34:1A64",
        "resident_field_offsets": ["0x0F", "0x3A", "0x3B", "0x10", "0x18", "0x49"],
        "checksum_offset": 9,
        "write_size": 10,
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
    start_marker = b"void near cfg_save_exit(void)\n"
    end_marker = b"\n}\n"
    if data.count(start_marker) != 1:
        raise RuntimeError("cfg_save_exit start anchor drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start) + len(end_marker)
    upstream.write_bytes(
        data[:start] + b'#include "src/op/config/cfg_save_exit.inl"\n' + data[end:]
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
    mstart, msize, mline = base.map_contribution(SNAPSHOT / "obj/th04/op.map")
    if (mstart, msize) != (PRODUCER_START, PRODUCER_SIZE):
        raise RuntimeError(f"baseline OP_MAIN_TEXT MAP contribution drift: {mline}")

    closure = source_closure(ROOT, ("src/op/config/cfg_save_exit.cpp",))
    source_hashes = {name: sha_file(ROOT / name) for name in closure}

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        for rel in closure:
            dst = work / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)

        before = {p.name for p in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"cfg-save-exit-standalone-{label}",
               "src/op/config/cfg_save_exit.cpp")
        standalone = [
            p for p in (work / "obj/th04").glob("*.obj")
            if p.name not in before
        ]
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
            raise RuntimeError(f"{label}: standalone cfg_save_exit codegen drift")

        patched_cfg_sha = overlay_source(work)
        op_main = work / "th04/op_main.cpp"
        if sha_file(op_main) != BASE_OP_MAIN_SOURCE_SHA:
            raise RuntimeError(f"{label}: pinned op_main.cpp drift")
        group_obj = work / "obj/th04/op_main.obj"
        group_obj.unlink()
        tcc_op(work, output, f"cfg-save-exit-group-{label}", "th04/op_main.cpp")
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
        linked_producer = image.program_image[
            PRODUCER_START:PRODUCER_START + PRODUCER_SIZE
        ]
        map_start, map_size, map_line = base.map_contribution(mp)
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
            raise RuntimeError(f"{label}: linked OP cfg_save_exit/layout drift")

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
        "patched_cfg_source_sha256",
        "standalone_link_relevant_omf_sha256",
        "standalone_code_sha256",
        "standalone_fixup_sites",
        "group_link_relevant_omf_sha256",
        "group_code_sha256",
        "linked_exe_sha256",
        "linked_map_sha256",
        "linked_program_sha256",
        "linked_function_sha256",
        "linked_producer_sha256",
        "raw_function_difference_count",
        "raw_producer_difference_count",
        "ordered_relocations",
        "map_contribution",
    )
    if any(builds["a"][k] != builds["b"][k] for k in stable):
        raise RuntimeError("independent OP cfg_save_exit cold rounds differ")
    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained cfg_save_exit source changed during replay")

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
        "limit": (
            "Decoded 126-byte cfg_save_exit only; no packed-file or whole-OP exactness."
        ),
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
