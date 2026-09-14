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


if __name__ == "__main__":
    unittest.main()
