#!/usr/bin/env python3
"""Fail-closed Borland identity, execution, OMF, MZ, and replay attestation."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

from lib.omf import OMFError, describe_omf
from lib.pc98 import FormatError, describe_blob, digest_file
from lib.toolchain import attest_surface


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "toolchain.toml"
DEFAULT_RECEIPT = ROOT / ".analysis" / "toolchain" / "attestation.json"


def run(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout: int = 120,
) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        timeout=timeout,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "output": completed.stdout.replace("\r", ""),
    }


def clean_probe_outputs(work: Path) -> None:
    for name in ("cprobe.obj", "APROBE.OBJ", "cprobe.exe", "cprobe.map"):
        path = work / name
        if path.exists():
            if not path.is_file() or path.is_symlink():
                raise RuntimeError(f"refusing to replace non-file probe output: {path}")
            path.unlink()


def write_probe_inputs(work: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "probes" / "toolchain" / "compiler_probe.c", work / "CPROBE.C")
    shutil.copyfile(ROOT / "probes" / "toolchain" / "assembler_probe.asm", work / "APROBE.ASM")
    (work / "LINK.RSP").write_bytes(
        b"-c -s c0l.obj C:\\TH04PROBE\\cprobe.obj, "
        b"C:\\TH04PROBE\\cprobe.exe, C:\\TH04PROBE\\cprobe.map, "
        b"emu.lib mathl.lib cl.lib\r\n"
    )


def run_execution_probes(config: dict[str, object]) -> dict[str, object]:
    paths = config["paths"]
    prefix = ROOT / str(paths["wine_prefix"])
    drive_c = prefix / "drive_c"
    work = drive_c / "TH04PROBE"
    wine = shutil.which("wine")
    if not wine:
        return {"pass": False, "error": "wine is not on PATH"}
    msdos = ROOT / str(paths["msdos_player"])
    environment = os.environ.copy()
    environment.update(
        {
            "WINEPREFIX": str(prefix),
            "WINEDEBUG": "-all",
            "MSDOS_PATH": r"C:\TC4\BIN",
        }
    )
    dos = [wine, str(msdos), "-e", "-x"]
    banner_expectations = config["banners"]
    producer_expectations = config["omf_producers"]
    probes: dict[str, object] = {}
    try:
        write_probe_inputs(work)
        banner_commands = {
            "tcc": dos + ["tcc"],
            "tlink": dos + ["tlink"],
            "tasm32": [wine, r"C:\TASM50\bin\TASM32.EXE"],
        }
        banners_ok = True
        for name, command in banner_commands.items():
            result = run(command, cwd=work, environment=environment)
            expected = str(banner_expectations[name])
            passed = result["returncode"] == 0 and expected in str(result["output"])
            result.update({"expected_substring": expected, "pass": passed})
            probes[f"{name}_banner"] = result
            banners_ok &= passed

        rounds: list[dict[str, object]] = []
        for number in (1, 2):
            clean_probe_outputs(work)
            compiler = run(
                dos
                + [
                    "tcc",
                    "-c",
                    "-ml",
                    "-3",
                    "-O",
                    "-Z",
                    "-nC:\\TH04PROBE\\",
                    r"C:\TH04PROBE\CPROBE.C",
                ],
                cwd=work,
                environment=environment,
            )
            assembler = run(
                [
                    wine,
                    r"C:\TASM50\bin\TASM32.EXE",
                    "/m",
                    "/mx",
                    "/kh32768",
                    "/t",
                    r"C:\TH04PROBE\APROBE.ASM",
                    r"C:\TH04PROBE\APROBE.OBJ",
                ],
                cwd=work,
                environment=environment,
            )
            linker = run(
                dos + ["tlink", r"@C:\TH04PROBE\LINK.RSP"],
                cwd=work,
                environment=environment,
            )
            executable = run(
                dos + [r"C:\TH04PROBE\cprobe.exe"],
                cwd=work,
                environment=environment,
            )
            outputs = {
                name: {
                    "size": (work / name).stat().st_size,
                    "sha256": digest_file(work / name),
                }
                for name in ("cprobe.obj", "APROBE.OBJ", "cprobe.exe", "cprobe.map")
                if (work / name).is_file()
            }
            compiler_omf = describe_omf((work / "cprobe.obj").read_bytes())
            assembler_omf = describe_omf((work / "APROBE.OBJ").read_bytes())
            mz = describe_blob((work / "cprobe.exe").read_bytes())
            passed = (
                all(item["returncode"] == 0 for item in (compiler, assembler, linker, executable))
                and len(outputs) == 4
                and compiler_omf["valid"]
                and assembler_omf["valid"]
                and producer_expectations["tcc"]
                in compiler_omf["translator_comments"]
                and producer_expectations["tasm32"]
                in assembler_omf["translator_comments"]
                and any(
                    path.lower().endswith("dos.h")
                    for path in compiler_omf["dependency_paths"]
                )
                and mz["format"] == "mz"
                and mz["format_integrity"]["valid"]
            )
            rounds.append(
                {
                    "round": number,
                    "pass": passed,
                    "commands": {
                        "compiler": compiler,
                        "assembler": assembler,
                        "linker": linker,
                        "executable": executable,
                    },
                    "outputs": outputs,
                    "compiler_omf": compiler_omf,
                    "assembler_omf": assembler_omf,
                    "mz": mz,
                }
            )
        replay_exact = rounds[0]["outputs"] == rounds[1]["outputs"]
        probes.update(
            {
                "rounds": rounds,
                "replay_exact": replay_exact,
                "source_sha256": {
                    "compiler_probe.c": digest_file(
                        ROOT / "probes" / "toolchain" / "compiler_probe.c"
                    ),
                    "assembler_probe.asm": digest_file(
                        ROOT / "probes" / "toolchain" / "assembler_probe.asm"
                    ),
                },
                "pass": banners_ok and replay_exact and all(item["pass"] for item in rounds),
            }
        )
    except (OSError, OMFError, FormatError, RuntimeError, subprocess.SubprocessError) as error:
        probes.update({"pass": False, "error": str(error)})
    return probes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or (
        DEFAULT_RECEIPT.with_name("identity-attestation.json")
        if args.identity_only
        else DEFAULT_RECEIPT
    )
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    surfaces = [attest_surface(ROOT, item) for item in config["surfaces"]]
    identity_pass = all(item["pass"] or not item["required"] for item in surfaces)
    execution = None if args.identity_only else run_execution_probes(config)
    execution_pass = True if args.identity_only else bool(execution and execution["pass"])
    report = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "manifest": str(CONFIG.relative_to(ROOT)),
        "manifest_sha256": digest_file(CONFIG),
        "identity_pass": identity_pass,
        "execution_pass": execution_pass,
        "ready": identity_pass and execution_pass and not args.identity_only,
        "surfaces": surfaces,
        "execution": execution,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for surface in surfaces:
            print(f"{'PASS' if surface['pass'] else 'FAIL'} identity {surface['id']}")
            if not surface["pass"]:
                print(f"  {surface.get('error')}")
        if execution is not None:
            print(f"{'PASS' if execution_pass else 'FAIL'} execution probes")
        if args.identity_only:
            print(f"toolchain identity: {'READY' if identity_pass else 'NOT READY'}")
        else:
            print(f"toolchain: {'READY' if report['ready'] else 'NOT READY'}")
        print(f"receipt: {output}")
    return 0 if report["ready"] or (args.identity_only and identity_pass) else 1


if __name__ == "__main__":
    sys.exit(main())
