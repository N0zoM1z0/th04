#!/usr/bin/env python3
"""Replay TH04 OP's OP_MUSIC_TEXT as a separate OMF contribution.

This is packed/link-topology diagnostic evidence only. The replay does not edit
MZ relocation-table bytes. It splits the existing th04_op.asm OP_MUSIC_TEXT
source segment into its own TASM object and places the already-separated master
CODE objects before historical VS/DATA ownership, preserving all code/data
bytes and the v402 snd_load-only payload residual.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import normalize_dependency_timestamps  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_master_object_split import build, compare, sha  # noqa: E402

TEMPLATE = ROOT / "config/replay/th04_op_music_segment_v427.asm.in"
TEMPLATE_SHA = "45aeb5c9f38a4210dfbdc611b7b47b0fdc380bfb2864e318c98d4fd2c9832b6e"
BASE = {
    "Tupfile.lua": "c753fc557e97ac10872bd7a8a7a2f07200193082889fb78160edcfaf22915a8e",
    "th04_op.asm": "a6b68a17662d865d64a4b2469c8f7751d506d0b8fd2ebddf66a779df2a4e59d3",
    "th04/zunsoft.asm": "f9dc8b94e98521d54bab6cde88e540c021a33bd887234a5ba66e71acd9dcfdec",
    "bin/th04/op.exe": "5a7af3868e28e2bc46268d413f8f7e78213603431b3c1acc3e4f85f4d8cb95eb",
    "obj/th04/op.map": "08ab21543cc5e7c58e29a566538011aab3514adb5d3193216df7e44d671b0cf3",
}
REFERENCE_CANDIDATE_SHA = "cb9b1c6cbd6b2c7bad6763fabd106c3cf451b1c20efef0f1fcfd3e3a47c0cdaa"
NEW_EXE = "78468a2ae389ba9c97fb7b391355e4eda2cb750f84f3cc4abf3e34802bceafbd"
NEW_MAP = "cd2e0a35b1d1262dca398db0302ab68243179cf18edfac2e1ec0810acf2ef334"
NEW_MUSIC_OBJ_NORM = "fd1796688022e6fecbdfbd54e38216a84b8d5fee10a269771db852cf86de7e55"

OLD_ORDER = '''\t{ "th04_op.asm", o = "op.obj" },\n\t"vsorig.obj",\n\t{ "th04_op_master_data_tail.asm", o = "opmdata.obj" },\n\t{ "th04_op_master_mid.asm", o = "opmmid.obj" },\n\t{ "th04_op_master_tail.asm", o = "opmtail.obj" },\n'''
NEW_ORDER = '''\t{ "th04_op.asm", o = "op.obj" },\n\t{ "th04_op_master_mid.asm", o = "opmmid.obj" },\n\t{ "th04_op_master_tail.asm", o = "opmtail.obj" },\n\t"vsorig.obj",\n\t{ "th04_op_master_data_tail.asm", o = "opmdata.obj" },\n\t{ "th04_op_music_master.asm", o = "opmusicm.obj" },\n'''
SEGMENT_START = "OP_MUSIC_TEXT segment byte public 'CODE' use16"
SEGMENT_END = "OP_MUSIC_TEXT ends"
EMPTY_SEGMENT = "OP_MUSIC_TEXT segment byte public 'CODE' use16\nOP_MUSIC_TEXT ends"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def output_dir(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-music-segment-", dir=parent))
    out = path.resolve()
    if out.exists() or not out.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    out.mkdir(parents=True)
    return out


def relocation_sites(path: Path) -> list[int]:
    image = parse_mz(path.read_bytes())
    if not image.valid:
        raise ValueError(f"invalid MZ: {path}")
    return [item.linear for item in image.relocations]


def order_metrics(candidate: list[int], target: list[int]) -> dict[str, object]:
    if Counter(candidate) != Counter(target):
        raise ValueError("relocation multisets differ")
    differing = [i for i, (left, right) in enumerate(zip(candidate, target)) if left != right]
    return {
        "count": len(candidate),
        "multiset_exact": True,
        "ordered_exact": not differing,
        "differing_indices": differing,
        "first_mismatch": differing[0] if differing else None,
        "last_mismatch": differing[-1] if differing else None,
        "same_index_count": sum(left == right for left, right in zip(candidate, target)),
        "mismatch_pairs": [[i, candidate[i], target[i]] for i in differing],
    }


def validate_payload(label: str, result: dict[str, object]) -> None:
    if result["payload_differing_bytes"] != 2:
        raise ValueError(f"{label}: payload differing-byte count drift")
    if [item["start"] for item in result["payload_mismatch_runs"]] != [0xDE8B]:
        raise ValueError(f"{label}: payload mismatch location drift")
    if result["relocation_multiset_exact"] is not True:
        raise ValueError(f"{label}: relocation multiset drift")
    if result["target_payload_size"] != result["candidate_payload_size"]:
        raise ValueError(f"{label}: payload size drift")


def apply_split(work: Path) -> None:
    head = work / "th04_op.asm"
    text = head.read_text()
    start = text.index(SEGMENT_START)
    finish = text.index(SEGMENT_END, start) + len(SEGMENT_END)
    body = text[start:finish]
    if "include th04/zunsoft.asm" not in body or body.count(SEGMENT_START) != 1:
        raise ValueError("OP_MUSIC_TEXT source span drift")
    head.write_text(text[:start] + EMPTY_SEGMENT + text[finish:])

    if sha(TEMPLATE) != TEMPLATE_SHA:
        raise ValueError("v427 OP music template identity drift")
    shutil.copy2(TEMPLATE, work / "th04_op_music_master.asm")

    tup = work / "Tupfile.lua"
    text = tup.read_text()
    if text.count(OLD_ORDER) != 1:
        raise ValueError("OP link-order anchor drift")
    tup.write_text(text.replace(OLD_ORDER, NEW_ORDER, 1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--reference-candidate", "--target-restored", dest="reference_candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    reference_candidate = args.reference_candidate.resolve()
    output = output_dir(args.output_dir)

    if not source_dir.is_dir():
        parser.error("--source-dir must exist")
    for rel, expected in BASE.items():
        path = source_dir / rel
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f"v402 baseline identity drift: {rel}")
    if not reference_candidate.is_file() or sha(reference_candidate) != REFERENCE_CANDIDATE_SHA:
        raise ValueError("reference-candidate OP identity drift")

    reference_sites = relocation_sites(reference_candidate)
    baseline_order = order_metrics(relocation_sites(source_dir / "bin/th04/op.exe"), reference_sites)
    if baseline_order["differing_indices"] != list(range(145, 188)):
        raise ValueError(f"v402 baseline order drift: {baseline_order}")
    baseline_payload = compare("th04-op", source_dir)
    validate_payload("baseline", baseline_payload)

    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "source"
        shutil.copytree(source_dir, work, symlinks=True)
        apply_split(work)
        build(work, output / f"build-{label}.log")
        payload = compare("th04-op", work)
        validate_payload(label, payload)
        exe = work / "bin/th04/op.exe"
        map_path = work / "obj/th04/op.map"
        music_obj = work / "obj/th04/opmusicm.obj"
        order = order_metrics(relocation_sites(exe), reference_sites)
        if order["ordered_exact"] is not True or order["same_index_count"] != 804:
            raise ValueError(f"{label}: v231 candidate-control relocation order not exact: {order}")
        normalized = digest(normalize_dependency_timestamps(music_obj.read_bytes()))
        if sha(exe) != NEW_EXE or sha(map_path) != NEW_MAP or normalized != NEW_MUSIC_OBJ_NORM:
            raise ValueError(f"{label}: output identity drift")
        builds[label] = {
            "exe_sha256": sha(exe),
            "map_sha256": sha(map_path),
            "music_object_sha256": sha(music_obj),
            "music_object_normalized_sha256": normalized,
            "relocation_order_vs_reference_candidate": order,
            "payload_comparison": payload,
        }

    for key in ("exe_sha256", "map_sha256", "music_object_normalized_sha256", "relocation_order_vs_reference_candidate"):
        if builds["a"][key] != builds["b"][key]:
            raise ValueError(f"A/B {key} differs")
    left = dict(builds["a"]["payload_comparison"])
    right = dict(builds["b"]["payload_comparison"])
    left.pop("candidate_path", None)
    right.pop("candidate_path", None)
    if left != right:
        raise ValueError("A/B payload comparison differs")

    receipt = {
        "schema_version": 1,
        "claim_scope": "TH04 OP OP_MUSIC_TEXT physical-object/v231 candidate-control relocation-order diagnostic; no packed-file or authored exactness claim",
        "baseline_identity": BASE,
        "reference_candidate_sha256": REFERENCE_CANDIDATE_SHA,
        "template_path": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": TEMPLATE_SHA,
        "baseline_relocation_order_vs_reference_candidate": baseline_order,
        "baseline_payload_comparison": baseline_payload,
        "object_order_after": ["op.obj", "opmmid.obj", "opmtail.obj", "vsorig.obj", "opmdata.obj", "opmusicm.obj"],
        "builds": builds,
        "observed_effect": (
            "Splitting only th04_op.asm's existing OP_MUSIC_TEXT source segment into its own TASM object and placing master CODE before VS/DATA ownership preserves the snd_load-only two-byte payload residual and the 804-site relocation multiset, while making the candidate MZ relocation table order identical to the pinned DIET-v231 candidate-control MZ table at all 804 indices. No relocation-table bytes are edited."
        ),
        "limit": (
            "DIET decompressor application order is a separate diagnostic surface and still differs from candidate MZ order; the v231 candidate-control MZ table is not independently proven to be the historical pre-DIET TLINK table. This replay grants no OP authored-source/function or packed-file exactness credit."
        ),
    }
    rp = output / "receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(rp),
        "receipt_sha256": sha(rp),
        "candidate_op_sha256": NEW_EXE,
        "reference_candidate_relocation_order_exact": True,
        "remaining_payload_differences": 2,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
