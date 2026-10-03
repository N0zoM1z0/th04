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
    linux_dialog = linux_dir / "th04-port64-dialog-contracts"
    windows_dialog = windows_dir / "th04-port64-dialog-contracts.exe"
    for path in (linux_main, linux_contracts, linux_live, linux_shots, linux_enemies, linux_bullets, linux_effects, linux_midboss, linux_orange, linux_dialog):
        require_elf_x86_64(path)
    for path in (windows_main, windows_contracts, windows_live, windows_shots, windows_enemies, windows_bullets, windows_effects, windows_midboss, windows_orange, windows_dialog):
        require_pe_x86_64(path)

    runner_env = os.environ.copy()
    runner_env.setdefault("WINEDEBUG", "-all")
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
        result = run(command+["--hdi",str(hdi),"--shooting-screenshots",str(images)],env=runner_env)
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
        result = run(command+["--hdi",str(hdi),"--combat-screenshots",str(images)],env=runner_env)
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
        result = run(command+["--hdi",str(hdi),"--midboss-screenshots",str(images)],env=runner_env)
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
        result = run(command+["--hdi",str(hdi),"--orange-screenshots",str(images)],env=runner_env)
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
    if args.font_bmp:
        for host, command in (("linux",[str(linux_main)]),
                              ("windows",[args.windows_runner,str(windows_main)])):
            images = output.parent / ("dialog-"+host)
            images.mkdir(parents=True,exist_ok=True)
            result = run(command+["--hdi",str(hdi),"--font-bmp",str(args.font_bmp.resolve()),"--dialog-screenshots",str(images)],env=runner_env)
            if result.count("MAIN dialog fixture=") != 40 or result.count("MAIN dialog stopped ") != 8:
                raise ValueError("ordinary Stage 1 dialog fixture missed progression")
            dialog_hashes[host] = {path.name:sha256(path) for path in sorted(images.glob("*.bmp"))}
            if len(dialog_hashes[host]) != 40:
                raise ValueError("dialog fixture has unexpected image files")
            dialog_outputs[host] = [line.split(" screenshot=")[0] for line in result.splitlines() if line.startswith("MAIN dialog")]
        if dialog_hashes["linux"] != dialog_hashes["windows"] or dialog_outputs["linux"] != dialog_outputs["windows"]:
            raise ValueError("ordinary dialog images or counters differ between hosts")

    manifest_sha256, source_files = source_manifest(root)
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
                "orange_contract_output": linux_orange_output,
                "orange_contracts_sha256": sha256(linux_orange),
                "dialog_contract_output": linux_dialog_output,
                "dialog_contracts_sha256": sha256(linux_dialog),
                "smoke_output": linux_smoke_output.splitlines(),
            },
            "windows": {
                "format": "PE32+ x86-64",
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
                "orange_contract_output": windows_orange_output,
                "orange_contracts_sha256": sha256(windows_orange),
                "dialog_contract_output": windows_dialog_output,
                "dialog_contracts_sha256": sha256(windows_dialog),
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
            "4cbbe895725e39fc1fb9b5c6271579833ab69c975824e0c91d20275066317f52"
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
            "stage-clear bonus/progression, "
            "later midbosses/bosses, bombs, player death, HUD, later-stage backgrounds, "
            "audio, saved-data I/O and complete OP/MAIN/MAINE behavior "
            "are not yet ported."
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
