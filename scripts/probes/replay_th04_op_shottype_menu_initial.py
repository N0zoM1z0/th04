#!/usr/bin/env python3
"""Cold-compile maintained OP shottype_menu_put_initial and relink OP_01_TEXT."""

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
SOURCE = ROOT / "src/op/menu/shottype_menu_initial.cpp"
BODY = ROOT / "src/op/menu/shottype_menu_initial.inl"
START = 0xD650
SIZE = 0x62
NEXT = START + SIZE
PRODUCER_START = 0xCF5E
PRODUCER_SIZE = 0xAB3
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "d7a63ea4c3995e47cf2186cf700f2744f75b3967a194797938c3841abd39beb2"
TARGET_PRODUCER_SHA = "bdebb9e5d9c426fabca3fcb288dc298114f5cf9fa3e53cca96d5c4ad6d8ec7bc"
BASE_MENU_SOURCE_SHA = "cd92a300b16f1aa357fe37dfd1e2bed83aa28e56223e67bb4df0f883630f2d3c"
BASE_MENU_OBJECT_SHA = "939a58bc7b67e212a2ffca3462a504024beb6bdbf3ccc6834e1d03a7fc4ea413"
BASE_MENU_CODE_SHA = "4dada9dc8d0be3cb8e42080b7e151fece1634cd84e26291b0f9a3cd7c150d043"


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
        raise RuntimeError("OP shottype_menu_put_initial target identity drift")
    import csv
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream)
                if int(row["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("OP shottype_menu_put_initial Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x2F10
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 5
    ):
        raise RuntimeError(f"OP shottype_menu_put_initial Ghidra extent drift: {row!r}")
    if (
        body[:8] != bytes.fromhex("55 8b ec 80 3e 78 3f 00")
        or body[8:12] != bytes.fromhex("75 0a 66 68")
        or body[12:16] != bytes.fromhex("2c 00 b8 00")
        or body[16:20] != bytes.fromhex("6a 28 eb 08")
        or body[20:24] != bytes.fromhex("66 68 2c 00")
        or body[24:28] != bytes.fromhex("b8 00 6a 29")
        or body[28] != 0x9A
        or int.from_bytes(body[29:31], "little") != 0x0766
        or int.from_bytes(body[31:33], "little") != 0x0DA1
        or body[33:39] != bytes.fromhex("66 68 01 00 c0 00")
        or body[39] != 0x9A
        or int.from_bytes(body[40:42], "little") != 0x10D2
        or body[44:56] != bytes.fromhex("66 68 34 00 37 00 66 68 1f 01 37 00")
        or body[56] != 0x9A
        or int.from_bytes(body[57:59], "little") != 0x0CA4
        or body[61:73] != bytes.fromhex("66 68 20 01 18 00 66 68 27 01 37 00")
        or body[73] != 0x9A
        or int.from_bytes(body[74:76], "little") != 0x0CA4
        or body[78:84] != bytes.fromhex("ba 7c 00 b0 00 ee")
        or body[84] != 0xE8
        or START + 87 + int.from_bytes(body[85:87], "little", signed=True) != 0xD595
        or body[87] != 0xA0
        or int.from_bytes(body[88:90], "little") != 0x3F79
        or body[90:93] != bytes.fromhex("b4 00 50")
        or body[93] != 0xE8
        or START + 96 + int.from_bytes(body[94:96], "little", signed=True) != 0xD465
        or body[-2:] != bytes.fromhex("5d c3")
    ):
        raise RuntimeError("OP shottype_menu_put_initial instruction/operand topology drift")
    required = (
        "0A74:2F10 idle  shottype_menu_put_initial()",
        "0F34:3F78 idle  _playchar_menu_sel",
        "0F34:3F79 idle  _shottype_menu_sel",
        "0DA1:0766       CDG_PUT_NOALPHA_8",
        "0000:10D2       GRCG_SETCOLOR",
        "0000:0CA4       GRCG_BYTEBOXFILL_X",
        "0A74:2E55 idle  shottype_title_box_put()",
        "0A74:2D25 idle  shottype_titles_put(int)",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP shottype_menu_put_initial MAP target drift")
    return {
        "segment_identity": "1A74",
        "segment_offset": "2F10",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 1,
        "callee_count": 5,
        "cdg_slots": [40, 41],
        "picture": {"left": 184, "top": 44, "width": 256, "height": 244},
        "grcg_off_port": "0x7C",
        "terminal": "RET",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/m_char.cpp"
    if sha_file(upstream) != BASE_MENU_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP m_char source drift")
    dst = work / "src/op/menu"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)
    data = upstream.read_bytes()
    start_marker = b"void near shottype_menu_put_initial(void)\n"
    end_marker = b"\n\nvoid near playchar_menu_put_initial(void)\n"
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise RuntimeError("shottype_menu_put_initial replacement anchor drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start)
    replacement = b'#include "src/op/menu/shottype_menu_initial.inl"'
    upstream.write_bytes(data[:start] + replacement + data[end:])
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
        (SNAPSHOT / "th04/m_char.cpp", BASE_MENU_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/m_char.obj", BASE_MENU_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    dependencies = (
        "src/shared/hardware/graphics.hpp",
        "src/shared/platform/abi.hpp",
        "src/shared/platform/pc98.hpp",
        "src/shared/platform/x86.hpp",
        "src/shared/platform/types.hpp",
    )
    source_hashes = {
        "src/op/menu/shottype_menu_initial.cpp": sha_file(SOURCE),
        "src/op/menu/shottype_menu_initial.inl": sha_file(BODY),
        **{path: sha_file(ROOT / path) for path in dependencies},
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
        raise RuntimeError("target OP_01_TEXT identity drift")
    if baseline.program_image[START:NEXT] != body or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 OP_01_TEXT producer differs from target")
    if "0A74:2F10 idle  shottype_menu_put_initial()" not in map_text:
        raise RuntimeError("v489 shottype_menu_put_initial MAP public drift")

    base_object = SNAPSHOT / "obj/th04/m_char.obj"
    base_code = segment_bytes(base_object, "OP_01_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_MENU_CODE_SHA:
        raise RuntimeError("pinned OP_01_TEXT object contribution drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        dst = work / "src/op/menu"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, dst / SOURCE.name)
        shutil.copy2(BODY, dst / BODY.name)
        for dep in dependencies:
            dep_dst = work / dep
            dep_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / dep, dep_dst)

        before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"v660-shottype-menu-initial-standalone-{label}",
               "src/op/menu/shottype_menu_initial.cpp")
        standalone = [path for path in (work / "obj/th04").glob("*.obj")
                      if path.name not in before]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_01_TEXT")
        local_fixups = [
            item
            for record in parse_omf(local_obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]
        expected_fixups = [(1, 94), (1, 88), (1, 85), (3, 74), (3, 57), (3, 40), (3, 29), (1, 5)]
        target_as_unlinked = bytearray(body)
        for kind, offset in expected_fixups:
            width = 2 if kind == 1 else 4
            target_as_unlinked[offset:offset + width] = b"\0" * width
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != bytes(target_as_unlinked)
            or local_fixups != expected_fixups
        ):
            raise RuntimeError(f"{label}: standalone shottype_menu_put_initial OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/m_char.obj"
        group_obj.unlink()
        tcc_op(work, output, f"v660-shottype-menu-initial-group-{label}", "th04/m_char.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_01_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained shottype_menu_put_initial changed grouped OP_01_TEXT")

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
            raise RuntimeError(f"{label}: linked OP m_char layout/body drift")

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
        raise RuntimeError("independent OP shottype_menu_put_initial cold rounds differ")
    current_hashes = {
        "src/op/menu/shottype_menu_initial.cpp": sha_file(SOURCE),
        "src/op/menu/shottype_menu_initial.inl": sha_file(BODY),
        **{path: sha_file(ROOT / path) for path in dependencies},
    }
    if current_hashes != source_hashes:
        raise RuntimeError("maintained shottype_menu_put_initial source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed shottype_menu_put_initial maintained-source cold-link replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "baseline_map_sha256": BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "OP_01_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "cold_determinism": {
            "link_relevant_omf_code_exe_map_program_and_relocations_equal": True,
        },
        "limit": "Decoded 98-byte function only; v489 remains surrounding build scaffold. No packed-file or whole-OP exactness.",
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
