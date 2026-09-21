#!/usr/bin/env python3
"""Scan FAT-free HDI runs for anonymous raw-code remnants of final TH04 blockers.

v413/v414 search recoverable files, archive headers, and trial text/member names.
This probe covers the complementary case where metadata was overwritten but raw
code from an older TH04 build survived in free FAT clusters. It is provenance
routing only and grants no source or exactness credit.
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

# Variable data-symbol words are wildcarded. Both legal MOV encodings are
# accepted so an older build would be found regardless of the final anomaly.
SND_SHORT = re.compile(
    rb"\x1e\xba..\xb8\x00\x3d\xcd\x21(?P<mov>\x89\xc3|\x8b\xd8)\x8b\x46\x06",
    re.S,
)
SND_LONG = re.compile(
    rb"\x1e\xba..\xb8\x00\x3d\xcd\x21(?P<mov>\x89\xc3|\x8b\xd8)"
    rb"\x8b\x46\x06\x80\xfc\x06\x75\x0b\x80\x3e..\x03\x75\x04"
    rb"\xcd\x61\xeb\x02\xcd\x60\xb8\x00\x3f\xb9\x00\x50\xcd\x21"
    rb"\x1f\xb4\x3e\xcd\x21",
    re.S,
)
CHECKER = bytes.fromhex("8e c2 b9 06 00 66 26 89 05 83 c7 08 e2 f7")
CARPET = re.compile(
    rb"\x55\x8b\xec\x56\x57\x1e\x07\xbb\x18\x00\x8b\x46\x06\xf7\xe3"
    rb"\x89\xc6\x81\xc6..\x8b\x46\x04\x01\xdb\xf7\xe3\x05..\x89\xc3"
    rb"\x31\xd2\xb9\x18\x00\xac",
    re.S,
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="hdi-raw-code-", dir=parent))
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
    row = runtime["image"]
    image = (ROOT / row["path"]).read_bytes()
    if len(image) != row["size"] or sha(image) != row["sha256"]:
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
    last_cluster = 1 + cluster_count
    fat = image[fat0:fat0 + boot.fat_sectors * bps]

    def fat12(cluster: int) -> int:
        pos = cluster + cluster // 2
        value = fat[pos] | (fat[pos + 1] << 8)
        return ((value >> 4) & 0xFFF) if cluster & 1 else (value & 0xFFF)

    free = [c for c in range(2, last_cluster + 1) if fat12(c) == 0]
    runs: list[list[int]] = []
    for cluster in free:
        if not runs or cluster != runs[-1][-1] + 1:
            runs.append([cluster])
        else:
            runs[-1].append(cluster)
    run_keys = [(r[0], r[-1]) for r in runs]
    if run_keys != EXPECTED_FREE_RUNS:
        raise ValueError(f"free-run topology drift: {run_keys}")

    findings: dict[str, list[dict[str, object]]] = {
        "snd_short": [], "snd_long": [], "checkerboard": [], "carpet": []
    }
    for run in runs:
        physical = data_offset + (run[0] - 2) * cluster_size
        end = data_offset + (run[-1] - 1) * cluster_size
        raw = image[physical:end]
        for name, pattern in (("snd_short", SND_SHORT), ("snd_long", SND_LONG), ("carpet", CARPET)):
            for match in pattern.finditer(raw):
                item: dict[str, object] = {
                    "file_offset": physical + match.start(),
                    "run_start_cluster": run[0],
                    "match_sha256": sha(match.group(0)),
                }
                if name.startswith("snd"):
                    item["mov_encoding"] = match.group("mov").hex()
                findings[name].append(item)
        pos = 0
        while True:
            found = raw.find(CHECKER, pos)
            if found < 0:
                break
            findings["checkerboard"].append({
                "file_offset": physical + found,
                "run_start_cluster": run[0],
                "match_sha256": sha(CHECKER),
            })
            pos = found + 1

    if any(findings.values()):
        raise ValueError(f"unexpected raw-code remnant found: {findings}")

    receipt = {
        "schema_version": 1,
        "claim_scope": "pinned HDI anonymous raw-code provenance search for TH04 final blockers",
        "image_sha256": sha(image),
        "fat": {
            "partition_offset": PARTITION_OFFSET,
            "cluster_size": cluster_size,
            "free_cluster_count": len(free),
            "free_runs": run_keys,
        },
        "patterns": {
            "snd_short": "PUSH DS / MOV DX,<wild> / MOV AX,3D00h / INT21 / MOV BX,AX (89C3 or 8BD8) / MOV AX,[BP+6]",
            "snd_long": "same loader prefix through DOS read, POP DS, and close; data-symbol words wildcarded",
            "checkerboard_hex": CHECKER.hex(),
            "carpet": "prologue plus PUSH DS/POP ES, two MUL BX, target register directions, CX=24, and LODSB; two data offsets wildcarded",
        },
        "findings": findings,
        "conclusion": "No FAT-free run contains even the short snd_load homolog with either handle-copy encoding, the longer loader body, the exact checkerboard LOOP core, or the distinctive carpet low-level prefix. No anonymous uncompressed raw-code remnant of a second TH04 build is recoverable from current free space.",
        "limit": "Compressed or overwritten remnants can remain undetectable. Absence of raw-code matches is provenance-negative only and grants no exactness or source-language inference.",
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "free_cluster_count": len(free),
        "findings": findings,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
