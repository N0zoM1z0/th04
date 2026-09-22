#!/usr/bin/env python3
"""Probe TC4J inline-helper effects on the remaining TH04 carpet codegen forms.

This is compiler-mechanism evidence only. Every candidate is natural C++:
no inline assembly, __emit__, target-byte injection, inert work, or product
source changes are used.
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
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import parse_omf  # noqa: E402

FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
PREFIX = "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n#include <dos.h>\n"
SUFFIX = "\n#pragma option -k.\n"

SOURCES = {
    # v417 controls plus inline boundaries.
    "mul_baseline": (
        "void near probe(void){ "
        "_AX=((unsigned int)_AX * (unsigned int)_BX); }"
    ),
    "mul_inline_return_regs": (
        "inline unsigned int mul_regs(void){ "
        "return ((unsigned int)_AX * (unsigned int)_BX); } "
        "void near probe(void){ _AX=mul_regs(); }"
    ),
    "mul_inline_write_regs": (
        "inline void mul_regs(void){ "
        "_AX=((unsigned int)_AX * (unsigned int)_BX); } "
        "void near probe(void){ mul_regs(); }"
    ),
    "mul_inline_args": (
        "inline unsigned int mul_u16(unsigned int a, unsigned int b){ "
        "return (a*b); } "
        "void near probe(void){ _AX=mul_u16(_AX,_BX); }"
    ),

    # v418 controls plus inline boundaries.
    "load_baseline": (
        "void near probe(void){ "
        "_AL=*reinterpret_cast<unsigned char near *>(_SI++); }"
    ),
    "load_inline_return_si": (
        "inline unsigned char load_si(void){ "
        "return *reinterpret_cast<unsigned char near *>(_SI++); } "
        "void near probe(void){ _AL=load_si(); }"
    ),
    "load_inline_write_si": (
        "inline void load_si(void){ "
        "_AL=*reinterpret_cast<unsigned char near *>(_SI++); } "
        "void near probe(void){ load_si(); }"
    ),
    "load_inline_ptr_arg": (
        "inline unsigned char load_p(unsigned char near *p){ return *p; } "
        "void near probe(void){ "
        "_AL=load_p(reinterpret_cast<unsigned char near *>(_SI)); _SI++; }"
    ),

    # v411 direction-sensitive controls plus the new inline boundary.
    "mov_si_inline_return_ax": (
        "inline unsigned int ax_value(void){ return _AX; } "
        "void near probe(void){ _SI=ax_value(); }"
    ),
    "mov_di_inline_return_dx": (
        "inline unsigned int dx_value(void){ return _DX; } "
        "void near probe(void){ _DI=dx_value(); }"
    ),
    "zero_dx_inline": (
        "inline void zero_dx(void){ _DX=0; } "
        "void near probe(void){ zero_dx(); }"
    ),
    "double_bx_inline": (
        "inline void double_bx(void){ _BX+=_BX; } "
        "void near probe(void){ double_bx(); }"
    ),
    "shift_di_inline": (
        "inline void shift_di(void){ _DI<<=1; } "
        "void near probe(void){ shift_di(); }"
    ),
}

TARGET_PATTERNS = {
    "mov_si_ax_89c6": bytes.fromhex("89c6"),
    "mov_di_dx_89d7": bytes.fromhex("89d7"),
    "xor_dx_31d2": bytes.fromhex("31d2"),
    "add_bx_01db": bytes.fromhex("01db"),
    "shl_di_d1e7": bytes.fromhex("d1e7"),
    "mul_bx_f7e3": bytes.fromhex("f7e3"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def omf_index(data: bytes, pos: int) -> tuple[int, int]:
    first = data[pos]
    if first < 0x80:
        return first, pos + 1
    return ((first & 0x7F) << 8) | data[pos + 1], pos + 2


def main_code_bytes(path: Path) -> bytes:
    """Return LEDATA from the first CPROBE_TEXT segment, excluding helper COMDATs."""
    chunks: list[tuple[int, bytes]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type != 0xA0:
            continue
        seg, pos = omf_index(record.data, 0)
        off = int.from_bytes(record.data[pos : pos + 2], "little")
        pos += 2
        if seg == 1:
            chunks.append((off, record.data[pos:]))
    if not chunks:
        raise ValueError(f"no primary CODE LEDATA in {path}")
    size = max(off + len(payload) for off, payload in chunks)
    out = bytearray(size)
    for off, payload in chunks:
        out[off : off + len(payload)] = payload
    return bytes(out)


def make_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="tc4-carpet-inline-v503-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
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
        raise ValueError("active TC4J identity drift")

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
        source.write_text(PREFIX + body + SUFFIX)
        command = [
            "wine", str(runner), "-e", "-x", "tcc",
            *FLAGS, f"-I{ROOT / '_reference/ReC98'}", "p.cpp",
        ]
        done = subprocess.run(
            command,
            cwd=work,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        (work / "compile.log").write_text(done.stdout + done.stderr)
        obj = work / "p.obj"
        if done.returncode or not obj.is_file():
            raise RuntimeError(
                f"{name}: compile failed: {done.returncode}\n{done.stdout}{done.stderr}"
            )

        code = main_code_bytes(obj)
        code_path = work / "p.code"
        code_path.write_bytes(code)
        dis = subprocess.run(
            ["ndisasm", "-b16", str(code_path)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        (work / "p.ndis").write_text(dis)

        hits = {
            key: pattern in code for key, pattern in TARGET_PATTERNS.items()
        }
        results[name] = {
            "source_sha256": sha(source.read_bytes()),
            "code_sha256": sha(code),
            "code_hex": code.hex(),
            "code_size": len(code),
            "has_call": any(
                " call " in (" " + line.lower() + " ") for line in dis.splitlines()
            ),
            "has_lodsb": any(
                "lodsb" in line.lower() for line in dis.splitlines()
            ),
            "target_pattern_hits": hits,
            "disassembly": dis.splitlines(),
        }

    baseline_pairs = (
        ("mul_baseline", "mul_inline_return_regs"),
        ("mul_baseline", "mul_inline_write_regs"),
        ("load_baseline", "load_inline_return_si"),
        ("load_baseline", "load_inline_write_si"),
    )
    same_as_baseline = {
        f"{a}__{b}": results[a]["code_hex"] == results[b]["code_hex"]
        for a, b in baseline_pairs
    }
    target_hits = {
        name: [
            key
            for key, hit in value["target_pattern_hits"].items()
            if hit
        ]
        for name, value in results.items()
    }
    lodsb_hits = [name for name, value in results.items() if value["has_lodsb"]]
    call_hits = [name for name, value in results.items() if value["has_call"]]

    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J inline-helper surface for TH04 carpet residual codegen",
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "probe_sha256": sha(Path(__file__).read_bytes()),
        "flags": list(FLAGS),
        "results": results,
        "same_as_baseline": same_as_baseline,
        "target_pattern_hits": target_hits,
        "lodsb_hits": lodsb_hits,
        "call_hits": call_hits,
        "limit": (
            "Compiler mechanism evidence only. Matching codegen would still require "
            "independent source provenance and exact replay; this probe itself grants "
            "no source ownership or exactness credit."
        ),
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "receipt": str(path),
                "receipt_sha256": sha(path.read_bytes()),
                "same_as_baseline": same_as_baseline,
                "target_pattern_hits": target_hits,
                "lodsb_hits": lodsb_hits,
                "call_hits": call_hits,
                "summary": {
                    key: {
                        "code_hex": value["code_hex"],
                        "size": value["code_size"],
                        "call": value["has_call"],
                        "lodsb": value["has_lodsb"],
                    }
                    for key, value in results.items()
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
