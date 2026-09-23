#!/usr/bin/env python3
"""Accept the bounded natural OP SCORE_TEXT rank renderer with its reachable tail."""

from __future__ import annotations

import argparse
from pathlib import Path

from op_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v553",
    name="rank_render",
    source="src/op/score/rank.cpp",
    body="src/op/score/rank_render.inl",
    object_stem="rank",
    offset=0xCA1A,
    size=0x7A,
    segment_offset=0x22DA,
    start_anchor=b"void near rank_render(void)\n{",
    end_anchor=b"void near regist_view_menu(void)",
    terminal="ret",
    map_public="0A74:22DA idle  rank_render()",
    next_public="0A74:2354       regist_view_menu()",
    target_references=(b"\x9a\x40\x00\xa1\x0d", b"\xe8\xa4\xfe", b"\xa0\x3b\x3f",
                       b"\x9a\x5a\x2d", b"\xeb\x05"),
    standalone_near_fixup_words=(0x35, 0x3E, 0x49),
    standalone_data_fixup_words=(0x52, 0x68),
    ghidra_prefix_size=0x3C,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
