from __future__ import annotations

from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from boundary_review.prepare_analysis_images import BoundaryPreparationError, difference_runs


class DifferenceRunTests(unittest.TestCase):
    def test_groups_adjacent_differences(self) -> None:
        self.assertEqual(
            difference_runs(b"abcdefghi", b"aBCdefgHi"),
            [
                {
                    "payload_offset": "0x1", "size": 2,
                    "target_hex": "6263", "candidate_hex": "4243",
                },
                {
                    "payload_offset": "0x7", "size": 1,
                    "target_hex": "68", "candidate_hex": "48",
                },
            ],
        )

    def test_rejects_unequal_sizes(self) -> None:
        with self.assertRaisesRegex(BoundaryPreparationError, "equal-sized"):
            difference_runs(b"a", b"ab")


if __name__ == "__main__":
    unittest.main()
