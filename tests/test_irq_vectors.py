from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/probes"))
from audit_th04_native_irq_vectors import direct_call_segments, vector_targets


class IrqVectorTests(unittest.TestCase):
    def test_group_base_changes_vector_destination(self) -> None:
        code = b"\x0e\x1f\xba\x0a\x00\xb8\x0a\x25\xcd\x21\x50\x1e\xb8"
        signatures = {10: b"\x50\x1e\xb8"}
        self.assertTrue(vector_targets(code, 0x2000, 0x200, signatures)[0]["pass_vector"])
        self.assertFalse(vector_targets(code, 0x2000, 0x100, signatures)[0]["pass_vector"])

    def test_absent_installation_cannot_pass(self) -> None:
        with self.assertRaises(ValueError):
            vector_targets(b"", 0, 0, {10: b"\x50\x1e\xb8"})

    def test_same_entry_can_have_distinct_call_segment_frames(self) -> None:
        calls = bytes.fromhex("9A10000200 9A20000100")
        self.assertEqual(direct_call_segments(calls, 0x30, {3, 8}, []), {1, 2})
        self.assertEqual(direct_call_segments(calls, 0x30, set(), []), set())

    def test_opcode_in_previous_operand_does_not_hide_relocated_call(self) -> None:
        self.assertEqual(direct_call_segments(bytes.fromhex("9A9A00010000"),
                                              0x100, {4}, []), {0})
