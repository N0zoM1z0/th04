#!/usr/bin/env python3
"""Install rebuilt TH04 products into a disposable original-data PC-98 image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/probes"))
from prepare_th04_maine_diagnostic_hdi import AUTOEXEC_PREFIX, Fat12, sha, u16, u32
from inspect_th04_handoff_trace import decode_config, game_file
from lib.pc98 import parse_mz

PRODUCTS = {"main": "MAIN.EXE", "op": "OP.EXE", "maine": "MAINE.EXE", "zun": "ZUN.COM"}


def replace_file(fs: Fat12, entry: int, contents: bytes) -> None:
    old_chain = fs.chain(u16(fs.image, entry + 26))
    needed = (len(contents) + fs.cluster_bytes - 1) // fs.cluster_bytes
    if needed < 1:
        raise ValueError("empty product file")
    chain = old_chain[:needed]
    if len(chain) < needed:
        available = [k for k in range(2, fs.max_cluster + 1) if fs.fat(k) == 0]
        if len(available) < needed - len(chain):
            raise ValueError("insufficient FAT12 space for rebuilt products")
        chain.extend(available[:needed - len(chain)])
    for cluster in old_chain[needed:]:
        fs.set_fat(cluster, 0)
    for i, cluster in enumerate(chain):
        fs.set_fat(cluster, chain[i + 1] if i + 1 < len(chain) else 0xFFF)
        offset = fs.cluster_offset(cluster)
        block = contents[i * fs.cluster_bytes:(i + 1) * fs.cluster_bytes]
        fs.image[offset:offset + fs.cluster_bytes] = block.ljust(fs.cluster_bytes, b"\0")
    fs.image[entry + 26:entry + 28] = chain[0].to_bytes(2, "little")
    fs.image[entry + 28:entry + 32] = len(contents).to_bytes(4, "little")
    if fs.file_bytes(chain[0], len(contents)) != contents:
        raise ValueError("FAT12 replacement readback failed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=ROOT / ".analysis/build/th04")
    parser.add_argument("--products", nargs="+", choices=PRODUCTS, default=list(PRODUCTS))
    parser.add_argument("--original", action="store_true",
                        help="prepare the pinned original executables as a runtime baseline")
    parser.add_argument("--lives", type=int, choices=range(1, 7),
                        help="starting configuration lives in this disposable image")
    parser.add_argument("--rank", type=int, choices=range(4),
                        help="starting configuration rank: Easy=0 through Lunatic=3")
    parser.add_argument("--bombs", type=int, choices=range(3),
                        help="starting configuration bombs in this disposable image")
    parser.add_argument("--config-from-run", type=Path,
                        help="start with the saved configuration from an attested completed run")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(ROOT / ".analysis/runtime/candidates"):
        parser.error("use a new directory below .analysis/runtime/candidates")
    build = args.build_dir.resolve()
    manifest = ({} if args.original else
                json.loads((build / "build.json").read_text(encoding="utf-8")))
    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    image_path = ROOT / runtime["image"]["path"]
    original = image_path.read_bytes()
    if len(original) != runtime["image"]["size"] or sha(original) != runtime["image"]["sha256"]:
        raise ValueError("original-data image identity drift")
    targets = tomllib.loads((ROOT / "config/targets.toml").read_text())
    targets = {r["id"]: r for r in targets["artifacts"]}
    fs = Fat12(bytearray(original))
    directory = fs.find_entry([fs.root], b"GENSO      ")
    offsets = [fs.cluster_offset(k) for k in fs.chain(u16(fs.image, directory + 26))]
    installed = {}
    for product in dict.fromkeys(args.products):
        name = PRODUCTS[product]
        base, ext = name.split(".")
        entry = fs.find_entry(offsets, f"{base:<8}{ext}".encode("ascii"))
        target = targets["th04-" + product]
        old = fs.file_bytes(u16(fs.image, entry + 26), u32(fs.image, entry + 28))
        if len(old) != target["size"] or sha(old) != target["sha256"]:
            raise ValueError(f"original image {name} does not match pinned target")
        if not parse_mz(old).valid:
            raise ValueError(f"original image {name} format failed")
        if args.original:
            continue
        data = (build / name).read_bytes()
        record = manifest["products"][product]
        if sha(data) != record["sha256"] or len(data) != record["size"]:
            raise ValueError(f"{name} differs from build receipt")
        if not parse_mz(data).valid:
            raise ValueError(f"{name} is not a valid executable")
        replace_file(fs, entry, data)
        installed[product] = record
    starting_options = None
    if any(value is not None for value in (
            args.rank, args.lives, args.bombs, args.config_from_run)):
        entry = fs.find_entry(offsets, b"MIKO    CFG")
        config = fs.file_bytes(u16(fs.image, entry + 26), u32(fs.image, entry + 28))
        if len(config) != 10:
            raise ValueError("expected ten-byte TH04 configuration")
        updated = bytearray(config)
        config_source = None
        if args.config_from_run is not None:
            run = args.config_from_run.resolve()
            if not run.is_relative_to(ROOT / ".analysis/runtime/candidates"):
                parser.error("configuration source must be a private runtime run")
            run_receipt_data = (run / "receipt.json").read_bytes()
            run_receipt = json.loads(run_receipt_data)
            executed = (run / "execution.hdi").read_bytes()
            if sha(executed) != run_receipt["executed_hdi_sha256"]:
                raise ValueError("configuration source image identity drift")
            saved = game_file(executed, b"MIKO    CFG")
            decoded = decode_config(saved)
            if (not decoded["checksum_valid"] or not decoded["options_valid"]
                    or decoded["resident_segment"] != 0 or decoded["debug"] != 0
                    or b"EXIT" not in bytes.fromhex(run_receipt["diagnostic_marker_hex"] or "")):
                raise ValueError("configuration source is not a valid saved DOS-exit config")
            updated = bytearray(saved)
            config_source = {"run": str(run), "receipt_sha256": sha(run_receipt_data),
                             "executed_hdi_sha256": sha(executed), "config_sha256": sha(saved)}
        if args.rank is not None:
            updated[0] = args.rank
        if args.lives is not None:
            updated[1] = args.lives
        if args.bombs is not None:
            updated[2] = args.bombs
        updated[9] = sum(updated[:6]) & 255
        replace_file(fs, entry, updated)
        starting_options = {"options_hex": bytes(updated[:6]).hex(),
                            "rank": updated[0], "lives": updated[1], "bombs": updated[2],
                            "config_source": config_source,
                            "before_sha256": sha(config), "after_sha256": sha(updated)}
    autoexec = AUTOEXEC_PREFIX + b"CALL GAME.BAT\r\nECHO EXIT >> A:\\DIAG.TXT\r\n\x1a"
    replace_file(fs, fs.find_entry([fs.root], b"AUTOEXECBAT"), autoexec)
    if sha(image_path.read_bytes()) != runtime["image"]["sha256"]:
        raise ValueError("original-data image changed during preparation")
    output.mkdir(parents=True)
    (output / "diagnostic.hdi").write_bytes(fs.image)
    (output / "receipt.json").write_text(json.dumps({
        "schema_version": 1, "artifact": "th04-game", "startup": "game-bat",
        "scope": ("pinned original game runtime baseline" if args.original else
                  "rebuilt products with pinned original game data"),
        "artifact_source": ("pinned originals" if args.original else
                            manifest.get("artifact_source", "TH04 maintained source")),
        "products": installed,
        "starting_options": starting_options,
        "original_hdi_sha256": runtime["image"]["sha256"],
        "diagnostic_hdi_sha256": sha(fs.image),
    }, indent=2) + "\n")
    print(output / "diagnostic.hdi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
