from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

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

    def test_completed_backend_discards_only_replay_worktrees(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            saved = Path(temp)
            for label in ("a", "b"):
                source = saved / label / "op" / "source"
                source.mkdir(parents=True)
                (source / "generated.obj").write_bytes(b"scratch")
            (saved / "receipt.json").write_text("{}")
            (saved / "compile.log").write_text("ok")
            (saved / "a-op.exe").write_bytes(b"candidate-a")
            (saved / "b-op.exe").write_bytes(b"candidate-b")
            self.assertEqual(
                acceptance.discard_backend_worktrees(saved),
                ["a/op/source", "b/op/source", "a-op.exe", "b-op.exe"],
            )
            self.assertTrue((saved / "receipt.json").is_file())
            self.assertTrue((saved / "compile.log").is_file())
            self.assertFalse((saved / "a/op/source").exists())
            self.assertFalse((saved / "b/op/source").exists())
            self.assertFalse((saved / "a-op.exe").exists())
            self.assertFalse((saved / "b-op.exe").exists())

    def test_backend_cleanup_rejects_source_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            saved = Path(temp) / "saved"
            external = Path(temp) / "external"
            (saved / "a/op").mkdir(parents=True)
            external.mkdir()
            (saved / "a/op/source").symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "unsafe decoded backend worktree"):
                acceptance.discard_backend_worktrees(saved)
            self.assertTrue(external.is_dir())

    def test_failed_raw_comparison_keeps_worktree_for_diagnosis(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            source = output / "probe/a/op/source"
            source.mkdir(parents=True)
            entry = {"artifact": "th04-op", "source": "src/op/score/clear.cpp",
                     "replay_backend": "probe"}
            with (patch.object(acceptance, "verified_target", return_value=(b"", "packed", "decoded")),
                  patch.object(acceptance, "backend", return_value=([b"", b""], 0, {})),
                  patch.object(acceptance, "compare_extent", return_value={"difference_count": 1}),
                  patch.object(acceptance, "require_exact_zero", side_effect=RuntimeError("raw mismatch"))):
                with self.assertRaisesRegex(RuntimeError, "raw mismatch"):
                    acceptance.replay("th04-op", [entry], output)
            self.assertTrue(source.is_dir())

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

    def test_input_wait_backend_is_bound_to_maintained_source_and_extent(self) -> None:
        entries = deepcopy(self.entries)
        wait = next(row for row in entries if row["replay_backend"] == "op-maine-input-wait-v565")
        wait["replay_backend"] = "op-maine-delay-v516"
        with self.assertRaisesRegex(ValueError, "delay backend does not compile"):
            self.check(entries)

    def test_se_reset_backend_is_bound_to_maintained_source_and_extent(self) -> None:
        entries = deepcopy(self.entries)
        reset = next(row for row in entries if row["replay_backend"] == "op-maine-se-reset-v581")
        reset["producer_size"] = "0xB"
        with self.assertRaisesRegex(ValueError, "sound-effect reset backend does not compile"):
            self.check(entries)

    def test_leaf_backends_are_bound_to_maintained_source_and_extent(self) -> None:
        cases = (
            ("maine-box-bg-put-v647", "0xC3D", "box-bg-put"),
            ("maine-cutscene-script-free-v582", "0xC3D", "cutscene-script-free"),
            ("maine-box-bg-free-v585", "0xC3D", "box-bg-free"),
            ("maine-script-param-first-v649", "0xC3D", "script-param-first"),
            ("maine-script-param-second-v590", "0xC3D", "script-param-second"),
            ("maine-cutscene-script-load-v614", "0xC3D", "cutscene-script-load"),
            ("maine-cfg-resident-v604", "0x238", "cfg-resident"),
            ("maine-game-exit-exec-v608", "0x238", "game-exit-exec"),
            ("maine-end-animate-v616", "0x238", "end-animate"),
            ("op-start-extra-v662", "0xD52", "start-extra"),
            ("op-start-game-v666", "0xD52", "start-game"),
            ("op-cfg-save-exit-v668", "0xD52", "cfg-save-exit"),
            ("op-cfg-save-v673", "0xD52", "cfg-save"),
            ("op-cfg-load-v680", "0xD52", "cfg-load"),
            ("op-game-init-op-v671", "0x81", "game-init-op"),
            ("op-menu-sel-update-v664", "0xD52", "menu-selection-update"),
            ("op-main-cdg-free-v583", "0x2C6", "main-CDG-free"),
            ("op-main-cdg-load-v602", "0x2C6", "main-CDG-load"),
            ("op-nopoly-free-v584", "0x6A4", "nopoly-free"),
            ("op-nopoly-snap-v606", "0x6A4", "nopoly-snap"),
            ("op-frame-delay-2-v587", "0x16", "frame-delay-2"),
            ("op-raise-bg-free-v588", "0xAB2", "raise-bg-free"),
            ("op-playchar-title-box-v638", "0xAB2", "playchar-title-box"),
            ("op-playchar-titles-v684", "0xAB2", "playchar-titles"),
            ("op-pic-darken-v640", "0xAB2", "pic-darken"),
            ("op-shottype-menu-initial-v660", "0xAB2", "shottype-menu-initial"),
            ("op-game-exit-to-dos-v592", "0x1A", "game-exit-to-dos"),
            ("op-tracklist-put-both-v594", "0x6A4", "tracklist-put-both"),
            ("op-track-put-both-v636", "0x6A4", "track-put-both"),
            ("op-polygon-build-v678", "0x6A4", "polygon-build"),
            ("op-cmt-unput-v598", "0x6A4", "cmt-unput"),
            ("op-cmt-fadein-v600", "0x6A4", "cmt-fadein"),
            ("op-cmt-put-v618", "0x6A4", "cmt-put"),
            ("op-cmt-load-v620", "0x6A4", "cmt-load"),
            ("op-cmt-transition-v622", "0x6A4", "cmt-transition"),
            ("op-music-update-flip-v610", "0x6A4", "music-update-flip"),
            ("op-help-put-v596", "0x5A5", "help-put"),
            ("op-rollup-v612", "0x5A5", "rollup"),
            ("op-bgm-choice-v624", "0x5A5", "BGM-choice"),
            ("op-se-choice-v626", "0x5A5", "SE-choice"),
            ("op-window-rollup-put-v628", "0x5A5", "window-rollup-put"),
            ("op-window-dropdown-put-v632", "0x5A5", "window-dropdown-put"),
            ("op-singleline-v634", "0x5A5", "singleline"),
            ("op-dropdown-v630", "0x5A5", "dropdown"),
        )
        for backend, bad_size, message in cases:
            entries = deepcopy(self.entries)
            row = next(item for item in entries if item["replay_backend"] == backend)
            row["producer_size"] = bad_size
            with self.subTest(backend=backend):
                with self.assertRaisesRegex(ValueError, message):
                    self.check(entries)

    def test_vector_math_backend_is_bound_to_maintained_source_and_extent(self) -> None:
        entries = deepcopy(self.entries)
        vector = next(row for row in entries
                      if row["replay_backend"] == "op-maine-vector-math-v570")
        vector["producer_size"] = "0x5F"
        with self.assertRaisesRegex(ValueError, "vector-math backend does not compile"):
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
        input_wait = acceptance.backend_command(
            "op-maine-input-wait-v565", saved, artifact="th04-op"
        )
        self.assertEqual(input_wait[1], "scripts/probes/replay_th04_shared_input_wait.py")
        self.assertIn("th04-op", input_wait)
        self.assertIn("--retain-candidates", input_wait)
        se_reset = acceptance.backend_command(
            "op-maine-se-reset-v581", saved, artifact="th04-op"
        )
        self.assertEqual(se_reset[1], "scripts/probes/replay_th04_shared_se_reset.py")
        self.assertIn("th04-op", se_reset)
        self.assertIn("--retain-candidates", se_reset)
        vector_math = acceptance.backend_command(
            "op-maine-vector-math-v570", saved, artifact="th04-maine"
        )
        self.assertEqual(vector_math[1], "scripts/probes/replay_th04_shared_vector_math.py")
        self.assertIn("th04-maine", vector_math)
        self.assertIn("--retain-candidates", vector_math)
        with self.assertRaisesRegex(ValueError, "requires one OP/MAINE artifact"):
            acceptance.backend_command("op-maine-vector-math-v570", saved, artifact="th04-zun")
        self.assertEqual(
            acceptance.backend_command("maine-score-insert-v543", saved)[1],
            "scripts/probes/replay_th04_maine_score_insert.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-score-put-v544", saved)[1],
            "scripts/probes/replay_th04_maine_score_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-cutscene-script-free-v582", saved)[1],
            "scripts/probes/replay_th04_maine_cutscene_script_free.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-box-bg-free-v585", saved)[1],
            "scripts/probes/replay_th04_maine_box_bg_free.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-script-param-second-v590", saved)[1],
            "scripts/probes/replay_th04_maine_script_param_second.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-cutscene-script-load-v614", saved)[1],
            "scripts/probes/replay_th04_maine_script_load.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-cfg-resident-v604", saved)[1],
            "scripts/probes/replay_th04_maine_cfg_resident_ptr.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-game-exit-exec-v608", saved)[1],
            "scripts/probes/replay_th04_maine_game_exit_and_exec.py",
        )
        maine_exit = acceptance.backend_command("maine-game-exit-v654", saved)
        self.assertEqual(maine_exit[1], "scripts/probes/replay_th04_op_maine_game_exit.py")
        self.assertEqual(maine_exit[2:4], ["--artifact", "maine"])
        self.assertEqual(
            acceptance.backend_command("maine-game-init-main-v656", saved)[1],
            "scripts/probes/replay_th04_maine_game_init_main.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-end-animate-v616", saved)[1],
            "scripts/probes/replay_th04_maine_end_animate.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-start-extra-v662", saved)[1],
            "scripts/probes/replay_th04_op_start_extra.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-start-game-v666", saved)[1],
            "scripts/probes/replay_th04_op_start_game.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-cfg-save-exit-v668", saved)[1],
            "scripts/probes/replay_th04_op_cfg_save_exit.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-cfg-save-v673", saved)[1],
            "scripts/probes/replay_th04_op_cfg_save.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-cfg-load-v680", saved)[1],
            "scripts/probes/replay_th04_op_cfg_load.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-game-init-op-v671", saved)[1],
            "scripts/probes/replay_th04_op_game_init_op.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-menu-sel-update-v664", saved)[1],
            "scripts/probes/replay_th04_op_menu_sel_update.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-stage-put-v545", saved)[1],
            "scripts/probes/replay_th04_op_stage_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-main-cdg-free-v583", saved)[1],
            "scripts/probes/replay_th04_op_main_cdg_free.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-main-cdg-load-v602", saved)[1],
            "scripts/probes/replay_th04_op_main_cdg_load.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-nopoly-free-v584", saved)[1],
            "scripts/probes/replay_th04_op_nopoly_free.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-nopoly-snap-v606", saved)[1],
            "scripts/probes/replay_th04_op_nopoly_snap.py",
        )
        frame2 = acceptance.backend_command("op-frame-delay-2-v587", saved)
        self.assertEqual(frame2[1], "scripts/probes/replay_th04_op_frame_delay_2.py")
        self.assertIn("--retain-candidates", frame2)
        self.assertEqual(
            acceptance.backend_command("op-raise-bg-free-v588", saved)[1],
            "scripts/probes/replay_th04_op_raise_bg_free.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-playchar-title-box-v638", saved)[1],
            "scripts/probes/replay_th04_op_playchar_title_box_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-playchar-titles-v684", saved)[1],
            "scripts/probes/replay_th04_op_playchar_titles_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-pic-darken-v640", saved)[1],
            "scripts/probes/replay_th04_op_pic_darken.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-shottype-menu-initial-v660", saved)[1],
            "scripts/probes/replay_th04_op_shottype_menu_initial.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-playchar-menu-initial-v658", saved)[1],
            "scripts/probes/replay_th04_op_playchar_menu_initial.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-game-exit-to-dos-v592", saved)[1],
            "scripts/probes/replay_th04_op_game_exit_to_dos.py",
        )
        op_exit = acceptance.backend_command("op-game-exit-v654", saved)
        self.assertEqual(op_exit[1], "scripts/probes/replay_th04_op_maine_game_exit.py")
        self.assertEqual(op_exit[2:4], ["--artifact", "op"])
        self.assertEqual(
            acceptance.backend_command("op-tracklist-put-both-v594", saved)[1],
            "scripts/probes/replay_th04_op_tracklist_put_both.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-track-put-both-v636", saved)[1],
            "scripts/probes/replay_th04_op_track_put_both.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-polygon-build-v678", saved)[1],
            "scripts/probes/replay_th04_op_polygon_build.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-cmt-unput-v598", saved)[1],
            "scripts/probes/replay_th04_op_cmt_unput_both_animate.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-cmt-fadein-v600", saved)[1],
            "scripts/probes/replay_th04_op_cmt_fadein_both_animate.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-cmt-put-v618", saved)[1],
            "scripts/probes/replay_th04_op_cmt_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-cmt-load-v620", saved)[1],
            "scripts/probes/replay_th04_op_cmt_load.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-cmt-transition-v622", saved)[1],
            "scripts/probes/replay_th04_op_cmt_load_unput_and_put_both_animate.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-music-update-flip-v610", saved)[1],
            "scripts/probes/replay_th04_op_music_update_render_and_flip.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-help-put-v596", saved)[1],
            "scripts/probes/replay_th04_op_help_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-rollup-v612", saved)[1],
            "scripts/probes/replay_th04_op_rollup.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-bgm-choice-v624", saved)[1],
            "scripts/probes/replay_th04_op_bgm_choice_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-se-choice-v626", saved)[1],
            "scripts/probes/replay_th04_op_se_choice_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-window-rollup-put-v628", saved)[1],
            "scripts/probes/replay_th04_op_window_rollup_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-window-dropdown-put-v632", saved)[1],
            "scripts/probes/replay_th04_op_window_dropdown_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-singleline-v634", saved)[1],
            "scripts/probes/replay_th04_op_singleline.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-dropdown-v630", saved)[1],
            "scripts/probes/replay_th04_op_dropdown.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-setup-menu-v676", saved)[1],
            "scripts/probes/replay_th04_op_setup_menu.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-place-put-v552", saved)[1],
            "scripts/probes/replay_th04_op_place_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("op-rank-render-v553", saved)[1],
            "scripts/probes/replay_th04_op_rank_render.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-stage-put-v547", saved)[1],
            "scripts/probes/replay_th04_maine_stage_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-name-cursor-v548", saved)[1],
            "scripts/probes/replay_th04_maine_name_cursor.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-place-row-v549", saved)[1],
            "scripts/probes/replay_th04_maine_place_row.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-places-v550", saved)[1],
            "scripts/probes/replay_th04_maine_places.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-alphabet-cursor-v551", saved)[1],
            "scripts/probes/replay_th04_maine_alphabet_cursor.py",
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

    def test_maine_scoredat_recreate_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-scoredat-recreate-v580")
        owner["producer_offset"] = "0xC205"
        owner["producer_size"] = "0xA8"
        with self.assertRaisesRegex(ValueError, "score-file regeneration backend does not compile"):
            self.check(entries)

        command = acceptance.backend_command(
            "maine-scoredat-recreate-v580", ROOT / ".analysis/reconstruction/probes/test"
        )
        self.assertEqual(command[1], "scripts/probes/replay_th04_maine_scoredat_recreate.py")
        self.assertIn("--retain-candidates", command)

    def test_maine_hiscore_save_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-hiscore-save-v682")
        owner["source"] = "src/maine/score/load_for.cpp"
        with self.assertRaisesRegex(ValueError, "missing or mismatched maintained source"):
            self.check(entries)

        command = acceptance.backend_command(
            "maine-hiscore-save-v682", ROOT / ".analysis/reconstruction/probes/test"
        )
        self.assertEqual(command[1], "scripts/probes/replay_th04_maine_hiscore_save.py")

    def test_maine_script_op_backend_is_artifact_source_and_producer_bound(self) -> None:
        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-script-op-v685")
        owner["source"] = "src/maine/cutscene/box_animate.cpp"
        with self.assertRaisesRegex(ValueError, "missing or mismatched maintained source"):
            self.check(entries)

        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-script-op-v685")
        owner["producer_offset"] = "0xA293"
        with self.assertRaisesRegex(ValueError, "script-op backend does not compile"):
            self.check(entries)

        self.assertEqual(
            acceptance.backend_command(
                "maine-script-op-v685",
                ROOT / ".analysis/reconstruction/probes/test",
            )[1],
            "scripts/probes/replay_th04_maine_script_op.py",
        )

    def test_maine_cutscene_animate_backend_is_artifact_source_and_producer_bound(self) -> None:
        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-cutscene-animate-v687")
        owner["source"] = "src/maine/cutscene/script_op.inl"
        with self.assertRaisesRegex(ValueError, "missing or mismatched maintained source"):
            self.check(entries)

        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-cutscene-animate-v687")
        owner["producer_offset"] = "0xA293"
        with self.assertRaisesRegex(ValueError, "cutscene-animate backend does not compile"):
            self.check(entries)

        self.assertEqual(
            acceptance.backend_command(
                "maine-cutscene-animate-v687",
                ROOT / ".analysis/reconstruction/probes/test",
            )[1],
            "scripts/probes/replay_th04_maine_cutscene_animate.py",
        )

    def test_maine_box_animate_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-box-animate-v573")
        owner["source"] = "src/maine/score/put.cpp"
        with self.assertRaisesRegex(ValueError, "missing or mismatched maintained source"):
            self.check(entries)

        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-box-animate-v573")
        owner["producer_offset"] = "0xA293"
        with self.assertRaisesRegex(ValueError, "box-animate backend does not compile"):
            self.check(entries)

        entries = deepcopy(self.entries)
        owner = next(row for row in entries
                     if row["replay_backend"] == "maine-box-animate-v573")
        owner["replay_backend"] = "maine-score-put-v544"
        with self.assertRaisesRegex(ValueError, "score-put backend does not compile"):
            self.check(entries)
        self.assertEqual(
            acceptance.backend_command("maine-box-animate-v573",
                                       ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_maine_box_animate.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-pic-copy-to-other-v651",
                                       ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_maine_pic_copy_to_other.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-cursor-advance-v643",
                                       ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_maine_cursor_advance.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-box-bg-put-v647",
                                       ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_maine_box_bg_put.py",
        )
        self.assertEqual(
            acceptance.backend_command("maine-script-param-first-v649",
                                       ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_maine_script_param_first.py",
        )

    def test_op_stage_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        stage = next(row for row in entries if row["replay_backend"] == "op-stage-put-v545")
        stage["replay_backend"] = "maine-score-put-v544"
        with self.assertRaisesRegex(ValueError, "score-put backend does not compile"):
            self.check(entries)

    def test_op_score_load_both_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        owner = next(row for row in entries if row["replay_backend"] == "op-score-load-both-v558")
        owner["source"] = "src/op/score/stage.cpp"
        with self.assertRaisesRegex(ValueError, "missing or mismatched maintained source"):
            self.check(entries)

        entries = deepcopy(self.entries)
        owner = next(row for row in entries if row["replay_backend"] == "op-score-load-both-v558")
        owner["replay_backend"] = "op-stage-put-v545"
        with self.assertRaisesRegex(ValueError, "OP stage-put backend does not compile"):
            self.check(entries)
        self.assertEqual(
            acceptance.backend_command("op-score-load-both-v558", ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_op_score_load_both.py",
        )

    def test_op_scores_put_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        owner = next(row for row in entries if row["replay_backend"] == "op-scores-put-v559")
        owner["source"] = "src/op/score/stage.cpp"
        with self.assertRaisesRegex(ValueError, "missing or mismatched maintained source"):
            self.check(entries)

        entries = deepcopy(self.entries)
        owner = next(row for row in entries if row["replay_backend"] == "op-scores-put-v559")
        owner["replay_backend"] = "op-score-load-both-v558"
        with self.assertRaisesRegex(ValueError, "OP high-score loader backend does not compile"):
            self.check(entries)
        self.assertEqual(
            acceptance.backend_command("op-scores-put-v559", ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_op_scores_put.py",
        )

    def test_op_scoredat_recreate_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        owner = next(row for row in entries if row["replay_backend"] == "op-scoredat-recreate-v561")
        owner["source"] = "src/op/score/stage.cpp"
        with self.assertRaisesRegex(ValueError, "missing or mismatched maintained source"):
            self.check(entries)

        entries = deepcopy(self.entries)
        owner = next(row for row in entries if row["replay_backend"] == "op-scoredat-recreate-v561")
        owner["replay_backend"] = "op-scores-put-v559"
        with self.assertRaisesRegex(ValueError, "OP scores-put backend does not compile"):
            self.check(entries)
        self.assertEqual(
            acceptance.backend_command("op-scoredat-recreate-v561", ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_op_scoredat_recreate.py",
        )

    def test_op_place_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        place = next(row for row in entries if row["replay_backend"] == "op-place-put-v552")
        place["replay_backend"] = "op-stage-put-v545"
        with self.assertRaisesRegex(ValueError, "OP stage-put backend does not compile"):
            self.check(entries)

    def test_op_rank_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        rank = next(row for row in entries if row["replay_backend"] == "op-rank-render-v553")
        rank["replay_backend"] = "op-place-put-v552"
        with self.assertRaisesRegex(ValueError, "OP place-put backend does not compile"):
            self.check(entries)

    def test_op_regist_menu_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        menu = next(row for row in entries if row["replay_backend"] == "op-regist-menu-v556")
        menu["replay_backend"] = "op-rank-render-v553"
        with self.assertRaisesRegex(ValueError, "OP rank-render backend does not compile"):
            self.check(entries)
        self.assertEqual(
            acceptance.backend_command("op-regist-menu-v556", ROOT / ".analysis/reconstruction/probes/test")[1],
            "scripts/probes/replay_th04_op_regist_view_menu.py",
        )

    def test_op_clear_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        clear = next(row for row in entries if row["replay_backend"] == "op-clear-sprites-v554")
        clear["replay_backend"] = "op-rank-render-v553"
        with self.assertRaisesRegex(ValueError, "OP rank-render backend does not compile"):
            self.check(entries)

    def test_maine_stage_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        stage = next(row for row in entries if row["replay_backend"] == "maine-stage-put-v547")
        stage["replay_backend"] = "op-stage-put-v545"
        with self.assertRaisesRegex(ValueError, "OP stage-put backend does not compile"):
            self.check(entries)

    def test_maine_name_cursor_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        cursor = next(row for row in entries if row["replay_backend"] == "maine-name-cursor-v548")
        cursor["replay_backend"] = "maine-stage-put-v547"
        with self.assertRaisesRegex(ValueError, "MAINE stage-put backend does not compile"):
            self.check(entries)

    def test_maine_place_row_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        row = next(row for row in entries if row["replay_backend"] == "maine-place-row-v549")
        row["replay_backend"] = "maine-name-cursor-v548"
        with self.assertRaisesRegex(ValueError, "MAINE name-cursor backend does not compile"):
            self.check(entries)

    def test_maine_places_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        places = next(row for row in entries if row["replay_backend"] == "maine-places-v550")
        places["replay_backend"] = "maine-place-row-v549"
        with self.assertRaisesRegex(ValueError, "MAINE place-row backend does not compile"):
            self.check(entries)

    def test_maine_alphabet_cursor_backend_is_artifact_and_source_bound(self) -> None:
        entries = deepcopy(self.entries)
        cursor = next(row for row in entries if row["replay_backend"] == "maine-alphabet-cursor-v551")
        cursor["replay_backend"] = "maine-places-v550"
        with self.assertRaisesRegex(ValueError, "MAINE places backend does not compile"):
            self.check(entries)


if __name__ == "__main__":
    unittest.main()
