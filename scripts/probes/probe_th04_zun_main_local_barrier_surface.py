#!/usr/bin/env python3
"""Close bounded natural-local and non-optimizer profile routes for ZUN _main."""

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

BASE_FLAGS = (
    "-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-mt",
    "-nobj/th04/",
)

PROFILE_VARIANTS = {
    "baseline": (),
    "r_on": ("-r",),
    "r_off": ("-r-",),
    "k_on": ("-k",),
    "k_off": ("-k-",),
    "N_on": ("-N",),
    "N_off": ("-N-",),
    "r_on_k_on": ("-r", "-k"),
    "r_off_k_on": ("-r-", "-k"),
    "r_on_k_off": ("-r", "-k-"),
}

EXPECTED_PROFILE = {
    "baseline": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
    "r_on": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
    "r_off": (293, "4ee3f2813a010b4eaf9aed35b520bd0006561a78a594e1e7bac789c0a851e4b6"),
    "k_on": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
    "k_off": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
    "N_on": (255, "398c58164ea5f91d9f3acb01e861a483dcc103fe297eddbe69053c974466db2b"),
    "N_off": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
    "r_on_k_on": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
    "r_off_k_on": (293, "4ee3f2813a010b4eaf9aed35b520bd0006561a78a594e1e7bac789c0a851e4b6"),
    "r_on_k_off": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
}

EXPECTED_SCOPED = {
    "scoped_message_both": (256, "647d6dbd462ae8f7fc687dd21bd0236beb4d8e3cca86dee72f7fbf3538a0e543"),
    "scoped_const_result_both": (256, "c023ada4f7d32cc6f080b2cca0cc43a477ce8e3ec96f031dacb37e964c3aeba9"),
    "scoped_register_const_result_both": (267, "172feab50d09ba05f2708e8929635ccc76592383553890890997d25e76105beb"),
}


def scoped_variants(source: str) -> dict[str, str]:
    bad_message = (
        '            const char *message = "そんなオプション付けられても、困るんですけど\\n\\n";\n'
        '            dos_puts2(message);\n'
        '            return 1;'
    )
    already_message = (
        '        const char *message = "わたし、すでにいますよぉ\\n\\n";\n'
        '        dos_puts2(message);\n'
        '        return 1;'
    )
    bad_result = (
        '            const int result = 1;\n'
        '            dos_puts2("そんなオプション付けられても、困るんですけど\\n\\n");\n'
        '            return result;'
    )
    already_result = (
        '        const int result = 1;\n'
        '        dos_puts2("わたし、すでにいますよぉ\\n\\n");\n'
        '        return result;'
    )
    bad_register = bad_result.replace("const int result", "register const int result")
    already_register = already_result.replace("const int result", "register const int result")

    result = {}
    for name, bad, already in (
        ("scoped_message_both", bad_message, already_message),
        ("scoped_const_result_both", bad_result, already_result),
        ("scoped_register_const_result_both", bad_register, already_register),
    ):
        candidate = base.replace_once(source, base.BAD, bad)
        candidate = base.replace_once(candidate, base.ALREADY, already)
        result[name] = candidate
    return result


def compile_twice(
    name: str, source: str, output: Path, flags: tuple[str, ...]
) -> dict[str, object]:
    old_flags = base.FLAGS
    try:
        base.FLAGS = flags
        a = base.compile_one(name, "a", source, output)
        b = base.compile_one(name, "b", source, output)
    finally:
        base.FLAGS = old_flags
    if a != b:
        raise RuntimeError(f"{name}: cold A/B result differs")
    code = output / name / "a" / "main.code"
    code_data = code.read_bytes()
    return {
        "flags": list(flags),
        "source_sha256": base.sha(source.encode("cp932")),
        "code_size": len(code_data),
        "code_sha256": base.sha(code_data),
        "raw_equal": len(code_data) == TARGET_SIZE and base.sha(code_data) == TARGET_SHA256,
        "build": a,
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

    profiles = {}
    for name, extra in PROFILE_VARIANTS.items():
        flags = BASE_FLAGS[:-1] + extra + (BASE_FLAGS[-1],)
        row = compile_twice(name, source, output, flags)
        expected = EXPECTED_PROFILE[name]
        if (row["code_size"], row["code_sha256"]) != expected:
            raise RuntimeError(f"{name}: profile output drift")
        if row["raw_equal"]:
            raise RuntimeError(f"{name}: profile unexpectedly became exact")
        profiles[name] = row

    scoped = {}
    for name, candidate in scoped_variants(source).items():
        row = compile_twice(name, candidate, output, BASE_FLAGS)
        expected = EXPECTED_SCOPED[name]
        if (row["code_size"], row["code_sha256"]) != expected:
            raise RuntimeError(f"{name}: scoped-local output drift")
        if row["raw_equal"]:
            raise RuntimeError(f"{name}: scoped-local form unexpectedly became exact")
        scoped[name] = row

    if any(row["code_size"] == TARGET_SIZE for row in [*profiles.values(), *scoped.values()]):
        raise RuntimeError("local barrier surface unexpectedly reached target size")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "bounded natural-local and non-optimizer-profile negatives for ZUN _main",
        "target_sha256": target_info["sha256"],
        "target_main_extent": "decoded ZUN.COM 0xE67..0xF62",
        "target_main_size": TARGET_SIZE,
        "target_main_sha256": TARGET_SHA256,
        "maintained_source_sha256": base.sha(SOURCE.read_bytes()),
        "profiles": profiles,
        "scoped_locals": scoped,
        "all_fail_size_gate": True,
        "conclusion": (
            "Register-variable, stack-frame/name-profile toggles and three real scoped-local "
            "forms fail to recover the 252-byte target _main. Scoped message/result variants "
            "materialize extra locals and remain nonexact; no tested form supplies the two "
            "missing unmerged dos_puts2 calls without unrelated code growth."
        ),
        "limit": (
            "This closes only the enumerated source/profile surface. It does not prove the "
            "original source shape and does not justify ReC98's inert self-assignment barriers."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "profiles": {k: v["code_size"] for k, v in profiles.items()},
        "scoped_locals": {k: v["code_size"] for k, v in scoped.items()},
        "receipt": str(path),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
