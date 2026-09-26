#!/usr/bin/env python3
"""Cold-link the maintained 223-byte ZUN launcher selector stub."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/probes"))

from lib.omf import describe_omf, parse_omf  # noqa: E402
from replay_th04_zun_source_only import PAYLOAD, PAYLOAD_SHA256  # noqa: E402

SOURCE = ROOT / "src/zun/launcher/selector.asm"
START = 0x12F
SIZE = 0xDF
TARGET_SHA256 = "cda3d3f38031f14988d236cc6725109d2f162e65224509101ca55c6dcb05fcfc"
TASM = ROOT / ".analysis/toolchain/wineprefix/drive_c/TASM50/bin/TASM32.EXE"
TASM_SHA256 = "ba50fe547863b96242d98cff54cdf95ab268a8682395afad172eedbfc46c5b26"
TLINK = ROOT / ".analysis/toolchain/wineprefix/drive_c/TC4/BIN/TLINK.EXE"
TLINK_SHA256 = "e54f517766a3982dff404ff639b0f94e43c16e688dffb7e14b92df87a8580ad0"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def execute(args: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    log.write_text(json.dumps(args) + f"\nexit={result.returncode}\n" + result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"tool failed: {log}")


def build(label: str, output: Path, target: bytes) -> dict[str, object]:
    work = output / label
    work.mkdir()
    local = work / "SELECTOR.ASM"
    local.write_bytes(SOURCE.read_text(encoding="utf-8").encode("cp932"))
    os.utime(local, (946684800, 946684800))
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    execute(
        ["wine", r"C:\TASM50\BIN\TASM32.EXE", "/m", "/mx", "/kh32768",
         "SELECTOR.ASM,SELECTOR.OBJ,SELECTOR.LST"],
        work, work / "assemble.log", env,
    )
    obj = (work / "SELECTOR.OBJ").read_bytes()
    desc = describe_omf(obj)
    if not desc["valid"] or desc["module_name"] != "SELECTOR.ASM":
        raise RuntimeError(f"{label}: invalid OMF producer")
    if desc["dependency_paths"] != ["SELECTOR.ASM"]:
        raise RuntimeError(f"{label}: unexpected OMF dependency")
    records = parse_omf(obj)
    ledata = [record for record in records if record.record_type == 0xA0]
    fixupp = [record for record in records if record.record_type == 0x9C]
    if len(ledata) != 1 or len(fixupp) != 1:
        raise RuntimeError(f"{label}: OMF data/fixup ownership drift")
    raw = ledata[0].data
    if raw[:3] != bytes((1, 0, 1)) or len(raw[3:]) != SIZE:
        raise RuntimeError(f"{label}: selector LEDATA offset or size drift")
    execute(
        ["wine", str(RUNNER), "-e", "-x", "tlink", "-x", "-t", "SELECTOR.OBJ,SELECTOR.BIN"],
        work, work / "link.log", env,
    )
    binary = (work / "selector.bin").read_bytes()
    if len(binary) != SIZE or binary != target:
        raise RuntimeError(f"{label}: complete selector differs from target")
    return {
        "omf_sha256": sha(obj),
        "omf_size": len(obj),
        "ledata_offset": "0x100",
        "ledata_size": len(raw[3:]),
        "fixupp_record_count": len(fixupp),
        "selector_sha256": sha(binary),
        "selector_size": len(binary),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output must be a new direct child of .analysis/reconstruction/probes")
    preflight = subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    for path, digest in ((TASM, TASM_SHA256), (TLINK, TLINK_SHA256), (RUNNER, RUNNER_SHA256)):
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned tool identity drift: {path}")
    payload = PAYLOAD.read_bytes()
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("decoded target identity drift")
    target = payload[START:START + SIZE]
    if len(target) != SIZE or sha(target) != TARGET_SHA256:
        raise RuntimeError("target selector identity drift")
    source = SOURCE.read_text(encoding="utf-8")
    if any(token in source.lower() for token in ("incbin", "include", "db 0x", "db 90h")):
        raise RuntimeError("selector source acquired an opaque binary dependency")
    output.mkdir()
    builds = {label: build(label, output, target) for label in ("a", "b")}
    if builds["a"] != builds["b"]:
        raise RuntimeError("two cold selector objects or binaries differ")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target_extent": "th04-zun/com-payload/0x12F+0xDF",
        "target_sha256": TARGET_SHA256,
        "target_payload_sha256": PAYLOAD_SHA256,
        "source_sha256": sha(SOURCE.read_bytes()),
        "probe_sha256": sha(Path(__file__).read_bytes()),
        "preflight_stdout_sha256": sha(preflight.stdout.encode()),
        "toolchain_sha256": {"tasm32": TASM_SHA256, "tlink": TLINK_SHA256, "dos_runner": RUNNER_SHA256},
        "builds": builds,
        "complete_selector_raw_equal": True,
        "limit": "The adjacent generated directory and remaining ZUN components are separate; packed ZUN.COM exactness is not claimed.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes()), "selector_sha256": TARGET_SHA256}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
