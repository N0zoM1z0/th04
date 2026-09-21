#!/usr/bin/env python3
"""Cold-compile TH04 stages.cpp and inspect natural carpet register directions.

This probe tests ordinary C++/pseudo-register statements in their real carpet
function context. The surrounding ReC98 scaffold is compiler-routing evidence
only; target-derived inline-assembly bytes receive no reconstruction credit.
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
import tarfile
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
REFERENCE = ROOT / "_reference/ReC98"
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import digest_file  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")
EXPECTED_CODE_SIZE = 0x204
EXPECTED_CODE_SHA256 = "12d1963ccc57bda0e55d40765cb0ca6b28acdf2dcb330e0513103588312b0c28"
CHECKS = (
    ("si_from_ax", 0x0F, 0x10299, "89c6", "8bf0"),
    ("scale_bx", 0x18, 0x102A2, "01db", "03db"),
    ("image_ptr", 0x1F, 0x102A9, "89c3", "8bd8"),
    ("tile_x_init", 0x21, 0x102AB, "31d2", "33d2"),
    ("tile_index_move", 0x2B, 0x102B5, "89d7", "8bfa"),
    ("dirty_index_move", 0x3E, 0x102C8, "89d7", "8bfa"),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="carpet-context-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output directory must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def stages_code(obj: Path) -> tuple[bytes, dict[str, object]]:
    raw = obj.read_bytes()
    records = parse_omf(raw)
    groups = code_ledata(records, "STAGES_TEXT")
    if not groups or groups[0][0] != 0:
        raise ValueError("missing STAGES_TEXT from offset zero")
    code = bytearray(groups[-1][1])
    cursor = 0
    for start, end, record_number, _ in groups:
        if start != cursor:
            raise ValueError("non-contiguous STAGES_TEXT")
        code[start:end] = records[record_number - 1].data[3:]
        cursor = end
    desc = describe_omf(raw)
    if not desc["valid"] or desc["translator_comments"] != ["TC86 Borland C++ 4.02"]:
        raise ValueError("unexpected TC86 object identity")
    return bytes(code), desc


def build(label: str, output: Path, revision: str, runner: Path, env: dict[str, str]) -> dict[str, object]:
    root = output / label
    source = root / "source"
    source.mkdir(parents=True)
    archive = root / "source.tar"
    subprocess.run(
        ["git", "archive", "--format=tar", f"--output={archive}", revision],
        cwd=REFERENCE, check=True,
    )
    with tarfile.open(archive) as bundle:
        bundle.extractall(source, filter="data")
    (source / "obj/th04").mkdir(parents=True)
    command = [
        "wine", str(runner), "-e", "-x", "tcc", *FLAGS,
        "th04/main/stage/stages.cpp",
    ]
    done = subprocess.run(command, cwd=source, env=env, capture_output=True, text=True, timeout=120)
    (root / "compile.log").write_text(done.stdout + done.stderr)
    obj = source / "obj/th04/stages.obj"
    if done.returncode or not obj.is_file():
        raise RuntimeError(f"{label}: stages.cpp compile failed")
    code, desc = stages_code(obj)
    if len(code) != EXPECTED_CODE_SIZE or sha(code) != EXPECTED_CODE_SHA256:
        raise ValueError(f"{label}: STAGES_TEXT code drift")
    return {
        "object_sha256": sha(obj.read_bytes()),
        "object_dependency_normalized_sha256": desc["dependency_timestamp_normalized_sha256"],
        "stages_text_size": len(code),
        "stages_text_sha256": sha(code),
        "code": code,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    output = new_output(args.output_dir)

    manifest = tomllib.loads((ROOT / "config/th04_main_exact_units.toml").read_text())
    revision = str(manifest["reference_revision"])
    resolved = subprocess.check_output(["git", "rev-parse", revision], cwd=REFERENCE, text=True).strip()
    if resolved != revision:
        raise ValueError("pinned ReC98 revision unavailable")
    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    if digest_file(ROOT / tcc["path"]) != tcc["sha256"]:
        raise ValueError("active TCC identity drift")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    builds = {label: build(label, output, revision, runner, env) for label in ("a", "b")}
    if builds["a"]["stages_text_sha256"] != builds["b"]["stages_text_sha256"]:
        raise ValueError("A/B STAGES_TEXT differs")
    if builds["a"]["object_dependency_normalized_sha256"] != builds["b"]["object_dependency_normalized_sha256"]:
        raise ValueError("A/B normalized object differs")

    target_cfg = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_row = next(item for item in target_cfg["artifacts"] if item["id"] == "th04-main")
    target_path = ROOT / target_row["private_path"]
    target = target_path.read_bytes()
    if len(target) != target_row["size"] or sha(target) != target_row["sha256"]:
        raise ValueError("TH04 MAIN target identity drift")

    checks = []
    code = builds["a"].pop("code")
    builds["b"].pop("code")
    for name, object_offset, file_offset, target_hex, candidate_hex in CHECKS:
        actual_target = target[file_offset:file_offset + 2].hex()
        actual_candidate = code[object_offset:object_offset + 2].hex()
        if actual_target != target_hex or actual_candidate != candidate_hex:
            raise ValueError(f"{name}: opcode observation drift")
        checks.append({
            "name": name,
            "object_offset": hex(object_offset),
            "target_file_offset": hex(file_offset),
            "target_hex": actual_target,
            "candidate_hex": actual_candidate,
            "raw_exact": False,
        })

    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 carpet natural register statements in full scaffold context; no exact promotion",
        "reference_revision": revision,
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": digest_file(runner),
        "flags": list(FLAGS),
        "builds": builds,
        "checks": checks,
        "conclusion": "Six ordinary C++/pseudo-register statements remain nonexact even in the complete carpet function context: target 89 C6/01 DB/89 C3/31 D2/89 D7/89 D7 versus TC4J 8B F0/03 DB/8B D8/33 D2/8B FA/8B FA.",
        "limit": "The surrounding ReC98 inline assembly is decompilation routing evidence only. This probe grants no credit to those instructions and does not prove original source language.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes()), "checks": checks}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
