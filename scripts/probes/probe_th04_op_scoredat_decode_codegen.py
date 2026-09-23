#!/usr/bin/env python3
"""Replay or record the pinned natural-C++ codegen result for OP scoredat_decode."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

import op_score_function_harness as harness
from op_score_function_harness import ScoreFunction
from lib.omf import describe_omf


ROOT = harness.ROOT
SPEC = ScoreFunction(
    version="v563",
    name="scoredat_decode",
    source="src/op/score/scoredec.cpp",
    body="src/op/score/scoredec.inl",
    object_stem="scoredec",
    offset=0xC57A,
    size=0xAD,
    segment_offset=0x1E3A,
    start_anchor=b"uint8_t pascal near scoredat_decode(void)\n{\n",
    end_anchor=b"\n}",
    terminal="ret",
    map_public="0A74:1E3A idle  scoredat_decode()",
    next_public="0A74:1EE7 idle  scoredat_encode()",
    target_references=(
        b"\xC8\x02\x00\x00",
        b"\xBE\x04\x00",
        b"\xC0\x4E\xFF\x03",
        b"\x39\x0E\xB4\x3D",
        b"\xA0\x78\x3E",
        b"\xC9\xC3",
    ),
    translation_unit="th04/formats/scoredat/decode.cpp",
    translation_unit_sha256="3dc54b4c4cc6fa862a4495b7a0a6a64a7698955fac42d8da7fe1158d2bf9d406",
)

CODEGEN_DRIFT_PREFIXES = (
    "a: standalone scoredat_decode CODE size drift",
    "a: scoredat_decode standalone CODE differs:",
    "a: scoredat_decode non-fixup CODE mismatch:",
    "b: standalone scoredat_decode CODE size drift",
    "b: scoredat_decode standalone CODE differs:",
    "b: scoredat_decode non-fixup CODE mismatch:",
)


def sha(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def differing_spans(left: bytes, right: bytes) -> list[dict[str, int]]:
    mismatch = [
        i for i in range(max(len(left), len(right)))
        if i >= len(left) or i >= len(right) or left[i] != right[i]
    ]
    spans: list[dict[str, int]] = []
    for offset in mismatch:
        if spans and spans[-1]["end"] == offset:
            spans[-1]["end"] += 1
        else:
            spans.append({"start": offset, "end": offset + 1})
    return spans


def negative_receipt(output: Path, stage: str) -> Path:
    obj = output / "a/op/source/obj/th04/scoredec.obj"
    if not obj.is_file():
        obj = output / "b/op/source/obj/th04/scoredec.obj"
    if not obj.is_file():
        raise RuntimeError("codegen mismatch had no standalone OMF object to attest")

    target = harness.prior.parse_mz(harness.prior.TARGET.read_bytes())
    if not target.valid:
        raise RuntimeError("target MZ invalid while recording natural-codegen mismatch")
    target_body = target.program_image[SPEC.offset:SPEC.offset + SPEC.size]
    producer = harness.prior.segment_bytes(obj, "SCORE_TEXT")
    omf = describe_omf(obj.read_bytes())
    if not omf["valid"] or "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
        raise RuntimeError("standalone producer OMF identity invalid")
    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm unavailable while retaining codegen diagnostic")
    listing = "\n".join(
        str(row["text"])
        for row in harness.prior.disassemble(ndisasm, producer, SPEC.offset)
    ) + "\n"
    listing_path = output / "standalone-scoredat_decode.ndisasm"
    listing_path.write_text(listing, encoding="ascii")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "pinned-TC86 natural-C++ standalone codegen probe only; not exact acceptance",
        "artifact": "th04-op",
        "function": SPEC.name,
        "payload_offset": "0xC57A",
        "segment_identity": "1A74",
        "segment_offset": "1E3A",
        "target_size": len(target_body),
        "target_sha256": sha(target_body),
        "maintained_source": [SPEC.source, SPEC.body],
        "source_sha256": {
            path: harness.prior.sha_file(ROOT / path)
            for path in harness.prior.source_closure(ROOT, (SPEC.source,))
        },
        "compiler": "TC86 Borland C++ 4.02, pinned OP function harness flags",
        "standalone_size": len(producer),
        "standalone_sha256": sha(producer),
        "standalone_omf_sha256": harness.prior.sha_file(obj),
        "target_equal": producer == target_body,
        "differing_spans_half_open": differing_spans(target_body, producer),
        "codegen_mismatch_stage": stage,
        "standalone_listing": listing_path.name,
        "standalone_listing_sha256": sha(listing.encode("ascii")),
        "target_rotate_opcode_offsets": ["0x14", "0x69"],
        "target_rotate_opcode": "C0 4E FF 03 (ROR byte [BP-1], 3)",
        "result": "nonexact-natural-cpp-codegen",
        "scratch_source_tree_pruned": True,
        "limit": "The natural C shift/OR rotation emits more bytes than the target's in-place ROR; no candidate inline assembly or altered compiler flags are used.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt_path


def run(output: Path) -> Path:
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    output = output.resolve()
    if output.exists() or output.parent != private:
        raise ValueError("output must be new directly below .analysis/reconstruction/probes")

    try:
        receipt_path = harness.run(SPEC, output)
    except RuntimeError as error:
        stage = str(error)
        if not stage.startswith(CODEGEN_DRIFT_PREFIXES):
            raise
        receipt_path = negative_receipt(output, stage)

    for label in ("a", "b"):
        tree = output / label
        if tree.exists():
            shutil.rmtree(tree)
    return receipt_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(run(args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
