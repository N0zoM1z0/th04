#!/usr/bin/env python3
"""Derive reconstruction status from machine-readable ledgers."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def reviewed_authored_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return current reviewed authored byte owners for denominator accounting.

    Excluded authored rows are historical/superseded records kept so prior
    evidence remains addressable. They are not current physical ownership and
    therefore must not be counted in the reviewed authored-byte denominator.
    """

    return [
        row
        for row in rows
        if row["origin"] == "authored"
        and row["boundary_state"] in {"reviewed", "shared"}
        and row["state"] != "excluded"
    ]


def artifact_report(
    artifact: dict[str, object],
    units: list[dict[str, str]],
    functions: list[dict[str, str]],
    boundaries: list[dict[str, str]],
) -> dict[str, object]:
    """Keep packed-file byte accounting separate from decoded function state."""

    artifact_id = str(artifact["id"])
    rows = [row for row in units if row["artifact"] == artifact_id]
    state_counts = Counter(row["state"] for row in rows)
    state_bytes: dict[str, int] = defaultdict(int)
    for row in rows:
        state_bytes[row["state"]] += int(row["size"], 0)

    reviewed_authored = reviewed_authored_rows(rows)
    file_backed = [row for row in reviewed_authored if row["file_offset"]]
    decoded_only = [row for row in reviewed_authored if not row["file_offset"]]
    known_authored = sum(int(row["size"], 0) for row in file_backed)
    exact_authored = sum(
        int(row["size"], 0) for row in file_backed if row["state"] == "exact"
    )
    reviewed_functions = [
        row
        for row in functions
        if row["artifact"] == artifact_id
        and row["boundary_state"] in {"reviewed", "shared"}
    ]
    exact_functions = [row for row in reviewed_functions if row["state"] == "exact"]
    artifact_boundaries = [row for row in boundaries if row["artifact"] == artifact_id]
    reconstruction_candidates = [
        row for row in artifact_boundaries if row["work_queue"] == "reconstruct"
    ]
    asm_candidates = [
        row for row in artifact_boundaries if row["work_queue"] == "attest-asm"
    ]
    candidate_states = Counter(row["accepted_state"] for row in reconstruction_candidates)
    boundary_states = Counter(row["boundary_state"] for row in reconstruction_candidates)
    return {
        "target_size": artifact["size"],
        "unit_count": len(rows),
        "states": dict(sorted(state_counts.items())),
        "state_bytes": dict(sorted(state_bytes.items())),
        "known_authored_bytes": known_authored,
        "exact_authored_bytes": exact_authored,
        "exact_authored_percent": (
            round(exact_authored * 100 / known_authored, 6) if known_authored else None
        ),
        "decoded_only_source_owner_bytes": sum(int(row["size"], 0) for row in decoded_only),
        # The separate function ledger currently covers MAIN only. A zero for
        # another artifact would incorrectly imply that no functions exist.
        "reviewed_authored_functions": len(reviewed_functions) if artifact_id == "th04-main" else None,
        "exact_authored_functions": len(exact_functions) if artifact_id == "th04-main" else None,
        "exact_authored_function_percent": (
            round(len(exact_functions) * 100 / len(reviewed_functions), 6)
            if artifact_id == "th04-main" and reviewed_functions
            else None
        ),
        "boundary_observations": len(artifact_boundaries),
        "authored_function_candidates": len(reconstruction_candidates),
        "authored_boundary_states": dict(sorted(boundary_states.items())),
        "authored_candidate_states": dict(sorted(candidate_states.items())),
        "accepted_exact_authored_functions": candidate_states["exact"],
        "unresolved_target_derived_asm_candidates": sum(
            row["source_form"] == "target-derived-asm"
            and row["accepted_state"] not in {"exact", "excluded"}
            for row in reconstruction_candidates
        ),
        "original_asm_attestation_candidates": len(asm_candidates),
        "original_asm_provisional_boundaries": sum(
            row["boundary_state"] == "provisional" for row in asm_candidates
        ),
        "excluded_boundary_observations": sum(
            row["work_queue"] == "exclude" for row in artifact_boundaries
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = tomllib.loads(
        (ROOT / "config" / "targets.toml").read_text(encoding="utf-8")
    )
    with (ROOT / "config" / "units.csv").open(newline="", encoding="utf-8") as stream:
        units = list(csv.DictReader(stream))
    function_path = ROOT / "config" / "th04_main_authored_functions.csv"
    if function_path.is_file():
        with function_path.open(newline="", encoding="utf-8") as stream:
            functions = list(csv.DictReader(stream))
    else:
        functions = []
    boundary_path = ROOT / "config" / "th04_function_boundaries.csv"
    if boundary_path.is_file():
        with boundary_path.open(newline="", encoding="utf-8") as stream:
            boundaries = list(csv.DictReader(stream))
    else:
        boundaries = []

    per_artifact: dict[str, dict[str, object]] = {}
    for artifact in (item for item in manifest["artifacts"] if item["game"] == "th04"):
        per_artifact[artifact["id"]] = artifact_report(
            artifact, units, functions, boundaries
        )
    output = {
        "schema_version": 1,
        "canonicality": manifest["source"]["canonicality"],
        "artifacts": per_artifact,
        "warning": (
            "Byte percentages cover only reviewed file-backed unit extents; "
            "decoded function acceptance and boundary confidence are separate. "
            "null means no honest denominator exists yet."
        ),
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"target canonicality: {output['canonicality']}")
        for artifact_id, report in per_artifact.items():
            percent = report["exact_authored_percent"]
            percent_text = "n/a" if percent is None else f"{percent:.6f}%"
            function_percent = report["exact_authored_function_percent"]
            function_percent_text = (
                "n/a" if function_percent is None else f"{function_percent:.6f}%"
            )
            function_text = (
                f"{report['exact_authored_functions']}/{report['reviewed_authored_functions']} "
                f"({function_percent_text})"
                if report["reviewed_authored_functions"] is not None else "n/a"
            )
            print(
                f"{artifact_id:12} units={report['unit_count']:4} "
                f"file-backed-authored={report['exact_authored_bytes']}/"
                f"{report['known_authored_bytes']} ({percent_text}) "
                f"main-function-ledger={function_text} "
                f"decoded-source-owner-bytes={report['decoded_only_source_owner_bytes']}"
            )
            candidate_states = report["authored_candidate_states"]
            boundary_states = report["authored_boundary_states"]
            print(
                f"{'':12} boundary-observations={report['boundary_observations']:4} "
                f"authored-candidates={report['authored_function_candidates']:4} "
                f"boundary-r/c/p={boundary_states.get('reviewed', 0)}/"
                f"{boundary_states.get('corroborated', 0)}/"
                f"{boundary_states.get('provisional', 0)} "
                f"function-exact={report['accepted_exact_authored_functions']:3} "
                f"blocked={candidate_states.get('blocked', 0):2} "
                f"unreviewed={candidate_states.get('unreviewed', 0):3} "
                f"origin-open={report['unresolved_target_derived_asm_candidates']:2} "
                f"asm-attest={report['original_asm_attestation_candidates']:2} "
                f"asm-provisional={report['original_asm_provisional_boundaries']:2}"
            )
        print(output["warning"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
