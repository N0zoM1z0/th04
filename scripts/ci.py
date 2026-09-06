#!/usr/bin/env python3
"""Run public control-plane tests and private target checks when available."""

from __future__ import annotations

import os
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
        run("Regenerate progress artifacts", [python, "scripts/progress.py"])
        run("Check generated progress", [python, "scripts/progress.py", "--check"])
        if os.environ.get("CI"):
            run(
                "Check generated progress is committed",
                [
                    "git",
                    "diff",
                    "--exit-code",
                    "--",
                    "docs/PROGRESS.md",
                    "resources/progress.svg",
                ],
            )
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
        analyzer = ROOT / ".tools" / "ghidra" / "support" / "analyzeHeadless"
        if analyzer.is_file():
            run(
                "Private Ghidra/JDK identity",
                [python, "scripts/attest_analysis_toolchain.py"],
            )
        else:
            print("\n[Private Ghidra/JDK identity]\nSKIP (.tools is not a public CI input)")
        private_main = ROOT / ".analysis" / "targets" / "th04" / "main.exe"
        project_file = ROOT / "ghidra-project" / "TH04-th04-main.gpr"
        project_store = ROOT / "ghidra-project" / "TH04-th04-main.rep"
        if (
            analyzer.is_file()
            and private_main.is_file()
            and project_file.is_file()
            and project_store.is_dir()
        ):
            run(
                "Private live Ghidra database replay",
                [
                    python,
                    "scripts/ghidra.py",
                    "th04-main",
                    "check",
                ],
            )
            run(
                "Private Ghidra Oracle mutations",
                [python, "scripts/smoke_ghidra_oracle.py", "th04-main"],
            )
        else:
            print(
                "\n[Private live Ghidra database replay]\n"
                "SKIP (target, analyzer, or private project is absent)"
            )
        print("\nCI: PASS")
        return 0
    except (OSError, subprocess.CalledProcessError, tomllib.TOMLDecodeError) as error:
        print(f"\nCI: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
