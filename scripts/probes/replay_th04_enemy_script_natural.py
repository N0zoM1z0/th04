#!/usr/bin/env python3
"""Compile the natural MAIN enemy VM and compare its complete switch topology."""

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

SOURCE = ROOT / "src/main/enemy/script_update.cpp"
SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
SNAPSHOT_SHA256 = "ae9105c56ff94cd6823ad365c03016a0106d923e0b0f653610cf1170e151a3e8"
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot_sha256() -> str:
    digest = hashlib.sha256()
    paths = sorted(SNAPSHOT.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("frozen compiler snapshot contains a symlink")
    for path in paths:
        if not path.is_file():
            continue
        data = path.read_bytes()
        digest.update(path.relative_to(SNAPSHOT).as_posix().encode() + b"\0")
        digest.update(str(len(data)).encode() + b"\0")
        digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def switch_topology(
    table: bytes,
) -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[int, ...], ...]]:
    if len(table) != 288:
        raise ValueError("switch table is not 144 words")
    groups: dict[int, list[int]] = {}
    for opcode in range(144):
        offset = int.from_bytes(table[opcode * 2:opcode * 2 + 2], "little")
        groups.setdefault(offset, []).append(opcode)
    partition = tuple(sorted(tuple(group) for group in groups.values()))
    physical_order = tuple(tuple(groups[offset]) for offset in sorted(groups))
    return partition, physical_order


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="enemy-vm-natural-", dir=parent))
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
    target_body = target[header_size + 0x155DD:header_size + 0x15C6D]
    if len(target_body) != 1680:
        raise ValueError("target VM physical extent changed")

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(s for s in surfaces if s["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise ValueError("active TCC identity failed")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    with tempfile.TemporaryDirectory(prefix="work-", dir=output) as scratch:
        work = Path(scratch) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        (work / "th04/escript.cpp").write_bytes(SOURCE.read_bytes())
        object_path = work / "obj/th04/escript.obj"
        command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, "th04/escript.cpp"]
        done = subprocess.run(command, cwd=work, env=env, capture_output=True,
                              text=True, timeout=120)
        (output / "compile.log").write_text(json.dumps(command) + "\n" +
                                            f"exit={done.returncode}\n" +
                                            done.stdout + done.stderr)
        if done.returncode or not object_path.is_file():
            raise ValueError("natural enemy VM compilation failed")
        obj = object_path.read_bytes()

    records = parse_omf(obj)
    groups = code_ledata(records, "B4M_UPDATE_TEXT")
    topology = [(start, end) for start, end, _, _ in groups]
    if topology != [(0, 1024), (1024, 1670)]:
        raise ValueError(f"natural VM CODE topology changed: {topology}")
    code = bytearray(1670)
    for start, end, record_number, _ in groups:
        code[start:end] = records[record_number - 1].data[3:]
    code = bytes(code)
    if len(code) != 1670 or len(code) == len(target_body):
        raise ValueError("natural VM size result changed")
    ignored = {index for start in (8, 12, 33, 40) for index in (start, start + 1)}
    if any(a != b for i, (a, b) in enumerate(zip(target_body[:42], code[:42]))
           if i not in ignored):
        raise ValueError("42-byte target VM entry opcode shape changed")
    target_groups, target_order = switch_topology(target_body[-288:])
    candidate_groups, candidate_order = switch_topology(code[-288:])
    if len(target_groups) != 49 or target_groups != candidate_groups:
        raise ValueError("144-case switch destination partition differs")
    if target_order != candidate_order:
        raise ValueError("49 switch destination groups differ in physical order")
    local_layout = bytes.fromhex("26 8A 45 03 88 46 FF C6 46 FE 04")
    target_layout_sites = [i for i in range(len(target_body)) if target_body.startswith(local_layout, i)]
    candidate_layout_sites = [i for i in range(len(code)) if code.startswith(local_layout, i)]
    if target_layout_sites != [76, 266] or candidate_layout_sites != target_layout_sites:
        raise ValueError("duration/advance BP local layout differs")
    (output / "enemy_vm.obj").write_bytes(obj)
    (output / "enemy_vm.code").write_bytes(code)

    receipt = {"schema_version": 1,
               "claim_scope": "MAIN B4M_UPDATE_TEXT 13A9:1B4D..21DC natural C++ VM; no exact promotion",
               "target_sha256": target_info["sha256"],
               "target_extent_file_offset": hex(header_size + 0x155DD),
               "target_extent_size": len(target_body),
               "target_extent_sha256": sha(target_body),
               "source_sha256": sha(SOURCE.read_bytes()),
               "snapshot_sha256": SNAPSHOT_SHA256,
               "tcc_sha256": tcc["sha256"], "runner_sha256": sha(runner.read_bytes()),
               "flags": list(FLAGS), "object_sha256": sha(obj),
               "omf_record_count": len(records),
               "omf_ledata": [[start, end, record_number] for start, end, record_number, _ in groups],
               "code_size": len(code), "code_sha256": sha(code),
               "target_executable_size": 1392,
               "candidate_executable_size": len(code) - 288,
               "switch_entries": 144, "switch_unique_destinations": len(target_groups),
               "switch_partition_equal": True,
               "switch_physical_group_order_equal": True,
               "duration_advance_bp_local_layout_equal": True,
               "entry_42_byte_opcode_shape_equal_after_four_word_mask": True,
               "result": "Natural C++ compiles to 1670 versus 1680 target bytes, with the same entry and BP-local shapes plus the same physical order for all 49 switch destination groups.",
               "limit": "The executable body is 10 bytes shorter; no linked raw, MAP, ordered relocation, runtime, or aggregate exactness gate passed."}
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
