#!/usr/bin/env python3
"""Compile the three natural MAIN enemy-script helpers without exact promotion."""

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
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/probes"))
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

SOURCE = ROOT / "src/main/enemy/script_helpers.cpp"
SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
SNAPSHOT_SHA256 = "ae9105c56ff94cd6823ad365c03016a0106d923e0b0f653610cf1170e151a3e8"
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")
HELPERS = (
    ("position", 0x1554F, 67, 0, 61),
    ("velocity", 0x15592, 24, 61, 24),
    ("aim", 0x155AA, 51, 85, 49),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot_sha256() -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in SNAPSHOT.rglob("*") if path.is_file())
    if any(path.is_symlink() for path in SNAPSHOT.rglob("*")):
        raise ValueError("snapshot contains unpinned symlinks")
    for path in files:
        data = path.read_bytes()
        digest.update(path.relative_to(SNAPSHOT).as_posix().encode() + b"\0")
        digest.update(str(len(data)).encode() + b"\0")
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def masked_equal(left: bytes, right: bytes, words: tuple[int, ...]) -> bool:
    if len(left) != len(right):
        return False
    ignored = {index for start in words for index in (start, start + 1)}
    return all(a == b for i, (a, b) in enumerate(zip(left, right)) if i not in ignored)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="enemy-helpers-", dir=parent))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(a for a in manifest["artifacts"] if a["id"] == "th04-main")
    target = (ROOT / target_info["private_path"]).read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise ValueError("MAIN target identity failed")
    header_size = int.from_bytes(target[8:10], "little") * 16
    if header_size != 6144:
        raise ValueError("MAIN MZ header changed")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(s for s in surfaces if s["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise ValueError("active TCC identity failed")
    if snapshot_sha256() != SNAPSHOT_SHA256:
        raise ValueError("frozen ReC98 compiler snapshot identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")

    with tempfile.TemporaryDirectory(prefix="work-", dir=output) as scratch:
        work = Path(scratch) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        (work / "th04/enscript.cpp").write_bytes(SOURCE.read_bytes())
        object_path = work / "obj/th04/enscript.obj"
        command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, "th04/enscript.cpp"]
        done = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=120)
        (output / "compile.log").write_text(json.dumps(command) + "\n" +
                                            f"exit={done.returncode}\n" + done.stdout + done.stderr)
        if done.returncode or not object_path.is_file():
            raise ValueError("TCC helper compilation failed")
        obj = object_path.read_bytes()
    records = parse_omf(obj)
    groups = code_ledata(records, "B4M_UPDATE_TEXT")
    if len(groups) != 1 or groups[0][:2] != (0, 134):
        raise ValueError("unexpected B4M_UPDATE_TEXT LEDATA topology")
    code = records[groups[0][2] - 1].data[3:]
    if len(code) != 134:
        raise ValueError("unexpected helper CODE length")
    (output / "helpers.obj").write_bytes(obj)
    (output / "helpers.code").write_bytes(code)

    results = {}
    for name, load_start, target_size, code_start, code_size in HELPERS:
        target_body = target[header_size + load_start:header_size + load_start + target_size]
        candidate = code[code_start:code_start + code_size]
        if len(target_body) != target_size or len(candidate) != code_size:
            raise ValueError(f"{name} extent changed")
        results[name] = {"target_size": target_size, "target_sha256": sha(target_body),
                         "candidate_size": code_size, "candidate_sha256": sha(candidate)}
    position = target[header_size + 0x1554F:header_size + 0x15592]
    velocity = target[header_size + 0x15592:header_size + 0x155AA]
    aim = target[header_size + 0x155AA:header_size + 0x155DD]
    anchor = bytes.fromhex("80 7C 20 00")
    pos_suffix_target = position[position.index(anchor):]
    pos_suffix_code = code[code.index(anchor):61]
    if not masked_equal(pos_suffix_target[:-2], pos_suffix_code[:-2], (36,)):
        raise ValueError("position helper body changed beyond the BP/local producer")
    if not masked_equal(velocity, code[61:85], (6, 19)):
        raise ValueError("velocity helper instructions changed")
    if aim[8] != 0x06 or aim[-4] != 0x07:
        raise ValueError("target aim helper ES save pair changed")
    aim_without_es = aim[:8] + aim[9:-4] + aim[-3:]
    if not masked_equal(aim_without_es, code[85:134], (6, 9, 16, 23, 44)):
        raise ValueError("aim helper differs beyond ES save and address fixups")

    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN B4M_UPDATE_TEXT 13A9:1ABF..1B4C; three helper compiler producers, no exact promotion",
        "target_sha256": target_info["sha256"],
        "source_sha256": sha(SOURCE.read_bytes()),
        "snapshot_path": str(SNAPSHOT.relative_to(ROOT)), "snapshot_sha256": SNAPSHOT_SHA256,
        "tcc_sha256": tcc["sha256"], "runner_sha256": sha(runner.read_bytes()),
        "flags": list(FLAGS), "object_sha256": sha(obj), "code_sha256": sha(code),
        "omf_record_count": len(records), "omf_ledata": [[a, b, n] for a, b, n, _ in groups],
        "helpers": results,
        "structural_result": {
            "position": "44-byte body suffix agrees apart from the absolute global word; target uses a 2-byte BP local and LEAVE, candidate uses SI and POP BP",
            "velocity": "24 instructions bytes agree after masking one absolute global word and one unresolved near CALL word",
            "aim": "49 instructions bytes agree after masking five address words and removing the target ES save pair",
        },
        "limit": "No linked raw, MAP, relocation, aggregate, or runtime exactness gate passed.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "result": receipt["structural_result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
