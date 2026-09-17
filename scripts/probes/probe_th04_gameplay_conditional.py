#!/usr/bin/env python3
"""Probe TC4J zero-distance jumps for two MAIN gameplay conditionals."""

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
sys.path.insert(0, str(ROOT / "scripts/probes"))
from probe_th04_gameplay_ternary import extract_code, FLAGS, CURRENT_MASK_CODE_SHA256

SOURCE = ROOT / "src/main/core/gameplay_loop.cpp"
SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
TARGET = ROOT / ".analysis/targets/th04/main.exe"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
TARGET_SHA256 = "077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b"
SOURCE_SHA256 = "eaaa9fc4bfb4c3c75600c5961701b38410ca4c993dea5ece41174257dbe1588f"

PALETTE_IF = """        if(palette_changed) {
            palette_show();
            palette_changed = false;
        }"""
PALETTE_CONDITIONAL = """        palette_changed
            ? (void)(palette_show(), palette_changed = false)
            : (void)0;"""
PALETTE_EMPTY_ELSE = """        if(palette_changed) {
            palette_show();
            palette_changed = false;
        } else {
        }"""
RAISE_IF = """        if((stage_frame % frames_per_playperf_raise) == 0) {
            playperf_raise(1);
        }"""
RAISE_CONDITIONAL = """        ((stage_frame % frames_per_playperf_raise) == 0)
            ? (void)playperf_raise(1)
            : (void)0;"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def variants(source: str) -> dict[str, str]:
    if source.count(PALETTE_IF) != 1 or source.count(RAISE_IF) != 1:
        raise RuntimeError("maintained gameplay conditionals changed")
    return {
        "current": source,
        "palette_empty_else": source.replace(PALETTE_IF, PALETTE_EMPTY_ELSE),
        "palette_conditional": source.replace(PALETTE_IF, PALETTE_CONDITIONAL),
        "raise_conditional": source.replace(RAISE_IF, RAISE_CONDITIONAL),
        "both_conditional": source.replace(PALETTE_IF, PALETTE_CONDITIONAL).replace(
            RAISE_IF, RAISE_CONDITIONAL
        ),
    }


def compile_round(label: str, sources: dict[str, str], output: Path) -> dict[str, dict[str, object]]:
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    results: dict[str, dict[str, object]] = {}
    round_output = output / label
    round_output.mkdir()
    with tempfile.TemporaryDirectory(prefix=f"{label}-", dir=output) as temporary:
        work = Path(temporary) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        source_path = work / "th04/looptry.cpp"
        object_path = work / "obj/th04/looptry.obj"
        for name, source in sources.items():
            source_path.write_text(source, encoding="utf-8")
            os.utime(source_path, (946684800, 946684800))
            object_path.unlink(missing_ok=True)
            command = ["wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS, "th04/looptry.cpp"]
            completed = subprocess.run(
                command, cwd=work, env=environment, capture_output=True,
                text=True, timeout=120,
            )
            log = round_output / f"{name}.log"
            log.write_text(
                f"command={command!r}\nexit={completed.returncode}\n"
                + completed.stdout + completed.stderr,
                encoding="utf-8",
            )
            if completed.returncode or not object_path.is_file():
                raise RuntimeError(f"{label}/{name}: TC4J compilation failed: {log}")
            obj = object_path.read_bytes()
            code, record_count = extract_code(obj)
            (round_output / f"{name}.obj").write_bytes(obj)
            (round_output / f"{name}.code").write_bytes(code)
            results[name] = {
                "source_sha256": sha(source.encode("utf-8")),
                "object_sha256": sha(obj),
                "code_size": len(code),
                "code_sha256": sha(code),
                "omf_record_count": record_count,
                "eb00_offsets": [
                    i for i in range(len(code) - 1) if code[i:i + 2] == b"\xEB\x00"
                ],
                "mov_dx_ax_count": code.count(b"\x8B\xD0"),
                "wide_mask_count": code.count(b"\x25\x0F\x00"),
                "compile_log_sha256": sha(log.read_bytes()),
            }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    allowed_parent = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != allowed_parent:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    target = TARGET.read_bytes()
    source = SOURCE.read_text(encoding="utf-8")
    if sha(target) != TARGET_SHA256 or sha(source.encode("utf-8")) != SOURCE_SHA256:
        raise RuntimeError("pinned MAIN target or maintained gameplay source changed")
    toolchain = tomllib.loads((ROOT / "config/toolchain.toml").read_text())
    tcc = next(item for item in toolchain["surfaces"] if item["id"] == "active-tcc")
    if sha((ROOT / str(tcc["path"])).read_bytes()) != tcc["sha256"]:
        raise RuntimeError("active TC4J identity changed")
    if sha((SNAPSHOT / "bin/th04/main.exe").read_bytes()) != (
        "1c1bcec509b775a6fa994d403d573ede75e74b8781ac5f0db06eb124d5fbae21"
    ):
        raise RuntimeError("v214 cold source snapshot changed")
    target_header = int.from_bytes(target[8:10], "little") * 16
    target_body = target[target_header + 0xAB88:target_header + 0xAD03]
    target_eb00 = [
        i for i in range(len(target_body) - 1) if target_body[i:i + 2] == b"\xEB\x00"
    ]
    if len(target_body) != 379 or target_eb00 != [0xF0, 0x16A]:
        raise RuntimeError("target gameplay branch extent changed")

    output.mkdir(parents=True)
    sources = variants(source)
    a = compile_round("a", sources, output)
    b = compile_round("b", sources, output)
    if a != b:
        raise RuntimeError("isolated compiler rounds differ")
    expected = {
        "current": (373, []),
        "palette_empty_else": (373, []),
        "palette_conditional": (375, [0xF0]),
        "raise_conditional": (375, [0x166]),
        "both_conditional": (377, [0xF0, 0x168]),
    }
    for name, (size, jumps) in expected.items():
        if (a[name]["code_size"], a[name]["eb00_offsets"]) != (size, jumps):
            raise RuntimeError(f"{name}: compiler shape changed")
    if a["current"]["code_sha256"] != CURRENT_MASK_CODE_SHA256:
        raise RuntimeError("maintained gameplay compiler baseline changed")
    if a["palette_empty_else"]["code_sha256"] != CURRENT_MASK_CODE_SHA256:
        raise RuntimeError("empty else unexpectedly changes compiler CODE")
    if a["both_conditional"]["mov_dx_ax_count"] or a["both_conditional"]["wide_mask_count"] != 1:
        raise RuntimeError("remaining target DX-copy or wide-mask observation changed")

    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN DEMO_TEXT conditional-expression EB 00 producer; compiler diagnostic only",
        "target_sha256": TARGET_SHA256,
        "target_extent": "DEMO_TEXT 0AAF:0098; load 0xAB88..0xAD02; file 0xC388..0xC502",
        "target_body_sha256": sha(target_body),
        "target_eb00_offsets": target_eb00,
        "source_sha256": SOURCE_SHA256,
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(RUNNER.read_bytes()),
        "flags": list(FLAGS),
        "variants_a": a,
        "variants_b": b,
        "result": "two natural conditional expressions produce both target EB 00 positions, leaving a 377/379-byte compiler candidate without target MOV DX,AX; source provenance unproved",
        "limit": "(void)0 arms are no-op source; this experiment does not justify adding them to maintained source or claim linked exactness",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"receipt: {receipt_path}")
    for name, item in a.items():
        print(f"{name}: CODE={item['code_size']} EB00={item['eb00_offsets']} DX={item['mov_dx_ax_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
