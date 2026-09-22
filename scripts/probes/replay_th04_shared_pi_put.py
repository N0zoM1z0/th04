#!/usr/bin/env python3
"""Cold-relink OP and MAINE with the maintained shared PI put TU.

This accepts decoded function bytes only, not either DIET-packed executable.
"""

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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a"
SOURCE = ROOT / "src/shared/formats/pi_put.cpp"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
RESTORED = ROOT / ".analysis/reconstruction/diet-replay"
ARTIFACTS = {
    "op": (0xDA50, 0xAD, 804, "v228-op-target-roundtrip/a/restored.bin",
           "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
           "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"),
    "maine": (0xCCB8, 0xAD, 559, "v228-maine-target-roundtrip/a/restored.bin",
              "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
              "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=180)
    log.write_text(json.dumps(command) + f"\nexit={result.returncode}\n"
                   + result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"command failed: {log}")


def contribution(path: Path) -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=SHARED\b.*\bM=th03/pi_put\.cpp(?:\s|$)", re.I,
    )
    matches = []
    for line in path.read_text(encoding="cp437").splitlines():
        found = pattern.search(line)
        if found:
            matches.append((int(found[1], 16) * 16 + int(found[2], 16),
                            int(found[3], 16), line.strip()))
    if len(matches) != 1:
        raise RuntimeError(f"expected one PI put MAP contribution: {path}")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        parser.error("output must be new below .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    if sha(RUNNER.read_bytes()) != RUNNER_SHA256:
        raise RuntimeError("pinned DOS runner identity drift")
    output.mkdir()
    source_hash = sha(SOURCE.read_bytes())
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    targets = {}
    baselines = {}
    for name, (start, size, reloc_count, target_rel, target_sha, baseline_sha) in ARTIFACTS.items():
        restored_bytes = (RESTORED / target_rel).read_bytes()
        baseline_bytes = (SNAPSHOT / name / "source/bin/th04" / f"{name}.exe").read_bytes()
        if sha(restored_bytes) != target_sha or sha(baseline_bytes) != baseline_sha:
            raise RuntimeError(f"{name}: target restore or link scaffold identity drift")
        targets[name] = parse_mz(restored_bytes)
        baselines[name] = parse_mz(baseline_bytes)
        if not targets[name].valid or not baselines[name].valid:
            raise RuntimeError(f"{name}: invalid MZ control")
        if len(targets[name].program_image[start:start + size]) != size:
            raise RuntimeError(f"{name}: truncated target PI put producer")
        if len(targets[name].relocations) != reloc_count:
            raise RuntimeError(f"{name}: target relocation count drift")

    builds = {}
    for label in ("a", "b"):
        builds[label] = {}
        for name, (start, size, reloc_count, _, _, baseline_sha) in ARTIFACTS.items():
            work = output / label / name / "source"
            work.parent.mkdir(parents=True)
            shutil.copytree(SNAPSHOT / name / "source", work, symlinks=True)
            shutil.copy2(SOURCE, work / "th03/pi_put.cpp")
            shared_dst = work / "src/shared"
            shared_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(ROOT / "src/shared", shared_dst, dirs_exist_ok=True)
            obj = work / "obj/th03/pi_put.obj"
            obj.unlink()
            command = ["wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.",
                       "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml",
                       "-nobj/th03/", "th03/pi_put.cpp"]
            run(command, work, output / f"compile-{label}-{name}.log", env)
            if not obj.is_file():
                raise RuntimeError(f"{label}/{name}: compiler omitted object")
            omf = describe_omf(obj.read_bytes())
            if "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
                raise RuntimeError(f"{label}/{name}: wrong OMF producer")
            exe = work / f"bin/th04/{name}.exe"
            map_path = work / f"obj/th04/{name}.map"
            exe.unlink()
            map_path.unlink()
            run(["wine", str(RUNNER), "-e", "-x", "tlink",
                 fr"@obj\th04\{name}.@l"], work,
                output / f"link-{label}-{name}.log", env)
            candidate = parse_mz(exe.read_bytes())
            if not candidate.valid:
                raise RuntimeError(f"{label}/{name}: invalid linked MZ")
            target = targets[name]
            relocations = [r.linear for r in candidate.relocations]
            target_relocations = [r.linear for r in target.relocations]
            if relocations != target_relocations or len(relocations) != reloc_count:
                raise RuntimeError(f"{label}/{name}: ordered relocations differ")
            map_start, map_size, map_line = contribution(map_path)
            if (map_start, map_size) != (start, size):
                raise RuntimeError(f"{label}/{name}: source ownership moved")
            expected = target.program_image[start:start + size]
            actual = candidate.program_image[start:start + size]
            differences = [i for i, (a, b) in enumerate(zip(expected, actual)) if a != b]
            if differences or candidate.program_image != baselines[name].program_image:
                raise RuntimeError(f"{label}/{name}: PI put producer or aggregate program differs")
            if sha(exe.read_bytes()) != baseline_sha:
                raise RuntimeError(f"{label}/{name}: aggregate EXE identity drift")
            builds[label][name] = {
                "source_object_normalized_sha256": omf["dependency_timestamp_normalized_sha256"],
                "exe_sha256": sha(exe.read_bytes()),
                "map_sha256": sha(map_path.read_bytes()),
                "map_contribution": map_line,
                "target_slice_sha256": sha(expected),
                "candidate_slice_sha256": sha(actual),
                "raw_difference_count": len(differences),
                "first_difference_offsets": differences[:16],
                "ordered_relocations": len(relocations),
                "candidate_program_sha256": sha(candidate.program_image),
                "baseline_program_equal": candidate.program_image == baselines[name].program_image,
            }
    for name in ARTIFACTS:
        if builds["a"][name] != builds["b"][name]:
            raise RuntimeError(f"{name}: cold rounds disagree")
    if sha(SOURCE.read_bytes()) != source_hash:
        raise RuntimeError("maintained source changed during replay")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "artifact-local decoded PI put producer raw replay",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "builds": builds,
        "limit": "No packed-file offsets or whole-artifact exact claim; ReC98 is link scaffolding.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({name: builds["a"][name]["raw_difference_count"]
                      for name in ARTIFACTS}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
