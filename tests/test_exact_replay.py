from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import replay_th04_main_exact_units as replay


class SourceSplitTests(unittest.TestCase):
    def fixture(self, root: Path, *, suffix: bool = True) -> tuple[Path, dict[str, object]]:
        repo = root / "repo"
        source = root / "source"
        repo.mkdir()
        source.mkdir()
        (repo / "fragment.cpp").write_text("tail\n", encoding="utf-8")
        (repo / "wrapper.cpp").write_text('#include "tail.cpp"\n', encoding="utf-8")
        scaffold = source / "impl.cpp"
        scaffold.write_text("head\ntail\n" if suffix else "tail\nhead\n", encoding="utf-8")
        (source / "Tupfile.lua").write_text('"base.cpp",\n', encoding="utf-8")
        split: dict[str, object] = {
            "id": "fixture-split",
            "trigger_units": ["unit-a"],
            "scaffold_path": "impl.cpp",
            "repo_fragment": "fragment.cpp",
            "remove_mode": "suffix",
            "fragment_overlay_path": "tail.cpp",
            "repo_wrapper": "wrapper.cpp",
            "wrapper_overlay_path": "extra.cpp",
            "build_file": "Tupfile.lua",
            "build_anchor": '"base.cpp",\n',
            "build_insert": '"extra.cpp",\n',
        }
        return source, split

    def test_source_split_is_exact_and_build_ordered(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, split = self.fixture(root)
            with patch.object(replay, "ROOT", root / "repo"):
                receipts = replay.apply_source_splits(source, [split], {"unit-a"})
            self.assertEqual((source / "impl.cpp").read_text(encoding="utf-8"), "head\n")
            self.assertEqual((source / "tail.cpp").read_text(encoding="utf-8"), "tail\n")
            self.assertEqual(
                (source / "extra.cpp").read_text(encoding="utf-8"),
                '#include "tail.cpp"\n',
            )
            self.assertEqual(
                (source / "Tupfile.lua").read_text(encoding="utf-8"),
                '"base.cpp",\n"extra.cpp",\n',
            )
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["fragment_offset"], 5)
            self.assertEqual(receipts[0]["fragment_size"], 5)

    def test_source_split_rejects_non_suffix_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, split = self.fixture(root, suffix=False)
            with patch.object(replay, "ROOT", root / "repo"):
                with self.assertRaisesRegex(RuntimeError, "not the scaffold suffix"):
                    replay.apply_source_splits(source, [split], {"unit-a"})


if __name__ == "__main__":
    unittest.main()
