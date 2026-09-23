#!/usr/bin/env python3
"""Record the pinned natural-C++ codegen limit for OP scoredat_encode."""

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
    version="v562",
    name="scoredat_encode",
    source="src/op/score/scoreenc.cpp",
    body="src/op/score/scoreenc.inl",
    object_stem="scoreenc",
    offset=0xC627,
    size=0x65,
    segment_offset=0x1EE7,
    start_anchor=b"void pascal near scoredat_encode(void)\n",
    end_anchor=b"\n}",
    terminal="ret",
    map_public="0A74:1EE7 idle  scoredat_encode()",
    next_public="0A74:1F4C idle  scoredat_recreate()",
    target_references=(
        b"\xC8\x02\x00\x00",
        b"\xC7\x06\xB4\x3D\x00\x00",
        b"\x9A\x4E\x20\x00\x00",
        b"\x8A\x84\xB2\x3D",
        b"\xC0\x4E\xFF\x03",
        b"\xC3",
    ),
    translation_unit="th04/formats/scoredat/encode.cpp",
    translation_unit_sha256="fca3a24051e1ffefe545f3dd1176ed9cffe4ff7b7a420fe5dcc68f5a8ae86981",
    target_data_references=(
        (0x204E, bytes.fromhex(
            "B8354EF726C6058BC8B85A01F726C40503C8B8354EF726C405050100"
            "13D1A3C4058BC2A3C60580E47FCB"
        )),
    ),
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


def run(output: Path) -> Path:
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    output = output.resolve()
    if output.exists() or output.parent != private:
        raise ValueError("output must be new directly below .analysis/reconstruction/probes")
    try:
        harness.run(SPEC, output)
    except RuntimeError as error:
        if str(error) != "a: standalone scoredat_encode CODE size drift":
            raise
    else:
        raise RuntimeError("natural-C++ source unexpectedly passed the exact function harness")

    work = output / "a/op/source"
    obj = work / "obj/th04/scoreenc.obj"
    if not obj.is_file():
        raise RuntimeError("expected standalone OMF object missing after codegen mismatch")
    target = harness.prior.parse_mz(harness.prior.TARGET.read_bytes())
    if not target.valid:
        raise RuntimeError("target MZ invalid while recording codegen mismatch")
    target_body = target.program_image[SPEC.offset:SPEC.offset + SPEC.size]
    producer = harness.prior.segment_bytes(obj, "SCORE_TEXT")
    omf = describe_omf(obj.read_bytes())
    if not omf["valid"] or "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
        raise RuntimeError("standalone producer OMF identity invalid")

    log = output / "compile-v562-local-a.log"
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "pinned-TC86 standalone natural-C++ codegen probe only; not an exact acceptance",
        "artifact": "th04-op",
        "function": SPEC.name,
        "payload_offset": "0xC627",
        "segment_identity": "1A74",
        "segment_offset": "1EE7",
        "target_size": len(target_body),
        "target_sha256": sha(target_body),
        "maintained_source": [SPEC.source, SPEC.body],
        "source_sha256": {
            path: harness.prior.sha_file(ROOT / path)
            for path in harness.prior.source_closure(ROOT, (SPEC.source,))
        },
        "candidate_translation_unit": SPEC.translation_unit,
        "candidate_translation_unit_sha256": SPEC.translation_unit_sha256,
        "compiler": "TC86 Borland C++ 4.02, pinned OP function harness flags",
        "standalone_size": len(producer),
        "standalone_sha256": sha(producer),
        "standalone_omf_sha256": harness.prior.sha_file(obj),
        "target_equal": producer == target_body,
        "differing_spans_half_open": differing_spans(target_body, producer),
        "target_rotate_opcode_offset": "0x55",
        "target_rotate_opcode": "C0 4E FF 03 (ROR byte [BP-1], 3)",
        "result": "nonexact-natural-cpp-codegen",
        "scratch_source_tree_pruned": True,
        "log": log.name,
        "limit": "The natural C++ _crotr call is not the target's in-place byte ROR. No target-derived inline assembly or altered compiler flags are used.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(output / "a")
    return receipt_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    print(run(args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
