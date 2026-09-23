#!/usr/bin/env python3
"""Cold-compile the maintained MAINE score renderer and relink SCORE_TEXT."""

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
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402
import replay_th04_maine_score_insert as prior  # noqa: E402

SOURCE = ROOT / "src/maine/score/put.cpp"
BODY = ROOT / "src/maine/score/score_put.inl"
START = 0xC506
SIZE = 0xE6
NEXT = START + SIZE


def target_boundary(body: bytes) -> dict[str, object]:
    row = ghidra_rows(prior.INVENTORY).get(START)
    if row is None or (
        int(row["entry_linear"], 0) != 0x1C506
        or int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x24B6
        or int(row["body_min_linear"], 0) != 0x1C506
        or int(row["body_max_linear"], 0) != 0x1C5EB
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
    ):
        raise RuntimeError("MAINE Ghidra score-put extent drift")
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
            or not str(rows[-1]["text"]).endswith("ret 0x4")):
        raise RuntimeError("MAINE target score-put tiling/RET 4 drift")
    edges = branch_edges(rows)
    if any(not START <= dest < NEXT or dest not in starts for _, _, dest in edges):
        raise RuntimeError("MAINE target score-put branch leaves body")
    for encoded in (b"\x86\x40", b"\x88\x40", b"\x27\x40", b"\x20\x40", b"\x9a\x5e\x27"):
        if encoded not in body:
            raise RuntimeError(f"MAINE target score-put reference drift: {encoded.hex()}")
    return {
        "segment_identity": "1A05",
        "segment_offset": "24B6",
        "payload_offset": "0xC506",
        "size": SIZE,
        "target_sha256": prior.sha(body),
        "ghidra_span": SIZE,
        "instruction_count": len(rows),
        "direct_branches": len(edges),
        "terminal": str(rows[-1]["text"]),
        "all_direct_branches_internal_aligned": True,
    }


def overlay_source(work: Path) -> None:
    path = work / "th04/score86.cpp"
    if prior.sha_file(path) != prior.BASE_SCORE_SOURCE_SHA:
        raise RuntimeError("v489 SCORE source drift")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/maine/score", work / "src/maine/score", dirs_exist_ok=True)
    data = path.read_bytes()
    start_anchor = b"void pascal near score_put(int place, unsigned char rendered_playchar)\n{"
    end_anchor = b"void pascal near stage_put(int place, int rendered_playchar, int gaiji)"
    if data.count(start_anchor) != 1 or data.count(end_anchor) != 1:
        raise RuntimeError("SCORE body anchors are not unique")
    start = data.index(start_anchor)
    end = data.index(end_anchor, start)
    path.write_bytes(data[:start] + b'#include "src/maine/score/score_put.inl"\n\n' + data[end:])


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
        (prior.SNAPSHOT / "obj/th04/scoreall.obj", prior.BASE_SCORE_OBJECT_SHA),
        (prior.SNAPSHOT / "th04/score86.cpp", prior.BASE_SCORE_SOURCE_SHA),
        (prior.INVENTORY, prior.INVENTORY_SHA),
        (prior.ANALYSIS_IMAGE, prior.ANALYSIS_IMAGE_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"input identity drift: {path}")
    closure = source_closure(ROOT, ("src/maine/score/put.cpp",))
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}
    target = parse_mz(prior.TARGET.read_bytes())
    base = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not base.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid MAINE target or candidate MZ")
    body = target.program_image[START:NEXT]
    boundary = target_boundary(body)
    if base.program_image[START:NEXT] != body:
        raise RuntimeError("v489 candidate score-put bytes differ from target")
    target_sites = [row.linear for row in target.relocations]
    if [row.linear for row in base.relocations] != target_sites:
        raise RuntimeError("baseline MAINE ordered relocations not target-exact")
    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    if ("0A05:24B6 idle  score_put(int,unsigned char)" not in map_text
            or "0A05:259C idle  stage_put(int,int,int)" not in map_text):
        raise RuntimeError("candidate SCORE MAP adjacency drift")
    base_code = segment_bytes(prior.SNAPSHOT / "obj/th04/scoreall.obj", "SCORE_TEXT")
    if len(base_code) != prior.SCORE_OWNER_SIZE or prior.sha(base_code) != prior.BASE_SCORE_CODE_SHA:
        raise RuntimeError("baseline grouped SCORE object drift")
    local_start = START - prior.SCORE_OWNER_OFFSET
    object_body = base_code[local_start:local_start + SIZE]
    if len(object_body) != SIZE:
        raise RuntimeError("baseline SCORE object body missing")

    private.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True)
    builds = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        shutil.copytree(prior.SNAPSHOT, work, symlinks=True)
        overlay_source(work)
        tcc(work, output, f"v544-score-put-local-{label}", "src/maine/score/put.cpp")
        local_obj = work / "obj/th04/put.obj"
        local_omf = describe_omf(local_obj.read_bytes())
        if not local_omf["valid"] or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]:
            raise RuntimeError("standalone SCORE renderer producer drift")
        local_code = segment_bytes(local_obj, "SCORE_TEXT")
        if local_code != object_body:
            raise RuntimeError(f"{label}: maintained score-put standalone code differs")
        (work / "obj/th04/scoreall.obj").unlink()
        tcc(work, output, f"v544-score-put-group-{label}", "th04/scoreall.cpp")
        group_obj = work / "obj/th04/scoreall.obj"
        group_omf = describe_omf(group_obj.read_bytes())
        if not group_omf["valid"] or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]:
            raise RuntimeError("grouped SCORE producer drift")
        if segment_bytes(group_obj, "SCORE_TEXT") != base_code:
            raise RuntimeError(f"{label}: grouped SCORE CODE changed")
        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink(); mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[START:NEXT]
        if (not image.valid or prior.sha_file(exe) != prior.BASE_EXE_SHA
                or prior.sha_file(mp) != prior.BASE_MAP_SHA
                or [row.linear for row in image.relocations] != target_sites
                or image.program_image != base.program_image or linked != body):
            raise RuntimeError(f"{label}: MAINE score-put function/layout mismatch")
        builds[label] = {
            "standalone_object_link_relevant_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": prior.sha(local_code),
            "group_object_link_relevant_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": prior.sha(base_code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_function_sha256": prior.sha(linked),
            "raw_function_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }
    if builds["a"] != builds["b"]:
        raise RuntimeError("cold MAINE score-put rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained SCORE source changed during replay")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed score_put and maintained-source decoded raw replay",
        "target_restored_sha256": prior.TARGET_SHA,
        "inventory_sha256": prior.INVENTORY_SHA,
        "analysis_image_sha256": prior.ANALYSIS_IMAGE_SHA,
        "baseline_exe_sha256": prior.BASE_EXE_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "builds": builds,
        "limit": "Decoded function only; no DIET-packed offset, complete SCORE TU, or whole MAINE exact claim. Surrounding v489 source remains candidate scaffold.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "function_raw_equal": True,
                      "ordered_relocations": prior.RELOCATIONS}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
