#!/usr/bin/env python3
"""Prepare a private seeded Good Ending, with source-built MAINE/OP/ZUN.

MAIN is replaced by an openly labeled diagnostic COM, not a gameplay product.
The original image supplies read-only game assets and the DOS startup files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]
from lib.pc98 import parse_mz
from prepare_product_hdi import Fat12, PRODUCTS, replace_file, u16
from inspect_th04_handoff_trace import game_file
from export_windows_play import product_name


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--character", choices=("reimu", "marisa"), required=True)
    parser.add_argument("--rank", type=int, choices=range(4), required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(ROOT / ".analysis/runtime/candidates"):
        parser.error("use a new private runtime directory")
    build = args.build_dir.resolve()
    manifest = json.loads((build / "build.json").read_text())
    if set(manifest["products"]) != set(PRODUCTS):
        raise ValueError("complete four-product build required")
    products = {}
    for artifact, name in PRODUCTS.items():
        data = (build / name).read_bytes()
        record = manifest["products"][artifact]
        if len(data) != record["size"] or sha(data) != record["sha256"] or not parse_mz(data).valid:
            raise ValueError(f"native product identity/format drift: {name}")
        products[artifact] = data
    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    image = (ROOT / runtime["image"]["path"]).read_bytes()
    if len(image) != runtime["image"]["size"] or sha(image) != runtime["image"]["sha256"]:
        raise ValueError("pinned original HDI identity drift")
    nasm = Path(shutil.which("nasm") or "")
    if not nasm.is_file():
        raise ValueError("NASM diagnostic compiler unavailable")
    fixture = ROOT / "scripts/runtime/fixtures/good_ending.asm"
    output.mkdir(parents=True)
    (output / "main-fixture.asm").write_bytes(fixture.read_bytes())
    command = [str(nasm), "-f", "bin", "-DCHAR_ASCII=" + str(48 + (args.character == "marisa")),
               "-DRANK=" + str(args.rank), str(output / "main-fixture.asm"),
               "-o", str(output / "main-fixture.com")]
    subprocess.run(command, check=True)
    products["main"] = (output / "main-fixture.com").read_bytes()
    fs = Fat12(bytearray(image))
    folder = fs.find_entry([fs.root], b"GENSO      ")
    directory = [fs.cluster_offset(c) for c in fs.chain(u16(fs.image, folder + 26))]
    for artifact, name in PRODUCTS.items():
        replace_file(fs, fs.find_entry(directory, product_name(name)), products[artifact])
    bat = game_file(image, b"GAME    BAT")
    if bat.count(b"\r\nop\r\n") != 5:
        raise ValueError("pinned GAME.BAT startup shape changed")
    bat = bat.replace(b"\r\nop\r\n", b"\r\nmain\r\n")
    replace_file(fs, fs.find_entry(directory, b"GAME    BAT"), bat)
    autoexec = (b"@ECHO OFF\r\nPATH A:\\DOS;A:\\\r\nSET TEMP=A:\\DOS\r\n"
                b"SET DOSDIR=A:\\DOS\r\nCD \\GENSO\r\n"
                b"ECHO START > A:\\DIAG.TXT\r\nCALL GAME.BAT\r\n"
                b"ECHO EXIT >> A:\\DIAG.TXT\r\n\x1a")
    replace_file(fs, fs.find_entry([fs.root], b"AUTOEXECBAT"), autoexec)
    final = bytes(fs.image)
    for artifact, name in PRODUCTS.items():
        if game_file(final, product_name(name)) != products[artifact]:
            raise ValueError("diagnostic image product readback failed")
    (output / "diagnostic.hdi").write_bytes(final)
    receipt = dict(schema_version=1, artifact="th04-game", startup="game-bat-direct-private-main-com",
                   artifact_source="maintained-source OP/MAINE/ZUN; MAIN is a diagnostic resident fixture",
                   scope="Seeded Good Ending through real MAINE; bypasses gameplay and OP initialization. Sound mode is the resident's zero default, using frame-based waits.",
                   character=args.character, rank=args.rank, build_run_id=manifest["run_id"],
                   products={a: dict(file=PRODUCTS[a], size=len(b), sha256=sha(b)) for a, b in products.items()},
                   original_hdi_sha256=sha(image), diagnostic_hdi_sha256=sha(final),
                   fixture_sha256=sha(fixture.read_bytes()), game_bat_sha256=sha(bat),
                   nasm_sha256=sha(nasm.read_bytes()), command=command)
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Prepared private {args.character} rank {args.rank} Good Ending: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
