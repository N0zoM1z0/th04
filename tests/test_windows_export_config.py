"""A cleaned demo package must remain a valid input to the Windows exporter."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from export_windows_play import package_reference_config, performance_config


class PackageReferenceConfigTests(unittest.TestCase):
    def test_missing_reference_restores_budget_and_preserves_both_mounts(self):
        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder) / 'reference.conf'
            for image in ('play.hdi', 'play-normal.hdi'):
                config = ('[cpu]\ncore=dynamic\ncputype=pentium\ncycles=24000\n'
                          '[dosbox]\nmachine=pc98\nmemsize=32\n'
                          '[autoexec]\nimgmount c ' + image + '\n').encode()
                reference = package_reference_config(missing, config)
                self.assertIn(b'cycles=15000', reference)
                self.assertEqual(performance_config(reference), config)
                self.assertFalse(missing.exists())

    def test_existing_reference_is_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'reference.conf'
            original = b'[cpu]\ncycles=15000\n[autoexec]\nimgmount c play.hdi\n'
            path.write_bytes(original)
            self.assertEqual(package_reference_config(path, b'unused'), original)

    def test_missing_reference_rejects_changed_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            for config in (b'cycles=36000', b'cycles=max', b'cycles=24000\ncycles=24000'):
                with self.assertRaises(ValueError):
                    package_reference_config(Path(folder) / 'missing.conf', config)


if __name__ == '__main__':
    unittest.main()
