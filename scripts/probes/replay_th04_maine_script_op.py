#!/usr/bin/env python3
"""Cold-replay maintained natural C++ for MAINE's large script dispatcher."""

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

from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402
import replay_th04_maine_score_insert as prior  # noqa: E402
import replay_th04_maine_box_animate as base  # noqa: E402

SOURCE = ROOT / "src/maine/cutscene/script_op.inl"
START = 0xA847
SIZE = 0x575
NEXT = START + SIZE
TABLE_START = NEXT
TABLE_SIZE = 0x40
PRODUCER_START = 0xA292
PRODUCER_SIZE = 0xC3E
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "bfe8e1a9a3aaa823807f3e3e2053ed2eae6e47fbe6cdc1406ba5d432acf7eb15"
BASE_CUTSCENE_SOURCE_SHA = base.BASE_CUTSCENE_SOURCE_SHA
BASE_CUTSCENE_OBJECT_SHA = base.BASE_CUTSCENE_OBJECT_SHA
BASE_CUTSCENE_CODE_SHA = base.BASE_CUTSCENE_CODE_SHA


def sha(data: bytes) -> str:
    return prior.sha(data)


def validate_target(body: bytes, table: bytes) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE script_op target identity drift")
    if not body.startswith(b"\xC8\x16\x00\x00\x56"):
        raise RuntimeError("MAINE script_op prologue drift")
    if body[-5:] != b"\x5E\xC9\xC2\x02\x00":
        raise RuntimeError("MAINE script_op RET 2 epilogue drift")
    if len(table) != TABLE_SIZE:
        raise RuntimeError("MAINE script_op switch table size drift")
    keys = [int.from_bytes(table[i:i + 2], "little") for i in range(0, 0x20, 2)]
    expected_keys = [ord(c) for c in "$=@bcef gkmnpstvw".replace(" ", "")]
    if keys != expected_keys:
        raise RuntimeError(f"MAINE script_op switch keys drift: {keys!r}")
    destinations = [int.from_bytes(table[i:i + 2], "little") for i in range(0x20, 0x40, 2)]
    if not all(0x07F7 <= value < 0x0D6C for value in destinations):
        raise RuntimeError(f"MAINE script_op switch destination drift: {destinations!r}")
    return {
        "segment_identity": "1A05",
        "segment_offset": "07F7",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "terminal": "ret 0x2",
        "switch_table_payload_offset": hex(TABLE_START),
        "switch_table_size": TABLE_SIZE,
        "switch_table_sha256": sha(table),
        "switch_keys": keys,
        "switch_destinations": destinations,
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th03/cutscene/cutscene.cpp"
    if prior.sha_file(upstream) != BASE_CUTSCENE_SOURCE_SHA:
        raise RuntimeError("pinned v489 cutscene translation unit drift")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/maine/cutscene", work / "src/maine/cutscene", dirs_exist_ok=True)
    data = upstream.read_bytes()
    start_anchor = b"script_ret_t pascal near script_op(unsigned char c)\n{"
    end_anchor = b"\n\nvoid near cutscene_animate(void)"
    if data.count(start_anchor) != 1 or data.count(end_anchor) != 1:
        raise RuntimeError("script_op replacement anchors are not unique")
    start = data.index(start_anchor)
    end = data.index(end_anchor, start)
    upstream.write_bytes(
        data[:start] + b'#include "src/maine/cutscene/script_op.inl"' + data[end:]
    )
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

    closure = source_closure(ROOT, ("src/maine/cutscene/script_op.inl",))
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}
    target = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")
    body = target.program_image[START:NEXT]
    table = target.program_image[TABLE_START:TABLE_START + TABLE_SIZE]
    target_producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    boundary = validate_target(body, table)
    if baseline.program_image[START:NEXT] != body:
        raise RuntimeError("v489 script_op bytes differ from target")
    if baseline.program_image[TABLE_START:TABLE_START + TABLE_SIZE] != table:
        raise RuntimeError("v489 script_op switch table differs from target")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != target_producer:
        raise RuntimeError("v489 CUTSCENE_TEXT producer differs from target")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 ordered relocations differ from target")

    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    if "0A05:07F7 idle  script_op(unsigned char)" not in map_text:
        raise RuntimeError("v489 MAINE script_op MAP entry drift")
    base_object = prior.SNAPSHOT / "obj/th04/cutscene.obj"
    base_omf = describe_omf(base_object.read_bytes())
    base_code = segment_bytes(base_object, "CUTSCENE_TEXT")
    if (not base_omf["valid"]
            or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
            or len(base_code) != PRODUCER_SIZE
            or sha(base_code) != BASE_CUTSCENE_CODE_SHA):
        raise RuntimeError("pinned v489 CUTSCENE_TEXT object drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        patched_source_sha = overlay_source(work)

        group_obj_path = work / "obj/th04/cutscene.obj"
        group_obj_path.unlink()
        tcc(work, output, f"v685-script-op-group-{label}", "th04/cutscene.cpp")
        group_omf = describe_omf(group_obj_path.read_bytes())
        group_code = segment_bytes(group_obj_path, "CUTSCENE_TEXT")
        if (not group_omf["valid"]
                or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
                or group_code != base_code):
            raise RuntimeError(f"{label}: maintained script_op changed grouped CUTSCENE_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[START:NEXT]
        linked_table = image.program_image[TABLE_START:TABLE_START + TABLE_SIZE]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (not image.valid
                or prior.sha_file(exe) != prior.BASE_EXE_SHA
                or prior.sha_file(mp) != prior.BASE_MAP_SHA
                or [item.linear for item in image.relocations] != target_sites
                or linked != body
                or linked_table != table
                or linked_producer != target_producer):
            raise RuntimeError(f"{label}: cold MAINE script_op link/layout drift")
        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "group_omf_sha256": prior.sha_file(group_obj_path),
            "group_code_sha256": sha(group_code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked),
            "linked_switch_table_sha256": sha(linked_table),
            "linked_producer_sha256": sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_switch_table_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable = lambda d: {k: v for k, v in d.items() if k != "group_omf_sha256"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent MAINE script_op cold rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained script_op source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed script dispatcher and maintained natural-C++ cold replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "baseline_exe_sha256": prior.BASE_EXE_SHA,
        "baseline_map_sha256": prior.BASE_MAP_SHA,
        "baseline_cutscene_object_sha256": BASE_CUTSCENE_OBJECT_SHA,
        "baseline_cutscene_code_sha256": BASE_CUTSCENE_CODE_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": prior.sha_file(Path(__file__).resolve()),
        "boundary": boundary,
        "producer": {
            "segment": "CUTSCENE_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(target_producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "cold_determinism": {
            "exe_map_linked_program_and_code_equal": True,
            "group_object_code_equal": True,
        },
        "limit": (
            "Decoded 1397-byte function body plus compiler-generated 64-byte switch table only; "
            "no packed-file or whole-MAINE exactness. The surrounding v489 tree remains replay scaffold."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": prior.sha_file(receipt_path),
        "function_sha256": TARGET_FUNCTION_SHA,
        "switch_table_sha256": sha(table),
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
