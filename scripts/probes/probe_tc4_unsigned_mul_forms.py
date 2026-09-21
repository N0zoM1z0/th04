#!/usr/bin/env python3
"""Probe TC4J signedness/width source forms for TH04 carpet MUL BX.

The carpet target uses unsigned ``MUL BX`` (F7 E3) twice.  This probe checks
natural C/C++ forms that materially change the source type semantics, rather
than retrying optimizer switches: explicit unsigned casts, unsigned locals, and
an unsigned 32-bit product whose high half is observable.  It is compiler-
surface evidence only and grants no exactness or inline-assembly provenance.
"""
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
PRIVATE = (ROOT / ".analysis").resolve()
sys.path.insert(0, str(ROOT / "scripts/probes"))
from probe_tc4_mov_bx_ax_encoding import code_bytes  # noqa: E402

FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
SOURCES = {
    "baseline_low16": "void near probe(void) { _AX = (_AX * _BX); }",
    "explicit_unsigned_low16": (
        "void near probe(void) { "
        "_AX = ((unsigned int)_AX * (unsigned int)_BX); }"
    ),
    "unsigned_locals_low16": (
        "void near probe(void) { unsigned int a=(unsigned int)_AX; "
        "unsigned int b=(unsigned int)_BX; _AX=(a*b); }"
    ),
    "register_unsigned_locals_low16": (
        "void near probe(void) { register unsigned int a=(unsigned int)_AX; "
        "register unsigned int b=(unsigned int)_BX; _AX=(a*b); }"
    ),
    "unsigned_32bit_result": (
        "unsigned long near probe(void) { return "
        "((unsigned long)(unsigned int)_AX * "
        "(unsigned long)(unsigned int)_BX); }"
    ),
}
EXPECTED = {
    "baseline_low16": "f7ebc3",
    "explicit_unsigned_low16": "f7ebc3",
    "unsigned_locals_low16": "c80400008946fe895efc8b46fef76efcc9c3",
    "register_unsigned_locals_low16": "568bc88bf38bc1f7ee5ec3",
    "unsigned_32bit_result": "660fb7c0660fb7d3660fafc2660fa4c210c3",
}
TARGET_MUL = bytes.fromhex("f7e3")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-unsigned-mul-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    out = make_output(args.output_dir)

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    tcc_path = ROOT / tcc["path"]
    if sha(tcc_path.read_bytes()) != tcc["sha256"]:
        raise ValueError("active TCC identity drift")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )

    results: dict[str, object] = {}
    for name, body in SOURCES.items():
        work = out / name
        work.mkdir()
        source = work / "p.cpp"
        source.write_text(
            "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n"
            "#include <dos.h>\n"
            + body + "\n"
            "#pragma option -k.\n"
        )
        command = [
            "wine", str(runner), "-e", "-x", "tcc",
            *FLAGS, f"-I{ROOT / '_reference/ReC98'}", source.name,
        ]
        done = subprocess.run(
            command, cwd=work, env=env, capture_output=True, text=True, timeout=120
        )
        (work / "compile.log").write_text(done.stdout + done.stderr)
        obj = work / "p.obj"
        if done.returncode or not obj.is_file():
            raise RuntimeError(f"{name}: compile failed")
        code = code_bytes(obj)
        (work / "p.code").write_bytes(code)
        if code.hex() != EXPECTED[name]:
            raise ValueError(f"{name}: codegen drift: {code.hex()}")
        if TARGET_MUL in code:
            raise ValueError(f"{name}: unexpectedly emits target MUL BX")
        results[name] = {
            "source_sha256": sha(source.read_bytes()),
            "object_sha256": sha(obj.read_bytes()),
            "code_hex": code.hex(),
            "contains_target_mul_bx": False,
        }

    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J natural signedness/width surface for TH04 carpet MUL BX; no exact promotion",
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "flags": list(FLAGS),
        "target_opcode_hex": TARGET_MUL.hex(),
        "results": results,
        "conclusion": (
            "Direct low-16-bit multiplication and explicit unsigned casts canonicalize to F7 EB "
            "(IMUL BX). Unsigned locals instead select memory/register IMUL forms, while an "
            "observable full unsigned 32-bit product emits 386 MOVZX/IMUL/SHLD code. None of "
            "the tested natural type-correct forms emits target F7 E3 MUL BX."
        ),
        "limit": (
            "This closes the tested signedness/product-width source forms only. It does not prove "
            "original source language and does not authorize target-derived inline assembly."
        ),
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "result_count": len(results),
        "target_mul_emitted": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
