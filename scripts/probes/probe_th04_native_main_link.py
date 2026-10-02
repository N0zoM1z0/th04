#!/usr/bin/env python3
"""Link the maintained TH04 MAIN physical roots and report the frontier.

This is a native-link diagnostic, not an exact MAIN build.  It preserves the
historical basename for manifest-routed owners (Borland derives default
segment names from that basename), compiles one object per physical C/C++
root, assembles the eight maintained DATA/BSS owners, and records TLINK's
unresolved/duplicate/group/fixup frontier.  The external ``masters.lib`` is
calibration only; ``--without-support`` is the TH04-source-only control.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis/reconstruction/probes").resolve()
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
SUPPORT_LIB = ROOT / "_reference/ReC98/bin/masters.lib"
SUPPORT_SHA256 = "6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6"
MANIFEST = ROOT / "config/native_main_sources.toml"
STATE_SOURCES = (
    Path("src/main/core/frame_state.asm"),
    Path("src/main/core/quit_state.asm"),
    Path("src/main/core/slowdown_state.asm"),
    Path("src/main/dialog/data.asm"),
    Path("src/main/dialog/script_state.asm"),
    Path("src/main/dialog/state.asm"),
    Path("src/main/scroll/page_state.asm"),
    Path("src/main/scroll/state.asm"),
)
SOURCE_SUFFIXES = {".c", ".cpp"}
SOURCE_ROOTS = (ROOT / "src/main", ROOT / "src/shared")
ASM_CACHE: dict[str, tuple[dict[str, object], Path]] = {}
LAYOUT_ANCHOR = Path("src/main/layout/main_code_order_anchor.asm")

# These are physical alternatives with duplicate publics.  The manifest's
# product owner is the left-hand side; the other producer stays available for
# its own focused replay but is not a MAIN link input.
SOURCE_EXCLUSIONS = {
    "src/main/item/splashes_init.cpp",
    "src/main/player/reimu_shot_b.cpp",
    "src/shared/core/game_exit.cpp",
    "src/shared/core/game_init_main.cpp",
    "src/shared/hardware/input_wait.cpp",
    "src/shared/math/vector.cpp",
}
# MAIN's large-model support library already owns the near `_TEXT` GRCG
# entry points consumed by its `superzom`/`supercln` modules.  The maintained
# far display-control owner is still used by OP/MAINE, but linking it here
# shadows masters.lib and creates unavoidable near-call fixup overflows.
ASM_EXCLUSIONS = {
    # MAIN is large-model: its runtime declaration passes a far string.
    # Keep the near implementation for ZUN/small-model consumers and link the
    # MAIN-owned far ABI implementation instead.
    "src/shared/dos/dos_puts2.asm",
}
# These maintained ASM files are intentionally body-only: the CIRCLE aggregate
# wrapper supplies their historical segment/extern/structure context.  The
# native diagnostic assembles each physical owner separately, so materialize a
# private context wrapper while keeping the current checked-in body as the
# source of emitted bytes.  The historical prefix/suffix are context only and
# never enter product source or exactness credit.
BODY_ONLY_SOURCES = frozenset({
    "src/main/boss/yuuka5_backdrop.asm",
    "src/main/bullet/invalidate.asm",
    "src/main/bullet/pellet_render.asm",
    "src/main/formats/bb_txt_put.asm",
    "src/main/formats/mpn_render.asm",
    "src/main/formats/z_super_put_16x16_mono.asm",
    "src/main/hardware/fillm64_56_256_256.asm",
    "src/main/player/shot_laser.asm",
    "src/main/pointnum/lifecycle.asm",
    "src/main/pointnum/put.asm",
    "src/main/pointnum/render.asm",
    "src/main/tile/bb_mask.asm",
})
FLAGS = (
    "-c", "-I.", "-Isrc/main/include", "-O", "-b-", "-3", "-Z", "-d",
    "-DGAME=4", "-DTH04P", "-ml", "-DBINARY='M'",
)

sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_native_main_manifest import audit  # noqa: E402
from lib.th04_sprites import generate_sprite_sources  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run(command: list[str], cwd: Path, env: dict[str, str], log: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=300)
    log.write_text(json.dumps(command) + f"\nexit={result.returncode}\n"
                   + result.stdout + result.stderr, encoding="utf-8")
    return result


def source_tree_digest(sources: list[Path]) -> str:
    digest = hashlib.sha256()
    for source in sources:
        digest.update(source.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256(source)))
    return digest.hexdigest()


def body_wrapper(source: Path, work: Path, index: int) -> Path:
    """Make a private context wrapper around one current body-only source."""

    relative = source.relative_to(ROOT).as_posix()
    if relative not in BODY_ONLY_SOURCES:
        return source
    current = source.read_text(encoding="utf-8")
    context = (work / relative).with_suffix(".context.inc")
    prefix, suffix = context.read_text(encoding="utf-8").split("; TH04_NATIVE_BODY\n")
    current_public = re.search(r"(?m)^public\s+", current)
    if current_public is None:
        raise RuntimeError(f"body-only source has no public boundary: {relative}")

    # Keep current symbolic constants (notably PLAYFIELD_VRAM_W=48) while
    # recovering only the removed historical context declarations.
    current_prefix = current[:current_public.start()]
    for line in current_prefix.splitlines():
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*.*$", line)
        if not match:
            continue
        name = match.group(1)
        assignment = re.compile(
            rf"(?m)^\s*{re.escape(name)}\s*=\s*[^\r\n]*$"
        )
        prefix, count = assignment.subn(line, prefix, count=1)
        if count != 1:
            raise RuntimeError(
                f"diagnostic context lost current constant {name} in {relative}"
            )
    wrapper_text = prefix + current[current_public.start():] + suffix
    # TASM's .MODEL derives an implicit segment name from the basename; keep
    # the generated basename alphabetic so a numeric index is not parsed as a
    # label prefix (for example, ``006_YUUK_TEXT``).
    wrapper = work / "diagnostic_wrappers" / f"body{index:03d}_{source.name}"
    wrapper.parent.mkdir(parents=True, exist_ok=True)
    wrapper.write_text(wrapper_text, encoding="utf-8")
    return wrapper


def materialize_body_wrappers(sources: list[Path], work: Path) -> dict[str, Path]:
    wrappers: dict[str, Path] = {}
    for index, source in enumerate(sources):
        relative = source.relative_to(ROOT).as_posix()
        wrapper = body_wrapper(source, work, index)
        if wrapper != source:
            wrappers[relative] = wrapper
    return wrappers


def apply_exit_trace_overlay(work: Path) -> dict[str, object]:
    path = work / "src/main/core/gameexecl.cpp"
    original = path.read_text(encoding="utf-8")
    helper = r'''
static void native_exit_trace(unsigned marker, unsigned detail)
{
    const char hex[] = "0123456789ABCDEF";
    char name[] = "MX00.BIN";
    name[2] = hex[marker >> 4]; name[3] = hex[marker & 15];
    unsigned sample[4] = {marker, detail, _psp,
        *(unsigned far *)MK_FP(_psp - 1, 3)};
    int handle; unsigned written;
    if(!_dos_creat(name, 0, &handle)) {
        _dos_write(handle, sample, sizeof(sample), &written);
        _dos_close(handle);
    }
}
'''
    anchor = "int pascal GameExecl(const char *binary_fn)\n{\n"
    if original.count(anchor) != 1:
        raise RuntimeError("MAIN exit trace entry anchor is not unique")
    patched = original.replace('#include <process.h>', '#include <dos.h>\n#include <errno.h>\n#include <process.h>', 1)
    patched = patched.replace(anchor, helper + "\n" + anchor + "    native_exit_trace(0, 0);\n", 1)
    calls = ["game_state_save_score();", "bb_txt_free();", "cdg_free_all();",
             "bb_boss_free();", "dialog_free();", "bb_playchar_free();", "std_free();",
             "map_free();", "super_free();", "graph_hide();", "text_clear();",
             "gaiji_restore();", "game_exit();"]
    for marker, call in enumerate(calls, 1):
        statement = "    " + call + "\n"
        if patched.count(statement) != 1:
            raise RuntimeError(f"MAIN exit trace call anchor is not unique: {call}")
        patched = patched.replace(statement, statement + f"    native_exit_trace({marker}, 0);\n", 1)
    statement = "    return execl((char *)binary_fn, (char *)binary_fn, NULL);"
    if patched.count(statement) != 1:
        raise RuntimeError("MAIN execl trace anchor is not unique")
    patched = patched.replace(statement, "    native_exit_trace(0x1E, 0);\n"
                              "    int result = execl((char *)binary_fn, (char *)binary_fn, NULL);\n"
                              "    native_exit_trace(0x1F, errno);\n    return result;", 1)
    path.write_text(patched, encoding="utf-8")
    return {"path": path.relative_to(work).as_posix(),
            "original_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "overlay_sha256": sha256(path), "after_calls": calls}


def apply_state_trace_overlay(work: Path) -> dict[str, object]:
    """Record sparse gameplay states in copied source, without product changes."""
    path = work / "src/main/core/gameplay_loop.cpp"
    original = path.read_text(encoding="utf-8")
    anchor = "void near gameplay_loop(void)\n{\n"
    checkpoint = "        bomb_update_and_render();\n"
    if original.count(anchor) != 1 or original.count(checkpoint) != 1:
        raise RuntimeError("state trace overlay anchors are not unique")
    helper = r'''
// Private state recorder: 24 little-endian 16-bit words per PLAY.BIN record.
extern unsigned char miss_time;
static void native_play_state(void)
{
    static unsigned previous_bombs = 0xFFFF;
    static unsigned previous_misses = 0xFFFF;
    static unsigned history[64][24];
    static unsigned count;
    if(count == 64) return;
    if((stage_frame & 63) && resident->bombs_used == previous_bombs &&
       resident->miss_count == previous_misses) return;
    previous_bombs = resident->bombs_used;
    previous_misses = resident->miss_count;
    unsigned sample[24];
    sample[0] = 1;
    sample[1] = stage_frame;
    sample[2] = key_det;
    sample[3] = stage_id;
    sample[4] = player_pos.cur.x.v;
    sample[5] = player_pos.cur.y.v;
    sample[6] = shot_time;
    sample[7] = 0;
    for(int i = 0; i < SHOT_COUNT; i++) {
        if(shots[i].flag == SF_ALIVE) sample[7]++;
    }
    sample[8] = bombing;
    sample[9] = resident->rem_lives;
    sample[10] = resident->rem_bombs;
    sample[11] = resident->miss_count;
    sample[12] = resident->bombs_used;
    sample[13] = miss_time;
    sample[14] = resident->rank;
    sample[15] = resident->playchar_ascii;
    for(int d = 0; d < SCORE_DIGITS; d++) sample[16 + d] = score.digits[d];
    for(int column = 0; column < 24; column++) history[count][column] = sample[column];
    count++;
    int handle;
    unsigned written;
    if(_dos_creat("PLAY.BIN", 0, &handle)) return;
    _dos_write(handle, history, count * sizeof(history[0]), &written);
    _dos_close(handle);
}
'''
    patched = original.replace(
        '#include "src/shared/runtime/api.hpp"\n',
        '#include "src/main/player/shot.hpp"\n'
        '#include "src/main/stage/stage.hpp"\n'
        '#include "src/shared/runtime/api.hpp"\n', 1,
    ).replace(anchor, helper + "\n" + anchor, 1).replace(
        checkpoint, checkpoint + "        native_play_state();\n", 1,
    )
    path.write_text(patched, encoding="utf-8")
    # main.cpp precedes gameplay_loop.cpp in the fused DEMO_TEXT producer.
    # DOS declarations must precede the maintained subset in platform.h.
    entry = work / "src/main/core/main.cpp"
    entry_original = entry.read_text(encoding="utf-8")
    entry_anchor = '#include "platform.h"\n'
    if entry_original.count(entry_anchor) != 1:
        raise RuntimeError("state trace entry include anchor is not unique")
    entry.write_text(entry_original.replace(
        entry_anchor, '#include <dos.h>\n' + entry_anchor, 1), encoding="utf-8")
    originals = {path.relative_to(work).as_posix(): original,
                 entry.relative_to(work).as_posix(): entry_original}
    return {"paths": list(originals),
            "original_sha256": {p: hashlib.sha256(s.encode()).hexdigest()
                                for p, s in originals.items()},
            "overlay_sha256": {p: sha256(work / p) for p in originals},
            "record_words": 24,
            "max_records": 64, "record_mode": "bounded full-buffer snapshots",
            "interval_frames": 64,
            "exit_trace": apply_exit_trace_overlay(work),
            "fields": ["version", "stage_frame", "key_det", "stage_id",
                       "player_x_subpixel", "player_y_subpixel", "shot_time",
                       "active_shots", "bombing", "rem_lives", "rem_bombs",
                       "miss_count", "bombs_used", "miss_time", "rank",
                       "playchar_ascii", *[f"score_digit_{i}" for i in range(8)]]}


def apply_input_trace_overlay(
    work: Path,
    stage_override: int | None = None,
) -> dict[str, object]:
    """Inject private MAIN/EMS/first-frame state recorders into the cold tree.

    The recorders are deliberately overlays on copied translation units. They
    never change the maintained source or the exact shared input_s module;
    the receipt records both source hashes so this diagnostic cannot be
    mistaken for a product build.
    """

    path = work / "src/main/core/gameplay_loop.cpp"
    original = path.read_text(encoding="utf-8")
    function_anchor = "void near gameplay_loop(void)\n{\n"
    sense_anchor = "        input_sense();\n"
    if original.count(function_anchor) != 1 or original.count(sense_anchor) != 1:
        raise RuntimeError("input trace overlay anchors are not unique")
    trace_function = r'''

// Private diagnostic overlay; this block is never part of maintained source.
static void native_input_trace_once(void)
{
    const char trace_fn[] = "INPUT.BIN";
    unsigned char sample[8];
    sample[0] = static_cast<unsigned char>(key_det & 0xFF);
    sample[1] = static_cast<unsigned char>(key_det >> 8);
    sample[2] = shiftkey ? 1 : 0;
    sample[3] = static_cast<unsigned char>(js_bexist & 0xFF);
    sample[4] = static_cast<unsigned char>(js_bexist >> 8);
    sample[5] = static_cast<unsigned char>(js_stat[0] & 0xFF);
    sample[6] = static_cast<unsigned char>(js_stat[0] >> 8);
    sample[7] = static_cast<unsigned char>(stage_frame & 0xFF);
    int handle;
    unsigned done;
    if(_dos_creat(trace_fn, 0, &handle) == 0) {
        _dos_write(handle, sample, sizeof(sample), &done);
        _dos_close(handle);
    }
}
static void native_game_trace(unsigned char marker)
{
    static const char hex[] = "0123456789ABCDEF";
    char trace_fn[] = "GAM00.BIN";
    int handle;
    unsigned done;
    trace_fn[3] = hex[(marker >> 4) & 0x0F];
    trace_fn[4] = hex[marker & 0x0F];
    if(_dos_creat(trace_fn, 0, &handle) == 0) {
        _dos_write(handle, &marker, 1, &done);
        _dos_close(handle);
    }
}
'''
    patched = original.replace(
        '#include "src/shared/runtime/api.hpp"\n',
        '#include <dos.h>\n#include "src/shared/runtime/api.hpp"\n',
        1,
    )
    patched = patched.replace(
        function_anchor,
        trace_function + "\n" + function_anchor + "    native_game_trace(0x01);\n",
        1,
    )
    patched = patched.replace(
        "    frame_delay(1);\n",
        "    frame_delay(1);\n    native_game_trace(0x02);\n",
        1,
    )
    patched = patched.replace(
        "    input_reset_sense();\n",
        "    input_reset_sense();\n    native_game_trace(0x03);\n",
        1,
    )
    patched = patched.replace(
        sense_anchor,
        sense_anchor + "        native_game_trace(0x04);\n"
        "        if(stage_frame == 0) {\n"
        "            native_input_trace_once();\n"
        "        }\n",
        1,
    )
    patched = patched.replace(
        "        stage_vm();\n",
        "        native_game_trace(0x05);\n"
        "        stage_vm();\n"
        "        native_game_trace(0x06);\n",
        1,
    )
    gameplay_markers = (
        (
            "        if(bombing == false) {\n",
            "        native_game_trace(0x10);\n"
            "        if(bombing == false) {\n",
        ),
        (
            "            bg_render_not_bombing();\n",
            "            bg_render_not_bombing();\n"
            "            native_game_trace(0x11);\n",
        ),
        (
            "            bg_render_bombing();\n",
            "            bg_render_bombing();\n"
            "            native_game_trace(0x11);\n",
        ),
        (
            "        pointnums_update();\n",
            "        native_game_trace(0x12);\n"
            "        pointnums_update();\n",
        ),
        (
            "        gather_update();\n",
            "        gather_update();\n"
            "        native_game_trace(0x13);\n",
        ),
        (
            "        stage_render();\n",
            "        native_game_trace(0x20);\n"
            "        stage_render();\n"
            "        native_game_trace(0x21);\n",
        ),
        (
            "        bomb_update_and_render();\n",
            "        native_game_trace(0x23);\n"
            "        bomb_update_and_render();\n"
            "        native_game_trace(0x24);\n",
        ),
        (
            "        boss_fg_render();\n",
            "        native_game_trace(0x25);\n"
            "        boss_fg_render();\n"
            "        native_game_trace(0x26);\n",
        ),
        (
            "        midboss_render();\n",
            "        native_game_trace(0x27);\n"
            "        midboss_render();\n"
            "        native_game_trace(0x28);\n",
        ),
        (
            "        enemies_render();\n",
            "        native_game_trace(0x29);\n"
            "        enemies_render();\n"
            "        native_game_trace(0x2A);\n",
        ),
        (
            "        shots_render();\n",
            "        native_game_trace(0x2B);\n"
            "        shots_render();\n"
            "        native_game_trace(0x2C);\n",
        ),
        (
            "        player_render();\n",
            "        native_game_trace(0x2D);\n"
            "        player_render();\n"
            "        native_game_trace(0x2E);\n",
        ),
        (
            "        grcg_setmode_rmw();\n",
            "        native_game_trace(0x30);\n"
            "        grcg_setmode_rmw();\n",
        ),
        (
            "        grcg_off();\n",
            "        grcg_off();\n"
            "        native_game_trace(0x31);\n",
        ),
        (
            "        overlay1();\n",
            "        native_game_trace(0x40);\n"
            "        overlay1();\n",
        ),
        (
            "        overlay2();\n",
            "        overlay2();\n"
            "        native_game_trace(0x41);\n",
        ),
        (
            "        playfield_shake_update_and_render();\n",
            "        native_game_trace(0x42);\n"
            "        playfield_shake_update_and_render();\n"
            "        native_game_trace(0x43);\n",
        ),
        (
            "        graph_accesspage(page_front);\n",
            "        native_game_trace(0x50);\n"
            "        graph_accesspage(page_front);\n",
        ),
    )
    for before, after in gameplay_markers:
        if patched.count(before) != 1:
            raise RuntimeError(f"gameplay trace overlay anchor is not unique: {before!r}")
        patched = patched.replace(before, after, 1)
    patched = patched.replace(
        "        graph_showpage(page_back);\n",
        "        native_game_trace(0x07);\n"
        "        graph_showpage(page_back);\n"
        "        native_game_trace(0x08);\n",
        1,
    )
    patched = patched.replace(
        "        score_update_and_render();\n",
        "        score_update_and_render();\n"
        "        native_game_trace(0x09);\n",
        1,
    )
    path.write_text(patched, encoding="utf-8")

    player_path = work / "src/main/player/render.cpp"
    player_original = player_path.read_text(encoding="utf-8")
    player_anchor = "void pascal near player_render(void)\n{\n"
    if player_original.count(player_anchor) != 1:
        raise RuntimeError("player trace overlay anchor is not unique")
    player_trace_function = r'''

// Private diagnostic overlay; this block is never part of maintained source.
static void native_player_trace(unsigned char marker)
{
    static const char hex[] = "0123456789ABCDEF";
    char trace_fn[] = "PLY00.BIN";
    int handle;
    unsigned done;
    unsigned char sample[2];
    trace_fn[3] = hex[(marker >> 4) & 0x0F];
    trace_fn[4] = hex[marker & 0x0F];
    sample[0] = marker;
    sample[1] = miss_time;
    if(_dos_creat(trace_fn, 0, &handle) == 0) {
        _dos_write(handle, sample, sizeof(sample), &done);
        _dos_close(handle);
    }
}
'''
    player_patched = player_original.replace(
        '#include "x86real.h"\n',
        '#include <dos.h>\n#include "x86real.h"\n',
        1,
    )
    player_patched = player_patched.replace(
        player_anchor,
        player_trace_function + "\n" + player_anchor + "    native_player_trace(0x01);\n",
        1,
    )
    player_replacements = (
        (
            "            super_roll_put(left, screen_y, patnum);\n",
            "            native_player_trace(0x02);\n"
            "            super_roll_put(left, screen_y, patnum);\n"
            "            native_player_trace(0x03);\n",
        ),
        (
            "        grcg_setmode_rmw();\n",
            "        native_player_trace(0x04);\n"
            "        grcg_setmode_rmw();\n"
            "        native_player_trace(0x05);\n",
        ),
        (
            "        z_super_roll_put_tiny_16x16_raw(player_option_patnum);\n",
            "        native_player_trace(0x06);\n"
            "        z_super_roll_put_tiny_16x16_raw(player_option_patnum);\n"
            "        native_player_trace(0x07);\n",
        ),
        (
            "        super_roll_put(left, screen_y, 3);\n",
            "        native_player_trace(0x10);\n"
            "        super_roll_put(left, screen_y, 3);\n"
            "        native_player_trace(0x11);\n",
        ),
    )
    for before, after in player_replacements:
        if player_patched.count(before) == 0:
            raise RuntimeError(f"player trace overlay anchor is missing: {before!r}")
        player_patched = player_patched.replace(before, after, 1)
    player_path.write_text(player_patched, encoding="utf-8")

    main_path = work / "src/main/core/main.cpp"
    main_original = main_path.read_text(encoding="utf-8")
    main_anchor = "void main(void)\n{\n"
    if main_original.count(main_anchor) != 1:
        raise RuntimeError("MAIN trace overlay anchor is not unique")
    main_trace_function = r'''

// Private diagnostic overlay; this block is never part of maintained source.
static void native_main_trace(unsigned char marker)
{
    const char trace_fn[] = "MAIN.BIN";
    int handle;
    unsigned done;
    if(_dos_creat(trace_fn, 0, &handle) == 0) {
        _dos_write(handle, &marker, 1, &done);
        _dos_close(handle);
    }
}
'''
    main_patched = main_original.replace(
        '#include "src/shared/config/resident.hpp"\n',
        '#include "src/shared/config/resident.hpp"\n'
        '#include <dos.h>\n'
        '#include "src/shared/runtime/api.hpp"\n',
        1,
    )
    main_patched = main_patched.replace(
        main_anchor,
        main_trace_function + "\n" + main_anchor + "    native_main_trace(0);\n",
        1,
    )
    stage_override_source = ""
    if stage_override is not None:
        stage_override_source = (
            f"        resident->stage = {stage_override};\n"
            f"        resident->stage_ascii = ('0' + {stage_override});\n"
            "        resident->demo_num = 0;\n"
        )
    main_replacements = (
        ("    if(!cfg_load_resident_ptr()) {\n", "    if(!cfg_load_resident_ptr()) {\n"),
        ("        return;\n", "        native_main_trace(0xF0);\n        return;\n"),
        ("    mem_assign_paras = (320000 >> 4);\n", "    native_main_trace(1);\n    mem_assign_paras = (320000 >> 4);\n"),
        ("    game_init_main(main_pf_fn);\n", "    game_init_main(main_pf_fn);\n    native_main_trace(2);\n"),
        ("    ems_allocate_and_preload_eyecatch();\n", "    ems_allocate_and_preload_eyecatch();\n    native_main_trace(3);\n"),
        ("    text_clear();\n", "    text_clear();\n    native_main_trace(0x31);\n"),
        ("    gaiji_backup();\n", "    gaiji_backup();\n    native_main_trace(0x32);\n"),
        (
            "    gaiji_entry_bfnt(gaiji_fn);\n",
            "    native_main_trace(0x33);\n"
            "    gaiji_entry_bfnt(gaiji_fn);\n"
            "    native_main_trace(4);\n",
        ),
        (
            "    snd_determine_modes(resident->bgm_mode, resident->se_mode);\n",
            "    native_main_trace(0x41);\n"
            "    snd_determine_modes(resident->bgm_mode, resident->se_mode);\n"
            "    native_main_trace(0x42);\n",
        ),
        (
            "    snd_load(se_fn, SND_LOAD_SE);\n",
            "    native_main_trace(0x43);\n"
            "    snd_load(se_fn, SND_LOAD_SE);\n"
            "    native_main_trace(5);\n",
        ),
        ("    for(;;) {\n", "    native_main_trace(6);\n    for(;;) {\n"),
        (
            "        stage_session_init();\n",
            stage_override_source
            + "        stage_session_init();\n"
            "        native_main_trace(7);\n",
        ),
        ("        gameplay_loop();\n", "        native_main_trace(8);\n        gameplay_loop();\n        native_main_trace(9);\n"),
        ("    GameExecl(op_fn);\n", "    native_main_trace(0xA0);\n    GameExecl(op_fn);\n"),
    )
    for before, after in main_replacements:
        if main_patched.count(before) != 1:
            raise RuntimeError(f"MAIN trace overlay anchor is not unique: {before!r}")
        main_patched = main_patched.replace(before, after, 1)
    main_path.write_text(main_patched, encoding="utf-8")
    ems_path = work / "src/main/ems.cpp"
    ems_original = ems_path.read_text(encoding="utf-8")
    ems_anchor = "void near ems_allocate_and_preload_eyecatch(void)\n{\n"
    if ems_original.count(ems_anchor) != 1:
        raise RuntimeError("EMS trace overlay anchor is not unique")
    ems_trace_function = r'''

// Private diagnostic overlay; this block is never part of maintained source.
static void native_ems_trace(unsigned char marker)
{
    const char trace_fn[] = "EMS.BIN";
    int handle;
    unsigned done;
    if(_dos_creat(trace_fn, 0, &handle) == 0) {
        _dos_write(handle, &marker, 1, &done);
        _dos_close(handle);
    }
}
'''
    ems_patched = ems_original.replace(
        '#include "src/shared/hardware/graphics.hpp"\n',
        '#include <dos.h>\n#include "src/shared/hardware/graphics.hpp"\n',
        1,
    )
    ems_patched = ems_patched.replace(
        ems_anchor,
        ems_trace_function + "\n" + ems_anchor + "\tnative_ems_trace(0x10);\n",
        1,
    )
    ems_replacements = (
        ("\tEms = nullptr;\n", "\tEms = nullptr;\n\tnative_ems_trace(0x11);\n"),
        ("\tif(!ems_exist() || (ems_space() < EMSSIZE)) {\n\t\treturn;\n\t}\n",
         "\tnative_ems_trace(0x12);\n\tif(!ems_exist()) {\n\t\tnative_ems_trace(0x13);\n\t\treturn;\n\t}\n\tnative_ems_trace(0x14);\n\tif(ems_space() < EMSSIZE) {\n\t\tnative_ems_trace(0x15);\n\t\treturn;\n\t}\n\tnative_ems_trace(0x16);\n"),
        ("\tEms = ems_allocate(EMSSIZE);\n", "\tnative_ems_trace(0x17);\n\tEms = ems_allocate(EMSSIZE);\n\tnative_ems_trace(0x18);\n"),
        ("\tif(Ems) {\n\t\tems_setname(Ems, EMS_NAME);\n\t\tcdg_load_single_noalpha(CDG_EYECATCH, eyename, 0);\n", "\tnative_ems_trace(0x19);\n\tif(Ems) {\n\t\tems_setname(Ems, EMS_NAME);\n\t\tnative_ems_trace(0x1A);\n\t\tcdg_load_single_noalpha(CDG_EYECATCH, eyename, 0);\n\t\tnative_ems_trace(0x1B);\n"),
        ("\t\tems_write_cdg_color_planes(Ems, EMS_EYECATCH_OFFSET, CDG_EYECATCH);\n", "\t\tems_write_cdg_color_planes(Ems, EMS_EYECATCH_OFFSET, CDG_EYECATCH);\n\t\tnative_ems_trace(0x1C);\n"),
        ("\t\tcdg_free(CDG_EYECATCH);\n", "\t\tcdg_free(CDG_EYECATCH);\n\t\tnative_ems_trace(0x1D);\n"),
    )
    for before, after in ems_replacements:
        if ems_patched.count(before) != 1:
            raise RuntimeError(f"EMS trace overlay anchor is not unique: {before!r}")
        ems_patched = ems_patched.replace(before, after, 1)
    ems_path.write_text(ems_patched, encoding="utf-8")
    stage_path = work / "src/main/stage/session_init.cpp"
    stage_original = stage_path.read_text(encoding="utf-8")
    stage_anchor = "void near stage_session_init(void)\n{\n"
    if stage_original.count(stage_anchor) != 1:
        raise RuntimeError("stage trace overlay anchor is not unique")
    stage_trace_function = r'''

// Private diagnostic overlay; this block is never part of maintained source.
static void native_stage_trace(unsigned char marker)
{
    static const char hex[] = "0123456789ABCDEF";
    char trace_fn[] = "STG00.BIN";
    int handle;
    unsigned done;
    trace_fn[3] = hex[(marker >> 4) & 0x0F];
    trace_fn[4] = hex[marker & 0x0F];
    if(_dos_creat(trace_fn, 0, &handle) == 0) {
        _dos_write(handle, &marker, 1, &done);
        _dos_close(handle);
    }
}
'''
    stage_patched = stage_original.replace(
        "#endif\n\n// TH04 stage/demo session setup",
        "#endif\n#include <dos.h>\n\n// TH04 stage/demo session setup",
        1,
    )
    stage_patched = stage_patched.replace(
        stage_anchor,
        stage_trace_function + "\n" + stage_anchor + "    native_stage_trace(0x60);\n",
        1,
    )
    sub_anchor = "    sub_12024();\n"
    if stage_patched.count(sub_anchor) != 2:
        raise RuntimeError("stage sub_12024 trace anchors are not unique")
    stage_patched = stage_patched.replace(
        sub_anchor,
        "    native_stage_trace(0x63);\n"
        "    sub_12024();\n"
        "    native_stage_trace(0x64);\n",
        1,
    )
    stage_replacements = (
        (
            "    if(load_playchar_resources != 0) {\n",
            "    if(load_playchar_resources != 0) {\n"
            "        native_stage_trace(0x70);\n",
        ),
        (
            "        super_entry_bfnt(miko16_bft);\n",
            "        super_entry_bfnt(miko16_bft);\n"
            "        native_stage_trace(0x71);\n",
        ),
        (
            "        for(int i = 20; i < 120; i++) {\n"
            "            super_convert_tiny(i);\n"
            "        }\n",
            "        native_stage_trace(0x72);\n"
            "        for(int i = 20; i < 120; i++) {\n"
            "            if(super_convert_tiny(i) != 0) {\n"
            "                native_stage_trace(0x81);\n"
            "            }\n"
            "        }\n"
            "        native_stage_trace(0x73);\n",
        ),
        (
            "    native_stage_trace(0x64);\n    graph_accesspage(0);\n",
            "    native_stage_trace(0x64);\n"
            "    graph_accesspage(0);\n"
            "    native_stage_trace(0x65);\n",
        ),
        (
            "    graph_accesspage(0);\n"
            "    native_stage_trace(0x65);\n"
            "    graph_showpage(0);\n",
            "    graph_accesspage(0);\n"
            "    native_stage_trace(0x65);\n"
            "    graph_showpage(0);\n"
            "    native_stage_trace(0x66);\n",
        ),
        (
            "    graph_showpage(0);\n"
            "    native_stage_trace(0x66);\n"
            "    palette_entry_rgb(eye_rgb);\n",
            "    graph_showpage(0);\n"
            "    native_stage_trace(0x66);\n"
            "    palette_entry_rgb(eye_rgb);\n"
            "    native_stage_trace(0x67);\n",
        ),
        (
            "    PaletteTone = 0;\n    palette_show();\n",
            "    PaletteTone = 0;\n"
            "    palette_show();\n"
            "    native_stage_trace(0x68);\n",
        ),
        (
            "    native_stage_trace(0x68);\n"
            "    sub_12024();\n"
            "    overlay_wipe();\n",
            "    native_stage_trace(0x68);\n"
            "    sub_12024();\n"
            "    overlay_wipe();\n"
            "    native_stage_trace(0x69);\n",
        ),
        (
            "        gameplay_session_init();\n",
            "        native_stage_trace(0x61);\n"
            "        gameplay_session_init();\n"
            "        native_stage_trace(0x62);\n",
        ),
    )
    for before, after in stage_replacements:
        if stage_patched.count(before) != 1:
            raise RuntimeError(f"stage trace overlay anchor is not unique: {before!r}")
        stage_patched = stage_patched.replace(before, after, 1)
    stage_path.write_text(stage_patched, encoding="utf-8")
    return {
        "paths": [
            "src/main/core/gameplay_loop.cpp",
            "src/main/core/main.cpp",
            "src/main/ems.cpp",
            "src/main/stage/session_init.cpp",
            "src/main/player/render.cpp",
        ],
        "original_sha256": {
            "src/main/core/gameplay_loop.cpp": sha256_bytes(original.encode("utf-8")),
            "src/main/core/main.cpp": sha256_bytes(main_original.encode("utf-8")),
            "src/main/ems.cpp": sha256_bytes(ems_original.encode("utf-8")),
            "src/main/stage/session_init.cpp": sha256_bytes(stage_original.encode("utf-8")),
            "src/main/player/render.cpp": sha256_bytes(player_original.encode("utf-8")),
        },
        "overlay_sha256": {
            "src/main/core/gameplay_loop.cpp": sha256(path),
            "src/main/core/main.cpp": sha256(main_path),
            "src/main/ems.cpp": sha256(ems_path),
            "src/main/stage/session_init.cpp": sha256(stage_path),
            "src/main/player/render.cpp": sha256(player_path),
        },
        "stage_override": stage_override,
    }


def apply_graphics_trace_overlay(work: Path) -> dict[str, object]:
    """Record loaded MPN bytes and the cache/initial rendered VRAM planes."""
    helper = r'''
#include <dos.h>
static void native_dump_vram(const char *filename)
{
    int handle;
    unsigned written;
    if(_dos_creat(filename, 0, &handle)) return;
    _dos_write(handle, (void far *)MK_FP(0xA800, 0), 32000, &written);
    _dos_write(handle, (void far *)MK_FP(0xB000, 0), 32000, &written);
    _dos_write(handle, (void far *)MK_FP(0xB800, 0), 32000, &written);
    _dos_write(handle, (void far *)MK_FP(0xE000, 0), 32000, &written);
    _dos_close(handle);
}
'''
    replacements = {
        "src/main/formats/mpn_load.cpp": (
            "\tfile_read(mpn.images, mpn_size);",
            r'''
    int native_dump_handle;
    unsigned native_dump_written;
    if(!_dos_creat("MPNDUMP.BIN", 0, &native_dump_handle)) {
        _dos_write(native_dump_handle, &mpn, sizeof(mpn), &native_dump_written);
        _dos_write(native_dump_handle, mpn.images, 128, &native_dump_written);
        _dos_write(native_dump_handle, &Palettes, sizeof(Palettes), &native_dump_written);
        _dos_close(native_dump_handle);
    }
''', "#include <dos.h>\n"),
        "src/main/formats/mpn_upload.cpp": (
            "\tmpn_free(0);", '\n\tnative_dump_vram("VRAMC.BIN");\n', helper),
        "src/main/stage/session_init.cpp": (
            "    graph_showpage(0);\n    tiles_render_all();",
            '\n    native_dump_vram("VRAMT.BIN");\n', helper),
    }
    records = {}
    for relative, (anchor, insertion, prefix) in replacements.items():
        path = work / relative
        original = path.read_text(encoding="utf-8")
        if original.count(anchor) != 1:
            raise RuntimeError(f"graphics trace anchor is not unique: {relative}")
        position = original.index(anchor)
        if relative.endswith("mpn_upload.cpp"):
            patched = original[:position] + insertion + original[position:]
        else:
            position += len(anchor)
            patched = original[:position] + insertion + original[position:]
        # TC4J's segment option pragmas must precede any header declarations.
        include = re.search(r"(?m)^#include\s", patched)
        if include is None:
            raise RuntimeError(f"graphics trace source has no include boundary: {relative}")
        patched = patched[:include.start()] + prefix + patched[include.start():]
        path.write_text(patched, encoding="utf-8")
        records[relative] = {"original_sha256": sha256_bytes(original.encode()),
                             "overlay_sha256": sha256(path)}
    return records


def index_value(data: bytes, cursor: int) -> tuple[int, int]:
    first = data[cursor]
    if first & 0x80:
        return ((first & 0x7F) << 8) | data[cursor + 1], cursor + 2
    return first, cursor + 1


def code_group(obj: Path) -> tuple[str, bool, tuple[str, ...]]:
    """Return primary code group, nonzero-code flag, and all code groups."""
    names = [""]
    segments: list[tuple[str, str, int]] = []
    groups: list[tuple[str, list[int]]] = []
    for record in parse_omf(obj.read_bytes()):
        data = record.data
        if record.record_type == 0x96:  # LNAMES
            cursor = 0
            while cursor < len(data):
                size = data[cursor]
                cursor += 1
                names.append(data[cursor:cursor + size].decode("ascii", "replace"))
                cursor += size
        elif record.record_type in (0x98, 0x99):  # SEGDEF16/32
            cursor = 1
            acbp = data[0]
            if ((acbp >> 5) & 0x7) == 0:
                cursor += 3
            length = int.from_bytes(data[cursor:cursor + 2], "little")
            cursor += 2
            segment_name, cursor = index_value(data, cursor)
            class_name, cursor = index_value(data, cursor)
            _, cursor = index_value(data, cursor)
            segments.append((names[segment_name], names[class_name], length))
        elif record.record_type == 0x9A:  # GRPDEF
            cursor = 0
            group_name, cursor = index_value(data, cursor)
            members: list[int] = []
            while cursor < len(data):
                if data[cursor] != 0xFF:
                    raise ValueError(f"malformed GRPDEF in {obj}")
                cursor += 1
                member, cursor = index_value(data, cursor)
                members.append(member)
            groups.append((names[group_name], members))

    group_by_segment: dict[int, str] = {}
    for group_name, members in groups:
        for member in members:
            group_by_segment[member] = group_name
    code = [
        (name, length, group_by_segment.get(index + 1))
        for index, (name, cls, length) in enumerate(segments)
        if cls.upper() == "CODE"
    ]
    all_groups = tuple(sorted({group for _, _, group in code if group}))
    # Zero-length code SEGDEFs still establish the producer's group.  Prefer
    # MAIN_03 when a TU also carries a zero MAIN_01 contribution.
    if "MAIN_03" in all_groups:
        primary = "MAIN_03"
    elif all_groups:
        primary = all_groups[0]
    else:
        primary = "none"
    return primary, any(length for _, length, _ in code), all_groups


def cpp_roots() -> tuple[list[Path], set[str]]:
    sources = sorted(
        source for root in SOURCE_ROOTS for source in root.rglob("*")
        if source.is_file() and source.suffix.lower() in SOURCE_SUFFIXES
    )
    included: set[str] = set()
    include_pattern = re.compile(r"#include\s+[\"<](src/[^\">]+\.cpp)[\">]")
    for source in sources:
        included.update(include_pattern.findall(source.read_text(encoding="utf-8", errors="replace")))
    roots = [source for source in sources
             if source.relative_to(ROOT).as_posix() not in included
             and source.relative_to(ROOT).as_posix() not in SOURCE_EXCLUSIONS]
    return roots, included


def asm_sources() -> list[Path]:
    return sorted(
        source for root in SOURCE_ROOTS for source in root.rglob("*.asm")
        if source.is_file()
        and source.relative_to(ROOT).as_posix() not in ASM_EXCLUSIONS
    )


def manifest_aliases() -> dict[str, str]:
    data = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for reference in data["reference_sources"]:
        if reference in data["direct_owners"]:
            local = data["direct_owners"][reference]
        elif reference in data["fused_owners"]:
            local = data["fused_owners"][reference]["local"]
        else:
            continue
        if local.endswith((".c", ".cpp")):
            # First historical route owns the physical producer's basename.
            result.setdefault(local, data["compile_aliases"].get(reference, reference))
    return result


EXTRA_ALIASES = {
    "src/main/core/demo_prefix.cpp": "th04/demo_main.cpp",
    "src/main/boss/boss_bg_main01.cpp": "th04/boss_bg.cpp",
    "src/main/boss/elly_update.cpp": "th04/elly.cpp",
    "src/main/boss/kurumi_update.cpp": "th04/kurumi.cpp",
    "src/main/boss/marisa4_main033.cpp": "th04/marisa4.cpp",
    "src/main/boss/mugetsu_main033.cpp": "th04/mugetsu.cpp",
    "src/main/boss/yuuka5.cpp": "th04/yuuka5.cpp",
    "src/main/boss/yuuka6_main034.cpp": "th04/yuuka6.cpp",
}


def compile_cpp(source: Path, alias: str, index: int, work: Path,
                output: Path, env: dict[str, str]) -> dict[str, object]:
    relative = source.relative_to(ROOT).as_posix()
    copied = work / source.relative_to(ROOT)
    compile_source = work / alias
    compile_source.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(copied, compile_source)
    if sha256(copied) != sha256(compile_source):
        raise RuntimeError(f"compile alias changed source bytes: {relative}")
    obj_dir = work / "obj/cpp" / f"{index:03d}"
    obj_dir.mkdir(parents=True)
    alias_relative = compile_source.relative_to(work).as_posix()
    command = ["wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS,
               f"-nobj/cpp/{index:03d}/", alias_relative]
    log = output / f"compile-{index:03d}.log"
    result = run(command, work, env, log)
    objects = sorted(obj_dir.glob("*.obj"))
    omf = describe_omf(objects[0].read_bytes()) if len(objects) == 1 else None
    primary, has_code, groups = code_group(objects[0]) if omf else ("none", False, ())
    return {
        "index": index,
        "source": relative,
        "source_sha256": sha256(copied),
        "compile_alias": alias,
        "compile_alias_sha256": sha256(compile_source),
        "compile_exit": result.returncode,
        "log": log.relative_to(output).as_posix(),
        "objects": [item.relative_to(work).as_posix() for item in objects],
        "object_sha256": sha256(objects[0]) if len(objects) == 1 else None,
        "omf_valid": bool(omf and omf["valid"]),
        "translator_comments": omf["translator_comments"] if omf else [],
        "primary_code_group": primary,
        "has_nonzero_code": has_code,
        "code_groups": list(groups),
    }


def assemble_asm(source: Path, index: int, work: Path, output: Path,
                 env: dict[str, str], subdir: str, log_prefix: str,
                 logical_source: Path | None = None) -> dict[str, object]:
    source = source if source.is_absolute() else ROOT / source
    logical_source = logical_source or source
    try:
        relative = source.relative_to(work).as_posix()
    except ValueError:
        relative = source.relative_to(ROOT).as_posix()
    obj = work / "obj" / subdir / f"{index:03d}.obj"
    obj.parent.mkdir(parents=True, exist_ok=True)
    try:
        logical_relative = logical_source.relative_to(ROOT).as_posix()
    except ValueError:
        logical_relative = logical_source.relative_to(work).as_posix()
    staged_source = work / relative
    if logical_relative in ASM_CACHE:
        cached, previous_obj = ASM_CACHE[logical_relative]
        if (cached["assembly_source"] == relative
                and cached["assembly_source_sha256"] == sha256(staged_source)
                and cached["source_sha256"] == sha256(logical_source)):
            shutil.copy2(previous_obj, obj)
            record = dict(cached)
            record.update(index=index, object=obj.relative_to(work).as_posix(),
                          reused_from=str(previous_obj), log=None)
            return record
    source_win = relative.replace("/", "\\")
    object_win = obj.relative_to(work).as_posix().replace("/", "\\")
    command = [
        "wine", "cmd", "/d", "/c",
        r"set PATH=C:\\TASM50\\BIN;C:\\TC4\\BIN;%PATH%&&"
        + f"tasm32 /m /mx /kh32768 /t /dGAME=4 /dTH04_LARGE_PRODUCT=1 "
        f"{source_win} {object_win}",
    ]
    log = output / f"{log_prefix}-{index:03d}.log"
    result = run(command, work, env, log)
    omf = describe_omf(obj.read_bytes()) if obj.is_file() else None
    try:
        logical_relative = logical_source.relative_to(ROOT).as_posix()
    except ValueError:
        logical_relative = logical_source.relative_to(work).as_posix()
    result = {
        "index": index,
        "source": logical_relative,
        "assembly_source": relative,
        "source_sha256": sha256(logical_source),
        "assembly_source_sha256": sha256(source),
        "object": obj.relative_to(work).as_posix() if obj.is_file() else None,
        "object_sha256": sha256(obj) if obj.is_file() else None,
        "assemble_exit": result.returncode,
        "omf_valid": bool(omf and omf["valid"]),
        "translator_comments": omf["translator_comments"] if omf else [],
        "log": log.relative_to(output).as_posix(),
    }
    return result


def assemble_state(source: Path, index: int, work: Path, output: Path,
                   env: dict[str, str]) -> dict[str, object]:
    return assemble_asm(source, index, work, output, env, "state", "assemble-state")


def link(work: Path, output: Path, objects: list[Path], env: dict[str, str],
         without_support: bool) -> dict[str, object]:
    bin_dir = work / "bin"
    bin_dir.mkdir(exist_ok=True)
    if not without_support:
        shutil.copy2(SUPPORT_LIB, bin_dir / "masters.lib")
    relative_objects = [str(item.relative_to(work)).replace("/", "\\") for item in objects]
    libraries = "emu.lib mathl.lib cl.lib" if without_support else \
        "bin\\masters.lib emu.lib mathl.lib cl.lib"
    response = work / "obj/main-native.@l"
    response.write_text(
        "-c -s -E c0l.obj " + " ".join(relative_objects)
        + ", bin\\main-native.exe, obj\\main-native.map, " + libraries + "\n",
        encoding="ascii",
    )
    command = ["wine", str(RUNNER), "-e", "-x", "tlink", "@obj\\main-native.@l"]
    log = output / "link.log"
    result = run(command, work, env, log)
    text = result.stdout + result.stderr
    errors = re.findall(r"^(?:Error|Fatal): (.+)$", text, re.MULTILINE)
    warnings = re.findall(r"^Warning: (.+)$", text, re.MULTILINE)
    undefined = re.findall(r"^Error: Undefined symbol (.+?) in module (.+)$", text, re.MULTILINE)
    duplicate = re.findall(r"^Error: (.+? defined in module .+? is duplicated in module .+)$",
                           text, re.MULTILINE)
    fixups = [item for item in errors if item.startswith("Fixup overflow")]
    groups = [item for item in errors if item.startswith("Group ") and "exceeds 64K" in item]
    exe = work / "bin/main-native.exe"
    map_file = work / "obj/main-native.map"
    mz: dict[str, object] | None = None
    if exe.is_file():
        try:
            parsed = parse_mz(exe.read_bytes())
            mz = {
                "sha256": sha256(exe),
                "size": exe.stat().st_size,
                "header_paragraphs": parsed.header.header_paragraphs,
                "relocations": len(parsed.relocations),
            }
        except Exception as exc:  # pragma: no cover - diagnostic receipt path
            mz = {"error": str(exc), "sha256": sha256(exe), "size": exe.stat().st_size}
    return {
        "command": command,
        "response": response.relative_to(work).as_posix(),
        "response_sha256": sha256(response),
        "log": log.relative_to(output).as_posix(),
        "exit": result.returncode,
        "errors": errors,
        "warnings": warnings,
        "undefined_symbols": [{"symbol": symbol, "module": module}
                              for symbol, module in undefined],
        "duplicate_errors": duplicate,
        "fixup_overflows": fixups,
        "group_overflows": groups,
        "map": map_file.relative_to(work).as_posix() if map_file.is_file() else None,
        "map_sha256": sha256(map_file) if map_file.is_file() else None,
        "mz": mz,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--without-support", action="store_true",
                        help="link TH04 objects with Borland system libraries only")
    parser.add_argument("--check-manifest", action="store_true",
                        help="audit the frozen MAIN routing manifest without building")
    parser.add_argument("--require-link", action="store_true",
                        help="return failure unless TLINK exits zero with no errors")
    parser.add_argument("--reuse-cpp-from", type=Path,
                        help="reuse C++ objects when the staged C/C++ include tree is unchanged")
    parser.add_argument("--reuse-asm-from", type=Path,
                        help="reuse ASM objects when source and assembly includes are unchanged")
    parser.add_argument("--graphics-trace", action="store_true",
                        help="private MPN/cache/initial-VRAM file checkpoints")
    parser.add_argument("--state-trace", action="store_true",
                        help="private sparse input/player/shot/bomb/score records")
    parser.add_argument(
        "--input-trace",
        action="store_true",
        help="inject a private first-frame INPUT.BIN state recorder",
    )
    parser.add_argument(
        "--force-stage",
        type=int,
        choices=range(7),
        help="private diagnostic overlay: force resident stage 0..6",
    )
    args = parser.parse_args()
    if args.check_manifest:
        if (args.output_dir or args.without_support or args.require_link
                or args.input_trace or args.force_stage is not None
                or args.graphics_trace or args.state_trace
                or args.reuse_cpp_from or args.reuse_asm_from):
            parser.error("--check-manifest cannot be combined with build options")
        result = audit()
        print(json.dumps({"artifact": "th04-main", "manifest": result}, sort_keys=True))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for a link diagnostic")
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        parser.error("output must be a new private directory")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    if sha256(RUNNER) != RUNNER_SHA256:
        raise RuntimeError("pinned TC4J runner identity drift")
    if not args.without_support and sha256(SUPPORT_LIB) != SUPPORT_SHA256:
        raise RuntimeError("pinned masters.lib identity drift")

    roots, included = cpp_roots()
    assembly_sources = asm_sources()
    state_source_names = {source.as_posix() for source in STATE_SOURCES}
    aliases = manifest_aliases()
    output.mkdir(parents=True)
    work = output / "source"
    shutil.copytree(ROOT / "src", work / "src")
    input_trace = (
        apply_input_trace_overlay(work, args.force_stage)
        if args.input_trace or args.force_stage is not None
        else None
    )
    graphics_trace = apply_graphics_trace_overlay(work) if args.graphics_trace else None
    state_trace = apply_state_trace_overlay(work) if args.state_trace else None
    cpp_cache = {}
    if args.reuse_cpp_from:
        previous = args.reuse_cpp_from.resolve()
        if not previous.is_relative_to(PRIVATE) or previous == output:
            parser.error("C++ cache must be an earlier private build directory")
        prior = json.loads((previous / "receipt.json").read_text(encoding="utf-8"))
        if prior["compiler_flags"] != list(FLAGS) or prior["runner_sha256"] != RUNNER_SHA256:
            raise RuntimeError("C++ cache toolchain/options differ")
        for record in prior["root_records"]:
            staged = work / record["source"]
            if (record["compile_exit"] != 0 or not record["omf_valid"]
                    or not staged.is_file() or sha256(staged) != record["source_sha256"]):
                continue
            obj = previous / "source" / record["objects"][0]
            if sha256(obj) != record["object_sha256"]:
                raise RuntimeError("C++ cache object identity drift")
            dependencies = describe_omf(obj.read_bytes())["dependency_paths"]
            unchanged = bool(dependencies)
            for dependency in dependencies:
                dependency = dependency.replace("\\", "/")
                # Vendor include files are covered by the toolchain attestation.
                if dependency.upper().startswith("C:/TC4/"):
                    continue
                old = previous / "source" / dependency
                current = (staged if dependency == record["compile_alias"]
                           else work / dependency)
                if (not old.is_file() or not current.is_file()
                        or sha256(old) != sha256(current)):
                    unchanged = False
                    break
            if unchanged:
                cpp_cache[record["source"]] = (record, obj)
    sprite_sources, sprite_asset_records = generate_sprite_sources(
        ROOT, work / "generated/sprites"
    )
    body_wrappers = materialize_body_wrappers(assembly_sources, work)
    if args.reuse_asm_from:
        previous = args.reuse_asm_from.resolve()
        if not previous.is_relative_to(PRIVATE) or previous == output:
            parser.error("ASM cache must be an earlier private build directory")
        prior = json.loads((previous / "receipt.json").read_text(encoding="utf-8"))
        if prior["runner_sha256"] != RUNNER_SHA256 or prior["compiler_flags"] != list(FLAGS):
            raise RuntimeError("ASM cache toolchain/options differ")
        for record in prior["asm_records"] + prior["state_records"]:
            if record["assemble_exit"] != 0 or not record["omf_valid"]:
                continue
            obj = previous / "source" / record["object"]
            if sha256(obj) != record["object_sha256"]:
                raise RuntimeError("ASM cache object identity drift")
            dependencies = describe_omf(obj.read_bytes())["dependency_paths"]
            unchanged = bool(dependencies)
            for dependency in dependencies:
                dependency = dependency.replace("\\", "/")
                old = previous / "source" / dependency
                current = work / dependency
                if (not old.is_file() or not current.is_file()
                        or sha256(old) != sha256(current)):
                    unchanged = False
                    break
            if unchanged:
                ASM_CACHE[record["source"]] = (record, obj)
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")

    # Historical aliases first; un-routed physical roots receive deterministic
    # short aliases. Their explicit pragma segment names remain intact.
    root_records: list[dict[str, object]] = []
    for index, source in enumerate(roots):
        relative = source.relative_to(ROOT).as_posix()
        alias = aliases.get(relative, EXTRA_ALIASES.get(
            relative, f"th04/u{index:03d}{source.suffix.lower()}"))
        if relative in cpp_cache:
            record, cached = cpp_cache[relative]
            record = dict(record)
            obj = work / f"obj/cpp/{index:03d}" / cached.name
            obj.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cached, obj)
            compile_alias = work / str(record["compile_alias"])
            compile_alias.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(work / relative, compile_alias)
            record.update(index=index, objects=[obj.relative_to(work).as_posix()],
                          reused_from=str(args.reuse_cpp_from), log=None)
            root_records.append(record)
        else:
            root_records.append(compile_cpp(source, alias, index, work, output, env))
    state_records = [assemble_state(source, index, work, output, env)
                     for index, source in enumerate(STATE_SOURCES)]
    asm_records = [
        assemble_asm(
            body_wrappers.get(source.relative_to(ROOT).as_posix(), source),
            index,
            work,
            output,
            env,
            "asm",
            "assemble-asm",
            logical_source=source,
        )
        for index, source in enumerate(assembly_sources)
        if source.relative_to(ROOT).as_posix() not in state_source_names
    ]
    sprite_records = [
        assemble_asm(source, index, work, output, env, "sprite", "assemble-sprite")
        for index, source in enumerate(sprite_sources)
    ]

    valid_cpp = [record for record in root_records
                 if record["compile_exit"] == 0 and record["omf_valid"]]
    valid_state = [record for record in state_records
                   if record["assemble_exit"] == 0 and record["omf_valid"]]
    valid_asm = [record for record in asm_records
                 if record["assemble_exit"] == 0 and record["omf_valid"]]
    valid_sprites = [record for record in sprite_records
                     if record["assemble_exit"] == 0 and record["omf_valid"]]
    # Keep each physical root once and order by group before TLINK.  This
    # prevents zero-length MAIN_03 state SEGDEFs from assigning later default
    # segments to the wrong group; it is a routing diagnostic, not exact order.
    priority = {"none": 0, "MAIN_01": 1, "MAIN_03": 2}
    ordered_records = sorted(
        valid_cpp,
        key=lambda item: (priority.get(str(item["primary_code_group"]), 3),
                          0 if item["has_nonzero_code"] else 1,
                          str(item["source"])),
    )
    anchor_records = [item for item in valid_asm
                      if item["source"] == LAYOUT_ANCHOR.as_posix()]
    if len(anchor_records) > 1:
        raise RuntimeError("layout anchor assembled more than once")
    other_asm = [item for item in valid_asm
                 if item["source"] != LAYOUT_ANCHOR.as_posix()]
    object_paths = [work / str(item["object"]) for item in anchor_records]
    object_paths.extend(work / str(item["objects"][0]) for item in ordered_records)
    object_paths.extend(work / str(item["object"]) for item in other_asm)
    object_paths.extend(work / str(item["object"]) for item in valid_state)
    object_paths.extend(work / str(item["object"]) for item in valid_sprites)
    link_result = link(work, output, object_paths, env, args.without_support)

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-main",
        "scope": "native MAIN physical-root link diagnostic",
        "runner_sha256": RUNNER_SHA256,
        "support_library": None if args.without_support else {
            "path": SUPPORT_LIB.relative_to(ROOT).as_posix(),
            "sha256": SUPPORT_SHA256,
        },
        "compiler_flags": list(FLAGS),
        "reused_cpp_count": len(cpp_cache),
        "source_tree_sha256": source_tree_digest(roots),
        "assembly_tree_sha256": source_tree_digest(assembly_sources),
        "root_count": len(roots),
        "included_cpp_count": len(included),
        "source_exclusions": sorted(SOURCE_EXCLUSIONS),
        "assembly_exclusions": sorted(ASM_EXCLUSIONS),
        "roots_compile_pass": len(valid_cpp),
        "roots_compile_fail": len(root_records) - len(valid_cpp),
        "state_count": len(STATE_SOURCES),
        "state_assemble_pass": len(valid_state),
        "state_assemble_fail": len(state_records) - len(valid_state),
        "asm_count": len(asm_records),
        "asm_assemble_pass": len(valid_asm),
        "asm_assemble_fail": len(asm_records) - len(valid_asm),
        "asm_state_exclusions": sorted(state_source_names),
        "body_only_contexts": {
            source: {"path": str(Path(source).with_suffix(".context.inc")),
                     "sha256": sha256((work / source).with_suffix(".context.inc"))}
            for source in sorted(BODY_ONLY_SOURCES)
        },
        "body_only_context_sources": sorted(BODY_ONLY_SOURCES),
        "input_trace": input_trace,
        "graphics_trace": graphics_trace,
        "state_trace": state_trace,
        "stage_override": args.force_stage,
        "sprite_asset_records": sprite_asset_records,
        "sprite_sources": sprite_records,
        "sprite_assemble_pass": len(valid_sprites),
        "sprite_assemble_fail": len(sprite_records) - len(valid_sprites),
        "root_records": root_records,
        "state_records": state_records,
        "asm_records": asm_records,
        "body_only_wrappers": {
            key: value.relative_to(work).as_posix()
            for key, value in body_wrappers.items()
        },
        "link": link_result,
        "limit": (
            "Native product build; runtime validation is separate. Twelve "
            "body-only ASM owners use checked-in declaration contexts. Sprite "
            "inputs are locally supplied reference BMPs. This build makes no "
            "byte-exactness claim; optional support-library mode is calibration."
        ),
    }
    (output / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "artifact": "th04-main",
        "root_count": len(roots),
        "roots_compile_pass": len(valid_cpp),
        "state_assemble_pass": len(valid_state),
        "sprite_assemble_pass": len(valid_sprites),
        "link_exit": link_result["exit"],
        "undefined": len(link_result["undefined_symbols"]),
        "duplicates": len(link_result["duplicate_errors"]),
        "group_overflows": len(link_result["group_overflows"]),
        "fixup_overflows": len(link_result["fixup_overflows"]),
        "mz": bool(link_result["mz"]),
    }, sort_keys=True))
    if args.require_link:
        complete = (len(valid_cpp) == len(root_records)
                    and len(valid_state) == len(state_records)
                    and len(valid_asm) == len(asm_records)
                    and len(valid_sprites) == len(sprite_records)
                    and link_result["exit"] == 0 and not link_result["errors"]
                    and link_result["mz"] and "error" not in link_result["mz"])
        return 0 if complete else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
