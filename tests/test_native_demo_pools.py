"""Complete raw pool comparisons must retain late and inactive differences."""
import io
import struct
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'port64'))
import verify_demo_pools as reader


class Frames:
    def __init__(self, change=None):
        self.frame=0
        self.change=change

    def read(self, size):
        self.frame+=1
        body=bytearray(reader.FRAME_BYTES-4)
        if self.change and self.frame==self.change[0]:
            body[self.change[1]]=self.change[2]
        return struct.pack('<HH',1,self.frame)+body


def reference():
    for frame in range(1,3997):
        yield frame,bytes(65536)


class NativeDemoPoolTests(unittest.TestCase):
    def test_complete_zero_pair(self):
        report=reader.compare_demo(reference(),Frames(),1)
        self.assertTrue(report['passed'])
        self.assertEqual(report['updates'],3996)
        self.assertEqual(set(report['pools']),{row[0] for row in reader.POOLS})

    def test_inactive_last_record_byte_rejects(self):
        report=reader.compare_demo(reference(),Frames((3996,reader.FRAME_BYTES-5,73)),1)
        self.assertFalse(report['passed'])
        row=report['pools']['gather_circles']
        self.assertEqual(row['differing_frames'],1)
        self.assertEqual(row['first_difference']['frame'],3996)
        self.assertEqual(row['first_difference']['changes'][0]['slot'],15)
        self.assertEqual(row['first_difference']['changes'][0]['record_offset'],41)

    def test_script_pointer_byte_rejects(self):
        # Enemy slot0 + script WORD at22; translation may not mask this field.
        report=reader.compare_demo(reference(),Frames((10,68*18+22,1)),1)
        self.assertFalse(report['passed'])
        self.assertEqual(report['pools']['enemies']['first_difference']['frame'],10)

    def test_short_pool_frame_rejects(self):
        with self.assertRaisesRegex(ValueError,'extent'):
            reader.read_frame(io.BytesIO(bytes(reader.FRAME_BYTES-1)),1,1)

    def test_wrong_demo_rejects(self):
        raw=struct.pack('<HH',2,1)+bytes(reader.FRAME_BYTES-4)
        with self.assertRaisesRegex(ValueError,'order'):
            reader.read_frame(io.BytesIO(raw),1,1)

    def test_missing_duplicate_and_terminal_reject(self):
        for frame,expected in ((0,1),(2,1),(1,2),(3997,3996)):
            raw=struct.pack('<HH',1,frame)+bytes(reader.FRAME_BYTES-4)
            with self.subTest(frame=frame),self.assertRaisesRegex(ValueError,'order'):
                reader.read_frame(io.BytesIO(raw),1,expected)

    def test_original_truncation_rejects(self):
        with self.assertRaisesRegex(ValueError,'complete demo'):
            reader.compare_demo([(1,bytes(65536))],Frames(),1)

    def test_original_pool_short_rejects(self):
        with self.assertRaisesRegex(ValueError,'paired pool extent'):
            reader.compare_demo([(1,bytes(16))],Frames(),1)


if __name__=='__main__':unittest.main()
