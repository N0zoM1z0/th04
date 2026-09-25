#!/usr/bin/env python3
"""Diagnose natural-C++ codegen for OP SND_SE_PLAY without exact credit."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[0:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]

from compact_op_maine_snapshot import copy_compact_snapshot
from lib.omf import parse_omf
from lib.pc98 import parse_mz
from replay_th04_op_help_put import SNAPSHOT, tcc_op, loose_segment_bytes
from replay_th04_scroll_driver_natural import fixup_locations
from replay_th04_zun_source_only import source_closure

TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin"
SOURCE = ROOT / "src/shared/sound/se_play.cpp"

START = 0xE2F2
SIZE = 0x39
TARGET_SHA = "fea779b877971c519c0729a6f0546e60f37225a2a675cd3fa4dc0975eef884b8"
NATURAL_SIZE = 0x3C
NATURAL_SHA = "4519e45ef064d7af3fb2d4be6d870277e558dfc3bb940cbe8fa5b70a7653e624"
NATURAL_FIXUPS = [
    (1, 53), (1, 49), (1, 43), (1, 37),
    (1, 29), (1, 22), (1, 15), (1, 8),
]
REF_SE = ROOT / "_reference/ReC98/th02/snd/se.cpp"
REF_SE_SHA = "3c8648ea60fa7fbae8c10068bb1ac1178e8481b3841eac297356b956109970df"
REF_IMPL = ROOT / "_reference/ReC98/th02/snd/impl.hpp"
REF_IMPL_SHA = "dc61f5435baab9dbc0e9e3aef3f66cf232db03e78d6f9d9b8f67dfc74ea9b6d7"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def object_fixups(obj: Path) -> list[tuple[int, int]]:
    return [
        item
        for rec in parse_omf(obj.read_bytes())
        if rec.record_type == 0x9C
        for item in fixup_locations(rec.data)
    ]


def target_boundary(body: bytes, map_text: str) -> dict[str, object]:
    if len(body) != SIZE or sha(body) != TARGET_SHA:
        raise RuntimeError("OP SND_SE_PLAY target identity drift")
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-op/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if int(row["entry_linear"], 0) == 0x10000 + START
        ]
    if len(rows) != 1:
        raise RuntimeError("OP SND_SE_PLAY Ghidra entry count drift")
    row = rows[0]
    if (
        int(row["entry_segment"], 0) != 0x1DA1
        or int(row["entry_offset"], 0) != 0x08E2
        or int(row["body_min_linear"], 0) != 0x10000 + START
        or int(row["body_max_linear"], 0) != 0x10000 + START + SIZE - 1
        or int(row["body_addresses"]) != SIZE
        or int(row["body_span"]) != SIZE
        or row["contiguous"] != "true"
        or row["body_range_count"] != "1"
        or int(row["caller_count"]) != 5
        or int(row["callee_count"]) != 0
    ):
        raise RuntimeError(f"OP SND_SE_PLAY Ghidra extent drift: {row!r}")
    if body != bytes.fromhex(
        "8b dc 36 8b 57 04 80 3e e0 09 00 74 29 "
        "80 3e 40 0a ff 75 07 88 16 40 0a ca 02 00 "
        "8a 1e 40 0a 32 ff 8a 87 be 09 8b da "
        "3a 87 be 09 77 09 88 16 40 0a c6 06 41 0a 00 ca 02 00"
    ):
        raise RuntimeError("OP SND_SE_PLAY instruction topology drift")
    required = (
        "0DA1:08E2       SND_SE_PLAY",
        "0F34:09E0       _snd_se_mode",
        "0F34:0A40       _snd_se_playing",
        "0F34:0A41       _snd_se_frame",
        "0F34:09BE       _snd_se_priorities",
    )
    if any(item not in map_text for item in required):
        raise RuntimeError("OP SND_SE_PLAY MAP target drift")
    return {
        "segment_identity": "1DA1",
        "segment_offset": "08E2",
        "payload_offset": hex(START),
        "size": SIZE,
        "target_sha256": sha(body),
        "caller_count": 5,
        "callee_count": 0,
        "target_parameter_load": "BX=SP; DX=SS:[BX+4]",
        "target_current_index": "BL=snd_se_playing; BH^=BH",
        "terminal": "RETF 2",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        ap.error("output must be a new direct child of .analysis/reconstruction/probes")
    output.mkdir(parents=True)

    target_mz = parse_mz(TARGET.read_bytes())
    body = target_mz.program_image[START:START + SIZE]
    map_text = (SNAPSHOT / "obj/th04/op.map").read_text(encoding="cp437")
    bound = target_boundary(body, map_text)

    closure = source_closure(ROOT, ("src/shared/sound/se_play.cpp",))
    source_hashes = {name: sha_file(ROOT / name) for name in closure}
    rounds = []
    codes = []
    for label in ("a", "b"):
        work = output / label / "op/source"
        work.parent.mkdir(parents=True)
        copy_compact_snapshot(SNAPSHOT, work, "op")
        for rel in closure:
            dst = work / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)
        before = {p.name for p in (work / "obj/th04").glob("*.obj")}
        tcc_op(work, output, f"snd-se-play-{label}", "src/shared/sound/se_play.cpp")
        objects = [p for p in (work / "obj/th04").glob("*.obj") if p.name not in before]
        if len(objects) != 1:
            raise RuntimeError(f"{label}: expected one standalone object")
        obj = objects[0]
        code = loose_segment_bytes(obj, "SHARED")
        fx = object_fixups(obj)
        if len(code) != NATURAL_SIZE or sha(code) != NATURAL_SHA or fx != NATURAL_FIXUPS:
            raise RuntimeError(f"{label}: natural SND_SE_PLAY codegen drift")
        codes.append(code)
        rounds.append({
            "label": label,
            "code_size": len(code),
            "code_sha256": sha(code),
            "fixups": [list(x) for x in fx],
        })
    if codes[0] != codes[1]:
        raise RuntimeError("natural SND_SE_PLAY cold codegen differs")
    if codes[0] == body:
        raise RuntimeError("SND_SE_PLAY unexpectedly became exact")

    expected_prefix = bytes.fromhex("55 8b ec 8b 56 06")
    if codes[0][:6] != expected_prefix:
        raise RuntimeError("natural SND_SE_PLAY parameter-load shape drift")
    if bytes.fromhex("a0 00 00 b4 00 8b d8") not in codes[0]:
        raise RuntimeError("natural SND_SE_PLAY current-index shape drift")

    for path, expected in ((REF_SE, REF_SE_SHA), (REF_IMPL, REF_IMPL_SHA)):
        if sha_file(path) != expected:
            raise RuntimeError(f"reference identity drift: {path}")
    se_text = REF_SE.read_text(encoding="shift_jis", errors="replace")
    impl_text = REF_IMPL.read_text(encoding="shift_jis", errors="replace")
    for marker in (
        "register int se = snd_get_param(new_se);",
        "_BL = snd_se_playing;",
        "_BH ^= _BH;",
    ):
        if marker not in se_text:
            raise RuntimeError(f"sound reference marker drift: {marker}")
    for marker in (
        "_BX = _SP;",
        "return peek(_SS, (_BX + 4));",
        "ZUN bloat: Just use [new_se] directly.",
    ):
        if marker not in impl_text:
            raise RuntimeError(f"sound impl reference marker drift: {marker}")

    if any(sha_file(ROOT / name) != digest for name, digest in source_hashes.items()):
        raise RuntimeError("maintained SND_SE_PLAY source changed during probe")

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-op",
        "function": "SND_SE_PLAY",
        "boundary": bound,
        "source_sha256": source_hashes,
        "natural": {
            "rounds": rounds,
            "target_size": SIZE,
            "candidate_size": NATURAL_SIZE,
            "size_delta_from_target": NATURAL_SIZE - SIZE,
            "mismatch": (
                "Ordinary Pascal C++ uses a BP frame and loads new_se from [BP+6], "
                "then zero-extends snd_se_playing through AL/AH before moving to BX. "
                "The target instead avoids the frame via BX=SP/SS:[BX+4] and uses "
                "BL with BH XOR-zeroing."
            ),
        },
        "exploration": {
            "variants_tested": [
                "direct int parameter",
                "register int parameter",
                "unsigned-char local",
                "register unsigned-char local",
            ],
            "variant_sizes": {
                "direct int": 60,
                "register int": 60,
                "unsigned-char local": 64,
                "register unsigned-char": 64,
            },
            "all_exact": False,
        },
        "reference_provenance": {
            "se_cpp": str(REF_SE.relative_to(ROOT)),
            "se_cpp_sha256": REF_SE_SHA,
            "impl_hpp": str(REF_IMPL.relative_to(ROOT)),
            "impl_hpp_sha256": REF_IMPL_SHA,
            "finding": (
                "The cross-game candidate explicitly uses pseudo-register stack "
                "access and BL/BH forcing; its own comments tell modders to replace "
                "those forms with ordinary parameters/indexing."
            ),
            "compiled": False,
            "source_credit": False,
        },
        "limit": (
            "Diagnostic codegen evidence only. Pseudoregister forcing is not "
            "accepted as authored source; the function remains source-present "
            "and nonexact."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(path),
        "target_sha256": TARGET_SHA,
        "natural_sha256": NATURAL_SHA,
        "target_size": SIZE,
        "natural_size": NATURAL_SIZE,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
