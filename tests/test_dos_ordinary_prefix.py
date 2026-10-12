import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from compare_th04_dos_ordinary_prefix import compare, ordinary_profile, validate_keyboard_capture


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


class KeyboardAdapterAdmissionTests(unittest.TestCase):
    def setUp(self):
        registers = bytearray(48)
        registers[32:36] = (0x0d2f).to_bytes(4, 'little')
        segments = bytearray(136)
        segments[:8] = (0x1000).to_bytes(8, 'little')
        segments[8:16] = (0x1b70).to_bytes(8, 'little')
        segments[24:32] = (0x2030).to_bytes(8, 'little')
        guard = dict(conventional_sha256='a' * 64, cpu_regs=registers.hex(), segments=segments.hex())
        self.clock = dict(requested_seed=64, resident_linear=0x10000, actions=[
            dict(tick=5000, due=5000, key='KBD_enter', pressed=True, resident_seed=64,
                 unchanged_guest=guard.copy()),
            dict(tick=7000, due=7000, key='KBD_z', pressed=True, resident_seed=64,
                 unchanged_guest=guard.copy()),
        ])
        resident = bytearray(80)
        resident[20:24] = (64).to_bytes(4, 'little')
        self.resident = resident.hex()
        self.first = dict(resident_pointer='00000010')

    def test_observed_seed_and_owner_pass(self):
        validate_keyboard_capture(self.clock, self.first, self.resident)

    def test_different_observed_seed_rejects(self):
        self.clock['actions'][0]['resident_seed'] = 63
        with self.assertRaisesRegex(ValueError, 'observed menu seed'):
            validate_keyboard_capture(self.clock, self.first, self.resident)

    def test_different_main_owner_rejects(self):
        self.first['resident_pointer'] = '00000020'
        with self.assertRaisesRegex(ValueError, 'resident ownership'):
            validate_keyboard_capture(self.clock, self.first, self.resident)

    def test_entry_seed_must_be_observed_trigger_seed(self):
        resident = bytearray.fromhex(self.resident)
        resident[20] = 65
        with self.assertRaisesRegex(ValueError, 'entry seed'):
            validate_keyboard_capture(self.clock, self.first, resident.hex())

    def test_clock_order_cannot_reverse(self):
        self.clock['actions'][-1]['tick'] = 4000
        with self.assertRaisesRegex(ValueError, 'virtual ordering'):
            validate_keyboard_capture(self.clock, self.first, self.resident)

    def test_missing_register_extent_rejects(self):
        self.clock['actions'][0]['unchanged_guest']['cpu_regs'] = '00' * 47
        with self.assertRaisesRegex(ValueError, 'snapshot extent'):
            validate_keyboard_capture(self.clock, self.first, self.resident)

    def test_wrong_op_instruction_rejects(self):
        registers = bytearray.fromhex(self.clock['actions'][0]['unchanged_guest']['cpu_regs'])
        registers[32] ^= 1
        self.clock['actions'][0]['unchanged_guest']['cpu_regs'] = registers.hex()
        with self.assertRaisesRegex(ValueError, 'counter instruction'):
            validate_keyboard_capture(self.clock, self.first, self.resident)


class PrivateProfileIsolationTests(unittest.TestCase):
    def test_repeated_ordinary_profiles_preserve_demo_profile(self):
        target = Path(__file__).resolve().parents[1] / '.analysis/targets/th04/main.exe'
        if not target.is_file():
            self.skipTest('private MAIN unavailable')
        from capture_th04_dos_demos import profile, sha
        data = target.read_bytes()
        self.assertEqual(sha(data), '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b')
        before = profile(data, None)
        first = ordinary_profile(data, data, None)
        second = ordinary_profile(data, data, None)
        self.assertEqual(first, second)
        self.assertEqual(profile(data, None), before)
        self.assertNotEqual(first['hooks'][1], before['hooks'][1])


if __name__ == '__main__':
    unittest.main()
