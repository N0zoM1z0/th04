from __future__ import annotations

import struct
import sys
from pathlib import Path
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from lib.pc98 import compare_blobs, parse_fat_boot_sector, parse_mz
from lib.reconstruction import comparison_vector
from lib.targets import TargetError
from export_analysis_bundle import private_output
from mine_shared_blocks import find_shared_blocks
from validate_tracking import accepted_oracle_passes


def synthetic_mz() -> bytes:
    header_size = 32
    program = bytearray(range(64))
    program[2:4] = b"\x34\x12"
    physical_size = header_size + len(program)
    pages, remainder = divmod(physical_size, 512)
    if remainder:
        pages += 1
    header = struct.pack(
        "<14H",
        0x5A4D,
        remainder,
        pages,
        1,
        header_size // 16,
        0,
        0xFFFF,
        0,
        0x100,
        0,
        0,
        0,
        28,
        0,
    )
    relocation = struct.pack("<HH", 2, 0)
    return header + relocation + bytes(program)


def synthetic_mz_with_relocations(
    relocations: tuple[tuple[int, int], ...]
) -> bytes:
    header_size = 16 * ((28 + 4 * len(relocations) + 15) // 16)
    program = bytes(range(64))
    physical_size = header_size + len(program)
    pages, remainder = divmod(physical_size, 512)
    if remainder:
        pages += 1
    header = struct.pack(
        "<14H",
        0x5A4D,
        remainder,
        pages,
        len(relocations),
        header_size // 16,
        0,
        0xFFFF,
        0,
        0x100,
        0,
        0,
        0,
        28,
        0,
    )
    table = b"".join(struct.pack("<HH", *item) for item in relocations)
    return header + table + bytes(header_size - len(header) - len(table)) + program


class MZTests(unittest.TestCase):
    def test_parse_and_self_compare(self) -> None:
        data = synthetic_mz()
        image = parse_mz(data)
        self.assertTrue(image.valid, image.errors)
        self.assertEqual(image.header.header_size, 32)
        self.assertEqual(image.relocations[0].linear, 2)
        self.assertTrue(compare_blobs(data, data)["verdict"]["raw_exact"])

    def test_relocated_word_normalization_is_diagnostic(self) -> None:
        data = synthetic_mz()
        changed = bytearray(data)
        changed[32 + 2] ^= 1
        result = compare_blobs(data, bytes(changed))
        self.assertFalse(result["verdict"]["raw_exact"])
        self.assertFalse(result["mz"]["program_image"]["exact"])
        self.assertTrue(result["mz"]["relocation_normalized_program"]["exact"])
        self.assertFalse(result["mz"]["relocations"]["site_values"]["exact"])
        self.assertGreater(
            result["mz"]["program_difference_partition"]
            ["at_relocation_site_bytes"],
            0,
        )
        self.assertEqual(
            result["mz"]["program_difference_partition"]
            ["outside_relocation_site_bytes"],
            0,
        )
        self.assertIn("relocated-word-values-only", result["routing_hints"])

    def test_relocation_applies_the_load_segment_modulo_16_bits(self) -> None:
        image = parse_mz(synthetic_mz())
        relocated = image.relocated_program_image(0xF000)
        self.assertEqual(struct.unpack_from("<H", relocated, 2)[0], 0x0234)

    def test_relocation_set_does_not_hide_changed_multiplicity(self) -> None:
        left = synthetic_mz_with_relocations(((2, 0), (4, 0), (4, 0)))
        right = synthetic_mz_with_relocations(((2, 0), (4, 0), (2, 0)))
        result = compare_blobs(left, right)
        self.assertTrue(result["mz"]["relocations"]["set_exact"])
        self.assertFalse(result["mz"]["relocations"]["multiset_exact"])
        self.assertIn(
            "relocation-site-multiplicity-difference", result["routing_hints"]
        )

    def test_non_relocation_change_survives_normalization(self) -> None:
        data = synthetic_mz()
        changed = bytearray(data)
        changed[32 + 8] ^= 1
        result = compare_blobs(data, bytes(changed))
        self.assertFalse(result["mz"]["relocation_normalized_program"]["exact"])
        self.assertEqual(
            result["mz"]["program_difference_partition"]
            ["at_relocation_site_bytes"],
            0,
        )
        self.assertGreater(
            result["mz"]["program_difference_partition"]
            ["outside_relocation_site_bytes"],
            0,
        )

    def test_header_and_overlay_are_separate(self) -> None:
        data = synthetic_mz()
        changed_header = bytearray(data)
        changed_header[0x0A] ^= 1
        header_result = compare_blobs(data, bytes(changed_header))
        self.assertFalse(header_result["mz"]["header_fields"]["exact"])
        self.assertTrue(header_result["mz"]["program_image"]["exact"])
        overlay_result = compare_blobs(data, data + b"x")
        self.assertTrue(overlay_result["mz"]["program_image"]["exact"])
        self.assertFalse(overlay_result["mz"]["overlay"]["exact"])
        self.assertIn("overlay-only-difference", overlay_result["routing_hints"])

    def test_upstream_policy_view_cannot_promote_a_header_mismatch(self) -> None:
        data = synthetic_mz()
        changed_header = bytearray(data)
        changed_header[0x0A] ^= 1
        vector = comparison_vector(compare_blobs(data, bytes(changed_header)))
        self.assertTrue(vector["rec98_rule1_core_dimensions_pass"])
        self.assertFalse(vector["header_fields_exact"])
        self.assertFalse(vector["raw_exact"])
        self.assertEqual(vector["program_differing_bytes"], 0)
        self.assertEqual(vector["raw_size_delta"], 0)

    def test_truncated_mz_candidate_is_a_rejection_vector(self) -> None:
        vector = comparison_vector(compare_blobs(synthetic_mz(), b"MZ"))
        self.assertFalse(vector["raw_exact"])
        self.assertFalse(vector["format_integrity"])
        self.assertFalse(vector["rec98_rule1_core_dimensions_pass"])
        self.assertEqual(vector["routing_hints"], ["invalid-mz-structure"])

    def test_com_comparison(self) -> None:
        left = b"\x90\xCD\x20"
        right = b"\x90\x90\x20"
        result = compare_blobs(left, right)
        self.assertEqual(result["formats"]["left"], "com")
        self.assertFalse(result["com_image"]["exact"])
        self.assertEqual(result["com_image"]["difference_run_count"], 1)


class FatTests(unittest.TestCase):
    def test_pc98_fat12_bpb(self) -> None:
        image = bytearray(4096)
        offset = 512
        sector = memoryview(image)[offset : offset + 512]
        sector[0:3] = b"\xEB\x45\x90"
        sector[3:11] = b"NEC  6.2"
        struct.pack_into("<H", sector, 11, 1024)
        sector[13] = 1
        struct.pack_into("<H", sector, 14, 1)
        sector[16] = 2
        struct.pack_into("<H", sector, 17, 32)
        struct.pack_into("<H", sector, 19, 3)
        sector[21] = 0xF8
        struct.pack_into("<H", sector, 22, 1)
        struct.pack_into("<H", sector, 24, 17)
        struct.pack_into("<H", sector, 26, 4)
        sector[43:54] = b"TOUHOU     "
        sector[54:62] = b"FAT12   "
        parsed = parse_fat_boot_sector(bytes(image), offset)
        self.assertEqual(parsed.bytes_per_sector, 1024)
        self.assertEqual(parsed.volume_label, "TOUHOU")


class SharedBlockTests(unittest.TestCase):
    def test_finds_maximal_unaligned_verified_block(self) -> None:
        shared = bytes(range(80))
        left = b"left-prefix" + shared + b"left-suffix"
        right = b"R" * 13 + shared + b"right-suffix"
        matches = find_shared_blocks(left, right, minimum_length=64)
        self.assertIn((11, 13, 80), matches)

    def test_rejects_short_matches(self) -> None:
        shared = bytes(range(38))
        matches = find_shared_blocks(
            b"L" * 41 + shared,
            b"R" * 47 + shared,
            minimum_length=64,
        )
        self.assertEqual(matches, [])


class ControlPlaneTests(unittest.TestCase):
    def test_analysis_bundle_cannot_escape_private_tree(self) -> None:
        with self.assertRaises(TargetError):
            private_output(Path("README.md"))

    def test_upstream_and_wrong_class_cannot_satisfy_exact_oracle(self) -> None:
        evidence = {
            "upstream": {
                "oracle": "raw-bytes",
                "result": "pass",
                "evidence_class": "upstream",
            },
            "wrong-class": {
                "oracle": "raw-bytes",
                "result": "pass",
                "evidence_class": "control-plane",
            },
            "local-binary": {
                "oracle": "raw-bytes",
                "result": "pass",
                "evidence_class": "binary",
            },
        }
        oracles = {
            "raw-bytes": {"accepts_evidence_classes": ["binary"]},
        }
        self.assertEqual(
            accepted_oracle_passes(
                ["upstream", "wrong-class"],
                evidence,
                oracles,
                {"upstream", "cross-game", "external", "inference"},
            ),
            set(),
        )
        self.assertEqual(
            accepted_oracle_passes(
                ["local-binary"],
                evidence,
                oracles,
                {"upstream", "cross-game", "external", "inference"},
            ),
            {"raw-bytes"},
        )

    def test_exact_evidence_is_bound_to_the_unit_artifact(self) -> None:
        evidence = {
            "other-binary": {
                "oracle": "raw-bytes",
                "artifact": "th04-op",
                "result": "pass",
                "evidence_class": "binary",
            },
            "global-binary": {
                "oracle": "raw-bytes",
                "artifact": "",
                "result": "pass",
                "evidence_class": "binary",
            },
            "global-toolchain": {
                "oracle": "toolchain-identity",
                "artifact": "",
                "result": "pass",
                "evidence_class": "compiler",
            },
        }
        oracles = {
            "raw-bytes": {"accepts_evidence_classes": ["binary"]},
            "toolchain-identity": {"accepts_evidence_classes": ["compiler"]},
        }
        self.assertEqual(
            accepted_oracle_passes(
                list(evidence),
                evidence,
                oracles,
                set(),
                artifact="th04-main",
                global_evidence_oracles={"toolchain-identity"},
            ),
            {"toolchain-identity"},
        )


if __name__ == "__main__":
    unittest.main()
