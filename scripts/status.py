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

    per_artifact: dict[str, dict[str, object]] = {}
    for artifact in (item for item in manifest["artifacts"] if item["game"] == "th04"):
        rows = [row for row in units if row["artifact"] == artifact["id"]]
        state_counts = Counter(row["state"] for row in rows)
        state_bytes: dict[str, int] = defaultdict(int)
        for row in rows:
            state_bytes[row["state"]] += int(row["size"], 0)
        known_authored = sum(
            int(row["size"], 0) for row in rows if row["origin"] == "authored"
        )
        exact_authored = sum(
            int(row["size"], 0)
            for row in rows
            if row["origin"] == "authored" and row["state"] == "exact"
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
            print(
                f"{artifact_id:12} units={report['unit_count']:4} "
                f"known-authored={report['known_authored_bytes']:7} "
                f"exact={report['exact_authored_bytes']:7} ({percent_text})"
            )
        print(output["warning"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
