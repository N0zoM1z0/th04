from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import decoded_function_acceptance as acceptance


class DecodedAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = acceptance.rows(acceptance.LEDGER, acceptance.HEADER)
        cls.boundaries = acceptance.rows(ROOT / "config/th04_function_boundaries.csv")
        cls.units = acceptance.rows(ROOT / "config/units.csv")
        cls.evidence = acceptance.rows(ROOT / "config/evidence.csv")

    def check(self, entries: list[dict[str, str]]) -> None:
        acceptance.validate(entries, self.boundaries, self.units, self.evidence)

    def test_current_three_artifact_ledger(self) -> None:
        self.check(self.entries)
        self.assertEqual({row["artifact"] for row in self.entries}, acceptance.ARTIFACTS)

    def test_rejects_cross_artifact_credit(self) -> None:
        entries = deepcopy(self.entries)
        entries[0]["artifact"] = "th04-maine"
        with self.assertRaisesRegex(ValueError, "artifact identity mismatch"):
            self.check(entries)

    def test_rejects_unreviewed_or_widened_boundary(self) -> None:
        entries = deepcopy(self.entries)
        entries[0]["size"] = "0x69"
        with self.assertRaisesRegex(ValueError, "physical decoded ownership mismatch"):
            self.check(entries)

    def test_rejects_duplicate_or_missing_exact(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate or unknown"):
            self.check([*self.entries, deepcopy(self.entries[0])])
        with self.assertRaisesRegex(ValueError, "missing decoded-exact"):
            self.check(self.entries[1:])

    def test_rejects_missing_function_scoped_raw_evidence(self) -> None:
        entries = deepcopy(self.entries)
        entries[0]["raw_evidence_id"] = "ev-th04-op-bgimage-raw-v489"
        with self.assertRaisesRegex(ValueError, "function-scoped raw evidence"):
            self.check(entries)

    def test_rejects_source_not_compiled_by_backend(self) -> None:
        entries = deepcopy(self.entries)
        entries[0]["source"] = "src/zun/config/cfg_init.cpp"
        with self.assertRaisesRegex(ValueError, "mismatched maintained source"):
            self.check(entries)

    def test_rejects_backend_claim_for_uncompiled_source(self) -> None:
        entries = deepcopy(self.entries)
        boundaries = deepcopy(self.boundaries)
        units = deepcopy(self.units)
        replacement = "src/shared/config/cfg.hpp"
        ident = entries[0]["boundary_id"]
        entries[0]["source"] = replacement
        next(row for row in boundaries if row["id"] == ident)["source_ref"] = replacement
        next(row for row in units if row["id"] == "th04-op-bgimage-snap-v247")["source"] = replacement
        with self.assertRaisesRegex(ValueError, "backend does not compile"):
            acceptance.validate(entries, boundaries, units, self.evidence)

    def test_rejects_false_equal_raw_hash_evidence(self) -> None:
        evidence = deepcopy(self.evidence)
        raw_id = self.entries[0]["raw_evidence_id"]
        next(row for row in evidence if row["id"] == raw_id)["output_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "function-scoped raw evidence"):
            acceptance.validate(self.entries, self.boundaries, self.units, evidence)

    def test_rejects_malformed_producer_receipt_digest(self) -> None:
        evidence = deepcopy(self.evidence)
        next(row for row in evidence if row["id"] == "ev-th04-op-vram-aggregate-v509")[
            "output_sha256"
        ] = "0" * 62
        with self.assertRaisesRegex(ValueError, "producer-scoped exact evidence"):
            acceptance.validate(self.entries, self.boundaries, self.units, evidence)

    def test_raw_comparison_rejects_target_drift_and_detects_candidate_mutation(self) -> None:
        entry = deepcopy(self.entries[0])
        entry["payload_offset"] = "0x1"
        entry["size"] = "0x3"
        entry["target_sha256"] = acceptance.sha(b"abc")
        result = acceptance.compare_extent(entry, b"_abc_", b"_adc_")
        self.assertEqual(result["raw_difference_count"], 1)
        self.assertEqual(result["first_difference_offsets"], [1])
        with self.assertRaisesRegex(RuntimeError, "no longer raw-match"):
            acceptance.require_exact_zero([result])
        with self.assertRaisesRegex(ValueError, "attested target slice changed"):
            acceptance.compare_extent(entry, b"_abd_", b"_abc_")
        with self.assertRaisesRegex(ValueError, "truncated"):
            acceptance.compare_extent(entry, b"_abc_", b"_ab")

    def test_zun_diagnostic_mismatch_never_counts_as_acceptance(self) -> None:
        entry = deepcopy(next(row for row in self.entries
                              if row["artifact"] == "th04-zun" and row["decoded_state"] == "source-present"))
        entry["payload_offset"] = "0x1"
        entry["size"] = "0x3"
        entry["target_sha256"] = acceptance.sha(b"abc")
        result = acceptance.compare_extent(entry, b"_abc_", b"_adc_")
        self.assertEqual(result["raw_difference_count"], 1)
        acceptance.require_exact_zero([result])

    def test_vram_backend_is_bound_to_maintained_source_and_artifact(self) -> None:
        entries = deepcopy(self.entries)
        vram = next(row for row in entries if row["replay_backend"] == "op-maine-vram-v509")
        vram["replay_backend"] = "op-maine-bgimage-v489"
        with self.assertRaisesRegex(ValueError, "BGIMAGE backend does not compile"):
            self.check(entries)


    def test_frame_delay_backend_is_bound_to_maintained_source_and_artifact(self) -> None:
        entries = deepcopy(self.entries)
        frame = next(row for row in entries if row["replay_backend"] == "op-maine-frame-delay-v510")
        frame["replay_backend"] = "op-maine-vram-v509"
        with self.assertRaisesRegex(ValueError, "VRAM backend does not compile"):
            self.check(entries)


    def test_pi_backends_are_bound_to_their_maintained_producers(self) -> None:
        entries = deepcopy(self.entries)
        pi_put = next(row for row in entries if row["replay_backend"] == "op-maine-pi-put-v511")
        pi_put["replay_backend"] = "op-maine-pi-load-v511"
        with self.assertRaisesRegex(ValueError, "PI load backend does not compile"):
            self.check(entries)


    def test_backend_dispatch_is_explicit_and_fail_closed(self) -> None:
        saved = ROOT / ".analysis/reconstruction/probes/unit-dispatch"
        self.assertEqual(
            acceptance.backend_command("op-maine-pi-put-v511", saved)[1],
            "scripts/probes/replay_th04_shared_pi_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-maine-pi-load-v511", saved)[1],
            "scripts/probes/replay_th04_shared_pi_load.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-maine-pmd-v512", saved)[1],
            "scripts/probes/replay_th04_shared_pmd.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-maine-mmd-v513", saved)[1],
            "scripts/probes/replay_th04_shared_mmd.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-maine-kaja-v514", saved)[1],
            "scripts/probes/replay_th04_shared_kaja.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-maine-mode-v515", saved)[1],
            "scripts/probes/replay_th04_shared_mode.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-maine-delay-v516", saved)[1],
            "scripts/probes/replay_th04_shared_delay_measure.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-score-insert-v543", saved)[1],
            "scripts/probes/replay_th04_maine_score_insert.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-score-put-v544", saved)[1],
            "scripts/probes/replay_th04_maine_score_put.py",
        )
        with self.assertRaisesRegex(ValueError, "unknown decoded replay backend"):
            acceptance.backend_command("not-a-backend", saved)

    def test_pmd_backend_is_bound_to_maintained_source(self) -> None:
        entries = deepcopy(self.entries)
        pmd = next(row for row in entries if row["replay_backend"] == "op-maine-pmd-v512")
        pmd["replay_backend"] = "op-maine-pi-load-v511"
        with self.assertRaisesRegex(ValueError, "PI load backend does not compile"):
            self.check(entries)


    def test_mmd_backend_is_bound_to_maintained_source(self) -> None:
        entries = deepcopy(self.entries)
        mmd = next(row for row in entries if row["replay_backend"] == "op-maine-mmd-v513")
        mmd["replay_backend"] = "op-maine-pmd-v512"
        with self.assertRaisesRegex(ValueError, "PMD backend does not compile"):
            self.check(entries)


    def test_kaja_backend_is_bound_to_maintained_source(self) -> None:
        entries = deepcopy(self.entries)
        kaja = next(row for row in entries if row["replay_backend"] == "op-maine-kaja-v514")
        kaja["replay_backend"] = "op-maine-mmd-v513"
        with self.assertRaisesRegex(ValueError, "MMD backend does not compile"):
            self.check(entries)


    def test_mode_backend_is_bound_to_maintained_source(self) -> None:
        entries = deepcopy(self.entries)
        mode = next(row for row in entries if row["replay_backend"] == "op-maine-mode-v515")
        mode["replay_backend"] = "op-maine-kaja-v514"
        with self.assertRaisesRegex(ValueError, "KAJA backend does not compile"):
            self.check(entries)


    def test_delay_backend_is_bound_to_maintained_source(self) -> None:
        entries = deepcopy(self.entries)
        delay = next(row for row in entries if row["replay_backend"] == "op-maine-delay-v516")
        delay["replay_backend"] = "op-maine-mode-v515"
        with self.assertRaisesRegex(ValueError, "mode backend does not compile"):
            self.check(entries)

    def test_maine_score_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        score = next(row for row in entries if row["replay_backend"] == "maine-score-insert-v543")
        score["replay_backend"] = "op-maine-delay-v516"
        with self.assertRaisesRegex(ValueError, "delay backend does not compile"):
            self.check(entries)

        entries = deepcopy(self.entries)
        score = next(row for row in entries if row["replay_backend"] == "maine-score-put-v544")
        score["replay_backend"] = "maine-score-insert-v543"
        with self.assertRaisesRegex(ValueError, "score-insert backend does not compile"):
            self.check(entries)


if __name__ == "__main__":
    unittest.main()
