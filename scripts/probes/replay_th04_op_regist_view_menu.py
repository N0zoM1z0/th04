#!/usr/bin/env python3
"""Probe OP's target-reviewed 335-byte registration-view menu function."""

from __future__ import annotations

import argparse
from pathlib import Path

from op_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v556",
    name="regist_view_menu",
    source="src/op/score/menu.cpp",
    body="src/op/score/regist_view_menu.inl",
    object_stem="menu",
    offset=0xCA94,
    size=0x14F,
    segment_offset=0x2354,
    start_anchor=b"void near regist_view_menu(void)\n{",
    end_anchor=b"#if (GAME == 5)\nvoid near cleardata_and_regist_view_sprites_load",
    terminal="ret",
    map_public="0A74:2354       regist_view_menu()",
    next_public="0A74:24A3       cleardata_and_regist_view_sprite()",
    target_references=(b"\xf6\x06\x11\x27\x20", b"\x66\xff\x36\x70\x23"),
    standalone_near_fixup_words=(57, 71, 150, 153, 192),
    standalone_data_fixup_words=(13, 54, 63, 129, 136, 171, 178, 235, 316),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
