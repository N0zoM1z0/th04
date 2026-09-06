"""Strict, dependency-free Intel OMF record validation.

Borland's 16-bit tools communicate through OMF objects and libraries.  A
successful process exit is therefore not sufficient evidence that a usable
object was produced: every record carries a length and an eight-bit checksum
that can be validated independently.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import struct
from typing import Any


RECORD_NAMES = {
    0x80: "THEADR",
    0x82: "LHEADR",
    0x88: "COMENT",
    0x8A: "MODEND",
    0x8B: "MODEND32",
    0x8C: "EXTDEF",
    0x90: "PUBDEF",
    0x91: "PUBDEF32",
    0x94: "LINNUM",
    0x95: "LINNUM32",
    0x96: "LNAMES",
    0x98: "SEGDEF",
    0x99: "SEGDEF32",
    0x9A: "GRPDEF",
    0x9C: "FIXUPP",
    0x9D: "FIXUPP32",
    0xA0: "LEDATA",
    0xA1: "LEDATA32",
    0xA2: "LIDATA",
    0xA3: "LIDATA32",
    0xB0: "COMDEF",
    0xB2: "BAKPAT",
    0xB3: "BAKPAT32",
    0xB4: "LEXTDEF",
    0xB6: "LPUBDEF",
    0xB7: "LPUBDEF32",
    0xB8: "LCOMDEF",
    0xBC: "CEXTDEF",
    0xC2: "COMDAT",
    0xC3: "COMDAT32",
    0xC4: "LINSYM",
    0xC5: "LINSYM32",
    0xC6: "ALIAS",
    0xC8: "NBKPAT",
    0xC9: "NBKPAT32",
    0xCA: "LLNAMES",
    0xCC: "VERNUM",
    0xCE: "VENDEXT",
}


class OMFError(ValueError):
    """Raised when an OMF stream violates record framing or checksums."""


@dataclass(frozen=True)
class OMFRecord:
    offset: int
    record_type: int
    length: int
    data: bytes
    checksum: int

    @property
    def name(self) -> str:
        return RECORD_NAMES.get(self.record_type, f"UNKNOWN_0x{self.record_type:02X}")


def parse_omf(data: bytes) -> tuple[OMFRecord, ...]:
    """Parse one object-module stream and reject any malformed record."""

    if not data:
        raise OMFError("OMF input is empty")
    records: list[OMFRecord] = []
    cursor = 0
    while cursor < len(data):
        if len(data) - cursor < 3:
            raise OMFError(f"truncated OMF record header at 0x{cursor:X}")
        record_type = data[cursor]
        length = struct.unpack_from("<H", data, cursor + 1)[0]
        if length < 1:
            raise OMFError(f"record at 0x{cursor:X} has zero length")
        end = cursor + 3 + length
        if end > len(data):
            raise OMFError(
                f"record at 0x{cursor:X} declares {length} bytes but extends "
                f"{end - len(data)} byte(s) past EOF"
            )
        framed = data[cursor:end]
        if sum(framed) & 0xFF:
            raise OMFError(f"record checksum failed at 0x{cursor:X}")
        records.append(
            OMFRecord(
                offset=cursor,
                record_type=record_type,
                length=length,
                data=data[cursor + 3 : end - 1],
                checksum=data[end - 1],
            )
        )
        cursor = end

    if records[0].record_type != 0x80:
        raise OMFError("object module does not begin with THEADR")
    if records[-1].record_type not in {0x8A, 0x8B}:
        raise OMFError("object module does not end with MODEND/MODEND32")
    return tuple(records)


def _pascal_string(data: bytes) -> str | None:
    if not data:
        return None
    length = data[0]
    if length + 1 > len(data):
        return None
    return data[1 : 1 + length].decode("ascii", errors="backslashreplace")


def normalize_dependency_timestamps(data: bytes) -> bytes:
    """Zero only Borland COMENT E9 DOS time/date fields and re-checksum.

    Open Watcom's primary OMF definition identifies the four bytes after the
    COMENT type/class as two little-endian ``dos_time``/``dos_date`` words.
    Source paths and every link-relevant record remain untouched.  In
    particular, source-level ``__DATE__``/``__TIME__`` bytes in LEDATA are not
    normalized.
    """

    records = parse_omf(data)
    normalized = bytearray(data)
    for record in records:
        if (
            record.record_type == 0x88
            and len(record.data) >= 7
            and record.data[1] == 0xE9
        ):
            payload = record.offset + 3
            normalized[payload + 2 : payload + 6] = b"\0\0\0\0"
            checksum = record.offset + 3 + record.length - 1
            normalized[checksum] = 0
            normalized[checksum] = (-sum(normalized[record.offset:checksum])) & 0xFF
    result = bytes(normalized)
    parse_omf(result)
    return result


def describe_omf(data: bytes) -> dict[str, Any]:
    records = parse_omf(data)
    counts = Counter(record.name for record in records)
    translators = [
        value
        for record in records
        if record.record_type == 0x88
        and len(record.data) >= 3
        and record.data[1] == 0x00
        and (value := _pascal_string(record.data[2:])) is not None
    ]
    dependencies = [
        value
        for record in records
        if record.record_type == 0x88
        and len(record.data) >= 7
        and record.data[1] == 0xE9
        and (value := _pascal_string(record.data[6:])) is not None
    ]
    return {
        "format": "intel-omf-object",
        "valid": True,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "dependency_timestamp_normalized_sha256": hashlib.sha256(
            normalize_dependency_timestamps(data)
        ).hexdigest(),
        "module_name": _pascal_string(records[0].data),
        "translator_comments": translators,
        "dependency_paths": dependencies,
        "record_count": len(records),
        "record_counts": dict(sorted(counts.items())),
        "first_record": records[0].name,
        "last_record": records[-1].name,
        "records": [
            {
                "offset": f"0x{record.offset:X}",
                "type": f"0x{record.record_type:02X}",
                "name": record.name,
                "length": record.length,
                "checksum": f"0x{record.checksum:02X}",
            }
            for record in records
        ],
    }
