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
        rows = [row for row in units if row["artifact"] == artifact["id"]]
        state_counts = Counter(row["state"] for row in rows)
        state_bytes: dict[str, int] = defaultdict(int)
        for row in rows:
            state_bytes[row["state"]] += int(row["size"], 0)
        reviewed_authored = [
            row
            for row in rows
            if row["origin"] == "authored"
            and row["boundary_state"] in {"reviewed", "shared"}
        ]
        known_authored = sum(int(row["size"], 0) for row in reviewed_authored)
        exact_authored = sum(
            int(row["size"], 0)
            for row in reviewed_authored
            if row["state"] == "exact"
        )
        reviewed_functions = [
            row
            for row in functions
            if row["artifact"] == artifact["id"]
            and row["boundary_state"] in {"reviewed", "shared"}
        ]
        exact_functions = [row for row in reviewed_functions if row["state"] == "exact"]
        artifact_boundaries = [
            row for row in boundaries if row["artifact"] == artifact["id"]
        ]
        reconstruction_candidates = [
            row for row in artifact_boundaries if row["work_queue"] == "reconstruct"
        ]
        candidate_states = Counter(
            row["accepted_state"] for row in reconstruction_candidates
        )
        per_artifact[artifact["id"]] = {
            "target_size": artifact["size"],
            "unit_count": len(rows),
            "states": dict(sorted(state_counts.items())),
            "state_bytes": dict(sorted(state_bytes.items())),
            "known_authored_bytes": known_authored,
            "exact_authored_bytes": exact_authored,
            "exact_authored_percent": (
                round(exact_authored * 100 / known_authored, 6)
                if known_authored
                else None
            ),
            "reviewed_authored_functions": len(reviewed_functions),
            "exact_authored_functions": len(exact_functions),
            "exact_authored_function_percent": (
                round(len(exact_functions) * 100 / len(reviewed_functions), 6)
                if reviewed_functions
                else None
            ),
            "boundary_observations": len(artifact_boundaries),
            "authored_function_candidates": len(reconstruction_candidates),
            "authored_candidate_states": dict(sorted(candidate_states.items())),
            "original_asm_attestation_candidates": sum(
                row["work_queue"] == "attest-asm" for row in artifact_boundaries
            ),
            "excluded_boundary_observations": sum(
                row["work_queue"] == "exclude" for row in artifact_boundaries
            ),
        }
    output = {
        "schema_version": 1,
        "canonicality": manifest["source"]["canonicality"],
        "artifacts": per_artifact,
        "warning": "Percentages use only reviewed ledger denominators; null means no honest denominator exists yet.",
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
            print(
                f"{artifact_id:12} units={report['unit_count']:4} "
                f"known-authored={report['known_authored_bytes']:7} "
                f"exact={report['exact_authored_bytes']:7} ({percent_text}) "
                f"functions={report['exact_authored_functions']}/"
                f"{report['reviewed_authored_functions']} ({function_percent_text})"
            )
            candidate_states = report["authored_candidate_states"]
            print(
                f"{'':12} boundary-observations={report['boundary_observations']:4} "
                f"authored-candidates={report['authored_function_candidates']:4} "
                f"exact={candidate_states.get('exact', 0):3} "
                f"blocked={candidate_states.get('blocked', 0):2} "
                f"unreviewed={candidate_states.get('unreviewed', 0):3} "
                f"asm-attest={report['original_asm_attestation_candidates']:2}"
            )
        print(output["warning"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
