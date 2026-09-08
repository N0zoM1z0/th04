from __future__ import annotations

from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from boundary_review.unpack_diet import (
    DietError,
    EmulationResult,
    RelocationObservation,
    normalize_payload,
    relocation_identity,
)


class DietNormalizationTests(unittest.TestCase):
    def test_reverses_observed_relocations_in_order(self) -> None:
        payload = bytearray(b"\x00" * 8)
        payload[1:3] = (0x3234).to_bytes(2, "little")
        relocations = (
            RelocationObservation(0, 0x2000, 1, 0, 1),
        )
        normalized = normalize_payload(bytes(payload), relocations, 0x2000)
        self.assertEqual(normalized[1:3], (0x1234).to_bytes(2, "little"))

    def test_duplicate_relocations_are_reversed_individually(self) -> None:
        payload = bytearray(b"\x00" * 4)
        payload[0:2] = (0x4100).to_bytes(2, "little")
        relocations = (
            RelocationObservation(0, 0x2000, 0, 0, 0),
            RelocationObservation(1, 0x2000, 0, 0, 0),
        )
        normalized = normalize_payload(bytes(payload), relocations, 0x2000)
        self.assertEqual(normalized[0:2], (0x0100).to_bytes(2, "little"))

    def test_out_of_range_relocation_fails_closed(self) -> None:
        with self.assertRaisesRegex(DietError, "escapes payload"):
            normalize_payload(
                b"\x00\x00",
                (RelocationObservation(0, 0x1000, 2, 0, 2),),
                0x1000,
            )

    def test_identity_excludes_absolute_load_address(self) -> None:
        one = EmulationResult(
            0x1000, b"", (RelocationObservation(0, 0x1010, 2, 0x10, 0x102),),
            0x1000, 0, 0, 0, 1, 1,
        )
        two = EmulationResult(
            0x2000, b"", (RelocationObservation(0, 0x2010, 2, 0x10, 0x102),),
            0x2000, 0, 0, 0, 1, 1,
        )
        self.assertEqual(relocation_identity(one), relocation_identity(two))


if __name__ == "__main__":
    unittest.main()
