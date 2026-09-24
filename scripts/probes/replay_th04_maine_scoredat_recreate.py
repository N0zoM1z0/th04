#!/usr/bin/env python3
"""Cold-compile and raw-compare MAINE's target-derived SCORE initializer."""

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
    version="v580",
    name="scoredat_recreate",
    source="src/maine/score/scoregen.cpp",
    body="src/maine/score/scoregen.inl",
    object_stem="scoregen",
    offset=0xC206,
    size=0xA7,
    segment_offset=0x21B6,
    start_anchor=b"{\n\tint i;\n\tint place;\n",
    end_anchor=b"\n}",
    terminal="ret",
    map_public="scoredat_recreate()",
    next_public="hiscore_scoredat_load_for(playchar_t)",
    target_references=(
        b"\xC6\x06\x70\x40\x19",        # cleared marker
        b"\xC6\x87\x25\x40\xA1",        # first-row seed digit
        b"\xC6\x87\xCE\x3F\x00",        # name terminator
        b"\x9A\x78\x09\x00\x00",        # file_create
        b"\x68\xC4\x00",                # serialized scoredat_section_t size
        b"\xE8\x12\xFF",                # scoredat_encode
        b"\xE8\xAB\xFE",                # scoredat_decode
        b"\x9A\x68\x09\x00\x00",        # file_close
    ),
    standalone_near_fixup_words=(0x87, 0x96),
    translation_unit="th04/formats/scoredat/recreate.cpp",
    translation_unit_sha256="079f4d72fa0f530af5b7c27f82e1d65673b7588a764961692a5170ecf15a8e62",
    replace_end_anchor=True,
)


def cleanup_intermediates(output: Path) -> None:
    for label in ("a", "b"):
        shutil.rmtree(output / label, ignore_errors=True)
    for pattern in ("compile-*.log", "link-*.log"):
        for log in output.glob(pattern):
            log.unlink()


def record_natural_codegen_result(output: Path, error: RuntimeError) -> bool:
    expected_errors = (
        "a: maintained scoredat_recreate standalone CODE size drift",
        "a: maintained scoredat_recreate standalone CODE differs",
    )
    if not str(error).startswith(expected_errors):
        return False

    obj = output / "a/maine/source/obj/th04/scoregen.obj"
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
    source_paths = sorted(harness.source_closure(harness.ROOT, (SPEC.source,)))
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
        "source_sha256": {
            path: harness.prior.sha_file(harness.ROOT / path) for path in source_paths
        },
        "candidate_translation_unit": SPEC.translation_unit,
        "candidate_translation_unit_sha256": SPEC.translation_unit_sha256,
        "compiler": "TC86 Borland C++ 4.02, MAINE SCORE_TEXT function harness flags",
        "standalone_size": len(producer),
        "standalone_size_delta_bytes": len(producer) - len(target_body),
        "standalone_sha256": harness.prior.sha(producer),
        "standalone_omf_sha256": harness.prior.sha_file(obj),
        "standalone_disassembly": [
            str(row["text"]) for row in harness.disassemble(ndisasm, producer, SPEC.offset)
        ],
        "target_disassembly": [
            str(row["text"])
            for row in harness.disassemble(ndisasm, target_body, SPEC.offset)
        ],
        "harness_failure": str(error),
        "limit": "Natural standalone CODE diagnostic only; no packed offset, full-TU or whole-MAINE exact claim.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    cleanup_intermediates(output)
    print(json.dumps({"receipt": str(receipt_path), "function_raw_equal": False,
                      "standalone_size": len(producer),
                      "target_size": len(target_body)}, sort_keys=True))
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retain-candidates", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    try:
        run(SPEC, output)
    except RuntimeError as error:
        if not record_natural_codegen_result(output, error):
            raise
    else:
        if not args.retain_candidates:
            cleanup_intermediates(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
