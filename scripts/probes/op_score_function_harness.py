"""Cold source/OMF/link gate for one OP SCORE_TEXT decoded function."""

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
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
import replay_th04_op_stage_put as prior  # noqa: E402


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
    standalone_near_fixup_words: tuple[int, ...] = ()
    standalone_data_fixup_words: tuple[int, ...] = ()
    ghidra_prefix_size: int | None = None
    translation_unit: str = "th04/hiscore/view.cpp"
    translation_unit_sha256: str | None = None
    replace_end_anchor: bool = False
    target_data_references: tuple[tuple[int, bytes], ...] = ()


def target_boundary(spec: ScoreFunction, body: bytes) -> dict[str, object]:
    row = prior.ghidra_rows(prior.INVENTORY).get(spec.offset)
    linear = 0x10000 + spec.offset
    ghidra_size = spec.ghidra_prefix_size or spec.size
    if spec.ghidra_prefix_size is not None and (
        spec.name != "rank_render" or spec.offset != 0xCA1A or spec.size != 0x7A
        or ghidra_size != 0x3C or body[0x3A:0x3C] != b"\xeb\x05"
    ):
        raise RuntimeError("OP rank_render Ghidra-tail exception drift")
    if row is None or (
        int(row["entry_linear"], 0) != linear
        or int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != spec.segment_offset
        or int(row["body_min_linear"], 0) != linear
        or int(row["body_max_linear"], 0) != linear + ghidra_size - 1
        or int(row["body_addresses"]) != ghidra_size
        or int(row["body_span"]) != ghidra_size
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
    ):
        raise RuntimeError(f"OP Ghidra {spec.name} extent drift")
    nd = shutil.which("ndisasm")
    if nd is None:
        raise RuntimeError("ndisasm unavailable")
    rows = prior.disassemble(nd, body, spec.offset)
    starts = {int(item["address"]) for item in rows}
    if (not rows or int(rows[0]["address"]) != spec.offset
            or any(int(a["address"]) + int(a["size"]) != int(b["address"])
                   for a, b in zip(rows, rows[1:]))
            or rows[-1]["mnemonic"] != "ret"
            or int(rows[-1]["address"]) + int(rows[-1]["size"]) != spec.offset + spec.size
            or not str(rows[-1]["text"]).endswith(spec.terminal)):
        raise RuntimeError(f"OP target {spec.name} instruction/RET drift")
    edges = prior.branch_edges(rows)
    if spec.ghidra_prefix_size is not None and not any(
        source == 0xCA54 and destination == 0xCA5B
        for source, _, destination in edges
    ):
        raise RuntimeError("OP rank_render reachable tail lost")
    if any(not spec.offset <= dest < spec.offset + spec.size or dest not in starts
           for _, _, dest in edges):
        raise RuntimeError(f"OP target {spec.name} direct branch escapes")
    for encoded in spec.target_references:
        if encoded not in body:
            raise RuntimeError(f"OP target {spec.name} reference drift: {encoded.hex()}")
    return {
        "segment_identity": "1A74",
        "segment_offset": f"{spec.segment_offset:04X}",
        "payload_offset": f"0x{spec.offset:X}",
        "size": spec.size,
        "target_sha256": prior.sha(body),
        "ghidra_span": ghidra_size,
        **({"target_reviewed_span": spec.size} if spec.ghidra_prefix_size is not None else {}),
        "instruction_count": len(rows),
        "direct_branches": len(edges),
        "terminal": str(rows[-1]["text"]),
        "all_direct_branches_internal_aligned": True,
    }


def overlay_source(spec: ScoreFunction, work: Path) -> None:
    path = work / spec.translation_unit
    expected = spec.translation_unit_sha256
    if expected is None:
        expected = prior.INPUTS.get(prior.SNAPSHOT / spec.translation_unit)
    if expected is None or prior.sha_file(path) != expected:
        raise RuntimeError(f"v489 OP high-score source drift: {spec.translation_unit}")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/op/score", work / "src/op/score", dirs_exist_ok=True)
    data = path.read_bytes()
    if data.count(spec.start_anchor) != 1:
        raise RuntimeError(f"{spec.name} source start anchor not unique")
    start = data.index(spec.start_anchor)
    if spec.end_anchor not in data[start:]:
        raise RuntimeError(f"{spec.name} source end anchor missing after start")
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
    if prior.sha_file(prior.RUNNER) != prior.RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in prior.INPUTS.items():
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"input identity drift: {path}")
    translation_unit = prior.SNAPSHOT / spec.translation_unit
    translation_unit_sha = prior.sha_file(translation_unit)
    expected_translation_unit_sha = spec.translation_unit_sha256
    if expected_translation_unit_sha is None:
        expected_translation_unit_sha = prior.INPUTS.get(translation_unit)
    if (expected_translation_unit_sha is None
            or translation_unit_sha != expected_translation_unit_sha):
        raise RuntimeError(f"candidate OP translation-unit identity drift: {translation_unit}")
    closure = prior.source_closure(ROOT, (spec.source,))
    if spec.body not in closure:
        raise RuntimeError("bounded source body is not in compile closure")
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}
    target = parse_mz(prior.TARGET.read_bytes())
    base = parse_mz((prior.SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not base.valid or len(target.relocations) != prior.EXPECTED_RELOCATIONS:
        raise RuntimeError("invalid OP target or candidate MZ")
    for offset, expected in spec.target_data_references:
        if target.program_image[offset:offset + len(expected)] != expected:
            raise RuntimeError(f"OP target {spec.name} data reference drift at {offset:#x}")
    end = spec.offset + spec.size
    body = target.program_image[spec.offset:end]
    boundary = target_boundary(spec, body)
    if base.program_image[spec.offset:end] != body:
        raise RuntimeError(f"v489 OP {spec.name} body differs from target")
    target_sites = [row.linear for row in target.relocations]
    if [row.linear for row in base.relocations] != target_sites:
        raise RuntimeError("baseline OP ordered relocations not target-exact")
    map_text = (prior.SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    if (spec.map_public and spec.map_public not in map_text) or (
        spec.next_public and spec.next_public not in map_text
    ):
        raise RuntimeError(f"OP {spec.name} MAP entry/adjacency drift")
    base_code = prior.segment_bytes(prior.SNAPSHOT / "obj/th04/scall.obj", "SCORE_TEXT")
    if len(base_code) != prior.SCORE_SIZE:
        raise RuntimeError("baseline grouped OP SCORE object drift")
    local_start = spec.offset - prior.SCORE_START
    object_body = base_code[local_start:local_start + spec.size]
    if len(object_body) != spec.size:
        raise RuntimeError("baseline OP SCORE object body missing")

    private.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True)
    builds = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        copy_compact_snapshot(prior.SNAPSHOT, work, "op")
        overlay_source(spec, work)
        prior.tcc(work, output, f"{spec.version}-local-{label}", spec.source)
        local_obj = work / f"obj/th04/{spec.object_stem}.obj"
        local_omf = describe_omf(local_obj.read_bytes())
        if not local_omf["valid"] or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]:
            raise RuntimeError(f"{label}: standalone {spec.name} OMF drift")
        local_code = prior.segment_bytes(local_obj, "SCORE_TEXT")
        differences = tuple(i for i, (left, right) in enumerate(zip(local_code, object_body))
                            if left != right)
        if len(local_code) != spec.size:
            raise RuntimeError(f"{label}: standalone {spec.name} CODE size drift")
        near_words = spec.standalone_near_fixup_words
        data_words = spec.standalone_data_fixup_words
        words = tuple(sorted(near_words + data_words))
        if not words:
            if differences:
                raise RuntimeError(f"{label}: {spec.name} standalone CODE differs: {differences}")
        else:
            allowed = {offset for word in words for offset in (word, word + 1)}
            if (tuple(sorted(set(words))) != words
                    or any(word < 1 or word + 1 >= spec.size
                           or local_code[word - 1] != 0xE8 or object_body[word - 1] != 0xE8
                           for word in near_words)
                    or any(word < 1 or word + 1 >= spec.size for word in data_words)
                    or not set(differences).issubset(allowed)
                    or any(word not in differences and word + 1 not in differences for word in words)):
                raise RuntimeError(f"{label}: {spec.name} non-fixup CODE mismatch: {differences}")
            fixups = [location for record in parse_omf(local_obj.read_bytes())
                      if record.record_type == 0x9C
                      for _, location in fixup_locations(record.data)]
            if any(word not in fixups for word in words):
                raise RuntimeError(f"{label}: {spec.name} declared OMF fixup missing")
        (work / "obj/th04/scall.obj").unlink()
        prior.tcc(work, output, f"{spec.version}-group-{label}", "th04/scall.cpp")
        group_obj = work / "obj/th04/scall.obj"
        group_omf = describe_omf(group_obj.read_bytes())
        if not group_omf["valid"] or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]:
            raise RuntimeError(f"{label}: grouped OP SCORE OMF drift")
        if prior.segment_bytes(group_obj, "SCORE_TEXT") != base_code:
            raise RuntimeError(f"{label}: grouped OP SCORE CODE changed")
        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink(); mp.unlink()
        prior.run_checked(["wine", str(prior.RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
                          work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[spec.offset:end]
        if (not image.valid or prior.sha_file(exe) != prior.INPUTS[prior.SNAPSHOT / "bin/th04/op.exe"]
                or prior.sha_file(mp) != prior.INPUTS[prior.SNAPSHOT / "obj/th04/op.map"]
                or [row.linear for row in image.relocations] != target_sites
                or image.program_image != base.program_image or linked != body):
            raise RuntimeError(f"{label}: OP {spec.name} linked function/layout mismatch")
        builds[label] = {
            "standalone_object_link_relevant_sha256": prior.link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": prior.sha(local_code),
            "standalone_code_difference_offsets": differences,
            "standalone_near_fixup_words": near_words,
            "standalone_data_fixup_words": data_words,
            "group_object_link_relevant_sha256": prior.link_relevant_omf_sha(group_obj),
            "group_code_sha256": prior.sha(base_code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_function_sha256": prior.sha(linked),
            "raw_function_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }
    if builds["a"] != builds["b"]:
        raise RuntimeError(f"cold OP {spec.name} rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained OP SCORE source changed during replay")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": f"OP target-reviewed {spec.name} maintained-source decoded raw replay",
        "target_restored_sha256": prior.INPUTS[prior.TARGET],
        "inventory_sha256": prior.INPUTS[prior.INVENTORY],
        "analysis_image_sha256": prior.INPUTS[prior.ANALYSIS_IMAGE],
        "baseline_exe_sha256": prior.INPUTS[prior.SNAPSHOT / "bin/th04/op.exe"],
        "candidate_translation_unit": spec.translation_unit,
        "candidate_translation_unit_sha256": translation_unit_sha,
        "replaced_end_anchor": spec.replace_end_anchor,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "target_data_references": [
            {"payload_offset": f"0x{offset:X}", "bytes_hex": expected.hex(),
             "sha256": prior.sha(expected)}
            for offset, expected in spec.target_data_references
        ],
        "candidate_map": {
            "sha256": prior.INPUTS[prior.SNAPSHOT / "obj/th04/op.map"],
            "public_at_start": spec.map_public,
            "next_public": spec.next_public,
            "role": "candidate link corroboration, not original symbol provenance",
        },
        "builds": builds,
        "limit": "Decoded function only; no packed offset, complete SCORE TU, or whole OP exact claim. Surrounding v489 source remains candidate scaffold.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "function_raw_equal": True,
                      "ordered_relocations": prior.EXPECTED_RELOCATIONS}, sort_keys=True))
    return path
