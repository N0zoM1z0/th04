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
import replay_th04_zun_file_ropen as file_ropen
import replay_th04_zun_file_write as file_write
import replay_th04_zun_file_seek as file_seek
import replay_th04_zun_file_append as file_append
import replay_th04_zun_file_close as file_close
import replay_th04_zun_fontopen as fontopen
import replay_th04_zun_version_grp as version_grp
import replay_th04_zun_file_state as file_state
import replay_th04_zun_file_read as file_read
import replay_th04_zun_resdata as resdata


class ZunSupportReplayImportTests(unittest.TestCase):
    def test_transitive_source_closure_is_live(self) -> None:
        for module in (resdata, file_read, dos_free, dos_axdx, dos_puts2, file_create, file_ropen, file_write, file_seek, file_append, file_close, fontopen, version_grp, file_state):
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


    def test_file_ropen_member_contract(self) -> None:
        self.assertEqual(file_ropen.FILE_ROPEN_MEMBER_POSITION, 170)
        self.assertEqual(file_ropen.FILE_ROPEN_TARGET_OFFSET, 0x1174)
        self.assertEqual(file_ropen.FILE_ROPEN_MODULE_SIZE, 0x36)
        self.assertTrue(file_ropen.LOCAL_FILE_ROPEN.is_file())


    def test_file_write_member_contract(self) -> None:
        self.assertEqual(file_write.FILE_WRITE_MEMBER_POSITION, 171)
        self.assertEqual(file_write.FILE_WRITE_TARGET_OFFSET, 0x11AA)
        self.assertEqual(file_write.FILE_WRITE_MODULE_SIZE, 0xA6)
        self.assertTrue(file_write.LOCAL_FILE_WRITE.is_file())


    def test_file_seek_member_contract(self) -> None:
        self.assertEqual(file_seek.FILE_SEEK_MEMBER_POSITION, 177)
        self.assertEqual(file_seek.FILE_SEEK_TARGET_OFFSET, 0x128C)
        self.assertEqual(file_seek.FILE_SEEK_BODY_SIZE, 0x33)
        self.assertEqual(file_seek.FILE_TELL_BODY_SIZE, 0x0E)
        self.assertEqual(file_seek.FILE_SEEK_MODULE_SIZE, 0x42)
        self.assertTrue(file_seek.LOCAL_FILE_SEEK.is_file())


    def test_file_append_member_contract(self) -> None:
        self.assertEqual(file_append.FILE_APPEND_MEMBER_POSITION, 182)
        self.assertEqual(file_append.FILE_APPEND_TARGET_OFFSET, 0x12CE)
        self.assertEqual(file_append.FILE_APPEND_MODULE_SIZE, 0x50)
        self.assertTrue(file_append.LOCAL_FILE_APPEND.is_file())


    def test_file_close_member_contract(self) -> None:
        self.assertEqual(file_close.FILE_CLOSE_MEMBER_POSITION, 167)
        self.assertEqual(file_close.FILE_CLOSE_TARGET_OFFSET, 0x10FA)
        self.assertEqual(file_close.FILE_FLUSH_BODY_SIZE, 0x6B)
        self.assertEqual(file_close.FILE_CLOSE_BODY_SIZE, 0x0E)
        self.assertEqual(file_close.FILE_CLOSE_MODULE_SIZE, 0x7A)
        self.assertTrue(file_close.LOCAL_FILE_CLOSE.is_file())


    def test_fontopen_member_contract(self) -> None:
        self.assertEqual(fontopen.FONTOPEN_MEMBER_POSITION, 337)
        self.assertEqual(fontopen.FONTOPEN_TARGET_CODE_OFFSET, 0x136C)
        self.assertEqual(fontopen.FONTOPEN_TARGET_DATA_OFFSET, 0x2212)
        self.assertEqual(fontopen.FONTOPEN_CODE_SIZE, 0x18)
        self.assertEqual(fontopen.FONTOPEN_DATA_SIZE, 0x02)
        self.assertTrue(fontopen.LOCAL_FONTOPEN.is_file())


    def test_version_grp_member_contract(self) -> None:
        self.assertEqual(version_grp.VERSION_MEMBER_POSITION, 0)
        self.assertEqual(version_grp.VERSION_TARGET_DATA_OFFSET, 0x219A)
        self.assertEqual(version_grp.VERSION_DATA_SIZE, 0x5D)
        self.assertEqual(version_grp.VERSION_TARGET_PADDING_OFFSET, 0x21F7)
        self.assertEqual(version_grp.GRP_MEMBER_POSITION, 91)
        self.assertEqual(version_grp.GRP_TARGET_DATA_OFFSET, 0x21F8)
        self.assertEqual(version_grp.GRP_DATA_SIZE, 0x0B)
        self.assertEqual(version_grp.GRP_TARGET_PADDING_OFFSET, 0x2203)
        self.assertTrue(version_grp.LOCAL_VERSION.is_file())
        self.assertTrue(version_grp.LOCAL_GRP.is_file())


    def test_file_state_member_contract(self) -> None:
        self.assertEqual(file_state.FILE_STATE_MEMBER_POSITION, 163)
        self.assertEqual(file_state.FILE_STATE_TARGET_DATA_OFFSET, 0x220E)
        self.assertEqual(file_state.FILE_STATE_DATA_SIZE, 0x04)
        self.assertEqual(file_state.FILE_STATE_BSS_SIZE, 0x14)
        self.assertTrue(file_state.LOCAL_FILE_STATE.is_file())

    def test_file_state_map_gate_only_allows_bufferpos_alias_swap(self) -> None:
        original = "\n".join((
            "prefix",
            " 0000:19E2 idle  _file_BufferPos",
            " 0000:19E2       file_BufferPos",
            "suffix",
        )).encode("cp437")
        swapped = "\n".join((
            "prefix",
            " 0000:19E2       file_BufferPos",
            " 0000:19E2 idle  _file_BufferPos",
            "suffix",
        )).encode("cp437")
        wrong = swapped.replace(b"19E2", b"19E4", 1)
        self.assertTrue(file_state.map_equal_except_bufferpos_alias_order(original, original))
        self.assertTrue(file_state.map_equal_except_bufferpos_alias_order(original, swapped))
        self.assertFalse(file_state.map_equal_except_bufferpos_alias_order(original, wrong))


if __name__ == "__main__":
    unittest.main()
