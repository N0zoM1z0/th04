#!/usr/bin/env python3
"""Scan every FAT-free run in the pinned HDI for partial TH04 trial remnants.

v413 ruled out intact deleted directory entries and recoverable executable file
starts. This follow-up closes the complementary case where a deleted archive's
first cluster was overwritten but later free clusters still preserve LHA member
headers or identifying trial/executable strings. All reads stay on the pinned
user-supplied HDI and all output stays below ignored .analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path.insert(0, str(ROOT / "scripts"))

from lib.pc98 import parse_fat_boot_sector  # noqa: E402

PARTITION_OFFSET = 38912
EXPECTED_FREE_RUNS = [(1481, 1482), (1484, 1487), (1495, 1495), (1508, 2583)]
EXPECTED_LZH_HEADERS = [
    (0xD3ECDF, "-lh5-", 8551, 21523, 0, "OMAKE.TXT", 58045),
    (0xD45267, "-lh5-", 8259, 27195, 0, "怪綺談.txt", 58774),
    (0xD4C6CC, "-lh5-", 2996, 7145, 0, "README.TXT", 32762),
    (0xD502A6, "-lh5-", 243, 301, 0, "GAMECB.BAT", 4398),
    (0xD503BB, "-lh5-", 16173, 28587, 0, "PMDPPZ.COM", 26316),
    (0xD55DB7, "-lh0-", 70, 70, 0, "RESET.BAT", 41491),
]
TRIAL_MARKERS = {
    "GEN_TS1": b"GEN_TS1",
    "TAIKEN": b"TAIKEN",
    "trial_jp": "体験版".encode("cp932"),
    "stage3_jp": "３面まで".encode("cp932"),
    "MAIN_EXE": b"MAIN.EXE",
    "OP_EXE": b"OP.EXE",
    "MAINE_EXE": b"MAINE.EXE",
    "ZUN_COM": b"ZUN.COM",
}
CONTEXT_MARKERS = {
    "th04_title_jp": "東方幻想郷".encode("cp932"),
    "GAME_BAT": b"GAME.BAT",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="hdi-partial-trial-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = output_dir(args.output_dir)

    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    image_row = runtime["image"]
    image = (ROOT / image_row["path"]).read_bytes()
    if len(image) != image_row["size"] or sha(image) != image_row["sha256"]:
        raise ValueError("runtime HDI identity drift")
    boot = parse_fat_boot_sector(image, PARTITION_OFFSET)
    if boot.filesystem != "FAT12" or boot.volume_label != "TOUHOU":
        raise ValueError("unexpected FAT volume identity")

    bps = boot.bytes_per_sector
    spc = boot.sectors_per_cluster
    root_sectors = math.ceil((boot.root_entries * 32) / bps)
    fat0 = PARTITION_OFFSET + boot.reserved_sectors * bps
    root_offset = PARTITION_OFFSET + (
        boot.reserved_sectors + boot.fat_count * boot.fat_sectors
    ) * bps
    data_offset = root_offset + boot.root_entries * 32
    cluster_size = bps * spc
    data_start_sector = (
        boot.reserved_sectors + boot.fat_count * boot.fat_sectors + root_sectors
    )
    cluster_count = math.ceil((boot.total_sectors - data_start_sector) / spc)
    last_cluster = 2 + cluster_count - 1
    fat = image[fat0:fat0 + boot.fat_sectors * bps]

    def fat12(cluster: int) -> int:
        off = cluster + cluster // 2
        value = fat[off] | (fat[off + 1] << 8)
        return ((value >> 4) & 0xFFF) if cluster & 1 else (value & 0xFFF)

    def cluster_offset(cluster: int) -> int:
        return data_offset + (cluster - 2) * cluster_size

    free = [c for c in range(2, last_cluster + 1) if fat12(c) == 0]
    runs: list[list[int]] = []
    for cluster in free:
        if not runs or cluster != runs[-1][-1] + 1:
            runs.append([cluster])
        else:
            runs[-1].append(cluster)
    run_keys = [(run[0], run[-1]) for run in runs]
    if run_keys != EXPECTED_FREE_RUNS:
        raise ValueError(f"FAT free-run topology drift: {run_keys}")

    trial_hits: list[dict[str, object]] = []
    context_hits: list[dict[str, object]] = []
    lzh_headers: list[dict[str, object]] = []
    method_re = re.compile(rb"-lh[0-9a-z]-", re.IGNORECASE)

    for run in runs:
        run_start = cluster_offset(run[0])
        run_end = cluster_offset(run[-1]) + cluster_size
        raw = image[run_start:run_end]
        for family, patterns in (("trial", TRIAL_MARKERS), ("context", CONTEXT_MARKERS)):
            sink = trial_hits if family == "trial" else context_hits
            for name, pattern in patterns.items():
                pos = 0
                while True:
                    hit = raw.find(pattern, pos)
                    if hit < 0:
                        break
                    absolute = run_start + hit
                    cluster = run[0] + (hit // cluster_size)
                    sink.append({
                        "pattern": name,
                        "file_offset": absolute,
                        "cluster": cluster,
                        "offset_in_cluster": hit % cluster_size,
                    })
                    pos = hit + 1

        # Scan the entire physically contiguous free run, not cluster-by-cluster,
        # so headers split across an 8 KiB cluster boundary are included.
        for match in method_re.finditer(raw):
            header = match.start() - 2
            if header < 0 or header + 24 > len(raw):
                continue
            header_size = raw[header]
            if header_size < 22 or header + 2 + header_size > len(raw):
                continue
            method = raw[header + 2:header + 7].decode("ascii", errors="replace")
            packed = int.from_bytes(raw[header + 7:header + 11], "little")
            original = int.from_bytes(raw[header + 11:header + 15], "little")
            level = raw[header + 20]
            name_len = raw[header + 21]
            if level not in (0, 1) or not (1 <= name_len <= 64):
                continue
            name_start = header + 22
            name_end = name_start + name_len
            if name_end + 2 > header + 2 + header_size:
                continue
            try:
                name = raw[name_start:name_end].decode("cp932")
            except UnicodeDecodeError:
                continue
            if any(ord(ch) < 32 for ch in name):
                continue
            crc16 = int.from_bytes(raw[name_end:name_end + 2], "little")
            absolute = run_start + header
            next_member = absolute + 2 + header_size + packed
            lzh_headers.append({
                "file_offset": absolute,
                "cluster": run[0] + (header // cluster_size),
                "offset_in_cluster": header % cluster_size,
                "header_size": header_size,
                "method": method,
                "packed_size": packed,
                "original_size": original,
                "level": level,
                "name": name,
                "crc16": crc16,
                "next_member_file_offset": next_member,
            })

    observed_lzh = [
        (
            row["file_offset"], row["method"], row["packed_size"],
            row["original_size"], row["level"], row["name"], row["crc16"],
        )
        for row in lzh_headers
    ]
    if observed_lzh != EXPECTED_LZH_HEADERS:
        raise ValueError(f"free-run LZH inventory drift: {observed_lzh}")
    if trial_hits:
        raise ValueError(f"unexpected TH04 trial/executable marker in free FAT data: {trial_hits}")

    # Confirm the only adjacent header pair is the old CanBe compatibility
    # archive discovered by v413. The other four headers are isolated remnants
    # from separate archives rather than one hidden continuous package.
    header_offsets = {int(row["file_offset"]) for row in lzh_headers}
    adjacent = [
        (row["name"], int(row["next_member_file_offset"]))
        for row in lzh_headers
        if int(row["next_member_file_offset"]) in header_offsets
    ]
    if adjacent != [("GAMECB.BAT", 0xD503BB)]:
        raise ValueError(f"unexpected contiguous LZH member topology: {adjacent}")

    executable_members = [
        row for row in lzh_headers
        if str(row["name"]).upper().endswith((".EXE", ".COM"))
        and str(row["name"]).upper() != "PMDPPZ.COM"
    ]
    if executable_members:
        raise ValueError(f"unexpected executable LZH member remnants: {executable_members}")

    receipt = {
        "schema_version": 1,
        "claim_scope": "pinned HDI partial/deleted TH04-trial archive remnant search",
        "image_sha256": sha(image),
        "free_cluster_count": len(free),
        "free_runs": [
            {"first_cluster": run[0], "last_cluster": run[-1], "cluster_count": len(run)}
            for run in runs
        ],
        "trial_marker_patterns": list(TRIAL_MARKERS),
        "trial_marker_hits": trial_hits,
        "context_marker_hits": context_hits,
        "lzh_member_headers": lzh_headers,
        "contiguous_lzh_pairs": adjacent,
        "conclusion": "Scanning every physically contiguous FAT-free run, including across cluster boundaries, finds no GEN_TS1/trial marker and no MAIN.EXE/OP.EXE/MAINE.EXE/ZUN.COM LHA member header. Six valid LHA member headers survive: isolated OMAKE.TXT, Kaikidan text, README.TXT, RESET.BAT, plus the adjacent GAMECB.BAT/PMDPPZ.COM CanBe pair already identified by v413. No recoverable partial TH04 trial archive member table is present.",
        "limit": "Compressed payload fragments without a surviving filename/header cannot be attributed to a specific build and therefore cannot establish independent provenance. This negative does not claim secure erasure of every historical byte.",
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "free_runs": run_keys,
        "trial_hits": len(trial_hits),
        "lzh_names": [row["name"] for row in lzh_headers],
        "context_hits": len(context_hits),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
