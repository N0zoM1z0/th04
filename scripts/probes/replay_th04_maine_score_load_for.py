#!/usr/bin/env python3
"""Cold-compile and raw-compare MAINE's bounded high-score loader."""

from __future__ import annotations

import argparse
from pathlib import Path

from maine_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v557",
    name="hiscore_scoredat_load_for",
    source="src/maine/score/load_for.cpp",
    body="src/maine/score/load_for.inl",
    object_stem="load_for",
    offset=0xC2AD,
    size=0x69,
    segment_offset=0x225D,
    start_anchor=b"#if ((GAME == 4) && (BINARY == 'M'))\n#define recreated",
    end_anchor=b"\treturn loaded;\n}",
    terminal="ret 0x2",
    map_public="hiscore_scoredat_load_for(playchar_t)",
    next_public="hiscore_scoredat_save()",
    target_references=(
        b"\xA0\x87\x40",       # target-local rank byte
        b"\x68\xD4\x03\x00\x00",  # second character's 5-record bank
        b"\x68\xC2\x3F",       # target-local hi record
        b"\x68\xC4\x00",       # 196-byte score section
    ),
    standalone_near_fixup_words=(0x54, 0x5B),
    translation_unit="th04/hiscore/score_ld.cpp",
    translation_unit_sha256="c4bea8a87a7d977704aac082582ca294de5f666c6ded0a14247303df91f507b4",
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
