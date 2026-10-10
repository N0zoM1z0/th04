"""Adversarial controls for complete TH04 demo traces, without private assets."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from capture_th04_dos_demos import FIELDS
from compare_th04_dos_demos import compare, validate_trace


class DemoTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = bytearray(96)
        cls.main[:2] = b'MZ'
        cls.main[8:10] = (2).to_bytes(2, 'little')
        cls.main = bytes(cls.main)
        cls.prof = dict(dgroup=1, hooks=[(1, 2, 3), (2, 2, 4), (3, 3, 5), (4, 3, 6)],
                        fields=[(f[0], 0, f[3]) for f in FIELDS])
        cls.demos = {1:bytes(8000)}
        resident = bytearray(80)
        resident[:11] = b'HUMAConfig\0'
        resident[0x12] = 48
        resident[0x3e] = 1
        cls.lines = ['L 1 1000 00000000 00000000 '+bytes(64).hex()]
        for frame in range(3997):
            values = {f[0]:bytes(f[3]).hex() for f in FIELDS}
            values['frame'] = frame.to_bytes(2, 'little').hex()
            values['stage'] = '03'
            kind, ip = ('T', 4) if frame == 3996 else ('I', 3)
            cls.lines.append(f'{kind} 1 1002 {ip:04x} 1001 0 0 '
                             +' '.join(values.values())+' '+resident.hex())

    def parse(self, lines):
        return validate_trace(('\n'.join(lines)+'\n').encode(), self.main, self.prof, self.demos, 1)

    def test_complete_extent_and_terminal(self):
        captures, diagnostics = self.parse(self.lines)
        self.assertEqual(len(captures[1]), 3997)
        self.assertEqual(captures[1][-1]['decision'], 'T')
        self.assertEqual(diagnostics['demos']['1']['rows'], 3997)

    def test_equal_prefix_is_incomplete(self):
        with self.assertRaisesRegex(ValueError, 'missing completed'):
            self.parse(self.lines[:-1])

    def test_duplicate_frame(self):
        with self.assertRaisesRegex(ValueError, 'duplicate/out-of-order'):
            self.parse(self.lines[:200]+[self.lines[199]]+self.lines[200:])

    def test_missing_frame(self):
        with self.assertRaisesRegex(ValueError, 'missing/duplicate'):
            self.parse(self.lines[:200]+self.lines[201:])

    def test_out_of_order_frame(self):
        lines = self.lines.copy()
        lines[200], lines[201] = lines[201], lines[200]
        with self.assertRaisesRegex(ValueError, 'out-of-order'):
            self.parse(lines)

    def test_terminal_is_not_update(self):
        lines = self.lines.copy()
        lines[-1] = lines[-1].replace('T 1 1002 0004', 'I 1 1002 0003')
        with self.assertRaisesRegex(ValueError, 'terminal update'):
            self.parse(lines)

    def test_last_input_must_be_consumed(self):
        lines = self.lines.copy()
        cells = lines[-1].split()
        cells[8] = '0100'
        lines[-1] = ' '.join(cells)
        with self.assertRaisesRegex(ValueError, 'consumed replay'):
            self.parse(lines)

    def test_loaded_byte_mutation(self):
        lines = self.lines.copy()
        lines[0] = lines[0][:-2]+'01'
        with self.assertRaisesRegex(ValueError, 'loaded MAIN'):
            self.parse(lines)

    def test_counter_without_caller_is_rejected(self):
        lines = self.lines.copy()
        cells = lines[101].split()
        cells[6] = '256'
        lines[101] = ' '.join(cells)
        with self.assertRaisesRegex(ValueError, 'complete caller log'):
            self.parse(lines)

    def test_extra_ring_wrap_is_visible_with_same_cursor(self):
        lines = self.lines.copy()
        rng = 'R 1 3 1003 0006 1001 0100 1234 0000'
        lines[101:101] = [rng]*256
        for index in range(357, len(lines)):
            cells = lines[index].split()
            cells[6] = '256'
            lines[index] = ' '.join(cells)
        mutated, _ = self.parse(lines)
        baseline, _ = self.parse(self.lines)
        self.assertEqual(baseline[1][100]['ring_cursor'], mutated[1][100]['ring_cursor'])
        self.assertEqual(mutated[1][100]['ring_calls'], 256)
        self.assertNotEqual(baseline[1][100], mutated[1][100])

    def test_rng_event_after_terminal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'RNG event order'):
            self.parse(self.lines+['R 1 3 1003 0006 1001 0100 1234 0000'])

    def test_equal_rng_state_with_different_mask_is_visible(self):
        prof = self.prof | dict(hooks=self.prof['hooks']+[(4, 3, 7)])
        def replay(mask):
            lines = self.lines.copy()
            for index in range(101, len(lines)):
                cells = lines[index].split()
                cells[6] = '1'
                lines[index] = ' '.join(cells)
            lines.insert(101, f'R 1 4 1003 0007 1001 0100 1234 {mask:04x}')
            return validate_trace(('\n'.join(lines)+'\n').encode(), self.main, prof, self.demos, 1)[0][1][100]
        a, b = replay(7), replay(31)
        self.assertEqual(a['ring_cursor'], b['ring_cursor'])
        self.assertEqual(a['ring_total_calls'], b['ring_total_calls'])
        self.assertNotEqual(a['rng_events'], b['rng_events'])

    def test_wrong_demo_rotation(self):
        lines = self.lines.copy()
        cells = lines[1].split()
        resident = bytearray.fromhex(cells[-1])
        resident[0x3e] = 2
        cells[-1] = resident.hex()
        lines[1] = ' '.join(cells)
        with self.assertRaisesRegex(ValueError, 'demo rotation'):
            self.parse(lines)

    def paired(self, candidate_lines, different_reset=False):
        original, diagnostics = self.parse(self.lines)
        candidate, _ = self.parse(candidate_lines)
        receipt = dict(demos=1, role='original', original_hdi_sha256='same',
                       starting_files={'CFG':'same'}, demo_sha256='same', archive_sha256='same',
                       font_sha256='same', config_sha256='same', emulator_sha256='same',
                       observer_source_sha256='same')
        other = receipt | dict(role='ordinary-reconstructed')
        if different_reset:
            other['starting_files'] = {'CFG':'different'}
        with patch('compare_th04_dos_demos.load_capture', side_effect=[
                (receipt, original, diagnostics), (other, candidate, diagnostics)]):
            return compare(Path('original'), Path('candidate'))

    def test_complete_pair(self):
        result = self.paired(self.lines)
        self.assertTrue(result['passed'])
        self.assertEqual(result['gameplay_rows'], 3996)
        self.assertEqual(result['terminal_rows'], 1)

    def test_first_score_difference(self):
        lines = self.lines.copy()
        cells = lines[101].split()
        cells[11] = '0100000000000000'
        lines[101] = ' '.join(cells)
        result = self.paired(lines)
        self.assertFalse(result['passed'])
        self.assertEqual(result['first_difference']['frame'], 100)
        self.assertEqual(list(result['first_difference']['fields']), ['score_digits'])
        self.assertEqual(result['demo_results']['1']['equal_boundaries'], 100)

    def test_equal_states_with_different_reset_fail(self):
        result = self.paired(self.lines, different_reset=True)
        self.assertFalse(result['passed'])
        self.assertIn('paired reset', result['invalid_capture'])


if __name__ == '__main__':
    unittest.main()
