#!/usr/bin/env python3
"""Check whether TC4J -y changes DIALOG_TEXT FIXUPP batching without code drift."""

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
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v213-dialog-reloc-diagnostic-001/a/source"
TARGET = ROOT / ".analysis/targets/th04/main.exe"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
TARGET_SHA256 = "077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b"
SNAPSHOT_MAIN_SHA256 = "5cb1f31d2a9ae67646763e55c6165320e9d0b7d84439370f7dab7c7c6b1b876a"
BASELINE_OBJECT_SHA256 = "15bf3a323b07d735ec0abae6b5c1bc48992038d83f6a4f5044853f28d0fc4e7c"
BASELINE_CODE_SHA256 = "0ebf658670b0b9800526b86c95185d41d06bbf65e30c0b338d0a02ed754a6d7a"
LINE_INFO_CODE_SHA256 = "3600f56beca306abd13e3336869ce7aab6677b09996d38b01e780dbfdcfafd0e"
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4",
         "-ml", "-DBINARY='M'", "-nobj/th04/")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def describe(path: Path) -> tuple[dict[str, object], bytes]:
    raw = path.read_bytes()
    records = parse_omf(raw)
    chunks = code_ledata(records, "DIALOG_TEXT")
    if [(start, end) for start, end, _, _ in chunks] != [(0, 1020), (1020, 2028)]:
        raise RuntimeError("DIALOG_TEXT OMF LEDATA boundary changed")
    code = bytearray(2028)
    for start, end, number, _ in chunks:
        code[start:end] = records[number - 1].data[3:]
    result = {
        "object_sha256": sha(raw),
        "code_size": len(code),
        "code_sha256": sha(code),
        "ledata_extents": [[start, end] for start, end, _, _ in chunks],
        "fixupp_record_count": len(chunks),
        "linnum_record_count": sum(record.record_type == 0x94 for record in records),
        "omf_record_count": len(records),
    }
    return result, bytes(code)


def round_build(label: str, output: Path) -> dict[str, object]:
    saved = output / label
    saved.mkdir()
    environment = os.environ.copy()
    environment.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
                       WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    with tempfile.TemporaryDirectory(prefix=f"dialog-line-{label}-", dir=output) as temporary:
        work = Path(temporary) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        object_path = work / "obj/th04/dialog.obj"
        results: dict[str, object] = {}
        codes = {}
        for name, extra in (("baseline", ()), ("line_info", ("-y",))):
            object_path.unlink(missing_ok=True)
            command = ["wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS,
                       *extra, "th04/dialog.cpp"]
            completed = subprocess.run(command, cwd=work, env=environment,
                                       capture_output=True, text=True, timeout=120)
            (saved / f"{name}.log").write_text(
                json.dumps(command) + f"\nexit={completed.returncode}\n"
                + completed.stdout + completed.stderr, encoding="utf-8")
            if completed.returncode or not object_path.is_file():
                raise RuntimeError(f"{label}/{name}: TC4J compile failed")
            (saved / f"{name}.obj").write_bytes(object_path.read_bytes())
            results[name], codes[name] = describe(object_path)
            (saved / f"{name}.code").write_bytes(codes[name])
        baseline, line_info = results["baseline"], results["line_info"]
        if (baseline["object_sha256"], baseline["code_sha256"]) != (
            BASELINE_OBJECT_SHA256, BASELINE_CODE_SHA256
        ):
            raise RuntimeError(f"{label}: baseline does not reproduce v213 dialog")
        if line_info["code_sha256"] != LINE_INFO_CODE_SHA256:
            raise RuntimeError(f"{label}: -y dialog CODE changed")
        differences = [index for index, (a, b) in enumerate(
            zip(codes["baseline"], codes["line_info"])) if a != b]
        if len(differences) != 20 or (min(differences), max(differences)) != (0x790, 0x7A6):
            raise RuntimeError(f"{label}: unexpected -y code drift")
        if (baseline["linnum_record_count"], line_info["linnum_record_count"]) != (0, 3):
            raise RuntimeError(f"{label}: -y line-number records changed")
        return {"baseline": baseline, "line_info": line_info,
                "different_byte_count": len(differences),
                "first_difference": differences[0], "last_difference": differences[-1]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or output.parent != (ROOT / ".analysis/reconstruction/probes").resolve():
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")
    if sha(TARGET.read_bytes()) != TARGET_SHA256:
        raise RuntimeError("pinned MAIN target changed")
    if sha((SNAPSHOT / "bin/th04/main.exe").read_bytes()) != SNAPSHOT_MAIN_SHA256:
        raise RuntimeError("v213 snapshot identity changed")
    toolchain = tomllib.loads((ROOT / "config/toolchain.toml").read_text())
    tcc = next(item for item in toolchain["surfaces"] if item["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise RuntimeError("active TC4J identity changed")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    output.mkdir(parents=True)
    rounds = {label: round_build(label, output) for label in ("a", "b")}
    if rounds["a"] != rounds["b"]:
        raise RuntimeError("cold dialog compiler rounds differ")
    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN DIALOG_TEXT -y line-number OMF batching control; no exact claim",
        "target_sha256": TARGET_SHA256,
        "tcc_sha256": tcc["sha256"],
        "snapshot_main_sha256": SNAPSHOT_MAIN_SHA256,
        "flags": list(FLAGS),
        "rounds": rounds,
        "result": "-y adds three LINNUM records but keeps two LEDATA/FIXUPP groups and changes 20 DIALOG_TEXT code bytes",
        "limit": "The target object remains unavailable; no source, relocation, or exact-state change.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("-y: same two FIXUPP groups; 20 code bytes differ; A/B deterministic")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
