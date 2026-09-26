#!/usr/bin/env python3
"""Cold-replay a maintained ASM module in its OP/MAINE artifact owners.

The shared linker contribution is accepted only against each artifact's own
attested decoded target. The retained ReC98 snapshot supplies link inputs,
not target evidence or authored-source credit.
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
RESTORED = ROOT / ".analysis/reconstruction/diet-replay"
RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA256 = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
ARTIFACTS = {
    "op": (804, "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d", "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"),
    "maine": (559, "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533", "d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c"),
}
MODULES = {
    "bgimager": ("src/shared/hardware/bgimager.asm", 0x82, {"op": 0xE4F8, "maine": 0xD6F6}),
    "cdg_p_na": ("src/shared/formats/cdg_put_noalpha_8.asm", 0x66, {"op": 0xE176}),
    "cdg_p_nc": ("src/op/formats/cdg_p_nc.asm", 0x52, {"op": 0xDC92}),
    "cdg_load": ("src/shared/formats/cdg_load.asm", 0x164, {"op": 0xE57A, "maine": 0xD778}),
    "cdg_put": ("src/shared/formats/cdg_put.asm", 0x9E, {"op": 0xE00E, "maine": 0xD356}),
    "grppsafx": ("src/op/hardware/graph_putsa_fx.asm", 0x15A, {"op": 0xDEB4}),
    "hfliplut": ("src/shared/hardware/hflip_lut.asm", 0x1E, {"op": 0xDB44}),
    "input_s": ("src/shared/hardware/input_s.asm", 0x10A, {"op": 0xE1DC, "maine": 0xD48A}),
}
DATA_EXTENTS = {"grppsafx": {"op": (0xFD40, 0x40)}}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def linked_omf_sha(data: bytes) -> str:
    digest = hashlib.sha256()
    for record in parse_omf(data):
        if record.record_type != 0x88:  # COMENT has no linker effect.
            digest.update(bytes([record.record_type]))
            digest.update(len(record.data).to_bytes(2, "little"))
            digest.update(record.data)
    return digest.hexdigest()


def run(command: list[str], cwd: Path, log: Path, env: dict[str, str]) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=240)
    log.write_text(json.dumps(command) + f"\nexit={result.returncode}\n"
                   + result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"command failed: {log}")


def contribution(path: Path, module: str, namespace: str,
                 segment: str = "SHARED", segment_class: str = "CODE") -> tuple[int, int, str]:
    pattern = re.compile(
        r"^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C="
        + re.escape(segment_class) + r".*\bS=" + re.escape(segment)
        + r"\b.*\bM=" + re.escape(fr"{namespace}\{module}.asm") + r"(?:\s|$)", re.I,
    )
    matches = []
    for line in path.read_text(encoding="cp437").splitlines():
        found = pattern.search(line)
        if found:
            matches.append((int(found[1], 16) * 16 + int(found[2], 16),
                            int(found[3], 16), line.strip()))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {module} contribution: {path}")
    return matches[0]


def overlapping(image, start: int, size: int) -> list[int]:
    return [r.linear for r in image.relocations
            if r.linear < start + size and r.linear + 2 > start]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", choices=sorted(MODULES), default="cdg_load")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    module = args.module
    namespace = "th03" if module == "hfliplut" else "th04"
    source_rel, size, starts = MODULES[module]
    source = ROOT / source_rel
    selected = {name: ARTIFACTS[name] for name in starts}
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        parser.error("output must be new below .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    if sha(RUNNER.read_bytes()) != RUNNER_SHA256:
        raise RuntimeError("pinned DOS runner changed")
    source_sha = sha(source.read_bytes())
    output.mkdir()
    env = os.environ.copy()
    env.update(WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
               WINEDEBUG="-all", MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN")

    controls = {}
    for name, (relocation_count, target_sha, baseline_sha) in selected.items():
        start = starts[name]
        target_bytes = (RESTORED / f"v228-{name}-target-roundtrip/a/restored.bin").read_bytes()
        baseline_bytes = (SNAPSHOT / name / "source/bin/th04" / f"{name}.exe").read_bytes()
        if sha(target_bytes) != target_sha or sha(baseline_bytes) != baseline_sha:
            raise RuntimeError(f"{name}: target or snapshot identity drift")
        target, baseline = parse_mz(target_bytes), parse_mz(baseline_bytes)
        if not target.valid or not baseline.valid or len(target.relocations) != relocation_count:
            raise RuntimeError(f"{name}: MZ integrity drift")
        if len(target.program_image[start:start + size]) != size:
            raise RuntimeError(f"{name}: target extent truncated")
        controls[name] = (target, baseline)

    builds = {}
    for label in ("a", "b"):
        builds[label] = {}
        for name, (relocation_count, _, baseline_sha) in selected.items():
            start = starts[name]
            work = output / label / name / "source"
            work.parent.mkdir(parents=True)
            copy_compact_snapshot(SNAPSHOT / name / "source", work, name)
            dest = work / namespace / f"{module}.asm"
            shutil.copy2(source, dest)
            obj = work / "obj" / namespace / f"{module}.obj"
            obj.unlink()
            run(["wine", r"C:\TASM50\bin\TASM32.EXE", "/m", "/mx", "/kh32768",
                 "/dGAME=4", fr"{namespace}\{module}.asm,obj\{namespace}\{module}.obj"],
                work, output / f"assemble-{label}-{name}.log", env)
            if not obj.is_file():
                raise RuntimeError(f"{label}/{name}: assembler omitted object")
            omf = describe_omf(obj.read_bytes())
            if not omf["valid"] or not any("Turbo Assembler" in comment
                                            for comment in omf["translator_comments"]):
                raise RuntimeError(f"{label}/{name}: wrong assembler OMF")
            exe = work / f"bin/th04/{name}.exe"
            map_path = work / f"obj/th04/{name}.map"
            exe.unlink()
            map_path.unlink()
            run(["wine", str(RUNNER), "-e", "-x", "tlink",
                 fr"@obj\th04\{name}.@l"], work,
                output / f"link-{label}-{name}.log", env)
            image = parse_mz(exe.read_bytes())
            target, baseline = controls[name]
            if not image.valid or len(image.relocations) != relocation_count:
                raise RuntimeError(f"{label}/{name}: linked MZ integrity drift")
            map_start, map_size, map_line = contribution(map_path, module, namespace)
            if (map_start, map_size) != (start, size):
                raise RuntimeError(f"{label}/{name}: {module} moved or changed size")
            target_relocs = [r.linear for r in target.relocations]
            candidate_relocs = [r.linear for r in image.relocations]
            if candidate_relocs != target_relocs:
                raise RuntimeError(f"{label}/{name}: ordered relocation table differs")
            expected = target.program_image[start:start + size]
            actual = image.program_image[start:start + size]
            differences = [index for index, (a, b) in enumerate(zip(expected, actual)) if a != b]
            if differences or overlapping(image, start, size) != overlapping(target, start, size):
                raise RuntimeError(f"{label}/{name}: {module} bytes or relocations differ")
            data_result = None
            if name in DATA_EXTENTS.get(module, {}):
                data_start, data_size = DATA_EXTENTS[module][name]
                got_start, got_size, data_map_line = contribution(
                    map_path, module, namespace, "_DATA", "DATA")
                if (got_start, got_size) != (data_start, data_size):
                    raise RuntimeError(f"{label}/{name}: {module} DATA moved or changed size")
                expected_data = target.program_image[data_start:data_start + data_size]
                actual_data = image.program_image[data_start:data_start + data_size]
                if len(expected_data) != data_size or actual_data != expected_data:
                    raise RuntimeError(f"{label}/{name}: {module} DATA bytes differ")
                if overlapping(image, data_start, data_size) != overlapping(target, data_start, data_size):
                    raise RuntimeError(f"{label}/{name}: {module} DATA relocations differ")
                data_result = {"map_contribution": data_map_line,
                               "target_extent_sha256": sha(expected_data),
                               "candidate_extent_sha256": sha(actual_data),
                               "raw_difference_count": 0,
                               "overlapping_relocations": overlapping(image, data_start, data_size)}
            if image.program_image != baseline.program_image or sha(exe.read_bytes()) != baseline_sha:
                raise RuntimeError(f"{label}/{name}: relink differs from retained snapshot")
            builds[label][name] = {
                "source_object_link_relevant_sha256": linked_omf_sha(obj.read_bytes()),
                "exe_sha256": sha(exe.read_bytes()),
                "map_contribution": map_line,
                "target_extent_sha256": sha(expected),
                "candidate_extent_sha256": sha(actual),
                "raw_difference_count": len(differences),
                "overlapping_relocations": overlapping(image, start, size),
                "ordered_relocations": len(candidate_relocs),
            }
            if data_result is not None:
                builds[label][name]["data_contribution"] = data_result
    if builds["a"] != builds["b"] or sha(source.read_bytes()) != source_sha:
        raise RuntimeError("cold builds or source changed")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": f"{', '.join(selected)} complete {module} ASM module cold replay",
        "module": module,
        "source": str(source.relative_to(ROOT)),
        "source_sha256": source_sha,
        "builds": builds,
        "limit": "Decoded module exactness only; no packed-file claim.",
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({name: builds["a"][name]["raw_difference_count"]
                      for name in selected}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
