from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from boundary_review.build_function_boundary_ledger import (
    BoundaryLedgerError,
    Contribution,
    classify_module,
    function_row,
    map_contributions,
    parse_map,
    parse_function_overrides,
    transform_range,
)


class MapBoundaryTests(unittest.TestCase):
    MAP = """
Detailed map of segments

 0000:0000 0100 C=CODE   S=_TEXT          G=(none)  M=c0.ASM     ACBP=28
 0000:0100 0020 C=CODE   S=GAME_TEXT      G=DGROUP  M=th04/game.cpp ACBP=28
 0000:0120 0004 C=DATA   S=_DATA          G=DGROUP  M=th04/game.cpp ACBP=48

  Address         Publics by Value

 0000:00100 idle  _main
 0000:00120       data_value

Program entry point at 0000:00100
"""

    def write_map(self, root: Path) -> Path:
        path = root / "test.map"
        path.write_bytes(self.MAP.encode("cp932"))
        return path

    def test_parses_only_nonempty_code_contributions(self) -> None:
        with TemporaryDirectory() as temporary:
            contributions, publics = parse_map(self.write_map(Path(temporary)))
        self.assertEqual(len(contributions), 2)
        self.assertEqual(publics[0x100], ["_main"])
        self.assertEqual(publics[0x120], ["data_value"])

    def test_filters_data_publics_after_module_classification(self) -> None:
        with TemporaryDirectory() as temporary:
            contributions, publics = map_contributions(
                "th04-test", self.write_map(Path(temporary)), [], "test"
            )
        self.assertEqual(len(contributions), 2)
        self.assertEqual(publics, {0x100: ["_main"]})
        self.assertEqual(contributions[1].origin, "authored")
        self.assertEqual(contributions[1].source_form, "candidate-cpp")

    def test_applies_com_bias_and_region_start(self) -> None:
        self.assertEqual(transform_range(0, 0x367, 0x100, 0xB68), (0xB68, 0xDCF))
        self.assertIsNone(transform_range(0, 0x100, 0x100, 0xB68))

    def test_monolith_override_is_segment_scoped(self) -> None:
        rules = [
            {
                "artifact": "th04-main", "module": "th04_main.asm",
                "segment": "_TEXT", "origin": "library",
                "source_form": "master-library-aggregate",
            }
        ]
        self.assertEqual(
            classify_module("th04-main", "th04_main.asm", "_TEXT", rules)[:2],
            ("library", "master-library-aggregate"),
        )
        self.assertEqual(
            classify_module("th04-main", "th04_main.asm", "GAME_TEXT", rules)[:2],
            ("authored", "target-derived-asm"),
        )

    def test_function_override_is_exact_entry_scoped(self) -> None:
        rules = parse_function_overrides(
            {
                "function_overrides": [
                    {
                        "artifact": "th04-main",
                        "payload_offset": 0x3680,
                        "origin": "authored",
                        "source_form": "target-derived-asm",
                        "source_ref": "candidate:th04_main.asm",
                    }
                ]
            }
        )
        self.assertEqual(rules[("th04-main", 0x3680)]["origin"], "authored")
        self.assertNotIn(("th04-main", 0x367F), rules)

    def test_target_rejected_shared_tail_requires_ghidra_only_entry(self) -> None:
        override = {
            "artifact": "th04-zun", "payload_offset": 0x517,
            "origin": "library", "source_form": "maintained-asm",
            "source_ref": "src/zun/ongchk/ongchk.asm",
            "expected_body_span": 0x1B, "reject_nonentry": True,
            "review_evidence_id": "ev-target-shared-tail",
        }
        parse_function_overrides({"function_overrides": [override]})
        with self.assertRaises(BoundaryLedgerError):
            parse_function_overrides({"function_overrides": [
                {**override, "reviewed_body_size": 0x1B}
            ]})
        contribution = Contribution(
            "th04-zun", 0x355, 0x6F3, "ongchk.com", "", "library",
            "embedded-library", "config:com-region:ongchk.com", "target",
        )
        ghidra = {
            "name": "FUN_1000_0517", "body_addresses": "27", "body_span": "27",
            "body_min_linear": "0x10517", "body_max_linear": "0x10531",
            "contiguous": "true", "body_range_count": "1",
            "caller_count": "2", "callee_count": "0", "symbol_source": "DEFAULT",
        }
        row = function_row(
            "th04-zun", 0x517, 0x10000, ghidra, [], contribution,
            None, None, None, False, override,
        )
        self.assertEqual(row["boundary_state"], "excluded")
        self.assertEqual(row["source_ref"], override["source_ref"])
        self.assertIn("shared tail", row["notes"])
        with self.assertRaises(BoundaryLedgerError):
            function_row(
                "th04-zun", 0x517, 0x10000, ghidra, ["public"],
                contribution, None, None, None, False, override,
            )



    def test_target_reviewed_override_requires_evidence_and_boundary_oracle(self) -> None:
        asm_base = {
            "artifact": "th04-zun",
            "payload_offset": 0x6F6,
            "origin": "authored",
            "source_form": "target-derived-asm",
            "source_ref": "candidate:th04_zuninit.asm",
            "reviewed_body_size": 0x12,
        }
        with self.assertRaises(BoundaryLedgerError):
            parse_function_overrides({"function_overrides": [asm_base]})
        with self.assertRaises(BoundaryLedgerError):
            parse_function_overrides({
                "function_overrides": [
                    {
                        **asm_base,
                        "expected_body_span": 0x12,
                        "review_evidence_id": "ev-review",
                    }
                ]
            })
        with self.assertRaises(BoundaryLedgerError):
            parse_function_overrides({
                "function_overrides": [
                    {**asm_base, "expected_tasm_proc": "sub_103"}
                ]
            })

        cpp_base = {
            "artifact": "th04-op",
            "payload_offset": 0xC627,
            "origin": "authored",
            "source_form": "candidate-cpp",
            "source_ref": "candidate:th04/score_e.cpp",
            "reviewed_body_size": 0x65,
        }
        with self.assertRaises(BoundaryLedgerError):
            parse_function_overrides({
                "function_overrides": [
                    {**cpp_base, "review_evidence_id": "ev-review"}
                ]
            })
        rules = parse_function_overrides({
            "function_overrides": [
                {
                    **cpp_base,
                    "expected_body_span": 0x65,
                    "review_evidence_id": "ev-review",
                }
            ]
        })
        self.assertEqual(
            rules[("th04-op", 0xC627)]["expected_body_span"], 0x65
        )

    def test_target_reviewed_override_sets_extent_without_ghidra(self) -> None:
        contribution = Contribution(
            "th04-zun", 0x6F3, 0xB68, "th04_zuninit.asm", "_TEXT",
            "authored", "target-derived-asm", "candidate:th04_zuninit.asm",
            "target-exact-composite+candidate-map",
        )
        override = {
            "artifact": "th04-zun",
            "payload_offset": 0x6F6,
            "origin": "authored",
            "source_form": "target-derived-asm",
            "source_ref": "candidate:th04_zuninit.asm",
            "expected_tasm_proc": "sub_103",
            "reviewed_body_size": 0x12,
            "review_evidence_id": "ev-review",
        }
        row = function_row(
            "th04-zun", 0x6F6, 0x10000, None, [], contribution, None, None,
            {
                "name": "sub_103", "distance": "far", "listing_line": "12",
            },
            False, override,
        )
        self.assertEqual(row["boundary_state"], "reviewed")
        self.assertEqual(row["body_size"], "0x12")
        self.assertEqual(row["body_span"], "0x12")
        self.assertEqual(row["origin"], "authored")
        self.assertEqual(row["source_form"], "target-derived-asm")
        self.assertIn("ev-review", row["notes"])

    def test_target_reviewed_cpp_override_uses_exact_ghidra_span(self) -> None:
        contribution = Contribution(
            "th04-op", 0xC627, 0xC68C, "th04/score_e.cpp", "SCORE_TEXT",
            "authored", "candidate-cpp", "candidate:th04/score_e.cpp",
            "target-unpacked-ghidra+candidate-map",
        )
        ghidra = {
            "name": "FUN_1a74_1ee7",
            "body_addresses": "101",
            "body_span": "101",
            "body_min_linear": "0x1C627",
            "body_max_linear": "0x1C68B",
            "contiguous": "true",
            "body_range_count": "1",
            "caller_count": "1",
            "callee_count": "1",
            "symbol_source": "DEFAULT",
        }
        override = {
            "artifact": "th04-op",
            "payload_offset": 0xC627,
            "origin": "authored",
            "source_form": "candidate-cpp",
            "source_ref": "candidate:th04/score_e.cpp",
            "expected_body_span": 0x65,
            "reviewed_body_size": 0x65,
            "review_evidence_id": "ev-review",
        }
        row = function_row(
            "th04-op", 0xC627, 0x10000, ghidra, [], contribution, None,
            None, None, False, override,
        )
        self.assertEqual(row["boundary_state"], "reviewed")
        self.assertEqual(row["body_size"], "0x65")
        self.assertEqual(row["body_span"], "0x65")
        self.assertEqual(row["source_form"], "candidate-cpp")
        self.assertIn("ev-review", row["notes"])



    def test_target_reviewed_cpp_override_can_require_no_ghidra_entry(self) -> None:
        contribution = Contribution(
            "th04-maine", 0xD594, 0xD5A0, "th02/snd_se_r.cpp", "SHARED",
            "authored", "cross-game-candidate-cpp", "candidate:th02/snd_se_r.cpp",
            "target-unpacked-ghidra+candidate-map",
        )
        override = {
            "artifact": "th04-maine",
            "payload_offset": 0xD594,
            "origin": "authored",
            "source_form": "cross-game-candidate-cpp",
            "source_ref": "candidate:th02/snd_se_r.cpp",
            "expected_no_ghidra": True,
            "reviewed_body_size": 0xB,
            "review_evidence_id": "ev-review",
        }
        rules = parse_function_overrides({"function_overrides": [override]})
        self.assertTrue(rules[("th04-maine", 0xD594)]["expected_no_ghidra"])
        row = function_row(
            "th04-maine", 0xD594, 0x10000, None, ["_snd_se_reset"],
            contribution, None, None, None, False, override,
        )
        self.assertEqual(row["boundary_state"], "reviewed")
        self.assertEqual(row["body_size"], "0xB")
        self.assertIn("expects no Ghidra function entry", row["notes"])

    def test_target_reviewed_no_ghidra_override_rejects_conflicting_observation(self) -> None:
        contribution = Contribution(
            "th04-maine", 0xD594, 0xD5A0, "th02/snd_se_r.cpp", "SHARED",
            "authored", "cross-game-candidate-cpp", "candidate:th02/snd_se_r.cpp",
            "target-unpacked-ghidra+candidate-map",
        )
        override = {
            "artifact": "th04-maine",
            "payload_offset": 0xD594,
            "origin": "authored",
            "source_form": "cross-game-candidate-cpp",
            "source_ref": "candidate:th02/snd_se_r.cpp",
            "expected_no_ghidra": True,
            "reviewed_body_size": 0xB,
            "review_evidence_id": "ev-review",
        }
        ghidra = {
            "name": "FUN_1cc7_0924",
            "body_addresses": "11",
            "body_span": "11",
            "body_min_linear": "0x1D594",
            "body_max_linear": "0x1D59E",
            "contiguous": "true",
            "body_range_count": "1",
            "caller_count": "1",
            "callee_count": "0",
            "symbol_source": "DEFAULT",
        }
        with self.assertRaises(BoundaryLedgerError):
            function_row(
                "th04-maine", 0xD594, 0x10000, ghidra, ["_snd_se_reset"],
                contribution, None, None, None, False, override,
            )
        with self.assertRaises(BoundaryLedgerError):
            function_row(
                "th04-maine", 0xD594, 0x10000, None, [],
                contribution, None, None, None, False, override,
            )

    def test_target_reviewed_no_ghidra_override_is_exclusive(self) -> None:
        base = {
            "artifact": "th04-maine",
            "payload_offset": 0xD594,
            "origin": "authored",
            "source_form": "cross-game-candidate-cpp",
            "source_ref": "candidate:th02/snd_se_r.cpp",
            "expected_no_ghidra": True,
            "reviewed_body_size": 0xB,
            "review_evidence_id": "ev-review",
        }
        with self.assertRaises(BoundaryLedgerError):
            parse_function_overrides({
                "function_overrides": [{**base, "expected_body_span": 0xB}]
            })

    def test_target_reviewed_override_rejects_owner_escape(self) -> None:
        contribution = Contribution(
            "th04-zun", 0x6F3, 0x700, "th04_zuninit.asm", "_TEXT",
            "authored", "target-derived-asm", "candidate:th04_zuninit.asm",
            "target-exact-composite+candidate-map",
        )
        override = {
            "origin": "authored",
            "source_form": "target-derived-asm",
            "source_ref": "candidate:th04_zuninit.asm",
            "expected_tasm_proc": "sub_103",
            "reviewed_body_size": 0x12,
            "review_evidence_id": "ev-review",
        }
        with self.assertRaises(BoundaryLedgerError):
            function_row(
                "th04-zun", 0x6F6, 0x10000, None, [], contribution, None, None,
                {
                    "name": "sub_103", "distance": "far", "listing_line": "12",
                },
                False, override,
            )

    def test_rejects_duplicate_function_override(self) -> None:
        rule = {
            "artifact": "th04-main",
            "payload_offset": 0x3680,
            "origin": "authored",
            "source_form": "target-derived-asm",
            "source_ref": "candidate:th04_main.asm",
        }
        with self.assertRaises(BoundaryLedgerError):
            parse_function_overrides({"function_overrides": [rule, rule]})


if __name__ == "__main__":
    unittest.main()
