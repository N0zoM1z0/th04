"""Reject filename-only, malformed-entry and weak score-checksum acceptance."""
import copy
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from compare_th04_dos_demos import relocated_module
from capture_th04_dos_demos import sha
from th04_dos_route import decode_score_sections, validate_entry


class OverlayEntryTests(unittest.TestCase):
    def setUp(self):
        header = bytearray(32)
        header[:2] = b'MZ'
        struct.pack_into('<HHHHHHHHHHHHH', header, 2, 64, 1, 1, 2, 1, 0xffff, 0, 32, 0, 0, 0, 28, 0)
        struct.pack_into('<HH', header, 28, 1, 0)
        self.image = bytes(header) + bytes(32)
        self.observed = relocated_module(self.image, 0x1010)
        registers, segments = bytearray(48), bytearray(136)
        segments[8:16] = (0x1010).to_bytes(8, 'little')
        psp, mcb = bytearray(256), bytearray(16)
        psp[:2] = b'\xcd\x20'
        psp[0x2c:0x2e] = (0x2000).to_bytes(2, 'little')
        mcb[0] = ord('M')
        mcb[1:3] = (0x1000).to_bytes(2, 'little')
        mcb[3:5] = (0x100).to_bytes(2, 'little')
        self.row = dict(artifact='th04-main', load_segment=0x1010, file_sha256=sha(self.image),
                        relocated_sha256=sha(self.observed), image_bytes=len(self.observed), cs=0x1010, ip=0,
                        cpu_regs=registers.hex(), segments=segments.hex(),
                        owner=dict(psp_hex=psp.hex(), mcb_hex=mcb.hex(), psp_segment=0x1000,
                                   mcb_segment=0xfff, mcb_paragraphs=0x100, load_segment=0x1010,
                                   environment_segment=0x2000, executable_hex=b'A:\\GENSO\\MAIN.EXE'.hex()))
        self.request = dict(kind='exec-request', ax=0x4b03, requested_artifact='th04-main',
                            overlay_load_segment=0x1010, overlay_relocation_factor=0x1010,
                            overlay_parameter_hex='10101010')

    def check(self):
        validate_entry(self.row, self.request, self.image, self.observed)

    def test_complete_relocated_image_pc_and_psp_can_pass(self):
        self.check()

    def test_correct_filename_without_matching_image_rejects(self):
        data = bytearray(self.observed)
        data[-1] ^= 1
        self.row['relocated_sha256'] = sha(data)
        with self.assertRaisesRegex(ValueError, 'complete raw'):
            validate_entry(self.row, self.request, self.image, bytes(data))

    def test_unapplied_relocation_rejects(self):
        with self.assertRaisesRegex(ValueError, 'complete raw'):
            validate_entry(self.row, self.request, self.image, self.image[32:])

    def test_wrong_actual_pc_rejects_despite_complete_image(self):
        self.row['cpu_regs'] = bytes(48).hex()
        self.row['ip'] = 1
        with self.assertRaisesRegex(ValueError, 'actual entry CPU'):
            self.check()

    def test_load_and_go_or_wrong_overlay_factor_cannot_be_relabelled(self):
        for key, value in (('ax', 0x4b00), ('overlay_relocation_factor', 0x1011)):
            before = self.request[key]
            self.request[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'overlay request'):
                self.check()
            self.request[key] = before

    def test_psp_name_or_allocation_header_alone_is_insufficient(self):
        self.row['owner']['mcb_hex'] = bytes(16).hex()
        with self.assertRaisesRegex(ValueError, 'MCB/PSP'):
            self.check()

    def test_truncated_image_or_registers_rejects(self):
        with self.assertRaisesRegex(ValueError, 'complete raw'):
            validate_entry(self.row, self.request, self.image, self.observed[:-1])
        self.row['cpu_regs'] = bytes(47).hex()
        with self.assertRaisesRegex(ValueError, 'actual entry CPU'):
            self.check()


class ScoreChecksumTests(unittest.TestCase):
    def encode(self, value, key1, key2):
        plain = bytearray(196)
        plain[0:2] = bytes((key1, key2))
        plain[4:] = bytes((value,)) * 192
        plain[2:4] = (sum(plain[4:]) & 65535).to_bytes(2, 'little')
        encoded = plain.copy()
        feedback = 0
        for i in range(195, 3, -1):
            encoded[i] = (plain[i] - key1 - feedback) & 255
            byte = encoded[i]
            feedback = (((byte >> 3) | (byte << 5)) & 255) ^ key2
        return bytes(encoded)

    def fixture(self):
        return b''.join(self.encode(i + 1, 37, 251) for i in range(10))

    def test_all_ten_complete_sections_decode(self):
        sections = decode_score_sections(self.fixture())
        self.assertEqual(sections, [bytes((i + 1,)) * 192 for i in range(10)])

    def test_high_checksum_byte_only_corruption_is_rejected(self):
        for number in range(10):
            data = bytearray(self.fixture())
            data[number * 196 + 3] ^= 1
            with self.subTest(section=number), self.assertRaisesRegex(ValueError, '16-bit score checksum'):
                decode_score_sections(data)

    def test_rekeyed_equal_payloads_still_use_full_checksum(self):
        a = self.encode(99, 0, 0) * 10
        b = self.encode(99, 255, 200) * 10
        self.assertNotEqual(a, b)
        self.assertEqual(decode_score_sections(a), decode_score_sections(b))

    def test_incomplete_or_extra_sections_reject(self):
        for size in (0, 1959, 1961):
            data = (self.fixture() + b'\0')[:size]
            with self.subTest(size=size), self.assertRaisesRegex(ValueError, 'score file extent'):
                decode_score_sections(data)


if __name__ == '__main__':
    unittest.main()


class RestartKeyboardTests(unittest.TestCase):
    def setUp(self):
        from th04_dos_route import validate_restart_keys
        self.validate = validate_restart_keys
        self.plan = [[1000 + delta + offset, 'KBD_enter', pressed]
                     for delta in (100, 1100, 2100) for offset, pressed in ((0, True), (120, False))]
        self.clock = dict(actions=[dict(due=due, tick=due, key=key, pressed=down, frame=None)
                                   for due, key, down in self.plan[:5]],
                          restart=dict(action_start=0, action_end=5, tick=1000, entry_tick=3200,
                                       resident_seed=65, cancelled=self.plan[5:], enter_down=True))

    def check(self):
        self.validate(self.clock, 0)

    def test_actual_key_prefix_and_explicit_pending_cancellation_pass(self):
        self.check()

    def test_missing_restart_confirmation_rejects(self):
        self.clock['actions'].pop(2)
        self.clock['restart']['action_end'] -= 1
        with self.assertRaisesRegex(ValueError, 'ordinary restart keys'):
            self.check()

    def test_gameplay_frame_must_not_survive_old_monitor_retirement(self):
        self.clock['actions'][0]['frame'] = 7547
        with self.assertRaisesRegex(ValueError, 'ordinary restart keys'):
            self.check()

    def test_unrecorded_cancellation_rejects(self):
        self.clock['restart']['cancelled'] = []
        with self.assertRaisesRegex(ValueError, 'ordinary restart keys'):
            self.check()

    def test_keys_after_entry_cannot_prove_restart(self):
        self.clock['actions'][-1]['tick'] = 3201
        with self.assertRaisesRegex(ValueError, 'ordinary restart keys'):
            self.check()

    def test_stale_seed_or_enter_state_rejects(self):
        self.clock['restart']['resident_seed'] = 64
        with self.assertRaisesRegex(ValueError, 'extent/seed'):
            self.check()
        self.clock['restart']['resident_seed'] = 65
        self.clock['restart']['enter_down'] = False
        with self.assertRaisesRegex(ValueError, 'ordinary restart keys'):
            self.check()
