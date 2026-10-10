"""Reject incomplete ownership and over-broad operand normalization."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/probes'))
from check_th04_pointnum_renderer import CALL_SITES, DATA_SITES, SELF_WIDTH_SITE, SELF_WIDTH_IMMEDIATE, SIZE, normalize, owner_extent


class PointnumRendererContractTests(unittest.TestCase):
    def setUp(self):
        self.entry = 0x1200
        self.callees = dict(scroll=0x700, put=0x1600)
        self.data = {name: 0x200+index*16 for index, name in
                     enumerate(dict.fromkeys(name for _, name, _ in DATA_SITES))}
        self.body = bytearray([0x90]*SIZE)
        for at, name, delta in DATA_SITES:
            struct.pack_into('<H', self.body, at, self.data[name]+delta)
        for at, name in CALL_SITES:
            self.body[at-1] = 0xE8
            struct.pack_into('<h', self.body, at, self.callees[name]-self.entry-at-2)
        self.body[SELF_WIDTH_SITE-3:SELF_WIDTH_SITE] = b'\x2e\x89\x0e'
        struct.pack_into('<H', self.body, SELF_WIDTH_SITE, self.entry+SELF_WIDTH_IMMEDIATE)
        self.mapping = ' 0708:2B2A 009A C=CODE S=CIRCLE_TEXT G=MAIN_01 M=diagnostic_wrappers\\body005_render.asm ACBP=48\n'

    def test_normalization_preserves_every_non_address_byte(self):
        before = normalize(self.body, self.entry, self.callees, self.data)
        excluded = {i for at, _, _ in DATA_SITES for i in (at, at+1)}
        excluded.update(i for at, _ in CALL_SITES for i in (at, at+1))
        excluded.update((SELF_WIDTH_SITE, SELF_WIDTH_SITE+1))
        for index in set(range(SIZE))-excluded:
            changed = self.body.copy()
            changed[index] ^= 1
            if index in {at-1 for at, _ in CALL_SITES}:
                with self.assertRaisesRegex(ValueError, 'callee'):
                    normalize(changed, self.entry, self.callees, self.data)
            elif index in range(SELF_WIDTH_SITE-3, SELF_WIDTH_SITE):
                with self.assertRaisesRegex(ValueError, 'self-modifying'):
                    normalize(changed, self.entry, self.callees, self.data)
            else:
                self.assertNotEqual(before, normalize(changed, self.entry, self.callees, self.data))

    def test_each_data_binding_is_checked_before_substitution(self):
        for at, _, _ in DATA_SITES:
            changed = self.body.copy()
            changed[at] ^= 1
            with self.assertRaisesRegex(ValueError, 'data binding'):
                normalize(changed, self.entry, self.callees, self.data)

    def test_each_near_call_target_is_checked(self):
        for at, name in CALL_SITES:
            changed = self.body.copy()
            changed[at] ^= 1
            with self.assertRaisesRegex(ValueError, 'callee'):
                normalize(changed, self.entry, self.callees, self.data)

    def test_self_modifying_store_must_address_its_own_immediate(self):
        changed = self.body.copy()
        changed[SELF_WIDTH_SITE] ^= 1
        with self.assertRaisesRegex(ValueError, 'self-modifying'):
            normalize(changed, self.entry, self.callees, self.data)

    def test_complete_extent_is_required(self):
        for changed in (self.body[:-1], self.body+b'\x90'):
            with self.assertRaisesRegex(ValueError, 'complete renderer extent'):
                normalize(changed, self.entry, self.callees, self.data)

    def test_map_owner_must_be_unique_and_start_at_function(self):
        wrapper = 'diagnostic_wrappers/body005_render.asm'
        self.assertEqual(owner_extent(self.mapping, wrapper, 0x708, 0x2B2A), SIZE)
        for changed in (self.mapping*2, self.mapping.replace('2B2A', '2B28'),
                        self.mapping.replace('S=CIRCLE_TEXT', 'S=OTHER_TEXT')):
            with self.assertRaisesRegex(ValueError, 'unique complete'):
                owner_extent(changed, wrapper, 0x708, 0x2B2A)


if __name__ == '__main__':
    unittest.main()
