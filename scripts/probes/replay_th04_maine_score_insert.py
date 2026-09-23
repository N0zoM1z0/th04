#!/usr/bin/env python3
"""Cold-compile the maintained MAINE score-insertion body and relink SCORE_TEXT."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_score_hiscore_boundaries import (  # noqa: E402
    branch_edges, disassemble, ghidra_rows,
)
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin"
INVENTORY = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
INVENTORY_SHA = "c82e4500191cc066a7e18bd6d3d4ceefe698127dd787993a8fff01ee510f8fd0"
ANALYSIS_IMAGE = ROOT / ".analysis/reconstruction/boundary-review/th04-maine/analysis.exe"
ANALYSIS_IMAGE_SHA = "8962948a573bf2820def666bb19845271ecb8e5fbc1cd45ccc86e62ab4a77822"
SOURCE_DIR = ROOT / "src/maine/score"
SOURCE = SOURCE_DIR / "insert.cpp"
HEADER = SOURCE_DIR / "scoredat.hpp"
BODY = SOURCE_DIR / "score_insert.inl"
FUNCTION_OFFSET = 0xC3B2
FUNCTION_SIZE = 0x154
FUNCTION_TARGET_SHA = "ed7880a5a1cd7aa721c2a95bafb819da15768fd660cf6dd96dbccc9fdc30c093"
FUNCTION_OBJECT_SHA = "978e0eb303d2875ed00983f0ea3fc9d48136949afbcd677190a7447eeba2d09c"
TARGET_SHA = "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533"
BASE_EXE_SHA = "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c"
BASE_MAP_SHA = "014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e"
BASE_SCORE_OBJECT_SHA = "8bfa4a6da8584f005e565b1bcd18136250e48b233b5c443bbd42264c560cdf03"
BASE_SCORE_SOURCE_SHA = "db28104988abdf426e25f767f272f12db8c5c54299cc72c86a34e073cf2178d4"
BASE_SCORE_CODE_SHA = "d8180ee4acb342cefe168337bb6dff4986b6bac625a4c614128c1b9430cec693"
SCORE_OWNER_OFFSET = 0xC149
SCORE_OWNER_SIZE = 0xB30
RELOCATIONS = 559


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def target_boundary(body: bytes) -> dict[str, object]:
    inv = ghidra_rows(INVENTORY)
    row = inv.get(FUNCTION_OFFSET)
    if row is None or (
        int(row["entry_linear"], 0) != 0x1C3B2
        or int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != 0x2362
        or int(row["body_min_linear"], 0) != 0x1C3B2
        or int(row["body_max_linear"], 0) != 0x1C505
        or int(row["body_addresses"]) != FUNCTION_SIZE
        or int(row["body_span"]) != FUNCTION_SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
    ):
        raise RuntimeError("MAINE Ghidra score-insert extent drift")
    nd = shutil.which("ndisasm")
    if nd is None:
        raise RuntimeError("ndisasm unavailable")
    rows = disassemble(nd, body, FUNCTION_OFFSET)
    starts = {int(item["address"]) for item in rows}
    if (not rows or int(rows[0]["address"]) != FUNCTION_OFFSET
            or any(int(left["address"]) + int(left["size"]) != int(right["address"])
                   for left, right in zip(rows, rows[1:]))
            or rows[-1]["mnemonic"] != "ret" or (
        int(rows[-1]["address"]) + int(rows[-1]["size"]) != FUNCTION_OFFSET + FUNCTION_SIZE
    )):
        raise RuntimeError("MAINE target score-insert has no terminal RET at next entry")
    edges = branch_edges(rows)
    if any(not FUNCTION_OFFSET <= dest < FUNCTION_OFFSET + FUNCTION_SIZE or dest not in starts
           for _, _, dest in edges):
        raise RuntimeError("MAINE target score-insert branch leaves function or misses instruction")
    # Distinct target-local globals independently constrain the declaration
    # layout: hi names/digits/stage, entered_place, and the far resident pointer.
    for encoding in (b"\xc6\x3f", b"\x20\x40", b"\x72\x40",
                     b"\x86\x40", b"\x9e\x0e"):
        if encoding not in body:
            raise RuntimeError(f"target score field-reference drift: {encoding.hex()}")
    return {
        "segment_identity": "1A05",
        "segment_offset": "2362",
        "payload_offset": "0xC3B2",
        "size": FUNCTION_SIZE,
        "target_sha256": sha(body),
        "ghidra_span": FUNCTION_SIZE,
        "instruction_count": len(rows),
        "terminal": str(rows[-1]["text"]),
        "direct_branches": len(edges),
        "all_direct_branches_internal_aligned": True,
    }


def overlay_source(work: Path) -> None:
    if sha_file(work / "th04/score86.cpp") != BASE_SCORE_SOURCE_SHA:
        raise RuntimeError("v489 score86 source drift")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(SOURCE_DIR, work / "src/maine/score", dirs_exist_ok=True)
    path = work / "th04/score86.cpp"
    data = path.read_bytes()
    start = data.index(b"void near score_insert(void)\n{")
    end = data.index(b"void pascal near score_put", start)
    if data.count(b"void near score_insert(void)\n{") != 1:
        raise RuntimeError("score-insert body anchor not unique")
    path.write_bytes(
        data[:start]
        + b'#include "src/maine/score/score_insert.inl"\n\n'
        + data[end:]
    )


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
        (SNAPSHOT / "bin/th04/maine.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/maine.map", BASE_MAP_SHA),
        (SNAPSHOT / "obj/th04/scoreall.obj", BASE_SCORE_OBJECT_SHA),
        (SNAPSHOT / "th04/score86.cpp", BASE_SCORE_SOURCE_SHA),
        (INVENTORY, INVENTORY_SHA),
        (ANALYSIS_IMAGE, ANALYSIS_IMAGE_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"input identity drift: {path}")
    source_closure = (
        SOURCE, HEADER, BODY,
        ROOT / "src/shared/config/resident.hpp",
        ROOT / "src/shared/config/score.hpp",
        ROOT / "src/shared/platform/types.hpp",
    )
    source_hashes = {str(path.relative_to(ROOT)): sha_file(path)
                     for path in source_closure}
    target = parse_mz(TARGET.read_bytes())
    base = parse_mz((SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not base.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid MAINE target or candidate MZ")
    target_body = target.program_image[FUNCTION_OFFSET:FUNCTION_OFFSET + FUNCTION_SIZE]
    if sha(target_body) != FUNCTION_TARGET_SHA:
        raise RuntimeError("target score-insert body identity drift")
    boundary = target_boundary(target_body)
    if base.program_image[FUNCTION_OFFSET:FUNCTION_OFFSET + FUNCTION_SIZE] != target_body:
        raise RuntimeError("v489 MAINE candidate function differs from target")
    target_sites = [row.linear for row in target.relocations]
    base_sites = [row.linear for row in base.relocations]
    if base_sites != target_sites:
        raise RuntimeError("baseline MAINE ordered relocations are not target-exact")
    map_text = (SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    if ("0A05:2362 idle  score_insert()" not in map_text
            or "0A05:24B6 idle  score_put(int,unsigned char)" not in map_text):
        raise RuntimeError("candidate MAP score entry adjacency drift")
    base_code = segment_bytes(SNAPSHOT / "obj/th04/scoreall.obj", "SCORE_TEXT")
    if len(base_code) != SCORE_OWNER_SIZE or sha(base_code) != BASE_SCORE_CODE_SHA:
        raise RuntimeError("baseline grouped SCORE producer drift")
    if sha(base_code[FUNCTION_OFFSET - SCORE_OWNER_OFFSET:
                     FUNCTION_OFFSET - SCORE_OWNER_OFFSET + FUNCTION_SIZE]) != FUNCTION_OBJECT_SHA:
        raise RuntimeError("baseline SCORE function object code drift")

    private.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True)
    builds = {}
    for label in ("a", "b"):
        work = output / label / "maine" / "source"
        work.parent.mkdir(parents=True)
        copy_compact_snapshot(SNAPSHOT, work, "maine")
        overlay_source(work)

        # First compile the TH04-owned semantic TU independently. The full
        # grouped replay below then consumes exactly its bounded .inl body.
        tcc(work, output, f"v543-score-local-{label}", "src/maine/score/insert.cpp")
        standalone_obj = work / "obj/th04/insert.obj"
        standalone_omf = describe_omf(standalone_obj.read_bytes())
        if (not standalone_omf["valid"] or
                "TC86 Borland C++ 4.02" not in standalone_omf["translator_comments"]):
            raise RuntimeError("standalone score TU producer drift")
        standalone_code = segment_bytes(standalone_obj, "SCORE_TEXT")
        if len(standalone_code) != FUNCTION_SIZE or sha(standalone_code) != FUNCTION_OBJECT_SHA:
            raise RuntimeError(f"{label}: maintained standalone score code not raw-exact")

        (work / "obj/th04/scoreall.obj").unlink()
        tcc(work, output, f"v543-score-group-{label}", "th04/scoreall.cpp")
        group_obj = work / "obj/th04/scoreall.obj"
        group_omf = describe_omf(group_obj.read_bytes())
        if (not group_omf["valid"] or
                "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]):
            raise RuntimeError("grouped SCORE TU producer drift")
        grouped_code = segment_bytes(group_obj, "SCORE_TEXT")
        if grouped_code != base_code:
            raise RuntimeError(f"{label}: grouped SCORE CODE changed")
        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink(); mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink",
                     r"@obj\th04\maine.@l"], work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        if not image.valid or sha_file(exe) != BASE_EXE_SHA or sha_file(mp) != BASE_MAP_SHA:
            raise RuntimeError(f"{label}: relink changed MAINE EXE or MAP")
        sites = [row.linear for row in image.relocations]
        linked = image.program_image[FUNCTION_OFFSET:FUNCTION_OFFSET + FUNCTION_SIZE]
        if sites != target_sites or image.program_image != base.program_image or linked != target_body:
            raise RuntimeError(f"{label}: MAINE function, program, or relocation mismatch")
        builds[label] = {
            "standalone_object_sha256": sha_file(standalone_obj),
            "standalone_object_link_relevant_sha256": link_relevant_omf_sha(standalone_obj),
            "standalone_code_sha256": sha(standalone_code),
            "group_object_sha256": sha_file(group_obj),
            "group_object_link_relevant_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": sha(grouped_code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_function_sha256": sha(linked),
            "raw_function_difference_count": 0,
            "ordered_relocations": len(sites),
            "baseline_program_equal": True,
        }
    # Dependency timestamp COMENT fields may differ. Every link-relevant
    # output and both complete function bodies must agree across cold rounds.
    for key in ("standalone_object_link_relevant_sha256", "group_object_link_relevant_sha256",
                "standalone_code_sha256", "group_code_sha256", "linked_exe_sha256",
                "linked_map_sha256", "linked_function_sha256", "raw_function_difference_count",
                "ordered_relocations", "baseline_program_equal"):
        if builds["a"][key] != builds["b"][key]:
            raise RuntimeError(f"cold rounds differ at {key}")
    if any(sha_file(ROOT / path) != digest for path, digest in source_hashes.items()):
        raise RuntimeError("maintained source changed during replay")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed score_insert and maintained-source decoded raw replay",
        "target_restored_sha256": TARGET_SHA,
        "inventory_sha256": INVENTORY_SHA,
        "analysis_image_sha256": ANALYSIS_IMAGE_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "builds": builds,
        "limit": (
            "No packed-file offset or whole packed-file exact claim. The v489 "
            "ReC98 snapshot supplies unaccepted surrounding SCORE/link scaffolding. "
            "The score_insert name is descriptive."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "function_raw_equal": True,
                      "ordered_relocations": RELOCATIONS}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
