#!/usr/bin/env python3
"""Survey every locally built ReC98 PC-98 output under strict local policy."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tomllib

from lib.omf import OMFError, parse_omf
from lib.pc98 import compare_blobs, digest_file
from lib.reconstruction import (
    canonical_json_sha256,
    comparison_vector,
    identity_record,
    omf_identities,
)
from lib.targets import load_target_manifest, read_verified_artifact
from lib.toolchain import ToolchainError, file_set_identity


ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "config" / "targets.toml"
CALIBRATION = ROOT / "config" / "rec98_pc98_calibration.toml"
GAMES = ("th01", "th02", "th03", "th04", "th05")


def candidate_path(source: Path, artifact: dict[str, object]) -> Path:
    filename = Path(str(artifact["private_path"])).name
    return source / "bin" / str(artifact["game"]) / filename


def triage_summary(vector: dict[str, object]) -> str:
    """Summarize only measured mismatch dimensions for fast agent routing."""

    if not vector["format_same"]:
        return (
            f"format {vector['left_format']}->{vector['right_format']}; "
            f"raw size delta {vector['raw_size_delta']:+d}"
        )
    if vector["left_format"] == "mz":
        return (
            f"program {vector['program_left_size']}->{vector['program_right_size']}; "
            "outside-reloc diff "
            f"{vector['program_differences_outside_relocation_sites']}; "
            f"relocs {vector['relocations_left_count']}"
            f"->{vector['relocations_right_count']}"
        )
    return (
        f"COM diff {vector['com_differing_bytes']}; "
        f"raw size delta {vector['raw_size_delta']:+d}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="cold snapshot root containing bin/")
    parser.add_argument(
        "--game",
        action="append",
        choices=GAMES,
        help="limit the survey; repeat for multiple games",
    )
    parser.add_argument(
        "--gate",
        choices=("exact", "diagnostic", "calibration"),
        default="exact",
        help=(
            "exact fails on any raw mismatch; diagnostic validates the survey; "
            "calibration requires the pinned known vector"
        ),
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="omit verbose per-byte comparison details but retain the full vector",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    selected_games = set(args.game or GAMES)
    manifest = load_target_manifest(TARGETS)
    selected = [
        artifact
        for artifact in manifest["artifacts"]
        if artifact["game"] in selected_games
    ]

    artifacts: list[dict[str, object]] = []
    candidate_paths: list[Path] = []
    for artifact in selected:
        target = read_verified_artifact(ROOT, artifact)
        candidate = candidate_path(source, artifact)
        if not candidate.is_file():
            print(f"missing candidate output: {candidate}", file=sys.stderr)
            return 1
        candidate_paths.append(candidate)
        comparison = compare_blobs(target, candidate.read_bytes())
        vector = comparison_vector(comparison)
        entry = {
            "id": artifact["id"],
            "game": artifact["game"],
            "filename": candidate.name,
            "target_sha256": artifact["sha256"],
            "candidate_size": candidate.stat().st_size,
            "candidate_sha256": digest_file(candidate),
            "vector_sha256": canonical_json_sha256(vector),
            "vector": vector,
        }
        if not args.compact:
            entry["comparison"] = comparison
        artifacts.append(entry)

    output_root = source / "bin"
    try:
        output_identity = identity_record(
            file_set_identity(output_root, candidate_paths)
        )
        game_output_identities = {
            game: identity_record(
                file_set_identity(
                    output_root,
                    [
                        path
                        for path in candidate_paths
                        if path.relative_to(output_root).parts[0] == game
                    ],
                )
            )
            for game in sorted(selected_games)
        }
    except ToolchainError as error:
        print(f"cannot identify candidate outputs: {error}", file=sys.stderr)
        return 1

    object_root = source / "obj"
    object_paths = sorted(object_root.rglob("*.obj"))
    object_failures: list[dict[str, str]] = []
    for path in object_paths:
        try:
            parse_omf(path.read_bytes())
        except (OSError, OMFError) as error:
            object_failures.append(
                {"path": path.relative_to(source).as_posix(), "error": str(error)}
            )
    object_identity = None
    game_object_identities: dict[str, dict[str, object]] = {}
    if object_paths and not object_failures:
        try:
            object_identity = omf_identities(object_root, object_paths)
            for game in sorted(selected_games):
                paths = [
                    path
                    for path in object_paths
                    if path.relative_to(object_root).parts[0] == game
                ]
                if paths:
                    game_object_identities[game] = omf_identities(object_root, paths)
        except (OMFError, ToolchainError) as error:
            object_failures.append({"path": "obj", "error": str(error)})

    stable_game_object_identities = {
        game: {
            "count": identity["count"],
            "total_size": identity["total_size"],
            "dependency_timestamp_normalized_sha256": identity[
                "dependency_timestamp_normalized_sha256"
            ],
        }
        for game, identity in game_object_identities.items()
    }
    game_omf_identity_sha256 = canonical_json_sha256(
        stable_game_object_identities
    )

    strict_pass = all(item["vector"]["raw_exact"] for item in artifacts)
    rec98_core_pass = all(
        item["vector"]["rec98_rule1_core_dimensions_pass"] for item in artifacts
    )
    calibration: dict[str, object] | None = None
    calibration_checks: dict[str, object] | None = None
    calibration_pass = False
    if args.gate == "calibration":
        if selected_games != set(GAMES):
            print("calibration gate requires all five games", file=sys.stderr)
            return 1
        calibration = tomllib.loads(CALIBRATION.read_text(encoding="utf-8"))
        expected_artifacts = {
            item["id"]: item for item in calibration["artifacts"]
        }
        actual_artifacts = {item["id"]: item for item in artifacts}
        artifact_set_match = set(expected_artifacts) == set(actual_artifacts)
        artifact_matches = {
            artifact_id: bool(
                artifact_id in actual_artifacts
                and actual_artifacts[artifact_id]["candidate_sha256"]
                == expected["candidate_sha256"]
                and actual_artifacts[artifact_id]["candidate_size"]
                == expected["candidate_size"]
                and actual_artifacts[artifact_id]["vector_sha256"]
                == expected["vector_sha256"]
            )
            for artifact_id, expected in expected_artifacts.items()
        }
        expected_outputs = calibration["candidate_outputs"]
        output_match = output_identity == {
            "count": expected_outputs["count"],
            "total_size": expected_outputs["total_size"],
            "sha256": expected_outputs["sha256"],
        }
        expected_omf = calibration["omf"]
        omf_games = expected_omf["games"]
        omf_game_matches = {
            game: bool(
                game in game_object_identities
                and game_object_identities[game]["count"] == expected["count"]
                and game_object_identities[game][
                    "dependency_timestamp_normalized_sha256"
                ]
                == expected["dependency_timestamp_normalized_sha256"]
            )
            for game, expected in omf_games.items()
        }
        omf_game_identity_match = (
            game_omf_identity_sha256 == expected_omf["games_sha256"]
        )
        archive = source.parent / "source.tar"
        receipt_path = source.parent / "build-receipt.json"
        archive_match = bool(
            archive.is_file()
            and archive.stat().st_size == calibration["source_archive_size"]
            and digest_file(archive) == calibration["source_archive_sha256"]
        )
        receipt_match = False
        if receipt_path.is_file():
            try:
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt_match = bool(
                    receipt["cold"]
                    and receipt["returncode"] == 0
                    and receipt["source_revision"] == calibration["source_revision"]
                    and receipt["source_archive"]["sha256"]
                    == calibration["source_archive_sha256"]
                )
            except (OSError, KeyError, TypeError, json.JSONDecodeError):
                receipt_match = False
        calibration_checks = {
            "source_archive": archive_match,
            "cold_build_receipt": receipt_match,
            "candidate_output_identity": output_match,
            "artifact_set": artifact_set_match,
            "artifacts": artifact_matches,
            "omf_all_valid": bool(object_paths) and not object_failures,
            "omf_object_count": len(object_paths)
            == expected_omf["all_object_count"],
            "omf_games": omf_game_matches,
            "omf_game_identity": omf_game_identity_match,
        }
        calibration_pass = bool(
            archive_match
            and receipt_match
            and output_match
            and artifact_set_match
            and all(artifact_matches.values())
            and object_paths
            and not object_failures
            and len(object_paths) == expected_omf["all_object_count"]
            and set(omf_games) == set(game_object_identities)
            and all(omf_game_matches.values())
            and omf_game_identity_match
        )
    report = {
        "schema_version": 1,
        "kind": "untrusted-rec98-pc98-output-survey",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "games": sorted(selected_games),
        "compact": args.compact,
        "policy": "Raw zero-difference is the only exact verdict.",
        "policy_views": {
            "local_strict_raw_pass": strict_pass,
            "rec98_rule1_core_dimensions_pass": rec98_core_pass,
            "differ": strict_pass != rec98_core_pass,
            "note": (
                "The ReC98 view models only its stated program-image and "
                "unordered-relocation core; it never changes the local verdict."
            ),
        },
        "artifact_count": len(artifacts),
        "exact_count": sum(bool(item["vector"]["raw_exact"]) for item in artifacts),
        "calibration_vector_pass": calibration_pass,
        "calibration_checks": calibration_checks,
        "candidate_outputs": output_identity,
        "game_candidate_outputs": game_output_identities,
        "omf_objects": {
            "all_valid": bool(object_paths) and not object_failures,
            **(object_identity or {"count": len(object_paths)}),
            "failures": object_failures,
        },
        "game_omf_objects": game_object_identities,
        "game_omf_stable_identity_sha256": game_omf_identity_sha256,
        "artifacts": artifacts,
    }
    output = args.output or source.parent / "rec98-pc98-survey.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in artifacts:
        grouped[str(item["game"])].append(item)
    for game in sorted(grouped):
        items = grouped[game]
        exact = sum(bool(item["vector"]["raw_exact"]) for item in items)
        rec98 = sum(
            bool(item["vector"]["rec98_rule1_core_dimensions_pass"])
            for item in items
        )
        print(f"{game}: local raw {exact}/{len(items)}; ReC98 core {rec98}/{len(items)}")
        for item in items:
            if not item["vector"]["raw_exact"]:
                hints = ", ".join(item["vector"]["routing_hints"])
                triage = triage_summary(item["vector"])
                print(f"  REJECT {item['filename']}: {hints} [{triage}]")
    print(f"OMF objects: {len(object_paths) - len(object_failures)}/{len(object_paths)} valid")
    print(f"strict raw gate: {'PASS' if strict_pass else 'FAIL'}")
    if args.gate == "calibration":
        print(f"known all-game vector: {'PASS' if calibration_pass else 'FAIL'}")
    print(f"report: {output}")
    valid_survey = bool(artifacts) and bool(object_paths) and not object_failures
    if args.gate == "exact":
        passed = strict_pass
    elif args.gate == "calibration":
        passed = calibration_pass
    else:
        passed = valid_survey
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
