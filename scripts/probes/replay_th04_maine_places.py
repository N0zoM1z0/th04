#!/usr/bin/env python3
"""Accept the bounded natural MAINE SCORE_TEXT row dispatcher."""

from __future__ import annotations

import argparse
from pathlib import Path

from maine_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v550",
    name="places_put",
    source="src/maine/score/places.cpp",
    body="src/maine/score/places_put.inl",
    object_stem="places",
    offset=0xC7C9,
    size=0x1A,
    segment_offset=0x2779,
    start_anchor=b"void pascal near places_put(int rendered_playchar)\n{",
    end_anchor=b"void pascal near alphabet_cursor_put(int col, int row, int color)",
    terminal="ret 0x2",
    map_public="0A05:2779 idle  places_put(int)",
    next_public="0A05:2793 idle  alphabet_cursor_put(int,int,int)",
    target_references=(b"\xe8\x39\xff", b"\x83\xfe\x0a"),
    standalone_near_fixup_word=0x0D,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
