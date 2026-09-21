#!/usr/bin/env python3
"""Scan every registered TH01-TH05 target for a semantic carpet-column analogue.

The signature intentionally ignores TH04-specific addresses, strides, and array
sizes. It looks for a word column-fill loop followed nearby by a byte dirty-flag
column-fill loop where both terminate at the same limit and the word stride is
exactly twice the byte stride. DIET targets are restored with the pinned local
DIET/DOSBox-X toolchain. This is provenance evidence only.
"""
from __future__ import annotations

import argparse, hashlib, json, re, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import load_target_manifest, read_verified_artifact  # noqa: E402
from probe_th04_final_blocker_crossartifact import restore_diet  # noqa: E402

WORD_LOOP = re.compile(
    rb"\x89\x85(..)\x83\xc7(.)\x81\xff(..)\x72(.)", re.S
)
DIRTY_LOOP = re.compile(
    rb"\xc6\x85(..)\x01\x83\xc7(.)\x81\xff(..)\x72(.)", re.S
)
EXPECTED = {
    "th04-main": [
        {
            "word_offset": 0xEABB,
            "dirty_offset": 0xEACA,
            "word_stride": 0x40,
            "dirty_stride": 0x20,
            "limit": 0x640,
            "word_disp": 0x4D40,
            "dirty_disp": 0x4700,
        }
    ]
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="carpet-lineage-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def program_image(raw: bytes) -> tuple[bytes, str, int]:
    if raw[:2] == b"MZ":
        mz = parse_mz(raw)
        if not mz.valid:
            raise ValueError("invalid MZ")
        return mz.program_image, "mz", len(mz.relocations)
    return raw, "flat", 0


def scan(image: bytes) -> list[dict[str, int]]:
    words = list(WORD_LOOP.finditer(image))
    dirties = list(DIRTY_LOOP.finditer(image))
    out: list[dict[str, int]] = []
    for w in words:
        word_stride = w.group(2)[0]
        word_limit = int.from_bytes(w.group(3), "little")
        for d in dirties:
            if not (w.start() < d.start() <= (w.start() + 96)):
                continue
            dirty_stride = d.group(2)[0]
            dirty_limit = int.from_bytes(d.group(3), "little")
            if word_stride != ((dirty_stride * 2) & 0xFF):
                continue
            if word_limit != dirty_limit:
                continue
            out.append({
                "word_offset": w.start(),
                "dirty_offset": d.start(),
                "word_stride": word_stride,
                "dirty_stride": dirty_stride,
                "limit": word_limit,
                "word_disp": int.from_bytes(w.group(1), "little"),
                "dirty_disp": int.from_bytes(d.group(1), "little"),
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = new_output(args.output_dir)
    artifacts = load_target_manifest(ROOT / "config/targets.toml")["artifacts"]
    results: dict[str, list[dict[str, int]]] = {}
    identities: dict[str, dict[str, object]] = {}
    restored_count = 0
    for artifact in artifacts:
        aid = str(artifact["id"])
        packed = read_verified_artifact(ROOT, artifact)
        raw = packed
        restore_meta = None
        if len(raw) >= 0x20 and raw[0x1C:0x20].lower() == b"diet":
            raw, restore_meta = restore_diet(artifact, packed, output)
            restored_count += 1
        image, fmt, reloc_count = program_image(raw)
        hits = scan(image)
        if hits:
            results[aid] = hits
        identities[aid] = {
            "target_sha256": str(artifact["sha256"]),
            "container_was_diet": restore_meta is not None,
            "restored_sha256": restore_meta["restored_sha256"] if restore_meta else None,
            "program_format": fmt,
            "program_image_size": len(image),
            "program_image_sha256": sha(image),
            "relocation_count": reloc_count,
            "semantic_pair_count": len(hits),
        }
    if len(identities) != 20 or restored_count != 8:
        raise ValueError("registered corpus/DIET partition drift")
    if results != EXPECTED:
        raise ValueError(f"semantic lineage result drift: {results}")
    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 carpet semantic cross-game lineage negative",
        "registered_artifact_count": len(identities),
        "diet_restored_artifact_count": restored_count,
        "signature": (
            "word [DI+disp16] column fill using ADD DI,stride / CMP DI,limit / JB, "
            "followed within 96 bytes by byte [DI+disp16]=1 dirty fill with the "
            "same limit and exactly half the stride"
        ),
        "hits": results,
        "artifacts": identities,
        "conclusion": (
            "Only TH04 MAIN contains the generalized paired column-fill architecture; "
            "no registered TH01/TH02/TH03/TH05 OP/MAIN/MAINE/ZUN image supplies an "
            "independent semantic analogue with different constants."
        ),
        "limit": (
            "This is stronger semantic-shape negative evidence, not a universal source "
            "language proof and not permission to promote target-derived inline assembly."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp.read_bytes()),
        "hits": results,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
