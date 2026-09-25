#!/usr/bin/env python3
"""Cold-replay only the maintained natural-C++ MAINE SCORE rectangle helper."""

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

REG_SOURCE = ROOT / "src/maine/score/regist_menu.inl"
EGC_SOURCE = ROOT / "src/maine/score/score_egc_start_copy.inl"
RECT_SOURCE = ROOT / "src/maine/score/score_rect_copy.inl"

REG_START = 0xC814
REG_SIZE = 0x39C
REG_NEXT = REG_START + REG_SIZE
REG_SHA = "7bef6c89de52462b75acb65a47dd919ce27eb38d5d920c082d73141e54cdad6b"

EGC_START = 0xCBB0
EGC_SIZE = 0x43
EGC_NEXT = EGC_START + EGC_SIZE
EGC_SHA = "a433967aff2092e185268abd34ea0c17d46b63c552db89e1a2dd191425930f85"

RECT_START = 0xCBF3
RECT_SIZE = 0x86
RECT_NEXT = RECT_START + RECT_SIZE
RECT_SHA = "86b8046d73b79655f913d1b7f62c34db3a3f6d43ffc168b9a4c855e78b7d7d2f"

PRODUCER_START = 0xC149
PRODUCER_SIZE = 0xB30
PRODUCER_SHA = "a7ccdd75806f46444a768186f6661ba31c69bd7bdb3163229428488860db24a0"

BASE_SCOREALL_SOURCE_SHA = "9082aff7bbc7a39ed84d05b124343ca110df4d3000d629df1ebe14f43ca1faff"
BASE_SCORE86_SOURCE_SHA = "db28104988abdf426e25f767f272f12db8c5c54299cc72c86a34e073cf2178d4"
BASE_OBJECT_SHA = "8bfa4a6da8584f005e565b1bcd18136250e48b233b5c443bbd42264c560cdf03"
BASE_CODE_SHA = "d8180ee4acb342cefe168337bb6dff4986b6bac625a4c614128c1b9430cec693"


def sha(data: bytes) -> str:
    return prior.sha(data)


def function_row(start: int) -> dict[str, str]:
    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = [r for r in csv.DictReader(stream)
                if int(r["entry_linear"], 0) == 0x10000 + start]
    if len(rows) != 1:
        raise RuntimeError(f"MAINE SCORE entry count drift at {start:#x}")
    return rows[0]


def validate_target(reg: bytes, egc: bytes, rect: bytes, map_text: str) -> dict[str, object]:
    for name, body, size, digest in (
        ("regist_menu", reg, REG_SIZE, REG_SHA),
        ("score_egc_start_copy", egc, EGC_SIZE, EGC_SHA),
        ("score_rect_copy", rect, RECT_SIZE, RECT_SHA),
    ):
        if len(body) != size or sha(body) != digest:
            raise RuntimeError(f"MAINE {name} target identity drift")

    rr = function_row(REG_START)
    er = function_row(EGC_START)
    cr = function_row(RECT_START)
    if (
        int(rr["entry_segment"], 0) != 0x1A05
        or int(rr["entry_offset"], 0) != 0x27C4
        or int(rr["body_addresses"]) != 0x4BA
        or int(rr["body_span"]) != 0xC392
        or rr["contiguous"] != "false"
        or rr["body_range_count"] != "5"
        or int(rr["caller_count"]) != 1
        or int(rr["callee_count"]) != 25
    ):
        raise RuntimeError(f"MAINE regist_menu Ghidra auto-body drift: {rr!r}")
    if (
        int(er["entry_segment"], 0) != 0x1A05
        or int(er["entry_offset"], 0) != 0x2B60
        or int(er["body_min_linear"], 0) != 0x10000 + EGC_START
        or int(er["body_max_linear"], 0) != 0x10000 + EGC_NEXT - 1
        or int(er["body_addresses"]) != EGC_SIZE
        or int(er["body_span"]) != EGC_SIZE
        or er["contiguous"] != "true"
        or er["body_range_count"] != "1"
    ):
        raise RuntimeError(f"MAINE score EGC-start Ghidra extent drift: {er!r}")
    if (
        int(cr["entry_segment"], 0) != 0x1A05
        or int(cr["entry_offset"], 0) != 0x2BA3
        or int(cr["body_min_linear"], 0) != 0x10000 + RECT_START
        or int(cr["body_max_linear"], 0) != 0x10000 + RECT_NEXT - 1
        or int(cr["body_addresses"]) != RECT_SIZE
        or int(cr["body_span"]) != RECT_SIZE
        or cr["contiguous"] != "true"
        or cr["body_range_count"] != "1"
    ):
        raise RuntimeError(f"MAINE score rect-copy Ghidra extent drift: {cr!r}")

    required = (
        "0A05:20F9 0B30 C=CODE   S=SCORE_TEXT     G=GROUP_01 M=th04/scoreall.cpp",
        "0A05:27C4       regist_menu()",
        "0A05:2B60 idle  score_egc_start_copy()",
        "0A05:2BA3 idle  score_rect_copy(int,int,int,int)",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("MAINE SCORE MAP evidence drift")

    listing = (ROOT / ".analysis/reconstruction/boundary-review/tasm/maine-th04_maine.lst").read_text(
        encoding="cp932", errors="replace"
    )
    for item in (
        "0462\t\t\t @regist_menu$qv proc near",
        "07FE\t\t\t @regist_menu$qv endp",
        "07FE\t\t\t _egc_start_copy_inlined proc near",
        "0841\t\t\t _egc_start_copy_inlined endp",
        "0841\t\t\t sub_CBF3\t proc near",
        "08C7\t\t\t sub_CBF3\t endp",
    ):
        if item not in listing:
            raise RuntimeError(f"MAINE SCORE TASM boundary marker drift: {item!r}")

    return {
        "regist_menu": {
            "payload_offset": hex(REG_START), "reviewed_body_size": REG_SIZE,
            "target_sha256": sha(reg), "ghidra_auto_body_addresses": int(rr["body_addresses"]),
            "ghidra_auto_body_span": int(rr["body_span"]), "ghidra_auto_range_count": int(rr["body_range_count"]),
        },
        "score_egc_start_copy": {
            "payload_offset": hex(EGC_START), "reviewed_body_size": EGC_SIZE,
            "target_sha256": sha(egc),
        },
        "score_rect_copy": {
            "payload_offset": hex(RECT_START), "reviewed_body_size": RECT_SIZE,
            "target_sha256": sha(rect),
        },
    }


def overlay_source(work: Path) -> str:
    scoreall = work / "th04/scoreall.cpp"
    score86 = work / "th04/score86.cpp"
    if prior.sha_file(scoreall) != BASE_SCOREALL_SOURCE_SHA:
        raise RuntimeError("pinned v489 scoreall.cpp drift")
    if prior.sha_file(score86) != BASE_SCORE86_SOURCE_SHA:
        raise RuntimeError("pinned v489 score86.cpp drift")

    dst = work / "src/maine/score"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RECT_SOURCE, dst / "score_rect_copy.inl")

    data = score86.read_bytes()
    rect_anchor = b"void pascal near score_rect_copy("
    if data.count(rect_anchor) != 2:
        raise RuntimeError("score_rect_copy declaration/definition count drift")
    rect_start = data.rindex(rect_anchor)
    data = data[:rect_start] + b'#include "src/maine/score/score_rect_copy.inl"\n'
    score86.write_bytes(data)
    return prior.sha_file(score86)


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
        (prior.SNAPSHOT / "th04/scoreall.cpp", BASE_SCOREALL_SOURCE_SHA),
        (prior.SNAPSHOT / "th04/score86.cpp", BASE_SCORE86_SOURCE_SHA),
        (prior.SNAPSHOT / "obj/th04/scoreall.obj", BASE_OBJECT_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    closure = source_closure(ROOT, ("src/maine/score/score_rect_copy.inl",))
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}

    target = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")

    reg = target.program_image[REG_START:REG_NEXT]
    egc = target.program_image[EGC_START:EGC_NEXT]
    rect = target.program_image[RECT_START:RECT_NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    boundaries = validate_target(reg, egc, rect, map_text)

    if sha(producer) != PRODUCER_SHA:
        raise RuntimeError("MAINE SCORE target producer identity drift")
    for start, stop, body, label in (
        (REG_START, REG_NEXT, reg, "regist_menu"),
        (EGC_START, EGC_NEXT, egc, "score_egc_start_copy"),
        (RECT_START, RECT_NEXT, rect, "score_rect_copy"),
        (PRODUCER_START, PRODUCER_START + PRODUCER_SIZE, producer, "SCORE producer"),
    ):
        if baseline.program_image[start:stop] != body:
            raise RuntimeError(f"v489 {label} differs from target")

    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 ordered relocations differ from target")

    base_obj = prior.SNAPSHOT / "obj/th04/scoreall.obj"
    base_omf = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "SCORE_TEXT")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_CODE_SHA
    ):
        raise RuntimeError("pinned v489 scoreall object drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        patched_source_sha = overlay_source(work)

        obj = work / "obj/th04/scoreall.obj"
        obj.unlink()
        tcc(work, output, f"v723-score-rect-natural-{label}", "th04/scoreall.cpp")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "SCORE_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained SCORE tail changed scoreall SCORE_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked_reg = image.program_image[REG_START:REG_NEXT]
        linked_egc = image.program_image[EGC_START:EGC_NEXT]
        linked_rect = image.program_image[RECT_START:RECT_NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or prior.sha_file(exe) != prior.BASE_EXE_SHA
            or prior.sha_file(mp) != prior.BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked_reg != reg
            or linked_egc != egc
            or linked_rect != rect
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: cold MAINE SCORE tail link/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_score86_source_sha256": patched_source_sha,
            "group_omf_sha256": prior.sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_regist_menu_sha256": sha(linked_reg),
            "linked_egc_start_sha256": sha(linked_egc),
            "linked_rect_copy_sha256": sha(linked_rect),
            "linked_producer_sha256": sha(linked_producer),
            "raw_regist_menu_difference_count": 0,
            "raw_egc_start_difference_count": 0,
            "raw_rect_copy_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable = lambda d: {k: v for k, v in d.items() if k != "group_omf_sha256"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent SCORE-tail cold rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained SCORE-tail source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE SCORE rectangle-copy maintained natural-C++ cold replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": prior.sha_file(Path(__file__).resolve()),
        "boundaries": boundaries,
        "producer": {
            "segment": "SCORE_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
            "raw_target_difference_count": 0,
        },
        "surrounding_scaffold": (
            "Pinned v489 regist_menu and EGC-start source are retained unchanged only as producer context. "
            "They use decomp.hpp compiler-shape helpers and receive no authored-source exactness credit here."
        ),
        "builds": builds,
        "limit": (
            "Exactness claim is limited to the maintained 0x86-byte score_rect_copy body. "
            "The complete 0xB30 SCORE_TEXT producer is checked only to prove placement/link stability. "
            "No exact claim is made for regist_menu or score_egc_start_copy, and no packed-file or whole-MAINE exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": prior.sha_file(path),
        "rect_copy_sha256": RECT_SHA,
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
