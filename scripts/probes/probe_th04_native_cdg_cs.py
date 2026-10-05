#!/usr/bin/env python3
"""Replay native MAINE CDG instruction patches with real, pinned staff assets.

CPU-only: ordinary RAM stands in for VRAM, so this verifies code ownership,
completed far calls and the plane renderer's aligned bytes, not GRCG behavior.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/probes")]
from lib.pc98 import parse_mz
from prepare_product_hdi import Fat12, u16, u32
from probe_th04_pf_archive import ARCHIVES, parse_archive
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.x86_const import (UC_X86_REG_CS, UC_X86_REG_IP, UC_X86_REG_DS,
                              UC_X86_REG_ES, UC_X86_REG_SS, UC_X86_REG_SP)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(ROOT / ".analysis/reconstruction/probes"):
        parser.error("use a new private probe directory")
    build = args.build_dir.resolve()
    manifest = json.loads((build / "build.json").read_text())
    data = (build / "MAINE.EXE").read_bytes()
    record = manifest["products"]["maine"]
    if len(data) != record["size"] or sha(data) != record["sha256"]:
        raise ValueError("native MAINE identity drift")
    mz = parse_mz(data)
    if not mz.valid:
        raise ValueError("invalid native MAINE MZ")
    map_path = Path(record["build_receipt"]).parent / "source/obj/product/maine-native.map"
    map_bytes = map_path.read_bytes()
    text = map_bytes.decode("ascii")
    def symbol(name: str) -> tuple[int, int]:
        match = re.search(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+" + re.escape(name) + r"\s*$", text)
        if not match:
            raise ValueError(f"missing linked public: {name}")
        return int(match[1], 16), int(match[2], 16)
    ds_frame, slot_offset = symbol("_cdg_slots")
    providers = {}
    for owner, public in (("src/maine/formats/cdg_put_plane.asm", "CDG_PUT_PLANE"),
                          ("src/shared/formats/cdg_put.asm", "CDG_PUT_8")):
        found = []
        for line in text.splitlines():
            m = re.match(r"\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE\b", line)
            if m and int(m[3], 16) and "M=" + owner.replace("/", "\\") + " " in line:
                found.append(tuple(int(m[i], 16) for i in (1, 2, 3)))
        if len(found) != 1 or symbol(public) != found[0][:2]:
            raise ValueError(f"ambiguous renderer ownership: {owner}")
        providers[public] = found[0]
    runtime = tomllib.loads((ROOT / "config/runtime.toml").read_text())
    image = (ROOT / runtime["image"]["path"]).read_bytes()
    if len(image) != runtime["image"]["size"] or sha(image) != runtime["image"]["sha256"]:
        raise ValueError("pinned HDI identity drift")
    fs = Fat12(bytearray(image))
    folder = fs.find_entry([fs.root], b"GENSO      ")
    directory = [fs.cluster_offset(c) for c in fs.chain(u16(fs.image, folder + 26))]
    archive = ARCHIVES["op_end"]
    entry = fs.find_entry(directory, archive["fat_name"])
    blob = fs.file_bytes(u16(fs.image, entry + 26), u32(fs.image, entry + 28))
    if sha(blob) != archive["sha256"]:
        raise ValueError("pinned staff archive identity drift")
    _, members = parse_archive(blob, "op_end", archive)
    results = []
    for public, fixture in (("CDG_PUT_PLANE", "SFF1B.CDG"), ("CDG_PUT_8", "SFF1.CDG")):
        seg, off, size = providers[public]
        start, end = seg * 16 + off, seg * 16 + off + size
        resource = members[fixture]
        header = bytearray(resource[:16])
        plane_bytes = u16(header, 0)
        # A high source segment avoids the relocated product and its DGROUP.
        colors_seg, alpha_seg, stack_seg = 0x8500, 0x8000, 0x9000
        header[12:16] = struct.pack("<HH", alpha_seg, colors_seg)
        colors = resource[16:] if public == "CDG_PUT_PLANE" else resource[16 + plane_bytes:]
        if len(colors) != plane_bytes * 4:
            raise ValueError("unexpected pinned CDG layout")
        for load in (0x2000, 0x6000):
            uc = Uc(UC_ARCH_X86, UC_MODE_16)
            uc.mem_map(0, 0x200000)
            program = mz.relocated_program_image(load)
            uc.mem_write(load * 16, program)
            actual_cs, actual_ds = load + seg, load + ds_frame
            uc.mem_write(actual_ds * 16 + slot_offset, bytes(header))
            uc.mem_write(colors_seg * 16, colors)
            if public == "CDG_PUT_8":
                uc.mem_write(alpha_seg * 16, resource[16:16 + plane_bytes])
            stop_cs, stop_ip, sp = 0x1000, 0x100, 0xFF00
            args_words = (0, 0, 160, 352) if public == "CDG_PUT_PLANE" else (0, 160, 352)
            stack = struct.pack("<" + "H" * (2 + len(args_words)), stop_ip, stop_cs, *args_words)
            uc.mem_write(stack_seg * 16 + sp, stack)
            for reg, value in ((UC_X86_REG_CS, actual_cs), (UC_X86_REG_IP, off),
                               (UC_X86_REG_DS, actual_ds), (UC_X86_REG_ES, actual_ds),
                               (UC_X86_REG_SS, stack_seg), (UC_X86_REG_SP, sp)):
                uc.reg_write(reg, value)
            writes, stopped = [], []
            def write_hook(cpu, access, address, count, value, user):
                if load * 16 <= address < load * 16 + len(program):
                    relative = address - load * 16
                    if not start <= relative or relative + count > end:
                        raise ValueError(f"renderer writes another code owner: {relative:05X}")
                    writes.append(dict(load_offset=relative, size=count, value=value))
            def code_hook(cpu, address, count, user):
                if address == stop_cs * 16 + stop_ip:
                    stopped.append(True)
                    cpu.emu_stop()
            uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
            uc.hook_add(UC_HOOK_CODE, code_hook)
            uc.emu_start(actual_cs * 16 + off, 0, count=1000000)
            if not stopped or len(writes) != (3 if public == "CDG_PUT_PLANE" else 1):
                raise ValueError("renderer did not complete its far call and code patches")
            expected_values = [u16(header, 8) * 2, 0xFFFF, 0xFFFF] if public == "CDG_PUT_PLANE" else [colors_seg]
            if [w["value"] for w in writes] != expected_values:
                raise ValueError("renderer instruction patch values differ")
            plane_pixels_pass = None
            if public == "CDG_PUT_PLANE":
                width, height = u16(header, 2) // 8, u16(header, 4)
                bottom = u16(header, 6)
                for row in range(height):
                    address = 0xA8000 + 160 * 80 + 352 // 8 + bottom - row * 80
                    if bytes(uc.mem_read(address, width)) != colors[row * width:(row + 1) * width]:
                        raise ValueError("aligned plane output differs from the pinned staff image")
                plane_pixels_pass = True
            results.append(dict(public=public, fixture=fixture, fixture_sha256=sha(resource),
                                load_segment=load, cs=actual_cs, ip=off, writes=writes,
                                completed_far_call=True, plane_pixels_pass=plane_pixels_pass))
    output.mkdir(parents=True)
    receipt = dict(schema_version=1, observed_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   mz_sha256=sha(data), map_sha256=sha(map_bytes), archive_sha256=sha(blob),
                   script_sha256=sha(Path(__file__).read_bytes()), results=results, passed=True,
                   scope="CPU-only complete CDG calls at two load segments; own-code patch destinations and aligned plane bytes. No GRCG or full Ending acceptance.")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("CDG own-code patches and aligned staff plane: PASS (two load segments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
