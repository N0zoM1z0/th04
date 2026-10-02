#!/usr/bin/env python3
"""Reduce private MAIN state records; this is bounded gameplay evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from prepare_th04_maine_diagnostic_hdi import Fat12, u16, u32

ROOT = Path(__file__).resolve().parents[2]


def reduce_records(data: bytes) -> dict[str, object]:
    if not data or len(data) % 48:
        raise ValueError("missing or truncated 24-word gameplay records")
    rows = list(struct.iter_unpack("<24H", data))
    if any(r[0] != 1 or r[7] > 68 or any(d > 9 for d in r[16:]) for r in rows):
        raise ValueError("invalid gameplay record schema or values")
    def signed(value: int) -> int:
        return value - 65536 if value >= 32768 else value
    moves_right = moves_left = bomb_used = miss_observed = False
    for previous, current in zip(rows, rows[1:]):
        if previous[3] != current[3] or current[1] < previous[1]:
            continue
        delta = signed(current[4]) - signed(previous[4])
        moves_right |= bool(previous[2] & current[2] & 8 and delta > 0)
        moves_left |= bool(previous[2] & current[2] & 4 and delta < 0)
        bomb_used |= current[12] != previous[12] and current[10] < previous[10]
        miss_observed |= current[11] != previous[11]
    actions = {
        "move_right": moves_right,
        "move_left": moves_left,
        "shoot": any(r[2] & 32 and r[7] > 0 for r in rows),
        "bomb": bomb_used and any(r[2] & 16 for r in rows),
    }
    return {
        "scope": "instrumented MAIN input and state progression; not complete game acceptance",
        "record_count": len(rows), "record_sha256": hashlib.sha256(data).hexdigest(),
        "stages": sorted({r[3] for r in rows}),
        "stage_frame_range": [min(r[1] for r in rows), max(r[1] for r in rows)],
        "input_masks": sorted({r[2] for r in rows}),
        "player_x_subpixel_range": [min(signed(r[4]) for r in rows),
                                    max(signed(r[4]) for r in rows)],
        "max_active_shots": max(r[7] for r in rows),
        "bomb_active_observed": any(r[8] for r in rows),
        "miss_observed": miss_observed,
        "score_range": [min(sum(d * 10**i for i, d in enumerate(r[16:])) for r in rows),
                        max(sum(d * 10**i for i, d in enumerate(r[16:])) for r in rows)],
        "actions": actions, "input_actions_pass": all(actions.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--require-input", action="store_true")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    if not run.is_relative_to(ROOT / ".analysis"):
        parser.error("run directory must be private")
    receipt_data = (run / "receipt.json").read_bytes()
    receipt = json.loads(receipt_data)
    image = (run / "execution.hdi").read_bytes()
    if hashlib.sha256(image).hexdigest() != receipt["executed_hdi_sha256"]:
        raise ValueError("executed image identity drift")
    fs = Fat12(bytearray(image))
    directory = fs.find_entry([fs.root], b"GENSO      ")
    offsets = [fs.cluster_offset(c) for c in fs.chain(u16(fs.image, directory + 26))]
    entry = fs.find_entry(offsets, b"PLAY    BIN")
    result = reduce_records(fs.file_bytes(u16(fs.image, entry + 26), u32(fs.image, entry + 28)))
    result["run_receipt_sha256"] = hashlib.sha256(receipt_data).hexdigest()
    (run / "play-state.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    return int(args.require_input and not result["input_actions_pass"])


if __name__ == "__main__":
    raise SystemExit(main())
