from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from th04_stage_input_plan import parse_stage_input


class StageInputPlanTests(unittest.TestCase):
    def test_v1_preserves_physical_latch_identity(self):
        self.assertEqual(parse_stage_input(b'TH04_STAGE_INPUT 1 2 2\n0 32 0\n1 56 0\n'),
                         (1, 2, 2, (32, 56), (32, 56)))

    def test_v2_keeps_ui_latch_separate_from_requested_buttons(self):
        self.assertEqual(parse_stage_input(b'TH04_STAGE_INPUT 2 2 2\n0 32 8192\n1 32 32\n'),
                         (2, 2, 2, (32, 32), (8192, 32)))

    def test_v2_allows_a_physical_escape_edge(self):
        self.assertEqual(parse_stage_input(b'TH04_STAGE_INPUT 2 0 1\n0 4128 4128\n')[3:],
                         ((4128,), (4128,)))

    def test_reserved_v1_word_and_unmapped_physical_keys_reject(self):
        for raw in (b'TH04_STAGE_INPUT 1 0 1\n0 32 8192\n',
                    b'TH04_STAGE_INPUT 1 0 1\n0 4096 0\n',
                    b'TH04_STAGE_INPUT 2 0 1\n0 64 0\n',
                    b'TH04_STAGE_INPUT 2 0 1\n0 8192 8192\n'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_stage_input(raw)

    def test_bad_order_extent_or_latch_width_reject(self):
        for raw in (b'', b'TH04_STAGE_INPUT 3 0 1\n0 32 0\n',
                    b'TH04_STAGE_INPUT 2 1 1\n0 32 32\n',
                    b'TH04_STAGE_INPUT 2 0 2\n0 32 32\n',
                    b'TH04_STAGE_INPUT 2 0 1\n1 32 32\n',
                    b'TH04_STAGE_INPUT 2 0 1\n0 32 -1\n',
                    b'TH04_STAGE_INPUT 2 0 1\n0 32 65536\n'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_stage_input(raw)


if __name__ == '__main__':
    unittest.main()
