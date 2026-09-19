#!/usr/bin/env python3
"""Inventory and validate the temporary compat/rec98 migration boundary."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SUFFIXES = {".c", ".cpp", ".h", ".hpp", ".inl"}
FORBIDDEN_PREFIXES = ("libs/", "platform/", "th01/", "th02/", "th03/", "th05/")
INCLUDE = re.compile(r'^\s*#\s*include\s+"([^"\r\n]+)"')


def origin(header: str) -> str:
    parts = header.split("/")
    if parts[:2] == ["libs", "master.lib"]:
        return "libs/master.lib"
    return parts[0]


def audit(root: Path) -> dict[str, object]:
    uses: dict[str, list[dict[str, object]]] = defaultdict(list)
    direct_forbidden: list[dict[str, object]] = []
    source_root = root / "src"
    for path in sorted(source_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            match = INCLUDE.match(line)
            if not match:
                continue
            include = match.group(1)
            if include.startswith("compat/rec98/"):
                header = include.removeprefix("compat/rec98/")
                uses[header].append({"source": relative, "line": line_number})
            elif include.startswith(FORBIDDEN_PREFIXES):
                direct_forbidden.append(
                    {"source": relative, "line": line_number, "include": include}
                )

    compat_root = root / "compat" / "rec98"
    forwarders: dict[str, Path] = {}
    invalid_forwarders: list[dict[str, str]] = []
    if compat_root.is_dir():
        for path in sorted(compat_root.rglob("*")):
            if not path.is_file() or path.name == "README.md":
                continue
            relative = path.relative_to(compat_root).as_posix()
            forwarders[relative] = path
            expected = f'#include "{relative}"\n'
            if path.is_symlink() or path.read_text(encoding="utf-8") != expected:
                invalid_forwarders.append(
                    {"header": relative, "expected": expected.rstrip("\n")}
                )

    forwarder_names = set(forwarders)
    used_names = set(uses)
    headers = [
        {
            "header": header,
            "origin": origin(header),
            "include_sites": len(sites),
            "source_files": len({str(site["source"]) for site in sites}),
            "sites": sites,
        }
        for header, sites in sorted(
            uses.items(), key=lambda item: (-len(item[1]), item[0])
        )
    ]
    origins = Counter(origin(header) for header in forwarder_names)
    source_files = {
        str(site["source"]) for sites in uses.values() for site in sites
    }
    return {
        "forwarders": len(forwarder_names),
        "include_sites": sum(len(sites) for sites in uses.values()),
        "source_files": len(source_files),
        "origins": dict(sorted(origins.items())),
        "headers": headers,
        "missing_forwarders": sorted(used_names - forwarder_names),
        "orphan_forwarders": sorted(forwarder_names - used_names),
        "invalid_forwarders": invalid_forwarders,
        "direct_forbidden_includes": direct_forbidden,
    }


def print_text(report: dict[str, object]) -> None:
    print(f"compat/rec98 forwarders: {report['forwarders']}")
    print(
        "product include sites: "
        f"{report['include_sites']} in {report['source_files']} source files"
    )
    origins = report["origins"]
    print("origins: " + ", ".join(f"{key}={value}" for key, value in origins.items()))
    print("most-used forwarders:")
    for item in report["headers"][:12]:
        print(
            f"  {item['include_sites']:>3}  {item['header']} "
            f"({item['source_files']} files)"
        )
    for key in (
        "missing_forwarders",
        "orphan_forwarders",
        "invalid_forwarders",
        "direct_forbidden_includes",
    ):
        values = report[key]
        print(f"{key.replace('_', ' ')}: {len(values)}")
        for value in values:
            print(f"  {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--check", action="store_true", help="fail on broken, direct, or unused adapters"
    )
    parser.add_argument(
        "--require-zero",
        action="store_true",
        help="fail until all compat/rec98 product dependencies are removed",
    )
    args = parser.parse_args()
    report = audit(ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    broken = any(
        report[key]
        for key in (
            "missing_forwarders",
            "orphan_forwarders",
            "invalid_forwarders",
            "direct_forbidden_includes",
        )
    )
    if args.require_zero and (report["forwarders"] or report["include_sites"]):
        return 1
    if args.check and broken:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
