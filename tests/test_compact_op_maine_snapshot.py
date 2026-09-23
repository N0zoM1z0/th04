from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/probes"))

from compact_op_maine_snapshot import copy_compact_snapshot


class CompactSnapshotTests(unittest.TestCase):
    def make_snapshot(self, root: Path) -> Path:
        snapshot = root / "snapshot"
        for name in ("th04", "th01", "obj/th04", "obj/th01", "bin/th04", ".tup"):
            (snapshot / name).mkdir(parents=True)
        (snapshot / "th04/scall.cpp").write_bytes(b"source")
        (snapshot / "th01/vplanset.cpp").write_bytes(b"shared")
        (snapshot / "obj/th04/scall.obj").write_bytes(b"score-object")
        (snapshot / "obj/th01/vplanset.obj").write_bytes(b"vram-object")
        (snapshot / "obj/th04/op.map").write_bytes(b"map")
        (snapshot / "obj/th04/op.@l").write_bytes(
            b"-c c0l.obj obj\\th04\\scall.obj obj\\th01\\vplanset.obj, "
            b"bin\\th04\\op.exe, obj\\th04\\op.map, emu.lib\r\n"
        )
        (snapshot / "bin/th04/op.exe").write_bytes(b"exe")
        (snapshot / "bin/masters.lib").write_bytes(b"master")
        (snapshot / "c0l.obj").write_bytes(b"startup")
        (snapshot / "emu.lib").write_bytes(b"library")
        (snapshot / "unused.lst").write_bytes(b"large-generated-listing")
        (snapshot / ".tup/cache").write_bytes(b"cache")
        return snapshot

    def test_copies_only_link_inputs_and_independent_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            snapshot = self.make_snapshot(root)
            work = root / "work"
            copy_compact_snapshot(snapshot, work, "op")
            self.assertEqual((work / "obj/th04/scall.obj").read_bytes(), b"score-object")
            self.assertEqual((work / "obj/th01/vplanset.obj").read_bytes(), b"vram-object")
            self.assertTrue((work / "bin/th04/op.exe").is_file())
            self.assertTrue((work / "bin/masters.lib").is_file())
            self.assertFalse((work / "unused.lst").exists())
            self.assertFalse((work / ".tup").exists())
            (work / "th04/scall.cpp").write_bytes(b"changed")
            self.assertEqual((snapshot / "th04/scall.cpp").read_bytes(), b"source")

    def test_missing_object_and_existing_destination_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            snapshot = self.make_snapshot(root)
            (snapshot / "obj/th01/vplanset.obj").unlink()
            with self.assertRaisesRegex(ValueError, "response object missing"):
                copy_compact_snapshot(snapshot, root / "work", "op")
            self.assertFalse((root / "work").exists())
            (root / "work").mkdir()
            with self.assertRaisesRegex(ValueError, "new worktree must not exist"):
                copy_compact_snapshot(snapshot, root / "work", "op")

    def test_nested_source_symlink_fails_before_creating_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            snapshot = self.make_snapshot(root)
            external = root / "external"
            external.write_bytes(b"private")
            (snapshot / "th04/alias.h").symlink_to(external)
            with self.assertRaisesRegex(ValueError, "snapshot symlink"):
                copy_compact_snapshot(snapshot, root / "work", "op")
            self.assertFalse((root / "work").exists())
            self.assertEqual(external.read_bytes(), b"private")


if __name__ == "__main__":
    unittest.main()
