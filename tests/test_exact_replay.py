from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import replay_th04_main_exact_units as replay


class Rec98CompatTests(unittest.TestCase):
    def test_forwarding_layer_is_materialized_and_attested(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            compat = root / "compat" / "rec98"
            source = root / "source"
            header = compat / "th02" / "hardware" / "frmdelay.h"
            header.parent.mkdir(parents=True)
            header.write_text('#include "th02/hardware/frmdelay.h"\n', encoding="utf-8")
            source.mkdir()
            with patch.object(replay, "REC98_COMPAT", compat):
                receipt = replay.materialize_rec98_compat(source)
            copied = source / "compat" / "rec98" / "th02" / "hardware" / "frmdelay.h"
            self.assertEqual(copied.read_bytes(), header.read_bytes())
            self.assertEqual(receipt[0]["path"], "th02/hardware/frmdelay.h")
            self.assertEqual(receipt[0]["sha256"], replay.digest_file(header))

    def test_forwarded_fragment_resolves_only_one_line_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            compat = Path(temporary) / "compat"
            header = compat / "th02" / "hardware" / "frmdelay.h"
            header.parent.mkdir(parents=True)
            header.write_text('#include "th02/hardware/frmdelay.h"\n', encoding="utf-8")
            source = b'#include "compat/rec98/th02/hardware/frmdelay.h"\nbody\n'
            with patch.object(replay, "REC98_COMPAT", compat):
                resolved, used = replay.resolve_rec98_forwarders(source)
            self.assertEqual(resolved, b'#include "th02/hardware/frmdelay.h"\nbody\n')
            self.assertEqual(used, ["th02/hardware/frmdelay.h"])


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


class SourceReplacementTests(unittest.TestCase):
    def test_source_replacement_is_hash_and_offset_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            source = root / "source"
            repo.mkdir()
            source.mkdir()
            replacement = repo / "replacement.cpp"
            replacement.write_text("natural();\n", encoding="utf-8")
            scaffold = source / "impl.cpp"
            original = b"head\nlowlevel();\ntail\n"
            scaffold.write_bytes(original)
            match = b"lowlevel();\n"
            entry = {
                "id": "unit-replace",
                "repo_source": "replacement.cpp",
                "source_mode": "replace",
                "patch_path": "impl.cpp",
                "scaffold_sha256": replay.digest_bytes(original),
                "replace_offset": original.index(match),
                "replace_size": len(match),
                "replace_sha256": replay.digest_bytes(match),
            }
            with patch.object(replay, "ROOT", repo):
                receipt = replay.overlay_sources(source, [entry])
            self.assertEqual(scaffold.read_text(encoding="utf-8"), "head\nnatural();\ntail\n")
            self.assertEqual(receipt[0]["mode"], "replace")
            self.assertEqual(receipt[0]["replace_offset"], original.index(match))
            self.assertEqual(receipt[0]["replacement_sha256"], replay.digest_file(replacement))

    def test_source_replacement_rejects_span_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            source = root / "source"
            repo.mkdir()
            source.mkdir()
            (repo / "replacement.cpp").write_text("natural();\n", encoding="utf-8")
            original = b"head\nlowlevel();\ntail\n"
            (source / "impl.cpp").write_bytes(original)
            match = b"lowlevel();\n"
            entry = {
                "id": "unit-replace",
                "repo_source": "replacement.cpp",
                "source_mode": "replace",
                "patch_path": "impl.cpp",
                "scaffold_sha256": replay.digest_bytes(original),
                "replace_offset": original.index(match),
                "replace_size": len(match),
                "replace_sha256": replay.digest_bytes(b"different();\n"),
            }
            with patch.object(replay, "ROOT", repo):
                with self.assertRaisesRegex(RuntimeError, "source span SHA-256 mismatch"):
                    replay.overlay_sources(source, [entry])

    def test_source_replacement_rejects_scaffold_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            source = root / "source"
            repo.mkdir()
            source.mkdir()
            (repo / "replacement.cpp").write_text("natural();\n", encoding="utf-8")
            (source / "impl.cpp").write_text("changed();\n", encoding="utf-8")
            entry = {
                "id": "unit-replace",
                "repo_source": "replacement.cpp",
                "source_mode": "replace",
                "patch_path": "impl.cpp",
                "scaffold_sha256": replay.digest_bytes(b"original();\n"),
                "replace_offset": 0,
                "replace_size": len(b"original();\n"),
                "replace_sha256": replay.digest_bytes(b"original();\n"),
            }
            with patch.object(replay, "ROOT", repo):
                with self.assertRaisesRegex(RuntimeError, "scaffold SHA-256 drift"):
                    replay.overlay_sources(source, [entry])


if __name__ == "__main__":
    unittest.main()
