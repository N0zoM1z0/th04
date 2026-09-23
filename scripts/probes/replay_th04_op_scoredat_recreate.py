#!/usr/bin/env python3
"""Cold-compile OP's target-reviewed SCORE file regeneration function."""

from __future__ import annotations

import argparse
from pathlib import Path

from op_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v561",
    name="scoredat_recreate",
    source="src/op/score/scoregen.cpp",
    body="src/op/score/scoregen.inl",
    object_stem="scoregen",
    offset=0xC68C,
    size=0xA7,
    segment_offset=0x1F4C,
    start_anchor=b"{\n\tint i;\n\tint place;\n",
    end_anchor=b"\n}",
    terminal="ret",
    map_public="0A74:1F4C idle  scoredat_recreate()",
    next_public="0A74:1FF3 idle  hiscore_scoredat_load_both()",
    target_references=(
        b"\xC8\x02\x00\x00\x56\x57",       # local byte plus callee-saved SI/DI
        b"\xC6\x46\xFF\xA9",               # initial encoded rank digit
        b"\xC6\x06\x60\x3E\x19",           # cleared flag
        b"\xC6\x81\x10\x3E\xA0",           # empty encoded score digits
        b"\xC6\x87\x15\x3E\xA1",           # first place's ones digit
        b"\x88\x87\x14\x3E",               # other places' leading digit
        b"\x88\x94\x62\x3E",               # per-place stage
        b"\xC6\x81\xB6\x3D\xC4",           # gaiji-dot name fill
        b"\xC6\x87\xBE\x3D\x00",           # name terminator
        b"\x1E\x68\x42\x13\x9A\x6A\x09", # file_create(DS:1342)
        b"\xE8\x12\xFF",                    # scoredat_encode
        b"\x1E\x68\xB2\x3D\x68\xC4\x00", # file_write(hi, 0xC4)
        b"\xE8\x56\xFE",                    # scoredat_decode
        b"\x9A\x5A\x09\x00\x00",           # file_close
    ),
    standalone_near_fixup_words=(0x87, 0x96),
    target_data_references=((0x10682, b"GENSOU.SCR\x00"),),
    translation_unit="th04/formats/scoredat/recreate.cpp",
    translation_unit_sha256="079f4d72fa0f530af5b7c27f82e1d65673b7588a764961692a5170ecf15a8e62",
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
