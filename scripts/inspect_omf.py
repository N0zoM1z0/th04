#!/usr/bin/env python3
"""Validate an Intel OMF object and emit a machine-readable record inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from lib.omf import OMFError, describe_omf


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("object", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = describe_omf(args.object.read_bytes())
    except (OSError, OMFError) as error:
        print(f"OMF FAIL: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"OMF PASS: {args.object} ({report['size']} bytes, "
            f"{report['record_count']} records, module={report['module_name']!r})"
        )
        for name, count in report["record_counts"].items():
            print(f"  {name}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

