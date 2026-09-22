from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import status


class ReviewedAuthoredRowsTests(unittest.TestCase):
    def test_excluded_historical_authored_rows_do_not_enter_denominator(self) -> None:
        rows = [
            {"id": "exact", "origin": "authored", "boundary_state": "reviewed", "state": "exact"},
            {"id": "blocked", "origin": "authored", "boundary_state": "reviewed", "state": "blocked"},
            {"id": "candidate", "origin": "authored", "boundary_state": "shared", "state": "candidate"},
            {"id": "superseded", "origin": "authored", "boundary_state": "reviewed", "state": "excluded"},
            {"id": "unreviewed", "origin": "authored", "boundary_state": "provisional", "state": "candidate"},
            {"id": "compiler", "origin": "compiler", "boundary_state": "reviewed", "state": "exact"},
        ]
        self.assertEqual(
            [row["id"] for row in status.reviewed_authored_rows(rows)],
            ["exact", "blocked", "candidate"],
        )

    def test_packed_decoded_exact_is_not_a_file_byte_percentage(self) -> None:
        report = status.artifact_report(
            {"id": "th04-op", "size": 42290},
            [{
                "artifact": "th04-op", "state": "source-present", "size": "0x68",
                "origin": "authored", "boundary_state": "reviewed", "file_offset": "",
            }],
            [],
            [{
                "artifact": "th04-op", "work_queue": "reconstruct",
                "boundary_state": "reviewed", "accepted_state": "exact",
                "source_form": "hybrid-cpp-symbolic-lowlevel",
            }],
        )
        self.assertEqual(report["accepted_exact_authored_functions"], 1)
        self.assertEqual(report["decoded_only_source_owner_bytes"], 0x68)
        self.assertEqual(report["known_authored_bytes"], 0)
        self.assertIsNone(report["exact_authored_percent"])
        self.assertIsNone(report["reviewed_authored_functions"])

    def test_main_file_backed_extent_keeps_its_exact_percentage(self) -> None:
        report = status.artifact_report(
            {"id": "th04-main", "size": 156258},
            [{
                "artifact": "th04-main", "state": "exact", "size": "0x20",
                "origin": "authored", "boundary_state": "reviewed", "file_offset": "0x100",
            }],
            [{
                "artifact": "th04-main", "boundary_state": "reviewed", "state": "exact",
            }],
            [{
                "artifact": "th04-main", "work_queue": "reconstruct",
                "boundary_state": "reviewed", "accepted_state": "exact",
                "source_form": "candidate-cpp",
            }],
        )
        self.assertEqual(report["exact_authored_bytes"], 0x20)
        self.assertEqual(report["exact_authored_percent"], 100.0)
        self.assertEqual(report["exact_authored_functions"], 1)


if __name__ == "__main__":
    unittest.main()
