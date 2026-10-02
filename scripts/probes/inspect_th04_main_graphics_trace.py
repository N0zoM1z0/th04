#!/usr/bin/env python3
"""Check MPN and four-plane VRAM checkpoints from a private MAIN run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tomllib

from prepare_th04_maine_diagnostic_hdi import Fat12, u16, u32
from probe_th04_pf_archive import ARCHIVES, parse_archive

ROOT = Path(__file__).resolve().parents[2]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def game_files(fs: Fat12) -> list[int]:
    entry = fs.find_entry([fs.root], b"GENSO      ")
    return [fs.cluster_offset(k) for k in fs.chain(u16(fs.image, entry + 26))]


def read_file(fs: Fat12, directory: list[int], name: bytes) -> bytes:
    entry = fs.find_entry(directory, name)
    return fs.file_bytes(u16(fs.image, entry + 26), u32(fs.image, entry + 28))


def tile_bytes(vram: bytes, left_byte: int, top: int) -> bytes:
    return b"".join(vram[plane * 32000 + (top + y) * 80 + left_byte:
                         plane * 32000 + (top + y) * 80 + left_byte + 2]
                    for plane in range(4) for y in range(16))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--mpn", default="ST00.MPN")
    parser.add_argument("--require-correct", action="store_true")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    if not run.is_relative_to(ROOT / ".analysis/runtime/candidates"):
        parser.error("use a private runtime directory")
    receipt = json.loads((run / "receipt.json").read_text())
    executed = (run / "execution.hdi").read_bytes()
    if sha(executed) != receipt["executed_hdi_sha256"]:
        raise ValueError("executed image identity drift")
    fs = Fat12(bytearray(executed))
    directory = game_files(fs)
    dumps = {name: read_file(fs, directory, name) for name in
             (b"MPNDUMP BIN", b"VRAMC   BIN", b"VRAMT   BIN")}
    loaded, cache, rendered = dumps.values()
    if (len(loaded), len(cache), len(rendered)) != (240, 128000, 128000):
        raise ValueError("missing or incomplete graphics checkpoints")

    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    original = (ROOT / runtime["image"]["path"]).read_bytes()
    if sha(original) != runtime["image"]["sha256"]:
        raise ValueError("original-data image identity drift")
    baseline = Fat12(bytearray(original))
    archive = ARCHIVES["main"]
    packed = read_file(baseline, game_files(baseline), archive["fat_name"])
    if sha(packed) != archive["sha256"]:
        raise ValueError("original MAIN archive identity drift")
    _, members = parse_archive(packed, "main", archive)
    mpn = members[args.mpn]
    count = mpn[4] + 1
    if len(mpn) != 54 + count * 128 or count > 100:
        raise ValueError("unsupported MPN geometry")
    images = [mpn[54 + i * 128:54 + (i + 1) * 128] for i in range(count)]
    mismatches = [(i, plane) for i, image in enumerate(images)
                  for plane in range(4)
                  if tile_bytes(cache, 72 + (i // 25) * 2, (i % 25) * 16)
                     [plane * 32:(plane + 1) * 32] != image[plane * 32:(plane + 1) * 32]]
    expected_tiles = set(images)
    broadcast_tiles = {image[:32] * 4 for image in images}
    tiles = [tile_bytes(rendered, 4 + x * 2, y * 16)
             for y in range(25) for x in range(24)]
    result = {
        "scope": "loaded MPN, cached planes and initial tile-copy transformation",
        "run_receipt_sha256": sha((run / "receipt.json").read_bytes()),
        "mpn": args.mpn, "mpn_sha256": sha(mpn),
        "checkpoint_sha256": {name.decode(): sha(data) for name, data in dumps.items()},
        "loaded_count_correct": u16(loaded, 4) == count - 1,
        "loaded_palette_correct": loaded[6:54] == mpn[6:54],
        "first_image_correct": loaded[64:192] == images[0],
        "active_palette_correct": loaded[192:240] == mpn[6:54],
        "cache_plane_mismatches": mismatches,
        "rendered_tiles": len(tiles),
        "rendered_tiles_from_mpn": sum(tile in expected_tiles for tile in tiles),
        "rendered_tiles_broadcasting_blue": sum(tile in broadcast_tiles for tile in tiles),
    }
    result["correct"] = (all(result[key] for key in (
        "loaded_count_correct", "loaded_palette_correct", "first_image_correct",
        "active_palette_correct")) and not mismatches
        and result["rendered_tiles_from_mpn"] == len(tiles))
    (run / "graphics.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    return int(args.require_correct and not result["correct"])


if __name__ == "__main__":
    raise SystemExit(main())
