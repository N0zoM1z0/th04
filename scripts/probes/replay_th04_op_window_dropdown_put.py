#!/usr/bin/env python3
"""Cold-compile maintained OP window_dropdown_put and relink OP_SETUP_TEXT."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_op_help_put import (  # noqa: E402
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
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402

SOURCE = ROOT / "src/op/setup/window_dropdown_put.cpp"
BODY = ROOT / "src/op/setup/window_dropdown_put.inl"
START = 0xB49F
SIZE = 0x7A
NEXT = START + SIZE
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "47435708ff5c7f8b0897a21c863c4a79c617b3d4d53e39537bf71dc0c8d7889c"


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP window_dropdown_put target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP window_dropdown_put Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x0D5F
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 2
    ):
        raise RuntimeError(f"OP window_dropdown_put Ghidra extent drift: {row!r}")

    far_calls = (
        (23, 0x0968, 0x0DA1),
        (32, 0x2D5A, 0x0000),
        (44, 0x2D5A, 0x0000),
        (63, 0x2D5A, 0x0000),
        (75, 0x2D5A, 0x0000),
        (99, 0x2D5A, 0x0000),
        (111, 0x2D5A, 0x0000),
    )
    if (
        body[:15] != bytes.fromhex("c8 02 00 00 56 57 8b 76 06 8b 7e 04 56 57 a1")
        or int.from_bytes(body[15:17], "little") != 0x2B48
        or int.from_bytes(body[87:89], "little") != 0x2B48
        or any(
            body[off] != 0x9A
            or int.from_bytes(body[off + 1:off + 3], "little") != target_off
            or int.from_bytes(body[off + 3:off + 5], "little") != target_seg
            for off, target_off, target_seg in far_calls
        )
        or body[30:32] != bytes.fromhex("6a 02")
        or body[42:44] != bytes.fromhex("6a 06")
        or body[61:63] != bytes.fromhex("6a 00")
        or body[73:75] != bytes.fromhex("6a 03")
        or body[97:99] != bytes.fromhex("6a 04")
        or body[109:111] != bytes.fromhex("6a 07")
        or body[-6:] != bytes.fromhex("5f 5e c9 c2 04 00")
    ):
        raise RuntimeError("OP window_dropdown_put instruction/operand topology drift")

    required = (
        "0F34:2B48 idle  _window",
        "0DA1:0968       egc_copy_rect_1_to_0_16(int,int,int,int)",
        "0000:2D5A       SUPER_PUT",
        "0A74:0D5F idle  window_dropdown_put(int,int)",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP window_dropdown_put MAP target drift")

    return {
        "segment_identity": "1A74",
        "segment_offset": "0D5F",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 2,
        "window_map_target": "0F34:2B48 _window",
        "window_w_operands": ["0x2B48", "0x2B48"],
        "far_call_targets": [
            "0DA1:0968 egc_copy_rect_1_to_0_16",
            "0000:2D5A SUPER_PUT",
        ],
        "patterns": {
            "left": [2, 6],
            "middle": [0, 3],
            "right": [4, 7],
        },
        "constants": {"MSWIN_W": 16, "MSWIN_H": 16, "DROP_SPEED": 8},
        "terminal": "RET 4",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/op/m_setup.cpp"
    if sha_file(upstream) != BASE_SETUP_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP setup source drift")

    dst = work / "src/op/setup"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)

    data = upstream.read_bytes()
    start_marker = b"void pascal near window_dropdown_put(\n\tscreen_x_t left, screen_y_t bottom_tile_top\n)\n"
    end_marker = b"\n\nvoid pascal near window_rollup_put(screen_x_t left, screen_y_t bottom_tile_top)\n"
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise RuntimeError("OP window_dropdown_put source anchors drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start)
    replacement = b'#include "src/op/setup/window_dropdown_put.inl"'
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

    source_hashes = {
        "src/op/setup/window_dropdown_put.cpp": sha_file(SOURCE),
        "src/op/setup/window_dropdown_put.inl": sha_file(BODY),
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
        raise RuntimeError("target OP_SETUP_TEXT identity drift")
    if (
        baseline.program_image[START:NEXT] != body
        or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        != producer
    ):
        raise RuntimeError("v489 OP setup producer differs from target")

    base_object = SNAPSHOT / "obj/th04/op_setup.obj"
    base_code = segment_bytes(base_object, "OP_SETUP_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_SETUP_CODE_SHA:
        raise RuntimeError("pinned OP_SETUP_TEXT object contribution drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        from compact_op_maine_snapshot import copy_compact_snapshot
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")

        dst = work / "src/op/setup"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, dst / SOURCE.name)
        shutil.copy2(BODY, dst / BODY.name)

        before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"v632-window-dropdown-put-standalone-{label}", "src/op/setup/window_dropdown_put.cpp")
        standalone = [
            path for path in (work / "obj/th04").glob("*.obj")
            if path.name not in before
        ]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone window_dropdown_put object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_SETUP_TEXT")
        local_fixups = [
            item
            for record in parse_omf(local_obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]
        target_unlinked = bytearray(body)
        expected_fixups = [(3, 112), (3, 100), (1, 87), (3, 76), (3, 64), (3, 45), (3, 33), (3, 24), (1, 15)]
        for kind, offset in expected_fixups:
            width = 2 if kind == 1 else 4
            target_unlinked[offset:offset + width] = b"\0" * width
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != bytes(target_unlinked)
            or local_fixups != expected_fixups
        ):
            raise RuntimeError(f"{label}: standalone OP window_dropdown_put OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/op_setup.obj"
        group_obj.unlink()
        tcc_op(work, output, f"v632-window-dropdown-put-group-{label}", "th04/op_setup.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_SETUP_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained window_dropdown_put changed grouped OP_SETUP_TEXT")

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
            raise RuntimeError(f"{label}: linked OP window_dropdown_put/layout drift")

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
        raise RuntimeError("independent OP window_dropdown_put cold rounds differ")
    if (
        sha_file(SOURCE) != source_hashes["src/op/setup/window_dropdown_put.cpp"]
        or sha_file(BODY) != source_hashes["src/op/setup/window_dropdown_put.inl"]
    ):
        raise RuntimeError("maintained OP window_dropdown_put source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed window_dropdown_put maintained-source cold-link replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "baseline_map_sha256": BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "OP_SETUP_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "limit": "Decoded 122-byte function only; no DIET-packed or whole-OP exactness.",
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
