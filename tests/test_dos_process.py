"""Require real MCB, PSP and environment ownership for process activity."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from th04_dos_process import artifact_for_path, c_string, process_owner


class ProcessOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.memory = bytearray(655360)
        self.mcb(0x1000, 0x1001, 0x1000)
        self.psp(0x1001, 0x3000)
        self.mcb(0x2fff, 0x1001, 0x40)
        env = b'PATH=C:\\DOS\0COMSPEC=C:\\COMMAND.COM\0\0\x01\x00C:\\GENSO\\MAIN.EXE\0'
        self.memory[0x30000:0x30000 + len(env)] = env

    def mcb(self, segment, owner, size):
        at = segment * 16
        self.memory[at] = ord('M')
        self.memory[at + 1:at + 3] = owner.to_bytes(2, 'little')
        self.memory[at + 3:at + 5] = size.to_bytes(2, 'little')

    def psp(self, segment, environment):
        at = segment * 16
        self.memory[at:at + 2] = b'\xcd\x20'
        self.memory[at + 0x16:at + 0x18] = (0x900).to_bytes(2, 'little')
        self.memory[at + 0x2c:at + 0x2e] = environment.to_bytes(2, 'little')

    def owner(self):
        return process_owner(bytes(self.memory), 0x1100, 0x20)

    def test_complete_psp_mcb_environment_identifies_actual_code_owner(self):
        row = self.owner()
        self.assertEqual(row['environment_artifact'], 'th04-main')
        self.assertEqual(row['psp_segment'], 0x1001)
        self.assertEqual(row['load_segment'], 0x1011)
        self.assertEqual(bytes.fromhex(row['executable_hex']), b'C:\\GENSO\\MAIN.EXE')

    def test_mcb_without_psp_signature_cannot_identify_a_process(self):
        self.memory[0x10010] = 0
        self.assertIsNone(self.owner())

    def test_free_or_other_owned_memory_cannot_become_the_executable_owner(self):
        self.mcb(0x1000, 0, 0x1000)
        self.assertIsNone(self.owner())

    def test_program_extent_must_cover_caller_and_stay_in_conventional_ram(self):
        for size in (16, 0xffff):
            self.mcb(0x1000, 0x1001, size)
            with self.subTest(size=size):
                self.assertIsNone(self.owner())

    def test_environment_requires_its_own_valid_block_and_filename_tail(self):
        self.memory[0x2fff0] = 0
        self.assertIsNone(self.owner())
        self.memory[0x2fff0] = ord('M')
        at = self.memory.find(b'\0\0\x01\0C:', 0x30000)
        self.memory[at + 2] = 0
        self.assertIsNone(self.owner())

    def test_overlapping_plausible_psps_are_rejected_as_ambiguous(self):
        self.mcb(0x1080, 0x1081, 0x200)
        self.psp(0x1081, 0x3000)
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            self.owner()

    def test_rom_or_out_of_memory_caller_has_no_conventional_process_owner(self):
        self.assertIsNone(process_owner(bytes(self.memory), 0xf000, 0))

    def test_dos_names_are_classified_without_changing_raw_paths(self):
        self.assertEqual(artifact_for_path(b'C:/GENSO/maine.exe'), 'th04-maine')
        self.assertIsNone(artifact_for_path(b'C:\\GENSO\\OTHER.EXE'))

    def test_string_decoder_rejects_unterminated_or_out_of_range_data(self):
        for data, address in ((b'ABC', 0), (b'ABC\0', 4), (b'ABC\0', -1)):
            with self.subTest(address=address), self.assertRaises(ValueError):
                c_string(data, address)


if __name__ == '__main__':
    unittest.main()
