"""Complete-cell and DATA ownership controls, without original executable bytes."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/probes'))
from check_th04_carpet_animation_table import EXTENT, compare_tables
from check_th04_carpet_image_table import initialized_table


class CarpetAnimationTests(unittest.TestCase):
    def setUp(self):
        self.main = bytearray(288)
        self.main[:2] = b'MZ'
        for offset, value in ((2, 288), (4, 1), (8, 2), (12, 0xffff), (16, 32), (24, 28)):
            struct.pack_into('<H', self.main, offset, value)
        self.main[32] = 0xb8
        struct.pack_into('<H', self.main, 33, 2)
        self.data = bytes(index % 3 for index in range(EXTENT))
        self.main[64:64+EXTENT] = self.data
        self.mapping = ' 00020H 000DFH 000C0H _DATA DATA\n'

    def test_every_cell_mutation_is_reported(self):
        self.assertTrue(compare_tables(self.data, self.data)['passed'])
        for index in range(EXTENT):
            mutated = bytearray(self.data)
            mutated[index] = (mutated[index]+1) % 3
            result = compare_tables(self.data, mutated)
            self.assertFalse(result['passed'])
            self.assertEqual([(x['cel'], x['column']) for x in result['differing_cells']],
                             [(index//24, index % 24)])

    def test_complete_initialized_animation(self):
        self.assertEqual(initialized_table(self.main, self.mapping, 2, 0, EXTENT), self.data)

    def test_short_bss_and_duplicate_owners_are_rejected(self):
        for mapping in (self.mapping.replace('_DATA DATA', '_BSS BSS'),
                        self.mapping.replace('000DFH', '000DEH'), self.mapping*2):
            with self.assertRaisesRegex(ValueError, 'complete initialized DATA'):
                initialized_table(self.main, mapping, 2, 0, EXTENT)

    def test_wrong_dgroup_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DGROUP'):
            initialized_table(self.main, self.mapping, 1, 16, EXTENT)

    def test_every_animation_relocation_is_rejected(self):
        struct.pack_into('<H', self.main, 6, 1)
        for offset in range(EXTENT):
            struct.pack_into('<HH', self.main, 28, offset, 2)
            with self.assertRaisesRegex(ValueError, 'relocation overlaps'):
                initialized_table(self.main, self.mapping, 2, 0, EXTENT)

    def test_missing_or_extra_cells_rejected(self):
        for data in (self.data[:-1], self.data+b'\0'):
            with self.assertRaisesRegex(ValueError, 'complete carpet animation extent'):
                compare_tables(self.data, data)

    def test_original_state_domain_rejected(self):
        mutated = bytearray(self.data)
        mutated[5*24+2] = 3
        with self.assertRaisesRegex(ValueError, 'state domain'):
            compare_tables(mutated, self.data)


if __name__ == '__main__':
    unittest.main()
