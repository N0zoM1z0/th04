#!/usr/bin/env python3
"""Accept the bounded natural MAINE SCORE_TEXT stage renderer."""

from __future__ import annotations

import argparse
from pathlib import Path

from maine_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v547",
    name="stage_put",
    source="src/maine/score/stage.cpp",
    body="src/maine/score/stage_put.inl",
    object_stem="stage",
    offset=0xC5EC,
    size=0x79,
    segment_offset=0x259C,
    start_anchor=b"void pascal near stage_put(int place, int rendered_playchar, int gaiji)\n{",
    end_anchor=b"void pascal near score_rect_copy(int left, int top, int w, int h);",
    terminal="ret 0x6",
    map_public="0A05:259C idle  stage_put(int,int,int)",
    next_public="0A05:2615 idle  name_cursor_put(int,unsigned char,unsigned char)",
    target_references=(b"\x86\x40", b"\x88\x40", b"\x9a\x60\x37"),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
