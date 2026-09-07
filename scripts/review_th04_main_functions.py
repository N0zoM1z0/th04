#!/usr/bin/env python3
"""Conservatively review TH04 MAIN authored functions against exact byte owners.

The private target/Ghidra/TLINK files are observations. Automatic acceptance requires
three independently replayed views to agree on the start and Ghidra's entire
*contiguous* body to be contained in one exact authored byte owner. Explicit manual
reviews may override a non-contiguous Ghidra body only when the configured span agrees
with Ghidra's min/max, a local TLINK public and exact owner, and an independent raw
16-bit ndisasm pass tiles the complete target span through a terminal RET/RETF. A
separate no-Ghidra path requires exact ownership, a TLINK public, raw terminal decode,
and an exact next-public or owner-end boundary without synthesizing Ghidra metadata.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "th04_main_function_review.toml"
UNITS = ROOT / "config" / "units.csv"


def parse_functions(path: Path) -> dict[int, str]:
    result: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split(None, 1)
        if len(fields) != 2:
            continue
        try:
            address = int(fields[0], 16)
        except ValueError:
            continue
        result[address] = fields[1]
    return result


def parse_publics(path: Path) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    pattern = re.compile(r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?(.+?)\s*$", re.I)
    for line in path.read_text(encoding="cp437", errors="replace").splitlines():
        match = pattern.match(line)
        if not match or "C=CODE" in line or "ACBP=" in line:
            continue
        address = int(match.group(1), 16) * 16 + int(match.group(2), 16) + 0x10000
        result.setdefault(address, []).append(match.group(3).strip())
    return result


def exact_authored_owners() -> list[dict[str, object]]:
    result = []
    with UNITS.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if (
                row["artifact"] != "th04-main"
                or row["origin"] != "authored"
                or row["state"] != "exact"
                or not row["file_offset"]
            ):
                continue
            start = int(row["file_offset"], 0) - 0x1800 + 0x10000
            result.append(
                {
                    "start": start,
                    "end": start + int(row["size"], 0),
                    "file_start": int(row["file_offset"], 0),
                    "unit_id": row["id"],
                    "source": row["source"],
                    "owner_name": row["name"],
                }
            )
    return result


def candidates(functions: dict[int, str], publics: dict[int, list[str]]) -> list[dict[str, object]]:
    policy = tomllib.loads(POLICY.read_text(encoding="utf-8"))
    provisional = {int(item["address"], 0) for item in policy.get("provisional", [])}
    result: dict[int, dict[str, object]] = {}
    for owner in exact_authored_owners():
        for address, ghidra_name in functions.items():
            if not (int(owner["start"]) <= address < int(owner["end"])):
                continue
            if address not in publics or address in provisional:
                continue
            result[address] = {
                "address": address,
                "address_hex": f"0x{address:X}",
                "ghidra_name": ghidra_name,
                "public": publics[address][0],
                "owner_unit": owner["unit_id"],
                "owner_start": owner["start"],
                "owner_end": owner["end"],
                "file_offset": int(owner["file_start"]) + (address - int(owner["start"])),
                "source": owner["source"],
                "owner_name": owner["owner_name"],
            }
    return [result[key] for key in sorted(result)]


def public_owner_candidates(publics: dict[int, list[str]]) -> list[dict[str, object]]:
    """Return TLINK public starts that fall inside exact authored byte owners."""
    result: dict[int, dict[str, object]] = {}
    for owner in exact_authored_owners():
        for address, names in publics.items():
            if int(owner["start"]) <= address < int(owner["end"]):
                result[address] = {
                    "address": address, "address_hex": f"0x{address:X}",
                    "ghidra_name": "", "public": names[0],
                    "owner_unit": owner["unit_id"], "owner_start": owner["start"],
                    "owner_end": owner["end"],
                    "file_offset": int(owner["file_start"]) + (address - int(owner["start"])),
                    "source": owner["source"], "owner_name": owner["owner_name"],
                }
    return [result[key] for key in sorted(result)]


def reviewed_exact_no_ghidra_reviews(functions, publics, target):
    policy = tomllib.loads(POLICY.read_text(encoding="utf-8"))
    by_address = {int(item["address"]): item for item in public_owner_candidates(publics)}
    raw_target = target.read_bytes()
    accepted = []

    def read_word(linear: int) -> int:
        offset = linear - 0x10000 + 0x1800
        if offset < 0 or offset + 2 > len(raw_target):
            raise ValueError(f"no-Ghidra switch table address 0x{linear:X} escapes target")
        return int.from_bytes(raw_target[offset:offset + 2], "little")

    for override in policy.get("reviewed_exact_no_ghidra", []):
        address = int(str(override["address"]), 0)
        file_offset = int(str(override["file_offset"]), 0)
        size = int(str(override["size"]), 0)
        decode_size = int(str(override.get("decode_size", override["size"])), 0)
        if not (0 < decode_size <= size):
            raise ValueError(f"no-Ghidra exact address 0x{address:X} has invalid decode_size")
        item = by_address.get(address)
        if item is None:
            raise ValueError(f"no-Ghidra exact address 0x{address:X} lacks exact-owner/TLINK-public candidate")
        if address in functions:
            raise ValueError(f"no-Ghidra exact address 0x{address:X} has a Ghidra function entry")
        if str(override["owner_unit"]) != str(item["owner_unit"]):
            raise ValueError(f"no-Ghidra exact address 0x{address:X} owner mismatch")
        if file_offset != address - 0x10000 + 0x1800:
            raise ValueError(f"no-Ghidra exact address 0x{address:X} file offset mismatch")
        if address + size > int(item["owner_end"]):
            raise ValueError(f"no-Ghidra exact address 0x{address:X} escapes exact owner")
        next_public = override.get("next_public_address")
        if next_public is not None:
            boundary = int(str(next_public), 0)
            if address + size != boundary or boundary not in publics:
                raise ValueError(f"no-Ghidra exact address 0x{address:X} next-public boundary mismatch")
            boundary_mode = f"next TLINK public 0x{boundary:X}"
        else:
            if address + size != int(item["owner_end"]):
                raise ValueError(f"no-Ghidra exact address 0x{address:X} must end at exact owner boundary")
            boundary_mode = f"exact owner end 0x{int(item['owner_end']):X}"

        decoded = linear_decode(target, address, file_offset, decode_size)
        instruction_addresses = set(int(value) for value in decoded["instruction_addresses"])
        switch_review = None
        if "jump_table_address" in override:
            code_end = address + decode_size
            extent_end = address + size
            jump_table_address = int(str(override["jump_table_address"]), 0)
            jump_table_count = int(override["jump_table_count"])
            cs_base = int(str(override["cs_base"]), 0)
            metadata_address = override.get("table_metadata_address")
            metadata_value = None
            expected_table_start = code_end
            if metadata_address is not None:
                metadata_linear = int(str(metadata_address), 0)
                if metadata_linear != code_end:
                    raise ValueError(f"no-Ghidra switch metadata for 0x{address:X} must start after code")
                metadata_offset = metadata_linear - 0x10000 + 0x1800
                metadata_value = raw_target[metadata_offset]
                if "table_metadata_value" in override and metadata_value != int(str(override["table_metadata_value"]), 0):
                    raise ValueError(f"no-Ghidra switch metadata for 0x{address:X} mismatches target")
                expected_table_start += 1
            if jump_table_address != expected_table_start:
                raise ValueError(f"no-Ghidra switch table for 0x{address:X} does not immediately follow code/metadata")
            table_end = jump_table_address + (jump_table_count * 2)
            if table_end != extent_end:
                raise ValueError(f"no-Ghidra switch table for 0x{address:X} does not fill trailing extent")
            jump_words = [read_word(jump_table_address + (index * 2)) for index in range(jump_table_count)]
            jump_targets = [cs_base + word for word in jump_words]
            bad_targets = [value for value in jump_targets if value not in instruction_addresses]
            if bad_targets:
                rendered = ", ".join(f"0x{value:X}" for value in bad_targets)
                raise ValueError(f"no-Ghidra switch table for 0x{address:X} targets non-instruction starts: {rendered}")
            switch_review = {
                "cs_base": f"0x{cs_base:X}",
                "jump_table_address": f"0x{jump_table_address:X}",
                "jump_table_count": jump_table_count,
                "jump_words": [f"0x{value:04X}" for value in jump_words],
                "jump_targets": [f"0x{value:X}" for value in jump_targets],
                "all_targets_are_instruction_starts": True,
                "table_metadata_address": (f"0x{int(str(metadata_address), 0):X}" if metadata_address is not None else None),
                "table_metadata_value": (f"0x{metadata_value:02X}" if metadata_value is not None else None),
                "trailing_extent_fully_accounted": True,
            }
        elif decode_size != size:
            raise ValueError(f"no-Ghidra exact address 0x{address:X} has unexplained trailing bytes")

        decoded.pop("instruction_addresses", None)
        accepted.append({
            **item,
            "id": str(override["id"]),
            "file_offset": file_offset,
            "size": size,
            "decode_size": decode_size,
            "evidence_id": str(override["evidence_id"]),
            "reason": str(override["reason"]),
            "decode": decoded,
            "switch_review": switch_review,
            "boundary_mode": boundary_mode,
        })
    return accepted


def parse_metadata(path: Path) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        row: dict[str, str] = {}
        for line in block.splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                row[key] = value
        if "address" in row:
            result[int(row["address"], 16)] = row
    return result


def linear_decode(path: Path, address: int, file_offset: int, size: int) -> dict[str, object]:
    data = path.read_bytes()[file_offset:file_offset + size]
    if len(data) != size:
        raise ValueError(f"manual function extent 0x{file_offset:X}+0x{size:X} exceeds target")
    with tempfile.NamedTemporaryFile(prefix="th04-fn-", suffix=".bin") as stream:
        stream.write(data)
        stream.flush()
        completed = subprocess.run(
            ["ndisasm", "-b16", f"-o0x{address:X}", stream.name],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
    parsed: list[dict[str, object]] = []
    pattern = re.compile(r"^([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+(.+)$")
    for line in completed.stdout.splitlines():
        match = pattern.match(line)
        if not match:
            # ndisasm wraps instructions longer than eight bytes onto a raw-byte
            # continuation line (for example ``         -00``). Boundaries must
            # therefore come from adjacent instruction addresses rather than from
            # the first display line's hex width.
            continue
        insn_address = int(match.group(1), 16)
        if len(match.group(2)) % 2:
            raise ValueError(f"odd ndisasm byte text at 0x{insn_address:X}")
        parsed.append({"address": insn_address, "text": match.group(3)})
    if not parsed:
        raise ValueError("ndisasm produced no instructions")
    if int(parsed[0]["address"]) != address:
        raise ValueError(
            f"ndisasm starts at 0x{int(parsed[0]['address']):X}; expected 0x{address:X}"
        )
    end = address + size
    instructions: list[dict[str, object]] = []
    for index, item in enumerate(parsed):
        insn_address = int(item["address"])
        next_address = (
            int(parsed[index + 1]["address"]) if index + 1 < len(parsed) else end
        )
        insn_size = next_address - insn_address
        if not (1 <= insn_size <= 15):
            raise ValueError(
                f"non-contiguous ndisasm output at 0x{insn_address:X}: "
                f"next boundary 0x{next_address:X}"
            )
        instructions.append(
            {"address": insn_address, "size": insn_size, "text": item["text"]}
        )
    expected = int(instructions[-1]["address"]) + int(instructions[-1]["size"])
    if expected != end:
        raise ValueError(f"ndisasm covered through 0x{expected:X}; expected 0x{end:X}")
    terminal = str(instructions[-1]["text"]).lower()
    if not terminal.startswith(("ret", "retf")):
        raise ValueError(f"manual function does not end in RET/RETF: {terminal}")
    return {
        "instruction_count": len(instructions),
        "instruction_addresses": [item["address"] for item in instructions],
        "terminal": instructions[-1]["text"],
        "first_address": f"0x{address:X}",
        "end_address_exclusive": f"0x{expected:X}",
    }


def manual_reviews(
    items: list[dict[str, object]],
    metadata: dict[int, dict[str, str]],
    target: Path,
) -> list[dict[str, object]]:
    policy = tomllib.loads(POLICY.read_text(encoding="utf-8"))
    by_address = {int(item["address"]): item for item in items}
    accepted: list[dict[str, object]] = []
    for override in policy.get("reviewed_exact", []):
        address = int(str(override["address"]), 0)
        file_offset = int(str(override["file_offset"]), 0)
        size = int(str(override["size"]), 0)
        item = by_address.get(address)
        if item is None:
            raise ValueError(f"manual exact address 0x{address:X} lacks exact-owner/public candidate")
        if str(override["owner_unit"]) != str(item["owner_unit"]):
            raise ValueError(f"manual exact address 0x{address:X} owner mismatch")
        expected_file = address - 0x10000 + 0x1800
        if file_offset != expected_file:
            raise ValueError(f"manual exact address 0x{address:X} file offset mismatch")
        if not (int(item["owner_start"]) <= address and address + size <= int(item["owner_end"])):
            raise ValueError(f"manual exact address 0x{address:X} escapes exact owner")
        data = metadata.get(address)
        if data is None:
            raise ValueError(f"manual exact address 0x{address:X} lacks Ghidra metadata")
        body_min = int(data["body_min"], 16)
        body_max = int(data["body_max"], 16)
        if body_min != address or body_max != address + size - 1:
            raise ValueError(f"manual exact address 0x{address:X} disagrees with Ghidra min/max span")
        decoded = linear_decode(target, address, file_offset, size)
        switch_review = None
        if "jump_table_address" in override:
            jump_table_address = int(str(override["jump_table_address"]), 0)
            jump_table_count = int(override["jump_table_count"])
            cs_base = int(str(override["cs_base"]), 0)
            if jump_table_address < address + size:
                raise ValueError(f"manual switch table for 0x{address:X} overlaps function body")
            raw_target = target.read_bytes()
            def read_word(linear: int) -> int:
                offset = linear - 0x10000 + 0x1800
                if offset < 0 or offset + 2 > len(raw_target):
                    raise ValueError(f"switch table address 0x{linear:X} escapes target")
                return int.from_bytes(raw_target[offset:offset + 2], "little")
            jump_words = [read_word(jump_table_address + (index * 2)) for index in range(jump_table_count)]
            jump_targets = [cs_base + word for word in jump_words]
            instruction_addresses = set(int(value) for value in decoded["instruction_addresses"])
            bad_targets = [target_address for target_address in jump_targets if target_address not in instruction_addresses]
            if bad_targets:
                rendered = ", ".join(f"0x{value:X}" for value in bad_targets)
                raise ValueError(f"switch table for 0x{address:X} targets non-instruction starts: {rendered}")
            compare_values = None
            if "compare_table_address" in override:
                compare_table_address = int(str(override["compare_table_address"]), 0)
                if compare_table_address < address + size:
                    raise ValueError(f"manual compare table for 0x{address:X} overlaps function body")
                compare_values = [read_word(compare_table_address + (index * 2)) for index in range(jump_table_count)]
            switch_review = {
                "cs_base": f"0x{cs_base:X}",
                "jump_table_address": f"0x{jump_table_address:X}",
                "jump_table_count": jump_table_count,
                "jump_words": [f"0x{value:04X}" for value in jump_words],
                "jump_targets": [f"0x{value:X}" for value in jump_targets],
                "all_targets_are_instruction_starts": True,
                "compare_table_address": (
                    f"0x{int(str(override['compare_table_address']), 0):X}"
                    if "compare_table_address" in override else None
                ),
                "compare_values": ([f"0x{value:04X}" for value in compare_values] if compare_values is not None else None),
            }
        decoded.pop("instruction_addresses", None)
        accepted.append({
            **item,
            "id": str(override["id"]),
            "file_offset": file_offset,
            "size": size,
            "body_min": body_min,
            "body_max": body_max,
            "body_addresses": int(data["body_addresses"]),
            "evidence_id": str(override["evidence_id"]),
            "reason": str(override["reason"]),
            "decode": decoded,
            "switch_review": switch_review,
        })
    return accepted



def reviewed_nonexact_reviews(
    items: list[dict[str, object]],
    metadata: dict[int, dict[str, str]],
    publics: dict[int, list[str]],
    target: Path,
    *,
    policy_key: str = "reviewed_nonexact",
    require_exact_extent: bool = False,
) -> list[dict[str, object]]:
    """Validate complete reviewed extents independent of Ghidra body construction.

    The default nonexact mode requires an exact-entry/public candidate, target
    Ghidra entry metadata, a gap-free raw decode through RET/RETF for the configured
    code span, and any declared trailing switch targets to land on decoded
    instruction starts. The complete reviewed extent may extend beyond the entry
    owner. Exact-extent mode reuses those gates but additionally requires the
    configured full extent to stay inside the named exact authored byte owner.
    """

    policy = tomllib.loads(POLICY.read_text(encoding="utf-8"))
    by_address = {int(item["address"]): item for item in items}
    raw_target = target.read_bytes()
    accepted: list[dict[str, object]] = []

    def read_word(linear: int) -> int:
        offset = linear - 0x10000 + 0x1800
        if offset < 0 or offset + 2 > len(raw_target):
            raise ValueError(f"switch table address 0x{linear:X} escapes target")
        return int.from_bytes(raw_target[offset:offset + 2], "little")

    for override in policy.get(policy_key, []):
        address = int(str(override["address"]), 0)
        file_offset = int(str(override["file_offset"]), 0)
        size = int(str(override["size"]), 0)
        decode_size = int(str(override.get("decode_size", override["size"])), 0)
        if not (0 < decode_size <= size):
            raise ValueError(f"reviewed nonexact 0x{address:X} has invalid decode_size")
        item = by_address.get(address)
        if item is None:
            raise ValueError(
                f"reviewed nonexact address 0x{address:X} lacks exact-entry/public candidate"
            )
        if require_exact_extent:
            owner_unit = str(override.get("owner_unit", ""))
            if not owner_unit or owner_unit != str(item["owner_unit"]):
                raise ValueError(
                    f"reviewed exact extent address 0x{address:X} owner mismatch"
                )
            if not (
                int(item["owner_start"]) <= address
                and address + size <= int(item["owner_end"])
            ):
                raise ValueError(
                    f"reviewed exact extent address 0x{address:X} escapes exact owner"
                )
        expected_file = address - 0x10000 + 0x1800
        if file_offset != expected_file:
            raise ValueError(f"reviewed nonexact address 0x{address:X} file offset mismatch")
        data = metadata.get(address)
        if data is None:
            raise ValueError(f"reviewed nonexact address 0x{address:X} lacks Ghidra metadata")
        if data.get("is_thunk") != "false" or data.get("is_external") != "false":
            raise ValueError(f"reviewed nonexact address 0x{address:X} is thunk/external")
        if address not in publics:
            raise ValueError(f"reviewed nonexact address 0x{address:X} lacks TLINK public")
        next_public = override.get("next_public_address")
        if next_public is not None:
            next_public_address = int(str(next_public), 0)
            if address + size != next_public_address or next_public_address not in publics:
                raise ValueError(
                    f"reviewed nonexact address 0x{address:X} next-public boundary mismatch"
                )
        decoded = linear_decode(target, address, file_offset, decode_size)
        instruction_addresses = set(int(value) for value in decoded["instruction_addresses"])
        switch_review = None
        if "jump_table_address" in override:
            jump_table_address = int(str(override["jump_table_address"]), 0)
            jump_table_count = int(override["jump_table_count"])
            cs_base = int(str(override["cs_base"]), 0)
            code_end = address + decode_size
            extent_end = address + size
            if not (code_end <= jump_table_address < extent_end):
                raise ValueError(
                    f"reviewed nonexact switch table for 0x{address:X} is outside trailing data"
                )
            table_end = jump_table_address + (jump_table_count * 2)
            if table_end > extent_end:
                raise ValueError(f"reviewed nonexact switch table for 0x{address:X} escapes extent")
            jump_words = [
                read_word(jump_table_address + (index * 2))
                for index in range(jump_table_count)
            ]
            jump_targets = [cs_base + word for word in jump_words]
            bad_targets = [value for value in jump_targets if value not in instruction_addresses]
            if bad_targets:
                rendered = ", ".join(f"0x{value:X}" for value in bad_targets)
                raise ValueError(
                    f"reviewed nonexact switch table for 0x{address:X} targets "
                    f"non-instruction starts: {rendered}"
                )
            metadata_address = override.get("table_metadata_address")
            metadata_value = None
            if metadata_address is not None:
                meta_linear = int(str(metadata_address), 0)
                if not (code_end <= meta_linear < extent_end):
                    raise ValueError(
                        f"reviewed nonexact table metadata for 0x{address:X} escapes trailing data"
                    )
                meta_offset = meta_linear - 0x10000 + 0x1800
                metadata_value = raw_target[meta_offset]
                if "table_metadata_value" in override and metadata_value != int(
                    str(override["table_metadata_value"]), 0
                ):
                    raise ValueError(
                        f"reviewed nonexact table metadata for 0x{address:X} mismatches target"
                    )
            switch_review = {
                "cs_base": f"0x{cs_base:X}",
                "jump_table_address": f"0x{jump_table_address:X}",
                "jump_table_count": jump_table_count,
                "jump_words": [f"0x{value:04X}" for value in jump_words],
                "jump_targets": [f"0x{value:X}" for value in jump_targets],
                "all_targets_are_instruction_starts": True,
                "table_metadata_address": (
                    f"0x{int(str(metadata_address), 0):X}" if metadata_address is not None else None
                ),
                "table_metadata_value": (
                    f"0x{metadata_value:02X}" if metadata_value is not None else None
                ),
            }
        decoded.pop("instruction_addresses", None)
        accepted.append(
            {
                **item,
                "id": str(override["id"]),
                "file_offset": file_offset,
                "size": size,
                "decode_size": decode_size,
                "reason": str(override["reason"]),
                "evidence_id": str(override.get("evidence_id", "")),
                "decode": decoded,
                "switch_review": switch_review,
                "next_public_address": (
                    f"0x{int(str(next_public), 0):X}" if next_public is not None else None
                ),
            }
        )
    return accepted

def review(items: list[dict[str, object]], metadata: dict[int, dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    accepted = []
    rejected = []
    for item in items:
        address = int(item["address"])
        data = metadata.get(address)
        reasons: list[str] = []
        if data is None:
            rejected.append({**item, "reasons": ["missing metadata"]})
            continue
        body_min = int(data["body_min"], 16)
        body_max = int(data["body_max"], 16)
        body_addresses = int(data["body_addresses"])
        if int(data["address"], 16) != address:
            reasons.append("entry mismatch")
        if body_min < int(item["owner_start"]) or body_max >= int(item["owner_end"]):
            reasons.append("body outside exact owner")
        span = body_max - body_min + 1
        if body_addresses != span:
            reasons.append(f"noncontiguous body {body_addresses}/{span}")
        if data.get("is_thunk") != "false":
            reasons.append("thunk")
        if data.get("is_external") != "false":
            reasons.append("external")
        reviewed = {
            **item,
            "body_min": body_min,
            "body_max": body_max,
            "body_addresses": body_addresses,
            "size": span,
            "calling_convention": data.get("calling_convention", ""),
            "signature": data.get("signature", ""),
        }
        if reasons:
            rejected.append({**reviewed, "reasons": reasons})
        else:
            accepted.append(reviewed)
    return accepted, rejected



def write_reviewed_ledger(
    path: Path,
    automatic_exact: list[dict[str, object]],
    manual_exact: list[dict[str, object]],
    reviewed_nonexact: list[dict[str, object]] | None = None,
) -> None:
    ledger = ROOT / "config" / "th04_main_authored_functions.csv"
    with ledger.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ValueError("authored function ledger lacks header")
        fieldnames = reader.fieldnames
        rows = list(reader)

    automatic_by_address = {int(item["address"]): item for item in automatic_exact}
    manual_by_id = {str(item["id"]): item for item in manual_exact}
    nonexact_by_id = {str(item["id"]): item for item in (reviewed_nonexact or [])}
    seen_automatic: set[int] = set()
    seen_manual: set[str] = set()
    seen_nonexact: set[str] = set()

    for row in rows:
        address = int(row["address"], 0)
        nonexact = nonexact_by_id.get(row["id"])
        if nonexact is not None:
            seen_nonexact.add(row["id"])
            if address != int(nonexact["address"]):
                raise ValueError(f"reviewed nonexact ledger address mismatch for {row['id']}")
            if row["state"] not in {"candidate", "blocked"}:
                raise ValueError(
                    f"reviewed nonexact ledger refuses state {row['state']!r} for {row['id']}"
                )
            row["file_offset"] = f"0x{int(nonexact['file_offset']):X}"
            row["size"] = f"0x{int(nonexact['size']):X}"
            row["boundary_state"] = "reviewed"
            row["state"] = "blocked"
            row["owner_unit"] = ""
            row["source"] = ""
            evidence = [value for value in row["evidence_ids"].split(";") if value]
            evidence_id = str(nonexact.get("evidence_id", ""))
            if evidence_id and evidence_id not in evidence:
                evidence.append(evidence_id)
            row["evidence_ids"] = ";".join(evidence)
            row["notes"] = "Reviewed nonexact target boundary: " + str(nonexact["reason"])
            continue
        automatic = automatic_by_address.get(address)
        if automatic is not None:
            seen_automatic.add(address)
            if row["state"] == "exact":
                if (
                    row["owner_unit"] != str(automatic["owner_unit"])
                    or row["source"] != str(automatic["source"])
                ):
                    raise ValueError(
                        f"automatic exact owner/source drift for {row['id']}"
                    )
                continue
            if row["state"] not in {"candidate", "blocked"}:
                raise ValueError(
                    f"automatic ledger refuses state {row['state']!r} for {row['id']}"
                )
            if not row["file_offset"] or not row["size"]:
                raise ValueError(f"automatic ledger lacks extent for {row['id']}")
            row["boundary_state"] = "reviewed"
            row["state"] = "exact"
            row["owner_unit"] = str(automatic["owner_unit"])
            row["source"] = str(automatic["source"])
            row["notes"] = (
                "Strict target boundary review: contiguous Ghidra body starts at the "
                "same local TLINK public and lies wholly inside exact authored owner "
                + str(automatic["owner_unit"]) + "."
            )
            continue

        manual = manual_by_id.get(row["id"])
        if manual is None:
            continue
        seen_manual.add(row["id"])
        if address != int(manual["address"]):
            raise ValueError(f"manual ledger address mismatch for {row['id']}")
        if row["state"] not in {"candidate", "blocked", "exact"}:
            raise ValueError(f"manual ledger refuses state {row['state']!r} for {row['id']}")
        row["file_offset"] = f"0x{int(manual['file_offset']):X}"
        row["size"] = f"0x{int(manual['size']):X}"
        row["boundary_state"] = "reviewed"
        row["state"] = "exact"
        row["owner_unit"] = str(manual["owner_unit"])
        row["source"] = str(manual["source"])
        evidence = [value for value in row["evidence_ids"].split(";") if value]
        evidence_id = str(manual["evidence_id"])
        if evidence_id not in evidence:
            evidence.append(evidence_id)
        row["evidence_ids"] = ";".join(evidence)
        switch = manual.get("switch_review")
        mode = (
            f"validated {switch['jump_table_count']}-entry switch table; "
            if isinstance(switch, dict) else "validated linear raw decode; "
        )
        row["notes"] = (
            "Manual target boundary review overrides a Ghidra body-construction false negative: "
            + mode + str(manual["reason"])
        )

    missing_automatic = sorted(set(automatic_by_address) - seen_automatic)
    policy = tomllib.loads(POLICY.read_text(encoding="utf-8"))
    new_exact = {
        int(item["address"], 0): item for item in policy.get("new_exact", [])
    }
    for address in missing_automatic:
        item = automatic_by_address[address]
        declaration = new_exact.get(address)
        if declaration is None:
            raise ValueError(
                f"automatic exact address 0x{address:X} is missing from the "
                "function ledger and lacks an explicit [[new_exact]] policy"
            )
        row = {field: "" for field in fieldnames}
        row.update(
            {
                "id": str(declaration["id"]),
                "artifact": "th04-main",
                "address": f"0x{address:X}",
                "file_offset": f"0x{int(item['file_offset']):X}",
                "size": f"0x{int(item['size']):X}",
                "boundary_state": "reviewed",
                "state": "exact",
                "name": str(item["public"]),
                "owner_unit": str(item["owner_unit"]),
                "source": str(item["source"]),
                "evidence_ids": str(declaration["evidence_id"]),
                "notes": (
                    "New exact-owner function admitted by explicit policy: "
                    + str(declaration["reason"])
                ),
            }
        )
        rows.append(row)
        seen_automatic.add(address)
    rows.sort(key=lambda row: int(row["address"], 0))
    missing_manual = sorted(set(manual_by_id) - seen_manual)
    for manual_id in list(missing_manual):
        item = manual_by_id[manual_id]
        address = int(item["address"])
        declaration = new_exact.get(address)
        if declaration is None or str(declaration["id"]) != manual_id:
            continue
        row = {field: "" for field in fieldnames}
        row.update({
            "id": manual_id,
            "artifact": "th04-main",
            "address": f"0x{address:X}",
            "file_offset": f"0x{int(item['file_offset']):X}",
            "size": f"0x{int(item['size']):X}",
            "boundary_state": "reviewed",
            "state": "exact",
            "name": str(item["public"]),
            "owner_unit": str(item["owner_unit"]),
            "source": str(item["source"]),
            "evidence_ids": str(item["evidence_id"]),
            "notes": "New manual exact function admitted by explicit policy: " + str(item["reason"]),
        })
        rows.append(row)
        seen_manual.add(manual_id)
    rows.sort(key=lambda row: int(row["address"], 0))
    missing_manual = sorted(set(manual_by_id) - seen_manual)
    if missing_manual:
        raise ValueError(
            "manual exact rows missing from function ledger: " + ", ".join(missing_manual)
        )
    missing_nonexact = sorted(set(nonexact_by_id) - seen_nonexact)
    if missing_nonexact:
        raise ValueError(
            "reviewed nonexact rows missing from function ledger: "
            + ", ".join(missing_nonexact)
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--functions", type=Path, required=True)
    parser.add_argument("--map", dest="map_path", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--addresses-out", type=Path)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--ledger-out", type=Path, help="write the current function ledger with validated manual exact overrides applied")
    args = parser.parse_args()

    functions = parse_functions(args.functions)
    publics = parse_publics(args.map_path)
    items = candidates(functions, publics)
    if args.addresses_out:
        args.addresses_out.parent.mkdir(parents=True, exist_ok=True)
        args.addresses_out.write_text("\n".join(str(item["address_hex"]) for item in items) + "\n", encoding="utf-8")
    report: dict[str, object] = {"schema_version": 1, "candidate_count": len(items), "candidates": items}
    if args.metadata:
        parsed_metadata = parse_metadata(args.metadata)
        accepted, rejected = review(items, parsed_metadata)
        policy = tomllib.loads(POLICY.read_text(encoding="utf-8"))
        manual_exact: list[dict[str, object]] = []
        manual_exact_no_ghidra: list[dict[str, object]] = []
        manual_exact_extent: list[dict[str, object]] = []
        reviewed_nonexact: list[dict[str, object]] = []
        if (
            policy.get("reviewed_exact", [])
            or policy.get("reviewed_exact_no_ghidra", [])
            or policy.get("reviewed_exact_extent", [])
            or policy.get("reviewed_nonexact", [])
        ):
            if args.target is None:
                parser.error("--target is required for manual/reviewed nonexact policy")
        if policy.get("reviewed_exact", []):
            assert args.target is not None
            manual_exact = manual_reviews(items, parsed_metadata, args.target)
        if policy.get("reviewed_exact_no_ghidra", []):
            assert args.target is not None
            manual_exact_no_ghidra = reviewed_exact_no_ghidra_reviews(functions, publics, args.target)
        if policy.get("reviewed_exact_extent", []):
            assert args.target is not None
            manual_exact_extent = reviewed_nonexact_reviews(
                items,
                parsed_metadata,
                publics,
                args.target,
                policy_key="reviewed_exact_extent",
                require_exact_extent=True,
            )
        if policy.get("reviewed_nonexact", []):
            assert args.target is not None
            reviewed_nonexact = reviewed_nonexact_reviews(
                items, parsed_metadata, publics, args.target
            )
        manual_exact_all = [*manual_exact, *manual_exact_no_ghidra, *manual_exact_extent]
        reviewed_addresses = {
            int(item["address"]) for item in [*manual_exact_all, *reviewed_nonexact]
        }
        rejected = [
            item for item in rejected if int(item["address"]) not in reviewed_addresses
        ]
        exact_count = len(accepted) + len(manual_exact_all)
        denominator = exact_count + len(reviewed_nonexact)
        report.update(
            {
                "strict_exact_count": len(accepted),
                "manual_exact_count": len(manual_exact_all),
                "manual_exact_no_ghidra_count": len(manual_exact_no_ghidra),
                "manual_exact_extent_count": len(manual_exact_extent),
                "exact_function_count": exact_count,
                "strict_rejected_count": len(rejected),
                "reviewed_nonexact_count": len(reviewed_nonexact),
                "reviewed_function_count": denominator,
                "exact_function_percent": (exact_count * 100 / denominator if denominator else None),
                "accepted": accepted,
                "manual_exact": manual_exact_all,
                "manual_exact_extent": manual_exact_extent,
                "rejected": rejected,
                "reviewed_nonexact": reviewed_nonexact,
            }
        )
        print(
            f"exact functions: {exact_count}/{denominator} "
            f"({exact_count * 100 / denominator:.6f}%); "
            f"automatic={len(accepted)} manual={len(manual_exact_all)}"
        )
        print(f"provisional strict rejections: {len(rejected)}")
        if args.ledger_out:
            write_reviewed_ledger(
                args.ledger_out, accepted, manual_exact_all, reviewed_nonexact
            )
            print(f"reviewed ledger: {args.ledger_out}")
    else:
        print(f"candidate starts: {len(items)}")
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
