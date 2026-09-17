#!/usr/bin/env python3
"""Probe natural TC4J far-to-near copy code for END_TEXT scroll helper.

The source is a small independent compiler control, not the 199-byte helper.
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
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

SOURCE = """#pragma option -zCEND_TEXT -zPmain_01
#include <dos.h>
#include <mem.h>
extern unsigned char tile_ring[2048];
extern unsigned int map_seg;
void near scroll_copy(unsigned int dst_off, unsigned int src_off) {
    __memcpy__(&tile_ring[dst_off], MK_FP(map_seg, src_off), 48);
}
"""
FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")


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
        output = Path(tempfile.mkdtemp(prefix="end-scroll-copy-", dir=parent))
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
        raise ValueError("reviewed target scroll helper changed")
    if target_body.count(bytes.fromhex("f3a5")) != 1:
        raise ValueError("target REP MOVSW count changed")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    compiler = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / compiler["path"]).read_bytes()) != compiler["sha256"]:
        raise ValueError("active TC4J identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    source_path = output / "SCROLLCP.CPP"
    source_path.write_text(SOURCE)
    os.utime(source_path, (946684800, 946684800))
    command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, source_path.name]
    done = subprocess.run(command, cwd=output, env=env, capture_output=True, text=True, timeout=120)
    (output / "compile.log").write_text(
        json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr
    )
    object_path = output / "scrollcp.obj"
    if done.returncode or not object_path.is_file():
        raise ValueError("TC4J scroll-copy control failed")
    obj = object_path.read_bytes()
    records = parse_omf(obj)
    groups = code_ledata(records, "END_TEXT")
    if len(groups) != 1 or groups[0][:2] != (0, 33):
        raise ValueError("unexpected END_TEXT control extent")
    code = records[groups[0][2] - 1].data[3:]
    if len(code) != 33 or code.count(bytes.fromhex("f3a5")) != 1:
        raise ValueError("natural copy did not emit one REP MOVSW")
    (output / "scrollcp.code").write_bytes(code)
    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN END_TEXT 0xB835 compiler control for 48-byte map-to-tile copy; no exact promotion",
        "target_sha256": target_info["sha256"],
        "target_body_sha256": sha(target_body),
        "target_load_extent": "0xB835..0xB8FB",
        "target_rep_movsw_load": "0xB8CB",
        "tcc_sha256": compiler["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "source_sha256": sha(SOURCE.encode()),
        "flags": list(FLAGS),
        "command": command,
        "object_sha256": sha(obj),
        "omf_record_count": len(records),
        "code_size": len(code),
        "code_sha256": sha(code),
        "code_hex": code.hex(),
        "result": "natural __memcpy__ emits one 24-word REP MOVSW with DS/ES exchange; setup order differs from the target",
        "limit": "No full semantic source, linked extent, MAP, ordered-relocation, or exact result for sub_B835.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
