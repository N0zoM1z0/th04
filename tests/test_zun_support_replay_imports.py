from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROBES = Path(__file__).resolve().parents[1] / "scripts" / "probes"
sys.path.insert(0, str(PROBES))

import replay_th04_zun_dos_puts2 as dos_puts2
import replay_th04_zun_dos_axdx as dos_axdx
import replay_th04_zun_dos_free as dos_free
import replay_th04_zun_file_create as file_create
import replay_th04_zun_file_read as file_read
import replay_th04_zun_resdata as resdata


class ZunSupportReplayImportTests(unittest.TestCase):
    def test_transitive_source_closure_is_live(self) -> None:
        for module in (resdata, file_read, dos_free, dos_axdx, dos_puts2, file_create):
            closure = module.source_closure(module.ROOT, tuple(module.SOURCES.values()))
            self.assertIn("src/zun/config/cfg_init.cpp", closure)
            self.assertIn("src/zun/resident/main.cpp", closure)
            self.assertNotIn("HEADERS", module.__dict__)


    def test_dos_free_member_contract(self) -> None:
        self.assertEqual(dos_free.DOS_FREE_MEMBER_POSITION, 211)
        self.assertEqual(dos_free.DOS_FREE_TARGET_OFFSET, 0x131E)
        self.assertEqual(dos_free.DOS_FREE_TARGET_SIZE, 0x10)
        self.assertTrue(dos_free.LOCAL_DOS_FREE.is_file())


    def test_dos_axdx_member_contract(self) -> None:
        self.assertEqual(dos_axdx.DOS_AXDX_MEMBER_POSITION, 216)
        self.assertEqual(dos_axdx.DOS_AXDX_TARGET_OFFSET, 0x132E)
        self.assertEqual(dos_axdx.DOS_AXDX_BODY_SIZE, 0x15)
        self.assertEqual(dos_axdx.DOS_AXDX_MODULE_SIZE, 0x16)
        self.assertTrue(dos_axdx.LOCAL_DOS_AXDX.is_file())


    def test_dos_puts2_member_contract(self) -> None:
        self.assertEqual(dos_puts2.DOS_PUTS2_MEMBER_POSITION, 221)
        self.assertEqual(dos_puts2.DOS_PUTS2_TARGET_OFFSET, 0x1344)
        self.assertEqual(dos_puts2.DOS_PUTS2_BODY_SIZE, 0x27)
        self.assertEqual(dos_puts2.DOS_PUTS2_MODULE_SIZE, 0x28)
        self.assertTrue(dos_puts2.LOCAL_DOS_PUTS2.is_file())


    def test_file_create_member_contract(self) -> None:
        self.assertEqual(file_create.FILE_CREATE_MEMBER_POSITION, 172)
        self.assertEqual(file_create.FILE_CREATE_TARGET_OFFSET, 0x1250)
        self.assertEqual(file_create.FILE_CREATE_BODY_SIZE, 0x3B)
        self.assertEqual(file_create.FILE_CREATE_MODULE_SIZE, 0x3C)
        self.assertTrue(file_create.LOCAL_FILE_CREATE.is_file())


if __name__ == "__main__":
    unittest.main()
