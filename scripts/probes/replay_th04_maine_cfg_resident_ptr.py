#!/usr/bin/env python3
"""Cold-compile maintained MAINE cfg_load_resident_ptr and relink MAINE_E_TEXT."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import csv
import hashlib
import json
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
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/maine/core/cfg_load_resident_ptr.cpp"
BODY = ROOT / "src/maine/core/cfg_load_resident_ptr.inl"

TARGET_SHA = "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533"
BASE_EXE_SHA = "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c"
BASE_MAP_SHA = "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e"
BASE_WRAPPER_SHA = "01e1e5ad494a8ed534080c4404f0f73e7fdaf1621e60ecbe8286c3ae1d0736af"
BASE_ENTRY_SHA = "12b2691adb49441da38573de5912938176e229fbd69a148eb747275e2a5128f6"
BASE_OBJECT_SHA = "561dbd875436121f4357763a6bd49b22ef087f0247ac460fff70e35d646f3c4e"
BASE_CODE_SHA = "e674aa8c05279f7a1f1f5d1c3eaee82928d193f36b14c901b5ef039af80947f1"

START = 0xA059
SIZE = 0x31
NEXT = START + SIZE
PRODUCER_START = START
PRODUCER_SIZE = 0x239
TARGET_FUNCTION_SHA = "d80e86557f5913ec5b6cd7a168bdefbc88623b97b6c691e4b555c694ac77ede1"
TARGET_PRODUCER_SHA = "2dc26bd755036b3f18a9616b09e66f1bf0854ffffe2dcce4757573e77df286d3"
RELOCATIONS = 559


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def map_contribution(path: Path) -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=MAINE_E_TEXT\b.*\bM=th04/maine_e\.cpp(?:\s|$)",
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
        raise RuntimeError(f"expected one MAINE_E_TEXT contribution: {matches}")
    return matches[0]


def loose_segment_bytes(path: Path, segment_name: str) -> bytes:
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


def target_boundary(body: bytes, target_program: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE cfg_load_resident_ptr target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("MAINE cfg_load_resident_ptr Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x0009
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 3
    ):
        raise RuntimeError(f"MAINE cfg_load_resident_ptr Ghidra extent drift: {row!r}")

    if (
        body[:7] != bytes.fromhex("c8 0a 00 00 56 1e 68")
        or int.from_bytes(body[7:9], "little") != 0x0094
        or body[9:14] != bytes.fromhex("9a 88 0a 00 00")
        or body[14:21] != bytes.fromhex("16 8d 46 f6 50 6a 0a")
        or body[21:26] != bytes.fromhex("9a d4 09 00 00")
        or body[26:31] != bytes.fromhex("9a 68 09 00 00")
        or body[31:38] != bytes.fromhex("8b 76 fc 89 36 a0 0e")
        or body[38:44] != bytes.fromhex("c7 06 9e 0e 00 00")
        or body[44:] != bytes.fromhex("8b c6 5e c9 c3")
    ):
        raise RuntimeError("MAINE cfg_load_resident_ptr instruction topology drift")

    cfg_linear = 0x0E53 * 16 + 0x0094
    if target_program[cfg_linear:cfg_linear + 9] != b"MIKO.CFG\0":
        raise RuntimeError("MAINE target CFG filename drift")
    required = (
        "0000:0A88       FILE_ROPEN",
        "0000:09D4       FILE_READ",
        "0000:0968       FILE_CLOSE",
        "0E53:0E9E       _resident",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE cfg resident MAP target drift")

    return {
        "segment_identity": "1A05",
        "segment_offset": "0009",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 3,
        "cfg_size": 10,
        "cfg_filename": "MIKO.CFG",
        "file_calls": ["FILE_ROPEN", "FILE_READ", "FILE_CLOSE"],
        "resident_map_target": "0E53:0E9E _resident",
    }


def overlay_source(work: Path) -> str:
    entry = work / "th04/end/entry.cpp"
    if sha_file(entry) != BASE_ENTRY_SHA:
        raise RuntimeError("pinned v489 end/entry.cpp drift")
    dst = work / "src/maine/core"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)
    data = entry.read_bytes()
    old = (
        b"resident_t __seg* near cfg_load_resident_ptr(void)\n"
        b"{\n"
        b"\tcfg_t cfg;\n"
        b"\treturn cfg_load_and_set_resident(cfg, CFG_FN);\n"
        b"}"
    )
    replacement = b'#include "src/maine/core/cfg_load_resident_ptr.inl"'
    if data.count(old) != 1:
        raise RuntimeError("cfg_load_resident_ptr replacement anchor drift")
    entry.write_bytes(data.replace(old, replacement, 1))
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
        "src/maine/core/cfg_load_resident_ptr.cpp": sha_file(SOURCE),
        "src/maine/core/cfg_load_resident_ptr.inl": sha_file(BODY),
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
    boundary = target_boundary(body, target.program_image, map_text)
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target MAINE_E_TEXT identity drift")
    if baseline.program_image[START:NEXT] != body or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 MAINE_E_TEXT differs from target")
    map_start, map_size, map_line = map_contribution(SNAPSHOT / "obj/th04/maine.map")
    if (map_start, map_size) != (PRODUCER_START, PRODUCER_SIZE):
        raise RuntimeError(f"v489 MAINE_E_TEXT ownership drift: {map_line}")
    if "0A05:0009 idle  cfg_load_resident_ptr()" not in map_text:
        raise RuntimeError("v489 cfg_load_resident_ptr MAP public drift")

    base_obj = SNAPSHOT / "obj/th04/maine_e.obj"
    base_code = segment_bytes(base_obj, "MAINE_E_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_CODE_SHA:
        raise RuntimeError("pinned MAINE_E_TEXT object contribution drift")

    standalone_expected = bytes.fromhex(
        "c8 0a 00 00 56 1e 68 00 00 9a 00 00 00 00 "
        "16 8d 46 f6 50 6a 0a 9a 00 00 00 00 9a 00 00 00 00 "
        "8b 76 fc 89 36 02 00 c7 06 00 00 00 00 8b c6 5e c9 c3"
    )
    grouped_expected = bytes.fromhex(
        "c8 0a 00 00 56 1e 68 04 00 9a 00 00 00 00 "
        "16 8d 46 f6 50 6a 0a 9a 00 00 00 00 9a 00 00 00 00 "
        "8b 76 fc 89 36 02 00 c7 06 00 00 00 00 8b c6 5e c9 c3"
    )
    if base_code[:SIZE] != grouped_expected:
        raise RuntimeError("pinned grouped cfg_load_resident_ptr bytes drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "maine")

        dst = work / "src/maine/core"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, dst / SOURCE.name)
        shutil.copy2(BODY, dst / BODY.name)

        before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc(work, output, f"v604-cfg-resident-standalone-{label}",
            "src/maine/core/cfg_load_resident_ptr.cpp")
        standalone = [path for path in (work / "obj/th04").glob("*.obj")
                      if path.name not in before]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "MAINE_E_TEXT")
        local_fixups = [
            item
            for record in parse_omf(local_obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != standalone_expected
            or local_fixups != [(1, 40), (1, 36), (3, 27), (3, 22), (3, 10), (1, 7)]
        ):
            raise RuntimeError(f"{label}: standalone cfg resident OMF/code drift")

        patched_entry_sha = overlay_source(work)
        group_obj = work / "obj/th04/maine_e.obj"
        group_obj.unlink()
        tcc(work, output, f"v604-cfg-resident-group-{label}", "th04/maine_e.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "MAINE_E_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained cfg resident changed grouped MAINE_E_TEXT")

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
            raise RuntimeError(f"{label}: linked MAINE cfg resident/layout drift")

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
        raise RuntimeError("independent MAINE cfg resident cold rounds differ")
    if (
        sha_file(SOURCE) != source_hashes["src/maine/core/cfg_load_resident_ptr.cpp"]
        or sha_file(BODY) != source_hashes["src/maine/core/cfg_load_resident_ptr.inl"]
    ):
        raise RuntimeError("maintained cfg resident source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed cfg_load_resident_ptr maintained-source cold-link replay",
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
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "limit": "Decoded 49-byte function only; no DIET-packed offset or whole-MAINE exactness.",
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
