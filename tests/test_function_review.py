from __future__ import annotations

import csv
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import review_th04_main_functions as review


class ManualFunctionReviewTests(unittest.TestCase):
    def fixture(self, root: Path, jump_word: int) -> tuple[Path, Path, list[dict[str, object]], dict[int, dict[str, str]]]:
        policy = root / "policy.toml"
        policy.write_text(
            """schema_version = 1

[[reviewed_exact]]
id = "fn"
address = "0x10000"
file_offset = "0x1800"
size = "0x2"
name = "fixture"
owner_unit = "owner"
evidence_id = "ev-fixture"
reason = "synthetic switch-boundary review"
jump_table_address = "0x10002"
jump_table_count = 1
cs_base = "0x10000"
""",
            encoding="utf-8",
        )
        target = root / "target.bin"
        data = bytearray(0x1804)
        data[0x1800:0x1802] = b"\x90\xC3"
        data[0x1802:0x1804] = jump_word.to_bytes(2, "little")
        target.write_bytes(data)
        items = [
            {
                "address": 0x10000,
                "address_hex": "0x10000",
                "ghidra_name": "FUN_10000",
                "public": "fixture",
                "owner_unit": "owner",
                "owner_start": 0x10000,
                "owner_end": 0x10010,
                "source": "src/fixture.cpp",
                "owner_name": "fixture.cpp",
            }
        ]
        metadata = {
            0x10000: {
                "address": "0x10000",
                "body_min": "0x10000",
                "body_max": "0x10001",
                "body_addresses": "1",
            }
        }
        return policy, target, items, metadata

    @staticmethod
    def decoded() -> dict[str, object]:
        return {
            "instruction_count": 2,
            "instruction_addresses": [0x10000, 0x10001],
            "terminal": "ret",
            "first_address": "0x10000",
            "end_address_exclusive": "0x10002",
        }

    def test_manual_switch_review_accepts_instruction_aligned_targets(self) -> None:
        with TemporaryDirectory() as temporary:
            policy, target, items, metadata = self.fixture(Path(temporary), 0)
            with patch.object(review, "POLICY", policy), patch.object(
                review, "linear_decode", return_value=self.decoded()
            ):
                accepted = review.manual_reviews(items, metadata, target)
            self.assertEqual(len(accepted), 1)
            switch = accepted[0]["switch_review"]
            self.assertIsInstance(switch, dict)
            assert isinstance(switch, dict)
            self.assertTrue(switch["all_targets_are_instruction_starts"])
            self.assertEqual(switch["jump_targets"], ["0x10000"])

    def test_manual_switch_review_rejects_non_instruction_target(self) -> None:
        with TemporaryDirectory() as temporary:
            policy, target, items, metadata = self.fixture(Path(temporary), 5)
            with patch.object(review, "POLICY", policy), patch.object(
                review, "linear_decode", return_value=self.decoded()
            ):
                with self.assertRaisesRegex(ValueError, "non-instruction starts"):
                    review.manual_reviews(items, metadata, target)


    def test_linear_decode_handles_ndisasm_raw_byte_continuation(self) -> None:
        with TemporaryDirectory() as temporary:
            target = Path(temporary) / "target.bin"
            target.write_bytes(bytes.fromhex("66 c7 06 a2 46 00 00 00 00 cb"))
            stdout = (
                "00001000  66C706A246000000  mov dword [0x46a2],0x0\n"
                "         -00\n"
                "00001009  CB                retf\n"
            )
            completed = __import__("subprocess").CompletedProcess(
                ["ndisasm"], 0, stdout=stdout
            )
            with patch.object(review.subprocess, "run", return_value=completed):
                decoded = review.linear_decode(target, 0x1000, 0, 10)
            self.assertEqual(decoded["instruction_count"], 2)
            self.assertEqual(decoded["instruction_addresses"], [0x1000, 0x1009])
            self.assertEqual(decoded["terminal"], "retf")
            self.assertEqual(decoded["end_address_exclusive"], "0x100A")

    def test_reviewed_nonexact_validates_trailing_switch_data(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text(
                """schema_version = 1

[[reviewed_nonexact]]
id = "fn-blocked"
address = "0x10000"
file_offset = "0x1800"
size = "0x5"
decode_size = "0x2"
name = "blocked_fixture"
evidence_id = "ev-blocked"
reason = "synthetic reviewed nonexact boundary"
table_metadata_address = "0x10002"
table_metadata_value = "0x00"
jump_table_address = "0x10003"
jump_table_count = 1
cs_base = "0x10000"
next_public_address = "0x10005"
""",
                encoding="utf-8",
            )
            target = root / "target.bin"
            data = bytearray(0x1805)
            data[0x1800:0x1805] = b"\x90\xC3\x00\x00\x00"
            target.write_bytes(data)
            items = [{
                "address": 0x10000,
                "address_hex": "0x10000",
                "ghidra_name": "FUN_10000",
                "public": "blocked_fixture",
                "owner_unit": "entry-owner",
                "owner_start": 0x10000,
                "owner_end": 0x10002,
                "file_offset": 0x1800,
                "source": "src/entry.cpp",
                "owner_name": "entry.cpp",
            }]
            metadata = {0x10000: {
                "address": "0x10000",
                "body_min": "0x10000",
                "body_max": "0x10001",
                "body_addresses": "2",
                "is_thunk": "false",
                "is_external": "false",
            }}
            publics = {0x10000: ["blocked_fixture"], 0x10005: ["next_fixture"]}
            decoded = {
                "instruction_count": 2,
                "instruction_addresses": [0x10000, 0x10001],
                "terminal": "ret",
                "first_address": "0x10000",
                "end_address_exclusive": "0x10002",
            }
            with patch.object(review, "POLICY", policy), patch.object(
                review, "linear_decode", return_value=decoded
            ):
                accepted = review.reviewed_nonexact_reviews(
                    items, metadata, publics, target
                )
            self.assertEqual(len(accepted), 1)
            self.assertEqual(accepted[0]["size"], 5)
            switch = accepted[0]["switch_review"]
            self.assertIsInstance(switch, dict)
            assert isinstance(switch, dict)
            self.assertEqual(switch["jump_targets"], ["0x10000"])
            self.assertEqual(switch["table_metadata_value"], "0x00")

    def test_reviewed_nonexact_ledger_sets_blocked_extent_and_evidence(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = [
                "id", "artifact", "address", "file_offset", "size",
                "boundary_state", "state", "name", "owner_unit", "source",
                "evidence_ids", "notes",
            ]
            row = {key: "" for key in header}
            row.update({
                "id": "fn-blocked", "artifact": "th04-main",
                "address": "0x100", "boundary_state": "provisional",
                "state": "candidate", "name": "fixture",
                "owner_unit": "stale-owner", "source": "src/stale.cpp",
                "evidence_ids": "ev-old",
            })
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=header)
                writer.writeheader()
                writer.writerow(row)
            out = root / "out.csv"
            old_root = review.ROOT
            review.ROOT = root
            try:
                review.write_reviewed_ledger(
                    out,
                    [],
                    [],
                    [{
                        "id": "fn-blocked", "address": 0x100,
                        "file_offset": 0x200, "size": 0x20,
                        "evidence_id": "ev-new", "reason": "reviewed boundary",
                    }],
                )
            finally:
                review.ROOT = old_root
            with out.open(newline="", encoding="utf-8") as stream:
                updated = next(csv.DictReader(stream))
            self.assertEqual(updated["boundary_state"], "reviewed")
            self.assertEqual(updated["state"], "blocked")
            self.assertEqual(updated["file_offset"], "0x200")
            self.assertEqual(updated["size"], "0x20")
            self.assertEqual(updated["owner_unit"], "")
            self.assertEqual(updated["source"], "")
            self.assertEqual(updated["evidence_ids"], "ev-old;ev-new")


    def test_reviewed_exact_extent_requires_full_exact_owner(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text(
                """schema_version = 1

[[reviewed_exact_extent]]
id = "fn-exact"
address = "0x10000"
file_offset = "0x1800"
size = "0x5"
decode_size = "0x2"
name = "exact_fixture"
owner_unit = "owner"
evidence_id = "ev-exact"
reason = "synthetic reviewed exact extent"
table_metadata_address = "0x10002"
table_metadata_value = "0x00"
jump_table_address = "0x10003"
jump_table_count = 1
cs_base = "0x10000"
next_public_address = "0x10005"
""",
                encoding="utf-8",
            )
            target = root / "target.bin"
            data = bytearray(0x1805)
            data[0x1800:0x1805] = b"\x90\xC3\x00\x00\x00"
            target.write_bytes(data)
            item = {
                "address": 0x10000,
                "address_hex": "0x10000",
                "ghidra_name": "FUN_10000",
                "public": "exact_fixture",
                "owner_unit": "owner",
                "owner_start": 0x10000,
                "owner_end": 0x10005,
                "file_offset": 0x1800,
                "source": "src/exact.cpp",
                "owner_name": "exact.cpp",
            }
            metadata = {0x10000: {
                "address": "0x10000",
                "body_min": "0x10000",
                "body_max": "0x10001",
                "body_addresses": "2",
                "is_thunk": "false",
                "is_external": "false",
            }}
            publics = {0x10000: ["exact_fixture"], 0x10005: ["next_fixture"]}
            decoded = {
                "instruction_count": 2,
                "instruction_addresses": [0x10000, 0x10001],
                "terminal": "ret",
                "first_address": "0x10000",
                "end_address_exclusive": "0x10002",
            }
            with patch.object(review, "POLICY", policy), patch.object(
                review, "linear_decode", return_value=decoded
            ):
                accepted = review.reviewed_nonexact_reviews(
                    [item], metadata, publics, target,
                    policy_key="reviewed_exact_extent",
                    require_exact_extent=True,
                )
                self.assertEqual(len(accepted), 1)
                escaped = dict(item)
                escaped["owner_end"] = 0x10004
                with self.assertRaisesRegex(ValueError, "escapes exact owner"):
                    review.reviewed_nonexact_reviews(
                        [escaped], metadata, publics, target,
                        policy_key="reviewed_exact_extent",
                        require_exact_extent=True,
                    )

    def test_manual_exact_extent_promotes_blocked_ledger_row(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = [
                "id", "artifact", "address", "file_offset", "size",
                "boundary_state", "state", "name", "owner_unit", "source",
                "evidence_ids", "notes",
            ]
            row = {key: "" for key in header}
            row.update({
                "id": "fn-exact", "artifact": "th04-main",
                "address": "0x100", "file_offset": "0x200", "size": "0x5",
                "boundary_state": "reviewed", "state": "blocked",
                "name": "fixture", "evidence_ids": "ev-old",
            })
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=header)
                writer.writeheader()
                writer.writerow(row)
            policy = root / "policy.toml"
            policy.write_text("schema_version = 1\n", encoding="utf-8")
            out = root / "out.csv"
            old_root, old_policy = review.ROOT, review.POLICY
            review.ROOT, review.POLICY = root, policy
            try:
                review.write_reviewed_ledger(
                    out,
                    [],
                    [{
                        "id": "fn-exact", "address": 0x100,
                        "file_offset": 0x200, "size": 0x5,
                        "owner_unit": "owner-exact", "source": "src/exact.cpp",
                        "evidence_id": "ev-new", "reason": "validated exact extent",
                        "switch_review": None,
                    }],
                )
            finally:
                review.ROOT, review.POLICY = old_root, old_policy
            with out.open(newline="", encoding="utf-8") as stream:
                promoted = next(csv.DictReader(stream))
            self.assertEqual(promoted["state"], "exact")
            self.assertEqual(promoted["owner_unit"], "owner-exact")
            self.assertEqual(promoted["source"], "src/exact.cpp")
            self.assertEqual(promoted["evidence_ids"], "ev-old;ev-new")


    def test_automatic_review_promotes_blocked_row(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = [
                "id", "artifact", "address", "file_offset", "size",
                "boundary_state", "state", "name", "owner_unit", "source",
                "evidence_ids", "notes",
            ]
            row = {key: "" for key in header}
            row.update({
                "id": "fn-100", "artifact": "th04-main", "address": "0x100",
                "file_offset": "0x200", "size": "0x4",
                "boundary_state": "reviewed", "state": "blocked",
                "name": "fixture", "evidence_ids": "ev-boundary",
            })
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=header)
                writer.writeheader()
                writer.writerow(row)
            out = root / "out.csv"
            old_root = review.ROOT
            review.ROOT = root
            try:
                review.write_reviewed_ledger(
                    out,
                    [{
                        "address": 0x100,
                        "owner_unit": "owner-exact",
                        "source": "src/unit.c",
                    }],
                    [],
                )
            finally:
                review.ROOT = old_root
            with out.open(newline="", encoding="utf-8") as stream:
                promoted = next(csv.DictReader(stream))
            self.assertEqual(promoted["state"], "exact")
            self.assertEqual(promoted["owner_unit"], "owner-exact")
            self.assertEqual(promoted["source"], "src/unit.c")

    def test_automatic_exact_owner_migration_requires_explicit_policy(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = ["id", "artifact", "address", "file_offset", "size", "boundary_state", "state", "name", "owner_unit", "source", "evidence_ids", "notes"]
            row = {key: "" for key in header}
            row.update({"id": "fn-100", "artifact": "th04-main", "address": "0x100", "file_offset": "0x200", "size": "0x4", "boundary_state": "reviewed", "state": "exact", "name": "fixture", "owner_unit": "old-owner", "source": "src/old.cpp", "evidence_ids": "ev-old"})
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=header); writer.writeheader(); writer.writerow(row)
            policy = root / "policy.toml"
            policy.write_text("schema_version = 1\n\n[[owner_migration]]\naddress = \"0x100\"\nfrom_owner = \"old-owner\"\nfrom_source = \"src/old.cpp\"\nto_owner = \"new-owner\"\nto_source = \"src/new.cpp\"\nevidence_id = \"ev-migrate\"\nreason = \"reviewed merged TU\"\n", encoding="utf-8")
            out = root / "out.csv"
            old_root, old_policy = review.ROOT, review.POLICY
            review.ROOT, review.POLICY = root, policy
            try:
                review.write_reviewed_ledger(out, [{"address": 0x100, "owner_unit": "new-owner", "source": "src/new.cpp"}], [])
            finally:
                review.ROOT, review.POLICY = old_root, old_policy
            with out.open(newline="", encoding="utf-8") as stream:
                migrated = next(csv.DictReader(stream))
            self.assertEqual(migrated["owner_unit"], "new-owner")
            self.assertEqual(migrated["source"], "src/new.cpp")
            self.assertEqual(migrated["evidence_ids"], "ev-old;ev-migrate")

    def test_automatic_exact_owner_migration_rejects_wrong_from_owner(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = ["id", "artifact", "address", "file_offset", "size", "boundary_state", "state", "name", "owner_unit", "source", "evidence_ids", "notes"]
            row = {key: "" for key in header}
            row.update({"id": "fn-100", "artifact": "th04-main", "address": "0x100", "file_offset": "0x200", "size": "0x4", "boundary_state": "reviewed", "state": "exact", "name": "fixture", "owner_unit": "actual-old", "source": "src/old.cpp"})
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=header); writer.writeheader(); writer.writerow(row)
            policy = root / "policy.toml"
            policy.write_text("schema_version = 1\n\n[[owner_migration]]\naddress = \"0x100\"\nfrom_owner = \"wrong-old\"\nfrom_source = \"src/old.cpp\"\nto_owner = \"new-owner\"\nto_source = \"src/new.cpp\"\nreason = \"must fail\"\n", encoding="utf-8")
            out = root / "out.csv"
            old_root, old_policy = review.ROOT, review.POLICY
            review.ROOT, review.POLICY = root, policy
            try:
                with self.assertRaisesRegex(ValueError, "from_owner mismatch"):
                    review.write_reviewed_ledger(out, [{"address": 0x100, "owner_unit": "new-owner", "source": "src/new.cpp"}], [])
            finally:
                review.ROOT, review.POLICY = old_root, old_policy

    def test_automatic_review_adds_explicit_new_exact_row(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = [
                "id", "artifact", "address", "file_offset", "size",
                "boundary_state", "state", "name", "owner_unit", "source",
                "evidence_ids", "notes",
            ]
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=header)
                writer.writeheader()
            policy = root / "policy.toml"
            policy.write_text(
                '[[new_exact]]\nid = "fn-new"\naddress = "0x100"\n'
                'evidence_id = "ev-new"\nreason = "explicit fixture"\n',
                encoding="utf-8",
            )
            out = root / "out.csv"
            old_root, old_policy = review.ROOT, review.POLICY
            review.ROOT, review.POLICY = root, policy
            try:
                review.write_reviewed_ledger(
                    out,
                    [{
                        "address": 0x100, "file_offset": 0x200, "size": 4,
                        "public": "fixture()", "owner_unit": "owner-exact",
                        "source": "src/unit.c",
                    }],
                    [],
                )
            finally:
                review.ROOT, review.POLICY = old_root, old_policy
            with out.open(newline="", encoding="utf-8") as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["id"], "fn-new")
            self.assertEqual(row["state"], "exact")
            self.assertEqual(row["evidence_ids"], "ev-new")

    def test_automatic_review_rejects_unlisted_new_exact_row(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = [
                "id", "artifact", "address", "file_offset", "size",
                "boundary_state", "state", "name", "owner_unit", "source",
                "evidence_ids", "notes",
            ]
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                csv.DictWriter(stream, fieldnames=header).writeheader()
            policy = root / "policy.toml"
            policy.write_text("schema_version = 1\n", encoding="utf-8")
            out = root / "out.csv"
            old_root, old_policy = review.ROOT, review.POLICY
            review.ROOT, review.POLICY = root, policy
            try:
                with self.assertRaisesRegex(ValueError, "lacks an explicit"):
                    review.write_reviewed_ledger(
                        out,
                        [{
                            "address": 0x100, "file_offset": 0x200, "size": 4,
                            "public": "fixture()", "owner_unit": "owner-exact",
                            "source": "src/unit.c",
                        }],
                        [],
                    )
            finally:
                review.ROOT, review.POLICY = old_root, old_policy

    def test_no_ghidra_exact_requires_public_owner_and_boundary(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text('''[[reviewed_exact_no_ghidra]]
id = "fn-new"
address = "0x10000"
file_offset = "0x1800"
size = "0x2"
name = "fixture"
owner_unit = "owner"
evidence_id = "ev-new"
reason = "missing Ghidra fixture"
next_public_address = "0x10002"
''', encoding="utf-8")
            target = root / "target.bin"
            target.write_bytes(bytearray(0x1800) + b"\x90\xC3")
            owners = [{"start": 0x10000, "end": 0x10010, "file_start": 0x1800,
                       "unit_id": "owner", "source": "src/exact.cpp", "owner_name": "exact"}]
            publics = {0x10000: ["fixture"], 0x10002: ["next"]}
            decoded = {"instruction_count": 2, "instruction_addresses": [0x10000, 0x10001],
                       "terminal": "ret", "first_address": "0x10000",
                       "end_address_exclusive": "0x10002"}
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ), patch.object(review, "linear_decode", return_value=decoded):
                accepted = review.reviewed_exact_no_ghidra_reviews({}, publics, target)
                self.assertEqual(len(accepted), 1)
                with self.assertRaisesRegex(ValueError, "has a Ghidra function entry"):
                    review.reviewed_exact_no_ghidra_reviews({0x10000: "FUN_10000"}, publics, target)
            policy.write_text(policy.read_text().replace('size = "0x2"', 'size = "0x1"'), encoding="utf-8")
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ), patch.object(review, "linear_decode", return_value=decoded):
                with self.assertRaisesRegex(ValueError, "next-public boundary mismatch"):
                    review.reviewed_exact_no_ghidra_reviews({}, publics, target)

    def test_new_manual_exact_row_can_be_declared_explicitly(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"; config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = ["id", "artifact", "address", "file_offset", "size", "boundary_state", "state",
                      "name", "owner_unit", "source", "evidence_ids", "notes"]
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                csv.DictWriter(stream, fieldnames=header).writeheader()
            policy = root / "policy.toml"
            policy.write_text('[[new_exact]]\nid = "fn-new"\naddress = "0x100"\nevidence_id = "ev-new"\nreason = "fixture"\n', encoding="utf-8")
            item = {"id": "fn-new", "address": 0x100, "file_offset": 0x200, "size": 4,
                    "public": "fixture()", "owner_unit": "owner", "source": "src/exact.cpp",
                    "evidence_id": "ev-new", "reason": "validated boundary", "switch_review": None}
            out = root / "out.csv"
            old_root, old_policy = review.ROOT, review.POLICY
            review.ROOT, review.POLICY = root, policy
            try:
                review.write_reviewed_ledger(out, [], [item])
            finally:
                review.ROOT, review.POLICY = old_root, old_policy
            with out.open(newline="", encoding="utf-8") as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["id"], "fn-new")
            self.assertEqual(row["state"], "exact")

    def test_no_ghidra_switch_extent_requires_aligned_targets_and_full_trailing_data(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text('''[[reviewed_exact_no_ghidra]]
id = "fn-switch"
address = "0x10000"
file_offset = "0x1800"
size = "0x5"
decode_size = "0x2"
name = "fixture"
owner_unit = "owner"
evidence_id = "ev-switch"
reason = "switch fixture"
table_metadata_address = "0x10002"
table_metadata_value = "0x00"
jump_table_address = "0x10003"
jump_table_count = 1
cs_base = "0x10000"
next_public_address = "0x10005"
''', encoding="utf-8")
            target = root / "target.bin"
            target.write_bytes(bytearray(0x1800) + b"\x90\xC3\x00\x00\x00")
            owners = [{"start": 0x10000, "end": 0x10005, "file_start": 0x1800,
                       "unit_id": "owner", "source": "src/exact.cpp", "owner_name": "exact"}]
            publics = {0x10000: ["fixture"], 0x10005: ["next"]}
            decoded = {"instruction_count": 2, "instruction_addresses": [0x10000, 0x10001],
                       "terminal": "ret", "first_address": "0x10000", "end_address_exclusive": "0x10002"}
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ), patch.object(review, "linear_decode", side_effect=lambda *args: dict(decoded)):
                accepted = review.reviewed_exact_no_ghidra_reviews({}, publics, target)
                self.assertTrue(accepted[0]["switch_review"]["trailing_extent_fully_accounted"])
            bad = bytearray(target.read_bytes()); bad[0x1803:0x1805] = b"\x05\x00"; target.write_bytes(bad)
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ), patch.object(review, "linear_decode", side_effect=lambda *args: dict(decoded)):
                with self.assertRaisesRegex(ValueError, "non-instruction starts"):
                    review.reviewed_exact_no_ghidra_reviews({}, publics, target)


    def test_internal_exact_requires_pointer_anchor_and_next_public(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text("""[[reviewed_exact_internal]]
id = "fn-internal"
address = "0x10000"
file_offset = "0x1800"
size = "0x2"
name = "static_fixture()"
owner_unit = "owner"
evidence_id = "ev-internal"
reason = "synthetic internal boundary"
next_public_address = "0x10002"
pointer_word_address = "0x10008"
cs_base = "0xF000"
""", encoding="utf-8")
            target = root / "target.bin"
            data = bytearray(0x1810)
            data[0x1800:0x1802] = b"\x90\xC3"
            data[0x1808:0x180A] = b"\x00\x10"
            target.write_bytes(data)
            owners = [{"start": 0x10000, "end": 0x10010, "file_start": 0x1800,
                       "unit_id": "owner", "source": "src/exact.cpp", "owner_name": "exact"}]
            metadata = {0x10000: {"address": "0x10000", "body_min": "0x10000",
                                  "body_max": "0x10001", "body_addresses": "2",
                                  "is_thunk": "false", "is_external": "false"}}
            publics = {0x10002: ["next"]}
            decoded = {"instruction_count": 2, "instruction_addresses": [0x10000, 0x10001],
                       "terminal": "ret", "first_address": "0x10000",
                       "end_address_exclusive": "0x10002"}
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ), patch.object(review, "linear_decode", return_value=decoded):
                accepted = review.reviewed_exact_internal_reviews(
                    {0x10000: "FUN_10000"}, metadata, publics, target
                )
            self.assertEqual(len(accepted), 1)
            self.assertEqual(accepted[0]["pointer_word"], "0x1000")
            self.assertEqual(accepted[0]["boundary_mode"], "next TLINK public 0x10002")

    def test_internal_exact_rejects_wrong_pointer_anchor(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text("""[[reviewed_exact_internal]]
id = "fn-internal"
address = "0x10000"
file_offset = "0x1800"
size = "0x2"
name = "static_fixture()"
owner_unit = "owner"
evidence_id = "ev-internal"
reason = "synthetic internal boundary"
next_public_address = "0x10002"
pointer_word_address = "0x10008"
cs_base = "0xF000"
""", encoding="utf-8")
            target = root / "target.bin"
            data = bytearray(0x1810)
            data[0x1800:0x1802] = b"\x90\xC3"
            data[0x1808:0x180A] = b"\x01\x10"
            target.write_bytes(data)
            owners = [{"start": 0x10000, "end": 0x10010, "file_start": 0x1800,
                       "unit_id": "owner", "source": "src/exact.cpp", "owner_name": "exact"}]
            metadata = {0x10000: {"address": "0x10000", "body_min": "0x10000",
                                  "body_max": "0x10001", "body_addresses": "2",
                                  "is_thunk": "false", "is_external": "false"}}
            publics = {0x10002: ["next"]}
            decoded = {"instruction_count": 2, "instruction_addresses": [0x10000, 0x10001],
                       "terminal": "ret", "first_address": "0x10000",
                       "end_address_exclusive": "0x10002"}
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ), patch.object(review, "linear_decode", return_value=decoded):
                with self.assertRaisesRegex(ValueError, "pointer word mismatch"):
                    review.reviewed_exact_internal_reviews(
                        {0x10000: "FUN_10000"}, metadata, publics, target
                    )



    def test_internal_call_exact_accepts_truncated_ghidra_with_call_anchor(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text("""[[reviewed_exact_internal_call]]
id = "fn-internal-call"
address = "0x10000"
file_offset = "0x1800"
size = "0x3"
name = "internal_call_fixture()"
owner_unit = "owner"
evidence_id = "ev-internal-call"
reason = "synthetic truncated-Ghidra internal boundary"
next_internal_address = "0x10003"
call_site_address = "0x10008"
""", encoding="utf-8")
            target = root / "target.bin"
            data = bytearray(0x1810)
            data[0x1800:0x1803] = b"\x90\x90\xC3"
            data[0x1808:0x180B] = b"\xE8\xF5\xFF"
            target.write_bytes(data)
            owners = [{"start": 0x10000, "end": 0x10010, "file_start": 0x1800,
                       "unit_id": "owner", "source": "src/exact.cpp", "owner_name": "exact"}]
            functions = {0x10000: "FUN_10000", 0x10003: "FUN_10003"}
            metadata = {
                0x10000: {"address": "0x10000", "body_min": "0x10000",
                          "body_max": "0x10000", "body_addresses": "1",
                          "is_thunk": "false", "is_external": "false"},
                0x10003: {"address": "0x10003", "body_min": "0x10003",
                          "body_max": "0x10005", "body_addresses": "3",
                          "is_thunk": "false", "is_external": "false"},
            }
            decoded = {"instruction_count": 3, "instruction_addresses": [0x10000,0x10001,0x10002],
                       "terminal": "ret", "first_address": "0x10000",
                       "end_address_exclusive": "0x10003"}
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ), patch.object(review, "linear_decode", return_value=dict(decoded)):
                accepted = review.reviewed_exact_internal_call_reviews(
                    functions, metadata, {}, target
                )
            self.assertEqual(len(accepted), 1)
            self.assertEqual(accepted[0]["resolved_call_target"], "0x10000")
            self.assertEqual(accepted[0]["boundary_mode"], "next internal Ghidra entry 0x10003")

    def test_internal_call_exact_rejects_wrong_call_target(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text("""[[reviewed_exact_internal_call]]
id = "fn-internal-call"
address = "0x10000"
file_offset = "0x1800"
size = "0x3"
name = "internal_call_fixture()"
owner_unit = "owner"
evidence_id = "ev-internal-call"
reason = "synthetic truncated-Ghidra internal boundary"
next_internal_address = "0x10003"
call_site_address = "0x10008"
""", encoding="utf-8")
            target = root / "target.bin"
            data = bytearray(0x1810)
            data[0x1800:0x1803] = b"\x90\x90\xC3"
            data[0x1808:0x180B] = b"\xE8\xF6\xFF"
            target.write_bytes(data)
            owners = [{"start": 0x10000, "end": 0x10010, "file_start": 0x1800,
                       "unit_id": "owner", "source": "src/exact.cpp", "owner_name": "exact"}]
            functions = {0x10000: "FUN_10000", 0x10003: "FUN_10003"}
            metadata = {
                0x10000: {"address": "0x10000", "body_min": "0x10000",
                          "body_max": "0x10000", "body_addresses": "1",
                          "is_thunk": "false", "is_external": "false"},
                0x10003: {"address": "0x10003", "body_min": "0x10003",
                          "body_max": "0x10005", "body_addresses": "3",
                          "is_thunk": "false", "is_external": "false"},
            }
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ):
                with self.assertRaisesRegex(ValueError, "call target mismatch"):
                    review.reviewed_exact_internal_call_reviews(
                        functions, metadata, {}, target
                    )



    def test_internal_call_exact_requires_configured_generated_public(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            policy = root / "policy.toml"
            policy.write_text("""[[reviewed_exact_internal_call]]
id = "fn-internal-call"
address = "0x10000"
file_offset = "0x1800"
size = "0x3"
name = "internal_call_fixture()"
owner_unit = "owner"
evidence_id = "ev-internal-call"
reason = "synthetic generated-public review"
next_internal_address = "0x10003"
call_site_address = "0x10008"
generated_public = "_generated"
""", encoding="utf-8")
            target = root / "target.bin"
            data = bytearray(0x1810)
            data[0x1800:0x1803] = b"\x90\x90\xC3"
            data[0x1808:0x180B] = b"\xE8\xF5\xFF"
            target.write_bytes(data)
            owners = [{"start": 0x10000, "end": 0x10010, "file_start": 0x1800,
                       "unit_id": "owner", "source": "src/exact.cpp", "owner_name": "exact"}]
            functions = {0x10000: "FUN_10000", 0x10003: "FUN_10003"}
            metadata = {
                0x10000: {"address": "0x10000", "body_min": "0x10000",
                          "body_max": "0x10000", "body_addresses": "1",
                          "is_thunk": "false", "is_external": "false"},
                0x10003: {"address": "0x10003", "body_min": "0x10003",
                          "body_max": "0x10005", "body_addresses": "3",
                          "is_thunk": "false", "is_external": "false"},
            }
            decoded = {"instruction_count": 3, "instruction_addresses": [0x10000,0x10001,0x10002],
                       "terminal": "ret", "first_address": "0x10000",
                       "end_address_exclusive": "0x10003"}
            with patch.object(review, "POLICY", policy), patch.object(
                review, "exact_authored_owners", return_value=owners
            ), patch.object(review, "linear_decode", return_value=dict(decoded)):
                accepted = review.reviewed_exact_internal_call_reviews(
                    functions, metadata, {0x10000: ["_generated"]}, target
                )
                self.assertEqual(len(accepted), 1)
                with self.assertRaisesRegex(ValueError, "lacks configured generated public"):
                    review.reviewed_exact_internal_call_reviews(
                        functions, metadata, {0x10000: ["_wrong"]}, target
                    )


class AutomaticManualOverlapTests(unittest.TestCase):
    def test_writer_rejects_automatic_manual_same_address(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.mkdir()
            ledger = config / "th04_main_authored_functions.csv"
            header = ["id", "artifact", "address", "file_offset", "size", "boundary_state", "state", "name", "owner_unit", "source", "evidence_ids", "notes"]
            with ledger.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=header)
                writer.writeheader()
            out = root / "out.csv"
            old_root = review.ROOT
            review.ROOT = root
            try:
                with self.assertRaisesRegex(ValueError, "automatic/manual exact address overlap"):
                    review.write_reviewed_ledger(
                        out,
                        [{"address": 0x100, "owner_unit": "owner", "source": "src.cpp"}],
                        [{"id": "fn-100", "address": 0x100}],
                    )
            finally:
                review.ROOT = old_root


if __name__ == "__main__":
    unittest.main()
