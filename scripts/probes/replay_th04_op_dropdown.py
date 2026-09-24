#!/usr/bin/env python3
"""Cold-compile maintained OP dropdown animation and relink OP_SETUP_TEXT."""

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

SOURCE = ROOT / "src/op/setup/dropdown.cpp"
BODY = ROOT / "src/op/setup/dropdown.inl"
START = 0xB572
SIZE = 0x70
NEXT = START + SIZE
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "470db02e3ed8c6f6009828909b500276b91855b2babf88a1afefd3e467863cc8"


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP dropdown target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP dropdown Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x0E32
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 2
        or int(row["callee_count"]) != 3
    ):
        raise RuntimeError(f"OP dropdown Ghidra extent drift: {row!r}")

    super_calls = (19, 39, 63)
    if any(
        body[offset] != 0x9A
        or int.from_bytes(body[offset + 1:offset + 3], "little") != 0x2D5A
        or int.from_bytes(body[offset + 3:offset + 5], "little") != 0x0000
        for offset in super_calls
    ):
        raise RuntimeError("OP dropdown SUPER_PUT target drift")
    if (
        body[:19] != bytes.fromhex(
            "c8 02 00 00 56 57 8b 46 06 89 46 fe 8b 76 04 50 56 6a 05"
        )
        or body[24:39] != bytes.fromhex(
            "83 46 fe 10 bf 01 00 eb 10 ff 76 fe 56 6a 01"
        )
        or body[44:63] != bytes.fromhex(
            "47 83 46 fe 10 a1 48 2b 48 3b c7 7f e8 ff 76 fe 56 6a 08"
        )
        or body[68:80] != bytes.fromhex(
            "83 c6 10 bf 01 00 eb 12 ff 76 06 56"
        )
        or body[80] != 0xE8
        or START + 83 + int.from_bytes(body[81:83], "little", signed=True) != 0xB49F
        or body[83:85] != bytes.fromhex("6a 01")
        or body[85] != 0x9A
        or int.from_bytes(body[86:88], "little") != 0x002B
        or int.from_bytes(body[88:90], "little") != 0x0DA1
        or body[90:] != bytes.fromhex(
            "47 83 c6 08 a1 4a 2b 03 c0 05 fd ff 3b c7 7f e2 5f 5e c9 c2 04 00"
        )
    ):
        raise RuntimeError("OP dropdown instruction/operand topology drift")

    required = (
        "0F34:2B48 idle  _window",
        "0000:2D5A       SUPER_PUT",
        "0DA1:002B       frame_delay(int)",
        "0A74:0D5F idle  window_dropdown_put(int,int)",
        "0A74:0E32 idle  dropdown(int,int)",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP dropdown MAP target drift")

    return {
        "segment_identity": "1A74",
        "segment_offset": "0E32",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 2,
        "callee_count": 3,
        "window_map_target": "0F34:2B48 _window",
        "window_operands": ["0x2B48 w", "0x2B4A h"],
        "near_call_target": "0xB49F window_dropdown_put",
        "far_call_targets": [
            "0000:2D5A SUPER_PUT",
            "0DA1:002B frame_delay",
        ],
        "constants": {
            "MSWIN_W": 16,
            "MSWIN_H": 16,
            "DROP_FRAMES_PER_TILE": 2,
            "DROP_SPEED": 8,
            "MSWIN_MIDDLE_TOP": 1,
            "MSWIN_LEFT_TOP": 5,
            "MSWIN_RIGHT_TOP": 8,
        },
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
    start_marker = b"void pascal near dropdown(screen_x_t left, screen_y_t top_)\n"
    end_marker = b"\n\nvoid pascal near singleline(screen_x_t left, screen_y_t top)\n"
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise RuntimeError("OP dropdown source anchors drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start)
    replacement = b'#include "src/op/setup/dropdown.inl"'
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
        "src/op/setup/dropdown.cpp": sha_file(SOURCE),
        "src/op/setup/dropdown.inl": sha_file(BODY),
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
        tcc_op(work, output, f"v630-dropdown-standalone-{label}", "src/op/setup/dropdown.cpp")
        standalone = [
            path for path in (work / "obj/th04").glob("*.obj")
            if path.name not in before
        ]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone dropdown object")
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
        expected_fixups = [(1, 95), (3, 86), (1, 81), (3, 64), (1, 50), (3, 40), (3, 20)]
        for kind, offset in expected_fixups:
            width = 2 if kind == 1 else 4
            target_unlinked[offset:offset + width] = b"\0" * width
        # The _window.h FIXUPP keeps the +2 structure-field addend in LEDATA.
        # Target operands 0x2B48/0x2B4A independently bind this to _window + 2.
        target_unlinked[95:97] = bytes((2, 0))
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != bytes(target_unlinked)
            or local_fixups != expected_fixups
        ):
            raise RuntimeError(f"{label}: standalone OP dropdown OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/op_setup.obj"
        group_obj.unlink()
        tcc_op(work, output, f"v630-dropdown-group-{label}", "th04/op_setup.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_SETUP_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained dropdown changed grouped OP_SETUP_TEXT")

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
            raise RuntimeError(f"{label}: linked OP dropdown/layout drift")

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
        raise RuntimeError("independent OP dropdown cold rounds differ")
    if (
        sha_file(SOURCE) != source_hashes["src/op/setup/dropdown.cpp"]
        or sha_file(BODY) != source_hashes["src/op/setup/dropdown.inl"]
    ):
        raise RuntimeError("maintained OP dropdown source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed dropdown maintained-source cold-link replay",
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
        "limit": "Decoded 89-byte function only; no DIET-packed or whole-OP exactness.",
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
