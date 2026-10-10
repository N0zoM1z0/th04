"""Independent host-memory and compressed-video stream mutation controls."""
import gzip
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/probes'))
import th04_demo_video as video


class HostVideoTests(unittest.TestCase):
    def setUp(self):
        self.memory = bytearray(2*1024*1024)
        self.symbols = {'vga': 0, 'pc98_pgraph_current_cpu_page': 600000,
                        'pc98_pgraph_current_display_page': 600008,
                        'pc98_pal_analog': 601000, 'pc98_pal_digital': 602000,
                        'pc98_text_palette': 603000, 'pc98_gdc': 604000}
        self.symbols.update({name: 610000+i for i, name in enumerate(video.MODES)})
        self.base = 1024*1024
        self.put(video.LAYOUT['vga_mem_linear'], self.base, 8)
        self.put(video.LAYOUT['vga_mem_size'], 0x44000, 4)
        self.put(self.symbols['pc98_pgraph_current_cpu_page'], self.base+0x4000, 8)
        self.put(self.symbols['pc98_pgraph_current_display_page'], self.base+0x4000, 8)
        self.reader = video.VideoRam(self.read, self.symbols)

    def put(self, address, value, size):
        self.memory[address:address+size] = value.to_bytes(size, 'little')

    def read(self, address, size):
        return self.memory[address:address+size]

    def test_both_pages_all_four_planes_and_unused_tail_bytes_preserved(self):
        for plane in range(4):
            for page in range(2):
                at = self.base+0x4000+plane*65536+page*32768+32767
                self.memory[at] = plane*2+page+1
        block, mapping = self.reader.capture(3)
        fields = video.regions(block)
        for plane in range(4):
            for page in range(2):
                self.assertEqual(fields[f'plane{plane}_page{page}'][-1], plane*2+page+1)
        self.assertEqual(mapping['backing_ram'], self.base)
        self.assertEqual(block[0], 3)

    def test_page_pointers_agree_with_selectors(self):
        self.memory[self.symbols['pc98_gdc_vramop']] = 1
        self.memory[self.symbols['GDC_display_plane']] = 1
        for name in ('pc98_pgraph_current_cpu_page', 'pc98_pgraph_current_display_page'):
            self.put(self.symbols[name], self.base+0xc000, 8)
        self.reader.capture(3)
        self.put(self.symbols['pc98_pgraph_current_display_page'], self.base+0x4000, 8)
        with self.assertRaisesRegex(ValueError, 'page pointers'):
            self.reader.capture(3)

    def test_unsupported_mode_bank_and_backing_extent_rejected(self):
        for name, value in (('pc98_gdc_vramop', 0x20), ('GDC_display_plane', 2),
                            ('GDC_display_plane_pending', 2), ('pc98_256kb_boundary', 1)):
            self.memory[self.symbols[name]] = value
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'bank mode'):
                self.reader.capture(3)
            self.memory[self.symbols[name]] = 0
        self.put(video.LAYOUT['vga_mem_size'], 0x43fff, 4)
        with self.assertRaisesRegex(ValueError, 'backing RAM'):
            self.reader.capture(3)

    def test_short_read_rejected_including_pointer_width(self):
        short = video.VideoRam(lambda address, size: bytes(max(0, size-1)), self.symbols)
        with self.assertRaisesRegex(ValueError, 'short host video'):
            short.capture(3)

    def test_all_palette_bytes_and_text_attribute_tail_preserved(self):
        self.memory[self.base+16383] = 7
        for name, symbol, size in (('analog', 'pc98_pal_analog', 768),
                                    ('digital', 'pc98_pal_digital', 8),
                                    ('text_palette', 'pc98_text_palette', 32)):
            self.memory[self.symbols[symbol]+size-1] = 15
        fields = video.regions(self.reader.capture(3)[0])
        self.assertEqual(fields['text'][-1], 7)
        for name in ('analog', 'digital', 'text_palette'):
            self.assertEqual(fields[name][-1], 15)

    def test_raw_gdc_retained_but_scan_clock_not_programmed_state(self):
        self.memory[self.symbols['pc98_gdc']+video.LAYOUT['scan_address']] = 17
        self.memory[self.symbols['pc98_gdc']+video.LAYOUT['param_ram']] = 19
        block, _ = self.reader.capture(3)
        self.assertEqual(block[video.OFFSETS['gdc']+video.LAYOUT['scan_address']], 17)
        fields = video.regions(block)
        self.assertEqual(fields['gdc0_param_ram'][0], 19)
        self.assertNotIn('gdc0_scan_address', fields)


class VideoStreamTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(video, 'UPDATE_COUNT', 3))
        self.directory = self.enterContext(tempfile.TemporaryDirectory())
        self.path = Path(self.directory)/'video.bin.gz'
        self.blocks = [bytes((3,))+bytes(video.BLOCK_SIZE-1) for _ in range(3)]

    def write(self, mutate=None, blocks=None, tail=b'', magic=video.MAGIC):
        previous = 0
        with gzip.open(self.path, 'wb') as stream:
            stream.write(magic)
            for frame, block in enumerate(self.blocks if blocks is None else blocks, 1):
                row = [1, frame, 0x10fc, 0x3230, 0x80000011, 0, 0x12f000]
                if mutate:
                    mutate(frame, row)
                stream.write(video.HEADER.pack(*row))
                value = int.from_bytes(block, 'little')
                stream.write((value ^ previous).to_bytes(video.BLOCK_SIZE, 'little'))
                previous = value
            stream.write(tail)

    def decode(self):
        return list(video.records(self.path, 1, 0x10fc, 0x3230, 3, 0x80000011, 0x12f000))

    def test_complete_independent_xor_encoder_preserves_each_block(self):
        blocks = list(self.blocks)
        value = bytearray(blocks[1])
        value[-1] = 127
        blocks[1] = bytes(value)
        self.write(blocks=blocks)
        self.assertEqual(self.decode(), list(enumerate(blocks, 1)))

    def test_every_header_field_mutation_rejected(self):
        for index in range(7):
            def mutate(frame, row):
                if frame == 2:
                    row[index] ^= 1
            self.write(mutate=mutate)
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, 'boundary'):
                self.decode()

    def test_equal_prefix_missing_tail_extra_bytes_and_wrong_magic_rejected(self):
        for args in (dict(blocks=self.blocks[:2]), dict(tail=b'\0'), dict(magic=b'BADVID2\n')):
            self.write(**args)
            with self.subTest(args=list(args)), self.assertRaises(ValueError):
                self.decode()

    def test_wrong_stage_and_incomplete_block_rejected(self):
        self.write(blocks=[bytes(video.BLOCK_SIZE), *self.blocks[1:]])
        with self.assertRaisesRegex(ValueError, 'stage'):
            self.decode()
        with gzip.open(self.path, 'wb') as stream:
            stream.write(video.MAGIC)
            stream.write(video.HEADER.pack(1, 1, 0x10fc, 0x3230, 0x80000011, 0, 0x12f000))
            stream.write(bytes(42))
        with self.assertRaisesRegex(ValueError, 'incomplete video block'):
            self.decode()

    def test_region_truncation_rejected(self):
        with self.assertRaisesRegex(ValueError, 'extent'):
            video.regions(bytes(video.BLOCK_SIZE-1))
