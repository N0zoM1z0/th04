"""Mutation controls for state ownership and complete scalar comparison."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
import th04_demo_globals as owners
import compare_th04_demo_dgroup as compare


class GlobalOwnerTests(unittest.TestCase):
    def setUp(self):
        self.field = ('boss', 0x1234, 24, 0x20, 0x100, 'c606431200', 2, 15, 'boss_reset()', 0, 32)
        self.target = bytearray(156258)
        self.target[6144+0x200+0x100:6144+0x200+0x105] = bytes.fromhex(self.field[5])
        self.candidate = bytearray(1024)
        self.candidate[8:10] = (2).to_bytes(2, 'little')
        self.start = 32+0x10*16+0x100
        self.candidate[self.start:self.start+5] = bytes.fromhex('c6060f3000')
        self.symbols = {'_boss': (0x200, 0x3000), 'boss_reset()': (0x10, 0x100)}
        self.enterContext(patch.object(owners, 'FIELDS', (self.field,)))
        self.enterContext(patch.object(owners, 'sha', return_value=
            '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'))

    def attest(self):
        return owners.attest_fields(self.target, self.candidate, self.symbols, 0x200)

    def test_complete_extent_and_both_instruction_addresses(self):
        extents, witnesses = self.attest()
        self.assertEqual(extents, [('boss', 0x1234, 0x3000, 1, 24)])
        self.assertEqual(witnesses[0]['original_ip'], 0x100)
        self.assertEqual(witnesses[0]['candidate_ip'], 0x100)

    def test_each_original_instruction_byte_is_required(self):
        for index in range(5):
            with self.subTest(index=index):
                at = 6144+0x300+index
                self.target[at] ^= 1
                with self.assertRaisesRegex(ValueError, 'original instruction'):
                    self.attest()
                self.target[at] ^= 1

    def test_candidate_opcode_operand_and_immediate_required(self):
        for index in range(5):
            with self.subTest(index=index):
                self.candidate[self.start+index] ^= 1
                with self.assertRaisesRegex(ValueError, 'candidate instruction'):
                    self.attest()
                self.candidate[self.start+index] ^= 1

    def test_matching_instruction_in_other_owner_rejected(self):
        instruction = self.candidate[self.start:self.start+5]
        self.candidate[self.start:self.start+5] = bytes(5)
        self.candidate[self.start+32:self.start+37] = instruction
        with self.assertRaisesRegex(ValueError, 'candidate instruction'):
            self.attest()

    def test_instruction_bytes_embedded_across_other_instructions_rejected(self):
        instruction = self.candidate[self.start:self.start+5]
        self.candidate[self.start:self.start+6] = b'\xb8'+instruction
        with self.assertRaisesRegex(ValueError, 'candidate instruction'):
            self.attest()

    def test_wrong_symbol_and_segment_rejected(self):
        for pair in ((0x201, 0x3000), (0x200, 0x3100), (0x200, 65520), (0x200, -1)):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                self.symbols['_boss'] = pair
                self.attest()

    def test_target_size_and_digest_required(self):
        self.target.pop()
        with self.assertRaisesRegex(ValueError, 'pinned Japanese'):
            self.attest()
        self.target.append(0)
        with patch.object(owners, 'sha', return_value='wrong'), self.assertRaises(ValueError):
            self.attest()

    def test_candidate_window_must_be_complete(self):
        del self.candidate[self.start+31:]
        with self.assertRaisesRegex(ValueError, 'complete candidate owner'):
            self.attest()

    def test_structure_member_addend_is_attested(self):
        changed = list(self.field)
        changed[7] = 14
        with patch.object(owners, 'FIELDS', (tuple(changed),)), self.assertRaisesRegex(ValueError, 'operand'):
            self.attest()


class GlobalComparisonTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(compare, 'UPDATE_COUNT', 3))
        self.original = [(frame, bytes(65536)) for frame in range(1, 4)]
        self.states = [(name, 20000+i*32, 22000+i*32, 1, size)
                       for i, (name, _, size, *_) in enumerate(owners.FIELDS)]

    def run_pair(self, candidate):
        return compare.summarize_pair(self.original, candidate, 100, 100, 12000, 12000, self.states)

    def test_every_byte_of_every_state_including_inactive_structures(self):
        for name, _, right, _, size in self.states:
            for offset in range(size):
                with self.subTest(name=name, offset=offset):
                    data = bytearray(65536)
                    data[right+offset] = 255
                    result = self.run_pair([self.original[0], (2, data), self.original[2]])
                    self.assertFalse(result['passed'])
                    self.assertTrue(result['bullets_graze_passed'])
                    self.assertEqual(result['pools'][name]['first_difference']['changes'][0]['offset'], offset)
                    self.assertEqual(result['pools'][name]['updates'], 3)

    def test_identical_all_zero_states_report_unexercised_coverage(self):
        result = self.run_pair(self.original)
        self.assertTrue(result['passed'])
        for row in result['pools'].values():
            self.assertEqual(row['coverage']['original_nonzero_frames'], 0)
            self.assertEqual(row['coverage']['candidate_distinct_values'], 1)

    def test_values_and_nonzero_coverage_are_counted_without_normalization(self):
        name, _, right, _, _ = self.states[0]
        data = bytearray(65536)
        data[right] = 128
        result = self.run_pair([(1, data), (2, data), self.original[2]])
        row = result['pools'][name]
        self.assertEqual(row['coverage']['candidate_nonzero_frames'], 2)
        self.assertEqual(row['coverage']['candidate_distinct_values'], 2)
        self.assertEqual(row['differing_frames'], 2)
