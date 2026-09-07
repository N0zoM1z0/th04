from __future__ import annotations

import contextlib
import csv
import io
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import tomllib
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_tracking import (
    EVIDENCE_HEADER,
    FUNCTION_HEADER,
    HYPOTHESIS_HEADER,
    KNOWLEDGE_HEADER,
    UNIT_HEADER,
    main as validate_tracking,
)


class ExactTrackingTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        repository = Path(__file__).resolve().parents[1]
        config = root / "config"
        config.mkdir()
        shutil.copyfile(repository / "config" / "targets.toml", config / "targets.toml")
        shutil.copyfile(repository / "config" / "oracles.toml", config / "oracles.toml")
        (root / "src" / "main").mkdir(parents=True)
        (root / "src" / "main" / "unit.c").write_text(
            "int unit(void) { return 0; }\n", encoding="utf-8"
        )
        (root / "scripts").mkdir()
        (root / "scripts" / "replay.py").write_text("# replay fixture\n", encoding="utf-8")

        unit = {
            "id": "unit-main-100",
            "artifact": "th04-main",
            "kind": "code",
            "segment": "CODE",
            "offset": "0x100",
            "file_offset": "0x100",
            "size": "16",
            "compare_size": "16",
            "boundary_state": "reviewed",
            "origin": "authored",
            "state": "exact",
            "name": "unit",
            "source": "src/main/unit.c",
            "evidence_ids": "",
            "replay_command": "python3 scripts/replay.py --unit unit-main-100",
            "notes": "synthetic exact-promotion fixture",
        }
        other = dict(unit)
        other.update(
            {
                "id": "unit-main-200",
                "offset": "0x200",
                "file_offset": "0x200",
                "state": "candidate",
                "evidence_ids": "",
            }
        )
        oracle_config = tomllib.loads((config / "oracles.toml").read_text(encoding="utf-8"))
        accepted = {
            item["id"]: item.get("accepts_evidence_classes", ["control-plane"])[0]
            for item in oracle_config["oracles"]
        }
        global_oracles = set(oracle_config["policy"]["global_evidence_oracles"])
        artifact_oracles = set(oracle_config["policy"]["artifact_evidence_oracles"])
        evidence: list[dict[str, str]] = []
        for oracle in oracle_config["policy"]["exact_requires"]:
            row = {field: "" for field in EVIDENCE_HEADER}
            row.update(
                {
                    "id": f"ev-{oracle}",
                    "oracle": oracle,
                    "location": "synthetic fixture",
                    "evidence_class": accepted[oracle],
                    "result": "pass",
                    "tool": "scripts/replay.py",
                    "command": "python3 scripts/replay.py --unit unit-main-100",
                    "input_sha256": "1" * 64,
                    "output_sha256": "1" * 64,
                    "observed_utc": "2026-09-06T00:00:00Z",
                    "notes": "synthetic exact evidence",
                }
            )
            if oracle in global_oracles:
                pass
            elif oracle in artifact_oracles:
                row["artifact"] = "th04-main"
            else:
                row.update(
                    {
                        "artifact": "th04-main",
                        "unit_id": unit["id"],
                        "extent_start": unit["file_offset"],
                        "extent_size": unit["compare_size"],
                    }
                )
            evidence.append(row)
        unit["evidence_ids"] = ";".join(row["id"] for row in evidence)
        return [unit, other], evidence

    @staticmethod
    def write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)

    def run_fixture(
        self,
        root: Path,
        units: list[dict[str, str]],
        evidence: list[dict[str, str]],
        functions: list[dict[str, str]] | None = None,
    ) -> int:
        config = root / "config"
        self.write_csv(config / "units.csv", UNIT_HEADER, units)
        self.write_csv(config / "evidence.csv", EVIDENCE_HEADER, evidence)
        self.write_csv(config / "hypotheses.csv", HYPOTHESIS_HEADER, [])
        self.write_csv(config / "knowledge.csv", KNOWLEDGE_HEADER, [])
        if functions is not None:
            self.write_csv(
                config / "th04_main_authored_functions.csv", FUNCTION_HEADER, functions
            )
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return validate_tracking(root)

    def test_complete_unit_bound_exact_fixture_passes(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            units, evidence = self.make_fixture(root)
            self.assertEqual(self.run_fixture(root, units, evidence), 0)

    def test_source_state_directory_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            units, evidence = self.make_fixture(root)
            forbidden = root / "src" / "main" / "exact"
            forbidden.mkdir()
            (forbidden / "unit.c").write_text("int forbidden;\n", encoding="utf-8")
            self.assertEqual(self.run_fixture(root, units, evidence), 1)

    def test_direct_cross_game_include_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            units, evidence = self.make_fixture(root)
            (root / "src" / "main" / "unit.c").write_text(
                '#include "th03/core/initexit.h"\n', encoding="utf-8"
            )
            self.assertEqual(self.run_fixture(root, units, evidence), 1)

    def test_rec98_forwarder_cannot_hide_copied_declarations(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            units, evidence = self.make_fixture(root)
            forwarder = root / "compat" / "rec98" / "th02" / "core" / "initexit.h"
            forwarder.parent.mkdir(parents=True)
            forwarder.write_text("int copied_declaration;\n", encoding="utf-8")
            self.assertEqual(self.run_fixture(root, units, evidence), 1)

    def test_adversarial_exact_claims_fail_closed(self) -> None:
        mutations = {
            "evidence reused by another unit": lambda units, evidence: next(
                row for row in evidence if row["oracle"] == "raw-bytes"
            ).update({"unit_id": "unit-main-200"}),
            "blank replay metadata": lambda units, evidence: next(
                row for row in evidence if row["oracle"] == "raw-bytes"
            ).update({"command": ""}),
            "unequal raw hashes": lambda units, evidence: next(
                row for row in evidence if row["oracle"] == "raw-bytes"
            ).update({"output_sha256": "2" * 64}),
            "missing source": lambda units, evidence: units[0].update(
                {"source": "src/missing.c"}
            ),
            "missing address": lambda units, evidence: units[0].update({"segment": ""}),
            "extent outside artifact": lambda units, evidence: units[0].update(
                {"file_offset": "156250"}
            ),
            "private replay driver": lambda units, evidence: units[0].update(
                {"replay_command": "python3 .analysis/fake.py"}
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), TemporaryDirectory() as temporary:
                root = Path(temporary)
                units, evidence = self.make_fixture(root)
                mutate(units, evidence)
                self.assertEqual(self.run_fixture(root, units, evidence), 1)

    def test_exact_function_requires_exact_authored_owner(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            units, evidence = self.make_fixture(root)
            function = {field: "" for field in FUNCTION_HEADER}
            function.update(
                {
                    "id": "fn-main-104",
                    "artifact": "th04-main",
                    "address": "0x10104",
                    "file_offset": "0x104",
                    "size": "4",
                    "boundary_state": "reviewed",
                    "state": "exact",
                    "name": "fixture_function",
                    "owner_unit": "unit-main-100",
                    "source": "src/main/unit.c",
                    "evidence_ids": "ev-boundary-ownership",
                    "notes": "synthetic reviewed function",
                }
            )
            self.assertEqual(self.run_fixture(root, units, evidence, [function]), 0)

            function["owner_unit"] = "unit-main-200"
            self.assertEqual(self.run_fixture(root, units, evidence, [function]), 1)

    def test_exact_function_cannot_escape_owner_or_use_provisional_boundary(self) -> None:
        for name, mutation in (
            ("escape owner", {"file_offset": "0x10F", "size": "4"}),
            ("provisional boundary", {"boundary_state": "provisional"}),
        ):
            with self.subTest(name=name), TemporaryDirectory() as temporary:
                root = Path(temporary)
                units, evidence = self.make_fixture(root)
                function = {field: "" for field in FUNCTION_HEADER}
                function.update(
                    {
                        "id": "fn-main-104",
                        "artifact": "th04-main",
                        "address": "0x10104",
                        "file_offset": "0x104",
                        "size": "4",
                        "boundary_state": "reviewed",
                        "state": "exact",
                        "name": "fixture_function",
                        "owner_unit": "unit-main-100",
                        "source": "src/main/unit.c",
                        "evidence_ids": "ev-boundary-ownership",
                        "notes": "synthetic reviewed function",
                    }
                )
                function.update(mutation)
                self.assertEqual(self.run_fixture(root, units, evidence, [function]), 1)


if __name__ == "__main__":
    unittest.main()
