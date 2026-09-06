#!/usr/bin/env python3
"""Conservatively review TH04 MAIN authored functions against exact byte owners.

The private target/Ghidra/TLINK files are observations.  This script only accepts a
function when three independently replayed views agree on its start and Ghidra's
entire *contiguous* body is contained in one exact authored byte owner.  It never
promotes non-contiguous switch/shared-tail bodies automatically.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "th04_main_function_review.toml"
UNITS = ROOT / "config" / "units.csv"


def parse_functions(path: Path) -> dict[int, str]:
    result: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split(None, 1)
        if len(fields) != 2:
            continue
        try:
            address = int(fields[0], 16)
        except ValueError:
            continue
        result[address] = fields[1]
    return result


def parse_publics(path: Path) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    pattern = re.compile(r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?(.+?)\s*$", re.I)
    for line in path.read_text(encoding="cp437", errors="replace").splitlines():
        match = pattern.match(line)
        if not match or "C=CODE" in line or "ACBP=" in line:
            continue
        address = int(match.group(1), 16) * 16 + int(match.group(2), 16) + 0x10000
        result.setdefault(address, []).append(match.group(3).strip())
    return result


def exact_authored_owners() -> list[dict[str, object]]:
    result = []
    with UNITS.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if (
                row["artifact"] != "th04-main"
                or row["origin"] != "authored"
                or row["state"] != "exact"
                or not row["file_offset"]
            ):
                continue
            start = int(row["file_offset"], 0) - 0x1800 + 0x10000
            result.append(
                {
                    "start": start,
                    "end": start + int(row["size"], 0),
                    "unit_id": row["id"],
                    "source": row["source"],
                    "owner_name": row["name"],
                }
            )
    return result


def candidates(functions: dict[int, str], publics: dict[int, list[str]]) -> list[dict[str, object]]:
    policy = tomllib.loads(POLICY.read_text(encoding="utf-8"))
    provisional = {int(item["address"], 0) for item in policy.get("provisional", [])}
    result: dict[int, dict[str, object]] = {}
    for owner in exact_authored_owners():
        for address, ghidra_name in functions.items():
            if not (int(owner["start"]) <= address < int(owner["end"])):
                continue
            if address not in publics or address in provisional:
                continue
            result[address] = {
                "address": address,
                "address_hex": f"0x{address:X}",
                "ghidra_name": ghidra_name,
                "public": publics[address][0],
                "owner_unit": owner["unit_id"],
                "owner_start": owner["start"],
                "owner_end": owner["end"],
                "source": owner["source"],
                "owner_name": owner["owner_name"],
            }
    return [result[key] for key in sorted(result)]


def parse_metadata(path: Path) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        row: dict[str, str] = {}
        for line in block.splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                row[key] = value
        if "address" in row:
            result[int(row["address"], 16)] = row
    return result


def review(items: list[dict[str, object]], metadata: dict[int, dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    accepted = []
    rejected = []
    for item in items:
        address = int(item["address"])
        data = metadata.get(address)
        reasons: list[str] = []
        if data is None:
            rejected.append({**item, "reasons": ["missing metadata"]})
            continue
        body_min = int(data["body_min"], 16)
        body_max = int(data["body_max"], 16)
        body_addresses = int(data["body_addresses"])
        if int(data["address"], 16) != address:
            reasons.append("entry mismatch")
        if body_min < int(item["owner_start"]) or body_max >= int(item["owner_end"]):
            reasons.append("body outside exact owner")
        span = body_max - body_min + 1
        if body_addresses != span:
            reasons.append(f"noncontiguous body {body_addresses}/{span}")
        if data.get("is_thunk") != "false":
            reasons.append("thunk")
        if data.get("is_external") != "false":
            reasons.append("external")
        reviewed = {
            **item,
            "body_min": body_min,
            "body_max": body_max,
            "body_addresses": body_addresses,
            "size": span,
            "calling_convention": data.get("calling_convention", ""),
            "signature": data.get("signature", ""),
        }
        if reasons:
            rejected.append({**reviewed, "reasons": reasons})
        else:
            accepted.append(reviewed)
    return accepted, rejected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--functions", type=Path, required=True)
    parser.add_argument("--map", dest="map_path", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--addresses-out", type=Path)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()

    items = candidates(parse_functions(args.functions), parse_publics(args.map_path))
    if args.addresses_out:
        args.addresses_out.parent.mkdir(parents=True, exist_ok=True)
        args.addresses_out.write_text("\n".join(str(item["address_hex"]) for item in items) + "\n", encoding="utf-8")
    report: dict[str, object] = {"schema_version": 1, "candidate_count": len(items), "candidates": items}
    if args.metadata:
        accepted, rejected = review(items, parse_metadata(args.metadata))
        policy = tomllib.loads(POLICY.read_text(encoding="utf-8"))
        reviewed_nonexact = policy.get("reviewed_nonexact", [])
        denominator = len(accepted) + len(reviewed_nonexact)
        report.update(
            {
                "strict_exact_count": len(accepted),
                "strict_rejected_count": len(rejected),
                "reviewed_nonexact_count": len(reviewed_nonexact),
                "reviewed_function_count": denominator,
                "exact_function_percent": (len(accepted) * 100 / denominator if denominator else None),
                "accepted": accepted,
                "rejected": rejected,
                "reviewed_nonexact": reviewed_nonexact,
            }
        )
        print(
            f"strict exact functions: {len(accepted)}/{denominator} "
            f"({len(accepted) * 100 / denominator:.6f}%)"
        )
        print(f"provisional strict rejections: {len(rejected)}")
    else:
        print(f"candidate starts: {len(items)}")
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
