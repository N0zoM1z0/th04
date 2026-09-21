#!/usr/bin/env python3
"""Compare the current OP/MAINE topology candidates with the real v228 target restore.

This probe deliberately does not treat DIET -RA output as the historical pre-DIET
TLINK file.  It only rebases the packed-topology diagnostic onto the target-derived
restore instead of the v231 restored-candidate inverse control used by v425/v427.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from analyze_diet_relocation_owners import blocks, map_contributions  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402

EXPECTED = {
    "th04-op": {
        "candidate_sha256": "78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd",
        "map_sha256": "cd2e0a35b1d1262dca398db0302ab68243179cf18edfac2e1ec0810acf2ef334",
        "target_restored_sha256": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "relocations": 804,
        "ordered_mismatches": 223,
        "same_index_count": 581,
        "first_mismatch": 146,
        "last_mismatch": 465,
        "candidate_owner_blocks": 37,
        "target_owner_blocks": 38,
        "changed_modules": {
            "th04/bgimage.cpp": (8, "reverse"),
            "th04/hi_view.cpp": (61, "other"),
            "th04_op_master_data_tail.asm": (4, "reverse"),
            "th04_op_music_master.asm": (35, "other"),
        },
    },
    "th04-maine": {
        "candidate_sha256": "9b14cad4fc3bbd079890cd15d64de03d3c7159fb2b4ae38dab111bdfc8a0df60",
        "map_sha256": "1dd895faa6c7fbfc537c2d56a95ff5ea693aa923b7f5701bb922f170dbfae4e0",
        "target_restored_sha256": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "relocations": 559,
        "ordered_mismatches": 299,
        "same_index_count": 260,
        "first_mismatch": 48,
        "last_mismatch": 346,
        "candidate_owner_blocks": 33,
        "target_owner_blocks": 34,
        "changed_modules": {
            "th04/bgimage.cpp": (8, "reverse"),
            "th04_maine.asm": (175, "other"),
            "th04_maine_master_data_tail.asm": (4, "reverse"),
        },
    },
}

HEADER_FIELDS = {
    "bytes_in_last_page": 2,
    "pages": 4,
    "relocations": 6,
    "header_paragraphs": 8,
    "minimum_extra_paragraphs": 10,
    "maximum_extra_paragraphs": 12,
    "initial_ss": 14,
    "initial_sp": 16,
    "checksum": 18,
    "initial_ip": 20,
    "initial_cs": 22,
    "relocation_table_offset": 24,
    "overlay": 26,
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="current-target-reloc-topology-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def header_values(data: bytes) -> dict[str, int]:
    return {name: int.from_bytes(data[offset:offset + 2], "little") for name, offset in HEADER_FIELDS.items()}


def analyze(artifact: str, candidate_path: Path, map_path: Path, restored_path: Path) -> dict[str, object]:
    expected = EXPECTED[artifact]
    candidate_bytes = candidate_path.read_bytes()
    map_bytes = map_path.read_bytes()
    restored_bytes = restored_path.read_bytes()
    identities = {
        "candidate_sha256": sha(candidate_bytes),
        "map_sha256": sha(map_bytes),
        "target_restored_sha256": sha(restored_bytes),
    }
    for key, value in identities.items():
        if value != expected[key]:
            raise ValueError(f"{artifact}: {key} drift: {value}")

    candidate = parse_mz(candidate_bytes)
    restored = parse_mz(restored_bytes)
    if not candidate.valid or not restored.valid:
        raise ValueError(f"{artifact}: invalid MZ")
    candidate_sites = [entry.linear for entry in candidate.relocations]
    restored_sites = [entry.linear for entry in restored.relocations]
    if Counter(candidate_sites) != Counter(restored_sites):
        raise ValueError(f"{artifact}: relocation site multiset differs")
    if len(candidate_sites) != expected["relocations"]:
        raise ValueError(f"{artifact}: relocation count drift")

    contributions = map_contributions(map_bytes)
    owners: dict[int, str] = {}
    owner_segments: dict[int, str] = {}
    for site in candidate_sites:
        matches = [row for row in contributions if row["start"] <= site < row["end"]]
        if len(matches) != 1:
            raise ValueError(f"{artifact}: site 0x{site:X} has {len(matches)} MAP owners")
        owners[site] = str(matches[0]["module"])
        owner_segments[site] = str(matches[0]["segment"])

    differing = [i for i, (left, right) in enumerate(zip(candidate_sites, restored_sites)) if left != right]
    current_blocks = blocks(candidate_sites, owners)
    target_blocks = blocks(restored_sites, owners)
    changed_modules = []
    for module in sorted(set(owners.values())):
        current = [site for site in candidate_sites if owners[site] == module]
        target = [site for site in restored_sites if owners[site] == module]
        if current == target:
            continue
        changed_modules.append({
            "module": module,
            "relocations": len(current),
            "relation": "reverse" if current[::-1] == target else "other",
            "same_local_index_count": sum(a == b for a, b in zip(current, target)),
            "current_sites": current,
            "target_restored_sites": target,
        })

    compact_changed = {row["module"]: (row["relocations"], row["relation"]) for row in changed_modules}
    if compact_changed != expected["changed_modules"]:
        raise ValueError(f"{artifact}: changed-module projection drift: {compact_changed}")
    checks = {
        "ordered_mismatches": len(differing),
        "same_index_count": sum(a == b for a, b in zip(candidate_sites, restored_sites)),
        "first_mismatch": differing[0] if differing else None,
        "last_mismatch": differing[-1] if differing else None,
        "candidate_owner_blocks": len(current_blocks),
        "target_owner_blocks": len(target_blocks),
    }
    for key, value in checks.items():
        if value != expected[key]:
            raise ValueError(f"{artifact}: {key} drift: {value}")

    candidate_header = header_values(candidate_bytes)
    restored_header = header_values(restored_bytes)
    header_differences = {
        name: {"candidate": candidate_header[name], "target_restored": restored_header[name]}
        for name in HEADER_FIELDS if candidate_header[name] != restored_header[name]
    }
    return {
        **identities,
        "candidate_size": len(candidate_bytes),
        "target_restored_size": len(restored_bytes),
        "relocation_count": len(candidate_sites),
        "relocation_multiset_exact": True,
        "ordered_mismatch_count": len(differing),
        "same_index_count": checks["same_index_count"],
        "first_mismatch": checks["first_mismatch"],
        "last_mismatch": checks["last_mismatch"],
        "candidate_owner_block_count": len(current_blocks),
        "target_restored_owner_block_count": len(target_blocks),
        "candidate_owner_blocks": current_blocks,
        "target_restored_owner_blocks": target_blocks,
        "changed_modules": changed_modules,
        "header_differences": header_differences,
        "site_owner_segments": {f"0x{site:X}": owner_segments[site] for site in candidate_sites},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for prefix in ("op", "maine"):
        parser.add_argument(f"--{prefix}-candidate", type=Path, required=True)
        parser.add_argument(f"--{prefix}-map", type=Path, required=True)
        parser.add_argument(f"--{prefix}-target-restored", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    out = output_dir(args.output_dir)
    artifacts = {
        "th04-op": analyze("th04-op", args.op_candidate.resolve(), args.op_map.resolve(), args.op_target_restored.resolve()),
        "th04-maine": analyze("th04-maine", args.maine_candidate.resolve(), args.maine_map.resolve(), args.maine_target_restored.resolve()),
    }
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "current-v425-v427-candidate versus v228 target-derived DIET restore relocation-topology diagnostic",
        "artifacts": artifacts,
        "interpretation": (
            "The current physical candidates still preserve target-equal relocation-site multisets, but their MZ relocation table order is far from the v228 target-derived restore: OP differs at 223/804 indices and MAINE at 299/559. The owner projection localizes the remaining order surfaces without editing source or relocation bytes."
        ),
        "limit": (
            "DIET -RA output is target-derived and repacks exactly, but it is not proven to be the historical pre-DIET TLINK file. These ordered differences route topology experiments and are not an exactness requirement by themselves."
        ),
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "op_ordered_mismatches": artifacts["th04-op"]["ordered_mismatch_count"],
        "maine_ordered_mismatches": artifacts["th04-maine"]["ordered_mismatch_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
