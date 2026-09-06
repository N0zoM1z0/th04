#!/usr/bin/env python3
"""Independently attest a private Ghidra MZ export against one pinned target."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from lib.analysis import load_analysis_config, repository_path
from lib.ghidra import GhidraError, attest_mz_export
from lib.pc98 import digest_file
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "targets.toml"
ANALYSIS_CONFIG = ROOT / "config" / "analysis_toolchain.toml"


def private_export(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to((ROOT / ".analysis").resolve())
    except ValueError as error:
        raise GhidraError("Ghidra attestation exports must stay below .analysis") from error
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_id")
    parser.add_argument("export_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-nonce")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        target_manifest = load_target_manifest(TARGETS)
        artifact = find_artifact(target_manifest, args.artifact_id)
        if artifact["format"] != "mz":
            raise GhidraError("the current database attestor requires an MZ target")
        target = read_verified_artifact(ROOT, artifact)
        analysis_config = load_analysis_config(ANALYSIS_CONFIG)
        export_dir = private_export(args.export_dir)
        if args.expected_nonce is not None and (
            len(args.expected_nonce) != 32
            or any(character not in "0123456789abcdef" for character in args.expected_nonce)
        ):
            raise GhidraError("--expected-nonce must be 32 lowercase hex digits")
        result = attest_mz_export(
            export_dir,
            target,
            artifact,
            analysis_config,
            expected_nonce=args.expected_nonce,
        )
        default_receipts = repository_path(
            ROOT, analysis_config["private_paths"]["database_receipts"]
        )
        output = private_export(args.output) if args.output else default_receipts / f"{args.artifact_id}.json"
        report = {
            "schema_version": 1,
            "observed_utc": datetime.now(timezone.utc).isoformat(),
            "target_manifest_sha256": digest_file(TARGETS),
            "analysis_manifest_sha256": digest_file(ANALYSIS_CONFIG),
            **result,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        temporary.replace(output)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            for name, passed in report["checks"].items():
                print(f"{'PASS' if passed else 'FAIL'} {name}")
            for sample in report["samples"]:
                print(
                    f"{'PASS' if sample['pass'] else 'FAIL'} sample "
                    f"{sample['load_module_offset']} {sample['preferred_address']}"
                )
            print(f"Ghidra database: {'READY' if report['ready'] else 'NOT READY'}")
            print(f"receipt: {output}")
        return 0 if report["ready"] else 1
    except (GhidraError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"error: Ghidra database attestation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
