from __future__ import annotations

import struct
import sys
from pathlib import Path
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.omf import OMFError, describe_omf, normalize_dependency_timestamps, parse_omf


def record(record_type: int, payload: bytes) -> bytes:
    length = len(payload) + 1
    header = bytes([record_type]) + struct.pack("<H", length)
    checksum = (-sum(header + payload)) & 0xFF
    return header + payload + bytes([checksum])


def synthetic_object() -> bytes:
    return (
        record(0x80, b"\x05PROBE")
        + record(0x88, b"\x00\x00\x08TEST OMF")
        + record(0x88, b"\x00\xE9\x00\x00\x00\x00\x07FILE.CP")
        + record(0x8A, b"\x00")
    )


def dependency_object(timestamp: bytes, path: bytes = b"FILE.C") -> bytes:
    return (
        record(0x80, b"\x05PROBE")
        + record(0x88, b"\x00\xE9" + timestamp + bytes([len(path)]) + path)
        + record(0x8A, b"\x00")
    )


class OMFTests(unittest.TestCase):
    def test_valid_object_inventory(self) -> None:
        report = describe_omf(synthetic_object())
        self.assertTrue(report["valid"])
        self.assertEqual(report["module_name"], "PROBE")
        self.assertEqual(report["record_counts"]["COMENT"], 2)
        self.assertEqual(report["translator_comments"], ["TEST OMF"])
        self.assertEqual(report["dependency_paths"], ["FILE.CP"])

    def test_checksum_mutation_fails(self) -> None:
        changed = bytearray(synthetic_object())
        changed[5] ^= 1
        with self.assertRaisesRegex(OMFError, "checksum"):
            parse_omf(bytes(changed))

    def test_truncation_fails(self) -> None:
        with self.assertRaisesRegex(OMFError, "past EOF"):
            parse_omf(synthetic_object()[:-1])

    def test_wrong_boundary_records_fail(self) -> None:
        with self.assertRaisesRegex(OMFError, "THEADR"):
            parse_omf(record(0x88, b"\x00") + record(0x8A, b"\x00"))
        with self.assertRaisesRegex(OMFError, "MODEND"):
            parse_omf(record(0x80, b"\x01X") + record(0x88, b"\x00"))

    def test_concatenated_modules_fail(self) -> None:
        with self.assertRaisesRegex(OMFError, "THEADR records"):
            parse_omf(synthetic_object() + synthetic_object())

    def test_dependency_timestamp_normalization_is_narrow(self) -> None:
        first = dependency_object(b"\x01\x02\x03\x04")
        second = dependency_object(b"\x05\x06\x07\x08")
        different_path = dependency_object(b"\x05\x06\x07\x08", b"OTHER.C")
        self.assertNotEqual(first, second)
        self.assertEqual(
            normalize_dependency_timestamps(first),
            normalize_dependency_timestamps(second),
        )
        self.assertNotEqual(
            normalize_dependency_timestamps(first),
            normalize_dependency_timestamps(different_path),
        )


if __name__ == "__main__":
    unittest.main()
