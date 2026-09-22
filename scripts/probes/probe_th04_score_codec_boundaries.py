#!/usr/bin/env python3
"""Target-review TH04 OP/MAINE score codec boundaries without accepting decompiled source."""

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
            ("scoredat_decode", 0xC57A, 0xAD, 0xC627,
             "5efe0d5065947fa7bc698dba06267ca16d3b34b3e90369907e14451fc9d0e2a5"),
            ("scoredat_encode", 0xC627, 0x65, 0xC68C,
             "737bdcca37820fb3848004e60f12b6e8121470668ea058fb233be1bac7e3b69f"),
            ("scoredat_recreate", 0xC68C, 0xA7, 0xC733,
             "b5f25d0f2b5b7b1448d75000b98578cd8710ae419e2c8c079d717a014c796909"),
        ),
    },
    "th04-maine": {
        "path": ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin",
        "sha256": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "candidate": ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source/bin/th04/maine.exe",
        "candidate_sha256": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        "inventory": ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv",
        "functions": (
            ("scoredat_decode", 0xC149, 0x58, 0xC1A1,
             "31ea6a61abea7712e7ddd2ef8d9ee446b5947b514611252cba2d70c3930aff99"),
            ("scoredat_encode", 0xC1A1, 0x65, 0xC206,
             "c5c56e733842e6ba9b2d0448109939b2e04c8536b8495057425c4e787437c497"),
            ("scoredat_recreate", 0xC206, 0xA7, 0xC2AD,
             "7bc9464f7f09359087fb329a0c829021a834415aba27383f717d38cd1ba98094"),
        ),
    },
}

SOURCE_PROVENANCE = {
    "th04/formats/scoredat/decode.cpp": {
        "intro": "36ecd3c7a9c7d988d0d0c1432c0d510d76b958a4",
        "pinned_sha256": "3dc54b4c4cc6fa862a4495b7a0a6a64a7698955fac42d8da7fe1158d2bf9d406",
        "subject": "[Decompilation] [th04/th05] GENSOU.SCR: Decryption",
    },
    "th04/formats/scoredat/encode.cpp": {
        "intro": "01684c4a1dfd3f5855a5798e17658b3d4bccab87",
        "pinned_sha256": "48bb08d8b34cf806bec7eede619b72928ef68ec88c4c52b35f06b11bc8d7edd9",
        "subject": "[Decompilation] [th04/th05] GENSOU.SCR: Encryption",
    },
    "th04/formats/scoredat/recreate.cpp": {
        "intro": "09dc7318edebfeae6e53647cf70d6731a8abf743",
        "pinned_sha256": "cfa667f847ae7a61357788edf2b643af9307940503178a61dd5f09b4e5e55cbd",
        "subject": "[Decompilation] [th04/th05] GENSOU.SCR: Default data",
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


def disassemble(ndisasm: str, body: bytes, start: int) -> list[dict[str, object]]:
    completed = subprocess.run(
        [ndisasm, "-b16", f"-o0x{start:X}", "-"],
        input=body,
        capture_output=True,
        check=True,
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


def jump_edges(rows: list[dict[str, object]]) -> list[tuple[int, str, int]]:
    result = []
    for row in rows:
        mnemonic = str(row["mnemonic"])
        if not mnemonic.startswith("j"):
            continue
        target = re.search(r"0x([0-9a-f]+)", str(row["operands"]))
        if not target:
            raise RuntimeError(f"non-direct jump in score codec: {row['text']}")
        result.append((
            int(row["address"]),
            mnemonic,
            int(target.group(1), 16),
        ))
    return result


def ghidra_rows(path: Path) -> dict[int, dict[str, str]]:
    result = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            result[int(row["entry_linear"], 0) - 0x10000] = row
    return result


def provenance() -> dict[str, object]:
    if git("rev-parse", PINNED_REF).decode().strip() != PINNED_REF:
        raise RuntimeError("pinned ReC98 revision unavailable")
    result = {}
    for path, expected in SOURCE_PROVENANCE.items():
        blob = git("show", f"{PINNED_REF}:{path}")
        if sha(blob) != expected["pinned_sha256"]:
            raise RuntimeError(f"{path}: pinned blob drift")
        history = git(
            "log", "--format=%H", PINNED_REF, "--", path
        ).decode().splitlines()
        if not history or history[-1] != expected["intro"]:
            raise RuntimeError(f"{path}: introduction history drift: {history[-3:]!r}")
        subject = git(
            "show", "-s", "--format=%s", expected["intro"]
        ).decode().strip()
        if subject != expected["subject"] or not subject.startswith("[Decompilation]"):
            raise RuntimeError(f"{path}: introduction provenance drift: {subject!r}")
        result[path] = {
            "pinned_blob_sha256": sha(blob),
            "introduction_commit": expected["intro"],
            "introduction_subject": subject,
            "history_commit_count": len(history),
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
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm is required")

    output.mkdir()
    artifact_results = {}
    for artifact, spec in TARGETS.items():
        target_path = spec["path"]
        candidate_path = spec["candidate"]
        if sha(target_path.read_bytes()) != spec["sha256"]:
            raise RuntimeError(f"{artifact}: target restored identity drift")
        if sha(candidate_path.read_bytes()) != spec["candidate_sha256"]:
            raise RuntimeError(f"{artifact}: v489 candidate identity drift")
        target_image = parse_mz_image(target_path)
        candidate_image = parse_mz_image(candidate_path)
        inventory = ghidra_rows(spec["inventory"])

        functions = []
        for name, start, size, next_start, expected_sha in spec["functions"]:
            if start + size != next_start:
                raise RuntimeError(f"{artifact}/{name}: configured chain is not contiguous")
            body = target_image[start:start + size]
            candidate_body = candidate_image[start:start + size]
            if len(body) != size or sha(body) != expected_sha:
                raise RuntimeError(f"{artifact}/{name}: target body identity drift")
            if candidate_body != body:
                raise RuntimeError(f"{artifact}/{name}: v489 candidate no longer raw-matches target")

            ghidra = inventory.get(start)
            if ghidra is None:
                raise RuntimeError(f"{artifact}/{name}: missing target Ghidra entry")
            if (
                int(ghidra["body_min_linear"], 0) != 0x10000 + start
                or int(ghidra["body_max_linear"], 0) != 0x10000 + start + size - 1
                or int(ghidra["body_addresses"]) != size
                or int(ghidra["body_span"]) != size
                or ghidra["contiguous"] != "true"
                or ghidra["body_range_count"] != "1"
            ):
                raise RuntimeError(f"{artifact}/{name}: Ghidra extent drift: {ghidra!r}")

            rows = disassemble(ndisasm, body, start)
            if not rows:
                raise RuntimeError(f"{artifact}/{name}: empty disassembly")
            if int(rows[0]["address"]) != start:
                raise RuntimeError(f"{artifact}/{name}: entry decode drift")
            last = rows[-1]
            if int(last["address"]) + int(last["size"]) != next_start:
                raise RuntimeError(f"{artifact}/{name}: instruction stream does not close at boundary")
            if last["mnemonic"] != "ret":
                raise RuntimeError(f"{artifact}/{name}: terminal is not RET: {last!r}")
            edges = jump_edges(rows)
            escaping = [
                edge for edge in edges
                if not (start <= edge[2] < next_start)
            ]
            if escaping:
                raise RuntimeError(f"{artifact}/{name}: jump escapes function: {escaping!r}")

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
                "jump_edges": [
                    {"source": f"0x{source:X}", "kind": kind, "target": f"0x{target:X}"}
                    for source, kind, target in edges
                ],
                "jump_edges_stay_inside": True,
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
            "TH04 OP/MAINE score codec target-local physical boundary review "
            "plus negative source-provenance intake"
        ),
        "artifacts": artifact_results,
        "pinned_rec98_revision": PINNED_REF,
        "source_provenance": provenance(),
        "conclusion": (
            "The decode/encode/recreate boundaries are independently closed on each "
            "target by contiguous target Ghidra bodies, complete ndisasm instruction "
            "streams ending in RET, internal-only jump edges, adjacency to the next "
            "function entry, and raw-equal v489 linked candidate slices. The three "
            "C++ implementation paths enter pinned ReC98 history explicitly as "
            "[Decompilation] work, so this receipt reviews physical boundaries but "
            "does not accept those candidate files as independent original source."
        ),
        "limit": (
            "No maintained product source is created, no source-present or exact "
            "unit is granted, and no OP evidence is transferred to MAINE or vice "
            "versa. A later natural source reconstruction must replay each artifact "
            "independently."
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
