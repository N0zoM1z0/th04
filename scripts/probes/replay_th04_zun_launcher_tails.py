#!/usr/bin/env python3
"""Cold-link the two short ZUN launcher tail stubs from maintained ASM."""

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
from replay_th04_zun_selector import (  # noqa: E402
    RUNNER, RUNNER_SHA256, TASM, TASM_SHA256, TLINK, TLINK_SHA256, sha,
)

STUBS = (
    ("MOVEUP", "src/zun/launcher/selector_moveup.asm", 0x3422, 0x8,
     "a580939da3b518b3001c1a4ff48fd9860511eddc239d702c6e13e41ac9125b00"),
    ("CUSTOM", "src/zun/launcher/customization_stub.asm", 0x342A, 0x44,
     "0982f4fa42c53b1df727fd10f64ef5ae2515bbdc90fb1a595209b8dc943d95fd"),
)


def execute(args: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    done = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    log.write_text(json.dumps(args) + f"\nexit={done.returncode}\n" + done.stdout + done.stderr)
    if done.returncode:
        raise RuntimeError(f"tool failed: {log}")


def build(label: str, output: Path, targets: dict[str, bytes]) -> dict[str, dict[str, object]]:
    work = output / label
    work.mkdir()
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    results = {}
    for name, source, _start, size, _target_sha in STUBS:
        local = work / f"{name}.ASM"
        local.write_bytes((ROOT / source).read_text(encoding="utf-8").encode("cp932"))
        os.utime(local, (946684800, 946684800))
        execute(
            ["wine", r"C:\TASM50\BIN\TASM32.EXE", "/m", "/mx", "/kh32768",
             f"{name}.ASM,{name}.OBJ,{name}.LST"],
            work, work / f"{name}.assemble.log", env,
        )
        obj = (work / f"{name}.OBJ").read_bytes()
        desc = describe_omf(obj)
        if not desc["valid"] or desc["module_name"] != f"{name}.ASM":
            raise RuntimeError(f"{label}/{name}: invalid OMF")
        if desc["dependency_paths"] != [f"{name}.ASM"]:
            raise RuntimeError(f"{label}/{name}: unexpected OMF dependency")
        records = parse_omf(obj)
        ledata = [record for record in records if record.record_type == 0xA0]
        fixupp = [record for record in records if record.record_type == 0x9C]
        if len(ledata) != 1 or ledata[0].data[:3] != bytes((1, 0, 1)):
            raise RuntimeError(f"{label}/{name}: wrong COM LEDATA origin")
        if len(ledata[0].data[3:]) != size or fixupp:
            raise RuntimeError(f"{label}/{name}: wrong emitting extent or unexpected fixup")
        execute(
            ["wine", str(RUNNER), "-e", "-x", "tlink", "-x", "-t",
             f"{name}.OBJ,{name}.BIN"],
            work, work / f"{name}.link.log", env,
        )
        binary = (work / f"{name.lower()}.bin").read_bytes()
        if len(binary) != size or binary != targets[name]:
            raise RuntimeError(f"{label}/{name}: complete raw target mismatch")
        results[name] = {
            "omf_sha256": sha(obj),
            "omf_size": len(obj),
            "ledata_offset": "0x100",
            "ledata_size": size,
            "fixupp_record_count": len(fixupp),
            "binary_sha256": sha(binary),
        }
    return results


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
    targets = {}
    sources = {}
    for name, source, start, size, digest in STUBS:
        targets[name] = payload[start:start + size]
        if len(targets[name]) != size or sha(targets[name]) != digest:
            raise RuntimeError(f"{name}: target extent identity drift")
        text = (ROOT / source).read_text(encoding="utf-8").lower()
        if any(token in text for token in ("incbin", "include", "db 0x", "db 90h")):
            raise RuntimeError(f"{name}: source acquired an opaque binary dependency")
        sources[source] = sha((ROOT / source).read_bytes())
    output.mkdir()
    builds = {label: build(label, output, targets) for label in ("a", "b")}
    if builds["a"] != builds["b"]:
        raise RuntimeError("cold OMF or linked launcher tail identity drift")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_extents": {name: {"start": f"0x{start:X}", "size": size, "sha256": digest}
                           for name, _source, start, size, digest in STUBS},
        "sources": sources,
        "probe_sha256": sha(Path(__file__).read_bytes()),
        "preflight_stdout_sha256": sha(preflight.stdout.encode()),
        "toolchain_sha256": {"tasm32": TASM_SHA256, "tlink": TLINK_SHA256, "dos_runner": RUNNER_SHA256},
        "builds": builds,
        "both_complete_stubs_raw_equal": True,
        "limit": "These isolated decoded launcher tails do not establish the generated directory or packed outer ZUN.COM exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
