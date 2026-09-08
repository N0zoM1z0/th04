from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from boundary_review.build_function_boundary_ledger import (
    BoundaryLedgerError,
    classify_module,
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
