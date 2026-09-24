#!/usr/bin/env python3
"""Cold-compile maintained MAINE pic_copy_to_other and relink CUTSCENE_TEXT."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402
import replay_th04_maine_box_animate as base  # noqa: E402

SOURCE = ROOT / "src/maine/cutscene/pic_copy_to_other.cpp"
BODY = ROOT / "src/maine/cutscene/pic_copy_to_other.inl"
START = 0xA30A
SIZE = 0x75
NEXT = START + SIZE
PRODUCER_START = 0xA292
PRODUCER_SIZE = 0xC3E
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "d5e7f8d80a8390a4d2bd5c029cdbee2840ac0cc1cd7e19848147a091ec73fd5f"
STANDALONE_CODE_SHA = "f0f25fd9b14b1e92a4ff7b305e95ca19062e7e04936aa15a1b3dc368bef40987"
STANDALONE_FIXUPS = [
    (3, 101), (1, 67), (1, 52), (1, 31),
]


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or base.prior.sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE pic_copy_to_other target identity drift")
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream)
                if int(row["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("MAINE pic_copy_to_other Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x02BA
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 2
    ):
        raise RuntimeError(f"MAINE pic_copy_to_other Ghidra extent drift: {row!r}")

    if (
        body[:31] != bytes.fromhex(
            "c8 04 00 00 56 57 8b 46 06 c1 f8 03 8b 56 04 c1 e2 06 "
            "03 c2 8b 56 04 c1 e2 04 03 c2 8b f0 e8"
        )
        or (START + 33 + int.from_bytes(body[31:33], "little", signed=True)) != 0xA2D6
        or body[33:52] != bytes.fromhex(
            "33 ff eb 39 c7 46 fe 00 00 eb 28 ba a6 00 b0 00 ee c4 1e"
        )
        or int.from_bytes(body[52:54], "little") != 0x170C
        or body[54:67] != bytes.fromhex(
            "03 de 26 8b 07 89 46 fc b0 01 ee 8b 1e"
        )
        or int.from_bytes(body[67:69], "little") != 0x170C
        or body[69:101] != bytes.fromhex(
            "03 de 8b 46 fc 26 89 07 83 46 fe 02 83 c6 02 "
            "83 7e fe 28 7c d2 47 83 c6 28 81 ff c8 00 7c c1 9a"
        )
        or int.from_bytes(body[101:103], "little") != 0x085C
        or int.from_bytes(body[103:105], "little") != 0x0000
        or body[105:] != bytes.fromhex(
            "ba a6 00 b0 00 ee 5f 5e c9 c2 04 00"
        )
    ):
        raise RuntimeError("MAINE pic_copy_to_other instruction/operand topology drift")

    required = (
        "0A05:02BA idle  pic_copy_to_other(int,int)",
        "0A05:0286 idle  egc_start_copy()",
        "0000:085C       EGC_OFF",
        "0E53:170C       _VRAM_PLANE_B",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE pic_copy_to_other MAP target drift")
    return {
        "segment_identity": "1A05",
        "segment_offset": "02BA",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": base.prior.sha(body),
        "caller_count": 1,
        "callee_count": 2,
        "egc_start_copy": "1A05:0286",
        "egc_off": "0000:085C",
        "vram_plane_b": "0E53:170C",
        "geometry": {"width_pixels": 320, "height": 200, "row_bytes": 40},
        "copy_direction": "VRAM page 0 to page 1",
        "terminal": "RET 4",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th03/cutscene/cutscene.cpp"
    if base.prior.sha_file(upstream) != base.BASE_CUTSCENE_SOURCE_SHA:
        raise RuntimeError("pinned v489 cutscene translation unit drift")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/maine/cutscene", work / "src/maine/cutscene",
                    dirs_exist_ok=True)
    data = upstream.read_bytes()
    start_anchor = b"void pascal near pic_copy_to_other(screen_x_t left, vram_y_t top)\n{"
    end_anchor = b"\n}\n\nvoid pascal near pic_put_both_masked("
    if data.count(start_anchor) != 1:
        raise RuntimeError("pic_copy_to_other start anchor is not unique")
    start = data.index(start_anchor)
    end_marker = data.find(end_anchor, start)
    if end_marker < 0 or data.find(end_anchor, end_marker + 1) >= 0:
        raise RuntimeError("pic_copy_to_other scoped end anchor is not unique")
    end = end_marker + 2
    upstream.write_bytes(
        data[:start] + b'#include "src/maine/cutscene/pic_copy_to_other.inl"'
        + data[end:]
    )
    return base.prior.sha_file(upstream)


def object_fixups(obj: Path) -> list[tuple[int, int]]:
    return [
        item
        for record in parse_omf(obj.read_bytes())
        if record.record_type == 0x9C
        for item in fixup_locations(record.data)
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    if base.prior.sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (base.prior.TARGET, base.prior.TARGET_SHA),
        (base.prior.SNAPSHOT / "bin/th04/maine.exe", base.prior.BASE_EXE_SHA),
        (base.prior.SNAPSHOT / "obj/th04/maine.map", base.prior.BASE_MAP_SHA),
        (base.prior.SNAPSHOT / "th03/cutscene/cutscene.cpp",
         base.BASE_CUTSCENE_SOURCE_SHA),
        (base.prior.SNAPSHOT / "obj/th04/cutscene.obj",
         base.BASE_CUTSCENE_OBJECT_SHA),
    ):
        if base.prior.sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    closure = source_closure(ROOT, ("src/maine/cutscene/pic_copy_to_other.cpp",))
    source_hashes = {name: base.prior.sha_file(ROOT / name) for name in closure}

    target = parse_mz(base.prior.TARGET.read_bytes())
    baseline = parse_mz((base.prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != base.prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")
    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (base.prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    boundary = target_boundary(body, map_text)
    target_sites = [item.linear for item in target.relocations]
    if (
        baseline.program_image[START:NEXT] != body
        or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        != producer
        or [item.linear for item in baseline.relocations] != target_sites
    ):
        raise RuntimeError("v489 MAINE pic_copy_to_other baseline differs from target")

    base_obj = base.prior.SNAPSHOT / "obj/th04/cutscene.obj"
    base_code = segment_bytes(base_obj, "CUTSCENE_TEXT")
    if (
        len(base_code) != PRODUCER_SIZE
        or base.prior.sha(base_code) != base.BASE_CUTSCENE_CODE_SHA
    ):
        raise RuntimeError("pinned CUTSCENE_TEXT object contribution drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(base.prior.SNAPSHOT, work, "maine")
        patched_source_sha = overlay_source(work)

        obj_dir = work / "obj/th04"
        before = {p.name for p in obj_dir.glob("*.obj")}
        base.tcc(work, output, f"pic-copy-to-other-standalone-{label}",
                 "src/maine/cutscene/pic_copy_to_other.cpp")
        standalone = [p for p in obj_dir.glob("*.obj") if p.name not in before]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = segment_bytes(local_obj, "CUTSCENE_TEXT")
        local_fixups = object_fixups(local_obj)
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or len(local_code) != SIZE
            or base.prior.sha(local_code) != STANDALONE_CODE_SHA
            or local_fixups != STANDALONE_FIXUPS
        ):
            raise RuntimeError(f"{label}: standalone pic_copy_to_other codegen drift")

        group_obj = work / "obj/th04/cutscene.obj"
        group_obj.unlink()
        base.tcc(work, output, f"pic-copy-to-other-group-{label}", "th04/cutscene.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "CUTSCENE_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained pic_copy_to_other changed grouped CUTSCENE_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[START:NEXT]
        linked_producer = image.program_image[
            PRODUCER_START:PRODUCER_START + PRODUCER_SIZE
        ]
        if (
            not image.valid
            or base.prior.sha_file(exe) != base.prior.BASE_EXE_SHA
            or base.prior.sha_file(mp) != base.prior.BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked != body
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked MAINE pic_copy_to_other/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "standalone_object_sha256": base.prior.sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": base.prior.sha(local_code),
            "standalone_fixup_sites": [list(x) for x in local_fixups],
            "group_object_sha256": base.prior.sha_file(group_obj),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": base.prior.sha(group_code),
            "linked_exe_sha256": base.prior.sha_file(exe),
            "linked_map_sha256": base.prior.sha_file(mp),
            "linked_program_sha256": base.prior.sha(image.program_image),
            "linked_function_sha256": base.prior.sha(linked),
            "linked_producer_sha256": base.prior.sha(linked_producer),
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
    if any(builds["a"][k] != builds["b"][k] for k in stable):
        raise RuntimeError("independent MAINE pic_copy_to_other cold rounds differ")
    if any(base.prior.sha_file(ROOT / name) != digest
           for name, digest in source_hashes.items()):
        raise RuntimeError("maintained pic_copy_to_other source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE pic_copy_to_other natural-source cold-link replay",
        "artifact": "th04-maine",
        "target_restored_sha256": base.prior.TARGET_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "CUTSCENE_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": base.prior.sha(producer),
        },
        "builds": builds,
        "limit": "Decoded 117-byte function only; no packed-file offset or whole-MAINE exactness.",
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
