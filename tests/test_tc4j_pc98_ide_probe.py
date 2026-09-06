from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import probe_tc4j_pc98_ide as probe


def record(record_type: int, data: bytes) -> bytes:
    length = len(data) + 1
    header = bytes((record_type, length & 0xFF, length >> 8))
    checksum = (-sum(header + data)) & 0xFF
    return header + data + bytes((checksum,))


def pstring(value: bytes) -> bytes:
    return bytes((len(value),)) + value


def fixture(*, segment_class: bytes = b"CODE") -> bytes:
    function = probe.EXPECTED_CURRENT_BYTES
    return b"".join(
        [
            record(0x80, pstring(b"probe.cpp")),
            record(0x96, pstring(b"PROBE_TEXT") + pstring(segment_class)),
            record(
                0x98,
                bytes((0x28,))
                + len(function).to_bytes(2, "little")
                + bytes((1, 2, 0)),
            ),
            record(
                0x90,
                bytes((0, 1))
                + pstring(probe.PROBE_NAME.encode("ascii"))
                + b"\x00\x00"
                + bytes((0,)),
            ),
            record(0xA0, bytes((1, 0, 0)) + function),
            record(0x8A, b"\x00"),
        ]
    )


class Pc98IdeProducerProbeTests(unittest.TestCase):
    def test_public_code_bytes_extracts_exact_ledata(self) -> None:
        code, public = probe.public_code_bytes(
            fixture(), probe.PROBE_NAME, len(probe.EXPECTED_CURRENT_BYTES)
        )
        self.assertEqual(code, probe.EXPECTED_CURRENT_BYTES)
        self.assertEqual(public["segment_name"], "PROBE_TEXT")
        self.assertEqual(public["segment_class"], "CODE")
        self.assertEqual(public["offset"], 0)

    def test_public_code_bytes_rejects_non_code_segment(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not in a CODE segment"):
            probe.public_code_bytes(
                fixture(segment_class=b"DATA"),
                probe.PROBE_NAME,
                len(probe.EXPECTED_CURRENT_BYTES),
            )


if __name__ == "__main__":
    unittest.main()
