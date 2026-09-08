#!/usr/bin/env python3
"""Build the all-artifact TH04 function-boundary review ledger.

The inputs are private, attested Ghidra inventories plus MAP files from a named
cold ReC98 candidate.  MAP ownership is corroboration, not target evidence.
The output keeps origin, boundary confidence, and accepted reconstruction state
separate so Ghidra guesses cannot silently become exact function claims.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "th04_boundary_review.toml"
DEFAULT_OUTPUT = ROOT / "config" / "th04_function_boundaries.csv"
EXISTING_MAIN = ROOT / "config" / "th04_main_authored_functions.csv"

HEADER = [
    "id", "artifact", "segment_identity", "segment_offset", "analysis_linear",
    "payload_offset", "body_size",
    "body_span", "boundary_state", "origin", "work_queue", "accepted_state",
    "name", "map_public", "map_module", "map_segment", "source_form",
    "source_ref", "observation", "tasm_proc", "tasm_distance", "tasm_listing_line",
    "ghidra_contiguous", "ghidra_range_count",
    "caller_count", "callee_count", "evidence_basis", "notes",
]

DETAIL_RE = re.compile(
    r"^\s*([0-9A-F]+):([0-9A-F]+)\s+([0-9A-F]+)\s+"
    r"C=(\S+)\s+S=(\S+)\s+G=(.*?)\s+M=(.*?)\s+ACBP=",
    re.IGNORECASE,
)
PUBLIC_RE = re.compile(
    r"^\s*([0-9A-F]+):([0-9A-F]+)\s+(?:idle\s+)?(.+?)\s*$",
    re.IGNORECASE,
)


class BoundaryLedgerError(ValueError):
    pass


@dataclass(frozen=True)
class Contribution:
    artifact: str
    start: int
    end: int
    module: str
    segment: str
    origin: str
    source_form: str
    source_ref: str
    evidence_basis: str

    def contains(self, offset: int) -> bool:
        return self.start <= offset < self.end


@dataclass(frozen=True)
class Region:
    artifact: str
    name: str
    start: int
    end: int
    kind: str
    origin: str
    entries: tuple[int, ...]

    def contains(self, offset: int) -> bool:
        return self.start <= offset < self.end


def linear(segment: str, offset: str) -> int:
    return int(segment, 16) * 16 + int(offset, 16)


def normalize_module(value: str) -> str:
    return value.strip().replace("\\", "/")


def parse_map(path: Path) -> tuple[list[dict[str, object]], dict[int, list[str]]]:
    """Return non-empty CODE contributions and value-sorted public symbols."""
    contributions: list[dict[str, object]] = []
    publics: dict[int, list[str]] = defaultdict(list)
    in_value_publics = False
    for line in path.read_text(encoding="cp932", errors="replace").splitlines():
        match = DETAIL_RE.match(line)
        if match:
            address = linear(match.group(1), match.group(2))
            size = int(match.group(3), 16)
            if match.group(4).upper() == "CODE" and size:
                contributions.append(
                    {
                        "start": address,
                        "end": address + size,
                        "segment": match.group(5).strip(),
                        "group": match.group(6).strip(),
                        "module": normalize_module(match.group(7)),
                    }
                )
            continue
        if "Publics by Value" in line:
            in_value_publics = True
            continue
        if in_value_publics and (
            line.lstrip().startswith("Program entry point")
            or line.lstrip().startswith("Bound resource files")
        ):
            in_value_publics = False
            continue
        if in_value_publics:
            match = PUBLIC_RE.match(line)
            if match:
                address = linear(match.group(1), match.group(2))
                name = match.group(3).strip()
                if name not in publics[address]:
                    publics[address].append(name)
    if not contributions:
        raise BoundaryLedgerError(f"no CODE contributions parsed from {path}")
    return contributions, dict(publics)


def overrides(config: dict[str, object]) -> list[dict[str, object]]:
    return [dict(row) for row in config.get("module_overrides", [])]


def parse_function_overrides(
    config: dict[str, object],
) -> dict[tuple[str, int], dict[str, object]]:
    result: dict[tuple[str, int], dict[str, object]] = {}
    for raw in config.get("function_overrides", []):
        rule = dict(raw)
        key = (str(rule["artifact"]), int(rule["payload_offset"]))
        if key in result:
            raise BoundaryLedgerError(
                f"duplicate function override for {key[0]} at {key[1]:#x}"
            )
        for field in ("origin", "source_form", "source_ref"):
            if not str(rule.get(field, "")).strip():
                raise BoundaryLedgerError(
                    f"function override for {key[0]} at {key[1]:#x} lacks {field}"
                )
        result[key] = rule
    return result


def classify_module(
    artifact: str,
    module: str,
    segment: str,
    rules: list[dict[str, object]],
) -> tuple[str, str, str]:
    normalized = normalize_module(module)
    for rule in rules:
        if rule.get("artifact") != artifact or normalize_module(str(rule["module"])).lower() != normalized.lower():
            continue
        if "segment" in rule and str(rule["segment"]).lower() != segment.lower():
            continue
        return str(rule["origin"]), str(rule["source_form"]), f"candidate:{normalized}"

    lower = normalized.lower()
    suffix = Path(lower).suffix
    if lower == "c0.asm":
        return "compiler", "compiler-startup", "toolchain:c0.asm"
    if re.match(r"^th\d\d/", lower) and suffix in {".c", ".cpp"}:
        form = "candidate-cpp" if suffix == ".cpp" else "candidate-c"
        if not lower.startswith("th04/"):
            form = "cross-game-" + form
        return "authored", form, f"candidate:{normalized}"
    if re.match(r"^th\d\d/", lower) and suffix == ".asm":
        return "original-asm", "candidate-asm", f"candidate:{normalized}"
    if lower.startswith("th04_") and suffix == ".asm":
        return "authored", "target-derived-asm", f"candidate:{normalized}"
    return "library", "linked-library", f"toolchain-or-library:{normalized}"


def transform_range(start: int, end: int, bias: int, artifact_start: int) -> tuple[int, int] | None:
    clipped_start = max(start, bias)
    if end <= clipped_start:
        return None
    return artifact_start + clipped_start - bias, artifact_start + end - bias


def map_contributions(
    artifact: str,
    path: Path,
    rules: list[dict[str, object]],
    evidence_basis: str,
    *,
    bias: int = 0,
    artifact_start: int = 0,
) -> tuple[list[Contribution], dict[int, list[str]]]:
    raw, raw_publics = parse_map(path)
    result: list[Contribution] = []
    for item in raw:
        transformed = transform_range(int(item["start"]), int(item["end"]), bias, artifact_start)
        if transformed is None:
            continue
        start, end = transformed
        origin, source_form, source_ref = classify_module(
            artifact, str(item["module"]), str(item["segment"]), rules
        )
        result.append(
            Contribution(
                artifact, start, end, str(item["module"]), str(item["segment"]),
                origin, source_form, source_ref, evidence_basis,
            )
        )
    publics: dict[int, list[str]] = defaultdict(list)
    for address, names in raw_publics.items():
        transformed = transform_range(address, address + 1, bias, artifact_start)
        if transformed is not None and any(item.contains(transformed[0]) for item in result):
            publics[transformed[0]].extend(names)
    return result, dict(publics)


def read_inventory(path: Path, runtime_base: int) -> dict[int, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    entries: dict[int, dict[str, str]] = {}
    for row in rows:
        runtime = int(row["entry_linear"], 0)
        offset = runtime - runtime_base
        if offset in entries:
            raise BoundaryLedgerError(f"duplicate Ghidra entry {runtime:#x} in {path}")
        entries[offset] = row
    return entries


def read_existing_main() -> dict[int, dict[str, str]]:
    with EXISTING_MAIN.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return {int(row["address"], 0) - 0x10000: row for row in rows}


def read_tasm_boundaries(path: Path) -> dict[str, dict[int, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    result: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        artifact = row["artifact"]
        offset = int(row["payload_offset"], 0)
        if offset in result[artifact]:
            raise BoundaryLedgerError(
                f"duplicate TASM boundary for {artifact} at {offset:#x}"
            )
        result[artifact][offset] = row
    return dict(result)


def choose_contribution(contributions: list[Contribution], offset: int) -> Contribution | None:
    matches = [item for item in contributions if item.contains(offset)]
    if not matches:
        return None
    return min(matches, key=lambda item: (item.end - item.start, item.start, item.module))


def choose_region(regions: list[Region], offset: int) -> Region | None:
    matches = [item for item in regions if item.contains(offset)]
    return min(matches, key=lambda item: item.end - item.start) if matches else None


def is_ghidra_switch_artifact(row: dict[str, str]) -> bool:
    return row["symbol_source"] == "ANALYSIS" and row["name"].startswith("switchD_")


def preferred_public(names: list[str]) -> str:
    if not names:
        return ""
    non_idle = [name for name in names if not name.startswith("__")]
    return (non_idle or names)[0]


def function_row(
    artifact: str,
    offset: int,
    runtime_base: int,
    ghidra: dict[str, str] | None,
    public_names: list[str],
    contribution: Contribution | None,
    region: Region | None,
    existing: dict[str, str] | None,
    tasm: dict[str, str] | None,
    configured_entry: bool,
    function_override: dict[str, object] | None,
) -> dict[str, str]:
    public = preferred_public(public_names)
    observations = []
    if ghidra:
        observations.append("ghidra")
    if public_names:
        observations.append("map-public")
    if tasm:
        observations.append("tasm-proc")
    observation = "+".join(observations)
    evidence_basis = contribution.evidence_basis if contribution else "target-ghidra"
    origin = contribution.origin if contribution else (
        region.origin if region and region.kind == "code" else "data"
    )
    source_form = contribution.source_form if contribution else (
        "configured-asm" if region and region.kind == "code" else
        "embedded-library" if region and region.origin == "library" else "non-code"
    )
    source_ref = contribution.source_ref if contribution else (
        f"config:com-region:{region.name}" if region else "target:non-code"
    )
    map_module = contribution.module if contribution else (region.name if region else "")
    map_segment = contribution.segment if contribution else ""
    map_public = ";".join(public_names)
    body_size = int(ghidra["body_addresses"]) if ghidra else 0
    body_span = int(ghidra["body_span"]) if ghidra else 0
    name = public or (tasm["name"] if tasm else "") or (
        ghidra["name"] if ghidra else f"sub_{offset:05x}"
    )
    notes: list[str] = []

    if function_override is not None:
        expected_tasm = str(function_override.get("expected_tasm_proc", ""))
        if expected_tasm and (tasm is None or tasm["name"] != expected_tasm):
            observed = tasm["name"] if tasm else "none"
            raise BoundaryLedgerError(
                f"function override for {artifact} at {offset:#x} expected TASM "
                f"PROC {expected_tasm}, observed {observed}"
            )
        if "expected_body_span" in function_override:
            expected_span = int(function_override["expected_body_span"])
            if ghidra is None or body_span != expected_span:
                raise BoundaryLedgerError(
                    f"function override for {artifact} at {offset:#x} expected "
                    f"Ghidra body span {expected_span:#x}, observed {body_span:#x}"
                )
        origin = str(function_override["origin"])
        source_form = str(function_override["source_form"])
        source_ref = str(function_override["source_ref"])
        if function_override.get("notes"):
            notes.append(str(function_override["notes"]))

    false_function = bool(ghidra and is_ghidra_switch_artifact(ghidra))
    if contribution is None and not (region and region.kind == "code"):
        false_function = True
    if (
        ghidra
        and not tasm
        and not public_names
        and contribution is not None
        and contribution.source_form == "target-derived-asm"
        and existing is None
    ):
        false_function = True
        notes.append(
            "Ghidra-only entry is not a PROC in the complete attested TASM listing."
        )
    if false_function:
        boundary_state = "excluded"
        work_queue = "exclude"
        accepted_state = "excluded"
        notes.append("Ghidra entry is a switch/data/non-code artifact, not an accepted function boundary.")
    else:
        body_fits = bool(
            ghidra
            and int(ghidra["body_min_linear"], 0) == runtime_base + offset
            and (
                contribution is not None
                and int(ghidra["body_max_linear"], 0) - runtime_base < contribution.end
                or region is not None
                and int(ghidra["body_max_linear"], 0) - runtime_base < region.end
            )
        )
        if configured_entry and body_fits:
            boundary_state = "reviewed"
        elif (
            (public_names or tasm)
            and ghidra
            and body_fits
            and ghidra["contiguous"] == "true"
        ):
            boundary_state = "corroborated"
        else:
            boundary_state = "provisional"
            if not ghidra:
                notes.append("TLINK public has no corresponding Ghidra function entry.")
            elif not public_names and not tasm and not configured_entry:
                notes.append("Ghidra-only boundary has no TLINK public or TASM PROC at its entry.")
            elif ghidra["contiguous"] != "true":
                notes.append("Ghidra body is noncontiguous and requires control-flow reconciliation.")
            elif not body_fits:
                notes.append("Ghidra body crosses its corroborating ownership region.")
        work_queue = "reconstruct" if origin == "authored" else "attest-asm" if origin == "original-asm" else "exclude"
        accepted_state = "unreviewed" if work_queue != "exclude" else "excluded"

    if existing is not None:
        boundary_state = existing["boundary_state"]
        origin = "authored"
        work_queue = "reconstruct"
        accepted_state = existing["state"]
        name = existing["name"]
        source_ref = existing["source"]
        body_size = int(existing["size"], 0)
        body_span = body_size
        evidence_basis = existing["evidence_ids"]
        notes = [existing["notes"]]

    return {
        "id": f"{artifact}-boundary-{offset:05x}",
        "artifact": artifact,
        "segment_identity": "com-payload" if artifact == "th04-zun" else "mz-load-module",
        "segment_offset": f"0x{offset:X}",
        "analysis_linear": f"0x{runtime_base + offset:X}",
        "payload_offset": f"0x{offset:X}",
        "body_size": f"0x{body_size:X}",
        "body_span": f"0x{body_span:X}",
        "boundary_state": boundary_state,
        "origin": origin,
        "work_queue": work_queue,
        "accepted_state": accepted_state,
        "name": name,
        "map_public": map_public,
        "map_module": map_module,
        "map_segment": map_segment,
        "source_form": source_form,
        "source_ref": source_ref,
        "observation": observation,
        "tasm_proc": tasm["name"] if tasm else "",
        "tasm_distance": tasm["distance"] if tasm else "",
        "tasm_listing_line": tasm["listing_line"] if tasm else "",
        "ghidra_contiguous": ghidra["contiguous"] if ghidra else "",
        "ghidra_range_count": ghidra["body_range_count"] if ghidra else "",
        "caller_count": ghidra["caller_count"] if ghidra else "",
        "callee_count": ghidra["callee_count"] if ghidra else "",
        "evidence_basis": evidence_basis,
        "notes": " ".join(notes),
    }


def build(
    candidate_root: Path,
    inventory_root: Path,
    tasm_functions: Path,
) -> list[dict[str, str]]:
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise BoundaryLedgerError("unsupported boundary-review schema")
    rules = overrides(config)
    function_rules = parse_function_overrides(config)
    all_contributions: dict[str, list[Contribution]] = defaultdict(list)
    all_publics: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    inventories: dict[str, dict[int, dict[str, str]]] = {}
    runtime_bases: dict[str, int] = {}
    evidence_bases: dict[str, str] = {}

    for item in config.get("map_artifacts", []):
        artifact = str(item["artifact"])
        runtime_base = int(item["runtime_base"])
        evidence = str(item["evidence_basis"])
        inventory_rel = Path(str(item["inventory"]))
        inventory_path = (
            inventory_root / artifact / "functions.csv"
            if inventory_root != ROOT else ROOT / inventory_rel
        )
        contributions, publics = map_contributions(
            artifact, candidate_root / str(item["map"]), rules, evidence
        )
        all_contributions[artifact].extend(contributions)
        for address, names in publics.items():
            all_publics[artifact][address].extend(names)
        inventories[artifact] = read_inventory(inventory_path, runtime_base)
        runtime_bases[artifact] = runtime_base
        evidence_bases[artifact] = evidence

    regions: list[Region] = []
    zun_artifact = "th04-zun"
    zun_runtime_base = 0x10000
    zun_inventory = inventory_root / "th04-zun-complete" / "functions.csv" if inventory_root != ROOT else ROOT / ".analysis/ghidra/boundary-exports/th04-zun-complete/functions.csv"
    inventories[zun_artifact] = read_inventory(zun_inventory, zun_runtime_base)
    runtime_bases[zun_artifact] = zun_runtime_base
    evidence_bases[zun_artifact] = "target-exact-composite+candidate-map"
    for item in config.get("com_regions", []):
        if item.get("artifact") != zun_artifact:
            continue
        start = int(item["start"])
        region = Region(
            zun_artifact, str(item["name"]), start, start + int(item["size"]),
            str(item["kind"]), str(item["origin"]),
            tuple(start + int(value) for value in item.get("entry_offsets", [])),
        )
        regions.append(region)
        if item.get("origin") == "map":
            contributions, publics = map_contributions(
                zun_artifact,
                candidate_root / str(item["map"]),
                rules,
                evidence_bases[zun_artifact],
                bias=int(item.get("map_address_bias", 0)),
                artifact_start=start,
            )
            all_contributions[zun_artifact].extend(contributions)
            for address, names in publics.items():
                all_publics[zun_artifact][address].extend(names)
        elif region.kind in {"code", "embedded-com"}:
            source_form = "embedded-library" if region.origin == "library" else "configured-asm"
            all_contributions[zun_artifact].append(
                Contribution(
                    zun_artifact, region.start, region.end, region.name, "",
                    region.origin, source_form, f"config:com-region:{region.name}",
                    evidence_bases[zun_artifact],
                )
            )
            for entry in region.entries:
                all_publics[zun_artifact][entry].append(region.name)

    existing_main = read_existing_main()
    tasm_boundaries = read_tasm_boundaries(tasm_functions)
    output: list[dict[str, str]] = []
    for artifact in ("th04-op", "th04-main", "th04-maine", "th04-zun"):
        ghidra_entries = inventories[artifact]
        public_entries = all_publics[artifact]
        existing_offsets = set(existing_main) if artifact == "th04-main" else set()
        offsets = sorted(
            set(ghidra_entries)
            | set(public_entries)
            | set(tasm_boundaries.get(artifact, {}))
            | existing_offsets
        )
        missing_overrides = sorted(
            offset
            for (rule_artifact, offset) in function_rules
            if rule_artifact == artifact and offset not in offsets
        )
        if missing_overrides:
            rendered = ", ".join(f"{offset:#x}" for offset in missing_overrides)
            raise BoundaryLedgerError(
                f"function overrides for {artifact} lack boundary observations: {rendered}"
            )
        artifact_regions = [item for item in regions if item.artifact == artifact]
        configured_entries = {entry for item in artifact_regions for entry in item.entries}
        for offset in offsets:
            if offset < 0:
                raise BoundaryLedgerError(f"negative payload offset for {artifact}: {offset:#x}")
            output.append(
                function_row(
                    artifact,
                    offset,
                    runtime_bases[artifact],
                    ghidra_entries.get(offset),
                    public_entries.get(offset, []),
                    choose_contribution(all_contributions[artifact], offset),
                    choose_region(artifact_regions, offset),
                    existing_main.get(offset) if artifact == "th04-main" else None,
                    tasm_boundaries.get(artifact, {}).get(offset),
                    offset in configured_entries,
                    function_rules.get((artifact, offset)),
                )
            )
    return output


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate-source-root", type=Path, required=True,
        help="cold ReC98 candidate root containing obj/th04/*.map",
    )
    parser.add_argument(
        "--inventory-root", type=Path,
        default=ROOT / ".analysis" / "ghidra" / "boundary-exports",
        help="private root containing artifact/functions.csv exports",
    )
    parser.add_argument(
        "--tasm-functions", type=Path,
        default=ROOT / ".analysis" / "reconstruction" / "boundary-review" / "tasm" / "functions.csv",
        help="private CSV emitted by export_tasm_function_boundaries.py",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        rows = build(
            args.candidate_source_root.resolve(),
            args.inventory_root.resolve(),
            args.tasm_functions.resolve(),
        )
        write_rows(args.output.resolve(), rows)
        counts: dict[tuple[str, str], int] = defaultdict(int)
        for row in rows:
            counts[(row["artifact"], row["work_queue"])] += 1
        print(f"wrote {len(rows)} boundary observations to {args.output}")
        for key in sorted(counts):
            print(f"{key[0]} {key[1]}={counts[key]}")
        return 0
    except (BoundaryLedgerError, KeyError, OSError, ValueError) as error:
        print(f"error: boundary ledger build failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
