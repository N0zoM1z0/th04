#!/usr/bin/env python3
"""Cold-compile maintained OP nopoly_B_free and relink OP_MUSIC_TEXT."""

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
SOURCE = ROOT / "src/op/music/nopoly_free.cpp"
BODY = ROOT / "src/op/music/nopoly_free.inl"
START = 0xBF99
SIZE = 0x0E
NEXT = START + SIZE
PRODUCER_START = 0xBED5
PRODUCER_SIZE = 0x6A5
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "dad94b2175fdd498a78ad17f20262bb52772c6d0779f82f92c0f3e7a96b66133"
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


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("OP nopoly_B_free target identity drift")
    nd = shutil.which("ndisasm")
    if nd is None:
        raise RuntimeError("ndisasm unavailable")
    rows = disassemble(nd, body, START)
    if (
        [str(row["mnemonic"]) for row in rows] != ["push", "mov", "push", "call", "pop", "ret"]
        or int(rows[0]["address"]) != START
        or int(rows[-1]["address"]) + int(rows[-1]["size"]) != NEXT
        or any(int(a["address"]) + int(a["size"]) != int(b["address"])
               for a, b in zip(rows, rows[1:]))
        or branch_edges(rows)
    ):
        raise RuntimeError(f"OP nopoly_B_free decode drift: {rows!r}")
    if (
        body[3:5] != b"\xff\x36"
        or int.from_bytes(body[5:7], "little") != 0x3A80
        or body[7] != 0x9A
        or int.from_bytes(body[8:10], "little") != 0x2856
        or int.from_bytes(body[10:12], "little") != 0
    ):
        raise RuntimeError("OP nopoly_B_free target operands drift")
    if (
        "0F34:3A80 idle  _nopoly_B" not in map_text
        or "0000:2856       HMEM_FREE" not in map_text
    ):
        raise RuntimeError("candidate map no longer corroborates nopoly_B/HMEM_FREE")
    return {
        "segment_identity": "1A74",
        "segment_offset": "1859",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "instruction_count": len(rows),
        "terminal": str(rows[-1]["text"]),
        "data_map_target": "0F34:3A80 _nopoly_B",
        "far_call_map_target": "0000:2856 HMEM_FREE",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th02/op/m_music.cpp"
    if sha_file(upstream) != BASE_MUSIC_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP music source drift")
    dst = work / "src/op/music"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)
    data = upstream.read_bytes()
    old = (
        b"void near nopoly_B_free(void)\n"
        b"{\n"
        b"\tHMem<dots8_t>::free(nopoly_B);\n"
        b"}"
    )
    replacement = b'#include "src/op/music/nopoly_free.inl"'
    if data.count(old) != 1:
        raise RuntimeError("nopoly_B_free replacement anchor drift")
    upstream.write_bytes(data.replace(old, replacement, 1))
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
        "src/op/music/nopoly_free.cpp": sha_file(SOURCE),
        "src/op/music/nopoly_free.inl": sha_file(BODY),
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
    boundary = target_boundary(body, map_text)
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target OP_MUSIC_TEXT identity drift")
    if baseline.program_image[START:NEXT] != body or baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 OP music producer differs from target")
    if "0A74:1859 idle  nopoly_b_free()" not in map_text:
        raise RuntimeError("v489 nopoly_B_free MAP public drift")

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
        tcc_op(work, output, f"v584-nopoly-free-standalone-{label}",
               "src/op/music/nopoly_free.cpp")
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
        target_as_unlinked = body[:5] + b"\0\0" + body[7:8] + b"\0\0\0\0" + body[12:]
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != target_as_unlinked
            or local_fixups != [(3, 8), (1, 5)]
        ):
            raise RuntimeError(f"{label}: standalone nopoly_B_free OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/op_music.obj"
        group_obj.unlink()
        tcc_op(work, output, f"v584-nopoly-free-group-{label}", "th04/op_music.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_MUSIC_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained nopoly_B_free changed grouped OP_MUSIC_TEXT")

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
            raise RuntimeError(f"{label}: linked OP title layout/body drift")

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
        raise RuntimeError("independent OP nopoly_B_free cold rounds differ")
    if sha_file(SOURCE) != source_hashes["src/op/music/nopoly_free.cpp"] or sha_file(BODY) != source_hashes["src/op/music/nopoly_free.inl"]:
        raise RuntimeError("maintained nopoly_B_free source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed nopoly_B_free maintained-source cold-link replay",
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
        "limit": "Decoded 10-byte function only; v489 remains surrounding build scaffold. No packed-file or whole-OP exactness.",
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
