#!/usr/bin/env python3
"""Partition OP/MAINE DIET packed residual among three MZ input surfaces.

Every hybrid is a private, target-derived diagnostic. It must not be used as
product source or as an accepted exact reconstruction.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from replay_diet145f import NAMES, check_toolchain, private_output, run_once, sha256  # noqa: E402
from roundtrip_diet_target import run_guest  # noqa: E402

FACTORS = "PRT"


def checked_receipt(path: Path, artifact: str, target_sha: str, kind: str) -> dict:
    receipt = json.loads(path.read_text())
    if receipt["artifact"] != artifact or receipt["target_sha256"] != target_sha:
        raise ValueError(f"{kind} receipt target identity mismatch")
    if kind == "candidate":
        if not receipt["candidate_inputs_identical"] or not receipt["packed_outputs_identical"]:
            raise ValueError("candidate A/B replay is not deterministic")
    elif not (
        receipt["restored_outputs_identical"]
        and receipt["repacked_outputs_identical"]
        and receipt["repacked_raw_exact"]
    ):
        raise ValueError("target round trip did not pass")
    return receipt


def first_difference(a: bytes, b: bytes) -> int | None:
    for index, (left, right) in enumerate(zip(a, b)):
        if left != right:
            return index
    return min(len(a), len(b)) if len(a) != len(b) else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", choices=("th04-op", "th04-maine"))
    parser.add_argument("--candidate-receipt", type=Path, required=True)
    parser.add_argument("--target-roundtrip-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    name = NAMES[args.artifact]
    target = read_verified_artifact(
        ROOT, find_artifact(load_target_manifest(ROOT / "config/targets.toml"), args.artifact)
    )
    candidate_receipt_path = args.candidate_receipt.resolve()
    target_receipt_path = args.target_roundtrip_receipt.resolve()
    candidate_receipt = checked_receipt(
        candidate_receipt_path, args.artifact, sha256(target), "candidate"
    )
    target_receipt = checked_receipt(
        target_receipt_path, args.artifact, sha256(target), "roundtrip"
    )
    candidate_path = Path(candidate_receipt["builds"][0]["candidate_path"])
    candidate = candidate_path.read_bytes()
    restored_path = Path(target_receipt["builds"][0]["restored_path"])
    restored_target = restored_path.read_bytes()
    if (
        sha256(candidate) != candidate_receipt["builds"][0]["candidate_sha256"]
        or sha256(restored_target) != target_receipt["builds"][0]["restored_sha256"]
    ):
        raise ValueError("candidate or restored-target input hash mismatch")
    candidate_mz = parse_mz(candidate)
    target_mz = parse_mz(restored_target)
    if not candidate_mz.valid or not target_mz.valid:
        raise ValueError("input MZ integrity failed")
    header_size = candidate_mz.header.header_paragraphs * 16
    if (
        header_size != target_mz.header.header_paragraphs * 16
        or candidate_mz.header.relocation_table_offset != target_mz.header.relocation_table_offset
        or len(candidate_mz.relocations) != len(target_mz.relocations)
        or len(candidate_mz.program_image) >= len(target_mz.program_image)
        or candidate[:2] != b"MZ"
        or candidate_mz.header.relocation_table_offset != 0x3E
    ):
        raise ValueError("MZ layouts are not comparable")
    relocation_begin = candidate_mz.header.relocation_table_offset
    relocation_end = relocation_begin + 4 * len(candidate_mz.relocations)
    extra = restored_target[len(candidate):]
    if not extra or any(extra):
        raise ValueError("restored-target MZ does not have a zero-only tail")
    if sorted(item.linear for item in candidate_mz.relocations) != sorted(
        item.linear for item in target_mz.relocations
    ):
        raise ValueError("relocation site multisets differ")
    output = private_output(args.output_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    inputs = output / "inputs"
    inputs.mkdir()
    binary, dosbox, config, options, toolchain = check_toolchain(args.artifact)
    inverse = output / "inverse"
    inverse.mkdir()
    packed_candidate_path = Path(candidate_receipt["builds"][0]["packed_path"])
    if sha256(packed_candidate_path.read_bytes()) != candidate_receipt["builds"][0]["packed_sha256"]:
        raise ValueError("candidate packed-file hash mismatch")
    shutil.copy2(binary, inverse / "DIET.EXE")
    shutil.copy2(packed_candidate_path, inverse / name)
    inverse_command = run_guest(
        inverse.resolve(), dosbox, config,
        f"diet.exe -ra {name.lower()}", "RESTORE.LOG"
    )
    if (inverse / name).read_bytes() != candidate:
        raise ValueError("DIET -RA did not recover the candidate MZ byte-for-byte")
    results: list[dict[str, object]] = []
    for mask in range(8):
        factors = "".join(factor for bit, factor in enumerate(FACTORS) if mask & (1 << bit))
        label = factors or "base"
        hybrid = bytearray(candidate)
        if "P" in factors:
            hybrid[header_size:] = restored_target[header_size:len(candidate)]
        if "R" in factors:
            hybrid[relocation_begin:relocation_end] = restored_target[relocation_begin:relocation_end]
        if "T" in factors:
            hybrid[10:12] = restored_target[10:12]
            hybrid[2:6] = restored_target[2:6]
            hybrid.extend(extra)
        hybrid_bytes = bytes(hybrid)
        hybrid_mz = parse_mz(hybrid_bytes)
        if not hybrid_mz.valid:
            raise ValueError(f"{label}: hybrid MZ integrity failed")
        if label == "base" and hybrid_bytes != candidate:
            raise ValueError("base input changed")
        if label == "PRT" and hybrid_bytes != restored_target:
            raise ValueError("three-surface partition does not cover target-restored MZ")
        input_path = inputs / f"{label}-{name}"
        input_path.write_bytes(hybrid_bytes)
        packed_record = run_once(
            label, input_path, output, name, binary, dosbox, config, options
        )
        packed = Path(packed_record["packed_path"]).read_bytes()
        results.append({
            "factors": factors,
            "input_size": len(hybrid_bytes),
            "input_sha256": sha256(hybrid_bytes),
            "packed_size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_exact": packed == target,
            "first_raw_difference": first_difference(packed, target),
            "guest_command": packed_record["guest_command"],
            "guest_log_sha256": packed_record["guest_log_sha256"],
        })
    if results[0]["raw_exact"] or not results[-1]["raw_exact"]:
        raise ValueError("base/full diagnostic controls failed")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "target-derived-mz-surface-partition-only",
        "artifact": args.artifact,
        "target_sha256": sha256(target),
        "candidate_receipt_sha256": sha256(candidate_receipt_path.read_bytes()),
        "target_roundtrip_receipt_sha256": sha256(target_receipt_path.read_bytes()),
        "toolchain": toolchain,
        "pack_options": options,
        "candidate_inverse_control": {
            "packed_candidate_sha256": sha256(packed_candidate_path.read_bytes()),
            "restored_candidate_sha256": sha256(candidate),
            "restored_candidate_raw_exact": True,
            "command": inverse_command,
        },
        "surfaces": {
            "P": "observed program-image payload bytes; excludes zero tail",
            "R": "ordered relocation table bytes",
        "T": "coupled minimum allocation, MZ file-length fields, and trailing zeros",
        },
        "candidate_payload_difference_bytes": sum(
            left != right for left, right in zip(
                candidate[header_size:], restored_target[header_size:len(candidate)]
            )
        ),
        "ordered_relocation_difference_bytes": sum(
            left != right for left, right in zip(
                candidate[relocation_begin:relocation_end],
                restored_target[relocation_begin:relocation_end],
            )
        ),
        "extra_zero_bytes": len(extra),
        "results": results,
        "source_acceptance": "none; all non-base hybrids copy target-derived bytes",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "artifact": args.artifact,
        "results": [
            [row["factors"] or "-", row["packed_size"], row["raw_exact"]]
            for row in results
        ],
        "receipt": str(output / "receipt.json"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
