#!/usr/bin/env python3
"""Fail closed on malformed reconstruction ledgers and exact claims."""

from __future__ import annotations

import csv
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
UNIT_HEADER = [
    "id", "artifact", "kind", "segment", "offset", "file_offset", "size",
    "compare_size", "boundary_state", "origin", "state", "name", "source",
    "evidence_ids", "replay_command", "notes",
]
EVIDENCE_HEADER = [
    "id", "claim_id", "oracle", "artifact", "location", "evidence_class",
    "result", "tool", "command", "input_sha256", "output_sha256",
    "observed_utc", "notes",
]
HYPOTHESIS_HEADER = [
    "id", "subject", "predicate", "value", "status", "confidence",
    "evidence_ids", "notes",
]
KNOWLEDGE_HEADER = [
    "id", "kind", "scope", "subject", "confidence", "evidence_ids",
    "source_refs", "summary", "last_verified_utc",
]
UNIT_STATES = {
    "candidate", "boundary-reviewed", "source-present", "structural", "exact",
    "blocked", "excluded",
}
BOUNDARY_STATES = {"provisional", "reviewed", "shared", "not-applicable"}
ORIGINS = {"unknown", "authored", "compiler", "library", "asset", "padding", "original-asm"}
EVIDENCE_RESULTS = {"pass", "fail", "inconclusive", "not-run"}
EVIDENCE_CLASSES = {
    "target", "target-analysis", "compiler", "linker", "binary", "runtime",
    "reproducibility", "cross-game", "external", "inference", "control-plane",
    "upstream",
}
HYPOTHESIS_STATUS = {"open", "confirmed", "rejected", "blocked"}
CONFIDENCE = {
    "observed", "compiler-observed", "runtime-observed", "corroborated",
    "inferred", "unknown",
}
KNOWLEDGE_KINDS = {
    "fact", "recipe", "pattern", "hazard", "negative-result", "open-question",
}


def read_csv(path: Path, expected: list[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != expected:
            raise ValueError(
                f"{path.relative_to(ROOT)} header mismatch: {reader.fieldnames}"
            )
        return list(reader)


def integer(value: str, context: str, *, allow_empty: bool = False) -> int | None:
    if allow_empty and not value:
        return None
    try:
        return int(value, 0)
    except ValueError as error:
        raise ValueError(f"{context}: expected integer, got {value!r}") from error


def split_ids(value: str) -> list[str]:
    return [part for part in value.split(";") if part]


def unique(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for line, row in enumerate(rows, start=2):
        row_id = row["id"]
        if not row_id or row_id in result:
            raise ValueError(f"{label}:{line}: id must be nonempty and unique")
        result[row_id] = row
    return result


def accepted_oracle_passes(
    evidence_ids: list[str],
    evidence: dict[str, dict[str, str]],
    oracle_by_id: dict[str, dict[str, object]],
    non_acceptance_classes: set[str],
) -> set[str]:
    """Return required-grade passes; diagnostic provenance cannot be promoted."""

    passed: set[str] = set()
    for evidence_id in evidence_ids:
        row = evidence[evidence_id]
        oracle_id = row["oracle"]
        accepted_classes = oracle_by_id[oracle_id].get(
            "accepts_evidence_classes", []
        )
        if (
            row["result"] == "pass"
            and row["evidence_class"] not in non_acceptance_classes
            and row["evidence_class"] in accepted_classes
        ):
            passed.add(oracle_id)
    return passed


def main() -> int:
    try:
        targets = tomllib.loads((CONFIG / "targets.toml").read_text(encoding="utf-8"))
        oracle_config = tomllib.loads(
            (CONFIG / "oracles.toml").read_text(encoding="utf-8")
        )
        artifacts = {item["id"]: item for item in targets["artifacts"]}
        oracle_ids = {item["id"] for item in oracle_config["oracles"]}
        oracle_by_id = {item["id"]: item for item in oracle_config["oracles"]}
        required_oracles = set(oracle_config["policy"]["exact_requires"])
        non_acceptance_classes = set(
            oracle_config["policy"]["non_acceptance_evidence_classes"]
        )
        if not required_oracles <= oracle_ids:
            raise ValueError("oracles.toml exact_requires names an unknown Oracle")
        for oracle_id in required_oracles:
            accepted = set(oracle_by_id[oracle_id].get("accepts_evidence_classes", []))
            if not accepted or not accepted <= EVIDENCE_CLASSES:
                raise ValueError(
                    f"required Oracle {oracle_id!r} lacks valid accepted evidence classes"
                )

        units = read_csv(CONFIG / "units.csv", UNIT_HEADER)
        evidence_rows = read_csv(CONFIG / "evidence.csv", EVIDENCE_HEADER)
        hypotheses = read_csv(CONFIG / "hypotheses.csv", HYPOTHESIS_HEADER)
        knowledge_rows = read_csv(CONFIG / "knowledge.csv", KNOWLEDGE_HEADER)
        units_by_id = unique(units, "config/units.csv")
        evidence = unique(evidence_rows, "config/evidence.csv")
        hypotheses_by_id = unique(hypotheses, "config/hypotheses.csv")
        knowledge = unique(knowledge_rows, "config/knowledge.csv")

        for line, row in enumerate(evidence_rows, start=2):
            if row["oracle"] not in oracle_ids:
                raise ValueError(f"evidence.csv:{line}: unknown Oracle {row['oracle']!r}")
            if row["artifact"] and row["artifact"] not in artifacts:
                raise ValueError(f"evidence.csv:{line}: unknown artifact")
            if row["evidence_class"] not in EVIDENCE_CLASSES:
                raise ValueError(f"evidence.csv:{line}: invalid evidence class")
            if row["result"] not in EVIDENCE_RESULTS:
                raise ValueError(f"evidence.csv:{line}: invalid result")

        for line, row in enumerate(hypotheses, start=2):
            if row["status"] not in HYPOTHESIS_STATUS:
                raise ValueError(f"hypotheses.csv:{line}: invalid status")
            if row["confidence"] not in CONFIDENCE:
                raise ValueError(f"hypotheses.csv:{line}: invalid confidence")
            for evidence_id in split_ids(row["evidence_ids"]):
                if evidence_id not in evidence:
                    raise ValueError(
                        f"hypotheses.csv:{line}: unknown evidence {evidence_id!r}"
                    )

        for line, row in enumerate(evidence_rows, start=2):
            if row["claim_id"] and row["claim_id"] not in hypotheses_by_id:
                raise ValueError(f"evidence.csv:{line}: unknown claim_id")

        for line, row in enumerate(knowledge_rows, start=2):
            if row["kind"] not in KNOWLEDGE_KINDS:
                raise ValueError(f"knowledge.csv:{line}: invalid kind")
            if row["confidence"] not in CONFIDENCE:
                raise ValueError(f"knowledge.csv:{line}: invalid confidence")
            if not row["scope"] or not row["subject"] or not row["summary"]:
                raise ValueError(f"knowledge.csv:{line}: missing required text")
            for evidence_id in split_ids(row["evidence_ids"]):
                if evidence_id not in evidence:
                    raise ValueError(
                        f"knowledge.csv:{line}: unknown evidence {evidence_id!r}"
                    )

        spans: dict[str, list[tuple[int, int, str]]] = {}
        for line, row in enumerate(units, start=2):
            if row["artifact"] not in artifacts:
                raise ValueError(f"units.csv:{line}: unknown artifact")
            if row["state"] not in UNIT_STATES:
                raise ValueError(f"units.csv:{line}: invalid state")
            if row["boundary_state"] not in BOUNDARY_STATES:
                raise ValueError(f"units.csv:{line}: invalid boundary state")
            if row["origin"] not in ORIGINS:
                raise ValueError(f"units.csv:{line}: invalid origin")
            size = integer(row["size"], f"units.csv:{line} size")
            compare_size = integer(
                row["compare_size"], f"units.csv:{line} compare_size"
            )
            file_offset = integer(
                row["file_offset"], f"units.csv:{line} file_offset",
                allow_empty=True,
            )
            if size is None or compare_size is None or size <= 0 or compare_size < size:
                raise ValueError(f"units.csv:{line}: invalid size/compare_size")
            if file_offset is not None:
                if file_offset < 0:
                    raise ValueError(f"units.csv:{line}: negative file offset")
                span = (file_offset, file_offset + compare_size, row["id"])
                for start, end, other in spans.setdefault(row["artifact"], []):
                    if span[0] < end and start < span[1]:
                        raise ValueError(
                            f"units.csv:{line}: byte ownership overlaps {other!r}"
                        )
                spans[row["artifact"]].append(span)
            evidence_ids = split_ids(row["evidence_ids"])
            for evidence_id in evidence_ids:
                if evidence_id not in evidence:
                    raise ValueError(
                        f"units.csv:{line}: unknown evidence {evidence_id!r}"
                    )
            if row["state"] == "exact":
                if row["boundary_state"] not in {"reviewed", "shared"}:
                    raise ValueError(f"units.csv:{line}: exact boundary not reviewed")
                if not row["source"] or not row["replay_command"]:
                    raise ValueError(f"units.csv:{line}: exact unit lacks source/replay")
                passed = accepted_oracle_passes(
                    evidence_ids,
                    evidence,
                    oracle_by_id,
                    non_acceptance_classes,
                )
                for required in required_oracles:
                    if required not in passed:
                        raise ValueError(
                            f"units.csv:{line}: exact unit lacks passing {required} evidence"
                        )

        print(
            "tracking OK: "
            f"{len(units_by_id)} units, {len(evidence)} evidence rows, "
            f"{len(hypotheses_by_id)} hypotheses, {len(knowledge)} knowledge rows, "
            f"{len(artifacts)} targets"
        )
        return 0
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
