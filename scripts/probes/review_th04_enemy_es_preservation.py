#!/usr/bin/env python3
"""Attest TH04 enemy ES-save sites and independent TH05 analogues."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[2]
SITES = {
    "th04-main": (
        ("aim_helper", 0x155AA, 51,
         "92972f0ba6797be9a7e5a3d16573dc6bb424093f7e0bfb26b8b7b803d3913571", 8, 47),
        ("opcode_20", 0x157EB, 73,
         "c67c7d9792b3e007ce3c1ae81d7382fce3a71aa42936cb9252eb308d2516510b", 60, 69),
    ),
    "th05-main-smoke": (
        ("aim_helper_analogue", 0x153CA, 21,
         "0b474de898a4027457c2f44d224e5a8837bdfc45662522b1ba6f4896291d8c26", 0, 16),
        ("bullet_calls_analogue", 0x155C7, 16,
         "9467975c74d3614ed52a787de9075e05bd8e1a7771c1d0b4c2ab9d3c1bf5124b", 0, 15),
        ("angle_call_analogue", 0x156B0, 26,
         "2c1a78adca2d8c21434b2743f875cebac1a3c920eefae0765df5131052095432", 0, 25),
    ),
}
EXPECTED_MZ = {
    "th04-main": {"header_size": 6144, "relocations": 1136},
    "th05-main-smoke": {"header_size": 4032, "relocations": 998},
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="enemy-es-preservation-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    artifacts = {artifact["id"]: artifact for artifact in manifest["artifacts"]}
    results = {}
    for artifact_id, sites in SITES.items():
        info = artifacts[artifact_id]
        target = (ROOT / info["private_path"]).read_bytes()
        if len(target) != info["size"] or sha(target) != info["sha256"]:
            raise ValueError(f"{artifact_id}: target identity failed")
        header_size = int.from_bytes(target[8:10], "little") * 16
        relocation_count = int.from_bytes(target[6:8], "little")
        if {"header_size": header_size, "relocations": relocation_count} != EXPECTED_MZ[artifact_id]:
            raise ValueError(f"{artifact_id}: MZ structure changed")
        load_module = target[header_size:]
        artifact_results = []
        for name, load_start, size, expected_sha, push_offset, pop_offset in sites:
            extent = load_module[load_start:load_start + size]
            if len(extent) != size or sha(extent) != expected_sha:
                raise ValueError(f"{artifact_id} {name}: extent identity failed")
            if extent[push_offset] != 0x06 or extent[pop_offset] != 0x07:
                raise ValueError(f"{artifact_id} {name}: ES save pair changed")
            if load_module.count(extent) != 1:
                raise ValueError(f"{artifact_id} {name}: extent is not unique")
            artifact_results.append({
                "name": name,
                "load_start": hex(load_start),
                "file_start": hex(header_size + load_start),
                "size": size,
                "sha256": expected_sha,
                "push_es_offset": push_offset,
                "pop_es_offset": pop_offset,
            })
        results[artifact_id] = {
            "target_sha256": info["sha256"],
            "header_size": header_size,
            "relocation_count": relocation_count,
            "sites": artifact_results,
        }

    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 MAIN enemy aim/opcode-20 ES preservation with TH05 target corroboration",
        "artifacts": results,
        "result": (
            "The attested TH04 target has PUSH ES / POP ES around the aim helper calls and "
            "opcode 0x20 bullet calls. The independently attested TH05 target contains the "
            "same preservation pattern at three enemy-script call sites."
        ),
        "limit": (
            "The target bytes establish semantics and cross-game corroboration, not original "
            "source syntax or a natural TC4J producer. No exact promotion follows."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
