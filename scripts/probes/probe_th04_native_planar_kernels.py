#!/usr/bin/env python3
"""Compare complete planar draw calls with independent scalar pixel models.

Synthetic ordinary RAM replaces VRAM. Instruction counts describe the bounded
CPU calls, not emulated PC-98 frame times or Windows hardware performance.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import struct
import sys

import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_INSN
from unicorn.x86_const import (
    UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS,
    UC_X86_REG_SP, UC_X86_REG_SI, UC_X86_REG_DI, UC_X86_REG_BP,
    UC_X86_REG_EFLAGS, UC_X86_INS_OUT,
)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402

LOAD = 0x2000
PLANES = (0x7000, 0x8000, 0x9000, 0xA000)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def product(exe, manifest):
    record = json.loads(manifest.read_text())["products"]["main"]
    assert sha(exe) == record["sha256"]
    receipt = Path(record["build_receipt"])
    link = json.loads(receipt.read_text())["link"]
    map_path = receipt.parent / "source" / link["map"]
    assert sha(map_path) == link["map_sha256"]
    entries = {}
    for line in map_path.read_text().splitlines():
        m = re.match(r"^\s*([\dA-Fa-f]{4}):([\dA-Fa-f]{4})\s+(?:idle\s+)?(.*)$", line)
        if m:
            entries[m[3]] = (int(m[1], 16), int(m[2], 16))
    blob = exe.read_bytes()
    assert parse_mz(blob).valid
    header = struct.unpack_from("<H", blob, 8)[0] * 16
    module = bytearray(blob[header:])
    reloc_count, reloc_table = struct.unpack_from("<H", blob, 6)[0], struct.unpack_from("<H", blob, 24)[0]
    for at in range(reloc_count):
        offset, segment = struct.unpack_from("<HH", blob, reloc_table + at * 4)
        site = segment * 16 + offset
        struct.pack_into("<H", module, site, (struct.unpack_from("<H", module, site)[0] + LOAD) & 65535)
    return dict(module=bytes(module),entries=entries,exe_sha256=sha(exe),map_sha256=sha(map_path))


def vm(prod, entry, args, flags=2, near=False):
    u = Uc(UC_ARCH_X86, UC_MODE_16)
    u.mem_map(0, 0x100000)
    u.mem_write(LOAD * 16, prod["module"])
    ds = LOAD + prod["entries"]["_VRAM_PLANE_B"][0]
    for reg, value in (
        (UC_X86_REG_DS, ds), (UC_X86_REG_ES, 0x1234),
        (UC_X86_REG_SS, 0x6000), (UC_X86_REG_SP, 0xE000),
        (UC_X86_REG_SI, 0x1357), (UC_X86_REG_DI, 0x2468),
        (UC_X86_REG_BP, 0xACE0), (UC_X86_REG_EFLAGS, flags),
    ):
        u.reg_write(reg, value)
    segment, offset = prod["entries"][entry]
    return_address = ((LOAD+segment)*16+0xFF00) if near else 0x60100
    frame = struct.pack("<H",0xFF00) if near else struct.pack("<HH",0x100,0x6000)
    u.mem_write(0x6E000, frame + args)
    u.reg_write(UC_X86_REG_CS, LOAD + segment)
    counts, ports = [0], []

    def step(machine, address, size, _):
        counts[0] += 1
        if address == return_address:
            machine.emu_stop()

    u.hook_add(UC_HOOK_CODE, step)
    u.hook_add(UC_HOOK_INSN, lambda machine, port, size, value, _: ports.append([port,size,value]), None, 1, 0, UC_X86_INS_OUT)

    def run():
        u.emu_start((LOAD + segment) * 16 + offset, return_address+1, count=10000000)
        assert u.reg_read(UC_X86_REG_CS) == ((LOAD+segment) if near else 0x6000)
        assert u.reg_read(UC_X86_REG_SP) == 0xE000 + len(frame) + len(args)
        for reg, value in ((UC_X86_REG_DS,ds),(UC_X86_REG_SI,0x1357),
                           (UC_X86_REG_DI,0x2468),(UC_X86_REG_BP,0xACE0)):
            assert u.reg_read(reg) == value
        return counts[0], ports

    def put(symbol, data):
        s, o = prod["entries"][symbol]
        u.mem_write((LOAD + s) * 16 + o, data)

    for symbol, plane in zip(("_VRAM_PLANE_B","_VRAM_PLANE_R","_VRAM_PLANE_G","_VRAM_PLANE_E"), PLANES):
        put(symbol, struct.pack("<HH", 0, plane))
    return u, run, put


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--baseline-manifest", required=True, type=Path)
    parser.add_argument("--baseline-exe", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists() or not out.is_relative_to(ROOT / ".analysis"):
        parser.error("output must be a new private directory")
    products = {"before":product(args.baseline_exe,args.baseline_manifest),
                "after":product(args.build_dir / "MAIN.EXE",args.build_dir / "build.json")}
    assert {"TH04_COPY_WORDS", "TH04_SPRITE_UNCLIPPED"} <= products["after"]["entries"].keys()
    results = []
    cases = [(w,32,64+shift,20,seed) for w in (1,2,3,4,8,31,32)
             for shift in range(8) for seed in (0,1,2)]
    cases += [(2,16,-5,-3,2),(4,32,635,392,2),(4,32,-100,20,2),
              (4,32,0,400,2),(32,255,0,0,2),(0,16,0,0,2),(4,0,0,0,2),
              (2,16,623,384,2),(4,32,607,368,2),(4,32,608,368,2),
              (31,32,391,368,2),(32,255,383,145,2),(1,1,631,399,2),
              (0,0,0,0,2)]
    for w,h,left,top,seed in cases:
        rng = random.Random(1232+w*17+seed)
        stride = w*h
        source = bytearray(rng.randrange(256) for _ in range(stride*5))
        if seed < 2:
            source[:stride] = bytes([255 if seed else 0])*stride
        initial = [bytes((x*37+p*13)&255 for x in range(32768)) for p in range(4)]
        expected = [bytearray(x) for x in initial]
        for y in range(h):
            for x in range(w*8):
                sx,sy = left+x,top+y
                if not (0<=sx<640 and 0<=sy<400):
                    continue
                at,bit = y*w+x//8,128>>(x&7)
                if not source[at]&bit:
                    continue
                dest,dbit = sy*80+sx//8,128>>(sx&7)
                for p in range(4):
                    expected[p][dest] = (expected[p][dest]&~dbit) | (dbit if source[(p+1)*stride+at]&bit else 0)
        row = dict(kind="sprite",width_bytes=w,height=h,left=left,top=top,alpha_kind=seed)
        for name,prod in products.items():
            u,run,put = vm(prod,"SUPER_PUT",struct.pack("<Hhh",0,top,left))
            put("_super_patnum",struct.pack("<H",1))
            put("_super_patdata",struct.pack("<H",0xB000))
            put("_super_patsize",struct.pack("<H",(w<<8)|h))
            if source:
                u.mem_write(0xB0000,bytes(source))
            for seg,data in zip(PLANES,initial):
                u.mem_write(seg*16,data)
            instructions,ports = run()
            for seg,data in zip(PLANES,expected):
                assert bytes(u.mem_read(seg*16,32768)) == bytes(data), (name,row,seg)
            assert ports == ([[0x7C,1,0]] if (w or h) else [])
            row[name+"_instructions"] = instructions
        results.append(row)
    # Execute the actual near Yuuka entity renderer with 1..31 live crosses.
    # Synthetic sprite planes isolate drawing cost from AI, IRQ and VRAM timing.
    for count in (1,8,16,31):
        rng = random.Random(6006)
        source = bytes(rng.randrange(256) for _ in range(4*32*5))
        images = []
        row = dict(kind="yuuka_crosses",count=count)
        for name,prod in products.items():
            u,run,put = vm(prod,"_yuuka6_entities_render",b"",near=True)
            put("_super_patnum",struct.pack("<H",512))
            put("_super_patdata",struct.pack("<H",0xB000)*512)
            put("_super_patsize",struct.pack("<H",0x0420)*512)
            u.mem_write(0xB0000,source)
            entities = bytearray(26*32)
            for i in range(count):
                entities[i*26] = 1
                struct.pack_into("<hh",entities,i*26+2,(64+i*11-16)*16,(40+i*7)*16)
                struct.pack_into("<H",entities,i*26+14,i*2)
            put("_custom_entities",bytes(entities))
            for p,seg in enumerate(PLANES):
                u.mem_write(seg*16,bytes((x*37+p*13)&255 for x in range(32768)))
            instructions,ports = run()
            assert ports == [[0x7C,1,0]]*count
            images.append(b"".join(bytes(u.mem_read(seg*16,32768)) for seg in PLANES))
            row[name+"_instructions"] = instructions
        assert images[0] == images[1]
        row["planes_sha256"] = hashlib.sha256(images[1]).hexdigest()
        results.append(row)
    packed_cases = [(0,0,16,seed) for seed in range(256)]
    packed_cases += [(0,400,640,37),(-8,0,16,81),(632,399,16,193),
                     (640,0,16,1),(7,0,16,2),(0,0,7,3)]
    for left,top,length,seed in packed_cases:
        source = bytes((seed+x*37)&255 for x in range(max(4,(length//8)*4)))
        initial = [bytes((x*37+p*13)&255 for x in range(32768)) for p in range(4)]
        expected = [bytearray(x) for x in initial]
        for byte in range(length//8):
            dst_x = (left>>3)+byte
            if not 0<=dst_x<80:
                continue
            for p in range(4):
                bits = 0
                for pixel in range(8):
                    pair = source[byte*4+pixel//2]
                    color = (pair&15) if pixel&1 else pair>>4
                    if color&(1<<p):
                        bits |= 128>>pixel
                expected[p][top*80+dst_x] = bits
        row = dict(kind="packed",left=left,top=top,pixels=length,seed=seed)
        for name,prod in products.items():
            u,run,_ = vm(prod,"GRAPH_PACK_PUT_8_NOCLIP",struct.pack("<HHHhh",length,0,0xB000,top,left))
            u.mem_write(0xB0000,source)
            for seg,data in zip(PLANES,initial):
                u.mem_write(seg*16,data)
            instructions,ports = run()
            assert not ports
            for seg,data in zip(PLANES,expected):
                assert bytes(u.mem_read(seg*16,32768)) == bytes(data), (name,row,seg)
            row[name+"_instructions"] = instructions
        results.append(row)
    for words in (0,1,2,3,15999,16000):
        for direction in (0,0x400):
            u,run,_ = vm(products["after"],"TH04_COPY_WORDS",struct.pack("<HHHHH",words,0x100,0xB000,0x100,0x7000),2|direction)
            data = bytes((x*31)&255 for x in range(words*2))
            u.mem_write(0xB0100, data or b"\0")
            u.mem_write(0x700FC,b"\xA5"*(words*2+8))
            instructions,_ = run()
            assert bytes(u.mem_read(0x70100,words*2)) == data
            assert bytes(u.mem_read(0x700FC,4)) == b"\xA5"*4
            assert bytes(u.mem_read(0x70100+words*2,4)) == b"\xA5"*4
            assert u.reg_read(UC_X86_REG_EFLAGS)&0x400 == direction
            results.append(dict(kind="copy",words=words,direction_flag=direction,instructions=instructions))
    engine = Path(unicorn.unicorn._uc._name).resolve()
    report = dict(observed_utc=datetime.now(timezone.utc).isoformat(),
                  scope=__doc__,script_sha256=sha(Path(__file__)),
                  unicorn_engine_sha256=sha(engine),load_segment=LOAD,
                  products={k:{f:v[f] for f in ("exe_sha256","map_sha256")} for k,v in products.items()},
                  passed=True,results=results)
    out.mkdir(parents=True)
    (out / "receipt.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(dict(passed=True,cases=len(results),receipt=str(out / "receipt.json"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
