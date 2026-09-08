#!/usr/bin/env python3
"""Compare unpacked TH04 targets with a cold candidate and prepare Ghidra views.

The generated MZ files are explicitly hybrid *analysis views*: their load module is
target-observed output from scripts/boundary_review/unpack_diet.py, while their header and relocation
table come from the named cold candidate after topology checks.  They are private,
diagnostic inputs and must never be presented as original executable reconstructions.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib.pc98 import MZImage, parse_mz


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "th04_boundary_review.toml"


class BoundaryPreparationError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to((ROOT / ".analysis").resolve())
    except ValueError as error:
        raise BoundaryPreparationError("analysis views must stay below ignored .analysis") from error
    return resolved


def policies() -> dict[str, dict[str, object]]:
    parsed = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    if parsed.get("schema_version") != 1:
        raise BoundaryPreparationError("unsupported boundary-review schema")
    result = {str(row["artifact"]): row for row in parsed.get("diet_artifacts", [])}
    if len(result) != len(parsed.get("diet_artifacts", [])):
        raise BoundaryPreparationError("duplicate DIET artifact policy")
    return result


def observed_relocations(path: Path) -> list[tuple[int, int, int]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
    expected = {
        "index", "relative_segment", "offset", "relative_linear",
        "observed_es_first_run",
    }
    if set(reader.fieldnames or ()) != expected:
        raise BoundaryPreparationError(f"unexpected relocation CSV schema: {path}")
    result: list[tuple[int, int, int]] = []
    for index, row in enumerate(rows):
        if int(row["index"], 0) != index:
            raise BoundaryPreparationError("observed relocation indices are not contiguous")
        segment = int(row["relative_segment"], 0)
        offset = int(row["offset"], 0)
        linear = int(row["relative_linear"], 0)
        if segment * 16 + offset != linear:
            raise BoundaryPreparationError("observed relocation tuple is internally inconsistent")
        result.append((segment, offset, linear))
    return result


def difference_runs(left: bytes, right: bytes) -> list[dict[str, object]]:
    if len(left) != len(right):
        raise BoundaryPreparationError("difference runs require equal-sized images")
    indices = [index for index, values in enumerate(zip(left, right)) if values[0] != values[1]]
    if not indices:
        return []
    runs: list[tuple[int, int]] = []
    start = previous = indices[0]
    for index in indices[1:]:
        if index != previous + 1:
            runs.append((start, previous + 1))
            start = index
        previous = index
    runs.append((start, previous + 1))
    return [
        {
            "payload_offset": f"0x{start:x}",
            "size": end - start,
            "target_hex": left[start:end].hex(),
            "candidate_hex": right[start:end].hex(),
        }
        for start, end in runs
    ]


def mz_checks(
    candidate: MZImage,
    policy: dict[str, object],
    observed: list[tuple[int, int, int]],
) -> dict[str, bool]:
    candidate_relocations = [
        (item.segment, item.offset, item.linear) for item in candidate.relocations
    ]
    return {
        "candidate_mz_structure": candidate.valid,
        "payload_size": len(candidate.program_image) == int(policy["payload_size"]),
        "header_paragraphs": candidate.header.header_paragraphs == int(policy["header_paragraphs"]),
        "entry": (
            candidate.header.initial_relative_cs == int(policy["entry_cs"])
            and candidate.header.initial_ip == int(policy["entry_ip"])
        ),
        "stack": (
            candidate.header.initial_relative_ss == int(policy["initial_ss"])
            and candidate.header.initial_sp == int(policy["initial_sp"])
        ),
        "relocation_count": len(candidate.relocations) == int(policy["relocation_count"]),
        # MZ relocation table order has no loader semantic meaning.  DIET's encoded
        # stream demonstrably reorders entries, so compare the complete multiset.
        "relocation_multiset": Counter(candidate_relocations) == Counter(observed),
    }


def prepare_one(
    artifact_id: str,
    policy: dict[str, object],
    candidate_path: Path,
    observation_dir: Path,
) -> dict[str, object]:
    receipt_path = observation_dir / "receipt.json"
    payload_path = observation_dir / "payload.bin"
    relocation_path = observation_dir / "relocations.csv"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    payload = payload_path.read_bytes()
    if receipt.get("artifact") != artifact_id:
        raise BoundaryPreparationError(f"observation receipt artifact mismatch for {artifact_id}")
    if digest(payload) != receipt.get("payload_sha256"):
        raise BoundaryPreparationError(f"observation payload digest mismatch for {artifact_id}")
    if len(payload) != int(policy["payload_size"]):
        raise BoundaryPreparationError(f"observation payload size mismatch for {artifact_id}")
    candidate_raw = candidate_path.read_bytes()
    original_format = str(policy["original_format"])

    if original_format == "mz":
        observed = observed_relocations(relocation_path)
        candidate = parse_mz(candidate_raw)
        checks = mz_checks(candidate, policy, observed)
        if not all(checks.values()):
            failed = ", ".join(key for key, value in checks.items() if not value)
            raise BoundaryPreparationError(f"{artifact_id} candidate topology failed: {failed}")
        candidate_payload = candidate.program_image
        analysis_name = "analysis.exe"
        analysis_image = (
            candidate_raw[:candidate.header.header_size]
            + payload
            + candidate.overlay
        )
    elif original_format == "com":
        if relocation_path.is_file():
            observed = observed_relocations(relocation_path)
            if observed:
                raise BoundaryPreparationError("COM observation unexpectedly has relocations")
        checks = {
            "candidate_payload_size": len(candidate_raw) == len(payload),
            "target_candidate_exact": candidate_raw == payload,
        }
        if not all(checks.values()):
            failed = ", ".join(key for key, value in checks.items() if not value)
            raise BoundaryPreparationError(f"{artifact_id} candidate topology failed: {failed}")
        candidate_payload = candidate_raw
        analysis_name = "analysis.com"
        analysis_image = payload
    else:
        raise BoundaryPreparationError(f"unsupported original format {original_format!r}")

    runs = difference_runs(payload, candidate_payload)
    analysis_path = observation_dir / analysis_name
    analysis_path.write_bytes(analysis_image)
    report = {
        "schema_version": 1,
        "artifact": artifact_id,
        "classification": "private diagnostic analysis view",
        "warning": (
            "For MZ, only the load module is target-observed; the header and relocation "
            "table are candidate-derived after topology checks. This is not an exact "
            "unpacked-original claim."
        ),
        "observation_receipt": str(receipt_path.relative_to(ROOT)),
        "packed_target_sha256": receipt["packed_target_sha256"],
        "target_payload_sha256": digest(payload),
        "candidate_path": str(candidate_path.resolve()),
        "candidate_sha256": digest(candidate_raw),
        "candidate_payload_sha256": digest(candidate_payload),
        "analysis_image": str(analysis_path.relative_to(ROOT)),
        "analysis_image_sha256": digest(analysis_image),
        "checks": checks,
        "differing_byte_count": sum(a != b for a, b in zip(payload, candidate_payload)),
        "difference_runs": runs,
    }
    (observation_dir / "candidate-comparison.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate-bin-dir", type=Path, required=True,
        help="directory containing cold candidate op.exe, maine.exe, and zun.com",
    )
    parser.add_argument(
        "--observation-root", type=Path,
        default=ROOT / ".analysis" / "reconstruction" / "boundary-review",
    )
    parser.add_argument(
        "artifact_ids", nargs="*", default=["th04-op", "th04-maine", "th04-zun"],
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        policy_by_artifact = policies()
        observation_root = private_output(args.observation_root)
        filenames = {"th04-op": "op.exe", "th04-maine": "maine.exe", "th04-zun": "zun.com"}
        for artifact_id in args.artifact_ids:
            if artifact_id not in filenames or artifact_id not in policy_by_artifact:
                raise BoundaryPreparationError(f"unsupported artifact {artifact_id!r}")
            report = prepare_one(
                artifact_id,
                policy_by_artifact[artifact_id],
                args.candidate_bin_dir / filenames[artifact_id],
                observation_root / artifact_id,
            )
            print(
                f"{artifact_id}: {report['differing_byte_count']} payload byte differences; "
                f"wrote {report['analysis_image']}"
            )
        return 0
    except (
        BoundaryPreparationError, KeyError, OSError, json.JSONDecodeError,
        tomllib.TOMLDecodeError,
    ) as error:
        print(f"error: boundary preparation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
