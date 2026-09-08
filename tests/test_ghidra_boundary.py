from __future__ import annotations

import csv
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from boundary_review.export_ghidra_inventory import (
    AnalysisError,
    FUNCTION_HEADER,
    attest_export,
)


class BoundaryInventoryAttestationTests(unittest.TestCase):
    def write_export(self, root: Path, *, nonce: str = "1" * 32) -> None:
        (root / "inventory.properties").write_text(
            "schema_version=1\n"
            f"export_nonce={nonce}\n"
            "executable_sha256=" + "2" * 64 + "\n"
            "language_id=x86:LE:16:Real Mode\n"
            "headless_analysis_timed_out=false\n"
            "function_count=1\n",
            encoding="utf-8",
        )
        with (root / "functions.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=FUNCTION_HEADER, lineterminator="\n")
            writer.writeheader()
            row = {field: "" for field in FUNCTION_HEADER}
            row.update({"index": "0", "entry_linear": "0x10000"})
            writer.writerow(row)

    def test_accepts_bound_export(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_export(root)
            self.assertEqual(attest_export(root, "2" * 64, "1" * 32), 1)

    def test_rejects_stale_nonce(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_export(root)
            with self.assertRaisesRegex(AnalysisError, "nonce"):
                attest_export(root, "2" * 64, "3" * 32)


if __name__ == "__main__":
    unittest.main()
