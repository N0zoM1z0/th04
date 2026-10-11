#!/usr/bin/env python3
"""Verify bounded original OP loading work and cold PMD elapsed-clock owners.

Requires complete read-only captures, including decoded entry, 30 target hooks,
guest INT21 entries and matched IRET returns before the measure wait, full GDC
streams and timer observations. A zero process exit cannot replace completion.
Results describe the attested DOSBox-X scenarios, not physical CPU/chip timing,
default native startup equivalence, complete processes or historical exactness.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_SHA = '13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74'
PACKED_SHA = '8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f'
HEADER = struct.Struct('<BBHBIHHHHH')
POINTS = {
    'driver_type': (0xDA1, 0x2F2), 'resolved_modes': (0xDA1, 0x36A),
    'logo_start': (0xA74, 0x14F5), 'song_load': (0xDA1, 0x3BA),
    'song_command': (0xDA1, 0x264), 'measure_start': (0xDA1, 0x370),
    'measure_end': (0xDA1, 0x39D), 'after_measure': (0xA74, 0x15FB),
    'super_load': (0, 0x2A86), 'logo_complete': (0xA74, 0xCC4),
    'title_start': (0xA74, 0x2592), 'title_complete': (0xA74, 0xCE3),
    'menu_ready': (0xA74, 0x756), 'main_entry': (0xA74, 0xC37),
    'game_init_return': (0xA74, 0xC56), 'gaiji_begin': (0xA74, 0xC6B),
    'gaiji_end': (0xA74, 0xC79), 'cfg_end': (0xA74, 0xC7C),
    'se_loaded': (0xA74, 0xCB6), 'pi_loaded': (0xA74, 0x1523),
    'pi_palette_done': (0xA74, 0x152A), 'pi_put_done': (0xA74, 0x1534),
    'pi_free_done': (0xA74, 0x1542), 'page_copy_done': (0xA74, 0x1549),
    'background_snap_done': (0xA74, 0x154E), 'clear_page1_done': (0xA74, 0x1559),
    'clear_page0_done': (0xA74, 0x1564), 'palette_loop_done': (0xA74, 0x15C2),
    'logo_song_loaded': (0xA74, 0x15CE), 'logo_started': (0xA74, 0x15D5),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def complete(directory: Path) -> tuple[dict, dict]:
    require((directory / 'startup-observation.json').is_file(), 'missing completion observation')
    observation = json.loads((directory / 'startup-observation.json').read_text())
    wrapper = json.loads((directory / 'wrapper-receipt.json').read_text())
    require(wrapper['passed'] and wrapper['exit_code'] == 0 and wrapper['completion_observed'], 'wrapper completion rejected')
    require(observation['passed'] and observation['controlled_host_stop'] and
            len(observation['rows']) == 41 and observation['rows'][-1]['name'] == 'menu_ready', 'bounded completion rejected')
    require(sha(directory / 'startup-observation.json') == wrapper['completion_sha256'], 'completion identity')
    require(sha(directory / 'capture.log') == wrapper['log_sha256'] and
            'OP_STARTUP_COMPLETE 41' in (directory / 'capture.log').read_text(), 'terminal log completion')
    return observation, wrapper


def pic(row: dict) -> float:
    state = row.get('cycle_state', row.get('cycles'))
    require(state['CPU_CycleMax'] > 0, 'invalid CPU budget')
    expected = state['pic_ticks'] + (state['CPU_CycleMax'] - state['CPU_CycleLeft'] - state['CPU_Cycles']) / state['CPU_CycleMax']
    require(row['pic_ms'] == expected, 'PIC time differs from raw fractional cycle budget')
    return expected


def equal_load(actual: bytes, expected: bytes) -> None:
    require(actual == expected, 'whole runtime load differs')


def dos_return(row: dict, request: dict) -> None:
    ip, cs, flags = struct.unpack('<HHH', bytes.fromhex(row['stack_hex']))
    registers = row['registers']
    require((registers['ss'], registers['sp'], ip, cs) ==
            (request['frame_ss'], request['frame_sp'], request['return_ip'], request['registers']['cs']), 'DOS return frame differs')
    require(row['via'] == 'iret' and row['iret_flags'] == flags, 'DOS return kind/flags differ')


def verify(directory: Path, output: Path, model: Path) -> dict:
    observation, wrapper = complete(directory)
    profile = json.loads((directory / 'profile.json').read_text())
    preparation = json.loads((directory / 'preparation.json').read_text())
    require(sha(directory / 'preparation.json') == wrapper['preparation_sha256'] and
            sha(directory / 'execution.hdi') == wrapper['final_image_sha256'], 'disk/preparation identity')
    require(sha(directory / 'profile.json') == preparation['profile_sha256'] and
            sha(directory / 'observer-profile.txt') == preparation['observer_profile_sha256'] and
            sha(directory / 'dosbox-x.conf') == preparation['config_sha256'], 'profile/config identity')
    require({r['name']: (r['segment'], r['offset']) for r in profile['hooks']} == POINTS, 'target point map differs')
    require(sha(Path(preparation['command'][0])) == preparation['emulator_sha256'] ==
            '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1', 'emulator identity')
    timer_layout = json.loads((directory / 'timer-layout.json').read_text())
    require(timer_layout['passed'] and sha(directory / 'timer-layout.json') == observation['timer_layout_sha256'], 'timer/CPU witness identity')
    for name, pin in timer_layout['source_inputs'].items():
        require(sha(Path(name)) == pin, 'original emulator source identity')
    payload_path = Path(profile['payload_path'])
    payload = bytearray(payload_path.read_bytes())
    require(len(payload) == 69028 and hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, 'decoded target identity')
    decoded = json.loads((payload_path.parent / 'receipt.json').read_text())
    require(decoded['packed_target_sha256'] == PACKED_SHA and all(decoded['checks'].values()), 'packed/decoded binding')
    relocations = payload_path.parent / 'relocations.csv'
    require(sha(relocations) == '84972ed592c6ecbac79fe880db94687522a8880e558bf4b084e92b7afbcf9417', 'relocation identity')
    with relocations.open(newline='') as stream:
        sites = [int(r['relative_linear'], 0) for r in csv.DictReader(stream)]
    require(sites == profile['relocations'] and len(sites) == 804, 'ordered relocation extent')
    lines = (directory / 'raw.txt').read_text().splitlines()
    loads = [line.split() for line in lines if line.startswith('L ')]
    inputs = [line.split() for line in lines if line.startswith('I ')]
    require(len(loads) == 1 and len(inputs) == 40 and len(lines) == 41, 'scalar stream extent')
    load = int(loads[0][2], 16)
    for site in sites:
        struct.pack_into('<H', payload, site, (struct.unpack_from('<H', payload, site)[0] + load) & 65535)
    loaded = bytes.fromhex(loads[0][-1])
    equal_load(loaded, payload)
    mutant = bytearray(loaded)
    mutant[0x522] ^= 1
    try:
        equal_load(mutant, payload)
    except ValueError:
        pass
    else:
        raise ValueError('load mutation accepted')
    rows = observation['rows']
    require({row['name'] for row in rows} == set(POINTS), 'missing named target boundary')
    for index, row in enumerate(rows):
        require(row['index'] == index and row['load_segment'] == load and row['process'] == 1 and row['ds'] == load + 0xF34, 'scalar load/DS/order')
        segment, offset = POINTS[row['name']]
        require((row['cs'], row['ip']) == (load + segment, offset), 'scalar caller differs')
        require(bytes.fromhex(row['guest_hook_bytes']) == loaded[segment * 16 + offset:segment * 16 + offset + 8], 'runtime opcode differs')
        pic(row)
    for line, row in zip(inputs, rows[:-1], strict=True):
        require(len(line) == 11 and int(line[1]) == 1 and tuple(int(x, 16) for x in line[2:5]) == (row['cs'], row['ip'], row['ds']), 'raw scalar caller')
        require(line[7] == row['sound_modes_hex'] and line[9] == row['resident_pointer_hex'] and line[10] == row['resident_hex'], 'raw scalar memory')
    require(len(observation['load_rows']) == 1, 'decoded entry count')
    entry = observation['load_rows'][0]
    require(entry['load_segment'] == load and entry['process'] == 1 and
            (entry['registers']['cs'], entry['registers']['ip'], entry['registers']['ds']) == (load, 0, load - 16), 'decoded entry registers')
    pic(entry)
    by_name = {row['name']: row for row in rows if row['name'] not in ('song_command', 'song_load', 'super_load')}
    require(by_name['driver_type']['ax'] == 0x4802 and by_name['resolved_modes']['sound_modes_hex'] == '010200', 'resolved PMD86 modes')
    require(struct.unpack_from('<HH', bytes.fromhex(by_name['measure_start']['stack_hex']), 4) == (0, 2) and by_name['measure_end']['ax'] == 2, 'measure contract')
    events = directory / 'video-clock-events.bin.gz'
    require(sha(events) == observation['clock_file_sha256'], 'GDC stream identity')
    expanded = output / (directory.name + '-events.bin')
    counts, boundaries, verticals, load_seen = Counter(), 0, 0, False
    with gzip.open(events, 'rb') as stream, expanded.open('xb') as target:
        require(stream.read(8) == b'TH04EP1\n', 'clock stream magic')
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
            require(active == process == 1 and observed_load == load, 'clock process identity')
            if parameter == 65535:
                require(not load_seen and boundaries == 0 and frame == 65535 and (cs, ip, ds) == (load, 0, load - 16), 'load clock context')
                row = entry
                load_seen = True
            else:
                row = rows[boundaries]
                require(parameter == frame == boundaries and (cs, ip, ds) == (row['cs'], row['ip'], row['ds']), 'scalar clock context')
                boundaries += 1
            require(verticals == row['display_events'] and hashlib.sha256(raw).hexdigest() == row['clock_sha256'], 'same-boundary clock payload')
    require(dict(counts) == observation['event_counts'] and counts['C'] == counts['E'] == 2 and counts['P'] == 0 and boundaries == 41 and load_seen, 'complete clock coverage')
    result = subprocess.run([str(model), str(expanded)], capture_output=True)
    (output / (directory.name + '-model.log')).write_bytes(result.stdout + result.stderr)
    require(result.returncode == 0, 'independent GDC model rejects')
    mutant = bytearray(expanded.read_bytes())
    first_v = next(i for i in range(0, len(mutant), 559) if mutant[i] == ord('V'))
    mutant[first_v + 19 + 197] ^= 1
    negative = output / (directory.name + '-counter-negative.bin')
    negative.write_bytes(mutant)
    result = subprocess.run([str(model), str(negative)], capture_output=True)
    (output / (directory.name + '-counter-negative.log')).write_bytes(result.stdout + result.stderr)
    require(result.returncode == 5, 'counter mutation accepted')
    timers = observation['timer_rows']
    for index, row in enumerate(timers):
        require(row['index'] == index, 'timer row order')
        pic(row)
        if row['kind'] == 'timer_schedule':
            raw = bytes.fromhex(row['fmtimer_hex'])
            period = (18 * (1024 - int.from_bytes(raw[:2], 'little')) if row['timer'] == 0 else 288 * (256 - raw[2])) / 1000
            require(abs(period - row['delta_ms']) < 1e-12, 'timer period differs')
    first_b = next(row for row in timers if row['kind'] == 'timer_schedule' and row['timer'] == 1)
    require(first_b['delta_ms'] == 73.728, 'cold installation deadline differs')
    dos = observation['dos_rows']
    requests, returns = {}, {}
    for index, row in enumerate(dos):
        require(row['index'] == index, 'DOS row order')
        pic(row)
        require(first_b['pic_ms'] <= row['pic_ms'] <= by_name['measure_start']['pic_ms'], 'DOS observation outside prefix')
        if row['kind'] == 'entry':
            require(row['interrupt_type'] & 1 and row['ah'] == row['registers']['ax'] >> 8, 'DOS software request')
            requests[index] = row
        else:
            key = row['request_index']
            require(key in requests and key not in returns, 'DOS return pairing')
            dos_return(row, requests[key])
            returns[key] = row
    pending = sorted(set(requests) - set(returns))
    require(pending == observation['dos_pending_request_indices'] and len(pending) == 1 and
            requests[pending[0]]['ah'] == 0x4B and bytes.fromhex(requests[pending[0]]['filename_hex']).endswith(b'OP.EXE'), 'unexpected unreturned file request')
    require(len(dos) == 123 and len(returns) == 61, 'DOS prefix extent')
    return_mutant = json.loads(json.dumps(next(iter(returns.values()))))
    stack = bytearray.fromhex(return_mutant['stack_hex'])
    stack[0] ^= 1
    return_mutant['stack_hex'] = stack.hex()
    try:
        dos_return(return_mutant, requests[return_mutant['request_index']])
    except ValueError:
        pass
    else:
        raise ValueError('DOS return mutation accepted')
    time_mutant = dict(by_name['pi_loaded'], pic_ms=by_name['pi_loaded']['pic_ms'] + 1)
    try:
        pic(time_mutant)
    except ValueError:
        pass
    else:
        raise ValueError('PIC time mutation accepted')
    play = [row for row in rows if row['name'] == 'song_command'][1]
    points = [('installation_first_B', first_b), ('decoded_entry', entry)] + [
        (name, by_name[name]) for name in ('main_entry', 'game_init_return', 'gaiji_begin', 'gaiji_end', 'cfg_end', 'se_loaded', 'logo_start', 'pi_loaded', 'pi_palette_done', 'pi_put_done', 'pi_free_done', 'page_copy_done', 'background_snap_done', 'clear_page1_done', 'clear_page0_done', 'palette_loop_done', 'logo_song_loaded')]
    points.append(('logo_play_command', play))
    intervals = []
    for (start, a), (end, b) in zip(points, points[1:]):
        require(b['pic_ms'] >= a['pic_ms'], 'phase timeline reversed')
        intervals.append(dict(start=start, end=end, elapsed_ms=b['pic_ms'] - a['pic_ms'], display_events=b['display_events'] - a['display_events']))
    return dict(capture=str(directory), cycles=preparation['cycles'], observation_sha256=sha(directory / 'startup-observation.json'), wrapper_sha256=sha(directory / 'wrapper-receipt.json'), complete_payload_sha256=hashlib.sha256(loaded).hexdigest(), load_segment=load, dgroup=load + 0xF34, scalar_rows=41, clock_events=dict(counts), timer_rows=len(timers), dos_rows=len(dos), dos_matched_returns=61, pending_child_exec=pending, intervals=intervals, install_to_play_ms=play['pic_ms'] - first_b['pic_ms'], measure_refreshes=by_name['measure_end']['display_events'] - by_name['measure_start']['display_events'], negative_controls=['loaded-byte', 'GDC-counter', 'DOS-return-frame', 'PIC-fractional-time'])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, action='append', required=True)
    parser.add_argument('--rejected-capture', type=Path)
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--model-receipt', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    require(not output.exists() and output.is_relative_to(ROOT / '.analysis'), 'use fresh private output')
    parent = json.loads(args.model_receipt.read_text())
    model = args.model_dir / 'model'
    require(parent['passed'] and sha(model) == parent['model_program_sha256'] and sha(args.model_dir / 'model.cpp') == parent['model_source_sha256'], 'independent model identity')
    rejected = None
    if args.rejected_capture:
        try:
            complete(args.rejected_capture)
        except ValueError as error:
            rejected = dict(path=str(args.rejected_capture), reason=str(error), wrapper_sha256=sha(args.rejected_capture / 'wrapper-receipt.json'))
        else:
            raise ValueError('incomplete capture accepted')
    output.mkdir(parents=True)
    captures = [verify(path.resolve(), output, model.resolve()) for path in args.capture]
    report = dict(passed=True, source_sha256=sha(Path(__file__)), model_program_sha256=sha(model), model_receipt_sha256=sha(args.model_receipt), captures=captures, incomplete_capture_rejected=rejected, scope=__doc__)
    (output / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS original loading phases, DOS returns and clocks:', [(r['cycles'], r['install_to_play_ms'], r['measure_refreshes']) for r in captures])


if __name__ == '__main__':
    main()
