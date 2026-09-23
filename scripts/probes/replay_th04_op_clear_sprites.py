#!/usr/bin/env python3
"""Probe OP's bounded natural registration-view clear/sprite initializer."""

from __future__ import annotations

import argparse
from pathlib import Path

from op_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v554",
    name="cleardata_and_regist_view_sprite",
    source="src/op/score/clear.cpp",
    body="src/op/score/clear_sprites_load.inl",
    object_stem="clear",
    offset=0xCBE3,
    size=0xB4,
    segment_offset=0x24A3,
    start_anchor=b"// ZUN bloat: Same as the TH05 version",
    end_anchor=b"#endif\n",
    terminal="ret",
    # The private function has no MAP public; Ghidra/target disassembly and
    # the grouped SCORE_TEXT contribution bound it instead.
    map_public="",
    next_public="",
    target_references=(b"\xe8\x42\xfb", b"\x3b\x3f", b"\x46\x3f", b"\x86\x2a"),
    standalone_near_fixup_words=(0x0C,),
    standalone_data_fixup_words=(
        0x05, 0x15, 0x21, 0x24, 0x2A, 0x30, 0x33, 0x3B, 0x41,
        0x49, 0x4D, 0x55, 0x5B, 0x63, 0x68, 0x6E, 0x76, 0x7A,
        0x82, 0x86, 0x8A, 0x8E, 0x9E, 0xA2, 0xAB,
    ),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
