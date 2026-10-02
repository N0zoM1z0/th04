#!/usr/bin/env python3
"""Execute native MAIN ring tuning and clipping in an isolated x86 Oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from capstone import Cs, CS_ARCH_X86, CS_MODE_16
import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_AX

from inspect_th04_emulator_cpu_fault import relocate


def probe(receipt: Path) -> dict:
    link = json.loads(receipt.read_text())["link"]
    source = receipt.parent / "source"
    image = (source / "bin/main-native.exe").read_bytes()
    mapping = (source / link["map"]).read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if (link["exit"] or link["errors"] or digest != link["mz"]["sha256"]
            or hashlib.sha256(mapping).hexdigest() != link["map_sha256"]):
        raise ValueError("native MAIN/MAP identity drift")
    text = mapping.decode("ascii")

    def symbol(name):
        locations = set(re.findall(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?"
                                   + re.escape(name) + r"\s*$", text))
        if len(locations) != 1:
            raise ValueError(f"ambiguous symbol: {name}")
        return tuple(int(v, 16) for v in next(iter(locations)))

    load = 0x1000
    body = relocate(image, load)
    clip_segment, clip_offset = symbol("bullet_template_clip()")
    data_segment, template = symbol("_bullet_template")
    _, clear = symbol("_bullet_clear_time")
    _, perf = symbol("_playperf")
    tune_segment, tune_offset = symbol("BULLET_TEMPLATE_TUNE_EASY")
    instructions = Cs(CS_ARCH_X86, CS_MODE_16).disasm(
        body[clip_segment * 16 + clip_offset:clip_segment * 16 + clip_offset + 128], clip_offset)
    fallback = next(i.address for i in instructions
                    if i.mnemonic == "cmp" and i.op_str == f"byte ptr [0x{clear:x}], 0")
    ds_address = (load + data_segment) * 16

    def execute(segment, offset, group, count, stop_at_fallback=False):
        machine = Uc(UC_ARCH_X86, UC_MODE_16)
        machine.mem_map(0, 0x100000)
        machine.mem_write(load * 16, body)
        machine.mem_write(ds_address + template + 10, bytes([group]))
        machine.mem_write(ds_address + template + 13, bytes([count]))
        machine.mem_write(ds_address + perf, b"\x04")
        for reg, value in ((UC_X86_REG_CS, load + segment), (UC_X86_REG_DS, load + data_segment),
                           (UC_X86_REG_SS, 0x6000), (UC_X86_REG_SP, 0x8000)):
            machine.reg_write(reg, value)
        machine.mem_write(0x68000, b"\x00\xff")
        reached = []
        def stop(machine, address, size, user_data):
            if stop_at_fallback and address == (load + clip_segment) * 16 + fallback:
                reached.append(True)
                machine.emu_stop()
        machine.hook_add(UC_HOOK_CODE, stop)
        machine.emu_start((load + segment) * 16 + offset,
                          (load + segment) * 16 + 0xff00, count=2000)
        return dict(result_count=machine.mem_read(ds_address + template + 13, 1)[0],
                    clipped=bool(machine.reg_read(UC_X86_REG_AX) & 0xff),
                    reached_original_checks=bool(reached), sp=machine.reg_read(UC_X86_REG_SP))

    tuned = execute(tune_segment, tune_offset, 0x2c, 6)
    if tuned["result_count"] != 0 or tuned["sp"] != 0x8002:
        raise ValueError("six-shot Easy/performance-4 control did not return zero")
    cases = []
    for group, count in ((0x26, 0), (0x2c, 0), (0x26, 1), (0x2c, 6), (0, 0)):
        result = execute(clip_segment, clip_offset, group, count, True)
        empty_ring = group in (0x26, 0x2c) and count == 0
        passed = ((result["clipped"] and result["sp"] == 0x8002
                   and not result["reached_original_checks"]) if empty_ring
                  else result["reached_original_checks"])
        cases.append(dict(group=group, count=count, passed=passed, **result))
    return dict(scope="isolated native x86 tuning/empty-ring branch; not PC-98 gameplay",
                unicorn_version=unicorn.__version__,
                executable_sha256=digest, map_sha256=link["map_sha256"], tuned=tuned,
                cases=cases, passed=all(row["passed"] for row in cases))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--link-receipt", required=True, type=Path)
    args = parser.parse_args()
    report = probe(args.link_receipt.resolve())
    output = args.link_receipt.parent / "empty-ring.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(report=str(output), passed=report["passed"])))
    raise SystemExit(0 if report["passed"] else 1)
