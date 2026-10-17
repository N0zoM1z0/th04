#!/usr/bin/env python3
"""Reduce actual pinned-emulator UART/IRQ/BIOS events without fitting a delay."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct


def moment(event):
    value = event['time']
    raw = value['raw']
    assert raw['CPU_CycleMax'] == 36000
    actual = Fraction(raw['PIC_Ticks']*36000 + 36000 - raw['CPU_CycleLeft'] - raw['CPU_Cycles'], 36000)
    assert actual == Fraction(value['numerator'], value['denominator'])
    return actual


def reduce(events):
    assert events['complete'] and events['error'] is None and events['api_count'] == 8
    assert events['markers'] == list(range(0xa0, 0xa9))
    requests, receives, interrupts, stores, markers = [], [], [], [], {}
    times = []
    for event in events['events']:
        times.append(moment(event))
        assert not event['context']['cpu_state'][1] & 0x80000001
        assert not event['context']['flags'] & 0x20000
        uart, raw = event['uart'], bytes.fromhex(event['uart']['raw'])
        assert len(raw) == 80 and len(bytes.fromhex(event['bios'])) == 10
        assert (uart['data'], uart['rx_busy'], uart['rx_ready'], uart['recv_in'], uart['recv_out']) == (raw[0], raw[13], raw[14], raw[72], raw[73])
        assert abs(struct.unpack('<d', raw[24:32])[0] - 55/96) < 1e-12
        kind = event['kind']
        if kind == 'request':
            assert event['unchanged_guest'] and moment(event) == Fraction(event['before_time']['numerator'], event['before_time']['denominator'])
            assert len(event['conventional_memory_sha256']) == 64
            requests.append(event)
        elif kind == 'rx-entry':
            receives.append(event)
        elif kind == 'irq1-request':
            interrupts.append(event)
        elif kind == 'bios-write':
            stores.append(event)
        elif kind == 'marker':
            markers[event['value']] = event
    assert times == sorted(times)
    assert len(requests) == len(receives) == len(interrupts) == len(stores) == 8
    expected = [('KBD_z', True, 0x29, 'shot'), ('KBD_z', False, 0xa9, 'shot'),
                ('KBD_enter', True, 0x1c, 'enter'), ('KBD_enter', False, 0x9c, 'enter'),
                ('KBD_z', True, 0x29, 'shot'), ('KBD_z', False, 0xa9, 'shot'),
                ('KBD_z', True, 0x29, 'shot'), ('KBD_z', False, 0xa9, 'shot')]
    rows = []
    previous_rx = Fraction(0)
    for request, rx, irq, store, expected_row in zip(requests, receives, interrupts, stores, expected, strict=True):
        key, down, code, cell = expected_row
        assert (request['key'], request['pressed']) == (key, down)
        assert rx['uart']['next_byte'] == irq['uart']['data'] == code
        assert store['cell'] == cell and moment(rx) == moment(irq)
        scheduled_from = max(moment(request), previous_rx)
        assert moment(rx) - scheduled_from == Fraction(55, 96)
        matrix = bytes.fromhex(store['bios'])
        assert bool(matrix[5 if cell == 'shot' else 3] & (2 if cell == 'shot' else 16)) == down
        latency = moment(store) - moment(rx)
        assert latency > 0
        rows.append(dict(key=key, pressed=down, scan_code=code,
                         request_to_rx_ms=str(moment(rx)-moment(request)),
                         scheduled_transfer_ms=str(moment(rx)-scheduled_from),
                         rx_to_bios_ms=str(latency)))
        previous_rx = moment(rx)
    blocked, pending, resumed = markers[0xa5], markers[0xa6], markers[0xa7]
    assert not blocked['context']['flags'] & 0x200 and not pending['context']['flags'] & 0x200
    assert resumed['context']['flags'] & 0x200
    assert pending['uart']['rx_ready'] and not bytes.fromhex(pending['bios'])[5] & 2
    assert moment(receives[6]) < moment(pending) < moment(stores[6]) < moment(resumed)
    assert all(row['rx_to_bios_ms'] == '1/2250' for i, row in enumerate(rows) if i != 6)
    return dict(passed=True, requests=8, rx_events=8, irq1_requests=8, bios_stores=8,
                serialized_transfer_ms='55/96', interrupt_mask_control_passed=True, rows=rows,
                scope='Observed pinned normal-core emulator on authored internal-DOS real-mode code. UART transfer is serialized at 55/96ms; enabled-interrupt BIOS service takes16 cycles in this fixture and CLI postpones it. Receive readiness alone is not BIOS admission. These are emulator/fixture observations, not original TH04 V86 latency, hardware timing or a justified native production delay.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads((args.capture/'receipt.json').read_text())
    raw = (args.capture/'events.json').read_bytes()
    assert receipt['passed'] and not receipt['timeout'] and hashlib.sha256(raw).hexdigest() == receipt['events_sha256']
    assert receipt['engine_sha256'] == '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1'
    manifest = json.loads((args.capture/'manifest.json').read_text())
    assert hashlib.sha256(Path(manifest['engine']).read_bytes()).hexdigest() == receipt['engine_sha256']
    for name, digest in receipt['inputs'].items():
        path = Path(name)
        if args.capture.resolve() in path.resolve().parents:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
    report = reduce(json.loads(raw))
    report.update(events_sha256=receipt['events_sha256'], receipt_sha256=hashlib.sha256((args.capture/'receipt.json').read_bytes()).hexdigest(),
                  reducer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PC98 UART ORACLE PASS; 8 requests/RX/IRQ/BIOS stores; CLI/STI control', flush=True)


if __name__ == '__main__':
    main()
