#!/usr/bin/env python3
"""Compare a cold TH04 candidate with the independently unpacked target payload.

This is a diagnostic payload Oracle for DIET-packed OP, MAINE, and ZUN. It never
claims packed-file exactness or promotes a unit in the acceptance ledger. The
target relocation sequence is the DIET stub's application order; it is not
attested as the original unpacked MZ relocation-table order.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402

ARTIFACT_FILES = {
    "th04-op": "op.exe",
    "th04-maine": "maine.exe",
    "th04-zun": "zun.com",
}
MAP_LINE = re.compile(
    r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+"
    r"C=(\S+)\s+S=(\S+)\s+.*?\bM=(\S+)", re.IGNORECASE
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_map(path: Path | None) -> list[dict[str, object]]:
    if path is None:
        return []
    owners = []
    for line in path.read_text(encoding="cp437", errors="replace").splitlines():
        match = MAP_LINE.search(line)
        if match is None:
            continue
        start = int(match[1], 16) * 16 + int(match[2], 16)
        size = int(match[3], 16)
        if size:
            owners.append({
                "start": start,
                "end_exclusive": start + size,
                "class": match[4],
                "segment": match[5],
                "module": match[6],
            })
    return owners


def mismatch_runs(target: bytes, candidate: bytes, owners: list[dict[str, object]]) -> list[dict[str, object]]:
    if len(target) != len(candidate):
        raise ValueError("cannot compute positions for unequal payload lengths")
    runs: list[dict[str, object]] = []
    for pos, (left, right) in enumerate(zip(target, candidate)):
        if left == right:
            continue
        if runs and runs[-1]["end_exclusive"] == pos:
            runs[-1]["end_exclusive"] = pos + 1
            runs[-1]["target_hex"] += f"{left:02x}"
            runs[-1]["candidate_hex"] += f"{right:02x}"
        else:
            runs.append({
                "start": pos,
                "end_exclusive": pos + 1,
                "target_hex": f"{left:02x}",
                "candidate_hex": f"{right:02x}",
                "owners": [o for o in owners if o["start"] <= pos < o["end_exclusive"]],
            })
    return runs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", choices=tuple(ARTIFACT_FILES))
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--observation-dir", required=True, type=Path)
    parser.add_argument("--map", dest="map_path", type=Path)
    args = parser.parse_args()
    artifact = next(
        item for item in tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
        if item["id"] == args.artifact
    )
    packed = (ROOT / artifact["private_path"]).read_bytes()
    if len(packed) != artifact["size"] or digest(packed) != artifact["sha256"]:
        raise ValueError("packed target failed manifest size/SHA-256 attestation")
    observation = args.observation_dir
    receipt = json.loads((observation / "receipt.json").read_text())
    payload = (observation / "payload.bin").read_bytes()
    if receipt["artifact"] != args.artifact or receipt["packed_target_sha256"] != artifact["sha256"]:
        raise ValueError("DIET observation belongs to another target")
    if len(payload) != receipt["payload_size"] or digest(payload) != receipt["payload_sha256"]:
        raise ValueError("DIET observation payload identity failed")
    if not all(receipt["checks"].values()) or len(receipt["runs"]) < 2:
        raise ValueError("DIET observation lacks two invariant load-segment runs")
    with (observation / "relocations.csv").open(newline="") as stream:
        target_relocations = [int(row["relative_linear"], 0) for row in csv.DictReader(stream)]
    if len(target_relocations) != receipt["relocation_count"]:
        raise ValueError("DIET observation relocation count failed")
    candidate_bytes = args.candidate.read_bytes()
    if args.artifact == "th04-zun":
        candidate_payload = candidate_bytes
        candidate_relocations: list[int] = []
        candidate_format = "flat-com"
    else:
        image = parse_mz(candidate_bytes)
        if not image.valid:
            raise ValueError("candidate MZ integrity failed")
        candidate_payload = image.program_image
        candidate_relocations = [item.linear for item in image.relocations]
        candidate_format = "mz"
    owners = load_map(args.map_path)
    result = {
        "artifact": args.artifact,
        "claim_scope": "decompressed-payload-diagnostic-only",
        "packed_target_sha256": artifact["sha256"],
        "target_observation_receipt_sha256": digest((observation / "receipt.json").read_bytes()),
        "target_payload_sha256": digest(payload),
        "candidate_path": str(args.candidate),
        "candidate_file_sha256": digest(candidate_bytes),
        "candidate_format": candidate_format,
        "candidate_payload_sha256": digest(candidate_payload),
        "target_payload_size": len(payload),
        "candidate_payload_size": len(candidate_payload),
        "target_relocation_count": len(target_relocations),
        "candidate_relocation_count": len(candidate_relocations),
        "diet_application_order_matches_candidate_mz": target_relocations == candidate_relocations,
        "relocation_multiset_exact": sorted(target_relocations) == sorted(candidate_relocations),
        "first_application_vs_mz_order_mismatch": next(
            (i for i, (left, right) in enumerate(zip(target_relocations, candidate_relocations)) if left != right),
            None,
        ),
        "payload_raw_exact": payload == candidate_payload,
        "payload_differing_bytes": (
            sum(left != right for left, right in zip(payload, candidate_payload))
            if len(payload) == len(candidate_payload) else None
        ),
        "payload_mismatch_runs": (
            mismatch_runs(payload, candidate_payload, owners)
            if len(payload) == len(candidate_payload) else []
        ),
        "candidate_map_sha256": digest(args.map_path.read_bytes()) if args.map_path else None,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
