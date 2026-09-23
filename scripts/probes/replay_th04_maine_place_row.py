#!/usr/bin/env python3
"""Accept the bounded natural MAINE SCORE_TEXT score-entry row renderer."""

from __future__ import annotations

import argparse
from pathlib import Path

from maine_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v549",
    name="place_row_put",
    source="src/maine/score/place.cpp",
    body="src/maine/score/place_row_put.inl",
    object_stem="place",
    offset=0xC711,
    size=0xB8,
    segment_offset=0x26C1,
    start_anchor=b"void pascal near place_row_put(int place, unsigned char rendered_playchar)\n{",
    end_anchor=b"void pascal near places_put(int rendered_playchar)",
    terminal="ret 0x4",
    map_public="0A05:26C1 idle  place_row_put(int,unsigned char)",
    next_public="0A05:2779 idle  places_put(int)",
    target_references=(b"\xe8\x54\xfd", b"\xe8\x29\xfe", b"\x9a\xb6\x36", b"\x9a\x08\x10"),
    standalone_near_fixup_words=(0x9F, 0xB0),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
