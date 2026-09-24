#!/usr/bin/env python3
"""Cold-compile maintained OP game_exit_to_dos and verify TLINK call optimization."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
from pathlib import Path
import re
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
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/op/core/game_exit_to_dos.cpp"

TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
BASE_OBJECT_SHA = "361de03efc438462c3b452176e3d720242575a88aa29ef1ca7de62ea6839b3cc"
RELOCATIONS = 804

START = 0xDDB1
SIZE = 0x19
NEXT = START + SIZE
TARGET_FUNCTION_SHA = "34ccc70330949c8ffb9377717a0361f8d043f2ea8b6a13480595bccc1b831ced"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def segment_bytes(path: Path, segment_name: str) -> bytes:
    records = parse_omf(path.read_bytes())
    names = [""]
    segments: list[str] = []
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                n = record.data[pos]
                names.append(record.data[pos + 1:pos + 1 + n].decode("latin-1"))
                pos += n + 1
        elif record.record_type == 0x98:
            data = record.data
            pos = 1 + (3 if (data[0] >> 5 == 0) else 2)
            ni, _ = omf_index(data, pos)
            segments.append(names[ni])
    if segments.count(segment_name) != 1:
        raise RuntimeError(f"expected one {segment_name}: {segments}")
    wanted = segments.index(segment_name) + 1
    chunks: list[tuple[int, bytes]] = []
    for record in records:
        if record.record_type != 0xA0:
            continue
        index, pos = omf_index(record.data, 0)
        if index != wanted:
            continue
        offset = int.from_bytes(record.data[pos:pos + 2], "little")
        chunks.append((offset, record.data[pos + 2:]))
    chunks.sort()
    out = bytearray()
    for offset, payload in chunks:
        if offset != len(out):
            raise RuntimeError(f"{segment_name} LEDATA gap/overlap at {offset:#x}")
        out += payload
    return bytes(out)


def map_contribution(path: Path) -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=SHARED\b.*\bM=th02/exit_dos\.cpp(?:\s|$)",
        re.I,
    )
    matches = []
    for line in path.read_text(encoding="cp437").splitlines():
        found = pattern.search(line)
        if found:
            matches.append((
                int(found[1], 16) * 16 + int(found[2], 16),
                int(found[3], 16),
                line.strip(),
            ))
    if len(matches) != 1:
        raise RuntimeError(f"expected one exit_dos MAP contribution: {matches}")
    return matches[0]


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP game_exit_to_dos target identity drift")
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP game_exit_to_dos Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1DA1
        or int(row["entry_offset"], 0) != 0x03A1
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 4
    ):
        raise RuntimeError(f"OP game_exit_to_dos Ghidra extent drift: {row!r}")

    # TLINK rewrites the same-segment FAR call to game_exit into
    # NOP / PUSH CS / CALL rel16 while preserving the 5-byte call footprint.
    if (
        body[:3] != b"\x55\x8b\xec"
        or body[3:5] != b"\x90\x0e"
        or body[5] != 0xE8
        or START + 8 + int.from_bytes(body[6:8], "little", signed=True) != 0xE0AC
        or body[8:13] != b"\x9a\x6a\x1d\x00\x00"
        or body[13:18] != b"\x9a\x32\x25\x00\x00"
        or body[18:23] != b"\x9a\x26\x25\x00\x00"
        or body[23:] != b"\x5d\xcb"
    ):
        raise RuntimeError("OP game_exit_to_dos target call topology drift")

    required = (
        "0DA1:069C       game_exit()",
        "0000:1D6A       KEY_BEEP_ON",
        "0000:2532       TEXT_SYSTEMLINE_SHOW",
        "0000:2526       TEXT_CURSOR_SHOW",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP game_exit_to_dos MAP call targets drift")

    return {
        "segment_identity": "1DA1",
        "segment_offset": "03A1",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 4,
        "same_segment_call": "0xE0AC game_exit",
        "far_calls": [
            "0000:1D6A KEY_BEEP_ON",
            "0000:2532 TEXT_SYSTEMLINE_SHOW",
            "0000:2526 TEXT_CURSOR_SHOW",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        parser.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "obj/th02/exit_dos.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid OP target/baseline control")
    target_relocs = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_relocs:
        raise RuntimeError("v489 OP ordered relocations differ from target")

    body = target.program_image[START:NEXT]
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    boundary = target_boundary(body, map_text)
    if baseline.program_image[START:NEXT] != body:
        raise RuntimeError("v489 game_exit_to_dos bytes differ from target")
    start, size, line = map_contribution(SNAPSHOT / "obj/th04/op.map")
    if (start, size) != (START, SIZE):
        raise RuntimeError(f"v489 exit_dos ownership drift: {line}")

    source_hash = sha_file(SOURCE)
    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        shutil.copy2(SOURCE, work / "th02/exit_dos.cpp")

        obj = work / "obj/th02/exit_dos.obj"
        obj.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-",
             "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th02/", "th02/exit_dos.cpp"],
            work, output / f"compile-{label}.log",
        )
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "SHARED")
        fixups = [
            item
            for record in parse_omf(obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]
        unlinked = (
            b"\x55\x8b\xec"
            + (b"\x9a" + b"\0\0\0\0") * 4
            + b"\x5d\xcb"
        )
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != unlinked
            or fixups != [(3, 19), (3, 14), (3, 9), (3, 4)]
        ):
            raise RuntimeError(f"{label}: exit_dos OMF/code/fixup drift")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[START:NEXT]
        map_start, map_size, map_line = map_contribution(mp)
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_relocs
            or image.program_image != baseline.program_image
            or linked != body
            or (map_start, map_size) != (START, SIZE)
        ):
            raise RuntimeError(f"{label}: linked OP game_exit_to_dos/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "source_object_sha256": sha_file(obj),
            "source_link_relevant_omf_sha256": link_relevant_omf_sha(obj),
            "source_code_sha256": sha(code),
            "source_fixup_sites": [list(item) for item in fixups],
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked),
            "raw_function_difference_count": 0,
            "ordered_relocations": len(target_relocs),
            "map_contribution": map_line,
            "tlink_same_segment_far_call_optimized": linked[3:8] == b"\x90\x0e\xe8\xf3\x02",
        }

    stable = (
        "source_link_relevant_omf_sha256", "source_code_sha256",
        "source_fixup_sites", "linked_exe_sha256", "linked_map_sha256",
        "linked_program_sha256", "linked_function_sha256",
        "raw_function_difference_count", "ordered_relocations",
        "map_contribution", "tlink_same_segment_far_call_optimized",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable):
        raise RuntimeError("independent OP game_exit_to_dos cold rounds differ")
    if sha_file(SOURCE) != source_hash:
        raise RuntimeError("maintained game_exit_to_dos source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed game_exit_to_dos maintained-source cold-link replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "baseline_map_sha256": BASE_MAP_SHA,
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "boundary": boundary,
        "producer": {
            "segment": "SHARED",
            "payload_offset": hex(START),
            "size": SIZE,
            "target_linked_sha256": sha(body),
        },
        "builds": builds,
        "limit": "Decoded 25-byte function only; no DIET-packed offset or whole-OP exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "function_sha256": builds["a"]["linked_function_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
