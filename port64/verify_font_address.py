#!/usr/bin/env python3
"""Compare GRAPH_PUTSA_FX's visible writes with original MAINE instructions."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess

from verify_cutscene import Original, PACKED_SHA, PAYLOAD_SHA
from unicorn.x86_const import (
    UC_X86_REG_BP, UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_EFLAGS,
    UC_X86_REG_SP, UC_X86_REG_SS,
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def configured():
    strings = ('82a0', '8abf', '4142', '2041', 'a1a2', '414282a04344',
               'e0408140', '7e207f')
    rows = [(80 + shift, 32, weight, (weight + shift) & 15, 3, text)
            for weight, shift, text in itertools.product(range(8), range(8), strings)]
    edges = ((640, 0), (639, 0), (-8, 0), (-1, 0), (-32768, 0), (32767, 0),
             (0, 399), (0, 400), (0, 1023), (0, 1024), (0, 1025),
             (120, 819), (127, 819), (-8, 819), (0, -1), (0, -32768),
             (0, 32767), (639, 1023), (-8, 1024), (32767, -32768))
    rows += [(x, y, weight, (weight * 3 + 5) & 15, 11, text)
             for (x, y), weight, text in itertools.product(edges, range(8),
                 ('4142', '82a08abf', '4182a042'))]
    rows += [(x, y, 3, color, 7, '82a041') for x, y, color in itertools.product(
        (-8, 80, 639), (0, 819, 1024), (0, 5, 15, 256, 65535))]
    return rows


class FontOriginal(Original):
    def font_write(self, cpu, access, address, size, value, unused):
        if not self.font_mode:
            return
        # A WORD write beginning at the last visible byte can spill outside
        # the page. Filter each physical byte, rather than only its start.
        for byte in range(size):
            at = address - 0xa8000 + byte
            if 0 <= at < 32000:
                for bit in range(8):
                    if value & (1 << (byte * 8 + 7 - bit)):
                        self.font_pixels[at * 8 + bit] = self.font_color & 15

    @staticmethod
    def rom(cell, column, selector):
        # Original OUTs choose these coordinates in the supplied Anex86 BMP.
        # This input adapter neither parses SJIS nor imports a native glyph.
        if column in (9, 10):
            byte_x = cell + (128 if column == 10 else 0)
            y = selector & 15
        else:
            byte_x = column * 2 + (0 if selector & 0x20 else 1)
            y = cell * 16 + (selector & 15)
        return ~((byte_x * 37 + y * 53 + 19) & 255) & 255

    def draw(self, row):
        x, y, weight, color, seed, text = row
        self.u.mem_write(self.load * 16, self.module)
        self.u.mem_write(self.ds * 16, self.data)
        self.u.mem_write(0xa8000, bytes(65536 + 1))
        self.u.mem_write(self.ds * 16 + 0x654, bytes.fromhex(text) + b'\0')
        self.write(0x5fc, 'H', weight)
        self.font_mode = True
        self.font_rows = []
        self.font_row = self.font_cell = self.font_column = 0
        self.font_rom = self.rom
        self.font_color = color
        self.font_pixels = bytearray(bytes((at * 73 + seed) & 15 for at in range(16)) * 16000)
        self.error = None
        self.done = False
        for reg, value in ((UC_X86_REG_CS, self.load + 0xcc7), (UC_X86_REG_DS, self.ds),
                           (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xf000),
                           (UC_X86_REG_BP, 0xabcd), (UC_X86_REG_EFLAGS, 2)):
            self.u.reg_write(reg, value)
        self.u.mem_write(0x7f000, struct.pack('<7H', 0xff00, self.cs, 0x654,
                                             self.ds, color & 65535, y & 65535, x & 65535))
        self.u.emu_start((self.load + 0xcc7) * 16 + 0x58c, 0x10ffff, count=100000)
        self.font_mode = False
        if self.error:
            raise RuntimeError('original font input adapter failed') from self.error
        assert self.done and self.u.reg_read(UC_X86_REG_SP) == 0xf00e
        assert self.u.reg_read(UC_X86_REG_BP) == 0xabcd
        return bytes(self.font_pixels)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--decoded-dir', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference', type=Path,
                        help='replay an already verified original receipt without executing it again')
    args = parser.parse_args()
    oracle = FontOriginal(args.target, args.decoded_dir)
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
    stream_path = (args.reference or args.output) / 'original-pages.bin.gz'
    controls = []
    try:
        with gzip.open(stream_path, 'rb' if prior else 'wb') as stream:
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
                    raise AssertionError(('font pixels differ', index, row, len(actual), first,
                                          actual[first:first+16] if first is not None else b'',
                                          expected[first:first+16] if first is not None else b''))
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
                   load=f'{oracle.load:04x}', entry='0CC7:058C', dgroup='0E53',
                   font_code_sha256=sha(oracle.payload[0xd1fc:0xd35c]),
                   font_tables_sha256=sha(oracle.data[0x5bc:0x600]),
                   native_sha256=sha(args.native.read_bytes()), controls=controls,
                   source={name:sha((source / name).read_bytes()) for name in
                       ('cutscene_scene.cpp', 'cutscene_scene.hpp', 'dialog.cpp', 'dialog.hpp',
                        'font_address_contracts.cpp', 'verify_cutscene.py',
                        'verify_font_address.py', 'CMakeLists.txt')},
                   reference_receipt_sha256=sha((args.reference / 'receipt.json').read_bytes())
                       if prior else None,
                   files={p.name:sha(p.read_bytes()) for p in args.output.iterdir()})
    (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('font address', len(rows), 'complete pages PASS', flush=True)


if __name__ == '__main__':
    main()
