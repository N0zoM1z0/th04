"""Independent validation of private Ghidra MZ attestation exports."""

from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
import re
import struct
from typing import Any

from .pc98 import MZImage, digest_bytes, digest_file, parse_mz


class GhidraError(ValueError):
    """Raised when a Ghidra export or project configuration fails closed."""


SEGMENTED_ADDRESS = re.compile(r"^(?:[A-Za-z0-9_]+:)?([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})$")


def parse_properties(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw or raw.startswith("#"):
            continue
        if "=" not in raw:
            raise GhidraError(f"invalid property at {path}:{line_number}")
        key, value = raw.split("=", 1)
        if not key or key in result:
            raise GhidraError(f"duplicate or empty property at {path}:{line_number}")
        result[key] = value
    return result


def parse_segmented_address(value: str) -> tuple[int, int]:
    match = SEGMENTED_ADDRESS.fullmatch(value)
    if not match:
        raise GhidraError(f"expected a 16-bit segmented address, got {value!r}")
    return int(match.group(1), 16), int(match.group(2), 16)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _coverage(
    rows: list[dict[str, str]], start: int, end: int, *, loaded: bool, address_space: str
) -> tuple[bool, int, int]:
    counts = bytearray(end - start)
    for row in rows:
        for field in ("initialized", "loaded"):
            if row[field] not in ("true", "false"):
                raise GhidraError(f"invalid boolean {row[field]!r} in block {row.get('block')}")
        if row["initialized"] != "true":
            continue
        if (row["loaded"] == "true") != loaded or row["address_space"] != address_space:
            continue
        range_start = int(row["file_offset"])
        range_end = range_start + int(row["length"])
        for offset in range(max(start, range_start), min(end, range_end)):
            counts[offset - start] += 1
    gaps = counts.count(0)
    overlaps = sum(value > 1 for value in counts)
    return gaps == 0 and overlaps == 0, gaps, overlaps


def _expected_relocations(image: MZImage, load_segment: int) -> Counter[tuple[object, ...]]:
    expected: Counter[tuple[object, ...]] = Counter()
    for relocation in image.relocations:
        original = image.program_image[relocation.linear : relocation.linear + 2]
        value = struct.unpack("<H", original)[0]
        relocated = (value + load_segment) & 0xFFFF
        expected[
            (
                (load_segment + relocation.segment) & 0xFFFF,
                relocation.offset,
                "APPLIED",
                0,
                (relocation.segment, relocation.offset, relocated),
                original.hex(),
                struct.pack("<H", relocated).hex(),
            )
        ] += 1
    return expected


def _actual_relocations(rows: list[dict[str, str]]) -> Counter[tuple[object, ...]]:
    actual: Counter[tuple[object, ...]] = Counter()
    for row in rows:
        segment, offset = parse_segmented_address(row["address"])
        if segment != int(row["address_segment"]) or offset != int(row["address_offset"]):
            raise GhidraError(f"relocation address columns disagree at row {row.get('index')}")
        value_tuple = tuple(int(value) for value in row["values"].split(";") if value)
        actual[
            (
                segment,
                offset,
                row["status"],
                int(row["type"]),
                value_tuple,
                row["original_bytes"],
                row["memory_bytes"],
            )
        ] += 1
    return actual


def _sample_offsets(image: MZImage) -> list[int]:
    size = len(image.program_image)
    candidates = [0, image.header.entry_linear, size // 4, size // 2, (size * 3) // 4, size - 16]
    if image.relocations:
        candidates.extend(
            [
                image.relocations[0].linear,
                image.relocations[len(image.relocations) // 2].linear,
                image.relocations[-1].linear,
            ]
        )
    return sorted({max(0, min(size - 1, offset)) for offset in candidates})


def attest_mz_export(
    export_dir: Path,
    target: bytes,
    artifact: dict[str, Any],
    analysis_config: dict[str, Any],
    expected_nonce: str | None = None,
) -> dict[str, object]:
    """Compare a Ghidra-exported database view against an independently parsed MZ."""

    image = parse_mz(target)
    if not image.valid:
        raise GhidraError("cannot attest a structurally invalid target")
    files = {
        "properties": export_dir / "program.properties",
        "blocks": export_dir / "blocks.csv",
        "relocations": export_dir / "relocations.csv",
        "entrypoints": export_dir / "entrypoints.txt",
        "filebytes_original": export_dir / "filebytes-original.bin",
        "filebytes_modified": export_dir / "filebytes-modified.bin",
        "header_memory": export_dir / "header-memory.bin",
        "load_memory": export_dir / "load-memory.bin",
    }
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise GhidraError("missing Ghidra export files: " + ", ".join(missing))
    properties = parse_properties(files["properties"])
    blocks = _read_csv(files["blocks"])
    relocations = _read_csv(files["relocations"])
    entries = [
        line.strip()
        for line in files["entrypoints"].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    original = files["filebytes_original"].read_bytes()
    modified = files["filebytes_modified"].read_bytes()
    header_memory = files["header_memory"].read_bytes()
    load_memory = files["load_memory"].read_bytes()
    loader = analysis_config["mz_loader"]
    load_segment = int(loader["load_segment"])
    relocated = image.relocated_program_image(load_segment)
    expected_modified = target[: image.header.header_size] + relocated + image.overlay
    expected_entry = (
        f"{(load_segment + image.header.initial_relative_cs) & 0xFFFF:04x}:"
        f"{image.header.initial_ip:04x}"
    )

    required_properties = {
        "schema_version": "1",
        "program_name": Path(str(artifact["private_path"])).name,
        "executable_sha256": str(artifact["sha256"]),
        "executable_format": str(loader["name"]),
        "language_id": str(loader["language_id"]),
        "compiler_spec_id": str(loader["compiler_spec_id"]),
        "image_base": "0000:0000",
        "filebytes_filename": Path(str(artifact["private_path"])).name,
        "filebytes_size": str(len(target)),
        "filebytes_original_sha256": digest_bytes(target),
        "filebytes_modified_sha256": digest_bytes(expected_modified),
        "header_memory_sha256": digest_bytes(target[: image.header.header_size]),
        "load_memory_sha256": digest_bytes(relocated),
        "header_size": str(image.header.header_size),
        "declared_size": str(image.header.declared_file_size),
        "load_module_size": str(len(image.program_image)),
        "relocation_count": str(len(image.relocations)),
        "external_entry_point_count": "1",
        "headless_analysis_timed_out": "false",
    }
    if expected_nonce is not None:
        required_properties["export_nonce"] = expected_nonce
    property_mismatches = {
        key: {"expected": expected, "actual": properties.get(key)}
        for key, expected in required_properties.items()
        if properties.get(key) != expected
    }

    header_coverage, header_gaps, header_overlaps = _coverage(
        blocks,
        0,
        image.header.header_size,
        loaded=False,
        address_space=str(loader["header_address_space"]),
    )
    program_coverage, program_gaps, program_overlaps = _coverage(
        blocks,
        image.header.header_size,
        image.header.declared_file_size,
        loaded=True,
        address_space=properties.get("default_address_space", ""),
    )
    address_mapping_errors: list[dict[str, object]] = []
    for row in blocks:
        if row["initialized"] != "true" or row["loaded"] != "true":
            continue
        start = int(row["file_offset"])
        end = start + int(row["length"])
        if end <= image.header.header_size or start >= image.header.declared_file_size:
            continue
        segment, offset = parse_segmented_address(row["min_address"])
        mapped_file_offset = (
            (((segment - load_segment) & 0xFFFF) << 4) + offset + image.header.header_size
        )
        if mapped_file_offset != start:
            address_mapping_errors.append(
                {
                    "block": row["block"],
                    "address": row["min_address"],
                    "reported_file_offset": start,
                    "derived_file_offset": mapped_file_offset,
                }
            )

    expected_relocations = _expected_relocations(image, load_segment)
    actual_relocations = _actual_relocations(relocations)
    checks = {
        "program_properties": not property_mismatches,
        "filebytes_original": original == target,
        "filebytes_modified": modified == expected_modified,
        "header_memory": header_memory == target[: image.header.header_size],
        "load_memory": load_memory == relocated,
        "header_mapping_coverage": header_coverage,
        "load_mapping_coverage": program_coverage,
        "load_mapping_addresses": not address_mapping_errors,
        "relocation_table": actual_relocations == expected_relocations,
        "external_entry_point": entries == [expected_entry],
        "source_range_count": properties.get("source_range_count") == str(len(blocks)),
    }
    samples = []
    for offset in _sample_offsets(image):
        length = min(16, len(relocated) - offset)
        samples.append(
            {
                "load_module_offset": f"0x{offset:X}",
                "preferred_address": (
                    f"{(load_segment + offset // 16) & 0xFFFF:04X}:{offset % 16:04X}"
                ),
                "length": length,
                "expected_hex": relocated[offset : offset + length].hex(),
                "database_hex": load_memory[offset : offset + length].hex(),
                "pass": relocated[offset : offset + length]
                == load_memory[offset : offset + length],
            }
        )
    ready = all(checks.values()) and all(bool(sample["pass"]) for sample in samples)
    return {
        "ready": ready,
        "artifact_id": artifact["id"],
        "target": {
            "size": len(target),
            "sha256": digest_bytes(target),
            "header_size": image.header.header_size,
            "header_sha256": digest_bytes(target[: image.header.header_size]),
            "load_module_size": len(image.program_image),
            "load_module_sha256": digest_bytes(image.program_image),
            "relocated_load_segment": f"0x{load_segment:04X}",
            "relocated_load_module_sha256": digest_bytes(relocated),
            "entry_cs_ip": (
                f"{image.header.initial_relative_cs:04X}:{image.header.initial_ip:04X}"
            ),
            "database_entry_cs_ip": expected_entry.upper(),
            "relocation_count": len(image.relocations),
        },
        "database": {
            "program_name": properties.get("program_name"),
            "format": properties.get("executable_format"),
            "language_id": properties.get("language_id"),
            "compiler_spec_id": properties.get("compiler_spec_id"),
            "image_base": properties.get("image_base"),
            "function_count": int(properties.get("function_count", "-1")),
            "instruction_count": int(properties.get("instruction_count", "-1")),
            "defined_data_count": int(properties.get("defined_data_count", "-1")),
            "source_range_count": len(blocks),
            "relocation_count": len(relocations),
            "external_entry_points": entries,
        },
        "checks": checks,
        "diagnostics": {
            "property_mismatches": property_mismatches,
            "header_mapping_gaps": header_gaps,
            "header_mapping_overlaps": header_overlaps,
            "load_mapping_gaps": program_gaps,
            "load_mapping_overlaps": program_overlaps,
            "load_mapping_address_errors": address_mapping_errors,
            "relocations_missing": sum((expected_relocations - actual_relocations).values()),
            "relocations_unexpected": sum((actual_relocations - expected_relocations).values()),
        },
        "samples": samples,
        "export_files": {
            name: {"size": path.stat().st_size, "sha256": digest_file(path)}
            for name, path in files.items()
        },
    }
