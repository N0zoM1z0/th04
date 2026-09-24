#!/usr/bin/env python3
"""Cold-compile and raw-compare MAINE's natural score-data decoder."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

import maine_score_function_harness as harness
from maine_score_function_harness import ScoreFunction, run
from lib.omf import describe_omf


SPEC = ScoreFunction(
    version="v574",
    name="scoredat_decode",
    source="src/maine/score/scoredec.cpp",
    body="src/maine/score/scoredec.inl",
    object_stem="scoredec",
    offset=0xC149,
    size=0x58,
    segment_offset=0x20F9,
    start_anchor=b'#include "th04/formats/scoredat/decode.cpp"\n',
    end_anchor=b'#include "th04/formats/scoredat/decode.cpp"\n',
    terminal="ret",
    map_public="scoredat_decode()",
    next_public="scoredat_encode()",
    target_references=(
        b"\x8A\x84\xC3\x3F",  # next encoded byte, indexed from key1
        b"\xC0\x4E\xFF\x03",  # ROR byte [BP-1], 3
        b"\xA0\xC2\x3F",       # key1
        b"\xA0\xC3\x3F",       # key2
        b"\x81\xFE\xC4\x00",  # 196-byte record boundary
    ),
    translation_unit="th04/score_d.cpp",
    translation_unit_sha256="0ce8302bd44c4cd4bb4198e15fd77c8ec67b480d34f4d9d2aa276143d1ba8f36",
    replace_end_anchor=True,
)


def record_natural_codegen_result(output: Path, error: RuntimeError) -> bool:
    expected_errors = (
        "a: maintained scoredat_decode standalone CODE size drift",
        "a: maintained scoredat_decode standalone CODE differs",
    )
    if not str(error).startswith(expected_errors):
        return False

    obj = output / "a/maine/source/obj/th04/scoredec.obj"
    if not obj.is_file():
        raise RuntimeError("natural-codegen mismatch has no standalone OMF object") from error
    target = harness.prior.parse_mz(harness.prior.TARGET.read_bytes())
    if not target.valid:
        raise RuntimeError("target MZ invalid while recording natural-codegen result") from error
    target_body = target.program_image[SPEC.offset:SPEC.offset + SPEC.size]
    producer = harness.segment_bytes(obj, "SCORE_TEXT")
    omf = describe_omf(obj.read_bytes())
    if not omf["valid"] or "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
        raise RuntimeError("standalone producer OMF identity invalid") from error
    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm unavailable while recording natural-codegen result") from error
    listing = [
        str(row["text"])
        for row in harness.disassemble(ndisasm, producer, SPEC.offset)
    ]
    target_listing = [
        str(row["text"])
        for row in harness.disassemble(ndisasm, target_body, SPEC.offset)
    ]
    source_paths = sorted(harness.source_closure(harness.ROOT, (SPEC.source,)))
    source_hashes = {
        path: harness.prior.sha_file(harness.ROOT / path) for path in source_paths
    }
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed natural-C++ standalone codegen diagnostic; not exact acceptance",
        "artifact": "th04-maine",
        "function": SPEC.name,
        "payload_offset": f"0x{SPEC.offset:X}",
        "segment_identity": "1A05",
        "segment_offset": f"0x{SPEC.segment_offset:04X}",
        "target_size": len(target_body),
        "target_sha256": harness.prior.sha(target_body),
        "target_boundary": harness.target_boundary(SPEC, target_body),
        "maintained_source": source_paths,
        "source_sha256": source_hashes,
        "compiler": "TC86 Borland C++ 4.02, MAINE SCORE_TEXT harness flags",
        "standalone_size": len(producer),
        "standalone_size_delta_bytes": len(producer) - len(target_body),
        "standalone_sha256": harness.prior.sha(producer),
        "standalone_omf_sha256": harness.prior.sha_file(obj),
        "standalone_disassembly": listing,
        "target_disassembly": target_listing,
        "harness_failure": str(error),
        "limit": "Natural standalone CODE diagnostic only; no packed offset, full-TU or whole-MAINE exact claim.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "function_raw_equal": False,
                      "standalone_size": len(producer),
                      "target_size": len(target_body)}, sort_keys=True))
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        run(SPEC, args.output_dir)
    except RuntimeError as error:
        if not record_natural_codegen_result(args.output_dir.resolve(), error):
            raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
