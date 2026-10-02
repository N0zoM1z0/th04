import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/probes"))
from inspect_th04_play_trace import reduce_records


def sample(frame, keys, x, shots=0, bombs=2, used=0):
    words = [1, frame, keys, 0, x, 4000, 0, shots, 0, 2, bombs, 0, used, 0, 1, 48]
    return struct.pack("<24H", *words, *([0] * 8))


class PlayTraceTests(unittest.TestCase):
    def test_actions_need_effects(self):
        data = (sample(0, 8, 200) + sample(32, 8, 240)
                + sample(40, 4, 230) + sample(64, 4, 190)
                + sample(72, 32, 190, shots=3)
                + sample(80, 16, 190, bombs=1, used=1))
        result = reduce_records(data)
        self.assertTrue(result["input_actions_pass"])
        self.assertEqual(result["max_active_shots"], 3)

    def test_keys_alone_do_not_accept_actions(self):
        data = b"".join(sample(i * 32, keys, 200)
                        for i, keys in enumerate([8, 8, 4, 4, 32, 16]))
        self.assertFalse(reduce_records(data)["input_actions_pass"])
        self.assertFalse(any(reduce_records(data)["actions"].values()))

    def test_stage_reset_does_not_prove_motion(self):
        data = sample(400, 8, 200) + sample(0, 8, 500)
        self.assertFalse(reduce_records(data)["actions"]["move_right"])

    def test_partial_and_invalid_records_fail(self):
        for data in (b"", b"x", sample(0, 0, 200)[:-1]):
            with self.assertRaises(ValueError):
                reduce_records(data)
        words = list(struct.unpack("<24H", sample(0, 0, 200)))
        words[-1] = 10
        with self.assertRaises(ValueError):
            reduce_records(struct.pack("<24H", *words))


if __name__ == "__main__":
    unittest.main()
