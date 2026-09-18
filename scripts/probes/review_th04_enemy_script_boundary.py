#!/usr/bin/env python3
"""Review the complete MAIN B4M enemy-script code and jump-table boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / ".analysis/targets/th04/main.exe"
TARGET_SHA256 = "077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b"
CS_LOAD_BASE = 0x13A90  # B4M_UPDATE_TEXT group 13A9:0000
START = 0x1554F
END = 0x15C6D
CODE_START = 0x155DD
TABLE_START = 0x15B4D
CALL_SITE = 0x17E9C  # Inside already exact enemies_update().

FUNCTIONS = (
    ("enemy_pos_update", 0x1554F, 0x15592),
    ("enemy_velocity_set", 0x15592, 0x155AA),
    ("enemy_aim_velocity_set", 0x155AA, 0x155DD),
    ("enemy_script_update_code", CODE_START, TABLE_START),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def word(data: bytes, pos: int) -> int:
    return int.from_bytes(data[pos : pos + 2], "little")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    expected_parent = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.parent != expected_parent or output.exists():
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")

    target = TARGET.read_bytes()
    if len(target) != 156258 or sha(target) != TARGET_SHA256 or target[:2] != b"MZ":
        raise RuntimeError("pinned MAIN target identity or format changed")
    header_size = word(target, 8) * 16
    relocation_count = word(target, 6)
    relocation_offset = word(target, 0x18)
    if header_size != 6144 or relocation_count != 1136:
        raise RuntimeError("pinned MAIN MZ topology changed")
    load = target[header_size:]
    if END > len(load):
        raise RuntimeError("bounded extent exceeds MZ load module")

    slices = []
    for name, start, end in FUNCTIONS:
        data = load[start:end]
        if not data or data[-1] != 0xC3:
            raise RuntimeError(f"{name}: expected terminal near RET at {end - 1:#x}")
        slices.append({
            "name": name,
            "segment_start": f"13A9:{start - CS_LOAD_BASE:04X}",
            "load_start": f"0x{start:X}",
            "load_end_exclusive": f"0x{end:X}",
            "file_start": f"0x{header_size + start:X}",
            "size": len(data),
            "sha256": sha(data),
        })
    table = load[TABLE_START:END]
    if len(table) != 288:
        raise RuntimeError("enemy script table is not 144 words")
    destinations = [CS_LOAD_BASE + word(table, pos) for pos in range(0, len(table), 2)]
    if not all(CODE_START <= dest < TABLE_START for dest in destinations):
        raise RuntimeError("switch table escapes the executable body")

    ndisasm = shutil.which("ndisasm")
    if not ndisasm:
        raise RuntimeError("ndisasm is required for the instruction-start cross-check")
    decoded = subprocess.run(
        [ndisasm, "-b", "16", "-o", hex(CODE_START), "-"],
        input=load[CODE_START:TABLE_START],
        capture_output=True,
        check=True,
    )
    starts = {
        int(match.group(1), 16)
        for line in decoded.stdout.decode("ascii").splitlines()
        if (match := re.match(r"([0-9A-Fa-f]{8})\s+", line))
    }
    missing = [dest for dest in destinations if dest not in starts]
    if missing:
        raise RuntimeError(f"{len(missing)} switch targets are not decoded instruction starts")

    call = load[CALL_SITE : CALL_SITE + 3]
    if len(call) != 3 or call[0] != 0xE8:
        raise RuntimeError("enemies_update caller no longer has a near CALL")
    disp = int.from_bytes(call[1:], "little", signed=True)
    if CALL_SITE + 3 + disp != CODE_START:
        raise RuntimeError("enemies_update near CALL no longer reaches enemy script")

    relocation_sites = []
    for index in range(relocation_count):
        pos = relocation_offset + index * 4
        site = word(target, pos + 2) * 16 + word(target, pos)
        if START <= site < END:
            relocation_sites.append({"index": index, "load_site": f"0x{site:X}"})

    receipt = {
        "schema_version": 1,
        "claim": "MAIN B4M enemy-script physical boundary and switch ownership",
        "target_sha256": TARGET_SHA256,
        "header_size": header_size,
        "relocation_count": relocation_count,
        "ndisasm_path": ndisasm,
        "ndisasm_sha256": sha(Path(ndisasm).read_bytes()),
        "extent": {
            "segment": "B4M_UPDATE_TEXT / main_03",
            "segment_start": "13A9:1ABF",
            "load_start": f"0x{START:X}",
            "load_end_exclusive": f"0x{END:X}",
            "file_start": f"0x{header_size + START:X}",
            "size": END - START,
            "sha256": sha(load[START:END]),
        },
        "functions": slices,
        "table": {
            "segment_start": f"13A9:{TABLE_START - CS_LOAD_BASE:04X}",
            "load_start": f"0x{TABLE_START:X}",
            "size": len(table),
            "sha256": sha(table),
            "entry_count": len(destinations),
            "unique_destinations": len(set(destinations)),
            "instruction_starts": len(starts),
            "first_destinations": [f"0x{dest:X}" for dest in destinations[:16]],
            "min_destination": f"0x{min(destinations):X}",
            "max_destination": f"0x{max(destinations):X}",
        },
        "caller": {
            "enemies_update_near_call_load": f"0x{CALL_SITE:X}",
            "resolved_load_target": f"0x{CODE_START:X}",
        },
        "ordered_relocation_sites": relocation_sites,
        "limit": "Target boundary review only. The original OMF/source is unknown; no source or exact credit is awarded.",
    }
    output.mkdir(parents=True)
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"extent={END - START} code={TABLE_START - CODE_START} table={len(table)}")
    print(f"switch_entries={len(destinations)} unique={len(set(destinations))} all_instruction_starts=true")
    print(f"relocations={[item['load_site'] for item in relocation_sites]}")
    print(f"receipt: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
