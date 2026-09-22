from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from boundary_review.validate_function_boundary_ledger import (
    ValidationError,
    validate_reviewed_overrides,
)


class ReviewedOverrideEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [{
            "id": "th04-zun-boundary-006f6",
            "artifact": "th04-zun",
            "payload_offset": "0x6F6",
            "body_size": "0x12",
            "body_span": "0x12",
            "boundary_state": "reviewed",
        }]
        self.rules = {
            ("th04-zun", 0x6F6): {
                "reviewed_body_size": 0x12,
                "review_evidence_id": "ev-review",
            }
        }
        self.evidence = {
            "ev-review": {
                "artifact": "th04-zun",
                "oracle": "boundary-ownership",
                "result": "pass",
                "evidence_class": "target-analysis",
                "extent_start": "0x6F3",
                "extent_size": "0x475",
            }
        }

    def test_accepts_covering_target_boundary_evidence(self) -> None:
        validate_reviewed_overrides(self.rows, self.rules, self.evidence)

    def test_rejects_missing_review_evidence(self) -> None:
        with self.assertRaises(ValidationError):
            validate_reviewed_overrides(self.rows, self.rules, {})

    def test_rejects_wrong_evidence_authority(self) -> None:
        for field, value in (
            ("artifact", "th04-op"),
            ("oracle", "raw-bytes"),
            ("result", "fail"),
            ("evidence_class", "upstream"),
        ):
            evidence = deepcopy(self.evidence)
            evidence["ev-review"][field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    validate_reviewed_overrides(self.rows, self.rules, evidence)

    def test_rejects_evidence_extent_that_does_not_cover_function(self) -> None:
        evidence = deepcopy(self.evidence)
        evidence["ev-review"]["extent_start"] = "0x700"
        evidence["ev-review"]["extent_size"] = "0x10"
        with self.assertRaises(ValidationError):
            validate_reviewed_overrides(self.rows, self.rules, evidence)

    def test_rejects_ledger_projection_drift(self) -> None:
        rows = deepcopy(self.rows)
        rows[0]["body_size"] = "0x11"
        with self.assertRaises(ValidationError):
            validate_reviewed_overrides(rows, self.rules, self.evidence)


if __name__ == "__main__":
    unittest.main()
