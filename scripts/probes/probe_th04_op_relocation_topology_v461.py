#!/usr/bin/env python3
"""Replay the v461 TH04 OP physical/FIXUPP topology without editing MZ bytes."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from analyze_diet_relocation_owners import blocks, map_contributions  # noqa: E402
from lib.omf import normalize_dependency_timestamps, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_master_object_split import build, compare, sha  # noqa: E402
from probe_th04_op_music_segment_order import BASE as V402_BASE, apply_split as apply_v427  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_snd_load_ext_v461.cpp.in"
TEMPLATE_SHA = "cdb73658c3bba224871005271bd8c0f5657509d9a7c203525a996b166b5299b2"
TARGET_RESTORED_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
NEW_EXE = "53db8945c76daaf04124636d98e7c1d187eae252f75c21c29305edb446922301"
NEW_MAP = "572b323a047b7b448822cce7179613fb91a14703f4cd0b746339b5ce19b59da2"
SNDLEXT_OBJ_LINK_SHA = "d8bf694166b79e266a39415edc07cece251da7fb8c849230fbb1b457f9b5b732"
OPMUSIC_OBJ_NORM = "fd1796688022e6fecbdfbd54e38216a84b8d5fee10a269771db852cf86de7e55"
OPTAIL_OBJ_NORM = "eb708b7e423b2cb350b48ece06202631d4ddaaaaaadd46886cf4f2536dacc214"
SND_EXT_TARGET_SITES = [0xFD32, 0xFD2E, 0xFD2A, 0xFD26]
EXPECTED_MISMATCH_BLOCKS = [
    ("th04/bgimage.cpp", 186, 8, 8),
    ("th04_op_music_master.asm", 271, 35, 34),
    ("th04/score_e.cpp", 403, 2, 2),
    ("th04/hi_view.cpp", 405, 61, 61),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def outdir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-reloc-topology-v461-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def relocations(path: Path) -> list[int]:
    mz = parse_mz(path.read_bytes())
    if not mz.valid:
        raise ValueError(f"invalid MZ: {path}")
    return [row.linear for row in mz.relocations]


def replace_once_bytes(path: Path, needles: tuple[bytes, ...]) -> None:
    data = path.read_bytes()
    for needle in needles:
        if data.count(needle) == 1:
            path.write_bytes(data.replace(needle, b"", 1))
            return
    raise ValueError(f"source anchor drift: {path}")


def apply_v461(work: Path) -> None:
    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("snd-load extension template identity drift")
    shutil.copy2(TEMPLATE, work / "th04/sndlext.cpp")
    replace_once_bytes(
        work / "th04_op_master_data_tail.asm",
        (b"include th04/snd/load[data].asm\n", b"include th04/snd/load[data].asm\r\n"),
    )

    tup = work / "Tupfile.lua"
    text = tup.read_text()
    marker = 'th04:branch(MODEL_LARGE, { cflags = "-DBINARY=\'O\'" }):link("op", {'
    start = text.index(marker)
    end = text.index("\n})", start) + 3
    block = text[start:end]
    for line in (
        '\t{ "th04_op_master_tail.asm", o = "opmtail.obj" },\n',
        '\t{ "th04_op_music_master.asm", o = "opmusicm.obj" },\n',
    ):
        if block.count(line) != 1:
            raise ValueError(f"OP owner-line drift: {line!r}")
        block = block.replace(line, "", 1)
    replacements = (
        (
            '\t"th03/pi_load.cpp",\n',
            '\t"th03/pi_load.cpp",\n\t{ "th04_op_master_tail.asm", o = "opmtail.obj" },\n',
        ),
        (
            '\t"th04/snd_load.cpp",\n',
            '\t"th04/snd_load.cpp",\n\t"th04/sndlext.cpp",\n',
        ),
        (
            '\t"th04/op_setup.cpp",\n',
            '\t"th04/op_setup.cpp",\n\t{ "th04_op_music_master.asm", o = "opmusicm.obj" },\n',
        ),
    )
    for old, new in replacements:
        if block.count(old) != 1:
            raise ValueError(f"OP topology anchor drift: {old!r}")
        block = block.replace(old, new, 1)
    tup.write_text(text[:start] + block + text[end:])


def validate_payload(label: str, result: dict[str, object]) -> None:
    if result["payload_differing_bytes"] != 2:
        raise ValueError(f"{label}: payload difference count drift")
    if [row["start"] for row in result["payload_mismatch_runs"]] != [0xDE8B]:
        raise ValueError(f"{label}: payload mismatch location drift")
    if result["relocation_multiset_exact"] is not True:
        raise ValueError(f"{label}: relocation multiset drift")
    if result["target_payload_size"] != result["candidate_payload_size"]:
        raise ValueError(f"{label}: payload size drift")


def mismatch_blocks(sites: list[int], target: list[int], map_path: Path) -> list[tuple[str, int, int, int]]:
    contributions = map_contributions(map_path.read_bytes())
    owners: dict[int, str] = {}
    for site in sites:
        matches = [row for row in contributions if row["start"] <= site < row["end"]]
        if len(matches) != 1:
            raise ValueError(f"site 0x{site:X} has {len(matches)} MAP owners")
        owners[site] = str(matches[0]["module"])
    result = []
    for block in blocks(sites, owners):
        begin = block["first_index"]
        count = block["count"]
        diff = sum(sites[i] != target[i] for i in range(begin, begin + count))
        if diff:
            result.append((str(block["owner"]), begin, count, diff))
    return result


def sndlext_fixups(path: Path) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x9C:
            found.extend(fixup_locations(record.data))
    return found


def normalized_sha(path: Path) -> str:
    return digest(normalize_dependency_timestamps(path.read_bytes()))


def link_relevant_omf_sha(path: Path) -> str:
    """Hash every non-COMENT OMF record; Borland duplicates DOS time in E8/E9."""
    h = hashlib.sha256()
    for record in parse_omf(path.read_bytes()):
        if record.record_type == 0x88:
            continue
        h.update(bytes([record.record_type]))
        h.update(len(record.data).to_bytes(2, "little"))
        h.update(record.data)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--target-restored", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    source = args.source_dir.resolve()
    target_path = args.target_restored.resolve()
    output = outdir(args.output_dir)

    if not source.is_dir():
        parser.error("--source-dir must exist")
    for rel, expected in V402_BASE.items():
        path = source / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"v402 source identity drift: {rel}")
    if not target_path.is_file() or sha(target_path) != TARGET_RESTORED_SHA:
        raise ValueError("v228 OP target-restored identity drift")
    target_sites = relocations(target_path)

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source, work, symlinks=True)
        apply_v427(work)
        apply_v461(work)
        build(work, output / f"build-{label}.log")

        exe = work / "bin/th04/op.exe"
        map_path = work / "obj/th04/op.map"
        snd_obj = work / "obj/th04/sndlext.obj"
        tail_obj = work / "obj/th04/opmtail.obj"
        music_obj = work / "obj/th04/opmusicm.obj"
        payload = compare("th04-op", work)
        validate_payload(label, payload)
        sites = relocations(exe)
        if Counter(sites) != Counter(target_sites):
            raise ValueError(f"{label}: target relocation multiset drift")
        differing = [i for i, (left, right) in enumerate(zip(sites, target_sites)) if left != right]
        if len(differing) != 105:
            raise ValueError(f"{label}: expected 105 ordered mismatches, got {len(differing)}")
        if sites[158:162] != SND_EXT_TARGET_SITES or target_sites[158:162] != SND_EXT_TARGET_SITES:
            raise ValueError(f"{label}: SND_LOAD_EXT block is not target-index exact")
        residual = mismatch_blocks(sites, target_sites, map_path)
        if residual != EXPECTED_MISMATCH_BLOCKS:
            raise ValueError(f"{label}: residual owner topology drift: {residual}")
        fixups = sndlext_fixups(snd_obj)
        if fixups != [(3, 0x0C), (3, 0x08), (3, 0x04), (3, 0x00)]:
            raise ValueError(f"{label}: TC86 initializer FIXUPP order drift: {fixups}")
        identities = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "sndlext_object_link_relevant_sha256": link_relevant_omf_sha(snd_obj),
            "opmtail_object_normalized_sha256": normalized_sha(tail_obj),
            "opmusic_object_normalized_sha256": normalized_sha(music_obj),
        }
        expected_ids = {
            "exe_sha256": NEW_EXE,
            "map_sha256": NEW_MAP,
            "sndlext_object_link_relevant_sha256": SNDLEXT_OBJ_LINK_SHA,
            "opmtail_object_normalized_sha256": OPTAIL_OBJ_NORM,
            "opmusic_object_normalized_sha256": OPMUSIC_OBJ_NORM,
        }
        if identities != expected_ids:
            raise ValueError(f"{label}: output identity drift: {identities}")
        builds[label] = {
            **identities,
            "payload_comparison": payload,
            "ordered_relocation_mismatches": len(differing),
            "same_index_relocations": len(sites) - len(differing),
            "snd_load_ext_indices": [158, 159, 160, 161],
            "snd_load_ext_sites": SND_EXT_TARGET_SITES,
            "snd_load_ext_fixupp_locations": [[kind, loc] for kind, loc in fixups],
            "residual_mismatch_blocks": [list(row) for row in residual],
        }

    for key in (
        "exe_sha256",
        "map_sha256",
        "sndlext_object_link_relevant_sha256",
        "opmtail_object_normalized_sha256",
        "opmusic_object_normalized_sha256",
        "ordered_relocation_mismatches",
        "snd_load_ext_sites",
        "residual_mismatch_blocks",
    ):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B {key} differs")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP natural source/object topology replay; no MZ relocation editing and no authored-function promotion",
        "source_baseline": V402_BASE,
        "target_restored_sha256": TARGET_RESTORED_SHA,
        "snd_load_ext_template": str(TEMPLATE.relative_to(ROOT)),
        "snd_load_ext_template_sha256": TEMPLATE_SHA,
        "topology": {
            "master_tail_after": "th03/pi_load.cpp",
            "snd_load_ext_after": "th04/snd_load.cpp",
            "op_music_master_after": "th04/op_setup.cpp",
        },
        "builds": builds,
        "observed_effect": (
            "TC86 naturally emits the four SND_LOAD_EXT far-pointer FIXUPPs in target reverse order. Moving only physical owners across different/zero-byte segment contributions keeps the OP program image unchanged apart from the pre-existing two-byte snd_load residual, keeps the 804-site relocation multiset exact, makes SND_LOAD_EXT target-index exact at 158..161, and reduces ordered relocation mismatches from the v429 223-entry frontier to 105. The remaining mismatches are confined to BGIMAGE, OP music internal FIXUPP order, and score_e/hi_view interleaving."
        ),
        "limit": (
            "Candidate MAP/object names remain reconstruction aids. The replay does not prove historical filenames or promote OP authored functions, and the remaining 105 ordered relocations plus packed T topology still block packed-file closure."
        ),
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(receipt_path),
        "receipt_sha256": sha(receipt_path),
        "candidate_sha256": NEW_EXE,
        "ordered_mismatches": 105,
        "snd_load_ext_target_index_exact": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
