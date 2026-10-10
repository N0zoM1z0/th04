"""Independent sparse-RAM fixtures for the read-only VM86 observer walker."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from th04_demo_host_ram import HostRam


class HostRamTests(unittest.TestCase):
    def setUp(self):
        self.memory = {}
        self.base = 0x100000000
        self.symbols = dict(MemBase=0x100, cpu=0x200, paging=0x300)
        self.put(0x100, self.base.to_bytes(8, 'little'))
        self.ram = HostRam(lambda p, n: bytes(self.memory.get(p+i, 0) for i in range(n)), self.symbols)

    def put(self, pointer, data):
        self.memory.update({pointer+i: b for i, b in enumerate(data)})

    def word(self, pointer, value):
        self.put(pointer, value.to_bytes(4, 'little'))

    def paged(self):
        self.word(0x210, 0x80000011)
        self.word(0x300, 0x1000)
        self.word(self.base+0x1000, 0x2001)

    def test_unpaged_host_ram(self):
        self.put(self.base+0x4321, b'RAM')
        data, pages, state = self.ram.read_range(0x4321, 3)
        self.assertEqual(data, b'RAM')
        self.assertEqual(pages, {'16384': 16384})
        self.assertEqual(state, (self.base, 0, 0, 0))

    def test_vm86_noncontiguous_pages(self):
        self.paged()
        self.word(self.base+0x2000+3*4, 0x9001)
        self.word(self.base+0x2000+4*4, 0xb001)
        self.put(self.base+0x9ffe, b'AB')
        self.put(self.base+0xb000, b'CD')
        data, pages, _ = self.ram.read_range(0x3ffe, 4)
        self.assertEqual(data, b'ABCD')
        self.assertEqual(pages, {'12288': 0x9000, '16384': 0xb000})

    def test_large_page(self):
        self.paged()
        self.word(0x218, 0x10)
        self.word(self.base+0x1000, 0x400081)
        self.put(self.base+0x403003, b'PSE')
        self.assertEqual(self.ram.read_range(0x3003, 3)[0], b'PSE')

    def test_missing_directory(self):
        self.paged()
        self.word(self.base+0x1000, 0)
        with self.assertRaisesRegex(ValueError, 'directory'):
            self.ram.read_range(0x3000, 1)

    def test_missing_page(self):
        self.paged()
        with self.assertRaisesRegex(ValueError, 'absent page'):
            self.ram.read_range(0x3000, 1)

    def test_pae_rejected(self):
        self.paged()
        self.word(0x218, 0x20)
        with self.assertRaisesRegex(ValueError, 'PAE'):
            self.ram.read_range(0x3000, 1)

    def test_physical_graphics_alias_rejected(self):
        self.paged()
        self.word(self.base+0x2000+3*4, 0xa0001)
        # 0xA000 remains ordinary RAM; the forbidden range starts at 0xA0000.
        self.assertEqual(self.ram.physical(0x3000), 0xa0000)
        with self.assertRaisesRegex(ValueError, 'physical read'):
            self.ram.read_range(0x3000, 1)

    def test_logical_graphics_and_crossing_rejected(self):
        for start, size in [(0xa0000, 1), (0x9ffff, 2), (-1, 1), (0, 0)]:
            with self.subTest(start=start, size=size), self.assertRaisesRegex(ValueError, 'conventional'):
                self.ram.read_range(start, size)

    def test_short_host_read_rejected(self):
        self.ram.read = lambda p, n: b''
        with self.assertRaisesRegex(ValueError, 'short'):
            self.ram.state()

    def test_short_mapped_page_read_rejected_without_retrying(self):
        read = self.ram.read
        for short in (b'', b'X'):
            self.ram.read = lambda p, n: short if p >= self.base else read(p, n)
            with self.subTest(short=short), self.assertRaisesRegex(ValueError, 'short mapped'):
                self.ram.read_range(0x4321, 2)


if __name__ == '__main__':
    unittest.main()
