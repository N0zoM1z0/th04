import gzip
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
import th04_ordinary_video as protocol


class OrdinaryVideoProtocolTests(unittest.TestCase):
    def encode(self, frames=(1, 2, 3), stage=0):
        result = bytearray(protocol.MAGIC)
        previous = 0
        for frame in frames:
            block = bytearray(protocol.BLOCK_SIZE)
            block[0] = stage
            block[-1] = frame
            result.extend(protocol.HEADER.pack(1, frame, 0x1000, 0x2000, 1, 0, 4096))
            value = int.from_bytes(block, 'little')
            result.extend((value ^ previous).to_bytes(protocol.BLOCK_SIZE, 'little'))
            previous = value
        return bytes(result)

    def decode(self, data, compressed=False):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'video.gz'
            path.write_bytes(data if compressed else gzip.compress(data))
            with patch.object(protocol, 'UPDATE_COUNT', 3):
                return list(protocol.records(path, 0x1000, 0x2000, 1, 4096))

    def test_complete_video_reconstructs_tail_bytes(self):
        records = self.decode(self.encode())
        self.assertEqual([block[-1] for _, block in records], [1, 2, 3])

    def test_demo_magic_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'magic'):
            self.decode(b'TH04VD2\n' + self.encode()[8:])

    def test_missing_duplicate_or_out_of_order_frame_rejects(self):
        for frames in ((1, 3, 3), (1, 1, 3), (2, 1, 3)):
            with self.subTest(frames=frames), self.assertRaisesRegex(ValueError, 'boundary'):
                self.decode(self.encode(frames=frames))

    def test_truncated_body_rejects(self):
        with self.assertRaisesRegex(ValueError, 'truncated.*body'):
            self.decode(self.encode()[:-1])

    def test_wrong_stage_rejects(self):
        with self.assertRaisesRegex(ValueError, 'stage'):
            self.decode(self.encode(stage=1))

    def test_trailing_data_or_bad_crc_rejects(self):
        with self.assertRaisesRegex(ValueError, 'extra ordinary'):
            self.decode(self.encode() + b'\0')
        corrupt = bytearray(gzip.compress(self.encode()))
        corrupt[-8] ^= 1
        with self.assertRaises(gzip.BadGzipFile):
            self.decode(bytes(corrupt), compressed=True)


if __name__ == '__main__':
    unittest.main()
