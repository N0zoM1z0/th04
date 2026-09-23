from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/probes"))

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402


class CompactSnapshotTests(unittest.TestCase):
    def test_materializes_compile_inputs_and_only_linked_objects(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            work = root / "work"
            files = {
                "obj/th04/op.@l": b"obj\\th04\\input.obj\n",
                "obj/th04/input.obj": b"linked-object",
                "obj/th04/op.map": b"link-map",
                "obj/th04/unused.obj": b"unneeded-object",
                "bin/th04/op.exe": b"candidate-exe",
                "bin/th04/op.map": b"candidate-map",
                "bin/libc.lib": b"toolchain-library",
                "th04/input.cpp": b"compile-root",
                "th04/include/input.hpp": b"header",
                "th04/include/table.csp": b"included-table",
                "th05/other.cpp": b"other-compile-root",
                "th05/large.lst": b"unneeded listing",
                "th05/asset.bmp": b"unneeded asset",
                "th05/manual.asm": b"unused assembler source",
                "README.md": b"unneeded documentation",
                ".tup/metadata": b"unneeded build metadata",
            }
            for relative, contents in files.items():
                path = snapshot / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(contents)

            copied = copy_compact_snapshot(snapshot, work, "op")

            self.assertEqual(copied["source_file_count"], 4)
            self.assertEqual(copied["source_bytes"], sum(
                len(files[path]) for path in (
                    "th04/input.cpp", "th04/include/input.hpp", "th04/include/table.csp",
                    "th05/other.cpp",
                )
            ))
            self.assertEqual(copied["linked_object_count"], 1)
            self.assertEqual(copied["linked_object_bytes"], len(files["obj/th04/input.obj"]))
            self.assertTrue((work / "th04/input.cpp").is_file())
            self.assertTrue((work / "th05/other.cpp").is_file())
            self.assertTrue((work / "obj/th04/input.obj").is_file())
            self.assertTrue((work / "bin/th04/op.exe").is_file())
            self.assertTrue((work / "bin/th04/op.map").is_file())
            self.assertTrue((work / "bin/libc.lib").is_file())
            self.assertFalse((work / "obj/th04/unused.obj").exists())
            self.assertFalse((work / "th05/large.lst").exists())
            self.assertFalse((work / "th05/asset.bmp").exists())
            self.assertFalse((work / "th05/manual.asm").exists())
            self.assertFalse((work / "README.md").exists())
            self.assertFalse((work / ".tup").exists())


if __name__ == "__main__":
    unittest.main()
