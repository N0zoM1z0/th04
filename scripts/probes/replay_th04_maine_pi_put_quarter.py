#!/usr/bin/env python3
"""Cold-rebuild MAINE's complete SHARED pi_put_quarter_8 producer."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
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

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import describe_omf
from lib.pc98 import parse_mz
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_zun_source_only import source_closure
import replay_th04_maine_score_insert as prior

SOURCE = ROOT / "src/shared/formats/pi_put_quarter.cpp"
SNAPSHOT = prior.SNAPSHOT
TARGET = prior.TARGET
START = 0xCDAB
SIZE = 0xB1
NEXT = START + SIZE
RELOCATIONS = prior.RELOCATIONS
TARGET_SHA = "371a715332cd353be0d47df96cf8099f9da02460d1ae4b8be63b38afb9bd1b23"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA = prior.RUNNER_SHA
RAW_CALLER = 0xACEB
RAW_CALL = bytes.fromhex("9A 3B 01 C7 0C")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=180)
    log.write_text(json.dumps(command) + f"\nexit={result.returncode}\n"
                   + result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"command failed; see {log}")


def contribution(map_path: Path) -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=SHARED\b.*\bM=th03/pi_put_q\.cpp(?:\s|$)", re.I,
    )
    matches = []
    for line in map_path.read_text(encoding="cp437").splitlines():
        found = pattern.search(line)
        if found:
            matches.append((
                int(found[1], 16) * 16 + int(found[2], 16),
                int(found[3], 16),
                line.strip(),
            ))
    if len(matches) != 1:
        raise RuntimeError(f"expected one pi_put_q MAP contribution: {matches!r}")
    return matches[0]


def target_boundary(program: bytes, body: bytes, map_text: str) -> dict[str, object]:
    actual_sha = sha(body)
    if len(body) != SIZE or actual_sha != TARGET_SHA:
        raise RuntimeError("MAINE pi_put_quarter_8 target identity drift")
    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = [r for r in csv.DictReader(stream)
                if int(r["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("MAINE pi_put_quarter_8 Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1CC7
        or int(row["entry_offset"], 0) != 0x013B
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
    ):
        raise RuntimeError(f"MAINE pi_put_quarter_8 Ghidra extent drift: {row!r}")
    if "0CC7:013B       pi_put_quarter_8(int,int,int,int)" not in map_text:
        raise RuntimeError("MAINE pi_put_quarter_8 MAP symbol drift")
    if program[RAW_CALLER:RAW_CALLER + len(RAW_CALL)] != RAW_CALL:
        raise RuntimeError("MAINE raw pi_put_quarter_8 caller drift")
    if "0CC7:01EC 001E C=CODE   S=SHARED" not in map_text:
        raise RuntimeError("MAINE pi_put_quarter_8 next contribution drift")
    return {
        "segment_identity": "1CC7",
        "segment_offset": "013B",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": actual_sha,
        "ghidra_caller_count": int(row["caller_count"]),
        "ghidra_callee_count": int(row["callee_count"]),
        "raw_caller_payload_offset": hex(RAW_CALLER),
        "raw_caller_target": "0CC7:013B",
        "next_contribution": "1CC7:01EC hfliplut.asm",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    if sha(RUNNER.read_bytes()) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")

    target_bytes = TARGET.read_bytes()
    baseline_exe = SNAPSHOT / "bin/th04/maine.exe"
    baseline_map = SNAPSHOT / "obj/th04/maine.map"
    if sha(target_bytes) != prior.TARGET_SHA or sha(baseline_exe.read_bytes()) != prior.BASE_EXE_SHA:
        raise RuntimeError("MAINE target/baseline identity drift")
    target = parse_mz(target_bytes)
    baseline = parse_mz(baseline_exe.read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid MAINE target/baseline")
    body = target.program_image[START:NEXT]
    map_text = baseline_map.read_text(encoding="cp437")
    boundary = target_boundary(target.program_image, body, map_text)
    if baseline.program_image[START:NEXT] != body:
        raise RuntimeError("baseline pi_put_quarter_8 differs from target")
    target_relocs = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_relocs:
        raise RuntimeError("baseline ordered relocations differ from target")

    closure = source_closure(ROOT, ("src/shared/formats/pi_put_quarter.cpp",))
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}

    output.mkdir(parents=True)
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "maine")
        shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
        shutil.copy2(SOURCE, work / "th03/pi_put_q.cpp")

        obj = work / "obj/th03/pi_put_q.obj"
        obj.unlink()
        command = [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-",
            "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th03/", "th03/pi_put_q.cpp",
        ]
        run(command, work, output / f"compile-{label}.log", env)
        if not obj.is_file():
            raise RuntimeError(f"{label}: compiler omitted pi_put_q.obj")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "SHARED")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or len(code) != SIZE
        ):
            raise RuntimeError(f"{label}: standalone pi_put_q object topology drift")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
            work, output / f"link-{label}.log", env)
        image = parse_mz(exe.read_bytes())
        if not image.valid:
            raise RuntimeError(f"{label}: invalid linked MAINE")
        if [item.linear for item in image.relocations] != target_relocs:
            raise RuntimeError(f"{label}: ordered relocations differ")
        map_start, map_size, map_line = contribution(mp)
        if (map_start, map_size) != (START, SIZE):
            raise RuntimeError(f"{label}: pi_put_q source ownership moved")
        linked = image.program_image[START:NEXT]
        diffs = [i for i, (a, b) in enumerate(zip(body, linked)) if a != b]
        if diffs or image.program_image != baseline.program_image:
            raise RuntimeError(f"{label}: linked pi_put_quarter_8/program differs: {diffs[:16]}")
        if prior.sha_file(exe) != prior.BASE_EXE_SHA:
            raise RuntimeError(f"{label}: aggregate EXE identity drift")
        builds[label] = {
            "compact_snapshot": compact,
            "object_sha256": prior.sha_file(obj),
            "object_normalized_sha256": omf["dependency_timestamp_normalized_sha256"],
            "object_code_sha256": sha(code),
            "map_contribution": map_line,
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked),
            "raw_function_difference_count": len(diffs),
            "ordered_relocations": len(target_relocs),
        }
    stable = lambda d: {k: v for k, v in d.items() if k != "object_sha256"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("pi_put_quarter_8 cold rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-maine",
        "claim_scope": "complete SHARED pi_put_quarter_8 object contribution and linked MAINE replay",
        "target_restored_sha256": prior.TARGET_SHA,
        "baseline_exe_sha256": prior.BASE_EXE_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "module": "th03/pi_put_q.cpp",
            "segment": "SHARED",
            "payload_offset": hex(START),
            "size": SIZE,
            "target_sha256": sha(body),
        },
        "builds": builds,
        "limit": "Decoded function/object contribution only; no packed-file or whole-MAINE exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": prior.sha_file(path),
        "target_function_sha256": sha(body),
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
