import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'sparse_capture_progress_target', ROOT/'scripts/probes/capture_th04_dos_sparse_fonts.py')
CAPTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAPTURE)


class Clock:
    now = 0


class Child:
    args = ['test-collector']

    def __init__(self, clock, steps):
        self.clock, self.steps = clock, iter(steps)

    def wait(self, timeout):
        try:
            action = next(self.steps)
        except StopIteration:
            return 0
        self.clock.now += 1
        action()
        raise subprocess.TimeoutExpired(self.args, timeout)


class SparseCaptureProgressTests(unittest.TestCase):
    def test_blocking_ui_progress_prevents_false_idle(self):
        for name in ['input-polls.jsonl', 'keyboard-admission.jsonl']:
            with self.subTest(stream=name), tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)
                head, stream = folder/'stage-input-loops.jsonl', folder/name
                head.write_text('one completed head\n')
                clock = Clock()

                def append():
                    with stream.open('a') as output:
                        output.write('one new observation\n')

                child = Child(clock, [append]*6)
                with patch.object(CAPTURE.time, 'monotonic', lambda: clock.now):
                    self.assertEqual(CAPTURE.wait_capture(child, head, 30, 2), 0)

    def test_all_stopped_streams_raise_idle(self):
        with tempfile.TemporaryDirectory() as temporary:
            head = Path(temporary)/'stage-input-loops.jsonl'
            head.write_text('one completed head\n')
            clock = Clock()
            child = Child(clock, [lambda: None]*6)
            with patch.object(CAPTURE.time, 'monotonic', lambda: clock.now):
                with self.assertRaisesRegex(CAPTURE.CaptureProgressTimeout, 'input-observation-idle'):
                    CAPTURE.wait_capture(child, head, 30, 2)

    def test_total_deadline_still_applies_to_growing_stream(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            head, stream = folder/'stage-input-loops.jsonl', folder/'keyboard-admission.jsonl'
            clock = Clock()

            def append():
                with stream.open('a') as output:
                    output.write('one new observation\n')

            child = Child(clock, [append]*6)
            with patch.object(CAPTURE.time, 'monotonic', lambda: clock.now):
                with self.assertRaises(subprocess.TimeoutExpired):
                    CAPTURE.wait_capture(child, head, 3, 5)


if __name__ == '__main__':
    unittest.main()
