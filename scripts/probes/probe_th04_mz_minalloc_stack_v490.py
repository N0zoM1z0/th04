#!/usr/bin/env python3
"""Show that TH04 DOS-MZ minalloc is derived from file extent and initial stack end.

This is packed-header routing evidence only. It does not reconstruct the target
T extent or modify any executable/header byte.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402

EXPECTED = {
    "op-candidate": {
        "sha256": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
        "file_size": 73636, "header_size": 4608, "ss": 4918, "sp": 128, "minalloc": 612,
    },
    "op-target-restored": {
        "sha256": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "file_size": 76864, "header_size": 4608, "ss": 4918, "sp": 128, "minalloc": 410,
    },
    "maine-candidate": {
        "sha256": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        "file_size": 65998, "header_size": 3584, "ss": 4709, "sp": 128, "minalloc": 817,
    },
    "maine-target-restored": {
        "sha256": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "file_size": 69218, "header_size": 3584, "ss": 4709, "sp": 128, "minalloc": 615,
    },
    "op-rt-control": {
        "file_size": 76864, "header_size": 4608, "ss": 4918, "sp": 128, "minalloc": 410,
    },
    "op-i-control": {
        "file_size": 83424, "header_size": 4608, "ss": 4918, "sp": 128, "minalloc": 0,
    },
    "maine-rt-control": {
        "file_size": 69218, "header_size": 3584, "ss": 4709, "sp": 128, "minalloc": 615,
    },
    "maine-i-control": {
        "file_size": 79056, "header_size": 3584, "ss": 4709, "sp": 128, "minalloc": 0,
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(label: str, path: Path) -> dict[str, int | str | bool]:
    raw = path.read_bytes()
    mz = parse_mz(raw)
    if not mz.valid:
        raise ValueError(f"{label}: invalid MZ")
    h = mz.header
    load_bytes = len(raw) - h.header_size
    stack_end = (h.initial_relative_ss * 16) + h.initial_sp
    required_bytes = max(0, stack_end - load_bytes)
    derived = (required_bytes + 15) // 16
    result = {
        "sha256": sha(path),
        "file_size": len(raw),
        "header_size": h.header_size,
        "load_image_bytes": load_bytes,
        "initial_ss": h.initial_relative_ss,
        "initial_sp": h.initial_sp,
        "stack_end_bytes": stack_end,
        "required_extra_bytes": required_bytes,
        "derived_minalloc_paragraphs": derived,
        "header_minalloc_paragraphs": h.minimum_extra_allocation,
        "formula_exact": derived == h.minimum_extra_allocation,
    }
    expected = EXPECTED[label]
    for key, actual_key in (
        ("file_size", "file_size"), ("header_size", "header_size"),
        ("ss", "initial_ss"), ("sp", "initial_sp"), ("minalloc", "header_minalloc_paragraphs"),
    ):
        if result[actual_key] != expected[key]:
            raise ValueError(f"{label}: {key} drift: {result[actual_key]} != {expected[key]}")
    if "sha256" in expected and result["sha256"] != expected["sha256"]:
        raise ValueError(f"{label}: identity drift")
    if not result["formula_exact"]:
        raise ValueError(f"{label}: minalloc formula failed")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--op-candidate", type=Path, required=True)
    ap.add_argument("--op-target-restored", type=Path, required=True)
    ap.add_argument("--maine-candidate", type=Path, required=True)
    ap.add_argument("--maine-target-restored", type=Path, required=True)
    ap.add_argument("--v436-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    paths = {
        "op-candidate": args.op_candidate.resolve(),
        "op-target-restored": args.op_target_restored.resolve(),
        "maine-candidate": args.maine_candidate.resolve(),
        "maine-target-restored": args.maine_target_restored.resolve(),
        "op-rt-control": (args.v436_dir.resolve() / "controls/th04-op-RT.exe"),
        "op-i-control": (args.v436_dir.resolve() / "controls/th04-op-target-PR-on-I.exe"),
        "maine-rt-control": (args.v436_dir.resolve() / "controls/th04-maine-RT.exe"),
        "maine-i-control": (args.v436_dir.resolve() / "controls/th04-maine-target-PR-on-I.exe"),
    }
    results = {label: inspect(label, path) for label, path in paths.items()}

    # The target T extent adds bytes while SS:SP remains byte-identical. The
    # corresponding minalloc drop is therefore derived, not an independent knob.
    relations = {}
    for art in ("op", "maine"):
        cand = results[f"{art}-candidate"]
        tgt = results[f"{art}-target-restored"]
        extra = int(tgt["load_image_bytes"]) - int(cand["load_image_bytes"])
        drop = int(cand["header_minalloc_paragraphs"]) - int(tgt["header_minalloc_paragraphs"])
        expected_drop = (extra + 15) // 16
        same_stack = (
            cand["initial_ss"] == tgt["initial_ss"] and cand["initial_sp"] == tgt["initial_sp"]
        )
        if not same_stack or drop != expected_drop:
            raise ValueError(f"{art}: T/minalloc relation drift")
        relations[art] = {
            "extra_file_backed_load_bytes": extra,
            "minalloc_drop_paragraphs": drop,
            "ceil_extra_bytes_over_16": expected_drop,
            "same_initial_ss_sp": same_stack,
        }

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP/MAINE DOS-MZ minalloc derivation from file-backed load extent and fixed SS:SP; no packed exactness promotion",
        "formula": "e_minalloc = ceil(max(0, e_ss*16 + e_sp - load_image_bytes) / 16)",
        "results": results,
        "t_extent_relations": relations,
        "conclusion": (
            "Across the current v489 OP/MAINE candidates, target-restored MZs, and the retained v436 RT and /i controls, the MZ minimum-extra-allocation field is exactly the paragraph gap from the file-backed load image end to the initial stack top SS:SP. OP and MAINE retain identical SS:SP between candidate and target-restored views; increasing the target T extent lowers minalloc by exactly ceil(extra_file_backed_bytes/16) = 202 paragraphs in both artifacts. Historical minalloc is therefore not an independent reconstruction degree of freedom once the T extent and stack endpoint are fixed."
        ),
        "limit": (
            "This does not explain the historical or post-link mechanism that produced the target-attested T file extent. It only removes minalloc as a separate provenance question. The target T extent itself remains open."
        ),
    }
    out = args.output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(out), "receipt_sha256": sha(out), "formula_exact_cases": len(results)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
