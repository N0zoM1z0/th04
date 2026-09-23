#!/usr/bin/env python3
"""Accept the bounded natural OP SCORE_TEXT two-column row renderer."""

from __future__ import annotations

import argparse
from pathlib import Path

from op_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v552",
    name="place_put",
    source="src/op/score/place.cpp",
    body="src/op/score/place_put.inl",
    object_stem="place",
    offset=0xC8F5,
    size=0x125,
    segment_offset=0x21B5,
    start_anchor=b"void pascal near place_put(int place)\n{",
    end_anchor=b"#endif\n\nvoid near rank_render(void)",
    terminal="ret 0x2",
    map_public="0A74:21B5 idle  place_put(int)",
    next_public="0A74:22DA idle  rank_render()",
    target_references=(b"\x9a\x8a\x3d", b"\xe8\x2e\xfe", b"\xe8\x25\xff",
                       b"\x62\x3e", b"\x26\x3f"),
    standalone_near_fixup_words=(0x79, 0x89, 0x101, 0x10F, 0x11D),
    standalone_data_fixup_words=(0x4E, 0x67, 0xDC, 0xF3, 0x117),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
