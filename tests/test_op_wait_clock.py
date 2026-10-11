"""Reject wait-owner mistakes that a successful refresh-count replay can hide."""
from pathlib import Path
import copy
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/runtime'))
import verify_op_wait_clock as waits


def row(name, time, one, two, index=0):
    ticks = int(time)
    state = dict(pic_ticks=ticks, CPU_CycleMax=1000000,
                 CPU_CycleLeft=1000000 - round((time - ticks) * 1000000), CPU_Cycles=0)
    actual = ticks + (state['CPU_CycleMax'] - state['CPU_CycleLeft']) / state['CPU_CycleMax']
    return dict(name=name, index=index, cycle_state=state, pic_ms=actual,
                vsync_counts_hex=struct.pack('<HH', one, two).hex(),
                display_events=12, stack_hex=struct.pack('<HHHH', 0, 0, 0, 2).hex(), ax=2)


def fixture(off=False):
    prefix = [row('measure_start', 0, 10, 10)]
    if off:
        prefix += [row('frame_delay_enter', .01, 10, 10),
                   row('frame_delay_return', .02, 0, 10), row('after_measure', .03, 0, 10)]
        first = [(1, 11), (2, 12), (0, 12)]
    else:
        prefix += [row('measure_end', .5, 100, 100), row('after_measure', .6, 100, 100)]
        first = [(104, 104), (104, 104), (0, 104)]
    for name, time, (one, two) in zip(waits.WAIT_POINTS, (1, 1.1, 1.100001), first, strict=True):
        prefix.append(row(name, time, one, two))
    last_two = first[-1][1]
    for name, time, pair in zip(waits.WAIT_POINTS, (1.2, 2, 2.000001),
                               ((0, last_two), (2, last_two + 2), (0, last_two + 2)), strict=True):
        prefix.append(row(name, time, *pair))
    for index, item in enumerate(prefix):
        item['index'] = index
    return prefix


class WaitOwnersTests(unittest.TestCase):
    def test_busy_measure_preserves_inherited_counter(self):
        result = waits.check_waits(fixture(), False)
        self.assertEqual(result['measure_ready'], (100, 100))
        self.assertEqual(result['logo_waits'][0]['counted_irq_progress'], 0)
        # Two counted IRQs may cross a different number of GDC observer seams.
        self.assertEqual(result['logo_waits'][1]['counted_irq_progress'], 2)
        self.assertEqual(result['logo_waits'][1]['gdc_events'], 0)

    def test_zero_fallback_resets_and_returns_without_irq_progress(self):
        result = waits.check_waits(fixture(True), True)
        self.assertEqual(result['measure_ready'], (0, 10))
        self.assertEqual(result['logo_waits'][0]['counted_irq_progress'], 1)

    def test_unsigned_wrap_and_irq_after_reset_preserve_second_counter(self):
        self.assertEqual(waits.continuous(row('a', 0, 65535, 65535), row('b', 1, 0, 0)), 1)
        waits.reset(row('a', 0, 9000, 65535), row('b', 1, 1, 0))

    def test_resetting_busy_counter_or_forgetting_logo_reset_rejects(self):
        for name in ('after_measure', 'logo_wait_reset'):
            changed = copy.deepcopy(fixture())
            target = next(r for r in changed if r['name'] == name)
            one, two = waits.counters(target)
            target['vsync_counts_hex'] = struct.pack('<HH', 0 if one else 104, two).hex()
            with self.subTest(name=name), self.assertRaises(ValueError):
                waits.check_waits(changed, False)

    def test_missing_terminal_pair_or_false_pic_time_rejects(self):
        changed = fixture()
        with self.assertRaises(ValueError):
            waits.check_waits(changed[:-1], False)
        changed[-2]['pic_ms'] += 1
        with self.assertRaisesRegex(ValueError, 'PIC time'):
            waits.check_waits(changed, False)

    def test_second_counter_extent_and_fallback_reset_are_required(self):
        with self.assertRaisesRegex(ValueError, 'extent'):
            waits.counters(dict(vsync_counts_hex='0000'))
        changed = fixture(True)
        changed[2]['vsync_counts_hex'] = struct.pack('<HH', 10, 10).hex()
        with self.assertRaisesRegex(ValueError, 'zero fallback'):
            waits.check_waits(changed, True)


if __name__ == '__main__':
    unittest.main()
