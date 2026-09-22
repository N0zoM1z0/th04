#!/usr/bin/env python3
"""Close the #pragma option -O- scope route for TH04 ZUN resident _main."""

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
TARGET_SIZE = 0xFC
TARGET_SHA256 = base.TARGET_MAIN_SHA256
TARGET_FINGERPRINT = {
    "not_resident": "jmp",
    "bad_option": "call",
    "already_resident": "call",
    "no_space": "call",
}
EXPECTED = {
    "file_no_jump": (
        248,
        "28f26e6f6ac85ed09aeb844df72d84edf6109651e8310c443fb92fc5621854f6",
        {"not_resident": "jmp", "bad_option": "jmp",
         "already_resident": "jmp", "no_space": "call"},
    ),
    "inner_no_jump_restore": (
        246,
        "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea",
        {"not_resident": "jmp", "bad_option": "jmp",
         "already_resident": "jmp", "no_space": "call"},
    ),
    "inner_no_jump_no_restore": (
        248,
        "28f26e6f6ac85ed09aeb844df72d84edf6109651e8310c443fb92fc5621854f6",
        {"not_resident": "jmp", "bad_option": "jmp",
         "already_resident": "jmp", "no_space": "call"},
    ),
}


def source_variants(source: str) -> dict[str, str]:
    file_no_jump = source.replace(
        "int main(int argc, const unsigned char **argv)\n",
        "#pragma option -O-\nint main(int argc, const unsigned char **argv)\n",
        1,
    )

    bad = (
        '            dos_puts2("そんなオプション付けられても、困るんですけど\\n\\n");\n'
    )
    already = (
        '        dos_puts2("わたし、すでにいますよぉ\\n\\n");\n'
        "        return 1;\n"
    )
    if source.count(bad) != 1 or source.count(already) != 1:
        raise RuntimeError("maintained _main error branches changed")

    inner_restore = source.replace(
        bad, "#pragma option -O-\n" + bad, 1
    ).replace(
        already, already + "#pragma option -O.\n", 1
    )
    inner_no_restore = source.replace(
        bad, "#pragma option -O-\n" + bad, 1
    )
    return {
        "file_no_jump": file_no_jump,
        "inner_no_jump_restore": inner_restore,
        "inner_no_jump_no_restore": inner_no_restore,
    }


def compile_variant(
    name: str,
    source: str,
    output: Path,
    ndisasm: str,
) -> dict[str, object]:
    a = base.compile_one(name, "a", source, output)
    b = base.compile_one(name, "b", source, output)
    if a != b:
        raise RuntimeError(f"{name}: cold compiler rounds differ")
    code_path = output / name / "a" / "main.code"
    code = code_path.read_bytes()
    instructions = opt.disassemble(ndisasm, code, TARGET_START)
    fingerprint = {
        branch: opt.next_after_push(instructions, immediate)
        for branch, immediate in opt.MESSAGE_PUSHES.items()
    }
    (output / name / "a" / "main.ndisasm").write_text(
        "\n".join(str(item["text"]) for item in instructions) + "\n",
        encoding="ascii",
    )

    expected_size, expected_sha, expected_fp = EXPECTED[name]
    if (
        len(code) != expected_size
        or base.sha(code) != expected_sha
        or fingerprint != expected_fp
    ):
        raise RuntimeError(
            f"{name}: pragma optimizer behavior drift: "
            f"{len(code)} {base.sha(code)} {fingerprint!r}"
        )
    if len(code) == TARGET_SIZE and base.sha(code) == TARGET_SHA256:
        raise RuntimeError(f"{name}: unexpected target-exact result")
    if fingerprint == TARGET_FINGERPRINT:
        raise RuntimeError(f"{name}: unexpected target selective tail fingerprint")
    return {
        "source_sha256": base.sha(source.encode("cp932")),
        "code_size": len(code),
        "code_sha256": base.sha(code),
        "error_tail_fingerprint": fingerprint,
        "build": a,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error(
            "output directory must be new directly below .analysis/reconstruction/probes"
        )

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    manifest = tomllib.loads((ROOT / "config/targets.toml").read_text())
    target_info = next(
        item for item in manifest["artifacts"] if item["id"] == "th04-zun"
    )
    packed = (ROOT / target_info["private_path"]).read_bytes()
    payload = base.PAYLOAD.read_bytes()
    target = payload[TARGET_START:TARGET_START + TARGET_SIZE]
    if len(packed) != target_info["size"] or base.sha(packed) != target_info["sha256"]:
        raise RuntimeError("pinned packed ZUN target changed")
    if base.sha(base.PAYLOAD.read_bytes()) != base.PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload changed")
    if len(target) != TARGET_SIZE or base.sha(target) != TARGET_SHA256:
        raise RuntimeError("target _main identity drift")

    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm is required")
    target_ins = opt.disassemble(ndisasm, target, TARGET_START)
    if opt.target_fingerprint(target_ins) != TARGET_FINGERPRINT:
        raise RuntimeError("target _main error-tail fingerprint drift")

    source = base.SOURCE.read_text(encoding="utf-8")
    variants = source_variants(source)
    output.mkdir(parents=True)
    results = {
        name: compile_variant(name, candidate, output, ndisasm)
        for name, candidate in variants.items()
    }

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": (
            "TH04 ZUN _main #pragma option -O- scope surface; "
            "negative exactness result"
        ),
        "target_sha256": target_info["sha256"],
        "target_payload_sha256": base.PAYLOAD_SHA256,
        "target_main_size": TARGET_SIZE,
        "target_main_sha256": TARGET_SHA256,
        "target_error_tail_fingerprint": TARGET_FINGERPRINT,
        "source_sha256": base.sha(base.SOURCE.read_bytes()),
        "compiler_flags": list(base.FLAGS),
        "variants": results,
        "conclusion": (
            "A file-boundary #pragma option -O- exactly reproduces the already-known "
            "248-byte no-jump-optimization build. A pragma restored inside _main has "
            "no effect on the current function and reproduces the 246-byte baseline; "
            "leaving it unrestored affects later compiler state enough to reproduce "
            "the same 248-byte build, but neither inner spelling changes the target "
            "error-call fingerprint. No pragma scope tested here restores the two "
            "missing dos_puts2 calls."
        ),
        "limit": (
            "This closes only the legal #pragma option -O- scope route. It does not "
            "prove the original source spelling and grants no exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(json.dumps(
        {
            name: {
                "size": row["code_size"],
                "fingerprint": row["error_tail_fingerprint"],
            }
            for name, row in results.items()
        },
        ensure_ascii=False,
        sort_keys=True,
    ))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
