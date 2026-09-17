#!/usr/bin/env python3
"""Replay maintained OP/MAINE BGIMAGE source as a bounded nonexact control.

The packed target's independently decoded payload and the pinned ReC98
candidate are comparison fixtures. No object is linked into a product build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001"
SOURCE = ROOT / "src/shared/hardware/bgimage.cpp"
HEADER = ROOT / "src/shared/hardware/bgimage.hpp"
HMEM_HEADER = ROOT / "src/shared/memory/hmem.hpp"
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")
BASELINE_CODE_SHA = "efb4f7170ae577f5f18df689baffeeaad9fb34db3766d01ebdb25209d1f8f554"
FREE_CODE_SHA = "051c7b582818659381d1ed35a4c7721dc51069c3eeb46adc0ce45ac14a4bcdbf"
TARGETS = {
    "op": (0xE428, "13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74",
           "cf61e4083c86599e123e65ceb3d64a83012283ac40128fbc7f69fbc911dba050"),
    "maine": (0xD626, "7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c",
              "bab5569b6f9bd6ee07585d28cbcb8bb7db191c9e70fc9054a3746d47086a04b8"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def code(obj: bytes) -> tuple[bytes, int]:
    records = parse_omf(obj)
    groups = code_ledata(records, "SHARED")
    if not groups or groups[0][0] != 0:
        raise ValueError("missing SHARED CODE from offset zero")
    combined = bytearray(groups[-1][1])
    cursor = 0
    for start, end, record_number, _ in groups:
        if start != cursor:
            raise ValueError("non-contiguous SHARED CODE")
        combined[start:end] = records[record_number - 1].data[3:]
        cursor = end
    return bytes(combined), len(records)


def external_names(obj: bytes) -> list[str]:
    result = []
    for record in parse_omf(obj):
        if record.record_type != 0x8C:
            continue
        pos = 0
        while pos < len(record.data):
            length = record.data[pos]
            pos += 1
            result.append(record.data[pos:pos + length].decode("ascii"))
            pos += length + 1  # Name plus its one-byte type index.
    return result


def target_checks(output: Path) -> dict[str, dict[str, object]]:
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    by_id = {item["id"]: item for item in manifest["artifacts"]}
    result = {}
    for name, (start, payload_sha, slice_sha) in TARGETS.items():
        item = by_id[f"th04-{name}"]
        packed = (ROOT / item["private_path"]).read_bytes()
        if len(packed) != item["size"] or sha(packed) != item["sha256"]:
            raise ValueError(f"{name}: packed target identity failed")
        payload = (ROOT / f".analysis/reconstruction/v218-th04-{name}-diet/payload.bin").read_bytes()
        if sha(payload) != payload_sha or sha(payload[start:start + 208]) != slice_sha:
            raise ValueError(f"{name}: decoded target payload identity failed")
        (output / f"{name}-target.bin").write_bytes(payload[start:start + 208])
        candidate = (SNAPSHOT / f"a/source/bin/th04/{name}.exe").read_bytes()
        if candidate[:2] != b"MZ":
            raise ValueError(f"{name}: candidate is not MZ")
        header = int.from_bytes(candidate[8:10], "little") * 16
        if candidate[header + start:header + start + 208] != payload[start:start + 208]:
            raise ValueError(f"{name}: candidate/target BGIMAGE slice differs")
        result[name] = {
            "packed_target_sha256": item["sha256"],
            "decoded_payload_sha256": payload_sha,
            "load_offset": f"0x{start:04X}",
            "extent_size": 208,
            "target_slice_sha256": slice_sha,
            "candidate_mz_sha256": sha(candidate),
            "candidate_slice_equal": True,
        }
    return result


def build(label: str, output: Path, work: Path, runner: Path, env: dict[str, str]) -> dict[str, object]:
    source_tree = work / "source"
    shutil.copytree(SNAPSHOT / label / "source", source_tree, symlinks=True)
    for product in (SOURCE, HEADER, HMEM_HEADER):
        destination = source_tree / product.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(product.read_bytes())
        os.utime(destination, (946684800, 946684800))
    # Give the product translation unit a distinct object name; preserve the
    # snapshot's original bgimage.obj solely as a comparison fixture.
    wrapper = source_tree / "th04/bgprod.cpp"
    wrapper.write_bytes(SOURCE.read_bytes())
    os.utime(wrapper, (946684800, 946684800))
    command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, "th04/bgprod.cpp"]
    done = subprocess.run(command, cwd=source_tree, env=env, capture_output=True, text=True, timeout=120)
    saved = output / label
    saved.mkdir()
    (saved / "compile.log").write_text(
        json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr
    )
    object_path = source_tree / "obj/th04/bgprod.obj"
    if done.returncode or not object_path.is_file():
        raise ValueError(f"{label}: maintained BGIMAGE source did not compile")
    obj = object_path.read_bytes()
    produced, record_count = code(obj)
    baseline_obj = (source_tree / "obj/th04/bgimage.obj").read_bytes()
    baseline, baseline_records = code(baseline_obj)
    produced_externals = external_names(obj)
    baseline_externals = external_names(baseline_obj)
    if len(baseline) != 208 or sha(baseline) != BASELINE_CODE_SHA:
        raise ValueError(f"{label}: changed ReC98 baseline object")
    if sorted(produced_externals) != sorted(baseline_externals + ["_memcpy"]):
        raise ValueError(f"{label}: unexpected external symbol set")
    (saved / "bgprod.obj").write_bytes(obj)
    (saved / "bgprod.code").write_bytes(produced)
    if len(produced) != 269 or sha(produced[-50:]) != FREE_CODE_SHA or produced[-50:] != baseline[-50:]:
        raise ValueError(f"{label}: unexpected maintained BGIMAGE code shape")
    return {
        "object_sha256": sha(obj), "omf_record_count": record_count,
        "code_size": len(produced), "code_sha256": sha(produced),
        "baseline_object_sha256": sha(baseline_obj), "baseline_omf_record_count": baseline_records,
        "baseline_code_size": len(baseline), "baseline_code_sha256": sha(baseline),
        "external_names": produced_externals, "baseline_external_names": baseline_externals,
        "free_tail_size": 50, "free_tail_sha256": sha(produced[-50:]),
    }


def standalone_compile(output: Path, runner: Path, env: dict[str, str]) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="standalone-", dir=output) as scratch:
        work = Path(scratch)
        for product in (SOURCE, HEADER, HMEM_HEADER):
            destination = work / product.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(product.read_bytes())
            os.utime(destination, (946684800, 946684800))
        (work / "obj").mkdir()
        command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS[:-1], "-nobj/",
                   "src/shared/hardware/bgimage.cpp"]
        done = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=120)
        (output / "standalone.log").write_text(
            json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr
        )
        path = work / "obj/bgimage.obj"
        if done.returncode or not path.is_file():
            raise ValueError("product-only BGIMAGE TU compilation failed")
        obj = path.read_bytes()
        produced, records = code(obj)
        (output / "standalone.obj").write_bytes(obj)
        (output / "standalone.code").write_bytes(produced)
        return {
            "object_sha256": sha(obj), "omf_record_count": records,
            "code_size": len(produced), "code_sha256": sha(produced),
            "external_names": external_names(obj),
            "product_files": [str(path.relative_to(ROOT)) for path in (SOURCE, HEADER, HMEM_HEADER)],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="bgimage-natural-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)
    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise ValueError("active TCC identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    targets = target_checks(output)
    with tempfile.TemporaryDirectory(prefix="work-", dir=output) as scratch:
        builds = {label: build(label, output, Path(scratch) / label, runner, env)
                  for label in ("a", "b")}
    if builds["a"] != builds["b"]:
        raise ValueError("A/B objects are not deterministic")
    standalone = standalone_compile(output, runner, env)
    if standalone["code_sha256"] != builds["a"]["code_sha256"]:
        raise ValueError("product-only TU differs from overlay diagnostic CODE")
    if sorted(standalone["external_names"]) != sorted(builds["a"]["external_names"]):
        raise ValueError("product-only TU external symbol set differs")
    receipt = {
        "schema_version": 1,
        "claim_scope": "OP/MAINE SHARED BGIMAGE natural source diagnostic; no exact promotion",
        "source_sha256": sha(SOURCE.read_bytes()), "header_sha256": sha(HEADER.read_bytes()),
        "hmem_header_sha256": sha(HMEM_HEADER.read_bytes()),
        "tcc_sha256": tcc["sha256"], "runner_sha256": sha(runner.read_bytes()),
        "flags": list(FLAGS), "target_slices": targets, "builds": builds,
        "standalone_tu": standalone,
        "result": "source-present; deterministic 269-byte CODE versus 208-byte target physical extent",
        "limit": "Only this TU compiles from product source plus pinned TC4J headers; no standalone artifact link, packed equality, or exact claim.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
