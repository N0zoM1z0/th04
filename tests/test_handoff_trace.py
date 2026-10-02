from __future__ import annotations

from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/probes"))
from inspect_th04_handoff_trace import (
    decode_config, decode_scores, reduce_checkpoints, reduce_config_save,
)


def checkpoint(marker: int, detail: int = 0) -> bytes:
    return struct.pack("<4H", marker, detail, 4332, 5312)


class HandoffTraceTests(unittest.TestCase):
    def test_returned_init_alone_does_not_accept_failed_allocation(self) -> None:
        files = {f"ME{i:02X}    BIN": checkpoint(i) for i in range(0x20, 0x2A)}
        files["ME02    BIN"] = checkpoint(2)
        files["ME21    BIN"] = checkpoint(0x21, 65528)
        self.assertFalse(reduce_checkpoints(files)["maine_initialized"])
        files["ME21    BIN"] = checkpoint(0x21)
        self.assertTrue(reduce_checkpoints(files)["maine_initialized"])

    def test_entry_is_not_init_completion(self) -> None:
        result = reduce_checkpoints({"ME00    BIN": checkpoint(0)})
        self.assertTrue(result["maine_entered"])
        self.assertFalse(result["maine_initialized"])

    def test_corrupt_checkpoint_rejected(self) -> None:
        for data in [b"", checkpoint(1)]:
            with self.assertRaises(ValueError):
                reduce_checkpoints({"ME00    BIN": data})

    def test_truncated_score_file_rejected(self) -> None:
        with self.assertRaises(ValueError):
            decode_scores(bytes(1959))

    def test_checksum_is_the_historical_byte_result(self) -> None:
        encoded = bytearray(1960)
        encoded[3] = 1  # A 256 difference is zero after the target's byte return.
        self.assertTrue(decode_scores(encoded)[0]["checksum_valid"])
        encoded[2] = 1
        self.assertFalse(decode_scores(encoded)[0]["checksum_valid"])

    def test_checksum_alone_does_not_supply_valid_score_digits(self) -> None:
        decoded = decode_scores(bytes(1960))
        self.assertTrue(all(section["checksum_valid"] for section in decoded))
        self.assertTrue(all(None in section["scores"] for section in decoded))

    def test_config_change_requires_checksum_and_valid_options(self) -> None:
        before = bytes.fromhex("020302020101ef9f000b")
        after = bytes.fromhex("0304010201010000000c")
        self.assertTrue(reduce_config_save(before, after)["saved"])
        self.assertFalse(reduce_config_save(before, after[:-1] + b"\x0b")["saved"])
        # A checksum-correct seven-life configuration is still invalid.
        invalid = bytes.fromhex("0307010201010000000f")
        self.assertFalse(reduce_config_save(before, invalid)["saved"])

    def test_saved_config_must_clear_resident_pointer(self) -> None:
        before = bytes.fromhex("020302020101ef9f000b")
        stale = bytes.fromhex("030401020101ef9f000c")
        self.assertFalse(reduce_config_save(before, stale)["saved"])

    def test_cleared_pointer_alone_is_not_changed_options(self) -> None:
        before = bytes.fromhex("020302020101ef9f000b")
        after = bytes.fromhex("0203020201010000000b")
        result = reduce_config_save(before, after)
        self.assertTrue(result["valid"])
        self.assertFalse(result["saved"])

    def test_truncated_config_rejected(self) -> None:
        with self.assertRaises(ValueError):
            decode_config(bytes(9))


if __name__ == "__main__":
    unittest.main()
