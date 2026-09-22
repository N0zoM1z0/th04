from __future__ import annotations

from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import progress


class ProgressPresentationTests(unittest.TestCase):
    def test_svg_names_all_four_artifacts_and_separates_byte_plane(self) -> None:
        svg = progress.render_svg()
        ET.fromstring(svg)
        for name in ("OP.EXE", "MAIN.EXE", "MAINE.EXE", "ZUN.COM"):
            self.assertIn(name, svg)
        self.assertIn("Function acceptance", svg)
        self.assertIn("MAIN file-backed authored bytes only", svg)
        self.assertIn("packed-file byte denominator: n/a", svg)

    def test_markdown_avoids_a_global_exact_byte_percentage(self) -> None:
        page = progress.render()
        self.assertIn("## All-artifact function routing", page)
        self.assertIn("## MAIN.EXE file-backed acceptance", page)
        self.assertNotIn("Exact / currently confirmed authored bytes", page)


if __name__ == "__main__":
    unittest.main()
