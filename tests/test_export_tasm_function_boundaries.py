from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from boundary_review.export_tasm_function_boundaries import listing_procedures


class TasmListingBoundaryTests(unittest.TestCase):
    def test_uses_emitting_listing_column_and_tracks_segments(self) -> None:
        content = (
            "    10\t0000\t\t\t GAME_TEXT segment byte public 'CODE' use16\n"
            "    11\t0010\t\t\t first proc near\n"
            "1  9528\t\t\t\t false_macro proc near\n"
            "    12\t\t\t\t ; Already in the BAD segment?\n"
            "    13\t0020\t\t\t second proc far\n"
            "    14\t0024\t\t\t GAME_TEXT ends\n"
        )
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.lst"
            path.write_text(content, encoding="cp932")
            rows = listing_procedures(path, "_TEXT")
        self.assertEqual(
            [(row["name"], row["segment"], row["listing_offset"]) for row in rows],
            [("first", "GAME_TEXT", 0x10), ("second", "GAME_TEXT", 0x20)],
        )


if __name__ == "__main__":
    unittest.main()
