#!/usr/bin/env python3
"""Verify Linux and Windows x64 TH04 portable builds against one legal HDI."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


PORT_FILES = (
    "port64/CMakeLists.txt",
    "port64/application_state.cpp",
    "port64/application_state.hpp",
    "port64/bullet_geometry.cpp",
    "port64/bullet_geometry.hpp",
    "port64/contracts.cpp",
    "port64/main.cpp",
    "port64/menu_state.cpp",
    "port64/menu_state.hpp",
    "port64/mingw64-toolchain.cmake",
    "port64/random_lcg.cpp",
    "port64/random_lcg.hpp",
    "port64/random_ring.cpp",
    "port64/random_ring.hpp",
    "port64/smoke.py",
    "port64/verify.py",
    "port64/view.cpp",
    "port64/view.hpp",
    "src/main/bullet/group_types.hpp",
    "src/main/bullet/types.hpp",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest(root: Path) -> tuple[str, list[dict[str, object]]]:
    digest = hashlib.sha256()
    files: list[dict[str, object]] = []
    for relative_text in PORT_FILES:
        path = root / relative_text
        data = path.read_bytes()
        relative = relative_text.encode("utf-8")
        digest.update(len(relative).to_bytes(4, "little"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "little"))
        digest.update(data)
        files.append({
            "path": relative_text,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return digest.hexdigest(), files


def require_elf_x86_64(path: Path) -> None:
    data = path.read_bytes()[:64]
    if not (
        len(data) >= 20 and data[:4] == b"\x7fELF" and data[4] == 2 and
        int.from_bytes(data[18:20], "little") == 62
    ):
        raise ValueError(f"not an ELF64 x86-64 executable: {path}")


def require_pe_x86_64(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ValueError(f"not an MZ executable: {path}")
    header = int.from_bytes(data[0x3C:0x40], "little")
    if not (
        header <= len(data) - 26 and data[header:header + 4] == b"PE\0\0" and
        int.from_bytes(data[header + 4:header + 6], "little") == 0x8664 and
        int.from_bytes(data[header + 24:header + 26], "little") == 0x20B
    ):
        raise ValueError(f"not a PE32+ x86-64 executable: {path}")


def run(command: list[str], env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command, capture_output=True, text=True, check=True, env=env
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--linux-dir", type=Path, required=True)
    parser.add_argument("--windows-dir", type=Path, required=True)
    parser.add_argument("--hdi", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--windows-runner", default="wine")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    linux_dir = args.linux_dir.resolve()
    windows_dir = args.windows_dir.resolve()
    hdi = args.hdi.resolve()
    output = args.output.resolve()
    linux_main = linux_dir / "th04-port64"
    linux_contracts = linux_dir / "th04-port64-contracts"
    windows_main = windows_dir / "th04-port64.exe"
    windows_contracts = windows_dir / "th04-port64-contracts.exe"
    for path in (linux_main, linux_contracts):
        require_elf_x86_64(path)
    for path in (windows_main, windows_contracts):
        require_pe_x86_64(path)

    runner_env = os.environ.copy()
    runner_env.setdefault("WINEDEBUG", "-all")
    linux_contract_output = run([str(linux_contracts)])
    windows_contract_output = run(
        [args.windows_runner, str(windows_contracts)], env=runner_env
    )
    expected_contract_output = (
        "TH04 portable contracts: PASS pointer_bits=64 "
        "angle_bits=8 menu_state=OP handoff_state=OP_MAIN_MAINE "
        "randring=SHARED_OVERLAP lcg=PROCESS_LOCAL32"
    )
    if linux_contract_output != expected_contract_output:
        raise ValueError("Linux portable contract did not pass")
    if windows_contract_output != expected_contract_output:
        raise ValueError("Windows portable contract did not pass")

    smoke = root / "port64/smoke.py"
    linux_smoke_output = run([
        sys.executable, str(smoke), "--exe", str(linux_main),
        "--hdi", str(hdi),
    ])
    windows_smoke_output = run([
        sys.executable, str(smoke), "--runner", args.windows_runner,
        "--exe", str(windows_main), "--hdi", str(hdi),
    ], env=runner_env)
    if "port64 smoke: PASS" not in linux_smoke_output:
        raise ValueError("Linux resource smoke did not pass")
    if "port64 smoke: PASS" not in windows_smoke_output:
        raise ValueError("Windows resource smoke did not pass")

    manifest_sha256, source_files = source_manifest(root)
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "TH04 portable Linux/Windows x86-64 bring-up",
        "source_manifest_sha256": manifest_sha256,
        "source_files": source_files,
        "hdi_sha256": sha256(hdi),
        "products": {
            "linux": {
                "format": "ELF64 x86-64",
                "main_sha256": sha256(linux_main),
                "contracts_sha256": sha256(linux_contracts),
                "contract_output": linux_contract_output,
                "smoke_output": linux_smoke_output.splitlines(),
            },
            "windows": {
                "format": "PE32+ x86-64",
                "main_sha256": sha256(windows_main),
                "contracts_sha256": sha256(windows_contracts),
                "contract_output": windows_contract_output,
                "smoke_output": windows_smoke_output.splitlines(),
            },
        },
        "title_bmp_sha256": (
            "b52ea8615865bfc11945fbe23828b7c391d8424c998062a8abfb5d62b4b31d2a"
        ),
        "options_bmp_sha256": (
            "a064338b0cfb89f7e418a85ab6bc84a7ea5ef835e4ca995b68772e0aef368185"
        ),
        "passed": True,
        "limit": (
            "Resource decoding, main/options composition, deterministic OP menu-state "
            "transitions, resident process handoff, process-local LCG and shared "
            "random-ring contracts "
            "only; gameplay, audio, saved-data I/O and complete OP/MAIN/MAINE behavior "
            "are not yet ported."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "passed": True,
        "receipt": str(output),
        "source_manifest_sha256": manifest_sha256,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
