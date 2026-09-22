#!/usr/bin/env python3
"""Target-review selected TH04 OP/MAINE SCORE hiscore boundaries without accepting decompiled C++."""

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
REF = ROOT / "_reference/ReC98"
PINNED_REF = "b6ba5b0a529edbb31efdf8c0e939263804f8ee47"

TARGETS = {
    "th04-op": {
        "path": ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin",
        "sha256": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "candidate": ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source/bin/th04/op.exe",
        "candidate_sha256": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
        "inventory": ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv",
        "functions": (
            ("hiscore_scoredat_load_both", 0xC733, 0x6B, 0xC79E,
             "81cd0235b3e97394fab9168a5faeb316cf3590646ef4b71941c06d2a7dbe5e72"),
            ("scores_put", 0xC79E, 0x107, 0xC8A5,
             "f2d96c5f6893b598f652e03a82b3264267304b86b88e011286c946dc01695841"),
        ),
    },
    "th04-maine": {
        "path": ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin",
        "sha256": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "candidate": ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source/bin/th04/maine.exe",
        "candidate_sha256": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        "inventory": ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv",
        "functions": (
            ("hiscore_scoredat_load_for", 0xC2AD, 0x69, 0xC316,
             "d7c242f31981b55c3dbdb0db4296e6bf59524f9d2d9bb6761d2fc8ea37e0d273"),
            ("hiscore_scoredat_save", 0xC316, 0x9C, 0xC3B2,
             "657805c7c6b0773da7bdcd1e6813507c1c3305fb75dd8ee695c3b6b75d9992b6"),
        ),
    },
}

PROVENANCE = {
    "hiscore_scoredat_load_both": {
        "commit": "f761f8e313724e242d61bf979b36b45f15f14f60",
        "subject": "[Decompilation] [th04/th05] High Score screen: GENSOU.SCR loading",
        "current_path": "th04/hiscore/score_ld.cpp",
        "current_sha256": "c4bea8a87a7d977704aac082582ca294de5f666c6ded0a14247303df91f507b4",
    },
    "hiscore_scoredat_load_for": {
        "commit": "f761f8e313724e242d61bf979b36b45f15f14f60",
        "subject": "[Decompilation] [th04/th05] High Score screen: GENSOU.SCR loading",
        "current_path": "th04/hiscore/score_ld.cpp",
        "current_sha256": "c4bea8a87a7d977704aac082582ca294de5f666c6ded0a14247303df91f507b4",
    },
    "scores_put": {
        "commit": "9eef948b9380e9caf0b1019893858a9ae13ec3ef",
        "subject": "[Decompilation] [th04/th05] High Score viewer: Score rendering",
        "current_path": "th04/hiscore/view.cpp",
        "current_sha256": "73c64e64b954f13b094d0bc9b0094944df5b512a65f6c8d94b3e8799de8726f9",
    },
    "hiscore_scoredat_save": {
        "commit": "952ac1c042d2dcee0362e2491542a8b8d5a8ad4f",
        "subject": "[Decompilation] [th04/th05] High Score menu: GENSOU.SCR saving",
        "current_path": "th04/hiscore/score_sv.cpp",
        "current_sha256": "bad5527c97d375e54a754c29f40b3ff2c1629953b5c53e413ed20ecb4fc2a2be",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=REF, capture_output=True, check=True
    ).stdout


def parse_mz_image(path: Path) -> bytes:
    sys.path.insert(0, str(ROOT / "scripts"))
    from lib.pc98 import parse_mz
    return parse_mz(path.read_bytes()).program_image


def ghidra_rows(path: Path) -> dict[int, dict[str, str]]:
    result = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            result[int(row["entry_linear"], 0) - 0x10000] = row
    return result


def disassemble(ndisasm: str, body: bytes, start: int) -> list[dict[str, object]]:
    completed = subprocess.run(
        [ndisasm, "-b16", f"-o0x{start:X}", "-"],
        input=body, capture_output=True, check=True,
    )
    pattern = re.compile(
        rb"^([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+([A-Za-z0-9]+)\s*(.*)$"
    )
    rows = []
    for raw in completed.stdout.splitlines():
        match = pattern.match(raw)
        if not match:
            raise RuntimeError(f"unexpected ndisasm line: {raw!r}")
        hex_bytes = match.group(2).decode("ascii")
        rows.append({
            "address": int(match.group(1), 16),
            "size": len(hex_bytes) // 2,
            "mnemonic": match.group(3).decode("ascii").lower(),
            "operands": match.group(4).decode("ascii").strip().lower(),
            "text": raw.decode("ascii"),
        })
    return rows


def branch_edges(rows: list[dict[str, object]]) -> list[tuple[int, str, int]]:
    result = []
    for row in rows:
        mnemonic = str(row["mnemonic"])
        if not mnemonic.startswith("j"):
            continue
        target = re.search(r"0x([0-9a-f]+)", str(row["operands"]))
        if target:
            result.append((
                int(row["address"]), mnemonic, int(target.group(1), 16)
            ))
    return result


def provenance() -> dict[str, object]:
    if git("rev-parse", PINNED_REF).decode().strip() != PINNED_REF:
        raise RuntimeError("pinned ReC98 revision unavailable")
    result = {}
    for symbol, expected in PROVENANCE.items():
        current = git("show", f"{PINNED_REF}:{expected['current_path']}")
        if sha(current) != expected["current_sha256"]:
            raise RuntimeError(f"{symbol}: pinned logical source blob drift")
        subject = git(
            "show", "-s", "--format=%s", expected["commit"]
        ).decode().strip()
        if subject != expected["subject"] or not subject.startswith("[Decompilation]"):
            raise RuntimeError(f"{symbol}: decompilation subject drift: {subject!r}")
        grep = git(
            "grep", "-n", symbol, expected["commit"], "--", "th04"
        ).decode("utf-8")
        if symbol not in grep:
            raise RuntimeError(f"{symbol}: symbol missing from decompilation commit")
        patch = git(
            "show", "--format=", "--unified=2", expected["commit"], "--", "th04"
        ).decode("utf-8", errors="replace")
        if symbol not in patch:
            raise RuntimeError(f"{symbol}: introduction patch no longer contains symbol")
        result[symbol] = {
            "decompilation_commit": expected["commit"],
            "decompilation_subject": subject,
            "current_logical_path": expected["current_path"],
            "current_logical_blob_sha256": sha(current),
            "commit_tree_symbol_matches": grep.splitlines(),
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
        parser.error(
            "output directory must be new directly below .analysis/reconstruction/probes"
        )

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm is required")
    output.mkdir()

    artifact_results = {}
    for artifact, spec in TARGETS.items():
        if sha(spec["path"].read_bytes()) != spec["sha256"]:
            raise RuntimeError(f"{artifact}: target restored identity drift")
        if sha(spec["candidate"].read_bytes()) != spec["candidate_sha256"]:
            raise RuntimeError(f"{artifact}: v489 candidate identity drift")
        target_image = parse_mz_image(spec["path"])
        candidate_image = parse_mz_image(spec["candidate"])
        inventory = ghidra_rows(spec["inventory"])
        functions = []

        for name, start, size, next_start, expected_sha in spec["functions"]:
            if start + size != next_start:
                raise RuntimeError(f"{artifact}/{name}: configured adjacency drift")
            body = target_image[start:start + size]
            candidate_body = candidate_image[start:start + size]
            if len(body) != size or sha(body) != expected_sha:
                raise RuntimeError(f"{artifact}/{name}: target body identity drift")
            if candidate_body != body:
                raise RuntimeError(f"{artifact}/{name}: v489 linked slice differs from target")

            ghidra = inventory.get(start)
            if ghidra is None:
                raise RuntimeError(f"{artifact}/{name}: missing Ghidra entry")
            if (
                int(ghidra["body_min_linear"], 0) != 0x10000 + start
                or int(ghidra["body_max_linear"], 0) != 0x10000 + next_start - 1
                or int(ghidra["body_addresses"]) != size
                or int(ghidra["body_span"]) != size
                or ghidra["contiguous"] != "true"
                or ghidra["body_range_count"] != "1"
            ):
                raise RuntimeError(f"{artifact}/{name}: Ghidra extent drift: {ghidra!r}")

            rows = disassemble(ndisasm, body, start)
            if not rows:
                raise RuntimeError(f"{artifact}/{name}: empty disassembly")
            last = rows[-1]
            if int(last["address"]) + int(last["size"]) != next_start:
                raise RuntimeError(f"{artifact}/{name}: instruction stream boundary drift")
            if last["mnemonic"] != "ret":
                raise RuntimeError(f"{artifact}/{name}: terminal is not RET: {last!r}")
            edges = branch_edges(rows)
            escaping = [
                edge for edge in edges
                if not (start <= edge[2] < next_start)
            ]
            if escaping:
                raise RuntimeError(f"{artifact}/{name}: branch escapes body: {escaping!r}")

            (output / f"{artifact}-{name}.ndisasm").write_text(
                "\n".join(str(row["text"]) for row in rows) + "\n",
                encoding="ascii",
            )
            functions.append({
                "name": name,
                "payload_offset": f"0x{start:X}",
                "size": size,
                "target_sha256": sha(body),
                "candidate_slice_raw_equal": True,
                "ghidra_body_span": int(ghidra["body_span"]),
                "ghidra_contiguous": True,
                "instruction_count": len(rows),
                "terminal": str(last["text"]),
                "branch_edges": [
                    {"source": f"0x{source:X}", "kind": kind,
                     "target": f"0x{target:X}"}
                    for source, kind, target in edges
                ],
                "branch_edges_stay_inside": True,
                "next_function_entry": f"0x{next_start:X}",
            })

        artifact_results[artifact] = {
            "target_restored_sha256": spec["sha256"],
            "candidate_exe_sha256": spec["candidate_sha256"],
            "functions": functions,
        }

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "TH04 OP/MAINE selected SCORE hiscore target-local physical boundary "
            "review plus function-level negative decompilation provenance"
        ),
        "artifacts": artifact_results,
        "pinned_rec98_revision": PINNED_REF,
        "function_provenance": provenance(),
        "conclusion": (
            "The four selected high-score boundaries close independently on each "
            "target through exact contiguous Ghidra spans, complete target "
            "disassembly ending at RET, internal branch closure, next-entry "
            "adjacency, and artifact-local v489 linked equality. Each logical "
            "implementation is directly present in a ReC98 commit explicitly titled "
            "[Decompilation], so candidate C++ remains corroborating producer input "
            "rather than accepted original source."
        ),
        "limit": (
            "No product source is created, no source-present or exact unit is "
            "granted, and OP/MAINE evidence is not shared across artifacts."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        artifact: [
            (row["name"], row["payload_offset"], row["size"])
            for row in result["functions"]
        ]
        for artifact, result in artifact_results.items()
    }, sort_keys=True))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
