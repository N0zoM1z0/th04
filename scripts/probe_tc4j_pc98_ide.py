#!/usr/bin/env python3
"""Replay the TC4J PC-98 IDE integrated-compiler MOV-direction probe.

This is a diagnostic producer fingerprint, not an exactness Oracle.  It extracts
only same-media Borland files into ignored ``.analysis`` space, runs the original
PC-98 ``TC.EXE`` under the pinned DOSBox-X PC-98 profile, adds one natural C++
``_BX = _AX`` function to Borland's own TCALC sample, and records the emitted
function bytes from the generated Intel OMF object.

No proprietary executable or generated object is written outside ``.analysis``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

from lib.omf import parse_omf, describe_omf
from lib.pc98 import digest_file


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / ".analysis" / "toolchain" / "media" / "tc40j" / "software" / "borland-4.0j"
INSTALLED = ROOT / ".analysis" / "toolchain" / "installed" / "tc40j"
REFERENCE_MSDOS = ROOT / "_reference" / "ReC98" / "bin" / "msdos.exe"
RUNTIME_MANIFEST = ROOT / "config" / "runtime.toml"
RUNTIME_CONFIG = ROOT / "config" / "runtime" / "dosbox-x-headless.conf"
DEFAULT_ROOT = ROOT / ".analysis" / "reconstruction" / "probes" / "tc4j-pc98-ide-mov"
PROBE_NAME = "_probe_mov_bx_ax"
PROBE_SOURCE = b"\r\nvoid far probe_mov_bx_ax(void)\r\n{\r\n    _BX = _AX;\r\n}\r\n"
EXPECTED_CURRENT_BYTES = bytes.fromhex("55 8B EC 8B D8 5D CB")
TARGET_MOV_BYTES = bytes.fromhex("89 C3")


def run_checked(argv: list[str], cwd: Path, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(argv)}\n{completed.stdout}"
        )
    return completed


def index_value(data: bytes, offset: int) -> tuple[int, int]:
    first = data[offset]
    if first & 0x80:
        return (((first & 0x7F) << 8) | data[offset + 1], offset + 2)
    return first, offset + 1


def public_code_bytes(obj: bytes, symbol: str, length: int) -> tuple[bytes, dict[str, object]]:
    records = parse_omf(obj)
    names = [""]
    segments: list[dict[str, object] | None] = [None]
    for record in records:
        if record.record_type == 0x96:  # LNAMES
            cursor = 0
            while cursor < len(record.data):
                size = record.data[cursor]
                cursor += 1
                names.append(record.data[cursor : cursor + size].decode("ascii", errors="backslashreplace"))
                cursor += size
        elif record.record_type == 0x98:  # SEGDEF16
            data = record.data
            acbp = data[0]
            cursor = 1
            if ((acbp >> 5) & 0x7) == 0:
                cursor += 3
            segment_length = int.from_bytes(data[cursor : cursor + 2], "little")
            cursor += 2
            segment_name_index, cursor = index_value(data, cursor)
            class_name_index, cursor = index_value(data, cursor)
            _, cursor = index_value(data, cursor)
            segments.append(
                {
                    "name": names[segment_name_index],
                    "class": names[class_name_index],
                    "length": segment_length,
                }
            )

    public_segment = None
    public_offset = None
    for record in records:
        if record.record_type != 0x90:  # PUBDEF16 only for this probe
            continue
        data = record.data
        cursor = 0
        _, cursor = index_value(data, cursor)  # group
        segment_index, cursor = index_value(data, cursor)
        if segment_index == 0:
            cursor += 2  # absolute frame
        while cursor < len(data):
            size = data[cursor]
            cursor += 1
            name = data[cursor : cursor + size].decode("ascii", errors="backslashreplace")
            cursor += size
            offset = int.from_bytes(data[cursor : cursor + 2], "little")
            cursor += 2
            _, cursor = index_value(data, cursor)  # type index
            if name == symbol:
                public_segment = segment_index
                public_offset = offset
                break
        if public_segment is not None:
            break
    if public_segment is None or public_offset is None:
        raise RuntimeError(f"public {symbol!r} not found in generated object")
    if public_segment >= len(segments) or segments[public_segment] is None:
        raise RuntimeError(f"public {symbol!r} references invalid segment {public_segment}")
    segment = segments[public_segment]
    assert segment is not None
    if str(segment["class"]).upper() != "CODE":
        raise RuntimeError(f"public {symbol!r} is not in a CODE segment: {segment}")

    image = bytearray(int(segment["length"]))
    coverage = bytearray(int(segment["length"]))
    for record in records:
        if record.record_type != 0xA0:  # LEDATA16
            continue
        data = record.data
        cursor = 0
        segment_index, cursor = index_value(data, cursor)
        offset = int.from_bytes(data[cursor : cursor + 2], "little")
        cursor += 2
        payload = data[cursor:]
        if segment_index != public_segment:
            continue
        end = offset + len(payload)
        if end > len(image):
            raise RuntimeError("LEDATA extends beyond SEGDEF length")
        image[offset:end] = payload
        coverage[offset:end] = b"\x01" * len(payload)
    end = public_offset + length
    if end > len(image) or any(value == 0 for value in coverage[public_offset:end]):
        raise RuntimeError(f"public {symbol!r} bytes are not fully covered by LEDATA")
    return bytes(image[public_offset:end]), {
        "symbol": symbol,
        "segment_index": public_segment,
        "segment_name": segment["name"],
        "segment_class": segment["class"],
        "segment_length": segment["length"],
        "offset": public_offset,
    }


def unpak(package: Path, destination: Path, work: Path, env: dict[str, str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MEDIA / "UNPAK.EXE", work / "UNPAK.EXE")
    shutil.copy2(package, work / package.name)
    relative_destination = destination.relative_to(work)
    run_checked(
        ["wine", str(REFERENCE_MSDOS), "-e", "-x", "UNPAK.EXE", "x", package.name, str(relative_destination)],
        work,
        env=env,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="latest")
    args = parser.parse_args()

    run_checked(
        [
            sys.executable,
            "scripts/attest_toolchain.py",
            "--identity-only",
            "--surface",
            "tc40j-media",
            "--surface",
            "msdos-player-p0281",
        ],
        ROOT,
    )

    runtime = tomllib.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
    dosbox_text = shutil.which(str(runtime["primary"]["command"]))
    if not dosbox_text:
        raise SystemExit("error: pinned DOSBox-X executable not found")
    dosbox = Path(dosbox_text).resolve()
    if digest_file(dosbox) != str(runtime["primary"]["binary_sha256"]):
        raise SystemExit("error: DOSBox-X identity mismatch; run scripts/smoke_runtime.py")
    if digest_file(RUNTIME_CONFIG) != str(runtime["primary"]["config_sha256"]):
        raise SystemExit("error: DOSBox-X PC-98 config identity mismatch")

    required = [
        MEDIA / "UNPAK.EXE",
        MEDIA / "TCPC98.PAK",
        MEDIA / "TCALC.PAK",
        REFERENCE_MSDOS,
        INSTALLED / "BIN",
        INSTALLED / "INCLUDE",
        INSTALLED / "LIB",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("error: missing TC4J probe inputs: " + ", ".join(missing))

    probe_root = DEFAULT_ROOT / args.run_id
    if probe_root.exists():
        raise SystemExit(f"error: probe run already exists: {probe_root.relative_to(ROOT)}")
    probe_root.mkdir(parents=True)
    unpack_root = probe_root / "unpack"
    unpack_root.mkdir()
    env = os.environ.copy()
    env.update(
        {
            "WINEPREFIX": str(ROOT / ".analysis" / "toolchain" / "wineprefix"),
            "WINEDEBUG": "-all",
            "MSDOS_PATH": r"C:\TC4\BIN",
        }
    )

    tc_dir = unpack_root / "pc98"
    tcalc_dir = unpack_root / "tcalc"
    unpak(MEDIA / "TCPC98.PAK", tc_dir, unpack_root, env)
    unpak(MEDIA / "TCALC.PAK", tcalc_dir, unpack_root, env)
    tc_exe = tc_dir / "TC.EXE"
    project = tcalc_dir / "TCALC.PRJ"
    source = tcalc_dir / "TCALC.C"
    if not (tc_exe.is_file() and project.is_file() and source.is_file()):
        raise RuntimeError("same-media extraction did not produce TC.EXE/TCALC.PRJ/TCALC.C")

    drive = probe_root / "drive"
    project_dir = drive / "TC4" / "EXAMPLES" / "TCALC"
    project_dir.mkdir(parents=True)
    shutil.copytree(INSTALLED / "BIN", drive / "TC4" / "BIN")
    shutil.copytree(INSTALLED / "INCLUDE", drive / "TC4" / "INCLUDE")
    shutil.copytree(INSTALLED / "LIB", drive / "TC4" / "LIB")
    shutil.copy2(tc_exe, drive / "TC4" / "BIN" / "TC.EXE")
    for path in tcalc_dir.iterdir():
        if path.is_file():
            shutil.copy2(path, project_dir / path.name)

    probe_source = project_dir / "TCALC.C"
    baseline_source = probe_source.read_bytes()
    probe_source.write_bytes(baseline_source + PROBE_SOURCE)

    session = probe_root / "xdg"
    environment = os.environ.copy()
    environment.update(
        {
            "SDL_VIDEODRIVER": str(runtime["primary"]["execution"]["video_driver"]),
            "SDL_AUDIODRIVER": str(runtime["primary"]["execution"]["audio_driver"]),
            "XDG_CACHE_HOME": str(session / "cache"),
            "XDG_CONFIG_HOME": str(session / "config"),
            "XDG_DATA_HOME": str(session / "data"),
        }
    )
    log = probe_root / "dosbox.log"
    command = [
        str(dosbox),
        "-defaultconf",
        "-defaultmapper",
        "-conf",
        str(RUNTIME_CONFIG),
        "-fastlaunch",
        "-nogui",
        "-nomenu",
        "-exit",
        "-time-limit",
        "30",
        "-c",
        f'mount c "{drive}"',
        "-c",
        "c:",
        "-c",
        r"set PATH=C:\TC4\BIN",
        "-c",
        r"cd \TC4\EXAMPLES\TCALC",
        "-c",
        "tc /b tcalc.prj",
        "-c",
        "exit",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=50,
    )
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"DOSBox-X integrated-compiler probe failed: {completed.returncode}")
    required_markers = list(runtime["primary"]["execution"]["required_log_markers"])
    missing_markers = [marker for marker in required_markers if str(marker) not in completed.stdout]
    if missing_markers:
        raise RuntimeError(f"DOSBox-X PC-98 markers missing: {missing_markers}")

    obj = project_dir / "TCALC.OBJ"
    if not obj.is_file():
        raise RuntimeError("integrated compiler produced no TCALC.OBJ")
    obj_bytes = obj.read_bytes()
    omf = describe_omf(obj_bytes)
    function_bytes, public = public_code_bytes(obj_bytes, PROBE_NAME, len(EXPECTED_CURRENT_BYTES))
    receipt = {
        "schema_version": 1,
        "kind": "tc4j-pc98-integrated-compiler-direction-probe",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "policy": "diagnostic only; never exactness evidence",
        "inputs": {
            "tcpc98_pak_sha256": digest_file(MEDIA / "TCPC98.PAK"),
            "tcalc_pak_sha256": digest_file(MEDIA / "TCALC.PAK"),
            "unpak_sha256": digest_file(MEDIA / "UNPAK.EXE"),
            "pc98_tc_exe_sha256": digest_file(tc_exe),
            "dosbox_sha256": digest_file(dosbox),
            "dosbox_config_sha256": digest_file(RUNTIME_CONFIG),
            "baseline_tcalc_source_sha256": hashlib.sha256(baseline_source).hexdigest(),
            "probe_source_append_sha256": hashlib.sha256(PROBE_SOURCE).hexdigest(),
            "probe_tcalc_source_sha256": digest_file(probe_source),
        },
        "object": {
            "path": str(obj.relative_to(ROOT)),
            "sha256": digest_file(obj),
            "module_name": omf["module_name"],
            "translator_comments": omf["translator_comments"],
            "valid": omf["valid"],
        },
        "public": public,
        "function_bytes_hex": function_bytes.hex(" "),
        "expected_current_bytes_hex": EXPECTED_CURRENT_BYTES.hex(" "),
        "emits_current_8bd8": function_bytes == EXPECTED_CURRENT_BYTES,
        "contains_target_89c3": TARGET_MOV_BYTES in function_bytes,
        "pass": (
            bool(omf["valid"])
            and omf["translator_comments"] == ["TC86 Borland C++ 4.02"]
            and function_bytes == EXPECTED_CURRENT_BYTES
            and TARGET_MOV_BYTES not in function_bytes
        ),
        "runtime_log": str(log.relative_to(ROOT)),
    }
    receipt_path = probe_root / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PC-98 IDE producer probe: {'PASS' if receipt['pass'] else 'CHANGED'}")
    print(f"function bytes: {receipt['function_bytes_hex']}")
    print(f"translator: {omf['translator_comments']}")
    print(f"receipt: {receipt_path.relative_to(ROOT)}")
    return 0 if receipt["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
