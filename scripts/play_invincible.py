#!/usr/bin/env python3
"""Launch the private invincible TH04 image in a persistent DOSBox-X window."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREPARED = ROOT / ".analysis/runtime/candidates/th04-invincible-play"
BUILD = ROOT / ".analysis/build/th04-invincible"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def live_dosbox(pid: int, image: Path) -> bool:
    command = Path(f"/proc/{pid}/cmdline")
    try:
        arguments = command.read_bytes()
        return b"dosbox-x" in arguments and os.fsencode(image) in arguments
    except (OSError, ValueError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-dir", type=Path, default=DEFAULT_PREPARED)
    parser.add_argument("--stop", action="store_true", help="stop this playable DOSBox-X window")
    args = parser.parse_args()
    prepared = args.prepared_dir.resolve()
    if not prepared.is_relative_to(ROOT / ".analysis/runtime/candidates"):
        parser.error("prepared image must be below .analysis/runtime/candidates")
    play = prepared / "play.hdi"
    pid_file = prepared / "dosbox.pid"
    if pid_file.is_file():
        pid = int(pid_file.read_text())
        if live_dosbox(pid, play):
            if args.stop:
                os.kill(pid, signal.SIGTERM)
                print(f"Stopped DOSBox-X PID {pid}")
            else:
                print(f"DOSBox-X is already running: PID {pid}, image {play}")
            return 0
    if args.stop:
        print("No live DOSBox-X window for this image")
        return 0

    manifest = json.loads((BUILD / "build.json").read_text(encoding="utf-8"))
    if manifest.get("variant") != "invincible-main":
        raise ValueError("build is not the invincible MAIN variant")
    source_receipt = json.loads((prepared / "receipt.json").read_text(encoding="utf-8"))
    if source_receipt.get("products") != manifest["products"]:
        raise ValueError("prepared image was made from a different build")
    base = prepared / "diagnostic.hdi"
    if sha256(base) != source_receipt["diagnostic_hdi_sha256"]:
        raise ValueError("prepared image identity drift")
    if not play.exists():
        shutil.copyfile(base, play)

    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    config_source = ROOT / runtime["primary"]["config"]
    config_bytes = config_source.read_bytes()
    if hashlib.sha256(config_bytes).hexdigest() != runtime["primary"]["config_sha256"]:
        raise ValueError("pinned emulator configuration identity drift")
    old_video = b"videodriver       = dummy"
    old_sound = b"nosound = true"
    if config_bytes.count(old_video) != 1 or config_bytes.count(old_sound) != 1:
        raise ValueError("unexpected DOSBox-X configuration format")
    config_bytes = config_bytes.replace(old_video, b"videodriver       = x11")
    config_bytes = config_bytes.replace(old_sound, b"nosound = false")
    config_bytes = config_bytes.replace(b"[dosbox]\n", b"[dosbox]\nquit warning = false\n", 1)
    config = prepared / "dosbox-x-play.conf"
    config.write_bytes(config_bytes)

    executable = shutil.which("dosbox-x")
    if not executable:
        raise FileNotFoundError("dosbox-x is unavailable")
    command = [executable, "-defaultconf", "-defaultmapper", "-conf", str(config),
               "-fastlaunch", "-nomenu", "-c",
               f'imgmount 2 "{play}" -t hdd -fs none', "-c", "boot -l c"]
    environment = os.environ.copy()
    environment.update(SDL_VIDEODRIVER="x11", SDL_AUDIODRIVER="pulseaudio",
                       XDG_CACHE_HOME=str(prepared / "cache"),
                       XDG_CONFIG_HOME=str(prepared / "config"),
                       XDG_DATA_HOME=str(prepared / "data"))
    log_path = prepared / "dosbox-play.log"
    with log_path.open("a", encoding="utf-8") as log:
        process = subprocess.Popen(command, cwd=ROOT, env=environment,
                                   stdin=subprocess.DEVNULL, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(3)
    if process.poll() is not None:
        raise RuntimeError(f"DOSBox-X exited with {process.returncode}; inspect {log_path}")
    pid_file.write_text(f"{process.pid}\n", encoding="ascii")
    print(f"DOSBox-X running: PID {process.pid}, image {play}, log {log_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Cannot start invincible TH04: {error}", file=sys.stderr)
        raise SystemExit(1)
