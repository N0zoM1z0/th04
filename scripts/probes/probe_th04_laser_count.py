#!/usr/bin/env python3
"""Test whether natural length expressions change TC4J's laser copy setup."""

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
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

FLAGS = ("-c", "-ml", "-3", "-O", "-Z", "-d", "-b-")
TARGET_CODE = bytes.fromhex("55 8b ec 56 57 b9 0c 00 1e 07 be d8 42 8b 7e 04 f3 a5 5f 5e 5d c2 02 00")
PREFIX = "#include <mem.h>\nstruct S { unsigned char bytes[24]; };\nextern S src;\n"
VARIANTS = {
    "F1": "void near pascal f(S near &dst) { __memcpy__(&dst, &src, sizeof(S)); }",
    "F2": "void near pascal f(S near &dst) { register unsigned int n = sizeof(S); __memcpy__(&dst, &src, n); }",
    "F3": "void near pascal f(S near &dst) { register unsigned int words = 12; __memcpy__(&dst, &src, words * 2); }",
    "F4": "void near pascal f(S near &dst) { const unsigned int n = sizeof(S); __memcpy__(&dst, &src, n); }",
}
EXPECTED_SIZES = {"F1": 24, "F2": 32, "F3": 36, "F4": 30}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="laser-count-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(item for item in manifest["artifacts"] if item["id"] == "th04-main")
    target = (ROOT / target_info["private_path"]).read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise ValueError("MAIN target identity failed")
    if target[0x175A5:0x175A5 + 24] != TARGET_CODE:
        raise ValueError("reviewed thick-laser helper changed")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    compiler = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / compiler["path"]).read_bytes()) != compiler["sha256"]:
        raise ValueError("active TC4J identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    results = {}
    for name, body in VARIANTS.items():
        source = (PREFIX + body + "\n").encode()
        (output / f"{name}.CPP").write_bytes(source)
        command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, f"{name}.CPP"]
        done = subprocess.run(command, cwd=output, env=env, capture_output=True,
                              text=True, timeout=120)
        (output / f"{name}.log").write_text(json.dumps(command) +
                                              f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr)
        object_path = output / f"{name.lower()}.obj"
        if done.returncode or not object_path.is_file():
            raise ValueError(f"{name}: compiler failed")
        obj = object_path.read_bytes()
        omf = describe_omf(obj)
        if not omf["valid"] or "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
            raise ValueError(f"{name}: invalid or unexpected OMF")
        records = parse_omf(obj)
        groups = code_ledata(records, name + "_TEXT")
        if len(groups) != 1 or groups[0][:2] != (0, EXPECTED_SIZES[name]):
            raise ValueError(f"{name}: unexpected CODE extent")
        code = records[groups[0][2] - 1].data[3:]
        if code.count(bytes.fromhex("f3 a5")) != 1 or code == TARGET_CODE:
            raise ValueError(f"{name}: unexpected copy instruction shape")
        (output / f"{name}.code").write_bytes(code)
        results[name] = {"source_sha256": sha(source), "object_sha256": sha(obj),
                         "code_sha256": sha(code), "code_size": len(code),
                         "code_hex": code.hex(" ")}
    receipt = {"schema_version": 1,
               "claim_scope": "MAIN B4M_UPDATE_TEXT 0x15DA5..0x15DBC synthetic copy-length producers; no exact promotion",
               "target_sha256": target_info["sha256"], "target_helper_sha256": sha(TARGET_CODE),
               "tcc_sha256": compiler["sha256"], "runner_sha256": sha(runner.read_bytes()),
               "flags": list(FLAGS), "variants": results,
               "result": "length expression forms preserve REP MOVSW but none emits target 24-byte setup; register lengths expand CODE",
               "limit": "Synthetic S[24] control; full thick-laser TU, linked MAP, relocations, and raw exactness remain open."}
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
