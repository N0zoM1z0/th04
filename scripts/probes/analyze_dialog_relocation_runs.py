#!/usr/bin/env python3
"""Inspect complete dialog.cpp MZ relocation order and candidate OMF records.

The target object is unavailable. Descending runs in its MZ relocation table
are observations, not proof of the target's LEDATA/FIXUPP record boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402


def mz_relocations(image: bytes) -> list[int]:
    if image[:2] != b"MZ":
        raise ValueError("not an MZ image")
    count = int.from_bytes(image[6:8], "little")
    table = int.from_bytes(image[24:26], "little")
    header_size = int.from_bytes(image[8:10], "little") * 16
    if table + (count * 4) > header_size or header_size > len(image):
        raise ValueError("MZ relocation table exceeds the header")
    return [
        (int.from_bytes(image[table + (i * 4) + 2 : table + (i * 4) + 4], "little") << 4)
        + int.from_bytes(image[table + (i * 4) : table + (i * 4) + 2], "little")
        for i in range(count)
    ]


def descending_runs(sites: list[int]) -> list[dict[str, object]]:
    runs: list[list[int]] = []
    for site in sites:
        if not runs or site >= runs[-1][-1]:
            runs.append([])
        runs[-1].append(site)
    return [
        {"count": len(run), "first": run[0], "last": run[-1], "sites": run}
        for run in runs
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        parser.error("unsupported run ID")
    run = ROOT / ".analysis/reconstruction/exact-unit-replay" / args.run_id
    receipt = json.loads((run / "receipt.json").read_text())
    target_info = next(
        item for item in tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
        if item["id"] == "th04-main"
    )
    target = (ROOT / target_info["private_path"]).read_bytes()
    target_sha256 = hashlib.sha256(target).hexdigest()
    if target_sha256 != target_info["sha256"] or receipt["target_sha256"] != target_sha256:
        raise ValueError("target identity differs from pinned manifest or replay")
    target_header = int.from_bytes(target[8:10], "little") * 16
    result: dict[str, object] = {
        "run_id": args.run_id,
        "target_sha256": target_sha256,
        "target_object_available": False,
        "builds": [],
    }
    for build in receipt["builds"]:
        label = build["label"]
        unit = build["units"]["th04-main-dialog-op"]
        start = unit["map_start"]
        end = start + unit["map_size"]
        candidate_path = run / label / "source/bin/th04/main.exe"
        candidate = candidate_path.read_bytes()
        candidate_header = int.from_bytes(candidate[8:10], "little") * 16
        target_sites = [site for site in mz_relocations(target) if start <= site < end]
        candidate_sites = [site for site in mz_relocations(candidate) if start <= site < end]
        if sorted(target_sites) != sorted(candidate_sites):
            raise ValueError(f"{label}: complete dialog contribution relocation sites differ")
        for site in target_sites:
            if target[target_header + site - 3] != 0x9A:
                raise ValueError(f"{label}: target site {site:#x} is not a far CALL")
        for site in candidate_sites:
            if candidate[candidate_header + site - 3] != 0x9A:
                raise ValueError(f"{label}: candidate site {site:#x} is not a far CALL")
        object_path = run / label / "source/obj/th04/dialog.obj"
        object_bytes = object_path.read_bytes()
        ledata = code_ledata(parse_omf(object_bytes), "DIALOG_TEXT")
        locations = []
        for site in candidate_sites:
            offset_word = site - start - 2
            matches = []
            for begin, finish, record, fixupp in ledata:
                if not begin <= offset_word < finish:
                    continue
                relative = offset_word - begin
                for pos in range(len(fixupp) - 1):
                    if (
                        (fixupp[pos] & 0xC0) == 0xC0
                        and (((fixupp[pos] & 3) << 8) | fixupp[pos + 1]) == relative
                    ):
                        matches.append((record, pos, site))
            if len(matches) != 1:
                raise ValueError(f"{label}: site {site:#x} has {len(matches)} LOCAT matches")
            locations.extend(matches)
        object_order = [site for _, _, site in sorted(locations)]
        if object_order != candidate_sites:
            raise ValueError(f"{label}: FIXUPP order differs from candidate MZ order")
        result["builds"].append({
            "label": label,
            "map_start": start,
            "map_end_exclusive": end,
            "candidate_exe_sha256": hashlib.sha256(candidate).hexdigest(),
            "candidate_object_sha256": hashlib.sha256(object_bytes).hexdigest(),
            "target_sites": target_sites,
            "candidate_sites": candidate_sites,
            "target_descending_runs": descending_runs(target_sites),
            "candidate_descending_runs": descending_runs(candidate_sites),
            "candidate_ledata": [
                {"start": begin, "end_exclusive": finish, "fixupp_record": record}
                for begin, finish, record, _ in ledata
            ],
            "candidate_fixupp_order_matches_mz": True,
            "candidate_fixupp_locations": [
                {"site": site, "record": record, "byte_offset": pos}
                for record, pos, site in sorted(locations)
            ],
        })
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
