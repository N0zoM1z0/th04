#!/usr/bin/env python3
"""Cold-compile maintained OP main_cdg_load and relink OP_TITLE_TEXT."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from inspect_dialog_fixup_order import omf_index  # noqa: E402
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_score_hiscore_boundaries import branch_edges, disassemble  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
RELOCATIONS = 804
SOURCE = ROOT / "src/op/title/main_cdg_load.cpp"
BODY = ROOT / "src/op/title/main_cdg_load.inl"
START = 0xCC97
SIZE = 0x31
NEXT = START + SIZE
PRODUCER_START = 0xCC97
PRODUCER_SIZE = 0x2C7
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "ba500a52961717b4b8e5d27b855c3b30dca24772fbd08f19db972091f1ce3a0d"
TARGET_PRODUCER_SHA = "7e9c8576c13b3e469bcbed947fbc6bf3d819328df88fc5c2a74d808271d86d79"
BASE_TITLE_SOURCE_SHA = "dfbfc0c5fabf19ed99d0624371cf57f6b687f5e88cb6e0343114c9cebbf0fa23"
BASE_TITLE_OBJECT_SHA = "b14094e67af79cba83ec7a9a6e6d80bed2f5f99fdb2da3d3ed2b1817bff360e3"
BASE_TITLE_CODE_SHA = "c9f3aac9a7e3d2f8edc3982a75bbd809cfe51d31ef18421dcc00dc73ffc9736d"


def sha(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def loose_segment_bytes(path: Path, segment_name: str) -> bytes:
    records = parse_omf(path.read_bytes())
    names = [""]
    segments: list[str] = []
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                length = record.data[pos]
                names.append(record.data[pos + 1:pos + 1 + length].decode("latin-1"))
                pos += length + 1
        elif record.record_type == 0x98:
            data = record.data
            pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            name_index, _ = omf_index(data, pos)
            segments.append(names[name_index])
    if segments.count(segment_name) != 1:
        raise RuntimeError(f"expected one {segment_name}: {segments}")
    wanted = segments.index(segment_name) + 1
    chunks: list[tuple[int, bytes]] = []
    for record in records:
        if record.record_type != 0xA0:
            continue
        index, pos = omf_index(record.data, 0)
        if index == wanted:
            offset = int.from_bytes(record.data[pos:pos + 2], "little")
            chunks.append((offset, record.data[pos + 2:]))
    chunks.sort()
    out = bytearray()
    for offset, payload in chunks:
        if offset != len(out):
            raise RuntimeError(f"{segment_name} LEDATA gap/overlap at {offset:#x}")
        out += payload
    return bytes(out)


def tcc_op(work: Path, output: Path, label: str, source: str) -> None:
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-", "-3",
         "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/", source],
        work, output / f"compile-{label}.log",
    )


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP main_cdg_load target identity drift")
    import csv
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream)
                if int(row["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("OP main_cdg_load Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x2557
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 2
    ):
        raise RuntimeError(f"OP main_cdg_load Ghidra extent drift: {row!r}")

    expected = [
        (0x00, 0x1378, 0x0C2E),
        (0x0A, 0x1381, 0x0C2E),
        (0x23, 0x138A, 0x0C2E),
        (0x28, 0x1392, 0x0C28),
    ]
    pos = 3
    for slot, string_off, call_off in expected:
        if (
            body[pos:pos + 2] != bytes((0x6A, slot))
            or body[pos + 2] != 0x1E
            or body[pos + 3] != 0x68
            or int.from_bytes(body[pos + 4:pos + 6], "little") != string_off
            or body[pos + 6] != 0x9A
            or int.from_bytes(body[pos + 7:pos + 9], "little") != call_off
            or int.from_bytes(body[pos + 9:pos + 11], "little") != 0x0DA1
        ):
            raise RuntimeError(f"OP main_cdg_load call block drift at {pos:#x}")
        pos += 11
    if body[:3] != bytes.fromhex("55 8b ec") or body[pos:] != bytes.fromhex("5d c3"):
        raise RuntimeError("OP main_cdg_load prologue/epilogue drift")
    if (
        "0DA1:0C2E       CDG_LOAD_ALL" not in map_text
        or "0DA1:0C28       CDG_LOAD_ALL_NOALPHA" not in map_text
    ):
        raise RuntimeError("candidate MAP no longer corroborates CDG load targets")
    return {
        "segment_identity": "1A74",
        "segment_offset": "2557",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 2,
        "slots": [0, 10, 35, 40],
        "string_offsets": ["0x1378", "0x1381", "0x138A", "0x1392"],
        "far_call_targets": ["0DA1:0C2E CDG_LOAD_ALL", "0DA1:0C28 CDG_LOAD_ALL_NOALPHA"],
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/op/title.cpp"
    if sha_file(upstream) != BASE_TITLE_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP title source drift")
    dst = work / "src/op/title"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)
    data = upstream.read_bytes()
    old = (
        b"void near main_cdg_load(void)\n"
        b"{\n"
        b"\top_cdg_load_shared();\n"
        b"\tcdg_load_all_noalpha(CDG_PIC, \"sl.cd2\");\n"
        b"}"
    )
    replacement = b'#include "src/op/title/main_cdg_load.inl"'
    if data.count(old) != 1:
        raise RuntimeError("main_cdg_load replacement anchor drift")
    upstream.write_bytes(data.replace(old, replacement, 1))
    return sha_file(upstream)


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
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/op/title.cpp", BASE_TITLE_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_title.obj", BASE_TITLE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        "src/op/title/main_cdg_load.cpp": sha_file(SOURCE),
        "src/op/title/main_cdg_load.inl": sha_file(BODY),
    }
    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target restore")
    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    boundary = target_boundary(body, map_text)
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target OP_TITLE_TEXT identity drift")
    if baseline.program_image[START:NEXT] != body or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 OP title producer differs from target")
    if "0A74:2557       main_cdg_load()" not in map_text:
        raise RuntimeError("v489 main_cdg_load MAP public drift")

    base_object = SNAPSHOT / "obj/th04/op_title.obj"
    base_code = segment_bytes(base_object, "OP_TITLE_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_TITLE_CODE_SHA:
        raise RuntimeError("pinned OP_TITLE_TEXT object contribution drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        dst = work / "src/op/title"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, dst / SOURCE.name)
        shutil.copy2(BODY, dst / BODY.name)

        before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"v602-main-cdg-load-standalone-{label}",
               "src/op/title/main_cdg_load.cpp")
        standalone = [path for path in (work / "obj/th04").glob("*.obj")
                      if path.name not in before]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_TITLE_TEXT")
        local_fixups = [
            item
            for record in parse_omf(local_obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]
        target_as_unlinked = bytes.fromhex(
            "55 8b ec 6a 00 1e 68 00 00 9a 00 00 00 00 "
            "6a 0a 1e 68 09 00 9a 00 00 00 00 "
            "6a 23 1e 68 12 00 9a 00 00 00 00 "
            "6a 28 1e 68 1a 00 9a 00 00 00 00 5d c3"
        )
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != target_as_unlinked
            or local_fixups != [(3, 43), (1, 40), (3, 32), (1, 29), (3, 21), (1, 18), (3, 10), (1, 7)]
        ):
            raise RuntimeError(f"{label}: standalone main_cdg_load OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/op_title.obj"
        group_obj.unlink()
        tcc_op(work, output, f"v602-main-cdg-load-group-{label}", "th04/op_title.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_TITLE_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained main_cdg_load changed grouped OP_TITLE_TEXT")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked_body = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked_body != body
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked OP title layout/body drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "standalone_object_sha256": sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": sha(local_code),
            "standalone_fixup_sites": [list(item) for item in local_fixups],
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
            "ordered_relocations": len(target_sites),
        }

    stable_keys = (
        "standalone_link_relevant_omf_sha256", "standalone_code_sha256",
        "standalone_fixup_sites", "group_link_relevant_omf_sha256", "group_code_sha256",
        "linked_exe_sha256", "linked_map_sha256", "linked_program_sha256",
        "linked_function_sha256", "linked_producer_sha256",
        "raw_function_difference_count", "raw_producer_difference_count",
        "ordered_relocations",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable_keys):
        raise RuntimeError("independent OP main_cdg_load cold rounds differ")
    if sha_file(SOURCE) != source_hashes["src/op/title/main_cdg_load.cpp"] or sha_file(BODY) != source_hashes["src/op/title/main_cdg_load.inl"]:
        raise RuntimeError("maintained main_cdg_load source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed main_cdg_load maintained-source cold-link replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "baseline_map_sha256": BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "OP_TITLE_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "cold_determinism": {
            "link_relevant_omf_code_exe_map_program_and_relocations_equal": True,
        },
        "limit": "Decoded 49-byte function only; v489 remains surrounding build scaffold. No packed-file or whole-OP exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "function_sha256": builds["a"]["linked_function_sha256"],
        "producer_sha256": builds["a"]["linked_producer_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
