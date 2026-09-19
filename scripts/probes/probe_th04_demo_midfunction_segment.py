#!/usr/bin/env python3
"""Test TC4J code-segment controls inside the MAIN pause() function.

This is a compiler diagnostic. It neither reconstructs target bytes nor
changes the accepted state of the DEMO session owner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf, parse_omf  # noqa: E402
from probes.inspect_dialog_fixup_order import code_ledata  # noqa: E402

SNAPSHOT = ROOT / ".analysis/reconstruction/exact-unit-replay/gptweb-v214-demo-fixupp-diagnostic-001/a/source"
SESSION_OBJECT_SHA256 = "3816b5f0aaabe5e8646243d22fbe13d40e97f53f012a398ae95ec76ae426f6ad"
TCC_FLAGS = ("-c", "-I.", "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml", "-nobj/th04/")
PAUSE_LOOP = "while(key_det != INPUT_NONE) { input_reset_sense(); }"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pause_source(session: str, directive: str) -> str:
    marker = '#include "th04/hardware/input.h"'
    if session.count(marker) != 1 or session.count(PAUSE_LOOP) != 2:
        raise ValueError("retained session source markers changed")
    first_function = session.index("void near stage_session_init(void)")
    _, tail = session.split(marker, 1)
    source = session[:first_function].replace(
        "#pragma option -zCDEMO_TEXT -zPmain_01",
        "#pragma option -zCPAUSE_HEAD_TEXT -zPmain_01",
        1,
    ) + marker + tail
    return source.replace(PAUSE_LOOP, PAUSE_LOOP + "\n" + directive, 1)


def compile_variant(
    name: str, source: str, work: Path, output: Path, runner: Path, env: dict[str, str]
) -> tuple[subprocess.CompletedProcess[str], Path]:
    source_path = work / "th04" / f"{name}.cpp"
    object_path = work / "obj" / "th04" / f"{name}.obj"
    source_path.write_text(source)
    object_path.unlink(missing_ok=True)
    command = ["wine", str(runner), "-e", "-x", "tcc", *TCC_FLAGS, f"th04/{name}.cpp"]
    result = subprocess.run(
        command, cwd=work, env=env, capture_output=True, text=True, timeout=180
    )
    (output / f"{name}.log").write_text(
        json.dumps(command) + f"\nexit={result.returncode}\n" + result.stdout + "\n" + result.stderr
    )
    return result, object_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private_root = (ROOT / ".analysis").resolve()
    if output.exists() or not output.is_relative_to(private_root):
        parser.error("output directory must be new and below .analysis")
    output.mkdir(parents=True)

    targets = tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
    target_info = next(item for item in targets if item["id"] == "th04-main")
    target = (ROOT / target_info["private_path"]).read_bytes()
    if len(target) != target_info["size"] or sha(target) != target_info["sha256"]:
        raise ValueError("MAIN target identity failed")
    if int.from_bytes(target[8:10], "little") * 16 != 0x1800:
        raise ValueError("MAIN MZ header size changed")

    session_object = SNAPSHOT / "obj/th04/sess.obj"
    if sha(session_object.read_bytes()) != SESSION_OBJECT_SHA256:
        raise ValueError("retained v214 session object changed")
    session_path = SNAPSHOT / "th04/sess.cpp"
    session = session_path.read_text()

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    pinned_tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    if sha((ROOT / pinned_tcc["path"]).read_bytes()) != pinned_tcc["sha256"]:
        raise ValueError("active TCC differs from pinned toolchain")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    env = os.environ.copy()
    env.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )

    option_source = pause_source(session, "#pragma option -zCPAUSE_TAIL_TEXT")
    codeseg_source = pause_source(session, "#pragma codeseg PAUSE_TAIL_TEXT main_01")
    with tempfile.TemporaryDirectory(prefix="demo-midsegment-", dir=output) as scratch:
        work = Path(scratch) / "source"
        shutil.copytree(SNAPSHOT, work, symlinks=True)
        option_result, option_object = compile_variant(
            "midopt", option_source, work, output, runner, env
        )
        option_diagnostic = "Incorrect pragma directive option: -zCPAUSE_TAIL_TEXT in function pause()"
        option_output = option_result.stdout + option_result.stderr
        if option_result.returncode == 0 or option_object.exists() or option_diagnostic not in option_output:
            raise ValueError("mid-function #pragma option rejection changed")

        codeseg_result, codeseg_object = compile_variant(
            "midcode", codeseg_source, work, output, runner, env
        )
        if codeseg_result.returncode or not codeseg_object.is_file():
            raise ValueError("mid-function #pragma codeseg compilation failed")
        object_bytes = codeseg_object.read_bytes()
        records = parse_omf(object_bytes)
        head_groups = code_ledata(records, "PAUSE_HEAD_TEXT")
        tail_groups = code_ledata(records, "PAUSE_TAIL_TEXT")
        if [(start, end) for start, end, _, _ in head_groups] != [(0, 0x11F)]:
            raise ValueError("pause() no longer remains in PAUSE_HEAD_TEXT")
        if tail_groups:
            raise ValueError("mid-function #pragma codeseg unexpectedly emitted tail CODE")

    receipt = {
        "schema_version": 1,
        "claim_scope": "MAIN DEMO pause() mid-function segment control; diagnostic only",
        "target_sha256": target_info["sha256"],
        "snapshot_session_source_sha256": sha(session_path.read_bytes()),
        "snapshot_session_object_sha256": SESSION_OBJECT_SHA256,
        "tcc_sha256": pinned_tcc["sha256"],
        "runner_sha256": sha(runner.read_bytes()),
        "flags": list(TCC_FLAGS),
        "hypothesis": "a source pragma can split pause() after its first far call without changing function bytes",
        "option_variant": {
            "source_sha256": sha(option_source.encode()),
            "exit": option_result.returncode,
            "expected_diagnostic": option_diagnostic,
            "object_created": option_object.exists(),
        },
        "codeseg_variant": {
            "source_sha256": sha(codeseg_source.encode()),
            "object_sha256": sha(object_bytes),
            "object": describe_omf(object_bytes),
            "pause_head_ledata_ranges": [[start, end] for start, end, _, _ in head_groups],
            "pause_tail_ledata_ranges": [[start, end] for start, end, _, _ in tail_groups],
        },
        "result": "refuted: -zC is rejected inside pause(); codeseg leaves all 0x11F bytes in the original function segment",
        "remaining_unknown": "the historical producer of target relocation order 0xB2DA + 40 core + 11 later pause sites",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
