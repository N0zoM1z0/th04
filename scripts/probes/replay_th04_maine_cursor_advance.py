#!/usr/bin/env python3
"""Cold-compile maintained MAINE cursor_advance_and_animate and relink CUTSCENE_TEXT."""

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

SOURCE = ROOT / "src/maine/cutscene/cursor_advance.cpp"
BODY = ROOT / "src/maine/cutscene/cursor_advance.inl"
START = 0xA73B
SIZE = 0x54
NEXT = START + SIZE
PRODUCER_START = 0xA292
PRODUCER_SIZE = 0xC3E
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "34023f82fc04d4b41c8cbfc49314c9a5a964b3158954ba7613ff49e8cb66b37b"
STANDALONE_CODE_SHA = "a599cef6450b9518fddb8232985798382a87ed2da8f2063d8d588cf46a6da619"
STANDALONE_FIXUPS = [
    (1, 80), (1, 71), (1, 60), (1, 54), (3, 48), (1, 40),
    (1, 36), (1, 29), (1, 23), (1, 18), (1, 10), (1, 5),
]


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or base.prior.sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE cursor target identity drift")
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream)
                if int(row["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("MAINE cursor Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x06EB
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 3
    ):
        raise RuntimeError(f"MAINE cursor Ghidra extent drift: {row!r}")

    if (
        body[:18] != bytes.fromhex(
            "55 8b ec 83 06 8c 3f 10 81 3e 8c 3f 30 02 7c 42 83 06"
        )
        or int.from_bytes(body[18:20], "little") != 0x3F8E
        or body[20:29] != bytes.fromhex("10 c7 06 8c 3f 90 00 81 3e")
        or int.from_bytes(body[29:31], "little") != 0x3F8E
        or body[31:35] != bytes.fromhex("80 01 7c 2f")
        or body[35] != 0xE8
        or (START + 38 + int.from_bytes(body[36:38], "little", signed=True)) != 0xA815
        or body[38:40] != bytes.fromhex("80 3e")
        or int.from_bytes(body[40:42], "little") != 0x3F4E
        or body[42:47] != bytes.fromhex("00 75 07 6a 00")
        or body[47] != 0x9A
        or int.from_bytes(body[48:50], "little") != 0x020A
        or int.from_bytes(body[50:52], "little") != 0x0CC7
        or body[52:70] != bytes.fromhex(
            "c7 06 8c 3f 50 00 c7 06 8e 3f 40 01 ba a6 00 b0 01 ee"
        )
        or body[70] != 0xE8
        or (START + 73 + int.from_bytes(body[71:73], "little", signed=True)) != 0xA59E
        or body[73:81] != bytes.fromhex("ba a6 00 b0 00 ee e8 11")
        or body[81:] != bytes.fromhex("fe 5d c3")
    ):
        raise RuntimeError("MAINE cursor instruction/operand topology drift")

    required = (
        "0A05:06EB idle  cursor_advance_and_animate()",
        "0A05:07C5 idle  box_1_to_0_animate()",
        "0A05:054E idle  box_bg_put()",
        "0CC7:020A       input_wait_for_change(int)",
        "0E53:3F8C       _cursor",
        "0E53:3F4E       _fast_forward",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE cursor MAP target drift")
    return {
        "segment_identity": "1A05",
        "segment_offset": "06EB",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": base.prior.sha(body),
        "caller_count": 1,
        "callee_count": 3,
        "cursor": "0E53:3F8C",
        "fast_forward": "0E53:3F4E",
        "constants": {
            "GLYPH_FULL_W": 16, "GLYPH_H": 16, "BOX_LEFT": 80,
            "NAME_AREA_LEFT": 144, "BOX_TOP": 320, "BOX_RIGHT": 560,
            "BOX_BOTTOM": 384,
        },
        "terminal": "RET",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th03/cutscene/cutscene.cpp"
    if base.prior.sha_file(upstream) != base.BASE_CUTSCENE_SOURCE_SHA:
        raise RuntimeError("pinned v489 cutscene translation unit drift")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/maine/cutscene", work / "src/maine/cutscene",
                    dirs_exist_ok=True)
    data = upstream.read_bytes()
    start_anchor = b"void near cursor_advance_and_animate(void)\n{"
    end_anchor = b"\n\n#if (GAME >= 4)\ntypedef enum {"
    if data.count(start_anchor) != 1 or data.count(end_anchor) != 1:
        raise RuntimeError("cursor replacement anchors are not unique")
    start = data.index(start_anchor)
    end = data.index(end_anchor, start)
    upstream.write_bytes(
        data[:start] + b'#include "src/maine/cutscene/cursor_advance.inl"\n'
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
    if output.exists() or output.parent != private:
        ap.error("output must be a new direct child of .analysis/reconstruction/probes")

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

    closure = source_closure(ROOT, ("src/maine/cutscene/cursor_advance.cpp",))
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
        raise RuntimeError("v489 MAINE cursor baseline differs from target")

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
        base.tcc(work, output, f"cursor-standalone-{label}",
                 "src/maine/cutscene/cursor_advance.cpp")
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
            raise RuntimeError(f"{label}: standalone cursor codegen drift")

        group_obj = work / "obj/th04/cutscene.obj"
        group_obj.unlink()
        base.tcc(work, output, f"cursor-group-{label}", "th04/cutscene.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "CUTSCENE_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained cursor changed grouped CUTSCENE_TEXT")

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
            raise RuntimeError(f"{label}: linked MAINE cursor/layout drift")

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
        raise RuntimeError("independent MAINE cursor cold rounds differ")
    if any(base.prior.sha_file(ROOT / name) != digest
           for name, digest in source_hashes.items()):
        raise RuntimeError("maintained cursor source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE cursor_advance_and_animate natural-source cold-link replay",
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
        "limit": "Decoded 84-byte function only; no packed-file offset or whole-MAINE exactness.",
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
