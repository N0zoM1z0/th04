#!/usr/bin/env python3
"""Fail closed on malformed reconstruction ledgers and exact claims."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
import shlex
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
    "id", "claim_id", "oracle", "artifact", "unit_id", "extent_start",
    "extent_size", "location", "evidence_class",
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
FUNCTION_HEADER = [
    "id", "artifact", "address", "file_offset", "size", "boundary_state",
    "state", "name", "owner_unit", "source", "evidence_ids", "notes",
]
FUNCTION_STATES = {"candidate", "boundary-reviewed", "exact", "blocked", "excluded"}
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


def read_csv(
    path: Path, expected: list[str], *, repository_root: Path = ROOT
) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != expected:
            raise ValueError(
                f"{path.relative_to(repository_root)} header mismatch: {reader.fieldnames}"
            )
        rows = list(reader)
        for line, row in enumerate(rows, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"{path.relative_to(repository_root)}:{line}: column count mismatch")
        return rows


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
    *,
    artifact: str | None = None,
    unit_id: str | None = None,
    extent_start: int | None = None,
    extent_size: int | None = None,
    global_evidence_oracles: set[str] | None = None,
    artifact_evidence_oracles: set[str] | None = None,
) -> set[str]:
    """Return replayable required-grade passes with explicit claim scoping."""

    passed: set[str] = set()
    globally_scoped = global_evidence_oracles or set()
    artifact_scoped = artifact_evidence_oracles or set()
    for evidence_id in evidence_ids:
        row = evidence[evidence_id]
        oracle_id = row["oracle"]
        accepted_classes = oracle_by_id[oracle_id].get(
            "accepts_evidence_classes", []
        )
        base_pass = (
            row["result"] == "pass"
            and row["evidence_class"] not in non_acceptance_classes
            and row["evidence_class"] in accepted_classes
        )
        if not base_pass:
            continue
        if unit_id is None:
            scoped = artifact is None or row.get("artifact") == artifact or (
                not row.get("artifact") and oracle_id in globally_scoped
            )
        elif oracle_id in globally_scoped:
            scoped = not any(
                row.get(field)
                for field in ("artifact", "unit_id", "extent_start", "extent_size")
            )
        elif oracle_id in artifact_scoped:
            scoped = row.get("artifact") == artifact and not any(
                row.get(field) for field in ("unit_id", "extent_start", "extent_size")
            )
        else:
            try:
                row_start = integer(
                    row.get("extent_start", ""),
                    f"evidence {evidence_id!r} extent_start",
                )
                row_size = integer(
                    row.get("extent_size", ""),
                    f"evidence {evidence_id!r} extent_size",
                )
            except ValueError:
                scoped = False
            else:
                scoped = (
                    row.get("artifact") == artifact
                    and row.get("unit_id") == unit_id
                    and row_start == extent_start
                    and row_size == extent_size
                )
        replayable = all(
            row.get(field)
            for field in ("tool", "command", "input_sha256", "output_sha256", "observed_utc")
        )
        hashes_valid = all(
            len(str(row.get(field, ""))) == 64
            and all(character in "0123456789abcdef" for character in str(row[field]))
            for field in ("input_sha256", "output_sha256")
        )
        timestamp_valid = False
        observed_utc = row.get("observed_utc") or ""
        if observed_utc.endswith("Z"):
            try:
                datetime.fromisoformat(observed_utc.removesuffix("Z") + "+00:00")
                timestamp_valid = True
            except ValueError:
                pass
        raw_equality_valid = (
            oracle_id != "raw-bytes"
            or row.get("input_sha256") == row.get("output_sha256")
        )
        if scoped and replayable and hashes_valid and timestamp_valid and raw_equality_valid:
            passed.add(oracle_id)
    return passed


def validate_replay_command(root: Path, value: str, context: str) -> None:
    """Require an exact replay to name a checked-in, shell-free driver."""

    try:
        tokens = shlex.split(value)
    except ValueError as error:
        raise ValueError(f"{context}: invalid replay command: {error}") from error
    shell_metacharacters = set("|&;<>()`$>\n")
    if not tokens or any(shell_metacharacters & set(token) for token in tokens):
        raise ValueError(f"{context}: replay command must be a shell-free argv")
    candidates = []
    if tokens[0] in {"python", "python3", "bash", "sh"} and len(tokens) > 1:
        candidates.append(tokens[1])
    else:
        candidates.append(tokens[0])
    script = Path(candidates[0])
    if script.is_absolute() or ".." in script.parts or not script.parts:
        raise ValueError(f"{context}: replay driver must be repository-relative")
    if script.parts[0] in {".analysis", ".tools", "ghidra-project", "_reference"}:
        raise ValueError(f"{context}: replay driver must be checked in")
    resolved = root / script
    if not resolved.is_file() or resolved.is_symlink():
        raise ValueError(f"{context}: replay driver does not exist: {script}")


def main(repository_root: Path = ROOT) -> int:
    try:
        config = repository_root / "config"
        targets = tomllib.loads((config / "targets.toml").read_text(encoding="utf-8"))
        oracle_config = tomllib.loads(
            (config / "oracles.toml").read_text(encoding="utf-8")
        )
        artifacts = {item["id"]: item for item in targets["artifacts"]}
        oracle_ids = {item["id"] for item in oracle_config["oracles"]}
        oracle_by_id = {item["id"]: item for item in oracle_config["oracles"]}
        required_oracles = set(oracle_config["policy"]["exact_requires"])
        non_acceptance_classes = set(
            oracle_config["policy"]["non_acceptance_evidence_classes"]
        )
        global_evidence_oracles = set(
            oracle_config["policy"]["global_evidence_oracles"]
        )
        artifact_evidence_oracles = set(
            oracle_config["policy"]["artifact_evidence_oracles"]
        )
        if not required_oracles <= oracle_ids:
            raise ValueError("oracles.toml exact_requires names an unknown Oracle")
        if not global_evidence_oracles <= required_oracles:
            raise ValueError("global evidence is allowed for a non-required Oracle")
        if not artifact_evidence_oracles <= required_oracles:
            raise ValueError("artifact evidence is allowed for a non-required Oracle")
        if global_evidence_oracles & artifact_evidence_oracles:
            raise ValueError("an Oracle cannot be both global and artifact-scoped")
        for oracle_id in required_oracles:
            accepted = set(oracle_by_id[oracle_id].get("accepts_evidence_classes", []))
            if not accepted or not accepted <= EVIDENCE_CLASSES:
                raise ValueError(
                    f"required Oracle {oracle_id!r} lacks valid accepted evidence classes"
                )

        units = read_csv(config / "units.csv", UNIT_HEADER, repository_root=repository_root)
        evidence_rows = read_csv(
            config / "evidence.csv", EVIDENCE_HEADER, repository_root=repository_root
        )
        hypotheses = read_csv(
            config / "hypotheses.csv", HYPOTHESIS_HEADER, repository_root=repository_root
        )
        knowledge_rows = read_csv(
            config / "knowledge.csv", KNOWLEDGE_HEADER, repository_root=repository_root
        )
        function_path = config / "th04_main_authored_functions.csv"
        function_rows = (
            read_csv(function_path, FUNCTION_HEADER, repository_root=repository_root)
            if function_path.is_file()
            else []
        )
        units_by_id = unique(units, "config/units.csv")
        evidence = unique(evidence_rows, "config/evidence.csv")
        hypotheses_by_id = unique(hypotheses, "config/hypotheses.csv")
        knowledge = unique(knowledge_rows, "config/knowledge.csv")
        functions_by_id = unique(function_rows, "config/th04_main_authored_functions.csv")

        for line, row in enumerate(evidence_rows, start=2):
            if row["oracle"] not in oracle_ids:
                raise ValueError(f"evidence.csv:{line}: unknown Oracle {row['oracle']!r}")
            if row["artifact"] and row["artifact"] not in artifacts:
                raise ValueError(f"evidence.csv:{line}: unknown artifact")
            if row["unit_id"] and row["unit_id"] not in units_by_id:
                raise ValueError(f"evidence.csv:{line}: unknown unit_id")
            if row["evidence_class"] not in EVIDENCE_CLASSES:
                raise ValueError(f"evidence.csv:{line}: invalid evidence class")
            if row["result"] not in EVIDENCE_RESULTS:
                raise ValueError(f"evidence.csv:{line}: invalid result")
            for field in ("extent_start", "extent_size"):
                value = integer(
                    row[field], f"evidence.csv:{line} {field}", allow_empty=True
                )
                if value is not None and value < 0:
                    raise ValueError(f"evidence.csv:{line}: negative {field}")
            if bool(row["extent_start"]) != bool(row["extent_size"]):
                raise ValueError(f"evidence.csv:{line}: incomplete extent binding")

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
                if not row["segment"] or not row["offset"] or file_offset is None:
                    raise ValueError(f"units.csv:{line}: exact unit lacks address/extent")
                unit_offset = integer(row["offset"], f"units.csv:{line} offset")
                if unit_offset is None or unit_offset < 0:
                    raise ValueError(f"units.csv:{line}: negative unit offset")
                if file_offset + compare_size > int(artifacts[row["artifact"]]["size"]):
                    raise ValueError(f"units.csv:{line}: exact extent exceeds artifact")
                source = Path(row["source"])
                if (
                    not row["source"]
                    or source.is_absolute()
                    or ".." in source.parts
                    or not (repository_root / source).is_file()
                    or (repository_root / source).is_symlink()
                ):
                    raise ValueError(f"units.csv:{line}: exact unit lacks checked-in source")
                if not row["replay_command"]:
                    raise ValueError(f"units.csv:{line}: exact unit lacks source/replay")
                validate_replay_command(
                    repository_root, row["replay_command"], f"units.csv:{line}"
                )
                passed = accepted_oracle_passes(
                    evidence_ids,
                    evidence,
                    oracle_by_id,
                    non_acceptance_classes,
                    artifact=row["artifact"],
                    unit_id=row["id"],
                    extent_start=file_offset,
                    extent_size=compare_size,
                    global_evidence_oracles=global_evidence_oracles,
                    artifact_evidence_oracles=artifact_evidence_oracles,
                )
                for required in required_oracles:
                    if required not in passed:
                        raise ValueError(
                            f"units.csv:{line}: exact unit lacks passing {required} evidence"
                        )

        reviewed_function_spans: dict[str, list[tuple[int, int, str]]] = {}
        seen_function_addresses: dict[str, set[int]] = {}
        for line, row in enumerate(function_rows, start=2):
            context = f"th04_main_authored_functions.csv:{line}"
            if row["artifact"] not in artifacts:
                raise ValueError(f"{context}: unknown artifact")
            if row["boundary_state"] not in BOUNDARY_STATES:
                raise ValueError(f"{context}: invalid boundary state")
            if row["state"] not in FUNCTION_STATES:
                raise ValueError(f"{context}: invalid function state")
            if not row["name"]:
                raise ValueError(f"{context}: missing function name")
            address = integer(row["address"], f"{context} address")
            if address is None or address < 0:
                raise ValueError(f"{context}: invalid function address")
            addresses = seen_function_addresses.setdefault(row["artifact"], set())
            if address in addresses:
                raise ValueError(f"{context}: duplicate function address")
            addresses.add(address)
            file_offset = integer(row["file_offset"], f"{context} file_offset", allow_empty=True)
            size = integer(row["size"], f"{context} size", allow_empty=True)
            if file_offset is not None and file_offset < 0:
                raise ValueError(f"{context}: negative file offset")
            if size is not None and size <= 0:
                raise ValueError(f"{context}: invalid function size")
            for evidence_id in split_ids(row["evidence_ids"]):
                if evidence_id not in evidence:
                    raise ValueError(f"{context}: unknown evidence {evidence_id!r}")
            if row["owner_unit"] and row["owner_unit"] not in units_by_id:
                raise ValueError(f"{context}: unknown owner unit")
            if row["boundary_state"] in {"reviewed", "shared"}:
                if file_offset is None or size is None:
                    raise ValueError(f"{context}: reviewed function lacks complete extent")
                span = (file_offset, file_offset + size, row["id"])
                for start, end, other in reviewed_function_spans.setdefault(row["artifact"], []):
                    if span[0] < end and start < span[1]:
                        raise ValueError(f"{context}: reviewed function overlaps {other!r}")
                reviewed_function_spans[row["artifact"]].append(span)
            if row["state"] == "exact":
                if row["boundary_state"] not in {"reviewed", "shared"}:
                    raise ValueError(f"{context}: exact function boundary not reviewed")
                if not row["owner_unit"]:
                    raise ValueError(f"{context}: exact function lacks exact byte owner")
                owner = units_by_id[row["owner_unit"]]
                if owner["artifact"] != row["artifact"] or owner["origin"] != "authored" or owner["state"] != "exact":
                    raise ValueError(f"{context}: function owner is not exact authored bytes")
                owner_start = integer(owner["file_offset"], f"{context} owner file_offset")
                owner_size = integer(owner["compare_size"], f"{context} owner compare_size")
                assert file_offset is not None and size is not None and owner_start is not None and owner_size is not None
                if not (owner_start <= file_offset and file_offset + size <= owner_start + owner_size):
                    raise ValueError(f"{context}: exact function body escapes exact byte owner")
                if row["source"] != owner["source"]:
                    raise ValueError(f"{context}: exact function source must equal owner source")
                source = Path(row["source"]); source_path = repository_root / source
                if not row["source"] or source.is_absolute() or ".." in source.parts or not source_path.is_file() or source_path.is_symlink():
                    raise ValueError(f"{context}: exact function lacks checked-in source")
                boundary_pass = any(
                    evidence[evidence_id]["oracle"] == "boundary-ownership"
                    and evidence[evidence_id]["artifact"] == row["artifact"]
                    and evidence[evidence_id]["evidence_class"] == "target-analysis"
                    and evidence[evidence_id]["result"] == "pass"
                    for evidence_id in split_ids(row["evidence_ids"])
                )
                if not boundary_pass:
                    raise ValueError(f"{context}: exact function lacks target-analysis boundary evidence")

        print(
            "tracking OK: "
            f"{len(units_by_id)} units, {len(evidence)} evidence rows, "
            f"{len(hypotheses_by_id)} hypotheses, {len(knowledge)} knowledge rows, "
            f"{len(functions_by_id)} authored-function rows, {len(artifacts)} targets"
        )
        return 0
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
