#!/usr/bin/env python3
"""Report available ingestion, analysis, build, and runtime tools."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tomllib

from lib.pc98 import digest_file
from lib.toolchain import attest_surface


ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN_CONFIG = ROOT / "config" / "toolchain.toml"
TOOLCHAIN_RECEIPT = ROOT / ".analysis" / "toolchain" / "attestation.json"


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
    toolchain_config = tomllib.loads(TOOLCHAIN_CONFIG.read_text(encoding="utf-8"))
    surface_reports = [
        attest_surface(ROOT, surface) for surface in toolchain_config["surfaces"]
    ]
    receipt: dict[str, object] = {}
    try:
        receipt = json.loads(TOOLCHAIN_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    toolchain_candidate = {
        "receipt": str(TOOLCHAIN_RECEIPT.relative_to(ROOT)),
        "receipt_ready": receipt.get("ready") is True,
        "manifest_current": receipt.get("manifest_sha256")
        == digest_file(TOOLCHAIN_CONFIG),
        "identity_current": all(item["pass"] for item in surface_reports),
        "failed_surfaces": [item["id"] for item in surface_reports if not item["pass"]],
    }
    toolchain_candidate["ready"] = all(
        toolchain_candidate[key]
        for key in ("receipt_ready", "manifest_current", "identity_current")
    )
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
        "attested_toolchain_candidate": toolchain_candidate["ready"],
        "pc98_runtime": bool(report["runtime"]["dosbox-x"] or report["runtime"]["np21w"]),
    }
    output = {
        "schema_version": 2,
        "tools": report,
        "toolchain_candidate": toolchain_candidate,
        "capabilities": capabilities,
    }
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
        print("missing/undiscovered on host PATH: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
