"""Reject pixel/palette/register differences even when actor traces match."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/probes'))
import compare_th04_demo_video as compare
import th04_demo_video as video


class VideoComparisonTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(compare, 'UPDATE_COUNT', 3))
        self.block = bytes((3,))+bytes(video.BLOCK_SIZE-1)
        self.original = [(i, self.block) for i in range(1, 4)]

    def compare(self, candidate, original=None):
        return compare.summarize_pair(self.original if original is None else original, candidate)

    def test_full_equal_extent_reports_zero_coverage_and_hashes(self):
        result = self.compare(self.original)
        self.assertTrue(result['passed'])
        self.assertEqual(result['updates'], 3)
        row = result['regions']['plane3_page1']
        self.assertEqual(row['original_sha256'], row['candidate_sha256'])
        self.assertEqual(row['original_nonzero_frames'], 0)
        self.assertEqual(row['original_distinct_frames'], 1)

    def test_every_plane_page_and_unused_tail_byte_is_compared(self):
        for plane in range(4):
            for page in range(2):
                data = bytearray(self.block)
                offset = video.OFFSETS['graphics']+plane*65536+page*32768+32767
                data[offset] = 128
                result = self.compare([(1, self.block), (2, bytes(data)), (3, self.block)])
                with self.subTest(plane=plane, page=page):
                    self.assertFalse(result['passed'])
                    row = result['regions'][f'plane{plane}_page{page}']
                    self.assertEqual(row['first_difference']['changes'][0]['offset'], 32767)
                    self.assertEqual(row['candidate_distinct_frames'], 2)

    def test_text_attributes_palettes_and_modes_reject(self):
        for name in ('text', 'analog', 'digital', 'text_palette', 'modes'):
            data = bytearray(self.block)
            data[video.OFFSETS[name]+video.SIZES[name]-1] = 1
            result = self.compare([(1, bytes(data)), *self.original[1:]])
            with self.subTest(name=name):
                self.assertFalse(result['passed'])
                self.assertEqual(result['regions'][name]['differing_frames'], 1)

    def test_gdc_programmed_params_and_display_flags_are_compared(self):
        for index in range(2):
            for name in ('param_ram', 'display_pitch', 'display_enable', 'row_height'):
                data = bytearray(self.block)
                data[video.OFFSETS['gdc']+index*video.LAYOUT['gdc_size']+video.LAYOUT[name]] = 1
                result = self.compare([(1, bytes(data)), *self.original[1:]])
                with self.subTest(index=index, name=name):
                    self.assertFalse(result['passed'])
                    self.assertEqual(result['regions'][f'gdc{index}_{name}']['differing_frames'], 1)

    def test_scan_clock_difference_is_retained_and_counted_separately(self):
        data = bytearray(self.block)
        data[video.OFFSETS['gdc']+video.LAYOUT['scan_address']] = 1
        result = self.compare([(1, bytes(data)), *self.original[1:]])
        self.assertTrue(result['passed'])
        self.assertEqual(result['raw_gdc_differing_frames'], 1)

    def test_incomplete_equal_prefix_and_unequal_lengths_rejected(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            self.compare(self.original[:2], self.original[:2])
        with self.assertRaises(ValueError):
            self.compare(self.original[:2])

    def test_frame_boundary_and_block_truncation_rejected(self):
        with self.assertRaisesRegex(ValueError, 'frame boundary'):
            self.compare([(2, self.block), *self.original[1:]])
        with self.assertRaisesRegex(ValueError, 'extent'):
            self.compare([(1, self.block[:-1]), *self.original[1:]])

    def test_first_diagnostics_bounded_but_all_differences_count(self):
        data = bytearray(self.block)
        start = video.OFFSETS['text']
        data[start:start+video.SIZES['text']] = bytes([255])*video.SIZES['text']
        result = self.compare([(i, bytes(data)) for i in range(1, 4)])
        self.assertEqual(result['updates'], 3)
        self.assertEqual(result['differing_frames'], 3)
        row = result['regions']['text']
        self.assertEqual(row['first_difference']['differing_bytes'], video.SIZES['text'])
        self.assertEqual(len(row['first_difference']['changes']), 32)

    def test_first_full_raw_blocks_retained_without_overwrite(self):
        data = bytearray(self.block)
        data[video.OFFSETS['digital']] = 1
        with tempfile.TemporaryDirectory() as name:
            prefix = Path(name)/'first'
            result = compare.summarize_pair(self.original, [(1, bytes(data)), *self.original[1:]], prefix)
            self.assertEqual(Path(result['first_difference']['candidate_dump']['path']).read_bytes(), bytes(data))
            with self.assertRaisesRegex(ValueError, 'fresh first-divergence'):
                compare.summarize_pair(self.original, [(1, bytes(data)), *self.original[1:]], prefix)


class VideoOrdinaryControlTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.observed, self.parent, self.source = (root/n for n in ('observed', 'parent', 'source'))
        for directory in (self.observed, self.parent, self.source):
            directory.mkdir()
        for directory in (self.observed, self.parent):
            (directory/'raw.txt').write_bytes(b'complete ordinary trace')
        for name in compare.SOURCE_NAMES:
            (self.source/name).write_bytes(name.encode())
        self.receipt = {name: 'pin' for name in compare.BASELINE_PINS}
        self.receipt['demos'] = 1
        self.receipt['emulator_receipt_sha256'] = 'pin'
        self.layout = dict(passed=True, layout=video.LAYOUT, emulator_sha256='pin', emulator_receipt_sha256='pin',
                           symbols={name:dict(address=1000+i, size=size)
                                    for i, (name, size) in enumerate(video.SYMBOL_SIZES.items())})
        self.layout_path = root/'layout.json'
        process = dict(frames=3996, load_segment=0x10fc, dgroup_segment=0x3230,
                       logical_to_physical_maps=[dict(first_frame=1, pages={'0x37000':0x37000})],
                       video_pointer_maps=[dict(first_frame=1, backing_ram=0x100000,
                                               backing_bytes=0x44000, cpu_page=0x104000, display_page=0x104000)])
        self.metadata = dict(schema_version=1, complete=True, boundary=video.BOUNDARY,
                             records_per_demo=3996, block_bytes=video.BLOCK_SIZE, layout=video.LAYOUT,
                             processes={'1':process}, video_symbols={name:row['address']+10000
                                                                   for name, row in self.layout['symbols'].items()})
        self.stream = dict(complete=True, layout_receipt_path=str(self.layout_path),
                           consumer_source_sha256={name:compare.sha((self.source/name).read_bytes())
                                                   for name in compare.SOURCE_NAMES})
        self.receipt['video_stream'] = self.stream
        (self.observed/'profile.json').write_text(json.dumps(dict(dgroup=0x2134)))
        self.write()

    def write(self):
        self.layout_path.write_text(json.dumps(self.layout))
        self.stream['layout_receipt_sha256'] = compare.sha(self.layout_path.read_bytes())
        (self.observed/'video-stream.json').write_text(json.dumps(self.metadata))
        (self.observed/'video-demo-1.bin.gz').write_bytes(b'file identity fixture; decoder tested separately')
        self.stream['files'] = {name:compare.sha((self.observed/name).read_bytes())
                                for name in ('video-stream.json', 'video-demo-1.bin.gz')}

    def read(self, parent=None):
        captures = [(self.receipt, None, dict(loads=[dict(load_segment=0x10fc)])),
                    (self.receipt if parent is None else parent, None, None)]
        with patch.object(compare, 'load_capture', side_effect=captures):
            return compare.read_side(self.observed, self.parent, self.source)

    def test_complete_ordinary_control_and_mapping_pass(self):
        self.read()

    def test_each_ordinary_identity_pin_required(self):
        for name in compare.BASELINE_PINS:
            parent = dict(self.receipt)
            parent[name] = 'changed'
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'identity mismatch'):
                self.read(parent)

    def test_complete_scalar_caller_trace_must_remain_identical(self):
        (self.parent/'raw.txt').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'complete ordinary'):
            self.read()

    def test_incomplete_producer_or_metadata_rejected(self):
        self.stream['complete'] = False
        with self.assertRaisesRegex(ValueError, 'incomplete video producer'):
            self.read()
        self.stream['complete'] = True
        self.metadata['complete'] = False
        self.write()
        with self.assertRaisesRegex(ValueError, 'metadata'):
            self.read()

    def test_changed_executed_source_stream_and_layout_receipt_rejected(self):
        for path, message in ((self.source/compare.SOURCE_NAMES[0], 'consumer identity'),
                               (self.observed/'video-demo-1.bin.gz', 'file identity'),
                               (self.layout_path, 'ABI receipt identity')):
            old = path.read_bytes()
            path.write_bytes(old+b'changed')
            with self.subTest(path=path.name), self.assertRaisesRegex(ValueError, message):
                self.read()
            path.write_bytes(old)

    def test_forged_abi_width_and_elf_bias_rejected(self):
        name = next(iter(self.layout['symbols']))
        self.layout['symbols'][name]['size'] += 1
        self.write()
        with self.assertRaisesRegex(ValueError, 'ABI/binary/ELF'):
            self.read()
        self.layout['symbols'][name]['size'] -= 1
        self.metadata['video_symbols'][name] += 1
        self.write()
        with self.assertRaisesRegex(ValueError, 'runtime mapping'):
            self.read()

    def test_page_pointer_and_non_ram_frame_mapping_rejected(self):
        process = self.metadata['processes']['1']
        process['video_pointer_maps'][0]['display_page'] += 1
        self.write()
        with self.assertRaisesRegex(ValueError, 'backing/page mapping'):
            self.read()
        process['video_pointer_maps'][0]['display_page'] -= 1
        process['logical_to_physical_maps'][0]['pages']['0x37000'] = 0xa0000
        self.write()
        with self.assertRaisesRegex(ValueError, 'conventional RAM'):
            self.read()

    def test_mapping_start_order_and_process_extent_rejected(self):
        process = self.metadata['processes']['1']
        process['frames'] = 3995
        self.write()
        with self.assertRaisesRegex(ValueError, 'process extent'):
            self.read()
        process['frames'] = 3996
        process['video_pointer_maps'][0]['first_frame'] = 2
        self.write()
        with self.assertRaisesRegex(ValueError, 'initial mapping'):
            self.read()
