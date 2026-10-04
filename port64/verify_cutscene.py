#!/usr/bin/env python3
"""Run MAINE's original cutscene control flow and compare portable requests.

The original packed executable is independently decoded by its own DIET stub.
Only external input, graphics, allocation, palette and audio consumers are
intercepted. Script dispatch, numeric parsing, cursor wrap and text-box mask
sequencing execute original instructions. No portable script parser is used
to produce the reference.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

import unicorn
from unicorn.x86_const import *

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.probes.prepare_th04_maine_diagnostic_hdi import Fat12
from scripts.probes.probe_th04_pf_archive import ARCHIVES, parse_archive

sha = lambda b: hashlib.sha256(b).hexdigest()
signed = lambda n: n if n < 32768 else n - 65536
PACKED_SHA = '670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8'
PAYLOAD_SHA = '7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c'
FUNCTIONS = ((0xa847, 0x575, 'bfe8e1a9a3aaa823807f3e3e2053ed2eae6e47fbe6cdc1406ba5d432acf7eb15'),
             (0xadfc, 0xd4, '7229d2bd0dc77c3664592cc7b9a6576d88aeef8f25fba919bc444c69f654d6c2'))


def ending_assets(path):
    image = Path(path).read_bytes()
    if sha(image) != '0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd':
        raise ValueError('original HDI identity differs')
    fat = Fat12(bytearray(image))
    directory = fat.find_entry([fat.root], b'GENSO      ')
    clusters = fat.chain(struct.unpack_from('<H', fat.image, directory + 26)[0])
    entry = fat.find_entry([fat.cluster_offset(c) for c in clusters], ARCHIVES['op_end']['fat_name'])
    blob = fat.file_bytes(struct.unpack_from('<H', fat.image, entry + 26)[0],
                          struct.unpack_from('<I', fat.image, entry + 28)[0])
    if sha(blob) != ARCHIVES['op_end']['sha256']:
        raise ValueError('Ending archive identity differs')
    return parse_archive(blob, 'op_end', ARCHIVES['op_end'])[1]


class Original:
    def __init__(self, target, decoded, load=0x2000):
        packed = Path(target).read_bytes()
        if len(packed) != 38035 or sha(packed) != PACKED_SHA:
            raise ValueError('packed MAINE identity differs')
        self.payload = (decoded / 'payload.bin').read_bytes()
        receipt = json.loads((decoded / 'receipt.json').read_text())
        if (sha(self.payload) != PAYLOAD_SHA or len(self.payload) != 62414 or
                receipt['packed_target_sha256'] != PACKED_SHA or
                receipt['payload_sha256'] != PAYLOAD_SHA or
                not all(receipt['checks'].values()) or receipt['relocation_count'] != 559):
            raise ValueError('original decompressor observation is not attested')
        for start, size, digest in FUNCTIONS:
            if sha(self.payload[start:start + size]) != digest:
                raise ValueError('original cutscene function extent differs')
        with (decoded / 'relocations.csv').open(newline='') as stream:
            sites = [int(r['relative_linear'], 0) for r in csv.DictReader(stream)]
        if len(sites) != 559:
            raise ValueError('original relocation stream differs')
        module = bytearray(self.payload)
        for at in sites:
            struct.pack_into('<H', module, at, (struct.unpack_from('<H', module, at)[0] + load) & 65535)
        self.load = load
        self.module = bytes(module)
        self.cs = load + 0xa05
        self.ds = load + 0xe53
        self.u = unicorn.Uc(unicorn.UC_ARCH_X86, unicorn.UC_MODE_16)
        self.u.mem_map(0, 0x110000)
        self.u.mem_write(load * 16, bytes(module))
        self.data = bytes(self.u.mem_read(self.ds * 16, 65536))
        self.u.hook_add(unicorn.UC_HOOK_CODE, self.hook)
        self.u.hook_add(unicorn.UC_HOOK_INSN, self.port, None, 1, 0, UC_X86_INS_OUT)
        self.events = []
        self.error = None
        self.font_mode = False
        self.u.hook_add(unicorn.UC_HOOK_INSN, self.input_port, None, 1, 0, UC_X86_INS_IN)
        self.u.hook_add(unicorn.UC_HOOK_MEM_WRITE, self.font_write)

    def write(self, at, fmt, *values):
        self.u.mem_write(self.ds * 16 + at, struct.pack('<' + fmt, *values))

    def read(self, at, fmt):
        return struct.unpack('<' + fmt, self.u.mem_read(self.ds * 16 + at, struct.calcsize('<' + fmt)))

    def event(self, kind, a=0, b=0, c=0, d=0, e=0, name=b''):
        self.events.append(f'{kind} {a} {b} {c} {d} {e} ' + (name.hex() if name else '-'))

    def port(self, u, port, size, value, unused):
        if self.font_mode:
            if port == 0xa5:
                self.font_row = value
            elif port == 0xa1:
                self.font_cell = value
            elif port == 0xa3:
                self.font_column = value
            elif port not in (0x68, 0x7c, 0x7e, 0xa1, 0xa3):
                self.error = ValueError(f'unexpected original font port {port:x}')
                u.emu_stop()
            return
        if port in (0xa4, 0xa6):
            self.event('show' if port == 0xa4 else 'access', value)
        elif port not in (0x7c, 0x7e):
            self.error = ValueError(f'unexpected original port {port:x}')
            u.emu_stop()

    def input_port(self, u, port, size, unused):
        if not self.font_mode or (port, size) != (0xa9, 1):
            self.error = ValueError('unexpected original input port')
            u.emu_stop()
            return 0
        if self.font_rom is not None:
            return self.font_rom(self.font_cell, self.font_column, self.font_row)
        row = self.font_rows[self.font_row & 15]
        # Explicit supplied CGROM adapter: the first read becomes AH, then
        # the second becomes AL; the target swaps them before VRAM writes.
        return (row >> (8 if self.font_row & 0x20 else 0)) & 255

    def font_write(self, u, access, address, size, value, unused):
        if not self.font_mode or not 0xa8000 <= address < 0xa8000+32000:
            return
        for i in range(size):
            at = address-0xa8000+i
            for bit in range(8):
                if value & (1 << (i*8+7-bit)):
                    self.font_pixels[at*8+bit] = self.font_color & 15

    def hook(self, u, address, size, unused):
        try:
            self.body(u, address)
        except Exception as error:
            self.error = error
            u.emu_stop()

    def body(self, u, address):
        cs = u.reg_read(UC_X86_REG_CS)
        ip = address - cs * 16
        sp = u.reg_read(UC_X86_REG_SP)
        relative = cs - self.load

        def words(count, far=True):
            return struct.unpack('<' + 'H' * count, u.mem_read(0x70000 + sp + (4 if far else 2), count * 2))

        def ret(args=0, far=True):
            values = struct.unpack('<HH' if far else '<H', u.mem_read(0x70000 + sp, 4 if far else 2))
            u.reg_write(UC_X86_REG_SP, sp + (4 if far else 2) + args)
            if far:
                u.reg_write(UC_X86_REG_CS, values[1])
            u.reg_write(UC_X86_REG_IP, values[0])

        def cstring(off, seg):
            raw = bytes(u.mem_read(seg * 16 + off, 16))
            if 0 not in raw:
                raise ValueError('original filename lacks bounded terminator')
            return raw[:raw.index(0)]

        if cs == self.cs and ip == 0xff00:
            self.done = True
            u.emu_stop()
            return
        if self.font_mode and relative == 0xcc7 and 0x58c <= ip <= 0x6eb:
            return
        if relative == 0xcc7 and ip == 0x81a:
            self.write(0x1b43, 'H', self.held)
            ret()
            return
        if relative == 0xa05:
            near = {0x45e: ('snap', 0), 0x54e: ('restore', 0),
                    0x52f: ('bg_free', 0), 0x286: ('egc_begin', 0)}
            if ip in near:
                kind, args = near[ip]
                self.event(kind)
                ret(args, False)
                return
            if ip == 0x73f:
                self.event('box_mask', words(1, False)[0])
                ret(2, False)
                return
            if ip == 0x32f:
                mask, quarter, top, left = words(4, False)
                self.event('pic_mask', signed(left), signed(top), signed(quarter), signed(mask))
                ret(8, False)
                return
            if ip == 0x2ba:
                top, left = words(2, False)
                self.event('pic_copy', signed(left), signed(top))
                ret(4, False)
                return
        if relative == 0:
            if ip == 0x40e7 or 0x40e7 <= ip <= 0x4117:
                return  # Execute original ctype/tolower, including its ABI.
            if ip == 0x85c:
                self.event('egc_end'); ret(); return
            if ip == 0x1188:
                self.event('clear'); ret(); return
            if ip == 0x11c2:
                self.event('copy_page', words(1)[0]); ret(2); return
            if ip == 0x1274:
                self.event('pi_free'); ret(8); return
            if ip == 0x19ec:
                # The caller stores PaletteTone, then calls palette_show()
                # with no stack argument. It is not a Pascal settone call.
                self.event('tone', self.read(0x132, 'h')[0]); ret(); return
            if ip == 0x1988:
                self.event('scroll', signed(words(1)[0])); ret(2); return
            if ip in (0x622, 0x666, 0x222c, 0x226c):
                self.event('fade', int(ip >= 0x222c), int(ip in (0x622, 0x222c)), signed(words(1)[0]))
                ret(2); return
            if ip == 0xc82:
                color, mode = words(2)
                assert (mode, color) == (0xc0, 0)
                ret(4); return
            if ip == 0xbea:
                bottom, right, top, left = words(4)
                # This GRCG entry accepts inclusive byte-column coordinates.
                self.event('clear_rect', signed(left)*8, signed(top), (signed(right)-signed(left)+1)*8, signed(bottom)-signed(top)+1)
                ret(8); return
            if ip == 0x3760:
                color, glyph, top, left = words(4)
                self.event('gaiji', signed(left), signed(top), glyph, color)
                ret(8); return
        if relative == 0xcc7:
            if ip in (0x33, 0x20a):
                self.event('delay' if ip == 0x33 else 'wait', signed(words(1)[0])); ret(2); return
            if ip == 0x3d6:
                frames, measure = words(2)
                self.event('measure', signed(measure), signed(frames)); ret(4); return
            if ip == 0x58c:
                off, seg, color, top, left = words(5)
                glyph = bytes(u.mem_read(seg * 16 + off, 3))
                assert glyph[2] == 0
                self.event('text', signed(left), signed(top), glyph[0]*256+glyph[1], color, self.read(0x5fc, 'H')[0])
                ret(10); return
            if ip == 0x48:
                assert words(1)[0] == 0
                self.event('pi_palette'); ret(2); return
            if ip == 0x6d:
                slot, top, left = words(3)
                assert slot == 0
                self.event('pi_put', signed(left), signed(top)); ret(6); return
            if ip == 0xf5:
                off, seg, slot = words(3)
                assert slot == 0
                self.event('pi_load', name=cstring(off, seg)); ret(6); return
            if ip == 0x13b:
                quarter, slot, top, left = words(4)
                assert slot == 0
                self.event('quarter', signed(left), signed(top), signed(quarter)); ret(8); return
            if ip == 0x31c:
                self.event('bgm_control', words(1)[0]); ret(2); return
            if ip == 0x4a2:
                mode, off, seg = words(3)
                self.event('bgm_load', mode, name=cstring(off, seg)); ret(6); return
            if ip == 0x924:
                self.event('se_begin'); ret(); return
            if ip == 0x930:
                self.event('se', signed(words(1)[0])); ret(2); return
            if ip == 0x96a:
                self.event('se_end'); ret(); return
        if relative == 0xa05 and 0x5fd <= ip < 0xe80:
            return
        raise ValueError(f'unexpected original execution {cs:04x}:{ip:04x}')

    def run(self, body, held):
        if len(body) > 8188:
            raise ValueError('script cannot fit the original near buffer')
        self.font_mode = False
        self.u.mem_write(self.ds * 16, self.data)
        self.u.mem_write(self.ds * 16 + 0x1f48, body + bytes(4))
        self.write(0x3f48, 'H', 0x1f48)
        self.events = []; self.error = None; self.done = False; self.held = held
        for reg, value in ((UC_X86_REG_CS, self.cs), (UC_X86_REG_DS, self.ds),
                           (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xff00),
                           (UC_X86_REG_BP, 0), (UC_X86_REG_EFLAGS, 2)):
            self.u.reg_write(reg, value)
        self.u.mem_write(0x7ff00, struct.pack('<H', 0xff00))
        self.u.emu_start(self.cs * 16 + 0xdac, 0x10ffff, count=2000000)
        if self.error:
            raise RuntimeError('original cutscene adapter rejected') from self.error
        if not self.done or self.u.reg_read(UC_X86_REG_SP) != 0xff02:
            raise ValueError('original cutscene did not return with its near ABI')
        offset = self.read(0x3f48, 'H')[0] - 0x1f48
        x, y, interval = self.read(0x3f8c, '3h')
        color = self.read(0x3f92, 'B')[0]
        weight = self.read(0x5fc, 'H')[0]
        default = self.read(0x3f94, 'h')[0]
        self.events.append(f'END {offset} {x} {y} {interval} {color} {weight} {default}')
        return self.events

    def glyph(self, rows, weight, color, x, y, text=0x82a0, rom=None):
        self.u.mem_write(self.load*16, self.module)
        self.u.mem_write(self.ds*16, self.data)
        self.u.mem_write(0xa8000, bytes(32000))
        self.u.mem_write(self.ds*16+0x654, text.to_bytes(2, 'big') + b'\0')
        self.write(0x5fc, 'H', weight)
        self.font_mode = True; self.font_rows = rows; self.font_row = 0
        self.font_rom = rom; self.font_cell = 0; self.font_column = 0
        self.font_color = color; self.font_pixels = bytearray(640*400)
        self.error = None; self.done = False
        for reg, value in ((UC_X86_REG_CS, self.load+0xcc7), (UC_X86_REG_DS, self.ds),
                           (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xf000),
                           (UC_X86_REG_BP, 0), (UC_X86_REG_EFLAGS, 2)):
            self.u.reg_write(reg, value)
        self.u.mem_write(0x7f000, struct.pack('<7H', 0xff00, self.cs, 0x654, self.ds, color, y, x))
        self.u.emu_start((self.load+0xcc7)*16+0x58c, 0x10ffff, count=100000)
        self.font_mode = False
        if self.error:
            raise RuntimeError('original font adapter rejected') from self.error
        if not self.done or self.u.reg_read(UC_X86_REG_SP) != 0xf00e:
            raise ValueError('original font did not return with FAR Pascal RETF10')
        return bytes(self.font_pixels)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--decoded-dir', type=Path, required=True)
    p.add_argument('--hdi', type=Path, required=True)
    p.add_argument('--exe', type=Path)
    p.add_argument('--runner')
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    (out / 'mismatch.json').unlink(missing_ok=True)
    assets = ending_assets(args.hdi)
    cases = [(n, b) for n, b in assets.items() if n.startswith('_ED')]
    assert len(cases) == 8
    synthetic = [b'\\N\\n\\n\\n\\s-\\$', b'\\c999\\b3\\v12\\e\\t\\$',
                 b'\\t1234Z\\e\\$', b'\\fi0\\fo2\\wi1\\WO0\\$',
                 b'\\g0\\ga255\\ga999\\w0\\wk2\\wmk12,34\\$',
                 b'\\m$\\m*\\m,END2 \\fm255\\fm256\\$',
                 b'\\pXZ\\pp\\p-\\p,123456789012\\p@\\p=\\$',
                 b'\\=4\\==0,0\\=\\==3,12\\vp1\\k2\\@\\$',
                 b'\\c1\\b0\\v0' + b'\x82\xa0' * 109 + b'\\s-\\$',
                 b'\\e\\ga\\e\\c\\e\\v\\e\\Q\\$']
    cases += [(f'synthetic-{i}', body) for i, body in enumerate(synthetic)]
    originals = [Original(args.target, args.decoded_dir, load) for load in (0x1000, 0x2000)]
    records = []
    for index, ((name, body), held) in enumerate(itertools.product(cases, (0, 0x20, 0x10, 0x30))):
        expected = originals[0].run(body, held)
        if expected != originals[1].run(body, held):
            raise ValueError('cutscene requests depend on DOS load segment')
        script = out / f'{index:03d}.txt'; script.write_bytes(body)
        trace = ('\n'.join(expected) + '\n').encode()
        (out / f'{index:03d}-trace.txt').write_bytes(trace)
        if args.exe:
            env = os.environ.copy(); env.setdefault('WINEDEBUG', '-all')
            cmd = ([args.runner] if args.runner else []) + [str(args.exe.resolve()), '--trace', str(script), str(held)]
            actual = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True).stdout.splitlines()
            if actual != expected:
                first = next(i for i, (a, b) in enumerate(itertools.zip_longest(actual, expected)) if a != b)
                (out / 'mismatch.json').write_text(json.dumps(dict(name=name, held=held, at=first,
                    actual=actual[max(0, first-3):first+4], expected=expected[max(0, first-3):first+4]), indent=2)+'\n')
                raise ValueError(f'cutscene {name} held{held} differs at {first}')
        records.append(dict(name=name, held=held, script_sha256=sha(body), records=len(expected), trace_sha256=sha(trace)))
    receipt = dict(passed=True, observed_utc=datetime.now(timezone.utc).isoformat(),
        packed_sha256=PACKED_SHA, payload_sha256=PAYLOAD_SHA, cases=records,
        source_sha256=sha(Path(__file__).read_bytes()), native_sha256=sha(args.exe.read_bytes()) if args.exe else None,
        unicorn_version=unicorn.__version__, unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
        scope='Original MAINE decoded 0A05:07F7/0DAC, numeric readers, cursor and box-mask loop at load1000/2000. All eight legal Ending scripts and synthetic controls; ordered requests and final cursor/default/color/weight/interval/offset.',
        limits='External graphics, palette, input, waits, allocation and sound are intercepted. No physical timing, whole-route Ending video, staff roll or score registration claim.')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(passed=True, cases=len(records), records=sum(r['records'] for r in records), native_compared=bool(args.exe))))


if __name__ == '__main__':
    main()
