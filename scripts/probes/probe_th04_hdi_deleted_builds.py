#!/usr/bin/env python3
"""Forensically check the pinned TH01-TH05 HDI for recoverable alternate TH04 builds.

The probe parses the attested FAT12 volume directly, including deleted directory
entries and file starts in unallocated clusters. It never promotes carved bytes
as source or target evidence by itself. The purpose is to determine whether the
user-supplied image contains a second recoverable TH04 executable that could
serve as independent provenance for the final blockers.
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
sys.path.insert(0, str(ROOT / "scripts"))

from lib.pc98 import parse_fat_boot_sector  # noqa: E402

PARTITION_OFFSET = 38912
EXPECTED_VOLUME = "TOUHOU"
EXPECTED_DELETED_ROOT = [
    ("?P2EMS.SYS", 1481, 2117),
    ("?P2HMA.SYS", 1495, 963),
]
EXPECTED_FREE_MZ_CLUSTER = 1694
EXPECTED_DELETED_MEMBERS = [
    ("GAMECB.BAT", "-lh5-", 243, 301, 0x112E),
    ("PMDPPZ.COM", "-lh5-", 16173, 28587, 0x66CC),
]
EXPECTED_CURRENT_CANBE_MEMBERS = [
    ("PMDPPZ.COM", "-lh5-", 16173, 28587, 0x66CC),
    ("GAMECB.BAT", "-lh5-", 175, 219, 0xBE9B),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="hdi-deleted-builds-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def short_name(entry: bytes) -> tuple[str, bool]:
    raw = bytearray(entry[:11])
    deleted = raw[0] == 0xE5
    if deleted:
        raw[0] = ord("?")
    elif raw[0] == 0x05:
        raw[0] = 0xE5
    base = bytes(raw[:8]).decode("cp932", errors="replace").rstrip()
    ext = bytes(raw[8:11]).decode("cp932", errors="replace").rstrip()
    return base + (("." + ext) if ext else ""), deleted


def parse_directory(raw: bytes, owner: str) -> list[dict[str, object]]:
    rows = []
    for slot in range(len(raw) // 32):
        entry = raw[slot * 32:(slot + 1) * 32]
        if entry[0] == 0x00 or entry[11] == 0x0F:
            continue
        name, deleted = short_name(entry)
        rows.append({
            "owner": owner,
            "slot": slot,
            "name": name,
            "deleted": deleted,
            "attributes": entry[11],
            "is_directory": bool(entry[11] & 0x10),
            "start_cluster": struct.unpack_from("<H", entry, 26)[0],
            "size": struct.unpack_from("<I", entry, 28)[0],
        })
    return rows


def parse_lzh_level01(raw: bytes, start: int) -> tuple[list[dict[str, object]], int]:
    rows = []
    pos = start
    while pos < len(raw):
        header_size = raw[pos]
        if header_size == 0:
            return rows, pos + 1
        if pos + 2 + header_size > len(raw):
            raise ValueError("truncated LZH header")
        method = raw[pos + 2:pos + 7].decode("ascii", errors="replace")
        packed = struct.unpack_from("<I", raw, pos + 7)[0]
        original = struct.unpack_from("<I", raw, pos + 11)[0]
        level = raw[pos + 20]
        if level not in (0, 1):
            raise ValueError(f"unsupported LZH level {level}")
        name_len = raw[pos + 21]
        name_start = pos + 22
        name_end = name_start + name_len
        if name_end + 2 > pos + 2 + header_size:
            raise ValueError("LZH filename escapes header")
        name = raw[name_start:name_end].decode("cp932", errors="replace")
        crc = struct.unpack_from("<H", raw, name_end)[0]
        payload_start = pos + 2 + header_size
        payload_end = payload_start + packed
        if payload_end > len(raw):
            raise ValueError("truncated LZH payload")
        rows.append({
            "name": name,
            "method": method,
            "packed_size": packed,
            "original_size": original,
            "level": level,
            "crc16": crc,
            "packed_sha256": sha(raw[payload_start:payload_end]),
        })
        pos = payload_end
    raise ValueError("LZH terminator missing")


def member_key(rows: list[dict[str, object]]) -> list[tuple[object, ...]]:
    return [
        (r["name"], r["method"], r["packed_size"], r["original_size"], r["crc16"])
        for r in rows
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = output_dir(args.output_dir)

    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    image_row = runtime["image"]
    image_path = ROOT / image_row["path"]
    image = image_path.read_bytes()
    if len(image) != image_row["size"] or sha(image) != image_row["sha256"]:
        raise ValueError("runtime HDI identity drift")

    boot = parse_fat_boot_sector(image, PARTITION_OFFSET)
    if boot.volume_label != EXPECTED_VOLUME or boot.filesystem != "FAT12":
        raise ValueError("unexpected FAT volume identity")
    bps = boot.bytes_per_sector
    spc = boot.sectors_per_cluster
    root_sectors = math.ceil((boot.root_entries * 32) / bps)
    fat0 = PARTITION_OFFSET + boot.reserved_sectors * bps
    root_offset = PARTITION_OFFSET + (boot.reserved_sectors + boot.fat_count * boot.fat_sectors) * bps
    root_size = boot.root_entries * 32
    data_offset = root_offset + root_size
    cluster_size = spc * bps
    data_start_sector = boot.reserved_sectors + boot.fat_count * boot.fat_sectors + root_sectors
    cluster_count = math.ceil((boot.total_sectors - data_start_sector) / spc)
    last_cluster = 2 + cluster_count - 1
    fat = image[fat0:fat0 + boot.fat_sectors * bps]

    def fat12(cluster: int) -> int:
        offset = cluster + cluster // 2
        value = fat[offset] | (fat[offset + 1] << 8)
        return ((value >> 4) & 0xFFF) if cluster & 1 else (value & 0xFFF)

    def cluster_offset(cluster: int) -> int:
        return data_offset + (cluster - 2) * cluster_size

    def chain(start: int) -> list[int]:
        result = []
        seen = set()
        cluster = start
        while 2 <= cluster < 0xFF8 and cluster not in seen:
            if cluster > last_cluster:
                raise ValueError("cluster chain escapes FAT volume")
            seen.add(cluster)
            result.append(cluster)
            cluster = fat12(cluster)
        return result

    def read_clusters(clusters: list[int]) -> bytes:
        return b"".join(
            image[cluster_offset(c):cluster_offset(c) + cluster_size] for c in clusters
        )

    root = parse_directory(image[root_offset:root_offset + root_size], "ROOT")
    genso = next(r for r in root if not r["deleted"] and r["is_directory"] and r["name"] == "GENSO")
    genso_rows = parse_directory(read_clusters(chain(int(genso["start_cluster"]))), "GENSO")
    deleted_root = [r for r in root if r["deleted"]]
    deleted_genso = [r for r in genso_rows if r["deleted"]]
    deleted_key = sorted((r["name"], r["start_cluster"], r["size"]) for r in deleted_root)
    if deleted_key != EXPECTED_DELETED_ROOT or deleted_genso:
        raise ValueError("deleted directory-entry inventory drift")

    # Verify the active TH04 executable set is unique in the GENSO directory.
    target_manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    th04 = {Path(r["dos_path"]).name.upper(): r for r in target_manifest["artifacts"] if r["game"] == "th04"}
    active_execs = []
    for row in genso_rows:
        name = str(row["name"]).upper()
        if row["deleted"] or row["is_directory"] or name not in th04:
            continue
        raw = read_clusters(chain(int(row["start_cluster"])))[:int(row["size"])]
        expected = th04[name]
        if len(raw) != expected["size"] or sha(raw) != expected["sha256"]:
            raise ValueError(f"active {name} identity drift")
        active_execs.append({"name": name, "size": len(raw), "sha256": sha(raw)})
    if sorted(x["name"] for x in active_execs) != sorted(th04):
        raise ValueError("active TH04 executable set drift")

    # Search recoverable file starts in every free cluster in the valid volume.
    free_clusters = [c for c in range(2, last_cluster + 1) if fat12(c) == 0]
    free_mz = []
    free_archive_heads = []
    for cluster in free_clusters:
        head = image[cluster_offset(cluster):cluster_offset(cluster) + 64]
        if head[:2] == b"MZ":
            free_mz.append(cluster)
        if head[:4] == b"PK\x03\x04" or head[2:5] == b"-lh":
            free_archive_heads.append(cluster)
    if free_mz != [EXPECTED_FREE_MZ_CLUSTER] or free_archive_heads:
        raise ValueError("free-cluster file-start inventory drift")

    # The sole free MZ is an LHA self-extractor. Its DOS-declared MZ image ends
    # exactly where the embedded LZH stream begins.
    mz_start = cluster_offset(EXPECTED_FREE_MZ_CLUSTER)
    mz_window = image[mz_start:mz_start + 4 * cluster_size]
    last, pages = struct.unpack_from("<HH", mz_window, 2)
    declared_mz_size = (pages - 1) * 512 + (last or 512)
    if declared_mz_size != 1702:
        raise ValueError("deleted SFX MZ extent drift")
    deleted_members, deleted_end = parse_lzh_level01(mz_window, declared_mz_size)
    if member_key(deleted_members) != EXPECTED_DELETED_MEMBERS:
        raise ValueError("deleted SFX LZH member table drift")

    # Compare that member table to the active CanBe compatibility archive.
    canbe = next(r for r in genso_rows if not r["deleted"] and r["name"].upper() == "CANBE.LZH")
    canbe_raw = read_clusters(chain(int(canbe["start_cluster"])))[:int(canbe["size"])]
    current_members, current_end = parse_lzh_level01(canbe_raw, 0)
    if member_key(current_members) != EXPECTED_CURRENT_CANBE_MEMBERS or current_end != len(canbe_raw):
        raise ValueError("active CANBE.LZH member table drift")
    deleted_pmd = next(r for r in deleted_members if r["name"].upper() == "PMDPPZ.COM")
    current_pmd = next(r for r in current_members if r["name"].upper() == "PMDPPZ.COM")
    if (deleted_pmd["original_size"], deleted_pmd["crc16"], deleted_pmd["packed_sha256"]) != (
        current_pmd["original_size"], current_pmd["crc16"], current_pmd["packed_sha256"]
    ):
        raise ValueError("deleted SFX PMDPPZ payload differs from active CANBE copy")

    receipt = {
        "schema_version": 1,
        "claim_scope": "pinned HDI deleted/unallocated alternate-TH04-build provenance search",
        "image_sha256": sha(image),
        "fat": {
            "partition_offset": PARTITION_OFFSET,
            "volume_label": boot.volume_label,
            "bytes_per_sector": bps,
            "sectors_per_cluster": spc,
            "cluster_size": cluster_size,
            "cluster_count": cluster_count,
            "free_cluster_count": len(free_clusters),
        },
        "active_th04_executables": active_execs,
        "deleted_root_entries": deleted_root,
        "deleted_genso_entries": deleted_genso,
        "free_mz_clusters": free_mz,
        "free_archive_head_clusters": free_archive_heads,
        "sole_free_mz": {
            "cluster": EXPECTED_FREE_MZ_CLUSTER,
            "file_offset": mz_start,
            "declared_mz_size": declared_mz_size,
            "lzh_members": deleted_members,
            "lzh_terminator_offset_in_carve": deleted_end,
        },
        "active_canbe": {
            "size": len(canbe_raw),
            "sha256": sha(canbe_raw),
            "lzh_members": current_members,
        },
        "conclusion": "The active GENSO directory contains exactly the registered TH04 MAIN/OP/MAINE/ZUN set. Deleted directory entries are only NP2 memory-driver SYS files. The sole recoverable MZ at a free-cluster file start is a CanBe/PMD compatibility LHA SFX containing only GAMECB.BAT and PMDPPZ.COM; its PMDPPZ compressed payload matches the active CANBE.LZH copy. No second recoverable TH04 executable file start is present.",
        "limit": "FAT forensics can only rule out recoverable file starts and intact deleted directory entries. It cannot exclude partial remnants whose original first cluster was overwritten or reallocated, and it grants no exact/source credit.",
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "free_cluster_count": len(free_clusters),
        "free_mz_clusters": free_mz,
        "deleted_root": deleted_key,
        "sole_mz_members": [r["name"] for r in deleted_members],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
