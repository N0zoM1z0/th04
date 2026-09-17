#!/usr/bin/env python3
"""Compile the maintained END_TEXT tile-ring helper from checked-in source.

This is source-presence compiler evidence, not a linked or exact unit replay.
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
SOURCE = ROOT / "src/main/scroll/tile_ring_update.cpp"
FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
EXPECTED_CODE_SHA256 = "1e7f95a4ca1d8e3893bb3d169b422b8ea799a3af9d79f4a1a3f75fef81773509"
REP_MOVSW = bytes.fromhex("f3a5")
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
        output = Path(tempfile.mkdtemp(prefix="scroll-tile-ring-", dir=parent))
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
    target_body = target[header + 0xB835:header + 0xB8FC]
    if len(target_body) != 199 or sha(target_body) != "80f17b65eee2a5e9ce7338e727e4a00dcef4f641a8cdddfae03e08e2925922d8":
        raise ValueError("reviewed END_TEXT scroll helper changed")
    if target_body.count(REP_MOVSW) != 1:
        raise ValueError("target tile-row copy no longer has one REP MOVSW")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    compiler = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / compiler["path"]).read_bytes()) != compiler["sha256"]:
        raise ValueError("active TC4J identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    source = SOURCE.read_bytes()
    source_path = output / "TILERING.CPP"
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
    object_path = output / "tilering.obj"
    if done.returncode or not object_path.is_file():
        raise ValueError("maintained tile-ring helper compilation failed")
    obj = object_path.read_bytes()
    omf = describe_omf(obj)
    if "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
        raise ValueError("unexpected tile-ring OMF producer")
    records = parse_omf(obj)
    groups = code_ledata(records, "END_TEXT")
    if len(groups) != 1 or groups[0][:2] != (0, 215):
        raise ValueError("unexpected END_TEXT CODE extent")
    code = records[groups[0][2] - 1].data[3:]
    if sha(code) != EXPECTED_CODE_SHA256 or code.count(REP_MOVSW) != 1:
        raise ValueError("maintained tile-ring helper code shape changed")
    (output / "tilering.code").write_bytes(code)
    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN END_TEXT 0xB835..0xB8FB natural source compile; no exact promotion",
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
        "target_rep_movsw_count": target_body.count(REP_MOVSW),
        "candidate_rep_movsw_count": code.count(REP_MOVSW),
        "result": "source-present, product-only TC4J compile; candidate CODE 215 bytes versus target 199",
        "limit": "The full helper has unresolved segment/copy setup, BSS aliases, MAP, ordered relocation, and raw exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
