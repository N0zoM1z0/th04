#!/usr/bin/env python3
"""Compile one frozen ReC98-overlay source with TC4J's original PC-98 IDE.

The driver is source-driven: it accepts a source file inside a cold materialized
source tree, rebuilds a private short-path PC-98 IDE workspace from the pinned
TC4J media, runs the original integrated compiler under the pinned DOSBox-X
PC-98 profile, validates the generated Intel OMF module, and copies only that
fresh object plus a JSON receipt back into the cold tree.

It never accepts a prebuilt object and never reads target bytes.
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

from lib.omf import describe_omf
from lib.pc98 import digest_file
from probe_tc4j_pc98_ide import (
    INSTALLED,
    MEDIA,
    REFERENCE_MSDOS,
    RUNTIME_CONFIG,
    RUNTIME_MANIFEST,
    run_checked,
    unpak,
)

ROOT = Path(__file__).resolve().parents[1]
PC98_TC_SHA256 = "91d410850da69c6ff894f902d1b5610f04b5e2b6d0097b2a11cf2fafa54f14b4"
PROJECT_SOURCE_NAME = b"M5A.CPP"  # seven bytes, replacing TCALC.C in-place


def contained(root: Path, text: str) -> Path:
    relative = Path(text)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"path must stay inside source root: {text}")
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes source root: {text}") from exc
    return path


def patch_project(source_project: Path, destination: Path) -> None:
    data = bytearray(source_project.read_bytes())
    needle = b"TCALC.C"
    changed = 0
    cursor = 0
    while True:
        offset = bytes(data).find(needle, cursor)
        if offset < 0:
            break
        # Preserve TCALC.CSM IDE-state/cache strings; only patch source entries.
        suffix = bytes(data[offset + len(needle) : offset + len(needle) + 2])
        if suffix != b"SM":
            data[offset : offset + len(needle)] = PROJECT_SOURCE_NAME
            changed += 1
        cursor = offset + len(needle)
    if changed != 2:
        raise RuntimeError(f"unexpected TCALC.PRJ source-entry count: {changed}")
    destination.write_bytes(bytes(data))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--source", required=True, help="path relative to source root")
    parser.add_argument("--output", required=True, help="object path relative to source root")
    parser.add_argument("--receipt", required=True, help="receipt path relative to source root")
    parser.add_argument("--game", type=int, default=4)
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    if not source_root.is_dir() or source_root.is_symlink():
        raise SystemExit(f"error: invalid cold source root: {source_root}")
    source = contained(source_root, args.source)
    output = contained(source_root, args.output)
    receipt_path = contained(source_root, args.receipt)
    if not source.is_file() or source.is_symlink():
        raise SystemExit(f"error: source is missing or symlinked: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)

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
        raise SystemExit("error: DOSBox-X identity mismatch")
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
        raise SystemExit("error: missing pinned integrated-compiler inputs: " + ", ".join(missing))

    source_bytes = source.read_bytes()
    with tempfile.TemporaryDirectory(prefix="th04-pc98-ide-") as temporary:
        work_root = Path(temporary)
        unpack_root = work_root / "unpack"
        unpack_root.mkdir()
        wine_env = os.environ.copy()
        wine_env.update(
            {
                "WINEPREFIX": str(ROOT / ".analysis" / "toolchain" / "wineprefix"),
                "WINEDEBUG": "-all",
                "MSDOS_PATH": r"C:\TC4\BIN",
            }
        )
        tc_dir = unpack_root / "pc98"
        sample_dir = unpack_root / "tcalc"
        unpak(MEDIA / "TCPC98.PAK", tc_dir, unpack_root, wine_env)
        unpak(MEDIA / "TCALC.PAK", sample_dir, unpack_root, wine_env)
        tc_exe = tc_dir / "TC.EXE"
        sample_project = sample_dir / "TCALC.PRJ"
        if not tc_exe.is_file() or not sample_project.is_file():
            raise RuntimeError("same-media extraction did not produce TC.EXE/TCALC.PRJ")
        if digest_file(tc_exe) != PC98_TC_SHA256:
            raise RuntimeError("PC-98 TC.EXE identity mismatch")

        drive = work_root / "drive"
        shutil.copytree(INSTALLED / "BIN", drive / "TC4" / "BIN")
        shutil.copytree(INSTALLED / "INCLUDE", drive / "TC4" / "INCLUDE")
        shutil.copytree(INSTALLED / "LIB", drive / "TC4" / "LIB")
        shutil.copy2(tc_exe, drive / "TC4" / "BIN" / "TC.EXE")
        project_dir = drive / "WORK"
        # The original IDE resolves project-relative include paths only on its C:
        # workspace, so copy the frozen source tree into this ephemeral one-shot
        # compiler root. Cold A/B trees are already isolated and serial.
        shutil.copytree(
            source_root,
            project_dir,
            ignore=shutil.ignore_patterns("obj", "bin", ".tup", "*.OBJ", "*.obj"),
        )
        project_source = project_dir / PROJECT_SOURCE_NAME.decode("ascii")
        project_source.write_bytes(f"#define GAME {args.game}\r\n".encode("ascii") + source_bytes.replace(b"\n", b"\r\n"))
        # TC4J's PC-98 IDE stores the primary source DOS timestamp in a
        # vendor COMENT record. Preserve the frozen cold-tree source mtime so
        # isolated A/B compiler workspaces see identical source metadata.
        source_stat = source.stat()
        os.utime(project_source, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
        project_file = project_dir / "M5A.PRJ"
        patch_project(sample_project, project_file)

        session = work_root / "xdg"
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
            "60",
            "-c",
            f'mount c "{drive}"',
            "-c",
            "c:",
            "-c",
            r"set PATH=C:\TC4\BIN",
            "-c",
            r"cd \WORK",
            "-c",
            "tc /b m5a.prj",
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
            timeout=90,
        )
        if completed.returncode:
            raise RuntimeError(f"DOSBox-X integrated compiler failed: {completed.returncode}\n{completed.stdout}")
        required_markers = list(runtime["primary"]["execution"]["required_log_markers"])
        missing_markers = [marker for marker in required_markers if str(marker) not in completed.stdout]
        if missing_markers:
            raise RuntimeError(f"DOSBox-X PC-98 markers missing: {missing_markers}")
        generated = project_dir / "M5A.OBJ"
        if not generated.is_file():
            raise RuntimeError(
                "integrated compiler produced no M5A.OBJ\n"
                f"DOSBox-X output:\n{completed.stdout}"
            )
        obj_bytes = generated.read_bytes()
        omf = describe_omf(obj_bytes)
        if not omf["valid"] or omf["translator_comments"] != ["TC86 Borland C++ 4.02"]:
            raise RuntimeError(f"unexpected integrated-compiler OMF identity: {omf['translator_comments']}")
        output.write_bytes(obj_bytes)

    receipt = {
        "schema_version": 1,
        "kind": "tc4j-pc98-integrated-compiler-object",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "source": args.source,
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "output": args.output,
        "object_sha256": digest_file(output),
        "object_dependency_normalized_sha256": omf["dependency_timestamp_normalized_sha256"],
        "object_module_name": omf["module_name"],
        "translator_comments": omf["translator_comments"],
        "pc98_tc_exe_sha256": PC98_TC_SHA256,
        "tcpc98_pak_sha256": digest_file(MEDIA / "TCPC98.PAK"),
        "tcalc_pak_sha256": digest_file(MEDIA / "TCALC.PAK"),
        "dosbox_sha256": digest_file(dosbox),
        "dosbox_config_sha256": digest_file(RUNTIME_CONFIG),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PC-98 IDE object: {output}")
    print(f"normalized SHA-256: {receipt['object_dependency_normalized_sha256']}")
    print(f"receipt: {receipt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
