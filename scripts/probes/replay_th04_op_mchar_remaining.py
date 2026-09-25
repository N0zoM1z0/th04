#!/usr/bin/env python3
"""Cold-replay five maintained natural-C++ OP m_char.cpp function bodies."""

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
    SNAPSHOT, TARGET, TARGET_SHA, BASE_EXE_SHA, BASE_MAP_SHA, RELOCATIONS,
    sha, sha_file, tcc_op,
)

PRODUCER_START = 0xCF5E
PRODUCER_SIZE = 0xAB3
PRODUCER_SHA = "bdebb9e5d9c426fabca3fcb288dc298114f5cf9fa3e53cca96d5c4ad6d8ec7bc"
BASE_SOURCE_SHA = "cd92a300b16f1aa357fe37dfd1e2bed83aa28e56223e67bb4df0f883630f2d3c"
BASE_OBJECT_SHA = "939a58bc7b67e212a2ffca3462a504024beb6bdbf3ccc6834e1d03a7fc4ea413"
BASE_CODE_SHA = "4dada9dc8d0be3cb8e42080b7e151fece1634cd84e26291b0f9a3cd7c150d043"

FUNCTIONS = (
    {
        "key": "raise_bg_allocate_and_snap",
        "source": "src/op/menu/raise_bg_allocate_and_snap.inl",
        "marker": "void near raise_bg_allocate_and_snap(void)\n",
        "start": 0xCF5E, "size": 0x1A1, "entry_offset": 0x281E,
        "sha256": "6eceb7513ca7d81860b5550f4f8d21b5dba25359b3fd5c11e41ae80d3794c15b",
        "callers": 1, "callees": 1,
        "map_public": "0A74:281E idle  raise_bg_allocate_and_snap()",
    },
    {
        "key": "raise_bg_put",
        "source": "src/op/menu/raise_bg_put.inl",
        "marker": "void near pascal raise_bg_put(playchar_t playchar_lowered)\n",
        "start": 0xD0FF, "size": 0xF4, "entry_offset": 0x29BF,
        "sha256": "76b988357cfa9808b822cc539951bb6f8b7bb67961fce5495b702da7982c9477",
        "callers": 1, "callees": 0,
        "map_public": "0A74:29BF idle  raise_bg_put(playchar_t)",
    },
    {
        "key": "pic_put",
        "source": "src/op/menu/pic_put.inl",
        "marker": "void near pic_put(void)\n",
        "start": 0xD3A2, "size": 0xC3, "entry_offset": 0x2C62,
        "sha256": "6b538f1183a27691c39a65dbcc00d5979066248d0ecccf2a7610d7209d88ca71",
        "callers": 2, "callees": 6,
        "map_public": "0A74:2C62 idle  pic_put()",
    },
    {
        "key": "shottype_titles_put",
        "source": "src/op/menu/shottype_titles_put.inl",
        "marker": "void near pascal shottype_titles_put(int sel)\n",
        "start": 0xD465, "size": 0x130, "entry_offset": 0x2D25,
        "sha256": "89b85ae1fa1a1351b158cd8603ac45dc95b9af5d700f8dbcf8237cda58d15e60",
        "callers": 2, "callees": 1,
        "map_public": "0A74:2D25 idle  shottype_titles_put(int)",
    },
    {
        "key": "shottype_title_box_put",
        "source": "src/op/menu/shottype_title_box_put.inl",
        "marker": "void near shottype_title_box_put(void)\n",
        "start": 0xD595, "size": 0xBB, "entry_offset": 0x2E55,
        "sha256": "b567047e46f146bee44d2e434f48b3aabbd8e7cacf36019b4f9db4c8a82d90b2",
        "callers": 1, "callees": 3,
        "map_public": "0A74:2E55 idle  shottype_title_box_put()",
    },
)


def find_function_end(text: str, start: int) -> int:
    brace = text.find("{", start)
    if brace < 0:
        raise RuntimeError("function opening brace drift")
    depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return pos + 1
    raise RuntimeError("unterminated function")


def validate_target(image: bytes, map_text: str) -> list[dict[str, object]]:
    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    contribution = "0A74:281E 0AB3 C=CODE   S=OP_01_TEXT     G=OP_01   M=th04/m_char.cpp"
    if contribution not in map_text:
        raise RuntimeError("m_char.cpp MAP contribution drift")

    out: list[dict[str, object]] = []
    for spec in FUNCTIONS:
        start, size = int(spec["start"]), int(spec["size"])
        body = image[start:start + size]
        if len(body) != size or sha(body) != spec["sha256"]:
            raise RuntimeError(f"{spec['key']}: target identity drift")
        matched = [r for r in rows if int(r["entry_linear"], 0) == 0x10000 + start]
        if len(matched) != 1:
            raise RuntimeError(f"{spec['key']}: Ghidra entry count drift")
        row = matched[0]
        if (
            int(row["entry_segment"], 0) != 0x1A74
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
        if spec["map_public"] not in map_text:
            raise RuntimeError(f"{spec['key']}: MAP public drift")
        out.append({
            "name": spec["key"],
            "payload_offset": hex(start),
            "size": size,
            "target_sha256": sha(body),
            "segment_identity": "1A74",
            "segment_offset": f"{int(spec['entry_offset']):04X}",
            "caller_count": int(spec["callers"]),
            "callee_count": int(spec["callees"]),
        })
    return out


def overlay_source(work: Path) -> str:
    upstream = work / "th04/m_char.cpp"
    if sha_file(upstream) != BASE_SOURCE_SHA:
        raise RuntimeError("pinned v489 m_char.cpp drift")

    dst_root = work / "src/op/menu"
    dst_root.mkdir(parents=True, exist_ok=True)
    for spec in FUNCTIONS:
        shutil.copy2(ROOT / spec["source"], dst_root / Path(spec["source"]).name)

    text = upstream.read_text(encoding="utf-8")
    positions = []
    for spec in FUNCTIONS:
        marker = str(spec["marker"])
        if text.count(marker) != 1:
            raise RuntimeError(f"{spec['key']}: source marker drift")
        positions.append((text.index(marker), spec))
    for start, spec in sorted(positions, reverse=True):
        end = find_function_end(text, start)
        text = text[:start] + f'#include "{spec["source"]}"' + text[end:]
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
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/m_char.cpp", BASE_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/m_char.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        str(spec["source"]): sha_file(ROOT / spec["source"]) for spec in FUNCTIONS
    }

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [r.linear for r in target.relocations]
    if [r.linear for r in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target")

    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    boundaries = validate_target(target.program_image, map_text)

    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != PRODUCER_SHA:
        raise RuntimeError("target m_char producer identity drift")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 m_char producer differs from target")

    base_obj = SNAPSHOT / "obj/th04/m_char.obj"
    base_omf = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "OP_01_TEXT")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_CODE_SHA
    ):
        raise RuntimeError("pinned m_char object/code drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        patched_source_sha = overlay_source(work)

        obj = work / "obj/th04/m_char.obj"
        obj.unlink()
        tcc_op(work, output, f"v738-mchar-remaining-{label}", "th04/m_char.cpp")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "OP_01_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained m_char bodies changed producer CODE")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [r.linear for r in image.relocations] != target_sites
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked OP m_char identity/layout drift")

        linked = {}
        for spec in FUNCTIONS:
            start, size = int(spec["start"]), int(spec["size"])
            body = image.program_image[start:start + size]
            target_body = target.program_image[start:start + size]
            if body != target_body:
                raise RuntimeError(f"{label}/{spec['key']}: linked body drift")
            linked[str(spec["key"])] = {
                "body_sha256": sha(body),
                "raw_body_difference_count": 0,
            }

        builds[label] = {
            "compact_snapshot": compact,
            "patched_source_sha256": patched_source_sha,
            "object_sha256": sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_producer_sha256": sha(linked_producer),
            "linked": linked,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    def stable(build: dict[str, object]) -> dict[str, object]:
        clean = dict(build)
        clean.pop("object_sha256", None)
        return clean

    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent m_char cold rounds differ")
    if any(sha_file(ROOT / path) != digest for path, digest in source_hashes.items()):
        raise RuntimeError("maintained m_char source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP five remaining m_char.cpp maintained natural-C++ cold replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": sha_file(Path(__file__).resolve()),
        "boundaries": boundaries,
        "producer": {
            "segment": "OP_01_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
            "raw_target_difference_count": 0,
        },
        "surrounding_scaffold": (
            "Other already-accepted m_char.cpp functions remain pinned current-v489 "
            "producer context and receive no new credit from this receipt."
        ),
        "builds": builds,
        "limit": (
            "Exactness claims are limited to raise_bg_allocate_and_snap, raise_bg_put, "
            "pic_put, shottype_titles_put, and shottype_title_box_put. "
            "No packed-file or whole-OP exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "function_count": len(FUNCTIONS),
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
