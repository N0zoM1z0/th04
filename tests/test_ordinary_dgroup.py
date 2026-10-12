import gzip
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
import th04_ordinary_dgroup as protocol


class OrdinaryDgroupProtocolTests(unittest.TestCase):
    def make_stream(self, headers=None, bad_stage=False):
        result = bytearray(protocol.MAGIC)
        previous = 0
        for frame in range(1, 4):
            data = bytearray(protocol.DGROUP_SIZE)
            data[2:4] = frame.to_bytes(2, 'little')
            data[4] = int(bad_stage and frame == 2)
            observed = frame if headers is None else headers[frame - 1]
            result.extend(protocol.HEADER.pack(1, observed, 0x1000, 0x2000, 1, 0, 4096))
            value = int.from_bytes(data, 'little')
            result.extend((value ^ previous).to_bytes(protocol.DGROUP_SIZE, 'little'))
            previous = value
        return bytes(result)

    def read(self, data, compressed=False):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'frames.gz'
            path.write_bytes(data if compressed else gzip.compress(data))
            with patch.object(protocol, 'UPDATE_COUNT', 3):
                return list(protocol.records(path, 0x1000, 0x2000,
                            [('frame', 2, 2), ('stage', 4, 1)], 1, 4096))

    def test_complete_delta_stream_reconstructs_all_frames(self):
        rows = self.read(self.make_stream())
        self.assertEqual([frame for frame, _ in rows], [1, 2, 3])
        self.assertEqual([int.from_bytes(data[2:4], 'little') for _, data in rows], [1, 2, 3])

    def test_missing_or_duplicate_frame_rejects(self):
        for headers in ([1, 3, 3], [1, 1, 3]):
            with self.subTest(headers=headers), self.assertRaisesRegex(ValueError, 'order/load'):
                self.read(self.make_stream(headers=headers))

    def test_partial_final_body_rejects(self):
        with self.assertRaisesRegex(ValueError, 'truncated.*body'):
            self.read(self.make_stream()[:-1])

    def test_non_stage_one_payload_rejects(self):
        with self.assertRaisesRegex(ValueError, 'field mismatch: stage'):
            self.read(self.make_stream(bad_stage=True))

    def test_extra_record_rejects(self):
        with self.assertRaisesRegex(ValueError, 'extra ordinary'):
            self.read(self.make_stream() + b'\0')

    def test_crc_failure_rejects(self):
        data = bytearray(gzip.compress(self.make_stream()))
        data[-8] ^= 1
        with self.assertRaises(gzip.BadGzipFile):
            self.read(bytes(data), compressed=True)


if __name__ == '__main__':
    unittest.main()
