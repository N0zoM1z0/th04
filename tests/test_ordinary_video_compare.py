"""Bounded Boss video must retain terminal, baseline and mapping guards."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
import compare_th04_ordinary_video as video
import compare_th04_ordinary_pools as pools


class BoundedVideoTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.layout = dict(passed=True, layout=video.LAYOUT, emulator_sha256='emulator',
                           emulator_receipt_sha256='receipt', source_inputs={},
                           symbols={name: dict(address=1000 + i, size=size)
                                    for i, (name, size) in enumerate(video.SYMBOL_SIZES.items())})
        layout = self.directory / 'layout.json'
        layout.write_text(json.dumps(self.layout))
        self.receipt = dict(end_after=7500, emulator_sha256='emulator',
                            emulator_receipt_sha256='receipt',
                            files={'ordinary-video.json': 'pin', 'ordinary-video.bin.gz': 'pin'},
                            video_layout=dict(path=str(layout), sha256=video.sha(layout.read_bytes())))
        self.terminal = dict(load_segment=0x1000, dgroup_segment=0x2000, cr0=1, cr3=4096)
        self.capture = dict(receipt=self.receipt, bounded_terminal=self.terminal)
        self.metadata = dict(schema_version=1, complete=True, boundary=video.BOUNDARY,
                             frames=7500, block_bytes=video.BLOCK_SIZE, layout=video.LAYOUT,
                             load_segment=0x1000, dgroup_segment=0x2000,
                             video_symbols={name: row['address'] + 10000
                                            for name, row in self.layout['symbols'].items()},
                             video_mappings=[dict(first_frame=1, backing_ram=0x100000,
                                                  backing_bytes=0x44000, cpu_page=0x104000,
                                                  display_page=0x10c000)])
        (self.directory / 'raw.txt').write_text('L 1 1000 1 1000\n')
        self.write()

    def write(self):
        (self.directory / 'receipt.json').write_text(json.dumps(self.receipt))
        (self.directory / 'ordinary-video.json').write_text(json.dumps(self.metadata))

    def read(self):
        # Target/terminal attestation and baseline semantics have separate controls.
        with patch.object(video, 'read_bounded_side', return_value=(self.capture, dict(dgroup=0x1000), iter(()))), \
             patch.object(video, 'scalar_control', return_value={'passed': True}), \
             patch.object(video, 'records', return_value=iter(())) as reader:
            video.video_side(self.directory, self.directory, b'', None)
            return reader.call_args.args

    def test_bounded_extent_reaches_reader(self):
        self.assertEqual(self.read()[-1], 7500)

    def test_old_extent_or_incomplete_metadata_rejects(self):
        for key, value in (('frames', 3996), ('complete', False), ('boundary', 'demo')):
            old = self.metadata[key]
            self.metadata[key] = value
            self.write()
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'extent/boundary'):
                self.read()
            self.metadata[key] = old

    def test_terminal_cpu_context_must_match_video(self):
        for key in self.terminal:
            self.terminal[key] += 1
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'terminal CPU'):
                self.read()
            self.terminal[key] -= 1

    def test_mapping_extent_and_elf_bias_remain_guarded(self):
        self.metadata['video_mappings'].append(dict(self.metadata['video_mappings'][0], first_frame=7501))
        self.write()
        with self.assertRaisesRegex(ValueError, 'backing/page extent'):
            self.read()
        self.metadata['video_mappings'].pop()
        self.metadata['video_symbols'][next(iter(video.SYMBOL_SIZES))] += 1
        self.write()
        with self.assertRaisesRegex(ValueError, 'ELF mapping'):
            self.read()


class IndependentControlTests(unittest.TestCase):
    def setUp(self):
        receipt = {key: 'pin' for key in ('role', 'main_sha256', 'map_sha256', 'initial_hdi_sha256',
                                         'emulator_sha256', 'debugger_sha256', 'font_sha256')}
        receipt.update(end_after=7500, dialog_at_frame=6548, termination='observed-after-update-prefix',
                       natural_game_exit=False, files={'dosbox-x.conf': 'config'})
        self.capture = dict(receipt=receipt, starting_files={})
        self.baseline = copy.deepcopy(self.capture)

    def check(self):
        with patch.object(pools, 'load', return_value=self.baseline), \
             patch.object(pools, 'compare', return_value={'passed': True}):
            return pools.scalar_control(self.capture, Path('baseline'), b'', None)

    def test_identical_contract_passes(self):
        self.assertTrue(self.check()['passed'])

    def test_different_extent_dialog_or_exit_class_rejects(self):
        for key, value in (('end_after', 3996), ('dialog_at_frame', 6547),
                           ('termination', 'natural-exit'), ('natural_game_exit', True)):
            old = self.baseline['receipt'][key]
            self.baseline['receipt'][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'baseline contract'):
                self.check()
            self.baseline['receipt'][key] = old

    def test_different_emulator_configuration_rejects(self):
        self.baseline['receipt']['files']['dosbox-x.conf'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'baseline emulator configuration'):
            self.check()


if __name__ == '__main__':
    unittest.main()
