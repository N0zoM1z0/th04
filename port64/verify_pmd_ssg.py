#!/usr/bin/env python3
"""Original PMD built-in SSG effect state and ordered register writes.

Runs the three unchanged COM drivers. DOS/board/readback/injected interrupts
use the guarded auxiliary-driver adapter. Mixer values are explicit chip seam
inputs. No captured writes are used to implement the native player. This
accepts effect control/register behavior, not music registers, synthesis,
physical timing, frontend capability, full routes or original-byte equality.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import unicorn as U
from verify import source_manifest, require_elf_x86_64, require_pe_x86_64
from verify_pmd_driver import directory_files, install, DRIVERS, HDI_SHA
from verify_cutscene import ending_assets

REGISTERS = (4, 5, 6, 7, 10, 11, 12, 13)
# PSP-relative identities in each supplied flat COM. These are target analysis
# views; the native engine has no executable or absolute address dependency.
LAYOUT = {'PMD.COM': (0x320, 0x2db8, 0x88),
          'PMD86.COM': (0xd69, 0x3c83, 0x188),
          'PMDB2.COM': (0x968, 0x388c, 0x88)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def operations(mixer):
    result = [('M', mixer)]
    for effect in range(40):
        result += [('S', 0), ('P', effect)]
        result += [('T', 2)] * 8 + [('T', 0)] * 2 + [('T', 1)] * 64
        # Restart the same effect, alter other mixer bits during a sweep, then
        # exercise simultaneous flags and explicit stop at a sounding boundary.
        result += [('P', effect), ('M', mixer ^ 0xdb), ('T', 3), ('S', 0)]
        result += [('M', mixer)]
    result += [('P', 12), ('P', 0), ('P', 11), ('T', 1), ('P', 1)]
    result += [('T', 3)] * 64 + [('S', 0), ('T', 1)]
    return result


def original_state(d, name, binary):
    base, table, port = LAYOUT[name]
    raw = bytes(d.u.mem_read(d.load * 16 + base, 12))
    pointer, tone, step = struct.unpack_from('<HHh', raw)
    resource, cursor = -1, 0
    if pointer:
        for effect in range(40):
            start = table + struct.unpack_from('<H', binary, table - 256 + effect * 3 + 1)[0]
            end = start
            while binary[end - 256] != 255:
                end += 11
            if start <= pointer <= end and (pointer - start) % 11 == 0:
                resource, cursor = effect, (pointer - start) // 11
                break
        if resource == -1:
            raise ValueError('original SSG cursor outside bounded semantic segments')
    packed = raw[8]
    noise_step = packed >> 4
    if noise_step >= 8:
        noise_step -= 16
    row = [resource, cursor, tone, step, raw[6], raw[7], noise_step,
           packed & 15, raw[9], raw[10], raw[11]]
    row += [d.registers.get((port, r), 0) for r in REGISTERS]
    writes = []
    selected = None
    for _, address, size, value in d.ports:
        if size != 1:
            raise ValueError('unexpected SSG I/O size')
        if address == port:
            selected = value
        elif address == port + 2 and selected in REGISTERS:
            writes += [selected, value]
    row += [len(writes) // 2] + writes
    return row


def produce(args, root, out, manifest, files):
    binaries = directory_files(args.hdi)
    assets = ending_assets(args.hdi)
    outputs, cases, first = {}, [], {}
    for mixer in (0, 0x5a, 0xbf, 255):
        ops = operations(mixer)
        operation = out / f'operations-{mixer:02x}.txt'
        operation.write_text(''.join(f'{op} {value}\n' for op, value in ops))
        outputs[operation.name] = sha(operation)
        for load in (0x1000, 0x2000):
            for name in DRIVERS:
                d = install(binaries[name], name, load)
                song = 'OP.' + DRIVERS[name][3]
                d.write_resource(0x600, assets[song])
                d.service(0)
                d.service(0x100)
                path = out / f'{name}-{load:04x}-{mixer:02x}.txt'
                with path.open('w') as output:
                    for tick, (op, value) in enumerate(ops):
                        d.ticks = tick
                        d.ports = []
                        if op == 'P':
                            d.service(0x300 | value)
                        elif op == 'S':
                            d.service(0x400)
                        elif op == 'M':
                            d.registers[(LAYOUT[name][2], 7)] = value
                        else:
                            d.irq(value)
                        row = original_state(d, name, binaries[name])
                        output.write(' '.join(map(str, row)) + '\n')
                outputs[path.name] = sha(path)
                key = mixer
                if key not in first:
                    first[key] = outputs[path.name]
                elif outputs[path.name] != first[key]:
                    raise ValueError('SSG effect control/register dialect or relocated replay differs')
                cases.append(dict(driver=name, load=f'{load:04x}', mixer=mixer,
                                  operations=operation.name, output=path.name,
                                  rows=len(ops), song_sha256=hashlib.sha256(assets[song]).hexdigest()))
                print(f'Original SSG {name} load{load:04x} mixer{mixer:02x}: {len(ops)}rows PASS', flush=True)
    return dict(cases=cases, outputs=outputs, rows=sum(c['rows'] for c in cases),
                drivers={n:dict(size=len(binaries[n]), sha256=hashlib.sha256(binaries[n]).hexdigest(),
                               state=f'PSP:{LAYOUT[n][0]:04x}', bank=f'PSP:{LAYOUT[n][1]:04x}') for n in DRIVERS},
                hdi_sha256=HDI_SHA, unicorn_version=U.__version__,
                unicorn_engine_sha256=sha(Path(U.unicorn._uc._name)))


def compare(args, root, out, manifest, files):
    reference = args.reference.resolve()
    producer = json.loads((reference / 'receipt.json').read_text())
    if not producer['passed'] or len(producer['cases']) != 24:
        raise ValueError('incomplete original SSG producer')
    for name, digest in producer['outputs'].items():
        if sha(reference / name) != digest:
            raise ValueError('original SSG reference changed: ' + name)
    binary = args.binary.resolve()
    identity = require_pe_x86_64(binary) if binary.suffix.lower() == '.exe' else require_elf_x86_64(binary)
    outputs, count, runs = {}, 0, {}
    for case in producer['cases']:
        mixer = case['mixer']
        if mixer not in runs:
            output = out / f'native-{mixer:02x}.txt'
            subprocess.run([str(binary), str(reference / case['operations']), str(output)], check=True)
            outputs[output.name] = sha(output)
            runs[mixer] = output.read_bytes()
        expected = (reference / case['output']).read_bytes()
        if runs[mixer] != expected:
            actual = runs[mixer].decode().splitlines()
            original = expected.decode().splitlines()
            for index, (a, b) in enumerate(zip(actual, original)):
                if a != b:
                    raise ValueError(f'SSG {case["output"]} row{index}: expected {b}; native {a}')
            raise ValueError('SSG native/reference row count differs')
        count += case['rows']
    return dict(rows=count, native_runs=len(runs), binary_sha256=sha(binary), binary_identity=identity,
                outputs=outputs, reference_receipt_sha256=sha(reference / 'receipt.json'),
                reference_source_manifest=producer['source_manifest'])


def sharing_song(effect, rest):
    # Construct a bounded PC-98 resource from its documented directory and
    # note/rhythm format. Original executable bytes are never changed. The
    # supplied songs leave channel C to drums, so this fixture challenges
    # music/drum handover which their ordinary control corpus does not reach.
    data = bytearray(25)
    data[0] = 0
    def append(part, stream):
        struct.pack_into('<H', data, 1 + 2 * part, len(data) - 1)
        data.extend(stream)
    for part in range(11):
        phrase = [0x80]
        if part == 8:
            phrase = ([0x4f, 2, 0x4f, 2] if rest else [0x40, 2, 0x41, 2])
            phrase += [0xda, 0x42, 0x46, 4, 0x43, 2, 0x80]
        elif part == 10:
            phrase = [0, 0x80]
        append(part, phrase)
    table = len(data)
    struct.pack_into('<H', data, 23, table - 1)
    data.extend(struct.pack('<H', table + 1))
    mask = 1 << effect
    data.extend([0x80 | (mask >> 8), mask & 255, 8, 255])
    return bytes(data)


def produce_sharing(args, root, out, manifest, files):
    from verify_pmd_sequence import original_state as music_state
    binaries = directory_files(args.hdi)
    ops = [('I', 3)] * 64 + [('S', 0)] + [('I', 3)] * 64
    ops += [('R', 0)] + [('I', 2)] * 8 + [('I', 1)] * 16 + [('I', 3)] * 64
    operation = out / 'operations.txt'
    operation.write_text(''.join(f'{op} {value}\n' for op, value in ops))
    outputs, cases = {operation.name: sha(operation)}, []
    for label, effect, rest in [('drum-note', 0, False), ('effect-note', 11, False), ('drum-rest', 1, True)]:
        song = out / (label + '.M26')
        song.write_bytes(sharing_song(effect, rest))
        outputs[song.name] = sha(song)
        for load in (0x1000, 0x2000):
            for name in DRIVERS:
                d = install(binaries[name], name, load)
                d.write_resource(0x600, song.read_bytes())
                d.service(0)
                path = out / f'{name}-{load:04x}-{label}.txt'
                def row():
                    return music_state(d) + original_state(d, name, binaries[name])[:11]
                with path.open('w') as output:
                    output.write(' '.join(map(str, row())) + '\n')
                    for tick, (op, value) in enumerate(ops):
                        d.ticks = tick
                        if op == 'I':
                            d.irq(value)
                        else:
                            d.service(0x100 if op == 'S' else 0)
                        output.write(' '.join(map(str, row())) + '\n')
                outputs[path.name] = sha(path)
                cases.append(dict(driver=name, load=load, board=DRIVERS[name][2],
                                  song=song.name, reference=path.name, rows=len(ops)+1))
                print(f'Original SSG/music sharing {name} load{load:04x} {label} PASS', flush=True)
    return dict(variant='ssg-song-sharing', cases=cases, rows=sum(c['rows'] for c in cases),
                hdi_sha256=HDI_SHA, outputs=outputs, command_format='constructed synthetic music, original executable',
                unicorn_version=U.__version__, unicorn_engine_sha256=sha(Path(U.unicorn._uc._name)))


def compare_sharing(args, root, out, manifest, files):
    ref = args.reference.resolve()
    receipt = json.loads((ref / 'receipt.json').read_text())
    if not receipt['passed'] or receipt.get('variant') != 'ssg-song-sharing' or len(receipt['cases']) != 18:
        raise ValueError('incomplete original SSG sharing producer')
    for name, digest in receipt['outputs'].items():
        if sha(ref / name) != digest:
            raise ValueError('SSG sharing reference changed')
    binary = args.binary.resolve()
    require_pe_x86_64(binary) if binary.suffix.lower() == '.exe' else require_elf_x86_64(binary)
    outputs, runs = {}, {}
    for c in receipt['cases']:
        key = c['driver'], c['song']
        if key not in runs:
            path = out / (c['driver'] + '-' + c['song'] + '.txt')
            subprocess.run([str(binary), str(ref/c['song']), str(c['board']), str(ref/'operations.txt'), str(path), 'ssg'], check=True)
            outputs[path.name] = sha(path)
            runs[key] = path.read_text().splitlines()
        expected = (ref/c['reference']).read_text().splitlines()
        actual = runs[key]
        if expected != actual:
            for n, (e, a) in enumerate(zip(expected, actual)):
                if e != a:
                    diff = [(i, x, y) for i, (x, y) in enumerate(zip(e.split(), a.split())) if x != y]
                    raise ValueError(f'SSG sharing {c} row{n}: {diff}')
            raise ValueError('SSG sharing row count differs')
    return dict(variant='ssg-song-sharing', rows=receipt['rows'], cases=18, native_runs=len(runs), outputs=outputs,
                binary_sha256=sha(binary), reference_receipt_sha256=sha(ref/'receipt.json'),
                reference_source_manifest=receipt['source_manifest'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hdi', type=Path)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sharing', action='store_true', help='challenge music/drum channel handover using constructed music')
    args = parser.parse_args()
    if bool(args.hdi) == bool(args.reference) or (args.reference and not args.binary):
        parser.error('provide --hdi or --reference with --binary')
    root = Path(__file__).resolve().parents[1]
    manifest, files = source_manifest(root)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    if args.sharing:
        receipt = produce_sharing(args, root, out, manifest, files) if args.hdi else compare_sharing(args, root, out, manifest, files)
    else:
        receipt = produce(args, root, out, manifest, files) if args.hdi else compare(args, root, out, manifest, files)
    if source_manifest(root)[0] != manifest:
        raise ValueError('source changed during SSG replay')
    receipt.update(passed=True, source_manifest=manifest, source_files=len(files),
                   utc=datetime.now(timezone.utc).isoformat(), command=sys.argv, scope=__doc__)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('PMD SSG effect state and ordered register writes PASS', receipt['rows'])


if __name__ == '__main__':
    main()
