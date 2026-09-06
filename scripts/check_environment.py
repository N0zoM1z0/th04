#!/usr/bin/env python3
"""Report available ingestion, analysis, build, and runtime tools."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys


TOOLS = {
    "ingestion": ["unar", "mcopy", "mdir"],
    "static": ["ndisasm", "objdump", "analyzeHeadless", "idat", "idat64"],
    "build": ["wine", "tup", "TCC.EXE", "TASM32.EXE", "TLINK.EXE"],
    "runtime": ["dosbox-x", "dosbox", "qemu-system-i386", "np21w"],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = {
        group: {tool: shutil.which(tool) for tool in tools}
        for group, tools in TOOLS.items()
    }
    capabilities = {
        "target_import": all(report["ingestion"][tool] for tool in ("unar", "mcopy")),
        "basic_disassembly": bool(
            report["static"]["ndisasm"] or report["static"]["objdump"]
        ),
        "headless_database": bool(
            report["static"]["analyzeHeadless"]
            or report["static"]["idat"]
            or report["static"]["idat64"]
        ),
        "exact_toolchain": all(
            report["build"][tool]
            for tool in ("TCC.EXE", "TASM32.EXE", "TLINK.EXE")
        ),
        "pc98_runtime": bool(report["runtime"]["dosbox-x"] or report["runtime"]["np21w"]),
    }
    output = {"schema_version": 1, "tools": report, "capabilities": capabilities}
    if args.json:
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        for capability, available in capabilities.items():
            print(f"{'YES' if available else 'NO ':3} {capability}")
        missing = [
            tool
            for group in report.values()
            for tool, path in group.items()
            if path is None
        ]
        print("missing/undiscovered: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
