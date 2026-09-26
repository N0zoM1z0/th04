#!/usr/bin/env python3
"""Cold-link the maintained ONGCHK library component against TH04 ZUN."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf, parse_omf  # noqa: E402

SOURCE = ROOT / "src/zun/ongchk/ongchk.asm"
PAYLOAD = ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin"
PAYLOAD_SHA = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
START, SIZE = 0x355, 926
COMPONENT_SHA = "4f9a9451f19bdd8d3ea8949a5ea75df6c2f92a9a84dcf39e1d7cf13421acc8a0"
TASM = ROOT / ".analysis/toolchain/wineprefix/drive_c/TASM50/bin/TASM32.EXE"
TASM_SHA = "ba50fe547863b96242d98cff54cdf95ab268a8682395afad172eedbfc46c5b26"
TLINK = ROOT / ".analysis/toolchain/wineprefix/drive_c/TC4/BIN/TLINK.EXE"
TLINK_SHA = "e54f517766a3982dff404ff639b0f94e43c16e688dffb7e14b92df87a8580ad0"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def command(args: list[str], work: Path, log: Path, env: dict[str, str]) -> None:
    result = subprocess.run(args, cwd=work, env=env, capture_output=True,
                            text=True, timeout=120)
    log.write_text(json.dumps(args) + f"\nexit={result.returncode}\n"
                   + result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"cold build failed; inspect {log}")


def build(label: str, output: Path, target: bytes) -> dict[str, object]:
    work = output / label
    work.mkdir()
    source = SOURCE.read_text(encoding="utf-8")
    if re.search(r"(?im)^\s*(?:incbin|include|dq|dt)\b", source):
        raise RuntimeError("ONGCHK source has a forbidden binary/include directive")
    (work / "ONGCHK.ASM").write_bytes(source.encode("cp932"))
    os.utime(work / "ONGCHK.ASM", (946684800, 946684800))
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    command(["wine", r"C:\TASM50\BIN\TASM32.EXE", "/m", "/mx", "/kh32768",
             "ONGCHK.ASM,ONGCHK.OBJ,ONGCHK.LST"],
            work, work / "assemble.log", env)
    obj = (work / "ONGCHK.OBJ").read_bytes()
    desc = describe_omf(obj)
    if not desc["valid"] or desc["module_name"] != "ONGCHK.ASM":
        raise RuntimeError(f"{label}: invalid OMF object")
    if desc["dependency_paths"] != ["ONGCHK.ASM"]:
        raise RuntimeError(f"{label}: unexpected OMF dependency")
    ledatas = [r for r in parse_omf(obj) if r.record_type == 0xA0]
    if len(ledatas) != 1 or ledatas[0].data[:3] != b"\x01\x00\x01":
        raise RuntimeError(f"{label}: unexpected COM LEDATA offset")
    code = ledatas[0].data[3:]
    if len(code) != SIZE or sha(code) != COMPONENT_SHA:
        raise RuntimeError(f"{label}: complete initialized OMF extent differs")
    (work / "LINK.RSP").write_bytes(
        b"-c -s -t ONGCHK.OBJ,ONGCHK.COM,ONGCHK.MAP,\r\n")
    command(["wine", str(RUNNER), "-e", "-x", "tlink", "@LINK.RSP"],
            work, work / "link.log", env)
    linked = (work / "ongchk.com").read_bytes()
    map_data = (work / "ongchk.map").read_bytes()
    if len(linked) != SIZE or linked != target:
        raise RuntimeError(f"{label}: complete linked ONGCHK differs from target")
    map_text = map_data.decode("cp437")
    if not re.search(r"0000:0000 04C8 C=CODE\s+S=_TEXT\s+G=DGROUP\s+M=ONGCHK\.ASM", map_text):
        raise RuntimeError(f"{label}: COM/BSS MAP contribution drift")
    return {"omf_sha256": sha(obj), "initialized_omf_sha256": sha(code),
            "omf_fixupp_records": desc["record_counts"].get("FIXUPP", 0),
            "map_sha256": sha(map_data), "component_sha256": sha(linked),
            "component_size": len(linked)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output must be a new direct child of .analysis/reconstruction/probes")
    preflight = subprocess.run([sys.executable, "scripts/preflight.py"],
                              cwd=ROOT, capture_output=True, text=True, check=True)
    for path, digest in ((TASM, TASM_SHA), (TLINK, TLINK_SHA), (RUNNER, RUNNER_SHA)):
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"toolchain identity drift: {path}")
    payload = PAYLOAD.read_bytes()
    target = payload[START:START + SIZE]
    if sha(payload) != PAYLOAD_SHA or len(target) != SIZE or sha(target) != COMPONENT_SHA:
        raise RuntimeError("attested target or decoded component identity drift")
    output.mkdir()
    builds = {label: build(label, output, target) for label in ("a", "b")}
    if builds["a"] != builds["b"]:
        raise RuntimeError("ONGCHK A/B cold outputs differ")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "maintained symbolic external-library ONGCHK COM component",
        "artifact": "th04-zun", "target_extent": "com-payload/0x355+0x39E",
        "target_payload_sha256": PAYLOAD_SHA,
        "target_component_sha256": COMPONENT_SHA,
        "source_sha256": sha(SOURCE.read_bytes()),
        "probe_sha256": sha(Path(__file__).read_bytes()),
        "preflight_sha256": sha(preflight.stdout.encode()),
        "toolchain_sha256": {"tasm32": TASM_SHA, "tlink": TLINK_SHA,
                             "dos_runner": RUNNER_SHA},
        "builds": builds, "complete_component_raw_equal": True,
        "limit": "External library ownership; no ZUN authored-function or packed-MZ exact credit.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes()),
                      "component_sha256": COMPONENT_SHA}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
