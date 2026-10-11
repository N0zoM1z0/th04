#!/usr/bin/env python3
"""Compare native angles with relocated original MAIN IATAN2 instructions."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import unicorn as u
from unicorn.x86_const import (
    UC_X86_REG_AX, UC_X86_REG_BP, UC_X86_REG_CS, UC_X86_REG_DS,
    UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_EFLAGS,
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def vectors():
    # Every possible other coordinate when either displacement is INT16_MIN.
    for n in range(-32768, 32768):
        yield (0, 0, -32768, n)
        yield (0, 0, n, -32768)
    # Whole signed-width ordinary axes/diagonal samples and nonzero origins.
    for n in range(-32767, 32768, 7):
        for x, y in ((n, 0), (0, n), (n, n), (n, -n)):
            yield (0, 0, x, y)
    rng = random.Random(1402)
    for _ in range(16384):
        yield tuple(rng.randrange(-32768, 32768) for _ in range(4))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / 'scripts/runtime'))
    from verify_dos_vsync_lifecycle import original
    target = original('main')  # Pinned MZ identity and all 1136 relocations.
    body = bytearray(target['body'])
    assert digest(body[0x1da8:0x1e14]) == 'd9bb0f779ed2fd28b4eb0926dd74112de3964e4d5aa67690be87b757cd1b4e06'
    table = bytes(body[0x2155e:0x2165e])
    assert digest(table) == 'cc502dcf07b43ece1e8d711b5ca5a3677c130dc688db176f76dbd3c2b362b754'
    args.output.mkdir(parents=True, exist_ok=False)
    load = 0x1000
    for site in target['sites']:
        word = struct.unpack_from('<H', body, site)[0]
        struct.pack_into('<H', body, site, (word + load) & 65535)
    fault = [False]

    def interrupt(uc, number, _):
        assert number == 0, number
        fault[0] = True
        uc.emu_stop()

    def machine():
        uc = u.Uc(u.UC_ARCH_X86, u.UC_MODE_16)
        uc.mem_map(0, 0x100000)
        uc.mem_write(load * 16, bytes(body))
        uc.hook_add(u.UC_HOOK_INTR, interrupt)
        return uc

    emulator = machine()
    rows = list(vectors())
    input_text = ''.join(' '.join(map(str, row)) + '\n' for row in rows)
    result = subprocess.run([str(args.native.resolve()), '--angle-vectors'],
                            input=input_text, text=True, capture_output=True, check=True)
    observed = result.stdout.splitlines()
    assert len(observed) == len(rows) and not result.stderr
    faults = 0
    transcript = args.output / 'comparisons.txt.gz'
    with gzip.open(transcript, 'wt') as stream:
        for index, ((fx, fy, tx, ty), native) in enumerate(zip(rows, observed)):
            x = ((tx - fx + 32768) & 65535) - 32768
            y = ((ty - fy + 32768) & 65535) - 32768
            fault[0] = False
            for register, value in ((UC_X86_REG_CS, load), (UC_X86_REG_DS, load + 0x2134),
                                    (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xff00),
                                    (UC_X86_REG_BP, 0xabcd), (UC_X86_REG_EFLAGS, 2)):
                emulator.reg_write(register, value)
            emulator.mem_write(0x7ff00, struct.pack('<4H', 0x8000, load, x & 65535, y & 65535))
            emulator.emu_start(load * 16 + 0x1da8, load * 16 + 0x8000, count=80)
            if fault[0]:
                expected = 'divide-error'
                faults += 1
                # Unicorn retains pending exception delivery after emu_stop
                # in an interrupt hook. Give the next call a fresh CPU.
                emulator = machine()
            else:
                assert emulator.reg_read(UC_X86_REG_SP) == 0xff08
                assert emulator.reg_read(UC_X86_REG_BP) == 0xabcd
                expected = str(emulator.reg_read(UC_X86_REG_AX))
            stream.write(f'{index} {fx} {fy} {tx} {ty} {expected} {native}\n')
            assert native == expected, (index, rows[index], expected, native)
    source = Path(__file__).resolve().parent
    paths = [source / n for n in ('motion.cpp', 'motion.hpp', 'motion_tables.hpp',
                                 'motion_contracts.cpp', 'verify_motion.py', 'CMakeLists.txt')]
    receipt = dict(passed=True, cases=len(rows), divide_errors=faults,
                   original=target['pins'], load_segment=hex(load),
                   entry='0000:1DA8', table='2134:021E',
                   native_sha256=digest(args.native.read_bytes()),
                   source={p.name: digest(p.read_bytes()) for p in paths},
                   comparisons_sha256=digest(transcript.read_bytes()))
    (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'IATAN2 PASS {len(rows)} vectors, {faults} original DIV faults')


if __name__ == '__main__':
    main()
