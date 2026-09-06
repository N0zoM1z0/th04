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
ANALYSIS_CONFIG = ROOT / "config" / "analysis_toolchain.toml"
TARGET_CONFIG = ROOT / "config" / "targets.toml"
ANALYSIS_RECEIPT = ROOT / ".analysis" / "ghidra" / "toolchain-attestation.json"
DATABASE_RECEIPTS = ROOT / ".analysis" / "ghidra" / "database-attestations"


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
    local_analyzer = ROOT / ".tools" / "ghidra" / "support" / "analyzeHeadless"
    if local_analyzer.is_file():
        report["static"]["analyzeHeadless"] = str(local_analyzer.resolve())
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
        "identity_current": all(
            item["pass"] or not item["required"] for item in surface_reports
        ),
        "failed_required_surfaces": [
            item["id"]
            for item in surface_reports
            if item["required"] and not item["pass"]
        ],
        "different_optional_surfaces": [
            item["id"]
            for item in surface_reports
            if not item["required"] and not item["pass"]
        ],
    }
    toolchain_candidate["ready"] = all(
        toolchain_candidate[key]
        for key in ("receipt_ready", "manifest_current", "identity_current")
    )
    analysis_receipt: dict[str, object] = {}
    try:
        analysis_receipt = json.loads(ANALYSIS_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    analysis_candidate = {
        "receipt": str(ANALYSIS_RECEIPT.relative_to(ROOT)),
        "receipt_ready": analysis_receipt.get("ready") is True,
        "manifest_current": analysis_receipt.get("manifest_sha256")
        == digest_file(ANALYSIS_CONFIG),
        "analyzer_present": local_analyzer.is_file(),
    }
    analysis_candidate["ready"] = all(
        analysis_candidate[key]
        for key in ("receipt_ready", "manifest_current", "analyzer_present")
    )
    database_receipts = []
    if DATABASE_RECEIPTS.is_dir():
        for path in sorted(DATABASE_RECEIPTS.glob("*.json")):
            try:
                receipt = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if (
                receipt.get("ready") is True
                and receipt.get("analysis_manifest_sha256") == digest_file(ANALYSIS_CONFIG)
                and receipt.get("target_manifest_sha256") == digest_file(TARGET_CONFIG)
            ):
                database_receipts.append(str(receipt.get("artifact_id")))
    capabilities = {
        "target_import": all(report["ingestion"][tool] for tool in ("unar", "mcopy")),
        "basic_disassembly": bool(
            report["static"]["ndisasm"] or report["static"]["objdump"]
        ),
        "headless_database": analysis_candidate["ready"] and bool(database_receipts),
        "attested_analysis_toolchain": analysis_candidate["ready"],
        "attested_toolchain_candidate": toolchain_candidate["ready"],
        "pc98_runtime": bool(report["runtime"]["dosbox-x"] or report["runtime"]["np21w"]),
    }
    output = {
        "schema_version": 2,
        "tools": report,
        "toolchain_candidate": toolchain_candidate,
        "analysis_toolchain": analysis_candidate,
        "attested_databases": database_receipts,
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
