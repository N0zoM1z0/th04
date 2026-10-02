#!/usr/bin/env python3
"""Check MAIN bullet switch tables in the CS frame used by its far caller."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from capstone import Cs, CS_ARCH_X86, CS_MODE_16
from capstone.x86_const import X86_OP_IMM, X86_OP_MEM, X86_REG_CS

from audit_th04_native_irq_vectors import direct_call_segments
from lib.pc98 import parse_mz

ROOT = Path(__file__).resolve().parents[2]


def audit(receipt_path: Path) -> dict:
    receipt = json.loads(receipt_path.read_text())
    link = receipt["link"]
    if receipt["artifact"] != "th04-main" or link["exit"] or link["errors"]:
        raise ValueError("requires a complete native MAIN link")
    work = receipt_path.parent / "source"
    image = (work / "bin/main-native.exe").read_bytes()
    map_bytes = (work / link["map"]).read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if not parse_mz(image).valid or digest != link["mz"]["sha256"]:
        raise ValueError("native MAIN identity or format drift")
    if hashlib.sha256(map_bytes).hexdigest() != link["map_sha256"]:
        raise ValueError("native MAP identity drift")
    body = image[int.from_bytes(image[8:10], "little") * 16:]
    roots = [r for r in receipt["root_records"]
             if r["source"] == "src/main/bullet/update.cpp"]
    if len(roots) != 1:
        raise ValueError("bullet update producer is not unique")
    module = roots[0]["compile_alias"]
    contributions = []
    code_ranges = []
    text = map_bytes.decode("ascii")
    for line in text.splitlines():
        match = re.match(r"\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})"
                         r"\s+C=CODE\b.*\bM=(\S+)", line)
        if not match or not int(match[3], 16):
            continue
        extent = tuple(int(match[i], 16) for i in (1, 2, 3))
        code_ranges.append(extent)
        if match[4].replace("\\", "/") == module:
            contributions.append(extent)
    if len(contributions) != 1:
        raise ValueError("bullet code contribution is not unique")
    segment, offset, size = contributions[0]
    start = segment * 16 + offset
    public = re.search(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+"
                       r"bullets_update\(\)\s*$", text)
    if not public:
        raise ValueError("bullet update entry is missing")
    entry = int(public[1], 16) * 16 + int(public[2], 16)
    relocations = set()
    table = int.from_bytes(image[24:26], "little")
    for i in range(int.from_bytes(image[6:8], "little")):
        pos = table + i * 4
        relocations.add(int.from_bytes(image[pos:pos + 2], "little")
                        + 16 * int.from_bytes(image[pos + 2:pos + 4], "little"))
    frames = direct_call_segments(body, entry, relocations, code_ranges)
    if frames != {segment}:
        raise ValueError(f"bullet far caller and MAP frames disagree: {frames}")
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    decoder.detail = True
    special = re.search(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?"
                        r"bullet_update_special\(.*$", text)
    if not special or int(special[1], 16) != segment:
        raise ValueError("special-motion entry has no matching CS frame")
    special_offset = int(special[2], 16)
    entry_offset = int(public[2], 16)
    # A compiler table can sit between these functions. Restart decoding at
    # each public entry instead of interpreting that table as instructions.
    instructions = []
    for begin, end in ((special_offset, entry_offset), (entry_offset, offset + size)):
        instructions.extend(decoder.disasm(body[segment * 16 + begin:
                                                segment * 16 + end], begin))
    rows = []
    for index, instruction in enumerate(instructions):
        if instruction.mnemonic != "jmp" or len(instruction.operands) != 1:
            continue
        operand = instruction.operands[0]
        if (operand.type != X86_OP_MEM or operand.mem.segment != X86_REG_CS
                or not operand.mem.base or operand.size != 2):
            continue
        limits = [i.operands[1].imm for i in instructions[max(0, index - 8):index]
                  if i.mnemonic == "cmp" and len(i.operands) == 2
                  and i.operands[1].type == X86_OP_IMM]
        if not limits or not 0 <= limits[-1] < 64:
            raise ValueError("switch bounds require separate review")
        count = limits[-1] + 1
        table_address = segment * 16 + (operand.mem.disp & 0xFFFF)
        inside = start <= table_address and table_address + 2 * count <= start + size
        targets = [segment * 16 + int.from_bytes(body[table_address + i * 2:
                   table_address + i * 2 + 2], "little") for i in range(count)]
        rows.append(dict(dispatch_offset=instruction.address, table_load_address=table_address,
                         count=count, target_load_addresses=targets,
                         pass_table=inside,
                         pass_targets=all(start <= t < start + size for t in targets)))
    if len(rows) != 2:
        raise ValueError(f"expected motion and rank switches, found {len(rows)}")
    return dict(scope="native bullet motion/rank switch CS frames; not gameplay acceptance",
                executable_sha256=digest, map_sha256=hashlib.sha256(map_bytes).hexdigest(),
                caller_cs=segment, contribution_start=start, contribution_size=size,
                switches=rows, passed=all(r["pass_table"] and r["pass_targets"] for r in rows))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--link-receipt", required=True, type=Path)
    args = parser.parse_args()
    path = args.link_receipt.resolve()
    if not path.is_relative_to(ROOT / ".analysis"):
        parser.error("link receipt must be private")
    result = audit(path)
    output = path.parent / "bullet-switches.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(passed=result["passed"], report=str(output), switches=result["switches"])))
    return int(not result["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
