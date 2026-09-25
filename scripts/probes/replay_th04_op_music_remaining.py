#!/usr/bin/env python3
"""Cold-replay natural-C++ OP polygons_update_and_render + musicroom_menu."""

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

PRODUCER_START = 0xBED5
PRODUCER_SIZE = 0x6A5
PRODUCER_SHA = "53495c80ca106bc0cde9b8b37c8060cdacb80732a810b8fa8ad3ea3eac57ef09"
BASE_WRAPPER_SHA = "6af2dc1efe4aed790dc5bc1dd760b56ed59e227b55f4476411848f0b0ff3680a"
BASE_IMPL_SHA = "a8ded4e33e974dccb35e8ac84d5e974e0c4b574ceace5adc4a07912e90f127cc"
BASE_OBJECT_SHA = "57f9c5d7ea06570eda6f5df3d936cadd20fb1d1bcf5553eb91724a4686f2697d"
BASE_CODE_SHA = "83a4d168eb1e4846a64d92dd423d2ea64d371223ce156fed54588ab03d7b2c46"
BASE_ASM_SHA = "8be25a4ed3040135fcc2a53e4ff8f782f6db20b2e74ee7a685e4b0d77997d5ca"

FUNCTIONS = (
    {
        "key": "polygons_update_and_render",
        "source": "src/op/music/polygons_update_and_render.inl",
        "marker": "void near polygons_update_and_render(void)\n",
        "start": 0xC04E, "size": 0x1F6, "entry_offset": 0x190E,
        "sha256": "8395ab3d636d10903599d941c54cc23d2935cfb387da3c4c6d218fce011be2dc",
        "callers": 1, "callees": 3,
        "ghidra_addresses": 397, "ghidra_span": 502, "ghidra_ranges": 2,
        "map_public": "0A74:190E idle  polygons_update_and_render()",
        "proc_symbol": "@polygons_update_and_render$qv",
    },
    {
        "key": "musicroom_menu",
        "source": "src/op/music/musicroom_menu.inl",
        "marker": "void MUSICROOM_DISTANCE musicroom_menu(void)\n",
        "start": 0xC3B7, "size": 0x1C3, "entry_offset": 0x1C77,
        "sha256": "285963cdf9e2f09f2dbd17a2eac2355edcaa75b0d0cf8759d6080e2dbaa2f646",
        "callers": 0, "callees": 21,
        "ghidra_addresses": 451, "ghidra_span": 451, "ghidra_ranges": 1,
        "map_public": "0A74:1C77       musicroom_menu()",
        "proc_symbol": "@musicroom_menu$qv",
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
    wrapper = work / "th04/op_music.cpp"
    impl = work / "th02/op/m_music.cpp"
    if sha_file(wrapper) != BASE_WRAPPER_SHA or sha_file(impl) != BASE_IMPL_SHA:
        raise RuntimeError("pinned v489 op_music source drift")

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
    asm = work / "obj/th04/op_music.asm"
    if asm.exists():
        asm.unlink()
    run_checked(
        [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-S", "-I.", "-O", "-b-", "-3",
            "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/",
            "th04/op_music.cpp",
        ],
        work, output / f"compile-asm-{label}.log",
    )
    if not asm.is_file():
        raise RuntimeError(f"{label}: missing TC86 generated op_music.asm")
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
        words = sum(1 for line in tail.splitlines() if line.lstrip().startswith("dw\t"))
        if words != 0:
            raise RuntimeError(f"{spec['key']}: unexpected switch table after ENDP")
        summary[str(spec["key"])] = {
            "proc_symbol": symbol,
            "switch_table_words_after_endp": 0,
            "segment_ends_before_next_proc": seg_end >= 0 and (next_proc < 0 or seg_end < next_proc),
        }
    return summary


def validate_target(image: bytes, map_text: str) -> list[dict[str, object]]:
    contribution = "0A74:1795 06A5 C=CODE   S=OP_MUSIC_TEXT  G=OP_01   M=th04/op_music.cpp"
    if contribution not in map_text:
        raise RuntimeError("OP_MUSIC_TEXT MAP contribution drift")

    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    out: list[dict[str, object]] = []
    for spec in FUNCTIONS:
        start, size = int(spec["start"]), int(spec["size"])
        body = image[start:start + size]
        if len(body) != size or sha(body) != spec["sha256"]:
            raise RuntimeError(f"{spec['key']}: target identity drift")
        if not body.endswith(bytes.fromhex("5d c3")):
            raise RuntimeError(f"{spec['key']}: target terminal drift")
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
            "reviewed_body_size": size,
            "target_sha256": sha(body),
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
        (SNAPSHOT / "th04/op_music.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "th02/op/m_music.cpp", BASE_IMPL_SHA),
        (SNAPSHOT / "obj/th04/op_music.obj", BASE_OBJECT_SHA),
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
        raise RuntimeError("target OP_MUSIC_TEXT producer identity drift")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("v489 OP_MUSIC_TEXT producer differs from target")

    base_obj = SNAPSHOT / "obj/th04/op_music.obj"
    base_omf = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "OP_MUSIC_TEXT")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_CODE_SHA
    ):
        raise RuntimeError("pinned op_music object/code drift")

    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")
        patched_source_sha = overlay_source(work)

        asm = run_tcc_asm(work, output, label)
        asm_layout = generated_asm_layout(asm)

        obj = work / "obj/th04/op_music.obj"
        obj.unlink()
        tcc_op(work, output, f"v746-op-music-remaining-{label}", "th04/op_music.cpp")
        omf = describe_omf(obj.read_bytes())
        code = segment_bytes(obj, "OP_MUSIC_TEXT")
        if (
            not omf["valid"]
            or "TC86 Borland C++ 4.02" not in omf["translator_comments"]
            or code != base_code
        ):
            raise RuntimeError(f"{label}: maintained OP music bodies changed producer CODE")

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
            raise RuntimeError(f"{label}: linked OP music identity/layout drift")

        linked: dict[str, dict[str, object]] = {}
        for spec in FUNCTIONS:
            start, size = int(spec["start"]), int(spec["size"])
            body = image.program_image[start:start + size]
            target_body = target.program_image[start:start + size]
            if body != target_body:
                raise RuntimeError(f"{label}/{spec['key']}: linked body drift")
            linked[str(spec["key"])] = {
                "body_sha256": sha(body),
                "raw_body_difference_count": 0,
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
        raise RuntimeError("independent OP music cold rounds differ")
    if any(sha_file(ROOT / path) != digest for path, digest in source_hashes.items()):
        raise RuntimeError("maintained OP music source changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP polygons_update_and_render + musicroom_menu maintained natural-C++ cold replay",
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
        "surrounding_scaffold": (
            "Other OP_MUSIC_TEXT functions, including low-level nopoly helpers, remain pinned "
            "current-v489 producer context and receive no new authored-source credit."
        ),
        "builds": builds,
        "limit": (
            "Exactness claims are limited to polygons_update_and_render and musicroom_menu. "
            "No packed-file or whole-OP exactness."
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
