#!/usr/bin/env python3
"""Cold-compile maintained OP BGM/SE help renderers and relink OP_SETUP_TEXT."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import csv
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
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from replay_th04_scroll_driver_natural import fixup_locations  # noqa: E402
from replay_th04_shared_delay_measure import link_relevant_omf_sha  # noqa: E402

SNAPSHOT = ROOT / ".analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source"
TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
TARGET_SHA = "40a981a671657ea49c2f916058f27ab14ab53553f555f1be843b1c8e3e50695d"
BASE_EXE_SHA = "c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274"
BASE_MAP_SHA = "65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee"
RELOCATIONS = 804

SOURCE = ROOT / "src/op/setup/help_put.cpp"
BODY = ROOT / "src/op/setup/help_put.inl"
PRODUCER_START = 0xB49F
PRODUCER_SIZE = 0x5A6
TARGET_PRODUCER_SHA = "8be1163840390fbd2b6b35ff373101f3f4f34f2a6178e43c849347ad3ae6e49c"
BASE_SETUP_SOURCE_SHA = "d614087787398ada4a5123002a3e4d46d8b5ecb420f912c13846c547b215738e"
BASE_SETUP_OBJECT_SHA = "123b54059c17d016a58692e83f0488ee1c6263210384689a2430e26f523b51a9"
BASE_SETUP_CODE_SHA = "3c40187708839196366d7f2d343cddc95d45d72b468b799a169bb7d4bb9a8b04"

FUNCTIONS = {
    "bgm_help_put": {
        "start": 0xB738,
        "segment_offset": 0x0FF8,
        "target_sha": "d8d9fdeaf1e480271c598c41c51e70e6a9ce1d3a6b09f591e4253d039661cc0e",
        "table_offset": 0x0A4C,
        "map_table": "_BGM_HELP",
    },
    "se_help_put": {
        "start": 0xB766,
        "segment_offset": 0x1026,
        "target_sha": "0d16f674796500c69f66927b5c4f05e027cad3d8e4771a52d561ab9fac1976e3",
        "table_offset": 0x0A70,
        "map_table": "_SE_HELP",
    },
}
FUNCTION_SIZE = 0x2E


def sha(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


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
        raise RuntimeError(f"expected one {segment_name}: {segments}")
    wanted = segments.index(segment_name) + 1
    chunks: list[tuple[int, bytes]] = []
    for record in records:
        if record.record_type != 0xA0:
            continue
        index, pos = omf_index(record.data, 0)
        if index == wanted:
            offset = int.from_bytes(record.data[pos:pos + 2], "little")
            chunks.append((offset, record.data[pos + 2:]))
    chunks.sort()
    out = bytearray()
    for offset, payload in chunks:
        if offset != len(out):
            raise RuntimeError(f"{segment_name} LEDATA gap/overlap at {offset:#x}")
        out += payload
    return bytes(out)


def tcc_op(work: Path, output: Path, label: str, source: str) -> None:
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tcc", "-c", "-I.", "-O", "-b-", "-3",
         "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/", source],
        work, output / f"compile-{label}.log",
    )


def target_boundary(
    name: str, spec: dict[str, object], body: bytes, map_text: str
) -> dict[str, object]:
    start = int(spec["start"])
    end = start + FUNCTION_SIZE
    if len(body) != FUNCTION_SIZE or sha(body) != spec["target_sha"]:
        raise RuntimeError(f"OP {name} target identity drift")

    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + start
        ]
    if len(rows) != 1:
        raise RuntimeError(f"OP {name} Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1A74
        or int(row["entry_offset"], 0) != int(spec["segment_offset"])
        or int(row["body_min_linear"], 0) != 0x10000 + start
        or int(row["body_max_linear"], 0) != 0x10000 + end - 1
        or int(row["body_addresses"]) != FUNCTION_SIZE
        or int(row["body_span"]) != FUNCTION_SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 1
        or int(row["callee_count"]) != 1
    ):
        raise RuntimeError(f"OP {name} Ghidra extent drift: {row!r}")

    # Both bodies differ only in the help-table displacement.
    if (
        body[:26] != bytes.fromhex(
            "55 8b ec 56 57 bf 88 00 33 f6 eb 19 68 d0 00 57 "
            "6a 0f 8b de c1 e3 02 66 ff b7"
        )
        or int.from_bytes(body[26:28], "little") != int(spec["table_offset"])
        or body[28:33] != b"\x9a\xa4\x04\xa1\x0d"
        or body[33:] != bytes.fromhex(
            "46 83 c7 10 83 fe 09 7c e2 5f 5e 5d c3"
        )
    ):
        raise RuntimeError(f"OP {name} instruction/operand topology drift")

    public = f"{int(spec['segment_offset']):04X} idle  {name}()"
    if public not in map_text:
        raise RuntimeError(f"OP {name} MAP public drift")
    if (
        f"0F34:{int(spec['table_offset']):04X} idle  {spec['map_table']}" not in map_text
        or "0DA1:04A4       GRAPH_PUTSA_FX" not in map_text
    ):
        raise RuntimeError(f"OP {name} MAP target drift")

    return {
        "segment_identity": "1A74",
        "segment_offset": f"{int(spec['segment_offset']):04X}",
        "payload_offset": hex(start),
        "size": FUNCTION_SIZE,
        "target_sha256": sha(body),
        "ghidra_contiguous": True,
        "caller_count": 1,
        "callee_count": 1,
        "help_top": 136,
        "help_left": 208,
        "help_lines": 9,
        "glyph_h": 16,
        "color": 15,
        "table_map_target": f"0F34:{int(spec['table_offset']):04X} {spec['map_table']}",
        "far_call_target": "0DA1:04A4 GRAPH_PUTSA_FX",
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/op/m_setup.cpp"
    if sha_file(upstream) != BASE_SETUP_SOURCE_SHA:
        raise RuntimeError("pinned v489 OP setup source drift")
    dst = work / "src/op/setup"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BODY, dst / BODY.name)
    data = upstream.read_bytes()
    old = (
        b"// ZUN bloat: Could have been inlined into setup_submenu().\n"
        b"void near bgm_help_put(void)\n"
        b"{\n"
        b"\tscreen_y_t top = HELP_TOP;\n"
        b"\tfor(int i = 0; i < HELP_LINES; (i++, top += GLYPH_H)) {\n"
        b"\t\tgraph_putsa_fx(HELP_LEFT, top, V_WHITE, BGM_HELP[i]);\n"
        b"\t}\n"
        b"}\n"
        b"\n"
        b"void near se_help_put(void)\n"
        b"{\n"
        b"\tscreen_y_t top = HELP_TOP;\n"
        b"\tfor(int i = 0; i < HELP_LINES; (i++, top += GLYPH_H)) {\n"
        b"\t\tgraph_putsa_fx(HELP_LEFT, top, V_WHITE, SE_HELP[i]);\n"
        b"\t}\n"
        b"}"
    )
    replacement = (
        b"// ZUN bloat: Could have been inlined into setup_submenu().\n"
        b'#include "src/op/setup/help_put.inl"'
    )
    if data.count(old) != 1:
        raise RuntimeError("OP help renderers replacement anchor drift")
    upstream.write_bytes(data.replace(old, replacement, 1))
    return sha_file(upstream)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/op/m_setup.cpp", BASE_SETUP_SOURCE_SHA),
        (SNAPSHOT / "obj/th04/op_setup.obj", BASE_SETUP_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [item.linear for item in target.relocations]
    if [item.linear for item in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target restore")

    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != TARGET_PRODUCER_SHA:
        raise RuntimeError("target OP_SETUP_TEXT identity drift")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 OP_SETUP_TEXT producer differs from target")

    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    target_bodies: dict[str, bytes] = {}
    boundaries: dict[str, dict[str, object]] = {}
    for name, spec in FUNCTIONS.items():
        start = int(spec["start"])
        body = target.program_image[start:start + FUNCTION_SIZE]
        target_bodies[name] = body
        boundaries[name] = target_boundary(name, spec, body, map_text)
        if baseline.program_image[start:start + FUNCTION_SIZE] != body:
            raise RuntimeError(f"v489 {name} differs from target")

    base_object = SNAPSHOT / "obj/th04/op_setup.obj"
    base_code = segment_bytes(base_object, "OP_SETUP_TEXT")
    if len(base_code) != PRODUCER_SIZE or sha(base_code) != BASE_SETUP_CODE_SHA:
        raise RuntimeError("pinned OP_SETUP_TEXT object contribution drift")

    source_hashes = {
        "src/op/setup/help_put.cpp": sha_file(SOURCE),
        "src/op/setup/help_put.inl": sha_file(BODY),
    }
    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        dst = work / "src/op/setup"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE, dst / SOURCE.name)
        shutil.copy2(BODY, dst / BODY.name)

        before = {path.name for path in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"v596-help-standalone-{label}",
               "src/op/setup/help_put.cpp")
        standalone = [
            path for path in (work / "obj/th04").glob("*.obj")
            if path.name not in before
        ]
        if len(standalone) != 1:
            raise RuntimeError(f"{label}: expected one standalone help object")
        local_obj = standalone[0]
        local_omf = describe_omf(local_obj.read_bytes())
        local_code = loose_segment_bytes(local_obj, "OP_SETUP_TEXT")
        local_fixups = [
            item
            for record in parse_omf(local_obj.read_bytes())
            if record.record_type == 0x9C
            for item in fixup_locations(record.data)
        ]

        expected_standalone = bytearray()
        for name in ("bgm_help_put", "se_help_put"):
            body = bytearray(target_bodies[name])
            body[26:28] = b"\0\0"
            body[29:33] = b"\0\0\0\0"
            expected_standalone += body
        if (
            not local_omf["valid"]
            or "TC86 Borland C++ 4.02" not in local_omf["translator_comments"]
            or local_code != bytes(expected_standalone)
            or local_fixups != [(3, 75), (1, 72), (3, 29), (1, 26)]
        ):
            raise RuntimeError(f"{label}: standalone OP help OMF/code drift")

        patched_source_sha = overlay_source(work)
        group_obj = work / "obj/th04/op_setup.obj"
        group_obj.unlink()
        tcc_op(work, output, f"v596-help-group-{label}", "th04/op_setup.cpp")
        group_omf = describe_omf(group_obj.read_bytes())
        group_code = segment_bytes(group_obj, "OP_SETUP_TEXT")
        if (
            not group_omf["valid"]
            or "TC86 Borland C++ 4.02" not in group_omf["translator_comments"]
            or group_code != base_code
        ):
            raise RuntimeError(f"{label}: maintained help pair changed grouped OP_SETUP_TEXT")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked_producer = image.program_image[
            PRODUCER_START:PRODUCER_START + PRODUCER_SIZE
        ]
        linked_functions = {
            name: image.program_image[
                int(spec["start"]):int(spec["start"]) + FUNCTION_SIZE
            ]
            for name, spec in FUNCTIONS.items()
        }
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [item.linear for item in image.relocations] != target_sites
            or image.program_image != baseline.program_image
            or linked_producer != producer
            or any(linked_functions[name] != target_bodies[name] for name in FUNCTIONS)
        ):
            raise RuntimeError(f"{label}: linked OP help/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "patched_upstream_tu_sha256": patched_source_sha,
            "standalone_object_sha256": sha_file(local_obj),
            "standalone_link_relevant_omf_sha256": link_relevant_omf_sha(local_obj),
            "standalone_code_sha256": sha(local_code),
            "standalone_fixup_sites": [list(item) for item in local_fixups],
            "group_object_sha256": sha_file(group_obj),
            "group_link_relevant_omf_sha256": link_relevant_omf_sha(group_obj),
            "group_code_sha256": sha(group_code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_producer_sha256": sha(linked_producer),
            "linked_function_sha256": {
                name: sha(linked_functions[name]) for name in FUNCTIONS
            },
            "raw_function_difference_count": {
                name: 0 for name in FUNCTIONS
            },
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    stable_keys = (
        "standalone_link_relevant_omf_sha256", "standalone_code_sha256",
        "standalone_fixup_sites", "group_link_relevant_omf_sha256",
        "group_code_sha256", "linked_exe_sha256", "linked_map_sha256",
        "linked_program_sha256", "linked_producer_sha256",
        "linked_function_sha256", "raw_function_difference_count",
        "raw_producer_difference_count", "ordered_relocations",
    )
    if any(builds["a"][key] != builds["b"][key] for key in stable_keys):
        raise RuntimeError("independent OP help cold rounds differ")
    if (
        sha_file(SOURCE) != source_hashes["src/op/setup/help_put.cpp"]
        or sha_file(BODY) != source_hashes["src/op/setup/help_put.inl"]
    ):
        raise RuntimeError("maintained OP help source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP target-reviewed BGM/SE help renderers maintained-source cold-link replay",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "baseline_exe_sha256": BASE_EXE_SHA,
        "baseline_map_sha256": BASE_MAP_SHA,
        "source_sha256": source_hashes,
        "boundaries": boundaries,
        "producer": {
            "segment": "OP_SETUP_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
        },
        "builds": builds,
        "limit": "Two decoded 46-byte functions only; no DIET-packed offsets or whole-OP exactness.",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "functions": {
            name: builds["a"]["linked_function_sha256"][name]
            for name in FUNCTIONS
        },
        "producer_sha256": builds["a"]["linked_producer_sha256"],
        "relocations": builds["a"]["ordered_relocations"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
