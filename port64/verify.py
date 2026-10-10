#!/usr/bin/env python3
"""Verify Linux and Windows x64 TH04 portable builds against one legal HDI."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


PORT_FILES = (
    "port64/verify_resident_sound_join.py",
    "port64/resident_sound_frontend_checks.inl",
    "port64/verify_pmd_resident.py",
    "port64/pmd_resident.hpp",
    "port64/pmd_resident.cpp",
    "port64/pmd_resident_checks.cpp",
    "port64/pmd_pcm.hpp",
    "port64/pmd_pcm.cpp",
    "port64/pmd_pcm_checks.cpp",
    "port64/verify_pmd_pcm.py",
    "port64/vendor/ymfm/LICENSE",
    "port64/vendor/ymfm/UPSTREAM.json",
    "port64/vendor/ymfm/src/ymfm.h",
    "port64/vendor/ymfm/src/ymfm_fm.h",
    "port64/vendor/ymfm/src/ymfm_fm.ipp",
    "port64/vendor/ymfm/src/ymfm_opn.h",
    "port64/vendor/ymfm/src/ymfm_opn.cpp",
    "port64/vendor/ymfm/src/ymfm_ssg.h",
    "port64/vendor/ymfm/src/ymfm_ssg.cpp",
    "port64/vendor/ymfm/src/ymfm_adpcm.h",
    "port64/vendor/ymfm/src/ymfm_adpcm.cpp",
    "port64/pmd_clock.hpp",
    "port64/pmd_clock.cpp",
    "port64/pmd_clock_checks.cpp",
    "port64/verify_pmd_clock.py",
    "port64/pmd_timer_player.hpp",
    "port64/pmd_timer_player.cpp",
    "port64/pmd_timer_player_checks.cpp",
    "port64/verify_pmd_timer_player.py",
    "port64/pmd_fm3_checks.cpp",
    "port64/startup_frontend_checks.inl",
    "port64/verify_startup_join.py",
    "port64/op_startup.hpp",
    "port64/op_startup.cpp",
    "port64/op_startup_checks.cpp",
    "port64/verify_op_startup.py",
    "port64/verify_op_startup_pixels.py",
    "port64/verify_startup_pixels_windows.ps1",
    "port64/verify_pmd_fm3.py",
    "port64/pmd_rhythm_checks.cpp",
    "port64/verify_pmd_rhythm.py",
    "port64/pmd_rhythm.hpp",
    "port64/pmd_rhythm.cpp",
    "port64/pmd_commands_checks.cpp",
    "port64/verify_pmd_commands.py",
    "port64/pmd_combined_checks.cpp",
    "port64/verify_pmd_combined.py",
    "port64/pmd_trace_state.hpp",
    "port64/pmd_trace_state.cpp",
    "port64/pmd_musical_lfo.hpp",
    "port64/pmd_musical_ssg.hpp",
    "port64/pmd_musical_ssg.cpp",
    "port64/pmd_musical_ssg_checks.cpp",
    "port64/verify_pmd_musical_ssg.py",
    "port64/pmd_fm_player.hpp",
    "port64/pmd_fm_player.cpp",
    "port64/pmd_fm_player_checks.cpp",
    "port64/verify_pmd_fm_player.py",
    "port64/pmd_musical_fm.hpp",
    "port64/pmd_musical_fm.cpp",
    "port64/pmd_musical_fm_checks.cpp",
    "port64/verify_pmd_musical_fm.py",
    "port64/pmd_fm_effects.hpp",
    "port64/pmd_fm_effects.cpp",
    "port64/pmd_fm_checks.cpp",
    "port64/verify_pmd_fm.py",
    "port64/verify_windows_current.ps1",
    "port64/pmd_sequence.hpp",
    "port64/pmd_ssg_effects.hpp",
    "port64/pmd_ssg_effects.cpp",
    "port64/pmd_ssg_checks.cpp",
    "port64/verify_pmd_ssg.py",
    "port64/pmd_sequence.cpp",
    "port64/pmd_sequence_checks.cpp",
    "port64/verify_pmd_sequence.py",
    "port64/sound_scenes.hpp",
    "port64/sound_scenes.cpp",
    "port64/sound_scenes_contracts.cpp",
    "port64/sound_scene_frontend_checks.inl",
    "port64/verify_sound_scenes.py",
    "port64/verify_pmd_driver.py",
    "port64/verify_pmd_controls.py",
    "port64/sound_runtime.hpp",
    "port64/sound_runtime.cpp",
    "port64/sound_runtime_contracts.cpp",
    "port64/sound_frontend_checks.inl",
    "port64/verify_sound_join.py",
    "port64/beeper.hpp",
    "port64/beeper.cpp",
    "port64/beeper_contracts.cpp",
    "port64/verify_beeper.py",
    "port64/sound_control.hpp",
    "port64/sound_control.cpp",
    "port64/sound_control_contracts.cpp",
    "port64/verify_sound_control.py",
    "port64/op_setup.hpp",
    "port64/op_setup.cpp",
    "port64/op_setup_text.inl",
    "port64/op_setup_contracts.cpp",
    "port64/verify_op_setup.py",
    "port64/op_setup_frontend_checks.inl",
    "port64/verify_op_setup_join.py",
    "port64/verify_op_setup_pixels.py",
    "port64/configuration.hpp",
    "port64/configuration.cpp",
    "port64/configuration_contracts.cpp",
    "port64/verify_configuration.py",
    "port64/configuration_frontend_checks.inl",
    "port64/verify_configuration_join.py",
    "port64/demo.hpp",
    "port64/demo.cpp",
    "port64/demo_contracts.cpp",
    "port64/demo_frontend_checks.inl",
    "port64/verify_demo.py",
    "port64/verify_demo_join.py",
    "port64/op_music.hpp",
    "port64/op_music.cpp",
    "port64/op_music_contracts.cpp",
    "port64/verify_op_music.py",
    "port64/verify_op_music_pixels.py",
    "port64/op_music_frontend_checks.inl",
    "port64/verify_op_music_join.py",
    "port64/verify_main_hud_join.py",
    "port64/hud.hpp",
    "port64/hud.cpp",
    "port64/hud_contracts.cpp",
    "port64/verify_hud.py",
    "port64/super_wave.hpp",
    "port64/super_wave.cpp",
    "port64/super_wave_contracts.cpp",
    "port64/verify_super_wave.py",
    "port64/gengetsu_render.hpp",
    "port64/gengetsu_render.cpp",
    "port64/verify_gengetsu_graphics.py",
    "port64/gengetsu_contracts.cpp",
    "port64/verify_gengetsu.py",
    "port64/gengetsu.hpp",
    "port64/gengetsu.cpp",
    "port64/gengetsu_frontend_checks.inl",
    "port64/extra_maine_frontend_checks.inl",
    "port64/verify_extra_maine_join.py",
    "port64/verify_fresh_main.py",
    "port64/op_score_frontend_checks.inl",
    "port64/verify_op_score_join.py",
    "port64/op_score.hpp",
    "port64/op_ranking.hpp",
    "port64/op_ranking.cpp",
    "port64/op_ranking_contracts.cpp",
    "port64/verify_op_ranking.py",
    "port64/verify_op_ranking_pixels.py",
    "port64/verify_op_ranking_join.py",
    "port64/op_ranking_frontend_checks.inl",
    "port64/op_score.cpp",
    "port64/op_score_contracts.cpp",
    "port64/verify_op_score.py",
    "port64/verify_extra_handoff.py",
    "port64/verify_extra_departure.py",
    "port64/verify_gengetsu_join.py",
    "port64/verify_mugetsu_join.py",
    "port64/verify_extra_dialog.py",
    "port64/extra_dialog.hpp",
    "port64/extra_dialog.cpp",
    "port64/mugetsu_frontend_checks.inl",
    "port64/verify_mugetsu.py",
    "port64/verify_mugetsu_graphics.py",
    "port64/mugetsu_contracts.cpp",
    "port64/mugetsu.hpp",
    "port64/mugetsu.cpp",
    "port64/stagex.hpp",
    "port64/stagex.cpp",
    "port64/midbossx.hpp",
    "port64/midbossx.cpp",
    "port64/extra_contracts.cpp",
    "port64/verify_extra.py",
    "port64/extra_frontend_checks.inl",
    "port64/maine_score_route.hpp",
    "port64/maine_score_route.cpp",
    "port64/maine_extra_route.hpp",
    "port64/maine_extra_route.cpp",
    "port64/score_route_frontend_checks.inl",
    "port64/bomb_frontend_checks.inl",
    "port64/verify_bomb_join.py",
    "port64/verify_score_route.py",
    "port64/verify_score_route_windows.ps1",
    "port64/gameover_frontend_checks.inl",
    "port64/verify_gameover_join.py",
    "port64/verify_gameover_join_windows.ps1",
    "port64/player_render.hpp",
    "port64/player_render.cpp",
    "port64/player_render_contracts.cpp",
    "port64/verify_player_render.py",
    "port64/verify_player_render_windows.ps1",
    "port64/verify_lifecycle_join.py",
    "port64/verify_lifecycle_join_windows.ps1",
    "port64/verify_gameover_render.py",
    "port64/verify_gameover_render_windows.ps1",
    "port64/gameover_render.hpp",
    "port64/gameover_render.cpp",
    "port64/player_bomb.hpp",
    "port64/player_bomb.cpp",
    "port64/player_bomb_contracts.cpp",
    "port64/verify_player_bomb.py",
    "port64/verify_player_bomb_pixels.py",
    "port64/verify_player_bomb_windows.ps1",
    "port64/verify_gameover.py",
    "port64/verify_gameover_scene.py",
    "port64/verify_main_score.py",
    "port64/verify_gameover_windows.ps1",
    "port64/gameover.hpp",
    "port64/gameover.cpp",
    "port64/gameover_contracts.cpp",
    "port64/verify_player_lifecycle_windows.ps1",
    "port64/player_lifecycle_contracts.cpp",
    "port64/verify_player_lifecycle.py",
    "port64/player_lifecycle.hpp",
    "port64/player_lifecycle.cpp",
    "port64/host_score.hpp",
    "port64/host_score.cpp",
    "port64/registration_scene.hpp",
    "port64/registration_scene.cpp",
    "port64/registration_scene_contracts.cpp",
    "port64/verify_registration_scene.py",
    "port64/verify_registration_join_windows.ps1",
    "port64/registration_render.hpp",
    "port64/registration_render.cpp",
    "port64/registration_render_contracts.cpp",
    "port64/verify_registration_render.py",
    "port64/verify_registration_render_windows.ps1",
    "port64/registration.hpp",
    "port64/registration.cpp",
    "port64/registration_contracts.cpp",
    "port64/verify_registration.py",
    "port64/verify_registration_windows.ps1",
    "port64/score_file.hpp",
    "port64/score_file.cpp",
    "port64/score_file_contracts.cpp",
    "port64/verify_score_file.py",
    "port64/verify_score_file_windows.ps1",
    "port64/verify_score_file_wrappers.py",
    "port64/maine_animation.hpp",
    "port64/maine_animation.cpp",
    "port64/congratulations.hpp",
    "port64/congratulations.cpp",
    "port64/congratulations_contracts.cpp",
    "port64/verify_congratulations.py",
    "port64/verdict_scene.hpp",
    "port64/verdict_scene.cpp",
    "port64/verify_verdict_pixels.py",
    "port64/verdict.hpp",
    "port64/verdict.cpp",
    "port64/verdict_contracts.cpp",
    "port64/verify_verdict.py",
    "port64/verify_verdict_windows.ps1",
    "port64/cdg_image.hpp",
    "port64/staff_roll.hpp",
    "port64/staff_roll.cpp",
    "port64/staff_roll_contracts.cpp",
    "port64/verify_staff_roll.py",
    "port64/verify_maine_join_windows.ps1",
    "port64/verify_ending_routes.py",
    "port64/verify_maine_join.py",
    "port64/run_statistics.hpp",
    "port64/run_statistics.cpp",
    "port64/maine_ending.hpp",
    "port64/maine_ending.cpp",
    "port64/cutscene.hpp",
    "port64/cutscene.cpp",
    "port64/cutscene_scene.hpp",
    "port64/cutscene_scene.cpp",
    "port64/cutscene_contracts.cpp",
    "port64/pi_image.hpp",
    "port64/pi_image.cpp",
    "port64/verify_cutscene.py",
    "port64/verify_cutscene_pixels.py",
    "port64/verify_cutscene_windows.ps1",
    "port64/verify_yuuka6_departure.py",
    "port64/yuuka6_pixels.cpp",
    "port64/verify_yuuka6_pixels.py",
    "port64/yuuka6_background.cpp",
    "port64/yuuka6_background.hpp",
    "port64/yuuka6_background_contracts.cpp",
    "port64/verify_yuuka6_background.py",
    "port64/yuuka6_foreground.hpp",
    "port64/yuuka6_foreground.cpp",
    "port64/yuuka6_render_contracts.cpp",
    "port64/verify_yuuka6_render.py",
    "port64/yuuka6_core.cpp",
    "port64/yuuka6_core_contracts.cpp",
    "port64/verify_yuuka6_core.py",
    "port64/yuuka6_attacks.cpp",
    "port64/yuuka6_attack_contracts.cpp",
    "port64/verify_yuuka6_attacks.py",
    "port64/yuuka6_entities.cpp",
    "port64/yuuka6_entities.hpp",
    "port64/yuuka6_entity_contracts.cpp",
    "port64/verify_yuuka6_entities.py",
    "port64/yuuka6.cpp",
    "port64/yuuka6.hpp",
    "port64/yuuka6_contracts.cpp",
    "port64/verify_yuuka6_motion.py",
    "port64/stage6.cpp",
    "port64/stage6.hpp",
    "port64/verify_stage6.py",
    "port64/verify_yuuka5_departure.py",
    "port64/yuuka5_render.cpp",
    "port64/verify_yuuka5_render.py",
    "port64/verify_yuuka5_pixels.py",
    "port64/yuuka5.hpp",
    "port64/yuuka5.cpp",
    "port64/yuuka5_contracts.cpp",
    "port64/verify_yuuka5.py",
    "port64/thick_lasers.hpp",
    "port64/thick_lasers.cpp",
    "port64/laser_contracts.cpp",
    "port64/verify_lasers.py",
    "port64/stage5.cpp",
    "port64/stage5.hpp",
    "port64/stage5_contracts.cpp",
    "port64/verify_stage5.py",
    "port64/marisa_render.cpp",
    "port64/verify_marisa_render.py",
    "port64/verify_marisa_pixels.py",
    "port64/marisa.hpp",
    "port64/marisa.cpp",
    "port64/marisa_contracts.cpp",
    "port64/verify_marisa.py",
    "port64/verify_marisa_setup.py",
    "port64/reimu.cpp",
    "port64/reimu_render.cpp",
    "port64/verify_reimu_render.py",
    "port64/verify_reimu_pixels.py",
    "port64/reimu.hpp",
    "port64/reimu_contracts.cpp",
    "port64/verify_reimu.py",
    "port64/verify_reimu_setup.py",
    "port64/verify_stage4_resources.py",
    "port64/stage4.cpp",
    "port64/stage4.hpp",
    "port64/verify_carpet.py",
    "port64/midboss4.cpp",
    "port64/midboss4.hpp",
    "port64/midboss4_contracts.cpp",
    "port64/verify_midboss4.py",
    "port64/verify_elly_render.py",
    "port64/verify_elly_setup.py",
    "port64/verify_elly.py",
    "port64/elly_contracts.cpp",
    "port64/elly.cpp",
    "port64/elly.hpp",
    "port64/verify_stage3_resources.py",
    "port64/midboss3.hpp",
    "port64/midboss3.cpp",
    "port64/midboss3_contracts.cpp",
    "port64/verify_midboss3.py",
    "port64/verify_kurumi_setup.py",
    "port64/kurumi.hpp",
    "port64/kurumi.cpp",
    "port64/kurumi_render.cpp",
    "port64/verify_kurumi_render.py",
    "port64/kurumi_contracts.cpp",
    "port64/verify_kurumi.py",
    "port64/verify_stage2_resources.py",
    "port64/midboss2.hpp",
    "port64/midboss2.cpp",
    "port64/midboss2_contracts.cpp",
    "port64/verify_midboss2.py",
    "port64/stage_session.hpp",
    "port64/stage_session.cpp",
    "port64/session_contracts.cpp",
    "port64/verify_session.py",
    "port64/stage_transition.hpp",
    "port64/stage_transition.cpp",
    "port64/transition_contracts.cpp",
    "port64/verify_transition.py",
    "port64/score.hpp",
    "port64/score.cpp",
    "port64/score_contracts.cpp",
    "port64/verify_score.py",
    "port64/stage_bonus.hpp",
    "port64/stage_bonus.cpp",
    "port64/bonus_text.hpp",
    "port64/bonus_contracts.cpp",
    "port64/verify_bonus.py",
    "port64/start-th04-port64.bat",
    "port64/verify_windows.ps1",
    "port64/dialog.hpp",
    "port64/dialog.cpp",
    "port64/dialog_contracts.cpp",
    "port64/verify_dialog.py",
    "port64/orange.hpp",
    "port64/orange.cpp",
    "port64/orange_render.cpp",
    "port64/circles.hpp",
    "port64/circles.cpp",
    "port64/orange_contracts.cpp",
    "port64/verify_orange.py",
    "port64/verify_orange_render.py",
    "port64/midboss.hpp",
    "port64/midboss.cpp",
    "port64/midboss_contracts.cpp",
    "port64/verify_midboss.py",
    "port64/CMakeLists.txt",
    "port64/application_state.cpp",
    "port64/application_state.hpp",
    "port64/bullet_geometry.cpp",
    "port64/bullet_geometry.hpp",
    "port64/contracts.cpp",
    "port64/enemy_contracts.cpp",
    "port64/enemy_bullets.cpp",
    "port64/enemy_bullets.hpp",
    "port64/effects.hpp",
    "port64/effects.cpp",
    "port64/effect_contracts.cpp",
    "port64/verify_effects.py",
    "port64/bullet_contracts.cpp",
    "port64/verify_bullets.py",
    "port64/enemy_system.cpp",
    "port64/enemy_system.hpp",
    "port64/stage_program.cpp",
    "port64/stage_program.hpp",
    "port64/verify_enemy.py",
    "port64/item_pool.cpp",
    "port64/item_pool.hpp",
    "port64/live_contracts.cpp",
    "port64/main_state.cpp",
    "port64/main_state.hpp",
    "port64/motion.cpp",
    "port64/motion.hpp",
    "port64/motion_tables.hpp",
    "port64/player_motion.cpp",
    "port64/player_motion.hpp",
    "port64/player_shots.cpp",
    "port64/player_shots.hpp",
    "port64/shot_contracts.cpp",
    "port64/verify_shots.py",
    "port64/sprite_sheet.cpp",
    "port64/sprite_sheet.hpp",
    "port64/stage_background.cpp",
    "port64/stage_background.hpp",
    "port64/probe_assets.py",
    "port64/verify_background.py",
    "port64/verify_movement.py",
    "port64/verify_window.py",
    "port64/item_system.cpp",
    "port64/item_system.hpp",
    "port64/main.cpp",
    "port64/menu_state.cpp",
    "port64/menu_state.hpp",
    "port64/mingw64-toolchain.cmake",
    "port64/random_lcg.cpp",
    "port64/random_lcg.hpp",
    "port64/random_ring.cpp",
    "port64/random_ring.hpp",
    "port64/selection_state.cpp",
    "port64/selection_state.hpp",
    "port64/smoke.py",
    "port64/verify.py",
    "port64/view.cpp",
    "port64/view.hpp",
    "src/main/bullet/group_types.hpp",
    "src/main/bullet/types.hpp",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest(root: Path) -> tuple[str, list[dict[str, object]]]:
    digest = hashlib.sha256()
    files: list[dict[str, object]] = []
    for relative_text in PORT_FILES:
        path = root / relative_text
        data = path.read_bytes()
        relative = relative_text.encode("utf-8")
        digest.update(len(relative).to_bytes(4, "little"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "little"))
        digest.update(data)
        files.append({
            "path": relative_text,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return digest.hexdigest(), files


def require_elf_x86_64(path: Path) -> None:
    data = path.read_bytes()[:64]
    if not (
        len(data) >= 20 and data[:4] == b"\x7fELF" and data[4] == 2 and
        int.from_bytes(data[18:20], "little") == 62
    ):
        raise ValueError(f"not an ELF64 x86-64 executable: {path}")


def require_pe_x86_64(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ValueError(f"not an MZ executable: {path}")
    header = int.from_bytes(data[0x3C:0x40], "little")
    if not (
        header <= len(data) - 26 and data[header:header + 4] == b"PE\0\0" and
        int.from_bytes(data[header + 4:header + 6], "little") == 0x8664 and
        int.from_bytes(data[header + 24:header + 26], "little") == 0x20B
    ):
        raise ValueError(f"not a PE32+ x86-64 executable: {path}")


def run(command: list[str], env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command, capture_output=True, text=True, check=True, env=env
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--linux-dir", type=Path, required=True)
    parser.add_argument("--windows-dir", type=Path, required=True)
    parser.add_argument("--hdi", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--windows-runner", default="wine")
    parser.add_argument("--font-bmp", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    initial_manifest_sha256 = source_manifest(root)[0]
    linux_dir = args.linux_dir.resolve()
    windows_dir = args.windows_dir.resolve()
    hdi = args.hdi.resolve()
    output = args.output.resolve()
    linux_main = linux_dir / "th04-port64"
    linux_contracts = linux_dir / "th04-port64-contracts"
    linux_live = linux_dir / "th04-port64-live-contracts"
    windows_live = windows_dir / "th04-port64-live-contracts.exe"
    windows_main = windows_dir / "th04-port64.exe"
    windows_contracts = windows_dir / "th04-port64-contracts.exe"
    linux_shots = linux_dir / "th04-port64-shot-contracts"
    windows_shots = windows_dir / "th04-port64-shot-contracts.exe"
    linux_enemies = linux_dir / "th04-port64-enemy-contracts"
    windows_enemies = windows_dir / "th04-port64-enemy-contracts.exe"
    linux_bullets = linux_dir / "th04-port64-bullet-contracts"
    windows_bullets = windows_dir / "th04-port64-bullet-contracts.exe"
    linux_effects = linux_dir / "th04-port64-effect-contracts"
    windows_effects = windows_dir / "th04-port64-effect-contracts.exe"
    linux_midboss = linux_dir / "th04-port64-midboss-contracts"
    windows_midboss = windows_dir / "th04-port64-midboss-contracts.exe"
    linux_orange = linux_dir / "th04-port64-orange-contracts"
    windows_orange = windows_dir / "th04-port64-orange-contracts.exe"
    linux_cutscene = linux_dir / "th04-port64-cutscene-contracts"
    windows_cutscene = windows_dir / "th04-port64-cutscene-contracts.exe"
    linux_dialog = linux_dir / "th04-port64-dialog-contracts"
    windows_dialog = windows_dir / "th04-port64-dialog-contracts.exe"
    linux_bonus = linux_dir / "th04-port64-bonus-contracts"
    windows_bonus = windows_dir / "th04-port64-bonus-contracts.exe"
    linux_score = linux_dir / "th04-port64-score-contracts"
    windows_score = windows_dir / "th04-port64-score-contracts.exe"
    linux_transition=linux_dir / "th04-port64-transition-contracts"
    windows_transition=windows_dir / "th04-port64-transition-contracts.exe"
    linux_midboss2=linux_dir / "th04-port64-midboss2-contracts"
    windows_midboss2=windows_dir / "th04-port64-midboss2-contracts.exe"
    linux_session=linux_dir / "th04-port64-session-contracts"
    windows_session=windows_dir / "th04-port64-session-contracts.exe"
    linux_midboss3=linux_dir / "th04-port64-midboss3-contracts"
    windows_midboss3=windows_dir / "th04-port64-midboss3-contracts.exe"
    linux_yuuka6_background=linux_dir / "th04-port64-yuuka6-background-contracts"
    windows_yuuka6_background=windows_dir / "th04-port64-yuuka6-background-contracts.exe"
    linux_yuuka6_render=linux_dir / "th04-port64-yuuka6-render-contracts"
    windows_yuuka6_render=windows_dir / "th04-port64-yuuka6-render-contracts.exe"
    linux_yuuka6_core=linux_dir / "th04-port64-yuuka6-core-contracts"
    windows_yuuka6_core=windows_dir / "th04-port64-yuuka6-core-contracts.exe"
    linux_yuuka6_attacks=linux_dir / "th04-port64-yuuka6-attack-contracts"
    windows_yuuka6_attacks=windows_dir / "th04-port64-yuuka6-attack-contracts.exe"
    linux_yuuka6_entities=linux_dir / "th04-port64-yuuka6-entity-contracts"
    windows_yuuka6_entities=windows_dir / "th04-port64-yuuka6-entity-contracts.exe"
    linux_yuuka6=linux_dir / "th04-port64-yuuka6-contracts"
    windows_yuuka6=windows_dir / "th04-port64-yuuka6-contracts.exe"
    linux_yuuka=linux_dir / "th04-port64-yuuka5-contracts"
    windows_yuuka=windows_dir / "th04-port64-yuuka5-contracts.exe"
    linux_lasers=linux_dir / "th04-port64-laser-contracts"
    windows_lasers=windows_dir / "th04-port64-laser-contracts.exe"
    linux_stage5=linux_dir / "th04-port64-stage5-contracts"
    windows_stage5=windows_dir / "th04-port64-stage5-contracts.exe"
    linux_marisa=linux_dir / "th04-port64-marisa-contracts"
    windows_marisa=windows_dir / "th04-port64-marisa-contracts.exe"
    linux_reimu=linux_dir / "th04-port64-reimu-contracts"
    windows_reimu=windows_dir / "th04-port64-reimu-contracts.exe"
    linux_midboss4=linux_dir / "th04-port64-midboss4-contracts"
    windows_midboss4=windows_dir / "th04-port64-midboss4-contracts.exe"
    linux_elly=linux_dir / "th04-port64-elly-contracts"
    windows_elly=windows_dir / "th04-port64-elly-contracts.exe"
    linux_kurumi=linux_dir / "th04-port64-kurumi-contracts"
    windows_kurumi=windows_dir / "th04-port64-kurumi-contracts.exe"
    for path in (linux_cutscene,linux_yuuka6_background,linux_yuuka6_render,linux_yuuka6_core,linux_yuuka6_attacks,linux_yuuka6_entities,linux_yuuka6,linux_yuuka,linux_lasers,linux_stage5,linux_marisa,linux_reimu,linux_midboss4,linux_elly,linux_midboss3,linux_kurumi,linux_midboss2,linux_session,linux_transition,linux_score,linux_bonus, linux_main, linux_contracts, linux_live, linux_shots, linux_enemies, linux_bullets, linux_effects, linux_midboss, linux_orange, linux_dialog):
        require_elf_x86_64(path)
    for path in (windows_cutscene,windows_yuuka6_background,windows_yuuka6_render,windows_yuuka6_core,windows_yuuka6_attacks,windows_yuuka6_entities,windows_yuuka6,windows_yuuka,windows_lasers,windows_stage5,windows_marisa,windows_reimu,windows_midboss4,windows_elly,windows_midboss3,windows_kurumi,windows_midboss2,windows_session,windows_transition,windows_score,windows_bonus, windows_main, windows_contracts, windows_live, windows_shots, windows_enemies, windows_bullets, windows_effects, windows_midboss, windows_orange, windows_dialog):
        require_pe_x86_64(path)

    runner_env = os.environ.copy()
    runner_env.setdefault("WINEDEBUG", "-all")
    linux_cutscene_output = run([str(linux_cutscene)])
    windows_cutscene_output = run([args.windows_runner,str(windows_cutscene)],env=runner_env)
    if linux_cutscene_output != "MAINE cutscene lifecycle contracts: PASS" or windows_cutscene_output != linux_cutscene_output:
        raise ValueError("MAINE cutscene lifecycle contracts failed")
    linux_yuuka6_background_output=run([str(linux_yuuka6_background)])
    windows_yuuka6_background_output=run([args.windows_runner,str(windows_yuuka6_background)],env=runner_env)
    if linux_yuuka6_background_output!="Stage 6 Yuuka background contracts PASS" or windows_yuuka6_background_output!=linux_yuuka6_background_output:
        raise ValueError("Yuuka6 background contracts did not pass on both hosts")
    linux_yuuka6_render_output=run([str(linux_yuuka6_render)])
    windows_yuuka6_render_output=run([args.windows_runner,str(windows_yuuka6_render)],env=runner_env)
    if linux_yuuka6_render_output!="Stage 6 Yuuka foreground contracts PASS" or windows_yuuka6_render_output!=linux_yuuka6_render_output:
        raise ValueError("Yuuka6 foreground contracts did not pass on both hosts")
    linux_yuuka6_core_output=run([str(linux_yuuka6_core)])
    windows_yuuka6_core_output=run([args.windows_runner,str(windows_yuuka6_core)],env=runner_env)
    if linux_yuuka6_core_output!="Stage 6 Yuuka core contracts PASS" or windows_yuuka6_core_output!=linux_yuuka6_core_output:raise ValueError("Yuuka6 core contracts failed")
    linux_yuuka6_attacks_output=run([str(linux_yuuka6_attacks)])
    windows_yuuka6_attacks_output=run([args.windows_runner,str(windows_yuuka6_attacks)],env=runner_env)
    if linux_yuuka6_attacks_output!="Stage 6 Yuuka attack contracts PASS" or windows_yuuka6_attacks_output!=linux_yuuka6_attacks_output:raise ValueError("Yuuka6 attack contracts failed")
    linux_yuuka6_entities_output=run([str(linux_yuuka6_entities)])
    windows_yuuka6_entities_output=run([args.windows_runner,str(windows_yuuka6_entities)],env=runner_env)
    if linux_yuuka6_entities_output!="Stage 6 Yuuka entity contracts PASS" or windows_yuuka6_entities_output!=linux_yuuka6_entities_output:raise ValueError("Yuuka6 entity contracts failed")
    linux_yuuka6_output=run([str(linux_yuuka6)])
    windows_yuuka6_output=run([args.windows_runner,str(windows_yuuka6)],env=runner_env)
    if linux_yuuka6_output!="Stage 6 Yuuka movement contracts PASS" or windows_yuuka6_output!=linux_yuuka6_output:raise ValueError("Yuuka6 movement contracts failed")
    linux_yuuka_output=run([str(linux_yuuka)])
    windows_yuuka_output=run([args.windows_runner,str(windows_yuuka)],env=runner_env)
    if linux_yuuka_output!="Stage 5 Yuuka contracts PASS" or windows_yuuka_output!=linux_yuuka_output:raise ValueError("Yuuka contracts failed")
    linux_laser_output=run([str(linux_lasers)])
    windows_laser_output=run([args.windows_runner,str(windows_lasers)],env=runner_env)
    if linux_laser_output!="Thick laser contracts PASS" or windows_laser_output!=linux_laser_output:raise ValueError("Thick laser contracts failed")
    linux_stage5_output=run([str(linux_stage5)])
    windows_stage5_output=run([args.windows_runner,str(windows_stage5)],env=runner_env)
    if linux_stage5_output!="Stage5 retained setup and star ownership: PASS" or windows_stage5_output!=linux_stage5_output:raise ValueError("Stage5 contracts failed")
    linux_marisa_output=run([str(linux_marisa)])
    windows_marisa_output=run([args.windows_runner,str(windows_marisa)],env=runner_env)
    if linux_marisa_output!="Stage 4 Marisa core contracts PASS" or windows_marisa_output!=linux_marisa_output:raise ValueError("Marisa core contracts failed")
    linux_reimu_output=run([str(linux_reimu)])
    windows_reimu_output=run([args.windows_runner,str(windows_reimu)],env=runner_env)
    if linux_reimu_output!="Stage 4 Reimu core contracts PASS" or windows_reimu_output!=linux_reimu_output:raise ValueError("Reimu core contracts failed")
    linux_midboss4_output=run([str(linux_midboss4)])
    windows_midboss4_output=run([args.windows_runner,str(windows_midboss4)],env=runner_env)
    if linux_midboss4_output!="Stage 4 midboss contracts PASS" or windows_midboss4_output!=linux_midboss4_output:raise ValueError("Stage4 midboss contracts failed")
    linux_elly_output=run([str(linux_elly)])
    windows_elly_output=run([args.windows_runner,str(windows_elly)],env=runner_env)
    if linux_elly_output!="Stage 3 Elly contracts PASS" or windows_elly_output!=linux_elly_output:
        raise ValueError("Elly contracts failed")
    linux_midboss3_output=run([str(linux_midboss3)])
    windows_midboss3_output=run([args.windows_runner,str(windows_midboss3)],env=runner_env)
    if linux_midboss3_output!="Stage 3 midboss contracts PASS" or windows_midboss3_output!="Stage 3 midboss contracts PASS":
        raise ValueError("Stage3 midboss contracts failed")
    linux_session_output=run([str(linux_session)])
    windows_session_output=run([args.windows_runner,str(windows_session)],env=runner_env)
    expected_session="stage_actors=REINITIALIZED pending_score=PRESERVED rng_draws=353 stage2_midboss=2600 pointer_bits=64"
    if linux_session_output!=expected_session or windows_session_output!=expected_session:
        raise ValueError("stage session actor contracts did not pass on both hosts")
    linux_contract_output = run([str(linux_contracts)])
    windows_contract_output = run(
        [args.windows_runner, str(windows_contracts)], env=runner_env
    )
    expected_contract_output = (
        "TH04 portable contracts: PASS pointer_bits=64 "
        "angle_bits=8 menu_state=OP handoff_state=OP_MAIN_MAINE "
        "selection=OP randring=SHARED_OVERLAP lcg=PROCESS_LOCAL32 "
        "items=FIXED_WIDTH_SAFE"
    )
    if linux_contract_output != expected_contract_output:
        raise ValueError("Linux portable contract did not pass")
    if windows_contract_output != expected_contract_output:
        raise ValueError("Windows portable contract did not pass")

    linux_live_output = run([str(linux_live)])
    windows_live_output = run([args.windows_runner, str(windows_live)], env=runner_env)
    expected_live = (
        "TH04 live MAIN contracts: PASS motion=Q12.4 player=HELD_KEYS "
        "items=32 sprites=BFNT pointer_bits=64"
    )
    if linux_live_output != expected_live or windows_live_output != expected_live:
        raise ValueError("live MAIN contracts did not pass on both hosts")
    expected_shots = "TH04 player shots: PASS routes=4 levels=10 pool=68 pointer_bits=64"
    linux_shot_output = run([str(linux_shots)])
    windows_shot_output = run([args.windows_runner,str(windows_shots)],env=runner_env)
    if linux_shot_output != expected_shots or windows_shot_output != expected_shots:
        raise ValueError("player shot contracts did not pass on both hosts")

    expected_enemies = "TH04 stage/enemy contracts: PASS pool=32 opcodes=52 pointer_bits=64"
    linux_enemy_output = run([str(linux_enemies)])
    windows_enemy_output = run([args.windows_runner,str(windows_enemies)],env=runner_env)
    if linux_enemy_output != expected_enemies or windows_enemy_output != expected_enemies:
        raise ValueError("stage enemy contracts did not pass on both hosts")

    expected_bullets = "TH04 enemy bullets: PASS pellets=240 large=200 motions=9 pointer_bits=64"
    linux_bullet_output = run([str(linux_bullets)])
    windows_bullet_output = run([args.windows_runner,str(windows_bullets)],env=runner_env)
    if linux_bullet_output != expected_bullets or windows_bullet_output != expected_bullets:
        raise ValueError("enemy bullet contracts did not pass on both hosts")
    expected_effects = "TH04 effects: PASS sparks=96 gathers=16 pointer_bits=64"
    linux_effect_output = run([str(linux_effects)])
    windows_effect_output = run([args.windows_runner,str(windows_effects)],env=runner_env)
    if linux_effect_output != expected_effects or windows_effect_output != expected_effects:
        raise ValueError("effect contracts did not pass on both hosts")
    linux_midboss2_output=run([str(linux_midboss2)])
    windows_midboss2_output=run([args.windows_runner,str(windows_midboss2)],env=runner_env)
    if linux_midboss2_output!="Stage 2 midboss contracts PASS" or windows_midboss2_output!=linux_midboss2_output:
        raise ValueError("Stage2 midboss contracts did not pass on both hosts")
    linux_kurumi_output=run([str(linux_kurumi)])
    windows_kurumi_output=run([args.windows_runner,str(windows_kurumi)],env=runner_env)
    if linux_kurumi_output!="Stage 2 Kurumi contracts PASS" or windows_kurumi_output!=linux_kurumi_output:
        raise ValueError("Stage2 Kurumi contracts did not pass on both hosts")
    expected_midboss = "Stage 1 midboss contracts PASS"
    linux_midboss_output = run([str(linux_midboss)])
    windows_midboss_output = run([args.windows_runner,str(windows_midboss)],env=runner_env)
    if linux_midboss_output != expected_midboss or windows_midboss_output != expected_midboss:
        raise ValueError("midboss contracts did not pass on both hosts")
    linux_orange_output = run([str(linux_orange)])
    windows_orange_output = run([args.windows_runner,str(windows_orange)],env=runner_env)
    if linux_orange_output != "Stage 1 Orange contracts PASS" or windows_orange_output != linux_orange_output:
        raise ValueError("Orange contracts did not pass on both hosts")
    linux_dialog_output = run([str(linux_dialog)])
    windows_dialog_output = run([args.windows_runner,str(windows_dialog)],env=runner_env)
    if linux_dialog_output != "Dialog contracts PASS" or windows_dialog_output != linux_dialog_output:
        raise ValueError("dialog contracts did not pass on both hosts")
    expected_bonus = "stage_bonus=WORD_COMPONENTS_STEPWISE32 timeout=ZERO_WITH_BOMB allclear=EXTENDS_DISABLED pointer_bits=64"
    linux_bonus_output = run([str(linux_bonus)])
    windows_bonus_output = run([args.windows_runner,str(windows_bonus)],env=runner_env)
    if linux_bonus_output != expected_bonus or windows_bonus_output != expected_bonus:
        raise ValueError("stage-bonus contracts did not pass on both hosts")
    expected_score="score=DECIMAL_BYTES_LOW_WORD_DRAIN extend=DIGIT_PREDICATES high_digit=UNNORMALIZED pointer_bits=64"
    linux_score_output=run([str(linux_score)])
    windows_score_output=run([args.windows_runner,str(windows_score)],env=runner_env)
    if linux_score_output!=expected_score or windows_score_output!=expected_score:
        raise ValueError("score contracts did not pass on both hosts")
    expected_transition="stage_transition=SHARED_BYTE_72 departure=DIALOG_416_488 pending_score=CARRIES pointer_bits=64"
    linux_transition_output=run([str(linux_transition)])
    windows_transition_output=run([args.windows_runner,str(windows_transition)],env=runner_env)
    if linux_transition_output!=expected_transition or windows_transition_output!=expected_transition:
        raise ValueError("stage-transition contracts did not pass on both hosts")
    smoke = root / "port64/smoke.py"
    linux_smoke_output = run([
        sys.executable, str(smoke), "--exe", str(linux_main),
        "--hdi", str(hdi),
    ])
    windows_smoke_output = run([
        sys.executable, str(smoke), "--runner", args.windows_runner,
        "--exe", str(windows_main), "--hdi", str(hdi),
    ], env=runner_env)
    if "port64 smoke: PASS" not in linux_smoke_output:
        raise ValueError("Linux resource smoke did not pass")
    if "port64 smoke: PASS" not in windows_smoke_output:
        raise ValueError("Windows resource smoke did not pass")
    shooting_hashes = {}
    for host, command in (("linux",[str(linux_main)]),
                          ("windows",[args.windows_runner,str(windows_main)])):
        images = output.parent / ("shooting-"+host)
        images.mkdir(parents=True,exist_ok=True)
        result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--shooting-screenshots",str(images)],env=runner_env)
        if result.count("MAIN shooting power=128") != 4:
            raise ValueError("shooting fixture did not collect full power on every route")
        shooting_hashes[host] = {name:sha256(images/(name+".bmp"))
                                for name in ("reimu-a","reimu-b","marisa-a","marisa-b")}
    if shooting_hashes["linux"] != shooting_hashes["windows"]:
        raise ValueError("shooting BMPs differ between Linux and Windows")

    combat_hashes = {}
    combat_outputs = {}
    for host, command in (("linux",[str(linux_main)]),
                          ("windows",[args.windows_runner,str(windows_main)])):
        images = output.parent / ("combat-"+host)
        images.mkdir(parents=True,exist_ok=True)
        result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--combat-screenshots",str(images)],env=runner_env)
        if result.count("MAIN combat frames=1200 killed=") != 2:
            raise ValueError("combat fixture did not exercise both characters")
        combat_hashes[host] = {name:sha256(images/(name+".bmp")) for name in ("reimu","marisa","reimu-bullets","marisa-bullets")}
        combat_outputs[host] = [line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith(("MAIN combat","MAIN barrage"))]
    if combat_hashes["linux"] != combat_hashes["windows"] or combat_outputs["linux"] != combat_outputs["windows"]:
        raise ValueError("combat images or gameplay counters differ between hosts")

    midboss_hashes = {}
    midboss_outputs = {}
    for host, command in (("linux",[str(linux_main)]),
                          ("windows",[args.windows_runner,str(windows_main)])):
        images = output.parent / ("midboss-"+host)
        images.mkdir(parents=True,exist_ok=True)
        result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--midboss-screenshots",str(images)],env=runner_env)
        if result.count("MAIN midboss case=") != 24:
            raise ValueError("midboss fixture did not reach all four scenarios/checkpoints")
        midboss_hashes[host] = {path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
        midboss_outputs[host] = [line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN midboss")]
    if midboss_hashes["linux"] != midboss_hashes["windows"] or midboss_outputs["linux"] != midboss_outputs["windows"]:
        raise ValueError("midboss images or gameplay counters differ between hosts")

    orange_hashes = {}
    orange_outputs = {}
    for host, command in (("linux",[str(linux_main)]),
                          ("windows",[args.windows_runner,str(windows_main)])):
        images = output.parent / ("orange-"+host)
        images.mkdir(parents=True,exist_ok=True)
        result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--orange-screenshots",str(images)],env=runner_env)
        if result.count("MAIN Orange fixture=") != 120 or result.count("MAIN Orange stopped ") != 8:
            raise ValueError("Orange fixture missed a character/rank/outcome/checkpoint")
        orange_hashes[host] = {path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
        if len(orange_hashes[host]) != 120:
            raise ValueError("Orange fixture has unexpected image files")
        orange_outputs[host] = [line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Orange")]
    if orange_hashes["linux"] != orange_hashes["windows"] or orange_outputs["linux"] != orange_outputs["windows"]:
        raise ValueError("Orange images or gameplay counters differ between hosts")

    dialog_hashes = {}
    dialog_outputs = {}
    stage2_hashes = {}
    stage2_outputs = {}
    kurumi_hashes = {}
    kurumi_outputs = {}
    stage3_hashes = {}
    stage3_outputs = {}
    stage4_hashes = {}
    stage4_outputs = {}
    stage5_hashes = {}
    stage5_outputs = {}
    yuuka5_hashes = {}
    yuuka5_outputs = {}
    stage6_hashes = {}
    stage6_outputs = {}
    marisa_hashes = {}
    marisa_outputs = {}
    reimu_hashes = {}
    reimu_outputs = {}
    elly_hashes = {}
    elly_outputs = {}
    if args.font_bmp:
        for host, command in (("linux",[str(linux_main)]),
                              ("windows",[args.windows_runner,str(windows_main)])):
            images = output.parent / ("dialog-"+host)
            images.mkdir(parents=True,exist_ok=True)
            result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--dialog-screenshots",str(images)],env=runner_env)
            if result.count("MAIN dialog fixture=") != 64 or result.count("MAIN dialog stopped ") != 8:
                raise ValueError("ordinary Stage 1 dialog fixture missed progression")
            dialog_hashes[host] = {path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(dialog_hashes[host]) != 64:
                raise ValueError("dialog fixture has unexpected image files")
            dialog_outputs[host] = [line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN dialog")]
        if dialog_hashes["linux"] != dialog_hashes["windows"] or dialog_outputs["linux"] != dialog_outputs["windows"]:
            raise ValueError("ordinary dialog images or counters differ between hosts")
        for host, command in (("linux",[str(linux_main)]),
                              ("windows",[args.windows_runner,str(windows_main)])):
            images = output.parent / ("stage2-"+host)
            images.mkdir(parents=True,exist_ok=True)
            result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--stage2-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Stage2 fixture=") != 32 or result.count("MAIN Stage2 stopped ") != 4:
                raise ValueError("natural Stage2 resource/dialog fixture missed progression")
            stage2_hashes[host] = {path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(stage2_hashes[host]) != 32:
                raise ValueError("Stage2 fixture has unexpected image files")
            stage2_outputs[host] = [line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Stage2")]
        if stage2_hashes["linux"] != stage2_hashes["windows"] or stage2_outputs["linux"] != stage2_outputs["windows"]:
            raise ValueError("Stage2 images or counters differ between hosts")

        for host, command in (("linux",[str(linux_main)]),
                              ("windows",[args.windows_runner,str(windows_main)])):
            images = output.parent / ("kurumi-"+host)
            images.mkdir(parents=True,exist_ok=True)
            result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--kurumi-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Kurumi fixture=") != 72 or result.count("MAIN Kurumi stopped ") != 8:
                raise ValueError("natural Kurumi fixture missed progression")
            kurumi_hashes[host] = {path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(kurumi_hashes[host]) != 72:
                raise ValueError("Kurumi fixture has unexpected image files")
            kurumi_outputs[host] = [line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Kurumi")]
        if kurumi_hashes["linux"] != kurumi_hashes["windows"] or kurumi_outputs["linux"] != kurumi_outputs["windows"]:
            raise ValueError("Kurumi images or counters differ between hosts")

        for host, command in (("linux",[str(linux_main)]),("windows",[args.windows_runner,str(windows_main)])):
            images = output.parent / ("stage3-"+host); images.mkdir(parents=True,exist_ok=True)
            result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--stage3-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Stage3 fixture=") != 72 or result.count("MAIN Stage3 stopped ") != 8:
                raise ValueError("natural Stage3 fixture missed progression")
            stage3_hashes[host] = {path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(stage3_hashes[host]) != 72: raise ValueError("unexpected Stage3 image files")
            stage3_outputs[host] = [line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Stage3")]
        if len(stage3_outputs["linux"])!=80 or len(stage3_outputs["windows"])!=80: raise ValueError("missing Stage3 scenario counters")
        if stage3_hashes["linux"] != stage3_hashes["windows"] or stage3_outputs["linux"] != stage3_outputs["windows"]:
            raise ValueError("Stage3 images or counters differ between hosts")

        for host, command in (("linux",[str(linux_main)]),("windows",[args.windows_runner,str(windows_main)])):
            images = output.parent / ("elly-"+host);images.mkdir(parents=True,exist_ok=True)
            result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--elly-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Elly fixture=")!=96 or result.count("MAIN Elly stopped ")!=8:raise ValueError("natural Elly fixture missed progression")
            elly_hashes[host]={path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(elly_hashes[host])!=96:raise ValueError("unexpected Elly image files")
            elly_outputs[host]=[line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Elly")]
        if elly_hashes["linux"]!=elly_hashes["windows"] or elly_outputs["linux"]!=elly_outputs["windows"]:raise ValueError("Elly images/counters differ between hosts")
        for host, command in (("linux",[str(linux_main)]),("windows",[args.windows_runner,str(windows_main)])):
            images = output.parent / ("stage4-"+host);images.mkdir(parents=True,exist_ok=True)
            result = run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--stage4-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Stage4 fixture=")!=96 or result.count("MAIN Stage4 stopped ")!=8:raise ValueError("natural Stage4 fixture missed progression")
            stage4_hashes[host]={path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(stage4_hashes[host])!=96:raise ValueError("unexpected Stage4 image files")
            stage4_outputs[host]=[line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Stage4")]
        if stage4_hashes["linux"]!=stage4_hashes["windows"] or stage4_outputs["linux"]!=stage4_outputs["windows"]:raise ValueError("Stage4 images/counters differ between hosts")

        for host, command in (("linux",[str(linux_main)]),("windows",[args.windows_runner,str(windows_main)])):
            images=output.parent/("reimu-"+host);images.mkdir(parents=True,exist_ok=True)
            result=run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--reimu-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Reimu fixture=")!=144 or result.count("MAIN Reimu stopped ")!=8:raise ValueError("natural Reimu fixture missed progression")
            reimu_hashes[host]={path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(reimu_hashes[host])!=144:raise ValueError("unexpected Reimu image files")
            reimu_outputs[host]=[line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Reimu")]
        if reimu_hashes["linux"]!=reimu_hashes["windows"] or reimu_outputs["linux"]!=reimu_outputs["windows"]:raise ValueError("Reimu images/counters differ between hosts")

        for host, command in (("linux",[str(linux_main)]),("windows",[args.windows_runner,str(windows_main)])):
            images=output.parent/("marisa-"+host);images.mkdir(parents=True,exist_ok=True)
            result=run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--marisa-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Marisa fixture=")!=162 or result.count("MAIN Marisa stopped ")!=8:raise ValueError("natural Marisa fixture missed progression")
            marisa_hashes[host]={path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(marisa_hashes[host])!=162:raise ValueError("unexpected Marisa image files")
            marisa_outputs[host]=[line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Marisa")]
        if marisa_hashes["linux"]!=marisa_hashes["windows"] or marisa_outputs["linux"]!=marisa_outputs["windows"]:raise ValueError("Marisa images/counters differ between hosts")

        for host, command in (("linux",[str(linux_main)]),("windows",[args.windows_runner,str(windows_main)])):
            images=output.parent/("stage5-"+host);images.mkdir(parents=True,exist_ok=True)
            result=run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--stage5-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Stage5 fixture=")!=112 or result.count("MAIN Stage5 stopped ")!=16:raise ValueError("natural Stage5 fixture missed progression")
            stage5_hashes[host]={path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(stage5_hashes[host])!=112:raise ValueError("unexpected Stage5 image files")
            stage5_outputs[host]=[line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Stage5")]
        if stage5_hashes["linux"]!=stage5_hashes["windows"] or stage5_outputs["linux"]!=stage5_outputs["windows"]:raise ValueError("Stage5 images/counters differ between hosts")

        for host, command in (("linux",[str(linux_main)]),("windows",[args.windows_runner,str(windows_main)])):
            images=output.parent/("yuuka5-"+host);images.mkdir(parents=True,exist_ok=True)
            result=run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--yuuka5-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Yuuka5 fixture=")!=698 or result.count("MAIN Yuuka5 stopped ")!=18:raise ValueError("natural Yuuka5 fixture missed progression")
            yuuka5_hashes[host]={path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(yuuka5_hashes[host])!=698:raise ValueError("unexpected Yuuka5 image files")
            yuuka5_outputs[host]=[line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Yuuka5")]
        if yuuka5_hashes["linux"]!=yuuka5_hashes["windows"] or yuuka5_outputs["linux"]!=yuuka5_outputs["windows"]:raise ValueError("Yuuka5 images/counters differ between hosts")

        for host, command in (("linux",[str(linux_main)]),("windows",[args.windows_runner,str(windows_main)])):
            images=output.parent/("stage6-"+host);images.mkdir(parents=True,exist_ok=True)
            result=run(command+["--pmd-driver","none","--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--stage6-screenshots",str(images)],env=runner_env)
            if result.count("MAIN Stage6 fixture=")!=112 or result.count("MAIN Stage6 battle fixture=")!=400 or result.count("MAIN Stage6 stopped ")!=16 or result.count("progression=good_ending_pending")!=16:raise ValueError("natural Stage6 fixture missed progression")
            stage6_hashes[host]={path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(stage6_hashes[host])!=512:raise ValueError("unexpected Stage6 image files")
            stage6_outputs[host]=[line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN Stage6")]
        if stage6_hashes["linux"]!=stage6_hashes["windows"] or stage6_outputs["linux"]!=stage6_outputs["windows"]:raise ValueError("Stage6 images/counters differ between hosts")

    manifest_sha256, source_files = source_manifest(root)
    if manifest_sha256 != initial_manifest_sha256:
        raise ValueError("portable sources changed during verification")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "TH04 portable Linux/Windows x86-64 bring-up",
        "source_manifest_sha256": manifest_sha256,
        "source_files": source_files,
        "hdi_sha256": sha256(hdi),
        "products": {
            "linux": {
                "format": "ELF64 x86-64",
                "yuuka6_core_contracts_sha256": sha256(linux_yuuka6_core),
                "yuuka6_background_contract_output": linux_yuuka6_background_output,
                "yuuka6_background_contracts_sha256": sha256(linux_yuuka6_background),
                "yuuka6_render_contract_output": linux_yuuka6_render_output,
                "yuuka6_render_contracts_sha256": sha256(linux_yuuka6_render),
                "yuuka6_core_contract_output": linux_yuuka6_core_output,
                "yuuka6_attacks_contracts_sha256": sha256(linux_yuuka6_attacks),
                "yuuka6_attacks_contract_output": linux_yuuka6_attacks_output,
                "yuuka6_entities_contracts_sha256": sha256(linux_yuuka6_entities),
                "yuuka6_entities_contract_output": linux_yuuka6_entities_output,
                "yuuka6_contracts_sha256": sha256(linux_yuuka6),
                "yuuka6_contract_output": linux_yuuka6_output,
                "yuuka5_contracts_sha256": sha256(linux_yuuka),
                "yuuka5_contract_output": linux_yuuka_output,
                "laser_contracts_sha256": sha256(linux_lasers),
                "laser_contract_output": linux_laser_output,
                "stage5_contracts_sha256": sha256(linux_stage5),
                "stage5_contract_output": linux_stage5_output,
                "main_sha256": sha256(linux_main),
                "contracts_sha256": sha256(linux_contracts),
                "contract_output": linux_contract_output,
                "live_contracts_sha256": sha256(linux_live),
                "live_contract_output": linux_live_output,
                "shot_contracts_sha256": sha256(linux_shots),
                "shot_contract_output": linux_shot_output,
                "enemy_contracts_sha256": sha256(linux_enemies),
                "enemy_contract_output": linux_enemy_output,
                "bullet_contract_output": linux_bullet_output,
                "bullet_contracts_sha256": sha256(linux_bullets),
                "effect_contract_output": linux_effect_output,
                "effect_contracts_sha256": sha256(linux_effects),
                "midboss_contract_output": linux_midboss_output,
                "midboss_contracts_sha256": sha256(linux_midboss),
                "midboss4_contract_output": linux_midboss4_output,
                "marisa_contracts_sha256": sha256(linux_marisa),
                "marisa_contracts_output": linux_marisa_output,
                "reimu_contracts_sha256": sha256(linux_reimu),
                "reimu_contracts_output": linux_reimu_output,
                "midboss4_contracts_sha256": sha256(linux_midboss4),
                "elly_contract_output": linux_elly_output,
                "elly_contracts_sha256": sha256(linux_elly),
                "midboss3_contract_output": linux_midboss3_output,
                "midboss3_contracts_sha256": sha256(linux_midboss3),
                "midboss2_contract_output": linux_midboss2_output,
                "midboss2_contracts_sha256": sha256(linux_midboss2),
                "kurumi_contract_output": linux_kurumi_output,
                "kurumi_contracts_sha256": sha256(linux_kurumi),
                "orange_contract_output": linux_orange_output,
                "orange_contracts_sha256": sha256(linux_orange),
                "cutscene_contract_output": linux_cutscene_output,
                "cutscene_contracts_sha256": sha256(linux_cutscene),
                "dialog_contract_output": linux_dialog_output,
                "dialog_contracts_sha256": sha256(linux_dialog),
                "session_contract_output": linux_session_output,
                "session_contracts_sha256": sha256(linux_session),
                "transition_contract_output": linux_transition_output,
                "transition_contracts_sha256": sha256(linux_transition),
                "score_contract_output": linux_score_output,
                "score_contracts_sha256": sha256(linux_score),
                "bonus_contract_output": linux_bonus_output,
                "bonus_contracts_sha256": sha256(linux_bonus),
                "smoke_output": linux_smoke_output.splitlines(),
            },
            "windows": {
                "format": "PE32+ x86-64",
                "yuuka6_core_contracts_sha256": sha256(windows_yuuka6_core),
                "yuuka6_background_contract_output": windows_yuuka6_background_output,
                "yuuka6_background_contracts_sha256": sha256(windows_yuuka6_background),
                "yuuka6_render_contract_output": windows_yuuka6_render_output,
                "yuuka6_render_contracts_sha256": sha256(windows_yuuka6_render),
                "yuuka6_core_contract_output": windows_yuuka6_core_output,
                "yuuka6_attacks_contracts_sha256": sha256(windows_yuuka6_attacks),
                "yuuka6_attacks_contract_output": windows_yuuka6_attacks_output,
                "yuuka6_entities_contracts_sha256": sha256(windows_yuuka6_entities),
                "yuuka6_entities_contract_output": windows_yuuka6_entities_output,
                "yuuka6_contracts_sha256": sha256(windows_yuuka6),
                "yuuka6_contract_output": windows_yuuka6_output,
                "yuuka5_contracts_sha256": sha256(windows_yuuka),
                "yuuka5_contract_output": windows_yuuka_output,
                "laser_contracts_sha256": sha256(windows_lasers),
                "laser_contract_output": windows_laser_output,
                "stage5_contracts_sha256": sha256(windows_stage5),
                "stage5_contract_output": windows_stage5_output,
                "main_sha256": sha256(windows_main),
                "contracts_sha256": sha256(windows_contracts),
                "contract_output": windows_contract_output,
                "live_contracts_sha256": sha256(windows_live),
                "live_contract_output": windows_live_output,
                "shot_contracts_sha256": sha256(windows_shots),
                "shot_contract_output": windows_shot_output,
                "enemy_contracts_sha256": sha256(windows_enemies),
                "enemy_contract_output": windows_enemy_output,
                "bullet_contract_output": windows_bullet_output,
                "bullet_contracts_sha256": sha256(windows_bullets),
                "effect_contract_output": windows_effect_output,
                "effect_contracts_sha256": sha256(windows_effects),
                "midboss_contract_output": windows_midboss_output,
                "midboss_contracts_sha256": sha256(windows_midboss),
                "midboss4_contract_output": windows_midboss4_output,
                "marisa_contracts_sha256": sha256(windows_marisa),
                "marisa_contracts_output": windows_marisa_output,
                "reimu_contracts_sha256": sha256(windows_reimu),
                "reimu_contracts_output": windows_reimu_output,
                "midboss4_contracts_sha256": sha256(windows_midboss4),
                "elly_contract_output": windows_elly_output,
                "elly_contracts_sha256": sha256(windows_elly),
                "midboss3_contract_output": windows_midboss3_output,
                "midboss3_contracts_sha256": sha256(windows_midboss3),
                "midboss2_contract_output": windows_midboss2_output,
                "midboss2_contracts_sha256": sha256(windows_midboss2),
                "kurumi_contract_output": windows_kurumi_output,
                "kurumi_contracts_sha256": sha256(windows_kurumi),
                "orange_contract_output": windows_orange_output,
                "orange_contracts_sha256": sha256(windows_orange),
                "cutscene_contract_output": windows_cutscene_output,
                "cutscene_contracts_sha256": sha256(windows_cutscene),
                "dialog_contract_output": windows_dialog_output,
                "dialog_contracts_sha256": sha256(windows_dialog),
                "session_contract_output": windows_session_output,
                "session_contracts_sha256": sha256(windows_session),
                "transition_contract_output": windows_transition_output,
                "transition_contracts_sha256": sha256(windows_transition),
                "score_contract_output": windows_score_output,
                "score_contracts_sha256": sha256(windows_score),
                "bonus_contract_output": windows_bonus_output,
                "bonus_contracts_sha256": sha256(windows_bonus),
                "smoke_output": windows_smoke_output.splitlines(),
            },
        },
        "title_bmp_sha256": (
            "b52ea8615865bfc11945fbe23828b7c391d8424c998062a8abfb5d62b4b31d2a"
        ),
        "options_bmp_sha256": (
            "a064338b0cfb89f7e418a85ab6bc84a7ea5ef835e4ca995b68772e0aef368185"
        ),
        "character_bmp_sha256": (
            "c1a795a36c2603004fed9309200af833ff8718434b4ba8de2c0977eb2acda199"
        ),
        "shot_bmp_sha256": (
            "12aa7616f49283462bb7c9dd41c3198fd66865a758da79ad24cf63de817ee438"
        ),
        "handoff_bmp_sha256": (
            "0b2c0f8cebb9e1c0e600de3bee29feb8f225efb5b798cb3a387b6c5538bb55c5"
        ),
        "main_fixture_bmp_sha256": (
            "c87c0242836cc3408ced95cf7fdba20f4ae6ca8d0d20b03d9b30d8c2b80c9eab"
        ),
        "passed": True,
        "shooting_fixture_bmp_sha256": shooting_hashes["linux"],
        "combat_fixture_bmp_sha256": combat_hashes["linux"],
        "combat_fixture_counters": combat_outputs["linux"],
        "midboss_fixture_bmp_sha256": midboss_hashes["linux"],
        "midboss_fixture_counters": midboss_outputs["linux"],
        "orange_fixture_bmp_sha256": orange_hashes["linux"],
        "orange_fixture_counters": orange_outputs["linux"],
        "dialog_fixture_bmp_sha256": dialog_hashes.get("linux",{}),
        "dialog_fixture_counters": dialog_outputs.get("linux",[]),
        "stage2_fixture_bmp_sha256": stage2_hashes.get("linux",{}),
        "stage2_fixture_counters": stage2_outputs.get("linux",[]),
        "kurumi_fixture_bmp_sha256": kurumi_hashes.get("linux",{}),
        "kurumi_fixture_counters": kurumi_outputs.get("linux",[]),
        "marisa_fixture_bmp_sha256": marisa_hashes.get("linux",{}),
        "marisa_fixture_counters": marisa_outputs.get("linux",[]),
        "reimu_fixture_bmp_sha256": reimu_hashes.get("linux",{}),
        "reimu_fixture_counters": reimu_outputs.get("linux",[]),
        "yuuka5_fixture_bmp_sha256": yuuka5_hashes.get("linux",{}),
        "yuuka5_fixture_counters": yuuka5_outputs.get("linux",[]),
        "stage6_fixture_bmp_sha256": stage6_hashes.get("linux",{}),
        "stage6_fixture_counters": stage6_outputs.get("linux",[]),
        "stage5_fixture_bmp_sha256": stage5_hashes.get("linux",{}),
        "stage5_fixture_counters": stage5_outputs.get("linux",[]),
        "stage4_fixture_bmp_sha256": stage4_hashes.get("linux",{}),
        "stage4_fixture_counters": stage4_outputs.get("linux",[]),
        "elly_fixture_bmp_sha256": elly_hashes.get("linux",{}),
        "elly_fixture_counters": elly_outputs.get("linux",[]),
        "stage3_fixture_bmp_sha256": stage3_hashes.get("linux",{}),
        "stage3_fixture_counters": stage3_outputs.get("linux",[]),
        "font_bmp_sha256": sha256(args.font_bmp) if args.font_bmp else None,
        "limit": (
            "Resource decoding, main/options/character/shot composition, deterministic "
            "OP menu-state transitions, resident process handoff, process-local LCG and shared "
            "random-ring contracts, live player movement, item entity motion/pickup and "
            "BFNT sprites, Stage 1 MPN/MAP/STD background rendering/scrolling and "
            "four-route player shots/lasers, all-seven STD wave schedules, enemy VM, 32-slot enemy lifecycle/hit/drop integration and original enemy BFNT sprites, enemy bullet tune/spawn/9 motions/graze/collision/clear/zap and cloud/pellet rendering; "
            "spark allocation/motion and gather release with synchronous shared RNG; "
            "Stage 1 midboss activation/tile animation/pattern/defeat; "
            "explicit Stage 1 Orange fixtures with actual shots/items/bullets, foreground/explosions/circles and host backdrop composition "
            "stop at the pending post-boss dialog (independent CPU comparisons are separate receipts); "
            "Stage 1 ordinary pre/post-boss dialog and sprite-bank replacement is checked when font-bmp is supplied; "
            "ordinary stage-clear bonus state/colored text is consumed exactly once; "
            "all-clear/Extra bonus math has separate CPU controls; "
            "ordinary completed frames drain score and feed extends into lives/performance/clear; "
            "post-dialog continuation completes its already entered actor frame, then enter/leave TRAM "
            "and416/488 departure reach the unloaded Stage2 resource request; "
            "Stage2 actor initialization and pre-midboss STD/MAP integration have separate CPU/native controls; "
            "Stage2 midboss behavior/geometry has separate selected CPU controls; "
            "Stages1..5 now join natural waves/midbosses/bosses/dialogue/clear/departure. "
            "Stage5 has sixteen Normal/Lunatic character/A-B shot/idle routes requesting Stage6 "
            "and two Easy bad-dialogue routes stopping before MAINE. Separate original CPU "
            "component controls support selected semantics; these host scenarios are not "
            "original whole-route or physical PC-98 hardware comparisons. Stage6 waves, full "
            "pre-battle dialogue, all Yuuka6 battle phases, defeat and all-clear additionally "
            "have sixteen natural host routes stopping at the nonreturning Ending entry. Extra, "
            "Bombs, player death/Continue, remaining HUD, audio, Ending and save I/O "
            "still need native implementation. No whole-game, FPS or DOS exact claim."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "passed": True,
        "receipt": str(output),
        "source_manifest_sha256": manifest_sha256,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
