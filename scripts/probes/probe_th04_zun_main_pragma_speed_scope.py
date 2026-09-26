#!/usr/bin/env python3
"""Probe function and inner-statement #pragma option -G scope in ZUN _main."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

PROBE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROBE_DIR))

import probe_th04_zun_main_branch_shapes as base
import probe_th04_zun_main_optimizer_profile as opt

ROOT = base.ROOT
TARGET_START = 0xE67
TARGET_SIZE = 252
TARGET_SHA = base.TARGET_MAIN_SHA256


def insert_once(source: str, marker: str, replacement: str) -> str:
    if source.count(marker) != 1:
        raise RuntimeError("maintained ZUN _main marker changed")
    return source.replace(marker, replacement, 1)


def variants(source: str) -> dict[str, str]:
    function = "int main(int argc, const unsigned char **argv)\n"
    bad = base.BAD
    already = base.ALREADY
    file_speed = insert_once(source, function, "#pragma option -G\n" + function)
    inner = insert_once(source, bad, "#pragma option -G\n" + bad)
    restored = insert_once(inner, already, already + "\n#pragma option -G-\n")
    bad_only = insert_once(inner, already, "#pragma option -G-\n" + already)
    return {
        "function_speed": file_speed,
        "inner_speed_restore": restored,
        "inner_speed_no_restore": inner,
        "bad_branch_only": bad_only,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output must be a new direct child of .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(item for item in manifest["artifacts"] if item["id"] == "th04-zun")
    packed = (ROOT / target_info["private_path"]).read_bytes()
    payload = base.PAYLOAD.read_bytes()
    target = payload[TARGET_START:TARGET_START + TARGET_SIZE]
    if base.sha(packed) != target_info["sha256"] or (
        base.sha(payload) != base.PAYLOAD_SHA256 or len(target) != TARGET_SIZE
        or base.sha(target) != TARGET_SHA
    ):
        raise RuntimeError("pinned ZUN packed/decoded target identity drift")
    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm is required")
    if opt.target_fingerprint(opt.disassemble(ndisasm, target, TARGET_START)) != opt.TARGET_FINGERPRINT:
        raise RuntimeError("target selective-tail fingerprint drift")
    source = base.SOURCE.read_text(encoding="utf-8")
    output.mkdir()
    results = {}
    for name, text in variants(source).items():
        a = base.compile_one(name, "a", text, output)
        b = base.compile_one(name, "b", text, output)
        if a != b:
            raise RuntimeError(f"{name}: A/B compiler outputs differ")
        code = (output / name / "a/main.code").read_bytes()
        instructions = opt.disassemble(ndisasm, code, TARGET_START)
        fingerprint = {
            branch: opt.next_after_push(instructions, immediate)
            for branch, immediate in opt.MESSAGE_PUSHES.items()
        }
        results[name] = {
            "source_sha256": base.sha(text.encode("cp932")),
            "object_sha256": a["object_sha256"],
            "code_size": len(code), "code_sha256": base.sha(code),
            "error_tail_fingerprint": fingerprint,
            "target_size_equal": len(code) == TARGET_SIZE,
            "target_tail_equal": fingerprint == opt.TARGET_FINGERPRINT,
        }
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "natural-source local -G compiler scope for ZUN resident _main",
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": base.PAYLOAD_SHA256,
        "target_main_sha256": TARGET_SHA,
        "target_main_size": TARGET_SIZE,
        "target_error_tail_fingerprint": opt.TARGET_FINGERPRINT,
        "maintained_source_sha256": base.sha(base.SOURCE.read_bytes()),
        "compiler_flags": list(base.FLAGS),
        "ndisasm_sha256": base.sha(Path(ndisasm).read_bytes()),
        "results": results,
        "limit": "Compiler mechanism probe only; no source edit or exact acceptance.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({name: {"size": value["code_size"],
                             "fingerprint": value["error_tail_fingerprint"]}
                      for name, value in results.items()}, ensure_ascii=False))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
