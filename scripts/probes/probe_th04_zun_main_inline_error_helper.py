#!/usr/bin/env python3
"""Test genuine error-print helper inlining in the ZUN resident main."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tomllib

import probe_th04_zun_main_branch_shapes as base


ROOT = base.ROOT
SOURCE = base.SOURCE
TARGET_SHA256 = base.TARGET_MAIN_SHA256


def replace_once(source: str, before: str, after: str) -> str:
    if source.count(before) != 1:
        raise RuntimeError("maintained resident source anchor drift")
    return source.replace(before, after, 1)


def variants(source: str) -> dict[str, str]:
    int_helper = (
        "static inline int near print_error(const char *message)\n"
        "{\n    dos_puts2(message);\n    return 1;\n}\n\n"
    )
    void_helper = (
        "static inline void near print_error(const char *message)\n"
        "{\n    dos_puts2(message);\n}\n\n"
    )
    bad_int = base.BAD.replace("dos_puts2(", "return print_error(").replace(
        "\n            return 1;", ""
    )
    already_int = base.ALREADY.replace("dos_puts2(", "return print_error(").replace(
        "\n        return 1;", ""
    )
    both_int = replace_once(replace_once(source, base.BAD, bad_int),
                            base.ALREADY, already_int)
    both_void = replace_once(
        replace_once(source, base.BAD, base.BAD.replace("dos_puts2(", "print_error(")),
        base.ALREADY, base.ALREADY.replace("dos_puts2(", "print_error("),
    )
    bad_only = replace_once(source, base.BAD, bad_int)
    already_only = replace_once(source, base.ALREADY, already_int)
    return {
        "inline_int_both": replace_once(both_int, "int main(", int_helper + "int main("),
        "inline_void_both": replace_once(both_void, "int main(", void_helper + "int main("),
        "inline_int_bad_only": replace_once(bad_only, "int main(", int_helper + "int main("),
        "inline_int_already_only": replace_once(already_only, "int main(", int_helper + "int main("),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output must be new directly below .analysis/reconstruction/probes")
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(x for x in manifest["artifacts"] if x["id"] == "th04-zun")
    packed = (ROOT / target_info["private_path"]).read_bytes()
    payload = base.PAYLOAD.read_bytes()
    target = payload[0xE67:0xF63]
    if (len(packed) != target_info["size"] or
            base.sha(packed) != target_info["sha256"] or
            base.sha(payload) != base.PAYLOAD_SHA256 or
            base.sha(target) != TARGET_SHA256):
        raise RuntimeError("pinned ZUN target identity drift")
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    source = SOURCE.read_text(encoding="utf-8")
    output.mkdir()
    results = {}
    for name, candidate in variants(source).items():
        a = base.compile_one(name, "a", candidate, output)
        b = base.compile_one(name, "b", candidate, output)
        if a != b:
            raise RuntimeError(f"{name}: cold A/B output drift")
        code = (output / name / "a" / "main.code").read_bytes()
        results[name] = {
            "source_sha256": base.sha(candidate.encode("cp932")),
            "code_size": len(code),
            "code_sha256": base.sha(code),
            "raw_equal_target_main": code == target,
            "build": a,
        }
        print(f"{name}: {len(code)} CODE bytes, raw_equal={code == target}")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "ZUN resident main genuine inline error helper codegen surface",
        "target_sha256": target_info["sha256"],
        "target_main_extent": "decoded payload 0xE67..0xF62",
        "target_main_sha256": TARGET_SHA256,
        "maintained_source_sha256": base.sha(SOURCE.read_bytes()),
        "header_sha256": {path: base.sha((ROOT / path).read_bytes()) for path in base.HEADERS},
        "flags": list(base.FLAGS),
        "results": results,
        "limit": "Source-only compiler probe; no resident link or exact promotion.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
