#!/usr/bin/env python3
"""Validate the tracked all-artifact TH04 function-boundary ledger."""

from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boundary_review.build_function_boundary_ledger import HEADER, parse_function_overrides


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "config" / "th04_function_boundaries.csv"
MAIN_LEDGER = ROOT / "config" / "th04_main_authored_functions.csv"
REVIEW_CONFIG = ROOT / "config" / "th04_boundary_review.toml"
EVIDENCE_LEDGER = ROOT / "config" / "evidence.csv"
ARTIFACTS = ("th04-op", "th04-main", "th04-maine", "th04-zun")
BOUNDARY_STATES = {"reviewed", "corroborated", "provisional", "excluded"}
ORIGINS = {"authored", "original-asm", "compiler", "library", "data"}
WORK_QUEUES = {"reconstruct", "attest-asm", "exclude"}
ACCEPTED_STATES = {"exact", "blocked", "unreviewed", "excluded"}


class ValidationError(ValueError):
    pass


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != HEADER:
            raise ValidationError(f"unexpected boundary ledger header: {path}")
        return list(reader)


def validate_reviewed_overrides(
    rows: list[dict[str, str]],
    review_rules: dict[tuple[str, int], dict[str, object]],
    evidence_by_id: dict[str, dict[str, str]],
) -> None:
    indexed = {
        (row["artifact"], int(row["payload_offset"], 0)): row
        for row in rows
    }
    for key, rule in review_rules.items():
        if "reviewed_body_size" not in rule:
            continue
        row = indexed.get(key)
        if row is None:
            raise ValidationError(
                f"target-reviewed override has no ledger row: {key[0]} {key[1]:#x}"
            )
        reviewed_size = int(rule["reviewed_body_size"])
        if (
            row["boundary_state"] != "reviewed"
            or int(row["body_size"], 0) != reviewed_size
            or int(row["body_span"], 0) != reviewed_size
        ):
            raise ValidationError(
                f"target-reviewed override did not project exactly: {row['id']}"
            )
        evidence_id = str(rule["review_evidence_id"])
        evidence = evidence_by_id.get(evidence_id)
        if evidence is None:
            raise ValidationError(
                f"target-reviewed override lacks tracked evidence: {evidence_id}"
            )
        if (
            evidence["artifact"] != key[0]
            or evidence["oracle"] != "boundary-ownership"
            or evidence["result"] != "pass"
            or evidence["evidence_class"] != "target-analysis"
        ):
            raise ValidationError(
                f"target-reviewed override has invalid evidence authority: {evidence_id}"
            )
        if not evidence["extent_start"] or not evidence["extent_size"]:
            raise ValidationError(
                f"target-reviewed override evidence lacks extent: {evidence_id}"
            )
        evidence_start = int(evidence["extent_start"], 0)
        evidence_size = int(evidence["extent_size"], 0)
        if (
            evidence_start > key[1]
            or evidence_start + evidence_size < key[1] + reviewed_size
        ):
            raise ValidationError(
                f"target-reviewed override escapes evidence extent: {evidence_id}"
            )


def validate(rows: list[dict[str, str]]) -> None:
    ids: set[str] = set()
    addresses: set[tuple[str, int]] = set()
    previous_key: tuple[int, int] | None = None
    artifact_order = {artifact: index for index, artifact in enumerate(ARTIFACTS)}
    for row in rows:
        artifact = row["artifact"]
        if artifact not in artifact_order:
            raise ValidationError(f"unknown artifact: {artifact}")
        offset = int(row["payload_offset"], 0)
        analysis_linear = int(row["analysis_linear"], 0)
        segment_offset = int(row["segment_offset"], 0)
        body_size = int(row["body_size"], 0)
        body_span = int(row["body_span"], 0)
        expected_segment = "com-payload" if artifact == "th04-zun" else "mz-load-module"
        if (
            offset < 0
            or segment_offset != offset
            or analysis_linear != 0x10000 + offset
            or row["segment_identity"] != expected_segment
        ):
            raise ValidationError(f"invalid address pair in {row['id']}")
        if body_size < 0 or body_span < body_size:
            raise ValidationError(f"invalid body extent in {row['id']}")
        expected_id = f"{artifact}-boundary-{offset:05x}"
        if row["id"] != expected_id or row["id"] in ids:
            raise ValidationError(f"invalid or duplicate ID: {row['id']}")
        ids.add(row["id"])
        address_key = (artifact, offset)
        if address_key in addresses:
            raise ValidationError(f"duplicate artifact address: {address_key}")
        addresses.add(address_key)
        sort_key = (artifact_order[artifact], offset)
        if previous_key is not None and sort_key <= previous_key:
            raise ValidationError("boundary ledger is not deterministically sorted")
        previous_key = sort_key
        if row["boundary_state"] not in BOUNDARY_STATES:
            raise ValidationError(f"invalid boundary state in {row['id']}")
        if row["origin"] not in ORIGINS:
            raise ValidationError(f"invalid origin in {row['id']}")
        if row["work_queue"] not in WORK_QUEUES:
            raise ValidationError(f"invalid work queue in {row['id']}")
        if row["accepted_state"] not in ACCEPTED_STATES:
            raise ValidationError(f"invalid accepted state in {row['id']}")
        if not row["name"] or not row["observation"] or not row["evidence_basis"]:
            raise ValidationError(f"missing provenance field in {row['id']}")
        if row["boundary_state"] == "excluded":
            if row["work_queue"] != "exclude" or row["accepted_state"] != "excluded":
                raise ValidationError(f"excluded boundary entered a work queue: {row['id']}")
        elif row["origin"] == "authored" and row["work_queue"] != "reconstruct":
            raise ValidationError(f"authored boundary missing reconstruct queue: {row['id']}")
        elif row["origin"] == "original-asm" and row["work_queue"] != "attest-asm":
            raise ValidationError(f"ASM boundary missing attestation queue: {row['id']}")
        elif row["origin"] not in {"authored", "original-asm"} and row["work_queue"] != "exclude":
            raise ValidationError(f"non-product boundary entered work queue: {row['id']}")
        if row["accepted_state"] in {"exact", "blocked"}:
            if row["boundary_state"] not in {"reviewed", "shared"}:
                raise ValidationError(f"accepted state on provisional boundary: {row['id']}")
            if row["origin"] != "authored":
                raise ValidationError(f"accepted state lacks authored ownership: {row['id']}")
            if row["accepted_state"] == "exact" and not row["source_ref"]:
                raise ValidationError(f"exact state lacks maintained source: {row['id']}")
        if "ghidra" in row["observation"]:
            if not row["ghidra_contiguous"] or not row["ghidra_range_count"]:
                raise ValidationError(f"missing Ghidra metadata in {row['id']}")
        elif any(row[field] for field in ("ghidra_contiguous", "ghidra_range_count")):
            raise ValidationError(f"orphaned Ghidra metadata in {row['id']}")
        if "tasm-proc" in row["observation"]:
            if not row["tasm_proc"] or not row["tasm_distance"] or not row["tasm_listing_line"]:
                raise ValidationError(f"missing TASM metadata in {row['id']}")
        elif any(row[field] for field in ("tasm_proc", "tasm_distance", "tasm_listing_line")):
            raise ValidationError(f"orphaned TASM metadata in {row['id']}")

    missing = [artifact for artifact in ARTIFACTS if not any(row["artifact"] == artifact for row in rows)]
    if missing:
        raise ValidationError("missing artifacts: " + ", ".join(missing))

    with MAIN_LEDGER.open(newline="", encoding="utf-8") as stream:
        main_rows = list(csv.DictReader(stream))
    indexed = {(row["artifact"], int(row["analysis_linear"], 0)): row for row in rows}
    for source in main_rows:
        key = (source["artifact"], int(source["address"], 0))
        candidate = indexed.get(key)
        if candidate is None:
            raise ValidationError(f"missing accepted MAIN function at {key[1]:#x}")
        checks = {
            "boundary": candidate["boundary_state"] == source["boundary_state"],
            "state": candidate["accepted_state"] == source["state"],
            "name": candidate["name"] == source["name"],
            "source": candidate["source_ref"] == source["source"],
            "size": int(candidate["body_size"], 0) == int(source["size"], 0),
        }
        if not all(checks.values()):
            failed = ", ".join(name for name, passed in checks.items() if not passed)
            raise ValidationError(f"MAIN ledger projection mismatch at {key[1]:#x}: {failed}")


def main() -> int:
    try:
        rows = read_rows(LEDGER)
        validate(rows)
        review_config = tomllib.loads(REVIEW_CONFIG.read_text(encoding="utf-8"))
        review_rules = parse_function_overrides(review_config)
        with EVIDENCE_LEDGER.open(newline="", encoding="utf-8") as stream:
            evidence_by_id = {
                row["id"]: row for row in csv.DictReader(stream)
            }
        validate_reviewed_overrides(rows, review_rules, evidence_by_id)
        counts = Counter((row["artifact"], row["work_queue"]) for row in rows)
        print(f"function boundary ledger: PASS ({len(rows)} observations)")
        for key in sorted(counts):
            print(f"  {key[0]} {key[1]}={counts[key]}")
        return 0
    except (OSError, ValidationError, ValueError) as error:
        print(f"error: function boundary ledger invalid: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
