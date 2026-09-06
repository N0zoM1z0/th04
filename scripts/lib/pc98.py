"""Small, dependency-free PC-98 target and DOS MZ helpers.

The module intentionally reports independent comparison dimensions.  Only
``raw_exact`` is an exact reconstruction verdict; every other equality is a
diagnostic that helps route the next experiment.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from collections import Counter
import hashlib
from pathlib import Path
import struct
from typing import Any, Iterable


MZ_FIELDS = (
    "magic",
    "bytes_on_last_page",
    "number_of_pages",
    "number_of_relocations",
    "header_paragraphs",
    "minimum_extra_allocation",
    "maximum_extra_allocation",
    "initial_relative_ss",
    "initial_sp",
    "checksum",
    "initial_ip",
    "initial_relative_cs",
    "relocation_table_offset",
    "overlay_number",
)


class FormatError(ValueError):
    """Raised when an input claims a format but violates its structure."""


@dataclass(frozen=True)
class MZHeader:
    magic: int
    bytes_on_last_page: int
    number_of_pages: int
    number_of_relocations: int
    header_paragraphs: int
    minimum_extra_allocation: int
    maximum_extra_allocation: int
    initial_relative_ss: int
    initial_sp: int
    checksum: int
    initial_ip: int
    initial_relative_cs: int
    relocation_table_offset: int
    overlay_number: int

    @property
    def header_size(self) -> int:
        return self.header_paragraphs * 16

    @property
    def declared_file_size(self) -> int:
        if self.number_of_pages == 0:
            return 0
        if self.bytes_on_last_page == 0:
            return self.number_of_pages * 512
        return (self.number_of_pages - 1) * 512 + self.bytes_on_last_page

    @property
    def entry_linear(self) -> int:
        return self.initial_relative_cs * 16 + self.initial_ip


@dataclass(frozen=True)
class MZRelocation:
    offset: int
    segment: int

    @property
    def linear(self) -> int:
        return self.segment * 16 + self.offset


@dataclass(frozen=True)
class MZImage:
    raw: bytes
    header: MZHeader
    relocations: tuple[MZRelocation, ...]
    program_image: bytes
    overlay: bytes
    relocation_table_end: int
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors

    def normalized_program_image(self) -> bytes:
        normalized = bytearray(self.program_image)
        for relocation in self.relocations:
            if 0 <= relocation.linear <= len(normalized) - 2:
                normalized[relocation.linear : relocation.linear + 2] = b"\0\0"
        return bytes(normalized)

    def relocated_program_image(self, load_segment: int) -> bytes:
        """Apply DOS MZ load-segment fixups to a copy of the load module."""

        if not 0 <= load_segment <= 0xFFFF:
            raise ValueError("MZ load segment must fit in 16 bits")
        relocated = bytearray(self.program_image)
        for relocation in self.relocations:
            if not 0 <= relocation.linear <= len(relocated) - 2:
                raise FormatError(
                    f"relocation site 0x{relocation.linear:X} is outside load module"
                )
            value = struct.unpack_from("<H", relocated, relocation.linear)[0]
            struct.pack_into(
                "<H", relocated, relocation.linear, (value + load_segment) & 0xFFFF
            )
        return bytes(relocated)


@dataclass(frozen=True)
class FatBootSector:
    offset: int
    oem_name: str
    bytes_per_sector: int
    sectors_per_cluster: int
    reserved_sectors: int
    fat_count: int
    root_entries: int
    total_sectors: int
    media_type: int
    fat_sectors: int
    sectors_per_track: int
    heads: int
    hidden_sectors: int
    volume_label: str
    filesystem: str


def digest_bytes(data: bytes, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


def digest_file(path: Path, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_mz(data: bytes) -> MZImage:
    if len(data) < 28:
        raise FormatError("MZ input is shorter than the 28-byte base header")
    values = struct.unpack_from("<14H", data)
    header = MZHeader(*values)
    if header.magic != 0x5A4D:
        raise FormatError("input does not begin with an MZ signature")

    errors: list[str] = []
    declared = header.declared_file_size
    header_size = header.header_size
    relocation_end = (
        header.relocation_table_offset + header.number_of_relocations * 4
    )

    if declared == 0:
        errors.append("MZ declared file size is zero")
        declared = len(data)
    if declared > len(data):
        errors.append(
            f"MZ declares {declared} bytes but physical input has {len(data)}"
        )
        declared = len(data)
    if header_size < 28:
        errors.append(f"MZ header size {header_size} is smaller than 28")
    if header_size > declared:
        errors.append(
            f"MZ header size {header_size} exceeds declared file size {declared}"
        )
        header_size = min(max(header_size, 28), declared)
    if header.relocation_table_offset < 28 and header.number_of_relocations:
        errors.append("MZ relocation table overlaps the base header")
    if relocation_end > header_size:
        errors.append("MZ relocation table extends beyond the header")

    relocations: list[MZRelocation] = []
    readable_relocation_end = min(relocation_end, header_size, len(data))
    cursor = header.relocation_table_offset
    while cursor + 4 <= readable_relocation_end:
        offset, segment = struct.unpack_from("<HH", data, cursor)
        relocations.append(MZRelocation(offset, segment))
        cursor += 4
    if len(relocations) != header.number_of_relocations:
        errors.append(
            "MZ relocation count does not fit in the readable relocation table"
        )

    program = data[header_size:declared]
    if header.entry_linear >= len(program):
        errors.append(
            f"MZ entry CS:IP resolves to 0x{header.entry_linear:X}, "
            f"outside the {len(program)}-byte load module"
        )
    invalid_sites = [r for r in relocations if r.linear > len(program) - 2]
    if invalid_sites:
        errors.append(
            f"{len(invalid_sites)} MZ relocation site(s) are outside the load module"
        )

    return MZImage(
        raw=data,
        header=header,
        relocations=tuple(relocations),
        program_image=program,
        overlay=data[declared:],
        relocation_table_end=relocation_end,
        errors=tuple(errors),
    )


def classify_format(data: bytes) -> str:
    return "mz" if data.startswith(b"MZ") else "com"


def _byte_comparison(left: bytes, right: bytes) -> dict[str, Any]:
    overlap = min(len(left), len(right))
    first_difference = next(
        (index for index in range(overlap) if left[index] != right[index]), None
    )
    if first_difference is None and len(left) != len(right):
        first_difference = overlap
    differing = sum(a != b for a, b in zip(left, right)) + abs(
        len(left) - len(right)
    )
    prefix = 0
    while prefix < overlap and left[prefix] == right[prefix]:
        prefix += 1
    suffix = 0
    suffix_limit = overlap - prefix
    while suffix < suffix_limit and left[-1 - suffix] == right[-1 - suffix]:
        suffix += 1
    runs: list[dict[str, int]] = []
    cursor = 0
    maximum = max(len(left), len(right))
    while cursor < maximum:
        left_byte = left[cursor] if cursor < len(left) else None
        right_byte = right[cursor] if cursor < len(right) else None
        if left_byte == right_byte:
            cursor += 1
            continue
        start = cursor
        cursor += 1
        while cursor < maximum:
            left_byte = left[cursor] if cursor < len(left) else None
            right_byte = right[cursor] if cursor < len(right) else None
            if left_byte == right_byte:
                break
            cursor += 1
        runs.append({"offset": start, "length": cursor - start})
    return {
        "exact": left == right,
        "left_size": len(left),
        "right_size": len(right),
        "differing_bytes": differing,
        "first_difference": (
            None if first_difference is None else f"0x{first_difference:X}"
        ),
        "common_prefix": prefix,
        "common_suffix": suffix,
        "difference_run_count": len(runs),
        "largest_difference_run": max(
            (run["length"] for run in runs), default=0
        ),
        "difference_runs": runs[:256],
        "difference_runs_truncated": len(runs) > 256,
        "left_sha256": digest_bytes(left),
        "right_sha256": digest_bytes(right),
    }


def _relocation_dicts(
    relocations: Iterable[MZRelocation],
) -> list[dict[str, Any]]:
    return [
        {
            "segment": f"0x{item.segment:04X}",
            "offset": f"0x{item.offset:04X}",
            "linear": f"0x{item.linear:X}",
        }
        for item in relocations
    ]


def describe_blob(data: bytes) -> dict[str, Any]:
    detected = classify_format(data)
    base: dict[str, Any] = {
        "format": detected,
        "size": len(data),
        "sha256": digest_bytes(data),
        "md5": digest_bytes(data, "md5"),
    }
    if detected == "com":
        base["format_integrity"] = {"valid": bool(data), "errors": []}
        return base
    image = parse_mz(data)
    base.update(
        {
            "format_integrity": {
                "valid": image.valid,
                "errors": list(image.errors),
            },
            "mz": {
                "header": {
                    **{
                        key: (
                            f"0x{getattr(image.header, key):04X}"
                            if key not in {
                                "bytes_on_last_page",
                                "number_of_pages",
                                "number_of_relocations",
                                "header_paragraphs",
                            }
                            else getattr(image.header, key)
                        )
                        for key in MZ_FIELDS
                    },
                    "header_size": image.header.header_size,
                    "declared_file_size": image.header.declared_file_size,
                    "entry_linear": f"0x{image.header.entry_linear:X}",
                },
                "relocations": {
                    "count": len(image.relocations),
                    "entries": _relocation_dicts(image.relocations),
                },
                "program_image": {
                    "size": len(image.program_image),
                    "sha256": digest_bytes(image.program_image),
                    "relocation_normalized_sha256": digest_bytes(
                        image.normalized_program_image()
                    ),
                },
                "overlay": {
                    "size": len(image.overlay),
                    "sha256": digest_bytes(image.overlay),
                },
            },
        }
    )
    return base


def compare_blobs(left: bytes, right: bytes) -> dict[str, Any]:
    left_format = classify_format(left)
    right_format = classify_format(right)
    result: dict[str, Any] = {
        "schema_version": 1,
        "verdict": {
            "raw_exact": left == right,
            "diagnostic_only": not (left == right),
            "note": "Only raw_exact=true is an exact reconstruction verdict.",
        },
        "formats": {
            "same": left_format == right_format,
            "left": left_format,
            "right": right_format,
        },
        "raw": _byte_comparison(left, right),
    }
    if left_format != right_format:
        result["routing_hints"] = ["format-or-target-mismatch"]
        return result
    if left_format == "com":
        result["com_image"] = _byte_comparison(left, right)
        result["routing_hints"] = (
            ["exact"] if left == right else ["flat-com-content-difference"]
        )
        return result

    try:
        left_mz = parse_mz(left)
        right_mz = parse_mz(right)
    except FormatError as error:
        result["format_integrity"] = {
            "both_valid": False,
            "parse_error": str(error),
        }
        return result

    left_header = asdict(left_mz.header)
    right_header = asdict(right_mz.header)
    changed_fields = [
        field for field in MZ_FIELDS if left_header[field] != right_header[field]
    ]
    left_relocations = [(r.segment, r.offset) for r in left_mz.relocations]
    right_relocations = [(r.segment, r.offset) for r in right_mz.relocations]
    left_multiset = Counter(left_relocations)
    right_multiset = Counter(right_relocations)
    left_set = set(left_relocations)
    right_set = set(right_relocations)
    shared_sites = sorted(left_set & right_set)
    relocation_value_differences: list[dict[str, Any]] = []
    for segment, offset in shared_sites:
        linear = segment * 16 + offset
        if linear > len(left_mz.program_image) - 2:
            continue
        if linear > len(right_mz.program_image) - 2:
            continue
        left_value = struct.unpack_from("<H", left_mz.program_image, linear)[0]
        right_value = struct.unpack_from("<H", right_mz.program_image, linear)[0]
        if left_value != right_value:
            relocation_value_differences.append(
                {
                    "segment": f"0x{segment:04X}",
                    "offset": f"0x{offset:04X}",
                    "linear": f"0x{linear:X}",
                    "left": f"0x{left_value:04X}",
                    "right": f"0x{right_value:04X}",
                }
            )

    left_header_size = min(left_mz.header.header_size, len(left))
    right_header_size = min(right_mz.header.header_size, len(right))
    relocation_byte_offsets = {
        byte_offset
        for relocation in (*left_mz.relocations, *right_mz.relocations)
        for byte_offset in (relocation.linear, relocation.linear + 1)
    }
    program_overlap = min(len(left_mz.program_image), len(right_mz.program_image))
    program_differences_at_relocations = sum(
        left_mz.program_image[index] != right_mz.program_image[index]
        for index in range(program_overlap)
        if index in relocation_byte_offsets
    )
    program_differences_outside_relocations = sum(
        left_mz.program_image[index] != right_mz.program_image[index]
        for index in range(program_overlap)
        if index not in relocation_byte_offsets
    ) + abs(len(left_mz.program_image) - len(right_mz.program_image))
    result["format_integrity"] = {
        "both_valid": left_mz.valid and right_mz.valid,
        "left_errors": list(left_mz.errors),
        "right_errors": list(right_mz.errors),
    }
    result["mz"] = {
        "header_fields": {
            "exact": not changed_fields,
            "changed": changed_fields,
        },
        "header_bytes": _byte_comparison(
            left[:left_header_size], right[:right_header_size]
        ),
        "relocations": {
            "ordered_exact": left_relocations == right_relocations,
            "multiset_exact": left_multiset == right_multiset,
            "set_exact": left_set == right_set,
            "left_count": len(left_relocations),
            "right_count": len(right_relocations),
            "only_left": [
                {"segment": f"0x{s:04X}", "offset": f"0x{o:04X}"}
                for s, o in sorted(left_set - right_set)
            ],
            "only_right": [
                {"segment": f"0x{s:04X}", "offset": f"0x{o:04X}"}
                for s, o in sorted(right_set - left_set)
            ],
            "site_values": {
                "exact": not relocation_value_differences,
                "differing_count": len(relocation_value_differences),
                "differences": relocation_value_differences[:256],
                "truncated": len(relocation_value_differences) > 256,
            },
        },
        "program_image": _byte_comparison(
            left_mz.program_image, right_mz.program_image
        ),
        "program_difference_partition": {
            "at_relocation_site_bytes": program_differences_at_relocations,
            "outside_relocation_site_bytes": (
                program_differences_outside_relocations
            ),
            "site_byte_basis": "union-of-left-and-right-relocation-sites",
        },
        "relocation_normalized_program": _byte_comparison(
            left_mz.normalized_program_image(),
            right_mz.normalized_program_image(),
        ),
        "overlay": _byte_comparison(left_mz.overlay, right_mz.overlay),
    }
    result["verdict"]["layout_structural_exact"] = bool(
        result["format_integrity"]["both_valid"]
        and result["mz"]["header_fields"]["exact"]
        and result["mz"]["relocations"]["ordered_exact"]
        and len(left_mz.program_image) == len(right_mz.program_image)
        and len(left_mz.overlay) == len(right_mz.overlay)
    )
    result["verdict"]["relocation_normalized_program_exact"] = result["mz"][
        "relocation_normalized_program"
    ]["exact"]
    hints: list[str] = []
    if result["verdict"]["raw_exact"]:
        hints.append("exact")
    else:
        header_exact = result["mz"]["header_bytes"]["exact"]
        reloc_order_exact = result["mz"]["relocations"]["ordered_exact"]
        program_exact = result["mz"]["program_image"]["exact"]
        normalized_exact = result["mz"]["relocation_normalized_program"]["exact"]
        overlay_exact = result["mz"]["overlay"]["exact"]
        if not result["format_integrity"]["both_valid"]:
            hints.append("invalid-mz-structure")
        if not header_exact and program_exact and overlay_exact:
            if result["mz"]["header_fields"]["exact"] and not reloc_order_exact:
                hints.append("relocation-table-order-or-header-padding-difference")
            else:
                hints.append("header-only-difference")
        if header_exact and reloc_order_exact and not program_exact and normalized_exact:
            hints.append("relocated-word-values-only")
        if header_exact and reloc_order_exact and program_exact and not overlay_exact:
            hints.append("overlay-only-difference")
        if not program_exact and not normalized_exact:
            hints.append("non-relocation-program-content-difference")
        if not result["mz"]["relocations"]["set_exact"]:
            hints.append("relocation-site-set-difference")
        elif not result["mz"]["relocations"]["multiset_exact"]:
            hints.append("relocation-site-multiplicity-difference")
        if not hints:
            hints.append("mixed-or-layout-difference")
    result["routing_hints"] = hints
    return result


def parse_fat_boot_sector(data: bytes, offset: int) -> FatBootSector:
    if offset < 0 or offset + 90 > len(data):
        raise FormatError("FAT boot-sector offset is outside the image")
    sector = data[offset : offset + 512]
    if sector[0] not in (0xE9, 0xEB):
        raise FormatError("FAT boot sector lacks an x86 jump instruction")
    bytes_per_sector = struct.unpack_from("<H", sector, 11)[0]
    sectors_per_cluster = sector[13]
    reserved = struct.unpack_from("<H", sector, 14)[0]
    fat_count = sector[16]
    root_entries = struct.unpack_from("<H", sector, 17)[0]
    total16 = struct.unpack_from("<H", sector, 19)[0]
    media_type = sector[21]
    fat_sectors = struct.unpack_from("<H", sector, 22)[0]
    sectors_per_track = struct.unpack_from("<H", sector, 24)[0]
    heads = struct.unpack_from("<H", sector, 26)[0]
    hidden = struct.unpack_from("<I", sector, 28)[0]
    total32 = struct.unpack_from("<I", sector, 32)[0]
    filesystem = sector[54:62].decode("ascii", errors="replace").strip()
    volume_label = sector[43:54].decode("ascii", errors="replace").rstrip()
    total = total16 or total32

    if bytes_per_sector not in (128, 256, 512, 1024, 2048, 4096):
        raise FormatError(f"implausible FAT bytes/sector: {bytes_per_sector}")
    if sectors_per_cluster == 0 or sectors_per_cluster & (sectors_per_cluster - 1):
        raise FormatError("FAT sectors/cluster is not a nonzero power of two")
    if reserved == 0 or fat_count not in range(1, 5):
        raise FormatError("implausible FAT reserved-sector or FAT count")
    if root_entries == 0 or total == 0 or fat_sectors == 0:
        raise FormatError("incomplete FAT12/16 BPB")
    if media_type < 0xF0:
        raise FormatError(f"implausible FAT media descriptor: 0x{media_type:02X}")
    if not filesystem.startswith(("FAT12", "FAT16")):
        raise FormatError(f"unsupported FAT marker: {filesystem!r}")
    if offset + total * bytes_per_sector > len(data):
        raise FormatError("FAT BPB extends beyond the containing image")

    return FatBootSector(
        offset=offset,
        oem_name=sector[3:11].decode("ascii", errors="replace").rstrip(),
        bytes_per_sector=bytes_per_sector,
        sectors_per_cluster=sectors_per_cluster,
        reserved_sectors=reserved,
        fat_count=fat_count,
        root_entries=root_entries,
        total_sectors=total,
        media_type=media_type,
        fat_sectors=fat_sectors,
        sectors_per_track=sectors_per_track,
        heads=heads,
        hidden_sectors=hidden,
        volume_label=volume_label,
        filesystem=filesystem,
    )


def find_fat_boot_sectors(
    data: bytes, start: int, physical_sector_size: int, scan_bytes: int = 4 << 20
) -> list[FatBootSector]:
    matches: list[FatBootSector] = []
    end = min(len(data) - 90, start + scan_bytes)
    for offset in range(start, end + 1, physical_sector_size):
        try:
            matches.append(parse_fat_boot_sector(data, offset))
        except FormatError:
            pass
    return matches
