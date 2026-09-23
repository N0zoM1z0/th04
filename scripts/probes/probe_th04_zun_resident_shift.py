#!/usr/bin/env python3
"""Diagnose ZUN resident layout displacement without mutating either binary."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin"
PAYLOAD_SHA = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
REPLAY = ROOT / ".analysis/reconstruction/probes/v546-zun-runtime-inventory-001"
REPLAY_RECEIPT_SHA = "a4cdbbf3480581e558f1354e9637b8ba2af99a1e32689c9b38ea68c3cfb02d12"
CANDIDATE_SHA = "a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab"
TARGET_COMPONENT_SHA = "cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110"
COMPONENT_START = 0xB68
COMPONENT_END = 0x2440
SIZE = COMPONENT_END - COMPONENT_START

# Target component offsets. The two excluded windows are actual near CALL
# instructions absent from the current natural _main; the candidate's six
# trailing zero bytes are excluded separately. These are comparison coordinates,
# never edits, patch bytes, or an acceptance transform.
TARGET_ONLY_CALLS = ((0x380, 0x383), (0x38C, 0x38F))
CANDIDATE_ONLY_FILL = (0x1482, 0x1488)
MAPPING = ((0, 0x380, 0), (0x383, 0x38C, -3),
           (0x38F, 0x1488, -6), (0x1488, SIZE, 0))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compare(target: bytes, candidate: bytes) -> dict[str, object]:
    if len(target) != SIZE or len(candidate) != SIZE:
        raise ValueError("resident component size drift")
    if any(target[start] != 0xE8 or end - start != 3
           for start, end in TARGET_ONLY_CALLS):
        raise ValueError("target-only _main near CALL shape drift")
    if candidate[CANDIDATE_ONLY_FILL[0]:CANDIDATE_ONLY_FILL[1]] != bytes(6):
        raise ValueError("candidate-only end fill drift")
    if not (MAPPING[0][1] == TARGET_ONLY_CALLS[0][0]
            and MAPPING[1][0] == TARGET_ONLY_CALLS[0][1]
            and MAPPING[1][1] == TARGET_ONLY_CALLS[1][0]
            and MAPPING[2][0] == TARGET_ONLY_CALLS[1][1]
            and MAPPING[2][1] == CANDIDATE_ONLY_FILL[1]
            and MAPPING[3][0] == CANDIDATE_ONLY_FILL[1]):
        raise ValueError("alignment partition drift")
    differences = []
    mapped = 0
    for start, end, displacement in MAPPING:
        for target_offset in range(start, end):
            candidate_offset = target_offset + displacement
            if not 0 <= candidate_offset < SIZE:
                raise ValueError("alignment leaves candidate")
            mapped += 1
            left = target[target_offset]
            right = candidate[candidate_offset]
            if left != right:
                differences.append({
                    "target_offset": f"0x{target_offset:04X}",
                    "candidate_offset": f"0x{candidate_offset:04X}",
                    "displacement": displacement,
                    "byte_delta_mod_256": (left - right) & 0xFF,
                })
    raw_differences = sum(left != right for left, right in zip(target, candidate))
    deltas = Counter(item["byte_delta_mod_256"] for item in differences)
    if (raw_differences != 4241 or mapped != SIZE - 6
            or len(differences) != 46
            or deltas != {6: 36, 250: 5, 3: 4, 1: 1}):
        raise ValueError("ZUN resident shift model no longer fits")
    return {
        "component_size": SIZE,
        "same_position_raw_differences": raw_differences,
        "target_only_call_offsets": [f"0x{start:04X}" for start, _ in TARGET_ONLY_CALLS],
        "target_only_call_total_bytes": 6,
        "candidate_only_zero_fill_offset": "0x1482",
        "candidate_only_zero_fill_size": 6,
        "mapped_positions": mapped,
        "mapped_equal_positions": mapped - len(differences),
        "mapped_difference_count": len(differences),
        "mapped_byte_delta_mod_256": {str(key): value for key, value in sorted(deltas.items())},
        "difference_coordinates": differences,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        ap.error("output must be new directly below .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   capture_output=True, text=True, check=True)
    payload = PAYLOAD.read_bytes()
    replay_bytes = (REPLAY / "receipt.json").read_bytes()
    candidate = (REPLAY / "a/res_huma.com").read_bytes()
    target = payload[COMPONENT_START:COMPONENT_END]
    if (digest(payload) != PAYLOAD_SHA or digest(replay_bytes) != REPLAY_RECEIPT_SHA
            or digest(candidate) != CANDIDATE_SHA or digest(target) != TARGET_COMPONENT_SHA):
        raise RuntimeError("ZUN target or replay identity drift")
    replay = json.loads(replay_bytes)
    if (replay["target_component_sha256"] != TARGET_COMPONENT_SHA
            or replay["component_raw_difference_count"] != 4241
            or replay["remaining_external_link_inputs"] != ["c0t.obj", "ct.lib"]
            or replay["exact"] is not False):
        raise RuntimeError("ZUN reduced-runtime replay contract drift")
    result = compare(target, candidate)
    output.mkdir(parents=True)
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_scope": "ZUN resident diagnostic alignment of the blocked six-byte _main gap",
        "target_payload_sha256": PAYLOAD_SHA,
        "target_component_sha256": TARGET_COMPONENT_SHA,
        "candidate_component_sha256": CANDIDATE_SHA,
        "candidate_replay_receipt_sha256": REPLAY_RECEIPT_SHA,
        "result": result,
        "limit": (
            "Read-only alignment diagnostic. No target/candidate bytes are patched, "
            "no source or exact state is promoted, and the 46 aligned byte "
            "differences still require source/link ownership review."
        ),
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"ZUN resident: {result['same_position_raw_differences']} same-position differences; "
          f"{result['mapped_difference_count']} aligned differences; not exact")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
