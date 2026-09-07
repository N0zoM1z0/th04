from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.toolchain import ToolchainError, file_set_identity, tree_identity
from attest_toolchain import gated_execution, probe_workspace_name, write_probe_inputs


class ToolchainIdentityTests(unittest.TestCase):
    def test_failed_identity_prevents_execution_probes(self) -> None:
        with patch("attest_toolchain.run_execution_probes") as probes:
            execution, passed = gated_execution(
                {}, identity_pass=False, identity_only=False
            )
        probes.assert_not_called()
        self.assertFalse(passed)
        self.assertTrue(execution["skipped"])


    def test_probe_workspace_name_is_process_unique_and_83_safe(self) -> None:
        first = probe_workspace_name(0x12345)
        second = probe_workspace_name(0x12346)
        self.assertEqual(len(first), 8)
        self.assertRegex(first, r"^[A-Z0-9]{8}$")
        self.assertNotEqual(first, second)

    def test_probe_link_response_uses_unique_dos_workspace(self) -> None:
        with TemporaryDirectory() as temporary:
            work = Path(temporary) / "T4ABCDEF"
            write_probe_inputs(work, r"C:\T4ABCDEF")
            response = (work / "LINK.RSP").read_text(encoding="ascii")
            self.assertIn(r"C:\T4ABCDEF\cprobe.obj", response)
            self.assertNotIn("TH04PROBE", response)

    def test_tree_identity_is_path_and_content_sensitive(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "sub").mkdir()
            (root / "a.bin").write_bytes(b"A")
            (root / "sub" / "b.bin").write_bytes(b"BC")
            first = tree_identity(root)
            second = tree_identity(root)
            self.assertEqual(first, second)
            self.assertEqual(first.file_count, 2)
            self.assertEqual(first.total_size, 3)
            (root / "sub" / "b.bin").write_bytes(b"BD")
            self.assertNotEqual(first.sha256, tree_identity(root).sha256)

    def test_empty_tree_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ToolchainError, "empty"):
                tree_identity(Path(temporary))

    def test_selected_file_identity_excludes_other_files(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            selected = root / "selected.obj"
            selected.write_bytes(b"OMF")
            ignored = root / "ignored.map"
            ignored.write_bytes(b"first")
            first = file_set_identity(root, [selected])
            ignored.write_bytes(b"second")
            second = file_set_identity(root, [selected])
            self.assertEqual(first, second)
            self.assertEqual(first.file_count, 1)

            transformed = file_set_identity(
                root,
                [selected],
                digest_function=lambda path: hashlib.sha256(b"normalized").hexdigest(),
            )
            self.assertNotEqual(first.sha256, transformed.sha256)

    def test_selected_file_identity_rejects_duplicates(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            selected = root / "selected.obj"
            selected.write_bytes(b"OMF")
            with self.assertRaisesRegex(ToolchainError, "duplicate"):
                file_set_identity(root, [selected, selected])

    def test_selected_file_identity_rejects_lexical_escape(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "root"
            root.mkdir()
            outside = root / ".." / "outside.obj"
            outside.write_bytes(b"OMF")
            with self.assertRaisesRegex(ToolchainError, "escapes"):
                file_set_identity(root, [outside])

    def test_symlink_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "real").write_bytes(b"x")
            (root / "alias").symlink_to("real")
            with self.assertRaisesRegex(ToolchainError, "symlink"):
                tree_identity(root)

    def test_symlink_tree_root_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            container = Path(temporary)
            root = container / "real"
            root.mkdir()
            (root / "file").write_bytes(b"x")
            alias = container / "alias"
            alias.symlink_to(root)
            with self.assertRaisesRegex(ToolchainError, "tree root"):
                tree_identity(alias)


if __name__ == "__main__":
    unittest.main()
