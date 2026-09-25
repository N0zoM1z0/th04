#!/usr/bin/env python3
"""Cold-replay maintained natural C++ for OP setup_bgm_menu + setup_se_menu."""

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
from replay_th04_op_help_put import (
    BASE_EXE_SHA, BASE_MAP_SHA, BASE_SETUP_CODE_SHA, BASE_SETUP_OBJECT_SHA,
    BASE_SETUP_SOURCE_SHA, PRODUCER_SIZE, PRODUCER_START, RELOCATIONS, SNAPSHOT,
    TARGET, TARGET_PRODUCER_SHA, TARGET_SHA, sha, sha_file, tcc_op,
)

FUNCTIONS = (
    {
        "key": "setup_bgm_menu",
        "source": "src/op/setup/setup_bgm_menu.inl",
        "marker": "void near setup_bgm_menu(void)\n",
        "start": 0xB794, "size": 0x11D, "entry_offset": 0x1054,
        "sha256": "e8e175a0523c2acfb81ccd7bd4ba41dfa745d2c06aeb0180a10c54eeb6190e62",
        "map_public": "0A74:1054 idle  setup_bgm_menu()",
    },
    {
        "key": "setup_se_menu",
        "source": "src/op/setup/setup_se_menu.inl",
        "marker": "void near setup_se_menu(void)\n",
        "start": 0xB8B1, "size": 0x11D, "entry_offset": 0x1171,
        "sha256": "832c428b8f4ae474aa53a15ff6a1f948c29d997293cf13a92f0163c2226db71b",
        "map_public": "0A74:1171 idle  setup_se_menu()",
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
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    contribution = "0A74:0D5F 05A6 C=CODE   S=OP_SETUP_TEXT  G=OP_01   M=th04/op_setup.cpp"
    if contribution not in map_text:
        raise RuntimeError("OP setup producer MAP contribution drift")

    out = []
    for spec in FUNCTIONS:
        start, size = int(spec["start"]), int(spec["size"])
        body = image[start:start + size]
        if len(body) != size or sha(body) != spec["sha256"]:
            raise RuntimeError(f"{spec['key']}: target identity drift")
        matches = [r for r in rows if int(r["entry_linear"], 0) == 0x10000 + start]
        if len(matches) != 1:
            raise RuntimeError(f"{spec['key']}: Ghidra entry count drift")
        row = matches[0]
        if (
            int(row["entry_segment"], 0) != 0x1A74
            or int(row["entry_offset"], 0) != int(spec["entry_offset"])
            or int(row["body_min_linear"], 0) != 0x10000 + start
            or int(row["body_max_linear"], 0) != 0x10000 + start + size - 1
            or int(row["body_addresses"]) != size
            or int(row["body_span"]) != size
            or row["contiguous"] != "true"
            or row["body_range_count"] != "1"
            or int(row["caller_count"]) != 1
            or int(row["callee_count"]) != 8
        ):
            raise RuntimeError(f"{spec['key']}: Ghidra extent drift: {row!r}")
        if spec["map_public"] not in map_text:
            raise RuntimeError(f"{spec['key']}: MAP public drift")
        if body[:4] != bytes.fromhex("c8 02 00 00") or body[-2:] != bytes.fromhex("c9 c3"):
            raise RuntimeError(f"{spec['key']}: body shape drift")
        out.append({
            "name": spec["key"],
            "payload_offset": hex(start),
            "size": size,
            "target_sha256": sha(body),
            "segment_identity": "1A74",
            "segment_offset": f"{int(spec['entry_offset']):04X}",
            "caller_count": 1,
            "callee_count": 8,
        })
    return out


def overlay_source(work: Path) -> str:
    upstream = work / "th04/op/m_setup.cpp"
    if sha_file(upstream) != BASE_SETUP_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP setup source drift")

    dst_root = work / "src/op/setup"
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
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/op/m_setup.cpp", BASE_SETUP_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_setup.obj", BASE_SETUP_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {str(s["source"]): sha_file(ROOT / s["source"]) for s in FUNCTIONS}

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [x.linear for x in target.relocations]
    if [x.linear for x in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target")

    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    boundaries = validate_target(target.program_image, map_text)
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target OP_SETUP_TEXT producer identity drift")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 OP setup producer differs from target")

    base_obj = SNAPSHOT / "obj/th04/op_setup.obj"
    base_desc = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "OP_SETUP_TEXT")
    if (
        not base_desc["valid"]
        or "TC86 Borland C++ 4.02" not in base_desc["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_SETUP_CODE_SHA
    ):
        raise RuntimeError("pinned OP setup object/code drift")

    output.mkdir(parents=True)
    builds = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        patched = overlay_source(work)

        obj = work / "obj/th04/op_setup.obj"
        obj.unlink()
        tcc_op(work, output, f"v745-setup-submenus-{label}", "th04/op_setup.cpp")
        desc = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "OP_SETUP_TEXT")
        if (
            not desc["valid"]
            or "TC86 Borland C++ 4.02" not in desc["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained setup submenus changed producer CODE")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink(); mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked_prod = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [x.linear for x in image.relocations] != target_sites
            or linked_prod != producer
        ):
            raise RuntimeError(f"{label}: linked OP setup producer/layout drift")

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
            "patched_source_sha256": patched,
            "object_sha256": sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_producer_sha256": sha(linked_prod),
            "linked": linked,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    def stable(d: dict[str, object]) -> dict[str, object]:
        c = dict(d); c.pop("object_sha256", None); return c
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent setup-submenu cold rounds differ")
    if any(sha_file(ROOT / p) != digest for p, digest in source_hashes.items()):
        raise RuntimeError("maintained setup submenu source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP setup_bgm_menu + setup_se_menu maintained natural-C++ cold replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": sha_file(Path(__file__).resolve()),
        "boundaries": boundaries,
        "producer": {
            "segment": "OP_SETUP_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "limit": (
            "Exactness claims are limited to setup_bgm_menu and setup_se_menu. "
            "Already accepted functions in the same producer remain pinned scaffold. "
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
