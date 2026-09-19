#!/usr/bin/env python3
"""Test bounded TC4J source-level ES-save forms for the MAIN aim helper."""

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

SOURCE = ROOT / "src/main/enemy/script_helpers.cpp"
SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
SNAPSHOT_SHA256 = "ae9105c56ff94cd6823ad365c03016a0106d923e0b0f653610cf1170e151a3e8"
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")
AIM_DECL = 'extern "C" void near enemy_aim_at_player(void)'
ENEMY_LINE = "    register enemy_t near *enemy = enemy_cur;"
VECTOR_LINE = "    vector2_near(enemy->pos.velocity, enemy->angle, enemy->speed.v);"
VARIANTS = {
    "baseline": ("", "", ""),
    "auto_unsigned": ("", "    unsigned saved_es = _ES;\n", "\n    _ES = saved_es;"),
    "register_unsigned": ("", "    register unsigned saved_es = _ES;\n", "\n    _ES = saved_es;"),
    "saveregs": ("__saveregs ", "", ""),
}
EXPECTED = {
    "baseline": (140, 49, "a87d0d359ff328753bba9879ec0ef2bfa4a79340616b2db1fdd017c67a671b54"),
    "auto_unsigned": (147, 56, "9253b5077559c9760c81804d6aefdbda6ef893122b5923a4f3a7f76ae0e20b7f"),
    "register_unsigned": (146, 55, "2a412819f71e7baa61e4b1b190306fd89191499c02af3026c7f99cc7e0df176a"),
    "saveregs": (158, 67, "9a2c9b0b514217e8972e6c2ded127888be4a3f218bf535b78b560474de7beb47"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot_sha256() -> str:
    digest = hashlib.sha256()
    paths = sorted(SNAPSHOT.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("frozen compiler snapshot contains a symlink")
    for path in paths:
        if path.is_file():
            data = path.read_bytes()
            digest.update(path.relative_to(SNAPSHOT).as_posix().encode() + b"\0")
            digest.update(str(len(data)).encode() + b"\0")
            digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def public_offsets(records: list) -> list[int]:
    return [
        int.from_bytes(record.data[-3:-1], "little")
        for record in records
        if record.name == "PUBDEF"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        parent = private / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="enemy-es-save-codegen-", dir=parent))
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
    target_aim = target[header_size + 0x155AA:header_size + 0x155DD]
    if len(target_aim) != 51 or sha(target_aim) != "92972f0ba6797be9a7e5a3d16573dc6bb424093f7e0bfb26b8b7b803d3913571":
        raise ValueError("target aim helper identity failed")
    if snapshot_sha256() != SNAPSHOT_SHA256:
        raise ValueError("frozen compiler snapshot identity failed")
    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(s for s in surfaces if s["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise ValueError("active TCC identity failed")

    source = SOURCE.read_text()
    aim_start = source.index(AIM_DECL)
    prefix, aim = source[:aim_start], source[aim_start:]
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    results = {}
    with tempfile.TemporaryDirectory(prefix="work-", dir=output) as scratch:
        work = Path(scratch) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        source_path = work / "th04/enes.cpp"
        object_path = work / "obj/th04/enes.obj"
        command = ["wine", str(runner), "-e", "-x", "tcc", *FLAGS, "th04/enes.cpp"]
        for name, (decl_prefix, before, after) in VARIANTS.items():
            variant_aim = aim.replace(AIM_DECL, f'extern "C" {decl_prefix}void near enemy_aim_at_player(void)', 1)
            variant_aim = variant_aim.replace(ENEMY_LINE, ENEMY_LINE + "\n" + before, 1)
            variant_aim = variant_aim.replace(VECTOR_LINE, VECTOR_LINE + after, 1)
            variant_source = prefix + variant_aim
            source_path.write_text(variant_source)
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
            code = bytearray(groups[-1][1])
            for start, end, record_number, _ in groups:
                code[start:end] = records[record_number - 1].data[3:]
            starts = public_offsets(records)
            if starts[:3] != [0, 67, 91]:
                raise ValueError(f"{name}: helper public offsets changed")
            aim_code = bytes(code[starts[2]:])
            expected_total, expected_size, expected_sha = EXPECTED[name]
            if (len(code), len(aim_code), sha(aim_code)) != (expected_total, expected_size, expected_sha):
                raise ValueError(f"{name}: compiler result changed")
            (output / f"{name}.code").write_bytes(aim_code)
            results[name] = {"source_sha256": sha(variant_source.encode()),
                             "object_sha256": sha(obj), "total_code_size": len(code),
                             "aim_size": len(aim_code), "aim_sha256": sha(aim_code)}

    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN enemy aim helper source-level ES preservation; compiler probe only",
        "target_sha256": target_info["sha256"],
        "target_aim_sha256": sha(target_aim),
        "snapshot_sha256": SNAPSHOT_SHA256,
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "flags": list(FLAGS),
        "variants": results,
        "result": (
            "Baseline omits ES preservation; unsigned saves use BP memory or DI, and "
            "__saveregs saves every general and segment register. None emits the target "
            "51-byte helper or its isolated PUSH ES / POP ES pair."
        ),
        "limit": "This bounded matrix does not prove original source syntax and gives no exact credit.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
