#!/usr/bin/env python3
"""Cold-relink OP with the maintained second frame-delay producer."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import csv
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

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/op/hardware/frame_delay_2.cpp"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"

TARGET_SHA256 = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA256 = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA256 = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"

START = 0xE6DE
SIZE = 0x15
END = START + SIZE
RELOCATIONS = 804
TARGET_FUNCTION_SHA256 = "1683f148a8bda60e6dbbe69510b3d79544e84057d6b7721facfaed4820f134aa"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def run(command: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    result = subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True, timeout=180
    )
    log.write_text(
        json.dumps(command) + f"\nexit={result.returncode}\n"
        + result.stdout + result.stderr,
        encoding="utf-8",
    )
    if result.returncode:
        raise RuntimeError(f"command failed: {log}")


def map_contribution(path: Path) -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=SHARED\b.*\bM=th02/frmdely2\.cpp(?:\s|$)",
        re.I,
    )
    matches = []
    for line in path.read_text(encoding="cp437").splitlines():
        found = pattern.search(line)
        if found:
            matches.append(
                (
                    int(found[1], 16) * 16 + int(found[2], 16),
                    int(found[3], 16),
                    line.strip(),
                )
            )
    if len(matches) != 1:
        raise RuntimeError(f"expected one frame_delay_2 MAP contribution: {matches}")
    return matches[0]


def target_boundary(body: bytes) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA256:
        raise RuntimeError("OP frame_delay_2 target identity drift")
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row
            for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP frame_delay_2 Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1DA1
        or int(row["entry_offset"], 0) != 0x0CCE
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + END - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 0
    ):
        raise RuntimeError(f"OP frame_delay_2 Ghidra extent drift: {row!r}")
    # Target-local instruction shape: zero one word, poll it against the Pascal
    # argument, short-loop backward, then RETF 2.
    if (
        body[:3] != b"\x55\x8b\xec"
        or body[3:7] != b"\xc7\x06\xc6\x1a"
        or body[7:9] != b"\x00\x00"
        or body[9:12] != b"\xa1\xc6\x1a"
        or body[12:15] != b"\x3b\x46\x06"
        or body[15:17] != b"\x72\xf8"
        or body[17:] != b"\x5d\xca\x02\x00"
    ):
        raise RuntimeError("OP frame_delay_2 instruction/operand topology drift")
    return {
        "payload_offset": hex(START),
        "segment_identity": "1DA1",
        "segment_offset": "0CCE",
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 0,
        "terminal": "RETF 2",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--retain-candidates", action="store_true")
    args = parser.parse_args()

    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        parser.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA256:
        raise RuntimeError("pinned DOS runner identity drift")
    if sha_file(TARGET) != TARGET_SHA256:
        raise RuntimeError("OP restored target identity drift")
    baseline_path = SNAPSHOT / "bin/th04/op.exe"
    map_path = SNAPSHOT / "obj/th04/op.map"
    if sha_file(baseline_path) != BASE_EXE_SHA256 or sha_file(map_path) != BASE_MAP_SHA256:
        raise RuntimeError("v489 OP baseline identity drift")

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz(baseline_path.read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target/baseline MZ control")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target")

    body = target.program_image[START:END]
    boundary = target_boundary(body)
    if baseline.program_image[START:END] != body:
        raise RuntimeError("v489 OP frame_delay_2 slice differs from target")
    base_start, base_size, base_line = map_contribution(map_path)
    if (base_start, base_size) != (START, SIZE):
        raise RuntimeError(f"v489 frame_delay_2 MAP ownership drift: {base_line}")
    if "0DA1:0CCE       frame_delay_2(int)" not in map_path.read_text(encoding="cp437"):
        raise RuntimeError("v489 frame_delay_2 MAP public drift")

    source_hash = sha_file(SOURCE)
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}

    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")

        source_dst = work / "src/op/hardware/frame_delay_2.cpp"
        source_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, source_dst)
        shared_dst = work / "src/shared"
        shared_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / "src/shared", shared_dst, dirs_exist_ok=True)
        shutil.copy2(SOURCE, work / "th02/frmdely2.cpp")

        obj = work / "obj/th02/frmdely2.obj"
        obj.unlink()
        run(
            [
                "wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O",
                "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th02/",
                "th02/frmdely2.cpp",
            ],
            work,
            output / f"compile-{label}.log",
            env,
        )
        if not obj.is_file():
            raise RuntimeError(f"{label}: compiler omitted frmdely2.obj")
        omf = describe_omf(obj.read_bytes())
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
        ):
            raise RuntimeError(f"{label}: invalid or wrong-producer OMF")

        exe = work / "bin/th04/op.exe"
        linked_map = work / "obj/th04/op.map"
        exe.unlink()
        linked_map.unlink()
        run(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work,
            output / f"link-{label}.log",
            env,
        )
        candidate = parse_mz(exe.read_bytes())
        if not candidate.valid:
            raise RuntimeError(f"{label}: invalid linked OP MZ")
        relocations = [item.linear for item in candidate.relocations]
        if relocations != target_sites:
            raise RuntimeError(f"{label}: ordered OP relocations differ")

        map_start, map_size, map_line = map_contribution(linked_map)
        if (map_start, map_size) != (START, SIZE):
            raise RuntimeError(f"{label}: frame_delay_2 source ownership moved")

        actual = candidate.program_image[START:END]
        differences = [
            i for i, (expected, got) in enumerate(zip(body, actual))
            if expected != got
        ]
        if (
            differences
            or candidate.program_image != baseline.program_image
            or sha_file(exe) != BASE_EXE_SHA256
            or sha_file(linked_map) != BASE_MAP_SHA256
        ):
            raise RuntimeError(
                f"{label}: frame_delay_2 or aggregate OP differs at {differences[:16]}"
            )
        builds[label] = {
            "compact_snapshot": compact,
            "source_object_sha256": sha_file(obj),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(linked_map),
            "map_contribution": map_line,
            "target_function_sha256": sha(body),
            "candidate_function_sha256": sha(actual),
            "raw_difference_count": len(differences),
            "ordered_relocations": len(relocations),
            "candidate_program_sha256": sha(candidate.program_image),
            "baseline_program_equal": candidate.program_image == baseline.program_image,
        }

    if builds["a"] != builds["b"]:
        raise RuntimeError("independent OP frame_delay_2 cold rounds differ")
    if sha_file(SOURCE) != source_hash:
        raise RuntimeError("maintained frame_delay_2 source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed frame_delay_2 maintained-source cold-link replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA256,
        "baseline_exe_sha256": BASE_EXE_SHA256,
        "baseline_map_sha256": BASE_MAP_SHA256,
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "boundary": boundary,
        "builds": builds,
        "limit": "Decoded 21-byte function only; no DIET-packed offset or whole-OP exactness.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if args.retain_candidates:
        for label in ("a", "b"):
            src = output / label / "op/source/bin/th04/op.exe"
            shutil.copy2(src, output / f"{label}-op.exe")

    if not args.retain_candidates:
        for label in ("a", "b"):
            shutil.rmtree(output / label)

    print(json.dumps({
        "receipt": str(receipt_path),
        "function_sha256": builds["a"]["candidate_function_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
