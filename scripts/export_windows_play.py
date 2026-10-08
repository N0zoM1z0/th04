#!/usr/bin/env python3
"""Package a maintained-source TH04 build for Windows DOSBox-X."""

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
from product_input_fingerprint import source_fingerprint  # noqa: E402


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


def performance_config(reference: bytes) -> bytes:
    old = b"cycles=15000"
    if reference.count(old) != 1:
        raise ValueError("Windows TH04 JP CPU setting changed")
    return reference.replace(old, b"cycles=24000", 1)


def package_reference_config(path: Path, config: bytes) -> bytes:
    """Recover the reference budget when a demo package omits that profile."""
    if path.is_file():
        return path.read_bytes()
    if config.count(b"cycles=24000") != 1:
        raise ValueError("Windows TH04 performance CPU setting changed")
    return config.replace(b"cycles=24000", b"cycles=15000", 1)


def write_atomic(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex[:8])
    temporary.write_bytes(data)
    temporary.replace(path)
    if path.read_bytes() != data:
        raise ValueError(f"copy readback failed: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--emulator-dir", type=Path,
                        help="Windows collection's dosbox-x directory; existing packages can reuse their verified copy")
    parser.add_argument("--build-dir", type=Path,
                        default=ROOT / ".analysis/build/th04-invincible")
    parser.add_argument("--image", type=Path, default=ROOT /
                        ".analysis/runtime/candidates/th04-invincible-play/play.hdi")
    parser.add_argument("--update", action="store_true",
                        help="refresh an existing package while preserving its saves")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    emulator = args.emulator_dir.resolve() if args.emulator_dir else None
    build = args.build_dir.resolve()
    manifest = json.loads((build / "build.json").read_text(encoding="utf-8"))
    variant = manifest.get("variant")
    if variant not in {"invincible-main", "normal"} or set(manifest["products"]) != set(PRODUCTS):
        raise ValueError("expected a complete normal or invincible four-product build")
    normal = variant == "normal"
    image_name = "play-normal.hdi" if normal else "play.hdi"
    config_name = "th04-normal.conf" if normal else "th04.conf"
    reference_name = "th04-normal-reference.conf" if normal else "th04-reference.conf"
    launcher_name = "start-th04-normal.bat" if normal else "start-th04.bat"
    reference_launcher_name = "start-th04-normal-reference.bat" if normal else "start-th04-reference.bat"
    highcpu_launcher_name = "start-th04-normal-highcpu.bat" if normal else "start-th04-highcpu.bat"
    bin_name = "bin-normal" if normal else "bin"
    current_fingerprint = source_fingerprint()
    if (manifest.get("source_fingerprint") is not None
            and manifest["source_fingerprint"] != current_fingerprint):
        raise ValueError("product inputs changed after the build")
    product_bytes = {}
    records = {}
    for artifact, name in PRODUCTS.items():
        data = (build / name).read_bytes()
        record = manifest["products"][artifact]
        if (record["file"] != name or record["size"] != len(data)
                or record["sha256"] != sha(data) or not parse_mz(data).valid):
            raise ValueError(f"unverified product: {name}")
        if artifact == "main":
            main_receipt = json.loads(Path(record["build_receipt"]).read_text(encoding="utf-8"))
            if (main_receipt["link"]["mz"]["sha256"] != sha(data)
                    or bool(main_receipt.get("invincible_overlay")) != (not normal)):
                raise ValueError("MAIN compiler receipt does not match the advertised gameplay variant")
            if main_receipt.get("bullet_load_trace"):
                raise ValueError("a private full-pool diagnostic cannot be exported as a playable game")
        product_bytes[artifact] = data
        records[artifact] = {"file": name, "size": len(data), "sha256": sha(data)}

    prior_receipt = output / ("normal-package.json" if normal else "package.json")
    prior = None
    source_receipt = None
    if output.exists() and any(output.iterdir()):
        if not args.update:
            parser.error("nonempty package requires --update")
        if prior_receipt.is_file():
            prior = json.loads(prior_receipt.read_text(encoding="utf-8"))
            if prior.get("variant") != variant:
                raise ValueError("existing package variant does not match the build")
            source_receipt = prior
            source = (output / image_name).read_bytes()
        elif normal and (output / "package.json").is_file():
            # The first normal image inherits the user's current saves. Later
            # normal updates preserve its own image rather than recloning it.
            source_receipt = json.loads((output / "package.json").read_text(encoding="utf-8"))
            if source_receipt.get("variant") != "invincible-main":
                raise ValueError("normal image seed is not a verified invincible package")
            source = (output / "play.hdi").read_bytes()
        else:
            parser.error("existing package requires its matching prior receipt")
        expected = source_receipt["products"]
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

    if emulator is not None:
        exe = (emulator / "dosbox-x.exe").read_bytes()
        font = (emulator / "font_jp.bmp").read_bytes()
        reference_config = render_config((emulator / "th04_jp.conf").read_bytes())
    elif source_receipt is not None:
        exe = (output / "dosbox-x.exe").read_bytes()
        font = (output / "FREECG98.bmp").read_bytes()
        seed_normal = source_receipt["variant"] == "normal"
        seed_config_name = "th04-normal.conf" if seed_normal else "th04.conf"
        seed_reference_name = "th04-normal-reference.conf" if seed_normal else "th04-reference.conf"
        config = (output / seed_config_name).read_bytes()
        reference_config = package_reference_config(output / seed_reference_name, config)
        if (sha(exe) != source_receipt["dosbox_x_sha256"]
                or sha(font) != source_receipt["font_sha256"]
                or sha(config) != source_receipt["config_sha256"]
                or ("reference_config_sha256" in source_receipt and
                    sha(reference_config) != source_receipt["reference_config_sha256"])):
            raise ValueError("existing DOSBox-X files differ from package receipt")
    else:
        parser.error("a new package requires --emulator-dir")
    if normal:
        if reference_config.count(b"imgmount c play.hdi") == 1:
            reference_config = reference_config.replace(b"imgmount c play.hdi", b"imgmount c play-normal.hdi", 1)
        elif reference_config.count(b"imgmount c play-normal.hdi") != 1:
            raise ValueError("normal configuration has no unique image mount")
    config = performance_config(reference_config)
    launcher = ('@echo off\r\ncd /d "%~dp0"\r\n'
                f'start "" "%~dp0dosbox-x.exe" -conf "%~dp0{config_name}"\r\n').encode("ascii")
    reference_launcher = ('@echo off\r\ncd /d "%~dp0"\r\n'
                          f'start "" "%~dp0dosbox-x.exe" -conf "%~dp0{reference_name}"\r\n').encode("ascii")
    highcpu_launcher = ('@echo off\r\ncd /d "%~dp0"\r\n'
                        'echo TH04: 36,000-cycle CPU profile. Close other TH04 instances first.\r\n'
                        f'start "" "%~dp0dosbox-x.exe" -conf "%~dp0{config_name}" '
                        '-set "cpu cycles=36000"\r\n').encode("ascii")
    builder_template = (ROOT / "scripts/windows/Build-TH04.ps1").read_text(encoding="utf-8")
    if builder_template.count("@REPO_PATH@") != 1:
        raise ValueError("Windows builder template has no unique repository placeholder")
    builder = builder_template.replace("@REPO_PATH@", str(ROOT).replace("'", "''"))
    builder_bytes = builder.encode("utf-8")
    builder_cmd = (ROOT / "scripts/windows/build-th04.cmd").read_bytes()
    builder_readme = (ROOT / "scripts/windows/README-build.txt").read_bytes()
    output.mkdir(parents=True, exist_ok=True)
    (output / bin_name).mkdir(exist_ok=True)
    for artifact, name in PRODUCTS.items():
        write_atomic(output / bin_name / name, product_bytes[artifact])
    write_atomic(output / image_name, image)
    write_atomic(output / "dosbox-x.exe", exe)
    write_atomic(output / "FREECG98.bmp", font)
    write_atomic(output / config_name, config)
    write_atomic(output / reference_name, reference_config)
    write_atomic(output / launcher_name, launcher)
    write_atomic(output / reference_launcher_name, reference_launcher)
    write_atomic(output / highcpu_launcher_name, highcpu_launcher)
    write_atomic(output / "Build-TH04.ps1", builder_bytes)
    write_atomic(output / "build-th04.cmd", builder_cmd)
    write_atomic(output / "README-build.txt", builder_readme)
    receipt = {
        "schema_version": 1,
        "variant": variant,
        "build_run_id": manifest["run_id"],
        "source_fingerprint": current_fingerprint,
        "products": records,
        "source_hdi_sha256": sha(source),
        "play_hdi_sha256_at_export": sha(image),
        "dosbox_x_sha256": sha(exe),
        "font_sha256": sha(font),
        "config_sha256": sha(config),
        "reference_config_sha256": sha(reference_config),
        "build_script_sha256": sha(builder_bytes),
        "build_cmd_sha256": sha(builder_cmd),
        "build_readme_sha256": sha(builder_readme),
        "launch": launcher_name,
        "highcpu_launch": highcpu_launcher_name,
        "highcpu_cycles": 36000,
        "highcpu_launcher_sha256": sha(highcpu_launcher),
        "image": image_name,
        "bin_dir": bin_name,
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
