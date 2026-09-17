#!/usr/bin/env python3
"""Replay TASM 5.0 EVEN fill control from checked-in symbolic source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]
from lib.omf import describe_omf, parse_omf  # noqa: E402
from inspect_dialog_fixup_order import omf_index  # noqa: E402

SOURCE = ROOT / "probes/toolchain/tasm_even_context.asm"
EXPECTED = {
    "DATA_IN_CODE": bytes.fromhex("01 00"),
    "DATA_IN_DATA": bytes.fromhex("01 00"),
    "INSTR_IN_DATA": bytes.fromhex("90 90"),
    "INSTR_IN_CODE": bytes.fromhex("90 90"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def segment_bytes(records: tuple) -> dict[str, bytes]:
    names = [""]
    segments = []
    payloads = {}
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                length = record.data[pos]
                names.append(record.data[pos + 1:pos + 1 + length].decode("latin-1"))
                pos += length + 1
        elif record.record_type == 0x98:
            data = record.data
            pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            index, _ = omf_index(data, pos)
            segments.append(names[index])
        elif record.record_type == 0xA0:
            index, pos = omf_index(record.data, 0)
            offset = int.from_bytes(record.data[pos:pos + 2], "little")
            if offset != 0 or segments[index - 1] in payloads:
                raise ValueError("unexpected EVEN control LEDATA layout")
            payloads[segments[index - 1]] = record.data[pos + 2:]
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="tasm-even-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    assembler = next(item for item in surfaces if item["id"] == "active-tasm32")
    if sha((ROOT / assembler["path"]).read_bytes()) != assembler["sha256"]:
        raise ValueError("active TASM32 identity failed")
    source = SOURCE.read_bytes()
    (output / "EVENCTX.ASM").write_bytes(source)
    command = ["wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx", "/kh32768",
               "EVENCTX.ASM,EVENCTX.OBJ,EVENCTX.LST"]
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"), WINEDEBUG="-all")
    done = subprocess.run(command, cwd=output, env=env, capture_output=True,
                          text=True, timeout=120)
    (output / "assemble.log").write_text(json.dumps(command) +
                                           f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr)
    object_path = output / "EVENCTX.OBJ"
    if done.returncode or not object_path.is_file():
        raise ValueError("TASM EVEN control assembly failed")
    obj = object_path.read_bytes()
    if not describe_omf(obj)["valid"]:
        raise ValueError("invalid TASM control OMF")
    payloads = segment_bytes(parse_omf(obj))
    if payloads != EXPECTED:
        raise ValueError(f"TASM EVEN fill changed: {payloads!r}")
    receipt = {"schema_version": 1,
               "claim_scope": "TASM 5.0 EVEN fill depends on preceding source kind in this four-segment control",
               "source_sha256": sha(source), "tasm_sha256": assembler["sha256"],
               "object_sha256": sha(obj), "command": command,
               "segments": {name: data.hex(" ") for name, data in payloads.items()},
               "result": "data then EVEN emits 00; instruction then EVEN emits 90 in both CODE and DATA classes",
               "limit": "Synthetic assembler control; OP/MAINE historical source and packed-file origins remain unknown."}
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
