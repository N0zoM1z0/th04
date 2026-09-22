#!/usr/bin/env python3
"""Probe whether TC4J inline pseudo-register returns alter AX->BX encoding.

Compiler-mechanism evidence only. All variants are natural C++ and contain no
inline assembly, __emit__, target bytes, or product-source changes.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path.insert(0, str(ROOT / "scripts/probes"))
from probe_tc4_mov_bx_ax_encoding import code_bytes  # noqa: E402

FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
PREFIX = "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n#include <dos.h>\n"
SUFFIX = "\n#pragma option -k.\n"
SOURCES = {
    "baseline": "void near probe(void){ _BX = _AX; }",
    "inline_return_ax": (
        "inline unsigned int ax_result(void){ return _AX; } "
        "void near probe(void){ _BX = ax_result(); }"
    ),
    "inline_return_ax_local": (
        "inline unsigned int ax_result(void){ return _AX; } "
        "void near probe(void){ unsigned int r=ax_result(); _BX=r; }"
    ),
    "inline_interrupt_return": (
        "inline unsigned int int21_result(void){ geninterrupt(0x21); return _AX; } "
        "void near probe(void){ _BX = int21_result(); }"
    ),
    "inline_open_return": (
        "inline unsigned int open_result(void){ _AX=0x3D00; geninterrupt(0x21); return _AX; } "
        "void near probe(void){ _BX = open_result(); }"
    ),
    "inline_open_dx_return": (
        "inline unsigned int open_result(unsigned int dx){ _DX=dx; _AX=0x3D00; "
        "geninterrupt(0x21); return _AX; } "
        "void near probe(void){ _BX = open_result(_DX); }"
    ),
}

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    if args.output_dir is None:
        out = Path(tempfile.mkdtemp(prefix="tc4-inline-return-v501-", dir=PRIVATE / "reconstruction/probes"))
    else:
        out = args.output_dir.resolve()
        if out.exists() or not out.is_relative_to(PRIVATE):
            raise ValueError("output directory must be new and below .analysis")
        out.mkdir(parents=True)
    cfg = tomllib.loads((ROOT / "config/toolchain.toml").read_text())
    tcc = next(x for x in cfg["surfaces"] if x["id"] == "active-tcc")
    tcc_path = ROOT / tcc["path"]
    if sha(tcc_path.read_bytes()) != tcc["sha256"]:
        raise ValueError("active TC4J identity drift")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"), WINEDEBUG="-all",
               MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    results = {}
    for name, body in SOURCES.items():
        work = out / name
        work.mkdir()
        src = work / "p.cpp"
        src.write_text(PREFIX + body + SUFFIX)
        cmd = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS,
               f"-I{ROOT / '_reference/ReC98'}", "p.cpp"]
        done = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=120)
        (work / "compile.log").write_text(done.stdout + done.stderr)
        obj = work / "p.obj"
        if done.returncode or not obj.is_file():
            raise RuntimeError(f"{name}: compile failed: {done.stdout}{done.stderr}")
        code = code_bytes(obj)
        (work / "p.code").write_bytes(code)
        dis = subprocess.run(["ndisasm", "-b16", str(work / "p.code")],
                             check=True, capture_output=True, text=True).stdout
        (work / "p.ndis").write_text(dis)
        results[name] = {
            "source_sha256": sha(src.read_bytes()),
            "code_sha256": sha(code),
            "code_hex": code.hex(),
            "contains_89c3": bytes.fromhex("89c3") in code,
            "contains_8bd8": bytes.fromhex("8bd8") in code,
            "contains_call": any(" call " in (" " + line.lower() + " ") for line in dis.splitlines()),
            "disassembly": dis.splitlines(),
        }
    if bytes.fromhex(results["baseline"]["code_hex"]) != bytes.fromhex("8bd8c3"):
        raise ValueError("baseline drift")
    receipt = {
        "schema_version": 1,
        "claim_scope": "TC4J inline pseudo-register return AX-to-BX codegen surface",
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "probe_sha256": sha(Path(__file__).read_bytes()),
        "flags": list(FLAGS),
        "results": results,
        "any_natural_89c3": any(v["contains_89c3"] for k,v in results.items() if k != "baseline"),
        "limit": "Compiler mechanism evidence only; no product-source or exactness credit.",
    }
    rp = out / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp.read_bytes()),
        "summary": {k: {
            "code_hex": v["code_hex"],
            "89c3": v["contains_89c3"],
            "8bd8": v["contains_8bd8"],
            "call": v["contains_call"],
        } for k,v in results.items()},
        "any_natural_89c3": receipt["any_natural_89c3"],
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
