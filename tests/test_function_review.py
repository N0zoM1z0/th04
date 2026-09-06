from __future__ import annotations

import csv
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import review_th04_main_functions as review


class ManualFunctionReviewTests(unittest.TestCase):
    def fixture(self, root: Path, jump_word: int) -> tuple[Path, Path, list[dict[str, object]], dict[int, dict[str, str]]]:
        policy = root / "policy.toml"
        policy.write_text(
            """schema_version = 1

[[reviewed_exact]]
id = "fn"
address = "0x10000"
file_offset = "0x1800"
size = "0x2"
name = "fixture"
owner_unit = "owner"
evidence_id = "ev-fixture"
reason = "synthetic switch-boundary review"
jump_table_address = "0x10002"
jump_table_count = 1
cs_base = "0x10000"
""",
            encoding="utf-8",
        )
        target = root / "target.bin"
        data = bytearray(0x1804)
        data[0x1800:0x1802] = b"\x90\xC3"
        data[0x1802:0x1804] = jump_word.to_bytes(2, "little")
        target.write_bytes(data)
        items = [
            {
                "address": 0x10000,
                "address_hex": "0x10000",
                "ghidra_name": "FUN_10000",
                "public": "fixture",
                "owner_unit": "owner",
                "owner_start": 0x10000,
                "owner_end": 0x10010,
                "source": "src/fixture.cpp",
                "owner_name": "fixture.cpp",
            }
        ]
        metadata = {
            0x10000: {
                "address": "0x10000",
                "body_min": "0x10000",
                "body_max": "0x10001",
                "body_addresses": "1",
            }
        }
        return policy, target, items, metadata

    @staticmethod
    def decoded() -> dict[str, object]:
        return {
            "instruction_count": 2,
            "instruction_addresses": [0x10000, 0x10001],
            "terminal": "ret",
            "first_address": "0x10000",
            "end_address_exclusive": "0x10002",
        }

    def test_manual_switch_review_accepts_instruction_aligned_targets(self) -> None:
        with TemporaryDirectory() as temporary:
            policy, target, items, metadata = self.fixture(Path(temporary), 0)
            with patch.object(review, "POLICY", policy), patch.object(
                review, "linear_decode", return_value=self.decoded()
            ):
                accepted = review.manual_reviews(items, metadata, target)
            self.assertEqual(len(accepted), 1)
            switch = accepted[0]["switch_review"]
            self.assertIsInstance(switch, dict)
            assert isinstance(switch, dict)
            self.assertTrue(switch["all_targets_are_instruction_starts"])
            self.assertEqual(switch["jump_targets"], ["0x10000"])

    def test_manual_switch_review_rejects_non_instruction_target(self) -> None:
        with TemporaryDirectory() as temporary:
            policy, target, items, metadata = self.fixture(Path(temporary), 5)
            with patch.object(review, "POLICY", policy), patch.object(
                review, "linear_decode", return_value=self.decoded()
            ):
                with self.assertRaisesRegex(ValueError, "non-instruction starts"):
                    review.manual_reviews(items, metadata, target)

    def test_automatic_review_promotes_blocked_row(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = [
                "id", "artifact", "address", "file_offset", "size",
                "boundary_state", "state", "name", "owner_unit", "source",
                "evidence_ids", "notes",
            ]
            row = {key: "" for key in header}
            row.update({
                "id": "fn-100", "artifact": "th04-main", "address": "0x100",
                "file_offset": "0x200", "size": "0x4",
                "boundary_state": "reviewed", "state": "blocked",
                "name": "fixture", "evidence_ids": "ev-boundary",
            })
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=header)
                writer.writeheader()
                writer.writerow(row)
            out = root / "out.csv"
            old_root = review.ROOT
            review.ROOT = root
            try:
                review.write_reviewed_ledger(
                    out,
                    [{
                        "address": 0x100,
                        "owner_unit": "owner-exact",
                        "source": "src/unit.c",
                    }],
                    [],
                )
            finally:
                review.ROOT = old_root
            with out.open(newline="", encoding="utf-8") as stream:
                promoted = next(csv.DictReader(stream))
            self.assertEqual(promoted["state"], "exact")
            self.assertEqual(promoted["owner_unit"], "owner-exact")
            self.assertEqual(promoted["source"], "src/unit.c")


if __name__ == "__main__":
    unittest.main()
