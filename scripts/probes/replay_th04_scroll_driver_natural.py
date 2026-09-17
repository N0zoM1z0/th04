#!/usr/bin/env python3
"""Compile the maintained MAI_TEXT scroll driver without ReC98 source.

This is a source-presence and code-shape probe. The complete 96-byte target
owner still fails byte exactness and is not linked by this script.
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
SOURCE = ROOT / "src/main/scroll/driver.cpp"
FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
EXPECTED_CODE_SHA256 = "1e6ded75015254eaff10edf27d2dad38f73226b247cfcb6d5c3973aa6776008d"
PREFIX_SIZE = 46
PREFIX_SYMBOL_WORDS = (4, 12, 18, 22, 29, 36, 42)
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf, parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402


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
        output = Path(tempfile.mkdtemp(prefix="scroll-driver-natural-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    targets = tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
    target_info = next(item for item in targets if item["id"] == "th04-main")
    target = (ROOT / target_info["private_path"]).read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise ValueError("MAIN target identity failed")
    header = int.from_bytes(target[8:10], "little") * 16
    target_body = target[header + 0xCCD6:header + 0xCD36]
    if len(target_body) != 96 or sha(target_body) != "0115bd70a1f2a3a1e637dfd111e6125e355934e3fdae7d654fa2f0f3171ccb9e":
        raise ValueError("reviewed MAI_TEXT scroll-driver extent changed")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    compiler = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / compiler["path"]).read_bytes()) != compiler["sha256"]:
        raise ValueError("active TC4J identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    source = SOURCE.read_bytes()
    source_path = output / "DRIVER.CPP"
    source_path.write_bytes(source)
    os.utime(source_path, (946684800, 946684800))
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, source_path.name]
    done = subprocess.run(command, cwd=output, env=env, capture_output=True, text=True, timeout=120)
    (output / "compile.log").write_text(
        json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr
    )
    object_path = output / "driver.obj"
    if done.returncode or not object_path.is_file():
        raise ValueError("maintained scroll driver compilation failed")
    obj = object_path.read_bytes()
    omf = describe_omf(obj)
    if "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
        raise ValueError("unexpected scroll-driver OMF producer")
    records = parse_omf(obj)
    groups = code_ledata(records, "MAI_TEXT")
    if len(groups) != 1 or groups[0][:2] != (0, 105):
        raise ValueError("unexpected MAI_TEXT CODE extent")
    code = records[groups[0][2] - 1].data[3:]
    if sha(code) != EXPECTED_CODE_SHA256:
        raise ValueError("maintained scroll-driver code shape changed")
    target_prefix = bytearray(target_body[:PREFIX_SIZE])
    code_prefix = bytearray(code[:PREFIX_SIZE])
    for start in PREFIX_SYMBOL_WORDS:
        target_prefix[start:start + 2] = b"\0\0"
        code_prefix[start:start + 2] = b"\0\0"
    if target_prefix != code_prefix:
        raise ValueError("scroll-driver initial opcode prefix differs from target")
    if b"\x29\x06\0\0\x7d\x06" not in code or b"\x29\x06\x78\x42\x79\x06" not in target_body:
        raise ValueError("scroll-driver subtraction/branch diagnostic changed")
    (output / "driver.code").write_bytes(code)
    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN MAI_TEXT 0xCCD6..0xCD35 natural source compile; no exact promotion",
        "target_sha256": target_info["sha256"],
        "target_body_sha256": sha(target_body),
        "target_body_size": len(target_body),
        "source_sha256": sha(source),
        "tcc_sha256": compiler["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "flags": list(FLAGS),
        "command": command,
        "object_sha256": sha(obj),
        "omf_record_count": len(records),
        "code_size": len(code),
        "code_sha256": sha(code),
        "fixed_opcode_prefix_size": PREFIX_SIZE,
        "fixed_opcode_prefix_masked_words": list(PREFIX_SYMBOL_WORDS),
        "fixed_opcode_prefix_equal": True,
        "sub_memory_ax_observed": True,
        "target_jns_candidate_jnl": True,
        "result": "source-present, product-only TC4J compile; first 46 fixed opcode bytes agree and SUB memory,AX appears; complete CODE 105 versus target 96 with JNL versus target JNS",
        "limit": "Storage/helper symbols still need link ownership; full raw/MAP/ordered-relocation and cold aggregate gates do not pass.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
