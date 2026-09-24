#!/usr/bin/env python3
"""Validate and cold-replay artifact-local decoded TH04 function acceptance.

This is deliberately separate from units.csv raw packed-file exactness. The
Shared OP/MAINE backends may relink both artifacts, while artifact-specific
backends run only their claimed product; the ZUN backend links its resident
component. A diagnostic source-present row never gains acceptance from a
successful compile or a normalized/shifted comparison.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

from lib.pc98 import parse_mz


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "config/th04_decoded_function_acceptance.csv"
HEADER = [
    "boundary_id", "artifact", "segment_identity", "payload_offset", "size",
    "producer_offset", "producer_size", "source", "decoded_state",
    "target_sha256", "replay_backend", "replay_evidence_id", "raw_evidence_id", "notes",
]
ARTIFACTS = {"th04-op", "th04-maine", "th04-zun"}
REQUIRED_PRODUCER_ORACLES = {
    "boundary-ownership", "toolchain-replay", "object-format-integrity",
    "cold-build-determinism", "layout-relocations",
    "cold-aggregate-replay",
}
RESTORED = {
    "th04-op": ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin",
    "th04-maine": ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin",
}
RESTORED_SHA256 = {
    "th04-op": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
    "th04-maine": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
}
ZUN_PAYLOAD = ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin"
ZUN_PAYLOAD_SHA256 = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
ZUN_COMPONENT_OFFSET = 0xB68
ZUN_COMPONENT_SHA256 = "cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110"
BGIMAGE_PRODUCERS = {"th04-op": 0xE428, "th04-maine": 0xD626}
VRAM_PRODUCERS = {"th04-op": 0xDA12, "th04-maine": 0xCC7A}
FRAME_DELAY_PRODUCERS = {"th04-op": 0xDA3B, "th04-maine": 0xCCA3}
INPUT_WAIT_PRODUCERS = {"th04-op": 0xDB62, "th04-maine": 0xCE7A}
SE_RESET_PRODUCERS = {"th04-op": 0xE2E6, "th04-maine": 0xD594}
VECTOR_MATH_PRODUCERS = {"th04-op": 0xDBB8, "th04-maine": 0xCED0}
PI_PUT_PRODUCERS = {"th04-op": 0xDA50, "th04-maine": 0xCCB8}
PI_LOAD_PRODUCERS = {"th04-op": 0xDAFD, "th04-maine": 0xCD65}
PMD_PRODUCERS = {"th04-op": 0xDC16, "th04-maine": 0xCF2E}
MMD_PRODUCERS = {"th04-op": 0xDC44, "th04-maine": 0xCF5C}
KAJA_PRODUCERS = {"th04-op": 0xDC74, "th04-maine": 0xCF8C}
MODE_PRODUCERS = {"th04-op": 0xDCE4, "th04-maine": 0xCFAA}
DELAY_PRODUCERS = {"th04-op": 0xDD80, "th04-maine": 0xD046}
MAINE_SCORE_INSERT_PRODUCER = 0xC3B2
MAINE_SCORE_PUT_PRODUCER = 0xC506
MAINE_BOX_ANIMATE_PRODUCER = 0xA292
MAINE_PIC_COPY_TO_OTHER_PRODUCER = 0xA292
MAINE_CURSOR_ADVANCE_PRODUCER = 0xA292
MAINE_BOX_BG_PUT_PRODUCER = 0xA292
MAINE_CUTSCENE_SCRIPT_FREE_PRODUCER = 0xA292
MAINE_BOX_BG_FREE_PRODUCER = 0xA292
MAINE_SCRIPT_PARAM_FIRST_PRODUCER = 0xA292
MAINE_SCRIPT_PARAM_SECOND_PRODUCER = 0xA292
MAINE_CUTSCENE_SCRIPT_LOAD_PRODUCER = 0xA292
MAINE_CFG_RESIDENT_PRODUCER = 0xA059
MAINE_GAME_EXIT_EXEC_PRODUCER = 0xA059
MAINE_GAME_EXIT_PRODUCER = 0xD3F4
MAINE_GAME_INIT_MAIN_PRODUCER = 0xD43C
MAINE_END_ANIMATE_PRODUCER = 0xA059
MAINE_SCORE_LOAD_FOR_PRODUCER = 0xC2AD
MAINE_SCORE_RECREATE_PRODUCER = 0xC206
MAINE_STAGE_PUT_PRODUCER = 0xC5EC
MAINE_NAME_CURSOR_PRODUCER = 0xC665
MAINE_PLACE_ROW_PRODUCER = 0xC711
MAINE_PLACES_PRODUCER = 0xC7C9
MAINE_ALPHABET_CURSOR_PRODUCER = 0xC7E3
OP_STAGE_PUT_PRODUCER = 0xC8A5
OP_PLACE_PUT_PRODUCER = 0xC8F5
OP_RANK_RENDER_PRODUCER = 0xCA1A
OP_REGIST_MENU_PRODUCER = 0xCA94
OP_CLEAR_SPRITES_PRODUCER = 0xCBE3
OP_HISCORE_LOAD_BOTH_PRODUCER = 0xC733
OP_SCORES_PUT_PRODUCER = 0xC79E
OP_SCOREDAT_RECREATE_PRODUCER = 0xC68C
OP_MAIN_CDG_FREE_PRODUCER = 0xCC97
OP_MAIN_CDG_LOAD_PRODUCER = 0xCC97
OP_NOPOLY_FREE_PRODUCER = 0xBED5
OP_NOPOLY_SNAP_PRODUCER = 0xBED5
OP_FRAME_DELAY_2_PRODUCER = 0xE6DE
OP_RAISE_BG_FREE_PRODUCER = 0xCF5E
OP_PLAYCHAR_TITLE_BOX_PRODUCER = 0xCF5E
OP_SHOTTYPE_MENU_INITIAL_PRODUCER = 0xCF5E
OP_PIC_DARKEN_PRODUCER = 0xCF5E
OP_PLAYCHAR_MENU_INITIAL_PRODUCER = 0xCF5E
OP_GAME_EXIT_TO_DOS_PRODUCER = 0xDDB1
OP_GAME_EXIT_PRODUCER = 0xE0AC
OP_TRACKLIST_PUT_BOTH_PRODUCER = 0xBED5
OP_TRACK_PUT_BOTH_PRODUCER = 0xBED5
OP_CMT_UNPUT_PRODUCER = 0xBED5
OP_CMT_FADEIN_PRODUCER = 0xBED5
OP_CMT_PUT_PRODUCER = 0xBED5
OP_CMT_LOAD_PRODUCER = 0xBED5
OP_CMT_TRANSITION_PRODUCER = 0xBED5
OP_MUSIC_UPDATE_PRODUCER = 0xBED5
OP_HELP_PUT_PRODUCER = 0xB49F
OP_ROLLUP_PRODUCER = 0xB49F
OP_BGM_CHOICE_PRODUCER = 0xB49F
OP_SE_CHOICE_PRODUCER = 0xB49F
OP_WINDOW_ROLLUP_PUT_PRODUCER = 0xB49F
OP_WINDOW_DROPDOWN_PUT_PRODUCER = 0xB49F
OP_SINGLELINE_PRODUCER = 0xB49F
OP_DROPDOWN_PRODUCER = 0xB49F
ZUN_LINKED_SOURCES = {
    "src/zun/config/cfg_init.cpp", "src/zun/resident/main.cpp",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def valid_digest(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def rows(path: Path, expected_header: list[str] | None = None) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if expected_header is not None and reader.fieldnames != expected_header:
            raise ValueError(f"{path.name}: invalid column schema")
        result = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in result):
        raise ValueError(f"{path.name}: malformed CSV row")
    return result


def number(value: str, label: str) -> int:
    try:
        result = int(value, 0)
    except ValueError as error:
        raise ValueError(f"{label}: invalid integer {value!r}") from error
    if result < 0:
        raise ValueError(f"{label}: negative extent")
    return result


def validate(
    entries: list[dict[str, str]],
    boundaries: list[dict[str, str]],
    units: list[dict[str, str]],
    evidence: list[dict[str, str]],
    *,
    root: Path = ROOT,
) -> None:
    """Fail closed on false cross-artifact or packed-file acceptance."""

    boundary_by_id = {row["id"]: row for row in boundaries}
    evidence_by_id = {row["id"]: row for row in evidence}
    exact_boundaries = {
        row["id"] for row in boundaries
        if row["artifact"] in ARTIFACTS
        and row["work_queue"] == "reconstruct"
        and row["accepted_state"] == "exact"
    }
    seen: set[str] = set()
    ranges: dict[str, list[tuple[int, int]]] = {artifact: [] for artifact in ARTIFACTS}
    for entry in entries:
        ident = entry["boundary_id"]
        if ident in seen or ident not in boundary_by_id:
            raise ValueError(f"duplicate or unknown decoded boundary: {ident}")
        seen.add(ident)
        boundary = boundary_by_id[ident]
        artifact = entry["artifact"]
        if artifact not in ARTIFACTS or artifact != boundary["artifact"]:
            raise ValueError(f"{ident}: artifact identity mismatch")
        expected_segment = "com-payload" if artifact == "th04-zun" else "mz-load-module"
        start = number(entry["payload_offset"], ident)
        size = number(entry["size"], ident)
        producer_start = number(entry["producer_offset"], ident)
        producer_size = number(entry["producer_size"], ident)
        if (
            not size or not producer_size
            or entry["segment_identity"] != expected_segment
            or boundary["segment_identity"] != expected_segment
            or start != number(boundary["payload_offset"], ident)
            or size != number(boundary["body_size"], ident)
            or size != number(boundary["body_span"], ident)
            or start < producer_start or start + size > producer_start + producer_size
            or boundary["boundary_state"] != "reviewed"
            or boundary["origin"] != "authored"
            or boundary["work_queue"] != "reconstruct"
        ):
            raise ValueError(f"{ident}: physical decoded ownership mismatch")
        if any(start < end and previous < start + size for previous, end in ranges[artifact]):
            raise ValueError(f"{ident}: overlapping decoded function extent")
        ranges[artifact].append((start, start + size))
        source_name = entry["source"]
        source_path = root / source_name
        if (
            not source_name.startswith("src/")
            or ".." in Path(source_name).parts
            or source_path.is_symlink()
            or not source_path.is_file()
            or not source_path.resolve().is_relative_to((root / "src").resolve())
            or source_name != boundary["source_ref"]
        ):
            raise ValueError(f"{ident}: missing or mismatched maintained source")
        owners = [
            unit for unit in units
            if unit["artifact"] == artifact
            and unit["offset"] and number(unit["offset"], ident) == start
            and number(unit["size"], ident) == size
            and unit["source"] == source_name
        ]
        if len(owners) != 1 or owners[0]["origin"] != "authored":
            raise ValueError(f"{ident}: expected one matching authored unit")
        owner = owners[0]
        if (owner["segment"] != f"{expected_segment}/{boundary['map_segment']}"):
            raise ValueError(f"{ident}: unit segment disagrees with physical boundary")
        if owner["file_offset"] or owner["state"] != "source-present":
            raise ValueError(f"{ident}: decoded owner must not claim packed-file exactness")
        digest = entry["target_sha256"]
        if not valid_digest(digest):
            raise ValueError(f"{ident}: invalid target slice SHA-256")
        backend = entry["replay_backend"]
        allowed_backend = ({"zun-resident-link"} if artifact == "th04-zun"
                           else {"op-maine-bgimage-v489", "op-maine-vram-v509", "op-maine-frame-delay-v510",
                                 "op-maine-pi-put-v511", "op-maine-pi-load-v511", "op-maine-pmd-v512",
                                 "op-maine-mmd-v513", "op-maine-kaja-v514", "op-maine-mode-v515", "op-maine-delay-v516",
                                 "op-maine-input-wait-v565", "op-maine-se-reset-v581", "op-maine-vector-math-v570",
                                 "op-score-load-both-v558", "op-scores-put-v559", "op-scoredat-recreate-v561",
                                 "op-main-cdg-free-v583", "op-main-cdg-load-v602", "op-nopoly-free-v584",
                                 "op-nopoly-snap-v606",
                                 "op-frame-delay-2-v587", "op-raise-bg-free-v588", "op-playchar-title-box-v638", "op-pic-darken-v640", "op-shottype-menu-initial-v660", "op-playchar-menu-initial-v658",
                                 "op-game-exit-to-dos-v592", "op-game-exit-v654",
                                 "op-tracklist-put-both-v594",
                                 "op-track-put-both-v636",
                                 "op-cmt-unput-v598",
                                 "op-cmt-fadein-v600",
                                 "op-cmt-put-v618",
                                 "op-cmt-load-v620",
                                 "op-cmt-transition-v622",
                                 "op-music-update-flip-v610",
                                 "op-help-put-v596",
                                 "op-rollup-v612",
                                 "op-bgm-choice-v624",
                                 "op-se-choice-v626",
                                 "op-window-rollup-put-v628",
                                 "op-window-dropdown-put-v632",
                                 "op-singleline-v634",
                                 "op-dropdown-v630",
                                 "maine-score-insert-v543", "maine-score-put-v544",
                                 "maine-box-animate-v573", "maine-pic-copy-to-other-v651", "maine-cursor-advance-v643", "maine-box-bg-put-v647", "maine-cutscene-script-free-v582", "maine-box-bg-free-v585",
                                 "maine-script-param-first-v649", "maine-script-param-second-v590",
                                 "maine-cutscene-script-load-v614",
                                 "maine-cfg-resident-v604",
                                 "maine-game-exit-exec-v608", "maine-game-exit-v654", "maine-game-init-main-v656",
                                 "maine-end-animate-v616",
                                 "maine-score-load-for-v557", "op-stage-put-v545",
                                 "maine-scoredat-recreate-v580",
                                 "op-place-put-v552", "op-rank-render-v553", "op-clear-sprites-v554",
                                 "op-regist-menu-v556",
                                 "maine-stage-put-v547", "maine-name-cursor-v548", "maine-place-row-v549",
                                 "maine-places-v550", "maine-alphabet-cursor-v551"})
        if backend not in allowed_backend:
            raise ValueError(f"{ident}: wrong artifact replay backend")
        if artifact == "th04-zun":
            if (source_name not in ZUN_LINKED_SOURCES
                    or producer_start != ZUN_COMPONENT_OFFSET or producer_size != 0x18D8):
                raise ValueError(f"{ident}: ZUN backend does not compile this producer")
        elif backend == "op-maine-bgimage-v489":
            if (source_name != "src/shared/hardware/bgimage.cpp"
                    or producer_start != BGIMAGE_PRODUCERS[artifact] or producer_size != 0xD0):
                raise ValueError(f"{ident}: BGIMAGE backend does not compile this producer")
        elif backend == "op-maine-vram-v509":
            if (source_name != "src/shared/hardware/vram_planes.cpp"
                    or producer_start != VRAM_PRODUCERS[artifact] or producer_size != 0x29):
                raise ValueError(f"{ident}: VRAM backend does not compile this producer")
        elif backend == "op-maine-frame-delay-v510":
            if (source_name != "src/shared/hardware/frame_delay.cpp"
                    or producer_start != FRAME_DELAY_PRODUCERS[artifact] or producer_size != 0x15):
                raise ValueError(f"{ident}: frame-delay backend does not compile this producer")
        elif backend == "op-maine-pi-put-v511":
            if (source_name != "src/shared/formats/pi_put.cpp"
                    or producer_start != PI_PUT_PRODUCERS[artifact] or producer_size != 0xAD):
                raise ValueError(f"{ident}: PI put backend does not compile this producer")
        elif backend == "op-maine-pi-load-v511":
            if (source_name != "src/shared/formats/pi_load.cpp"
                    or producer_start != PI_LOAD_PRODUCERS[artifact] or producer_size != 0x46):
                raise ValueError(f"{ident}: PI load backend does not compile this producer")
        elif backend == "op-maine-pmd-v512":
            if (source_name != "src/shared/sound/pmd_resident.c"
                    or producer_start != PMD_PRODUCERS[artifact] or producer_size != 0x2E):
                raise ValueError(f"{ident}: PMD backend does not compile this producer")
        elif backend == "op-maine-mmd-v513":
            if (source_name != "src/shared/sound/mmd_resident.c"
                    or producer_start != MMD_PRODUCERS[artifact] or producer_size != 0x2F):
                raise ValueError(f"{ident}: MMD backend does not compile this producer")
        elif backend == "op-maine-kaja-v514":
            if (source_name != "src/shared/sound/kaja_interrupt.cpp"
                    or producer_start != KAJA_PRODUCERS[artifact] or producer_size != 0x1E):
                raise ValueError(f"{ident}: KAJA backend does not compile this producer")
        elif backend == "op-maine-mode-v515":
            if (source_name != "src/shared/sound/determine_modes.cpp"
                    or producer_start != MODE_PRODUCERS[artifact] or producer_size != 0x9C):
                raise ValueError(f"{ident}: mode backend does not compile this producer")
        elif backend == "maine-score-insert-v543":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/insert.cpp"
                    or producer_start != MAINE_SCORE_INSERT_PRODUCER
                    or producer_size != 0x154):
                raise ValueError(f"{ident}: MAINE score-insert backend does not compile this producer")
        elif backend == "maine-score-put-v544":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/put.cpp"
                    or producer_start != MAINE_SCORE_PUT_PRODUCER
                    or producer_size != 0xE6):
                raise ValueError(f"{ident}: MAINE score-put backend does not compile this producer")
        elif backend == "maine-box-animate-v573":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/box_animate.cpp"
                    or producer_start != MAINE_BOX_ANIMATE_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE box-animate backend does not compile this producer")
        elif backend == "maine-pic-copy-to-other-v651":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/pic_copy_to_other.cpp"
                    or producer_start != MAINE_PIC_COPY_TO_OTHER_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE pic-copy-to-other backend does not compile this producer")
        elif backend == "maine-cursor-advance-v643":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/cursor_advance.cpp"
                    or producer_start != MAINE_CURSOR_ADVANCE_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE cursor-advance backend does not compile this producer")
        elif backend == "maine-box-bg-put-v647":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/box_bg_put.cpp"
                    or producer_start != MAINE_BOX_BG_PUT_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE box-bg-put backend does not compile this producer")
        elif backend == "maine-cutscene-script-free-v582":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/script_free.cpp"
                    or producer_start != MAINE_CUTSCENE_SCRIPT_FREE_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE cutscene-script-free backend does not compile this producer")
        elif backend == "maine-box-bg-free-v585":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/box_bg_free.cpp"
                    or producer_start != MAINE_BOX_BG_FREE_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE box-bg-free backend does not compile this producer")
        elif backend == "maine-script-param-first-v649":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/script_param_first.cpp"
                    or producer_start != MAINE_SCRIPT_PARAM_FIRST_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE script-param-first backend does not compile this producer")
        elif backend == "maine-script-param-second-v590":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/script_param_second.cpp"
                    or producer_start != MAINE_SCRIPT_PARAM_SECOND_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE script-param-second backend does not compile this producer")
        elif backend == "maine-cutscene-script-load-v614":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/cutscene/script_load.cpp"
                    or producer_start != MAINE_CUTSCENE_SCRIPT_LOAD_PRODUCER
                    or producer_size != 0xC3E):
                raise ValueError(f"{ident}: MAINE cutscene-script-load backend does not compile this producer")
        elif backend == "maine-cfg-resident-v604":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/core/cfg_load_resident_ptr.cpp"
                    or producer_start != MAINE_CFG_RESIDENT_PRODUCER
                    or producer_size != 0x239):
                raise ValueError(f"{ident}: MAINE cfg-resident backend does not compile this producer")
        elif backend == "maine-game-exit-exec-v608":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/core/game_exit_and_exec.cpp"
                    or producer_start != MAINE_GAME_EXIT_EXEC_PRODUCER
                    or producer_size != 0x239):
                raise ValueError(f"{ident}: MAINE game-exit-exec backend does not compile this producer")
        elif backend == "maine-game-exit-v654":
            if (artifact != "th04-maine"
                    or source_name != "src/shared/core/game_exit.cpp"
                    or producer_start != MAINE_GAME_EXIT_PRODUCER
                    or producer_size != 0x48):
                raise ValueError(f"{ident}: MAINE shared-game-exit backend does not compile this producer")
        elif backend == "maine-game-init-main-v656":
            if (artifact != "th04-maine"
                    or source_name != "src/shared/core/game_init_main.cpp"
                    or producer_start != MAINE_GAME_INIT_MAIN_PRODUCER
                    or producer_size != 0x4E):
                raise ValueError(f"{ident}: MAINE game-init-main backend does not compile this producer")
        elif backend == "maine-end-animate-v616":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/end/end_animate.cpp"
                    or producer_start != MAINE_END_ANIMATE_PRODUCER
                    or producer_size != 0x239):
                raise ValueError(f"{ident}: MAINE end-animate backend does not compile this producer")
        elif backend == "maine-score-load-for-v557":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/load_for.cpp"
                    or producer_start != MAINE_SCORE_LOAD_FOR_PRODUCER
                    or producer_size != 0x69):
                raise ValueError(f"{ident}: MAINE score-load backend does not compile this producer")
        elif backend == "maine-scoredat-recreate-v580":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/scoregen.cpp"
                    or producer_start != MAINE_SCORE_RECREATE_PRODUCER
                    or producer_size != 0xA7):
                raise ValueError(f"{ident}: MAINE score-file regeneration backend does not compile this producer")
        elif backend == "maine-stage-put-v547":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/stage.cpp"
                    or producer_start != MAINE_STAGE_PUT_PRODUCER
                    or producer_size != 0x79):
                raise ValueError(f"{ident}: MAINE stage-put backend does not compile this producer")
        elif backend == "maine-name-cursor-v548":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/cursor.cpp"
                    or producer_start != MAINE_NAME_CURSOR_PRODUCER
                    or producer_size != 0xAC):
                raise ValueError(f"{ident}: MAINE name-cursor backend does not compile this producer")
        elif backend == "maine-place-row-v549":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/place.cpp"
                    or producer_start != MAINE_PLACE_ROW_PRODUCER
                    or producer_size != 0xB8):
                raise ValueError(f"{ident}: MAINE place-row backend does not compile this producer")
        elif backend == "maine-places-v550":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/places.cpp"
                    or producer_start != MAINE_PLACES_PRODUCER
                    or producer_size != 0x1A):
                raise ValueError(f"{ident}: MAINE places backend does not compile this producer")
        elif backend == "maine-alphabet-cursor-v551":
            if (artifact != "th04-maine"
                    or source_name != "src/maine/score/alpha.cpp"
                    or producer_start != MAINE_ALPHABET_CURSOR_PRODUCER
                    or producer_size != 0x31):
                raise ValueError(f"{ident}: MAINE alphabet-cursor backend does not compile this producer")
        elif backend == "op-score-load-both-v558":
            if (artifact != "th04-op"
                    or source_name != "src/op/score/loadboth.cpp"
                    or producer_start != OP_HISCORE_LOAD_BOTH_PRODUCER
                    or producer_size != 0x6B):
                raise ValueError(f"{ident}: OP high-score loader backend does not compile this producer")
        elif backend == "op-scores-put-v559":
            if (artifact != "th04-op"
                    or source_name != "src/op/score/scoreput.cpp"
                    or producer_start != OP_SCORES_PUT_PRODUCER
                    or producer_size != 0x107):
                raise ValueError(f"{ident}: OP scores-put backend does not compile this producer")
        elif backend == "op-scoredat-recreate-v561":
            if (artifact != "th04-op"
                    or source_name != "src/op/score/scoregen.cpp"
                    or producer_start != OP_SCOREDAT_RECREATE_PRODUCER
                    or producer_size != 0xA7):
                raise ValueError(f"{ident}: OP score-file regeneration backend does not compile this producer")
        elif backend == "op-main-cdg-free-v583":
            if (artifact != "th04-op"
                    or source_name != "src/op/title/main_cdg_free.cpp"
                    or producer_start != OP_MAIN_CDG_FREE_PRODUCER
                    or producer_size != 0x2C7):
                raise ValueError(f"{ident}: OP main-CDG-free backend does not compile this producer")
        elif backend == "op-main-cdg-load-v602":
            if (artifact != "th04-op"
                    or source_name != "src/op/title/main_cdg_load.cpp"
                    or producer_start != OP_MAIN_CDG_LOAD_PRODUCER
                    or producer_size != 0x2C7):
                raise ValueError(f"{ident}: OP main-CDG-load backend does not compile this producer")
        elif backend == "op-nopoly-free-v584":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/nopoly_free.cpp"
                    or producer_start != OP_NOPOLY_FREE_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP nopoly-free backend does not compile this producer")
        elif backend == "op-nopoly-snap-v606":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/nopoly_snap.cpp"
                    or producer_start != OP_NOPOLY_SNAP_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP nopoly-snap backend does not compile this producer")
        elif backend == "op-frame-delay-2-v587":
            if (artifact != "th04-op"
                    or source_name != "src/op/hardware/frame_delay_2.cpp"
                    or producer_start != OP_FRAME_DELAY_2_PRODUCER
                    or producer_size != 0x15):
                raise ValueError(f"{ident}: OP frame-delay-2 backend does not compile this producer")
        elif backend == "op-raise-bg-free-v588":
            if (artifact != "th04-op"
                    or source_name != "src/op/menu/raise_bg_free.cpp"
                    or producer_start != OP_RAISE_BG_FREE_PRODUCER
                    or producer_size != 0xAB3):
                raise ValueError(f"{ident}: OP raise-bg-free backend does not compile this producer")
        elif backend == "op-playchar-title-box-v638":
            if (artifact != "th04-op"
                    or source_name != "src/op/menu/playchar_title_box_put.cpp"
                    or producer_start != OP_PLAYCHAR_TITLE_BOX_PRODUCER
                    or producer_size != 0xAB3):
                raise ValueError(f"{ident}: OP playchar-title-box backend does not compile this producer")
        elif backend == "op-pic-darken-v640":
            if (artifact != "th04-op"
                    or source_name != "src/op/menu/pic_darken.cpp"
                    or producer_start != OP_PIC_DARKEN_PRODUCER
                    or producer_size != 0xAB3):
                raise ValueError(f"{ident}: OP pic-darken backend does not compile this producer")
        elif backend == "op-shottype-menu-initial-v660":
            if (artifact != "th04-op"
                    or source_name != "src/op/menu/shottype_menu_initial.cpp"
                    or producer_start != OP_SHOTTYPE_MENU_INITIAL_PRODUCER
                    or producer_size != 0xAB3):
                raise ValueError(f"{ident}: OP shottype-menu-initial backend does not compile this producer")
        elif backend == "op-playchar-menu-initial-v658":
            if (artifact != "th04-op"
                    or source_name != "src/op/menu/playchar_menu_initial.cpp"
                    or producer_start != OP_PLAYCHAR_MENU_INITIAL_PRODUCER
                    or producer_size != 0xAB3):
                raise ValueError(f"{ident}: OP playchar-menu-initial backend does not compile this producer")
        elif backend == "op-game-exit-to-dos-v592":
            if (artifact != "th04-op"
                    or source_name != "src/op/core/game_exit_to_dos.cpp"
                    or producer_start != OP_GAME_EXIT_TO_DOS_PRODUCER
                    or producer_size != 0x19):
                raise ValueError(f"{ident}: OP game-exit-to-dos backend does not compile this producer")
        elif backend == "op-game-exit-v654":
            if (artifact != "th04-op"
                    or source_name != "src/shared/core/game_exit.cpp"
                    or producer_start != OP_GAME_EXIT_PRODUCER
                    or producer_size != 0x48):
                raise ValueError(f"{ident}: OP shared-game-exit backend does not compile this producer")
        elif backend == "op-tracklist-put-both-v594":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/tracklist_put_both.cpp"
                    or producer_start != OP_TRACKLIST_PUT_BOTH_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP tracklist-put-both backend does not compile this producer")
        elif backend == "op-track-put-both-v636":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/track_put_both.cpp"
                    or producer_start != OP_TRACK_PUT_BOTH_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP track-put-both backend does not compile this producer")
        elif backend == "op-cmt-unput-v598":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/cmt_unput_both_animate.cpp"
                    or producer_start != OP_CMT_UNPUT_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP cmt-unput backend does not compile this producer")
        elif backend == "op-cmt-fadein-v600":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/cmt_fadein_both_animate.cpp"
                    or producer_start != OP_CMT_FADEIN_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP cmt-fadein backend does not compile this producer")
        elif backend == "op-cmt-put-v618":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/cmt_put.cpp"
                    or producer_start != OP_CMT_PUT_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP cmt-put backend does not compile this producer")
        elif backend == "op-cmt-load-v620":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/cmt_load.cpp"
                    or producer_start != OP_CMT_LOAD_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP cmt-load backend does not compile this producer")
        elif backend == "op-cmt-transition-v622":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/cmt_load_unput_and_put_both_animate.cpp"
                    or producer_start != OP_CMT_TRANSITION_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP cmt-transition backend does not compile this producer")
        elif backend == "op-music-update-flip-v610":
            if (artifact != "th04-op"
                    or source_name != "src/op/music/music_update_render_and_flip.cpp"
                    or producer_start != OP_MUSIC_UPDATE_PRODUCER
                    or producer_size != 0x6A5):
                raise ValueError(f"{ident}: OP music-update-flip backend does not compile this producer")
        elif backend == "op-help-put-v596":
            if (artifact != "th04-op"
                    or source_name != "src/op/setup/help_put.cpp"
                    or producer_start != OP_HELP_PUT_PRODUCER
                    or producer_size != 0x5A6):
                raise ValueError(f"{ident}: OP help-put backend does not compile this producer")
        elif backend == "op-rollup-v612":
            if (artifact != "th04-op"
                    or source_name != "src/op/setup/rollup.cpp"
                    or producer_start != OP_ROLLUP_PRODUCER
                    or producer_size != 0x5A6):
                raise ValueError(f"{ident}: OP rollup backend does not compile this producer")
        elif backend == "op-bgm-choice-v624":
            if (artifact != "th04-op"
                    or source_name != "src/op/setup/bgm_choice_put.cpp"
                    or producer_start != OP_BGM_CHOICE_PRODUCER
                    or producer_size != 0x5A6):
                raise ValueError(f"{ident}: OP BGM-choice backend does not compile this producer")
        elif backend == "op-se-choice-v626":
            if (artifact != "th04-op"
                    or source_name != "src/op/setup/se_choice_put.cpp"
                    or producer_start != OP_SE_CHOICE_PRODUCER
                    or producer_size != 0x5A6):
                raise ValueError(f"{ident}: OP SE-choice backend does not compile this producer")
        elif backend == "op-window-rollup-put-v628":
            if (artifact != "th04-op"
                    or source_name != "src/op/setup/window_rollup_put.cpp"
                    or producer_start != OP_WINDOW_ROLLUP_PUT_PRODUCER
                    or producer_size != 0x5A6):
                raise ValueError(f"{ident}: OP window-rollup-put backend does not compile this producer")
        elif backend == "op-window-dropdown-put-v632":
            if (artifact != "th04-op"
                    or source_name != "src/op/setup/window_dropdown_put.cpp"
                    or producer_start != OP_WINDOW_DROPDOWN_PUT_PRODUCER
                    or producer_size != 0x5A6):
                raise ValueError(f"{ident}: OP window-dropdown-put backend does not compile this producer")
        elif backend == "op-singleline-v634":
            if (artifact != "th04-op"
                    or source_name != "src/op/setup/singleline.cpp"
                    or producer_start != OP_SINGLELINE_PRODUCER
                    or producer_size != 0x5A6):
                raise ValueError(f"{ident}: OP singleline backend does not compile this producer")
        elif backend == "op-dropdown-v630":
            if (artifact != "th04-op"
                    or source_name != "src/op/setup/dropdown.cpp"
                    or producer_start != OP_DROPDOWN_PRODUCER
                    or producer_size != 0x5A6):
                raise ValueError(f"{ident}: OP dropdown backend does not compile this producer")
        elif backend == "op-stage-put-v545":
            if (artifact != "th04-op"
                    or source_name != "src/op/score/stage.cpp"
                    or producer_start != OP_STAGE_PUT_PRODUCER
                    or producer_size != 0x50):
                raise ValueError(f"{ident}: OP stage-put backend does not compile this producer")
        elif backend == "op-place-put-v552":
            if (artifact != "th04-op"
                    or source_name != "src/op/score/place.cpp"
                    or producer_start != OP_PLACE_PUT_PRODUCER
                    or producer_size != 0x125):
                raise ValueError(f"{ident}: OP place-put backend does not compile this producer")
        elif backend == "op-rank-render-v553":
            if (artifact != "th04-op"
                    or source_name != "src/op/score/rank.cpp"
                    or producer_start != OP_RANK_RENDER_PRODUCER
                    or producer_size != 0x7A):
                raise ValueError(f"{ident}: OP rank-render backend does not compile this producer")
        elif backend == "op-regist-menu-v556":
            if (artifact != "th04-op"
                    or source_name != "src/op/score/menu.cpp"
                    or producer_start != OP_REGIST_MENU_PRODUCER
                    or producer_size != 0x14F):
                raise ValueError(f"{ident}: OP registration-menu backend does not compile this producer")
        elif backend == "op-clear-sprites-v554":
            if (artifact != "th04-op"
                    or source_name != "src/op/score/clear.cpp"
                    or producer_start != OP_CLEAR_SPRITES_PRODUCER
                    or producer_size != 0xB4):
                raise ValueError(f"{ident}: OP clear-sprites backend does not compile this producer")
        elif backend == "op-maine-input-wait-v565":
            if (source_name != "src/shared/hardware/input_wait.cpp"
                    or producer_start != INPUT_WAIT_PRODUCERS[artifact]
                    or producer_size != 0x56):
                raise ValueError(f"{ident}: input-wait backend does not compile this producer")
        elif backend == "op-maine-se-reset-v581":
            if (source_name != "src/shared/sound/se_reset.cpp"
                    or producer_start != SE_RESET_PRODUCERS[artifact]
                    or producer_size != 0x0C):
                raise ValueError(f"{ident}: sound-effect reset backend does not compile this producer")
        elif backend == "op-maine-vector-math-v570":
            if (source_name != "src/shared/math/vector.cpp"
                    or producer_start != VECTOR_MATH_PRODUCERS[artifact]
                    or producer_size != 0x5E):
                raise ValueError(f"{ident}: vector-math backend does not compile this producer")
        elif (source_name != "src/shared/sound/delay_until_measure.cpp"
              or producer_start != DELAY_PRODUCERS[artifact] or producer_size != 0x31):
            raise ValueError(f"{ident}: delay backend does not compile this producer")
        evidence_id = entry["replay_evidence_id"]
        if evidence_id not in evidence_by_id or evidence_by_id[evidence_id]["artifact"] != artifact:
            raise ValueError(f"{ident}: missing artifact-local replay evidence")
        state = entry["decoded_state"]
        if state not in {"decoded-exact", "source-present"}:
            raise ValueError(f"{ident}: invalid decoded acceptance state")
        if state == "decoded-exact":
            if boundary["accepted_state"] != "exact" or evidence_id not in owner["evidence_ids"].split(";"):
                raise ValueError(f"{ident}: decoded exact conflicts with existing ledgers")
            raw_id = entry["raw_evidence_id"]
            raw = evidence_by_id.get(raw_id)
            if (
                raw is None or raw["oracle"] != "raw-bytes"
                or raw["artifact"] != artifact or raw["unit_id"] != owner["id"]
                or raw["result"] != "pass" or raw["evidence_class"] != "binary"
                or not raw["extent_start"] or not raw["extent_size"]
                or number(raw["extent_start"], raw_id) != start
                or number(raw["extent_size"], raw_id) != size
                or raw["input_sha256"] != digest or raw["output_sha256"] != digest
                or not all(raw[field] for field in ("location", "tool", "command", "observed_utc"))
            ):
                raise ValueError(f"{ident}: missing exact function-scoped raw evidence")
            supporting = {
                ev["oracle"] for eid in owner["evidence_ids"].split(";")
                if (ev := evidence_by_id.get(eid)) is not None
                and ev["artifact"] == artifact and ev["result"] == "pass"
                and valid_digest(ev["input_sha256"])
                and valid_digest(ev["output_sha256"])
                and ev["extent_start"] and ev["extent_size"]
                and number(ev["extent_start"], eid) == producer_start
                and number(ev["extent_size"], eid) == producer_size
            }
            if not REQUIRED_PRODUCER_ORACLES.issubset(supporting):
                raise ValueError(f"{ident}: missing producer-scoped exact evidence")
        elif boundary["accepted_state"] == "exact":
            raise ValueError(f"{ident}: exact boundary cannot be diagnostic")
        elif entry["raw_evidence_id"]:
            raise ValueError(f"{ident}: diagnostic row cannot claim raw equality")
    if seen & exact_boundaries != exact_boundaries:
        raise ValueError(f"missing decoded-exact boundary rows: {sorted(exact_boundaries - seen)}")


def compare_extent(
    entry: dict[str, str], target: bytes, candidate: bytes, *, candidate_origin: int = 0
) -> dict[str, object]:
    """Compare the complete physical function slice without normalization."""

    ident = entry["boundary_id"]
    offset = number(entry["payload_offset"], ident)
    size = number(entry["size"], ident)
    local = offset - candidate_origin
    if offset + size > len(target) or local < 0 or local + size > len(candidate):
        raise ValueError(f"{ident}: truncated target or candidate extent")
    expected = target[offset:offset + size]
    actual = candidate[local:local + size]
    if sha(expected) != entry["target_sha256"]:
        raise ValueError(f"{ident}: attested target slice changed")
    differences = [index for index, pair in enumerate(zip(expected, actual)) if pair[0] != pair[1]]
    return {
        "boundary_id": ident,
        "segment_identity": entry["segment_identity"],
        "payload_offset": entry["payload_offset"],
        "size": size,
        "source": entry["source"],
        "source_sha256": sha((ROOT / entry["source"]).read_bytes()),
        "decoded_state": entry["decoded_state"],
        "target_slice_sha256": sha(expected),
        "candidate_slice_sha256": sha(actual),
        "raw_difference_count": len(differences),
        "first_difference_offsets": differences[:16],
    }


def require_exact_zero(results: list[dict[str, object]]) -> None:
    failed = [row["boundary_id"] for row in results
              if row["decoded_state"] == "decoded-exact" and row["raw_difference_count"]]
    if failed:
        raise RuntimeError(f"decoded-exact rows no longer raw-match: {failed}")


def output_directory(requested: Path | None) -> Path:
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    private.mkdir(parents=True, exist_ok=True)
    if requested is None:
        return Path(tempfile.mkdtemp(prefix="decoded-acceptance-", dir=private))
    output = requested.resolve()
    if output.exists() or output.parent != private:
        raise ValueError("output must be a new direct child of .analysis/reconstruction/probes")
    output.mkdir()
    return output


def verified_target(artifact: str) -> tuple[bytes, str, str]:
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text(encoding="utf-8"))
    info = next(row for row in manifest["artifacts"] if row["id"] == artifact)
    packed = (ROOT / info["private_path"]).read_bytes()
    if len(packed) != info["size"] or sha(packed) != info["sha256"]:
        raise ValueError(f"{artifact}: packed target identity drift")
    if not parse_mz(packed).valid:
        raise ValueError(f"{artifact}: packed target MZ integrity failure")
    if artifact == "th04-zun":
        decoded = ZUN_PAYLOAD.read_bytes()
        expected = ZUN_PAYLOAD_SHA256
    else:
        restored = RESTORED[artifact].read_bytes()
        if sha(restored) != RESTORED_SHA256[artifact]:
            raise ValueError(f"{artifact}: target-derived DIET restore drift")
        mz = parse_mz(restored)
        if not mz.valid:
            raise ValueError(f"{artifact}: invalid restored MZ")
        decoded = mz.program_image
        expected = sha(decoded)
    if sha(decoded) != expected:
        raise ValueError(f"{artifact}: decoded target identity drift")
    return decoded, info["sha256"], expected


def backend_command(backend_id: str, saved: Path, *, artifact: str | None = None) -> list[str]:
    """Return the exact cold replay command for one accepted backend ID."""
    if backend_id == "zun-resident-link":
        return [sys.executable, "scripts/probes/replay_th04_zun_separate_link.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-vram-v509":
        return [sys.executable, "scripts/probes/replay_th04_shared_vram.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-frame-delay-v510":
        return [sys.executable, "scripts/probes/replay_th04_shared_frame_delay.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-pi-put-v511":
        return [sys.executable, "scripts/probes/replay_th04_shared_pi_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-pi-load-v511":
        return [sys.executable, "scripts/probes/replay_th04_shared_pi_load.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-pmd-v512":
        return [sys.executable, "scripts/probes/replay_th04_shared_pmd.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-mmd-v513":
        return [sys.executable, "scripts/probes/replay_th04_shared_mmd.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-kaja-v514":
        return [sys.executable, "scripts/probes/replay_th04_shared_kaja.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-mode-v515":
        return [sys.executable, "scripts/probes/replay_th04_shared_mode.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-delay-v516":
        return [sys.executable, "scripts/probes/replay_th04_shared_delay_measure.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-input-wait-v565":
        if artifact not in {"th04-op", "th04-maine"}:
            raise ValueError("input-wait backend requires one OP/MAINE artifact")
        return [sys.executable, "scripts/probes/replay_th04_shared_input_wait.py",
                "--artifact", artifact, "--retain-candidates", "--output-dir", str(saved)]
    if backend_id == "op-maine-se-reset-v581":
        if artifact not in {"th04-op", "th04-maine"}:
            raise ValueError("sound-effect reset backend requires one OP/MAINE artifact")
        return [sys.executable, "scripts/probes/replay_th04_shared_se_reset.py",
                "--artifact", artifact, "--retain-candidates", "--output-dir", str(saved)]
    if backend_id == "op-maine-vector-math-v570":
        if artifact not in {"th04-op", "th04-maine"}:
            raise ValueError("vector-math backend requires one OP/MAINE artifact")
        return [sys.executable, "scripts/probes/replay_th04_shared_vector_math.py",
                "--artifact", artifact, "--retain-candidates", "--output-dir", str(saved)]
    if backend_id == "op-score-load-both-v558":
        return [sys.executable, "scripts/probes/replay_th04_op_score_load_both.py",
                "--output-dir", str(saved)]
    if backend_id == "op-scores-put-v559":
        return [sys.executable, "scripts/probes/replay_th04_op_scores_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-scoredat-recreate-v561":
        return [sys.executable, "scripts/probes/replay_th04_op_scoredat_recreate.py",
                "--output-dir", str(saved)]
    if backend_id == "op-main-cdg-free-v583":
        return [sys.executable, "scripts/probes/replay_th04_op_main_cdg_free.py",
                "--output-dir", str(saved)]
    if backend_id == "op-main-cdg-load-v602":
        return [sys.executable, "scripts/probes/replay_th04_op_main_cdg_load.py",
                "--output-dir", str(saved)]
    if backend_id == "op-nopoly-free-v584":
        return [sys.executable, "scripts/probes/replay_th04_op_nopoly_free.py",
                "--output-dir", str(saved)]
    if backend_id == "op-nopoly-snap-v606":
        return [sys.executable, "scripts/probes/replay_th04_op_nopoly_snap.py",
                "--output-dir", str(saved)]
    if backend_id == "op-frame-delay-2-v587":
        return [sys.executable, "scripts/probes/replay_th04_op_frame_delay_2.py",
                "--retain-candidates", "--output-dir", str(saved)]
    if backend_id == "op-raise-bg-free-v588":
        return [sys.executable, "scripts/probes/replay_th04_op_raise_bg_free.py",
                "--output-dir", str(saved)]
    if backend_id == "op-playchar-title-box-v638":
        return [sys.executable, "scripts/probes/replay_th04_op_playchar_title_box_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-pic-darken-v640":
        return [sys.executable, "scripts/probes/replay_th04_op_pic_darken.py",
                "--output-dir", str(saved)]
    if backend_id == "op-shottype-menu-initial-v660":
        return [sys.executable, "scripts/probes/replay_th04_op_shottype_menu_initial.py",
                "--output-dir", str(saved)]
    if backend_id == "op-playchar-menu-initial-v658":
        return [sys.executable, "scripts/probes/replay_th04_op_playchar_menu_initial.py",
                "--output-dir", str(saved)]
    if backend_id == "op-game-exit-to-dos-v592":
        return [sys.executable, "scripts/probes/replay_th04_op_game_exit_to_dos.py",
                "--output-dir", str(saved)]
    if backend_id == "op-game-exit-v654":
        return [sys.executable, "scripts/probes/replay_th04_op_maine_game_exit.py",
                "--artifact", "op", "--output-dir", str(saved)]
    if backend_id == "op-tracklist-put-both-v594":
        return [sys.executable, "scripts/probes/replay_th04_op_tracklist_put_both.py",
                "--output-dir", str(saved)]
    if backend_id == "op-track-put-both-v636":
        return [sys.executable, "scripts/probes/replay_th04_op_track_put_both.py",
                "--output-dir", str(saved)]
    if backend_id == "op-cmt-unput-v598":
        return [sys.executable, "scripts/probes/replay_th04_op_cmt_unput_both_animate.py",
                "--output-dir", str(saved)]
    if backend_id == "op-cmt-fadein-v600":
        return [sys.executable, "scripts/probes/replay_th04_op_cmt_fadein_both_animate.py",
                "--output-dir", str(saved)]
    if backend_id == "op-cmt-put-v618":
        return [sys.executable, "scripts/probes/replay_th04_op_cmt_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-cmt-load-v620":
        return [sys.executable, "scripts/probes/replay_th04_op_cmt_load.py",
                "--output-dir", str(saved)]
    if backend_id == "op-cmt-transition-v622":
        return [sys.executable, "scripts/probes/replay_th04_op_cmt_load_unput_and_put_both_animate.py",
                "--output-dir", str(saved)]
    if backend_id == "op-music-update-flip-v610":
        return [sys.executable, "scripts/probes/replay_th04_op_music_update_render_and_flip.py",
                "--output-dir", str(saved)]
    if backend_id == "op-help-put-v596":
        return [sys.executable, "scripts/probes/replay_th04_op_help_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-rollup-v612":
        return [sys.executable, "scripts/probes/replay_th04_op_rollup.py",
                "--output-dir", str(saved)]
    if backend_id == "op-bgm-choice-v624":
        return [sys.executable, "scripts/probes/replay_th04_op_bgm_choice_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-se-choice-v626":
        return [sys.executable, "scripts/probes/replay_th04_op_se_choice_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-window-rollup-put-v628":
        return [sys.executable, "scripts/probes/replay_th04_op_window_rollup_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-window-dropdown-put-v632":
        return [sys.executable, "scripts/probes/replay_th04_op_window_dropdown_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-singleline-v634":
        return [sys.executable, "scripts/probes/replay_th04_op_singleline.py",
                "--output-dir", str(saved)]
    if backend_id == "op-dropdown-v630":
        return [sys.executable, "scripts/probes/replay_th04_op_dropdown.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-score-insert-v543":
        return [sys.executable, "scripts/probes/replay_th04_maine_score_insert.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-box-animate-v573":
        return [sys.executable, "scripts/probes/replay_th04_maine_box_animate.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-pic-copy-to-other-v651":
        return [sys.executable, "scripts/probes/replay_th04_maine_pic_copy_to_other.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-cursor-advance-v643":
        return [sys.executable, "scripts/probes/replay_th04_maine_cursor_advance.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-box-bg-put-v647":
        return [sys.executable, "scripts/probes/replay_th04_maine_box_bg_put.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-cutscene-script-free-v582":
        return [sys.executable, "scripts/probes/replay_th04_maine_cutscene_script_free.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-box-bg-free-v585":
        return [sys.executable, "scripts/probes/replay_th04_maine_box_bg_free.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-script-param-first-v649":
        return [sys.executable, "scripts/probes/replay_th04_maine_script_param_first.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-script-param-second-v590":
        return [sys.executable, "scripts/probes/replay_th04_maine_script_param_second.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-cutscene-script-load-v614":
        return [sys.executable, "scripts/probes/replay_th04_maine_script_load.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-cfg-resident-v604":
        return [sys.executable, "scripts/probes/replay_th04_maine_cfg_resident_ptr.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-game-exit-exec-v608":
        return [sys.executable, "scripts/probes/replay_th04_maine_game_exit_and_exec.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-game-exit-v654":
        return [sys.executable, "scripts/probes/replay_th04_op_maine_game_exit.py",
                "--artifact", "maine", "--output-dir", str(saved)]
    if backend_id == "maine-game-init-main-v656":
        return [sys.executable, "scripts/probes/replay_th04_maine_game_init_main.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-end-animate-v616":
        return [sys.executable, "scripts/probes/replay_th04_maine_end_animate.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-score-put-v544":
        return [sys.executable, "scripts/probes/replay_th04_maine_score_put.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-score-load-for-v557":
        return [sys.executable, "scripts/probes/replay_th04_maine_score_load_for.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-scoredat-recreate-v580":
        return [sys.executable, "scripts/probes/replay_th04_maine_scoredat_recreate.py",
                "--retain-candidates", "--output-dir", str(saved)]
    if backend_id == "maine-stage-put-v547":
        return [sys.executable, "scripts/probes/replay_th04_maine_stage_put.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-name-cursor-v548":
        return [sys.executable, "scripts/probes/replay_th04_maine_name_cursor.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-place-row-v549":
        return [sys.executable, "scripts/probes/replay_th04_maine_place_row.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-places-v550":
        return [sys.executable, "scripts/probes/replay_th04_maine_places.py",
                "--output-dir", str(saved)]
    if backend_id == "maine-alphabet-cursor-v551":
        return [sys.executable, "scripts/probes/replay_th04_maine_alphabet_cursor.py",
                "--output-dir", str(saved)]
    if backend_id == "op-stage-put-v545":
        return [sys.executable, "scripts/probes/replay_th04_op_stage_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-place-put-v552":
        return [sys.executable, "scripts/probes/replay_th04_op_place_put.py",
                "--output-dir", str(saved)]
    if backend_id == "op-rank-render-v553":
        return [sys.executable, "scripts/probes/replay_th04_op_rank_render.py",
                "--output-dir", str(saved)]
    if backend_id == "op-regist-menu-v556":
        return [sys.executable, "scripts/probes/replay_th04_op_regist_view_menu.py",
                "--output-dir", str(saved)]
    if backend_id == "op-clear-sprites-v554":
        return [sys.executable, "scripts/probes/replay_th04_op_clear_sprites.py",
                "--output-dir", str(saved)]
    if backend_id == "op-maine-bgimage-v489":
        snapshot = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a"
        return [
            sys.executable, "scripts/probes/probe_th04_bgimage_hybrid_v489.py",
            "--current-snapshot",
            "--op-source-dir", str(snapshot / "op/source"),
            "--maine-source-dir", str(snapshot / "maine/source"),
            "--op-target-restored", str(RESTORED["th04-op"]),
            "--maine-target-restored", str(RESTORED["th04-maine"]),
            "--output-dir", str(saved),
        ]
    raise ValueError(f"unknown decoded replay backend: {backend_id}")


def discard_backend_worktrees(saved: Path) -> list[str]:
    """Drop completed source snapshots and transient candidate MZ files only."""
    removed = []
    for label in ("a", "b"):
        for game in ("op", "maine"):
            source = saved / label / game / "source"
            if not source.exists() and not source.is_symlink():
                continue
            if (source.is_symlink() or not source.is_dir()
                    or not source.resolve().is_relative_to(saved.resolve())):
                raise RuntimeError(f"unsafe decoded backend worktree: {source}")
            shutil.rmtree(source)
            removed.append(source.relative_to(saved).as_posix())
    for game in ("op", "maine"):
        for label in ("a", "b"):
            candidate = saved / f"{label}-{game}.exe"
            if not candidate.exists() and not candidate.is_symlink():
                continue
            if (candidate.is_symlink() or not candidate.is_file()
                    or not candidate.resolve().is_relative_to(saved.resolve())):
                raise RuntimeError(f"unsafe decoded candidate artifact: {candidate}")
            candidate.unlink()
            removed.append(candidate.relative_to(saved).as_posix())
    return removed


def backend(artifact: str, backend_id: str, output: Path) -> tuple[list[bytes], int, dict[str, object]]:
    saved = output / backend_id
    command = backend_command(backend_id, saved, artifact=artifact)
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600)
    (output / f"{backend_id}.log").write_text(
        json.dumps(command) + f"\nexit={completed.returncode}\n"
        + completed.stdout + completed.stderr, encoding="utf-8"
    )
    if completed.returncode:
        raise RuntimeError(f"{artifact}: cold backend failed; see {output / f'{backend_id}.log'}")
    receipt = saved / "receipt.json"
    if not receipt.is_file():
        raise RuntimeError(f"{artifact}: cold backend omitted receipt")
    if backend_id == "zun-resident-link":
        candidate = [(saved / label / "res_huma.com").read_bytes() for label in ("a", "b")]
        if sha(candidate[0]) != sha(candidate[1]):
            raise RuntimeError("ZUN cold component links disagree")
        if len(candidate[0]) != 0x18D8:
            raise RuntimeError("ZUN component size drift")
        target = ZUN_PAYLOAD.read_bytes()[ZUN_COMPONENT_OFFSET:ZUN_COMPONENT_OFFSET + 0x18D8]
        if sha(target) != ZUN_COMPONENT_SHA256:
            raise RuntimeError("ZUN target component identity drift")
        origin = ZUN_COMPONENT_OFFSET
        layout = {"component_size": len(candidate[0]), "component_sha256": sha(candidate[0]),
                  "target_component_sha256": sha(target)}
    elif backend_id in {"op-maine-input-wait-v565", "op-maine-se-reset-v581", "op-maine-vector-math-v570"}:
        name = "op" if artifact == "th04-op" else "maine"
        target_mz = parse_mz(RESTORED[artifact].read_bytes())
        images = [parse_mz((saved / f"{label}-{name}.exe").read_bytes())
                  for label in ("a", "b")]
        if any(not image.valid for image in images):
            raise RuntimeError(f"{artifact}: invalid cold linked MZ")
        target_relocs = [item.linear for item in target_mz.relocations]
        if any([item.linear for item in image.relocations] != target_relocs for image in images):
            raise RuntimeError(f"{artifact}: ordered relocation mismatch")
        candidate = [image.program_image for image in images]
        if candidate[0] != candidate[1]:
            raise RuntimeError(f"{artifact}: cold linked program images disagree")
        origin = 0
        layout = {"ordered_relocations": len(target_relocs),
                  "candidate_program_size": len(candidate[0]),
                  "target_program_size": len(target_mz.program_image)}
    else:
        name = "op" if artifact == "th04-op" else "maine"
        target_mz = parse_mz(RESTORED[artifact].read_bytes())
        images = []
        for label in ("a", "b"):
            path = (saved / label / name / "source/bin/th04" / f"{name}.exe")
            images.append(parse_mz(path.read_bytes()))
        if any(not image.valid for image in images):
            raise RuntimeError(f"{artifact}: invalid cold linked MZ")
        target_relocs = [item.linear for item in target_mz.relocations]
        if any([item.linear for item in image.relocations] != target_relocs for image in images):
            raise RuntimeError(f"{artifact}: ordered relocation mismatch")
        candidate = [image.program_image for image in images]
        if candidate[0] != candidate[1]:
            raise RuntimeError(f"{artifact}: cold linked program images disagree")
        origin = 0
        layout = {"ordered_relocations": len(target_relocs),
                  "candidate_program_size": len(candidate[0]),
                  "target_program_size": len(target_mz.program_image)}
    return candidate, origin, {
        "command": command, "receipt_sha256": sha(receipt.read_bytes()), "layout": layout,
    }


def replay(artifact: str, entries: list[dict[str, str]], output: Path,
           *, keep_workdirs: bool = False) -> dict[str, object]:
    target, packed_sha, decoded_sha = verified_target(artifact)
    selected = [entry for entry in entries if entry["artifact"] == artifact]
    if not selected:
        raise ValueError(f"{artifact}: no decoded acceptance entries")
    source_hashes = {entry["source"]: sha((ROOT / entry["source"]).read_bytes())
                     for entry in selected}
    groups: dict[str, list[dict[str, str]]] = {}
    for entry in selected:
        groups.setdefault(entry["replay_backend"], []).append(entry)
    compared: list[dict[str, object]] = []
    builds: dict[str, dict[str, object]] = {}
    candidates: dict[str, list[str]] = {}
    for backend_id, group in groups.items():
        candidate_rounds, origin, build = backend(artifact, backend_id, output)
        rounds = [
            [compare_extent(entry, target, candidate, candidate_origin=origin) for entry in group]
            for candidate in candidate_rounds
        ]
        if rounds[0] != rounds[1]:
            raise RuntimeError(f"{artifact}/{backend_id}: cold function comparisons disagree")
        require_exact_zero(rounds[0])
        if any(sha((ROOT / entry["source"]).read_bytes()) != source_hashes[entry["source"]]
               for entry in group):
            raise RuntimeError(f"{artifact}/{backend_id}: maintained source changed during replay")
        build["discarded_replay_worktrees"] = (
            [] if keep_workdirs else discard_backend_worktrees(output / backend_id)
        )
        compared.extend(rounds[0])
        builds[backend_id] = build
        candidates[backend_id] = [sha(candidate) for candidate in candidate_rounds]
    if any(sha((ROOT / source).read_bytes()) != digest
           for source, digest in source_hashes.items()):
        raise RuntimeError(f"{artifact}: maintained source changed during cold replay")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": artifact,
        "packed_target_sha256": packed_sha,
        "decoded_target_sha256": decoded_sha,
        "candidate_round_sha256": candidates,
        "backends": builds,
        "functions": compared,
        "limit": "Decoded artifact-local function comparison only; no raw packed-file byte or standalone product acceptance.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", choices=sorted(ARTIFACTS), help="run the cold artifact backend")
    parser.add_argument("--output-dir", type=Path, help="new private receipt directory")
    parser.add_argument("--keep-workdirs", action="store_true",
                        help="retain large generated A/B source snapshots for debugging")
    args = parser.parse_args()
    entries = rows(LEDGER, HEADER)
    validate(
        entries,
        rows(ROOT / "config/th04_function_boundaries.csv"),
        rows(ROOT / "config/units.csv"),
        rows(ROOT / "config/evidence.csv"),
    )
    print(f"decoded function ledger: PASS ({len(entries)} rows; 3 artifacts)")
    if args.artifact:
        output = output_directory(args.output_dir)
        receipt = replay(args.artifact, entries, output,
                         keep_workdirs=args.keep_workdirs)
        print(f"{args.artifact}: {len(receipt['functions'])} slices checked; receipt: {output / 'receipt.json'}")
    elif args.output_dir:
        parser.error("--output-dir requires --artifact")
    elif args.keep_workdirs:
        parser.error("--keep-workdirs requires --artifact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
