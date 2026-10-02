#!/usr/bin/env python3
"""Attest a CPU exception debugger for the unchanged primary DOSBox-X."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tomllib

from build_th04_cpu_fault_emulator import PRIVATE, ROOT, sha

BUILD_ID = "e4b8aef97aab79c506f019e4409fa3b72a137fb4"
SCRIPT = Path(__file__).with_name("th04_primary_cpu_fault.gdb")


def build_id(path: Path) -> str:
    output = subprocess.check_output(["readelf", "-n", str(path)], text=True,
                                     stderr=subprocess.DEVNULL)
    values = re.findall(r"Build ID: ([0-9a-f]+)", output)
    if len(values) != 1:
        raise ValueError("ELF has no unique build ID")
    return values[0]


def attest_debugger(path: Path) -> dict:
    if not path.resolve().is_relative_to(PRIVATE):
        raise ValueError("CPU debugger receipt must be private")
    record = json.loads(path.read_text())
    primary = tomllib.loads((ROOT / "config/runtime.toml").read_text())["primary"]
    debug = Path(record["debug_file"]).resolve()
    binary = Path(record["binary"]).resolve()
    gdb = Path(record["gdb"]).resolve()
    if (not debug.is_relative_to(PRIVATE) or record["build_id"] != BUILD_ID
            or record["binary_sha256"] != primary["binary_sha256"]
            or sha(binary) != primary["binary_sha256"]
            or sha(debug) != record["debug_file_sha256"]
            or build_id(binary) != BUILD_ID or build_id(debug) != BUILD_ID
            or sha(gdb) != record["gdb_sha256"] or sha(SCRIPT) != record["script_sha256"]):
        raise ValueError("primary CPU debugger identity drift")
    return record


def command_prefix(record: dict) -> list[str]:
    return [record["gdb"], "-nx", "--batch", "-iex", "set debuginfod enabled off",
            "-x", str(SCRIPT), "--args"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--debug-file", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        parser.error("use a new private debugger directory")
    primary = tomllib.loads((ROOT / "config/runtime.toml").read_text())["primary"]
    binary = Path(shutil.which(primary["command"])).resolve()
    gdb = Path(shutil.which("gdb")).resolve()
    debug = args.debug_file.resolve()
    record = dict(scope="pinned primary emulator under CPU exception debugger; not gameplay acceptance",
                  binary=str(binary), binary_sha256=sha(binary), build_id=BUILD_ID,
                  debug_file=str(debug), debug_file_sha256=sha(debug),
                  debug_source_url="https://ddebs.ubuntu.com/pool/universe/d/dosbox-x/"
                                   "dosbox-x-dbgsym_2024.03.01+dfsg-1build2_amd64.ddeb",
                  gdb=str(gdb), gdb_sha256=sha(gdb), script_sha256=sha(SCRIPT),
                  gdb_version=subprocess.check_output([str(gdb), "--version"], text=True).splitlines()[0])
    output.mkdir(parents=True)
    path = output / "receipt.json"
    path.write_text(json.dumps(record, indent=2) + "\n")
    attest_debugger(path)
    print(json.dumps(dict(receipt=str(path), binary_sha256=record["binary_sha256"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
