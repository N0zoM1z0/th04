#!/usr/bin/env python3
"""Attest and smoke-test the pinned headless DOSBox-X PC-98 baseline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

from lib.pc98 import digest_file


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "runtime.toml"
RECEIPT = ROOT / ".analysis" / "runtime" / "smoke-attestation.json"
LOG = ROOT / ".analysis" / "runtime" / "smoke.log"


def fail(message: str) -> "None":
    raise SystemExit(f"error: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--boot-image",
        action="store_true",
        help="also mount and briefly boot the pinned private zun.hdi",
    )
    args = parser.parse_args()

    manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    primary = manifest["primary"]
    execution = primary["execution"]
    image = manifest["image"]

    executable_name = str(primary["command"])
    executable_text = shutil.which(executable_name)
    if not executable_text:
        fail(f"{executable_name} not found; see docs/RUNTIME.md")
    executable = Path(executable_text).resolve()
    binary_sha256 = digest_file(executable)
    if binary_sha256 != primary["binary_sha256"]:
        fail(
            f"DOSBox-X binary identity mismatch: {binary_sha256}; "
            "do not treat an uncalibrated emulator as runtime evidence"
        )

    package_version = subprocess.run(
        [
            "dpkg-query",
            "-W",
            "-f=${Version}",
            str(primary["package"]),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    observed_package_version = package_version.stdout.strip()
    if (
        package_version.returncode
        or observed_package_version != primary["package_version"]
    ):
        fail(
            "DOSBox-X package version mismatch: "
            f"{observed_package_version or 'not installed'}"
        )

    config = ROOT / str(primary["config"])
    if not config.is_file():
        fail(f"runtime config not found: {config}")
    config_sha256 = digest_file(config)
    if config_sha256 != primary["config_sha256"]:
        fail(f"runtime config identity mismatch: {config_sha256}")

    version = subprocess.run(
        [str(executable), "--version"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    version_text = version.stdout + version.stderr
    # Ubuntu's 2024.03.01 build prints the valid banner but exits 1 for
    # --version, so identity is the pinned banner plus executable digest.
    if str(primary["banner"]) not in version_text:
        fail("DOSBox-X version banner does not match config/runtime.toml")

    runtime_root = ROOT / ".analysis" / "runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    boot_image: Path | None = None
    image_sha256: str | None = None
    if args.boot_image:
        boot_image = ROOT / str(image["path"])
        if not boot_image.is_file():
            fail(
                f"private runtime image is missing: {boot_image}; rerun target "
                "import with --retain-runtime-image"
            )
        if boot_image.stat().st_size != int(image["size"]):
            fail(f"runtime image size mismatch: {boot_image.stat().st_size}")
        image_sha256 = digest_file(boot_image)
        if image_sha256 != image["sha256"]:
            fail(f"runtime image SHA-256 mismatch: {image_sha256}")

    command = [
        str(executable),
        "-defaultconf",
        "-defaultmapper",
        "-conf",
        str(config),
        "-fastlaunch",
        "-nogui",
        "-nomenu",
        "-exit",
        "-time-limit",
        str(execution["time_limit_seconds"]),
    ]
    if boot_image is None:
        command.extend(["-c", "ver", "-c", "exit"])
    else:
        command.extend(
            [
                "-c",
                f'imgmount 2 "{boot_image}" -t hdd -fs none',
                "-c",
                "boot -l c",
            ]
        )

    with tempfile.TemporaryDirectory(prefix="session-", dir=runtime_root) as raw_tmp:
        session = Path(raw_tmp)
        environment = os.environ.copy()
        environment.update(
            {
                "SDL_VIDEODRIVER": str(execution["video_driver"]),
                "SDL_AUDIODRIVER": str(execution["audio_driver"]),
                "XDG_CACHE_HOME": str(session / "cache"),
                "XDG_CONFIG_HOME": str(session / "config"),
                "XDG_DATA_HOME": str(session / "data"),
            }
        )
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=int(execution["time_limit_seconds"]) + 10,
            )
        except subprocess.TimeoutExpired as error:
            fail(f"DOSBox-X exceeded the outer timeout: {error}")

    log_text = result.stdout + result.stderr
    LOG.write_text(log_text, encoding="utf-8")
    required_markers = list(execution["required_log_markers"])
    if boot_image is not None:
        required_markers.extend(execution["boot_required_log_markers"])
    missing_markers = [
        marker
        for marker in required_markers
        if str(marker) not in log_text
    ]
    ready = result.returncode == 0 and not missing_markers
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "ready": ready,
        "scope": manifest["policy"]["scope"],
        "not_proven": manifest["policy"]["not_proven"],
        "emulator": {
            "path": str(executable),
            "sha256": binary_sha256,
            "banner": str(primary["banner"]),
            "version_returncode": version.returncode,
            "package": str(primary["package"]),
            "package_version": observed_package_version,
        },
        "config": {
            "path": str(config.relative_to(ROOT)),
            "sha256": config_sha256,
        },
        "image": None
        if boot_image is None
        else {
            "path": str(boot_image),
            "sha256": image_sha256,
            "canonicality": str(image["canonicality"]),
        },
        "command": command,
        "returncode": result.returncode,
        "required_log_markers": required_markers,
        "missing_log_markers": missing_markers,
        "log": str(LOG.relative_to(ROOT)),
    }
    RECEIPT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not ready:
        fail(
            f"runtime smoke failed (returncode={result.returncode}, "
            f"missing_markers={missing_markers}); see {LOG.relative_to(ROOT)}"
        )
    mode = "pinned-image boot" if boot_image else "PC-98 startup"
    print(f"runtime smoke: PASS ({mode}; headless host baseline only)")
    print(f"receipt: {RECEIPT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
