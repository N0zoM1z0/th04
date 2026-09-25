#!/usr/bin/env python3
"""Cold-compile and raw-compare MAINE's high-score save wrapper."""

from __future__ import annotations

import argparse
from pathlib import Path

from maine_score_function_harness import ScoreFunction, run


SPEC = ScoreFunction(
    version="v682",
    name="hiscore_scoredat_save",
    source="src/maine/score/hisave.cpp",
    body="src/maine/score/hisave.inl",
    object_stem="hisave",
    offset=0xC316,
    size=0x9C,
    segment_offset=0x22C6,
    start_anchor=b"void near hiscore_scoredat_save(void)\n{",
    end_anchor=b"\n}\n",
    terminal="ret",
    map_public="hiscore_scoredat_save()",
    next_public="score_insert()",
    target_references=(
        b"\xE8\x84\xFE",              # initial scoredat_encode()
        b"\x9A\xA8\x08\x00\x00", # FILE_APPEND
        b"\xA0\x87\x40",              # rank
        b"\x68\xD4\x03\x00\x00", # second playchar bank (5 * 196)
        b"\x80\x3E\x88\x40\x00", # playchar != 0
        b"\x68\xC2\x3F",              # hi
        b"\x68\xC4\x00",              # sizeof(scoredat_section_t)
        b"\x9A\xD4\x09\x00\x00", # FILE_READ
        b"\xE8\xC7\xFD",              # scoredat_decode()
        b"\xE8\x1C\xFE",              # scoredat_encode()
        b"\x9A\x14\x0B\x00\x00", # FILE_WRITE
        b"\x9A\x68\x09\x00\x00", # FILE_CLOSE
    ),
    standalone_near_fixup_words=(0x05, 0x6A, 0x6D),
    translation_unit="th04/hiscore/score_sv.cpp",
    translation_unit_sha256="bad5527c97d375e54a754c29f40b3ff2c1629953b5c53e413ed20ecb4fc2a2be",
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
