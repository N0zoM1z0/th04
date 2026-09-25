#!/usr/bin/env python3
"""Cold-replay maintained natural C++ for MAINE sub_BB81 + verdict_animate."""

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

BB_SOURCE = ROOT / "src/maine/end/sub_BB81.inl"
ANIM_SOURCE = ROOT / "src/maine/end/verdict_animate.inl"

BB_START = 0xBB81
BB_SIZE = 0x560
BB_NEXT = BB_START + BB_SIZE
BB_SHA = "ff93cd8c668d62c9f47f6b44549cfcfbfb96c4d4dff9485d5a4145f4229b48b4"

AUX_START = BB_NEXT
AUX_SIZE = 0x17
AUX_NEXT = AUX_START + AUX_SIZE
AUX_SHA = "91bb16d2778765ba933c8025285a6a1398426341379975b9de9d914bbe58bb96"

ANIM_START = 0xC0F8
ANIM_SIZE = 0x51
ANIM_NEXT = ANIM_START + ANIM_SIZE
ANIM_SHA = "3073045c3b95f8d1000a127cfefd7e5444af9a825618a0a4443f6debba7ae17b"

PRODUCER_START = BB_START
PRODUCER_SIZE = 0x5C8
PRODUCER_SHA = "6c4abcf2cf53fdd2e4132233917546de9ff3423b460ca3f392bd8941085c531e"

BASE_SOURCE_SHA = "eb6fcbcba3296fe3a1d57abe8fae88eb90fae6f0b16aab2813d42425ebe8f3ea"
BASE_OBJECT_SHA = "344d1bd0ed254e75d7434fa3f2445d25e28af0cb6451e8a0c3eea79c33e191a3"
BASE_CODE_SHA = "2d0522052c27bd5c67ae201f2cbd0e16238aa536308e83ac0167ce8ca5b86c90"


def sha(data: bytes) -> str:
    return prior.sha(data)


def ghidra_rows() -> tuple[dict[str, str], dict[str, str]]:
    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    bb = [r for r in rows if int(r["entry_linear"], 0) == 0x10000 + BB_START]
    anim = [r for r in rows if int(r["entry_linear"], 0) == 0x10000 + ANIM_START]
    if len(bb) != 1 or len(anim) != 1:
        raise RuntimeError("MAINE verdict Ghidra entry count drift")
    return bb[0], anim[0]


def validate_target(
    bb_body: bytes, aux: bytes, anim_body: bytes, map_text: str
) -> dict[str, object]:
    if len(bb_body) != BB_SIZE or sha(bb_body) != BB_SHA:
        raise RuntimeError("MAINE sub_BB81 target identity drift")
    if len(aux) != AUX_SIZE or sha(aux) != AUX_SHA:
        raise RuntimeError("MAINE sub_BB81 auxiliary identity drift")
    if len(anim_body) != ANIM_SIZE or sha(anim_body) != ANIM_SHA:
        raise RuntimeError("MAINE verdict_animate target identity drift")

    bb, anim = ghidra_rows()
    if (
        int(bb["entry_segment"], 0) != 0x1A05
        or int(bb["entry_offset"], 0) != 0x1B31
        or int(bb["body_addresses"]) != 0x605
        or int(bb["body_span"]) != 0xA9CE
        or bb["contiguous"] != "false"
        or bb["body_range_count"] != "7"
        or int(bb["caller_count"]) != 1
        or int(bb["callee_count"]) != 22
    ):
        raise RuntimeError(f"MAINE sub_BB81 Ghidra auto-body drift: {bb!r}")
    if (
        int(anim["entry_segment"], 0) != 0x1A05
        or int(anim["entry_offset"], 0) != 0x20A8
        or int(anim["body_min_linear"], 0) != 0x10000 + ANIM_START
        or int(anim["body_max_linear"], 0) != 0x10000 + ANIM_NEXT - 1
        or int(anim["body_addresses"]) != ANIM_SIZE
        or int(anim["body_span"]) != ANIM_SIZE
        or anim["contiguous"] != "true"
        or anim["body_range_count"] != "1"
        or int(anim["caller_count"]) != 1
        or int(anim["callee_count"]) != 8
    ):
        raise RuntimeError(f"MAINE verdict_animate Ghidra extent drift: {anim!r}")

    required = (
        "0A05:1B31 05C8 C=CODE   S=MAINE_01_TEXT  G=GROUP_01 M=th04/vb.cpp",
        "0A05:1B31 idle  sub_bb81()",
        "0A05:20A8       verdict_animate()",
        "0A05:20F9 idle  scoredat_decode()",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE verdict MAP evidence drift")
    if not bb_body.startswith(bytes.fromhex("c8 04 00 00 56")):
        raise RuntimeError("MAINE sub_BB81 prologue drift")
    if bb_body[-3:] != bytes.fromhex("5e c9 c3"):
        raise RuntimeError("MAINE sub_BB81 epilogue drift")
    if not anim_body.startswith(bytes.fromhex("55 8b ec")) or anim_body[-3:] != bytes.fromhex("fa 5d c3"):
        raise RuntimeError("MAINE verdict_animate body shape drift")

    return {
        "sub_BB81": {
            "segment_identity": "1A05",
            "segment_offset": "1B31",
            "payload_offset": hex(BB_START),
            "reviewed_body_size": BB_SIZE,
            "target_sha256": sha(bb_body),
            "ghidra_auto_body_addresses": int(bb["body_addresses"]),
            "ghidra_auto_body_span": int(bb["body_span"]),
            "ghidra_auto_range_count": int(bb["body_range_count"]),
            "terminal": "pop si; leave; ret",
        },
        "verdict_animate": {
            "segment_identity": "1A05",
            "segment_offset": "20A8",
            "payload_offset": hex(ANIM_START),
            "reviewed_body_size": ANIM_SIZE,
            "target_sha256": sha(anim_body),
            "caller_count": 1,
            "callee_count": 8,
            "terminal": "pop bp; ret",
        },
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/vb.cpp"
    if prior.sha_file(upstream) != BASE_SOURCE_SHA:
        raise RuntimeError("pinned v489 vb.cpp drift")
    shutil.copytree(ROOT / "src/maine/end", work / "src/maine/end", dirs_exist_ok=True)

    data = upstream.read_bytes()

    anim_start_anchor = b"void near verdict_animate(void)\n"
    anim_end_anchor = b"\n#pragma codeseg\n"
    if data.count(anim_start_anchor) != 1:
        raise RuntimeError("verdict_animate replacement start drift")
    anim_start = data.index(anim_start_anchor)
    anim_end = data.index(anim_end_anchor, anim_start)
    data = (
        data[:anim_start]
        + b'#include "src/maine/end/verdict_animate.inl"'
        + data[anim_end:]
    )

    bb_start_anchor = b"void near sub_BB81(void)\n"
    bb_end_anchor = b'\n#pragma codeseg\n\n#include "th02/formats/pi.h"'
    if data.count(bb_start_anchor) != 1 or data.count(bb_end_anchor) != 1:
        raise RuntimeError("sub_BB81 replacement anchors drift")
    bb_start = data.index(bb_start_anchor)
    bb_end = data.index(bb_end_anchor, bb_start)
    data = (
        data[:bb_start]
        + b'#include "src/maine/end/sub_BB81.inl"'
        + data[bb_end:]
    )

    upstream.write_bytes(data)
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
        (prior.SNAPSHOT / "th04/vb.cpp", BASE_SOURCE_SHA),
        (prior.SNAPSHOT / "obj/th04/vb.obj", BASE_OBJECT_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    closure = source_closure(
        ROOT,
        ("src/maine/end/sub_BB81.inl", "src/maine/end/verdict_animate.inl"),
    )
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}

    target = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")

    bb_body = target.program_image[BB_START:BB_NEXT]
    aux = target.program_image[AUX_START:AUX_NEXT]
    anim_body = target.program_image[ANIM_START:ANIM_NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    boundary = validate_target(bb_body, aux, anim_body, map_text)

    if sha(producer) != PRODUCER_SHA:
        raise RuntimeError("MAINE vb target producer identity drift")
    if baseline.program_image[BB_START:BB_NEXT] != bb_body:
        raise RuntimeError("v489 sub_BB81 bytes differ from target")
    if baseline.program_image[AUX_START:AUX_NEXT] != aux:
        raise RuntimeError("v489 BB81 auxiliary bytes differ from target")
    if baseline.program_image[ANIM_START:ANIM_NEXT] != anim_body:
        raise RuntimeError("v489 verdict_animate bytes differ from target")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 vb producer differs from target")

    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 ordered relocations differ from target")

    base_obj = prior.SNAPSHOT / "obj/th04/vb.obj"
    base_omf = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "MAINE_01_TEXT")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_CODE_SHA
    ):
        raise RuntimeError("pinned v489 vb object drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        patched_source_sha = overlay_source(work)

        obj = work / "obj/th04/vb.obj"
        obj.unlink()
        tcc(work, output, f"v717-verdict-owner-{label}", "th04/vb.cpp")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "MAINE_01_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained verdict source changed vb MAINE_01_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked_bb = image.program_image[BB_START:BB_NEXT]
        linked_aux = image.program_image[AUX_START:AUX_NEXT]
        linked_anim = image.program_image[ANIM_START:ANIM_NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or prior.sha_file(exe) != prior.BASE_EXE_SHA
            or prior.sha_file(mp) != prior.BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked_bb != bb_body
            or linked_aux != aux
            or linked_anim != anim_body
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: cold MAINE verdict owner link/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_vb_source_sha256": patched_source_sha,
            "group_omf_sha256": prior.sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_sub_BB81_sha256": sha(linked_bb),
            "linked_aux_sha256": sha(linked_aux),
            "linked_verdict_animate_sha256": sha(linked_anim),
            "linked_producer_sha256": sha(linked_producer),
            "raw_sub_BB81_difference_count": 0,
            "raw_aux_difference_count": 0,
            "raw_verdict_animate_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable = lambda d: {k: v for k, v in d.items() if k != "group_omf_sha256"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent verdict-owner cold rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained verdict source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE sub_BB81 + verdict_animate maintained natural-C++ cold replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": prior.sha_file(Path(__file__).resolve()),
        "boundaries": boundary,
        "sub_BB81_auxiliary_switch_tables": {
            "payload_offset": hex(AUX_START),
            "size": AUX_SIZE,
            "target_sha256": sha(aux),
            "raw_target_difference_count": 0,
        },
        "producer": {
            "segment": "MAINE_01_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "limit": (
            "Decoded 0x560-byte sub_BB81 body, adjacent 0x17-byte compiler switch-table extent, "
            "and 0x51-byte verdict_animate body inside the 0x5C8 vb.cpp producer. "
            "No packed-file or whole-MAINE exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": prior.sha_file(path),
        "sub_BB81_sha256": BB_SHA,
        "aux_sha256": AUX_SHA,
        "verdict_animate_sha256": ANIM_SHA,
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
