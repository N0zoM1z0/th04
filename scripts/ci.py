#!/usr/bin/env python3
"""Run public control-plane tests and private target checks when available."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> None:
    print(f"\n[{label}]", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    python = sys.executable
    try:
        run("Python unit tests", [python, "-m", "unittest", "discover", "-s", "tests", "-v"])
        run("Tracking ledgers", [python, "scripts/validate_tracking.py"])
        run("Python syntax", [python, "-m", "compileall", "-q", "scripts", "tests"])
        manifest = tomllib.loads(
            (ROOT / "config" / "targets.toml").read_text(encoding="utf-8")
        )
        required = [
            ROOT / item["private_path"]
            for item in manifest["artifacts"]
            if item["game"] == "th04" and item["required"]
        ]
        if all(path.is_file() for path in required):
            run("Private TH04 targets", [python, "scripts/verify_targets.py", "--game", "th04"])
        else:
            print("\n[Private TH04 targets]\nSKIP (targets are not public CI inputs)")
        calibration = [ROOT / item["private_path"] for item in manifest["artifacts"]]
        if all(path.is_file() for path in calibration):
            run("Private cross-game Oracle calibration", [python, "scripts/smoke_oracles.py"])
        else:
            print(
                "\n[Private cross-game Oracle calibration]\n"
                "SKIP (TH01-TH05 targets are not public CI inputs)"
            )
        print("\nCI: PASS")
        return 0
    except (OSError, subprocess.CalledProcessError, tomllib.TOMLDecodeError) as error:
        print(f"\nCI: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
