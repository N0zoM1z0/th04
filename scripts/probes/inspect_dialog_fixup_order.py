#!/usr/bin/env python3
"""Relate a TH04 replay's far-call FIXUPP locations to MZ relocations.

This is a diagnostic Oracle. It does not edit an object or promote exactness.
The LOCAT scan is deliberately restricted to target-attested far CALL sites;
each site must have exactly one matching location in the selected LEDATA's
following FIXUPP record.
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

UNITS = ("th04-main-dialog-op", "th04-main-dialog-run")


def omf_index(data: bytes, pos: int) -> tuple[int, int]:
    first = data[pos]
    if first < 0x80:
        return first, pos + 1
    return ((first & 0x7F) << 8) | data[pos + 1], pos + 2


def code_ledata(records: tuple, segment_name: str) -> list[tuple[int, int, int, bytes]]:
    names = [""]
    segments: list[str] = []
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                length = record.data[pos]
                names.append(record.data[pos + 1 : pos + 1 + length].decode("latin-1"))
                pos += length + 1
        elif record.record_type == 0x98:
            data = record.data
            pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            name_index, _ = omf_index(data, pos)
            segments.append(names[name_index])
    code_segment = segments.index(segment_name) + 1
    result: list[tuple[int, int, int, bytes]] = []
    for number, record in enumerate(records):
        if record.record_type != 0xA0:
            continue
        index, pos = omf_index(record.data, 0)
        if index != code_segment:
            continue
        offset = int.from_bytes(record.data[pos : pos + 2], "little")
        payload = record.data[pos + 2 :]
        following = records[number + 1]
        if following.record_type != 0x9C:
            raise ValueError(f"{segment_name} LEDATA {number} lacks following FIXUPP")
        result.append((offset, offset + len(payload), number + 1, following.data))
    return result


def rotation(source: list[int], target: list[int]) -> int | None:
    if len(source) != len(target):
        return None
    return next(
        (index for index in range(len(source)) if source[index:] + source[:index] == target),
        None,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id", help="existing private exact-unit replay run ID")
    parser.add_argument("--unit", action="append", dest="units",
                        help="unit to inspect (repeatable; default: dialog op and run)")
    parser.add_argument("--segment", default="DIALOG_TEXT", help="OMF CODE segment")
    parser.add_argument("--object-path", default="th04/dialog.obj",
                        help="path below each build's source/obj directory")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        parser.error("run ID contains unsupported characters")
    if (
        not re.fullmatch(r"[A-Za-z0-9_./-]+", args.object_path)
        or Path(args.object_path).is_absolute()
        or ".." in Path(args.object_path).parts
    ):
        parser.error("object path contains unsupported characters")
    units = tuple(args.units) if args.units else UNITS
    run = ROOT / ".analysis/reconstruction/exact-unit-replay" / args.run_id
    receipt = json.loads((run / "receipt.json").read_text())
    target_info = next(
        item for item in tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
        if item["id"] == "th04-main"
    )
    target = (ROOT / target_info["private_path"]).read_bytes()
    if hashlib.sha256(target).hexdigest() != target_info["sha256"]:
        raise ValueError("private MAIN target identity failed")
    header_size = int.from_bytes(target[8:10], "little") * 16
    result = {"run_id": args.run_id, "target_sha256": target_info["sha256"], "builds": []}
    for build in receipt["builds"]:
        label = build["label"]
        object_path = run / label / "source/obj" / args.object_path
        object_bytes = object_path.read_bytes()
        records = parse_omf(object_bytes)
        ledata = code_ledata(records, args.segment)
        build_result = {
            "label": label,
            "object_sha256": hashlib.sha256(object_bytes).hexdigest(),
            "ledata": [{"start": start, "end": end, "fixupp_record": record}
                       for start, end, record, _ in ledata],
            "units": {},
        }
        for unit_id in units:
            unit = build["units"][unit_id]
            contribution_base = unit["map_start"]
            locations = []
            for site in unit["candidate_overlapping_relocations"]:
                if target[header_size + site - 3] != 0x9A:
                    raise ValueError(f"{unit_id}: load {site:#x} is not a target far CALL")
                offset_word = site - contribution_base - 2
                matches = []
                for start, end, record_number, fixupp in ledata:
                    if not start <= offset_word < end:
                        continue
                    relative = offset_word - start
                    for pos in range(len(fixupp) - 1):
                        if (
                            (fixupp[pos] & 0xC0) == 0xC0
                            and (((fixupp[pos] & 3) << 8) | fixupp[pos + 1]) == relative
                        ):
                            matches.append((record_number, pos, site))
                if len(matches) != 1:
                    raise ValueError(f"{unit_id}: load {site:#x} has {len(matches)} FIXUPP LOCAT matches")
                locations.extend(matches)
            object_order = [site for _, _, site in sorted(locations)]
            candidate = unit["candidate_overlapping_relocations"]
            target_order = unit["target_overlapping_relocations"]
            build_result["units"][unit_id] = {
                "raw_exact": unit["raw_exact"],
                "map_exact": unit["map_exact"],
                "relocations_exact": unit["relocations_exact"],
                "fixupp_order_matches_candidate": object_order == candidate,
                "candidate_rotation_to_target": rotation(candidate, target_order),
                "fixupp_locations": [
                    {"site": site, "record": record, "byte_offset": pos}
                    for record, pos, site in sorted(locations)
                ],
            }
            if object_order != candidate:
                raise ValueError(f"{unit_id}: FIXUPP order does not explain candidate MZ order")
        result["builds"].append(build_result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
