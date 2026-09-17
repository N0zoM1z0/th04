#!/usr/bin/env python3
"""Compare OP/MAINE candidate and target-restored relocation order by MAP owner.

The MAP assigns candidate producer ownership to physical load offsets. It is
not evidence for the historical target's source file or OMF record layout.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from replay_diet145f import private_output, sha256  # noqa: E402

MAP_LINE = re.compile(
    r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+"
    r"C=(\S+)\s+S=(\S+)\s+G=\S+\s+M=(\S+)"
)


def map_contributions(data: bytes) -> list[dict[str, object]]:
    intervals = []
    for line in data.decode("cp437", errors="replace").splitlines():
        match = MAP_LINE.match(line)
        if match is None:
            continue
        segment, offset, size, klass, name, module = match.groups()
        start = int(segment, 16) * 16 + int(offset, 16)
        length = int(size, 16)
        if length:
            intervals.append({
                "start": start, "end": start + length, "class": klass,
                "segment": name, "module": module,
            })
    if not intervals:
        raise ValueError("no detailed TLINK MAP contributions found")
    return intervals


def blocks(sites: list[int], owners: dict[int, str]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for index, site in enumerate(sites):
        owner = owners[site]
        if not result or result[-1]["owner"] != owner:
            result.append({
                "owner": owner, "first_index": index, "count": 1,
                "first_site": site, "last_site": site,
            })
        else:
            result[-1]["count"] += 1
            result[-1]["last_site"] = site
    return result


def first_mismatch(left: list[int], right: list[int]) -> int | None:
    return next((i for i, (a, b) in enumerate(zip(left, right)) if a != b), None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", choices=("th04-op", "th04-maine"))
    parser.add_argument("--candidate-receipt", type=Path, required=True)
    parser.add_argument("--target-roundtrip-receipt", type=Path, required=True)
    parser.add_argument("--candidate-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target = read_verified_artifact(
        ROOT, find_artifact(load_target_manifest(ROOT / "config/targets.toml"), args.artifact)
    )
    candidate_receipt_path = args.candidate_receipt.resolve()
    target_receipt_path = args.target_roundtrip_receipt.resolve()
    candidate_receipt = json.loads(candidate_receipt_path.read_text())
    target_receipt = json.loads(target_receipt_path.read_text())
    if (
        candidate_receipt["artifact"] != args.artifact
        or target_receipt["artifact"] != args.artifact
        or candidate_receipt["target_sha256"] != sha256(target)
        or target_receipt["target_sha256"] != sha256(target)
        or not candidate_receipt["candidate_inputs_identical"]
        or not candidate_receipt["packed_outputs_identical"]
        or not target_receipt["repacked_raw_exact"]
        or not target_receipt["restored_outputs_identical"]
    ):
        raise ValueError("receipt identity or replay guard failed")
    candidate_path = Path(candidate_receipt["builds"][0]["candidate_path"])
    restored_path = Path(target_receipt["builds"][0]["restored_path"])
    candidate_bytes = candidate_path.read_bytes()
    restored_bytes = restored_path.read_bytes()
    if (
        sha256(candidate_bytes) != candidate_receipt["builds"][0]["candidate_sha256"]
        or sha256(restored_bytes) != target_receipt["builds"][0]["restored_sha256"]
    ):
        raise ValueError("MZ identity mismatch")
    candidate = parse_mz(candidate_bytes)
    restored = parse_mz(restored_bytes)
    if not candidate.valid or not restored.valid:
        raise ValueError("MZ integrity failed")
    candidate_sites = [item.linear for item in candidate.relocations]
    restored_sites = [item.linear for item in restored.relocations]
    if len(set(candidate_sites)) != len(candidate_sites):
        raise ValueError("duplicate candidate relocation sites")
    if Counter(candidate_sites) != Counter(restored_sites):
        raise ValueError("relocation site multisets differ")
    map_path = args.candidate_map.resolve()
    map_bytes = map_path.read_bytes()
    contributions = map_contributions(map_bytes)
    site_owners: dict[int, str] = {}
    owner_segments: dict[int, str] = {}
    for site in candidate_sites:
        matches = [row for row in contributions if row["start"] <= site < row["end"]]
        if len(matches) != 1:
            raise ValueError(f"site 0x{site:X} has {len(matches)} MAP owners")
        site_owners[site] = str(matches[0]["module"])
        owner_segments[site] = str(matches[0]["segment"])
    candidate_blocks = blocks(candidate_sites, site_owners)
    restored_blocks = blocks(restored_sites, site_owners)
    module_differences = []
    for module in sorted(set(site_owners.values())):
        left = [site for site in candidate_sites if site_owners[site] == module]
        right = [site for site in restored_sites if site_owners[site] == module]
        if left != right:
            module_differences.append({
                "module": module,
                "relocations": len(left),
                "relation": "reverse" if left[::-1] == right else "other",
                "first_projected_mismatch": first_mismatch(left, right),
                "candidate_sites": left,
                "target_restored_sites": right,
            })
    output = private_output(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError("output already exists")
    report = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "candidate-map-projected-target-restored-relocation-diagnostic",
        "artifact": args.artifact,
        "target_sha256": sha256(target),
        "candidate_receipt_sha256": sha256(candidate_receipt_path.read_bytes()),
        "target_roundtrip_receipt_sha256": sha256(target_receipt_path.read_bytes()),
        "candidate_map_sha256": sha256(map_bytes),
        "candidate_mz_sha256": sha256(candidate_bytes),
        "target_restored_mz_sha256": sha256(restored_bytes),
        "relocation_count": len(candidate_sites),
        "relocation_sites_unique_and_equal": True,
        "first_order_mismatch": first_mismatch(candidate_sites, restored_sites),
        "candidate_owner_blocks": candidate_blocks,
        "target_restored_owner_blocks": restored_blocks,
        "candidate_owner_block_count": len(candidate_blocks),
        "target_restored_owner_block_count": len(restored_blocks),
        "module_differences": module_differences,
        "site_owner_segments": {
            f"0x{site:X}": owner_segments[site] for site in candidate_sites
        },
        "source_acceptance": "none; target OMF and historical pre-DIET MZ unavailable",
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "artifact": args.artifact,
        "relocations": len(candidate_sites),
        "first_order_mismatch": report["first_order_mismatch"],
        "owner_blocks": [len(candidate_blocks), len(restored_blocks)],
        "within_module_changes": [
            [row["module"], row["relocations"], row["relation"]]
            for row in module_differences
        ],
        "report": str(output),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
