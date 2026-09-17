#!/usr/bin/env python3
"""Test natural TC4J frame-increment spellings in the MAIN gameplay loop."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tomllib

from probe_th04_gameplay_conditional import (
    ROOT, SOURCE, SOURCE_SHA256, SNAPSHOT, TARGET, TARGET_SHA256,
    RUNNER, compile_round,
)
from probe_th04_gameplay_ternary import CURRENT_MASK_CODE_SHA256, FLAGS

FRAME = "_AX = ((stage_frame = stage_frame + 1) & 15);"
FORMS = {
    "current": FRAME,
    "pre_increment": "_AX = (++stage_frame & 15);",
    "add_assign": "_AX = ((stage_frame += 1) & 15);",
    "post_increment_plus_one": "_AX = (((stage_frame++) + 1) & 15);",
    "post_increment_then_read": "stage_frame++;\n        _AX = (stage_frame & 15);",
}
EXPECTED_SIZES = {
    "current": 373,
    "pre_increment": 373,
    "add_assign": 373,
    "post_increment_plus_one": 374,
    "post_increment_then_read": 373,
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or output.parent != (ROOT / ".analysis/reconstruction/probes").resolve():
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    source = SOURCE.read_text(encoding="utf-8")
    target = TARGET.read_bytes()
    if sha(source.encode()) != SOURCE_SHA256 or sha(target) != TARGET_SHA256:
        raise RuntimeError("pinned MAIN target or gameplay source changed")
    if source.count(FRAME) != 1:
        raise RuntimeError("maintained frame expression changed")
    if sha((SNAPSHOT / "bin/th04/main.exe").read_bytes()) != (
        "1c1bcec509b775a6fa994d403d573ede75e74b8781ac5f0db06eb124d5fbae21"
    ):
        raise RuntimeError("v214 cold source snapshot changed")
    tcc = next(
        item for item in tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
        if item["id"] == "active-tcc"
    )
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise RuntimeError("active TC4J identity changed")

    header = int.from_bytes(target[8:10], "little") * 16
    target_body = target[header + 0xAB88:header + 0xAD03]
    if len(target_body) != 379 or target_body[0x115:0x121] != bytes.fromhex(
        "a1 8a 53 8b d0 40 a3 8a 53 25 0f 00"
    ):
        raise RuntimeError("target gameplay frame sequence changed")

    sources = {name: source.replace(FRAME, form) for name, form in FORMS.items()}
    output.mkdir(parents=True)
    a = compile_round("a", sources, output)
    b = compile_round("b", sources, output)
    if a != b:
        raise RuntimeError("isolated compiler rounds differ")
    for name, expected_size in EXPECTED_SIZES.items():
        item = a[name]
        if item["code_size"] != expected_size or item["mov_dx_ax_count"] != 0:
            raise RuntimeError(f"{name}: compiler shape changed")
    if a["current"]["code_sha256"] != CURRENT_MASK_CODE_SHA256:
        raise RuntimeError("maintained gameplay CODE changed")

    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN DEMO_TEXT gameplay frame-increment source controls; compiler diagnostic only",
        "target_sha256": TARGET_SHA256,
        "target_extent": "DEMO_TEXT 0AAF:0098; load 0xAB88..0xAD02; file 0xC388..0xC502",
        "target_body_sha256": sha(target_body),
        "target_frame_bytes": target_body[0x115:0x121].hex(),
        "source_sha256": SOURCE_SHA256,
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(RUNNER.read_bytes()),
        "flags": list(FLAGS),
        "variants_a": a,
        "variants_b": b,
        "result": "four ordinary increment spellings remain 373 or 374 bytes and none emits target MOV DX,AX before INC AX",
        "limit": "Compiler control only; no linked raw/MAP/ordered-relocation match or exact promotion.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    for name, item in a.items():
        print(f"{name}: CODE={item['code_size']} MOV_DX_AX={item['mov_dx_ax_count']}")
    print(f"receipt: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
