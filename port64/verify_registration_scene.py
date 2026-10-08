#!/usr/bin/env python3
"""Execute original palette fades and compare the native registration clock.

Full original fade instructions run at two loads; VBlank and palette output
are explicit adapters. This is a refresh contract, not physical PC-98 timing.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import subprocess

from unicorn.x86_const import *
from verify_congratulations import Original
from verify import source_manifest

sha = lambda b: hashlib.sha256(b).hexdigest()


def fade(original, start, speed):
    u = original.u
    u.mem_write(original.load * 16, original.module)
    u.mem_write(original.ds * 16, original.data)
    original.clock = 0
    original.clock_mode = True
    original.previous_tone = -1
    original.palette = []
    original.events = []
    original.flow = []
    original.error = None
    original.done = False
    for reg, value in (
        (UC_X86_REG_CS, original.load), (UC_X86_REG_DS, original.ds),
        (UC_X86_REG_ES, 0), (UC_X86_REG_SS, 0x7000),
        (UC_X86_REG_SP, 0xf000), (UC_X86_REG_BP, 0), (UC_X86_REG_EFLAGS, 2),
    ):
        u.reg_write(reg, value)
    u.mem_write(0x7f000, struct.pack("<HHH", 0xff00, original.cs, speed))
    u.emu_start(original.load * 16 + start, 0x10ffff, count=100000)
    if original.error:
        raise RuntimeError("original fade adapter rejected") from original.error
    assert original.done and u.reg_read(UC_X86_REG_SP) == 0xf006
    assert len(original.palette) == 18
    return original.clock, [tuple(map(int, row.split()[1:])) for row in original.palette]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("target", "decoded-dir", "exe", "output-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--runner")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists():
        raise ValueError("use a fresh output directory")
    out.mkdir(parents=True)
    references = []
    for load in (0x1000, 0x2000):
        original = Original(args.target, args.decoded_dir, load)
        references.append({
            "IN": fade(original, 0x622, 2),
            "OUT": fade(original, 0x666, 1),
        })
    assert references[0] == references[1], "load metamorphism changed palette clock"
    command = ([args.runner] if args.runner else []) + [str(args.exe.resolve()), "--fade-clock"]
    native = subprocess.check_output(command, timeout=60).decode().splitlines()
    (out / "native.txt").write_text("\n".join(native) + "\n")
    expected = []
    for kind in ("IN", "OUT"):
        count, palette = references[0][kind]
        tone = 0 if kind == "IN" else 100
        index = 0
        for tick in range(1, count + 1):
            while index < len(palette) and palette[index][0] <= tick:
                tone = palette[index][1]
                index += 1
            expected.append(f"{kind} {tick} {tone}")
    assert native == expected, "native registration palette refresh schedule differs"
    receipt = dict(
        passed=True, observed_utc=datetime.now(timezone.utc).isoformat(),
        source_manifest=source_manifest(Path(__file__).resolve().parents[1])[0],
        target_sha256=sha(args.target.read_bytes()), executable_sha256=sha(args.exe.read_bytes()),
        fade_extent=dict(artifact="th04-maine",segment="decoded relative 0000",
                         start="0x0622",end="0x06A3",sha256=sha(original.module[0x622:0x6a3])),
        load_segments=[0x1000, 0x2000], controls=references[0],
        trace_sha256=sha(("\n".join(expected) + "\n").encode()),
        scope="Original palette-black-in(2)/out(1) CPU bodies and VBlank/palette adapters. "
              "Host save/graphics/input integration has separate controls; no physical timing or exact claim.",
    )
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("Original registration fade clocks PASS: two loads, 35+18 refreshes")


if __name__ == "__main__":
    main()
