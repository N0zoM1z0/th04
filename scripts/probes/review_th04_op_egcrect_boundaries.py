#!/usr/bin/env python3
"""Review OP egcrect physical boundaries without granting source exactness."""

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

PRODUCER_START = 0xE378
PRODUCER_SIZE = 0xB0
PRODUCER_SHA = "2322e97ef7c81b397c759eeb8d427ebd522dfe18fa193c9dccdcd07b26aa52a4"
BASE_WRAPPER_SHA = "03d9d5649c513be4a3884d1df99416428f0bc10c4050eb2ed7881407a570f7be"
BASE_IMPL_SHA = "17dc0d8f283f3dc52c8dd6ae6fe46c73de3d94ea4e0cd3a95937e45e3a10967e"
BASE_OBJECT_SHA = "1580c7d8625362e4c2d85cda675e43257d55cdb93776731e4ac59c15877bad46"
BASE_CODE_SHA = "92335bb098e3abbd079a469c866f982a2ac678a170ff3056bb28d7808578bed3"

COPY_START = 0xE378
COPY_SIZE = 0x6F
COPY_SHA = "3a4dfb3ccd7e3c021dd3548f4f338e221a682ccafa6e012575f6e5864bc68e22"
PAD1_START = 0xE3E7
PAD_SHA = "9e076ceaf246b6003d9c2680a2b4cf0bffd069805902b0b5edeebf49039fe4bd"
START_START = 0xE3E8
START_SIZE = 0x3F
START_SHA = "622c9606a69af201c244d98bd4564fb6bdd159da63951e9e240d4ab038701b85"
PAD2_START = 0xE427


def run_tcc_asm(work: Path, output: Path, label: str) -> Path:
    asm = work / "obj/th04/egcrect.asm"
    if asm.exists():
        asm.unlink()
    run_checked(
        [
            "wine", str(RUNNER), "-e", "-x", "tcc", "-S", "-I.", "-O", "-b-", "-3",
            "-Z", "-d", "-DGAME=4", "-ml", "-DBINARY='O'", "-nobj/th04/",
            "th04/egcrect.cpp",
        ],
        work, output / f"compile-asm-{label}.log",
    )
    if not asm.is_file():
        raise RuntimeError(f"{label}: missing generated egcrect.asm")
    return asm


def asm_layout(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="cp437", errors="replace")
    first = "@EGC_COPY_RECT_1_TO_0_16$QIIII"
    second = "@egc_start_copy$qv"
    for symbol in (first, second):
        if text.count(f"{symbol}\tproc") != 1 or text.count(f"{symbol}\tendp") != 1:
            raise RuntimeError(f"generated PROC/ENDP drift: {symbol}")
    first_end = text.index(f"{first}\tendp") + len(f"{first}\tendp")
    second_proc = text.index(f"{second}\tproc", first_end)
    between = text[first_end:second_proc]
    if "db\t144" not in between:
        raise RuntimeError("missing compiler NOP between egcrect bodies")
    second_end = text.index(f"{second}\tendp", second_proc) + len(f"{second}\tendp")
    seg_end = text.index("SHARED\tends", second_end)
    tail = text[second_end:seg_end]
    if "db\t144" not in tail:
        raise RuntimeError("missing compiler NOP after egc_start_copy")
    return {
        "copy_proc_symbol": first,
        "start_proc_symbol": second,
        "nop_between_bodies": True,
        "nop_after_start_body": True,
    }


def target_boundaries(image: bytes) -> list[dict[str, object]]:
    pieces = (
        ("egc_copy_rect_1_to_0_16", COPY_START, COPY_SIZE, COPY_SHA),
        ("egc_start_copy", START_START, START_SIZE, START_SHA),
    )
    inv = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inv.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    out: list[dict[str, object]] = []
    for name, start, size, digest in pieces:
        body = image[start:start + size]
        if len(body) != size or sha(body) != digest:
            raise RuntimeError(f"{name}: target body identity drift")
        match = [r for r in rows if int(r["entry_linear"], 0) == 0x10000 + start]
        if len(match) != 1:
            raise RuntimeError(f"{name}: Ghidra entry count drift")
        row = match[0]
        if (
            int(row["body_addresses"]) != size
            or int(row["body_span"]) != size
            or row["contiguous"] != "true"
            or row["body_range_count"] != "1"
        ):
            raise RuntimeError(f"{name}: Ghidra body drift: {row!r}")
        out.append({
            "name": name,
            "payload_offset": hex(start),
            "reviewed_body_size": size,
            "target_sha256": digest,
            "entry_segment": row["entry_segment"],
            "entry_offset": row["entry_offset"],
            "caller_count": int(row["caller_count"]),
            "callee_count": int(row["callee_count"]),
        })

    if sha(image[PAD1_START:PAD1_START + 1]) != PAD_SHA:
        raise RuntimeError("first target NOP drift")
    if sha(image[PAD2_START:PAD2_START + 1]) != PAD_SHA:
        raise RuntimeError("second target NOP drift")
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
        (SNAPSHOT / "th04/egcrect.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "th04/hardware/egcrect.cpp", BASE_IMPL_SHA),
        (SNAPSHOT / "obj/th04/egcrect.obj", BASE_OBJECT_SHA),
    ):
        if sha_file(path) != expected:
            raise RuntimeError(f"pinned input identity drift: {path}")

    impl = (SNAPSHOT / "th04/hardware/egcrect.cpp").read_text(encoding="utf-8")
    forcing = {
        "inline_asm": ("asm {" in impl or "_asm {" in impl),
        "pseudo_registers": any(token in impl for token in ("_AX", "_BX", "_CX", "_DX", "_DI", "_ES")),
        "codestring_nop": '#pragma codestring "\\x90"' in impl,
    }
    if not all(forcing.values()):
        raise RuntimeError(f"expected diagnostic forcing markers drift: {forcing}")

    target = parse_mz(TARGET.read_bytes())
    baseline = parse_mz((SNAPSHOT / "bin/th04/op.exe").read_bytes())
    if not target.valid or not baseline.valid or len(target.relocations) != RELOCATIONS:
        raise RuntimeError("invalid target/baseline MZ")
    boundaries = target_boundaries(target.program_image)

    producer = target.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    if sha(producer) != PRODUCER_SHA:
        raise RuntimeError("target egcrect producer identity drift")
    if baseline.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE] != producer:
        raise RuntimeError("pinned OP egcrect producer differs from target")

    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    if "0DA1:0968 00B0 C=CODE   S=SHARED         G=(none)  M=th04/egcrect.cpp" not in map_text:
        raise RuntimeError("egcrect MAP contribution drift")
    if "0DA1:0968       egc_copy_rect_1_to_0_16(int,int,int,int)" not in map_text:
        raise RuntimeError("egcrect public drift")

    base_obj = SNAPSHOT / "obj/th04/egcrect.obj"
    base_omf = describe_omf(base_obj.read_bytes())
    base_code = segment_bytes(base_obj, "SHARED")
    if (
        not base_omf["valid"]
        or "TC86 Borland C++ 4.02" not in base_omf["translator_comments"]
        or len(base_code) != PRODUCER_SIZE
        or sha(base_code) != BASE_CODE_SHA
    ):
        raise RuntimeError("pinned egcrect object/code drift")

    target_sites = [r.linear for r in target.relocations]
    output.mkdir(parents=True)
    builds: dict[str, dict[str, object]] = {}
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        compact = copy_compact_snapshot(SNAPSHOT, work, "op")

        asm = run_tcc_asm(work, output, label)
        layout = asm_layout(asm)

        obj = work / "obj/th04/egcrect.obj"
        obj.unlink()
        tcc_op(work, output, f"v756-op-egcrect-boundary-{label}", "th04/egcrect.cpp")
        code = segment_bytes(obj, "SHARED")
        if code != base_code:
            raise RuntimeError(f"{label}: egcrect object CODE drift")

        exe = work / "bin/th04/op.exe"
        mp = work / "obj/th04/op.map"
        exe.unlink()
        mp.unlink()
        run_checked(
            ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
            work, output / f"link-{label}.log",
        )
        image = parse_mz(exe.read_bytes())
        linked = image.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
        if (
            not image.valid
            or sha_file(exe) != BASE_EXE_SHA
            or sha_file(mp) != BASE_MAP_SHA
            or [r.linear for r in image.relocations] != target_sites
            or linked != producer
        ):
            raise RuntimeError(f"{label}: egcrect linked identity/layout drift")

        builds[label] = {
            "compact_snapshot": compact,
            "generated_asm_sha256": sha_file(asm),
            "generated_asm_layout": layout,
            "object_sha256": sha_file(obj),
            "group_code_sha256": sha(code),
            "linked_exe_sha256": sha_file(exe),
            "linked_map_sha256": sha_file(mp),
            "linked_program_sha256": sha(image.program_image),
            "linked_producer_sha256": sha(linked),
            "ordered_relocations": len(target_sites),
        }

    stable = lambda d: {k: v for k, v in d.items() if k not in {"generated_asm_sha256", "object_sha256"}}
    if stable(builds["a"]) != stable(builds["b"]):
        raise RuntimeError("independent egcrect boundary rounds differ")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "OP egcrect physical-boundary review; diagnostic source reproduction only",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source_sha256": {
            "th04/egcrect.cpp": BASE_WRAPPER_SHA,
            "th04/hardware/egcrect.cpp": BASE_IMPL_SHA,
        },
        "driver_sha256": sha_file(Path(__file__).resolve()),
        "boundaries": boundaries,
        "compiler_owned_nops": [
            {"payload_offset": hex(PAD1_START), "size": 1, "sha256": PAD_SHA},
            {"payload_offset": hex(PAD2_START), "size": 1, "sha256": PAD_SHA},
        ],
        "producer": {
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_linked_sha256": PRODUCER_SHA,
            "raw_target_difference_count": 0,
        },
        "forcing_markers": forcing,
        "source_credit": "diagnostic-only; no authored exactness credit",
        "builds": builds,
        "limit": (
            "This receipt establishes physical boundaries and deterministic current-source reproduction only. "
            "The current source deliberately uses inline ASM, pseudo-registers, and codestring NOPs, so it is "
            "not admissible as natural authored-source exactness."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha_file(path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
