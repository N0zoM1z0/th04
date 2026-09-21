#!/usr/bin/env python3
"""Replay natural TH04 MAINE SND_LOAD_EXT and score/end TC86 producers.

This packet isolates producer direction from global relocation-table placement.
It starts from the retained v401 source snapshot, reconstructs the accepted
v425 MAINE topology, then replaces only two producer shapes:

* the four-pointer SND_LOAD_EXT table moves from a TASM data include to an
  ordinary TC86 global initializer at the same DATA position;
* score_e.cpp + hi_end.cpp compile as one TC86 TU, preserving SCORE_TEXT code
  order while allowing TC86 to emit their segment FIXUPPs as one record.

No MZ relocation bytes, target payload bytes, or function bodies are patched.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from inspect_dialog_fixup_order import code_ledata  # noqa: E402
from lib.omf import parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_master_relocation_order import (  # noqa: E402
    BASE as V401_BASE,
    NEW_EXE as V425_EXE,
    NEW_MAP as V425_MAP,
    patch as apply_v425,
)
from probe_th04_master_object_split import build, compare, sha  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

RUNNER = ROOT / "_reference/ReC98/bin/msdos.exe"
RUNNER_SHA = "f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02"
SND_TEMPLATE = ROOT / "config/replay/th04_snd_load_ext_v461.cpp.in"
SND_TEMPLATE_SHA = "cdb73658c3bba224871005271bd8c0f5657509d9a7c203525a996b166b5299b2"
SCORE_HI_TEMPLATE = ROOT / "config/replay/th04_maine_score_hi_v468.cpp.in"
SCORE_HI_TEMPLATE_SHA = "10396ec634f403c156a4623c880ed3e68f8f8fd7a2b50f6831fdb0735c87988a"
TARGET_RESTORED_SHA = "6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533"
FINAL_EXE = "f23a056af351c748269f02fed19c11e7d21270cda756b83151d65af3de103af4"
FINAL_MAP = "032ff715818b483ee488cb688c834958c058eeb576947e62b3386d548e91f234"
SCORE_HI_CODE_SHA = "a32897ac03f600e4e1c0375af3a68c88e1fa6e6e6dbf7f5f4d886c9151b0f48f"
SCORE_HI_CODE_SIZE = 0x211
SND_SITES = [0xEAE2, 0xEADE, 0xEADA, 0xEAD6]
HI_SITES = [
    0xC3AD, 0xC3A2, 0xC396, 0xC37D, 0xC371, 0xC35A, 0xC34E, 0xC33A,
    0xC324, 0xC2FE, 0xC2F9, 0xC2ED, 0xC2DA, 0xC2C4, 0xC2B7, 0xC2A7,
    0xC299, 0xC286,
]
SCORE_SITES = [0xC1CD, 0xC1C5]
SCORE_HI_KIND3 = [
    0x20A, 0x1FF, 0x1F3, 0x1DA, 0x1CE, 0x1B7, 0x1AB, 0x197, 0x181,
    0x15B, 0x156, 0x14A, 0x137, 0x121, 0x114, 0x104, 0x0F6, 0x0E3,
    0x02A, 0x022,
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="maine-score-producers-v468-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def env() -> dict[str, str]:
    e = os.environ.copy()
    e.update(
        WINEPREFIX=str(ROOT / ".analysis/toolchain/wineprefix"),
        WINEDEBUG="-all",
        MSDOS_PATH=r"C:\TC4\BIN;C:\TASM50\BIN",
    )
    return e


def run_checked(command: list[str], cwd: Path, log: Path, timeout: int = 180) -> None:
    done = subprocess.run(command, cwd=cwd, env=env(), capture_output=True, text=True, timeout=timeout)
    log.write_text(json.dumps(command) + f"\nexit={done.returncode}\n" + done.stdout + "\n" + done.stderr)
    if done.returncode:
        raise RuntimeError(f"command failed; see {log}")


def mz_sites(path: Path) -> list[int]:
    image = parse_mz(path.read_bytes())
    if not image.valid:
        raise ValueError(f"invalid MZ: {path}")
    return [row.linear for row in image.relocations]


def segment_bytes(path: Path, segment: str) -> bytes:
    records = parse_omf(path.read_bytes())
    groups = code_ledata(records, segment)
    if not groups:
        return b""
    end = max(row[1] for row in groups)
    data = bytearray(end)
    for start, stop, record_number, _ in groups:
        data[start:stop] = records[record_number - 1].data[3:]
    return bytes(data)


def kind3_locations(path: Path) -> list[int]:
    result: list[int] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            result.extend(loc for kind, loc in fixup_locations(record.data) if kind == 3)
    return result


def apply_producer_sources(work: Path) -> None:
    if sha(SND_TEMPLATE) != SND_TEMPLATE_SHA or sha(SCORE_HI_TEMPLATE) != SCORE_HI_TEMPLATE_SHA:
        raise ValueError("replay template identity drift")
    shutil.copy2(SND_TEMPLATE, work / "th04/sndlext.cpp")
    shutil.copy2(SCORE_HI_TEMPLATE, work / "th04/score_hi.cpp")

    data_tail = work / "th04_maine_master_data_tail.asm"
    data = data_tail.read_bytes()
    for needle in (b"include th04/snd/load[data].asm\r\n", b"include th04/snd/load[data].asm\n"):
        if data.count(needle) == 1:
            data_tail.write_bytes(data.replace(needle, b"", 1))
            break
    else:
        raise ValueError("MAINE SND_LOAD_EXT include anchor drift")

    # Compile-scaffold hygiene only. The original function bodies stay intact.
    scoredat = work / "th04/formats/scoredat/scoredat.hpp"
    text = scoredat.read_text()
    if not text.startswith("#ifndef V468_SCOREDAT_HPP_GUARD"):
        scoredat.write_text(
            "#ifndef V468_SCOREDAT_HPP_GUARD\n#define V468_SCOREDAT_HPP_GUARD\n"
            + text + "\n#endif\n"
        )
    recreate = work / "th04/formats/scoredat/recreate.cpp"
    text = recreate.read_text()
    pragma = "#pragma option -zCSCORE_TEXT\n\n"
    if text.count(pragma) != 1:
        raise ValueError("recreate SCORE_TEXT pragma anchor drift")
    recreate.write_text(text.replace(pragma, "", 1))


def targeted_rebuild(work: Path, output: Path, label: str) -> None:
    # Compile the two natural TC86 producers only.
    for source in ("th04/sndlext.cpp", "th04/score_hi.cpp"):
        stem = Path(source).stem
        obj = work / f"obj/th04/{stem}.obj"
        obj.unlink(missing_ok=True)
        run_checked(
            [
                "wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-", "-3", "-Z", "-d",
                "-DGAME=4", "-ml", "-DBINARY='E'", "-nobj/th04/", source,
            ],
            work,
            output / f"compile-{stem}-{label}.log",
        )
        if not obj.is_file():
            raise ValueError(f"missing compiler output: {obj}")

    # Reassemble the data-tail owner after removing only the old pointer table.
    mdata = work / "obj/th04/mainemdata.obj"
    mdata.unlink(missing_ok=True)
    command = (
        r"set PATH=C:\TASM50\BIN;C:\TC4\BIN;%PATH%&&"
        r"tasm32 /m /mx /kh32768 /t /dGAME=4 th04_maine_master_data_tail.asm obj\th04\mainemdata.obj"
    )
    run_checked(["wine", "cmd", "/d", "/c", command], work, output / f"assemble-mdata-{label}.log")
    if not mdata.is_file():
        raise ValueError("missing rebuilt mainemdata.obj")

    # Preserve physical positions. Only producer ownership changes.
    rsp = work / "obj/th04/maine.@l"
    text = rsp.read_text()
    old = (
        r"obj\th04\mainemdata.obj obj\th04\score_d.obj "
        r"obj\th04\score_e.obj obj\th04\hi_end.obj"
    )
    new = (
        r"obj\th04\mainemdata.obj obj\th04\sndlext.obj obj\th04\score_d.obj "
        r"obj\th04\score_hi.obj"
    )
    if text.count(old) != 1:
        raise ValueError("MAINE response producer anchor drift")
    rsp.write_text(text.replace(old, new, 1))

    exe = work / "bin/th04/maine.exe"
    map_path = work / "obj/th04/maine.map"
    exe.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
        work,
        output / f"link-{label}.log",
    )
    if not exe.is_file() or not map_path.is_file():
        raise ValueError("targeted MAINE relink did not produce EXE/MAP")


def validate_payload(label: str, result: dict[str, object]) -> None:
    if result["payload_differing_bytes"] != 2:
        raise ValueError(f"{label}: payload difference count drift")
    if [row["start"] for row in result["payload_mismatch_runs"]] != [0xD1D3]:
        raise ValueError(f"{label}: snd_load payload location drift")
    if result["relocation_multiset_exact"] is not True:
        raise ValueError(f"{label}: relocation multiset drift")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--target-restored", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    source = args.source_dir.resolve()
    target_path = args.target_restored.resolve()
    output = output_dir(args.output_dir)

    if sha(RUNNER) != RUNNER_SHA:
        raise ValueError("MS-DOS runner identity drift")
    for rel, expected in V401_BASE.items():
        path = source / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"v401 source identity drift: {rel}")
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("v228 MAINE target-restored identity drift")
    target_sites = mz_sites(target_path)

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        apply_v425(work)
        build(work, output / f"baseline-build-{label}.log")
        baseline_exe = work / "bin/th04/maine.exe"
        baseline_map = work / "obj/th04/maine.map"
        if sha(baseline_exe) != V425_EXE or sha(baseline_map) != V425_MAP:
            raise ValueError(f"{label}: v425 baseline identity drift")
        baseline_program = parse_mz(baseline_exe.read_bytes()).program_image
        baseline_sites = mz_sites(baseline_exe)
        baseline_payload = compare("th04-maine", work)
        validate_payload(f"{label}-baseline", baseline_payload)
        if sum(a != b for a, b in zip(baseline_sites, target_sites)) != 299:
            raise ValueError(f"{label}: v425 target-order frontier drift")

        apply_producer_sources(work)
        targeted_rebuild(work, output, label)
        exe = work / "bin/th04/maine.exe"
        map_path = work / "obj/th04/maine.map"
        image = parse_mz(exe.read_bytes())
        sites = [row.linear for row in image.relocations]
        payload = compare("th04-maine", work)
        validate_payload(label, payload)
        if image.program_image != baseline_program:
            raise ValueError(f"{label}: producer replacement changed linked program bytes")
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: target relocation-site multiset drift")
        changed = [i for i, (left, right) in enumerate(zip(baseline_sites, sites)) if left != right]
        if changed != list(range(51, 75)):
            raise ValueError(f"{label}: changed-index set drift: {changed}")
        if sites[51:55] != SND_SITES:
            raise ValueError(f"{label}: SND_LOAD_EXT direction drift: {sites[51:55]}")
        if sites[55:73] != HI_SITES or sites[73:75] != SCORE_SITES:
            raise ValueError(f"{label}: combined score/end relocation direction drift")
        if target_sites[58:62] != SND_SITES:
            raise ValueError("target SND_LOAD_EXT projection drift")
        if target_sites[291:309] != HI_SITES or target_sites[309:311] != SCORE_SITES:
            raise ValueError("target score/end projection drift")
        ordered = sum(left != right for left, right in zip(sites, target_sites))
        if ordered != 299:
            raise ValueError(f"{label}: global placement frontier unexpectedly changed: {ordered}")

        snd_obj = work / "obj/th04/sndlext.obj"
        score_obj = work / "obj/th04/score_hi.obj"
        snd_kind3 = kind3_locations(snd_obj)
        score_kind3 = kind3_locations(score_obj)
        if snd_kind3 != [0x0C, 0x08, 0x04, 0x00]:
            raise ValueError(f"{label}: SND_LOAD_EXT FIXUPP direction drift: {snd_kind3}")
        if score_kind3 != SCORE_HI_KIND3:
            raise ValueError(f"{label}: score/end FIXUPP direction drift: {score_kind3}")
        score_code = segment_bytes(score_obj, "SCORE_TEXT")
        if len(score_code) != SCORE_HI_CODE_SIZE or digest(score_code) != SCORE_HI_CODE_SHA:
            raise ValueError(f"{label}: combined score/end code identity drift")
        if sha(exe) != FINAL_EXE or sha(map_path) != FINAL_MAP:
            raise ValueError(f"{label}: final MAINE identity drift")

        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "program_image_sha256": digest(image.program_image),
            "payload_comparison": payload,
            "ordered_relocation_mismatches": ordered,
            "changed_indices_vs_v425": changed,
            "snd_load_ext_indices": [51, 52, 53, 54],
            "snd_load_ext_sites": sites[51:55],
            "snd_load_ext_fixupp_locations": snd_kind3,
            "score_hi_indices": [55, 74],
            "hi_sites": sites[55:73],
            "score_sites": sites[73:75],
            "score_hi_fixupp_kind3_locations": score_kind3,
            "score_hi_code_size": len(score_code),
            "score_hi_code_sha256": digest(score_code),
        }

    for key in (
        "exe_sha256", "map_sha256", "program_image_sha256", "ordered_relocation_mismatches",
        "changed_indices_vs_v425", "snd_load_ext_sites", "snd_load_ext_fixupp_locations",
        "hi_sites", "score_sites", "score_hi_fixupp_kind3_locations", "score_hi_code_sha256",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 MAINE natural producer-direction replay; global relocation placement intentionally unresolved",
        "source_baseline": V401_BASE,
        "v425_baseline_exe_sha256": V425_EXE,
        "v425_baseline_map_sha256": V425_MAP,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "snd_load_ext_template": str(SND_TEMPLATE.relative_to(ROOT)),
        "score_hi_template": str(SCORE_HI_TEMPLATE.relative_to(ROOT)),
        "builds": builds,
        "observed_effect": (
            "Replacing only producer shapes keeps the complete v425 MAINE program image byte-identical and the 559-site relocation multiset target-equal. Ordinary TC86 static initialization reverses the four SND_LOAD_EXT segment fixups. Compiling score_e + hi_end as one TC86 TU preserves linked SCORE_TEXT bytes while emitting one descending segment-fixup stream: hi_end's 18 relocation sites followed by score_e's 2, exactly the target-local direction. The global target-order mismatch remains 299 because these now-correct blocks are still at the v425 physical object positions; recovering MAINE_01_TEXT/SCORE_TEXT ownership is the next blocker."
        ),
        "limit": (
            "The temporary include guard and duplicate SCORE_TEXT pragma suppression are compile-scaffold hygiene needed to test the combined TU with the ReC98 source tree; they do not alter either function body and are not proposed product-source edits. This replay proves producer direction only, not historical global object placement, authored-source promotion, or packed-file exactness."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_sha256": FINAL_EXE,
        "program_image_unchanged": True,
        "natural_direction_entries": 24,
        "global_ordered_mismatches": 299,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
