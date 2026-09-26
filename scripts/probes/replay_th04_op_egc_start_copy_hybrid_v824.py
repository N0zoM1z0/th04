#!/usr/bin/env python3
"""Replay the TH04 OP internal egc_start_copy() hybrid source.

The accepted source boundary is intentionally narrow. Two low-level regions
remain symbolic: the 28-byte GRCG/EGC-enable hardware primitive, and the
6-byte TC4J pseudoregister address-zero write. The intervening EGC word writes
and final bit-length write remain ordinary C++/TC4J codegen.

Independent machine-code corroboration comes from attested TH05 OP and MAINE
targets, which contain the complete 63-byte helper verbatim. An older TH03
ZUNSP/SPRITE16 reverse-engineering lineage corroborates the same hardware
programming architecture but is not treated as original-source proof.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = (ROOT / ".analysis").resolve()
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot  # noqa: E402
from lib.omf import describe_omf  # noqa: E402
from lib.pc98 import parse_mz  # noqa: E402
from lib.targets import find_artifact, load_target_manifest, read_verified_artifact  # noqa: E402
from probe_th04_final_blocker_crossartifact import restore_diet  # noqa: E402
from probe_th04_maine_score_producers_v468 import RUNNER, RUNNER_SHA, run_checked  # noqa: E402
from probe_th04_maine_staff_full_cpp_v478 import segment_bytes  # noqa: E402
from review_th04_op_egcrect_boundaries import (
    SNAPSHOT,
    TARGET,
    TARGET_SHA,
    BASE_EXE_SHA,
    BASE_MAP_SHA,
    RELOCATIONS,
    BASE_WRAPPER_SHA,
    BASE_IMPL_SHA,
    BASE_CODE_SHA,
    PRODUCER_START,
    PRODUCER_SIZE,
    PRODUCER_SHA,
    tcc_op,
)  # noqa: E402

SOURCE = ROOT / "src/op/hardware/egc_start_copy.inl"
SOURCE_SHA = "69b7f83563ea58741c18446250c8be669acb5a5525c2e7ac98a9814ef1889049"

START = 0xE3E8
SIZE = 0x3F
TARGET_SHA256 = "622c9606a69af201c244d98bd4564fb6bdd159da63951e9e240d4ab038701b85"
SYMBOLIC_RANGES = (
    ("grcg_egc_enable", 0x00, 0x1C, "f77d30b7a2a53d73f0da6f1999b6eb229ee26473d442fff16d98e9fef5fffabd"),
    ("address_zero_write", 0x31, 0x37, "e8424abd7a8b2d99bd61ac9fa60a4d3adf3e9a56450d1b4e2656abbad97f9ff5"),
)
ORDINARY_RANGES = (
    ("egc_word_writes", 0x1C, 0x31, "70700e02da72b13d2fec7db86d91e587544c6dec5d863a8fa72cef54e6fd0cda"),
    ("bitlength_and_return", 0x37, 0x3F, "3a4fdb8641095dc74dea6c70c0f78916a84e7683d218f5bf78e6ee2247786d85"),
)

TH05 = {
    "th05-op-smoke": {
        "packed_sha256": "c94efc071a4b1adf8ce6e2c5a7eefb9eb47c26f8bab61b2e58e736dda8130abb",
        "restored_sha256": "1caaa7f804146838e8771ae69487005f1ccd70cc8369dcb62e8adaf6addad71c",
        "offset": 0xE354,
        "program_size": 75786,
        "relocations": 952,
    },
    "th05-maine-smoke": {
        "packed_sha256": "8308c416e756a07766f9f66dbf5575fa12c09189059226931a9562e7272b6997",
        "restored_sha256": "247a7b90bb912562999da15267fe6e98fa72c8cccdbab3f1a88eee37c82fc9a4",
        "offset": 0xF47E,
        "program_size": 75958,
        "relocations": 667,
    },
}
TH05_OP_MAP = ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source/obj/th05/op.map"
TH05_OP_MAP_SHA = "da2598ec3f3c707fdc968d0d9dcca5cddf333beb9b8241d76d123ee0970af907"
TH05_OP_OWNER = "0D30:0FD8 00BC C=CODE   S=SHARED         G=(none)  M=th05/egcrect.cpp ACBP=28"

SPRITE16 = ROOT / "_reference/ReC98/libs/sprite16/sprite16.asm"
SPRITE16_SHA = "d0b5366a317911fcd45b6d8e9abb80331ed999a73110cd8090fac98a26b0739d"
SPRITE_INITIAL = "3b497286a5d23b74eab97c09e194b7b2ba6c5da9"
SPRITE_EGC_WRITES = "41622254"
SPRITE_EGC_ENABLE = "f6a32460"
TH04_DECOMP = "baac3f76823f18cee2c8f5987beed73b0169f49a"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def new_output(path: Path | None) -> Path:
    if path is None:
        parent = PRIVATE / "reconstruction/probes"
        parent.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="op-egc-start-v824-", dir=parent))
    output = path.resolve()
    if output.exists() or not output.is_relative_to(PRIVATE):
        raise ValueError("output must be new and below .analysis")
    output.mkdir(parents=True)
    return output


def git_subject(commit: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT / "_reference/ReC98"), "show", "-s", "--format=%s", commit],
        text=True,
    ).strip()


def source_policy() -> dict[str, object]:
    if sha_file(SOURCE) != SOURCE_SHA:
        raise ValueError("maintained EGC helper source identity drift")
    text = SOURCE.read_text()
    forbidden = ("__emit__", "#pragma codestring", "unsigned char target", "db 0x", "db 6")
    if any(token in text for token in forbidden):
        raise ValueError("maintained EGC helper contains byte-forcing surface")
    if text.count("asm {") != 1:
        raise ValueError("EGC helper must have one bounded symbolic assembly block")
    for marker in (
        "push es", "pushf", "cli", "mov al, GC_TDW", "out 0x7C, al",
        "mov byte ptr es:[0x495], al", "popf", "pop es",
        "mov al, 0x07", "out 0x6A, al", "mov al, 0x05", "mov al, 0x06",
        "outport(EGC_ACTIVEPLANEREG, 0xFFF0);",
        "outport(EGC_READPLANEREG, 0x00FF);",
        "outport(EGC_MASKREG, 0xFFFF);",
        "_DX = EGC_ADDRRESSREG;", "_AX -= _AX;", "outport(_DX, _AX);",
        "outport(EGC_BITLENGTHREG, 0xF);",
    ):
        if marker not in text:
            raise ValueError(f"maintained EGC helper marker drift: {marker}")
    return {
        "symbolic_low_level": [
            "28-byte GRCG TDW / BIOS shadow / immediate-port EGC-enable block",
            "6-byte TC4J pseudoregister MOV DX,04ACh / SUB AX,AX / OUT DX,AX block",
        ],
        "ordinary_cpp": [
            "ACTIVE/READ/MASK EGC word-register writes",
            "BITLENGTH word-register write and compiler RET",
        ],
        "symbolic_assembly_blocks": 1,
        "compiler_pseudoregister_primitives": 1,
        "no_emitted_opcode_arrays": True,
        "no_codestring_in_function_source": True,
        "no_scaffold_graph_egc_helper_dependency": True,
    }


def crossgame_targets(output: Path, expected_helper: bytes) -> dict[str, object]:
    manifest = load_target_manifest(ROOT / "config/targets.toml")
    cross = output / "crossgame"
    cross.mkdir()
    results: dict[str, object] = {}
    for aid, spec in TH05.items():
        artifact = find_artifact(manifest, aid)
        packed = read_verified_artifact(ROOT, artifact)
        if artifact["sha256"] != spec["packed_sha256"] or sha(packed) != spec["packed_sha256"]:
            raise ValueError(f"{aid}: packed target identity drift")
        restored, restore_meta = restore_diet(artifact, packed, cross)
        if sha(restored) != spec["restored_sha256"]:
            raise ValueError(f"{aid}: restored target identity drift")
        mz = parse_mz(restored)
        if (
            not mz.valid
            or len(mz.program_image) != spec["program_size"]
            or len(mz.relocations) != spec["relocations"]
        ):
            raise ValueError(f"{aid}: restored MZ structure drift")
        offset = int(spec["offset"])
        helper = mz.program_image[offset:offset + SIZE]
        if helper != expected_helper or sha(helper) != TARGET_SHA256:
            raise ValueError(f"{aid}: full EGC helper drift")
        hits = []
        pos = 0
        while True:
            pos = mz.program_image.find(expected_helper, pos)
            if pos < 0:
                break
            hits.append(pos)
            pos += 1
        if hits != [offset]:
            raise ValueError(f"{aid}: EGC helper occurrence drift: {hits}")
        results[aid] = {
            "packed_sha256": spec["packed_sha256"],
            "restored_sha256": spec["restored_sha256"],
            "payload_offset": hex(offset),
            "helper_sha256": sha(helper),
            "unique_full_helper_match": True,
            "program_size": len(mz.program_image),
            "ordered_relocations": len(mz.relocations),
            "restore_log_sha256": restore_meta["restore_log_sha256"],
        }

    if sha_file(TH05_OP_MAP) != TH05_OP_MAP_SHA:
        raise ValueError("pinned TH05 OP MAP identity drift")
    map_text = TH05_OP_MAP.read_text(encoding="cp437", errors="replace")
    if TH05_OP_OWNER not in map_text:
        raise ValueError("TH05 OP egcrect MAP owner drift")
    results["th05-op-map-binding"] = {
        "map_sha256": TH05_OP_MAP_SHA,
        "owner": TH05_OP_OWNER,
        "producer_load_offset": "0xE2D8",
        "helper_relative_offset": "0x7C",
        "helper_load_offset": "0xE354",
    }
    shutil.rmtree(cross)
    return results


def older_machine_lineage() -> dict[str, object]:
    if sha_file(SPRITE16) != SPRITE16_SHA:
        raise ValueError("SPRITE16 source identity drift")
    text = SPRITE16.read_text(encoding="cp437", errors="replace")
    for marker in (
        "sub_BD0", "GRCG_SETMODE_VIA_MOV al, GC_TDW",
        "outw\tEGC_ACTIVEPLANEREG, 0FFF0h",
        "outw\tEGC_READPLANEREG, 0FFh",
        "outw\tEGC_MASKREG, 0FFFFh",
        "mov\tdx, EGC_ADDRRESSREG",
        "outw\tEGC_BITLENGTHREG, 0Fh",
    ):
        if marker not in text:
            raise ValueError(f"SPRITE16 EGC lineage marker drift: {marker}")

    subjects = {
        "initial": git_subject(SPRITE_INITIAL),
        "egc_register_writes": git_subject(SPRITE_EGC_WRITES),
        "egc_enable_disable": git_subject(SPRITE_EGC_ENABLE),
        "th04_egcrect_decompilation": git_subject(TH04_DECOMP),
    }
    if (
        subjects["initial"] != "[th03/zunsp] Initial state"
        or "EGC register writes" not in subjects["egc_register_writes"]
        or "Enabling and disabling the EGC" not in subjects["egc_enable_disable"]
        or subjects["th04_egcrect_decompilation"]
        != "[Decompilation] [th04/th05] EGC-powered page 1→0 rectangle blitting"
    ):
        raise ValueError(f"EGC historical subject drift: {subjects}")
    return {
        "path": str(SPRITE16.relative_to(ROOT)),
        "sha256": SPRITE16_SHA,
        "subjects": subjects,
        "classification": (
            "older independent reverse-engineering lineage; machine-mechanism corroboration only, "
            "not original-source proof"
        ),
    }


def overlay_source(work: Path) -> str:
    upstream = work / "th04/hardware/egcrect.cpp"
    if sha_file(upstream) != BASE_IMPL_SHA:
        raise ValueError("pinned TH04 egcrect source drift")
    destination = work / "src/op/hardware/egc_start_copy.inl"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, destination)

    text = upstream.read_text()
    pattern = re.compile(
        r"static void near egc_start_copy\(void\)\n\{.*?\n\}\n\n"
        r'(#pragma codestring "\\x90")',
        re.S,
    )
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError("egc_start_copy definition replacement anchor drift")
    replacement = '#include "src/op/hardware/egc_start_copy.inl"\n\n' + matches[0].group(1)
    upstream.write_text(text[:matches[0].start()] + replacement + text[matches[0].end():])
    return sha_file(upstream)


def build_round(output: Path, label: str, target_mz) -> dict[str, object]:
    work = output / label / "op/source"
    work.parent.mkdir(parents=True)
    compact = copy_compact_snapshot(SNAPSHOT, work, "op")
    overlay_sha = overlay_source(work)

    obj = work / "obj/th04/egcrect.obj"
    obj.unlink()
    tcc_op(work, output, f"egc-start-hybrid-{label}", "th04/egcrect.cpp")
    desc = describe_omf(obj.read_bytes())
    code = segment_bytes(obj, "SHARED")
    if (
        not desc["valid"]
        or "TC86 Borland C++ 4.02" not in desc["translator_comments"]
        or len(code) != PRODUCER_SIZE
        or sha(code) != BASE_CODE_SHA
    ):
        raise ValueError(f"{label}: EGC hybrid object/code drift")
    helper = code[START - PRODUCER_START:START - PRODUCER_START + SIZE]
    if sha(helper) != TARGET_SHA256:
        raise ValueError(f"{label}: EGC helper object bytes drift")
    for name, start, end, digest in (*SYMBOLIC_RANGES, *ORDINARY_RANGES):
        if sha(helper[start:end]) != digest:
            raise ValueError(f"{label}: EGC helper range drift: {name}")

    exe = work / "bin/th04/op.exe"
    map_path = work / "obj/th04/op.map"
    exe.unlink()
    map_path.unlink()
    run_checked(
        ["wine", str(RUNNER), "-e", "-x", "tlink", r"@obj\th04\op.@l"],
        work,
        output / f"link-{label}.log",
        timeout=300,
    )
    linked = parse_mz(exe.read_bytes())
    if not linked.valid:
        raise ValueError(f"{label}: invalid linked OP")
    target_relocs = [item.linear for item in target_mz.relocations]
    if [item.linear for item in linked.relocations] != target_relocs:
        raise ValueError(f"{label}: ordered relocation drift")
    if sha_file(exe) != BASE_EXE_SHA or sha_file(map_path) != BASE_MAP_SHA:
        raise ValueError(f"{label}: OP EXE/MAP baseline drift")
    linked_producer = linked.program_image[PRODUCER_START:PRODUCER_START + PRODUCER_SIZE]
    linked_helper = linked.program_image[START:START + SIZE]
    if sha(linked_producer) != PRODUCER_SHA or sha(linked_helper) != TARGET_SHA256:
        raise ValueError(f"{label}: linked EGC producer/helper drift")

    return {
        "compact_snapshot": compact,
        "overlay_source_sha256": overlay_sha,
        "object_code_size": len(code),
        "object_code_sha256": sha(code),
        "helper_sha256": sha(helper),
        "symbolic_ranges": {
            name: {"start": start, "end": end, "sha256": sha(helper[start:end])}
            for name, start, end, _ in SYMBOLIC_RANGES
        },
        "ordinary_ranges": {
            name: {"start": start, "end": end, "sha256": sha(helper[start:end])}
            for name, start, end, _ in ORDINARY_RANGES
        },
        "linked_exe_sha256": sha_file(exe),
        "linked_map_sha256": sha_file(map_path),
        "linked_producer_sha256": sha(linked_producer),
        "linked_helper_sha256": sha(linked_helper),
        "ordered_relocations": len(linked.relocations),
        "raw_helper_difference_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    output = new_output(args.output_dir)

    subprocess.run(
        [sys.executable, "scripts/preflight.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    if sha_file(RUNNER) != RUNNER_SHA:
        raise ValueError("pinned DOS runner drift")
    if sha_file(TARGET) != TARGET_SHA:
        raise ValueError("OP restored target identity drift")
    for path, expected in (
        (SNAPSHOT / "bin/th04/op.exe", BASE_EXE_SHA),
        (SNAPSHOT / "obj/th04/op.map", BASE_MAP_SHA),
        (SNAPSHOT / "th04/egcrect.cpp", BASE_WRAPPER_SHA),
        (SNAPSHOT / "th04/hardware/egcrect.cpp", BASE_IMPL_SHA),
    ):
        if sha_file(path) != expected:
            raise ValueError(f"pinned OP EGC input drift: {path}")

    policy = source_policy()
    target_mz = parse_mz(TARGET.read_bytes())
    if not target_mz.valid or len(target_mz.relocations) != RELOCATIONS:
        raise ValueError("OP target MZ/relocation drift")
    target_helper = target_mz.program_image[START:START + SIZE]
    if len(target_helper) != SIZE or sha(target_helper) != TARGET_SHA256:
        raise ValueError("OP target EGC helper drift")
    for name, start, end, digest in (*SYMBOLIC_RANGES, *ORDINARY_RANGES):
        if sha(target_helper[start:end]) != digest:
            raise ValueError(f"OP target EGC helper range drift: {name}")

    crossgame = crossgame_targets(output, target_helper)
    lineage = older_machine_lineage()
    source_hash = sha_file(SOURCE)

    builds = {
        label: build_round(output, label, target_mz)
        for label in ("a", "b")
    }
    stable = lambda row: {k: v for k, v in row.items() if k != "compact_snapshot"}
    if stable(builds["a"]) != stable(builds["b"]):
        raise ValueError("independent EGC hybrid cold rounds disagree")
    if sha_file(SOURCE) != source_hash:
        raise ValueError("maintained EGC helper changed during replay")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "TH04 OP internal egc_start_copy hybrid-source decoded exactness",
        "artifact": "th04-op",
        "target_restored_sha256": TARGET_SHA,
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "boundary": {
            "payload_offset": hex(START),
            "size": SIZE,
            "target_sha256": TARGET_SHA256,
            "symbolic_ranges": [
                {"name": name, "start": start, "end": end, "size": end - start, "sha256": digest}
                for name, start, end, digest in SYMBOLIC_RANGES
            ],
            "ordinary_ranges": [
                {"name": name, "start": start, "end": end, "size": end - start, "sha256": digest}
                for name, start, end, digest in ORDINARY_RANGES
            ],
        },
        "source_policy": policy,
        "crossgame_targets": crossgame,
        "older_machine_lineage": lineage,
        "complete_translation_unit": {
            "payload_offset": hex(PRODUCER_START),
            "size": PRODUCER_SIZE,
            "target_sha256": PRODUCER_SHA,
            "note": (
                "The 0xB0 translation-unit contribution is replayed only as a layout guard. "
                "The preceding 111-byte egc_copy_rect_1_to_0_16 remains blocked and receives no credit."
            ),
        },
        "builds": builds,
        "conclusion": (
            "Two cold TC4.02/TLINK rounds reproduce the complete 63-byte helper raw-zero, "
            "the surrounding 0xB0 producer, the accepted OP EXE/MAP, and all 804 ordered "
            "relocations. Non-ordinary source is limited to two independently TH05-corroborated "
            "hardware/compiler primitives (28 + 6 bytes); the remaining 29 bytes are ordinary C++ "
            "and compiler return code."
        ),
        "limit": (
            "Decoded-function exactness only. The adjacent 111-byte rectangle-copy function "
            "remains blocked; packed-file and original-source-spelling exactness are not claimed."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha_file(path),
        "helper_sha256": TARGET_SHA256,
        "crossgame_helpers": {
            key: value["payload_offset"]
            for key, value in crossgame.items()
            if key in TH05
        },
        "symbolic_low_level_bytes": sum(end - start for _, start, end, _ in SYMBOLIC_RANGES),
        "ordinary_cpp_bytes": sum(end - start for _, start, end, _ in ORDINARY_RANGES),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
