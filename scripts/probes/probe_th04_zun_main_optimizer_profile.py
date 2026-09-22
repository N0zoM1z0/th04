#!/usr/bin/env python3
"""Bound the supported TC4J optimizer/debug profile surface for TH04 ZUN _main."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay_th04_zun_cfg_init import code
from replay_th04_zun_source_only import (
    FLAGS, PAYLOAD, PAYLOAD_SHA256, ROOT, RUNNER, sha, source_closure,
)

SOURCE_RELATIVE = "src/zun/resident/main.cpp"
TARGET_START = 0xE67
TARGET_SIZE = 0xFC
TARGET_SHA256 = "db04398b52ca5780c734f839e2cf3768718f7f7c65705a9cdb9e88e34aa64871"
TARGET_FINGERPRINT = {
    "not_resident": "jmp",
    "bad_option": "call",
    "already_resident": "call",
    "no_space": "call",
}
MESSAGE_PUSHES = {
    "not_resident": "0x58",
    "bad_option": "0x92",
    "already_resident": "0xc1",
    "no_space": "0xdc",
}
EXPECTED = {
    "baseline": (246, "24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea"),
    "no_jump_opt": (248, "28f26e6f6ac85ed09aeb844df72d84edf6109651e8310c443fb92fc5621854f6"),
    "speed": (280, "382ec71d1a32523aa9b85c4ca4126cb475d6d951a843e1ac458edf547cab6cf3"),
    "no_reload_suppression": (258, "0cca90b189eac6aa5c0baa3674d31d69a72996b8ac32d3581cb7e99c4daef5b8"),
    "source_debug": (254, "87ef59647d469a22950596e9d1b2b1f51ca1b670bff2f7ae60f772a0621a6d66"),
    "line_numbers": (256, "4a89ae50be1be1b77587529264f8e719967ddf24eb5d51c785d20d6e23171f41"),
    "line_no_jump_opt": (260, "fe6fdab1b7f51b6b2081f2f0af816fd0c6ae0ffb2cbd20e62ff81a3319e6343e"),
}


def profile_flags(name: str) -> tuple[str, ...]:
    flags = list(FLAGS)
    if name == "no_jump_opt":
        flags[flags.index("-O")] = "-O-"
    elif name == "speed":
        flags.insert(flags.index("-O"), "-G")
    elif name == "no_reload_suppression":
        flags[flags.index("-Z")] = "-Z-"
    elif name == "source_debug":
        flags.insert(-1, "-v")
    elif name == "line_numbers":
        flags.insert(-1, "-y")
    elif name == "line_no_jump_opt":
        flags[flags.index("-O")] = "-O-"
        flags.insert(-1, "-y")
    elif name != "baseline":
        raise ValueError(f"unknown profile {name}")
    return tuple(flags)


def disassemble(ndisasm: str, code_bytes: bytes, origin: int) -> list[dict[str, object]]:
    completed = subprocess.run(
        [ndisasm, "-b16", f"-o0x{origin:X}", "-"],
        input=code_bytes, capture_output=True, check=True,
    )
    text = completed.stdout.decode("ascii")
    result: list[dict[str, object]] = []
    pattern = re.compile(r"^([0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+([a-z][a-z0-9]*)\s*(.*)$")
    for line in text.splitlines():
        match = pattern.match(line)
        if not match:
            raise RuntimeError(f"unexpected ndisasm line: {line}")
        result.append({
            "address": int(match[1], 16),
            "hex": match[2].lower(),
            "mnemonic": match[3].lower(),
            "operands": match[4].strip().lower(),
            "text": line,
        })
    return result


def next_after_push(instructions: list[dict[str, object]], immediate: str) -> str:
    matches = []
    for index, insn in enumerate(instructions[:-1]):
        if insn["mnemonic"] == "push" and insn["operands"] == f"word {immediate}":
            matches.append(instructions[index + 1]["mnemonic"])
    if len(matches) != 1:
        raise RuntimeError(f"expected one push word {immediate}, got {matches}")
    return str(matches[0])


def target_fingerprint(instructions: list[dict[str, object]]) -> dict[str, str]:
    # These are target-local instruction starts from the reviewed 0xE67..0xF62 body.
    expected = {
        "not_resident": (0xEB0, "push", 0xEB3, "jmp"),
        "bad_option": (0xEE5, "push", 0xEE8, "call"),
        "already_resident": (0xEF1, "push", 0xEF4, "call"),
        "no_space": (0xF09, "push", 0xF0C, "call"),
    }
    by_address = {int(item["address"]): item for item in instructions}
    result = {}
    for name, (push_at, push_op, next_at, next_op) in expected.items():
        if (
            push_at not in by_address or next_at not in by_address
            or by_address[push_at]["mnemonic"] != push_op
            or by_address[next_at]["mnemonic"] != next_op
        ):
            raise RuntimeError(f"target error-tail fingerprint drift at {name}")
        result[name] = next_op
    return result


def compile_profile(
    profile: str,
    label: str,
    output: Path,
    inputs: tuple[str, ...],
    ndisasm: str,
) -> dict[str, object]:
    saved = output / profile / label
    saved.mkdir(parents=True)
    environment = os.environ.copy()
    environment.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    with tempfile.TemporaryDirectory(prefix=f"zun-profile-{profile}-{label}-", dir=output) as temporary:
        work = Path(temporary)
        (work / "obj/th04").mkdir(parents=True)
        for relative in inputs:
            source = ROOT / relative
            destination = work / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            data = (
                source.read_text(encoding="utf-8").encode("cp932")
                if relative.endswith(".cpp")
                else source.read_bytes()
            )
            destination.write_bytes(data)
            os.utime(destination, (946684800, 946684800))
        flags = profile_flags(profile)
        command = ["wine", str(RUNNER), "-e", "-x", "tcc", *flags, SOURCE_RELATIVE]
        completed = subprocess.run(
            command, cwd=work, env=environment,
            capture_output=True, text=True, timeout=120,
        )
        log = saved / "compile.log"
        log.write_text(
            json.dumps(command) + f"\nexit={completed.returncode}\n"
            + completed.stdout + completed.stderr,
            encoding="utf-8",
        )
        obj = work / "obj/th04/main.obj"
        if completed.returncode or not obj.is_file():
            raise RuntimeError(f"{profile}/{label}: compile failed: {log}")
        saved_obj = saved / "main.obj"
        saved_obj.write_bytes(obj.read_bytes())
        compiled = code(saved_obj)
        (saved / "main.code").write_bytes(compiled)
        expected_size, expected_sha = EXPECTED[profile]
        if len(compiled) != expected_size or sha(compiled) != expected_sha:
            raise RuntimeError(f"{profile}/{label}: CODE drift")
        instructions = disassemble(ndisasm, compiled, TARGET_START)
        (saved / "main.ndisasm").write_text(
            "\n".join(str(item["text"]) for item in instructions) + "\n",
            encoding="ascii",
        )
        fingerprint = {
            name: next_after_push(instructions, immediate)
            for name, immediate in MESSAGE_PUSHES.items()
        }
        return {
            "flags": list(flags),
            "object_sha256": sha(saved_obj.read_bytes()),
            "code_size": len(compiled),
            "code_sha256": sha(compiled),
            "error_tail_fingerprint": fingerprint,
            "log_sha256": sha(log.read_bytes()),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    payload = PAYLOAD.read_bytes()
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload identity drift")
    target = payload[TARGET_START:TARGET_START + TARGET_SIZE]
    if len(target) != TARGET_SIZE or sha(target) != TARGET_SHA256:
        raise RuntimeError("target _main identity drift")

    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm is required")
    ndisasm_sha = sha(Path(ndisasm).read_bytes())
    target_instructions = disassemble(ndisasm, target, TARGET_START)
    target_tail = target_fingerprint(target_instructions)
    if target_tail != TARGET_FINGERPRINT:
        raise RuntimeError("target selective error-tail fingerprint drift")

    manifest = tomllib.loads((ROOT / "config/toolchain.toml").read_text(encoding="utf-8"))
    tcc = next(item for item in manifest["surfaces"] if item["id"] == "active-tcc")
    if sha((ROOT / tcc["path"]).read_bytes()) != tcc["sha256"]:
        raise RuntimeError("active TC4J identity drift")

    inputs = source_closure(ROOT, (SOURCE_RELATIVE,))
    input_hashes = {relative: sha((ROOT / relative).read_bytes()) for relative in inputs}
    output.mkdir()
    results: dict[str, object] = {}
    for profile in EXPECTED:
        a = compile_profile(profile, "a", output, inputs, ndisasm)
        b = compile_profile(profile, "b", output, inputs, ndisasm)
        if a != b:
            raise RuntimeError(f"{profile}: cold rounds disagree")
        if a["code_size"] == TARGET_SIZE or a["error_tail_fingerprint"] == TARGET_FINGERPRINT:
            raise RuntimeError(f"{profile}: expected negative unexpectedly reached target fingerprint")
        results[profile] = a

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 ZUN _main supported TC4J optimizer/debug profile surface; negative exactness result",
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_main_sha256": TARGET_SHA256,
        "target_main_size": TARGET_SIZE,
        "target_error_tail_fingerprint": target_tail,
        "source_input_sha256": input_hashes,
        "tcc_sha256": tcc["sha256"],
        "runner_sha256": sha(RUNNER.read_bytes()),
        "ndisasm_path": ndisasm,
        "ndisasm_sha256": ndisasm_sha,
        "profiles": results,
        "conclusion": (
            "No supported profile tested here reproduces both the 252-byte target size "
            "and its selective error-call placement. Baseline and -O- merge too many "
            "calls; -G, -v, and -y preserve additional calls but alter other codegen."
        ),
        "limit": (
            "This closes the tested compiler-profile surface only. It does not prove "
            "the original source spelling and grants no ZUN exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        name: {
            "size": row["code_size"],
            "fingerprint": row["error_tail_fingerprint"],
        }
        for name, row in results.items()
    }, sort_keys=True))
    print(f"receipt: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
