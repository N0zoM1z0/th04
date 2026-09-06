#!/usr/bin/env python3
"""Mine relocation-normalized cross-game byte blocks as routing candidates only."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from lib.pc98 import classify_format, digest_bytes, parse_mz
from lib.targets import (
    TargetError,
    find_artifact,
    load_target_manifest,
    read_verified_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "targets.toml"


def analysis_view(data: bytes) -> tuple[bytes, bytes, int, tuple[int, ...]]:
    """Return normalized bytes, original bytes, file bias, and relocation sites."""

    if classify_format(data) == "com":
        return data, data, 0, ()
    image = parse_mz(data)
    return (
        image.normalized_program_image(),
        image.program_image,
        image.header.header_size,
        tuple(relocation.linear for relocation in image.relocations),
    )


def _seed(data: bytes) -> bytes:
    return hashlib.blake2s(data, digest_size=12).digest()


def find_shared_blocks(
    left: bytes,
    right: bytes,
    *,
    minimum_length: int,
    seed_size: int = 32,
    index_stride: int = 8,
    maximum_seed_occurrences: int = 8,
) -> list[tuple[int, int, int]]:
    """Find maximal exact blocks; hashing only proposes and byte equality verifies."""

    if minimum_length < seed_size + index_stride - 1:
        raise ValueError("minimum_length is too small for complete strided seeding")
    if len(left) < minimum_length or len(right) < minimum_length:
        return []

    positions: dict[bytes, list[int]] = defaultdict(list)
    saturated: set[bytes] = set()
    for right_pos in range(0, len(right) - seed_size + 1, index_stride):
        key = _seed(right[right_pos : right_pos + seed_size])
        bucket = positions[key]
        if len(bucket) < maximum_seed_occurrences:
            bucket.append(right_pos)
        else:
            saturated.add(key)

    matches: set[tuple[int, int, int]] = set()
    covered: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for left_pos in range(0, len(left) - seed_size + 1):
        key = _seed(left[left_pos : left_pos + seed_size])
        if key in saturated:
            continue
        for right_pos in positions.get(key, []):
            if left[left_pos : left_pos + seed_size] != right[
                right_pos : right_pos + seed_size
            ]:
                continue
            delta = right_pos - left_pos
            if any(start <= left_pos < end for start, end in covered[delta]):
                continue
            left_start = left_pos
            right_start = right_pos
            while (
                left_start > 0
                and right_start > 0
                and left[left_start - 1] == right[right_start - 1]
            ):
                left_start -= 1
                right_start -= 1
            left_end = left_pos + seed_size
            right_end = right_pos + seed_size
            while (
                left_end < len(left)
                and right_end < len(right)
                and left[left_end] == right[right_end]
            ):
                left_end += 1
                right_end += 1
            length = left_end - left_start
            if length >= minimum_length:
                matches.add((left_start, right_start, length))
                covered[delta].append((left_start, left_end))
    return sorted(matches, key=lambda item: (-item[2], item[0], item[1]))


def count_sites(sites: tuple[int, ...], start: int, length: int) -> int:
    end = start + length
    return sum(start <= site < end for site in sites)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left_artifact_id")
    parser.add_argument("right_artifact_id")
    parser.add_argument("--min-length", type=int, default=64)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--output",
        type=Path,
        help="also write deterministic JSON below the ignored .analysis directory",
    )
    args = parser.parse_args()
    if args.min_length < 39:
        parser.error("--min-length must be at least 39 bytes")
    if args.limit < 1:
        parser.error("--limit must be positive")

    try:
        manifest = load_target_manifest(MANIFEST)
        left_artifact = find_artifact(manifest, args.left_artifact_id)
        right_artifact = find_artifact(manifest, args.right_artifact_id)
        left_data = read_verified_artifact(ROOT, left_artifact)
        right_data = read_verified_artifact(ROOT, right_artifact)
    except TargetError as error:
        parser.error(str(error))

    left_view, left_raw, left_bias, left_sites = analysis_view(left_data)
    right_view, right_raw, right_bias, right_sites = analysis_view(right_data)
    blocks = find_shared_blocks(
        left_view, right_view, minimum_length=args.min_length
    )[: args.limit]
    records: list[dict[str, Any]] = []
    for left_start, right_start, length in blocks:
        raw_equal = sum(
            a == b
            for a, b in zip(
                left_raw[left_start : left_start + length],
                right_raw[right_start : right_start + length],
            )
        )
        records.append(
            {
                "length": length,
                "left": {
                    "module_offset": left_start,
                    "file_offset": left_start + left_bias,
                    "relocation_sites": count_sites(left_sites, left_start, length),
                },
                "right": {
                    "module_offset": right_start,
                    "file_offset": right_start + right_bias,
                    "relocation_sites": count_sites(right_sites, right_start, length),
                },
                "raw_equal_bytes": raw_equal,
                "raw_equal_ratio": round(raw_equal / length, 6),
                "normalized_sha256": digest_bytes(
                    left_view[left_start : left_start + length]
                ),
            }
        )

    output = {
        "schema_version": 1,
        "candidate_only": True,
        "warning": (
            "Shared bytes route reverse engineering work; they do not prove common "
            "source, function boundaries, semantics, or an exact reconstruction."
        ),
        "normalization": (
            "MZ load-module relocation words are zeroed; COM bytes are unchanged."
        ),
        "inputs": {
            "left": {
                "id": left_artifact["id"],
                "sha256": left_artifact["sha256"],
            },
            "right": {
                "id": right_artifact["id"],
                "sha256": right_artifact["sha256"],
            },
        },
        "parameters": {
            "minimum_length": args.min_length,
            "limit": args.limit,
            "seed_size": 32,
            "index_stride": 8,
            "maximum_seed_occurrences": 8,
        },
        "blocks": records,
    }
    encoded = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        destination = (ROOT / args.output).resolve()
        private_root = (ROOT / ".analysis").resolve()
        if destination == private_root or private_root not in destination.parents:
            parser.error("--output must remain below the ignored .analysis directory")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
