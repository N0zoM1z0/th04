#!/usr/bin/env python3
"""Admit ordinary DOS prefixes before comparing game state.

This gate requires identical consumed input and initial RNG. A rejected pair
does not establish a reconstruction mismatch. Runtime addresses and resident
performance counters remain raw evidence outside the compared fields.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import tomllib

from capture_th04_dos_demos import ARCHIVES, Fat12, ROOT, map_symbols, profile, sha, u16, u32
from compare_th04_dos_demos import relocated_module, require
from th04_demo_globals import attest_fields


def validate_keyboard_capture(clock: dict, first: dict, resident: str) -> None:
    actions = clock['actions']
    require(clock['requested_seed'] == 64 and actions, 'keyboard scenario/extent')
    require(actions[0]['key'] == 'KBD_enter' and actions[0]['pressed'] is True,
            'keyboard start selection')
    require(actions[-1]['key'] == 'KBD_z' and actions[-1]['pressed'] is True,
            'keyboard gameplay Shot')
    previous = -1
    for action in actions:
        require(action['tick'] >= previous and action['due'] <= action['tick'], 'keyboard virtual ordering')
        require(action['key'] in ('KBD_enter', 'KBD_z') and isinstance(action['pressed'], bool),
                'keyboard event ownership')
        require(action['resident_seed'] == 64, 'keyboard observed menu seed')
        guard = action['unchanged_guest']
        require(re.fullmatch('[0-9a-f]{64}', guard['conventional_sha256']) is not None and
                len(bytes.fromhex(guard['cpu_regs'])) == 48 and
                len(bytes.fromhex(guard['segments'])) == 136, 'keyboard guest snapshot extent')
        previous = action['tick']
    raw = bytes.fromhex(resident)
    pointer = bytes.fromhex(first['resident_pointer'])
    address = int.from_bytes(pointer[:2], 'little') + int.from_bytes(pointer[2:], 'little') * 16
    require(clock['resident_linear'] == address and int.from_bytes(raw[20:24], 'little') == 64,
            'keyboard resident ownership/entry seed')
    registers = bytes.fromhex(actions[0]['unchanged_guest']['cpu_regs'])
    segments = bytes.fromhex(actions[0]['unchanged_guest']['segments'])
    cs = int.from_bytes(segments[8:16], 'little')
    ds = int.from_bytes(segments[24:32], 'little')
    es = int.from_bytes(segments[:8], 'little')
    bx = int.from_bytes(registers[12:16], 'little') & 65535
    ip = int.from_bytes(registers[32:36], 'little') & 65535
    require(cs >= 0x0a74 and ip == 0x0d2f and ds == cs - 0x0a74 + 0x0f34 and
            es * 16 + bx == address, 'original OP counter instruction/context')


def ordinary_profile(main: bytes, original: bytes, map_path: Path | None, end_after=None) -> dict:
    candidate = main if map_path else original
    result = profile(main, map_path)
    result['hooks'] = list(result['hooks'])
    segment, offset = result['hooks'][0][1:]
    header = int.from_bytes(main[8:10], 'little') * 16
    at = header + segment * 16 + offset + 5
    require(main[at:at + 2] == b'\x74\x0c', 'ordinary terminal branch drift')
    result['hooks'][1] = (2, segment, offset + 5)
    result['boundary'] = 'ordinary-pre-update-through-frame-3996'
    result['terminal_bytes'] = '740c'
    if map_path:
        extents, witnesses = attest_fields(original, candidate, map_symbols(map_path), result['dgroup'])
        extra = [(name, right, size) for name, _, right, _, size in extents]
        result['witnesses'] = witnesses
    else:
        from th04_demo_globals import FIELDS
        require(sha(original) == '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b',
                'original identity drift')
        for name, _, _, seg, ip, pattern, *_ in FIELDS:
            start = 6144 + seg * 16 + ip
            require(original[start:start + len(bytes.fromhex(pattern))] == bytes.fromhex(pattern),
                    f'original field witness: {name}')
        extra = [(name, offset, size) for name, offset, size, *_ in FIELDS]
    names = {field[0] for field in result['fields']}
    result['fields'][-1:-1] = [field for field in extra if field[0] not in names]
    if end_after is not None:
        require(isinstance(end_after, int) and 1 <= end_after <= 65535, 'bounded frame WORD')
        guarded = profile(main, map_path)
        result['hooks'][1] = guarded['hooks'][1]
        result['terminal_bytes'] = guarded['terminal_bytes']
        result['boundary'] = 'ordinary-bounded-after-update-v2'
        result['end_after'] = end_after
    return result


def load(directory: Path, original: bytes, source_snapshot: Path | None = None) -> dict:
    receipt = json.loads((directory / 'receipt.json').read_text())
    require(receipt['complete'] and receipt['exit'] == 0, 'capture incomplete')
    for path, digest in receipt['files'].items():
        require(sha((directory / path).read_bytes()) == digest, f'capture identity: {path}')
    main = Path(receipt['main_path']).read_bytes()
    require(sha(main) == receipt['main_sha256'], 'MAIN identity drift')
    initial = (directory / 'prepared/diagnostic.hdi').read_bytes()
    require(sha(initial) == receipt['initial_hdi_sha256'], 'initial image identity drift')
    require(sha((directory / 'execution.hdi').read_bytes()) == receipt['final_hdi_sha256'],
            'final image identity drift')
    filesystem = Fat12(bytearray(initial))
    entry = filesystem.find_entry([filesystem.root], b'GENSO      ')
    offsets = [filesystem.cluster_offset(k) for k in filesystem.chain(u16(filesystem.image, entry + 26))]
    def image_file(name):
        entry = filesystem.find_entry(offsets, name)
        return filesystem.file_bytes(u16(filesystem.image, entry + 26), u32(filesystem.image, entry + 28))
    targets = tomllib.loads((ROOT / 'config/targets.toml').read_text())['artifacts']
    for product, name in [('main', b'MAIN    EXE'), ('op', b'OP      EXE'),
                          ('maine', b'MAINE   EXE'), ('zun', b'ZUN     COM')]:
        data = image_file(name)
        target = next(target for target in targets if target['id'] == 'th04-' + product)
        require(data == main if product == 'main' else
                len(data) == target['size'] and sha(data) == target['sha256'], 'executed product: ' + product)
    for artifact in ARCHIVES.values():
        data = image_file(artifact['fat_name'])
        require(len(data) == artifact['size'] and sha(data) == artifact['sha256'], 'game-data archive drift')
    starting_files = {name.decode(): image_file(name).hex() for name in (b'MIKO    CFG', b'GENSOU  SCR')}
    config = bytes.fromhex(starting_files['MIKO    CFG'])
    require(len(config) == 10 and config[:6] == bytes.fromhex('010600020101') and
            config[9] == sum(config[:6]) & 255, 'starting legal options/checksum')
    map_path = Path(receipt['map_path']) if receipt['role'] == 'candidate' else None
    if map_path:
        require(sha(map_path.read_bytes()) == receipt['map_sha256'], 'MAP identity drift')
    actual = json.loads((directory / 'profile.json').read_text())
    bounded = receipt.get('end_after')
    expected = ordinary_profile(main, original, map_path, bounded)
    # The original producer recorded candidate witnesses as extra provenance.
    if not map_path:
        actual.pop('witnesses', None)
    require(actual == json.loads(json.dumps(expected)), 'profile differs from attested instructions')
    fields = expected['fields']
    names = [field[0] for field in fields]
    rows, resident_rows, events, pending = [], [], [], []
    counts = Counter()
    load_segment = None
    terminal = False
    for line in (directory / 'raw.txt').read_text().splitlines():
        cells = line.split()
        kind = cells[0]
        require(not terminal, 'events after terminal')
        if kind == 'L':
            require(load_segment is None and len(cells) == 6 and cells[1] == '1', 'MAIN process extent')
            load_segment = int(cells[2], 16)
            require(bytes.fromhex(cells[-1]) == relocated_module(main, load_segment), 'loaded module drift')
        elif kind == 'R':
            require(load_segment is not None and len(cells) == 9 and cells[1] == '1', 'RNG event shape')
            index = int(cells[2])
            require(2 <= index < len(expected['hooks']), 'RNG hook index')
            hook, segment, offset = expected['hooks'][index]
            require(int(cells[3], 16) == load_segment + segment and int(cells[4], 16) == offset,
                    'RNG hook address')
            counts['lcg' if hook == 3 else 'ring'] += 1
            pending.append([index, int(cells[8], 16) if index in (4, 5, 7, 8) else None])
        elif kind in ('I', 'T'):
            require(load_segment is not None and len(cells) == len(fields) + 8 and cells[1] == '1',
                    'frame shape/process')
            _, segment, offset = expected['hooks'][0 if kind == 'I' else 1]
            require([int(x, 16) for x in cells[2:5]] ==
                    [load_segment + segment, offset, load_segment + expected['dgroup']], 'frame address')
            require([int(x) for x in cells[5:7]] == [counts['lcg'], counts['ring']], 'RNG event counters')
            values = {}
            for (name, _, size), value in zip(fields, cells[7:-1]):
                require(len(value) == size * 2 and len(bytes.fromhex(value)) == size, f'field width: {name}')
                values[name] = value
            resident = bytes.fromhex(cells[-1])
            require(len(resident) == 80 and resident[:11] == b'HUMAConfig\0' and resident[0x3e] == 0,
                    'ordinary resident identity')
            frame = int.from_bytes(bytes.fromhex(values['frame']), 'little')
            if kind == 'I':
                require(frame == len(rows), 'noncontiguous ordinary prefix')
                rows.append(values)
                resident_rows.append(resident.hex())
                events.append(pending)
                pending = []
            else:
                require(bounded is None, 'Demo terminal in bounded ordinary run')
                require(frame == 3996 and len(rows) == 3997 and values == rows[-1] and not pending,
                        'ordinary terminal extent')
                terminal = True
        else:
            raise ValueError('unknown trace event')
    bounded_terminal = None
    if bounded is None:
        require(terminal and len(rows) == 3997, 'missing terminal')
    else:
        require('ordinary-terminal.json' in receipt['files'] and not terminal and
                len(rows) == bounded, 'bounded sample/terminal extent')
        require(receipt['termination'] == 'observed-after-update-prefix' and
                receipt['natural_game_exit'] is False, 'bounded termination class')
        bounded_terminal = json.loads((directory / 'ordinary-terminal.json').read_text())
        validate_bounded_terminal(bounded_terminal, main, expected, load_segment, counts)
    if 'adapter_sha256' in receipt:
        require('clock-input.json' in receipt['files'], 'missing pinned keyboard record')
        validate_keyboard_capture(json.loads((directory / 'clock-input.json').read_text()),
                                  rows[0], resident_rows[0])
        for path, digest in receipt['source_files'].items():
            live = Path(path)
            observed = sha(live.read_bytes()) if live.is_file() else None
            if observed != digest and source_snapshot is not None and live.is_relative_to(ROOT):
                frozen = source_snapshot / live.relative_to(ROOT)
                observed = sha(frozen.read_bytes()) if frozen.is_file() else None
            require(observed == digest, 'keyboard source identity drift: ' + path)
    return dict(receipt=receipt, fields=names, rows=rows, resident=resident_rows, events=events,
                starting_files=starting_files, bounded_terminal=bounded_terminal, terminal_events=pending)


def validate_bounded_terminal(terminal, main, profile, load, counts):
    require(terminal['schema_version'] == 1 and terminal['complete_prefix'] is True and
            terminal['natural_game_exit'] is False and
            terminal['boundary'] == 'ordinary stage_frame write, before mod counters and score update',
            'bounded terminal class/boundary')
    require(terminal['frame'] == profile['end_after'] and terminal['load_segment'] == load and
            terminal['dgroup_segment'] == load + profile['dgroup'], 'bounded terminal extent/address')
    require(terminal['lcg_calls'] == counts['lcg'] and terminal['ring_calls'] == counts['ring'],
            'bounded terminal RNG counters')
    values = terminal['values']
    require(set(values) == {name for name, _, _ in profile['fields']}, 'bounded terminal fields')
    for name, _, size in profile['fields']:
        require(len(bytes.fromhex(values[name])) == size, 'bounded terminal field width: ' + name)
    require(int.from_bytes(bytes.fromhex(values['frame']), 'little') == profile['end_after'] and
            values['stage'] == '00', 'bounded terminal frame/stage')
    resident = bytes.fromhex(terminal['resident'])
    require(len(resident) == 80 and resident[:11] == b'HUMAConfig\0' and resident[62] == 0,
            'bounded ordinary resident')
    segment, seam = profile['hooks'][0][1:]
    require(terminal['cs'] == load + segment and seam - 0x1f <= terminal['ip'] < seam - 0x1f + 0x300,
            'bounded terminal gameplay owner')
    module = relocated_module(main, load)
    at = segment * 16 + terminal['ip']
    opcode = bytes.fromhex(terminal['opcode'])
    frame_offset = profile['fields'][0][1]
    require(len(opcode) == 16 and module[at:at + 16] == opcode and
            opcode[:3] == b'\xa3' + frame_offset.to_bytes(2, 'little'), 'bounded terminal frame-store opcode')
    registers, segments = bytes.fromhex(terminal['cpu_regs']), bytes.fromhex(terminal['segments'])
    require(len(registers) == 48 and len(segments) == 136 and
            int.from_bytes(registers[32:36], 'little') & 65535 == terminal['ip'] and
            int.from_bytes(segments[8:16], 'little') == terminal['cs'], 'bounded CPU terminal context')


def admit(left: dict, right: dict) -> list[str]:
    reasons = []
    require(left['fields'] == right['fields'] and len(left['rows']) == len(right['rows']), 'pair extent')
    for field in ('input', 'shift_raw', 'stage'):
        if any(a[field] != b[field] for a, b in zip(left['rows'], right['rows'])):
            reasons.append('consumed-' + field)
    for field in ('lcg', 'ring', 'ring_cursor'):
        if left['rows'][0][field] != right['rows'][0][field]:
            reasons.append('initial-' + field)
    # Resident settings and entry seed are fixture inputs, not comparable outputs.
    a, b = (bytes.fromhex(capture['resident'][0]) for capture in (left, right))
    if a[:0x1d] != b[:0x1d] or a[0x3a:0x40] != b[0x3a:0x40]:
        reasons.append('initial-resident-settings-seed')
    return reasons


def compare(left: dict, right: dict) -> dict:
    reasons = admit(left, right)
    result = dict(admitted=not reasons, rejection_reasons=reasons, passed=False, first_difference=None,
                  complete_updates=len(left['rows']) if left.get('bounded_terminal') else len(left['rows']) - 1,
                  sampled_frames=len(left['rows']),
                  scope='Ordinary pre-update fields and RNG calls; no full actor pools, pixels, timing or campaign acceptance')
    if reasons:
        return result
    fields = [name for name in left['fields'] if name != 'resident_pointer']
    for frame, (a, b) in enumerate(zip(left['rows'], right['rows'])):
        for field in fields:
            if a[field] != b[field]:
                result['first_difference'] = dict(frame=frame, field=field, original=a[field], candidate=b[field])
                return result
        if left['events'][frame] != right['events'][frame]:
            result['first_difference'] = dict(frame=frame, field='ordered-rng-calls')
            return result
    result['passed'] = True
    if left.get('bounded_terminal') or right.get('bounded_terminal'):
        require(left.get('bounded_terminal') and right.get('bounded_terminal'), 'mixed terminal contracts')
        if left['terminal_events'] != right['terminal_events']:
            result.update(passed=False, first_difference=dict(frame=len(left['rows']), field='terminal-rng-calls'))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original_capture', type=Path)
    parser.add_argument('candidate_capture', type=Path)
    parser.add_argument('--original-main', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    original = args.original_main.read_bytes()
    left, right = load(args.original_capture, original), load(args.candidate_capture, original)
    require(left['receipt']['role'] == 'original' and right['receipt']['role'] == 'candidate', 'pair roles')
    require(left['receipt']['emulator_receipt_sha256'] == right['receipt']['emulator_receipt_sha256'],
            'emulator differs')
    require(left['starting_files'] == right['starting_files'], 'starting physical files differ')
    require(left['receipt']['files']['dosbox-x.conf'] == right['receipt']['files']['dosbox-x.conf'],
            'emulator config differs')
    if 'adapter_sha256' in left['receipt'] or 'adapter_sha256' in right['receipt']:
        for key in ('adapter_sha256', 'walker_sha256', 'debugger_sha256', 'font_sha256'):
            require(left['receipt'].get(key) == right['receipt'].get(key), 'keyboard producer differs: ' + key)
    result = compare(left, right)
    result['capture_receipts'] = {str(directory): sha((directory / 'receipt.json').read_bytes())
                                  for directory in (args.original_capture, args.candidate_capture)}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
