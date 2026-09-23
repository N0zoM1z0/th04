#!/usr/bin/env python3
"""Review five OP hi_view physical functions, including Ghidra's truncated rank_render."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from probe_th04_score_hiscore_boundaries import (
    PINNED_REF, ROOT, TARGETS, branch_edges, disassemble, ghidra_rows,
    git, parse_mz_image, sha,
)

OP = TARGETS["th04-op"]
INVENTORY_SHA256 = "518d87142070b5c82643a74432bec826796b663e5268546373773fafe7d0ace0"
ANALYSIS_IMAGE = ROOT / ".analysis/reconstruction/boundary-review/th04-op/analysis.exe"
ANALYSIS_IMAGE_SHA256 = "3183cdc7943bc3e10160955b79b6df76d281399dbb3a47c3940c1aa0b95f7d33"
MAP = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source/obj/th04/op.map"
MAP_SHA256 = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"

# Payload offsets, not packed-file offsets. The end is the next entry, including
# rank_render's 0x3E bytes that Ghidra omitted after a nonterminal jump.
FUNCTIONS = (
    ("stage_put", 0xC8A5, 0xC8F5, 0x50,
     "c082747d5014d29b84ada4662b93dc0a11b6b22a6ce7cb44e798429e2960b363"),
    ("place_put", 0xC8F5, 0xCA1A, 0x125,
     "79322cc0563bb1c1753393eb704c5869f07563fc658da33c71c217e66b865c71"),
    ("rank_render", 0xCA1A, 0xCA94, 0x3C,
     "42f01ff3f1a4f34d2f5b06cce22e05d6b617e3491f0dfa7b8ee6d72bc9be8a1e"),
    ("regist_view_menu", 0xCA94, 0xCBE3, 0x14F,
     "907bc127317f2fb9e5fc10d14030f13051b9cee40a9d7fd66a90cd9dc6c16355"),
    ("cleardata_and_regist_view_sprite", 0xCBE3, 0xCC97, 0xB4,
     "2093f45b6f1e8fda9ef6004999ba3dedbf24c6ec12134c11262ad8dd455b633c"),
)

DECOMPILATION_COMMITS = {
    "stage_put": ("423e6c8aded13f8ad5ba6148c4d03713effc322a", "stage_put"),
    "place_put": ("97730856dfd15ebfb90c7219a53d30a164987e00", "place_put"),
    "rank_render": ("97120c12b369b364fb35e1b0d71d1e46e912601a", "rank_render"),
    "regist_view_menu": ("495205e16a71dfcc55afdca43a22904b50ba8515", "regist_view_menu"),
    "cleardata_and_regist_view_sprite": (
        "840aedebf65c858bd9a379aadc4fa1636d0785f8",
        "cleardata_and_regist_view_sprites_load",
    ),
}


def provenance() -> dict[str, object]:
    if git("rev-parse", "HEAD").decode().strip() != PINNED_REF:
        raise RuntimeError("pinned ReC98 revision drift")
    logical_source = git("show", f"{PINNED_REF}:th04/hiscore/view.cpp")
    if sha(logical_source) != "73c64e64b954f13b094d0bc9b0094944df5b512a65f6c8d94b3e8799de8726f9":
        raise RuntimeError("pinned logical source drift")
    result = {}
    for name, (commit, introduced_name) in DECOMPILATION_COMMITS.items():
        subject = git("show", "-s", "--format=%s", commit).decode().strip()
        patch = git("show", "--format=", "--unified=0", commit, "--", "th04")
        added_lines = [line[1:] for line in patch.splitlines()
                       if line.startswith(b"+") and not line.startswith(b"+++")]
        if not subject.startswith("[Decompilation]") or not any(
            re.search(rb"\b" + re.escape(introduced_name.encode()) + rb"\b", line)
            for line in added_lines
        ):
            raise RuntimeError(f"{name}: decompilation introduction drift")
        result[name] = {
            "commit": commit,
            "subject": subject,
            "introduced_name": introduced_name,
            "independent_original_source": False,
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   capture_output=True, text=True, check=True)
    ndisasm = shutil.which("ndisasm")
    if ndisasm is None:
        raise RuntimeError("ndisasm is required")
    for path, digest in (
        (OP["path"], OP["sha256"]),
        (OP["candidate"], OP["candidate_sha256"]),
        (OP["inventory"], INVENTORY_SHA256),
        (ANALYSIS_IMAGE, ANALYSIS_IMAGE_SHA256),
        (MAP, MAP_SHA256),
    ):
        if sha(path.read_bytes()) != digest:
            raise RuntimeError(f"input identity drift: {path}")

    target = parse_mz_image(OP["path"])
    candidate = parse_mz_image(OP["candidate"])
    inventory = ghidra_rows(OP["inventory"])
    map_publics = set()
    for line in MAP.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^\s*0A74:([0-9A-F]{4})\s+(?:idle\s+)?(.+)$", line)
        if match and not re.match(r"^[0-9A-F]{4}\s+C=", match.group(2)):
            offset = int(match.group(1), 16)
            if 0x2165 <= offset <= 0x2557:
                map_publics.add((offset, match.group(2).strip()))
    expected_publics = {
        (0x2165, "stage_put(int,int,int)"),
        (0x21B5, "place_put(int)"),
        (0x22DA, "rank_render()"),
        (0x2354, "regist_view_menu()"),
        (0x24A3, "cleardata_and_regist_view_sprite()"),
        (0x2557, "main_cdg_load()"),
    }
    if map_publics != expected_publics:
        raise RuntimeError(f"candidate MAP adjacency drift: {map_publics ^ expected_publics}")
    reviewed = []
    disassemblies = {}
    for name, start, end, ghidra_span, expected_sha in FUNCTIONS:
        body = target[start:end]
        if len(body) != end - start or sha(body) != expected_sha:
            raise RuntimeError(f"{name}: target body drift")
        if candidate[start:end] != body:
            raise RuntimeError(f"{name}: OP-local v489 candidate slice differs")
        observed = inventory.get(start)
        if observed is None or (
            int(observed["entry_linear"], 0) != 0x10000 + start
            or int(observed["entry_segment"], 0) != 0x1A74
            or int(observed["entry_offset"], 0) != start - 0xA740
            or int(observed["body_min_linear"], 0) != 0x10000 + start
            or int(observed["body_span"]) != ghidra_span
            or int(observed["body_addresses"]) != ghidra_span
            or int(observed["body_max_linear"], 0) != 0x10000 + start + ghidra_span - 1
            or observed["contiguous"] != "true"
            or observed["body_range_count"] != "1"
        ):
            raise RuntimeError(f"{name}: Ghidra inventory drift")
        rows = disassemble(ndisasm, body, start)
        instruction_starts = {int(row["address"]) for row in rows}
        if not rows or int(rows[0]["address"]) != start:
            raise RuntimeError(f"{name}: missing entry instruction")
        if any(
            int(left["address"]) + int(left["size"]) != int(right["address"])
            for left, right in zip(rows, rows[1:])
        ):
            raise RuntimeError(f"{name}: incomplete instruction tiling")
        last = rows[-1]
        if int(last["address"]) + int(last["size"]) != end or last["mnemonic"] != "ret":
            raise RuntimeError(f"{name}: no terminal RET at next entry")
        edges = branch_edges(rows)
        if any(not start <= dest < end or dest not in instruction_starts
               for _, _, dest in edges):
            raise RuntimeError(f"{name}: escaping or unaligned direct branch")
        if name == "rank_render":
            # A Ghidra omission, not trailing padding: the last instruction in
            # its truncated body jumps directly into the unclaimed suffix.
            if not any(src == 0xCA54 and dest == 0xCA5B and kind == "jmp"
                       for src, kind, dest in edges):
                raise RuntimeError("rank_render: missing branch into Ghidra-unclaimed tail")
            if start + ghidra_span != 0xCA56 or end - (start + ghidra_span) != 0x3E:
                raise RuntimeError("rank_render: tail extent drift")
        disassemblies[name] = "\n".join(str(row["text"]) for row in rows) + "\n"
        reviewed.append({
            "name": name,
            "payload_offset": f"0x{start:X}",
            "segment_identity": "0x1A74",
            "segment_offset": f"0x{start - 0xA740:X}",
            "end_exclusive": f"0x{end:X}",
            "reviewed_size": end - start,
            "target_sha256": expected_sha,
            "ghidra_body_span": ghidra_span,
            "ghidra_omitted_tail_bytes": end - start - ghidra_span,
            "candidate_slice_raw_equal": True,
            "instruction_count": len(rows),
            "terminal": str(last["text"]),
            "branch_edges": [
                {"source": f"0x{src:X}", "kind": kind, "target": f"0x{dest:X}"}
                for src, kind, dest in edges
            ],
            "direct_branches_stay_inside_and_aligned": True,
        })

    source_provenance = provenance()
    private.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    for name, disassembly in disassemblies.items():
        (output / f"th04-op-{name}.ndisasm").write_text(disassembly, encoding="ascii")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP hi_view five target-local physical boundaries, including rank_render control-flow correction",
        "target_restored_sha256": OP["sha256"],
        "candidate_exe_sha256": OP["candidate_sha256"],
        "inventory_sha256": INVENTORY_SHA256,
        "analysis_image_sha256": ANALYSIS_IMAGE_SHA256,
        "candidate_map_sha256": MAP_SHA256,
        "candidate_map_publics": [
            {"offset": f"0x{offset:X}", "name": name}
            for offset, name in sorted(map_publics)
        ],
        "functions": reviewed,
        "pinned_rec98_revision": PINNED_REF,
        "function_provenance": source_provenance,
        "conclusion": (
            "Five OP hi_view extents tile 0xC8A5..0xCC96. rank_render owns "
            "0xCA1A..0xCA93; Ghidra omits a reachable 0x3E-byte tail. "
            "ReC98 logical source is explicitly introduced as decompilation."
        ),
        "limit": "Physical boundary review only; no maintained source or exact acceptance is granted.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([(row["name"], row["reviewed_size"]) for row in reviewed]))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
