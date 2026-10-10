"""Reject incomplete ownership and over-broad operand normalization."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/probes'))
from check_th04_bullet_invalidation import CALL_SITES, DATA_SITES, SIZE, normalize, owner_extent


class BulletInvalidationContractTests(unittest.TestCase):
    def setUp(self):
        self.entry, self.around = 0x1200, 0x700
        self.data = {name: 0x200+index*16 for index, name in
                     enumerate(dict.fromkeys(name for _, name, _ in DATA_SITES))}
        self.body = bytearray([0x90]*SIZE)
        for at, name, delta in DATA_SITES:
            struct.pack_into('<H', self.body, at, self.data[name]+delta)
        for at in CALL_SITES:
            self.body[at-1] = 0xE8
            struct.pack_into('<h', self.body, at, self.around-self.entry-at-2)
        self.mapping = ' 0708:3364 0096 C=CODE S=TILE_TEXT G=MAIN_01 M=diagnostic_wrappers\\body007_invalidate.asm ACBP=48\n'

    def test_normalization_preserves_every_non_address_byte(self):
        before = normalize(self.body, self.entry, self.around, self.data)
        excluded = {i for at, _, _ in DATA_SITES for i in (at, at+1)}
        excluded.update(i for at in CALL_SITES for i in (at, at+1))
        for index in set(range(SIZE))-excluded:
            changed = self.body.copy()
            changed[index] ^= 1
            if index in {at-1 for at in CALL_SITES}:
                with self.assertRaisesRegex(ValueError, 'callee'):
                    normalize(changed, self.entry, self.around, self.data)
            else:
                self.assertNotEqual(before, normalize(changed, self.entry, self.around, self.data))

    def test_each_data_binding_is_checked_before_substitution(self):
        for at, _, _ in DATA_SITES:
            changed = self.body.copy()
            changed[at] ^= 1
            with self.assertRaisesRegex(ValueError, 'data binding'):
                normalize(changed, self.entry, self.around, self.data)

    def test_each_near_call_target_is_checked(self):
        for at in CALL_SITES:
            changed = self.body.copy()
            changed[at] ^= 1
            with self.assertRaisesRegex(ValueError, 'callee'):
                normalize(changed, self.entry, self.around, self.data)

    def test_complete_extent_is_required(self):
        for changed in (self.body[:-1], self.body+b'\x90'):
            with self.assertRaisesRegex(ValueError, 'complete invalidator extent'):
                normalize(changed, self.entry, self.around, self.data)

    def test_map_owner_must_be_unique_and_start_at_function(self):
        wrapper = 'diagnostic_wrappers/body007_invalidate.asm'
        self.assertEqual(owner_extent(self.mapping, wrapper, 0x708, 0x3364), SIZE)
        for changed in (self.mapping*2, self.mapping.replace('3364', '3362'),
                        self.mapping.replace('S=TILE_TEXT', 'S=OTHER_TEXT')):
            with self.assertRaisesRegex(ValueError, 'unique complete'):
                owner_extent(changed, wrapper, 0x708, 0x3364)


if __name__ == '__main__':
    unittest.main()
