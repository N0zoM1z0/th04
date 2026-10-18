#!/usr/bin/env python3
"""Verify real repeat calls and BIOS gaps during one uninterrupted physical hold."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ENGINE_SHA = '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def moment(row):
    value = row['time']
    raw = value['raw']
    assert raw['CPU_CycleMax'] == 36000
    result = Fraction(value['numerator'], value['denominator'])
    assert result == Fraction(raw['PIC_Ticks']*36000 + 36000 - raw['CPU_CycleLeft'] - raw['CPU_Cycles'], 36000)
    return result


def keyboard(row):
    # Restricted to this binary; the pinned compiler and actual ELF operands
    # independently bind these host offsets. They are not guest BIOS offsets.
    raw = bytes.fromhex(row['keyboard_raw'])
    assert len(raw) == 352
    return dict(key=int.from_bytes(raw[240:244], 'little'),
                wait=int.from_bytes(raw[248:256], 'little'),
                pause=int.from_bytes(raw[256:264], 'little'),
                rate=int.from_bytes(raw[264:272], 'little'))


def reduce(micro, rows):
    assert micro['complete'] and micro['error'] is None and micro['api_count'] == 2
    assert micro['markers'] == list(range(0xa0, 0xa7))
    assert [row['ordinal'] for row in rows] == list(range(len(rows)))
    for row in rows:
        assert not row['context']['cpu_state'][1] & 0x80000001
        assert not row['context']['flags'] & 0x20000
    external = [row for row in rows if row['kind'] == 'request-entry']
    returned = [row for row in rows if row['kind'] == 'request-return']
    internal = [row for row in rows if row['kind'] == 'internal-repeat-entry']
    internal_returned = [row for row in rows if row['kind'] == 'internal-repeat-return']
    received = [row for row in rows if row['kind'] == 'rx-entry']
    stores = [row for row in rows if row['kind'] == 'bios-write-return']
    independent = [row for row in micro['events'] if row['kind'] == 'bios-write']
    assert [(row['key'], row['pressed']) for row in external] == [(30, True), (30, False)]
    assert [(row['key'], row['pressed']) for row in internal] == [(30, True), (30, True)]
    assert len(returned) == len(internal_returned) == 2
    assert len(received) == len(stores) == len(independent) == 6
    codes = [row['uart']['next_byte'] for row in received]
    assert codes == [0x29, 0xa9, 0x29, 0xa9, 0x29, 0xa9]
    for after, before in zip(returned, external, strict=True):
        assert after['call'] == before['call'] and after['unchanged_guest']
        assert after['context'] == before['context'] and moment(after) == moment(before)
    assert keyboard(returned[0]) == dict(key=30, wait=500, pause=500, rate=33)
    assert keyboard(returned[1]) == dict(key=0, wait=0, pause=500, rate=33)
    for before, after in zip(internal, internal_returned, strict=True):
        assert keyboard(before) == dict(key=30, wait=0, pause=500, rate=33)
        assert keyboard(after) == dict(key=30, wait=33, pause=500, rate=33)
        assert any('TIMER_AddTick' in (frame['name'] or '') for frame in before['host_stack'])
    for actual, reference in zip(stores, independent, strict=True):
        for field in ['time', 'bios', 'context', 'uart']:
            assert actual[field] == reference[field]
        assert actual['address'] == 0x52f and actual['value'] in (0, 2)
    assert moment(internal[1]) - moment(internal[0]) == 33
    gaps = [moment(stores[i+1]) - moment(stores[i]) for i in (1, 3)]
    assert gaps == [Fraction(55, 96)]*2
    assert external[0]['ordinal'] < internal[0]['ordinal'] < stores[1]['ordinal'] < stores[2]['ordinal'] < internal[1]['ordinal'] < stores[3]['ordinal'] < stores[4]['ordinal'] < external[1]['ordinal']
    return dict(passed=True, external_calls=2, internal_repeat_calls=2, scan_codes=codes,
                independent_software_hardware_pairs=6, repeat_period_ms='33',
                bios_clear_intervals_ms=[str(value) for value in gaps],
                initial_request_to_first_repeat_ms=str(moment(internal[0])-moment(external[0])),
                observed_keyboard_parameters=dict(pause_ticks=500, rate_ticks=33),
                scope='Pinned internal-DOS real-mode fixture. One physical press stays held through two normal timer-driven repeat calls; only then is release requested. Repeated A9/29 bytes create two 55/96ms BIOS clear intervals. Six software stores match independent hardware writes exactly. This does not establish real-PC98 hardware, original TH04 V86 timing or a native production delay.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    capture = args.capture.resolve()
    receipt = json.loads((capture/'receipt.json').read_text())
    assert receipt['passed'] and not receipt['timeout'] and receipt['exit'] == 0
    assert receipt['engine_sha256'] == ENGINE_SHA
    manifest = json.loads((capture/'manifest.json').read_text())
    assert sha(manifest['engine']) == ENGINE_SHA
    for name, digest in receipt['inputs'].items():
        path = Path(name)
        if capture in path.resolve().parents:
            assert sha(path) == digest, name
    assert sha(capture/'events.json') == receipt['events_sha256']
    meta = json.loads((capture/'keyboard-admission.json').read_text())
    assert meta['complete'] and meta['error'] is None and meta['api_calls'] == 2
    assert sha(capture/'keyboard-admission.jsonl') == meta['stream_sha256']
    rows = [json.loads(line) for line in (capture/'keyboard-admission.jsonl').read_text().splitlines()]
    report = reduce(json.loads((capture/'events.json').read_text()), rows)
    report.update(receipt_sha256=sha(capture/'receipt.json'), events_sha256=receipt['events_sha256'],
                  admission_stream_sha256=meta['stream_sha256'], reader_sha256=sha(__file__))
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PC98 HELD REPEAT PASS; 2 external/2 internal; 6 independent writes; 33ms repeats; 55/96ms gaps', flush=True)


if __name__ == '__main__':
    main()
