#!/usr/bin/env python3
"""Cold-compile one maintained MAINE cutscene helper and relink CUTSCENE_TEXT."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_score_hiscore_boundaries import branch_edges, disassemble  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
from replay_th04_zun_source_only import source_closure  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
import replay_th04_maine_score_insert as prior  # noqa: E402

SOURCE = ROOT / "src/maine/cutscene/box_animate.cpp"
BODY = ROOT / "src/maine/cutscene/box_animate.inl"
START = 0xA815
SIZE = 0x32
NEXT = START + SIZE
PRODUCER_START = 0xA292
PRODUCER_SIZE = 0xC3E
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "a37885def37b920a0c19ce2670e7a0e7468fb74069bfe4565cd44f4a3b8c6b9f"
BASE_CUTSCENE_SOURCE_SHA = "49fbde7cc661dda1d8a290debe285d625f4d274abb9c68c42d28150c59afb760"
BASE_CUTSCENE_OBJECT_SHA = "1ada8b7c8539aaaefe56c13e2e2407256207e25bde7ba9c9d532f2bba12c8f7e"
BASE_CUTSCENE_CODE_SHA = "a7e160b07189e0752a71705ad4d96fda85ba91fefb014574fa93019880f779a1"
BASE_FUNCTION_OBJECT_SHA = "3326df26ca33006dd3b584e1d8ec31477aa54f79beda90f864bcc86094684c5a"


def standalone_fixups(obj: Path) -> tuple[list[tuple[int, int]], int]:
    data = obj.read_bytes()
    pos = 0
    code_records = []
    fixups: list[tuple[int, int]] = []
    while pos < len(data):
        if pos + 3 > len(data):
            raise RuntimeError("truncated standalone OMF record header")
        kind = data[pos]
        length = int.from_bytes(data[pos + 1:pos + 3], "little")
        end = pos + 3 + length
        if length < 1 or end > len(data):
            raise RuntimeError("truncated standalone OMF record")
        payload = data[pos + 3:end - 1]
        if kind == 0xA0:  # LEDATA
            index_bytes = 1 if payload[0] < 0x80 else 2
            offset_pos = index_bytes
            segment_offset = int.from_bytes(payload[offset_pos:offset_pos + 2], "little")
            code_records.append((segment_offset, len(payload) - offset_pos - 2))
        elif kind == 0x9C:  # FIXUPP
            fixups.extend(fixup_locations(payload))
        pos = end
    if len(code_records) != 1 or code_records[0] != (0, SIZE):
        raise RuntimeError(f"standalone helper OMF LEDATA topology drift: {code_records}")
    return fixups, code_records[0][1]


def target_boundary(body: bytes) -> dict[str, object]:
    if len(body) != SIZE or prior.sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE target helper identity drift")
    nd = shutil.which("ndisasm")
    if nd is None:
        raise RuntimeError("ndisasm unavailable")
    rows = disassemble(nd, body, START)
    starts = {int(item["address"]) for item in rows}
    if (not rows or int(rows[0]["address"]) != START
            or any(int(a["address"]) + int(a["size"]) != int(b["address"])
                   for a, b in zip(rows, rows[1:]))
            or rows[-1]["mnemonic"] != "ret"
            or int(rows[-1]["address"]) + int(rows[-1]["size"]) != NEXT):
        raise RuntimeError("MAINE target helper tiling/RET drift")
    edges = branch_edges(rows)
    if any(not START <= dest < NEXT or dest not in starts for _, _, dest in edges):
        raise RuntimeError("MAINE target helper branch leaves body or enters data")
    return {
        "segment_identity": "1A05",
        "segment_offset": "07C5",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": prior.sha(body),
        "instruction_count": len(rows),
        "direct_branches": len(edges),
        "terminal": str(rows[-1]["text"]),
        "all_direct_branches_internal_aligned": True,
        "ndisasm": str(Path(nd).resolve()),
        "ndisasm_sha256": prior.sha_file(Path(nd).resolve()),
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th03/cutscene/cutscene.cpp"
    if prior.sha_file(upstream) != BASE_CUTSCENE_SOURCE_SHA:
        raise RuntimeError("pinned v489 cutscene translation unit drift")
    shutil.copytree(ROOT / "src/shared", work / "src/shared", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/maine/cutscene", work / "src/maine/cutscene", dirs_exist_ok=True)
    data = upstream.read_bytes()
    start_anchor = b"void near box_1_to_0_animate(void)\n{"
    end_anchor = b"\n#endif\n\n#if (GAME == 5)\nvoid pascal near box_wait_animate"
    if data.count(start_anchor) != 1 or data.count(end_anchor) != 1:
        raise RuntimeError("cutscene helper replacement anchors are not unique")
    start = data.index(start_anchor)
    end = data.index(end_anchor, start)
    if end <= start:
        raise RuntimeError("cutscene helper replacement range is inverted")
    upstream.write_bytes(
        data[:start] + b'#include "src/maine/cutscene/box_animate.inl"\n' + data[end:]
    )
    return prior.sha_file(upstream)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   capture_output=True, text=True, check=True)
    if prior.sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (prior.TARGET, prior.TARGET_SHA),
        (prior.SNAPSHOT / "bin/th04/maine.exe", prior.BASE_EXE_SHA),
        (prior.SNAPSHOT / "obj/th04/maine.map", prior.BASE_MAP_SHA),
        (prior.SNAPSHOT / "th03/cutscene/cutscene.cpp", BASE_CUTSCENE_SOURCE_SHA),
        (prior.SNAPSHOT / "obj/th04/cutscene.obj", BASE_CUTSCENE_OBJECT_SHA),
    ):
        if prior.sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    closure = source_closure(ROOT, ("src/maine/cutscene/box_animate.cpp",))
    source_hashes = {name: prior.sha_file(ROOT / name) for name in closure}
    target = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")
    body = target.program_image[START:NEXT]
    target_producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    boundary = target_boundary(body)
    if baseline.program_image[START:NEXT] != body:
        raise RuntimeError("v489 target-local helper bytes differ from restored target")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != target_producer:
        raise RuntimeError("v489 CUTSCENE_TEXT producer bytes differ from restored target")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 MAINE ordered relocations differ from target restore")

    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    if "0A05:07C5 idle  box_1_to_0_animate()" not in map_text:
        raise RuntimeError("v489 MAINE helper MAP entry drift")
    base_object = prior.SNAPSHOT / "obj/th04/cutscene.obj"
    base_omf = describe_omf(base_object.read_bytes())
    base_code = segment_bytes(base_object, "CUTSCENE_TEXT")
    if (not base_omf["valid"]
            or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
            or len(base_code) != PRODUCER_SIZE
            or prior.sha(base_code) != BASE_CUTSCENE_CODE_SHA
            or prior.sha(base_code[LOCAL_START:LOCAL_START + SIZE]) != BASE_FUNCTION_OBJECT_SHA):
        raise RuntimeError("pinned v489 CUTSCENE_TEXT producer drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        patched_source_sha = overlay_source(work)

        obj_dir = work / "obj/th04"
        objects_before = {path.name for path in obj_dir.glob("*.obj")}
        tcc(work, output, f"v573-box-animate-standalone-{label}",
            "src/maine/cutscene/box_animate.cpp")
        standalone_objects = [path for path in obj_dir.glob("*.obj")
                              if path.name not in objects_before]
        if len(standalone_objects) != 1:
            raise RuntimeError(f"{label}: expected one DOS-created standalone OMF object")
        local_obj = standalone_objects[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = segment_bytes(local_obj, "CUTSCENE_TEXT")
        if (not local_omf["valid"]
                or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
                or len(local_code) != SIZE):
            raise RuntimeError(f"{label}: standalone maintained helper OMF/code drift")
        standalone_omf_fixups, standalone_leddata_size = standalone_fixups(local_obj)

        group_obj_path = work / "obj/th04/cutscene.obj"
        group_obj_path.unlink()
        tcc(work, output, f"v573-box-animate-group-{label}", "th04/cutscene.cpp")
        group_omf = describe_omf(group_obj_path.read_bytes())
        group_code = segment_bytes(group_obj_path, "CUTSCENE_TEXT")
        if (not group_omf["valid"]
                or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
                or group_code != base_code):
            raise RuntimeError(f"{label}: maintained helper changed grouped CUTSCENE_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (not image.valid
                or prior.sha_file(exe) != prior.BASE_EXE_SHA
                or prior.sha_file(mp) != prior.BASE_MAP_SHA
                or [item.linear for item in image.relocations] != target_sites
                or linked != body or linked_producer != target_producer):
            raise RuntimeError(f"{label}: cold MAINE link/layout/helper bytes drift")
        standalone_diff_offsets = [
            index for index, (actual, expected) in enumerate(zip(
                local_code, base_code[LOCAL_START:LOCAL_START + SIZE]
            )) if actual != expected
        ]
        unresolved_internal_near_calls = sorted(
            offset for location, offset in standalone_omf_fixups
            if location == 1 and offset in {5, 20, 40}
        )
        expected_unresolved_call_bytes = sorted(
            byte for offset in unresolved_internal_near_calls for byte in (offset, offset + 1)
        )
        if (unresolved_internal_near_calls != [5, 20, 40]
                or standalone_diff_offsets != expected_unresolved_call_bytes):
            raise RuntimeError(f"{label}: standalone/grouped differences are not only internal near-call fixups")
        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "standalone_omf_sha256": prior.sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_size": len(local_code),
            "standalone_code_sha256": prior.sha(local_code),
            "standalone_vs_grouped_object_slice_raw_equal":
                local_code == base_code[LOCAL_START:LOCAL_START + SIZE],
            "standalone_vs_grouped_object_diff_offsets": standalone_diff_offsets,
            "standalone_ledata_size": standalone_leddata_size,
            "standalone_fixup_sites": [
                {"location_kind": location, "leddata_offset": offset}
                for location, offset in standalone_omf_fixups
            ],
            "unresolved_internal_near_call_fixup_offsets": unresolved_internal_near_calls,
            "group_omf_sha256": prior.sha_file(group_obj_path),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj_path),
            "group_code_sha256": prior.sha(group_code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": prior.sha(image.program_image),
            "linked_function_sha256": prior.sha(linked),
            "linked_producer_sha256": prior.sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }
    stable_a = {key: value for key, value in builds["a"].items()
                if key != "group_omf_sha256"}
    stable_b = {key: value for key, value in builds["b"].items()
                if key != "group_omf_sha256"}
    if stable_a != stable_b:
        raise RuntimeError("independent MAINE cutscene helper cold rounds differ")
    if any(prior.sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained cutscene source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed decoded helper and maintained-source cold-link replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "baseline_exe_sha256": prior.BASE_EXE_SHA,
        "baseline_map_sha256": prior.BASE_MAP_SHA,
        "baseline_cutscene_object_sha256": BASE_CUTSCENE_OBJECT_SHA,
        "baseline_cutscene_code_sha256": BASE_CUTSCENE_CODE_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": prior.sha_file(Path(__file__).resolve()),
        "boundary": boundary,
        "producer": {
            "segment": "CUTSCENE_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": prior.sha(target_producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "cold_determinism": {
            "exe_map_linked_program_and_code_equal": True,
            "standalone_omf_raw_equal": builds["a"]["standalone_omf_sha256"]
                == builds["b"]["standalone_omf_sha256"],
            "group_omf_raw_sha256_by_round": {
                label: builds[label]["group_omf_sha256"] for label in ("a", "b")
            },
            "group_omf_link_relevant_sha256_equal":
                builds["a"]["group_link_relevant_omf_sha256"]
                == builds["b"]["group_link_relevant_omf_sha256"],
            "group_object_metadata_note":
                "Raw group OMF may differ in Borland E9 dependency timestamp words only; equality is gated on the strict timestamp-normalized OMF digest.",
        },
        "limit": "Decoded 50-byte function only; no packed-file offset or complete MAINE exactness. v489 remains surrounding build scaffold.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(receipt_path), "function_raw_equal": True,
                      "ordered_relocations": len(target_sites)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
