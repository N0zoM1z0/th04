#!/usr/bin/env python3
"""Cold-compare historical ASM branches before/after native Ending/scroll fixes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from lib.omf import describe_omf, normalize_dependency_timestamps

ROOT = Path(__file__).resolve().parents[1]
OWNERS = ("src/shared/formats/cdg_put.asm", "src/maine/formats/cdg_put_plane.asm",
          "src/main/scroll/state.asm", "src/main/stage/resource_state.asm")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default="08b52c2")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(ROOT / ".analysis/reconstruction/probes"):
        parser.error("use a new private probe directory")
    # Resolve once, so a moving ref cannot change the baseline during replay.
    baseline = subprocess.check_output(["git", "rev-parse", args.baseline_ref + "^{commit}"],
                                       cwd=ROOT, text=True).strip()
    output.mkdir(parents=True)
    with (output / "toolchain.log").open("w") as log:
        subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT, check=True, stdout=log)
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"), WINEDEBUG="-all")
    records = []
    for index, source in enumerate(OWNERS):
        pair, inputs = [], []
        for mode in ("before", "after"):
            work = output / mode
            path = work / source
            path.parent.mkdir(parents=True, exist_ok=True)
            contents = (subprocess.check_output(["git", "show", baseline + ":" + source], cwd=ROOT)
                        if mode == "before" else (ROOT / source).read_bytes())
            path.write_bytes(contents)
            inputs.append(sha(contents))
            object_name = f"owner{index}.obj"
            command = ["wine", "cmd", "/d", "/c",
                       "set PATH=C:\\TASM50\\BIN;C:\\TC4\\BIN;%PATH%&&"
                       "tasm32 /m /mx /kh32768 /t /dGAME=4 " + source.replace("/", "\\") + " " + object_name]
            result = subprocess.run(command, cwd=work, env=env, capture_output=True, timeout=120)
            (work / f"owner{index}.log").write_bytes(json.dumps(command).encode() + b"\n" +
                                                  result.stdout + result.stderr)
            if result.returncode:
                raise RuntimeError(f"TASM failed: {mode} {source}")
            data = (work / object_name).read_bytes()
            describe_omf(data)
            pair.append(data)
        records.append(dict(source=source, source_sha256=inputs, raw_equal=pair[0] == pair[1],
                            normalized_equal=normalize_dependency_timestamps(pair[0]) ==
                                             normalize_dependency_timestamps(pair[1]),
                            before_sha256=sha(pair[0]), after_sha256=sha(pair[1])))
    passed = all(record["normalized_equal"] for record in records)
    receipt = dict(baseline_commit=baseline, script_sha256=sha(Path(__file__).read_bytes()),
                   toolchain_log_sha256=sha((output / "toolchain.log").read_bytes()), owners=records,
                   passed=passed, scope="Cold historical-branch source-to-source OMF preservation; source timestamps normalized. Not original-target equality.")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("Historical ASM link-relevant OMF:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
