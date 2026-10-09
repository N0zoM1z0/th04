#!/usr/bin/env python3
"""Independent original PMD bytecode/timer state versus native Sequence.

All supplied songs execute in their original resident driver. Published work
pointers, cursor/duration/loop/note/volume/transposition/detune/mask fields,
actual measure/status/volume queries and timer settings are captured. Flat COM,
DOS and injected IRQ adapters are those separately attested by v1329. This
compares all selected bytecode control fields, including SSG drum/SE masks.
Unselected chip, envelope and voice state remain outside this comparison.
It does not accept native
FM synthesis, chip requests, physical timing, or device output.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from verify import source_manifest, require_elf_x86_64, require_pe_x86_64
from verify_pmd_driver import directory_files, install, DRIVERS, HDI_SHA
from verify_cutscene import ending_assets


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def control_row(line):
    row = list(map(int, line.split()))
    if len(row) != 128:
        raise ValueError('incomplete PMD control state')
    return row


def original_state(driver):
    work = driver.service(0x1000)
    segment = driver.load + work['ds']
    table = segment * 16 + work['dx']
    song = driver.service(0x600)
    if song['ds'] != work['ds']:
        raise ValueError('song/work segment ownership differs')
    address = song['dx']
    state = driver.snapshot()
    memory = driver.u.mem_read(table - 129, 144)
    row = [state['measure'], state['volume'] & 255, state['status'],
           memory[0], memory[5], memory[4], memory[76]]
    # The original published part pointer table has eleven entries. Their
    # first 0x60 bytes retain this common layout in all three attested drivers.
    for pointer in struct.unpack('<11H', driver.u.mem_read(table, 22)):
        part = bytes(driver.u.mem_read(segment * 16 + pointer, 0x60))
        position, loop = struct.unpack_from('<HH', part)
        row += [position - address if position else 0,
                loop - address if loop else 0, part[4], part[0x32], part[0x5a],
                part[0x12], part[0x13], part[0x5f],
                struct.unpack_from('<h', part, 8)[0], part[0x31], part[0x3b]]
    return row


def operations(ticks):
    # Timer B, Timer A, no-status and simultaneous interrupts are independent.
    result = [('I', 1)] * 128 + [('I', 3)] * ticks
    result += [('F', 4)] + [('I', 1)] * 128 + [('F', -7)] + [('I', 1)] * 64
    result += [('S', 0)] + [('I', 3)] * 128 + [('R', 0)]
    result += [('I', 0)] * 8 + [('I', 2)] * 128
    return result


def produce(args, root, out, manifest, files):
    binaries = directory_files(args.hdi)
    assets = ending_assets(args.hdi)
    ops = operations(args.ticks)
    (out / 'operations.txt').write_text(''.join(f'{op} {value}\n' for op, value in ops))
    outputs = {'operations.txt': sha(out / 'operations.txt')}
    cases = []
    for load in (0x1000, 0x2000):
        for name, (_, _, board, extension, _) in DRIVERS.items():
            for song, data in sorted(assets.items()):
                if not song.endswith('.' + extension):
                    continue
                # A fresh resident starts every song; restart in the same case
                # independently checks retained note counters and mutable loops.
                d = install(binaries[name], name, load)
                d.write_resource(0xb00, assets['MIKO.EFC'])
                d.write_resource(0x600, data)
                d.service(0)
                output = out / f'{name}-{load:04x}-{song}.txt'
                with output.open('w') as f:
                    f.write(' '.join(map(str, original_state(d))) + '\n')
                    for tick, (op, value) in enumerate(ops):
                        d.ticks = tick
                        if op == 'I':
                            d.irq(value)
                        elif op == 'F':
                            d.service(0x200 | (value & 255))
                        elif op == 'S':
                            d.service(0x100)
                        else:
                            d.service(0)
                        f.write(' '.join(map(str, original_state(d))) + '\n')
                resource = out / song
                if not resource.exists():
                    resource.write_bytes(data)
                outputs[output.name] = sha(output)
                outputs[song] = sha(resource)
                cases.append(dict(driver=name, board=board, song=song, load=load,
                                  reference=output.name, rows=len(ops) + 1))
                print(f'Original Sequence {name} {song} load{load:04x} PASS', flush=True)
    if source_manifest(root)[0] != manifest:
        raise ValueError('source changed during original Sequence replay')
    return dict(passed=True, utc=datetime.now(timezone.utc).isoformat(), command=sys.argv,
                source_manifest=manifest, source_files=len(files), hdi_sha256=HDI_SHA,
                cases=cases, outputs=outputs, rows=sum(c['rows'] for c in cases),
                scope=__doc__)


def consume(args, root, out, manifest, files):
    ref = args.reference.resolve()
    receipt = json.loads((ref / 'receipt.json').read_text())
    if not receipt['passed'] or len(receipt['cases']) != 138 or receipt['hdi_sha256'] != HDI_SHA:
        raise ValueError('incomplete original Sequence reference')
    for name, digest in receipt['outputs'].items():
        if sha(ref / name) != digest:
            raise ValueError('original reference hash differs: ' + name)
    binary = args.binary.resolve()
    if binary.read_bytes()[:2] == b'MZ':
        require_pe_x86_64(binary)
    else:
        require_elf_x86_64(binary)
    outputs = {}
    completed = {}
    for case in receipt['cases']:
        key = (case['driver'], case['song'])
        if key not in completed:
            name = f'{case["driver"]}-{case["song"]}.txt'
            path = out / name
            subprocess.run([str(binary), str(ref / case['song']), str(case['board']),
                            str(ref / 'operations.txt'), str(path)], check=True)
            outputs[name] = sha(path)
            completed[key] = path
        path = completed[key]
        expected = [control_row(r) for r in (ref / case['reference']).read_text().splitlines()]
        actual = [control_row(r) for r in path.read_text().splitlines()]
        if expected != actual:
            for row, (e, a) in enumerate(zip(expected, actual)):
                if e != a:
                    columns = [(i, ev, av) for i, (ev, av) in enumerate(zip(e, a)) if ev != av]
                    raise ValueError(f'{key} load{case["load"]:04x} row{row} differs: {columns}')
            raise ValueError(f'{key} incomplete row count')
    if source_manifest(root)[0] != manifest:
        raise ValueError('source changed during native Sequence replay')
    return dict(passed=True, utc=datetime.now(timezone.utc).isoformat(), command=sys.argv,
                source_manifest=manifest, source_files=len(files),
                reference_receipt_sha256=sha(ref / 'receipt.json'),
                reference_source_manifest=receipt['source_manifest'], binary_sha256=sha(binary),
                cases=len(receipt['cases']), rows=receipt['rows'], native_runs=len(completed),
                outputs=outputs, uncompared_fields=['unselected chip/voice/gate/LFO/envelope work fields'],
                scope=__doc__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hdi', type=Path)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--ticks', type=int, default=384)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if bool(args.hdi) == bool(args.reference) or bool(args.reference) != bool(args.binary):
        raise ValueError('choose --hdi producer or --reference and --binary consumer')
    if not 384 <= args.ticks <= 4096:
        raise ValueError('bounded sequence replay requires384..4096 music ticks')
    root = Path(__file__).resolve().parents[1]
    manifest, files = source_manifest(root)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    receipt = produce(args, root, out, manifest, files) if args.hdi else consume(args, root, out, manifest, files)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Original/native PMD Sequence controls PASS', receipt['rows'], 'rows')


if __name__ == '__main__':
    main()
