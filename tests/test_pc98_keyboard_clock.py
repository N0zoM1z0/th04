"""Independent failure dimensions for the timer transaction proof reader."""
import copy
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('keyboard_clock', ROOT/'scripts/probes/pc98_keyboard_clock.py')
CLOCK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLOCK)


def fixture():
    timer = 0x1000
    rows = []
    definitions = [
        ('clock-start', 10, 9000, 0, False, False, 0x2000),
        ('timer-entry', 10, -7, 0, False, False, timer),
        ('tick-store', 11, -7, 0, True, True, timer+0x17),
        ('budget-credit', 11, 35993, 0, False, True, timer+0x42),
        ('queue-credit', 11, 35993, 0, False, False, timer+0x81),
        ('timer-return', 11, 35993, 0, False, False, 0x2100),
        ('clock-end', 11, 32400, 0, False, False, 0x2200),
    ]
    for i, (kind, ticks, left, cycles, credit, queue, pc) in enumerate(definitions):
        raw = dict(PIC_Ticks=ticks, CPU_CycleMax=36000, CPU_CycleLeft=left, CPU_Cycles=cycles)
        value = Fraction(ticks*36000+36000-left-cycles, 36000)
        canonical = value-int(credit)
        rows.append(dict(ordinal=i, kind=kind, host_pc=pc, return_pc=0x2100,
            context={'registers':'unchanged'}, pic={'uart_entries':[]},
            time=dict(numerator=value.numerator, denominator=value.denominator, raw=raw,
                clock_audit=dict(records=i, tick_credit_pending=credit, tick_queue_pending=queue,
                    canonical_numerator=canonical.numerator, canonical_denominator=canonical.denominator))))
    return timer, rows


class KeyboardClockTests(unittest.TestCase):
    def test_complete_transaction_preserves_overrun_and_raw_regression(self):
        timer, rows = fixture()
        report, times = CLOCK.audit_rows(rows, [], timer)
        self.assertTrue(report['passed'])
        self.assertEqual(report['timer_transactions'], 1)
        self.assertEqual(report['merged_raw_regressions'], 1)
        self.assertEqual(report['merged_canonical_regressions'], 0)
        self.assertEqual(times, [])

    def test_reported_phase_cannot_override_instruction_transaction(self):
        timer, rows = fixture()
        rows[2]['time']['clock_audit']['tick_credit_pending'] = False
        with self.assertRaises(AssertionError):
            CLOCK.audit_rows(rows, [], timer)

    def test_tick_write_must_be_the_actual_instruction_boundary(self):
        timer, rows = fixture()
        rows[2]['host_pc'] += 1
        with self.assertRaises(AssertionError):
            CLOCK.audit_rows(rows, [], timer)

    def test_rebased_credit_time_still_needs_budget_continuity(self):
        timer, rows = fixture()
        item = rows[3]['time']
        item['raw']['CPU_CycleLeft'] -= 1
        value = Fraction(item['raw']['PIC_Ticks']*36000+36000-item['raw']['CPU_CycleLeft'],36000)
        item.update(numerator=value.numerator, denominator=value.denominator)
        item['clock_audit'].update(canonical_numerator=value.numerator, canonical_denominator=value.denominator)
        with self.assertRaises(AssertionError):
            CLOCK.audit_rows(rows, [], timer)

    def test_guest_cpu_must_be_unchanged_across_timer(self):
        timer, rows = fixture()
        rows[4]['context']['registers'] = 'changed'
        with self.assertRaises(AssertionError):
            CLOCK.audit_rows(rows, [], timer)

    def test_queue_normalization_requires_exactly_one_millisecond(self):
        timer, rows = fixture()
        one_and_half = (0xc000000000000000).to_bytes(8,'little')+(0x3fff).to_bytes(2,'little')+bytes(6)
        half = (0x8000000000000000).to_bytes(8,'little')+(0x3ffe).to_bytes(2,'little')+bytes(6)
        rows[3]['pic']['uart_entries'] = [dict(slot=4, index_raw=one_and_half.hex())]
        rows[4]['pic']['uart_entries'] = [dict(slot=4, index_raw=half.hex())]
        report, _ = CLOCK.audit_rows(rows, [], timer)
        self.assertEqual(report['queue_entries_observed_minus_one'], 1)
        rows[4]['pic']['uart_entries'][0]['index_raw'] = (half[:8]+(0xbffe).to_bytes(2,'little')+bytes(6)).hex()
        with self.assertRaises(AssertionError):
            CLOCK.audit_rows(rows, [], timer)

    def test_clamping_cannot_replace_the_pending_credit(self):
        timer, rows = fixture()
        proof = rows[2]['time']['clock_audit']
        proof['canonical_numerator'] = rows[2]['time']['numerator']
        proof['canonical_denominator'] = rows[2]['time']['denominator']
        with self.assertRaises(AssertionError):
            CLOCK.audit_rows(rows, [], timer)

    def test_admission_phase_is_derived_from_prior_clock_records(self):
        timer, rows = fixture()
        admission = copy.deepcopy(rows[2])
        admission['ordinal'] = 0
        admission['kind'] = 'request-entry'
        admission['time']['clock_audit']['records'] = 3
        report, values = CLOCK.audit_rows(rows, [admission], timer)
        self.assertEqual(report['admission_samples_with_pending_credit'], 1)
        self.assertEqual(values, [Fraction(11)+Fraction(7,36000)])
        admission['time']['clock_audit']['records'] = 4
        with self.assertRaises(AssertionError):
            CLOCK.audit_rows(rows, [admission], timer)


if __name__ == '__main__':
    unittest.main()
