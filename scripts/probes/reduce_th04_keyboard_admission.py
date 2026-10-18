#!/usr/bin/env python3
"""Reduce a pinned original V86 keyboard capture without assigning input or time."""
from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct


ENGINE = '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1'
# Enum/scan pairs belong to the pinned emulator, not the game's key_det bits.
SCANS = {30: 0x29, 31: 0x2a, 52: 0x1c, 83: 0x3b,
         84: 0x3a, 85: 0x3d, 86: 0x3c}


def moment(row):
    time = row['time']
    raw = time['raw']
    assert raw['CPU_CycleMax'] == 36000
    value = Fraction(time['numerator'], time['denominator'])
    assert value == Fraction(raw['PIC_Ticks']*36000 + 36000 -
                             raw['CPU_CycleLeft'] - raw['CPU_Cycles'], 36000)
    return value


def uart(row):
    item = row['uart']
    raw = bytes.fromhex(item['raw'])
    assert len(raw) == 80 and item['mode'] == raw[8] == 0x3a
    for key, offset in [('data', 0), ('valid', 12), ('rx_busy', 13),
                        ('rx_ready', 14), ('recv_in', 72), ('recv_out', 73)]:
        assert item[key] == raw[offset]
    assert item['recv_in'] < 32 and item['recv_out'] < 32
    assert item['next_byte'] == raw[40+item['recv_out']]
    assert item['io_delay_raw'] == raw[24:32].hex()
    return item, raw


def repeat(row):
    raw = bytes.fromhex(row['keyboard_raw'])
    assert len(raw) == 352
    values = [int.from_bytes(raw[offset:offset+size], 'little')
              for offset, size in [(240, 4), (248, 8), (256, 8), (264, 8)]]
    assert values[2:] == [500, 33], 'pinned repeat pause/rate'
    return values


def x87_index(raw):
    """Decode the actual 80-bit value; the remaining six host bytes are padding."""
    value = bytes.fromhex(raw)
    assert len(value) == 16
    mantissa = int.from_bytes(value[:8], 'little')
    word = int.from_bytes(value[8:10], 'little')
    exponent = word & 0x7fff
    assert exponent != 0x7fff
    if not mantissa:
        return Fraction(0)
    power = (exponent or 1)-16383-63
    result = Fraction(mantissa)*(Fraction(2)**power)
    return -result if word & 0x8000 else result


def pic(row, symbols):
    state = row['pic']
    assert 0 <= state['active_queue_nodes'] <= 8192
    x87_index(state['service_index_raw'])
    slots = set()
    for entry in state['uart_entries']:
        raw = bytes.fromhex(entry['node_raw'])
        assert len(raw) == 48 and raw[:16].hex() == entry['index_raw']
        assert int.from_bytes(raw[16:24], 'little') == entry['value']
        assert int.from_bytes(raw[24:32], 'little') == symbols['_Z12uart_rx_loadm']
        assert 0 <= entry['slot'] < 8192 and entry['slot'] not in slots
        slots.add(entry['slot'])
        pointer = int.from_bytes(raw[32:40], 'little')
        base = symbols['_ZL9pic_queue']
        assert not pointer or (base <= pointer < base+0x60000 and (pointer-base)%48 == 0)
        x87_index(entry['index_raw'])


def reduce(rows, meta, polls, loops):
    assert meta['complete'] and not meta['error'] and not meta['active'] and not meta['in_irq']
    assert len(rows) == meta['records']
    assert [v['ordinal'] for v in rows] == list(range(len(rows)))
    kinds = Counter(v['kind'] for v in rows)
    assert kinds['packet-start'] == kinds['packet-end'] == len(meta['packets'])
    pending = {}
    queue = deque()
    packet = None
    packet_cursor = 0
    previous_repeat = None
    origins = []
    stores = []
    latencies = Counter()
    code_counts = Counter()
    repeat_counts = Counter()
    repeat_intervals = Counter()
    repeat_raw_q = Counter()
    api_counter_splits = 0
    queued_due_offsets = Counter()
    regressions = []
    poll_cursor = 0
    bios_write = None
    rx = None
    irq = None
    for index, row in enumerate(rows):
        kind = row['kind']
        now = moment(row)
        u, raw = uart(row)
        pic(row, meta['symbols'])
        assert struct.unpack('<d', bytes.fromhex(u['io_delay_raw']))[0] == 55/96
        assert row['stage'] == 2
        if index and now < moment(rows[index-1]):
            regressions.append(dict(before=index-1, after=index,
                                    kinds=[rows[index-1]['kind'], kind],
                                    delta_ms=str(now-moment(rows[index-1]))))
        if kind == 'packet-start':
            assert packet is None and not pending and rx is None and irq is None
            packet = row
            proof = meta['packets'][packet_cursor]
            assert (proof['stage'], proof['start_frame'], proof['start_ordinal']) == (row['stage'], row['frame'], index)
            previous_repeat = None
            queue = deque(dict(code=raw[40+(u['recv_out']+i)%32],
                               kind='unobserved-before-packet', ordinal=None)
                          for i in range((u['recv_in']-u['recv_out'])%32))
            repeat(row)
        elif kind == 'packet-end':
            assert packet is not None and not pending and rx is None and irq is None
            repeat(row)
            proof = meta['packets'][packet_cursor]
            assert (proof['end_stage'], proof['end_frame'], proof['end_ordinal']) == (row['stage'], row['frame'], index+1)
            packet_cursor += 1
            packet = None
        elif kind in ('request-entry', 'internal-repeat-entry'):
            assert kind not in pending
            pending[kind] = row
            key, wait, pause, rate = repeat(row)
            if kind == 'internal-repeat-entry':
                assert row['pressed'] and row['key'] == key and wait == 0
                assert any(v['name'] == 'TIMER_AddTick()' for v in row['host_stack'])
                if previous_repeat is not None:
                    assert previous_repeat['key'] == row['key']
                    interval = row['time']['raw']['PIC_Ticks']-previous_repeat['time']['raw']['PIC_Ticks']
                    assert interval == 33, 'uninterrupted typematic tick count'
                    repeat_intervals[str(interval)] += 1
                    repeat_raw_q[str(now-moment(previous_repeat))] += 1
                previous_repeat = row
            else:
                previous_repeat = None
        elif kind in ('request-return', 'internal-repeat-return'):
            entry = pending.pop(kind.replace('return', 'entry'))
            old, old_raw = uart(entry)
            assert entry['context'] == row['context'] and moment(entry) == now
            assert old['recv_out'] == u['recv_out']
            count = (u['recv_in']-old['recv_in'])%32
            added = [raw[40+(old['recv_in']+i)%32] for i in range(count)]
            before, after = repeat(entry), repeat(row)
            code = SCANS[entry['key']]
            if kind == 'internal-repeat-return':
                assert added == [code | 0x80, code], 'repeat break/make pair'
                assert after[:2] == [entry['key'], 33]
                repeat_counts[entry['key']] += 1
            else:
                assert entry['call'] == row['call'] and row['unchanged_guest']
                assert len(bytes.fromhex(entry['conventional_memory_sha256'])) == 32
                assert added == [code if entry['pressed'] else code | 0x80]
                if entry['pressed']:
                    assert after[:2] == [entry['key'], 500]
                elif before[0] == entry['key']:
                    assert after[1] == 0
                api_counter_splits += entry['time']['raw'] != row['time']['raw']
                if not old['rx_busy']:
                    scheduled = row['pic']['uart_entries']
                    assert len(scheduled) == 1
                    due = row['time']['raw']['PIC_Ticks'] + x87_index(scheduled[0]['index_raw'])
                    queued_due_offsets[str(due-now)] += 1
            queue.extend(dict(code=code, kind=entry['kind'], ordinal=entry['ordinal'])
                         for code in added)
        elif kind == 'rx-entry':
            assert rx is None and queue and row['pic']['in_event_service']
            origin = queue[0]
            assert u['next_byte'] == origin['code']
            rx = dict(entry=row, origin=origin)
        elif kind == 'irq1-request':
            assert rx is not None and moment(rx['entry']) == now
            assert u['data'] == rx['origin']['code'] and u['rx_ready'] == 1
        elif kind == 'rx-return':
            assert rx is not None and moment(rx['entry']) == now
            assert u['recv_out'] == (rx['entry']['uart']['recv_out']+1)%32
            assert u['data'] == rx['origin']['code'] and u['rx_ready'] == 1
            assert queue.popleft() == rx['origin']
        elif kind == 'bios-irq-entry':
            assert irq is None and rx is not None and u['rx_ready'] == 1
            assert u['data'] == rx['origin']['code']
            delay = now-moment(rx['entry'])
            assert delay >= 0
            latencies[str(delay)] += 1
            irq = row
        elif kind == 'bios-write-entry':
            assert irq is not None and bios_write is None
            code = rx['origin']['code']
            address, bit = 0x52a+(code & 0x7f)//8, 1 << (code & 7)
            bios = bytes.fromhex(row['bios'])
            expected = bios[address-0x52a]
            expected = expected & ~bit if code & 0x80 else expected | bit
            assert row['address'] == address and row['value'] == expected
            bios_write = row
        elif kind == 'bios-write-return':
            assert bios_write is not None and irq is not None
            assert moment(bios_write) == now
            assert (row['address'], row['value']) == (bios_write['address'], bios_write['value'])
            expected = bytearray.fromhex(bios_write['bios'])
            expected[row['address']-0x52a] = row['value']
            assert bytes.fromhex(row['bios']) == bytes(expected)
            stores.append(dict(row=row, origin=rx['origin']))
            origins.append(rx['origin'])
            code_counts[rx['origin']['code']] += 1
            bios_write = None
        elif kind == 'bios-irq-return':
            assert irq is not None and bios_write is None and u['rx_ready'] == 0
            assert moment(irq) == now
            irq, rx = None, None
        elif kind in ('sampler-entry', 'sampler-return'):
            observed = polls[poll_cursor]
            assert kind == 'sampler-'+observed['kind']
            for field in ('pair', 'stage', 'frame', 'bios', 'key_det', 'return_cs', 'return_ip', 'caller_bytes'):
                assert row[field] == observed[field], (index, field)
            assert now == Fraction(observed['pic_ms_numerator'], observed['pic_ms_denominator'])
            assert row['context']['registers'] == observed['registers']
            assert row['context']['segments'] == observed['segments']
            assert row['context']['cpu_state'] == observed['cpu_state']
            assert row['context']['cpu_state'][1] & 1 and row['context']['flags'] & (1 << 17)
            poll_cursor += 1
        else:
            raise AssertionError('unhandled event '+kind)
    assert packet is None and not pending and rx is None and irq is None
    assert poll_cursor == len(polls)
    assert kinds['request-entry'] == kinds['request-return'] == meta['api_calls']
    assert kinds['internal-repeat-entry'] == kinds['internal-repeat-return']
    assert all(kinds[k] == len(stores) for k in ('rx-entry', 'rx-return', 'irq1-request',
               'bios-irq-entry', 'bios-irq-return', 'bios-write-entry', 'bios-write-return'))
    gaps = []
    for a, b in zip(stores, stores[1:]):
        x, y = a['row'], b['row']
        if (a['origin']['kind'] == b['origin']['kind'] == 'internal-repeat-entry' and
                a['origin']['ordinal'] == b['origin']['ordinal'] and
                a['origin']['code'] == 0xa9 and b['origin']['code'] == 0x29):
            assert x['address'] == y['address'] == 0x52f and not x['value'] & 2 and y['value'] & 2
            assert moment(y) > moment(x)
            gaps.append((x, y, a['origin']['ordinal']))
    zero_tails = []
    for row in rows:
        if row['kind'] != 'sampler-return' or row['return_ip'] != 0x158 or row['key_det'] != 0:
            continue
        candidates = [(a, b, origin) for a, b, origin in gaps
                      if a['ordinal'] < row['ordinal'] < b['ordinal']]
        assert len(candidates) == 1, 'zero tail requires a same-run repeat origin'
        a, b, origin = candidates[0]
        assert moment(a) < moment(row) < moment(b)
        assert loops[row['frame']]['physical'] == 32
        assert not any(v['kind'] == 'request-entry' for v in rows[a['ordinal']:b['ordinal']])
        zero_tails.append(dict(loop=row['frame'], actor_frame=row['frame']+1,
                               repeat_ordinal=origin, break_ordinal=a['ordinal'],
                               sample_ordinal=row['ordinal'], make_ordinal=b['ordinal'],
                               clear_gap_ms=str(moment(b)-moment(a))))
    return dict(passed=True, records=len(rows), packets=len(meta['packets']),
                api_preservation_checks=meta['api_calls'], api_raw_counter_redistributions=api_counter_splits,
                queued_due_from_raw_api_q_ms=dict(queued_due_offsets),
                internal_repeats=dict(repeat_counts), rx_irq_bios_stores=len(stores),
                uninterrupted_repeat_tick_deltas=dict(repeat_intervals),
                uninterrupted_repeat_raw_q_ms=dict(repeat_raw_q),
                scan_counts=dict(code_counts), rx_to_bios_ms=dict(latencies),
                independently_paired_sampler_records=poll_cursor,
                same_run_shot_repeat_gaps=len(gaps),
                shot_clear_gap_ms=dict(Counter(str(moment(b)-moment(a)) for a, b, _ in gaps)),
                zero_tails_inside_repeat_gaps=zero_tails, raw_pic_time_regressions=regressions,
                unattributed_before_packet_bytes=sum(v['kind'] == 'unobserved-before-packet' for v in origins),
                scope='Pinned DOSBox-X original V86 windows only. Actual FIFO bytes bind external requests or normal TIMER_AddTick repeats to RX/IRQ/BIOS stores; pre-packet origins remain unassigned. All sampler records agree with the separate guest CPU observer. Held Shot zero tails require same-run break/sample/make witnesses and no external release. Raw PIC bookkeeping samples are retained, including regressions; they are not a universal event clock. No fitted repeat phase, expected latch, game mutation, native timing, hardware/NP2 or complete-campaign acceptance.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--layout', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads((args.capture/'receipt.json').read_text())
    layout = json.loads(args.layout.read_text())
    assert receipt['complete'] and not receipt['timeout'] and receipt['exit'] == 0
    assert receipt['emulator_sha256'] == layout['engine_sha256'] == ENGINE and layout['passed']
    assert {k: layout['layout'][k] for k in ('keyb_size', 'repeat_key', 'repeat_wait', 'repeat_pause', 'repeat_rate')} == dict(keyb_size=352, repeat_key=240, repeat_wait=248, repeat_pause=256, repeat_rate=264)
    for path, digest in layout['inputs'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
    assert hashlib.sha256(Path(layout['compiler']['path']).read_bytes()).hexdigest() == layout['compiler']['sha256']
    assert hashlib.sha256(args.layout.with_name('probe').read_bytes()).hexdigest() == layout['probe_sha256']
    def data(name):
        value = (args.capture/name).read_bytes()
        assert hashlib.sha256(value).hexdigest() == receipt['files'][name], name
        return value
    raw = data('keyboard-admission.jsonl')
    meta = json.loads(data('keyboard-admission.json'))
    assert hashlib.sha256(raw).hexdigest() == meta['stream_sha256']
    polls = [json.loads(line) for line in data('input-polls.jsonl').splitlines()]
    loops = [json.loads(line) for line in data('stage-input-loops.jsonl').splitlines()]
    report = reduce([json.loads(line) for line in raw.splitlines()], meta, polls, loops)
    report['capture_receipt_sha256'] = hashlib.sha256((args.capture/'receipt.json').read_bytes()).hexdigest()
    report['layout_receipt_sha256'] = hashlib.sha256(args.layout.read_bytes()).hexdigest()
    report['stream_sha256'] = hashlib.sha256(raw).hexdigest()
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('V86 ADMISSION PASS', report['rx_irq_bios_stores'], 'stores;',
          sum(report['internal_repeats'].values()), 'internal repeats;',
          len(report['zero_tails_inside_repeat_gaps']), 'same-run zero tails')


if __name__ == '__main__':
    main()
