"""Mutation controls for initialized DATA ownership, without original assets."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from check_th04_midboss4_initial_state import data_byte


class MidbossInitialStateTests(unittest.TestCase):
    def setUp(self):
        self.main = bytearray(96)
        self.main[:2] = b'MZ'
        for offset, value in ((2, 96), (4, 1), (8, 2), (12, 0xffff), (16, 32), (24, 28)):
            self.main[offset:offset+2] = value.to_bytes(2, 'little')
        self.main[32] = 0xb8
        self.main[33:35] = (2).to_bytes(2, 'little')
        self.main[32+32+3] = 1
        self.map = ' 00020H 00027H 00008H _DATA DATA\n'

    def test_initialized_value_and_mutation(self):
        self.assertEqual(data_byte(self.main, self.map, 2, 3), 1)
        self.main[67] = 0
        self.assertEqual(data_byte(self.main, self.map, 2, 3), 0)

    def test_bss_rejected_even_with_correct_backing_byte(self):
        with self.assertRaisesRegex(ValueError, 'initialized _DATA'):
            data_byte(self.main, self.map.replace('_DATA DATA', '_BSS BSS'), 2, 3)

    def test_wrong_dgroup_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DGROUP'):
            data_byte(self.main, self.map, 1, 19)

    def test_symbol_outside_data_rejected(self):
        with self.assertRaisesRegex(ValueError, 'initialized _DATA'):
            data_byte(self.main, self.map, 2, 8)

    def test_duplicate_data_owner_rejected(self):
        with self.assertRaisesRegex(ValueError, 'initialized _DATA'):
            data_byte(self.main, self.map+self.map, 2, 3)


if __name__ == '__main__':
    unittest.main()
