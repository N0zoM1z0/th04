#!/usr/bin/env python3
"""Cold-link the complete ZUNINIT COM component from maintained symbolic ASM."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/probes"))

from lib.omf import describe_omf, parse_omf  # noqa: E402
from replay_th04_zun_source_only import PAYLOAD, PAYLOAD_SHA256  # noqa: E402

SOURCES = (
    ("INTUI", "src/zun/zuninit/interrupt_ui.asm", 0x100, 0xBD),
    ("TEXTSUP", "src/zun/zuninit/text_support.asm", 0x000, 0x4D),
    ("MESSAGES", "src/zun/zuninit/messages.asm", 0x000, 0x102),
    ("CHECK", "src/zun/zuninit/resident_check.asm", 0x000, 0x27),
    ("MAIN", "src/zun/zuninit/main.asm", 0x000, 0xDA),
    ("TAIL", "src/zun/zuninit/trailing_text.asm", 0x000, 0x168),
)
LAYOUT = (
    ("INTUI", 0x0000, 0x01BD),
    ("TEXTSUP", 0x01BD, 0x004D),
    ("MESSAGES", 0x020A, 0x0102),
    ("CHECK", 0x030C, 0x0027),
    ("MAIN", 0x0333, 0x00DA),
    ("TAIL", 0x040D, 0x0168),
)
COMPONENT_START = 0x6F3
COMPONENT_SIZE = 0x475
COMPONENT_SHA256 = "692b1e056d907a9649bd1effa6e83239f71039d17de3569464067d0b42b7aa5e"
TASM = ROOT / ".analysis/toolchain/wineprefix/drive_c/TASM50/bin/TASM32.EXE"
TASM_SHA256 = "ba50fe547863b96242d98cff54cdf95ab268a8682395afad172eedbfc46c5b26"
TLINK = ROOT / ".analysis/toolchain/wineprefix/drive_c/TC4/BIN/TLINK.EXE"
TLINK_SHA256 = "e54f517766a3982dff404ff639b0f94e43c16e688dffb7e14b92df87a8580ad0"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def command(args: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    done = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    log.write_text(json.dumps(args) + f"\nexit={done.returncode}\n" + done.stdout + done.stderr)
    if done.returncode:
        raise RuntimeError(f"command failed: {log}")


def source_audit(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    forbidden = []
    for raw in text.splitlines():
        code = raw.split(";", 1)[0].strip().lower()
        if re.match(r"^(incbin|include|dq|dt)\b", code):
            forbidden.append(code)
    if forbidden:
        raise RuntimeError(f"{path}: forbidden binary/include directive {forbidden}")
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())}


def object_receipt(path: Path, name: str, led_offset: int, led_size: int) -> dict[str, object]:
    data = path.read_bytes()
    desc = describe_omf(data)
    if not desc["valid"] or desc["module_name"] != f"{name}.ASM":
        raise RuntimeError(f"{name}: invalid TASM OMF identity")
    if desc["dependency_paths"] != [f"{name}.ASM"]:
        raise RuntimeError(f"{name}: unexpected OMF source dependencies")
    records = parse_omf(data)
    ledata = [record for record in records if record.record_type == 0xA0]
    if len(ledata) != 1 or ledata[0].data[:3] != bytes((1, led_offset & 0xFF, led_offset >> 8)):
        raise RuntimeError(f"{name}: LEDATA segment/offset drift")
    code = ledata[0].data[3:]
    if len(code) != led_size:
        raise RuntimeError(f"{name}: LEDATA size drift: {len(code)}")
    fixups = [record for record in records if record.record_type == 0x9C]
    if bool(fixups) != (name in {"INTUI", "CHECK", "MAIN"}):
        raise RuntimeError(f"{name}: FIXUPP ownership drift")
    return {
        "module": name,
        "omf_sha256": sha(data),
        "omf_size": len(data),
        "ledata_offset": f"0x{led_offset:X}",
        "ledata_size": len(code),
        "ledata_sha256": sha(code),
        "fixupp_record_count": len(fixups),
        "public_count": desc["record_counts"].get("PUBDEF", 0),
    }


def build(label: str, output: Path, target: bytes) -> dict[str, object]:
    work = output / label
    work.mkdir()
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    objects = []
    for name, path, offset, size in SOURCES:
        source = ROOT / path
        local = work / f"{name}.ASM"
        local.write_bytes(source.read_text(encoding="utf-8").encode("cp932"))
        os.utime(local, (946684800, 946684800))
        command(
            ["wine", r"C:\TASM50\BIN\TASM32.EXE", "/m", "/mx", "/kh32768",
             f"{name}.ASM,{name}.OBJ,{name}.LST"],
            work, work / f"{name}.assemble.log", env,
        )
        objects.append(object_receipt(work / f"{name}.OBJ", name, offset, size))

    response = (
        "-c -s -t " + " ".join(f"{name}.OBJ" for name, *_ in SOURCES)
        + ",ZUNINIT.COM,ZUNINIT.MAP,\r\n"
    )
    (work / "LINK.RSP").write_bytes(response.encode("ascii"))
    command(
        ["wine", str(RUNNER), "-e", "-x", "tlink", "@LINK.RSP"],
        work, work / "link.log", env,
    )
    component = (work / "zuninit.com").read_bytes()
    map_bytes = (work / "zuninit.map").read_bytes()
    map_text = map_bytes.decode("cp437")
    if len(component) != COMPONENT_SIZE or component != target or sha(component) != COMPONENT_SHA256:
        raise RuntimeError(f"{label}: complete ZUNINIT COM differs from attested target")
    for name, start, size in LAYOUT:
        pattern = rf"0000:{start:04X} {size:04X} C=CODE\s+S=_TEXT\s+G=\(none\)\s+M={name}\.ASM"
        if not re.search(pattern, map_text):
            raise RuntimeError(f"{label}: MAP owner/position drift for {name}")
    if not re.search(r"0000:0100\s+idle\s+ZUNINIT_START", map_text):
        raise RuntimeError(f"{label}: COM entry public drift")
    return {
        "objects": objects,
        "component_size": len(component),
        "component_sha256": sha(component),
        "map_sha256": sha(map_bytes),
        "response_sha256": sha((work / "LINK.RSP").read_bytes()),
        "layout": [
            {"module": name, "segment_start": f"0x{start:X}", "size": size}
            for name, start, size in LAYOUT
        ],
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
        raise RuntimeError("decoded ZUN target identity drift")
    target = payload[COMPONENT_START:COMPONENT_START + COMPONENT_SIZE]
    if len(target) != COMPONENT_SIZE or sha(target) != COMPONENT_SHA256:
        raise RuntimeError("target ZUNINIT component identity drift")
    sources = [source_audit(ROOT / path) for _name, path, _offset, _size in SOURCES]
    output.mkdir()
    builds = {label: build(label, output, target) for label in ("a", "b")}
    if builds["a"] != builds["b"]:
        raise RuntimeError("two cold ZUNINIT OMF/COM/MAP builds differ")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "complete maintained symbolic ZUNINIT.COM decoded component cold link",
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_extent": "th04-zun/com-payload/0x6F3+0x475",
        "target_component_sha256": COMPONENT_SHA256,
        "probe_source_sha256": sha(Path(__file__).read_bytes()),
        "preflight_stdout_sha256": sha(preflight.stdout.encode()),
        "toolchain_sha256": {"tasm32": TASM_SHA256, "tlink": TLINK_SHA256, "dos_runner": RUNNER_SHA256},
        "sources": sources,
        "builds": builds,
        "complete_component_raw_equal": True,
        "limit": (
            "This proves the complete decoded ZUNINIT.COM component from maintained original-style ASM. "
            "Original historical source provenance and the packed outer ZUN.COM artifact remain unresolved."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes()), "component_sha256": COMPONENT_SHA256}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
