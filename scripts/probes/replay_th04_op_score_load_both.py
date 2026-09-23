#!/usr/bin/env python3
"""Cold-compile OP's target-reviewed two-column score loader."""

from __future__ import annotations

import argparse
from pathlib import Path

from op_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v558",
    name="hiscore_scoredat_load_both",
    source="src/op/score/loadboth.cpp",
    body="src/op/score/load_both.inl",
    object_stem="loadboth",
    offset=0xC733,
    size=0x6B,
    segment_offset=0x1FF3,
    start_anchor=b"{\n#if (BINARY == 'O')\n\t#define SCOREDAT_FN_0 SCOREDAT_FN",
    end_anchor=b"\n\treturn loaded;\n}",
    terminal="ret",
    map_public="0A74:1FF3 idle  hiscore_scoredat_load_both()",
    next_public="0A74:205E idle  scores_put(int,int)",
    target_references=(
        b"\x68\x42\x13",                 # DS:1342 file-name pointer
        b"\xA0\x3B\x3F",                 # target-local rank byte
        b"\x69\xC0\xC4\x00",           # rank * 196-byte section
        b"\x66\x68\x10\x03\x00\x00", # second character bank: +0x310
        b"\x68\xB2\x3D",                 # first decoded hi section
        b"\x68\x76\x3E",                 # second decoded hi2 section
    ),
    standalone_near_fixup_words=(90, 97),  # scoredat_decode and scoredat_recreate
    standalone_data_fixup_words=(26, 74),  # rank and hi2 in DGROUP
    translation_unit="th04/hiscore/score_ld.cpp",
    translation_unit_sha256="c4bea8a87a7d977704aac082582ca294de5f666c6ded0a14247303df91f507b4",
    replace_end_anchor=True,
    target_data_references=((0x10682, b"GENSOU.SCR\0"),),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    run(SPEC, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
