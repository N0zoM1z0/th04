import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from compare_th04_dos_ordinary_prefix import compare


class OrdinaryPrefixAdmissionTests(unittest.TestCase):
    def setUp(self):
        row = dict(frame='0000', input='2000', shift_raw='00', stage='00',
                   lcg='12345678', ring='aabb', ring_cursor='0000', hit='00',
                   resident_pointer='00000010')
        resident = bytearray(80)
        resident[:11] = b'HUMAConfig\0'
        resident[15] = 1
        self.left = dict(fields=list(row), rows=[row], resident=[resident.hex()], events=[[]])
        self.right = copy.deepcopy(self.left)

    def test_same_fixture_passes(self):
        self.assertTrue(compare(self.left, self.right)['passed'])

    def test_different_initial_rng_rejects_before_state_comparison(self):
        self.right['rows'][0]['lcg'] = '87654321'
        self.right['rows'][0]['hit'] = '01'
        result = compare(self.left, self.right)
        self.assertFalse(result['admitted'])
        self.assertIn('initial-lcg', result['rejection_reasons'])
        self.assertIsNone(result['first_difference'])

    def test_different_ring_or_cursor_rejects(self):
        for field in ('ring', 'ring_cursor'):
            with self.subTest(field=field):
                right = copy.deepcopy(self.right)
                right['rows'][0][field] = 'ffff'
                self.assertIn('initial-' + field, compare(self.left, right)['rejection_reasons'])

    def test_different_consumed_input_rejects(self):
        for field in ('input', 'shift_raw', 'stage'):
            with self.subTest(field=field):
                right = copy.deepcopy(self.right)
                right['rows'][0][field] = '00'
                if field != 'input':
                    right['rows'][0][field] = '01'
                self.assertIn('consumed-' + field, compare(self.left, right)['rejection_reasons'])

    def test_entry_resident_seed_rejects(self):
        value = bytearray.fromhex(self.right['resident'][0])
        value[20] = 1
        self.right['resident'][0] = value.hex()
        self.assertIn('initial-resident-settings-seed', compare(self.left, self.right)['rejection_reasons'])

    def test_admitted_hit_difference_is_a_state_failure(self):
        self.right['rows'][0]['hit'] = '01'
        result = compare(self.left, self.right)
        self.assertTrue(result['admitted'])
        self.assertFalse(result['passed'])
        self.assertEqual(result['first_difference']['field'], 'hit')

    def test_admitted_rng_call_difference_is_a_failure(self):
        self.right['events'][0].append([4, 15])
        self.assertEqual(compare(self.left, self.right)['first_difference']['field'], 'ordered-rng-calls')

    def test_runtime_pointer_is_preserved_outside_state_comparison(self):
        self.right['rows'][0]['resident_pointer'] = '00000020'
        self.assertTrue(compare(self.left, self.right)['passed'])

    def test_performance_counters_are_outside_fixture_admission(self):
        value = bytearray.fromhex(self.right['resident'][0])
        value[64:72] = bytes(range(8))
        self.right['resident'][0] = value.hex()
        self.assertTrue(compare(self.left, self.right)['passed'])


if __name__ == '__main__':
    unittest.main()
