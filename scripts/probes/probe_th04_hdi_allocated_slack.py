#!/usr/bin/env python3
"""Scan allocated FAT12 file/directory slack for final TH04 blocker remnants.

v415 covers clusters marked free in FAT. This complementary probe scans bytes
that are physically allocated but logically unused: the tail of each regular
file's final cluster and directory bytes after the first end marker. These bytes
can retain prior content after file replacement. No carved bytes are accepted as
source or exactness evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_fat_boot_sector  # noqa: E402
from probe_th04_hdi_raw_code_remnants import (  # noqa: E402
    CARPET,
    CHECKER,
    PARTITION_OFFSET,
    SND_LONG,
    SND_SHORT,
)

EXPECTED_FILE_COUNT = 163
EXPECTED_DIRECTORY_COUNT = 7
EXPECTED_SLACK_SEGMENTS = 169
EXPECTED_SLACK_BYTES = 880571


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="hdi-allocated-slack-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def short_name(entry: bytes) -> str:
    raw = bytearray(entry[:11])
    if raw[0] == 0x05:
        raw[0] = 0xE5
    base = bytes(raw[:8]).decode("cp932", errors="replace").rstrip()
    ext = bytes(raw[8:11]).decode("cp932", errors="replace").rstrip()
    return base + (("." + ext) if ext else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = output_dir(args.output_dir)

    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    row = runtime["image"]
    image = (ROOT / row["path"]).read_bytes()
    if len(image) != row["size"] or sha(image) != row["sha256"]:
        raise ValueError("runtime HDI identity drift")
    boot = parse_fat_boot_sector(image, PARTITION_OFFSET)
    if boot.filesystem != "FAT12" or boot.volume_label != "TOUHOU":
        raise ValueError("unexpected FAT volume identity")

    bps = boot.bytes_per_sector
    spc = boot.sectors_per_cluster
    cluster_size = bps * spc
    root_sectors = math.ceil((boot.root_entries * 32) / bps)
    fat0 = PARTITION_OFFSET + boot.reserved_sectors * bps
    root_offset = PARTITION_OFFSET + (
        boot.reserved_sectors + boot.fat_count * boot.fat_sectors
    ) * bps
    root_size = boot.root_entries * 32
    data_offset = root_offset + root_size
    data_start_sector = (
        boot.reserved_sectors + boot.fat_count * boot.fat_sectors + root_sectors
    )
    cluster_count = math.ceil((boot.total_sectors - data_start_sector) / spc)
    last_cluster = 1 + cluster_count
    fat = image[fat0:fat0 + boot.fat_sectors * bps]

    def fat12(cluster: int) -> int:
        pos = cluster + cluster // 2
        value = fat[pos] | (fat[pos + 1] << 8)
        return ((value >> 4) & 0xFFF) if cluster & 1 else (value & 0xFFF)

    def cluster_offset(cluster: int) -> int:
        return data_offset + (cluster - 2) * cluster_size

    def chain(start: int) -> list[int]:
        result: list[int] = []
        seen: set[int] = set()
        cluster = start
        while 2 <= cluster < 0xFF8 and cluster not in seen:
            if cluster > last_cluster:
                raise ValueError("cluster chain escapes FAT volume")
            seen.add(cluster)
            result.append(cluster)
            cluster = fat12(cluster)
        return result

    def chain_bytes(clusters: list[int]) -> bytes:
        return b"".join(
            image[cluster_offset(c):cluster_offset(c) + cluster_size] for c in clusters
        )

    slack: list[dict[str, object]] = []
    files: list[dict[str, object]] = []
    directories: list[dict[str, object]] = []
    visited: set[tuple[int, ...] | str] = set()

    def add_directory_tail(owner: str, raw: bytes, end_offset: int, clusters: list[int] | None) -> None:
        tail = raw[end_offset:]
        if not tail:
            return
        slack.append({
            "kind": "directory-tail",
            "owner": owner,
            "logical_offset": end_offset,
            "physical_offset": root_offset + end_offset if clusters is None else None,
            "clusters": clusters or [],
            "bytes": tail,
        })

    def scan_directory(raw: bytes, owner: str, clusters: list[int] | None) -> None:
        key: tuple[int, ...] | str = tuple(clusters) if clusters is not None else "ROOT"
        if key in visited:
            return
        visited.add(key)
        directories.append({"owner": owner, "clusters": clusters or [], "allocated_size": len(raw)})
        first_end: int | None = None
        for slot in range(len(raw) // 32):
            entry = raw[slot * 32:(slot + 1) * 32]
            if entry[0] == 0x00:
                if first_end is None:
                    first_end = slot * 32
                continue
            if entry[0] == 0xE5 or entry[11] == 0x0F:
                continue
            name = short_name(entry)
            attr = entry[11]
            start = struct.unpack_from("<H", entry, 26)[0]
            size = struct.unpack_from("<I", entry, 28)[0]
            if attr & 0x08:
                continue
            if attr & 0x10:
                if name in (".", "..") or start < 2:
                    continue
                sub_chain = chain(start)
                scan_directory(chain_bytes(sub_chain), owner + "/" + name, sub_chain)
                continue
            if start < 2 or size == 0:
                continue
            file_chain = chain(start)
            if not file_chain:
                continue
            allocated = len(file_chain) * cluster_size
            if size > allocated:
                raise ValueError(f"{owner}/{name}: logical size escapes cluster chain")
            remainder = size % cluster_size
            tail_size = 0 if remainder == 0 else cluster_size - remainder
            files.append({
                "owner": owner + "/" + name,
                "size": size,
                "clusters": file_chain,
                "slack_size": tail_size,
            })
            if tail_size:
                physical = cluster_offset(file_chain[-1]) + remainder
                slack.append({
                    "kind": "file-slack",
                    "owner": owner + "/" + name,
                    "logical_offset": size,
                    "physical_offset": physical,
                    "clusters": [file_chain[-1]],
                    "bytes": image[physical:physical + tail_size],
                })
        if first_end is not None:
            add_directory_tail(owner, raw, first_end, clusters)

    scan_directory(image[root_offset:root_offset + root_size], "ROOT", None)

    slack_bytes = sum(len(item["bytes"]) for item in slack)
    if (
        len(files) != EXPECTED_FILE_COUNT
        or len(directories) != EXPECTED_DIRECTORY_COUNT
        or len(slack) != EXPECTED_SLACK_SEGMENTS
        or slack_bytes != EXPECTED_SLACK_BYTES
    ):
        raise ValueError(
            "allocated slack inventory drift: "
            f"files={len(files)} dirs={len(directories)} segments={len(slack)} bytes={slack_bytes}"
        )

    findings: dict[str, list[dict[str, object]]] = {
        "snd_short": [], "snd_long": [], "checkerboard": [], "carpet": []
    }
    regexes = (("snd_short", SND_SHORT), ("snd_long", SND_LONG), ("carpet", CARPET))
    for segment in slack:
        raw = segment["bytes"]
        assert isinstance(raw, bytes)
        for name, pattern in regexes:
            for match in pattern.finditer(raw):
                findings[name].append({
                    "owner": segment["owner"],
                    "kind": segment["kind"],
                    "relative_offset": match.start(),
                    "physical_offset": (
                        int(segment["physical_offset"]) + match.start()
                        if segment["physical_offset"] is not None else None
                    ),
                    "match_sha256": sha(match.group(0)),
                    **({"mov_encoding": match.group("mov").hex()} if name.startswith("snd") else {}),
                })
        pos = 0
        while True:
            found = raw.find(CHECKER, pos)
            if found < 0:
                break
            findings["checkerboard"].append({
                "owner": segment["owner"],
                "kind": segment["kind"],
                "relative_offset": found,
                "physical_offset": (
                    int(segment["physical_offset"]) + found
                    if segment["physical_offset"] is not None else None
                ),
                "match_sha256": sha(CHECKER),
            })
            pos = found + 1

    if any(findings.values()):
        raise ValueError(f"unexpected blocker code in allocated slack: {findings}")

    largest = sorted(
        ({"owner": item["owner"], "kind": item["kind"], "size": len(item["bytes"])} for item in slack),
        key=lambda item: int(item["size"]),
        reverse=True,
    )[:12]
    receipt = {
        "schema_version": 1,
        "claim_scope": "pinned HDI allocated file/directory slack provenance search for TH04 final blockers",
        "image_sha256": sha(image),
        "inventory": {
            "regular_file_count": len(files),
            "directory_count": len(directories),
            "slack_segment_count": len(slack),
            "slack_byte_count": slack_bytes,
            "largest_slack_segments": largest,
        },
        "patterns": {
            "snd_short": "same v415 wildcarded DOS-open homolog accepting 89 C3 or 8B D8",
            "snd_long": "same v415 wildcarded read/close loader body",
            "checkerboard_hex": CHECKER.hex(),
            "carpet": "same v415 distinctive low-level prefix",
        },
        "findings": findings,
        "conclusion": "No allocated regular-file tail slack or directory tail after the first FAT end marker contains a final-blocker code signature. Together with v415, neither FAT-free nor logically unused allocated space retains an anonymous uncompressed second TH04 build fragment.",
        "limit": "Compressed, overwritten, or still-live bytes inside unrelated logical file contents are not classified as provenance by this probe. The result grants no exactness or source-language inference.",
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "files": len(files),
        "directories": len(directories),
        "slack_segments": len(slack),
        "slack_bytes": slack_bytes,
        "findings": findings,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
