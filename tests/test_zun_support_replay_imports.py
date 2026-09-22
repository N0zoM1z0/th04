from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROBES = Path(__file__).resolve().parents[1] / "scripts" / "probes"
sys.path.insert(0, str(PROBES))

import replay_th04_zun_dos_free as dos_free
import replay_th04_zun_file_read as file_read
import replay_th04_zun_resdata as resdata


class ZunSupportReplayImportTests(unittest.TestCase):
    def test_transitive_source_closure_is_live(self) -> None:
        for module in (resdata, file_read, dos_free):
            closure = module.source_closure(module.ROOT, tuple(module.SOURCES.values()))
            self.assertIn("src/zun/config/cfg_init.cpp", closure)
            self.assertIn("src/zun/resident/main.cpp", closure)
            self.assertNotIn("HEADERS", module.__dict__)


    def test_dos_free_member_contract(self) -> None:
        self.assertEqual(dos_free.DOS_FREE_MEMBER_POSITION, 211)
        self.assertEqual(dos_free.DOS_FREE_TARGET_OFFSET, 0x131E)
        self.assertEqual(dos_free.DOS_FREE_TARGET_SIZE, 0x10)
        self.assertTrue(dos_free.LOCAL_DOS_FREE.is_file())


if __name__ == "__main__":
    unittest.main()
