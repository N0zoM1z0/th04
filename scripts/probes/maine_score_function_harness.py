"""Shared cold source/OMF/link gate for one MAINE SCORE_TEXT function.

This helper does not grant credit itself. A caller pins one target-reviewed
extent, semantic source, and source replacement anchors.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_score_hiscore_boundaries import branch_edges, disassemble, ghidra_rows  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
import replay_th04_maine_score_insert as prior  # noqa: E402


@dataclass(frozen=True)
class ScoreFunction:
    version: str
    name: str
    source: str
    body: str
    object_stem: str
    offset: int
    size: int
    segment_offset: int
    start_anchor: bytes
    end_anchor: bytes
    terminal: str
    map_public: str
    next_public: str
    target_references: tuple[bytes, ...]
    standalone_near_fixup_word: int | None = None
    standalone_near_fixup_words: tuple[int, ...] = ()
    translation_unit: str = "th04/score86.cpp"
    translation_unit_sha256: str | None = None
    replace_end_anchor: bool = False


def target_boundary(spec: ScoreFunction, body: bytes) -> dict[str, object]:
    row = ghidra_rows(prior.INVENTORY).get(spec.offset)
    linear = 0x10000 + spec.offset
    if row is None or (
        int(row["entry_linear"], 0) != linear
        or int(row["entry_segment"], 0) != 0x1A05
        or int(row["entry_offset"], 0) != spec.segment_offset
        or int(row["body_min_linear"], 0) != linear
        or int(row["body_max_linear"], 0) != linear + spec.size - 1
        or int(row["body_addresses"]) != spec.size
        or int(row["body_span"]) != spec.size
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
    ):
        raise RuntimeError(f"MAINE Ghidra {spec.name} extent drift")
    nd = shutil.which("ndisasm")
    if nd is None:
        raise RuntimeError("ndisasm unavailable")
    rows = disassemble(nd, body, spec.offset)
    starts = {int(item["address"]) for item in rows}
    if (not rows or int(rows[0]["address"]) != spec.offset
            or any(int(a["address"]) + int(a["size"]) != int(b["address"])
                   for a, b in zip(rows, rows[1:]))
            or rows[-1]["mnemonic"] != "ret"
            or int(rows[-1]["address"]) + int(rows[-1]["size"]) != spec.offset + spec.size
            or not str(rows[-1]["text"]).endswith(spec.terminal)):
        raise RuntimeError(f"MAINE target {spec.name} instruction/RET drift")
    edges = branch_edges(rows)
    if any(not spec.offset <= dest < spec.offset + spec.size or dest not in starts
           for _, _, dest in edges):
        raise RuntimeError(f"MAINE target {spec.name} direct branch escapes")
    for encoded in spec.target_references:
        if encoded not in body:
            raise RuntimeError(f"MAINE target {spec.name} reference drift: {encoded.hex()}")
    return {
        "segment_identity": "1A05",
        "segment_offset": f"{spec.segment_offset:04X}",
        "payload_offset": f"0x{spec.offset:X}",
        "size": spec.size,
        "target_sha256": prior.sha(body),
        "ghidra_span": spec.size,
        "instruction_count": len(rows),
        "direct_branches": len(edges),
        "terminal": str(rows[-1]["text"]),
        "all_direct_branches_internal_aligned": True,
    }


def overlay_source(spec: ScoreFunction, work: Path) -> None:
    path = work / spec.translation_unit
    expected = spec.translation_unit_sha256
    if expected is None and spec.translation_unit == "th04/score86.cpp":
        expected = prior.BASE_SCORE_SOURCE_SHA
    if expected is None or prior.sha_file(path) != expected:
        raise RuntimeError(f"v489 SCORE translation-unit drift: {spec.translation_unit}")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/maine/score", work / "src/maine/score", dirs_exist_ok=True)
    data = path.read_bytes()
    if data.count(spec.start_anchor) != 1 or data.count(spec.end_anchor) != 1:
        raise RuntimeError(f"{spec.name} source anchors not unique")
    start = data.index(spec.start_anchor)
    end = data.index(spec.end_anchor, start)
    if spec.replace_end_anchor:
        end += len(spec.end_anchor)
    include = f'#include "{spec.body}"\n\n'.encode("ascii")
    path.write_bytes(data[:start] + include + data[end:])


def run(spec: ScoreFunction, output: Path) -> Path:
    output = output.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        raise ValueError("output must be new below .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   capture_output=True, text=True, check=True)
    if prior.sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (prior.TARGET, prior.TARGET_SHA),
        (prior.SNAPSHOT / "bin/th04/maine.exe", prior.BASE_EXE_SHA),
        (prior.SNAPSHOT / "obj/th04/maine.map", prior.BASE_MAP_SHA),
        (prior.SNAPSHOT / "obj/th04/scoreall.obj", prior.BASE_SCORE_OBJECT_SHA),
        (prior.SNAPSHOT / "th04/score86.cpp", prior.BASE_SCORE_SOURCE_SHA),
        (prior.INVENTORY, prior.INVENTORY_SHA),
        (prior.ANALYSIS_IMAGE, prior.ANALYSIS_IMAGE_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"input identity drift: {path}")
    translation_unit = prior.SNAPSHOT / spec.translation_unit
    translation_unit_sha = prior.sha_file(translation_unit)
    expected_translation_unit_sha = spec.translation_unit_sha256
    if expected_translation_unit_sha is None and spec.translation_unit == "th04/score86.cpp":
        expected_translation_unit_sha = prior.BASE_SCORE_SOURCE_SHA
    if (expected_translation_unit_sha is None
            or translation_unit_sha != expected_translation_unit_sha):
        raise RuntimeError(f"candidate translation-unit identity drift: {translation_unit}")
    closure = source_closure(ROOT, (spec.source,))
    if spec.body not in closure:
        raise RuntimeError("bounded source body is not in compile closure")
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}
    target = parse_mz(prior.TARGET.read_bytes())
    base = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not base.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid MAINE target or candidate MZ")
    end = spec.offset + spec.size
    body = target.program_image[spec.offset:end]
    boundary = target_boundary(spec, body)
    if base.program_image[spec.offset:end] != body:
        raise RuntimeError(f"v489 MAINE {spec.name} body differs from target")
    target_sites = [row.linear for row in target.relocations]
    if [row.linear for row in base.relocations] != target_sites:
        raise RuntimeError("baseline MAINE ordered relocations not target-exact")
    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    if spec.map_public not in map_text or spec.next_public not in map_text:
        raise RuntimeError(f"MAINE {spec.name} MAP entry/adjacency drift")
    base_code = segment_bytes(prior.SNAPSHOT / "obj/th04/scoreall.obj", "SCORE_TEXT")
    if len(base_code) != prior.SCORE_OWNER_SIZE or prior.sha(base_code) != prior.BASE_SCORE_CODE_SHA:
        raise RuntimeError("baseline grouped SCORE object drift")
    local_start = spec.offset - prior.SCORE_OWNER_OFFSET
    object_body = base_code[local_start:local_start + spec.size]
    if len(object_body) != spec.size:
        raise RuntimeError("baseline SCORE object body missing")

    private.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True)
    builds = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        overlay_source(spec, work)
        tcc(work, output, f"{spec.version}-local-{label}", spec.source)
        local_obj = work / f"obj/th04/{spec.object_stem}.obj"
        local_omf = describe_omf(local_obj.read_bytes())
        if not local_omf["valid"] or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]:
            raise RuntimeError(f"{label}: standalone {spec.name} OMF drift")
        local_code = segment_bytes(local_obj, "SCORE_TEXT")
        differences = tuple(i for i, (left, right) in enumerate(zip(local_code, object_body))
                            if left != right)
        if len(local_code) != spec.size:
            raise RuntimeError(f"{label}: maintained {spec.name} standalone CODE size drift")
        if spec.standalone_near_fixup_word is not None and spec.standalone_near_fixup_words:
            raise RuntimeError(f"{spec.name}: conflicting near-fixup declarations")
        words = ((spec.standalone_near_fixup_word,)
                 if spec.standalone_near_fixup_word is not None
                 else spec.standalone_near_fixup_words)
        if not words:
            if differences:
                raise RuntimeError(f"{label}: maintained {spec.name} standalone CODE differs")
        else:
            expected = tuple(offset for word in words for offset in (word, word + 1))
            if (tuple(sorted(set(words))) != words or differences != expected
                    or any(word < 1 or word + 1 >= spec.size
                           or local_code[word - 1] != 0xE8 or object_body[word - 1] != 0xE8
                           for word in words)):
                raise RuntimeError(f"{label}: {spec.name} non-fixup CODE mismatch: {differences}")
            fixups = [location for record in parse_omf(local_obj.read_bytes())
                      if record.record_type == 0x9C
                      for _, location in fixup_locations(record.data)]
            if any(word not in fixups for word in words):
                raise RuntimeError(f"{label}: {spec.name} near-call OMF fixup missing")
        (work / "obj/th04/scoreall.obj").unlink()
        tcc(work, output, f"{spec.version}-group-{label}", "th04/scoreall.cpp")
        group_obj = work / "obj/th04/scoreall.obj"
        group_omf = describe_omf(group_obj.read_bytes())
        if not group_omf["valid"] or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]:
            raise RuntimeError(f"{label}: grouped SCORE OMF drift")
        if segment_bytes(group_obj, "SCORE_TEXT") != base_code:
            raise RuntimeError(f"{label}: grouped SCORE CODE changed")
        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink(); mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[spec.offset:end]
        if (not image.valid or prior.sha_file(exe) != prior.BASE_EXE_SHA
                or prior.sha_file(mp) != prior.BASE_MAP_SHA
                or [row.linear for row in image.relocations] != target_sites
                or image.program_image != base.program_image or linked != body):
            raise RuntimeError(f"{label}: MAINE {spec.name} linked function/layout mismatch")
        builds[label] = {
            "standalone_object_link_relevant_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": prior.sha(local_code),
            "standalone_code_difference_offsets": differences,
            "standalone_near_fixup_word": spec.standalone_near_fixup_word,
            **({"standalone_near_fixup_words": words} if spec.standalone_near_fixup_words else {}),
            "group_object_link_relevant_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": prior.sha(base_code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_function_sha256": prior.sha(linked),
            "raw_function_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }
    if builds["a"] != builds["b"]:
        raise RuntimeError(f"cold MAINE {spec.name} rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained SCORE source changed during replay")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": f"MAINE target-reviewed {spec.name} maintained-source decoded raw replay",
        "target_restored_sha256": prior.TARGET_SHA,
        "inventory_sha256": prior.INVENTORY_SHA,
        "analysis_image_sha256": prior.ANALYSIS_IMAGE_SHA,
        "baseline_exe_sha256": prior.BASE_EXE_SHA,
        "candidate_translation_unit": spec.translation_unit,
        "candidate_translation_unit_sha256": translation_unit_sha,
        "replaced_end_anchor": spec.replace_end_anchor,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "builds": builds,
        "limit": "Decoded function only; no packed offset, complete SCORE TU, or whole MAINE exact claim. Surrounding v489 source remains candidate scaffold.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "function_raw_equal": True,
                      "ordered_relocations": prior.RELOCATIONS}, sort_keys=True))
    return path
