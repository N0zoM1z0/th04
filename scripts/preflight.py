#!/usr/bin/env python3
"""Run the fail-closed checks required before target-dependent work."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str], required: bool = True) -> bool:
    print(f"\n[{label}]", flush=True)
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode and required:
        print(f"error: {label} failed", file=sys.stderr)
        return False
    return True


def main() -> int:
    python = sys.executable
    checks = [
        run("Environment", [python, "scripts/check_environment.py"], required=False),
        run("Tracking", [python, "scripts/validate_tracking.py"]),
        run("TH04 targets", [python, "scripts/verify_targets.py", "--game", "th04"]),
        run("Status", [python, "scripts/status.py"]),
    ]
    ok = all(checks)
    print(f"\npreflight: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
