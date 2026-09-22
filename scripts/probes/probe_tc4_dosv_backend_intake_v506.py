#!/usr/bin/env python3
"""Bind the same-media TC4J DOS/V integrated compiler as a distinct backend.

This probe is intentionally structural. It re-extracts the PC-98 and DOS/V
TC.EXE binaries from the pinned Turbo C++ 4.0J media, verifies their identities,
and compares their 16-bit NE segment inventories. It does not claim that the
DOS/V backend can currently be executed by an attested runner, and it grants no
TH04 source or exactness credit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
MEDIA = PRIVATE / "toolchain/media/tc40j/software/borland-4.0j"
INSTALLED = PRIVATE / "toolchain/installed/tc40j"
MSDOS = ROOT / "_reference/ReC98/bin/msdos.exe"

EXPECTED = {
    "TCDOSV.PAK": "d8fa9bded6d4b7dd1ac65508e525c3ee04be2a85547887bcdd17293a5f15bfef",
    "TCPC98.PAK": "abdeac6cf17e76c096848ed3769c7b40cd9d535e0cf7aab937a44b4408715261",
    "UNPAK.EXE": "6bbe916fb74028ee77ecbb3d0cb81011648ea89ade5b726d6dc25ee00aae6c87",
    "DPMI16BI.OVL": "8cbd449979801b74771c8f651450f0b029b311410d0fd7703e7c7c2a295830c8",
    "RTM.EXE": "11ea23bebfdbe1eefb4faced127d07000089c89954da4a2fa597b4ac98fd9488",
    "msdos.exe": "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02",
    "TC.EXE:dosv": "9bc31d09ae8fb5b776269142e7785f5a7c7f06ca603d1d8ced71a116078a2aa2",
    "TC.EXE:pc98": "91d410850da69c6ff894f902d1b5610f04b5e2b6d0097b2a11cf2fafa54f14b4",
}
EXPECTED_SIZES = {
    "TC.EXE:dosv": 1544672,
    "TC.EXE:pc98": 1546720,
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-dosv-backend-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def require_hash(path: Path, expected: str, label: str) -> str:
    actual = file_sha(path)
    if actual != expected:
        raise ValueError(f"{label} identity drift: {actual}")
    return actual


def extract(package: Path, destination: Path, work: Path) -> Path:
    destination.mkdir(parents=True)
    shutil.copy2(MEDIA / "UNPAK.EXE", work / "UNPAK.EXE")
    shutil.copy2(package, work / package.name)
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(PRIVATE / "toolchain/wineprefix"),
        WINEDEBUG="-all",
    )
    done = subprocess.run(
        [
            "wine",
            str(MSDOS),
            "-e",
            "-x",
            "UNPAK.EXE",
            "x",
            package.name,
            destination.name,
        ],
        cwd=work,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    (work / f"{package.stem}.unpak.log").write_text(done.stdout + done.stderr)
    if done.returncode:
        raise RuntimeError(f"UNPAK failed for {package.name}: {done.stdout}{done.stderr}")
    tc = destination / "TC.EXE"
    if not tc.is_file():
        raise ValueError(f"{package.name} did not extract TC.EXE")
    return tc


def parse_ne(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    if raw[:2] != b"MZ":
        raise ValueError(f"{path.name}: missing MZ stub")
    ne_offset = struct.unpack_from("<I", raw, 0x3C)[0]
    if ne_offset + 0x40 > len(raw) or raw[ne_offset:ne_offset + 2] != b"NE":
        raise ValueError(f"{path.name}: missing NE header")
    segment_count = struct.unpack_from("<H", raw, ne_offset + 0x1C)[0]
    segment_table_offset = struct.unpack_from("<H", raw, ne_offset + 0x22)[0]
    alignment_shift = struct.unpack_from("<H", raw, ne_offset + 0x32)[0]
    if not segment_count or segment_count > 4096:
        raise ValueError(f"{path.name}: implausible NE segment count {segment_count}")
    table = ne_offset + segment_table_offset
    if table + segment_count * 8 > len(raw):
        raise ValueError(f"{path.name}: truncated NE segment table")

    segments = []
    for index in range(segment_count):
        sector, length_word, flags, min_alloc = struct.unpack_from(
            "<HHHH", raw, table + index * 8
        )
        size = length_word or 0x10000
        offset = sector << alignment_shift
        end = offset + size
        if offset <= 0 or end > len(raw):
            raise ValueError(
                f"{path.name}: segment {index + 1} escapes file "
                f"(0x{offset:X}..0x{end:X})"
            )
        payload = raw[offset:end]
        segments.append(
            {
                "index": index + 1,
                "offset": offset,
                "size": size,
                "flags": f"0x{flags:04X}",
                "kind": "data" if (flags & 1) else "code",
                "min_alloc": min_alloc,
                "sha256": sha(payload),
            }
        )
    return {
        "file_size": len(raw),
        "sha256": sha(raw),
        "ne_offset": ne_offset,
        "linker_version": raw[ne_offset + 2],
        "linker_revision": raw[ne_offset + 3],
        "segment_count": segment_count,
        "alignment_shift": alignment_shift,
        "code_segment_count": sum(s["kind"] == "code" for s in segments),
        "data_segment_count": sum(s["kind"] == "data" for s in segments),
        "segments": segments,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = make_output(args.output_dir)

    subprocess.run(
        [
            sys.executable,
            "scripts/attest_toolchain.py",
            "--identity-only",
            "--surface",
            "tc40j-media",
            "--surface",
            "tc40j-bin",
            "--surface",
            "msdos-player-p0281",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )

    inputs = {
        "TCDOSV.PAK": MEDIA / "TCDOSV.PAK",
        "TCPC98.PAK": MEDIA / "TCPC98.PAK",
        "UNPAK.EXE": MEDIA / "UNPAK.EXE",
        "DPMI16BI.OVL": INSTALLED / "BIN/DPMI16BI.OVL",
        "RTM.EXE": INSTALLED / "BIN/RTM.EXE",
        "msdos.exe": MSDOS,
    }
    input_hashes = {
        label: require_hash(path, EXPECTED[label], label)
        for label, path in inputs.items()
    }

    work = out / "extract"
    work.mkdir()
    dosv = extract(MEDIA / "TCDOSV.PAK", work / "dosv", work)
    pc98 = extract(MEDIA / "TCPC98.PAK", work / "pc98", work)
    require_hash(dosv, EXPECTED["TC.EXE:dosv"], "DOS/V TC.EXE")
    require_hash(pc98, EXPECTED["TC.EXE:pc98"], "PC-98 TC.EXE")
    if dosv.stat().st_size != EXPECTED_SIZES["TC.EXE:dosv"]:
        raise ValueError("DOS/V TC.EXE size drift")
    if pc98.stat().st_size != EXPECTED_SIZES["TC.EXE:pc98"]:
        raise ValueError("PC-98 TC.EXE size drift")
    if dosv.read_bytes() == pc98.read_bytes():
        raise ValueError("DOS/V and PC-98 TC.EXE unexpectedly identical")

    dosv_ne = parse_ne(dosv)
    pc98_ne = parse_ne(pc98)
    dosv_code = {s["sha256"] for s in dosv_ne["segments"] if s["kind"] == "code"}
    pc98_code = {s["sha256"] for s in pc98_ne["segments"] if s["kind"] == "code"}
    shared_code = sorted(dosv_code & pc98_code)
    positional_equal = sum(
        a["sha256"] == b["sha256"]
        for a, b in zip(dosv_ne["segments"], pc98_ne["segments"])
    )

    bundle = {
        "input_hashes": input_hashes,
        "expected_tc_hashes": {
            "dosv": EXPECTED["TC.EXE:dosv"],
            "pc98": EXPECTED["TC.EXE:pc98"],
        },
        "ne": {"dosv": dosv_ne, "pc98": pc98_ne},
        "shared_code_segment_hashes": shared_code,
        "positionally_equal_segment_count": positional_equal,
    }
    input_bundle_sha256 = sha(
        json.dumps(
            {
                "probe_sha256": sha(Path(__file__).read_bytes()),
                "inputs": input_hashes,
            },
            sort_keys=True,
        ).encode()
    )
    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J same-media DOS/V integrated compiler backend intake",
        "probe_sha256": sha(Path(__file__).read_bytes()),
        "input_bundle_sha256": input_bundle_sha256,
        **bundle,
        "conclusion": (
            "The pinned TC4J media contains a DOS/V TC.EXE that is reproducibly "
            "extractable from TCDOSV.PAK and is byte-distinct from the already "
            "tested PC-98 TC.EXE from TCPC98.PAK. Both are 16-bit NE integrated "
            "compiler executables and contain the TC86 Borland C++ 4.02 producer "
            "identity. This establishes a genuinely distinct same-media backend "
            "candidate only; it does not establish its code generation."
        ),
        "dynamic_status": (
            "unattested: no currently accepted runner has produced a valid OMF "
            "from the DOS/V integrated compiler"
        ),
        "exactness_credit": 0,
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(path),
                "receipt_sha256": sha(path.read_bytes()),
                "probe_sha256": receipt["probe_sha256"],
                "input_bundle_sha256": input_bundle_sha256,
                "dosv_tc_sha256": dosv_ne["sha256"],
                "pc98_tc_sha256": pc98_ne["sha256"],
                "dosv_segments": dosv_ne["segment_count"],
                "pc98_segments": pc98_ne["segment_count"],
                "shared_code_segment_count": len(shared_code),
                "positionally_equal_segment_count": positional_equal,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
