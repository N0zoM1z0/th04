#!/usr/bin/env python3
"""Cold-compile maintained OP menu_sel_update_and_render and relink OP_MAIN_TEXT."""

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
from replay_th04_op_help_put import tcc_op, loose_segment_bytes
from replay_th04_scroll_driver_natural import fixup_locations
from replay_th04_shared_delay_measure import link_relevant_omf_sha
from replay_th04_zun_source_only import source_closure

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/op/main/menu_sel_update.cpp"
BODY = ROOT / "src/op/main/menu_sel_update.inl"

TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
BASE_M_MAIN_SOURCE_SHA = "ee74c5c1d0a2328630c8f8453cf864a49640a0d59ca9b181ae11cef0400cb233"
BASE_OP_MAIN_SOURCE_SHA = "5cf36e94fc4d72672edd5a225f73d4ac3ae9c551f67dfd249715c8c7a7484efd"
BASE_OBJECT_SHA = "6706f32fba2b8753716a66d22a2cc64539d5e96051e0ba2dbca8405b22687481"
BASE_LINK_OMF_SHA = "92d7bff8542364834b9f9f3b3d4eb74b582fa2209b5906e103325ca1b5a8b4a0"
BASE_CODE_SHA = "926ac58cb1ac3225d93ac70122377ee8ae10a35cee069aa9e5da9b76ce4b41b7"
RELOCATIONS = 804

START = 0xAE28
SIZE = 0x6E
NEXT = START + SIZE
PRODUCER_START = 0xA74C
PRODUCER_SIZE = 0xD53
TARGET_FUNCTION_SHA = "20166ad36ad2ecda3b47fa3d9883e7f2d1def5468bae4e7a0273e239ffc58d03"
TARGET_PRODUCER_SHA = "02ba00a11483ba325fc88687232ee277e8525047372a9d0c722c92cb4ffb1659"
STANDALONE_CODE_SHA = "528ba3613baa4e77ac05d2e80b02bf54c5348962821711a6c7cabe17720d1c4f"
STANDALONE_FIXUPS = [
    (3, 102), (3, 97), (3, 90), (1, 87), (1, 79), (1, 76),
    (1, 66), (1, 56), (1, 50), (1, 45), (1, 36), (1, 33),
    (1, 22), (1, 19), (1, 12), (1, 4),
]


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
        r"\bS=OP_MAIN_TEXT\b.*\bM=th04/op_main\.cpp(?:\s|$)",
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
        raise RuntimeError(f"expected one OP_MAIN_TEXT contribution: {matches}")
    return matches[0]


def target_boundary(body: bytes, target_program: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP menu_sel_update_and_render target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP menu_sel_update_and_render Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x06E8
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 2
        or int(row["callee_count"]) != 3
    ):
        raise RuntimeError(f"OP menu_sel_update_and_render Ghidra extent drift: {row!r}")

    if (
        body[:14] != bytes.fromhex("55 8b ec a0 9b 00 98 50 6a 01 ff 16 6a 1a")
        or body[17:24] != bytes.fromhex("00 06 9b 00 a0 9b 00")
        or body[32:38] != bytes.fromhex("a2 9b 00 a0 9b 00")
        or body[43:53] != bytes.fromhex("c6 06 9b 00 00 80 3e 46 3f 00")
        or body[55:62] != bytes.fromhex("a0 9b 00 98 3d 01 00")
        or body[64:69] != bytes.fromhex("80 3e 68 1a 00")
        or body[74:81] != bytes.fromhex("00 06 9b 00 a0 9b 00")
        or body[85:89] != bytes.fromhex("ff 16 6a 1a")
        or body[89:94] != bytes.fromhex("9a d6 08 a1 0d")
        or body[94:101] != bytes.fromhex("6a 01 9a e2 08 a1 0d")
        or body[101:106] != bytes.fromhex("9a 1c 09 a1 0d")
        or body[-3:] != bytes.fromhex("c2 04 00")
    ):
        raise RuntimeError("OP menu_sel_update_and_render instruction/operand topology drift")

    required = (
        "0A74:06E8 idle  menu_sel_update_and_render(char,char)",
        "0F34:009B idle  _menu_sel",
        "0F34:1A6A idle  _menu_unput_and_put",
        "0F34:3F46       _extra_unlocked",
        "0F34:1A68 idle  _in_option",
        "0DA1:08D6       _snd_se_reset",
        "0DA1:08E2       SND_SE_PLAY",
        "0DA1:091C       _snd_se_update",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP menu_sel_update_and_render MAP target drift")
    return {
        "segment_identity": "1A74",
        "segment_offset": "06E8",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 2,
        "callee_count": 3,
        "menu_sel": "0F34:009B",
        "menu_unput_and_put": "0F34:1A6A near Pascal function pointer",
        "extra_unlocked": "0F34:3F46",
        "in_option": "0F34:1A68",
        "locked_choice": 1,
        "colors": {"inactive": 1, "active": 8},
        "sound_force_sequence": ["_snd_se_reset", "SND_SE_PLAY(1)", "_snd_se_update"],
        "terminal": "RET 4",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/op/m_main.cpp"
    if sha_file(upstream) != BASE_M_MAIN_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP m_main source drift")
    dst = work / "src/op/main"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)
    data = upstream.read_bytes()
    start_marker = b"void pascal near menu_sel_update_and_render(int8_t max, int8_t direction)\n"
    end_marker = b"\n\n#define menu_init("
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise RuntimeError("menu_sel_update_and_render replacement anchors drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start)
    upstream.write_bytes(
        data[:start] + b'#include "src/op/main/menu_sel_update.inl"' + data[end:]
    )
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
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/op/m_main.cpp", BASE_M_MAIN_SOURCE_SHA),
        (SNAPSHOT / "th04/op_main.cpp", BASE_OP_MAIN_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_main.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    base_obj = SNAPSHOT / "obj/th04/op_main.obj"
    base_code = segment_bytes(base_obj, "OP_MAIN_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_CODE_SHA:
        raise RuntimeError("baseline OP_MAIN_TEXT object contribution drift")
    if link_relevant_omf_sha(base_obj) != BASE_LINK_OMF_SHA:
        raise RuntimeError("baseline op_main.obj link-relevant OMF drift")

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid OP target/baseline")
    sites = [x.linear for x in target.relocations]
    if [x.linear for x in baseline.relocations] != sites:
        raise RuntimeError("OP baseline relocation order drift")

    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target OP_MAIN_TEXT producer identity drift")
    if (
        baseline.program_image[START:NEXT] != body
        or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer
    ):
        raise RuntimeError("v489 OP_MAIN_TEXT differs from target")
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    bound = target_boundary(body, target.program_image, map_text)
    mstart, msize, mline = map_contribution(SNAPSHOT / "obj/th04/op.map")
    if (mstart, msize) != (PRODUCER_START, PRODUCER_SIZE):
        raise RuntimeError(f"baseline OP_MAIN_TEXT MAP contribution drift: {mline}")

    closure = source_closure(ROOT, ("src/op/main/menu_sel_update.cpp",))
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
        tcc_op(work, output, f"menu-sel-update-standalone-{label}",
               "src/op/main/menu_sel_update.cpp")
        standalone = [
            p for p in (work / "obj/th04").glob("*.obj")
            if p.name not in before
        ]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_desc = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_MAIN_TEXT")
        local_fixups = object_fixups(local_obj)
        masked_target = bytearray(body)
        for kind, off in STANDALONE_FIXUPS:
            width = 2 if kind == 1 else 4
            masked_target[off:off + width] = b"\0" * width
        if (
            not local_desc["valid"]
            or "TC86 Borland C++ 4.02" not in local_desc["translator_comments"]
            or len(local_code) != SIZE
            or sha(local_code) != STANDALONE_CODE_SHA
            or local_fixups != STANDALONE_FIXUPS
            or local_code != bytes(masked_target)
        ):
            raise RuntimeError(f"{label}: standalone menu_sel_update_and_render codegen drift")

        patched_m_main_sha = overlay_source(work)
        op_main = work / "th04/op_main.cpp"
        if sha_file(op_main) != BASE_OP_MAIN_SOURCE_SHA:
            raise RuntimeError(f"{label}: pinned op_main.cpp drift")
        group_obj = work / "obj/th04/op_main.obj"
        group_obj.unlink()
        tcc_op(work, output, f"menu-sel-update-group-{label}", "th04/op_main.cpp")
        group_desc = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_MAIN_TEXT")
        if (
            not group_desc["valid"]
            or "TC86 Borland C++ 4.02" not in group_desc["translator_comments"]
            or group_code != base_code
            or link_relevant_omf_sha(group_obj) != BASE_LINK_OMF_SHA
        ):
            raise RuntimeError(f"{label}: grouped op_main.obj drift")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked_body = image.program_image[START:NEXT]
        linked_producer = image.program_image[
            PRODUCER_START:PRODUCER_START + PRODUCER_SIZE
        ]
        map_start, map_size, map_line = map_contribution(mp)
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [x.linear for x in image.relocations] != sites
            or image.program_image != baseline.program_image
            or linked_body != body
            or linked_producer != producer
            or (map_start, map_size) != (PRODUCER_START, PRODUCER_SIZE)
        ):
            raise RuntimeError(f"{label}: linked OP menu_sel_update_and_render/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_m_main_source_sha256": patched_m_main_sha,
            "standalone_object_sha256": sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": sha(local_code),
            "standalone_fixup_sites": [list(x) for x in local_fixups],
            "group_object_sha256": sha_file(group_obj),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": sha(group_code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_function_sha256": sha(linked_body),
            "linked_producer_sha256": sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(sites),
            "map_contribution": map_line,
        }

    stable = (
        "patched_m_main_source_sha256",
        "standalone_link_relevant_omf_sha256",
        "standalone_code_sha256",
        "standalone_fixup_sites",
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
    )
    if any(builds["a"][k] != builds["b"][k] for k in stable):
        raise RuntimeError("independent OP menu_sel_update_and_render cold rounds differ")
    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained menu_sel_update_and_render source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "source_sha256": source_hashes,
        "boundary": bound,
        "producer": {
            "segment": "OP_MAIN_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "limit": (
            "Decoded 93-byte menu_sel_update_and_render only; full OP_MAIN_TEXT is verified as "
            "its containing producer. No packed-file or whole-OP exactness."
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
