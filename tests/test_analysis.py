from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import tomllib
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.analysis import (
    AnalysisError,
    default_project_root,
    link_aware_tree_identity,
    validate_project_root,
)


class AnalysisPathTests(unittest.TestCase):
    def test_manifest_and_bootstrap_keep_tools_under_dot_tools(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        with (repository / "config" / "analysis_toolchain.toml").open("rb") as stream:
            config = tomllib.load(stream)
        bootstrap = (repository / "scripts" / "bootstrap_analysis_toolchain.sh").read_text(
            encoding="utf-8"
        )
        for section in (config["ghidra"], config["temurin_jdk"]):
            self.assertTrue(section["archive_path"].startswith(".tools/"))
            self.assertTrue(section["install_path"].startswith(".tools/"))
            self.assertTrue(section["stable_path"].startswith(".tools/"))
            for key in ("asset", "url", "archive_sha256"):
                self.assertIn(str(section[key]), bootstrap)

    def test_default_project_matches_ignored_th095_style_layout(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "th04"
            root.mkdir()
            config = {"private_paths": {"project_root": "ghidra-project"}}
            self.assertEqual(default_project_root(root, config), root / "ghidra-project")
            self.assertEqual(
                validate_project_root(root, root / "ghidra-project"),
                (root / "ghidra-project").resolve(),
            )

    def test_other_repository_internal_project_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "th04"
            root.mkdir()
            with self.assertRaisesRegex(AnalysisError, "only allowed"):
                validate_project_root(root, root / "private-project")

    def test_dot_prefixed_project_component_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "th04"
            root.mkdir()
            with self.assertRaisesRegex(AnalysisError, "dot-prefixed"):
                validate_project_root(root, root / ".analysis" / "ghidra")


class LinkAwareTreeTests(unittest.TestCase):
    def test_internal_symlink_topology_is_stable_and_sensitive(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "lib").mkdir()
            (root / "lib" / "real").write_bytes(b"jdk")
            (root / "lib" / "other").write_bytes(b"jdk")
            (root / "bin").mkdir()
            (root / "bin" / "alias").symlink_to("../lib/real")
            first = link_aware_tree_identity(root)
            second = link_aware_tree_identity(root)
            self.assertEqual(first, second)
            self.assertEqual(first.file_count, 2)
            self.assertEqual(first.symlink_count, 1)
            (root / "bin" / "alias").unlink()
            (root / "bin" / "alias").symlink_to("../lib/other")
            self.assertNotEqual(first.sha256, link_aware_tree_identity(root).sha256)

    def test_external_symlink_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            container = Path(temporary)
            root = container / "tree"
            root.mkdir()
            outside = container / "outside"
            outside.write_bytes(b"x")
            (root / "escape").symlink_to(outside)
            with self.assertRaisesRegex(AnalysisError, "escapes"):
                link_aware_tree_identity(root)


if __name__ == "__main__":
    unittest.main()
