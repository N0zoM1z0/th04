"""Portable data-container checks using authored synthetic files, no game data."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_assets', ROOT / 'port64/prepare_assets.py')
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


class PrepareAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = {
            'MAIN.EXE': bytes(range(256)) * 35,
            '幻想郷ED.DAT': b'ending' * 1601,
            '東方幻想.郷': b'main data' * 3101,
        }
        game = tuple((name, len(data), assets.digest(data)) for name, data in self.files.items())
        self.pinned = patch.object(assets, 'GAME', game)
        self.pinned.start()
        self.addCleanup(self.pinned.stop)

    def image_path(self):
        path = self.root / 'test.hdi'
        path.write_bytes(assets.build_image(self.files))
        return path

    def test_deterministic_multicluster_round_trip(self):
        path = self.image_path()
        self.assertEqual(path.stat().st_size, assets.IMAGE_BYTES)
        self.assertEqual(path.read_bytes(), assets.build_image(self.files))
        self.assertEqual(assets.compatible_image(path), self.files)
        self.assertEqual(assets.short_name('幻想郷ED.DAT'), '幻想郷ED'.encode('cp932') + b'DAT')

    def test_find_content_even_when_names_are_garbled(self):
        for i, data in enumerate(self.files.values()):
            (self.root / f'garbled-{i}.bin').write_bytes(data)
        self.assertEqual(assets.installed_files(self.root), self.files)
        (self.root / 'garbled-0.bin').write_bytes(b'trial or modified data')
        with self.assertRaisesRegex(ValueError, 'missing full-version'):
            assets.installed_files(self.root)

    def test_corrupt_geometry_or_payload_rejected(self):
        path = self.image_path()
        data = bytearray(path.read_bytes())
        data[assets.DATA + assets.CLUSTER + 100] ^= 1
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'game data differs'):
            assets.compatible_image(path)
        data[assets.PARTITION + 11] ^= 1
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'unsupported HDI layout'):
            assets.compatible_image(path)

    def test_fat_mismatch_and_cycle_rejected(self):
        path = self.image_path()
        data = bytearray(path.read_bytes())
        # Directory cluster 2 loops to itself; first corrupt just one mirror.
        first = assets.PARTITION + assets.SECTOR
        data[first + 3] = 2
        data[first + 4] &= 0xf0
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'mirrors disagree'):
            assets.compatible_image(path)
        data[first + assets.FAT_BYTES:first + 2 * assets.FAT_BYTES] = data[first:first + assets.FAT_BYTES]
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'invalid HDI FAT chain'):
            assets.compatible_image(path)

    def test_cli_preserves_existing_files_before_writing(self):
        source = self.root / 'original'
        source.mkdir()
        for name, data in self.files.items():
            (source / name).write_bytes(data)
        font = self.root / 'font.bmp'
        font.write_bytes(b'authored test font')
        rom = self.root / 'rom.bin'
        rom.write_bytes(b'authored test rhythm')
        output = self.root / 'output'
        output.mkdir()
        (output / 'FREECG98.BMP').write_bytes(b'existing font')
        args = ['prepare_assets.py', '--game-dir', str(source), '--font', str(font),
                '--rhythm-rom', str(rom), '--output-dir', str(output)]
        with patch('sys.argv', args), patch.object(assets, 'FONT_SHAS', {assets.digest(font.read_bytes())}), \
                patch.object(assets, 'ROM_SHA', assets.digest(rom.read_bytes())), \
                redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as rejected:
                assets.main()
            self.assertEqual(rejected.exception.code, 2)
            self.assertFalse((output / 'th04.hdi').exists())
            self.assertEqual((output / 'FREECG98.BMP').read_bytes(), b'existing font')
            (output / 'FREECG98.BMP').unlink()
            assets.main()
            before = {p.name: p.read_bytes() for p in output.iterdir()}
            assets.main()
            self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})
            self.assertEqual(assets.compatible_image(output / 'th04.hdi'), self.files)


if __name__ == '__main__':
    unittest.main()
