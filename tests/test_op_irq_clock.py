"""Independent IRQ phase and counter-stream rejecting mutations."""
from pathlib import Path
import copy
import math
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/runtime'))
import verify_op_irq_clock as irq


def sample(time):
    ticks = int(time)
    left = 24000 - math.ceil((time - ticks) * 24000)
    state = dict(pic_ticks=ticks, CPU_CycleMax=24000, CPU_CycleLeft=left, CPU_Cycles=0)
    return ticks + (24000-left)/24000, state


def fixture():
    rows, timers = [], []
    def scalar(name, time, one, two):
        ms, state = sample(time)
        rows.append(dict(name=name, pic_ms=ms, cycle_state=state,
                         vsync_counts_hex=struct.pack('<HH', one, two).hex(),
                         cadence_increment_hex='0000', cadence_accumulator_hex='0000', ax=0))
    scalar('main_entry', 0, 0, 0)
    period = 106*440*1000/2631575
    for index in range(2):
        raw = bytearray(540)
        struct.pack_into('<HHH6B', raw, 180, 400,80,80,8,8,10,8,7,25)
        struct.pack_into('<d', raw, 491, index*period)
        struct.pack_into('<d', raw, 499, period)
        raw[196:199] = raw[428:431] = bytes((0,index+1,32))
        delay, _ = irq.raster(raw)
        actual, state = sample(index*period + delay + 2/24000)
        timers.append(dict(kind='vsync_irq_event', armed=1, pic_ms=actual, cycles=state,
                           gdc_clock_hex=raw.hex(), display_events=index+1))
        scalar('irq_before_increment', actual+(60-index*10)/24000, index,index)
    scalar('logo_wait_reset', 35, 0,2)
    return dict(rows=rows, timer_rows=timers)


class IrqClockTests(unittest.TestCase):
    def test_raster_and_complete_counter_progression(self):
        result = irq.check_irqs(fixture())
        self.assertEqual(result['counted_irqs'], 2)
        self.assertEqual(result['terminal_counters'], (0,2))
        self.assertGreater(result['service_latency_cycles'][0], result['service_latency_cycles'][1])

    def test_missing_or_duplicated_irq_and_wrong_counter_reject(self):
        original = fixture()
        for kind in ('missing', 'duplicate', 'word'):
            changed = copy.deepcopy(original)
            if kind == 'missing':changed['rows'].pop(1)
            elif kind == 'duplicate':changed['rows'].insert(1,copy.deepcopy(changed['rows'][1]))
            else:changed['rows'][1]['vsync_counts_hex'] = '00000100'
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                irq.check_irqs(changed)

    def test_blink_and_frame_start_cannot_supply_irq_phase(self):
        for offset in (197,491):
            changed = fixture();row = changed['timer_rows'][0]
            raw = bytearray.fromhex(row['gdc_clock_hex'])
            if offset == 197:raw[offset] ^= 1
            else:struct.pack_into('<d',raw,offset,1)
            row['gdc_clock_hex'] = raw.hex()
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                irq.check_irqs(changed)

    def test_unobserved_skip_or_rate_and_false_pic_time_reject(self):
        changed = fixture();changed['rows'][1]['cadence_increment_hex'] = '0100'
        with self.assertRaises(ValueError):irq.check_irqs(changed)
        changed = fixture();changed['timer_rows'][0]['pic_ms'] += .001
        with self.assertRaises(ValueError):irq.check_irqs(changed)
        raw = bytearray.fromhex(fixture()['timer_rows'][0]['gdc_clock_hex']);raw[535] = 1
        with self.assertRaises(ValueError):irq.raster(raw)


if __name__ == '__main__':
    unittest.main()
