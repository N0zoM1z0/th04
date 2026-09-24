#!/usr/bin/env python3
"""Cold-compile maintained TH04 script_param_read_number_second and relink MAINE."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
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
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_score_hiscore_boundaries import branch_edges, disassemble  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
import replay_th04_maine_score_insert as prior  # noqa: E402

SOURCE = ROOT / "src/maine/cutscene/script_param_second.cpp"
BODY = ROOT / "src/maine/cutscene/script_param_second.inl"
START = 0xA713
SIZE = 0x28
NEXT = START + SIZE
PRODUCER_START = 0xA292
PRODUCER_SIZE = 0xC3E
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "c1084216dbfe91eb2070e9da7cbccb2084d35e4569af9c60f2adc02e25a9d93e"
BASE_CUTSCENE_SOURCE_SHA = "49fbde7cc661dda1d8a290debe285d625f4d274abb9c68c42d28150c59afb760"
BASE_SCRIPT_HEADER_SHA = "b43f978834d21ea9d63f2525a48cbc30a25378a3209eef305473b2b03cd41598"
BASE_CUTSCENE_OBJECT_SHA = "1ada8b7c8539aaaefe56c13e2e2407256207e25bde7ba9c9d532f2bba12c8f7e"
BASE_CUTSCENE_CODE_SHA = "a7e160b07189e0752a71705ad4d96fda85ba91fefb014574fa93019880f779a1"


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
        raise RuntimeError(f"expected one {segment_name} segment: {segments}")
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
    if not chunks:
        raise RuntimeError(f"{segment_name} has no LEDATA")
    chunks.sort()
    out = bytearray()
    for offset, payload in chunks:
        if offset != len(out):
            raise RuntimeError(f"{segment_name} LEDATA gap/overlap at {offset:#x}")
        out += payload
    return bytes(out)


def target_boundary(body: bytes) -> dict[str, object]:
    if len(body) != SIZE or prior.sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE script_param_second target identity drift")
    import csv
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream)
                if int(row["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("MAINE script_param_second Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x06C3
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 0
        or int(row["callee_count"]) != 1
    ):
        raise RuntimeError(f"MAINE script_param_second Ghidra extent drift: {row!r}")
    if (
        body[:3] != b"\x55\x8b\xec"
        or body[3:7] != b"\x8b\x1e\x48\x3f"
        or body[7:10] != b"\x80\x3f\x2c"
        or body[10:12] != b"\x75\x0f"
        or body[12:16] != b"\xff\x06\x48\x3f"
        or body[16:20] != b"\x66\xff\x76\x04"
        or body[20] != 0xE8
        or body[23:27] != b"\x5d\xc2\x04\x00"
        or body[27:30] != b"\xc4\x5e\x04"
        or body[30:33] != b"\xa1\x94\x3f"
        or body[33:37] != b"\x26\x89\x07\x5d"
        or body[37:] != b"\xc2\x04\x00"
    ):
        raise RuntimeError("MAINE script_param_second instruction/operand topology drift")
    call_target = START + 23 + int.from_bytes(body[21:23], "little", signed=True)
    if call_target != 0xA64D:
        raise RuntimeError(f"MAINE script_param_second near call drift: {call_target:#x}")
    return {
        "segment_identity": "1A05",
        "segment_offset": "06C3",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": prior.sha(body),
        "ghidra_contiguous": True,
        "ghidra_callers": 0,
        "ghidra_callees": 1,
        "script_p_map_target": "0E53:3F48 _script_p",
        "default_map_target": "0E53:3F94 _script_param_number_default",
        "near_call_target": "0xA64D script_param_read_number_first",
        "terminal": "RET 4 at 0xA738",
    }


def overlay_source(work: Path) -> str:
    header = work / "th03/formats/script.hpp"
    if prior.sha_file(header) != BASE_SCRIPT_HEADER_SHA:
        raise RuntimeError("pinned v489 script.hpp drift")
    destination = work / "src/maine/cutscene"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, destination / BODY.name)
    data = header.read_bytes()
    old = (
        b"void pascal near script_param_read_number_second(int& ret)\n"
        b"{\n"
        b"\tif(*script_p == ',') {\n"
        b"\t\tscript_p++;\n"
        b"\t\tscript_param_read_number_first(ret);\n"
        b"\t} else {\n"
        b"\t\tret = script_param_number_default;\n"
        b"\t}\n"
        b"}"
    )
    replacement = b'#include "src/maine/cutscene/script_param_second.inl"'
    if data.count(old) != 1:
        raise RuntimeError("script_param_second replacement anchor drift")
    header.write_bytes(data.replace(old, replacement, 1))
    return prior.sha_file(header)


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
    if prior.sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (prior.TARGET, prior.TARGET_SHA),
        (prior.SNAPSHOT / "bin/th04/maine.exe", prior.BASE_EXE_SHA),
        (prior.SNAPSHOT / "obj/th04/maine.map", prior.BASE_MAP_SHA),
        (prior.SNAPSHOT / "th03/cutscene/cutscene.cpp", BASE_CUTSCENE_SOURCE_SHA),
        (prior.SNAPSHOT / "th03/formats/script.hpp", BASE_SCRIPT_HEADER_SHA),
        (prior.SNAPSHOT / "obj/th04/cutscene.obj", BASE_CUTSCENE_OBJECT_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        "src/maine/cutscene/script_param_second.cpp": prior.sha_file(SOURCE),
        "src/maine/cutscene/script_param_second.inl": prior.sha_file(BODY),
    }
    target = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 MAINE ordered relocations differ from target restore")

    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    boundary = target_boundary(body)
    if baseline.program_image[START:NEXT] != body:
        raise RuntimeError("v489 script_param_second bytes differ from target")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 CUTSCENE_TEXT differs from target")

    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    if "0A05:06C3 idle  script_param_read_number_second(int far&)" not in map_text:
        raise RuntimeError("v489 script_param_second MAP public drift")

    base_object = prior.SNAPSHOT / "obj/th04/cutscene.obj"
    base_code = segment_bytes(base_object, "CUTSCENE_TEXT")
    if len(base_code) != PRODUCER_SIZE or prior.sha(base_code) != BASE_CUTSCENE_CODE_SHA:
        raise RuntimeError("pinned CUTSCENE_TEXT object contribution drift")
    zeros = bytes((0, 0))
    grouped_expected = (
        body[:5] + zeros + body[7:14] + zeros
        + body[16:31] + zeros + body[33:]
    )
    if base_code[LOCAL_START:LOCAL_START + SIZE] != grouped_expected:
        raise RuntimeError("pinned grouped object script_param_second bytes drift")
    standalone_expected = grouped_expected[:21] + zeros + grouped_expected[23:]

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        destination = work / "src/maine/cutscene"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, destination / SOURCE.name)
        shutil.copy2(BODY, destination / BODY.name)
        objects_before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc(work, output, f"v590-script-param-second-standalone-{label}",
            "src/maine/cutscene/script_param_second.cpp")
        standalone = [path for path in (work / "obj/th04").glob("*.obj")
                      if path.name not in objects_before]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "CUTSCENE_TEXT")
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
            or local_fixups != [(1, 31), (1, 21), (1, 14), (1, 5)]
        ):
            raise RuntimeError(f"{label}: standalone script_param_second OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/cutscene.obj"
        group_obj.unlink()
        tcc(work, output, f"v590-script-param-second-group-{label}", "th04/cutscene.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "CUTSCENE_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained no-op changed grouped CUTSCENE_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked_body = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or prior.sha_file(exe) != prior.BASE_EXE_SHA
            or prior.sha_file(mp) != prior.BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked_body != body
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked MAINE layout/body drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "standalone_object_sha256": prior.sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": prior.sha(local_code),
            "standalone_code_size": len(local_code),
            "standalone_fixup_sites": [list(item) for item in local_fixups],
            "group_object_sha256": prior.sha_file(group_obj),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": prior.sha(group_code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": prior.sha(image.program_image),
            "linked_function_sha256": prior.sha(linked_body),
            "linked_producer_sha256": prior.sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable_keys = (
        "standalone_link_relevant_omf_sha256", "standalone_code_sha256",
        "standalone_code_size", "standalone_fixup_sites",
        "group_link_relevant_omf_sha256", "group_code_sha256",
        "linked_exe_sha256", "linked_map_sha256", "linked_program_sha256",
        "linked_function_sha256", "linked_producer_sha256",
        "raw_function_difference_count", "raw_producer_difference_count",
        "ordered_relocations",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable_keys):
        raise RuntimeError("independent script_param_second cold rounds differ")
    if (
        prior.sha_file(SOURCE) != source_hashes["src/maine/cutscene/script_param_second.cpp"]
        or prior.sha_file(BODY) != source_hashes["src/maine/cutscene/script_param_second.inl"]
    ):
        raise RuntimeError("maintained script_param_second source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed script_param_read_number_second maintained-source cold-link replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "baseline_exe_sha256": prior.BASE_EXE_SHA,
        "baseline_map_sha256": prior.BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "CUTSCENE_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": prior.sha(producer),
        },
        "builds": builds,
        "cold_determinism": {
            "link_relevant_omf_code_exe_map_program_and_relocations_equal": True,
        },
        "limit": "Decoded 5-byte function only; v489 remains surrounding build scaffold. No packed-file or whole-MAINE exactness.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(receipt_path),
        "function_sha256": builds["a"]["linked_function_sha256"],
        "producer_sha256": builds["a"]["linked_producer_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
