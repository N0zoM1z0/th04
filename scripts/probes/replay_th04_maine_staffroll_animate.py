#!/usr/bin/env python3
"""Cold-replay maintained natural C++ for MAINE staffroll_animate."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import describe_omf
from lib.pc98 import parse_mz
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from probe_th04_maine_segment_topology_v470 import tcc
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from replay_th04_zun_source_only import source_closure
import replay_th04_maine_score_insert as prior

SOURCE = ROOT / "src/maine/end/staffroll_animate.inl"
START = 0xB44D
SIZE = 0x33A
NEXT = START + SIZE
PRODUCER_START = 0xAED0
PRODUCER_SIZE = 0x8B7
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "46cebdb10d5c0bb2cfe1e0bb1b6136caf6b1bc28f5477e38f7f6c43a6610142e"
TARGET_PRODUCER_SHA = "1bf488943682cd811d5dad81ac088c91772e87e33adbc2867d2296dc797b21f2"
BASE_SOURCE_SHA = "ddd3c9f94720b92dc8e8c14ebb21e673e5e5bc8e98d9e1d4b48f5e54164f4334"
BASE_OBJECT_SHA = "0ac7f5d08bd3d1ad2f9047bad2b0612b3322ca061fdc7073561ce899c2f76779"
BASE_CODE_SHA = "d30e94167ce85eb5e38ecf6f9dce4f634a9088b7a3f8a9fcb238d5697a0da4d4"


def sha(data: bytes) -> str:
    return prior.sha(data)


def validate_target(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE staffroll_animate target identity drift")
    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = [r for r in csv.DictReader(stream)
                if int(r["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("MAINE staffroll animate Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x13FD
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 20
    ):
        raise RuntimeError(f"MAINE staffroll animate Ghidra extent drift: {row!r}")
    required = (
        "0A05:0E80 08B7 C=CODE   S=MAINE_01_TEXT  G=GROUP_01 M=th04/staffall.cpp",
        "0A05:13FD       staffroll_animate()",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE staffroll animate MAP evidence drift")
    if not body.startswith(bytes.fromhex("55 8b ec")):
        raise RuntimeError("MAINE staffroll animate prologue drift")
    if body[-2:] != bytes.fromhex("5d c3"):
        raise RuntimeError("MAINE staffroll animate epilogue drift")
    return {
        "segment_identity": "1A05",
        "segment_offset": "13FD",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 1,
        "callee_count": 20,
        "terminal": "pop bp; ret",
        "producer": "1A05:0E80 MAINE_01_TEXT size 0x8B7",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/staffall.cpp"
    if prior.sha_file(upstream) != BASE_SOURCE_SHA:
        raise RuntimeError("pinned v489 staffall.cpp drift")
    shutil.copytree(ROOT / "src/maine/end", work / "src/maine/end", dirs_exist_ok=True)
    data = upstream.read_bytes()
    start_anchor = b"void near staffroll_animate(void)\n{"
    end_anchor = b"\n}\n#pragma codeseg"
    if data.count(start_anchor) != 1:
        raise RuntimeError("staffroll animate start anchor drift")
    start = data.index(start_anchor)
    end = data.index(end_anchor, start) + 2
    upstream.write_bytes(
        data[:start] + b'#include "src/maine/end/staffroll_animate.inl"' + data[end:]
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
        (prior.SNAPSHOT / "th04/staffall.cpp", BASE_SOURCE_SHA),
        (prior.SNAPSHOT / "obj/th04/staffall.obj", BASE_OBJECT_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    closure = source_closure(ROOT, ("src/maine/end/staffroll_animate.inl",))
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}
    target = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")

    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    boundary = validate_target(body, map_text)
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("MAINE staffall target producer identity drift")
    if baseline.program_image[START:NEXT] != body:
        raise RuntimeError("v489 staffroll animate bytes differ from target")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 staffall producer differs from target")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 ordered relocations differ from target")

    base_obj = prior.SNAPSHOT / "obj/th04/staffall.obj"
    base_omf = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "MAINE_01_TEXT")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_CODE_SHA
    ):
        raise RuntimeError("pinned v489 staffall object drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        patched_source_sha = overlay_source(work)

        obj = work / "obj/th04/staffall.obj"
        obj.unlink()
        tcc(work, output, f"v702-staffroll-animate-{label}", "th04/staffall.cpp")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "MAINE_01_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained helper changed staffall MAINE_01_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or prior.sha_file(exe) != prior.BASE_EXE_SHA
            or prior.sha_file(mp) != prior.BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked != body
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: cold MAINE staffroll animate link/layout drift")
        builds[label] = {
            "compact_snapshot": compact,
            "patched_staffall_source_sha256": patched_source_sha,
            "group_omf_sha256": prior.sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked),
            "linked_producer_sha256": sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable = lambda d: {k: v for k, v in d.items() if k != "group_omf_sha256"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent staffroll animate cold rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained staffroll animate source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE staffroll_animate maintained natural-C++ cold replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": prior.sha_file(Path(__file__).resolve()),
        "boundary": boundary,
        "producer": {
            "segment": "MAINE_01_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "limit": (
            "Decoded 826-byte staffroll_animate only. The surrounding staffall.cpp is pinned replay "
            "scaffold and contains other functions whose source provenance/exactness is not "
            "granted by this receipt. No packed-file or whole-MAINE exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": prior.sha_file(path),
        "function_sha256": TARGET_FUNCTION_SHA,
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
