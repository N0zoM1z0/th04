#!/usr/bin/env python3
"""Cold-check that native renderer segment branches leave default OMF unchanged.

This is a compiler regression check against an explicit source revision. It
does not substitute for complete historical links or target exactness gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf, parse_omf

SOURCES = {
    "bgimager": "src/shared/hardware/bgimager.asm",
    "grppsafx": "src/shared/hardware/graph_putsa_fx.asm",
    "superrol": "src/shared/hardware/super_roll_put.asm",
    "superrl1": "src/shared/hardware/super_roll_put_1plane.asm",
}
FLAGS = ["/m", "/mx", "/kh32768", "/dGAME=4"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def link_records(data: bytes) -> str:
    digest = hashlib.sha256()
    for record in parse_omf(data):
        if record.record_type != 0x88:  # COMENT has no linker effect.
            digest.update(bytes([record.record_type]))
            digest.update(len(record.data).to_bytes(2, "little"))
            digest.update(record.data)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-revision", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(ROOT / ".analysis/reconstruction/probes"):
        parser.error("use a new private output directory")
    revision = subprocess.check_output(
        ["git", "rev-parse", "--verify", args.baseline_revision + "^{commit}"], cwd=ROOT,
        text=True).strip()
    subprocess.run([sys.executable, "scripts/attest_toolchain.py"], cwd=ROOT,
                   check=True, stdout=subprocess.DEVNULL)
    output.mkdir()
    env = dict(os.environ, WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    observations = {}
    for name, source in SOURCES.items():
        baseline = subprocess.check_output(["git", "show", revision + ":" + source], cwd=ROOT)
        current = (ROOT / source).read_bytes()
        rounds = {}
        for label, data in (("baseline", baseline), ("a", current), ("b", current)):
            work = output / name / label
            (work / "th04").mkdir(parents=True)
            (work / "obj").mkdir()
            (work / f"th04/{name}.asm").write_bytes(data)
            command = ["wine", r"C:\TASM50\bin\TASM32.EXE", *FLAGS,
                       fr"th04\{name}.asm,obj\{name}.obj"]
            run = subprocess.run(command, cwd=work, env=env, capture_output=True, timeout=240)
            (work / "assemble.log").write_bytes(run.stdout + run.stderr)
            if run.returncode:
                raise RuntimeError(f"assembler failed: {work}")
            obj = (work / f"obj/{name}.obj").read_bytes()
            omf = describe_omf(obj)
            if not omf["valid"] or not any("Turbo Assembler  Version 5.0" in text
                                           for text in omf["translator_comments"]):
                raise RuntimeError(f"OMF identity/integrity failed: {work}")
            rounds[label] = dict(source_sha256=sha(data), object_sha256=sha(obj),
                                 link_records_sha256=link_records(obj))
        observations[source] = dict(rounds=rounds, equal=len({
            row["link_records_sha256"] for row in rounds.values()}) == 1)
    result = dict(scope="default assembler inputs; no complete-link or exactness claim",
                  baseline_revision=revision, assembler_flags=FLAGS,
                  observations=observations, equal=all(row["equal"] for row in observations.values()))
    (output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(equal=result["equal"], sources=len(observations))))
    return int(not result["equal"])


if __name__ == "__main__":
    raise SystemExit(main())
