#!/usr/bin/env python3
"""Cold-compile maintained MAINE end_animate and relink MAINE_E_TEXT."""

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

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_maine_game_exit_and_exec import (  # noqa: E402
    BASE_CODE_SHA,
    BASE_ENTRY_SHA,
    BASE_EXE_SHA,
    BASE_MAP_SHA,
    BASE_OBJECT_SHA,
    BASE_WRAPPER_SHA,
    PRODUCER_SIZE,
    PRODUCER_START,
    RELOCATIONS,
    SNAPSHOT,
    TARGET,
    TARGET_PRODUCER_SHA,
    TARGET_SHA,
    loose_segment_bytes,
    map_contribution,
    sha,
    sha_file,
)
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402

SOURCE = ROOT / "src/maine/end/end_animate.cpp"
BODY = ROOT / "src/maine/end/end_animate.inl"
RESIDENT = ROOT / "src/shared/config/resident.hpp"
SCORE = ROOT / "src/shared/config/score.hpp"
TYPES = ROOT / "src/shared/platform/types.hpp"

START = 0xA0BD
SIZE = 0x45
NEXT = START + SIZE
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "3e1b8ce8c2a22d9c97342ddb6214fdddc33076dc341eb2175c57c59e0f08e725"
BASE_LINK_RELEVANT_OMF_SHA = "24f9e7d7a0399632906e14a8a0de12254e7fe697a4c90d6ca7102a67a96c86ae"


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE end_animate target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("MAINE end_animate Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x006D
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 3
    ):
        raise RuntimeError(f"MAINE end_animate Ghidra extent drift: {row!r}")

    # Three resident fields are copied into SCRIPT_FN[3:6], then the script is
    # loaded, animated, and freed. The raw offsets are target evidence.
    if (
        body[:3] != bytes.fromhex("55 8b ec")
        or body[3:11] != bytes.fromhex("c4 1e 9e 0e 26 8a 47 12")
        or body[11:19] != bytes.fromhex("c4 1e 90 00 26 88 47 03")
        or body[19:27] != bytes.fromhex("c4 1e 9e 0e 26 8a 47 19")
        or body[27:29] != bytes.fromhex("04 30")
        or body[29:37] != bytes.fromhex("c4 1e 90 00 26 88 47 04")
        or body[37:45] != bytes.fromhex("c4 1e 9e 0e 26 8a 47 25")
        or body[45:53] != bytes.fromhex("c4 1e 90 00 26 88 47 05")
        or body[53:58] != bytes.fromhex("ff 36 92 00 53")
        or body[58] != 0xE8
        or START + 61 + int.from_bytes(body[59:61], "little", signed=True) != 0xA292
        or body[61] != 0xE8
        or START + 64 + int.from_bytes(body[62:64], "little", signed=True) != 0xADFC
        or body[64] != 0xE8
        or START + 67 + int.from_bytes(body[65:67], "little", signed=True) != 0xA2D1
        or body[67:] != bytes.fromhex("5d c3")
    ):
        raise RuntimeError("MAINE end_animate instruction/operand topology drift")

    required = (
        "0E53:0E9E       _resident",
        "0A05:0242       cutscene_script_load(const char far*)",
        "0A05:0DAC       cutscene_animate()",
        "0A05:0281       cutscene_script_free()",
        "0A05:006D idle  end_animate()",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE end_animate MAP target drift")

    return {
        "segment_identity": "1A05",
        "segment_offset": "006D",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 3,
        "resident_map_target": "0E53:0E9E _resident",
        "resident_field_offsets": {
            "playchar_ascii": 0x12,
            "shottype": 0x19,
            "end_type_ascii": 0x25,
        },
        "script_pointer_operand": "DGROUP:0090/0092",
        "near_calls": [
            "0xA292 cutscene_script_load",
            "0xADFC cutscene_animate",
            "0xA2D1 cutscene_script_free",
        ],
    }


def overlay_source(work: Path) -> str:
    entry = work / "th04/end/entry.cpp"
    if sha_file(entry) != BASE_ENTRY_SHA:
        raise RuntimeError("pinned v489 end/entry.cpp drift")
    dst = work / "src/maine/end"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)

    data = entry.read_bytes()
    start_marker = b"void near end_animate(void)\n"
    end_marker = b"\n\n#define congratulations_animate"
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise RuntimeError("end_animate source anchors drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start)
    replacement = b'#include "src/maine/end/end_animate.inl"'
    entry.write_bytes(data[:start] + replacement + data[end:])
    return sha_file(entry)


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
        (SNAPSHOT / "bin/th04/maine.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/maine.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/maine_e.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "th04/end/entry.cpp", BASE_ENTRY_SHA),
        (SNAPSHOT / "obj/th04/maine_e.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        "src/maine/end/end_animate.cpp": sha_file(SOURCE),
        "src/maine/end/end_animate.inl": sha_file(BODY),
        "src/shared/config/resident.hpp": sha_file(RESIDENT),
        "src/shared/config/score.hpp": sha_file(SCORE),
        "src/shared/platform/types.hpp": sha_file(TYPES),
    }

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid MAINE target/baseline control")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 MAINE ordered relocations differ from target")

    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    boundary = target_boundary(body, map_text)
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target MAINE_E_TEXT identity drift")
    if (
        baseline.program_image[START:NEXT] != body
        or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        != producer
    ):
        raise RuntimeError("v489 MAINE_E_TEXT differs from target")
    map_start, map_size, map_line = map_contribution(SNAPSHOT / "obj/th04/maine.map")
    if (map_start, map_size) != (PRODUCER_START, PRODUCER_SIZE):
        raise RuntimeError(f"v489 MAINE_E_TEXT ownership drift: {map_line}")

    base_obj = SNAPSHOT / "obj/th04/maine_e.obj"
    base_code = segment_bytes(base_obj, "MAINE_E_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_CODE_SHA:
        raise RuntimeError("pinned MAINE_E_TEXT object contribution drift")

    # All ten references remain OMF fixups in the grouped object too.
    grouped_expected = bytearray(body)
    for off in (5, 13, 21, 31, 39, 47, 59, 62, 65):
        grouped_expected[off:off + 2] = bytes((0, 0))
    grouped_expected[55:57] = bytes((2, 0))
    if base_code[LOCAL_START:LOCAL_START + SIZE] != bytes(grouped_expected):
        raise RuntimeError("pinned grouped end_animate bytes drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "maine")

        for src in (SOURCE, BODY, RESIDENT, SCORE, TYPES):
            rel = src.relative_to(ROOT)
            dst = work / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc(work, output, f"v616-end-animate-standalone-{label}",
            "src/maine/end/end_animate.cpp")
        standalone = [
            path for path in (work / "obj/th04").glob("*.obj")
            if path.name not in before
        ]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone end object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "MAINE_E_TEXT")
        local_fixups = [
            item
            for record in parse_omf(local_obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]
        standalone_expected = grouped_expected
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != bytes(standalone_expected)
            or local_fixups != [
                (3, 0),
                (1, 65), (1, 62), (1, 59), (1, 55), (1, 47),
                (1, 39), (1, 31), (1, 21), (1, 13), (1, 5),
            ]
        ):
            raise RuntimeError(f"{label}: standalone end_animate OMF/code drift")

        patched_entry_sha = overlay_source(work)
        group_obj = work / "obj/th04/maine_e.obj"
        group_obj.unlink()
        tcc(work, output, f"v616-end-animate-group-{label}", "th04/maine_e.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "MAINE_E_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
            or link_relevant_omf_sha(group_obj) != BASE_LINK_RELEVANT_OMF_SHA
        ):
            raise RuntimeError(f"{label}: maintained end_animate changed grouped MAINE_E_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked_body = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        linked_start, linked_size, linked_line = map_contribution(mp)
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or image.program_image != baseline.program_image
            or linked_body != body
            or linked_producer != producer
            or (linked_start, linked_size) != (PRODUCER_START, PRODUCER_SIZE)
        ):
            raise RuntimeError(f"{label}: linked MAINE end_animate/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_entry_sha256": patched_entry_sha,
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
            "map_contribution": linked_line,
        }

    stable = (
        "standalone_link_relevant_omf_sha256", "standalone_code_sha256",
        "standalone_fixup_sites", "group_link_relevant_omf_sha256",
        "group_code_sha256", "linked_exe_sha256", "linked_map_sha256",
        "linked_program_sha256", "linked_function_sha256", "linked_producer_sha256",
        "raw_function_difference_count", "raw_producer_difference_count",
        "ordered_relocations", "map_contribution",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable):
        raise RuntimeError("independent MAINE end_animate cold rounds differ")
    for path, digest in source_hashes.items():
        if sha_file(ROOT / path) != digest:
            raise RuntimeError(f"maintained source changed during replay: {path}")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed end_animate maintained-source cold-link replay",
        "artifact": "th04-maine",
        "target_restored_sha256": TARGET_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "baseline_map_sha256": BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "MAINE_E_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "limit": "Decoded 69-byte function only; no DIET-packed or whole-MAINE exactness.",
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
