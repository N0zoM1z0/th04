#!/usr/bin/env python3
"""Cold-compile maintained OP start_extra and relink OP_MAIN_TEXT."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
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

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/op/start/start_extra.cpp"
BODY = ROOT / "src/op/start/start_extra.inl"

TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
BASE_START_SOURCE_SHA = "b2d57d857e5fff08960ef1338af7174ec7309ab1eaa39762881323924a543349"
BASE_OP_MAIN_SOURCE_SHA = "5cf36e94fc4d72672edd5a225f73d4ac3ae9c551f67dfd249715c8c7a7484efd"
BASE_OBJECT_SHA = "6706f32fba2b8753716a66d22a2cc64539d5e96051e0ba2dbca8405b22687481"
BASE_LINK_OMF_SHA = "92d7bff8542364834b9f9f3b3d4eb74b582fa2209b5906e103325ca1b5a8b4a0"
BASE_CODE_SHA = "926ac58cb1ac3225d93ac70122377ee8ae10a35cee069aa9e5da9b76ce4b41b7"
RELOCATIONS = 804

START = 0xA96C
SIZE = 0x5D
NEXT = START + SIZE
PRODUCER_START = 0xA74C
PRODUCER_SIZE = 0xD53
TARGET_FUNCTION_SHA = "a844d77702f1ed106371a666aa58cd0b5ccaf2c9852fb05a8df4d4eb42ddf855"
TARGET_PRODUCER_SHA = "02ba00a11483ba325fc88687232ee277e8525047372a9d0c722c92cb4ffb1659"
STANDALONE_CODE_SHA = "c94afeff05e9a8ed9d9474ba8d9af68ff3d7b055f0593b7b9ddde35fb52f6af5"
STANDALONE_FIXUPS = [
    (3, 84), (1, 81), (1, 77), (3, 68), (3, 63), (3, 55),
    (1, 52), (1, 49), (1, 41), (1, 33), (1, 5),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def object_fixups(obj: Path) -> list[tuple[int, int]]:
    return [
        item
        for rec in parse_omf(obj.read_bytes())
        if rec.record_type == 0x9C
        for item in fixup_locations(rec.data)
    ]


def map_contribution(path: Path) -> tuple[int, int, str]:
    pat = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=OP_MAIN_TEXT\b.*\bM=th04/op_main\.cpp(?:\s|$)",
        re.I,
    )
    matches = []
    for line in path.read_text(encoding="cp437").splitlines():
        m = pat.search(line)
        if m:
            matches.append((
                int(m[1], 16) * 16 + int(m[2], 16),
                int(m[3], 16),
                line.strip(),
            ))
    if len(matches) != 1:
        raise RuntimeError(f"expected one OP_MAIN_TEXT contribution: {matches}")
    return matches[0]


def target_boundary(body: bytes, target_program: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP start_extra target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP start_extra Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x022C
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 0
        or int(row["callee_count"]) != 7
    ):
        raise RuntimeError(f"OP start_extra Ghidra extent drift: {row!r}")

    # Target-first field/write topology and near-call destinations.
    if (
        body[:7] != bytes.fromhex("55 8b ec c4 1e 64 1a")
        or body[7:32] != bytes.fromhex(
            "26 c6 47 11 06 26 c6 47 0c 03 26 c6 47 0e 02 "
            "26 c6 47 12 30 26 c6 47 13 36"
        )
        or body[32] != 0xE8
        or START + 35 + int.from_bytes(body[33:35], "little", signed=True) != 0xD708
        or body[35:39] != bytes.fromhex("0b c0 75 34")
        or body[39:48] != bytes.fromhex("c4 1e 64 1a 26 c6 47 3e 00")
        or body[48] != 0xE8
        or START + 51 + int.from_bytes(body[49:51], "little", signed=True) != 0xCCC8
        or body[51] != 0xE8
        or START + 54 + int.from_bytes(body[52:54], "little", signed=True) != 0xA7F0
        or body[54] != 0x9A
        or int.from_bytes(body[55:57], "little") != 0x1356
        or int.from_bytes(body[57:59], "little") != 0x0000
        or body[59:62] != bytes.fromhex("68 0a 02")
        or body[62] != 0x9A
        or int.from_bytes(body[63:65], "little") != 0x0264
        or int.from_bytes(body[65:67], "little") != 0x0DA1
        or body[67] != 0x9A
        or int.from_bytes(body[68:70], "little") != 0x069C
        or int.from_bytes(body[70:72], "little") != 0x0DA1
        or body[72:76] != bytes.fromhex("66 6a 00 1e")
        or body[76] != 0x68
        or int.from_bytes(body[77:79], "little") != 0x0111
        or body[79] != 0x1E
        or body[80] != 0x68
        or int.from_bytes(body[81:83], "little") != 0x0111
        or body[83] != 0x9A
        or int.from_bytes(body[84:86], "little") != 0x9F9D
        or int.from_bytes(body[86:88], "little") != 0x0000
        or body[88:] != bytes.fromhex("83 c4 0c 5d c3")
    ):
        raise RuntimeError("OP start_extra instruction/operand topology drift")

    required = (
        "0F34:1A64       _resident",
        "0A74:2FC8       playchar_menu()",
        "0A74:2588       main_cdg_free()",
        "0A74:00B0 idle  cfg_save()",
        "0000:1356       GAIJI_RESTORE",
        "0DA1:0264       SND_KAJA_INTERRUPT",
        "0DA1:069C       game_exit()",
        "0000:9F9D       _execl",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP start_extra MAP target drift")
    if target_program[0xF340 + 0x0111:0xF340 + 0x0116] != b"main\0":
        raise RuntimeError("OP start_extra BINARY_MAIN target string drift")

    return {
        "segment_identity": "1A74",
        "segment_offset": "022C",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 0,
        "callee_count": 7,
        "resident_pointer": "0F34:1A64",
        "resident_writes": {
            "stage": 6,
            "credit_lives": 3,
            "credit_bombs": 2,
            "playchar_ascii": "0",
            "stage_ascii": "6",
            "demo_num_after_menu": 0,
        },
        "menu_cancel_returns": True,
        "kaja_ax": "0x020A",
        "binary_main": "main",
        "terminal": "RET",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/op/start.cpp"
    if sha_file(upstream) != BASE_START_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP start source drift")
    dst = work / "src/op/start"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)
    data = upstream.read_bytes()
    start_marker = b"void near start_extra(void)\n"
    end_marker = b"\n\ninline void resident_set_demo("
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise RuntimeError("start_extra replacement anchors drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start)
    upstream.write_bytes(
        data[:start] + b'#include "src/op/start/start_extra.inl"' + data[end:]
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
        (SNAPSHOT / "th04/op/start.cpp", BASE_START_SOURCE_SHA),
        (SNAPSHOT / "th04/op_main.cpp", BASE_OP_MAIN_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_main.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    base_obj = SNAPSHOT / "obj/th04/op_main.obj"
    base_code = segment_bytes(base_obj, "OP_MAIN_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_CODE_SHA:
        raise RuntimeError("baseline OP_MAIN_TEXT object contribution drift")
    if link_relevant_omf_sha(base_obj) != BASE_LINK_OMF_SHA:
        raise RuntimeError("baseline op_main.obj link-relevant OMF drift")

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
    mstart, msize, mline = map_contribution(SNAPSHOT / "obj/th04/op.map")
    if (mstart, msize) != (PRODUCER_START, PRODUCER_SIZE):
        raise RuntimeError(f"baseline OP_MAIN_TEXT MAP contribution drift: {mline}")

    closure = source_closure(ROOT, ("src/op/start/start_extra.cpp",))
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
        tcc_op(work, output, f"start-extra-standalone-{label}",
               "src/op/start/start_extra.cpp")
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
        for kind, off in STANDALONE_FIXUPS:
            width = 2 if kind == 1 else 4
            masked_target[off:off + width] = b"\0" * width
        if (
            not local_desc["valid"]
            or "TC86 Borland C++ 4.02" not in local_desc["translator_comments"]
            or len(local_code) != SIZE
            or sha(local_code) != STANDALONE_CODE_SHA
            or local_fixups != STANDALONE_FIXUPS
            or local_code != bytes(masked_target)
        ):
            raise RuntimeError(f"{label}: standalone start_extra codegen drift")

        patched_start_sha = overlay_source(work)
        op_main = work / "th04/op_main.cpp"
        if sha_file(op_main) != BASE_OP_MAIN_SOURCE_SHA:
            raise RuntimeError(f"{label}: pinned op_main.cpp drift")
        group_obj = work / "obj/th04/op_main.obj"
        group_obj.unlink()
        tcc_op(work, output, f"start-extra-group-{label}", "th04/op_main.cpp")
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
        map_start, map_size, map_line = map_contribution(mp)
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
            raise RuntimeError(f"{label}: linked OP start_extra/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_start_source_sha256": patched_start_sha,
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
        "patched_start_source_sha256",
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
        raise RuntimeError("independent OP start_extra cold rounds differ")
    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained start_extra source changed during replay")

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
            "Decoded 93-byte start_extra only; full OP_MAIN_TEXT is verified as "
            "its containing producer. No packed-file or whole-OP exactness."
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
