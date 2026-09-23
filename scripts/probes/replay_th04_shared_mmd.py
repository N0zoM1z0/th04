#!/usr/bin/env python3
"""Cold-relink OP and MAINE with maintained MMD source plus zero-code alignment.

The authored claim is only the reviewed 0x2F-byte snd_mmd_resident body. The
following target 0x90 byte is external padding and is deliberately not emitted
or credited by this replay.
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
from compact_op_maine_snapshot import copy_compact_snapshot

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a"
SOURCE = ROOT / "src/shared/sound/mmd_resident.c"
ALIGN_SOURCE = ROOT / "src/main/sound/mmd_align.c"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
RESTORED = ROOT / ".analysis/reconstruction/diet-replay"
ARTIFACTS = {
    "op": (0xDC44, 0x2F, 0xDC73, 804, "v228-op-target-roundtrip/a/restored.bin",
           "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d",
           "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"),
    "maine": (0xCF5C, 0x2F, 0xCF8B, 559, "v228-maine-target-roundtrip/a/restored.bin",
              "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533",
              "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def link_relevant_omf_sha(path: Path) -> str:
    """Hash every non-COMENT OMF record; Borland COMENT data is non-linking."""
    digest = hashlib.sha256()
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x88:
            continue
        digest.update(bytes([record.record_type]))
        digest.update(len(record.data).to_bytes(2, "little"))
        digest.update(record.data)
    return digest.hexdigest()


def run(command: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=180)
    log.write_text(json.dumps(command) + f"\nexit={result.returncode}\n"
                   + result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"command failed: {log}")


def contribution(path: Path, module: str) -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE.*"
        + rf"\bS=SHARED\b.*\bM={re.escape(module)}(?:\s|$)", re.I,
    )
    matches = []
    for line in path.read_text(encoding="cp437").splitlines():
        found = pattern.search(line)
        if found:
            matches.append((int(found[1], 16) * 16 + int(found[2], 16),
                            int(found[3], 16), line.strip()))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {module} MAP contribution: {path}")
    return matches[0]


def insert_alignment_object(path: Path) -> None:
    data = path.read_bytes()
    anchor = br"obj\th04\snd_mmdr.obj "
    if data.count(anchor) != 1:
        raise RuntimeError(f"expected one snd_mmdr link anchor: {path}")
    path.write_bytes(data.replace(
        anchor, anchor + br"obj\th04\mmdaln.obj ", 1
    ))


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
    align_source_hash = sha(ALIGN_SOURCE.read_bytes())
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")

    targets = {}
    baselines = {}
    for name, (start, size, padding, reloc_count, target_rel, target_sha,
               baseline_sha) in ARTIFACTS.items():
        restored_bytes = (RESTORED / target_rel).read_bytes()
        baseline_bytes = (SNAPSHOT / name / "source/bin/th04" / f"{name}.exe").read_bytes()
        if sha(restored_bytes) != target_sha or sha(baseline_bytes) != baseline_sha:
            raise RuntimeError(f"{name}: target restore or link scaffold identity drift")
        target = parse_mz(restored_bytes)
        baseline = parse_mz(baseline_bytes)
        if not target.valid or not baseline.valid:
            raise RuntimeError(f"{name}: invalid MZ control")
        if len(target.relocations) != reloc_count:
            raise RuntimeError(f"{name}: target relocation count drift")
        if len(target.program_image[start:start + size]) != size:
            raise RuntimeError(f"{name}: truncated target MMD resident function")
        if target.program_image[padding] != 0x90 or baseline.program_image[padding] != 0x90:
            raise RuntimeError(f"{name}: expected external target/scaffold MMD padding 0x90")
        targets[name] = target
        baselines[name] = baseline

    builds = {}
    for label in ("a", "b"):
        builds[label] = {}
        for name, (start, size, padding, reloc_count, _, _, _) in ARTIFACTS.items():
            work = output / label / name / "source"
            work.parent.mkdir(parents=True)
            copy_compact_snapshot(SNAPSHOT / name / "source", work, name)
            shutil.copy2(SOURCE, work / "th04/snd_mmdr.c")
            shutil.copy2(ALIGN_SOURCE, work / "th04/mmdaln.c")
            shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)

            mmd_obj = work / "obj/th04/snd_mmdr.obj"
            align_obj = work / "obj/th04/mmdaln.obj"
            mmd_obj.unlink()
            if align_obj.exists():
                align_obj.unlink()

            common = ["wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.",
                      "-O", "-b-", "-3", "-Z", "-d", "-DGAME=4", "-ml",
                      "-nobj/th04/"]
            run(common + ["th04/snd_mmdr.c"], work,
                output / f"compile-mmd-{label}-{name}.log", env)
            run(common + ["th04/mmdaln.c"], work,
                output / f"compile-align-{label}-{name}.log", env)
            if not mmd_obj.is_file() or not align_obj.is_file():
                raise RuntimeError(f"{label}/{name}: compiler omitted MMD or alignment object")

            mmd_omf = describe_omf(mmd_obj.read_bytes())
            align_omf = describe_omf(align_obj.read_bytes())
            for desc, kind in ((mmd_omf, "MMD"), (align_omf, "alignment")):
                if not desc["valid"] or "TC86 Borland C++ 4.02" not in desc["translator_comments"]:
                    raise RuntimeError(f"{label}/{name}: invalid or wrong {kind} OMF producer")
            if align_omf["record_counts"].get("LEDATA", 0) != 0:
                raise RuntimeError(f"{label}/{name}: alignment object emitted LEDATA")
            if align_omf["record_counts"].get("SEGDEF", 0) < 1:
                raise RuntimeError(f"{label}/{name}: alignment object omitted SEGDEF")

            response = work / f"obj/th04/{name}.@l"
            insert_alignment_object(response)
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
            baseline = baselines[name]
            relocations = [r.linear for r in candidate.relocations]
            target_relocations = [r.linear for r in target.relocations]
            if relocations != target_relocations or len(relocations) != reloc_count:
                raise RuntimeError(f"{label}/{name}: ordered relocations differ")

            map_start, map_size, map_line = contribution(map_path, "th04/snd_mmdr.c")
            if (map_start, map_size) != (start, size):
                raise RuntimeError(f"{label}/{name}: MMD source ownership moved")
            align_start, align_size, align_line = contribution(map_path, "th04/mmdaln.c")
            expected_align_start = padding + 1
            if (align_start, align_size) != (expected_align_start, 0):
                raise RuntimeError(f"{label}/{name}: zero-code alignment contribution moved")

            expected = target.program_image[start:start + size]
            actual = candidate.program_image[start:start + size]
            raw_differences = [i for i, (a, b) in enumerate(zip(expected, actual)) if a != b]
            if raw_differences:
                raise RuntimeError(f"{label}/{name}: MMD resident function differs")

            aggregate_differences = [
                i for i, (a, b) in enumerate(zip(baseline.program_image, candidate.program_image))
                if a != b
            ]
            if aggregate_differences != [padding]:
                raise RuntimeError(
                    f"{label}/{name}: aggregate differences are not exactly external MMD padding"
                )
            if candidate.program_image[padding] != 0x00:
                raise RuntimeError(f"{label}/{name}: natural linker fill at excluded padding is not 0x00")

            builds[label][name] = {
                "source_object_link_relevant_sha256": link_relevant_omf_sha(mmd_obj),
                "alignment_object_link_relevant_sha256": link_relevant_omf_sha(align_obj),
                "alignment_zero_code": True,
                "alignment_ledata_count": align_omf["record_counts"].get("LEDATA", 0),
                "exe_sha256": sha(exe.read_bytes()),
                "map_sha256": sha(map_path.read_bytes()),
                "map_contribution": map_line,
                "alignment_map_contribution": align_line,
                "target_slice_sha256": sha(expected),
                "candidate_slice_sha256": sha(actual),
                "raw_difference_count": len(raw_differences),
                "ordered_relocations": len(relocations),
                "candidate_program_sha256": sha(candidate.program_image),
                "aggregate_difference_offsets": aggregate_differences,
                "excluded_padding": {
                    "offset": padding,
                    "target": target.program_image[padding],
                    "baseline": baseline.program_image[padding],
                    "candidate": candidate.program_image[padding],
                },
            }

    for name in ARTIFACTS:
        if builds["a"][name] != builds["b"][name]:
            raise RuntimeError(f"{name}: cold rounds disagree")
    if sha(SOURCE.read_bytes()) != source_hash:
        raise RuntimeError("maintained MMD source changed during replay")
    if sha(ALIGN_SOURCE.read_bytes()) != align_source_hash:
        raise RuntimeError("zero-code alignment source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "artifact-local decoded MMD resident body with excluded external padding",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "alignment_source": str(ALIGN_SOURCE.relative_to(ROOT)),
        "alignment_source_sha256": align_source_hash,
        "builds": builds,
        "limit": (
            "The following target 0x90 is external padding and is neither emitted nor "
            "credited. No packed-file offsets or whole-artifact exact claim."
        ),
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        name: {
            "raw_difference_count": builds["a"][name]["raw_difference_count"],
            "aggregate_difference_offsets": builds["a"][name]["aggregate_difference_offsets"],
        }
        for name in ARTIFACTS
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
