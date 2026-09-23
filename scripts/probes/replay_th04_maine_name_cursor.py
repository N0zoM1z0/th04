#!/usr/bin/env python3
"""Accept the bounded natural MAINE SCORE_TEXT name cursor renderer."""

from __future__ import annotations

import argparse
from pathlib import Path

from maine_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v548",
    name="name_cursor_put",
    source="src/maine/score/cursor.cpp",
    body="src/maine/score/name_cursor.inl",
    object_stem="cursor",
    offset=0xC665,
    size=0xAC,
    segment_offset=0x2615,
    start_anchor=b"void pascal near name_cursor_put(int place, unsigned char rendered_playchar, unsigned char cursor)\n{",
    end_anchor=b"extern unsigned char gALPHABET[];",
    terminal="ret 0x6",
    map_public="0A05:2615 idle  name_cursor_put(int,unsigned char,unsigned char)",
    next_public="0A05:26C1 idle  place_row_put(int,unsigned char)",
    target_references=(b"\xe8\x4a\x05",),
    standalone_near_fixup_word=0x42,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
