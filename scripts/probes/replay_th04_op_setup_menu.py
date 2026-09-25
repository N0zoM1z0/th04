#!/usr/bin/env python3
"""Cold-compile maintained OP setup_menu and relink OP_SETUP_TEXT."""

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
from replay_th04_op_help_put import (
    BASE_EXE_SHA,
    BASE_MAP_SHA,
    BASE_SETUP_CODE_SHA,
    BASE_SETUP_OBJECT_SHA,
    BASE_SETUP_SOURCE_SHA,
    PRODUCER_SIZE,
    PRODUCER_START,
    RELOCATIONS,
    SNAPSHOT,
    TARGET,
    TARGET_PRODUCER_SHA,
    TARGET_SHA,
    loose_segment_bytes,
    sha,
    sha_file,
    tcc_op,
)
from replay_th04_scroll_driver_natural import fixup_locations
from replay_th04_shared_delay_measure import link_relevant_omf_sha
from replay_th04_zun_source_only import source_closure

SOURCE = ROOT / "src/op/setup/setup_menu.cpp"
BODY = ROOT / "src/op/setup/setup_menu.inl"
START = 0xB9CE
SIZE = 0x77
NEXT = START + SIZE
TARGET_FUNCTION_SHA = "88ee8739a039039549ed4c7902a3cdeae05276b4a8d7cb5c70d9974ad9686df5"
STANDALONE_CODE_SHA = "28f522d472d9004734caa7b4261a222b976cbac56868edaa8a0df8b8f4169631"
STANDALONE_FIXUPS = [
    (3, 113), (3, 108), (1, 103), (3, 98), (3, 91),
    (1, 86), (3, 81), (3, 74), (3, 67), (1, 64),
    (1, 59), (3, 53), (3, 43), (3, 36), (1, 33),
    (3, 19), (1, 16), (3, 10), (1, 5),
]


def object_fixups(obj: Path) -> list[tuple[int, int]]:
    return [
        item
        for rec in parse_omf(obj.read_bytes())
        if rec.record_type == 0x9C
        for item in fixup_locations(rec.data)
    ]


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP setup_menu target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP setup_menu Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x128E
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 13
    ):
        raise RuntimeError(f"OP setup_menu Ghidra extent drift: {row!r}")

    far_calls = (
        (9, 0x1DE0, 0x0000),
        (18, 0x2A86, 0x0000),
        (35, 0x00ED, 0x0DA1),
        (42, 0x0040, 0x0DA1),
        (52, 0x0065, 0x0DA1),
        (66, 0x1618, 0x0000),
        (73, 0x156C, 0x0000),
        (80, 0x0622, 0x0000),
        (90, 0x002B, 0x0DA1),
        (97, 0x156C, 0x0000),
        (107, 0x0666, 0x0000),
        (112, 0x2922, 0x0000),
    )
    if (
        body[:9] != bytes.fromhex("55 8b ec c7 06 86 05 00 00")
        or any(
            body[off] != 0x9A
            or int.from_bytes(body[off + 1:off + 3], "little") != target_off
            or int.from_bytes(body[off + 3:off + 5], "little") != target_seg
            for off, target_off, target_seg in far_calls
        )
        or body[14:18] != bytes.fromhex("1e 68 6f 0e")
        or body[23:29] != bytes.fromhex("ba a6 00 b0 01 ee")
        or body[29:35] != bytes.fromhex("6a 00 1e 68 79 0e")
        or body[40:42] != bytes.fromhex("6a 00")
        or body[47:52] != bytes.fromhex("66 6a 00 6a 00")
        or body[57:66] != bytes.fromhex("1e 68 88 23 66 ff 36 70 23")
        or body[71:73] != bytes.fromhex("6a 00")
        or body[78:80] != bytes.fromhex("6a 01")
        or body[85] != 0xE8
        or START + 88 + int.from_bytes(body[86:88], "little", signed=True) != 0xB794
        or body[88:90] != bytes.fromhex("6a 01")
        or body[95:97] != bytes.fromhex("6a 00")
        or body[102] != 0xE8
        or START + 105 + int.from_bytes(body[103:105], "little", signed=True) != 0xB8B1
        or body[105:107] != bytes.fromhex("6a 01")
        or body[-2:] != bytes.fromhex("5d c3")
    ):
        raise RuntimeError("OP setup_menu instruction/operand topology drift")

    required = (
        "0A74:128E       setup_menu()",
        "0A74:1054 idle  setup_bgm_menu()",
        "0A74:1171 idle  setup_se_menu()",
        "0000:1DE0       PALETTE_SHOW",
        "0000:2A86       SUPER_ENTRY_BFNT",
        "0DA1:00ED       pi_load(int,const char far*)",
        "0DA1:0040       pi_palette_apply(int)",
        "0DA1:0065       pi_put_8(int,int,int)",
        "0000:1618       GRAPH_PI_FREE",
        "0000:156C       GRAPH_COPY_PAGE",
        "0000:0622       PALETTE_BLACK_IN",
        "0DA1:002B       frame_delay(int)",
        "0000:0666       PALETTE_BLACK_OUT",
        "0000:2922       SUPER_FREE",
        "0F34:0586       _PaletteTone",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP setup_menu MAP target drift")

    return {
        "segment_identity": "1A74",
        "segment_offset": "128E",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 1,
        "callee_count": 13,
        "palette_tone": 0,
        "access_page": 1,
        "pi_slot": 0,
        "frame_delay": 1,
        "terminal": "RET",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/op/m_setup.cpp"
    if sha_file(upstream) != BASE_SETUP_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP setup source drift")

    dst = work / "src/op/setup"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)

    data = upstream.read_bytes()
    start_marker = b"void near setup_menu(void)\n"
    if data.count(start_marker) != 1:
        raise RuntimeError("OP setup_menu source anchor drift")
    start = data.index(start_marker)
    tail = data[start:]
    end_marker = b"\tsuper_free();\n}\n"
    if tail.count(end_marker) != 1:
        raise RuntimeError("OP setup_menu end anchor drift")
    end = start + tail.index(end_marker) + len(end_marker)
    if data[end:].strip():
        raise RuntimeError("unexpected source after setup_menu")
    upstream.write_bytes(
        data[:start] + b'#include "src/op/setup/setup_menu.inl"\n'
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
        (SNAPSHOT / "th04/op/m_setup.cpp", BASE_SETUP_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_setup.obj", BASE_SETUP_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target")

    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    bound = target_boundary(body, map_text)
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target OP_SETUP_TEXT identity drift")
    if (
        baseline.program_image[START:NEXT] != body
        or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer
    ):
        raise RuntimeError("v489 OP setup producer differs from target")

    base_obj = SNAPSHOT / "obj/th04/op_setup.obj"
    base_code = segment_bytes(base_obj, "OP_SETUP_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_SETUP_CODE_SHA:
        raise RuntimeError("pinned OP_SETUP_TEXT object contribution drift")

    closure = source_closure(ROOT, ("src/op/setup/setup_menu.cpp",))
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
        tcc_op(work, output, f"setup-menu-standalone-{label}",
               "src/op/setup/setup_menu.cpp")
        standalone = [
            p for p in (work / "obj/th04").glob("*.obj")
            if p.name not in before
        ]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone setup_menu object")
        local_obj = standalone[0]
        local_desc = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_SETUP_TEXT")
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
            raise RuntimeError(f"{label}: standalone setup_menu OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/op_setup.obj"
        group_obj.unlink()
        tcc_op(work, output, f"setup-menu-group-{label}", "th04/op_setup.cpp")
        group_desc = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_SETUP_TEXT")
        if (
            not group_desc["valid"]
            or "TC86 Borland C++ 4.02" not in group_desc["translator_comments"]
            or group_code != base_code
            or link_relevant_omf_sha(group_obj) != link_relevant_omf_sha(
                SNAPSHOT / "obj/th04/op_setup.obj"
            )
        ):
            raise RuntimeError(f"{label}: grouped OP setup object drift")

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
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or image.program_image != baseline.program_image
            or linked_body != body
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked OP setup_menu/layout drift")

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

    stable = (
        "standalone_link_relevant_omf_sha256", "standalone_code_sha256",
        "standalone_fixup_sites", "group_link_relevant_omf_sha256",
        "group_code_sha256", "linked_exe_sha256", "linked_map_sha256",
        "linked_program_sha256", "linked_function_sha256",
        "linked_producer_sha256", "raw_function_difference_count",
        "raw_producer_difference_count", "ordered_relocations",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable):
        raise RuntimeError("independent OP setup_menu cold rounds differ")
    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained OP setup_menu source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "source_sha256": source_hashes,
        "boundary": bound,
        "producer": {
            "segment": "OP_SETUP_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "limit": "Decoded 119-byte setup_menu only; no packed-file or whole-OP exactness.",
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
