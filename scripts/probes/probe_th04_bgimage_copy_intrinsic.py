#!/usr/bin/env python3
"""Test whether TC4J's __memcpy__ emits the target BGIMAGE REP MOVSD loops.

The two product-only TU builds are compiler controls, not exact candidates.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib

from replay_th04_bgimage_natural import (
    ROOT, SOURCE, HEADER, HMEM_HEADER, FLAGS, code, external_names,
    sha, target_checks,
)

REP_MOVSD = bytes.fromhex("F3 66 A5")
REP_MOVSW = bytes.fromhex("F3 A5")


def compile_variant(label: str, source: str, output: Path, runner: Path, env: dict[str, str]) -> dict[str, object]:
    work = output / label
    work.mkdir()
    for product in (SOURCE, HEADER, HMEM_HEADER):
        destination = work / product.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.encode() if product == SOURCE else product.read_bytes())
        os.utime(destination, (946684800, 946684800))
    (work / "obj").mkdir()
    command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS[:-1], "-nobj/",
               "src/shared/hardware/bgimage.cpp"]
    done = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=120)
    (output / f"{label}.log").write_text(
        json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr
    )
    object_path = work / "obj/bgimage.obj"
    if done.returncode or not object_path.is_file():
        raise ValueError(f"{label}: product-only TC4J compilation failed")
    obj = object_path.read_bytes()
    emitted, record_count = code(obj)
    (output / f"{label}.obj").write_bytes(obj)
    (output / f"{label}.code").write_bytes(emitted)
    # The temporary source tree is no longer needed; retained object, CODE,
    # source hash, and log are enough to replay from checked-in product source.
    shutil.rmtree(work)
    return {
        "source_sha256": sha(source.encode()), "object_sha256": sha(obj),
        "omf_record_count": record_count, "code_size": len(emitted),
        "code_sha256": sha(emitted), "rep_movsd_count": emitted.count(REP_MOVSD),
        "rep_movsw_count": emitted.count(REP_MOVSW),
        "external_names": external_names(obj),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="bgimage-intrinsic-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)
    targets = target_checks(output)
    for short in ("op", "maine"):
        if (output / f"{short}-target.bin").read_bytes().count(REP_MOVSD) != 2:
            raise ValueError(f"{short}: target BGIMAGE copy-loop shape changed")
    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise ValueError("active TCC identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    baseline = SOURCE.read_text()
    if baseline.count("memcpy(") != 8:
        raise ValueError("maintained BGIMAGE copy-call count changed")
    variants = {
        "baseline": baseline,
        "intrinsic": baseline.replace("memcpy(", "__memcpy__("),
    }
    results = {label: compile_variant(label, source, output, runner, env)
               for label, source in variants.items()}
    if (results["baseline"]["code_size"], results["intrinsic"]["code_size"]) != (269, 275):
        raise ValueError("unexpected BGIMAGE compiler CODE sizes")
    if (results["intrinsic"]["rep_movsd_count"], results["intrinsic"]["rep_movsw_count"]) != (0, 8):
        raise ValueError("unexpected TC4J intrinsic copy-loop shape")
    receipt = {
        "schema_version": 1,
        "claim_scope": "OP/MAINE BGIMAGE product-only TU intrinsic codegen control; no exact promotion",
        "target_slices": targets, "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()), "flags": [*FLAGS[:-1], "-nobj/"],
        "variants": results,
        "result": "__memcpy__ emits eight REP MOVSW sequences and 275 CODE bytes; target uses two REP MOVSD loops in 208 bytes",
        "limit": "This falsifies only the pinned intrinsic shape, not every possible natural copy producer.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
