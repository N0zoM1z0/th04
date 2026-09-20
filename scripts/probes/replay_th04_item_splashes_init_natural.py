#!/usr/bin/env python3
"""Compile the maintained natural item_splashes_init() source.

This is source-presence/compiler-negative evidence, not an exact linked replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/main/item/splashes_init.cpp"
FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-I.")
TARGET_LOAD = 0x13F16
TARGET_SIZE = 0x1A
EXPECTED_NATURAL_SIZE = 0x1C
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
        output = Path(tempfile.mkdtemp(prefix="item-splashes-init-", dir=parent))
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
    target_body = target[header + TARGET_LOAD:header + TARGET_LOAD + TARGET_SIZE]
    if len(target_body) != TARGET_SIZE:
        raise ValueError("target item_splashes_init extent changed")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    compiler = next(item for item in surfaces if item["id"] == "active-tcc")
    compiler_path = ROOT / compiler["path"]
    if sha(compiler_path.read_bytes()) != compiler["sha256"]:
        raise ValueError("active TC4J identity failed")

    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    source = SOURCE.read_bytes()

    with tempfile.TemporaryDirectory(prefix="item-splash-src-", dir=output) as td:
        work = Path(td) / "source"
        shutil.copytree(ROOT / "_reference/ReC98", work, symlinks=True)
        source_path = work / "th04/iteminit.cpp"
        source_path.write_bytes(source)
        os.utime(source_path, (946684800, 946684800))
        (work / "obj/th04").mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env.update(
            WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
            WINEDEBUG="-all",
            MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
        )
        command = [
            "wine", str(runner), "-e", "-x", "tcc",
            *FLAGS, "-nobj/th04/", "th04/iteminit.cpp",
        ]
        done = subprocess.run(
            command, cwd=work, env=env, capture_output=True, text=True, timeout=120
        )
        (output / "compile.log").write_text(
            json.dumps(command) + f"\nexit={done.returncode}\n"
            + done.stdout + "\n" + done.stderr
        )
        object_path = work / "obj/th04/iteminit.obj"
        if done.returncode or not object_path.is_file():
            raise ValueError("maintained item_splashes_init compilation failed")
        obj = object_path.read_bytes()
        shutil.copy2(object_path, output / "iteminit.obj")

    omf = describe_omf(obj)
    if "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
        raise ValueError("unexpected item_splashes_init OMF producer")
    records = parse_omf(obj)
    groups = code_ledata(records, "IT_SPL_U_TEXT")
    if len(groups) != 1 or groups[0][:2] != (0, EXPECTED_NATURAL_SIZE):
        raise ValueError("unexpected maintained item_splashes_init CODE extent")
    code = records[groups[0][2] - 1].data[3:]
    if len(code) != EXPECTED_NATURAL_SIZE:
        raise ValueError("maintained item_splashes_init code size changed")
    (output / "iteminit.code").write_bytes(code)

    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN item_splashes_init natural source compile; no exact promotion",
        "target_sha256": target_info["sha256"],
        "target_body_sha256": sha(target_body),
        "target_body_size": len(target_body),
        "source_sha256": sha(source),
        "tcc_sha256": compiler["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "flags": list(FLAGS),
        "command": command,
        "object_sha256": sha(obj),
        "object_normalized_sha256": omf["dependency_timestamp_normalized_sha256"],
        "code_size": len(code),
        "code_sha256": sha(code),
        "target_size": len(target_body),
        "result": "source-present natural C++; CODE 28 bytes versus target 26",
        "limit": (
            "TC4J lowers memset to a FAR library call rather than the target inline "
            "REP STOSW sequence. No exact credit is claimed."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
