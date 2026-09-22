#!/usr/bin/env python3
"""Test semantically equivalent if/else organizations for TH04 ZUN _main."""

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
TARGET_SIZE = 0xFC
TARGET_SHA256 = base.TARGET_MAIN_SHA256
EXPECTED = {'both': (246, '24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea'),
 'resident_else': (246, '24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea'),
 'separate_d_if': (246, '24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea')}

OPTION_OLD = """        } else if(arg_is(argv[1], 'D', 'd')) {
            debug = 1;
        } else {
            dos_puts2("そんなオプション付けられても、困るんですけど\n\n");
            return 1;
        }
"""
OPTION_NEW = """        }
        if(arg_is(argv[1], 'D', 'd')) {
            debug = 1;
        } else {
            dos_puts2("そんなオプション付けられても、困るんですけど\n\n");
            return 1;
        }
"""
RESIDENT_OLD = """    if(seg) {
        dos_puts2("わたし、すでにいますよぉ\n\n");
        return 1;
    }

    seg = ResData<resident_t>::create_with_id_from_pointer(res_id);
    if(!seg) {
        dos_puts2("作れません、わたしの居場所がないの！\n\n");
        return 1;
    }
"""
RESIDENT_NEW = """    if(seg) {
        dos_puts2("わたし、すでにいますよぉ\n\n");
        return 1;
    } else {
        seg = ResData<resident_t>::create_with_id_from_pointer(res_id);
        if(!seg) {
            dos_puts2("作れません、わたしの居場所がないの！\n\n");
            return 1;
        }
    }
"""


def replace_once(source: str, before: str, after: str) -> str:
    if source.count(before) != 1:
        raise RuntimeError("maintained source structural anchor drift")
    return source.replace(before, after, 1)


def variants(source: str) -> dict[str, str]:
    separate = replace_once(source, OPTION_OLD, OPTION_NEW)
    resident = replace_once(source, RESIDENT_OLD, RESIDENT_NEW)
    return {
        "separate_d_if": separate,
        "resident_else": resident,
        "both": replace_once(separate, RESIDENT_OLD, RESIDENT_NEW),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(x for x in manifest["artifacts"] if x["id"] == "th04-zun")
    packed = (ROOT / target_info["private_path"]).read_bytes()
    payload = base.PAYLOAD.read_bytes()
    target = payload[0xE67:0xF63]
    if len(packed) != target_info["size"] or base.sha(packed) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target identity drift")
    if base.sha(payload) != base.PAYLOAD_SHA256 or base.sha(target) != TARGET_SHA256:
        raise RuntimeError("decoded target _main identity drift")

    subprocess.run(
        [sys.executable, "scripts/attest_toolchain.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    output.mkdir()
    source = SOURCE.read_text(encoding="utf-8")
    results = {}
    for name, candidate in variants(source).items():
        a = base.compile_one(name, "a", candidate, output)
        b = base.compile_one(name, "b", candidate, output)
        if a != b:
            raise RuntimeError(f"{name}: cold A/B output drift")
        code = (output / name / "a" / "main.code").read_bytes()
        row = {
            "source_sha256": base.sha(candidate.encode("cp932")),
            "code_size": len(code),
            "code_sha256": base.sha(code),
            "raw_equal": code == target,
            "build": a,
        }
        if (row["code_size"], row["code_sha256"]) != EXPECTED[name]:
            raise RuntimeError(f"{name}: structural-if output drift")
        if row["code_size"] == TARGET_SIZE or row["raw_equal"]:
            raise RuntimeError(f"{name}: structural-if route unexpectedly reached target")
        results[name] = row

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "semantic if/else organization negatives for TH04 ZUN _main",
        "target_sha256": target_info["sha256"],
        "target_main_size": TARGET_SIZE,
        "target_main_sha256": TARGET_SHA256,
        "maintained_source_sha256": base.sha(SOURCE.read_bytes()),
        "results": results,
        "all_fail_size_gate": True,
        "conclusion": (
            "Separating the D-option test from the R branch, wrapping create logic in "
            "the resident else branch, and combining both semantically equivalent "
            "organizations all remain nonexact. None recovers the 252-byte target."
        ),
        "limit": (
            "This closes only the three enumerated control-flow organizations. It does "
            "not prove the original source form or justify inert optimizer barriers."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v["code_size"] for k, v in results.items()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
