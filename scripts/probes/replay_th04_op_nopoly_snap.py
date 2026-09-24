#!/usr/bin/env python3
"""Cold-compile maintained OP nopoly_B_snap and relink OP_MUSIC_TEXT."""

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
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_op_nopoly_free import (  # noqa: E402
    BASE_EXE_SHA,
    BASE_MAP_SHA,
    BASE_MUSIC_CODE_SHA,
    BASE_MUSIC_OBJECT_SHA,
    BASE_MUSIC_SOURCE_SHA,
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

SOURCE = ROOT / "src/op/music/nopoly_snap.cpp"
BODY = ROOT / "src/op/music/nopoly_snap.inl"
HMEM = ROOT / "src/shared/memory/hmem.hpp"
START = 0xBF68
SIZE = 0x31
NEXT = START + SIZE
PRODUCER_START = 0xBED5
PRODUCER_SIZE = 0x6A5
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "878219a9c64061c7ea7c8428034b8aa7868d17441c95bae7fe2cb08c6c25ca68"


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP nopoly_B_snap target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP nopoly_B_snap Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x1828
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 1
    ):
        raise RuntimeError(f"OP nopoly_B_snap Ghidra extent drift: {row!r}")

    if (
        body[:8] != bytes.fromhex("55 8b ec 56 68 00 7d 9a")
        or int.from_bytes(body[8:10], "little") != 0x2752
        or int.from_bytes(body[10:12], "little") != 0
        or body[12] != 0xA3
        or int.from_bytes(body[13:15], "little") != 0x3A80
        or body[15:21] != bytes.fromhex("33 f6 eb 15 c4 1e")
        or int.from_bytes(body[21:23], "little") != 0x22DA
        or body[23:31] != bytes.fromhex("03 de 66 26 8b 07 8e 06")
        or int.from_bytes(body[31:33], "little") != 0x3A80
        or body[33:] != bytes.fromhex(
            "66 26 89 04 83 c6 04 81 fe 00 7d 7c e5 5e 5d c3"
        )
    ):
        raise RuntimeError("OP nopoly_B_snap instruction/operand topology drift")

    for required in (
        "0000:2752       HMEM_ALLOCBYTE",
        "0F34:3A80 idle  _nopoly_B",
        "0F34:22DA       _VRAM_PLANE_B",
        "0A74:1828 idle  nopoly_b_snap()",
    ):
        if required not in map_text:
            raise RuntimeError(f"OP nopoly_B_snap MAP drift: {required}")

    return {
        "segment_identity": "1A74",
        "segment_offset": "1828",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 1,
        "allocation_size": 0x7D00,
        "allocation_target": "0000:2752 HMEM_ALLOCBYTE",
        "buffer_target": "0F34:3A80 _nopoly_B",
        "source_vram_target": "0F34:22DA _VRAM_PLANE_B",
        "loop_step": 4,
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th02/op/m_music.cpp"
    if sha_file(upstream) != BASE_MUSIC_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP music source drift")

    dst = work / "src/op/music"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)

    data = upstream.read_bytes()
    old = """void near nopoly_B_snap(void)
{
	nopoly_B = HMem<dots8_t>::alloc(PLANE_SIZE);
	for(vram_offset_t p = 0; p < PLANE_SIZE; p += int(sizeof(dots32_t))) {
		*reinterpret_cast<dots32_t far *>(nopoly_B + p) = VRAM_CHUNK(B, p, 32);
	}
}""".encode("ascii")
    replacement = b'#include "src/op/music/nopoly_snap.inl"'
    if data.count(old) != 1:
        raise RuntimeError("nopoly_B_snap replacement anchor drift")
    upstream.write_bytes(data.replace(old, replacement, 1))
    return sha_file(upstream)


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
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th02/op/m_music.cpp", BASE_MUSIC_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_music.obj", BASE_MUSIC_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        "src/op/music/nopoly_snap.cpp": sha_file(SOURCE),
        "src/op/music/nopoly_snap.inl": sha_file(BODY),
        "src/shared/memory/hmem.hpp": sha_file(HMEM),
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
        raise RuntimeError("target OP_MUSIC_TEXT identity drift")
    if (
        baseline.program_image[START:NEXT] != body
        or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        != producer
    ):
        raise RuntimeError("v489 OP music producer differs from target")

    base_object = SNAPSHOT / "obj/th04/op_music.obj"
    base_code = segment_bytes(base_object, "OP_MUSIC_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_MUSIC_CODE_SHA:
        raise RuntimeError("pinned OP_MUSIC_TEXT object contribution drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")

        dst = work / "src/op/music"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, dst / SOURCE.name)
        shutil.copy2(BODY, dst / BODY.name)
        hmem_dst = work / "src/shared/memory/hmem.hpp"
        hmem_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HMEM, hmem_dst)

        before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc_op(
            work, output, f"v606-nopoly-snap-standalone-{label}",
            "src/op/music/nopoly_snap.cpp",
        )
        standalone = [
            path for path in (work / "obj/th04").glob("*.obj")
            if path.name not in before
        ]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_MUSIC_TEXT")
        local_fixups = [
            item
            for record in parse_omf(local_obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]
        target_unlinked = (
            body[:8] + bytes((0, 0, 0, 0))
            + body[12:13] + bytes((0, 0))
            + body[15:21] + bytes((0, 0))
            + body[23:31] + bytes((0, 0))
            + body[33:]
        )
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != target_unlinked
            or local_fixups != [(1, 31), (1, 21), (1, 13), (3, 8)]
        ):
            raise RuntimeError(f"{label}: standalone nopoly_B_snap OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/op_music.obj"
        group_obj.unlink()
        tcc_op(work, output, f"v606-nopoly-snap-group-{label}", "th04/op_music.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_MUSIC_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(
                f"{label}: maintained nopoly_B_snap changed grouped OP_MUSIC_TEXT"
            )

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
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
            raise RuntimeError(f"{label}: linked OP nopoly_B_snap/layout drift")

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
        raise RuntimeError("independent OP nopoly_B_snap cold rounds differ")
    if (
        sha_file(SOURCE) != source_hashes["src/op/music/nopoly_snap.cpp"]
        or sha_file(BODY) != source_hashes["src/op/music/nopoly_snap.inl"]
        or sha_file(HMEM) != source_hashes["src/shared/memory/hmem.hpp"]
    ):
        raise RuntimeError("maintained nopoly_B_snap source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed nopoly_B_snap maintained-source cold-link replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "baseline_map_sha256": BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "OP_MUSIC_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "cold_determinism": {
            "link_relevant_omf_code_exe_map_program_and_relocations_equal": True,
        },
        "limit": "Decoded 49-byte function only; no packed-file or whole-OP exactness.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + chr(10), encoding="utf-8")
    print(json.dumps({
        "receipt": str(receipt_path),
        "function_sha256": builds["a"]["linked_function_sha256"],
        "producer_sha256": builds["a"]["linked_producer_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
