#!/usr/bin/env python3
"""Cold-compile maintained TH04 box_bg_free and relink MAINE CUTSCENE_TEXT."""

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

SOURCE = ROOT / "src/maine/cutscene/box_bg_free.cpp"
BODY = ROOT / "src/maine/cutscene/box_bg_free.inl"
START = 0xA57F
SIZE = 0x1F
NEXT = START + SIZE
PRODUCER_START = 0xA292
PRODUCER_SIZE = 0xC3E
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "7d9df3820e96a0c9810587b91594913a108ee097624f695883a88ce4516ad83d"
BASE_CUTSCENE_SOURCE_SHA = "49fbde7cc661dda1d8a290debe285d625f4d274abb9c68c42d28150c59afb760"
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
        raise RuntimeError("MAINE box_bg_free target identity drift")
    # Independently bound by the attested Ghidra export: one contiguous 31-byte
    # near body at 1A05:052F, two callers, one callee.
    import csv
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream)
                if int(row["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("MAINE box_bg_free Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x052F
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 2
        or int(row["callee_count"]) != 1
    ):
        raise RuntimeError(f"MAINE box_bg_free Ghidra extent drift: {row!r}")
    # Exact target operands: compare/clear the dword far pointer at 3F4A,
    # push its segment word at +2, call HMEM_FREE at 0000:2454.
    if (
        body[:3] != b"\x55\x8b\xec"
        or body[3:9] != b"\x66\x83\x3e\x4a\x3f\x00"
        or body[9:11] != b"\x74\x12"
        or body[11:15] != b"\xff\x36\x4c\x3f"
        or body[15:20] != b"\x9a\x54\x24\x00\x00"
        or body[20:29] != b"\x66\xc7\x06\x4a\x3f\x00\x00\x00\x00"
        or body[29:] != b"\x5d\xc3"
    ):
        raise RuntimeError("MAINE box_bg_free raw instruction/operand topology drift")
    return {
        "segment_identity": "1A05",
        "segment_offset": "052F",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": prior.sha(body),
        "ghidra_contiguous": True,
        "ghidra_callers": 2,
        "ghidra_callees": 1,
        "data_map_target": "0E53:3F4A _box_bg",
        "far_call_map_target": "0000:2454 HMEM_FREE",
        "terminal": "RET at 0xA59D",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th03/cutscene/cutscene.cpp"
    if prior.sha_file(upstream) != BASE_CUTSCENE_SOURCE_SHA:
        raise RuntimeError("pinned v489 cutscene translation unit drift")
    destination = work / "src/maine/cutscene"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, destination / BODY.name)
    data = upstream.read_bytes()
    old = (
        b"void near box_bg_free(void)\n"
        b"{\n"
        b"\tif(box_bg) {\n"
        b"\t\tHMem< Planar<dots16_t> >::free(box_bg);\n"
        b"\t\tbox_bg = nullptr;\n"
        b"\t}\n"
        b"}"
    )
    replacement = b'#include "src/maine/cutscene/box_bg_free.inl"'
    if data.count(old) != 1:
        raise RuntimeError("box_bg_free replacement anchor drift")
    upstream.write_bytes(data.replace(old, replacement, 1))
    return prior.sha_file(upstream)


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
        (prior.SNAPSHOT / "obj/th04/cutscene.obj", BASE_CUTSCENE_OBJECT_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        "src/maine/cutscene/box_bg_free.cpp": prior.sha_file(SOURCE),
        "src/maine/cutscene/box_bg_free.inl": prior.sha_file(BODY),
        "src/shared/memory/hmem.hpp": prior.sha_file(ROOT / "src/shared/memory/hmem.hpp"),
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
        raise RuntimeError("v489 box_bg_free bytes differ from target")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 CUTSCENE_TEXT differs from target")

    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    if "0A05:052F idle  box_bg_free()" not in map_text:
        raise RuntimeError("v489 box_bg_free MAP public drift")

    base_object = prior.SNAPSHOT / "obj/th04/cutscene.obj"
    base_code = segment_bytes(base_object, "CUTSCENE_TEXT")
    if len(base_code) != PRODUCER_SIZE or prior.sha(base_code) != BASE_CUTSCENE_CODE_SHA:
        raise RuntimeError("pinned CUTSCENE_TEXT object contribution drift")
    expected_unlinked = (
        body[:6] + b"\0\0" + body[8:13] + b"\x02\0"
        + body[15:16] + b"\0\0\0\0"
        + body[20:23] + b"\0\0" + body[25:]
    )
    if base_code[LOCAL_START:LOCAL_START + SIZE] != expected_unlinked:
        raise RuntimeError("pinned object box_bg_free unlinked bytes drift")

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
        shared_header = ROOT / 'src/shared/memory/hmem.hpp'
        shared_destination = work / 'src/shared/memory/hmem.hpp'
        shared_destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shared_header, shared_destination)

        objects_before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc(work, output, f"v585-box-bg-free-standalone-{label}",
            "src/maine/cutscene/box_bg_free.cpp")
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
        expected_unlinked = (
            body[:6] + b"\0\0" + body[8:13] + b"\x02\x00"
            + body[15:16] + b"\0\0\0\0"
            + body[20:23] + b"\0\0" + body[25:]
        )
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != expected_unlinked
            or local_fixups != [(1, 23), (3, 16), (1, 13), (1, 6)]
        ):
            raise RuntimeError(f"{label}: standalone box_bg_free OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/cutscene.obj"
        group_obj.unlink()
        tcc(work, output, f"v585-box-bg-free-group-{label}", "th04/cutscene.cpp")
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
        raise RuntimeError("independent box_bg_free cold rounds differ")
    if (
        prior.sha_file(SOURCE) != source_hashes["src/maine/cutscene/box_bg_free.cpp"]
        or prior.sha_file(BODY) != source_hashes["src/maine/cutscene/box_bg_free.inl"]
        or prior.sha_file(ROOT / "src/shared/memory/hmem.hpp") != source_hashes["src/shared/memory/hmem.hpp"]
    ):
        raise RuntimeError("maintained box_bg_free source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed box_bg_free maintained-source cold-link replay",
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
