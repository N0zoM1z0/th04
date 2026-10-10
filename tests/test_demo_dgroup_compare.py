"""Mutation controls for the complete pool comparison, including unused bytes."""
import sys
import hashlib
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
import compare_th04_demo_dgroup as compare


class DgroupCompareTests(unittest.TestCase):
    pool, graze = 100, 12000

    def setUp(self):
        self.original = [(n, bytes(65536)) for n in range(1, 4)]

    def run_pair(self, candidate, original=None, graze=None):
        with patch.object(compare, 'UPDATE_COUNT', 3):
            return compare.summarize_pair(self.original if original is None else original,
                                          candidate, self.pool, self.pool, self.graze,
                                          self.graze if graze is None else graze)

    def test_complete_identical_extent(self):
        result = self.run_pair(self.original)
        self.assertTrue(result['passed'])
        self.assertEqual(result['updates'], 3)
        self.assertEqual(result['original_pool_sha256'], result['candidate_pool_sha256'])

    def test_inactive_tail_slot_and_each_byte_are_compared(self):
        for offset in range(26):
            with self.subTest(offset=offset):
                changed = bytearray(65536)
                changed[self.pool+439*26+offset] = 1
                result = self.run_pair([self.original[0], (2, changed), self.original[2]])
                self.assertFalse(result['passed'])
                first = result['first_difference']
                self.assertEqual((first['frame'], first['after_update'], first['differing_slots']), (2, 1, 1))
                self.assertEqual(first['bullets'][0]['slot'], 439)
                self.assertEqual(first['bullets'][0]['changed_offsets'], [offset])

    def test_graze_alone_is_a_difference(self):
        changed = bytearray(65536)
        changed[self.graze+1] = 1
        result = self.run_pair([(1, changed), *self.original[1:]])
        self.assertFalse(result['passed'])
        self.assertEqual(result['first_difference']['candidate_graze'], 256)
        self.assertEqual(result['first_difference']['differing_slots'], 0)

    def test_diagnostic_is_bounded_but_all_slots_and_frames_count(self):
        changed = bytearray(65536)
        for slot in range(440):
            changed[self.pool+slot*26] = 1
        result = self.run_pair([(n, changed) for n in range(1, 4)])
        self.assertEqual(result['updates'], 3)
        self.assertEqual(result['differing_frames'], 3)
        self.assertEqual(result['first_difference']['differing_slots'], 440)
        self.assertEqual(len(result['first_difference']['bullets']), 12)

    def test_equal_prefix_and_unequal_lengths_rejected(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            self.run_pair(self.original[:2], self.original[:2])
        with self.assertRaises(ValueError):
            self.run_pair(self.original[:2])

    def test_shifted_frame_boundary_rejected(self):
        with self.assertRaisesRegex(ValueError, 'boundary'):
            self.run_pair([(2, self.original[0][1]), *self.original[1:]])

    def test_pool_and_graze_truncation_rejected(self):
        for size, pattern in [(1000, 'pool'), (self.graze+1, 'graze')]:
            with self.subTest(size=size), self.assertRaisesRegex(ValueError, pattern):
                self.run_pair([(1, bytes(size)), *self.original[1:]])

    def test_additional_pool_compares_pointer_and_padding_bytes(self):
        for offset in (22, 23, 63, 32*64-1):
            with self.subTest(offset=offset), patch.object(compare, 'UPDATE_COUNT', 3):
                changed = bytearray(65536)
                changed[20000+offset] = 0x7f
                result = compare.summarize_pair(self.original, [(1, changed), *self.original[1:]],
                    self.pool, self.pool, self.graze, self.graze, [('enemies', 20000, 20000, 32, 64)])
                self.assertFalse(result['passed'])
                self.assertTrue(result['bullets_graze_passed'])
                self.assertFalse(result['all_pools_passed'])
                row = result['pools']['enemies']
                self.assertEqual(row['updates'], 3)
                self.assertEqual(row['bytes_per_frame'], 2048)
                self.assertEqual(row['first_difference']['changes'][0]['offset'], offset)

    def test_actual_clear_destinations_counts_and_callees_attested(self):
        offsets = [offset for _, offset, _, _ in compare.POOLS]
        body = bytearray(0x57)
        for (_, _, count, stride), offset in zip(compare.POOLS, offsets):
            body += b'\x68'+offset.to_bytes(2, 'little')
            dwords = count*stride//4
            body += b'\x6a'+bytes((dwords,)) if dwords < 128 else b'\x68'+dwords.to_bytes(2, 'little')
            body += b'\xe8'+((0x185e-(0x73db+len(body)+3)) & 65535).to_bytes(2, 'little')
        compare.attest_clear_calls(body, 0x73db, 0x185e, offsets)
        for offset in (0x58, 0x5b, 0x5e, len(body)-1):
            with self.subTest(offset=offset):
                changed = body.copy()
                changed[offset] ^= 1
                with self.assertRaises(ValueError):
                    compare.attest_clear_calls(changed, 0x73db, 0x185e, offsets)


class DgroupOrdinaryControlTests(unittest.TestCase):
    """The added observer must leave the complete ordinary trace unchanged."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.observed, self.parent, self.source = (root/name for name in ('observed', 'parent', 'source'))
        for directory in (self.observed, self.parent, self.source):
            directory.mkdir()
        for directory in (self.observed, self.parent):
            (directory/'raw.txt').write_bytes(b'complete ordinary trace')
        for name in compare.SOURCE_NAMES:
            (self.source/name).write_bytes(name.encode())
        self.receipt = {name: 'pin' for name in compare.BASELINE_PINS}
        self.receipt['demos'] = 1
        maps = dict(first_frame=1, pages={str(page):page for page in range(0x32300 & ~4095,
                                                                       ((0x32300+65535) & ~4095)+4096, 4096)})
        self.metadata = dict(schema_version=1, complete=True, boundary=compare.BOUNDARY,
            records_per_demo=3996, dgroup_bytes=65536,
            processes={'1':dict(frames=3996, load_segment=0x10fc, dgroup_segment=0x3230,
                                 logical_to_physical_maps=[maps])})
        self.profile = dict(dgroup=0x2134)
        self.stream = dict(complete=True, consumer_source_sha256={
            name:hashlib.sha256((self.source/name).read_bytes()).hexdigest() for name in compare.SOURCE_NAMES})
        self.receipt['dgroup_stream'] = self.stream
        self.diagnostic = dict(loads=[dict(load_segment=0x10fc)])
        self.write()

    def write(self):
        (self.observed/'profile.json').write_text(json.dumps(self.profile))
        (self.observed/'dgroup-stream.json').write_text(json.dumps(self.metadata))
        (self.observed/'dgroup-demo-1.bin.gz').write_bytes(b'producer file identity only; decoder tested separately')
        self.stream['files'] = {name:hashlib.sha256((self.observed/name).read_bytes()).hexdigest()
                               for name in ('dgroup-stream.json', 'dgroup-demo-1.bin.gz')}

    def read(self):
        with patch.object(compare, 'load_capture', return_value=(self.receipt, None, self.diagnostic)):
            return compare.read_side(self.observed, self.parent, self.source)

    def test_complete_ordinary_trace_control(self):
        self.read()

    def test_matching_prefix_is_not_complete_trace_equality(self):
        (self.observed/'raw.txt').write_bytes(b'complete ordinary')
        with self.assertRaisesRegex(ValueError, 'ordinary scalar/caller trace'):
            self.read()

    def test_consumer_change_rejected(self):
        (self.source/compare.SOURCE_NAMES[0]).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'consumer source identity'):
            self.read()

    def test_unrecorded_file_change_rejected(self):
        (self.observed/'dgroup-demo-1.bin.gz').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'file identity'):
            self.read()

    def test_missing_process_or_wrong_boundary_rejected(self):
        self.metadata['processes'] = {}
        self.write()
        with self.assertRaisesRegex(ValueError, 'boundary/extent'):
            self.read()

    def test_graphics_alias_or_missing_mapping_rejected(self):
        pages = self.metadata['processes']['1']['logical_to_physical_maps'][0]['pages']
        first = next(iter(pages))
        pages[first] = 0xa0000
        self.write()
        with self.assertRaisesRegex(ValueError, 'outside RAM'):
            self.read()
        del pages[first]
        self.write()
        with self.assertRaisesRegex(ValueError, 'mapping extent/order'):
            self.read()


if __name__ == '__main__':
    unittest.main()
