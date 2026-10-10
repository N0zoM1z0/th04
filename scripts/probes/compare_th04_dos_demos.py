#!/usr/bin/env python3
"""Fail-closed logical-frame input/score/RNG comparison of complete DOS demos."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from capture_th04_dos_demos import ARCHIVES, FIELDS, Fat12, parse_archive, sha, u16, u32


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def relocated_module(main: bytes, load: int) -> bytes:
    header = int.from_bytes(main[8:10], 'little')*16
    result = bytearray(main[header:])
    count = int.from_bytes(main[6:8], 'little')
    table = int.from_bytes(main[24:26], 'little')
    for i in range(count):
        offset = int.from_bytes(main[table+i*4:table+i*4+2], 'little')
        segment = int.from_bytes(main[table+i*4+2:table+i*4+4], 'little')
        at = segment*16+offset
        require(at+2 <= len(result), 'relocation outside MAIN')
        word = (int.from_bytes(result[at:at+2], 'little')+load)&65535
        result[at:at+2] = word.to_bytes(2, 'little')
    return bytes(result)


def load_capture(directory: Path) -> tuple[dict, dict[int, list[dict]], dict]:
    receipt = json.loads((directory / 'receipt.json').read_text())
    require(receipt['capture_complete'] and not receipt['timeout'] and receipt['exit_code'] == 0,
            'capture incomplete/timeout/nonzero exit')
    require(receipt['demos'] in (1, 4), 'unsupported demo extent')
    prof_bytes = (directory / 'profile.json').read_bytes()
    require(sha(prof_bytes) == receipt['profile_json_sha256'], 'profile JSON identity drift')
    prof = json.loads(prof_bytes)
    require(prof['boundary'] == 'after-demo-before-update-v1', 'logical boundary mismatch')
    raw = (directory / 'raw.txt').read_bytes()
    require(sha(raw) == receipt['raw_sha256'], 'raw trace identity drift')
    main = Path(receipt['main_path']).read_bytes()
    require(sha(main) == receipt['main_sha256'], 'captured MAIN identity drift')
    require(sha((directory / 'observer-profile.txt').read_bytes()) == receipt['profile_sha256'],
            'observer profile identity drift')
    initial = (directory / 'prepared/diagnostic.hdi').read_bytes()
    require(sha(initial) == receipt['initial_hdi_sha256'],
            'initial image identity drift')
    require(sha((directory / 'execution.hdi').read_bytes()) == receipt['final_hdi_sha256'], 'final image identity drift')
    fs = Fat12(bytearray(initial))
    entry = fs.find_entry([fs.root], b'GENSO      ')
    offsets = [fs.cluster_offset(k) for k in fs.chain(u16(fs.image, entry+26))]
    for name, record in receipt['starting_files'].items():
        entry = fs.find_entry(offsets, name.encode('ascii'))
        data = fs.file_bytes(u16(fs.image, entry+26), u32(fs.image, entry+28))
        require(len(data) == record['size'] and sha(data) == record['sha256'] and data.hex() == record['hex'],
                'starting file independent readback mismatch')
    for product, filename in dict(main='MAIN    EXE', op='OP      EXE', maine='MAINE   EXE', zun='ZUN     COM').items():
        entry = fs.find_entry(offsets, filename.encode('ascii'))
        data = fs.file_bytes(u16(fs.image, entry+26), u32(fs.image, entry+28))
        record = receipt['products'][product]
        require(len(data) == record['size'] and sha(data) == record['sha256'], 'product independent readback mismatch')
        if product == 'main':
            require(data == main, 'initial MAIN differs from observed executable')
    entry = fs.find_entry(offsets, ARCHIVES['main']['fat_name'])
    archive = fs.file_bytes(u16(fs.image, entry+26), u32(fs.image, entry+28))
    require(len(archive) == ARCHIVES['main']['size']
            and sha(archive) == ARCHIVES['main']['sha256'] == receipt['archive_sha256'],
            'initial MAIN archive identity drift')
    _, assets = parse_archive(archive, 'main', ARCHIVES['main'])
    require(sha((directory / 'dosbox-x.conf').read_bytes()) == receipt['config_sha256'], 'config identity drift')
    require(sha((directory / 'FREECG98.BMP').read_bytes()) == receipt['font_sha256'], 'font identity drift')
    demo_bytes = {}
    for number in range(1, 5):
        data = (directory / f'DEMO{number}.REC').read_bytes()
        require(len(data) == 8000 and sha(data) == receipt['demo_sha256'][str(number)]
                and data == assets[f'DEMO{number}.REC'], 'replay identity drift')
        demo_bytes[number] = data
    captures, diagnostics = validate_trace(raw, main, prof, demo_bytes, receipt['demos'])
    return receipt, captures, diagnostics


def validate_trace(raw: bytes, main: bytes, prof: dict, demo_bytes: dict[int, bytes], expected_demos: int):
    names = [f[0] for f in prof['fields']]
    require(names == [f[0] for f in FIELDS], 'capture field schema drift')
    require([f[2] for f in prof['fields']] == [f[3] for f in FIELDS], 'capture field width schema drift')
    captures = {}
    process = 0
    frame = 0
    current = []
    counts = Counter()
    loads = []
    base_counts = None
    load_segment = None
    terminal = False
    events = []
    for line_number, line in enumerate(raw.decode('ascii').splitlines(), 1):
        cells = line.split()
        require(bool(cells), f'empty raw row {line_number}')
        kind = cells[0]
        if kind == 'L':
            require(len(cells) == 6 and (process == 0 or terminal), 'duplicate/unterminated MAIN load')
            process += 1
            require(int(cells[1]) == process and process <= expected_demos, 'MAIN load order')
            load_segment = int(cells[2], 16)
            require(bytes.fromhex(cells[5]) == relocated_module(main, load_segment), 'loaded MAIN relocation/bytes mismatch')
            loads.append(dict(process=process, load_segment=load_segment, cr0=int(cells[3], 16), cr3=int(cells[4], 16)))
            frame = 0
            current = []
            counts = Counter()
            base_counts = None
            terminal = False
            events = []
        elif kind == 'R':
            require(len(cells) == 9 and process > 0 and not terminal and int(cells[1]) == process, 'RNG event order')
            hook_index = int(cells[2])
            require(2 <= hook_index < len(prof['hooks']), 'RNG hook index')
            hook_kind, segment, offset = prof['hooks'][hook_index]
            require(hook_kind in (3, 4) and int(cells[3], 16) == load_segment+segment
                    and int(cells[4], 16) == offset, 'RNG address mismatch')
            counts['lcg_calls' if hook_kind == 3 else 'ring_calls'] += 1
            # These six guarded helpers are near calls. Their first stack word
            # after the return IP is the mask/divisor for and/mod variants.
            events.append([hook_index, int(cells[8], 16) if hook_index in (4, 5, 7, 8) else None])
        elif kind in ('I', 'T'):
            require(len(cells) == 8+len(names) and process > 0 and not terminal
                    and int(cells[1]) == process, 'frame row shape/order')
            hook_kind, segment, offset = prof['hooks'][0 if kind == 'I' else 1]
            require(int(cells[2], 16) == load_segment+segment and int(cells[3], 16) == offset
                    and int(cells[4], 16) == load_segment+prof['dgroup'], 'frame address/DGROUP mismatch')
            require(int(cells[5]) == counts['lcg_calls'] and int(cells[6]) == counts['ring_calls'],
                    'RNG counters disagree with complete caller log')
            values = {}
            for name, _, size in prof['fields']:
                cell = cells[7+len(values)]
                require(len(cell) == size*2 and len(bytes.fromhex(cell)) == size, f'field width: {name}')
                values[name] = cell
            resident = bytes.fromhex(cells[-1])
            require(len(resident) == 80 and resident[:11] == b'HUMAConfig\0', 'resident identity/width')
            number = resident[0x3e]
            require(number == process, 'demo rotation/order')
            numeric_frame = int.from_bytes(bytes.fromhex(values['frame']), 'little')
            require(numeric_frame == frame, f'missing/duplicate/out-of-order frame: {numeric_frame} expected {frame}')
            require(kind == ('T' if frame == 3996 else 'I'), 'terminal update/decision mismatch')
            replay = demo_bytes[number]
            require(values['input'] == bytes((replay[frame], 0)).hex()
                    and values['shift_raw'] == bytes((replay[4000+frame],)).hex(), 'consumed replay input mismatch')
            require(int(values['stage'], 16) == (3, 0, 2, 1)[number-1], 'demo stage mismatch')
            require(resident[0x12] == (48, 49, 48, 49)[number-1]
                    and resident[0x19] == int(number >= 3), 'demo character/shot mismatch')
            if base_counts is None:
                base_counts = counts.copy()
            row = {k:v for k,v in values.items() if k != 'resident_pointer'}
            row.update(demo=number, decision=kind,
                       lcg_calls=counts['lcg_calls']-base_counts['lcg_calls'],
                       ring_calls=counts['ring_calls']-base_counts['ring_calls'],
                       lcg_total_calls=counts['lcg_calls'], ring_total_calls=counts['ring_calls'],
                       rng_events=events,
                       lives=resident[0x0b], bombs=resident[0x0d], credit=resident[0x0e],
                       misses=resident[0x31], bombs_used=resident[0x32])
            current.append(row)
            events = []
            frame += 1
            if kind == 'T':
                require(len(current) == 3997, 'truncated demo')
                captures[number] = current
                terminal = True
        else:
            raise ValueError(f'unknown trace row: {kind}')
    require(terminal and len(captures) == expected_demos, 'missing completed demo/terminal row')
    diagnostics = dict(loads=loads, demos={str(n):dict(rows=len(rows),
        sha256=sha(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode())) for n,rows in captures.items()})
    return captures, diagnostics


def compare(left: Path, right: Path) -> dict:
    try:
        a, ar, ad = load_capture(left)
        b, br, bd = load_capture(right)
        for key in ('demos', 'original_hdi_sha256', 'starting_files', 'demo_sha256', 'archive_sha256',
                    'font_sha256', 'config_sha256', 'emulator_sha256', 'observer_source_sha256'):
            require(a[key] == b[key], f'paired reset/observer mismatch: {key}')
        require(a['role'] == 'original' and b['role'] in ('original', 'ordinary-reconstructed'), 'comparison roles')
        result = dict(passed=True, scope='complete bundled-demo consumed input, score and RNG at before-update boundary',
                      left=ad, right=bd, demos=a['demos'], gameplay_rows=a['demos']*3996,
                      terminal_rows=a['demos'], first_difference=None, demo_results={})
        for number in ar:
            demo_result = dict(passed=True, equal_boundaries=3997, first_difference=None)
            for index, (x, y) in enumerate(zip(ar[number], br[number], strict=True)):
                if x != y:
                    differences = {key:dict(original=x[key], candidate=y[key]) for key in x if x[key] != y[key]}
                    first = dict(demo=number, frame=index, fields=differences)
                    demo_result.update(passed=False, equal_boundaries=index, first_difference=first)
                    result['passed'] = False
                    if result['first_difference'] is None:
                        result['first_difference'] = first | dict(
                            original_context=ar[number][max(0,index-2):index+3],
                            candidate_context=br[number][max(0,index-2):index+3])
                    break
            result['demo_results'][str(number)] = demo_result
        return result
    except (ValueError, KeyError, IndexError, TypeError, OSError, UnicodeError) as error:
        return dict(passed=False, invalid_capture=str(error), first_difference=None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = compare(args.original.resolve(), args.candidate.resolve())
    result.update(original_receipt_sha256=sha((args.original / 'receipt.json').read_bytes()),
                  candidate_receipt_sha256=sha((args.candidate / 'receipt.json').read_bytes()))
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('left', 'right', 'first_difference')}
                     | dict(first_difference=None if result.get('first_difference') is None else
                            {k:v for k,v in result['first_difference'].items() if k.endswith('context') is False})))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
