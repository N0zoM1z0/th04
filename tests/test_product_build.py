import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "th04_product_build", Path(__file__).resolve().parents[1] / "scripts/build.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prepare_product_hdi as IMAGE


class ProductBuildTests(unittest.TestCase):
    def test_single_product_rebuild_keeps_verified_other_products(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "products"
            output.mkdir()
            op = b"previous OP executable"
            (output / "OP.EXE").write_bytes(op)
            (output / "MAINE.EXE").write_bytes(b"unverified modified MAINE")
            (output / "build.json").write_text(json.dumps({"products": {
                "op": {"file": "OP.EXE", "size": len(op),
                       "sha256": hashlib.sha256(op).hexdigest()},
                "maine": {"file": "MAINE.EXE", "size": 1, "sha256": "stale"},
            }}))
            candidate = root / "candidate.exe"
            candidate.write_bytes(b"new MAIN")
            with patch.object(BUILD, "ROOT", root), \
                    patch.object(BUILD, "PROBES", root / "probes"), \
                    patch.object(BUILD, "build_product", return_value=candidate), \
                    patch.object(sys, "argv", ["build.py", "--only", "main",
                                               "--output-dir", str(output)]):
                self.assertEqual(BUILD.main(), 0)
            products = json.loads((output / "build.json").read_text())["products"]
            self.assertEqual(set(products), {"main", "op"})
            self.assertEqual((output / "OP.EXE").read_bytes(), op)

    def test_successful_probe_process_does_not_hide_link_failure(self):
        # Frontier probes intentionally return zero even for unresolved symbols.
        with patch.object(BUILD, "invoke", return_value={"link_complete": False}):
            with self.assertRaisesRegex(RuntimeError, "OP.EXE failed"):
                BUILD.build_product("op", Path("unused"), None)

    def test_failed_second_product_preserves_previously_published_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old_output = root / "products"
            old_output.mkdir()
            (old_output / "MAIN.EXE").write_bytes(b"previous executable")
            (old_output / "build.json").write_bytes(b"previous receipt")
            candidate = root / "candidate.exe"
            candidate.write_bytes(b"new main")
            with patch.object(BUILD, "ROOT", root), \
                    patch.object(BUILD, "PROBES", root / "probes"), \
                    patch.object(BUILD, "build_product", side_effect=[candidate, RuntimeError("OP link failed")]), \
                    patch.object(sys, "argv", ["build.py", "--only", "main", "op",
                                               "--output-dir", str(old_output)]):
                with self.assertRaisesRegex(RuntimeError, "OP link failed"):
                    BUILD.main()
            self.assertEqual((old_output / "MAIN.EXE").read_bytes(), b"previous executable")
            self.assertEqual((old_output / "build.json").read_bytes(), b"previous receipt")

    def test_product_image_growth_and_shrink_preserve_other_files_and_fat_mirrors(self):
        # A fragmented original chain must grow around an occupied neighbor,
        # then release its excess clusters when a smaller product replaces it.
        partition = 0x9800
        image = bytearray(partition + 20706 * 1024)
        for offset, value in [(11, 1024), (14, 1), (17, 1536), (19, 20706), (22, 4)]:
            image[partition + offset:partition + offset + 2] = value.to_bytes(2, "little")
        image[partition + 13] = 8
        image[partition + 16] = 2
        fs = IMAGE.Fat12(image)
        fs.set_fat(2, 0xFFF)
        fs.set_fat(3, 0xFFF)
        image[fs.root + 26:fs.root + 28] = (2).to_bytes(2, "little")
        neighbor = b"unrelated original data"
        offset = fs.cluster_offset(3)
        image[offset:offset + len(neighbor)] = neighbor
        large = b"rebuilt executable" * 1000
        IMAGE.replace_file(fs, fs.root, large)
        readback = IMAGE.Fat12(image)  # Also validates the two complete FAT mirrors.
        self.assertEqual(readback.file_bytes(2, len(large)), large)
        self.assertEqual(readback.chain(2), [2, 4, 5])
        IMAGE.replace_file(fs, fs.root, b"small product")
        readback = IMAGE.Fat12(image)
        self.assertEqual(readback.chain(2), [2])
        self.assertEqual(readback.fat(4), 0)
        self.assertEqual(readback.fat(5), 0)
        self.assertEqual(readback.file_bytes(3, len(neighbor)), neighbor)


if __name__ == "__main__":
    unittest.main()
