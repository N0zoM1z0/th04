"""The native differential reader must reject omissions and hidden RNG wraps."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'port64'))
spec = importlib.util.spec_from_file_location('native_demo_reader', ROOT/'port64/verify_demo_state.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def corpus():
    rows = []
    for demo in range(1, 5):
        for frame in range(3997):
            cells = [str(demo),str(frame),'T' if frame==3996 else 'I','0','0','0',
                     '00'*8,'0','0','1','00'*256,'0','0','0','128','0','0','0',
                     '3','2','0','0','0','0']
            rows.append(' '.join(cells))
    return ('\n'.join(rows)+'\n').encode()


class NativeDemoTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = corpus()
        cls.rows = reader.parse_native(cls.raw)

    def test_complete_equal_pair(self):
        report=reader.compare(self.rows,self.rows)
        self.assertTrue(report['passed'])
        self.assertEqual(report['gameplay_boundaries'],15984)
        self.assertEqual(report['terminal_boundaries'],4)

    def test_rejects_missing_frame(self):
        with self.assertRaisesRegex(ValueError,'extent'):
            reader.parse_native(self.raw.split(b'\n',1)[1])

    def test_rejects_duplicate_frame(self):
        lines=self.raw.splitlines();lines[1]=lines[0]
        with self.assertRaisesRegex(ValueError,'order'):
            reader.parse_native(b'\n'.join(lines))

    def test_rejects_terminal_gameplay(self):
        lines=self.raw.splitlines();lines[3996]=lines[3996].replace(b' T ',b' I ')
        with self.assertRaisesRegex(ValueError,'terminal'):
            reader.parse_native(b'\n'.join(lines))

    def test_complete_ring_bytes_are_compared(self):
        changed=copy.deepcopy(self.rows)
        changed[4][3996]['ring']='00'*255+'01'
        report=reader.compare(self.rows,changed)
        self.assertFalse(report['passed'])
        self.assertEqual(report['first_difference']['demo'],4)
        self.assertEqual(report['first_difference']['frame'],3996)

    def test_counter_rejects_equal_wrapped_cursor(self):
        changed=copy.deepcopy(self.rows)
        changed[2][281]['ring_calls']=256
        report=reader.compare(self.rows,changed)
        self.assertFalse(report['passed'])
        self.assertEqual(report['first_difference']['fields']['ring_calls']['native'],256)

    def test_score_difference_does_not_accept_other_demos(self):
        changed=copy.deepcopy(self.rows);changed[2][3533]['score_delta']='01000000'
        report=reader.compare(self.rows,changed)
        self.assertFalse(report['passed'])
        self.assertTrue(report['demos']['1']['passed'])
        self.assertFalse(report['demos']['2']['passed'])

    def test_rejects_counter_decrease(self):
        lines=self.raw.splitlines();cells=lines[1].split();cells[-1]=b'1';lines[1]=b' '.join(cells)
        with self.assertRaisesRegex(ValueError,'count order'):
            reader.parse_native(b'\n'.join(lines))
