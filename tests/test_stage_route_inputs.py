"""Reject independent raw-latch and physical-edge mutations in route evidence."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/probes'))
from attest_th04_stage3_route import attest_input_rows


class StageRouteInputTests(unittest.TestCase):
    def fixture(self, physical, expected):
        rows = [dict(stage=2, frame=i, physical=p, actual=e, expected=e)
                for i, (p, e) in enumerate(zip(physical, expected, strict=True))]
        raw = {(2, i): dict(fields=dict(input=e.to_bytes(2, 'little').hex(), shift_raw='00'))
               for i, e in enumerate(expected)}
        return rows, raw

    def test_v1_cannot_declare_a_different_latch(self):
        rows, raw = self.fixture([32, 32], [32, 8192])
        with self.assertRaisesRegex(ValueError, 'V1 physical/latch identity'):
            attest_input_rows([32, 32], rows, raw, [], expected_inputs=[32, 8192])

    def test_v2_accepts_only_the_declared_independent_raw_latch(self):
        rows, raw = self.fixture([32, 32], [32, 8192])
        self.assertEqual(attest_input_rows([32, 32], rows, raw, [],
                         expected_inputs=[32, 8192], version=2), 0)
        mutated = copy.deepcopy(raw)
        mutated[(2, 1)]['fields']['input'] = '2000'
        with self.assertRaisesRegex(ValueError, 'independent raw inputs'):
            attest_input_rows([32, 32], rows, mutated, [],
                              expected_inputs=[32, 8192], version=2)

    def test_v2_physical_sidecar_cannot_be_replaced_with_latch(self):
        rows, raw = self.fixture([32, 32], [32, 8192])
        rows[1]['physical'] = 8192
        with self.assertRaisesRegex(ValueError, 'physical sidecar'):
            attest_input_rows([32, 32], rows, raw, [],
                              expected_inputs=[32, 8192], version=2)

    def test_escape_edges_follow_physical_intent_and_keep_ram_guard(self):
        physical, expected = [32, 4128, 32], [32, 0, 8192]
        rows, raw = self.fixture(physical, expected)
        actions = [dict(stage=2, next_loop_frame=i, key='KBD_esc', pressed=pressed,
                        unchanged_guest=True, conventional_memory_sha256='ab' * 32, tick=i)
                   for i, pressed in [(1, True), (2, False)]]
        self.assertEqual(attest_input_rows(physical, rows, raw, actions,
                         expected_inputs=expected, version=2), 2)
        for name in ('wrong-edge', 'failed-guard'):
            changed = copy.deepcopy(actions)
            if name == 'wrong-edge':
                changed[0]['next_loop_frame'] = 2
                message = 'ordered real keyboard edges'
            else:
                changed[0]['unchanged_guest'] = False
                message = 'keyboard CPU/tick/full RAM guards'
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, message):
                attest_input_rows(physical, rows, raw, changed,
                                  expected_inputs=expected, version=2)


if __name__ == '__main__':
    unittest.main()
