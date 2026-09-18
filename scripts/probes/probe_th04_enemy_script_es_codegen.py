#!/usr/bin/env python3
"""Test natural TC4J producers for the MAIN enemy-script ES:DI entry."""

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
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes"), *sys.path]
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
SNAPSHOT_SHA256 = "ae9105c56ff94cd6823ad365c03016a0106d923e0b0f653610cf1170e151a3e8"
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")
HEADER = """#pragma option -zCB4M_UPDATE_TEXT -zPmain_03
#include <dos.h>
#include "th04/main/enemy/enemy.hpp"
#include "th04/formats/std.hpp"
extern "C" unsigned char near enemy_script_update(void)
{
    register enemy_t near *enemy = enemy_cur;
"""
TAIL = """    switch(*instr) {
    case 0: enemy->flag = EF_KILLED; return 1;
    case 1: enemy->angle = instr[1]; return 0;
    case 2: enemy->speed.v = instr[1]; return 0;
    default: return 0;
    }
}
"""
VARIANTS = {
    "ordinary_far": """    register unsigned char far *instr = reinterpret_cast<unsigned char far *>(
        MK_FP(FP_SEG(std_seg), (unsigned)enemy->script + enemy->script_ip)
    );
""",
    "es_combined": """    _ES = FP_SEG(std_seg);
    register unsigned char __es *instr = reinterpret_cast<unsigned char __es *>(
        (unsigned)enemy->script + enemy->script_ip
    );
""",
    "es_split": """    _ES = FP_SEG(std_seg);
    register unsigned char __es *instr = reinterpret_cast<unsigned char __es *>(enemy->script);
    instr += enemy->script_ip;
""",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot_sha256() -> str:
    digest = hashlib.sha256()
    paths = sorted(SNAPSHOT.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("frozen snapshot contains a symlink")
    for path in paths:
        if not path.is_file():
            continue
        data = path.read_bytes()
        digest.update(path.relative_to(SNAPSHOT).as_posix().encode() + b"\0")
        digest.update(str(len(data)).encode() + b"\0")
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def entry_matches(candidate: bytes, target: bytes) -> bool:
    if len(candidate) < 24:
        return False
    # Target ENTER 4 precedes the register setup; these tiny probes need no locals.
    left, right = target[4:25], candidate[3:24]
    ignored = {4, 5, 8, 9}  # DS symbol operands before link placement.
    return all(a == b for i, (a, b) in enumerate(zip(left, right)) if i not in ignored)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="enemy-es-codegen-", dir=parent))
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
    if header_size != 6144 or snapshot_sha256() != SNAPSHOT_SHA256:
        raise ValueError("MZ header or compiler snapshot identity failed")
    entry = target[header_size + 0x155DD:header_size + 0x15607]
    if len(entry) != 42 or entry[:4] != bytes.fromhex("C8 04 00 00"):
        raise ValueError("target dispatcher entry changed")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(s for s in surfaces if s["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise ValueError("active TCC identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")

    results = {}
    with tempfile.TemporaryDirectory(prefix="work-", dir=output) as scratch:
        work = Path(scratch) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        source_path = work / "th04/esvm.cpp"
        object_path = work / "obj/th04/esvm.obj"
        command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, "th04/esvm.cpp"]
        for name, fragment in VARIANTS.items():
            source = HEADER + fragment + TAIL
            source_path.write_text(source)
            object_path.unlink(missing_ok=True)
            done = subprocess.run(command, cwd=work, env=env, capture_output=True,
                                  text=True, timeout=120)
            (output / f"{name}.log").write_text(json.dumps(command) + "\n" +
                                                  f"exit={done.returncode}\n" +
                                                  done.stdout + done.stderr)
            if done.returncode or not object_path.is_file():
                raise ValueError(f"{name}: TCC compilation failed")
            obj = object_path.read_bytes()
            records = parse_omf(obj)
            groups = code_ledata(records, "B4M_UPDATE_TEXT")
            if len(groups) != 1 or groups[0][0] != 0:
                raise ValueError(f"{name}: unexpected CODE topology")
            code = records[groups[0][2] - 1].data[3:]
            (output / f"{name}.code").write_bytes(code)
            results[name] = {"source_sha256": sha(source.encode()),
                             "object_sha256": sha(obj), "code_sha256": sha(code),
                             "code_size": len(code), "entry_21_byte_shape": entry_matches(code, entry)}
    if [results[name]["code_size"] for name in VARIANTS] != [84, 73, 71]:
        raise ValueError("compiler variant sizes changed")
    if [results[name]["entry_21_byte_shape"] for name in VARIANTS] != [False, False, True]:
        raise ValueError("ES pointer producer result changed")

    receipt = {"schema_version": 1,
               "claim_scope": "MAIN B4M_UPDATE_TEXT 13A9:1B4D dispatcher entry; compiler shape only",
               "target_sha256": target_info["sha256"], "target_entry_sha256": sha(entry),
               "target_entry_file_offset": hex(header_size + 0x155DD),
               "snapshot_sha256": SNAPSHOT_SHA256,
               "tcc_sha256": tcc["sha256"], "runner_sha256": sha(runner.read_bytes()),
               "flags": list(FLAGS), "variants": results,
               "result": "Only a register __es pointer with split pointer addition reproduces the 21-byte SI/ES/DI entry sequence after masking two DS addresses.",
               "limit": "The probe uses a three-case toy switch. It does not reproduce the 1392-byte dispatcher, 144-word table, linked bytes, or relocations."}
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
