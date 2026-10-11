#!/usr/bin/env python3
"""Compare original filled-circle calls and visible HLINE/circle write masks."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
import unicorn as u
from unicorn.x86_const import (
    UC_X86_REG_BP, UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_EFLAGS,
    UC_X86_REG_IP, UC_X86_REG_SI, UC_X86_REG_DI, UC_X86_REG_SP, UC_X86_REG_SS,
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def configured():
    radii = (0, 1, 2, 8, 16, 64, 180, 511, 512, 513, 1024, 16383,
             16384, 32767, 32768, 32769, 49152, 65534, 65535)
    requests = [(224, 200, r) for r in radii]
    requests += [(x, y, r) for x, y, r in itertools.product(
        (-32768, 32767), (-32768, 32767), (0, 513, 32768, 65535))]
    edges = (-32768, -32767, -1, 0, 31, 32, 33, 414, 415, 416, 32767)
    hlines = list(itertools.product(edges, edges, (15, 16, 200, 383, 384)))
    discs = [(224, 200, r) for r in (0, 1, 16, 180, 511, 512, 513, 1024)]
    discs += [(x, y, r) for x, y, r in itertools.product(
        (-32768, 32767), (16, 383), (0, 1, 513))]
    return [('requests', requests), ('hline', hlines), ('disc', discs)]


class Original:
    def __init__(self, record):
        body = bytearray(record['body'])
        self.pins = record['pins']
        assert sha(body[0x114c:0x11e2]) == '154cdc0fe014eb077dd8e25da4d1532c001c753775d4939d3f161d0d32d01bd7'
        self.loaded = 0x1000
        for site in record['sites']:
            word = struct.unpack_from('<H', body, site)[0]
            struct.pack_into('<H', body, site, (word + self.loaded) & 65535)
        self.cpu = u.Uc(u.UC_ARCH_X86, u.UC_MODE_16)
        self.cpu.mem_map(0, 0x100000)
        self.cpu.mem_write(self.loaded * 16, bytes(body))
        self.capture = False
        self.requests = bytearray()
        self.mask = bytearray(32000)
        self.error = None
        for ip in (0x14dc, 0x1700):
            at = self.loaded * 16 + ip
            self.cpu.hook_add(u.UC_HOOK_CODE, self.callee, None, at, at)
        self.cpu.hook_add(u.UC_HOOK_MEM_WRITE, self.write, None, 0xa8000, 0xafcff)
        # The existing stage clip is an explicit input. Its EDGES masks are
        # actual original DGROUP data, read by the unmodified HLINE callee.
        self.cpu.mem_write(0x31340 + 0x32c, struct.pack('<7H', 32, 383, 415, 16, 367, 383, 0xa850))

    def callee(self, cpu, address, size, _):
        if not self.capture:
            return
        try:
            point = address == self.loaded * 16 + 0x1700
            sp = cpu.reg_read(UC_X86_REG_SP)
            if point:
                y, left = struct.unpack('<2h', cpu.mem_read(0x70000 + sp + 4, 4))
                right = left
            else:
                y, right, left = struct.unpack('<3h', cpu.mem_read(0x70000 + sp + 4, 6))
            self.requests.extend(struct.pack('<B3h', int(not point), left, right, y))
            ip, cs = struct.unpack('<2H', cpu.mem_read(0x70000 + sp, 4))
            cpu.reg_write(UC_X86_REG_SP, sp + (8 if point else 10))
            cpu.reg_write(UC_X86_REG_CS, cs)
            cpu.reg_write(UC_X86_REG_IP, ip)
        except Exception as error:
            self.error = error
            cpu.emu_stop()

    def write(self, cpu, access, address, size, value, _):
        try:
            if self.capture:
                raise ValueError('intercepted circle unexpectedly wrote VRAM')
            for byte in range(size):
                at = address - 0xa8000 + byte
                if not 0 <= at < 32000:
                    raise ValueError('GRCG write exceeds visible mask')
                self.mask[at] |= (value >> (byte * 8)) & 255
        except Exception as error:
            self.error = error
            cpu.emu_stop()

    def call(self, mode, row):
        self.capture = mode == 'requests'
        self.requests.clear()
        self.mask[:] = bytes(32000)
        self.error = None
        x, y, radius = row
        args = (radius, y, x)
        # HLINE input rows are left/right/y; Pascal pushes left then right
        # then y. Circle input rows are x/y/radius in the same stack order.
        entry = 0x14dc if mode == 'hline' else 0x114c
        for register, value in ((UC_X86_REG_CS, self.loaded), (UC_X86_REG_DS, 0x3134),
                                (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xff00),
                                (UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1234),
                                (UC_X86_REG_DI, 0x5678), (UC_X86_REG_EFLAGS, 2)):
            self.cpu.reg_write(register, value)
        self.cpu.mem_write(0x7ff00, struct.pack('<5H', 0x8000, self.loaded, *(n & 65535 for n in args)))
        self.cpu.emu_start(self.loaded * 16 + entry, self.loaded * 16 + 0x8000, count=6000000)
        if self.error:
            raise RuntimeError('GRCG original callback failed') from self.error
        assert self.cpu.reg_read(UC_X86_REG_IP) == 0x8000
        assert self.cpu.reg_read(UC_X86_REG_SP) == 0xff0a
        assert self.cpu.reg_read(UC_X86_REG_BP) == 0xabcd
        if mode != 'hline':
            assert self.cpu.reg_read(UC_X86_REG_SI) == 0x1234
        assert self.cpu.reg_read(UC_X86_REG_DI) == 0x5678
        return bytes(self.requests if self.capture else self.mask)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.root.resolve() / 'scripts/runtime'))
    from verify_dos_vsync_lifecycle import original
    record = original('main')
    oracle = Original(record)
    args.output.mkdir(parents=True, exist_ok=False)
    controls = {}
    for mode, rows in configured():
        fixture = args.output / (mode + '.txt')
        fixture.write_text(''.join(' '.join(map(str, row)) + '\n' for row in rows))
        command = [str(args.native.resolve()), '--' + mode, str(fixture.resolve())]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        results = []
        try:
            with gzip.open(args.output / (mode + '-original.bin.gz'), 'wb') as stream:
                for index, row in enumerate(rows):
                    expected = oracle.call(mode, row)
                    if mode == 'requests':
                        header = process.stdout.read(4)
                        assert len(header) == 4 and struct.unpack('<I', header)[0] * 7 == len(expected)
                    actual = process.stdout.read(len(expected))
                    stream.write(struct.pack('<I', len(expected)) + expected)
                    assert actual == expected, (mode, index, row)
                    results.append(dict(input=row,bytes=len(expected),sha256=sha(expected)))
            assert not process.stdout.read(1)
            assert process.wait(timeout=30) == 0 and not process.stderr.read()
        except BaseException:
            process.kill()
            process.wait(timeout=30)
            raise
        controls[mode] = results
        print(mode, len(rows), 'PASS', flush=True)
    source = Path(__file__).resolve().parent
    receipt = dict(passed=True, original=record['pins'], load='1000', dgroup='3134',
                   circle_entry='0000:114C', hline_entry='0000:14DC', pset_entry='0000:1700',
                   native_sha256=sha(args.native.read_bytes()), controls=controls,
                   source={n:sha((source/n).read_bytes()) for n in (
                       'grcg_raster.cpp','grcg_raster.hpp','grcg_raster_contracts.cpp',
                       'yuuka5_render.cpp','motion.cpp','motion.hpp','CMakeLists.txt','verify_grcg_raster.py')},
                   files={p.name:sha(p.read_bytes()) for p in args.output.iterdir()})
    (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
