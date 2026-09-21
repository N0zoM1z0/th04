#!/usr/bin/env python3
"""Probe hidden Borland-style optimizer suboptions on pinned Turbo C++ 4.0J.

This is compiler-surface evidence only. It does not change the accepted
compiler profile or grant exactness to any reconstruction unit.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_FLAGS = ("-c", "-ml", "-b-", "-3", "-Z", "-d")
OPTIONS = ("-O", "-Ob", "-Oc", "-Oe", "-Og", "-Oi", "-Ol", "-Om", "-Op", "-Os", "-Ot", "-Ov", "-O1", "-O2", "-Ox", "-Od")
SOURCE = (
    "#pragma option -zCPROBE_TEXT -zPmain_01 -k-\n"
    "#include <dos.h>\n"
    "void near probe(void) { _CX=6; L: _ES=_DX; "
    "*reinterpret_cast<unsigned long __es *>(_DI)=_EAX; _DI+=8; "
    "if(--_CX) goto L; }\n"
    "#pragma option -k.\n"
)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        out = Path(tempfile.mkdtemp(prefix="tc4-opt-surface-", dir=parent))
    else:
        out = args.output_dir.resolve()
        if out.exists() or not out.is_relative_to(private):
            ap.error("output directory must be new and below .analysis")
        out.mkdir(parents=True)

    cfg = tomllib.loads((ROOT / "config/toolchain.toml").read_text())
    surfaces = cfg["surfaces"]
    compiler = next(x for x in surfaces if x["id"] == "active-tcc")
    tcc = ROOT / compiler["path"]
    if sha(tcc.read_bytes()) != compiler["sha256"]:
        raise ValueError("active TC4J identity failed")
    tc4_bin = tcc.parent
    bcc = sorted(p.name for p in tc4_bin.iterdir() if p.is_file() and p.name.upper().startswith("BCC") and p.suffix.upper() == ".EXE")

    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"), WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    source = out / "p.cpp"
    source.write_text(SOURCE)
    results = []
    for opt in OPTIONS:
        obj = out / "p.obj"
        if obj.exists():
            obj.unlink()
        cmd = ["wine", str(runner), "-e", "-x", "tcc", *BASE_FLAGS, opt, f"-I{ROOT / '_reference/ReC98'}", source.name]
        done = subprocess.run(cmd, cwd=out, env=env, capture_output=True, text=True, timeout=120)
        obj_bytes = obj.read_bytes() if obj.is_file() else b""
        results.append({
            "option": opt,
            "exit_code": done.returncode,
            "object_present": bool(obj_bytes),
            "object_sha256": sha(obj_bytes) if obj_bytes else None,
            "stdout_stderr": (done.stdout + done.stderr).strip(),
        })
    accepted = [x["option"] for x in results if x["exit_code"] == 0 and x["object_present"]]
    if accepted != ["-O"]:
        raise ValueError(f"unexpected accepted optimizer surface: {accepted}")
    receipt = {
        "schema_version": 1,
        "claim_scope": "Turbo C++ 4.0J optimizer suboption surface",
        "tcc_sha256": compiler["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "source_sha256": sha(source.read_bytes()),
        "base_flags": list(BASE_FLAGS),
        "installed_bcc_executables": bcc,
        "results": results,
        "accepted_options": accepted,
        "conclusion": "Pinned Turbo C++ 4.0J accepts -O but rejects the tested Borland-style -O* optimizer suboptions; the active TC4 BIN contains no BCC.EXE.",
        "limit": "This closes only the tested optimizer-driver surface. It does not prove that every possible source form is incapable of producing any blocked opcode shape.",
    }
    rp = out / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(rp), "receipt_sha256": sha(rp.read_bytes()), "accepted": accepted, "bcc": bcc}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
