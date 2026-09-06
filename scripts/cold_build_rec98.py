#!/usr/bin/env python3
"""Cold-build a pinned ReC98 snapshot as an untrusted calibration candidate."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from lib.pc98 import digest_file
from lib.toolchain import tree_identity


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "_reference" / "ReC98"
REVISION = "b6ba5b0a529edbb31efdf8c0e939263804f8ee47"


def command_output(command: list[str], cwd: Path) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def inventory(root: Path, pattern: str) -> list[dict[str, object]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": digest_file(path),
        }
        for path in sorted(root.glob(pattern))
        if path.is_file()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-id",
        default=datetime.now(timezone.utc).strftime("cold-%Y%m%dT%H%M%SZ"),
        help="new private run directory name",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.run_id):
        parser.error("--run-id must contain only letters, digits, dot, underscore, or dash")
    if not REFERENCE.is_dir():
        print("missing _reference/ReC98; run the README clone command", file=sys.stderr)
        return 1
    resolved = command_output(["git", "rev-parse", REVISION], REFERENCE)
    if resolved != REVISION:
        print(f"pinned ReC98 revision is unavailable: {REVISION}", file=sys.stderr)
        return 1

    # Re-run every identity and executable probe immediately before the build.
    attestation = subprocess.run(
        [sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT
    )
    if attestation.returncode:
        return attestation.returncode

    run_root = ROOT / ".analysis" / "builds" / f"rec98-{REVISION[:10]}" / args.run_id
    if run_root.exists():
        print(f"refusing to overwrite prior run: {run_root}", file=sys.stderr)
        return 1
    source = run_root / "source"
    source.mkdir(parents=True)
    archive = run_root / "source.tar"
    subprocess.run(
        ["git", "archive", "--format=tar", f"--output={archive}", REVISION],
        cwd=REFERENCE,
        check=True,
    )
    subprocess.run(["tar", "-xf", archive, "-C", source], check=True)

    prefix = ROOT / ".analysis" / "toolchain" / "wineprefix"
    environment = os.environ.copy()
    environment.update(
        {
            "WINEPREFIX": str(prefix),
            "WINEDEBUG": "-all",
            "MSDOS_PATH": r"C:\TC4\BIN",
        }
    )
    windows_command = (
        r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%"
        r"&&set PROCESSOR_ARCHITECTURE=AMD64"
        r"&&set PROCESSOR_ARCHITEW6432=AMD64"
        r"&&build.bat"
    )
    command = ["wine", "cmd", "/d", "/c", windows_command]
    log = run_root / "build.log"
    started = datetime.now(timezone.utc)
    with log.open("wb") as stream:
        completed = subprocess.run(
            command,
            cwd=source,
            env=environment,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
    finished = datetime.now(timezone.utc)

    receipt = {
        "schema_version": 1,
        "kind": "untrusted-rec98-cold-build-candidate",
        "cold": True,
        "source_materialization": "git-archive",
        "reference_remote": command_output(
            ["git", "remote", "get-url", "origin"], REFERENCE
        ),
        "source_revision": REVISION,
        "source_tree": command_output(["git", "rev-parse", f"{REVISION}^{{tree}}"], REFERENCE),
        "source_archive": {
            "size": archive.stat().st_size,
            "sha256": digest_file(archive),
        },
        "toolchain_attestation": {
            "path": ".analysis/toolchain/attestation.json",
            "sha256": digest_file(ROOT / ".analysis" / "toolchain" / "attestation.json"),
        },
        "command": command,
        "environment": {
            "WINEPREFIX": ".analysis/toolchain/wineprefix",
            "WINEDEBUG": "-all",
            "MSDOS_PATH": r"C:\TC4\BIN",
            "PROCESSOR_ARCHITECTURE": "AMD64 (set inside cmd.exe)",
            "PROCESSOR_ARCHITEW6432": "AMD64 (set inside cmd.exe)",
        },
        "started_utc": started.isoformat(),
        "finished_utc": finished.isoformat(),
        "returncode": completed.returncode,
        "build_log": {"size": log.stat().st_size, "sha256": digest_file(log)},
        "th01_outputs": inventory(source, "bin/th01/*"),
        "th01_maps": inventory(source, "obj/th01/*.map"),
        "th01_link_responses": inventory(source, "obj/th01/*.@l"),
    }
    if (source / "bin" / "th01").is_dir():
        identity = tree_identity(source / "bin" / "th01")
        receipt["th01_output_tree"] = {
            "sha256": identity.sha256,
            "file_count": identity.file_count,
            "total_size": identity.total_size,
        }
    receipt_path = run_root / "build-receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if completed.returncode:
        print(f"ReC98 cold build FAILED; inspect {log}", file=sys.stderr)
        return completed.returncode
    print(f"ReC98 cold build PASS (candidate only): {run_root}")
    print(f"receipt: {receipt_path}")
    print("next: python3 scripts/compare_rec98_th01.py " + str(source))
    return 0


if __name__ == "__main__":
    sys.exit(main())

