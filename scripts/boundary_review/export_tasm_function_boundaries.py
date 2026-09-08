#!/usr/bin/env python3
"""Export local PROC boundaries from attested TASM listings.

This closes a known Ghidra/MAP blind spot: TLINK MAP files omit non-public
assembly procedures, while Ghidra may miss or split them.  The result remains
compiler-observed candidate evidence because the input assembly is
target-derived ReC98 material.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from boundary_review.build_function_boundary_ledger import (
    BoundaryLedgerError,
    classify_module,
    map_contributions,
    overrides,
)
from lib.omf import describe_omf


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "th04_boundary_review.toml"
TOOLCHAIN = ROOT / "config" / "toolchain.toml"
DEFAULT_OUTPUT_DIR = ROOT / ".analysis" / "reconstruction" / "boundary-review" / "tasm"
CSV_HEADER = [
    "artifact", "payload_offset", "name", "distance", "segment",
    "listing_offset", "module", "source", "listing_line", "source_sha256",
    "listing_sha256",
]
SEGMENT_RE = re.compile(r"\b([A-Za-z_?$@][\w?$@]*)\s+segment\b", re.IGNORECASE)
ENDS_RE = re.compile(r"\b([A-Za-z_?$@][\w?$@]*)\s+ends\b", re.IGNORECASE)


class TasmBoundaryError(ValueError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to((ROOT / ".analysis").resolve())
    except ValueError as error:
        raise TasmBoundaryError("TASM boundary output must stay below ignored .analysis") from error
    return resolved


def windows_path(path: Path, environment: dict[str, str]) -> str:
    completed = subprocess.run(
        ["winepath", "-w", str(path)], env=environment, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return completed.stdout.strip()


def listing_procedures(path: Path, default_segment: str) -> list[dict[str, object]]:
    current_segment = default_segment
    rows: list[dict[str, object]] = []
    for line_number, raw_line in enumerate(
        path.read_text(encoding="cp932", errors="replace").splitlines(), 1
    ):
        line = raw_line.replace("\f", "")
        segment_match = SEGMENT_RE.search(line)
        if segment_match and ";" not in line[:segment_match.start()]:
            current_segment = segment_match.group(1)
        tokens = line.split()
        for index, token in enumerate(tokens):
            if token.lower() != "proc" or index < 1 or index + 1 >= len(tokens):
                continue
            if ";" in " ".join(tokens[:index]):
                continue
            if tokens[index + 1].lower() not in {"near", "far"}:
                continue
            fields = line.split("\t")
            address_match = (
                re.match(r"^\s*([0-9A-Fa-f]{4})(?:\s|$)", fields[1])
                if len(fields) > 1 else None
            )
            # The second listing column is empty for false conditional and
            # non-emitting macro definitions.  Their source line number can
            # otherwise look exactly like a four-digit hexadecimal offset.
            if address_match is None:
                continue
            address_text = address_match.group(1)
            rows.append(
                {
                    "name": tokens[index - 1],
                    "distance": tokens[index + 1].lower(),
                    "segment": current_segment,
                    "listing_offset": int(address_text, 16),
                    "listing_line": line_number,
                }
            )
            break
        ends_match = ENDS_RE.search(line)
        if (
            ends_match
            and ";" not in line[:ends_match.start()]
            and ends_match.group(1).lower() == current_segment.lower()
        ):
            current_segment = default_segment
    if not rows:
        raise TasmBoundaryError(f"no PROC boundaries parsed from {path}")
    return rows


def assemble(
    candidate_root: Path,
    source: Path,
    object_path: Path,
    listing_path: Path,
    environment: dict[str, str],
) -> str:
    for output in (object_path, listing_path):
        if output.exists():
            if not output.is_file() or output.is_symlink():
                raise TasmBoundaryError(f"refusing to replace non-file output: {output}")
            output.unlink()
    command = [
        "wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx", "/kh32768",
        "/t", "/dGAME=4", "/la", str(source),
        windows_path(object_path, environment), windows_path(listing_path, environment),
    ]
    completed = subprocess.run(
        command, cwd=candidate_root, env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, errors="replace", timeout=300,
    )
    if completed.returncode != 0 or not object_path.is_file() or not listing_path.is_file():
        raise TasmBoundaryError(
            f"TASM failed for {source} ({completed.returncode}): {completed.stdout.strip()}"
        )
    omf = describe_omf(object_path.read_bytes())
    if not omf.get("valid") or "Turbo Assembler  Version 5.0" not in omf.get("translator_comments", []):
        raise TasmBoundaryError(f"unexpected TASM OMF producer for {source}")
    return " ".join(command)


def contribution_for(
    contributions: list[object], module: str, segment: str
):
    matches = [
        item for item in contributions
        if item.module.lower() == module.lower() and item.segment.lower() == segment.lower()
    ]
    if not matches:
        raise TasmBoundaryError(f"no MAP contribution for {module}:{segment}")
    if len(matches) != 1:
        raise TasmBoundaryError(f"ambiguous MAP contribution for {module}:{segment}")
    return matches[0]


def export(candidate_root: Path, output_dir: Path) -> list[dict[str, str]]:
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    toolchain = tomllib.loads(TOOLCHAIN.read_text(encoding="utf-8"))
    rules = overrides(config)
    prefix = ROOT / str(toolchain["paths"]["wine_prefix"])
    environment = os.environ.copy()
    environment.update(
        {"WINEPREFIX": str(prefix), "WINEDEBUG": "-all", "MSDOS_PATH": r"C:\TC4\BIN"}
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    attestation = output_dir / "toolchain-attestation.json"
    subprocess.run(
        [
            sys.executable, "scripts/attest_toolchain.py", "--identity-only",
            "--surface", "active-tasm32", "--output", str(attestation),
        ], cwd=ROOT, check=True,
    )

    output_rows: list[dict[str, str]] = []
    commands: list[str] = []
    listings: list[dict[str, object]] = []
    for item in config.get("assembly_boundary_sources", []):
        artifact = str(item["artifact"])
        source_rel = Path(str(item["source"]))
        source = candidate_root / source_rel
        if not source.is_file():
            raise TasmBoundaryError(f"missing assembly candidate: {source}")
        stem = f"{artifact}-{source.stem}".replace("th04-", "")
        object_path = output_dir / f"{stem}.obj"
        listing_path = output_dir / f"{stem}.lst"
        commands.append(assemble(candidate_root, source_rel, object_path, listing_path, environment))
        contributions, _ = map_contributions(
            artifact,
            candidate_root / str(item["map"]),
            rules,
            "candidate-map+tasm-listing",
            bias=int(item.get("map_address_bias", 0)),
            artifact_start=int(item.get("artifact_start", 0)),
        )
        listing_bias = int(item.get("listing_address_bias", 0))
        source_sha = digest(source)
        listing_sha = digest(listing_path)
        procedures = listing_procedures(listing_path, str(item["default_segment"]))
        for procedure in procedures:
            contribution = contribution_for(
                contributions, str(item["module"]), str(procedure["segment"])
            )
            local = int(procedure["listing_offset"]) - listing_bias
            if local < 0:
                raise TasmBoundaryError(f"listing offset precedes bias for {source_rel}")
            payload_offset = contribution.start + local
            if not contribution.contains(payload_offset):
                raise TasmBoundaryError(
                    f"PROC {procedure['name']} falls outside {contribution.module}:"
                    f"{contribution.segment}"
                )
            output_rows.append(
                {
                    "artifact": artifact,
                    "payload_offset": f"0x{payload_offset:X}",
                    "name": str(procedure["name"]),
                    "distance": str(procedure["distance"]),
                    "segment": str(procedure["segment"]),
                    "listing_offset": f"0x{int(procedure['listing_offset']):X}",
                    "module": str(item["module"]),
                    "source": str(source_rel).replace("\\", "/"),
                    "listing_line": str(procedure["listing_line"]),
                    "source_sha256": source_sha,
                    "listing_sha256": listing_sha,
                }
            )
        listings.append(
            {
                "artifact": artifact,
                "source": str(source_rel),
                "source_sha256": source_sha,
                "object_sha256": digest(object_path),
                "listing_sha256": listing_sha,
                "procedure_count": len(procedures),
            }
        )

    output_rows.sort(key=lambda row: (row["artifact"], int(row["payload_offset"], 0), row["name"]))
    seen: set[tuple[str, int, str]] = set()
    for row in output_rows:
        key = (row["artifact"], int(row["payload_offset"], 0), row["name"].lower())
        if key in seen:
            raise TasmBoundaryError(f"duplicate TASM boundary: {key}")
        seen.add(key)
    csv_path = output_dir / "functions.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    receipt = {
        "schema_version": 1,
        "classification": "compiler-observed boundaries from target-derived candidate assembly",
        "candidate_root": str(candidate_root),
        "tasm_sha256": digest(prefix / "drive_c" / "TASM50" / "bin" / "TASM32.EXE"),
        "function_csv_sha256": digest(csv_path),
        "function_count": len(output_rows),
        "listings": listings,
        "commands": commands,
    }
    (output_dir / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return output_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output_dir = private_output(args.output_dir)
        rows = export(args.candidate_source_root.resolve(), output_dir)
        print(f"exported {len(rows)} TASM PROC boundaries to {output_dir / 'functions.csv'}")
        return 0
    except (
        BoundaryLedgerError, KeyError, OSError, subprocess.CalledProcessError,
        subprocess.TimeoutExpired, TasmBoundaryError, ValueError,
    ) as error:
        print(f"error: TASM boundary export failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
