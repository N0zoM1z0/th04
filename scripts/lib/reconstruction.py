"""Shared strict and diagnostic views for reconstruction candidates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .omf import normalize_dependency_timestamps
from .toolchain import TreeIdentity, file_set_identity


def canonical_json_sha256(value: object) -> str:
    """Hash a JSON-compatible value without presentation-dependent whitespace."""

    encoded = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def identity_record(identity: TreeIdentity) -> dict[str, object]:
    """Return the stable public fields of a file-set identity."""

    return {
        "count": identity.file_count,
        "total_size": identity.total_size,
        "sha256": identity.sha256,
    }


def comparison_vector(comparison: dict[str, object]) -> dict[str, object]:
    """Return compact local-strict and ReC98-policy dimensions."""

    result: dict[str, object] = {
        "raw_exact": comparison["verdict"]["raw_exact"],
        "format_same": comparison["formats"]["same"],
        "left_format": comparison["formats"]["left"],
        "right_format": comparison["formats"]["right"],
        "routing_hints": comparison.get("routing_hints", []),
        "raw_left_size": comparison["raw"]["left_size"],
        "raw_right_size": comparison["raw"]["right_size"],
        "raw_size_delta": (
            comparison["raw"]["right_size"] - comparison["raw"]["left_size"]
        ),
        "raw_differing_bytes": comparison["raw"]["differing_bytes"],
        "raw_first_difference": comparison["raw"]["first_difference"],
        "raw_difference_run_count": comparison["raw"]["difference_run_count"],
        "raw_largest_difference_run": comparison["raw"]["largest_difference_run"],
        "raw_common_prefix": comparison["raw"]["common_prefix"],
        "raw_common_suffix": comparison["raw"]["common_suffix"],
    }
    if (
        comparison["formats"]["left"] == "mz"
        and comparison["formats"]["same"]
        and "mz" in comparison
    ):
        mz = comparison["mz"]
        result.update(
            {
                "format_integrity": comparison["format_integrity"]["both_valid"],
                "header_fields_exact": mz["header_fields"]["exact"],
                "header_changed_fields": mz["header_fields"]["changed"],
                "header_bytes_exact": mz["header_bytes"]["exact"],
                "header_left_size": mz["header_bytes"]["left_size"],
                "header_right_size": mz["header_bytes"]["right_size"],
                "header_differing_bytes": mz["header_bytes"]["differing_bytes"],
                "relocations_ordered_exact": mz["relocations"]["ordered_exact"],
                "relocations_multiset_exact": mz["relocations"]["multiset_exact"],
                "relocations_left_count": mz["relocations"]["left_count"],
                "relocations_right_count": mz["relocations"]["right_count"],
                "relocations_only_left_count": len(mz["relocations"]["only_left"]),
                "relocations_only_right_count": len(
                    mz["relocations"]["only_right"]
                ),
                "relocation_site_values_exact": mz["relocations"]["site_values"][
                    "exact"
                ],
                "relocation_site_value_difference_count": mz["relocations"][
                    "site_values"
                ]["differing_count"],
                "program_image_exact": mz["program_image"]["exact"],
                "program_left_size": mz["program_image"]["left_size"],
                "program_right_size": mz["program_image"]["right_size"],
                "program_differing_bytes": mz["program_image"]["differing_bytes"],
                "program_difference_run_count": mz["program_image"][
                    "difference_run_count"
                ],
                "program_largest_difference_run": mz["program_image"][
                    "largest_difference_run"
                ],
                "program_common_prefix": mz["program_image"]["common_prefix"],
                "program_common_suffix": mz["program_image"]["common_suffix"],
                "program_differences_at_relocation_sites": mz[
                    "program_difference_partition"
                ]["at_relocation_site_bytes"],
                "program_differences_outside_relocation_sites": mz[
                    "program_difference_partition"
                ]["outside_relocation_site_bytes"],
                "normalized_program_exact": mz["relocation_normalized_program"][
                    "exact"
                ],
                "normalized_program_differing_bytes": mz[
                    "relocation_normalized_program"
                ]["differing_bytes"],
                "overlay_exact": mz["overlay"]["exact"],
                "overlay_left_size": mz["overlay"]["left_size"],
                "overlay_right_size": mz["overlay"]["right_size"],
                "overlay_differing_bytes": mz["overlay"]["differing_bytes"],
            }
        )
        result["rec98_rule1_core_dimensions_pass"] = bool(
            result["program_image_exact"]
            and result["relocations_multiset_exact"]
        )
    elif comparison["formats"]["left"] == "com" and comparison["formats"]["same"]:
        result.update(
            {
                "com_differing_bytes": comparison["com_image"]["differing_bytes"],
                "com_difference_run_count": comparison["com_image"][
                    "difference_run_count"
                ],
                "com_common_prefix": comparison["com_image"]["common_prefix"],
                "com_common_suffix": comparison["com_image"]["common_suffix"],
            }
        )
        result["rec98_rule1_core_dimensions_pass"] = bool(result["raw_exact"])
    else:
        if "format_integrity" in comparison:
            result["format_integrity"] = comparison["format_integrity"].get(
                "both_valid", False
            )
            result["format_error"] = comparison["format_integrity"].get(
                "parse_error"
            )
        result["rec98_rule1_core_dimensions_pass"] = bool(result["raw_exact"])
    return result


def omf_identities(root: Path, paths: list[Path]) -> dict[str, object]:
    """Return raw and narrowly metadata-normalized identities for OMF files."""

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
