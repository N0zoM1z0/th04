#!/usr/bin/env python3
"""Package the maintained-source TH04 invincible build for Windows DOSBox-X."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/probes"))
from inspect_th04_handoff_trace import game_file  # noqa: E402
from prepare_product_hdi import Fat12, PRODUCTS, replace_file, u16  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def product_name(name: str) -> bytes:
    stem, extension = name.upper().split(".")
    return (stem.ljust(8) + extension.ljust(3)).encode("ascii")


def render_config(reference: bytes) -> bytes:
    text = reference.decode("utf-8-sig")
    old = "imgmount c jp.hdi"
    if text.count(old) != 1 or "machine=pc98" not in text:
        raise ValueError("Windows TH04 JP config format changed")
    return text.replace(old, "imgmount c play.hdi", 1).encode("ascii")


def write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex[:8])
    temporary.write_bytes(data)
    temporary.replace(path)
    if path.read_bytes() != data:
        raise ValueError(f"copy readback failed: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--emulator-dir", type=Path, required=True,
                        help="Windows collection's dosbox-x directory")
    parser.add_argument("--build-dir", type=Path,
                        default=ROOT / ".analysis/build/th04-invincible")
    parser.add_argument("--image", type=Path, default=ROOT /
                        ".analysis/runtime/candidates/th04-invincible-play/play.hdi")
    parser.add_argument("--update", action="store_true",
                        help="refresh an existing package while preserving its saves")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    emulator = args.emulator_dir.resolve()
    build = args.build_dir.resolve()
    manifest = json.loads((build / "build.json").read_text(encoding="utf-8"))
    if manifest.get("variant") != "invincible-main" or set(manifest["products"]) != set(PRODUCTS):
        raise ValueError("expected a complete invincible four-product build")
    product_bytes = {}
    records = {}
    for artifact, name in PRODUCTS.items():
        data = (build / name).read_bytes()
        record = manifest["products"][artifact]
        if (record["file"] != name or record["size"] != len(data)
                or record["sha256"] != sha(data) or not parse_mz(data).valid):
            raise ValueError(f"unverified product: {name}")
        product_bytes[artifact] = data
        records[artifact] = {"file": name, "size": len(data), "sha256": sha(data)}

    prior_receipt = output / "package.json"
    if output.exists() and any(output.iterdir()):
        if not args.update or not prior_receipt.is_file():
            parser.error("nonempty package requires --update and its prior package.json")
        prior = json.loads(prior_receipt.read_text(encoding="utf-8"))
        if prior.get("variant") != "invincible-main":
            raise ValueError("existing package is not the invincible variant")
        source = (output / "play.hdi").read_bytes()
        expected = prior["products"]
    else:
        source = args.image.resolve().read_bytes()
        expected = records
    if set(expected) != set(PRODUCTS):
        raise ValueError("existing image receipt lacks a product")
    if len(source) != 21415936:
        raise ValueError("unexpected TH04 HDI size")
    for artifact, record in expected.items():
        name = PRODUCTS[artifact]
        embedded = game_file(source, product_name(name))
        if len(embedded) != record["size"] or sha(embedded) != record["sha256"]:
            raise ValueError(f"existing image {name} differs from its package receipt")

    fs = Fat12(bytearray(source))
    folder = fs.find_entry([fs.root], b"GENSO      ")
    directory = [fs.cluster_offset(cluster)
                 for cluster in fs.chain(u16(fs.image, folder + 26))]
    for artifact, name in PRODUCTS.items():
        entry = fs.find_entry(directory, product_name(name))
        replace_file(fs, entry, product_bytes[artifact])
    image = bytes(fs.image)
    for artifact, name in PRODUCTS.items():
        if game_file(image, product_name(name)) != product_bytes[artifact]:
            raise ValueError(f"image readback failed: {name}")

    exe = (emulator / "dosbox-x.exe").read_bytes()
    font = (emulator / "font_jp.bmp").read_bytes()
    config = render_config((emulator / "th04_jp.conf").read_bytes())
    launcher = (b'@echo off\r\ncd /d "%~dp0"\r\n'
                b'start "" "%~dp0dosbox-x.exe" -conf "%~dp0th04.conf"\r\n')
    output.mkdir(parents=True, exist_ok=True)
    (output / "bin").mkdir(exist_ok=True)
    for artifact, name in PRODUCTS.items():
        write_atomic(output / "bin" / name, product_bytes[artifact])
    write_atomic(output / "play.hdi", image)
    write_atomic(output / "dosbox-x.exe", exe)
    write_atomic(output / "FREECG98.bmp", font)
    write_atomic(output / "th04.conf", config)
    write_atomic(output / "start-th04.bat", launcher)
    receipt = {
        "schema_version": 1,
        "variant": "invincible-main",
        "build_run_id": manifest["run_id"],
        "products": records,
        "source_hdi_sha256": sha(source),
        "play_hdi_sha256_at_export": sha(image),
        "dosbox_x_sha256": sha(exe),
        "font_sha256": sha(font),
        "config_sha256": sha(config),
        "launch": "start-th04.bat",
    }
    write_atomic(prior_receipt, (json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
    print(f"Packaged {', '.join(PRODUCTS.values())} in {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, UnicodeError) as error:
        print(f"Windows play export failed: {error}", file=sys.stderr)
        raise SystemExit(1)
