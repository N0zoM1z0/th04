#!/usr/bin/env python3
"""Import pinned TH04 (and optional TH01 smoke) targets from the legal RAR."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import tomllib

from lib.pc98 import (
    classify_format,
    digest_file,
    find_fat_boot_sectors,
    parse_fat_boot_sector,
    parse_mz,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "targets.toml"


def fail(message: str) -> "None":
    raise SystemExit(f"error: {message}")


def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, **kwargs)


def extract_hdi(archive: Path, destination: Path, expected_sha256: str) -> Path:
    extractor = shutil.which("unar")
    if not extractor:
        fail("unar is required to extract this RAR variant")
    run(
        [
            extractor,
            "-quiet",
            "-force-overwrite",
            "-output-directory",
            str(destination),
            str(archive),
        ]
    )
    candidates = [
        path
        for path in destination.rglob("*")
        if path.is_file() and path.name.casefold() == "zun.hdi"
    ]
    matches = [path for path in candidates if digest_file(path) == expected_sha256]
    if len(matches) != 1:
        fail(
            f"expected exactly one zun.hdi with SHA-256 {expected_sha256}; "
            f"found {len(matches)}"
        )
    return matches[0]


def verify_hdi(hdi: Path, source: dict[str, object]) -> dict[str, object]:
    data = hdi.read_bytes()
    if len(data) < 32:
        fail("HDI is too small for an Anex86 header")
    (
        reserved,
        hdd_type,
        header_size,
        data_size,
        physical_sector_size,
        sectors,
        heads,
        cylinders,
    ) = struct.unpack_from("<8I", data)
    if reserved != 0:
        fail("Anex86 HDI reserved header field is nonzero")
    if header_size + data_size != len(data):
        fail("Anex86 HDI header/data sizes do not equal physical size")
    if header_size != int(source["hdi_header_size"]):
        fail(f"HDI header size mismatch: {header_size}")
    expected_partition = int(source["fat_partition_offset"])
    boot = parse_fat_boot_sector(data, expected_partition)
    discovered = find_fat_boot_sectors(data, header_size, physical_sector_size)
    if not any(candidate.offset == expected_partition for candidate in discovered):
        fail("pinned FAT partition was not found by the independent scanner")
    if boot.volume_label != source["fat_volume_label"]:
        fail(
            f"FAT volume label mismatch: {boot.volume_label!r} != "
            f"{source['fat_volume_label']!r}"
        )
    return {
        "hdd_type": hdd_type,
        "header_size": header_size,
        "data_size": data_size,
        "physical_sector_size": physical_sector_size,
        "sectors": sectors,
        "heads": heads,
        "cylinders": cylinders,
        "fat": boot.__dict__,
        "fat_candidates": [item.__dict__ for item in discovered],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--include-th01-smoke",
        action="store_true",
        help="also import private TH01 artifacts used by Oracle smoke tests",
    )
    parser.add_argument(
        "--include-all-games-smoke",
        action="store_true",
        help="import the complete TH01-TH05 private executable calibration corpus",
    )
    args = parser.parse_args()
    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    source = manifest["source"]

    archive = args.archive.resolve()
    if not archive.is_file():
        fail(f"archive not found: {archive}")
    archive_sha256 = digest_file(archive)
    mcopy = shutil.which("mcopy")
    if not mcopy:
        fail("mcopy from mtools is required for the PC-98 FAT filesystem")

    analysis = ROOT / ".analysis"
    analysis.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="target-import-", dir=analysis) as raw_tmp:
        temporary = Path(raw_tmp)
        hdi = extract_hdi(archive, temporary / "archive", source["hdi_sha256"])
        if digest_file(hdi) != source["hdi_sha256"]:
            fail("HDI digest changed after selection")
        hdi_info = verify_hdi(hdi, source)
        fat_offset = int(source["fat_partition_offset"])
        stage = temporary / "stage"
        stage.mkdir()
        selected = [
            artifact
            for artifact in manifest["artifacts"]
            if artifact["game"] == "th04"
            or args.include_all_games_smoke
            or (args.include_th01_smoke and artifact["game"] == "th01")
        ]
        receipts: list[dict[str, object]] = []
        environment = os.environ.copy()
        environment["MTOOLS_SKIP_CHECK"] = "1"
        for artifact in selected:
            staged = stage / artifact["id"]
            run(
                [
                    mcopy,
                    "-i",
                    f"{hdi}@@{fat_offset}",
                    f"::{artifact['dos_path']}",
                    str(staged),
                ],
                env=environment,
            )
            actual_size = staged.stat().st_size
            actual_sha256 = digest_file(staged)
            actual_md5 = digest_file(staged, "md5")
            detected = classify_format(staged.read_bytes())
            if actual_size != artifact["size"]:
                fail(f"{artifact['id']}: size mismatch: {actual_size}")
            if actual_sha256 != artifact["sha256"]:
                fail(f"{artifact['id']}: SHA-256 mismatch: {actual_sha256}")
            if actual_md5 != artifact["md5"]:
                fail(f"{artifact['id']}: MD5 mismatch: {actual_md5}")
            if detected != artifact["format"]:
                fail(
                    f"{artifact['id']}: format mismatch: {detected} != "
                    f"{artifact['format']}"
                )
            if detected == "mz":
                image = parse_mz(staged.read_bytes())
                if not image.valid:
                    fail(f"{artifact['id']}: invalid MZ: {'; '.join(image.errors)}")
            receipts.append(
                {
                    "id": artifact["id"],
                    "dos_path": artifact["dos_path"],
                    "private_path": artifact["private_path"],
                    "size": actual_size,
                    "sha256": actual_sha256,
                    "md5": actual_md5,
                    "format": detected,
                }
            )

        for artifact in selected:
            destination = ROOT / artifact["private_path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(stage / artifact["id"], destination)

        receipt = {
            "schema_version": 1,
            "imported_utc": datetime.now(timezone.utc).isoformat(),
            "archive": {"path": str(archive), "sha256": archive_sha256},
            "hdi": {"sha256": source["hdi_sha256"], **hdi_info},
            "canonicality": source["canonicality"],
            "artifacts": receipts,
        }
        (analysis / "target-import.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(
        f"imported {len(receipts)} pinned artifact(s) into .analysis/targets; "
        f"canonicality={source['canonicality']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
