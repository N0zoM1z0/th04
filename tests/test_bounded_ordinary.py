import copy
from collections import Counter
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from compare_th04_dos_ordinary_prefix import validate_bounded_terminal


class BoundedTerminalTests(unittest.TestCase):
    def setUp(self):
        header = bytearray(32)
        header[:2] = b'MZ'
        struct.pack_into('<H', header, 8, 2)
        module = b'\xa3\x10\x00' + bytes(29)
        self.main = bytes(header) + module
        self.profile = dict(end_after=3, dgroup=1, hooks=[(1, 0, 0x1f)],
                            fields=[('frame', 16, 2), ('stage', 18, 1), ('resident_pointer', 20, 4)])
        resident = bytearray(80)
        resident[:11] = b'HUMAConfig\0'
        regs, segments = bytearray(48), bytearray(136)
        segments[8:16] = (0x1000).to_bytes(8, 'little')
        self.terminal = dict(schema_version=1, complete_prefix=True, natural_game_exit=False,
            boundary='ordinary stage_frame write, before mod counters and score update',
            frame=3, load_segment=0x1000, dgroup_segment=0x1001,
            lcg_calls=1, ring_calls=2, values=dict(frame='0300', stage='00', resident_pointer='00000010'),
            resident=resident.hex(), cs=0x1000, ip=0, opcode=module[:16].hex(),
            cpu_regs=regs.hex(), segments=segments.hex())
        self.counts = Counter(lcg=1, ring=2)

    def check(self, terminal):
        validate_bounded_terminal(terminal, self.main, self.profile, 0x1000, self.counts)

    def test_observed_prefix_can_pass_without_natural_exit(self):
        self.check(self.terminal)

    def test_natural_exit_claim_rejects(self):
        self.terminal['natural_game_exit'] = True
        with self.assertRaisesRegex(ValueError, 'class/boundary'):
            self.check(self.terminal)

    def test_wrong_extent_or_data_segment_rejects(self):
        for key in ('frame', 'dgroup_segment'):
            terminal = copy.deepcopy(self.terminal)
            terminal[key] += 1
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'extent/address'):
                self.check(terminal)

    def test_unobserved_rng_call_rejects(self):
        self.terminal['ring_calls'] += 1
        with self.assertRaisesRegex(ValueError, 'RNG counters'):
            self.check(self.terminal)

    def test_wrong_frame_store_or_code_owner_rejects(self):
        for key, value in [('opcode', '90' * 16), ('cs', 0x1001)]:
            terminal = copy.deepcopy(self.terminal)
            terminal[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check(terminal)

    def test_relocated_cpu_context_must_match_instruction(self):
        self.terminal['cpu_regs'] = '00' * 47
        with self.assertRaisesRegex(ValueError, 'CPU terminal'):
            self.check(self.terminal)


if __name__ == '__main__':
    unittest.main()
