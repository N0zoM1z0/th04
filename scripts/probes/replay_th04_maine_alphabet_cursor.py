#!/usr/bin/env python3
"""Accept the bounded natural MAINE SCORE_TEXT alphabet cursor renderer."""

from __future__ import annotations

import argparse
from pathlib import Path

from maine_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v551",
    name="alphabet_cursor_put",
    source="src/maine/score/alpha.cpp",
    body="src/maine/score/alphabet_cursor.inl",
    object_stem="alpha",
    offset=0xC7E3,
    size=0x31,
    segment_offset=0x2793,
    start_anchor=b"void pascal near alphabet_cursor_put(int col, int row, int color)\n{",
    end_anchor=b"static const int ALPHABET_ROWS = 3;",
    terminal="ret 0x6",
    map_public="0A05:2793 idle  alphabet_cursor_put(int,int,int)",
    next_public="0A05:27C4       regist_menu()",
    target_references=(b"\x8a\x80\x2c\x08", b"\x9a\xc4\x0f"),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
