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
import uuid

ROOT = Path(__file__).resolve().parents[1]
PROBES = ROOT / ".analysis/reconstruction/probes"
PRODUCTS = {"main": "MAIN.EXE", "op": "OP.EXE", "maine": "MAINE.EXE", "zun": "ZUN.COM"}


def invoke(script: str, output: Path, *arguments: str) -> dict:
    command = [sys.executable, str(ROOT / "scripts/probes" / script),
               "--output-dir", str(output), *arguments]
    subprocess.run(command, cwd=ROOT, check=True)
    return json.loads((output / "receipt.json").read_text(encoding="utf-8"))


def build_product(artifact: str, work: Path, cache: Path | None) -> Path:
    if artifact == "zun":
        source = invoke("probe_th04_native_zun_composite.py", work)
        if not source.get("cold_equal"):
            raise RuntimeError("ZUN component build failed")
        packed_dir = work.with_name(work.name + "-diet")
        invoke("replay_diet145f.py", packed_dir, "th04-zun",
               "--candidate-a", str(work / "a.flat.bin"),
               "--candidate-b", str(work / "b.flat.bin"))
        return packed_dir / "a/ZUN.COM"
    arguments = ["--without-support"]
    if artifact == "main":
        arguments.append("--require-link")
        if cache:
            arguments.extend(["--reuse-cpp-from", str(cache.resolve()),
                              "--reuse-asm-from", str(cache.resolve())])
    elif cache:
        arguments.extend(["--reuse-from", str(cache.resolve())])
    receipt = invoke(f"probe_th04_native_{artifact}_link.py", work, *arguments)
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
    return work / f"source/bin/{artifact}-native.exe"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=PRODUCTS, default=list(PRODUCTS))
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".analysis/build/th04")
    parser.add_argument("--main-cpp-cache", type=Path,
                        help="previous MAIN build; objects are reused only for unchanged inputs")
    parser.add_argument("--op-cache", type=Path, help="previous OP build with verified objects")
    parser.add_argument("--maine-cache", type=Path, help="previous MAINE build with verified objects")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    lock_path = ROOT / ".analysis/native-build.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("another TH04 product build is running")
        run_id = "product-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
        records = {}
        products = {}
        caches = {"main": args.main_cpp_cache, "op": args.op_cache, "maine": args.maine_cache}
        for artifact in dict.fromkeys(args.only):
            work = PROBES / (run_id + "-" + artifact)
            print(f"Building {PRODUCTS[artifact]}...", flush=True)
            product = build_product(artifact, work, caches.get(artifact))
            products[artifact] = product
            records[artifact] = {
                "file": PRODUCTS[artifact], "size": product.stat().st_size,
                "sha256": hashlib.sha256(product.read_bytes()).hexdigest(),
                "build_receipt": str(work / "receipt.json"),
            }
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
