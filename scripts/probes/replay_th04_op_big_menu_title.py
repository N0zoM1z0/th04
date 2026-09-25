#!/usr/bin/env python3
"""Cold-replay maintained natural C++ for OP op_animate and playchar_menu."""

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
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_op_playchar_menu_initial import (
    SNAPSHOT,
    TARGET,
    TARGET_SHA,
    BASE_EXE_SHA,
    BASE_MAP_SHA,
    RELOCATIONS,
    sha,
    sha_file,
    tcc_op,
)

SPECS = (
    {
        "key": "op_animate",
        "source": ROOT / "src/op/title/op_animate.inl",
        "upstream": "th04/op/title.cpp",
        "compile_tu": "th04/op_title.cpp",
        "wrapper_sha": "8c34511d4e23774726ca94a4ee4c74c6249e0c0ee2e29f6b026407e81b6c1845",
        "obj": "obj/th04/op_title.obj",
        "segment": "OP_TITLE_TEXT",
        "start": 0xCCD2,
        "size": 0x28C,
        "entry_segment": 0x1A74,
        "entry_offset": 0x2592,
        "callers": 1,
        "callees": 12,
        "body_sha": "c10de2697fd175363918df9fac9f3930e24097284ddda3f8e3d63061866847be",
        "producer_start": 0xCC97,
        "producer_size": 0x2C7,
        "producer_sha": "7e9c8576c13b3e469bcbed947fbc6bf3d819328df88fc5c2a74d808271d86d79",
        "base_source_sha": "dfbfc0c5fabf19ed99d0624371cf57f6b687f5e88cb6e0343114c9cebbf0fa23",
        "base_object_sha": "b14094e67af79cba83ec7a9a6e6d80bed2f5f99fdb2da3d3ed2b1817bff360e3",
        "base_code_sha": "c9f3aac9a7e3d2f8edc3982a75bbd809cfe51d31ef18421dcc00dc73ffc9736d",
        "marker": "void near op_animate(void)\n",
        "map_contribution": "0A74:2557 02C7 C=CODE   S=OP_TITLE_TEXT  G=OP_01   M=th04/op_title.cpp",
        "map_public": "0A74:2592       op_animate()",
        "terminal": bytes.fromhex("5f 5e c9 c3"),
    },
    {
        "key": "playchar_menu",
        "source": ROOT / "src/op/menu/playchar_menu.inl",
        "upstream": "th04/m_char.cpp",
        "compile_tu": "th04/m_char.cpp",
        "wrapper_sha": None,
        "obj": "obj/th04/m_char.obj",
        "segment": "OP_01_TEXT",
        "start": 0xD708,
        "size": 0x309,
        "entry_segment": 0x1A74,
        "entry_offset": 0x2FC8,
        "callers": 2,
        "callees": 16,
        "body_sha": "e0ef449f80bbf1fcec7d7f9e35a32f2b1664814d4ba92aaf67b89dc20b753309",
        "producer_start": 0xCF5E,
        "producer_size": 0xAB3,
        "producer_sha": "bdebb9e5d9c426fabca3fcb288dc298114f5cf9fa3e53cca96d5c4ad6d8ec7bc",
        "base_source_sha": "cd92a300b16f1aa357fe37dfd1e2bed83aa28e56223e67bb4df0f883630f2d3c",
        "base_object_sha": "939a58bc7b67e212a2ffca3462a504024beb6bdbf3ccc6834e1d03a7fc4ea413",
        "base_code_sha": "4dada9dc8d0be3cb8e42080b7e151fece1634cd84e26291b0f9a3cd7c150d043",
        "marker": "bool16 near playchar_menu(void)\n",
        "map_contribution": "0A74:281E 0AB3 C=CODE   S=OP_01_TEXT     G=OP_01   M=th04/m_char.cpp",
        "map_public": "0A74:2FC8       playchar_menu()",
        "terminal": bytes.fromhex("5f 5e c9 c3"),
    },
)


def find_function_end(text: str, start: int) -> int:
    brace = text.find("{", start)
    if brace < 0:
        raise RuntimeError("function opening brace drift")
    depth = 0
    for pos in range(brace, len(text)):
        ch = text[pos]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return pos + 1
    raise RuntimeError("unterminated function")


def validate_target(spec: dict[str, object], image: bytes, map_text: str) -> dict[str, object]:
    start = int(spec["start"])
    size = int(spec["size"])
    body = image[start:start + size]
    if len(body) != size or sha(body) != spec["body_sha"]:
        raise RuntimeError(f"{spec['key']}: target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + start
        ]
    if len(rows) != 1:
        raise RuntimeError(f"{spec['key']}: Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != int(spec["entry_segment"])
        or int(row["entry_offset"], 0) != int(spec["entry_offset"])
        or int(row["body_min_linear"], 0) != 0x10000 + start
        or int(row["body_max_linear"], 0) != 0x10000 + start + size - 1
        or int(row["body_addresses"]) != size
        or int(row["body_span"]) != size
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != int(spec["callers"])
        or int(row["callee_count"]) != int(spec["callees"])
    ):
        raise RuntimeError(f"{spec['key']}: Ghidra extent drift: {row!r}")

    if str(spec["map_contribution"]) not in map_text or str(spec["map_public"]) not in map_text:
        raise RuntimeError(f"{spec['key']}: MAP owner/public drift")

    producer_start = int(spec["producer_start"])
    producer_size = int(spec["producer_size"])
    if start + size != producer_start + producer_size:
        raise RuntimeError(f"{spec['key']}: function no longer closes producer")
    if not body.endswith(spec["terminal"]):
        raise RuntimeError(f"{spec['key']}: terminal drift")

    return {
        "name": spec["key"],
        "payload_offset": hex(start),
        "size": size,
        "target_sha256": sha(body),
        "segment_identity": f"{int(spec['entry_segment']):04X}",
        "segment_offset": f"{int(spec['entry_offset']):04X}",
        "caller_count": int(spec["callers"]),
        "callee_count": int(spec["callees"]),
        "producer_payload_offset": hex(producer_start),
        "producer_size": producer_size,
        "physical_closure": "function ends exactly at its TLINK module contribution end",
    }


def overlay_one(work: Path, spec: dict[str, object]) -> str:
    upstream = work / str(spec["upstream"])
    if sha_file(upstream) != spec["base_source_sha"]:
        raise RuntimeError(f"{spec['key']}: pinned source drift")

    source = Path(spec["source"])
    rel = source.relative_to(ROOT)
    dst = work / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dst)

    text = upstream.read_text(encoding="utf-8")
    marker = str(spec["marker"])
    if text.count(marker) != 1:
        raise RuntimeError(f"{spec['key']}: source marker drift")
    start = text.index(marker)
    end = find_function_end(text, start)
    text = text[:start] + f'#include "{rel.as_posix()}"' + text[end:]
    upstream.write_text(text, encoding="utf-8")
    return sha_file(upstream)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    for spec in SPECS:
        checks = [
            (SNAPSHOT / str(spec["upstream"]), spec["base_source_sha"]),
            (SNAPSHOT / str(spec["obj"]), spec["base_object_sha"]),
        ]
        if spec.get("wrapper_sha"):
            checks.append((SNAPSHOT / str(spec["compile_tu"]), spec["wrapper_sha"]))
        for path, expected in checks:
            if sha_file(path) != expected:
                raise RuntimeError(f"{spec['key']}: pinned input identity drift: {path}")

    source_hashes = {
        str(Path(spec["source"]).relative_to(ROOT)): sha_file(Path(spec["source"]))
        for spec in SPECS
    }
    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target")

    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    boundaries = [validate_target(spec, target.program_image, map_text) for spec in SPECS]

    for spec in SPECS:
        start = int(spec["start"])
        size = int(spec["size"])
        producer_start = int(spec["producer_start"])
        producer_size = int(spec["producer_size"])
        body = target.program_image[start:start + size]
        producer = target.program_image[producer_start:producer_start + producer_size]
        if sha(producer) != spec["producer_sha"]:
            raise RuntimeError(f"{spec['key']}: target producer identity drift")
        if baseline.program_image[start:start + size] != body:
            raise RuntimeError(f"{spec['key']}: v489 linked body differs from target")
        if baseline.program_image[producer_start:producer_start + producer_size] != producer:
            raise RuntimeError(f"{spec['key']}: v489 producer differs from target")

        obj = SNAPSHOT / str(spec["obj"])
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, str(spec["segment"]))
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or len(code) != producer_size
            or sha(code) != spec["base_code_sha"]
        ):
            raise RuntimeError(f"{spec['key']}: pinned object/code drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        patched_sources: dict[str, str] = {}
        object_results: dict[str, dict[str, object]] = {}

        for spec in SPECS:
            patched_sources[str(spec["key"])] = overlay_one(work, spec)
            obj = work / str(spec["obj"])
            obj.unlink()
            tcc_op(work, output, f"v735-{spec['key']}-{label}", str(spec["compile_tu"]))
            omf = describe_omf(obj.read_bytes())
            code = segment_bytes(obj, str(spec["segment"]))
            base_code = segment_bytes(SNAPSHOT / str(spec["obj"]), str(spec["segment"]))
            if (
                not omf["valid"]
                or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
                or code != base_code
            ):
                raise RuntimeError(f"{label}/{spec['key']}: maintained source changed producer CODE")
            object_results[str(spec["key"])] = {
                "object_sha256": sha_file(obj),
                "code_sha256": sha(code),
                "code_size": len(code),
            }

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work,
            output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
        ):
            raise RuntimeError(f"{label}: linked OP identity/layout drift")

        linked: dict[str, dict[str, object]] = {}
        for spec in SPECS:
            start = int(spec["start"])
            size = int(spec["size"])
            producer_start = int(spec["producer_start"])
            producer_size = int(spec["producer_size"])
            linked_body = image.program_image[start:start + size]
            linked_producer = image.program_image[
                producer_start:producer_start + producer_size
            ]
            target_body = target.program_image[start:start + size]
            target_producer = target.program_image[
                producer_start:producer_start + producer_size
            ]
            if linked_body != target_body or linked_producer != target_producer:
                raise RuntimeError(f"{label}/{spec['key']}: linked target equality drift")
            linked[str(spec["key"])] = {
                "body_sha256": sha(linked_body),
                "producer_sha256": sha(linked_producer),
                "raw_body_difference_count": 0,
                "raw_producer_difference_count": 0,
            }

        builds[label] = {
            "compact_snapshot": compact,
            "patched_source_sha256": patched_sources,
            "objects": object_results,
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked": linked,
            "ordered_relocations": len(target_sites),
        }

    def stable(build: dict[str, object]) -> dict[str, object]:
        clean = json.loads(json.dumps(build))
        for obj in clean["objects"].values():
            obj.pop("object_sha256", None)
        return clean

    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent OP big-function cold rounds differ")
    if any(
        sha_file(ROOT / source) != digest
        for source, digest in source_hashes.items()
    ):
        raise RuntimeError("maintained OP big-function source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP op_animate + playchar_menu maintained natural-C++ cold replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": sha_file(Path(__file__).resolve()),
        "boundaries": boundaries,
        "builds": builds,
        "limit": (
            "Exactness is limited to the maintained 652-byte op_animate and "
            "777-byte playchar_menu bodies. Each ends exactly at its own TLINK "
            "producer boundary. The v489 OP baseline retains the known two-byte "
            "SND_LOAD difference outside these producers; no packed-file or "
            "whole-OP exactness is claimed."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "functions": [spec["key"] for spec in SPECS],
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
