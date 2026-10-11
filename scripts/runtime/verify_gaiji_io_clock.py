#!/usr/bin/env python3
"""Verify original OP Gaiji transfers and emulator-specific elapsed I/O work.

Accept only complete, pinned, read-only captures ending at OP 0A74:0C79.
Replay complete GDC streams and reject mutated loads, cycles, port counts and
incomplete captures. These are DOSBox-X observations, not physical ISA/CGROM
measurements or default native startup equivalence.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path
import struct
import subprocess
from verify_op_loading_clock import ROOT, HEADER, PACKED_SHA, PAYLOAD_SHA, sha, require, pic, equal_load

POINTS = {
    'main_entry': (0xA74, 0xC37), 'gaiji_begin': (0xA74, 0xC6B),
    'backup_return': (0xA74, 0xC70), 'gaiji_end': (0xA74, 0xC79),
    'read_all_begin': (0, 0x1450), 'read_all_end': (0, 0x1471),
    'write_all_begin': (0, 0x14BE), 'write_all_end': (0, 0x14E1),
    'read_glyph': (0, 0x1408),
}
# Static target loops: 256 glyphs, 16 rows, two row selectors/data bytes.
PORT_COUNTS = {
    'read_all_begin': {('write', 0x68): 2, ('write', 0xA1): 256,
                       ('write', 0xA3): 256, ('write', 0xA5): 8192,
                       ('read', 0xA9): 8192},
    'write_all_begin': {('write', 0x68): 2, ('write', 0xA1): 256,
                        ('write', 0xA3): 256, ('write', 0xA5): 8192,
                        ('write', 0xA9): 8192},
}


def complete(directory: Path) -> tuple[dict, dict]:
    require((directory / 'startup-observation.json').is_file(), 'missing Gaiji completion')
    observation = json.loads((directory / 'startup-observation.json').read_text())
    wrapper = json.loads((directory / 'wrapper-receipt.json').read_text())
    require(wrapper['passed'] and wrapper['exit_code'] == 0 and wrapper['completion_observed'], 'wrapper completion')
    rows = observation['rows']
    require(observation['passed'] and observation['controlled_host_stop'] and
            len(rows) == 264 and rows[-1]['name'] == 'gaiji_end', 'bounded Gaiji completion')
    require(sha(directory / 'startup-observation.json') == wrapper['completion_sha256'], 'completion hash')
    require(sha(directory / 'capture.log') == wrapper['log_sha256'] and
            'OP_GAIJI_COMPLETE 264' in (directory / 'capture.log').read_text(), 'terminal marker')
    return observation, wrapper


def ports(window: dict, load: int) -> dict:
    counts = {(row['side'], row['port']): row['count'] for row in window['gaiji_counts']}
    require(len(counts) == len(window['gaiji_counts']) and counts == PORT_COUNTS[window['window']], 'Gaiji port count differs')
    complete_counts = {(row['side'], row['port'], row['cs']): row['count'] for row in window['counts']}
    require(len(complete_counts) == len(window['counts']), 'duplicate full I/O count')
    projection = {(side, port): count for (side, port, cs), count in complete_counts.items()
                  if cs == load and port in (0x68, 0xA1, 0xA3, 0xA5, 0xA9)}
    require(projection == counts, 'full I/O stream ownership differs')
    return counts


def clock_stream(directory: Path, observation: dict, load: int, output: Path, model: Path) -> dict:
    events = directory / 'video-clock-events.bin.gz'
    require(sha(events) == observation['clock_file_sha256'], 'clock stream hash')
    expanded = output / (directory.name + '-events.bin')
    counts, boundaries, verticals, load_seen = Counter(), 0, 0, False
    rows = observation['rows']
    with gzip.open(events, 'rb') as stream, expanded.open('xb') as target:
        require(stream.read(8) == b'TH04EP1\n', 'clock magic')
        while header := stream.read(HEADER.size):
            raw = stream.read(540)
            require(len(header) == HEADER.size and len(raw) == 540, 'clock record extent')
            target.write(header + raw)
            kind, side, parameter, active, process, observed_load, frame, cs, ip, ds = HEADER.unpack(header)
            kind = chr(kind)
            require(kind in 'CEVPF', 'clock event kind')
            counts[kind] += 1
            verticals += kind == 'V'
            if kind != 'F':
                continue
            require(active == process == 1 and observed_load == load, 'clock process')
            if parameter == 65535:
                require(not load_seen and boundaries == 0 and frame == 65535 and
                        (cs, ip, ds) == (load, 0, load - 16), 'decoded entry clock')
                row = observation['load_rows'][0]
                load_seen = True
            else:
                require(boundaries < len(rows), 'extra clock boundary')
                row = rows[boundaries]
                require(parameter == frame == boundaries and
                        (cs, ip, ds) == (row['cs'], row['ip'], row['ds']), 'scalar clock context')
                boundaries += 1
            require(verticals == row['display_events'] and
                    hashlib.sha256(raw).hexdigest() == row['clock_sha256'], 'same-boundary GDC payload')
    require(dict(counts) == observation['event_counts'] and counts['C'] == counts['E'] == 2 and
            counts['P'] == 0 and boundaries == 264 and load_seen, 'complete GDC coverage')
    result = subprocess.run([str(model), str(expanded)], capture_output=True)
    (output / (directory.name + '-model.log')).write_bytes(result.stdout + result.stderr)
    require(result.returncode == 0, 'independent GDC model')
    mutant = bytearray(expanded.read_bytes())
    first_v = next(i for i in range(0, len(mutant), 559) if mutant[i] == ord('V'))
    mutant[first_v + 19 + 197] ^= 1
    negative = output / (directory.name + '-counter-negative.bin')
    negative.write_bytes(mutant)
    result = subprocess.run([str(model), str(negative)], capture_output=True)
    (output / (directory.name + '-counter-negative.log')).write_bytes(result.stdout + result.stderr)
    require(result.returncode == 5, 'GDC counter mutation accepted')
    return dict(counts)


def verify(directory: Path, output: Path, model: Path) -> dict:
    observation, wrapper = complete(directory)
    preparation = json.loads((directory / 'preparation.json').read_text())
    profile = json.loads((directory / 'profile.json').read_text())
    require(sha(directory / 'preparation.json') == wrapper['preparation_sha256'] and
            sha(directory / 'execution.hdi') == wrapper['final_image_sha256'], 'disk/preparation identity')
    for name, key in [('profile.json', 'profile_sha256'), ('observer-profile.txt', 'observer_profile_sha256'), ('dosbox-x.conf', 'config_sha256')]:
        require(sha(directory / name) == preparation[key], 'profile/config identity')
    require({r['name']: (r['segment'], r['offset']) for r in profile['hooks']} == POINTS, 'target hook map')
    require(sha(Path(preparation['command'][0])) == preparation['emulator_sha256'] ==
            '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1', 'emulator identity')
    witness = json.loads((directory / 'timer-layout.json').read_text())
    require(witness['passed'] and sha(directory / 'timer-layout.json') == observation['timer_layout_sha256'] and
            witness['io_functions'] == observation['io_function_witnesses'], 'I/O runtime witness')
    for name, pin in witness['source_inputs'].items():
        require(sha(Path(name)) == pin, 'pinned emulator source')
    payload_path = Path(profile['payload_path'])
    payload = bytearray(payload_path.read_bytes())
    require(len(payload) == 69028 and hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, 'decoded target')
    decoded = json.loads((payload_path.parent / 'receipt.json').read_text())
    require(decoded['packed_target_sha256'] == PACKED_SHA and all(decoded['checks'].values()), 'packed target binding')
    relocations = payload_path.parent / 'relocations.csv'
    require(sha(relocations) == '84972ed592c6ecbac79fe880db94687522a8880e558bf4b084e92b7afbcf9417', 'relocation identity')
    with relocations.open(newline='') as stream:
        sites = [int(r['relative_linear'], 0) for r in csv.DictReader(stream)]
    require(sites == profile['relocations'] and len(sites) == 804, 'ordered relocations')
    lines = (directory / 'raw.txt').read_text().splitlines()
    loads = [line.split() for line in lines if line.startswith('L ')]
    inputs = [line.split() for line in lines if line.startswith('I ')]
    require(len(loads) == 1 and len(inputs) == 263 and len(lines) == 264, 'raw stream extent')
    load = int(loads[0][2], 16)
    for site in sites:
        struct.pack_into('<H', payload, site, (struct.unpack_from('<H', payload, site)[0] + load) & 65535)
    loaded = bytes.fromhex(loads[0][-1])
    equal_load(loaded, payload)
    mutant = bytearray(loaded)
    mutant[0x1408] ^= 1
    try:
        equal_load(mutant, payload)
    except ValueError:
        pass
    else:
        raise ValueError('loaded-byte mutation accepted')
    rows = observation['rows']
    previous = -1.0
    for index, row in enumerate(rows):
        segment, offset = POINTS[row['name']]
        require(row['index'] == index and row['load_segment'] == load and row['process'] == 1 and
                (row['cs'], row['ip'], row['ds']) == (load + segment, offset, load + 0xF34), 'scalar context')
        width = 8 + (segment * 16 + offset + 7 in sites)
        require(len(bytes.fromhex(row['guest_hook_bytes'])) == width and
                bytes.fromhex(row['guest_hook_bytes']) == loaded[segment * 16 + offset:segment * 16 + offset + width], 'relocated complete opcode window')
        require(row['cycle_state']['CPU_CycleMax'] == preparation['cycles'] and
                row['cycle_auto_adjust'] == row['last_callback'] == 0, 'fixed guest cycle context')
        previous_time = pic(row)
        require(previous_time >= previous, 'reversed time')
        previous = previous_time
    for line, row in zip(inputs, rows[:-1], strict=True):
        require(len(line) == 11 and int(line[1]) == 1 and
                tuple(int(x, 16) for x in line[2:5]) == (row['cs'], row['ip'], row['ds']), 'raw scalar caller')
        require(line[7] == row['sound_modes_hex'] and line[9] == row['resident_pointer_hex'] and
                line[10] == row['resident_hex'], 'raw memory')
    by_name = {row['name']: row for row in rows}
    glyphs = [row for row in rows if row['name'] == 'read_glyph']
    require(len(glyphs) == 256 and [row['ax'] for row in glyphs] ==
            [(0x5680 + i) & 0xFF7F for i in range(256)], 'runtime glyph loop')
    require([row['name'] for row in rows if row['name'] != 'read_glyph'] ==
            ['main_entry', 'gaiji_begin', 'read_all_begin', 'read_all_end', 'backup_return',
             'write_all_begin', 'write_all_end', 'gaiji_end'], 'transfer ordering')
    require(by_name['backup_return']['ax'] == by_name['gaiji_end']['ax'] == 1, 'font transfer result')
    require(len(observation['load_rows']) == 1, 'entry count')
    entry = observation['load_rows'][0]
    require((entry['registers']['cs'], entry['registers']['ip'], entry['registers']['ds']) ==
            (load, 0, load - 16), 'decoded entry')
    pic(entry)
    clock_events = clock_stream(directory, observation, load, output, model)
    windows = observation['io_rows']
    require([w['window'] for w in windows] == ['read_all_begin', 'write_all_begin'], 'port windows')
    negative_window = json.loads(json.dumps(windows[0]))
    negative_window['gaiji_counts'][0]['count'] += 1
    try:
        ports(negative_window, load)
    except ValueError:
        pass
    else:
        raise ValueError('port-count mutation accepted')
    negative_time = dict(by_name['gaiji_end'], pic_ms=by_name['gaiji_end']['pic_ms'] + 1)
    try:
        pic(negative_time)
    except ValueError:
        pass
    else:
        raise ValueError('PIC fractional-time mutation accepted')
    intervals = []
    for window, end in zip(windows, ['read_all_end', 'write_all_end'], strict=True):
        counts = ports(window, load)
        a, b = by_name[window['window']], by_name[end]
        ns = a['io_delay_ns'][0]
        require(all(r['io_delay_ns'] == a['io_delay_ns'] for r in rows), 'I/O delay changed')
        require((preparation['iodelay'] is None and ns > 0) or (preparation['iodelay'] == ns == 0), 'delay profile differs')
        budget = preparation['cycles']
        predicted = sum(count * (budget * ns // 1000000 if side == 'read' else budget * ns * 3 // 4000000)
                        for (side, port), count in counts.items())
        observed = b['io_delay_removed'] - a['io_delay_removed']
        require(observed >= predicted, 'I/O debit below witnessed ports')
        intervals.append(dict(start=window['window'], end=end, elapsed_ms=pic(b)-pic(a),
                              port_counts=window['gaiji_counts'], gaiji_io_cycles=predicted,
                              aggregate_io_cycles=observed, other_removed_cycles=observed-predicted,
                              gaiji_io_ms=predicted/budget, non_gaiji_debit_ms=(observed-predicted)/budget))
    return dict(capture=str(directory), cycles=preparation['cycles'], iodelay=preparation['iodelay'],
                io_delay_ns=rows[0]['io_delay_ns'], load_segment=load, scalar_rows=len(rows),
                observation_sha256=sha(directory/'startup-observation.json'), wrapper_sha256=sha(directory/'wrapper-receipt.json'),
                initial_image_sha256=preparation['initial_image_sha256'], config_sha256=preparation['config_sha256'],
                clock_events=clock_events, intervals=intervals, negative_controls=['loaded-byte', 'port-count', 'PIC-fractional-time', 'GDC-counter'],
                gaiji_elapsed_ms=pic(by_name['gaiji_end'])-pic(by_name['gaiji_begin']),
                backup_elapsed_ms=pic(by_name['backup_return'])-pic(by_name['gaiji_begin']))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, action='append', required=True)
    parser.add_argument('--rejected-capture', type=Path, action='append', default=[])
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--model-receipt', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    require(not output.exists() and output.is_relative_to(ROOT/'.analysis'), 'fresh private output required')
    parent = json.loads(args.model_receipt.read_text())
    model = args.model_dir/'model'
    require(parent['passed'] and sha(model) == parent['model_program_sha256'] and
            sha(args.model_dir/'model.cpp') == parent['model_source_sha256'], 'independent model identity')
    rejected = []
    for path in args.rejected_capture:
        try:
            complete(path)
        except ValueError as error:
            rejected.append(dict(capture=str(path), reason=str(error), wrapper_sha256=sha(path/'wrapper-receipt.json')))
        else:
            raise ValueError('incomplete capture accepted')
    output.mkdir(parents=True)
    captures = [verify(path.resolve(), output, model.resolve()) for path in args.capture]
    require(len({r['initial_image_sha256'] for r in captures}) == 1, 'reset image differs')
    normalized_configs = []
    for path in args.capture:
        raw = (path/'dosbox-x.conf').read_bytes()
        normalized_configs.append(re.sub(rb'(?m)^cycles = fixed (24000|36000)$', b'cycles = fixed CPU', raw).replace(b'iodelay = 0\n', b''))
    require(len(set(normalized_configs)) == 1, 'uncontrolled config changes')
    report = dict(passed=True, source_sha256=sha(Path(__file__)), shared_reader_sha256=sha(Path(__file__).with_name('verify_op_loading_clock.py')),
                  model_program_sha256=sha(model), model_receipt_sha256=sha(args.model_receipt),
                  captures=captures, incomplete_captures_rejected=rejected, scope=__doc__)
    (output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS bounded Gaiji transfers:', [(r['cycles'],r['iodelay'],r['gaiji_elapsed_ms']) for r in captures])


if __name__ == '__main__':
    main()
