#!/usr/bin/env python3
"""Compile maintained ZUN C++ units using only checked-in TH04 source/header text."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay_th04_zun_cfg_init import code

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
PAYLOAD = ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin"
PAYLOAD_SHA256 = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
EXPECTED_CODE = {
    "cfg_init": (152, "4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4"),
    "main": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
}
SOURCES = {
    "cfg_init": "src/zun/config/cfg_init.cpp",
    "main": "src/zun/resident/main.cpp",
}
LOCAL_INCLUDE = re.compile(rb'^\s*#\s*include\s+"(src/[^"\r\n]+)"', re.MULTILINE)
FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-mt", "-nobj/th04/")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_closure(root: Path, roots: tuple[str, ...]) -> tuple[str, ...]:
    """Hash and materialize every repository-local quoted include transitively."""

    source_root = (root / "src").resolve()
    pending = list(roots)
    visited: set[str] = set()
    while pending:
        relative = pending.pop()
        path = Path(relative)
        if path.is_absolute() or not path.parts or path.parts[0] != "src" or ".." in path.parts:
            raise ValueError(f"unsafe local include: {relative}")
        if relative in visited:
            continue
        source = (root / path).resolve()
        if not source.is_relative_to(source_root) or not source.is_file():
            raise ValueError(f"missing or escaping local include: {relative}")
        visited.add(relative)
        for match in LOCAL_INCLUDE.finditer(source.read_bytes()):
            pending.append(match.group(1).decode("ascii"))
    return tuple(sorted(visited))


def build(label: str, output: Path, inputs: dict[str, str]) -> dict[str, dict[str, object]]:
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    results: dict[str, dict[str, object]] = {}
    saved = output / label
    saved.mkdir()
    with tempfile.TemporaryDirectory(prefix=f"zun-source-{label}-", dir=output) as temporary:
        work = Path(temporary)
        (work / "obj/th04").mkdir(parents=True)
        for relative in inputs:
            source = ROOT / relative
            destination = work / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_text(encoding="utf-8").encode("cp932") if relative.endswith(".cpp") else source.read_bytes()
            destination.write_bytes(data)
            os.utime(destination, (946684800, 946684800))
        if {p.relative_to(work).as_posix() for p in work.rglob("*") if p.is_file()} != set(inputs):
            raise RuntimeError(f"{label}: materialized source has unexpected files")

        for name, relative in SOURCES.items():
            command = ["wine", str(RUNNER), "-e", "-x", "tcc", *FLAGS, relative]
            completed = subprocess.run(
                command, cwd=work, env=environment,
                capture_output=True, text=True, timeout=120,
            )
            log = saved / f"{name}.log"
            log.write_text(
                json.dumps(command) + f"\nexit={completed.returncode}\n"
                + completed.stdout + completed.stderr,
                encoding="utf-8",
            )
            obj = work / "obj/th04" / f"{name}.obj"
            if completed.returncode or not obj.is_file():
                raise RuntimeError(f"{label}/{name}: standalone TC4J compile failed: {log}")
            saved_obj = saved / f"{name}.obj"
            saved_obj.write_bytes(obj.read_bytes())
            compiled = code(saved_obj)  # Parses and checksum-validates OMF.
            (saved / f"{name}.code").write_bytes(compiled)
            size, digest = EXPECTED_CODE[name]
            if len(compiled) != size or sha(compiled) != digest:
                raise RuntimeError(f"{label}/{name}: standalone CODE differs from pinned baseline")
            results[name] = {
                "command": command,
                "object_sha256": sha(saved_obj.read_bytes()),
                "code_size": len(compiled),
                "code_sha256": sha(compiled),
                "log_sha256": sha(log.read_bytes()),
            }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or output.parent != (ROOT / ".analysis/reconstruction/probes").resolve():
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text(encoding="utf-8"))
    target_info = next(item for item in manifest["artifacts"] if item["id"] == "th04-zun")
    target = (ROOT / target_info["private_path"]).read_bytes()
    payload = PAYLOAD.read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if sha(payload) != PAYLOAD_SHA256 or len(payload[0xDCF:0xE67]) != 152 or len(payload[0xE67:0xF63]) != 252:
        raise RuntimeError("attested decoded ZUN payload changed")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text(encoding="utf-8"))["surfaces"]
    tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise RuntimeError("active TC4J identity changed")

    inputs = {
        relative: sha((ROOT / relative).read_bytes())
        for relative in source_closure(ROOT, tuple(SOURCES.values()))
    }
    output.mkdir(parents=True)
    a = build("a", output, inputs)
    b = build("b", output, inputs)
    if a != b:
        raise RuntimeError("cold source-only compiler rounds differ")
    receipt = {
        "schema_version": 1,
        "claim_scope": "ZUN cfg_init and _main C++ source/header compile closure; no standalone link or exact promotion",
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": PAYLOAD_SHA256,
        "source_input_sha256": inputs,
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(RUNNER.read_bytes()),
        "flags": list(FLAGS),
        "builds": {"a": a, "b": b},
        "result": (
            "both maintained ZUN C++ translation units compile from "
            f"{len(inputs)} checked-in TH04 source/header files alone"
        ),
        "limit": "The other ZUN components, libraries, TLINK inputs, and DIET product build are not yet checked in; natural _main remains 246 versus 252 target bytes.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    for name in SOURCES:
        print(f"{name}: {a[name]['code_size']} CODE bytes {a[name]['code_sha256']}")
    print(f"receipt: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
