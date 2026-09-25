#!/usr/bin/env python3
"""Cold-replay the four maintained natural-C++ TH04 OP ZUNSOFT functions."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import describe_omf
from lib.pc98 import parse_mz
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes
from replay_th04_op_playchar_menu_initial import (
    SNAPSHOT, TARGET, TARGET_SHA, BASE_EXE_SHA, BASE_MAP_SHA, RELOCATIONS,
    sha, sha_file, tcc_op,
)

PRODUCER_START = 0xBA45
PRODUCER_SIZE = 0x490
PRODUCER_SHA = "c0b9629f17aaa316af5b332cd6883e0f119f956ff2cfa64892dc067c3281c23e"
BASE_WRAPPER_SHA = "f7a5c6321cf62709a47c401fe41f3c2d4178e06d86844a2a77e632e030d8d606"
BASE_IMPL_SHA = "5099eb2b49f17e7bb1191c0eec98f253ca00d3b4b8efe204dddd52738536ee72"
BASE_OBJECT_SHA = "73b25061b4b450115e80545f792cd0fb998248cd4fd0812b0653424aa417abf9"
BASE_CODE_SHA = "6de863f67773f2f1b8041127c80971708bb9a3d7ae669ed07492501aa7c3d92a"
BASE_ASM_SHA = "b864b43353972abcf9dda36973d4b22a362c68d2d7dab492586c316e20ea0835"

FUNCTIONS = (
    {
        "key": "zunsoft_pyro_new",
        "source": "src/op/music/zunsoft_pyro_new.inl",
        "marker": 'extern "C" void pascal near zunsoft_pyro_new(\n',
        "start": 0xBA45, "body_size": 0x84, "aux_size": 0,
        "body_sha": "df2adf09d0e2a577192d3d8ee54bcbd7f33336ce8d6ec2a404139eec9cb3f28e",
        "entry_offset": 0x1305, "callers": 0, "callees": 1,
        "ghidra_addresses": 132, "ghidra_span": 132, "ghidra_ranges": 1,
        "proc_symbol": "ZUNSOFT_PYRO_NEW",
        "map_public": "0A74:1305 idle  ZUNSOFT_PYRO_NEW",
    },
    {
        "key": "zunsoft_update_and_render",
        "source": "src/op/music/zunsoft_update_and_render.inl",
        "marker": 'extern "C" void pascal near zunsoft_update_and_render(void)\n',
        "start": 0xBAC9, "body_size": 0x12B, "aux_size": 0,
        "body_sha": "a2ecb4e9a3c07ff4bb8cf81f539d642a0622b871ce2c456d25a91793e1d5b6b7",
        "entry_offset": 0x1389, "callers": 1, "callees": 3,
        "ghidra_addresses": 299, "ghidra_span": 299, "ghidra_ranges": 1,
        "proc_symbol": "ZUNSOFT_UPDATE_AND_RENDER",
        "map_public": "0A74:1389 idle  ZUNSOFT_UPDATE_AND_RENDER",
    },
    {
        "key": "zunsoft_palette_update_and_show",
        "source": "src/op/music/zunsoft_palette_update_and_show.inl",
        "marker": 'extern "C" void pascal near zunsoft_palette_update_and_show(int tone)\n',
        "start": 0xBBF4, "body_size": 0x41, "aux_size": 0,
        "body_sha": "08fc22f1c1142e43cb2ce54b09a86b1472f5788c1287637847f6b0e7ee90e04c",
        "entry_offset": 0x14B4, "callers": 1, "callees": 1,
        "ghidra_addresses": 65, "ghidra_span": 65, "ghidra_ranges": 1,
        "proc_symbol": "ZUNSOFT_PALETTE_UPDATE_AND_SHOW",
        "map_public": "0A74:14B4 idle  ZUNSOFT_PALETTE_UPDATE_AND_SHOW",
    },
    {
        "key": "zunsoft_animate",
        "source": "src/op/music/zunsoft_animate.inl",
        "marker": "void near zunsoft_animate(void)\n",
        "start": 0xBC35, "body_size": 0x26F, "aux_size": 0x31,
        "body_sha": "f213c936e6e73ccbf1d7a978e3b5360892d111b8d43aca09b5627cc587e1af1c",
        "aux_sha": "9f291855385ab0a945a5a4460d0537362cb25f6e76a4e02f4002bf5adaff55be",
        "entry_offset": 0x14F5, "callers": 1, "callees": 21,
        "ghidra_addresses": 522, "ghidra_span": 623, "ghidra_ranges": 2,
        "proc_symbol": "@zunsoft_animate$qv",
        "map_public": "0A74:14F5       zunsoft_animate()",
    },
)


def find_function_end(text: str, start: int) -> int:
    brace = text.find("{", start)
    if brace < 0:
        raise RuntimeError("function opening brace drift")
    depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return pos + 1
    raise RuntimeError("unterminated function")


def overlay_source(work: Path) -> str:
    wrapper = work / "th04/zunsoft.cpp"
    impl = work / "th04/op/zunsoft.cpp"
    if sha_file(wrapper) != BASE_WRAPPER_SHA or sha_file(impl) != BASE_IMPL_SHA:
        raise RuntimeError("pinned v489 zunsoft source drift")

    for spec in FUNCTIONS:
        src = ROOT / spec["source"]
        dst = work / spec["source"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    text = impl.read_text(encoding="utf-8")
    positions: list[tuple[int, dict[str, object]]] = []
    for spec in FUNCTIONS:
        marker = str(spec["marker"])
        if text.count(marker) != 1:
            raise RuntimeError(f"{spec['key']}: source marker drift")
        positions.append((text.index(marker), spec))
    for start, spec in sorted(positions, reverse=True):
        end = find_function_end(text, start)
        text = text[:start] + f'#include "{spec["source"]}"' + text[end:]
    impl.write_text(text, encoding="utf-8")
    return sha_file(impl)


def run_tcc_asm(work: Path, output: Path, label: str) -> Path:
    asm = work / "obj/th04/zunsoft.asm"
    if asm.exists():
        asm.unlink()
    run_checked(
        [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-S", "-I.", "-O", "-b-", "-3",
            "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/",
            "th04/zunsoft.cpp",
        ],
        work, output / f"compile-asm-{label}.log",
    )
    if not asm.is_file():
        raise RuntimeError(f"{label}: missing TC86 generated zunsoft.asm")
    return asm


def generated_asm_layout(path: Path) -> dict[str, dict[str, object]]:
    text = path.read_text(encoding="cp437", errors="replace")
    summary: dict[str, dict[str, object]] = {}
    for spec in FUNCTIONS:
        symbol = str(spec["proc_symbol"])
        proc = f"{symbol}\tproc"
        endp = f"{symbol}\tendp"
        if text.count(proc) != 1 or text.count(endp) != 1:
            raise RuntimeError(f"{spec['key']}: generated PROC/ENDP drift")
        start = text.index(proc)
        end = text.index(endp, start) + len(endp)
        next_proc = text.find("\tproc", end)
        seg_end = text.find("OP_MUSIC_TEXT\tends", end)
        stops = [x for x in (next_proc, seg_end) if x >= 0]
        stop = min(stops) if stops else len(text)
        tail = text[end:stop]
        db_count = sum(1 for line in tail.splitlines() if line.lstrip().startswith("db\t"))
        dw_count = sum(1 for line in tail.splitlines() if line.lstrip().startswith("dw\t"))
        if spec["key"] == "zunsoft_animate":
            if db_count != 24 or dw_count != 12:
                raise RuntimeError(
                    f"zunsoft_animate: expected 24 case-value bytes and 12 jump words, got {db_count}/{dw_count}"
                )
        elif db_count or dw_count:
            raise RuntimeError(f"{spec['key']}: unexpected compiler data after ENDP")
        summary[str(spec["key"])] = {
            "proc_symbol": symbol,
            "case_value_db_count_after_endp": db_count,
            "switch_jump_word_count_after_endp": dw_count,
        }
    return summary


def validate_target(image: bytes, map_text: str) -> list[dict[str, object]]:
    contribution = "0A74:1305 0490 C=CODE   S=OP_MUSIC_TEXT  G=OP_01   M=th04/zunsoft.cpp"
    if contribution not in map_text:
        raise RuntimeError("ZUNSOFT MAP contribution drift")

    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    out: list[dict[str, object]] = []
    for spec in FUNCTIONS:
        start = int(spec["start"])
        body_size = int(spec["body_size"])
        aux_size = int(spec["aux_size"])
        body = image[start:start + body_size]
        aux = image[start + body_size:start + body_size + aux_size]
        if len(body) != body_size or sha(body) != spec["body_sha"]:
            raise RuntimeError(f"{spec['key']}: target body identity drift")
        if aux_size and (len(aux) != aux_size or sha(aux) != spec["aux_sha"]):
            raise RuntimeError(f"{spec['key']}: target auxiliary identity drift")

        matched = [r for r in rows if int(r["entry_linear"], 0) == 0x10000 + start]
        if len(matched) != 1:
            raise RuntimeError(f"{spec['key']}: Ghidra entry count drift")
        row = matched[0]
        if (
            int(row["entry_segment"], 0) != 0x1A74
            or int(row["entry_offset"], 0) != int(spec["entry_offset"])
            or int(row["body_addresses"]) != int(spec["ghidra_addresses"])
            or int(row["body_span"]) != int(spec["ghidra_span"])
            or int(row["body_range_count"]) != int(spec["ghidra_ranges"])
            or int(row["caller_count"]) != int(spec["callers"])
            or int(row["callee_count"]) != int(spec["callees"])
        ):
            raise RuntimeError(f"{spec['key']}: Ghidra observation drift: {row!r}")
        if spec["map_public"] not in map_text:
            raise RuntimeError(f"{spec['key']}: MAP public drift")

        out.append({
            "name": spec["key"],
            "payload_offset": hex(start),
            "reviewed_body_size": body_size,
            "target_sha256": sha(body),
            "auxiliary_size": aux_size,
            "auxiliary_sha256": sha(aux) if aux_size else None,
            "segment_identity": "1A74",
            "segment_offset": f"{int(spec['entry_offset']):04X}",
            "ghidra_auto_body_addresses": int(spec["ghidra_addresses"]),
            "ghidra_auto_body_span": int(spec["ghidra_span"]),
            "ghidra_auto_range_count": int(spec["ghidra_ranges"]),
            "caller_count": int(spec["callers"]),
            "callee_count": int(spec["callees"]),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output == private or not output.is_relative_to(private):
        ap.error("output must be new below .analysis/reconstruction/probes")

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise RuntimeError("pinned DOS runner drift")
    for path, expected in (
        (TARGET, TARGET_SHA),
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/zunsoft.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "th04/op/zunsoft.cpp", BASE_IMPL_SHA),
        (SNAPSHOT / "obj/th04/zunsoft.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    source_hashes = {
        str(spec["source"]): sha_file(ROOT / spec["source"]) for spec in FUNCTIONS
    }

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target restore or v489 OP candidate")
    target_sites = [r.linear for r in target.relocations]
    if [r.linear for r in baseline.relocations] != target_sites:
        raise RuntimeError("v489 OP ordered relocations differ from target")

    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    boundaries = validate_target(target.program_image, map_text)

    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != PRODUCER_SHA:
        raise RuntimeError("target ZUNSOFT producer identity drift")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 linked ZUNSOFT producer differs from target")

    base_obj = SNAPSHOT / "obj/th04/zunsoft.obj"
    base_omf = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "OP_MUSIC_TEXT")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_CODE_SHA
    ):
        raise RuntimeError("pinned zunsoft object/code drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        patched_source_sha = overlay_source(work)

        asm = run_tcc_asm(work, output, label)
        asm_layout = generated_asm_layout(asm)

        obj = work / "obj/th04/zunsoft.obj"
        obj.unlink()
        tcc_op(work, output, f"v753-op-zunsoft-natural-{label}", "th04/zunsoft.cpp")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "OP_MUSIC_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained ZUNSOFT bodies changed producer CODE")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked_producer = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [r.linear for r in image.relocations] != target_sites
            or linked_producer != producer
        ):
            raise RuntimeError(f"{label}: linked ZUNSOFT identity/layout drift")

        linked: dict[str, dict[str, object]] = {}
        for spec in FUNCTIONS:
            start = int(spec["start"])
            body_size = int(spec["body_size"])
            aux_size = int(spec["aux_size"])
            body = image.program_image[start:start + body_size]
            aux = image.program_image[start + body_size:start + body_size + aux_size]
            target_body = target.program_image[start:start + body_size]
            target_aux = target.program_image[start + body_size:start + body_size + aux_size]
            if body != target_body or aux != target_aux:
                raise RuntimeError(f"{label}/{spec['key']}: linked body/aux drift")
            linked[str(spec["key"])] = {
                "body_sha256": sha(body),
                "auxiliary_sha256": sha(aux) if aux_size else None,
                "raw_body_difference_count": 0,
                "raw_auxiliary_difference_count": 0 if aux_size else None,
            }

        builds[label] = {
            "compact_snapshot": compact,
            "patched_source_sha256": patched_source_sha,
            "generated_asm_sha256": sha_file(asm),
            "generated_asm_layout": asm_layout,
            "object_sha256": sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_producer_sha256": sha(linked_producer),
            "linked": linked,
            "raw_producer_difference_count": 0,
            "ordered_relocations": len(target_sites),
        }

    def stable(build: dict[str, object]) -> dict[str, object]:
        clean = json.loads(json.dumps(build))
        clean.pop("object_sha256", None)
        clean.pop("generated_asm_sha256", None)
        return clean

    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent ZUNSOFT cold rounds differ")
    if any(sha_file(ROOT / path) != digest for path, digest in source_hashes.items()):
        raise RuntimeError("maintained ZUNSOFT source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP four ZUNSOFT maintained natural-C++ functions",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source_sha256": source_hashes,
        "driver_sha256": sha_file(Path(__file__).resolve()),
        "generated_asm_reference_sha256": BASE_ASM_SHA,
        "boundaries": boundaries,
        "producer": {
            "segment": "OP_MUSIC_TEXT",
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": sha(producer),
            "raw_target_difference_count": 0,
        },
        "builds": builds,
        "limit": (
            "Exactness claims are limited to the four maintained ZUNSOFT bodies and the "
            "0x31-byte compiler-owned alignment/sparse-switch extent after zunsoft_animate. "
            "The full OP candidate image is required to remain unchanged, but whole-OP target "
            "exactness is not claimed."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "function_count": len(FUNCTIONS),
        "source_sha256": source_hashes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
