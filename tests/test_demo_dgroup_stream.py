"""Adversarial compressed-stream controls without private targets/assets."""
import gzip
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
import th04_demo_dgroup as dg


class DgroupStreamTests(unittest.TestCase):
    fields = [('frame', 0, 2), ('input', 2, 2), ('shift_raw', 4, 1), ('stage', 5, 1)]
    replay = bytes(8000)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'stream.gz'
        self.parts = []
        for frame in range(1, 4):
            body = bytearray(dg.DGROUP_SIZE)
            body[:2] = frame.to_bytes(2, 'little')
            body[5] = 3
            self.parts.append((dg.HEADER.pack(1, frame, 0x10fc, 0x3230, 0x80000011, 0, 0x12f000), bytes(body)))

    def write(self, parts=None, delta=True):
        raw = dg.MAGIC if delta else dg.MAGIC_RAW
        previous = bytes(dg.DGROUP_SIZE)
        for header, body in self.parts if parts is None else parts:
            encoded = bytes(x ^ y for x, y in zip(body, previous)) if delta else body
            raw += header+encoded
            previous = body
        self.path.write_bytes(gzip.compress(raw, mtime=0))

    def read(self):
        with patch.object(dg, 'UPDATE_COUNT', 3):
            return list(dg.records(self.path, 1, 0x10fc, 0x3230, self.fields,
                                   self.replay, 0x80000011, 0x12f000))

    def test_complete_extent(self):
        self.write()
        self.assertEqual([n for n, _ in self.read()], [1, 2, 3])

    def test_delta_reconstructs_every_raw_byte(self):
        changed = bytearray(self.parts[1][1])
        changed[60000:60003] = b'\xff\x01\x80'
        self.parts[1] = (self.parts[1][0], bytes(changed))
        self.write()
        self.assertEqual([b for _, b in self.read()], [b for _, b in self.parts])
        self.write(delta=False)
        self.assertEqual([b for _, b in self.read()], [b for _, b in self.parts])

    def test_equal_truncated_prefix_rejected(self):
        self.write(self.parts[:2])
        with self.assertRaisesRegex(ValueError, 'truncated DGROUP header'):
            self.read()

    def test_duplicate_out_of_order_and_missing_frames(self):
        for indexes in [(0, 0, 2), (1, 0, 2), (0, 2)]:
            with self.subTest(indexes=indexes):
                self.write([self.parts[n] for n in indexes])
                with self.assertRaisesRegex(ValueError, 'out-of-order'):
                    self.read()

    def test_wrong_process_load_data_or_cpu(self):
        header = list(dg.HEADER.unpack(self.parts[0][0]))
        for index in [0, 2, 3, 4, 6]:
            with self.subTest(index=index):
                changed = header.copy()
                changed[index] += 1
                self.write([(dg.HEADER.pack(*changed), self.parts[0][1]), *self.parts[1:]])
                with self.assertRaises(ValueError):
                    self.read()

    def test_wrong_frame_or_stage_body(self):
        for offset in [0, 5]:
            with self.subTest(offset=offset):
                changed = bytearray(self.parts[0][1])
                changed[offset] += 1
                self.write([(self.parts[0][0], changed), *self.parts[1:]])
                with self.assertRaises(ValueError):
                    self.read()

    def test_post_reset_input_is_preserved_not_reinterpreted_as_replay_input(self):
        changed = bytearray(self.parts[0][1])
        changed[2:5] = b'\x20\x00\x01'
        self.parts[0] = (self.parts[0][0], bytes(changed))
        self.write()
        self.assertEqual(self.read()[0][1], bytes(changed))

    def test_extra_frame_rejected(self):
        self.write(self.parts+[self.parts[-1]])
        with self.assertRaisesRegex(ValueError, 'extra DGROUP'):
            self.read()

    def test_truncated_body_rejected(self):
        self.write([*self.parts[:2], (self.parts[2][0], self.parts[2][1][:-1])])
        with self.assertRaisesRegex(ValueError, 'truncated DGROUP body'):
            self.read()

    def test_gzip_footer_is_required(self):
        self.write()
        self.path.write_bytes(self.path.read_bytes()[:-8])
        with self.assertRaises(EOFError):
            self.read()

    def test_bad_magic_rejected(self):
        self.path.write_bytes(gzip.compress(b'badmagic'))
        with self.assertRaisesRegex(ValueError, 'magic'):
            self.read()

    def test_extra_gzip_member_rejected(self):
        self.write()
        self.path.write_bytes(self.path.read_bytes()+gzip.compress(b'extra'))
        with self.assertRaisesRegex(ValueError, 'extra DGROUP'):
            self.read()

    def test_startup_partial_word_clear(self):
        seq = dg.FrameSequence(3996, 3)
        self.assertFalse(seq.observe(3840))
        self.assertFalse(seq.observe(0))
        self.assertTrue(seq.observe(1))
        self.assertTrue(seq.observe(2))
        self.assertTrue(seq.observe(3))
        self.assertEqual(seq.frames, 3)

    def test_zero_start_needs_no_write_of_zero(self):
        seq = dg.FrameSequence(0, 3)
        self.assertTrue(seq.observe(1))

    def test_reset_jump_duplicate_and_extra_update_rejected(self):
        for bad in [0, 1, 3]:
            seq = dg.FrameSequence(0, 3)
            seq.observe(1)
            with self.assertRaises(ValueError):
                seq.observe(bad)
        seq = dg.FrameSequence(0, 1)
        seq.observe(1)
        with self.assertRaises(ValueError):
            seq.observe(2)


if __name__ == '__main__':
    unittest.main()
