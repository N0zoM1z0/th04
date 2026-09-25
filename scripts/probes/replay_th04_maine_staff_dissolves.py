#!/usr/bin/env python3
"""Cold-replay six maintained natural-C++ MAINE staff dissolve helpers."""

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

FUNCTIONS = [
    {
        "name": "staffroll_dissolve_radial_put",
        "source": "src/maine/end/staffroll_dissolve_radial_put.inl",
        "start": 0xAED0, "size": 0x15D, "segment_offset": 0x0E80,
        "sha256": "ff63d7e7d4b9f0f4478e602bb85311e085dca416943c1bd61315c8050bf2c675",
        "caller_count": 0, "callee_count": 4, "tasm": "sub_AED0",
    },
    {
        "name": "staffroll_dissolve_diagonal_put",
        "source": "src/maine/end/staffroll_dissolve_diagonal_put.inl",
        "start": 0xB02D, "size": 0x117, "segment_offset": 0x0FDD,
        "sha256": "37b7fe4e213fffcf2e896c2a9ffb85e7528b351908ab81d57c01ee233281a6c4",
        "caller_count": 0, "callee_count": 4, "tasm": "sub_B02D",
    },
    {
        "name": "staffroll_dissolve_axis_put",
        "source": "src/maine/end/staffroll_dissolve_axis_put.inl",
        "start": 0xB144, "size": 0x117, "segment_offset": 0x10F4,
        "sha256": "a6e43d03fa57aaf32899bdf61fd77bb8ee50ed4ada6ccc59d80361d949c343ab",
        "caller_count": 0, "callee_count": 4, "tasm": "sub_B144",
    },
    {
        "name": "staffroll_dissolve_out",
        "source": "src/maine/end/staffroll_dissolve_out.inl",
        "start": 0xB291, "size": 0x8D, "segment_offset": 0x1241,
        "sha256": "2d51ccb26d06653b4bf2af84afe2d93e5fecc2341ebcff1321c1b8e5a82b98e9",
        "caller_count": 1, "callee_count": 2, "tasm": "sub_B291",
    },
    {
        "name": "staffroll_dissolve_in",
        "source": "src/maine/end/staffroll_dissolve_in.inl",
        "start": 0xB31E, "size": 0x8E, "segment_offset": 0x12CE,
        "sha256": "1203e745b8fcdfb4e8696c1b2aa29713a9a0ffc67d173208b0b07c864d06f455",
        "caller_count": 1, "callee_count": 2, "tasm": "sub_B31E",
    },
    {
        "name": "staffroll_dissolve_two",
        "source": "src/maine/end/staffroll_dissolve_two.inl",
        "start": 0xB3AC, "size": 0xA1, "segment_offset": 0x135C,
        "sha256": "cc3877685057b5e5001de68fc0a0eaf5f03ffe120f0fc5961ec377f39c6b25f4",
        "caller_count": 1, "callee_count": 2, "tasm": "sub_B3AC",
    },
]

PRODUCER_START = 0xAED0
PRODUCER_SIZE = 0x8B7
TARGET_PRODUCER_SHA = "1bf488943682cd811d5dad81ac088c91772e87e33adbc2867d2296dc797b21f2"
BASE_SOURCE_SHA = "ddd3c9f94720b92dc8e8c14ebb21e673e5e5bc8e98d9e1d4b48f5e54164f4334"
BASE_OBJECT_SHA = "0ac7f5d08bd3d1ad2f9047bad2b0612b3322ca061fdc7073561ce899c2f76779"
BASE_CODE_SHA = "d30e94167ce85eb5e38ecf6f9dce4f634a9088b7a3f8a9fcb238d5697a0da4d4"


def sha(data: bytes) -> str:
    return prior.sha(data)


def function_rows() -> dict[int, dict[str, str]]:
    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return {int(r["entry_linear"], 0) - 0x10000: r for r in rows}


def validate_target(target: bytes, map_text: str) -> list[dict[str, object]]:
    rows = function_rows()
    listing = (ROOT / ".analysis/reconstruction/boundary-review/tasm/maine-th04_maine.lst").read_text(
        encoding="cp932", errors="replace"
    )
    result: list[dict[str, object]] = []
    required_map = [
        "0A05:0E80 08B7 C=CODE   S=MAINE_01_TEXT  G=GROUP_01 M=th04/staffall.cpp",
        "0A05:0E80 idle  staffroll_dissolve_radial_put(int,int,int)",
        "0A05:0FDD idle  staffroll_dissolve_diagonal_put(int,int,int)",
        "0A05:10F4 idle  staffroll_dissolve_axis_put(int,int,int)",
        "0A05:1241 idle  staffroll_dissolve_out(int,int)",
        "0A05:12CE idle  staffroll_dissolve_in(int,int)",
        "0A05:135C idle  staffroll_dissolve_two(int,int,int,int)",
    ]
    if any(item not in map_text for item in required_map):
        raise RuntimeError("MAINE staff dissolve MAP evidence drift")

    for spec in FUNCTIONS:
        start = spec["start"]
        size = spec["size"]
        body = target[start:start + size]
        if len(body) != size or sha(body) != spec["sha256"]:
            raise RuntimeError(f"MAINE {spec['name']} target identity drift")
        row = rows.get(start)
        if row is None:
            raise RuntimeError(f"MAINE {spec['name']} Ghidra entry missing")
        if (
            int(row["entry_segment"], 0) != 0x1A05
            or int(row["entry_offset"], 0) != spec["segment_offset"]
            or int(row["body_min_linear"], 0) != 0x10000 + start
            or int(row["body_max_linear"], 0) != 0x10000 + start + size - 1
            or int(row["body_addresses"]) != size
            or int(row["body_span"]) != size
            or row["contiguous"] != "true"
            or row["body_range_count"] != "1"
            or int(row["caller_count"]) != spec["caller_count"]
            or int(row["callee_count"]) != spec["callee_count"]
        ):
            raise RuntimeError(f"MAINE {spec['name']} Ghidra extent drift: {row!r}")
        proc = f" {spec['tasm']}\t proc near"
        endp = f" {spec['tasm']}\t endp"
        if proc not in listing or endp not in listing:
            raise RuntimeError(f"MAINE {spec['name']} TASM PROC/ENDP drift")
        result.append({
            "name": spec["name"],
            "payload_offset": hex(start),
            "segment_offset": hex(spec["segment_offset"]),
            "size": size,
            "target_sha256": sha(body),
            "caller_count": spec["caller_count"],
            "callee_count": spec["callee_count"],
            "tasm_proc": spec["tasm"],
        })
    return result


def replace_function(data: str, name: str, include: str) -> str:
    marker = f"void pascal near {name}("
    if data.count(marker) != 1:
        raise RuntimeError(f"{name} replacement start drift")
    start = data.index(marker)
    brace = data.index("{", start)
    depth = 0
    end = None
    for i in range(brace, len(data)):
        if data[i] == "{":
            depth += 1
        elif data[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError(f"{name} replacement end drift")
    return data[:start] + f'#include "{include}"' + data[end:]


def overlay_source(work: Path) -> str:
    upstream = work / "th04/staffall.cpp"
    if prior.sha_file(upstream) != BASE_SOURCE_SHA:
        raise RuntimeError("pinned v489 staffall.cpp drift")
    dst = work / "src/maine/end"
    dst.mkdir(parents=True, exist_ok=True)
    for spec in FUNCTIONS:
        shutil.copy2(ROOT / spec["source"], dst / Path(spec["source"]).name)

    data = upstream.read_text()
    # Replace from high address to low address so each original function marker remains unique.
    for spec in reversed(FUNCTIONS):
        data = replace_function(data, spec["name"], spec["source"])
    upstream.write_text(data)
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

    closure = source_closure(ROOT, tuple(spec["source"] for spec in FUNCTIONS))
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}
    target_mz = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target_mz.valid or not baseline.valid or len(target_mz.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")

    target = target_mz.program_image
    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    boundaries = validate_target(target, map_text)
    producer = target[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("MAINE staffall target producer identity drift")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 staffall producer differs from target")
    for spec in FUNCTIONS:
        start, size = spec["start"], spec["size"]
        if baseline.program_image[start:start + size] != target[start:start + size]:
            raise RuntimeError(f"v489 {spec['name']} differs from target")
    target_sites = [item.linear for item in target_mz.relocations]
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
        tcc(work, output, f"v725-staff-dissolves-{label}", "th04/staffall.cpp")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "MAINE_01_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained dissolve helpers changed staffall MAINE_01_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or prior.sha_file(exe) != prior.BASE_EXE_SHA
            or prior.sha_file(mp) != prior.BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: cold MAINE staff dissolve link/layout drift")

        function_hashes: dict[str, str] = {}
        for spec in FUNCTIONS:
            start, size = spec["start"], spec["size"]
            linked = image.program_image[start:start + size]
            expected = target[start:start + size]
            if linked != expected:
                raise RuntimeError(f"{label}: {spec['name']} linked body drift")
            function_hashes[spec["name"]] = sha(linked)

        builds[label] = {
            "compact_snapshot": compact,
            "patched_staffall_source_sha256": patched_source_sha,
            "group_omf_sha256": prior.sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_producer_sha256": sha(linked_producer),
            "linked_function_sha256": function_hashes,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable = lambda d: {k: v for k, v in d.items() if k != "group_omf_sha256"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent staff dissolve cold rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained staff dissolve source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE six staff dissolve helpers maintained natural-C++ cold replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": prior.sha_file(Path(__file__).resolve()),
        "boundaries": boundaries,
        "producer": {
            "segment": "MAINE_01_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "limit": (
            "Exactness claims are limited to the six maintained dissolve helpers. "
            "The already accepted staff background helper and staffroll_animate remain pinned producer context. "
            "No packed-file or whole-MAINE exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": prior.sha_file(path),
        "function_count": len(FUNCTIONS),
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
