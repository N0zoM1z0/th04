#!/usr/bin/env python3
"""Compare MAINE animation fades with original OP/MAINE palette callers.

Original function instructions execute with guarded palette_show/VSYNC_WAIT
consumers. Each wait consumes one explicit ideal refresh; all original tone
stores, show calls and wait records are retained. Native comparison folds
same-refresh shows to their final tone, matching Animation's public clock.
This does not measure DAC scanout, interrupt cadence or physical elapsed time.
"""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys

import unicorn
from unicorn.x86_const import *

SPEEDS = (0, 1, 2, 4, 16, 32767, 32768, 65535, 65536, 131071, -1, -32768)
ROWS = list(itertools.product((0, 1), SPEEDS))
SHA = lambda raw: hashlib.sha256(raw).hexdigest()

def original_case(record, artifact, load, direction, speed, carrier):
    body = bytearray(record['body'])
    for at in record['sites']:
        value = struct.unpack_from('<H', body, at)[0]
        struct.pack_into('<H', body, at, (value + load) & 65535)
    tone_offset, show, wait = (0x586, 0x1de0, 0x2648) if artifact == 'op' else (0x132, 0x19ec, 0x2206)
    start, end = (0x622, 0x665) if direction else (0x666, 0x6a4)
    cpu = unicorn.Uc(unicorn.UC_ARCH_X86, unicorn.UC_MODE_16)
    cpu.mem_map(0, 0x110000); cpu.mem_write(load * 16, bytes(body))
    ds = load + record['dg']; tone_address = ds * 16 + tone_offset
    cpu.mem_write(tone_address, struct.pack('<H', 0x1234))
    for reg, value in ((UC_X86_REG_CS, load), (UC_X86_REG_DS, ds),
                       (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xf000),
                       (UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1357),
                       (UC_X86_REG_DI, 0x2468), (UC_X86_REG_EFLAGS, 2)):
        cpu.reg_write(reg, value)
    cpu.mem_write(0x7f000, struct.pack('<HHH', 0xff00, load, speed & 65535))
    clock = 0; done = False; error = None; shows = []; writes = []; folded = {}
    expanded = hashlib.sha256()
    def tone(): return struct.unpack('<h', cpu.mem_read(tone_address, 2))[0]
    def ret():
        sp = cpu.reg_read(UC_X86_REG_SP)
        ip, cs = struct.unpack('<HH', cpu.mem_read(0x70000 + sp, 4))
        cpu.reg_write(UC_X86_REG_SP, sp + 4)
        cpu.reg_write(UC_X86_REG_CS, cs); cpu.reg_write(UC_X86_REG_IP, ip)
    with gzip.open(carrier, 'wb') as waits:
        def code(u, address, size, unused):
            nonlocal clock, done, error
            try:
                if address == load * 16 + wait:
                    folded[clock] = tone(); clock += 1
                    raw = struct.pack('<Ih', clock, tone())
                    waits.write(raw); expanded.update(raw); ret()
                elif address == load * 16 + show:
                    shows.append([clock, tone()]); folded[clock] = tone(); ret()
                elif address == load * 16 + 0xff00:
                    done = True; u.emu_stop()
            except Exception as exc:
                error = repr(exc); u.emu_stop()
        def write(u, access, address, size, value, unused):
            nonlocal error
            if address == tone_address:
                if size != 2: error = 'non-WORD palette tone store'; u.emu_stop()
                writes.append([clock, value & 65535])
        for entry in (wait, show, 0xff00):
            cpu.hook_add(unicorn.UC_HOOK_CODE, code, None, load * 16 + entry, load * 16 + entry)
        cpu.hook_add(unicorn.UC_HOOK_MEM_WRITE, write, None, tone_address, tone_address + 1)
        cpu.emu_start(load * 16 + start, 0x10ffff, count=20000000)
    assert error is None and done, (artifact, direction, speed, error)
    assert cpu.reg_read(UC_X86_REG_SP) == 0xf006
    for reg, value in ((UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1357),
                       (UC_X86_REG_DI, 0x2468), (UC_X86_REG_DS, ds)):
        assert cpu.reg_read(reg) == value
    assert len(shows) == 18 and len(writes) == 19
    folded[clock] = tone()
    previous = None; samples = []
    for tick, value in sorted(folded.items()):
        if value != previous: samples.append([tick, value]); previous = value
    return dict(artifact=artifact, load=f'{load:04x}', direction=direction,
                speed=speed, argument_word=speed & 65535, waits=clock,
                samples=samples, shows=shows, tone_writes=writes, final_tone=tone(),
                sp=cpu.reg_read(UC_X86_REG_SP), carrier=carrier.name,
                wait_bytes=clock * 6, wait_expanded_sha256=expanded.hexdigest())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'native', 'output'): parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--diagnostic', action='store_true')
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(args.root / 'scripts/runtime'))
    from verify_dos_vsync_lifecycle import original
    if args.reference:
        ref = json.loads((args.reference / 'receipt.json').read_text())
        assert ref['passed']
        for name, pin in ref['files'].items(): assert SHA((args.reference / name).read_bytes()) == pin
        controls = json.loads((args.reference / 'original.json').read_text())
        originals = ref['originals']
    else:
        controls = []; originals = {}
        for artifact in ('op', 'maine'):
            record = original(artifact)
            originals[artifact] = dict(pins=record['pins'], dg=record['dg'], functions={})
            for direction, start, end in ((1, 0x622, 0x665), (0, 0x666, 0x6a4)):
                raw = bytes(record['body'][start:end])
                (args.output / f'{artifact}-{direction}.bin').write_bytes(raw)
                originals[artifact]['functions'][str(direction)] = dict(entry=f'0000:{start:04x}',
                    length=len(raw), sha256=SHA(raw))
            for load in (0x1000, 0x3333):
                for index, (direction, speed) in enumerate(ROWS):
                    controls.append(original_case(record, artifact, load, direction, speed,
                        args.output / f'{artifact}-{load:04x}-{index:02}.bin.gz'))
            print('Original palette', artifact, 'PASS', flush=True)
        (args.output / 'original.json').write_text(json.dumps(controls, indent=2) + '\n')
    assert len(controls) == 96
    baseline = [row for row in controls if row['artifact'] == 'maine' and row['load'] == '1000']
    for index, (direction, speed) in enumerate(ROWS):
        expected = baseline[index]
        assert all(row['samples'] == expected['samples'] and row['waits'] == expected['waits']
                   for row in controls if (row['direction'], row['speed']) == (direction, speed))
    vectors = args.output / 'vectors.txt'
    vectors.write_text(''.join(f'{direction} {speed}\n' for direction, speed in ROWS))
    expected = ''.join(f'CASE {index}\n' + ''.join(f'TONE {tick} {tone}\n' for tick, tone in row['samples'])
                       + f'END {row["waits"]}\n' for index, row in enumerate(baseline)).encode()
    result = subprocess.run([str(args.native.resolve()), '--vectors', str(vectors.resolve())], capture_output=True)
    (args.output / 'native.txt').write_bytes(result.stdout)
    (args.output / 'expected.txt').write_bytes(expected)
    (args.output / 'stderr.txt').write_bytes(result.stderr)
    equal = result.returncode == 0 and result.stdout == expected and not result.stderr
    source = Path(__file__).resolve().parent
    receipt = dict(passed=equal, diagnostic=args.diagnostic, original_controls=len(controls),
        native_cases=len(ROWS), originals=originals, native_sha256=SHA(args.native.read_bytes()),
        reference_receipt_sha256=SHA((args.reference / 'receipt.json').read_bytes()) if args.reference else None,
        sources={name: SHA((source / name).read_bytes()) for name in ('maine_animation.cpp',
            'maine_animation.hpp', 'palette_animation_contracts.cpp', 'verify_palette_animation.py', 'CMakeLists.txt')},
        files={path.name: SHA(path.read_bytes()) for path in args.output.iterdir()}, scope=__doc__)
    (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert equal != args.diagnostic, 'palette animation comparison failed'
    print('Palette animation', 'PREDECESSOR REJECTED' if args.diagnostic else 'PASS', flush=True)

if __name__ == '__main__': main()
