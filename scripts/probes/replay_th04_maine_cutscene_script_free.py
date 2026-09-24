#!/usr/bin/env python3
"""Cold-compile the maintained TH04 cutscene-script no-op and relink MAINE."""

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

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from inspect_dialog_fixup_order import omf_index  # noqa: E402
from lib.omf import describe_omf, parse_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_segment_topology_v470 import tcc  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from probe_th04_score_hiscore_boundaries import branch_edges, disassemble  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402
import replay_th04_maine_score_insert as prior  # noqa: E402

SOURCE = ROOT / "src/maine/cutscene/script_free.cpp"
BODY = ROOT / "src/maine/cutscene/script_free.inl"
START = 0xA2D1
SIZE = 0x05
NEXT = START + SIZE
PRODUCER_START = 0xA292
PRODUCER_SIZE = 0xC3E
LOCAL_START = START - PRODUCER_START
TARGET_FUNCTION_SHA = "7178bc05f1e5707e6c3dae3e068488f3df05d53b0e5eb728edd1abc56533f087"
BASE_CUTSCENE_SOURCE_SHA = "49fbde7cc661dda1d8a290debe285d625f4d274abb9c68c42d28150c59afb760"
BASE_CUTSCENE_OBJECT_SHA = "1ada8b7c8539aaaefe56c13e2e2407256207e25bde7ba9c9d532f2bba12c8f7e"
BASE_CUTSCENE_CODE_SHA = "a7e160b07189e0752a71705ad4d96fda85ba91fefb014574fa93019880f779a1"


def loose_segment_bytes(path: Path, segment_name: str) -> bytes:
    records = parse_omf(path.read_bytes())
    names = [""]
    segments: list[str] = []
    for record in records:
        if record.record_type == 0x96:
            pos = 0
            while pos < len(record.data):
                length = record.data[pos]
                names.append(record.data[pos + 1:pos + 1 + length].decode("latin-1"))
                pos += length + 1
        elif record.record_type == 0x98:
            data = record.data
            pos = 1 + (3 if (data[0] >> 5) == 0 else 2)
            name_index, _ = omf_index(data, pos)
            segments.append(names[name_index])
    if segments.count(segment_name) != 1:
        raise RuntimeError(f"expected one {segment_name} segment: {segments}")
    wanted = segments.index(segment_name) + 1
    chunks: list[tuple[int, bytes]] = []
    for record in records:
        if record.record_type != 0xA0:
            continue
        index, pos = omf_index(record.data, 0)
        if index != wanted:
            continue
        offset = int.from_bytes(record.data[pos:pos + 2], "little")
        chunks.append((offset, record.data[pos + 2:]))
    if not chunks:
        raise RuntimeError(f"{segment_name} has no LEDATA")
    chunks.sort()
    out = bytearray()
    for offset, payload in chunks:
        if offset != len(out):
            raise RuntimeError(f"{segment_name} LEDATA gap/overlap at {offset:#x}")
        out += payload
    return bytes(out)


def target_boundary(body: bytes) -> dict[str, object]:
    if len(body) != SIZE or prior.sha(body) != TARGET_FUNCTION_SHA:
        raise RuntimeError("MAINE cutscene_script_free target identity drift")
    nd = shutil.which("ndisasm")
    if nd is None:
        raise RuntimeError("ndisasm unavailable")
    rows = disassemble(nd, body, START)
    expected = ["push", "mov", "pop", "ret"]
    if (
        len(rows) != 4
        or [str(row["mnemonic"]) for row in rows] != expected
        or int(rows[0]["address"]) != START
        or any(int(a["address"]) + int(a["size"]) != int(b["address"])
               for a, b in zip(rows, rows[1:]))
        or int(rows[-1]["address"]) + int(rows[-1]["size"]) != NEXT
        or branch_edges(rows)
    ):
        raise RuntimeError(f"MAINE cutscene_script_free decode drift: {rows!r}")
    return {
        "segment_identity": "1A05",
        "segment_offset": "0281",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": prior.sha(body),
        "instruction_count": len(rows),
        "terminal": str(rows[-1]["text"]),
        "direct_branches": 0,
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th03/cutscene/cutscene.cpp"
    if prior.sha_file(upstream) != BASE_CUTSCENE_SOURCE_SHA:
        raise RuntimeError("pinned v489 cutscene translation unit drift")
    destination = work / "src/maine/cutscene"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, destination / BODY.name)
    data = upstream.read_bytes()
    old = (
        b"void near cutscene_script_free(void)\n"
        b"{\n"
        b"#if (GAME == 3)\n"
        b"\tif(script) {\n"
        b"\t\tHMem<unsigned char>::free(script);\n"
        b"\t\tscript = nullptr;\n"
        b"\t}\n"
        b"#endif\n"
        b"}"
    )
    replacement = b'#include "src/maine/cutscene/script_free.inl"'
    if data.count(old) != 1:
        raise RuntimeError("cutscene_script_free replacement anchor drift")
    upstream.write_bytes(data.replace(old, replacement, 1))
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

    source_hashes = {
        "src/maine/cutscene/script_free.cpp": prior.sha_file(SOURCE),
        "src/maine/cutscene/script_free.inl": prior.sha_file(BODY),
    }
    target = parse_mz(prior.TARGET.read_bytes())
    baseline = parse_mz((prior.SNAPSHOT / "bin/th04/maine.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != prior.RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 MAINE candidate")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 MAINE ordered relocations differ from target restore")

    body = target.program_image[START:NEXT]
    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    boundary = target_boundary(body)
    if baseline.program_image[START:NEXT] != body:
        raise RuntimeError("v489 cutscene_script_free bytes differ from target")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 CUTSCENE_TEXT differs from target")

    map_text = (prior.SNAPSHOT / "obj/th04/maine.map").read_text(encoding="cp437")
    if "0A05:0281       cutscene_script_free()" not in map_text:
        raise RuntimeError("v489 cutscene_script_free MAP public drift")

    base_object = prior.SNAPSHOT / "obj/th04/cutscene.obj"
    base_code = segment_bytes(base_object, "CUTSCENE_TEXT")
    if len(base_code) != PRODUCER_SIZE or prior.sha(base_code) != BASE_CUTSCENE_CODE_SHA:
        raise RuntimeError("pinned CUTSCENE_TEXT object contribution drift")
    if base_code[LOCAL_START:LOCAL_START + SIZE] != body:
        raise RuntimeError("pinned object cutscene_script_free differs from target")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "maine/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(prior.SNAPSHOT, work, "maine")
        destination = work / "src/maine/cutscene"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, destination / SOURCE.name)
        shutil.copy2(BODY, destination / BODY.name)

        objects_before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc(work, output, f"v582-script-free-standalone-{label}",
            "src/maine/cutscene/script_free.cpp")
        standalone = [path for path in (work / "obj/th04").glob("*.obj")
                      if path.name not in objects_before]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "CUTSCENE_TEXT")
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != body
            or any(record.record_type == 0x9C for record in parse_omf(local_obj.read_bytes()))
        ):
            raise RuntimeError(f"{label}: standalone no-op OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/cutscene.obj"
        group_obj.unlink()
        tcc(work, output, f"v582-script-free-group-{label}", "th04/cutscene.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "CUTSCENE_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained no-op changed grouped CUTSCENE_TEXT")

        exe = work / "bin/th04/maine.exe"
        mp = work / "obj/th04/maine.map"
        exe.unlink()
        mp.unlink()
        run_checked(["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\maine.@l"],
                    work, output / f"link-{label}.log")
        image = parse_mz(exe.read_bytes())
        linked_body = image.program_image[START:NEXT]
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or prior.sha_file(exe) != prior.BASE_EXE_SHA
            or prior.sha_file(mp) != prior.BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or linked_body != body
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked MAINE layout/body drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "standalone_object_sha256": prior.sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": prior.sha(local_code),
            "standalone_code_size": len(local_code),
            "standalone_fixupp_records": sum(
                record.record_type == 0x9C for record in parse_omf(local_obj.read_bytes())
            ),
            "group_object_sha256": prior.sha_file(group_obj),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": prior.sha(group_code),
            "linked_exe_sha256": prior.sha_file(exe),
            "linked_map_sha256": prior.sha_file(mp),
            "linked_program_sha256": prior.sha(image.program_image),
            "linked_function_sha256": prior.sha(linked_body),
            "linked_producer_sha256": prior.sha(linked_producer),
            "raw_function_difference_count": 0,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable_keys = (
        "standalone_link_relevant_omf_sha256", "standalone_code_sha256",
        "standalone_code_size", "standalone_fixupp_records",
        "group_link_relevant_omf_sha256", "group_code_sha256",
        "linked_exe_sha256", "linked_map_sha256", "linked_program_sha256",
        "linked_function_sha256", "linked_producer_sha256",
        "raw_function_difference_count", "raw_producer_difference_count",
        "ordered_relocations",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable_keys):
        raise RuntimeError("independent cutscene_script_free cold rounds differ")
    if (
        prior.sha_file(SOURCE) != source_hashes["src/maine/cutscene/script_free.cpp"]
        or prior.sha_file(BODY) != source_hashes["src/maine/cutscene/script_free.inl"]
    ):
        raise RuntimeError("maintained cutscene_script_free source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "MAINE target-reviewed cutscene_script_free maintained-source cold-link replay",
        "artifact": "th04-maine",
        "target_restored_sha256": prior.TARGET_SHA,
        "baseline_exe_sha256": prior.BASE_EXE_SHA,
        "baseline_map_sha256": prior.BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundary": boundary,
        "producer": {
            "segment": "CUTSCENE_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "local_function_offset": hex(LOCAL_START),
            "target_linked_sha256": prior.sha(producer),
        },
        "builds": builds,
        "cold_determinism": {
            "link_relevant_omf_code_exe_map_program_and_relocations_equal": True,
        },
        "limit": "Decoded 5-byte function only; v489 remains surrounding build scaffold. No packed-file or whole-MAINE exactness.",
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(receipt_path),
        "function_sha256": builds["a"]["linked_function_sha256"],
        "producer_sha256": builds["a"]["linked_producer_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
