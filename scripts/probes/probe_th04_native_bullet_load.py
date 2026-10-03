#!/usr/bin/env python3
"""Bounded bullet-pool CPU and GRCG stress controls, not a complete Lunatic route.

Execute the complete relocated native MAIN calls. Independent pixel models
check the tiny color-mask and pellet services; ordered VRAM writes and port
events must also agree before/after. Counts measure instructions, not FPS.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import struct

import unicorn
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_AX, UC_X86_REG_DX, UC_X86_REG_ES

from probe_th04_native_planar_kernels import ROOT, LOAD, product, sha, vm

PELLETS, REGULAR, STRIDE = 240, 200, 26
VRAM = 0xA8000
INITIAL = tuple(bytes((i * 37 + p * 13) & 255 for i in range(32768))
                for p in range(4))


def address(prod, symbol):
    segment, offset = prod["entries"][symbol]
    return (LOAD + segment) * 16 + offset


def mask_vm(prod, entry, args=b"", near=True, mode="tiny"):
    u, run, put = vm(prod, entry, args, near=near)
    u.reg_write(UC_X86_REG_ES, 0xA800)
    writes = []

    def write(machine, access, at, size, value, _):
        if VRAM <= at < VRAM + 32768:
            writes.append((at - VRAM, size, value))

    u.hook_add(UC_HOOK_MEM_WRITE, write)

    def finish():
        instructions, ports = run()
        # A separate shadow of all planes models GRCG RMW: set mask bits
        # select the current tile color; zero mask bits preserve old pixels.
        planes = initial_planes()
        if mode == "tiny":
            colors = [sum(bool(ports[j + p][2]) << p for p in range(4))
                      for j in range(0, len(ports), 4)]
            assert all(port == 0x7E and size == 1 and value in (0, 255)
                       for port, size, value in ports)
            # Pair writes with the color active when they execute. A second
            # hook below records the ordered event stream to avoid guessing
            # how many writes each variable-density color layer performs.
            assert colors == tile_colors
        else:
            assert not ports
        for at, size, value, color in colored_writes:
            for byte in range(size):
                mask = (value >> (byte * 8)) & 255
                for p, plane in enumerate(planes):
                    plane[at + byte] = ((plane[at + byte] & ~mask) |
                                        (mask if color & (1 << p) else 0))
        return instructions, ports, writes, bytes().join(map(bytes, planes))

    tile_colors, colored_writes, tile_bytes = [], [], []
    # Existing vm() already records OUT. This hook only models the hardware
    # color latch independently, with four successive writes per tile.
    from unicorn.x86_const import UC_X86_INS_OUT

    def out(machine, port, size, value, _):
        assert port == 0x7E and size == 1
        tile_bytes.append(value)
        if len(tile_bytes) % 4 == 0:
            tile_colors.append(sum(bool(v) << p for p, v in enumerate(tile_bytes[-4:])))

    def colored(machine, access, at, size, value, _):
        if VRAM <= at < VRAM + 32768:
            color = tile_colors[-1] if mode == "tiny" else (15 if mode == "top" else 9)
            colored_writes.append((at - VRAM, size, value, color))

    u.hook_add(unicorn.UC_HOOK_INSN, out, None, 1, 0, UC_X86_INS_OUT)
    u.hook_add(UC_HOOK_MEM_WRITE, colored)
    return u, finish, put


def initial_planes():
    return list(map(bytearray, INITIAL))


def pixel(planes, x, y, color):
    at, bit = (y % 400) * 80 + x // 8, 128 >> (x & 7)
    for p, plane in enumerate(planes):
        plane[at] = (plane[at] & ~bit) | (bit if color & (1 << p) else 0)


def tiny_pattern(width, kind):
    rng = random.Random(1235 + width + kind)
    layers = []
    for color in (15, 9, 6):
        data = bytes((0 if kind == 0 else 255 if kind == 1 else rng.randrange(256))
                     for _ in range(width * width // 8))
        layers.append((color, data))
    return layers, b"".join(bytes((0x80, color)) + data for color, data in layers) + b"\0\0"


def tiny_expected(width, left, top, layers):
    planes = initial_planes()
    for color, data in layers:
        for y in range(width):
            for x in range(width):
                if data[y * (width // 8) + x // 8] & (128 >> (x & 7)):
                    pixel(planes, left + x, top + y, color)
    return b"".join(map(bytes, planes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists() or not out.is_relative_to(ROOT / ".analysis"):
        parser.error("output must be a new private directory")
    products = {name: product(path / "MAIN.EXE", path / "build.json")
                for name, path in (("before", args.baseline_dir), ("after", args.build_dir))}
    results = []
    for width in (16, 32):
        for kind in (0, 1, 2):
            layers, source = tiny_pattern(width, kind)
            for shift in range(8):
                for odd in (0, 1):
                    for top in (0, 400 - width, 400 - width + 1, 399):
                        left = 32 + odd * 8 + shift
                        expected = tiny_expected(width, left, top, layers)
                        row = dict(kind="tiny",width=width,mask_kind=kind,left=left,top=top)
                        actual = []
                        for name, prod in products.items():
                            u, run, put = mask_vm(prod, f"Z_SUPER_ROLL_PUT_TINY_{width}X{width}_RAW", b"\0\0")
                            put("_super_patdata", struct.pack("<H", 0xB000))
                            u.mem_write(0xB0000, source)
                            u.reg_write(UC_X86_REG_AX, left)
                            u.reg_write(UC_X86_REG_DX, top)
                            instructions, ports, writes, planes = run()
                            assert planes == expected, (name, row)
                            actual.append((ports, writes))
                            row[name + "_instructions"] = instructions
                        assert actual[0] == actual[1], row
                        results.append(row)
    # Exercise every scroll row and sub-byte shift with both full pellet
    # passes. The bottom service deliberately repeats its first source word.
    for shift in range(8):
        for top in range(400):
            row = dict(kind="pellet",left=32+shift,top=top)
            actual = []
            expected_list = None
            for name, prod in products.items():
                u, run, put = mask_vm(prod, "_pellets_render_top", near=False, mode="top")
                put("_pellets_render_count", struct.pack("<H",1))
                put("_pellets_render", struct.pack("<hh",32+shift,top))
                source = bytes(u.mem_read(address(prod,"_sPELLET") + shift*16, 12))
                planes = initial_planes()
                for y in range(6):
                    for x in range(16 if shift else 8):
                        if source[y*2+x//8] & (128>>(x&7)):
                            pixel(planes,32+x,top+y,15)
                instructions, ports, writes, screen = run()
                assert screen == b"".join(map(bytes,planes)), (name,row,"top")
                bottom = bytes(u.mem_read(address(prod,"_pellets_render"),4))
                sprite = (prod["entries"]["_sPELLET_BOTTOM"][1] + shift*8) & 65535
                expected_list = struct.pack("<HH", ((top+3)%400)*80+4, sprite)
                assert bottom == expected_list, (name,row,bottom.hex(),expected_list.hex())
                u2, run2, put2 = mask_vm(prod,"_pellets_render_bottom",near=False,mode="bottom")
                put2("_pellets_render_count",struct.pack("<H",1))
                put2("_pellets_render",bottom)
                source = bytes(u2.mem_read(address(prod,"_sPELLET_BOTTOM") + shift*8,8))
                planes = initial_planes()
                for y, source_y in enumerate((0,0,1,2,3)):
                    for x in range(16):
                        if source[source_y*2+x//8] & (128>>(x&7)):
                            pixel(planes,32+x,top+3+y,9)
                instructions2, ports2, writes2, screen2 = run2()
                assert screen2 == b"".join(map(bytes,planes)), (name,row,"bottom")
                actual.append((ports,writes,ports2,writes2))
                row[name+"_instructions"] = instructions+instructions2
            assert actual[0] == actual[1], row
            results.append(row)
    # Execute the complete update and renderer, not a loop around a stand-in.
    # Geometry keeps the player away from the seeded stationary pool so this
    # isolates update/render and its Lunatic policy from HUD/graze side effects.
    for count in (0,60,120,240,440):
        for clouds in (False,True):
            for turbo in (0,1):
                row = dict(kind="pool",count=count,clouds=clouds,turbo=turbo,rank=3)
                actual = []
                for name, prod in products.items():
                    u, run, put = vm(prod,"bullets_update()",b"")
                    pool = bytearray(STRIDE*(PELLETS+REGULAR))
                    for i in range(count):
                        at = i*STRIDE
                        pool[at] = 1
                        struct.pack_into("<hh",pool,at+2,(32+(i*13)%300)*16,(32+(i*7)%240)*16)
                        pool[at+18],pool[at+19] = (4 if clouds and i>=PELLETS else 1),2
                        struct.pack_into("<H",pool,at+24,0)
                    put("_bullets",bytes(pool))
                    put("_player_pos",struct.pack("<hh",180*16,350*16))
                    put("_player_invincibility_time",b"\x01")
                    put("_bullet_zap",b"\0\0")
                    put("_bullet_clear_time",b"\0")
                    put("_rank",b"\x03")
                    put("_playperf",b"\x00")
                    put("_turbo_mode",bytes((turbo,)))
                    put("_stage_frame_mod2",b"\0")
                    put("_scroll_line",b"\0\0")
                    put("_slowdown_factor",b"\x01\0")
                    instructions, ports = run()
                    assert not ports
                    updated = bytes(u.mem_read(address(prod,"_bullets"),len(pool)))
                    render_count = bytes(u.mem_read(address(prod,"_pellets_render_count"),2))
                    render_list = bytes(u.mem_read(address(prod,"_pellets_render"),PELLETS*4))
                    slowdown = bytes(u.mem_read(address(prod,"_slowdown_factor"),2))
                    assert int.from_bytes(render_count,"little") == min(count,PELLETS)
                    assert int.from_bytes(slowdown,"little") == (2 if not turbo and count>=48 else 1)
                    row[name+"_update_instructions"] = instructions
                    # GRCG direct color service and full renderer share near CS.
                    ur, runr, putr = vm(prod,"BULLETS_RENDER",b"",near=True)
                    ur.reg_write(UC_X86_REG_ES,0xA800)
                    for symbol,data in (("_bullets",updated),("_pellets_render",render_list),
                                        ("_pellets_render_count",render_count),("_bullet_zap",b"\0\0"),
                                        ("_bullet_clear_time",b"\0"),("_scroll_line",b"\0\0")):
                        putr(symbol,data)
                    # Valid synthetic tiny patterns for both regular/cloud
                    # sizes; real resource timing is measured separately.
                    _, source16 = tiny_pattern(16,2)
                    _, source32 = tiny_pattern(32,2)
                    ur.mem_write(0xB0000,source16)
                    ur.mem_write(0xB1000,source32)
                    putr("_super_patdata",struct.pack("<H",0xB100)*512)
                    putr("_super_patdata",struct.pack("<H",0xB000))
                    instructions_r,ports_r = runr()
                    row[name+"_render_instructions"] = instructions_r
                    actual.append((updated,render_list,render_count,slowdown,ports_r,
                                   bytes(ur.mem_read(VRAM,32768))))
                assert actual[0] == actual[1], row
                results.append(row)
    engine = Path(unicorn.unicorn._uc._name).resolve()
    report = dict(observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,
                  script_sha256=sha(Path(__file__)),unicorn_engine_sha256=sha(engine),
                  load_segment=LOAD,pool=dict(pellets=PELLETS,regular=REGULAR,stride=STRIDE),
                  products={k:{f:v[f] for f in ("exe_sha256","map_sha256")} for k,v in products.items()},
                  passed=True,results=results)
    out.mkdir(parents=True)
    (out/"receipt.json").write_text(json.dumps(report,indent=2)+"\n")
    print(f"PASS {len(results)} bullet pixel/ordered-I/O/maximum-pool controls")


if __name__ == "__main__":
    main()
