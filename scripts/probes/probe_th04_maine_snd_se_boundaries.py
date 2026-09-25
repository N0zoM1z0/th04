#!/usr/bin/env python3
"""Target-first physical boundary review for MAINE SND_SE_PLAY / snd_se_update."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.pc98 import parse_mz

TARGET = ROOT / ".analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin"
SNAPSHOT = ROOT / ".analysis/gpt-web/v401-master-vs-object-replay-001/a/source"
MAP = SNAPSHOT / "obj/th04/maine.map"
BASELINE = SNAPSHOT / "bin/th04/maine.exe"
OBJECT = SNAPSHOT / "obj/th04/snd_se.obj"

MODULE_START = 0xD5A0
MODULE_SIZE = 0x86
PLAY_START = 0xD5A0
PLAY_SIZE = 0x39
PADDING = 0xD5D9
UPDATE_START = 0xD5DA
UPDATE_SIZE = 0x4C
NEXT_START = 0xD626

PLAY_SHA = "f62d225fbdd7fc8aa2bbad4b0b96251617478720bc63503a51f91b38aafbb52e"
UPDATE_SHA = "29186338ee7246d51f2168c7dda72b3f5205edcd0d5ae1997ca4ad4479a97fed"
OBJECT_SHA = "c901ecd69d399b104f035582794e6c8e88a47f73efeaccaa0bcf4738714053bd"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def disassemble(data: bytes, origin: int) -> list[str]:
    proc = subprocess.run(
        ["ndisasm", "-b16", f"-o{origin:#x}", "-"],
        input=data, capture_output=True, check=True,
    )
    return proc.stdout.decode("ascii", errors="replace").splitlines()


def require_map(text: str) -> None:
    required = (
        "0CC7:0930 0086 C=CODE   S=SHARED         G=(none)  M=th04/snd_se.cpp",
        "0CC7:09B6 00D0 C=CODE   S=SHARED         G=(none)  M=th04/bgimage.cpp",
        "0CC7:0930       SND_SE_PLAY",
        "0CC7:096A       _snd_se_update",
        "0CC7:09B6       _bgimage_snap",
    )
    for item in required:
        if item not in text:
            raise RuntimeError(f"MAINE sound MAP evidence drift: {item}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if out.exists() or out.parent != private:
        ap.error("output must be a new direct child of .analysis/reconstruction/probes")
    out.mkdir(parents=True)

    target_mz = parse_mz(TARGET.read_bytes())
    baseline_mz = parse_mz(BASELINE.read_bytes())
    if not target_mz.valid or not baseline_mz.valid:
        raise RuntimeError("invalid MAINE MZ input")

    target = target_mz.program_image
    baseline = baseline_mz.program_image
    map_text = MAP.read_text(encoding="cp437")
    require_map(map_text)

    play = target[PLAY_START:PLAY_START + PLAY_SIZE]
    update = target[UPDATE_START:UPDATE_START + UPDATE_SIZE]
    module = target[MODULE_START:MODULE_START + MODULE_SIZE]
    if len(play) != PLAY_SIZE or sha(play) != PLAY_SHA:
        raise RuntimeError("MAINE SND_SE_PLAY target identity drift")
    if len(update) != UPDATE_SIZE or sha(update) != UPDATE_SHA:
        raise RuntimeError("MAINE snd_se_update target identity drift")
    if target[PADDING] != 0x90:
        raise RuntimeError("MAINE sound inter-function padding drift")
    if MODULE_START + MODULE_SIZE != NEXT_START:
        raise RuntimeError("MAINE sound module arithmetic drift")
    if module != baseline[MODULE_START:MODULE_START + MODULE_SIZE]:
        raise RuntimeError("retained linked sound module differs from restored target")

    # The target Ghidra inventory deliberately has no entries for these publics.
    inventory = ROOT / ".analysis/ghidra/boundary-exports/th04-maine/functions.csv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    for off in (PLAY_START, UPDATE_START):
        if any(int(row["entry_linear"], 0) == 0x10000 + off for row in rows):
            raise RuntimeError(f"unexpected Ghidra function appeared at {off:#x}")

    # Direct opcode topology closes the two function owners around the one-byte NOP.
    if not play.startswith(bytes.fromhex("8b dc 36 8b 57 04")):
        raise RuntimeError("SND_SE_PLAY stack-parameter prologue drift")
    if play[-3:] != bytes.fromhex("ca 02 00"):
        raise RuntimeError("SND_SE_PLAY RETF 2 drift")
    if update[-1:] != b"\xcb":
        raise RuntimeError("snd_se_update RETF drift")
    if target[NEXT_START:NEXT_START + 2] != bytes.fromhex("56 57"):
        raise RuntimeError("next SHARED function boundary drift")

    play_listing = disassemble(play, PLAY_START)
    update_listing = disassemble(update, UPDATE_START)

    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-maine",
        "claim_scope": "target-first physical boundaries for MAINE sound effect play/update",
        "target_restored_sha256": sha(TARGET.read_bytes()),
        "baseline_exe_sha256": sha(BASELINE.read_bytes()),
        "candidate_object_sha256": sha(OBJECT.read_bytes()),
        "candidate_object_expected_sha256": OBJECT_SHA,
        "module": {
            "map_segment": "SHARED",
            "map_module": "th04/snd_se.cpp",
            "loaded_start": "0CC7:0930",
            "payload_offset": hex(MODULE_START),
            "size": MODULE_SIZE,
            "target_sha256": sha(module),
            "linked_baseline_raw_equal": True,
            "next_module": "0CC7:09B6 th04/bgimage.cpp",
        },
        "functions": [
            {
                "name": "SND_SE_PLAY",
                "payload_offset": hex(PLAY_START),
                "loaded": "0CC7:0930",
                "size": PLAY_SIZE,
                "target_sha256": sha(play),
                "terminal": "retf 2",
                "ghidra_entry": False,
                "listing": play_listing,
            },
            {
                "name": "_snd_se_update",
                "payload_offset": hex(UPDATE_START),
                "loaded": "0CC7:096A",
                "size": UPDATE_SIZE,
                "target_sha256": sha(update),
                "terminal": "retf",
                "ghidra_entry": False,
                "listing": update_listing,
            },
        ],
        "inter_function_padding": {
            "payload_offset": hex(PADDING),
            "size": 1,
            "bytes": "90",
            "classification": "compiler/module padding, not part of either function",
        },
        "limit": (
            "Boundary/ownership evidence only. The historical candidate uses pseudo-register "
            "forcing for exact code shape; this receipt grants no decoded-exact source credit."
        ),
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(path),
        "receipt_sha256": sha(path.read_bytes()),
        "play_size": PLAY_SIZE,
        "update_size": UPDATE_SIZE,
        "module_size": MODULE_SIZE,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
