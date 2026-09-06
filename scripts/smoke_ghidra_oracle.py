#!/usr/bin/env python3
"""Calibrate the Ghidra database Oracle with independent negative mutations."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import shutil
import sys
import tempfile

from lib.analysis import load_analysis_config
from lib.ghidra import GhidraError, attest_mz_export, parse_properties
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact


ROOT = Path(__file__).resolve().parents[1]


def copy_case(source: Path, parent: Path, name: str) -> Path:
    destination = parent / name
    shutil.copytree(source, destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_id", nargs="?", default="th04-main")
    parser.add_argument("--export-dir", type=Path)
    args = parser.parse_args()
    try:
        manifest = load_target_manifest(ROOT / "config" / "targets.toml")
        artifact = find_artifact(manifest, args.artifact_id)
        target = read_verified_artifact(ROOT, artifact)
        config = load_analysis_config(ROOT / "config" / "analysis_toolchain.toml")
        export_dir = (
            args.export_dir or ROOT / ".analysis" / "ghidra" / "exports" / args.artifact_id
        ).resolve()
        properties = parse_properties(export_dir / "program.properties")
        nonce = properties.get("export_nonce")
        if nonce is None:
            raise GhidraError("positive fixture has no export nonce")
        positive = attest_mz_export(
            export_dir, target, artifact, config, expected_nonce=nonce
        )
        results = {"positive": bool(positive["ready"])}

        scratch_parent = ROOT / ".analysis" / "ghidra"
        scratch_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="oracle-smoke-", dir=scratch_parent) as temporary:
            temporary_root = Path(temporary)

            load_case = copy_case(export_dir, temporary_root, "load-byte")
            load = bytearray((load_case / "load-memory.bin").read_bytes())
            load[len(load) // 2] ^= 1
            (load_case / "load-memory.bin").write_bytes(load)
            report = attest_mz_export(load_case, target, artifact, config)
            results["load_byte_mutation"] = (
                not report["ready"] and not report["checks"]["load_memory"]
            )

            relocation_case = copy_case(export_dir, temporary_root, "relocation")
            relocation_path = relocation_case / "relocations.csv"
            with relocation_path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
                fields = list(rows[0]) if rows else []
            if rows:
                original = rows[0]["memory_bytes"]
                rows[0]["memory_bytes"] = original[:-1] + ("0" if original[-1] != "0" else "1")
                with relocation_path.open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.DictWriter(stream, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)
                report = attest_mz_export(relocation_case, target, artifact, config)
                results["relocation_mutation"] = (
                    not report["ready"] and not report["checks"]["relocation_table"]
                )
            else:
                results["relocation_mutation"] = "not-applicable"

            mapping_case = copy_case(export_dir, temporary_root, "mapping")
            mapping_path = mapping_case / "blocks.csv"
            with mapping_path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
                fields = list(rows[0])
            loaded_row = next((row for row in rows if row["loaded"] == "true"), None)
            if loaded_row is None:
                raise GhidraError("positive fixture contains no loaded block")
            loaded_row["file_offset"] = str(int(loaded_row["file_offset"]) + 1)
            with mapping_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            report = attest_mz_export(mapping_case, target, artifact, config)
            results["mapping_mutation"] = (
                not report["ready"]
                and (
                    not report["checks"]["load_mapping_coverage"]
                    or not report["checks"]["load_mapping_addresses"]
                )
            )

            alias_case = copy_case(export_dir, temporary_root, "cross-category-alias")
            alias_path = alias_case / "blocks.csv"
            with alias_path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
                fields = list(rows[0])
            alias = dict(rows[0])
            alias.update(
                {
                    "block": "UNEXPECTED_HEADER_ALIAS",
                    "initialized": "true",
                    "loaded": "true",
                    "file_offset": "0",
                    "length": "1",
                    "min_address": "1000:0000",
                    "max_address": "1000:0000",
                    "address_space": properties["default_address_space"],
                    "description": "negative-control alias",
                }
            )
            rows.append(alias)
            with alias_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            alias_properties = alias_case / "program.properties"
            alias_properties.write_text(
                alias_properties.read_text(encoding="utf-8").replace(
                    f"source_range_count={len(rows) - 1}",
                    f"source_range_count={len(rows)}",
                ),
                encoding="utf-8",
            )
            report = attest_mz_export(alias_case, target, artifact, config)
            results["cross_category_alias"] = (
                not report["ready"] and not report["checks"]["mapping_partition"]
            )

        stale_nonce = "0" * 32 if nonce != "0" * 32 else "1" * 32
        stale = attest_mz_export(
            export_dir, target, artifact, config, expected_nonce=stale_nonce
        )
        results["stale_export_nonce"] = (
            not stale["ready"]
            and "export_nonce" in stale["diagnostics"]["property_mismatches"]
        )
        for name, passed in results.items():
            label = "SKIP" if passed == "not-applicable" else "PASS" if passed else "FAIL"
            print(f"{label} {name}")
        required = [value for value in results.values() if value != "not-applicable"]
        ready = all(required)
        print(f"Ghidra Oracle smoke: {'PASS' if ready else 'FAIL'}")
        return 0 if ready else 1
    except (GhidraError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"error: Ghidra Oracle smoke failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
