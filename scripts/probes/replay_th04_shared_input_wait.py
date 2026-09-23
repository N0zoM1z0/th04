#!/usr/bin/env python3
"""Cold-relink the maintained shared input-wait TU into OP and MAINE."""

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
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
import probe_th04_score_codec_boundaries as codec  # noqa: E402
from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402


SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
RESTORED = ROOT / ".analysis/reconstruction/diet-replay"
SOURCE = ROOT / "src/shared/hardware/input_wait.cpp"
SOURCE_FILES = (
    "src/shared/hardware/input_wait.cpp",
    "src/shared/hardware/input.hpp",
    "src/shared/hardware/frame_delay.hpp",
)
ARTIFACTS = {
    "op": {
        "start": 0xDB62,
        "end": 0xDBB8,
        "load_segment": 0x1DA1,
        "segment_offset": 0x0152,
        "map_segment": 0x0DA1,
        "map_offset": 0x0152,
        "relocations": 804,
        "restored": "v228-op-target-roundtrip/a/restored.bin",
        "target_sha256": "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
        "candidate_sha256": "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274",
        "function_sha256": "2ef0578d61ec126f795bcb95f6b2698bd1a8dba3d6160e511889521620ed776e",
    },
    "maine": {
        "start": 0xCE7A,
        "end": 0xCED0,
        "load_segment": 0x1CC7,
        "segment_offset": 0x020A,
        "map_segment": 0x0CC7,
        "map_offset": 0x020A,
        "relocations": 559,
        "restored": "v228-maine-target-roundtrip/a/restored.bin",
        "target_sha256": "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
        "candidate_sha256": "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c",
        "function_sha256": "3a73aea1528421db6658b8419aa06f4313b6341b968ffd9c1a043db8ed6964cf",
    },
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


def shared_contribution(path: Path) -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        r"\bS=SHARED\b.*\bM=th04/input_w\.cpp(?:\s|$)", re.I,
    )
    matches = []
    for line in path.read_text(encoding="cp437").splitlines():
        found = pattern.search(line)
        if found:
            matches.append((int(found[1], 16) * 16 + int(found[2], 16),
                            int(found[3], 16), line.strip()))
    if len(matches) != 1:
        raise RuntimeError(f"expected one input-wait MAP contribution: {path}")
    return matches[0]


def target_boundary(name: str, spec: dict[str, object], target) -> dict[str, object]:
    start = int(spec["start"])
    end = int(spec["end"])
    body = target.program_image[start:end]
    if len(body) != end - start or sha(body) != spec["function_sha256"]:
        raise RuntimeError(f"{name}: target input-wait slice identity drift")
    functions = codec.ghidra_rows(codec.TARGETS[f"th04-{name}"]["inventory"])
    row = functions.get(start)
    if row is None or (
        int(row["entry_linear"], 0) != 0x10000 + start
        or int(row["entry_segment"], 0) != spec["load_segment"]
        or int(row["entry_offset"], 0) != spec["segment_offset"]
        or int(row["body_min_linear"], 0) != 0x10000 + start
        or int(row["body_max_linear"], 0) != 0x10000 + end - 1
        or int(row["body_addresses"]) != end - start
        or int(row["body_span"]) != end - start
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
    ):
        raise RuntimeError(f"{name}: attested Ghidra extent drift: {row!r}")

    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm unavailable")
    instructions = codec.disassemble(ndisasm, body, start)
    edges = codec.jump_edges(instructions)
    starts = {int(item["address"]) for item in instructions}
    if (
        not instructions
        or int(instructions[0]["address"]) != start
        or any(int(a["address"]) + int(a["size"]) != int(b["address"])
               for a, b in zip(instructions, instructions[1:]))
        or int(instructions[-1]["address"]) + int(instructions[-1]["size"]) != end
        or instructions[-1]["mnemonic"] != "retf"
        or str(instructions[-1]["operands"]) != "0x2"
        or any(not start <= target < end or target not in starts
               for _, _, target in edges)
    ):
        raise RuntimeError(f"{name}: target instruction closure drift")
    return {
        "payload_offset": f"0x{start:X}",
        "segment_identity": f"{int(spec['load_segment']):04X}",
        "segment_offset": f"{int(spec['segment_offset']):04X}",
        "size": len(body),
        "sha256": sha(body),
        "instruction_count": len(instructions),
        "direct_branch_count": len(edges),
        "direct_branches_internal_and_aligned": True,
        "terminal": str(instructions[-1]["text"]),
        "ghidra_span": int(row["body_span"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", choices=("th04-op", "th04-maine"),
                        help="replay one artifact for decoded acceptance")
    parser.add_argument("--retain-candidates", action="store_true",
                        help="retain only the two linked MZ candidates for the outer acceptance comparator")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        parser.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    artifact_names = {"th04-op": "op", "th04-maine": "maine"}
    selected_names = (artifact_names if args.artifact is None else
                      {args.artifact: artifact_names[args.artifact]})

    for artifact in selected_names:
        subprocess.run([sys.executable, "scripts/ghidra.py", artifact, "check"],
                       cwd=ROOT, check=True, capture_output=True, text=True)
    if sha(RUNNER.read_bytes()) != RUNNER_SHA256:
        raise RuntimeError("pinned DOS runner identity drift")

    source_hashes = {path: sha((ROOT / path).read_bytes()) for path in SOURCE_FILES}
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")
    targets = {}
    baselines = {}
    boundaries = {}
    artifact_specs = {name: ARTIFACTS[name] for name in selected_names.values()}
    for name, spec in artifact_specs.items():
        target_path = RESTORED / str(spec["restored"])
        baseline_path = SNAPSHOT / name / "source/bin/th04" / f"{name}.exe"
        restored_bytes = target_path.read_bytes()
        baseline_bytes = baseline_path.read_bytes()
        if sha(restored_bytes) != spec["target_sha256"]:
            raise RuntimeError(f"{name}: restored target identity drift")
        if sha(baseline_bytes) != spec["candidate_sha256"]:
            raise RuntimeError(f"{name}: candidate baseline identity drift")
        targets[name] = parse_mz(restored_bytes)
        baselines[name] = parse_mz(baseline_bytes)
        if (not targets[name].valid or not baselines[name].valid
                or len(targets[name].relocations) != spec["relocations"]):
            raise RuntimeError(f"{name}: target/baseline MZ integrity drift")
        boundaries[name] = target_boundary(name, spec, targets[name])

    builds: dict[str, dict[str, object]] = {}
    snapshot_materialization: dict[str, dict[str, object]] = {}
    output.mkdir(parents=True)
    for label in ("a", "b"):
        builds[label] = {}
        snapshot_materialization[label] = {}
        for name, spec in artifact_specs.items():
            work = output / label / name / "source"
            work.parent.mkdir(parents=True)
            snapshot_materialization[label][name] = copy_compact_snapshot(
                SNAPSHOT / name / "source", work, name
            )
            for source_name in SOURCE_FILES:
                source_path = ROOT / source_name
                destination = work / source_name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, destination)
            shutil.copy2(SOURCE, work / "th04/hardware/input_w.cpp")

            obj = work / "obj/th04/input_w.obj"
            if obj.exists():
                obj.unlink()
            command = ["wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.",
                       "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml",
                       "-nobj/th04/", "th04/input_w.cpp"]
            run(command, work, output / f"compile-{label}-{name}.log", env)
            if not obj.is_file():
                raise RuntimeError(f"{label}/{name}: compiler omitted input_w.obj")
            omf = describe_omf(obj.read_bytes())
            if not omf["valid"] or "TC86 Borland C++ 4.02" not in omf["translator_comments"]:
                raise RuntimeError(f"{label}/{name}: invalid or wrong-producer OMF")

            exe = work / f"bin/th04/{name}.exe"
            map_path = work / f"obj/th04/{name}.map"
            if exe.exists():
                exe.unlink()
            if map_path.exists():
                map_path.unlink()
            run(["wine", str(RUNNER), "-e", "-x", "tlink",
                 fr"@obj\th04\{name}.@l"], work,
                output / f"link-{label}-{name}.log", env)
            candidate = parse_mz(exe.read_bytes())
            if not candidate.valid:
                raise RuntimeError(f"{label}/{name}: invalid linked MZ")
            target = targets[name]
            relocation_sites = [item.linear for item in candidate.relocations]
            target_sites = [item.linear for item in target.relocations]
            if relocation_sites != target_sites or len(relocation_sites) != spec["relocations"]:
                raise RuntimeError(f"{label}/{name}: ordered MZ relocations differ")

            map_start, map_size, map_line = shared_contribution(map_path)
            if (map_start, map_size) != (int(spec["start"]), int(spec["end"]) - int(spec["start"])):
                raise RuntimeError(f"{label}/{name}: SHARED source extent drift: {map_line}")
            public = f"{int(spec['map_segment']):04X}:{int(spec['map_offset']):04X}       input_wait_for_change(int)"
            map_text = map_path.read_text(encoding="cp437")
            if public not in map_text:
                raise RuntimeError(f"{label}/{name}: input-wait MAP public drift")

            start = int(spec["start"])
            end = int(spec["end"])
            expected = target.program_image[start:end]
            actual = candidate.program_image[start:end]
            differences = [i for i, (left, right) in enumerate(zip(expected, actual))
                           if left != right]
            if (differences or len(actual) != len(expected)
                    or candidate.program_image != baselines[name].program_image
                    or sha(exe.read_bytes()) != spec["candidate_sha256"]):
                raise RuntimeError(f"{label}/{name}: function or aggregate program differs at {differences[:24]}")

            builds[label][name] = {
                "source_object_sha256": sha(obj.read_bytes()),
                "exe_sha256": sha(exe.read_bytes()),
                "map_sha256": sha(map_path.read_bytes()),
                "map_contribution": map_line,
                "target_function_sha256": sha(expected),
                "candidate_function_sha256": sha(actual),
                "raw_difference_count": len(differences),
                "ordered_relocations": len(relocation_sites),
                "candidate_program_sha256": sha(candidate.program_image),
                "baseline_program_equal": candidate.program_image == baselines[name].program_image,
            }

    for name in artifact_specs:
        if builds["a"][name] != builds["b"][name]:
            raise RuntimeError(f"{name}: cold rounds disagree")
    if {path: sha((ROOT / path).read_bytes()) for path in SOURCE_FILES} != source_hashes:
        raise RuntimeError("maintained input-wait source/header changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP/MAINE artifact-local decoded input_wait_for_change raw replay",
        "artifacts": [f"th04-{name}" for name in artifact_specs],
        "source_sha256": source_hashes,
        "target_boundaries": boundaries,
        "snapshot_materialization": snapshot_materialization,
        "builds": builds,
        "limit": "Decoded function bytes only; no DIET-packed file offset or whole-artifact exact claim.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if args.retain_candidates:
        for name in artifact_specs:
            for label in ("a", "b"):
                source_exe = output / label / name / "source/bin/th04" / f"{name}.exe"
                shutil.copy2(source_exe, output / f"{label}-{name}.exe")
    for label in ("a", "b"):
        shutil.rmtree(output / label)
    print(json.dumps({name: builds["a"][name]["raw_difference_count"]
                      for name in artifact_specs}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
