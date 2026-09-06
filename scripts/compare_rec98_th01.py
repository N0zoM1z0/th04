#!/usr/bin/env python3
"""Compare a local ReC98 TH01 build against pinned targets, without trust."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tomllib

from lib.omf import OMFError, normalize_dependency_timestamps, parse_omf
from lib.pc98 import compare_blobs, digest_file
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact
from lib.toolchain import ToolchainError, file_set_identity


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "targets.toml"
CALIBRATION = ROOT / "config" / "rec98_th01_calibration.toml"
MAPPING = (
    ("th01-op-smoke", "op.exe"),
    ("th01-reiiden-smoke", "reiiden.exe"),
    ("th01-fuuin-smoke", "fuuin.exe"),
    ("th01-zunsoft-smoke", "zunsoft.com"),
)


def vector(comparison: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {
        "raw_exact": comparison["verdict"]["raw_exact"],
        "format_same": comparison["formats"]["same"],
        "routing_hints": comparison.get("routing_hints", []),
    }
    if comparison["formats"]["left"] == "mz" and comparison["formats"]["same"]:
        mz = comparison["mz"]
        result.update(
            {
                "format_integrity": comparison["format_integrity"]["both_valid"],
                "header_fields_exact": mz["header_fields"]["exact"],
                "header_bytes_exact": mz["header_bytes"]["exact"],
                "relocations_ordered_exact": mz["relocations"]["ordered_exact"],
                "relocations_multiset_exact": mz["relocations"]["multiset_exact"],
                "relocation_site_values_exact": mz["relocations"]["site_values"]["exact"],
                "program_image_exact": mz["program_image"]["exact"],
                "normalized_program_exact": mz["relocation_normalized_program"]["exact"],
                "overlay_exact": mz["overlay"]["exact"],
            }
        )
        result["rec98_rule1_core_dimensions_pass"] = bool(
            result["program_image_exact"]
            and result["relocations_multiset_exact"]
        )
    else:
        result["rec98_rule1_core_dimensions_pass"] = bool(result["raw_exact"])
    return result


def omf_identities(root: Path, paths: list[Path]) -> dict[str, object]:
    raw = file_set_identity(root, paths)
    normalized = file_set_identity(
        root,
        paths,
        digest_function=lambda path: hashlib.sha256(
            normalize_dependency_timestamps(path.read_bytes())
        ).hexdigest(),
    )
    return {
        "count": raw.file_count,
        "total_size": raw.total_size,
        "raw_sha256": raw.sha256,
        "dependency_timestamp_normalized_sha256": normalized.sha256,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="cold snapshot root containing bin/th01")
    parser.add_argument(
        "--gate",
        choices=("exact", "calibration"),
        default="exact",
        help="exact rejects any raw mismatch; calibration checks the pinned known vector",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    manifest = load_target_manifest(TARGETS)
    expected = None
    expected_omf = None
    if args.gate == "calibration":
        calibration = tomllib.loads(CALIBRATION.read_text(encoding="utf-8"))
        expected = {item["id"]: item for item in calibration["artifacts"]}
        expected_omf = calibration["omf"]

    artifacts: list[dict[str, object]] = []
    for artifact_id, filename in MAPPING:
        artifact = find_artifact(manifest, artifact_id)
        target = read_verified_artifact(ROOT, artifact)
        candidate_path = source / "bin" / "th01" / filename
        if not candidate_path.is_file():
            print(f"missing candidate output: {candidate_path}", file=sys.stderr)
            return 1
        candidate = candidate_path.read_bytes()
        comparison = compare_blobs(target, candidate)
        observed = vector(comparison)
        entry = {
            "id": artifact_id,
            "filename": filename,
            "target_sha256": artifact["sha256"],
            "candidate_sha256": digest_file(candidate_path),
            "candidate_size": len(candidate),
            "vector": observed,
            "comparison": comparison,
        }
        if expected is not None:
            expected_entry = expected[artifact_id]
            expected_vector = {
                key: value
                for key, value in expected_entry.items()
                if key not in {"id", "filename", "candidate_sha256", "candidate_size"}
            }
            actual_vector = {
                key: value for key, value in observed.items() if key in expected_vector
            }
            entry["calibration_match"] = (
                entry["candidate_sha256"] == expected_entry["candidate_sha256"]
                and entry["candidate_size"] == expected_entry["candidate_size"]
                and actual_vector == expected_vector
            )
        artifacts.append(entry)

    object_count = 0
    object_failures: list[dict[str, str]] = []
    object_root = source / "obj"
    object_paths = sorted(object_root.rglob("*.obj"))
    for path in object_paths:
        object_count += 1
        try:
            parse_omf(path.read_bytes())
        except (OSError, OMFError) as error:
            object_failures.append(
                {"path": path.relative_to(source).as_posix(), "error": str(error)}
            )
    object_identity = None
    th01_object_identity = None
    if object_paths:
        try:
            object_identity = omf_identities(object_root, object_paths)
            th01_paths = [
                path
                for path in object_paths
                if path.relative_to(object_root).parts[0] == "th01"
            ]
            th01_object_identity = omf_identities(object_root, th01_paths)
        except (OMFError, ToolchainError) as error:
            object_failures.append({"path": "obj", "error": str(error)})
    omf_calibration_match = bool(
        expected_omf is not None
        and object_identity
        and th01_object_identity
        and object_identity["count"] == expected_omf["all_object_count"]
        and th01_object_identity["count"] == expected_omf["th01_object_count"]
        and th01_object_identity["dependency_timestamp_normalized_sha256"]
        == expected_omf["th01_dependency_timestamp_normalized_sha256"]
    )
    strict_pass = all(item["vector"]["raw_exact"] for item in artifacts)
    rec98_rule1_core_pass = all(
        item["vector"]["rec98_rule1_core_dimensions_pass"] for item in artifacts
    )
    calibration_pass = bool(
        expected is not None
        and all(item.get("calibration_match") for item in artifacts)
        and object_count > 0
        and not object_failures
        and omf_calibration_match
    )
    report = {
        "schema_version": 1,
        "kind": "untrusted-rec98-th01-candidate-comparison",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "policy": "Raw zero-difference is the only exact verdict.",
        "strict_raw_pass": strict_pass,
        "policy_views": {
            "local_strict_raw_pass": strict_pass,
            "rec98_rule1_core_dimensions_pass": rec98_rule1_core_pass,
            "differ": strict_pass != rec98_rule1_core_pass,
            "note": "The ReC98 view models only its stated program-image and unordered-relocation core; it never changes the local verdict.",
        },
        "calibration_vector_pass": calibration_pass,
        "omf_calibration_match": omf_calibration_match,
        "exact_count": sum(bool(item["vector"]["raw_exact"]) for item in artifacts),
        "artifact_count": len(artifacts),
        "omf_objects": {
            "count": object_count,
            "all_valid": not object_failures and object_count > 0,
            **(object_identity or {}),
            "failures": object_failures,
        },
        "th01_omf_objects": th01_object_identity,
        "artifacts": artifacts,
    }
    output = args.output or source.parent / "th01-comparison.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for item in artifacts:
        verdict = "EXACT" if item["vector"]["raw_exact"] else "REJECT"
        print(f"{verdict:6} {item['id']}: {', '.join(item['vector']['routing_hints'])}")
    print(f"OMF objects: {object_count - len(object_failures)}/{object_count} valid")
    print(f"strict raw gate: {'PASS' if strict_pass else 'FAIL'}")
    if expected is not None:
        print(f"known diagnostic vector: {'PASS' if calibration_pass else 'FAIL'}")
        print(
            "known TH01 OMF identity: "
            + ("PASS" if omf_calibration_match else "FAIL")
        )
    print(f"report: {output}")
    passed = strict_pass if args.gate == "exact" else calibration_pass
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
