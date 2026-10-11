#!/usr/bin/env python3
"""Verify original OP busy-measure, reset-counter and inherited-counter waits.

Reads complete original captures through the second Logo counter reset. Checks
packed/decoded/load, executable and config inputs, scalar/PIC/IRQ observations,
full GDC clocks and independent model mutations. Includes a config-only BGM-off
control. IRQ counters and GDC blink counters have separate owners; these scoped
DOSBox-X observations do not establish native, physical or byte-exact acceptance.
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
import sys
import tomllib

import verify_op_loading_clock as loading

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/probes')]
from lib.pc98 import parse_mz
from prepare_th04_maine_diagnostic_hdi import Fat12, u16, u32

sha, require, pic = loading.sha, loading.require, loading.pic
WAIT_POINTS = {'logo_wait_enter': (0xA74, 0x16DD),
               'logo_wait_pass': (0xA74, 0x16E9),
               'logo_wait_reset': (0xA74, 0x16EF)}


def counters(row: dict) -> tuple[int, int]:
    raw = bytes.fromhex(row['vsync_counts_hex'])
    require(len(raw) == 4, 'IRQ counter extent')
    return struct.unpack('<HH', raw)


def continuous(a: dict, b: dict) -> int:
    one_a, two_a = counters(a)
    one_b, two_b = counters(b)
    delta = (two_b - two_a) & 65535
    require((one_b - one_a) & 65535 == delta, 'Count1 reset inside continuous interval')
    require(pic(b) >= pic(a), 'counter interval time reversed')
    return delta


def reset(a: dict, b: dict) -> None:
    require(counters(b)[0] == (counters(b)[1] - counters(a)[1]) & 65535,
            'Count1 reset / continuous Count2 differs')
    require(pic(b) >= pic(a), 'reset time reversed')


def check_waits(rows: list[dict], bgm_off: bool) -> dict:
    def one(name):
        found = [row for row in rows if row['name'] == name]
        require(len(found) == 1, 'unique wait boundary: ' + name)
        return found[0]

    start, ready = one('measure_start'), one('after_measure')
    require(struct.unpack_from('<HH', bytes.fromhex(start['stack_hex']), 4) == (0, 2),
            'measure / fallback arguments')
    triples = [[row for row in rows if row['name'] == name] for name in WAIT_POINTS]
    require(all(len(found) == 2 for found in triples), 'two complete Logo waits required')
    enters, passes, resets = triples
    require(rows[-1] == resets[-1], 'terminal second reset missing')
    require([row['index'] for group in zip(*triples, strict=True) for row in group] ==
            list(range(len(rows) - 6, len(rows))), 'Logo wait boundary order')
    if bgm_off:
        before, after = one('frame_delay_enter'), one('frame_delay_return')
        require(not any(row['name'] == 'measure_end' for row in rows), 'inactive active-path exit')
        require(counters(before)[0] > 0 and counters(after)[0] == 0 and
                counters(before)[1] == counters(after)[1], 'zero fallback must reset without waiting')
        require(struct.unpack_from('<H', bytes.fromhex(before['stack_hex']), 4)[0] == 0,
                'frame_delay fallback argument')
        continuous(start, before)
        continuous(after, ready)
    else:
        end = one('measure_end')
        require(end['ax'] == 2, 'returned measure')
        require(continuous(start, end) > 0, 'busy wait lacks IRQ progression')
        continuous(end, ready)
    continuous(ready, enters[0])
    waits = []
    for index, (enter, passed, cleared) in enumerate(zip(*triples, strict=True)):
        progress = continuous(enter, passed)
        require(counters(passed)[0] >= 2, 'Logo unsigned wait threshold')
        reset(passed, cleared)
        if index:
            continuous(resets[index - 1], enter)
        waits.append(dict(enter=counters(enter), passed=counters(passed),
                          cleared=counters(cleared), counted_irq_progress=progress,
                          elapsed_ms=pic(passed) - pic(enter),
                          gdc_events=passed['display_events'] - enter['display_events']))
    if not bgm_off:
        require(counters(enters[0])[0] >= 2 and waits[0]['counted_irq_progress'] == 0,
                'first active Logo wait must inherit already sufficient count')
    require(counters(enters[1])[0] < 2 and waits[1]['counted_irq_progress'] > 0,
            'second Logo wait must actually await counted interrupts')
    return dict(bgm_off=bgm_off, measure_start=counters(start), measure_ready=counters(ready),
                measure_elapsed_ms=pic(ready) - pic(start), logo_waits=waits)


def static_waits(payload: bytes) -> dict:
    from capstone import Cs, CS_ARCH_X86, CS_MODE_16
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    extents = [('frame_delay', 0xDA1, 0x2B, 21),
               ('snd_delay_until_measure', 0xDA1, 0x370, 49),
               ('logo_wait', 0xA74, 0x16DD, 25), ('irq_prefix', 0, 0x25C6, 24)]
    decoded, result = {}, {}
    for name, segment, offset, size in extents:
        raw = payload[segment * 16 + offset:segment * 16 + offset + size]
        instructions = list(decoder.disasm(raw, offset))
        require(sum(i.size for i in instructions) == size, 'static instruction extent')
        decoded[name] = {i.address: (i.mnemonic, i.op_str) for i in instructions}
        result[name] = dict(segment=segment, offset=offset, size=size,
                            sha256=hashlib.sha256(raw).hexdigest(),
                            instructions=[dict(offset=i.address, mnemonic=i.mnemonic,
                                               operands=i.op_str) for i in instructions])
    expected = {
        'frame_delay': {0x2E: ('mov', 'word ptr [0x1ac6], 0'),
                        0x34: ('mov', 'ax, word ptr [0x1ac6]'),
                        0x3A: ('jb', '0x34'), 0x3D: ('retf', '2')},
        'snd_delay_until_measure': {0x373: ('cmp', 'byte ptr [0x9e1], 0'),
            0x378: ('jne', '0x386'), 0x37F: ('call', '0x2b'),
            0x38F: ('int', '0x60'), 0x396: ('int', '0x61'),
            0x398: ('cmp', 'ax, word ptr [bp + 8]'), 0x39B: ('jb', '0x386')},
        'logo_wait': {0x16E2: ('cmp', 'word ptr [0x1ac6], 2'),
                      0x16E7: ('jb', '0x16e2'),
                      0x16E9: ('mov', 'word ptr [0x1ac6], 0')},
        'irq_prefix': {0x25C8: ('mov', 'ax, 0xf34'),
                       0x25CD: ('mov', 'ax, word ptr [0x854]'),
                       0x25D0: ('add', 'word ptr [0x1ace], ax'),
                       0x25D4: ('jb', '0x25f7'),
                       0x25D6: ('inc', 'word ptr [0x1ac6]'),
                       0x25DA: ('inc', 'word ptr [0x1ac8]')},
    }
    for name, points in expected.items():
        require(all(decoded[name].get(at) == value for at, value in points.items()),
                'static wait owner differs: ' + name)
    return result


def inputs(directory: Path, preparation: dict) -> bool:
    image = bytearray((directory / 'execution.hdi').read_bytes())
    fs = Fat12(image)
    genso = fs.find_entry([fs.root], b'GENSO      ')
    offsets = [fs.cluster_offset(k) for k in fs.chain(u16(image, genso + 26))]
    def read(name):
        entry = fs.find_entry(offsets, name)
        return fs.file_bytes(u16(image, entry + 26), u32(image, entry + 28))
    targets = [r for r in tomllib.loads((ROOT / 'config/targets.toml').read_text())['artifacts']
               if r['game'] == 'th04' and r['required']]
    for target in targets:
        raw = read(f"{Path(target['dos_path']).stem:<8}{Path(target['dos_path']).suffix[1:]}".encode())
        require(len(raw) == target['size'] and hashlib.sha256(raw).hexdigest() == target['sha256']
                and parse_mz(raw).valid, 'original product identity / MZ structure')
    for name, pin in preparation['input_files'].items():
        raw = read(name.encode())
        require(len(raw) == pin['size'] and hashlib.sha256(raw).hexdigest() == pin['sha256'],
                'physical input identity: ' + name)
    cfg = read(b'MIKO    CFG')
    bgm_off = 'bgm_off_control' in preparation
    require(cfg.hex() == ('020302000101ef9f0009' if bgm_off else '020302020101ef9f000b'),
            'physical BGM config')
    if bgm_off:
        original = (directory / 'prepared/diagnostic.hdi').read_bytes()
        original_cfg = preparation['bgm_off_control']['original_cfg_hex']
        require(original_cfg == '020302020101ef9f000b' and
                hashlib.sha256(original).hexdigest() == preparation['bgm_off_control']['original_image_sha256'],
                'BGM control original image identity')
        entry = fs.find_entry(offsets, b'MIKO    CFG')
        at = fs.cluster_offset(u16(image, entry + 26))
        initial = bytearray(original)
        require(initial[at:at + len(cfg)].hex() == original_cfg, 'BGM original config extent')
        initial[at:at + len(cfg)] = cfg
        require(preparation['bgm_off_control']['changed_absolute_offsets'] == [at + 3, at + 9] and
                hashlib.sha256(initial).hexdigest() == preparation['initial_image_sha256'],
                'BGM initial image changes bytes beyond option/checksum')
        # GAME.BAT writes its own diagnostic file during normal execution.
        # The final image has a separate full hash; it is not the initial disk.
    return bgm_off


def verify(directory: Path, output: Path, model: Path) -> dict:
    observation = json.loads((directory / 'startup-observation.json').read_text())
    wrapper = json.loads((directory / 'wrapper-receipt.json').read_text())
    preparation = json.loads((directory / 'preparation.json').read_text())
    profile = json.loads((directory / 'profile.json').read_text())
    require(wrapper['passed'] and wrapper['exit_code'] == 0 and wrapper['completion_observed'] and
            observation['passed'] and observation['controlled_host_stop'], 'capture incomplete')
    for path, pin in [('startup-observation.json', wrapper['completion_sha256']),
                      ('preparation.json', wrapper['preparation_sha256']),
                      ('capture.log', wrapper['log_sha256']), ('execution.hdi', wrapper['final_image_sha256']),
                      ('profile.json', preparation['profile_sha256']),
                      ('observer-profile.txt', preparation['observer_profile_sha256']),
                      ('dosbox-x.conf', preparation['config_sha256']),
                      ('timer-layout.json', observation['timer_layout_sha256'])]:
        require(sha(directory / path) == pin, 'capture identity: ' + path)
    require(sha(Path(wrapper['command'][4])) == wrapper['gdb_source_sha256'], 'observer source identity')
    require(sha(Path(preparation['command'][0])) == preparation['emulator_sha256'] ==
            '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1', 'emulator identity')
    timer = json.loads((directory / 'timer-layout.json').read_text())
    require(timer['passed'], 'timer witness incomplete')
    for name, pin in timer['source_inputs'].items():
        require(sha(Path(name)) == pin, 'emulator source identity')
    bgm_off = inputs(directory, preparation)
    points = dict(loading.POINTS, **WAIT_POINTS)
    del points['menu_ready']
    if bgm_off:
        del points['measure_end'], points['title_complete']
        points.update(frame_delay_enter=(0xDA1, 0x2B), frame_delay_return=(0xDA1, 0x3C))
    require(len(profile['hooks']) == 32 and
            {h['name']: (h['segment'], h['offset']) for h in profile['hooks']} == points,
            'bounded target point map')
    payload_path = Path(profile['payload_path'])
    payload = payload_path.read_bytes()
    require(len(payload) == 69028 and hashlib.sha256(payload).hexdigest() == loading.PAYLOAD_SHA,
            'decoded payload identity')
    decoded = json.loads((payload_path.parent / 'receipt.json').read_text())
    require(sha(payload_path.parent / 'receipt.json') == profile['decoded_receipt_sha256'] and
            decoded['packed_target_sha256'] == loading.PACKED_SHA and all(decoded['checks'].values()),
            'packed/decoded binding')
    relocs = payload_path.parent / 'relocations.csv'
    require(sha(relocs) == '84972ed592c6ecbac79fe880db94687522a8880e558bf4b084e92b7afbcf9417',
            'ordered relocations identity')
    with relocs.open(newline='') as stream:
        sites = [int(r['relative_linear'], 0) for r in csv.DictReader(stream)]
    require(sites == profile['relocations'] and len(sites) == 804, 'complete relocation topology')
    lines = [line.split() for line in (directory / 'raw.txt').read_text().splitlines()]
    require(len(lines) == 37 and lines[0][0] == 'L' and all(x[0] == 'I' for x in lines[1:]),
            'complete scalar stream extent')
    load, loaded = int(lines[0][2], 16), bytes.fromhex(lines[0][-1])
    expected = bytearray(payload)
    for site in sites:
        struct.pack_into('<H', expected, site, (struct.unpack_from('<H', expected, site)[0] + load) & 65535)
    loading.equal_load(loaded, expected)
    rows = observation['rows']
    require(len(rows) == 37 and 'OP_STARTUP_COMPLETE 37' in (directory / 'capture.log').read_text(),
            'terminal completion extent')
    for index, row in enumerate(rows):
        segment, offset = points[row['name']]
        require(row['index'] == index and row['load_segment'] == load and row['process'] == 1 and
                (row['cs'], row['ip'], row['ds']) == (load + segment, offset, load + 0xF34),
                'scalar address / order')
        require(bytes.fromhex(row['guest_hook_bytes']) == loaded[segment * 16 + offset:segment * 16 + offset + 8],
                'relocated runtime opcode')
        pic(row)
        if index:
            require(struct.unpack('<HH', bytes.fromhex(row['vsync_vector_hex'])) == (0x25C6, load),
                    'runtime IRQ vector owner')
    for line, row in zip(lines[1:], rows[:-1], strict=True):
        require(len(line) == 11 and line[1] == '1' and
                tuple(int(x, 16) for x in line[2:5]) == (row['cs'], row['ip'], row['ds']) and
                line[7:11] == [row['sound_modes_hex'], row['vsync_counts_hex'],
                               row['resident_pointer_hex'], row['resident_hex']], 'raw scalar witness')
    resolved = next(r['index'] for r in rows if r['name'] == 'resolved_modes')
    require([r['sound_modes_hex'] for r in rows[resolved:]] ==
            ['010000' if bgm_off else '010200'] * (len(rows) - resolved),
            'resolved sound mode')
    waits = check_waits(rows, bgm_off)
    events = directory / 'video-clock-events.bin.gz'
    require(sha(events) == observation['clock_file_sha256'], 'complete clock stream identity')
    expanded = output / (directory.name + '-events.bin')
    counts, boundaries, verticals, entry_seen = Counter(), 0, 0, False
    require(len(observation['load_rows']) == 1, 'decoded entry witness')
    entry = observation['load_rows'][0]
    pic(entry)
    with gzip.open(events, 'rb') as source, expanded.open('xb') as destination:
        require(source.read(8) == b'TH04EP1\n', 'clock magic')
        while header := source.read(loading.HEADER.size):
            raw = source.read(540)
            require(len(header) == 19 and len(raw) == 540, 'complete clock record')
            destination.write(header + raw)
            kind, side, parameter, active, process, observed_load, frame, cs, ip, ds = loading.HEADER.unpack(header)
            kind = chr(kind)
            require(kind in 'CEVF', 'clock event kind')
            counts[kind] += 1
            verticals += kind == 'V'
            if kind != 'F':
                continue
            require(active == process == 1 and observed_load == load, 'clock process')
            if parameter == 65535:
                require(not entry_seen and boundaries == 0 and frame == 65535 and
                        (cs, ip, ds) == (load, 0, load - 16), 'decoded entry clock')
                row, entry_seen = entry, True
            else:
                require(boundaries < len(rows), 'extra scalar clock')
                row = rows[boundaries]
                require(parameter == frame == boundaries and (cs, ip, ds) == (row['cs'], row['ip'], row['ds']),
                        'scalar clock address')
                boundaries += 1
            require(verticals == row['display_events'] and hashlib.sha256(raw).hexdigest() == row['clock_sha256'],
                    'same-boundary clock witness')
    require(dict(counts) == observation['event_counts'] and counts['C'] == counts['E'] == 2 and
            boundaries == 37 and entry_seen, 'complete GDC coverage')
    def run_model(path, suffix):
        result = subprocess.run([str(model), str(path)], capture_output=True)
        (output / (directory.name + suffix + '.log')).write_bytes(result.stdout + result.stderr)
        return result.returncode
    require(run_model(expanded, '-model') == 0, 'independent GDC model rejects')
    mutant = bytearray(expanded.read_bytes())
    first_v = next(i for i in range(0, len(mutant), 559) if mutant[i] == ord('V'))
    mutant[first_v + 19 + 197] ^= 1
    negative = output / (directory.name + '-gdc-negative.bin')
    negative.write_bytes(mutant)
    require(run_model(negative, '-gdc-negative') == 5, 'GDC mutation accepted')
    for index, row in enumerate(observation['timer_rows']):
        require(row['index'] == index, 'timer order')
        pic(row)
    requests, returned = {}, set()
    for index, row in enumerate(observation['dos_rows']):
        require(row['index'] == index, 'DOS order')
        pic(row)
        if row['kind'] == 'entry':
            requests[index] = row
        else:
            require(row['request_index'] in requests and row['request_index'] not in returned, 'DOS return pairing')
            loading.dos_return(row, requests[row['request_index']])
            returned.add(row['request_index'])
    require(sorted(set(requests) - returned) == observation['dos_pending_request_indices'], 'pending DOS extent')
    # Mutations preserve the rest of each captured row; reset and inherited
    # counter mistakes must reject even when filenames, pixels and exit match.
    negatives = []
    first_negative = 'fallback-reset' if bgm_off else 'busy-reset'
    for kind in (first_negative, 'missing-logo-reset', 'below-threshold', 'PIC-time'):
        changed = json.loads(json.dumps(rows))
        name = {'busy-reset': 'after_measure', 'fallback-reset': 'after_measure', 'missing-logo-reset': 'logo_wait_reset',
                'below-threshold': 'logo_wait_pass', 'PIC-time': 'logo_wait_enter'}[kind]
        row = next(r for r in changed if r['name'] == name)
        a, b = counters(row)
        if kind == 'PIC-time':
            row['pic_ms'] += 1
        else:
            a = 65535 if kind == 'missing-logo-reset' else (1 if kind == 'fallback-reset' else 0)
            row['vsync_counts_hex'] = struct.pack('<HH', a, b).hex()
        try:
            check_waits(changed, bgm_off)
        except ValueError:
            negatives.append(kind)
        else:
            raise ValueError('wait mutation accepted: ' + kind)
    return dict(capture=str(directory), cycles=preparation['cycles'], load_segment=load,
                dgroup=load + 0xF34, completion_sha256=sha(directory / 'startup-observation.json'),
                wrapper_sha256=sha(directory / 'wrapper-receipt.json'), waits=waits,
                clock_events=dict(counts), timer_rows=len(observation['timer_rows']),
                dos_rows=len(observation['dos_rows']), dos_matched_returns=len(returned),
                negative_controls=negatives + ['GDC-counter'], static_owners=static_waits(payload))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, action='append', required=True)
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--model-receipt', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    require(not output.exists() and output.is_relative_to(ROOT / '.analysis'), 'fresh private output required')
    parent = json.loads(args.model_receipt.read_text())
    model = args.model_dir.resolve() / 'model'
    require(parent['passed'] and sha(model) == parent['model_program_sha256'] and
            sha(args.model_dir / 'model.cpp') == parent['model_source_sha256'], 'independent model identity')
    output.mkdir(parents=True)
    captures = [verify(path.resolve(), output, model) for path in args.capture]
    require(sorted((c['cycles'], c['waits']['bgm_off']) for c in captures) ==
            [(24000, False), (24000, True), (36000, False)], 'complete CPU / config control set')
    report = dict(passed=True, source_sha256=sha(Path(__file__)),
                  shared_reader_sha256=sha(Path(loading.__file__)), model_program_sha256=sha(model),
                  model_receipt_sha256=sha(args.model_receipt), captures=captures, scope=__doc__)
    (output / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS original OP wait owners:', [(c['cycles'], c['waits']) for c in captures])


if __name__ == '__main__':
    main()
