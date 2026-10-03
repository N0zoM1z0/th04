#!/usr/bin/env python3
"""Build standalone TH04 products from maintained source (no byte-match gate)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import tomllib
import uuid

from product_input_fingerprint import source_fingerprint

ROOT = Path(__file__).resolve().parents[1]
PROBES = ROOT / ".analysis/reconstruction/probes"
PRODUCTS = {"main": "MAIN.EXE", "op": "OP.EXE", "maine": "MAINE.EXE", "zun": "ZUN.COM"}


def object_total(artifact: str) -> int:
    if artifact == "main":
        # Native MAIN currently owns 193 C/C++, 154 ASM, 8 state and 4 sprite objects.
        return 193 + 154 + 8 + 4
    if artifact in ("op", "maine"):
        manifest = tomllib.loads((ROOT / "config" / f"native_{artifact}_sources.toml")
                                 .read_text(encoding="utf-8"))
        return len(manifest["c_sources"]) + len(manifest["asm_sources"])
    return 0


def verified_zun_receipts(path: Path, product_sha256: str) -> bool:
    if not path.is_file():
        return False
    diet_path = path.parent.with_name(path.parent.name + "-diet") / "receipt.json"
    if not diet_path.is_file():
        return False
    source = json.loads(path.read_text(encoding="utf-8"))
    diet = json.loads(diet_path.read_text(encoding="utf-8"))
    packed = diet.get("builds", [])
    return (source.get("artifact") == "th04-zun" and source.get("cold_equal") is True
            and diet.get("artifact") == "th04-zun"
            and diet.get("candidate_inputs_identical") is True
            and diet.get("packed_outputs_identical") is True
            and len(packed) == 2
            and {record.get("label") for record in packed} == {"a", "b"}
            and all(record.get("packed_sha256") == product_sha256 for record in packed))


def invoke(script: str, output: Path, *arguments: str,
           progress_label: str | None = None, expected_objects: int = 0,
           cached_objects: bool = False) -> dict:
    command = [sys.executable, str(ROOT / "scripts/probes" / script),
               "--output-dir", str(output), *arguments]
    if progress_label is None:
        subprocess.run(command, cwd=ROOT, check=True)
    else:
        log_path = output.with_name(output.name + "-driver.log")
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(command, cwd=ROOT, stdout=log,
                                       stderr=subprocess.STDOUT)
            while process.poll() is None:
                count = sum(1 for _ in (output / "source").rglob("*.obj"))
                if expected_objects:
                    fraction = min(count / expected_objects, 1.0)
                    filled = int(fraction * 24)
                    phase = (("Checking/building" if cached_objects else "Compiling")
                             if count < expected_objects else "Linking")
                    detail = f"{phase} {count}/{expected_objects} objects"
                else:
                    if script == "probe_th04_native_zun_composite.py":
                        count = len(list(output.glob("*.log"))) + sum(
                            (output / f"{side}.flat.bin").is_file()
                            for side in ("a", "b")
                        )
                        filled = min(24, count * 24 // 9)
                        detail = f"Assembling {count}/9 source steps"
                    else:
                        count = sum((output / side / "ZUN.COM").is_file()
                                    for side in ("a", "b"))
                        filled = count * 12
                        detail = f"Packing {count}/2 verified binaries"
                bar = "#" * filled + "-" * (24 - filled)
                print(f"\r  {progress_label:<9} [{bar}] {detail:<34}",
                      end="", flush=True)
                time.sleep(0.5)
            print("\r" + " " * 85 + "\r", end="", flush=True)
            if process.returncode:
                tail = "\n".join(log_path.read_text(encoding="utf-8",
                                                    errors="replace").splitlines()[-25:])
                print(tail, file=sys.stderr)
                raise subprocess.CalledProcessError(process.returncode, command)
    return json.loads((output / "receipt.json").read_text(encoding="utf-8"))


def build_product(artifact: str, work: Path, cache: Path | None,
                  invincible_main: bool = False, progress: bool = False) -> Path:
    if artifact == "zun":
        source = invoke("probe_th04_native_zun_composite.py", work,
                        progress_label="ZUN.COM" if progress else None)
        if not source.get("cold_equal"):
            raise RuntimeError("ZUN component build failed")
        packed_dir = work.with_name(work.name + "-diet")
        invoke("replay_diet145f.py", packed_dir, "th04-zun",
               "--candidate-a", str(work / "a.flat.bin"),
               "--candidate-b", str(work / "b.flat.bin"),
               progress_label="ZUN.COM" if progress else None)
        return packed_dir / "a/ZUN.COM"
    arguments = ["--without-support"]
    if artifact == "main":
        arguments.append("--require-link")
        if invincible_main:
            arguments.append("--invincible")
        if cache:
            arguments.extend(["--reuse-cpp-from", str(cache.resolve()),
                              "--reuse-asm-from", str(cache.resolve())])
    elif cache:
        arguments.extend(["--reuse-from", str(cache.resolve())])
    receipt = invoke(f"probe_th04_native_{artifact}_link.py", work, *arguments,
                     progress_label=PRODUCTS[artifact] if progress else None,
                     expected_objects=object_total(artifact) if progress else 0,
                     cached_objects=cache is not None)
    if artifact == "main":
        failures = sum(receipt.get(key, 0) for key in (
            "roots_compile_fail", "asm_assemble_fail", "state_assemble_fail", "sprite_assemble_fail"))
        complete = (not failures and receipt["link"]["exit"] == 0
                    and not receipt["link"]["errors"] and receipt["link"]["mz"])
    else:
        complete = receipt.get("link_complete")
    if not complete:
        raise RuntimeError(f"{PRODUCTS[artifact]} failed; inspect {work / 'link.log'}")
    subprocess.run([sys.executable,
                    str(ROOT / "scripts/probes/audit_th04_native_irq_vectors.py"),
                    "--link-receipt", str(work / "receipt.json")], cwd=ROOT, check=True)
    if artifact == "main":
        subprocess.run([sys.executable,
                        str(ROOT / "scripts/probes/audit_th04_native_bullet_switches.py"),
                        "--link-receipt", str(work / "receipt.json")], cwd=ROOT, check=True)
    return work / f"source/bin/{artifact}-native.exe"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=PRODUCTS, default=list(PRODUCTS))
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".analysis/build/th04")
    parser.add_argument("--main-cpp-cache", type=Path,
                        help="previous MAIN build; objects are reused only for unchanged inputs")
    parser.add_argument("--op-cache", type=Path, help="previous OP build with verified objects")
    parser.add_argument("--maine-cache", type=Path, help="previous MAINE build with verified objects")
    parser.add_argument("--invincible-main", action="store_true",
                        help="build a separately labeled playable MAIN with collision damage disabled")
    parser.add_argument("--progress", action="store_true",
                        help="show source-object progress for the Windows command-line build")
    parser.add_argument("--incremental-from", type=Path,
                        help="previous Windows package.json; verify cache and rebuild changed inputs")
    args = parser.parse_args()
    if args.invincible_main and "main" not in args.only:
        parser.error("--invincible-main requires MAIN in --only")
    if args.invincible_main and args.output_dir.resolve() == (ROOT / ".analysis/build/th04").resolve():
        parser.error("--invincible-main requires a separate --output-dir")
    output = args.output_dir.resolve()
    lock_path = ROOT / ".analysis/native-build.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("another TH04 product build is running")
        run_id = "product-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
        input_fingerprint = source_fingerprint()
        records = {}
        products = {}
        caches = {"main": args.main_cpp_cache, "op": args.op_cache, "maine": args.maine_cache}
        requested = list(dict.fromkeys(args.only))
        if args.incremental_from:
            if not args.invincible_main or requested != list(PRODUCTS):
                parser.error("--incremental-from requires the complete invincible build request")
            previous_path = output / "build.json"
            package_path = args.incremental_from.resolve()
            if not previous_path.is_file() or not package_path.is_file():
                print("No complete cache; building all four products from source", flush=True)
            else:
                package = json.loads(package_path.read_text(encoding="utf-8"))
                previous = json.loads(previous_path.read_text(encoding="utf-8"))
                if previous.get("variant") != "invincible-main":
                    raise ValueError("incremental cache is not an invincible product build")
                for artifact in ("main", "op", "maine"):
                    receipt = Path(previous["products"][artifact]["build_receipt"])
                    if not receipt.is_file():
                        raise ValueError(f"missing {artifact} object-cache receipt")
                    caches[artifact] = receipt.parent
                old_zun = previous["products"]["zun"]
                zun_file = output / PRODUCTS["zun"]
                reuse_zun = (
                    package.get("build_run_id") == previous.get("run_id")
                    and package.get("source_fingerprint") == input_fingerprint
                    and package.get("products", {}).get("zun", {}).get("sha256") == old_zun.get("sha256")
                    and old_zun.get("file") == PRODUCTS["zun"]
                    and zun_file.is_file()
                    and hashlib.sha256(zun_file.read_bytes()).hexdigest() == old_zun.get("sha256")
                    and verified_zun_receipts(Path(old_zun["build_receipt"]), old_zun["sha256"])
                )
                if reuse_zun:
                    requested.remove("zun")
                    print("Verified source fingerprint: unchanged", flush=True)
                    if args.progress:
                        print(f"  ZUN.COM   [{'#' * 24}] REUSED  "
                              f"{old_zun['size']} bytes  SHA-256 {old_zun['sha256']}", flush=True)
                else:
                    print("ZUN inputs or receipt changed; rebuilding ZUN.COM from source", flush=True)
                print("Rechecking cached objects and relinking MAIN.EXE, OP.EXE, MAINE.EXE", flush=True)
        for artifact in requested:
            work = PROBES / (run_id + "-" + artifact)
            print(f"Building {PRODUCTS[artifact]}...", flush=True)
            product = build_product(artifact, work, caches.get(artifact),
                                    args.invincible_main and artifact == "main", args.progress)
            products[artifact] = product
            records[artifact] = {
                "file": PRODUCTS[artifact], "size": product.stat().st_size,
                "sha256": hashlib.sha256(product.read_bytes()).hexdigest(),
                "build_receipt": str(work / "receipt.json"),
            }
            if args.progress:
                print(f"  {PRODUCTS[artifact]:<9} [{'#' * 24}] PASS  "
                      f"{records[artifact]['size']} bytes  "
                      f"SHA-256 {records[artifact]['sha256']}", flush=True)
        if input_fingerprint != source_fingerprint():
            raise RuntimeError("product inputs changed during the build")
        # Keep checksum-verified products from a preceding full build when
        # iterating one artifact, so the game-image entrypoint still has a
        # complete inventory. Changed/unverified files never inherit a receipt.
        previous_manifest = output / "build.json"
        if previous_manifest.is_file():
            try:
                previous_records = json.loads(previous_manifest.read_text()).get("products", {})
            except (ValueError, AttributeError):
                previous_records = {}
            if not isinstance(previous_records, dict):
                previous_records = {}
            for artifact, record in previous_records.items():
                if artifact not in PRODUCTS or artifact in records or not isinstance(record, dict):
                    continue
                existing = output / PRODUCTS[artifact]
                if (record.get("file") == PRODUCTS[artifact] and existing.is_file()
                        and existing.stat().st_size == record.get("size")
                        and hashlib.sha256(existing.read_bytes()).hexdigest() == record.get("sha256")):
                    records[artifact] = record
        # Publish only after all requested products have built successfully.
        output.mkdir(parents=True, exist_ok=True)
        for artifact, product in products.items():
            temporary = output / (PRODUCTS[artifact] + ".tmp")
            shutil.copyfile(product, temporary)
            temporary.replace(output / PRODUCTS[artifact])
        manifest_text = json.dumps({
            "schema_version": 1, "run_id": run_id, "products": records,
            "source_fingerprint": input_fingerprint,
            "variant": "invincible-main" if args.invincible_main else "normal",
            "acceptance": "standalone build; runtime validation is separate; no byte equality required",
        }, indent=2) + "\n"
        PROBES.mkdir(parents=True, exist_ok=True)
        (PROBES / (run_id + "-build.json")).write_text(manifest_text, encoding="utf-8")
        (output / "build.json").write_text(manifest_text, encoding="utf-8")
        print(f"Built {', '.join(PRODUCTS[p] for p in products)} in {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        raise SystemExit(1)
