#!/usr/bin/env python3
"""Review ONGCHK call entries and two Ghidra-split shared tails from target bytes."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / ".analysis/reconstruction/v218-th04-zun-diet/payload.bin"
PAYLOAD_SHA = "baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e"
COMPONENT_SHA = "4f9a9451f19bdd8d3ea8949a5ea75df6c2f92a9a84dcf39e1d7cf13421acc8a0"
ENTRY = 0x100
CODE_END = 0x47C
CALL_TARGETS = {0x127: 1, 0x1A0: 2, 0x247: 1, 0x2E4: 1, 0x2FB: 1,
                0x3A8: 1, 0x428: 2, 0x449: 1, 0x455: 28}
SHARED_TAILS = {0x2C2: 3, 0x2DD: 5}
LINE = re.compile(r"^([0-9A-F]{8})\s+([0-9A-F]+)\s+(.+)$")
DIRECT_TARGET = re.compile(r"\b0x([0-9a-f]+)$")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output must be a new direct child of .analysis/reconstruction/probes")
    subprocess.run([sys.executable, "scripts/preflight.py"], cwd=ROOT,
                   capture_output=True, text=True, check=True)
    payload = PAYLOAD.read_bytes()
    component = payload[0x355:0x6F3]
    if sha(payload) != PAYLOAD_SHA or len(component) != 926 or sha(component) != COMPONENT_SHA:
        raise RuntimeError("attested target component identity drift")
    output.mkdir()
    target_path = output / "ongchk-target.com"
    target_path.write_bytes(component)
    result = subprocess.run(["ndisasm", "-b16", "-o0x100", str(target_path)],
                            capture_output=True, text=True, check=True)
    starts: set[int] = set()
    instruction_count = 0
    next_addr = ENTRY
    calls: Counter[int] = Counter()
    branches: Counter[int] = Counter()
    for line in result.stdout.splitlines():
        match = LINE.match(line)
        if not match:
            raise RuntimeError(f"unparsed disassembly line: {line}")
        addr = int(match[1], 16)
        if addr >= CODE_END:
            break
        opcode = bytes.fromhex(match[2])
        if addr != next_addr or component[addr - ENTRY:addr - ENTRY + len(opcode)] != opcode:
            raise RuntimeError(f"noncontiguous or incorrect target decode at {addr:#x}")
        starts.add(addr)
        instruction_count += 1
        next_addr += len(opcode)
        mnemonic = match[3].split()[0]
        direct = DIRECT_TARGET.search(match[3])
        if direct and mnemonic == "call":
            calls[int(direct[1], 16)] += 1
        elif direct and (mnemonic.startswith("j") or mnemonic == "loop"):
            branches[int(direct[1], 16)] += 1
    if next_addr != CODE_END or instruction_count != 390:
        raise RuntimeError("ONGCHK code/data seam or instruction count drift")
    if dict(calls) != CALL_TARGETS:
        raise RuntimeError(f"ONGCHK near-CALL target set drift: {dict(calls)}")
    if any(dest not in starts for dest in calls | branches):
        raise RuntimeError("direct branch/call lands outside decoded instruction starts")
    if any(calls[tail] or branches[tail] != count
           for tail, count in SHARED_TAILS.items()):
        raise RuntimeError("shared-tail control-flow premise failed")
    if component[CODE_END - ENTRY:0x49C - ENTRY] != b"*+=-PMD ADPCM RAM Check Data-=+*":
        raise RuntimeError("ONGCHK initialized data boundary drift")
    if component[0x49C - ENTRY:] != b"\xFF\x00":
        raise RuntimeError("ONGCHK final initialized bytes drift")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "artifact": "th04-zun", "target_extent": "com-payload/0x355+0x39E",
        "target_payload_sha256": PAYLOAD_SHA, "target_component_sha256": COMPONENT_SHA,
        "code_runtime_extent": "0x100..0x47B", "instruction_count": instruction_count,
        "call_targets": {f"0x{k:X}": v for k, v in sorted(calls.items())},
        "shared_tail_jump_targets": {f"0x{k:X}": branches[k] for k in SHARED_TAILS},
        "false_ghidra_function_starts_in_payload": ["0x517", "0x532"],
        "data_runtime_extent": "0x47C..0x49D",
        "claim": "0x2C2 and 0x2DD are branch-only shared tails, not call entries",
    }
    path = output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(path), "receipt_sha256": sha(path.read_bytes())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
