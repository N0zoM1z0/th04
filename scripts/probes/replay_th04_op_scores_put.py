#!/usr/bin/env python3
"""Cold-compile OP's target-reviewed two-column score renderer."""

from __future__ import annotations

import argparse
from pathlib import Path

from op_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v559",
    name="scores_put",
    source="src/op/score/scoreput.cpp",
    body="src/op/score/scores_put.inl",
    object_stem="scoreput",
    offset=0xC79E,
    size=0x107,
    segment_offset=0x205E,
    start_anchor=b"{\n\tint digit;\n\tpixel_t rel_left = DIGIT_W;",
    end_anchor=b"\n\t}\n}",
    terminal="ret 0x4",
    map_public="0A74:205E idle  scores_put(int,int)",
    next_public="0A74:2165 idle  stage_put(int,int,int)",
    target_references=(
        b"\xC8\x04\x00\x00",       # two local words
        b"\x8B\x7E\x06",             # top argument
        b"\x8B\x76\x04",             # place argument
        b"\xC7\x46\xFC\x10\x00", # first 16-pixel step
        b"\x8A\x87\x17\x3E",         # hi digits[7] via place*8
        b"\x8A\x87\xDB\x3E",         # hi2 digits[7] via place*8
        b"\x8A\x87\x10\x3E",         # hi digits[0..6] via place*8
        b"\x8A\x87\xD4\x3E",         # hi2 digits[0..6] via place*8
        b"\x68\x8C\x00",             # Reimu optional leading digit
        b"\x68\xC0\x01",             # Marisa optional leading digit
        b"\x68\x9C\x00",             # Reimu ones digit
        b"\x68\xD0\x01",             # Marisa ones digit
        b"\x05\x60\xFF",             # subtract gaiji zero 0xA0
        b"\x3D\x0A\x00",             # suppress zero leading pair
        b"\xBB\x0A\x00\x99\xF7\xFB", # signed divide by ten
        b"\x9A\x5A\x2D",             # target super_put call
        b"\xC7\x46\xFE\x06\x00", # remaining seven digits
        b"\x83\x7E\xFE\x00",       # loop to digit zero
    ),
    standalone_near_fixup_words=(),
    # Only these four unresolved score-array address words differ from the
    # historical grouped SCORE object; all are parsed OMF FIXUPP sites.
    standalone_data_fixup_words=(0x49, 0x60, 0x9C, 0xE7),
    translation_unit="th04/hiscore/view.cpp",
    replace_end_anchor=True,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
