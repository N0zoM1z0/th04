#!/usr/bin/env python3
"""Test whether a source-level code-segment switch flushes TC4J OMF FIXUPP.

This is a compiler control, not a reconstructed TH04 unit or exactness claim.
The generated 1830-byte CODE is long enough to cross one LEDATA boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import parse_omf  # noqa: E402
from inspect_dialog_fixup_order import code_ledata  # noqa: E402

TCC_FLAGS = ("-c", "-ml", "-O", "-b-", "-3", "-Z", "-d")
NAMES = ("lbase", "lrepeat", "lbounce")
EXPECTED_RANGES = ((0, 1020), (1020, 1830))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sources() -> dict[str, str]:
    prefix = (
        "#pragma option -zCDIALOG_TEXT -zPmain_01\n"
        "extern void far e();\n"
        "extern volatile unsigned int x;\n"
    )
    functions = [f"void far {name}(){{e();\n" + ("x++;\n" * 150) + "}\n" for name in "abc"]
    separators = {
        "lbase": "",
        "lrepeat": "#pragma codeseg DIALOG_TEXT main_01\n",
        "lbounce": (
            "#pragma codeseg TEMP_TEXT main_01\n"
            "#pragma codeseg DIALOG_TEXT main_01\n"
        ),
    }
    return {name: prefix + separators[name].join(functions) for name in NAMES}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    private_root = (ROOT / ".analysis").resolve()
    if args.output_dir is None:
        probe_root = private_root / "reconstruction/probes"
        probe_root.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix="dialog-segment-flush-", dir=probe_root))
    else:
        output = args.output_dir.resolve()
        if output.exists() or not output.is_relative_to(private_root):
            parser.error("output directory must be new and below .analysis")
        output.mkdir(parents=True)

    surfaces = tomllib.loads((ROOT / "config/toolchain.toml").read_text())["surfaces"]
    pinned_tcc = next(item for item in surfaces if item["id"] == "active-tcc")
    tcc_path = ROOT / pinned_tcc["path"]
    if sha(tcc_path.read_bytes()) != pinned_tcc["sha256"]:
        raise ValueError("active TCC differs from pinned toolchain")
    runner = ROOT / "_reference/ReC98/bin/msdos.exe"
    runner_sha = sha(runner.read_bytes())
    env = os.environ.copy()
    env["WINEPREFIX"] = str(ROOT / ".analysis/toolchain/wineprefix")
    env["WINEDEBUG"] = "-all"
    env["MSDOS_PATH"] = r"C:\TC4\BIN;C:\TASM50\BIN"

    builds: dict[str, dict[str, object]] = {}
    for name, source in sources().items():
        source_path = output / f"{name}.cpp"
        object_path = output / f"{name}.obj"
        source_path.write_text(source)
        object_path.unlink(missing_ok=True)
        command = ["wine", str(runner), "-e", "-x", "tcc", *TCC_FLAGS, source_path.name]
        completed = subprocess.run(
            command, cwd=output, env=env, capture_output=True, text=True, timeout=120,
        )
        (output / f"{name}.log").write_text(
            json.dumps(command) + f"\nexit={completed.returncode}\n"
            + completed.stdout + "\n" + completed.stderr
        )
        if completed.returncode or not object_path.is_file():
            raise ValueError(f"{name}: TC4J compilation failed")
        object_bytes = object_path.read_bytes()
        groups = code_ledata(parse_omf(object_bytes), "DIALOG_TEXT")
        if tuple((start, end) for start, end, _, _ in groups) != EXPECTED_RANGES:
            raise ValueError(f"{name}: unexpected LEDATA boundary")
        code = bytearray(groups[-1][1])
        records = parse_omf(object_bytes)
        for start, end, record_number, _ in groups:
            code[start:end] = records[record_number - 1].data[3:]
        (output / f"{name}.code").write_bytes(code)
        builds[name] = {
            "source_sha256": sha(source_path.read_bytes()),
            "object_sha256": sha(object_bytes),
            "code_size": len(code),
            "code_sha256": sha(code),
            "ledata_ranges": [[start, end] for start, end, _, _ in groups],
            "fixupp_sha256": [sha(fixupp) for _, _, _, fixupp in groups],
            "fixupp_size": [len(fixupp) for _, _, _, fixupp in groups],
            "omf_record_count": len(records),
        }
    baseline = builds["lbase"]
    for name in ("lrepeat", "lbounce"):
        candidate = builds[name]
        for field in ("code_size", "code_sha256", "ledata_ranges", "fixupp_sha256", "fixupp_size"):
            if candidate[field] != baseline[field]:
                raise ValueError(f"{name}: {field} changed; hypothesis needs review")
    receipt = {
        "schema_version": 1,
        "claim_scope": "compiler control for MAIN DIALOG_TEXT OMF grouping; no exact promotion",
        "hypothesis": "same-segment or empty bounce #pragma codeseg forces LEDATA/FIXUPP flush",
        "result": "refuted for this pinned 1830-byte control",
        "tcc_sha256": pinned_tcc["sha256"],
        "runner_sha256": runner_sha,
        "flags": list(TCC_FLAGS),
        "builds": builds,
        "target_specific_limit": "The original TH04 dialog object is unavailable; this control does not prove its producer history.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(output / "receipt.json"), "result": receipt["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
