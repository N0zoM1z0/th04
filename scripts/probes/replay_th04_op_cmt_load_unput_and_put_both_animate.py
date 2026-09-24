#!/usr/bin/env python3
"""Cold-compile maintained OP cmt_load_unput_and_put_both_animate and relink OP_MUSIC_TEXT."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from inspect_dialog_fixup_order import omf_index  # noqa: E402
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_score_hiscore_boundaries import branch_edges, disassemble  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
RELOCATIONS = 804
SOURCE = ROOT / "src/op/music/cmt_load_unput_and_put_both_animate.cpp"
BODY = ROOT / "src/op/music/cmt_load_unput_and_put_both_animate.inl"
START = 0xC36F
SIZE = 0x48
NEXT = START + SIZE
PRODUCER_START = 0xBED5
PRODUCER_SIZE = 0x6A5
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "b1096abaffaa3a96347a93b6be062d72be094d7488668fe0234daf320765434b"
TARGET_PRODUCER_SHA = "53495c80ca106bc0cde9b8b37c8060cdacb80732a810b8fa8ad3ea3eac57ef09"
BASE_MUSIC_SOURCE_SHA = "a8ded4e33e974dccb35e8ac84d5e974e0c4b574ceace5adc4a07912e90f127cc"
BASE_MUSIC_OBJECT_SHA = "57f9c5d7ea06570eda6f5df3d936cadd20fb1d1bcf5553eb91724a4686f2697d"
BASE_MUSIC_CODE_SHA = "83a4d168eb1e4846a64d92dd423d2ea64d371223ce156fed54588ab03d7b2c46"


def sha(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def loose_segment_bytes(path: Path, segment_name: str) -> bytes:
    records = parse_omf(path.read_bytes())
    names = [""]
    segments: list[str] = []
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                length = record.data[pos]
                names.append(record.data[pos + 1:pos + 1 + length].decode("latin-1"))
                pos += length + 1
        elif record.record_type == 0x98:
            data = record.data
            pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            name_index, _ = omf_index(data, pos)
            segments.append(names[name_index])
    if segments.count(segment_name) != 1:
        raise RuntimeError(f"expected one {segment_name}: {segments}")
    wanted = segments.index(segment_name) + 1
    chunks: list[tuple[int, bytes]] = []
    for record in records:
        if record.record_type != 0xA0:
            continue
        index, pos = omf_index(record.data, 0)
        if index == wanted:
            offset = int.from_bytes(record.data[pos:pos + 2], "little")
            chunks.append((offset, record.data[pos + 2:]))
    chunks.sort()
    out = bytearray()
    for offset, payload in chunks:
        if offset != len(out):
            raise RuntimeError(f"{segment_name} LEDATA gap/overlap at {offset:#x}")
        out += payload
    return bytes(out)


def tcc_op(work: Path, output: Path, label: str, source: str) -> None:
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-", "-3",
         "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/", source],
        work, output / f"compile-{label}.log",
    )


def target_boundary(body: bytes, map_text: str, target_program: bytes) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP cmt_load_unput_and_put_both_animate target identity drift")

    import csv
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream)
                if int(row["entry_linear"], 0) == 0x10000 + START]
    if len(rows) != 1:
        raise RuntimeError("OP cmt wrapper Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x1C2F
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + NEXT - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 7
    ):
        raise RuntimeError(f"OP cmt wrapper Ghidra extent drift: {row!r}")

    # Target control flow: optional unput, load, redundant B-plane put +
    # background restore, then either fade in or first-show put/flip/put,
    # followed by the final redundant B-plane put.
    if (
        body[:8] != bytes.fromhex("55 8b ec 80 3e 7e 3a 00")
        or body[8:10] != bytes.fromhex("74 03")
        or body[10] != 0xE8
        or START + 13 + int.from_bytes(body[11:13], "little", signed=True) != 0xC33F
        or body[13:16] != bytes.fromhex("ff 76 04")
        or body[16] != 0xE8
        or START + 19 + int.from_bytes(body[17:19], "little", signed=True) != 0xC27B
        or body[19] != 0xE8
        or START + 22 + int.from_bytes(body[20:22], "little", signed=True) != 0xBFA7
        or body[22:34] != bytes.fromhex("66 68 40 00 40 01 66 68 40 01 40 01")
        or body[34] != 0x9A
        or int.from_bytes(body[35:37], "little") != 0x0AE8
        or int.from_bytes(body[37:39], "little") != 0x0DA1
        or body[39:46] != bytes.fromhex("80 3e 7e 3a 00 74 05")
        or body[46] != 0xE8
        or START + 49 + int.from_bytes(body[47:49], "little", signed=True) != 0xC30E
        or body[49:51] != bytes.fromhex("eb 0e")
        or body[51:56] != bytes.fromhex("c6 06 7e 3a 01")
        or body[56] != 0xE8
        or START + 59 + int.from_bytes(body[57:59], "little", signed=True) != 0xC2C4
        or body[59] != 0xE8
        or START + 62 + int.from_bytes(body[60:62], "little", signed=True) != 0xC244
        or body[62] != 0xE8
        or START + 65 + int.from_bytes(body[63:65], "little", signed=True) != 0xC2C4
        or body[65] != 0xE8
        or START + 68 + int.from_bytes(body[66:68], "little", signed=True) != 0xBFA7
        or body[68:] != bytes.fromhex("5d c2 02 00")
    ):
        raise RuntimeError("OP cmt wrapper instruction/operand topology drift")

    required = (
        "0F34:3A7E idle  _cmt_shown_initial",
        "0A74:1BFF idle  cmt_unput_both_animate()",
        "0A74:1B3B idle  cmt_load(int)",
        "0A74:1867 idle  nopoly_b_put()",
        "0DA1:0AE8       BGIMAGE_PUT_RECT_16",
        "0A74:1BCE idle  cmt_fadein_both_animate()",
        "0A74:1B84 idle  cmt_put()",
        "0A74:1B04 idle  music_update_render_and_flip()",
        "0A74:1C2F idle  cmt_load_unput_and_put_both_anim(int)",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP cmt wrapper MAP target drift")

    return {
        "segment_identity": "1A74",
        "segment_offset": "1C2F",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 7,
        "shown_flag": "0F34:3A7E _cmt_shown_initial",
        "bgimage_rect": [320, 64, 320, 320],
        "calls": [
            "0xC33F cmt_unput_both_animate",
            "0xC27B cmt_load",
            "0xBFA7 nopoly_b_put",
            "0DA1:0AE8 BGIMAGE_PUT_RECT_16",
            "0xC30E cmt_fadein_both_animate",
            "0xC2C4 cmt_put",
            "0xC244 music_update_render_and_flip",
        ],
        "terminal": "RET 2",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th02/op/m_music.cpp"
    if sha_file(upstream) != BASE_MUSIC_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP music source drift")

    dst = work / "src/op/music"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)

    data = upstream.read_bytes()
    start_marker = b"void pascal near cmt_load_unput_and_put_both_animate(int track)\n"
    end_marker = b"\n#else\nvoid near cmt_bg_free(void)\n"
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise RuntimeError("cmt wrapper source anchors drift")
    start = data.index(start_marker)
    end = data.index(end_marker, start)
    replacement = b'#include "src/op/music/cmt_load_unput_and_put_both_animate.inl"'
    upstream.write_bytes(data[:start] + replacement + data[end:])
    return sha_file(upstream)


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
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th02/op/m_music.cpp", BASE_MUSIC_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_music.obj", BASE_MUSIC_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        "src/op/music/cmt_load_unput_and_put_both_animate.cpp": sha_file(SOURCE),
        "src/op/music/cmt_load_unput_and_put_both_animate.inl": sha_file(BODY),
    }
    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target restore")
    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    boundary = target_boundary(body, map_text, target.program_image)
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target OP_MUSIC_TEXT identity drift")
    if baseline.program_image[START:NEXT] != body or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 OP music producer differs from target")
    if "0A74:1C2F idle  cmt_load_unput_and_put_both_anim(int)" not in map_text:
        raise RuntimeError("v489 cmt wrapper MAP public drift")

    base_object = SNAPSHOT / "obj/th04/op_music.obj"
    base_code = segment_bytes(base_object, "OP_MUSIC_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_MUSIC_CODE_SHA:
        raise RuntimeError("pinned OP_MUSIC_TEXT object contribution drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        dst = work / "src/op/music"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, dst / SOURCE.name)
        shutil.copy2(BODY, dst / BODY.name)

        before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"v622-cmt-wrapper-standalone-{label}",
               "src/op/music/cmt_load_unput_and_put_both_animate.cpp")
        standalone = [path for path in (work / "obj/th04").glob("*.obj")
                      if path.name not in before]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_MUSIC_TEXT")
        local_fixups = [
            item
            for record in parse_omf(local_obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]
        target_as_unlinked = bytes.fromhex(
            "55 8b ec 80 3e 00 00 00 74 03 e8 00 00 ff 76 04 "
            "e8 00 00 e8 00 00 66 68 40 00 40 01 66 68 40 01 40 01 "
            "9a 00 00 00 00 80 3e 00 00 00 74 05 e8 00 00 eb 0e "
            "c6 06 00 00 01 e8 00 00 e8 00 00 e8 00 00 e8 00 00 "
            "5d c2 02 00"
        )
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != target_as_unlinked
            or local_fixups != [(1, 66), (1, 63), (1, 60), (1, 57), (1, 53), (1, 47), (1, 41), (3, 35), (1, 20), (1, 17), (1, 11), (1, 5)]
        ):
            raise RuntimeError(f"{label}: standalone cmt wrapper OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/op_music.obj"
        group_obj.unlink()
        tcc_op(work, output, f"v622-cmt-wrapper-group-{label}", "th04/op_music.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_MUSIC_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained cmt wrapper changed grouped OP_MUSIC_TEXT")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked_body = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked_body != body
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked OP cmt wrapper/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "standalone_object_sha256": sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": sha(local_code),
            "standalone_fixup_sites": [list(item) for item in local_fixups],
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
            "ordered_relocations": len(target_sites),
        }

    stable_keys = (
        "standalone_link_relevant_omf_sha256", "standalone_code_sha256",
        "standalone_fixup_sites", "group_link_relevant_omf_sha256", "group_code_sha256",
        "linked_exe_sha256", "linked_map_sha256", "linked_program_sha256",
        "linked_function_sha256", "linked_producer_sha256",
        "raw_function_difference_count", "raw_producer_difference_count",
        "ordered_relocations",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable_keys):
        raise RuntimeError("independent OP cmt wrapper cold rounds differ")
    for rel, digest in source_hashes.items():
        if sha_file(ROOT / rel) != digest:
            raise RuntimeError(f"maintained cmt wrapper source changed during replay: {rel}")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed cmt_load_unput_and_put_both_animate maintained-source cold-link replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "baseline_map_sha256": BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "OP_MUSIC_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "cold_determinism": {
            "link_relevant_omf_code_exe_map_program_and_relocations_equal": True,
        },
        "limit": "Decoded 72-byte function only; v489 remains surrounding build scaffold. No packed-file or whole-OP exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "function_sha256": builds["a"]["linked_function_sha256"],
        "producer_sha256": builds["a"]["linked_producer_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
