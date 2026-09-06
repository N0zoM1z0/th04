#!/usr/bin/env python3
"""Verify private targets against the checked-in manifest and MZ invariants."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tomllib

from lib.pc98 import classify_format, describe_blob, digest_file


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game", choices=("th01", "th02", "th03", "th04", "th05", "all"), default="th04"
    )
    parser.add_argument(
        "--allow-missing-optional",
        action="store_true",
        help="skip absent artifacts whose manifest required flag is false",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    manifest = tomllib.loads(
        (ROOT / "config" / "targets.toml").read_text(encoding="utf-8")
    )
    selected = [
        item
        for item in manifest["artifacts"]
        if args.game == "all" or item["game"] == args.game
    ]
    reports: list[dict[str, object]] = []
    failed = False
    for artifact in selected:
        path = ROOT / artifact["private_path"]
        report: dict[str, object] = {
            "id": artifact["id"],
            "path": artifact["private_path"],
            "present": path.is_file(),
            "required": artifact["required"],
        }
        if not path.is_file():
            optional_skip = not artifact["required"] and args.allow_missing_optional
            report["ok"] = optional_skip
            report["skipped"] = optional_skip
            reports.append(report)
            failed |= not optional_skip
            continue
        data = path.read_bytes()
        description = describe_blob(data)
        checks = {
            "size": len(data) == artifact["size"],
            "sha256": description["sha256"] == artifact["sha256"],
            "md5": description["md5"] == artifact["md5"],
            "format": classify_format(data) == artifact["format"],
            "format_integrity": description["format_integrity"]["valid"],
        }
        report.update({"ok": all(checks.values()), "checks": checks, **description})
        reports.append(report)
        failed |= not report["ok"]

    output = {
        "schema_version": 1,
        "game": args.game,
        "canonicality": manifest["source"]["canonicality"],
        "ok": not failed,
        "artifacts": reports,
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for report in reports:
            state = "OK" if report["ok"] else "FAIL"
            suffix = " (missing optional)" if report.get("skipped") else ""
            print(f"{state:4} {report['id']}{suffix}")
        print(
            f"target verification: {'PASS' if output['ok'] else 'FAIL'}; "
            f"canonicality={output['canonicality']}"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
