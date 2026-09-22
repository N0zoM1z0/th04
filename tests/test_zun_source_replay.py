from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "probes"))

from replay_th04_zun_source_only import SOURCES, source_closure


class ZunSourceClosureTests(unittest.TestCase):
    def test_current_local_headers_are_transitive_inputs(self) -> None:
        closure = source_closure(ROOT, tuple(SOURCES.values()))
        self.assertIn("src/shared/config/score.hpp", closure)
        self.assertEqual(len(closure), 7)

    def test_parent_path_include_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "src" / "probe.cpp"
            source.parent.mkdir()
            source.write_text('#include "src/../secret.hpp"\n', encoding="ascii")
            with self.assertRaisesRegex(ValueError, "unsafe local include"):
                source_closure(root, ("src/probe.cpp",))


if __name__ == "__main__":
    unittest.main()
