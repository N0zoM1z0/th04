from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import sys
from tempfile import TemporaryDirectory
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.ghidra import GhidraError, attest_mz_export, parse_properties, parse_segmented_address
from lib.pc98 import parse_mz


def synthetic_mz() -> bytes:
    header = bytearray(32)
    struct.pack_into(
        "<14H",
        header,
        0,
        0x5A4D,
        48,
        1,
        1,
        2,
        0x1000,
        0xFFFF,
        0,
        0xFFFE,
        0,
        0,
        0,
        28,
        0,
    )
    struct.pack_into("<HH", header, 28, 2, 0)
    program = bytearray(range(16))
    struct.pack_into("<H", program, 2, 0x1234)
    return bytes(header + program)


def write_export(root: Path, target: bytes) -> tuple[dict[str, object], dict[str, object]]:
    image = parse_mz(target)
    relocated = image.relocated_program_image(0x1000)
    modified = target[: image.header.header_size] + relocated
    artifact = {
        "id": "synthetic",
        "private_path": ".analysis/targets/th04/main.exe",
        "sha256": hashlib.sha256(target).hexdigest(),
    }
    config = {
        "mz_loader": {
            "name": "Old-style DOS Executable (MZ)",
            "language_id": "x86:LE:16:Real Mode",
            "compiler_spec_id": "default",
            "load_segment": 0x1000,
            "header_address_space": "HEADER",
        }
    }
    properties = {
        "schema_version": "1",
        "export_nonce": "0" * 32,
        "program_name": "main.exe",
        "executable_path": "/private/main.exe",
        "executable_sha256": artifact["sha256"],
        "executable_format": config["mz_loader"]["name"],
        "language_id": config["mz_loader"]["language_id"],
        "compiler_spec_id": "default",
        "image_base": "0000:0000",
        "default_address_space": "ram",
        "filebytes_filename": "main.exe",
        "filebytes_size": str(len(target)),
        "filebytes_original_sha256": hashlib.sha256(target).hexdigest(),
        "filebytes_modified_sha256": hashlib.sha256(modified).hexdigest(),
        "header_memory_sha256": hashlib.sha256(target[:32]).hexdigest(),
        "load_memory_sha256": hashlib.sha256(relocated).hexdigest(),
        "header_size": "32",
        "declared_size": "48",
        "load_module_size": "16",
        "source_range_count": "2",
        "relocation_count": "1",
        "external_entry_point_count": "1",
        "function_count": "0",
        "instruction_count": "0",
        "defined_data_count": "2",
        "headless_analysis_timed_out": "false",
    }
    (root / "program.properties").write_text(
        "".join(f"{key}={value}\n" for key, value in properties.items()), encoding="utf-8"
    )
    (root / "blocks.csv").write_text(
        "block,initialized,loaded,file_offset,length,min_address,max_address,address_space,description\n"
        "HEADER,true,false,0,32,HEADER::00000000,HEADER::0000001f,HEADER,\n"
        "CODE_0,true,true,32,16,1000:0000,1000:000f,ram,\n",
        encoding="utf-8",
    )
    original = image.program_image[2:4]
    relocated_value = (struct.unpack("<H", original)[0] + 0x1000) & 0xFFFF
    (root / "relocations.csv").write_text(
        "index,address,address_segment,address_offset,status,type,values,original_bytes,memory_bytes\n"
        f"0,1000:0002,4096,2,APPLIED,0,0;2;{relocated_value},"
        f"{original.hex()},{struct.pack('<H', relocated_value).hex()}\n",
        encoding="utf-8",
    )
    (root / "entrypoints.txt").write_text("1000:0000\n", encoding="utf-8")
    (root / "filebytes-original.bin").write_bytes(target)
    (root / "filebytes-modified.bin").write_bytes(modified)
    (root / "header-memory.bin").write_bytes(target[:32])
    (root / "load-memory.bin").write_bytes(relocated)
    return artifact, config


class GhidraExportTests(unittest.TestCase):
    def test_synthetic_mz_export_passes_all_dimensions(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = synthetic_mz()
            artifact, config = write_export(root, target)
            report = attest_mz_export(
                root, target, artifact, config, expected_nonce="0" * 32
            )
            self.assertTrue(report["ready"])
            self.assertTrue(all(report["checks"].values()))

    def test_loaded_memory_mutation_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = synthetic_mz()
            artifact, config = write_export(root, target)
            loaded = bytearray((root / "load-memory.bin").read_bytes())
            loaded[-1] ^= 1
            (root / "load-memory.bin").write_bytes(loaded)
            report = attest_mz_export(root, target, artifact, config)
            self.assertFalse(report["ready"])
            self.assertFalse(report["checks"]["load_memory"])

    def test_extra_cross_category_mapping_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = synthetic_mz()
            artifact, config = write_export(root, target)
            blocks = root / "blocks.csv"
            with blocks.open("a", encoding="utf-8") as stream:
                stream.write("ALIAS,true,true,0,1,1000:0000,1000:0000,ram,\n")
            properties = root / "program.properties"
            properties.write_text(
                properties.read_text(encoding="utf-8").replace(
                    "source_range_count=2", "source_range_count=3"
                ),
                encoding="utf-8",
            )
            report = attest_mz_export(root, target, artifact, config)
            self.assertFalse(report["ready"])
            self.assertFalse(report["checks"]["mapping_partition"])

    def test_stale_export_nonce_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = synthetic_mz()
            artifact, config = write_export(root, target)
            report = attest_mz_export(
                root, target, artifact, config, expected_nonce="1" * 32
            )
            self.assertFalse(report["ready"])
            self.assertIn("export_nonce", report["diagnostics"]["property_mismatches"])

    def test_properties_reject_duplicates(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "program.properties"
            path.write_text("a=1\na=2\n", encoding="utf-8")
            with self.assertRaisesRegex(GhidraError, "duplicate"):
                parse_properties(path)

    def test_segmented_address_parser_is_strict(self) -> None:
        self.assertEqual(parse_segmented_address("1000:00af"), (0x1000, 0xAF))
        with self.assertRaises(GhidraError):
            parse_segmented_address("0x1000:0")


if __name__ == "__main__":
    unittest.main()
