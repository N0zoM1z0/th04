"""Data ownership and mutation controls without original executable bytes."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/probes'))
from check_th04_carpet_image_table import EXTENT, compare_tables, initialized_table


class CarpetTableTests(unittest.TestCase):
    def setUp(self):
        self.main = bytearray(256)
        self.main[:2] = b'MZ'
        for offset, value in ((2, 256), (4, 1), (8, 2), (12, 0xffff), (16, 32), (24, 28)):
            struct.pack_into('<H', self.main, offset, value)
        self.main[32] = 0xb8
        struct.pack_into('<H', self.main, 33, 2)
        self.data = struct.pack('<72H', *range(72))
        self.main[64:64+EXTENT] = self.data
        self.map = ' 00020H 000AFH 00090H _DATA DATA\n'

    def test_each_word_mutation_is_reported(self):
        self.assertTrue(compare_tables(self.data, self.data)['passed'])
        for word in range(72):
            mutated = bytearray(self.data)
            mutated[word*2] ^= 128
            result = compare_tables(self.data, mutated)
            self.assertFalse(result['passed'])
            self.assertEqual([(x['level'], x['column']) for x in result['differing_words']],
                             [(word//24, word % 24)])

    def test_initialized_data(self):
        self.assertEqual(initialized_table(self.main, self.map, 2, 0), self.data)

    def test_bss_short_or_duplicate_owner(self):
        for mapping in (self.map.replace('_DATA DATA', '_BSS BSS'),
                        self.map.replace('000AFH', '000AEH'), self.map+self.map):
            with self.assertRaisesRegex(ValueError, 'complete initialized DATA'):
                initialized_table(self.main, mapping, 2, 0)

    def test_wrong_dgroup(self):
        with self.assertRaisesRegex(ValueError, 'DGROUP'):
            initialized_table(self.main, self.map, 1, 16)

    def test_relocated_offset_rejected(self):
        struct.pack_into('<H', self.main, 6, 1)
        struct.pack_into('<HH', self.main, 28, 0, 2)
        with self.assertRaisesRegex(ValueError, 'relocation overlaps'):
            initialized_table(self.main, self.map, 2, 0)

    def test_extent_rejected(self):
        with self.assertRaisesRegex(ValueError, 'extent'):
            compare_tables(self.data, self.data[:-1])


if __name__ == '__main__':
    unittest.main()
