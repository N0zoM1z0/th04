#!/usr/bin/env python3
"""Cold-compile OP's maintained high-score stage renderer and relink SCORE_TEXT."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_score_hiscore_boundaries import branch_edges, disassemble, ghidra_rows  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402
from replay_th04_maine_score_insert import sha, sha_file  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
INVENTORY = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
ANALYSIS_IMAGE = ROOT / ".analysis/reconstruction/boundary-review/th04-op/analysis.exe"
START = 0xC8A5
SIZE = 0x50
NEXT = START + SIZE
SCORE_START = 0xC57A
SCORE_SIZE = 0x71D
EXPECTED_RELOCATIONS = 804
INPUTS = {
    TARGET: "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
    SNAPSHOT / "bin/th04/op.exe": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
    SNAPSHOT / "obj/th04/op.map": "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee",
    SNAPSHOT / "obj/th04/scall.obj": "34c12256366c793835895de4e51eb470a146af980aeec8399b9da804d1205fc7",
    SNAPSHOT / "th04/hiscore/view.cpp": "3e704aefa95bbef04c34dd93cf94804bb02aac45a05902e8b190a37a515fbf83",
    SNAPSHOT / "th04/scall.cpp": "7789531bbc2d529beb7354915b87e2877585a270b2108ed00fc8c375d52e7bfd",
    INVENTORY: "518d87142070b5c82643a74432bec826796b663e5268546373773fafe7d0ace0",
    ANALYSIS_IMAGE: "3183cdc7943bc3e10160955b79b6df76d281399dbb3a47c3940c1aa0b95f7d33",
}


def target_boundary(body: bytes) -> dict[str, object]:
    row = ghidra_rows(INVENTORY).get(START)
    if row is None or (
        int(row["entry_linear"], 0) != 0x1C8A5
        or int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != 0x2165
        or int(row["body_min_linear"], 0) != 0x1C8A5
        or int(row["body_max_linear"], 0) != 0x1C8F4
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
    ):
        raise RuntimeError("OP Ghidra stage-put extent drift")
    nd = shutil.which("ndisasm")
    if nd is None:
        raise RuntimeError("ndisasm unavailable")
    rows = disassemble(nd, body, START)
    starts = {int(item["address"]) for item in rows}
    if (not rows or int(rows[0]["address"]) != START
            or any(int(a["address"]) + int(a["size"]) != int(b["address"])
                   for a, b in zip(rows, rows[1:]))
            or rows[-1]["mnemonic"] != "ret"
            or int(rows[-1]["address"]) + int(rows[-1]["size"]) != NEXT
            or not str(rows[-1]["text"]).endswith("ret 0x6")):
        raise RuntimeError("OP target stage-put tiling/RET 6 drift")
    edges = branch_edges(rows)
    if any(not START <= dest < NEXT or dest not in starts for _, _, dest in edges):
        raise RuntimeError("OP target stage-put branch leaves function")
    if body.count(b"\x9a\x34\x3e") != 3 or b"\xff\x00" not in body or b"\xef\x00" not in body:
        raise RuntimeError("OP target gaiji call/immediate drift")
    return {
        "segment_identity": "1A74",
        "segment_offset": "2165",
        "payload_offset": "0xC8A5",
        "size": SIZE,
        "target_sha256": sha(body),
        "ghidra_span": SIZE,
        "instruction_count": len(rows),
        "direct_branches": len(edges),
        "terminal": str(rows[-1]["text"]),
        "all_direct_branches_internal_aligned": True,
    }


def overlay_source(work: Path) -> None:
    path = work / "th04/hiscore/view.cpp"
    if sha_file(path) != INPUTS[SNAPSHOT / "th04/hiscore/view.cpp"]:
        raise RuntimeError("v489 OP high-score source drift")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/op/score", work / "src/op/score", dirs_exist_ok=True)
    data = path.read_bytes()
    start_anchor = b"void pascal near stage_put(\n"
    end_anchor = b"#define name_put_shadowed"
    if data.count(start_anchor) != 1 or data.count(end_anchor) != 1:
        raise RuntimeError("OP stage-put anchors are not unique")
    start = data.index(start_anchor)
    end = data.index(end_anchor, start)
    path.write_bytes(data[:start] + b'#include "src/op/score/stage_put.inl"\n\n' + data[end:])


def tcc(work: Path, output: Path, label: str, source: str) -> None:
    run_checked([
        "wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-", "-3", "-Z", "-d",
        "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/", source,
    ], work, output / f"compile-{label}.log")


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
    for path, expected in INPUTS.items():
        if sha_file(path) != expected:
            raise RuntimeError(f"input identity drift: {path}")
    closure = source_closure(ROOT, ("src/op/score/stage.cpp",))
    source_hashes = {name: sha_file(ROOT / name) for name in closure}
    target = parse_mz(TARGET.read_bytes())
    base = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not base.valid or len(target.relocations) != EXPECTED_RELOCATIONS:
        raise RuntimeError("invalid OP target or candidate MZ")
    body = target.program_image[START:NEXT]
    boundary = target_boundary(body)
    if base.program_image[START:NEXT] != body:
        raise RuntimeError("v489 OP candidate stage-put body differs from target")
    sites = [row.linear for row in target.relocations]
    if [row.linear for row in base.relocations] != sites:
        raise RuntimeError("baseline OP ordered relocations are not target-exact")
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    if ("0A74:2165 idle  stage_put(int,int,int)" not in map_text
            or "0A74:21B5" not in map_text):
        raise RuntimeError("OP SCORE MAP entry/adjacency drift")
    base_code = segment_bytes(SNAPSHOT / "obj/th04/scall.obj", "SCORE_TEXT")
    if len(base_code) != SCORE_SIZE:
        raise RuntimeError("baseline OP grouped SCORE object size drift")
    local_start = START - SCORE_START
    object_body = base_code[local_start:local_start + SIZE]
    if len(object_body) != SIZE:
        raise RuntimeError("baseline OP object stage body missing")

    private.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True)
    builds = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        overlay_source(work)
        tcc(work, output, f"v545-stage-local-{label}", "src/op/score/stage.cpp")
        local_obj = work / "obj/th04/stage.obj"
        local_omf = describe_omf(local_obj.read_bytes())
        if not local_omf["valid"] or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]:
            raise RuntimeError("standalone OP stage producer drift")
        local_code = segment_bytes(local_obj, "SCORE_TEXT")
        if local_code != object_body:
            raise RuntimeError(f"{label}: maintained OP stage standalone CODE differs")
        (work / "obj/th04/scall.obj").unlink()
        tcc(work, output, f"v545-stage-group-{label}", "th04/scall.cpp")
        group_obj = work / "obj/th04/scall.obj"
        group_omf = describe_omf(group_obj.read_bytes())
        if not group_omf["valid"] or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]:
            raise RuntimeError("grouped OP SCORE producer drift")
        if segment_bytes(group_obj, "SCORE_TEXT") != base_code:
            raise RuntimeError(f"{label}: grouped OP SCORE CODE changed")
        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink(); mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[START:NEXT]
        if (not image.valid or sha_file(exe) != INPUTS[SNAPSHOT / "bin/th04/op.exe"]
                or sha_file(mp) != INPUTS[SNAPSHOT / "obj/th04/op.map"]
                or [row.linear for row in image.relocations] != sites
                or image.program_image != base.program_image or linked != body):
            raise RuntimeError(f"{label}: OP stage linked function/layout mismatch")
        builds[label] = {
            "standalone_object_link_relevant_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": sha(local_code),
            "group_object_link_relevant_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": sha(base_code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_function_sha256": sha(linked),
            "raw_function_difference_count": 0,
            "ordered_relocations": len(sites),
        }
    if builds["a"] != builds["b"]:
        raise RuntimeError("cold OP stage rounds differ")
    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained OP stage source changed during replay")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed stage_put and maintained-source decoded raw replay",
        "target_restored_sha256": INPUTS[TARGET],
        "inventory_sha256": INPUTS[INVENTORY],
        "analysis_image_sha256": INPUTS[ANALYSIS_IMAGE],
        "baseline_exe_sha256": INPUTS[SNAPSHOT / "bin/th04/op.exe"],
        "source_sha256": source_hashes,
        "boundary": boundary,
        "builds": builds,
        "limit": "Decoded stage function only; no DIET-packed offset, complete SCORE TU, or whole OP exact claim. Surrounding v489 source remains candidate scaffold.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "function_raw_equal": True,
                      "ordered_relocations": EXPECTED_RELOCATIONS}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
