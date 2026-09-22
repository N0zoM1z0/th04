#!/usr/bin/env python3
"""Fail-closed intake for a candidate TH04 1998-07-02 trial self-extractor.

This probe never executes the candidate. It verifies the published outer size,
DOS MZ/SFX structure, the appended level-0/1 LHA member table, archive CRCs,
and decompressed trial-document markers. Passing establishes only a stable
candidate identity suitable for later cross-build analysis; it does not prove
an official pristine download, source provenance, or exactness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path.insert(0, str(ROOT / "scripts"))

from lib.pc98 import parse_mz  # noqa: E402

OFFICIAL_OUTER_SIZE = 597_930
EXPECTED_MEMBER_BASENAMES = {"GAME.BAT", "体験版.TXT"}
EXPECTED_TEXT_MARKERS = (
    "東方幻想郷".encode("cp932"),
    "体験版 ver1.00".encode("cp932"),
    "３面まで".encode("cp932"),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="th04-trial-intake-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def require_private_regular(path: Path) -> Path:
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(PRIVATE):
        raise ValueError("candidate input must be below .analysis")
    if path.is_symlink() or not resolved.is_file():
        raise ValueError("candidate input must be a regular non-symlink file")
    return resolved


def parse_lha_level01(raw: bytes, start: int) -> tuple[list[dict[str, object]], int]:
    """Parse the simple sequential level-0/1 LHA stream used by old DOS SFXes."""
    rows: list[dict[str, object]] = []
    pos = start
    while pos < len(raw):
        header_size = raw[pos]
        if header_size == 0:
            if not rows:
                raise ValueError("empty LHA stream")
            return rows, pos + 1
        if pos + 2 + header_size > len(raw):
            raise ValueError("truncated LHA header")
        stored_checksum = raw[pos + 1]
        calculated_checksum = sum(raw[pos + 2 : pos + 2 + header_size]) & 0xFF
        if stored_checksum != calculated_checksum:
            raise ValueError(
                f"LHA header checksum mismatch at 0x{pos:X}: "
                f"{stored_checksum:02X} != {calculated_checksum:02X}"
            )
        method_raw = raw[pos + 2 : pos + 7]
        if len(method_raw) != 5 or not (
            method_raw.startswith(b"-lh") and method_raw.endswith(b"-")
        ):
            raise ValueError(f"invalid LHA method at 0x{pos:X}: {method_raw!r}")
        method = method_raw.decode("ascii")
        packed = struct.unpack_from("<I", raw, pos + 7)[0]
        original = struct.unpack_from("<I", raw, pos + 11)[0]
        level = raw[pos + 20]
        if level not in (0, 1):
            raise ValueError(
                f"unsupported LHA level {level}; v500 intentionally accepts only 0/1"
            )
        name_len = raw[pos + 21]
        name_start = pos + 22
        name_end = name_start + name_len
        if name_end + 2 > pos + 2 + header_size:
            raise ValueError("LHA filename/CRC escapes header")
        name_raw = raw[name_start:name_end]
        name = name_raw.decode("cp932", errors="strict")
        crc = struct.unpack_from("<H", raw, name_end)[0]
        payload_start = pos + 2 + header_size
        payload_end = payload_start + packed
        if payload_end > len(raw):
            raise ValueError("truncated LHA payload")
        rows.append(
            {
                "name": name,
                "method": method,
                "packed_size": packed,
                "original_size": original,
                "level": level,
                "crc16": crc,
                "packed_sha256": sha(raw[payload_start:payload_end]),
            }
        )
        pos = payload_end
    raise ValueError("LHA terminator missing")


def basename_cp932(name: str) -> str:
    return name.replace("\\", "/").rsplit("/", 1)[-1].upper()


def run_archive_tool(command: list[str], *, binary: bool = False) -> bytes | str:
    done = subprocess.run(command, check=False, capture_output=True)
    if done.returncode:
        out = (done.stdout + done.stderr).decode("utf-8", errors="replace")
        raise ValueError(f"archive tool failed ({done.returncode}): {' '.join(command)}\n{out}")
    if binary:
        return done.stdout
    return done.stdout.decode("utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()

    candidate = require_private_regular(args.input)
    out = output_dir(args.output_dir)
    raw = candidate.read_bytes()

    if len(raw) != OFFICIAL_OUTER_SIZE:
        raise ValueError(
            f"candidate size {len(raw)} != published TH04 trial size {OFFICIAL_OUTER_SIZE}"
        )

    mz = parse_mz(raw)
    if not mz.valid:
        raise ValueError(f"candidate SFX MZ failed structure checks: {list(mz.errors)}")
    lha_start = mz.header.declared_file_size
    if lha_start >= len(raw):
        raise ValueError("candidate MZ has no appended archive")
    if raw[lha_start + 2 : lha_start + 5] != b"-lh":
        raise ValueError(
            "candidate appended bytes do not begin with an LHA member at MZ declared end"
        )

    members, lha_end = parse_lha_level01(raw, lha_start)
    names = [str(row["name"]) for row in members]
    basenames = {basename_cp932(name) for name in names}
    missing = sorted(EXPECTED_MEMBER_BASENAMES - basenames)
    if missing:
        raise ValueError(f"candidate archive misses expected trial members: {missing}")

    trailing = raw[lha_end:]
    if trailing and any(trailing):
        raise ValueError(
            f"candidate has {len(trailing)} nonzero/trailing byte(s) after LHA terminator"
        )

    archive_path = out / "trial-stream.lzh"
    archive_path.write_bytes(raw[lha_start:lha_end])

    lha = shutil.which("lha")
    seven = shutil.which("7z")
    if not lha or not seven:
        raise ValueError("v500 requires host lha and 7z readers")

    # Two independent readers must accept the stream; neither executes the SFX.
    lha_test = run_archive_tool([lha, "-tq2", str(archive_path)])
    seven_test = run_archive_tool([seven, "t", "-y", str(archive_path)])
    unpacked = run_archive_tool([lha, "-pq2", str(archive_path)], binary=True)
    assert isinstance(unpacked, bytes)

    marker_hits = {
        marker.decode("cp932"): (marker in unpacked) for marker in EXPECTED_TEXT_MARKERS
    }
    if not all(marker_hits.values()):
        raise ValueError(f"trial text marker mismatch: {marker_hits}")

    executable_members = [
        name
        for name in names
        if basename_cp932(name).endswith((".EXE", ".COM", ".BAT"))
    ]
    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 1998-07-02 public trial candidate intake",
        "candidate_sha256": sha(raw),
        "candidate_size": len(raw),
        "published_outer_size_constraint": OFFICIAL_OUTER_SIZE,
        "candidate_canonicality": "candidate-public-trial-structural",
        "official_pristine_identity_proved": False,
        "sfx": {
            "declared_mz_size": mz.header.declared_file_size,
            "header_size": mz.header.header_size,
            "relocation_count": len(mz.relocations),
            "entry_cs": mz.header.initial_relative_cs,
            "entry_ip": mz.header.initial_ip,
            "program_sha256": sha(mz.program_image),
        },
        "lha": {
            "offset": lha_start,
            "end": lha_end,
            "stream_sha256": sha(raw[lha_start:lha_end]),
            "member_count": len(members),
            "members": members,
            "expected_member_basenames": sorted(EXPECTED_MEMBER_BASENAMES),
            "executable_members": executable_members,
            "decompressed_stream_sha256": sha(unpacked),
            "trial_text_marker_hits": marker_hits,
        },
        "readers": {
            "lha_path": lha,
            "lha_sha256": file_sha(Path(lha)),
            "lha_test_output": str(lha_test).strip(),
            "7z_path": seven,
            "7z_sha256": file_sha(Path(seven)),
            "7z_test_output_tail": str(seven_test).splitlines()[-12:],
        },
        "conclusion": (
            "The candidate has the published 597930-byte TH04 trial outer size, "
            "a valid DOS MZ self-extractor, a CRC-valid appended LHA stream accepted "
            "by two independent readers, the expected GAME.BAT and 体験版.TXT members, "
            "and decompressed TH04 trial ver1.00/stage-3 markers. Its SHA-256 is now "
            "stable for later semantic comparison."
        ),
        "limit": (
            "No authoritative historical digest is available in this probe. Passing "
            "does not prove the candidate is an official pristine download, does not "
            "make it a target Oracle, and grants no TH04 retail source/exactness credit."
        ),
    }
    receipt_path = out / "receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "receipt": str(receipt_path),
                "receipt_sha256": sha(receipt_path.read_bytes()),
                "candidate_sha256": receipt["candidate_sha256"],
                "member_count": len(members),
                "executable_members": executable_members,
                "canonicality": receipt["candidate_canonicality"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
