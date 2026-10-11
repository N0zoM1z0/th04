#!/usr/bin/env python3
"""Compare original and linked DOS Gaiji port and full-address write streams."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
import struct
import sys

from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_INSN, UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from verify_dos_vsync_lifecycle import original

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.pc98 import parse_mz

sha = lambda data: hashlib.sha256(data).hexdigest()


def configured():
    rows = [('putc', 80 + shift, 32, 0, c, (c + shift) & 15)
            for c, shift in itertools.product(range(256), (0, 7))]
    rows += [('putc', 80 + shift, 32, 0, c, 5)
             for c, shift in itertools.product((0, 127, 128, 255, 256, 257,
                                               32767, 32768, 65407, 65408, 65535), range(8))]
    edges = ((640, 0), (639, 0), (-8, 0), (-1, 0), (-32768, 0), (32767, 0),
             (0, 399), (0, 400), (0, 1024), (0, 4096), (120, 819), (127, 819),
             (-8, 819), (0, -1), (0, -32768), (0, 32767))
    rows += [('putc', x, y, 0, c, color)
             for (x, y), c, color in itertools.product(edges, (0, 127, 128, 255, 65535), (0, 15))]
    rows += [('puts', x, y, step, text, 5)
             for x, y, step, text in itertools.product(
                 (-8, 7, 80, 639, 640, 32767), (32, 819),
                 (-32768, -1, 0, 1, 7, 8, 15, 16, 17, 255, 32767, 65535),
                 ('01027f80ff', '010002', '-'))]
    rows += [('puts', x, y, step, bytes(range(1, 256)).hex(), 65535)
             for x, y, step in itertools.product((-8, 639), (0, 819), (16, -1))]
    return rows


def linked(exe, mp):
    raw = exe.read_bytes()
    assert parse_mz(raw).valid
    body = raw[int.from_bytes(raw[8:10], 'little') * 16:]
    sites = []
    for index in range(int.from_bytes(raw[6:8], 'little')):
        off, seg = struct.unpack_from('<HH', raw, int.from_bytes(raw[24:26], 'little') + index * 4)
        assert seg * 16 + off + 1 < len(body)
        sites.append(seg * 16 + off)
    text = mp.read_text()
    def public(name):
        matches = set(re.findall(r'(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+' + re.escape(name) + r'\s*$', text))
        assert len(matches) == 1, (name, matches)
        return tuple(int(x, 16) for x in matches.pop())
    putc = public('GRAPH_GAIJI_PUTC')
    puts = public('GRAPH_GAIJI_PUTS')
    dg, vram = public('_graph_VramSeg')
    return dict(body=body, sites=sites, dg=dg, vram=vram, putc=putc, puts=puts,
                pins=dict(executable=sha(raw), map=sha(mp.read_bytes()), payload=sha(body)))


class Machine:
    def __init__(self, layout, load):
        self.layout = layout
        self.load = load
        body = bytearray(layout['body'])
        for at in layout['sites']:
            struct.pack_into('<H', body, at, (struct.unpack_from('<H', body, at)[0] + load) & 65535)
        self.body = bytes(body)
        self.cpu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.cpu.mem_map(0, 0x100000)
        self.cpu.hook_add(UC_HOOK_CODE, self.code)
        self.cpu.hook_add(UC_HOOK_INSN, self.output, None, 1, 0, UC_X86_INS_OUT)
        self.cpu.hook_add(UC_HOOK_INSN, self.input, None, 1, 0, UC_X86_INS_IN)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.write)

    def code(self, cpu, address, size, unused):
        if address == 0x6f000:
            self.done = True
            cpu.emu_stop()

    def output(self, cpu, port, size, value, unused):
        if size != 1 or port not in (0x68, 0x7c, 0x7e, 0xa1, 0xa3, 0xa5):
            self.error = ('unexpected output', port, size, value)
            cpu.emu_stop()
            return
        self.ports.extend(struct.pack('<HBBB', port, size, value, bool(cpu.reg_read(UC_X86_REG_EFLAGS) & 0x200)))
        if port == 0xa1:
            self.cell = value
        elif port == 0xa3:
            self.column = value
        elif port == 0xa5:
            self.selector = value

    def input(self, cpu, port, size, unused):
        if (port, size) != (0xa9, 1):
            self.error = ('unexpected input', port, size)
            cpu.emu_stop()
            return 0
        # Explicit CGROM input selected by the target's actual OUTs. All
        # cell/column bytes are admitted for the WORD character diagnostics.
        return (self.cell * 17 + self.column * 113 + self.selector * 29 + 7) & 255

    def write(self, cpu, access, address, size, value, unused):
        if not 0xa8000 <= address < 0xb8001:
            return
        at = address - 0xa8000
        if size not in (1, 2) or at + size > len(self.mask):
            self.error = ('unexpected VRAM write', at, size)
            cpu.emu_stop()
            return
        self.writes.extend(struct.pack('<IBI', at, size, value))
        for byte in range(size):
            self.mask[at + byte] |= (value >> (byte * 8)) & 255

    def run(self, row, interrupt):
        kind, x, y, step, text, color = row
        cpu = self.cpu
        cpu.mem_write(self.load * 16, self.body)
        ds = self.load + self.layout['dg']
        cpu.mem_write(ds * 16 + self.layout['vram'], struct.pack('<H', 0xa800))
        raw = bytes.fromhex(text) if kind == 'puts' and text != '-' else b''
        cpu.mem_write(ds * 16 + 0x5000, raw + b'\0')
        cpu.mem_write(0xa8000, bytes(65537))
        self.ports = bytearray()
        self.writes = bytearray()
        self.mask = bytearray(65537)
        self.cell = self.column = self.selector = 0
        self.done = False
        self.error = None
        cs, ip = self.layout[kind]
        for reg, value in ((UC_X86_REG_CS, self.load + cs), (UC_X86_REG_DS, ds),
                           (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xf000),
                           (UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1234),
                           (UC_X86_REG_DI, 0x5678), (UC_X86_REG_ES, 0x6789),
                           (UC_X86_REG_EFLAGS, 2 | (interrupt << 9))):
            cpu.reg_write(reg, value)
        args = (color, text, y, x) if kind == 'putc' else (color, 0x5000, ds, step, y, x)
        stack = (0, 0x6f00, *(n & 65535 for n in args))
        cpu.mem_write(0x7f000, struct.pack('<' + 'H' * len(stack), *stack))
        cpu.emu_start((self.load + cs) * 16 + ip, 0xfffff, count=2000000)
        assert self.error is None, self.error
        assert self.done and cpu.reg_read(UC_X86_REG_SP) == 0xf000 + len(stack) * 2
        for reg, value in ((UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1234),
                           (UC_X86_REG_DI, 0x5678), (UC_X86_REG_DS, ds)):
            assert cpu.reg_read(reg) == value, (reg, cpu.reg_read(reg), value)
        assert bool(cpu.reg_read(UC_X86_REG_EFLAGS) & 0x200) == bool(interrupt)
        return bytes(self.mask), bytes(self.ports), bytes(self.writes), cpu.reg_read(UC_X86_REG_ES)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--artifact', choices=('op', 'maine'), required=True)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--map', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--diagnostic', action='store_true', help='record predecessor differences without accepting them')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    reference = original(args.artifact)
    entries = dict(op=(0x3e34, 0x3d8a, 0x570), maine=(0x3760, 0x36b6, 0x11c))
    putc, puts, vram = entries[args.artifact]
    reference.update(putc=(0, putc), puts=(0, puts), vram=vram)
    current = linked(args.exe, args.map)
    rows = configured()
    if args.limit:
        rows = rows[:args.limit]
    args.output.mkdir(parents=True, exist_ok=False)
    controls = []
    differences = []
    for load in (0x1000, 0x3333):
        target = Machine(reference, load)
        product = Machine(current, load)
        with gzip.open(args.output / f'transcripts-{load:04x}.bin.gz', 'wb') as stream:
            for index, row in enumerate(rows):
                expected = target.run(row, index & 1)
                actual = product.run(row, index & 1)
                equal = expected == actual
                if not equal:
                    diff = dict(load=f'{load:04x}', index=index, input=row,
                                mask_bytes=sum(a != b for a, b in zip(expected[0], actual[0])),
                                ports_equal=expected[1] == actual[1], writes_equal=expected[2] == actual[2],
                                es_equal=expected[3] == actual[3])
                    differences.append(diff)
                    assert args.diagnostic, diff
                for result in (expected, actual):
                    for data in result[:3]:
                        stream.write(struct.pack('<I', len(data)) + data)
                controls.append(dict(load=f'{load:04x}', input=row, equal=equal,
                                     original_es=f'{expected[3]:04x}', candidate_es=f'{actual[3]:04x}',
                                     original=[sha(x) for x in expected[:3]],
                                     candidate=[sha(x) for x in actual[:3]]))
        print(args.artifact, f'{load:04x}', len(rows), 'checked', flush=True)
    receipt = dict(passed=not differences, diagnostic=args.diagnostic, artifact=args.artifact,
                   original=reference['pins'], candidate=current['pins'],
                   original_entries=dict(putc=f'0000:{putc:04x}', puts=f'0000:{puts:04x}'),
                   candidate_entries={n:list(current[n]) for n in ('putc', 'puts')},
                   candidate_dgroup=current['dg'], original_dgroup=reference['dg'],
                   controls=controls, differences=differences,
                   source_sha256=sha((ROOT / 'src/shared/hardware/graph_gaiji.cpp').read_bytes()),
                   producer_sha256=sha(Path(__file__).read_bytes()),
                   files={p.name:sha(p.read_bytes()) for p in args.output.iterdir()})
    (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('DOS Gaiji', args.artifact, len(controls), 'PASS' if not differences else f'{len(differences)} differences')


if __name__ == '__main__':
    main()
