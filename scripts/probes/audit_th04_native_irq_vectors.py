#!/usr/bin/env python3
"""Check native CS-relative vectors and self-modifying renderer operands."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.pc98 import parse_mz

ROOT = Path(__file__).resolve().parents[2]
PROVIDERS = {
    "VSYNC_START": ("src/shared/hardware/vsync_irq.asm", {
        0x0A: b"\x50\x1e\xb8", 0x18: b"\x9c\x2e\xff\x1e",
    }),
    "BGM_TIMER_START": ("src/shared/sound/bgm_timer.asm", {
        0x08: b"\x50\x53\x51\x52\x56\x57\x55\x1e\x06",
    }),
    "PF_HOOK_INSTALL": ("src/shared/formats/pf_int21.asm", {
        0x21: b"\x2e\x80\x3e",
    }),
}
SELF_MODIFYING = {
    "src/shared/hardware/bgimager.asm", "src/shared/hardware/graph_putsa_fx.asm",
    "src/shared/hardware/super_roll_put.asm", "src/shared/hardware/super_roll_put_1plane.asm",
    "src/shared/formats/cdg_put.asm",
}
RENDERER_ENTRIES = {
    "src/shared/formats/cdg_put.asm": "CDG_PUT_8",
    "src/maine/formats/cdg_put_plane.asm": "CDG_PUT_PLANE",
    "src/shared/hardware/bgimager.asm": "BGIMAGE_PUT_RECT_16",
    "src/shared/hardware/graph_putsa_fx.asm": "GRAPH_PUTSA_FX",
    "src/shared/hardware/super_roll_put.asm": "SUPER_ROLL_PUT",
    "src/shared/hardware/super_roll_put_1plane.asm": "SUPER_ROLL_PUT_1PLANE",
    "src/op/formats/cdg_p_nc.asm": "CDG_PUT_NOCOLORS_8",
}


def direct_call_segments(body: bytes, entry: int, relocation_sites: set[int],
                         code_ranges: list[tuple[int, int, int]]) -> set[int]:
    segments = set()
    for call in re.finditer(rb"(?=\x9a(....))", body, re.S):
        if call.start() + 3 not in relocation_sites:
            continue
        offset = int.from_bytes(call[1][:2], "little")
        segment = int.from_bytes(call[1][2:], "little")
        if segment * 16 + offset == entry:
            segments.add(segment)
    for segment, offset, size in code_ranges:
        start = segment * 16 + offset
        for call in re.finditer(rb"\x0e\xe8(..)", body[start:start + size], re.S):
            displacement = int.from_bytes(call[1], "little", signed=True)
            destination = (offset + call.start() + 4 + displacement) & 65535
            if segment * 16 + destination == entry:
                segments.add(segment)
    return segments


def vector_targets(code: bytes, start: int, call_cs: int,
                   signatures: dict[int, bytes]) -> list[dict]:
    result = []
    # PUSH CS / POP DS / MOV DX,offset / MOV AX,25xxh / INT 21h.
    for match in re.finditer(rb"\x0e\x1f\xba(..)\xb8(.)\x25\xcd\x21", code, re.S):
        vector = match[2][0]
        if vector not in signatures:
            raise ValueError(f"unexpected installed vector: {vector:02X}")
        signature = signatures[vector]
        offsets = [m.start() for m in re.finditer(re.escape(signature), code)]
        if len(offsets) != 1:
            raise ValueError(f"handler has no unique signature: INT {vector:02X}")
        stored_offset = int.from_bytes(match[1], "little")
        expected = start + offsets[0]
        actual = call_cs * 16 + stored_offset
        result.append(dict(vector=vector, call_cs=call_cs, stored_offset=stored_offset,
                           expected_load_address=expected, actual_load_address=actual,
                           pass_vector=expected == actual))
    if {r["vector"] for r in result} != set(signatures) or len(result) != len(signatures):
        raise ValueError("missing or repeated IRQ installation")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--link-receipt", required=True, type=Path)
    args = parser.parse_args()
    receipt_path = args.link_receipt.resolve()
    if not receipt_path.is_relative_to(ROOT / ".analysis"):
        parser.error("link receipt must be private")
    receipt = json.loads(receipt_path.read_text())
    link = receipt.get("link", {})
    complete = receipt.get("link_complete", link.get("exit") == 0 and not link.get("errors"))
    if not complete:
        raise ValueError("requires a complete native link")
    artifact = receipt["artifact"].removeprefix("th04-")
    renderer_sources = SELF_MODIFYING | ({"src/op/formats/cdg_p_nc.asm"} if artifact == "op" else set())
    if artifact == "maine":
        renderer_sources.add("src/maine/formats/cdg_put_plane.asm")
    work = receipt_path.parent / "source"
    exe = work / f"bin/{artifact}-native.exe"
    maps = list(work.glob(f"obj/**/{artifact}-native.map"))
    if len(maps) != 1:
        raise ValueError("native MAP is not unique")
    image = exe.read_bytes()
    mz = parse_mz(image)
    header = receipt.get("mz_header", link.get("mz", {}))
    if not mz.valid or hashlib.sha256(image).hexdigest() != header["sha256"]:
        raise ValueError("native executable identity or format drift")
    body = image[int.from_bytes(image[8:10], "little") * 16:]
    relocation_table = int.from_bytes(image[0x18:0x1A], "little")
    relocation_count = int.from_bytes(image[6:8], "little")
    relocation_sites = set()
    for index in range(relocation_count):
        pos = relocation_table + index * 4
        relocation_sites.add(int.from_bytes(image[pos:pos + 2], "little")
                             + 16 * int.from_bytes(image[pos + 2:pos + 4], "little"))
    map_text = maps[0].read_text()
    code_ranges = []
    for line in map_text.splitlines():
        m = re.match(r"\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE\b", line)
        if m and int(m[3], 16):
            code_ranges.append(tuple(int(m[i], 16) for i in (1, 2, 3)))
    rows = []
    for public, (source, signatures) in PROVIDERS.items():
        contributions = []
        for line in map_text.splitlines():
            m = re.match(r"\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE\b.*\bM=(\S+)", line)
            if m and m[4].replace("\\", "/") == source and int(m[3], 16):
                contributions.append(tuple(int(m[i], 16) for i in (1, 2, 3)))
        if len(contributions) != 1:
            raise ValueError(f"IRQ provider contribution is not unique: {source}")
        segment, offset, size = contributions[0]
        start = segment * 16 + offset
        public_match = re.search(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+" + public + r"\s*$", map_text)
        if not public_match:
            raise ValueError(f"IRQ entry missing: {public}")
        entry = int(public_match[1], 16) * 16 + int(public_match[2], 16)
        call_segments = direct_call_segments(body, entry, relocation_sites, code_ranges)
        if not call_segments:
            raise ValueError(f"IRQ entry has no far call: {public}")
        for call_cs in sorted(call_segments):
            rows.extend(dict(provider=public, **r) for r in
                        vector_targets(body[start:start + size], start, call_cs, signatures))
    from capstone import Cs, CS_ARCH_X86, CS_MODE_16
    from capstone.x86_const import X86_OP_MEM, X86_REG_CS
    disassembler = Cs(CS_ARCH_X86, CS_MODE_16)
    disassembler.detail = True
    patches = []
    frames = []
    seen_sources = set()
    for line in map_text.splitlines():
        match = re.match(r"\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE\b.*\bM=(\S+)", line)
        if not match or match[4].replace("\\", "/") not in renderer_sources or not int(match[3], 16):
            continue
        source = match[4].replace("\\", "/")
        seen_sources.add(source)
        segment, offset, size = (int(match[i], 16) for i in (1, 2, 3))
        start = segment * 16 + offset
        public = RENDERER_ENTRIES[source]
        entry_match = re.search(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?"
                                + public + r"\s*$", map_text)
        if not entry_match:
            raise ValueError(f"renderer entry missing: {public}")
        entry_segment, entry_offset = (int(entry_match[i], 16) for i in (1, 2))
        call_segments = direct_call_segments(body, entry_segment * 16 + entry_offset,
                                            relocation_sites, code_ranges)
        frames.append(dict(source=source, direct_call_cs=sorted(call_segments),
                           map_entry_cs=entry_segment))
        # An uncalled owner has no runtime call-frame evidence. Check its MAP
        # public frame, and expose that distinction in the report.
        checked_segments = call_segments or {entry_segment}
        for instruction in disassembler.disasm(body[start:start + size], offset):
            for operand in instruction.operands:
                if operand.type != X86_OP_MEM or operand.mem.segment != X86_REG_CS:
                    continue
                if operand.mem.base or operand.mem.index:
                    raise ValueError(f"dynamic CS operand needs a separate audit: {source}")
                for call_cs in sorted(checked_segments):
                    destination = call_cs * 16 + operand.mem.disp
                    patches.append(dict(source=source, call_cs=call_cs,
                                        instruction_offset=instruction.address,
                                        destination_load_address=destination,
                                        pass_operand=start <= destination and destination + operand.size <= start + size))
    if seen_sources != renderer_sources or not patches:
        raise ValueError("self-modifying providers are missing from the native MAP")
    result = dict(scope="linked native IRQ vectors and CS-relative renderer operands; not complete runtime acceptance",
                  executable_sha256=hashlib.sha256(image).hexdigest(),
                  map_sha256=hashlib.sha256(maps[0].read_bytes()).hexdigest(),
                  vectors=rows, renderer_frames=frames, code_operands=patches,
                  pass_vectors=all(r["pass_vector"] for r in rows),
                  pass_code_operands=all(r["pass_operand"] for r in patches))
    (receipt_path.parent / "irq-vectors.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(pass_vectors=result["pass_vectors"], vector_count=len(rows),
                          pass_code_operands=result["pass_code_operands"],
                          code_operand_count=len(patches)), sort_keys=True))
    return int(not result["pass_vectors"] or not result["pass_code_operands"])


if __name__ == "__main__":
    raise SystemExit(main())
