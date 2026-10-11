#!/usr/bin/env python3
"""Compare Gaiji character/string writes with original MAINE instructions."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess

from verify_font_address import FontOriginal, PACKED_SHA, PAYLOAD_SHA
from unicorn.x86_const import (
    UC_X86_REG_BP, UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_EFLAGS,
    UC_X86_REG_SP, UC_X86_REG_SS, UC_X86_REG_SI, UC_X86_REG_DI,
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def configured():
    rows = [('putc', 80 + shift, 32, 0, (glyph + shift) & 15, 3,
             (glyph % 3) * 17, f'{glyph:02x}')
            for glyph, shift in itertools.product(range(256), range(8))]
    edges = ((640, 0), (639, 0), (-8, 0), (-1, 0), (-32768, 0), (32767, 0),
             (0, 399), (0, 400), (0, 1023), (0, 1024), (0, 4096),
             (120, 819), (127, 819), (-8, 819), (0, -1), (0, -32768),
             (0, 32767), (639, 1023), (-8, 4096), (32767, -32768))
    rows += [('putc', x, y, 0, 5, 11, 17, f'{glyph:02x}')
             for (x, y), glyph in itertools.product(edges, (0, 1, 127, 128, 255))]
    rows += [('puts', x, y, step, 5, 11, 34, text)
             for x, y, step, text in itertools.product(
                 (-8, 0, 7, 80, 639, 640, 32767), (32, 819),
                 (-32768, -1, 0, 1, 7, 8, 15, 16, 17, 255, 32767, 65535),
                 ('01027f80ff', 'fffe01808203', '010002', '-'))]
    all_codes = bytes(range(1, 256)).hex()
    rows += [('puts', x, y, step, 15, 7, 65535, all_codes)
             for x, y, step in itertools.product((-8, 639), (0, 819), (16, -1))]
    rows += [('puts', 640, 0, 16, color, 7, 0, '0180ff')
             for color in (0, 5, 15, 256, 65535)]
    return rows


class GaijiOriginal(FontOriginal):
    def body(self, cpu, address):
        cs = cpu.reg_read(UC_X86_REG_CS)
        if self.font_mode and cs == self.load and 0x36b6 <= address-cs*16 < 0x37f3:
            return
        super().body(cpu, address)

    @staticmethod
    def rom(cell, column, selector):
        assert column in (0x56, 0x57), (cell, column, selector)
        glyph = cell + (column - 0x56) * 128
        half = 0 if selector & 0x20 else 1
        return (glyph * 17 + (selector & 15) * 29 + half * 113 + 7) & 255

    def draw(self, row):
        kind, x, y, step, color, seed, padding, text = row
        raw = bytes.fromhex(text) if text != '-' else b''
        self.u.mem_write(self.load * 16, self.module)
        self.u.mem_write(self.ds * 16, self.data)
        self.u.mem_write(0xa8000, bytes(65537))
        self.u.mem_write(self.ds * 16 + 0x4000, raw + b'\0')
        self.write(0x11c, 'H', 0xa800)
        self.font_mode = True
        self.font_rows = []
        self.font_row = self.font_cell = self.font_column = 0
        self.font_rom = self.rom
        self.font_color = color
        self.font_pixels = bytearray(bytes((at * 73 + seed) & 15 for at in range(16)) * 16000)
        self.error = None
        self.done = False
        for reg, value in ((UC_X86_REG_CS, self.load), (UC_X86_REG_DS, self.ds),
                           (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xf000),
                           (UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1234),
                           (UC_X86_REG_DI, 0x5678), (UC_X86_REG_EFLAGS, 0x202)):
            self.u.reg_write(reg, value)
        if kind == 'putc':
            assert len(raw) == 1
            args = (color, raw[0], y, x)
            entry = 0x3760
        else:
            args = (color, 0x4000, self.ds, step, y, x)
            entry = 0x36b6
        stack = (0xff00, self.cs, *(n & 65535 for n in args))
        self.u.mem_write(0x7f000, struct.pack('<' + 'H' * len(stack), *stack))
        self.u.emu_start(self.load * 16 + entry, 0x10ffff, count=1000000)
        self.font_mode = False
        if self.error:
            raise RuntimeError('original Gaiji input adapter failed') from self.error
        assert self.done and self.u.reg_read(UC_X86_REG_SP) == 0xf000 + len(stack) * 2
        for reg, value in ((UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1234),
                           (UC_X86_REG_DI, 0x5678), (UC_X86_REG_DS, self.ds)):
            assert self.u.reg_read(reg) == value
        assert self.u.reg_read(UC_X86_REG_EFLAGS) & 0x200
        return bytes(self.font_pixels)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--decoded-dir', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference', type=Path)
    args = parser.parse_args()
    oracle = GaijiOriginal(args.target, args.decoded_dir)
    rows = configured()
    prior = None
    if args.reference:
        prior = json.loads((args.reference / 'receipt.json').read_text())
        assert prior['passed'] and prior['packed_sha256'] == PACKED_SHA
        assert prior['payload_sha256'] == PAYLOAD_SHA
        assert [r['input'] for r in prior['controls']] == [list(row) for row in rows]
        for name, digest in prior['files'].items():
            assert sha((args.reference / name).read_bytes()) == digest
    args.output.mkdir(parents=True, exist_ok=False)
    fixture = args.output / 'vectors.txt'
    fixture.write_text(''.join(' '.join(map(str, row)) + '\n' for row in rows))
    process = subprocess.Popen([str(args.native.resolve()), '--vectors', str(fixture.resolve())],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    controls = []
    try:
        with gzip.open((args.reference or args.output) / 'original-pages.bin.gz', 'rb' if prior else 'wb') as stream:
            for index, row in enumerate(rows):
                expected = stream.read(256000) if prior else oracle.draw(row)
                assert len(expected) == 256000
                if prior:
                    assert sha(expected) == prior['controls'][index]['sha256']
                else:
                    stream.write(expected)
                actual = process.stdout.read(256000)
                if actual != expected:
                    first = next((at for at, (a, b) in enumerate(zip(actual, expected)) if a != b), None)
                    raise AssertionError(('Gaiji pixels differ', index, row, len(actual), first))
                controls.append(dict(input=row, bytes=256000, sha256=sha(expected)))
            if prior:
                assert not stream.read(1)
        assert not process.stdout.read(1)
        assert process.wait(timeout=30) == 0 and not process.stderr.read()
    except BaseException:
        process.kill()
        process.wait(timeout=30)
        raise
    source = Path(__file__).resolve().parent
    receipt = dict(passed=True, packed_sha256=PACKED_SHA, payload_sha256=PAYLOAD_SHA,
                   load=f'{oracle.load:04x}', putc_entry='0000:3760', puts_entry='0000:36B6',
                   dgroup='0E53', vram_segment='A800',
                   putc_sha256=sha(oracle.payload[0x3760:0x37f3]),
                   puts_sha256=sha(oracle.payload[0x36b6:0x375f]),
                   native_sha256=sha(args.native.read_bytes()), controls=controls,
                   source={name:sha((source / name).read_bytes()) for name in
                       ('cutscene_scene.cpp', 'cutscene_scene.hpp', 'gaiji_address_contracts.cpp',
                        'verify_cutscene.py', 'verify_font_address.py',
                        'verify_gaiji_address.py', 'CMakeLists.txt')},
                   reference_receipt_sha256=sha((args.reference / 'receipt.json').read_bytes())
                       if prior else None,
                   files={p.name:sha(p.read_bytes()) for p in args.output.iterdir()})
    (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Gaiji addresses', len(rows), 'complete pages PASS', flush=True)


if __name__ == '__main__':
    main()
