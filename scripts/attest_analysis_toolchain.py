#!/usr/bin/env python3
"""Fail-closed identity and execution attestation for pinned Ghidra and JDK."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from lib.analysis import AnalysisError, attest_analysis_install, load_analysis_config, repository_path
from lib.pc98 import digest_file


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "analysis_toolchain.toml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        config = load_analysis_config(CONFIG)
        output = args.output or repository_path(ROOT, config["private_paths"]["receipt"])
        installation = attest_analysis_install(ROOT, config)
        report = {
            "schema_version": 1,
            "observed_utc": datetime.now(timezone.utc).isoformat(),
            "manifest": str(CONFIG.relative_to(ROOT)),
            "manifest_sha256": digest_file(CONFIG),
            **installation,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        temporary.replace(output)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            for name, check in report["checks"].items():
                print(f"{'PASS' if check['pass'] else 'FAIL'} identity {name}")
                if not check["pass"] and "error" in check:
                    print(f"  {check['error']}")
            for name, check in report["executions"].items():
                print(f"{'PASS' if check['pass'] else 'FAIL'} execution {name}")
            print(f"analysis toolchain: {'READY' if report['ready'] else 'NOT READY'}")
            print(f"receipt: {output}")
        return 0 if report["ready"] else 1
    except (AnalysisError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"error: analysis toolchain attestation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
