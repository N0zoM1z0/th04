#!/usr/bin/env python3
"""Cold-compile maintained OP game_init_op and verify TLINK same-segment call optimization."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import describe_omf, parse_omf
from lib.pc98 import parse_mz
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_op_help_put import SNAPSHOT, tcc_op, loose_segment_bytes
from replay_th04_scroll_driver_natural import fixup_locations
from replay_th04_shared_delay_measure import link_relevant_omf_sha
from replay_th04_zun_source_only import source_closure

TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/shared/core/game_init_op.cpp"

TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
BASE_WRAPPER_SHA = "8cd7f9d900d888988c27ca2a9278dcc928b6fb6d874edaa58b9b4f4f8e89918b"
BASE_OBJECT_SHA = "7f85bb351c7baf842c202a6a233520b758b94feec779131ab46a99eae8677238"
BASE_LINK_OMF_SHA = "c9f63f632abd951c012a4ad47fc0dc42e6a0c4bc53319a31e8039f51c3f1942b"
BASE_CODE_SHA = "486a8626639b0df19c72a4d392e9b3d9a8e985f582da782b8d178978a58c31c6"
STANDALONE_CODE_SHA = "3e8065c747fac27b2bc77d7c6e98347a3ab3ebf0b4cd0de64eaf7563d7f4aed6"
STANDALONE_FIXUPS = [
    (3, 121), (3, 113), (3, 95), (3, 90), (3, 85),
    (3, 80), (3, 75), (3, 70), (1, 65), (3, 49),
    (3, 38), (3, 27), (3, 22), (3, 8), (1, 5),
]
RELOCATIONS = 804

START = 0xE0F4
SIZE = 0x81
NEXT = START + SIZE
PRODUCER_SIZE = 0x82
TARGET_FUNCTION_SHA = "3242fc6b331e7d6a9068d08ca41d7c5bcec1f61a20931fa9c69daa2d3df675c4"
TARGET_PRODUCER_SHA = "3bb04ee1153214fc65d84463e62713d1174f4783934337839af0ce6753562a97"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def object_fixups(obj: Path) -> list[tuple[int, int]]:
    return [
        item
        for rec in parse_omf(obj.read_bytes())
        if rec.record_type == 0x9C
        for item in fixup_locations(rec.data)
    ]


def map_contribution(path: Path) -> tuple[int, int, str]:
    pat = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=SHARED\b.*\bM=th04/initop\.cpp(?:\s|$)",
        re.I,
    )
    matches = []
    for line in path.read_text(encoding="cp437").splitlines():
        m = pat.search(line)
        if m:
            matches.append((
                int(m[1], 16) * 16 + int(m[2], 16),
                int(m[3], 16),
                line.strip(),
            ))
    if len(matches) != 1:
        raise RuntimeError(f"expected one initop MAP contribution: {matches}")
    return matches[0]


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP game_init_op target identity drift")
    p = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    rows = [
        row
        for row in csv.DictReader(p.open(newline="", encoding="utf-8"))
        if int(row["entry_linear"], 0) == 0x10000 + START
    ]
    if len(rows) != 1:
        raise RuntimeError("OP game_init_op Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1DA1
        or int(row["entry_offset"], 0) != 0x06E4
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 12
    ):
        raise RuntimeError(f"OP game_init_op Ghidra extent drift: {row!r}")

    required = (
        "0DA1:06E4       game_init_op(const unsigned char far*)",
        "0F34:270E       _mem_assign_paras",
        "0000:26E2       MEM_ASSIGN_DOS",
        "0DA1:0002       vram_planes_set()",
        "0000:1D32       GRAPH_START",
        "0000:1532       GRAPH_CLEAR",
        "0F34:05BE       _bbufsiz",
        "0000:2552       VSYNC_START",
        "0000:1D5E       KEY_BEEP_OFF",
        "0000:252C       TEXT_SYSTEMLINE_HIDE",
        "0000:2520       TEXT_CURSOR_HIDE",
        "0000:086E       EGC_START",
        "0000:323A       JS_START",
        "0000:2FE2       PFSTART",
        "0000:3B6E       BGM_INIT",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP game_init_op MAP target drift")

    if (
        body[:7] != bytes.fromhex("55 8b ec ff 36 0e 27")
        or body[7] != 0x9A
        or int.from_bytes(body[8:10], "little") != 0x26E2
        or int.from_bytes(body[10:12], "little") != 0x0000
        or body[12:21] != bytes.fromhex("0b c0 74 05 b8 01 00 5d cb")
        or body[21:26] != bytes.fromhex("90 0e e8 04 f9")
        or body[26] != 0x9A
        or int.from_bytes(body[27:29], "little") != 0x1D32
        or body[31:37] != bytes.fromhex("ba a6 00 b0 01 ee")
        or body[42:48] != bytes.fromhex("ba a6 00 b0 00 ee")
        or body[53:63] != bytes.fromhex("ba a6 00 b0 00 ee ba a4 00 ee")
        or body[63:69] != bytes.fromhex("c7 06 be 05 00 20")
        or body[99:108] != bytes.fromhex("c4 5e 06 26 80 3f 00 74 09")
        or body[108:113] != bytes.fromhex("ff 76 08 53 9a")
        or int.from_bytes(body[113:115], "little") != 0x2FE2
        or body[117:121] != bytes.fromhex("68 00 04 9a")
        or int.from_bytes(body[121:123], "little") != 0x3B6E
        or body[125:] != bytes.fromhex("33 c0 5d cb")
    ):
        raise RuntimeError("OP game_init_op target topology drift")

    return {
        "segment_identity": "1DA1",
        "segment_offset": "06E4",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 1,
        "callee_count": 12,
        "same_segment_call": "vram_planes_set via TLINK NOP/PUSH CS/CALL rel16",
        "graph_clear_both": True,
        "bbufsiz": 8192,
        "optional_pfstart": True,
        "bgm_init_bytes": 1024,
        "terminal": "RETF",
    }


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
        check=True,
        capture_output=True,
        text=True,
    )
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/initop.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "obj/th04/initop.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")

    base_obj = SNAPSHOT / "obj/th04/initop.obj"
    base_code = segment_bytes(base_obj, "SHARED")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_CODE_SHA:
        raise RuntimeError("baseline initop SHARED contribution drift")
    if link_relevant_omf_sha(base_obj) != BASE_LINK_OMF_SHA:
        raise RuntimeError("baseline initop OMF drift")

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid OP target/baseline")
    sites = [x.linear for x in target.relocations]
    if [x.linear for x in baseline.relocations] != sites:
        raise RuntimeError("OP baseline relocation order drift")

    body = target.program_image[START:NEXT]
    producer = target.program_image[START:START + PRODUCER_SIZE]
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("OP game_init_op producer identity drift")
    if (
        baseline.program_image[START:NEXT] != body
        or baseline.program_image[START:START + PRODUCER_SIZE] != producer
    ):
        raise RuntimeError("v489 game_init_op baseline differs from target")
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    bound = target_boundary(body, map_text)
    mstart, msize, mline = map_contribution(SNAPSHOT / "obj/th04/op.map")
    if (mstart, msize) != (START, PRODUCER_SIZE):
        raise RuntimeError(f"baseline initop MAP contribution drift: {mline}")

    closure = source_closure(ROOT, ("src/shared/core/game_init_op.cpp",))
    source_hashes = {name: sha_file(ROOT / name) for name in closure}

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        for rel in closure:
            dst = work / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)

        before = {p.name for p in (work / "obj/th04").glob("*.obj")}
        tcc_op(
            work,
            output,
            f"game-init-op-standalone-{label}",
            "src/shared/core/game_init_op.cpp",
        )
        standalone = [
            p for p in (work / "obj/th04").glob("*.obj")
            if p.name not in before
        ]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_desc = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "SHARED")
        local_fixups = object_fixups(local_obj)
        if (
            not local_desc["valid"]
            or "TC86 Borland C++ 4.02" not in local_desc["translator_comments"]
            or len(local_code) != SIZE
            or sha(local_code) != STANDALONE_CODE_SHA
            or local_fixups != STANDALONE_FIXUPS
        ):
            raise RuntimeError(f"{label}: standalone game_init_op codegen drift")

        masked_target = bytearray(body)
        masked_local = bytearray(local_code)
        for kind, off in STANDALONE_FIXUPS:
            width = 2 if kind == 1 else 4
            masked_target[off:off + width] = b"\0" * width
            masked_local[off:off + width] = b"\0" * width
        diffs = [
            i for i, (a, b) in enumerate(zip(masked_target, masked_local))
            if a != b
        ]
        if diffs != [21] or masked_target[21] != 0x90 or masked_local[21] != 0x9A:
            raise RuntimeError(
                f"{label}: non-fixup delta no longer isolates TLINK call optimization: {diffs}"
            )

        wrapper = work / "th04/initop.cpp"
        if sha_file(wrapper) != BASE_WRAPPER_SHA:
            raise RuntimeError(f"{label}: initop wrapper drift")
        wrapper.write_text(
            '#include "src/shared/core/game_init_op.cpp"\n'
            '#pragma codestring "\\x00"\n'
        )
        wrapper_sha = sha_file(wrapper)
        group_obj = work / "obj/th04/initop.obj"
        group_obj.unlink()
        tcc_op(work, output, f"game-init-op-group-{label}", "th04/initop.cpp")
        group_desc = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "SHARED")
        if (
            not group_desc["valid"]
            or "TC86 Borland C++ 4.02" not in group_desc["translator_comments"]
            or group_code != base_code
            or link_relevant_omf_sha(group_obj) != BASE_LINK_OMF_SHA
        ):
            raise RuntimeError(f"{label}: grouped initop.obj drift")

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
        linked = image.program_image[START:NEXT]
        linked_producer = image.program_image[START:START + PRODUCER_SIZE]
        map_start, map_size, map_line = map_contribution(mp)
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [x.linear for x in image.relocations] != sites
            or image.program_image != baseline.program_image
            or linked != body
            or linked_producer != producer
            or (map_start, map_size) != (START, PRODUCER_SIZE)
        ):
            raise RuntimeError(f"{label}: linked OP game_init_op/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_wrapper_sha256": wrapper_sha,
            "standalone_object_sha256": sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": sha(local_code),
            "standalone_fixup_sites": [list(x) for x in local_fixups],
            "standalone_masked_difference_offsets": diffs,
            "group_object_sha256": sha_file(group_obj),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": sha(group_code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked),
            "linked_producer_sha256": sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(sites),
            "map_contribution": map_line,
            "tlink_same_segment_far_call_optimized": (
                linked[21:26] == bytes.fromhex("90 0e e8 04 f9")
            ),
        }

    stable = (
        "patched_wrapper_sha256",
        "standalone_link_relevant_omf_sha256",
        "standalone_code_sha256",
        "standalone_fixup_sites",
        "standalone_masked_difference_offsets",
        "group_link_relevant_omf_sha256",
        "group_code_sha256",
        "linked_exe_sha256",
        "linked_map_sha256",
        "linked_program_sha256",
        "linked_function_sha256",
        "linked_producer_sha256",
        "raw_function_difference_count",
        "raw_producer_difference_count",
        "ordered_relocations",
        "map_contribution",
        "tlink_same_segment_far_call_optimized",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable):
        raise RuntimeError("independent OP game_init_op cold rounds differ")
    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained game_init_op source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "source_sha256": source_hashes,
        "boundary": bound,
        "producer": {
            "segment": "SHARED",
            "payload_offset": hex(START),
            "size": PRODUCER_SIZE,
            "function_size": SIZE,
            "padding_size": PRODUCER_SIZE - SIZE,
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "limit": (
            "Decoded 129-byte game_init_op only; the 130th owner byte is "
            "source/linker padding. No packed-file or whole-OP exactness."
        ),
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
