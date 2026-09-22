import struct
import unittest

from scripts.probes.probe_th04_trial_intake_v500 import (
    basename_cp932,
    parse_lha_level01,
)


def level0_member(name: str, payload: bytes) -> bytes:
    name_raw = name.encode("cp932")
    rest = (
        b"-lh0-"
        + struct.pack("<I", len(payload))
        + struct.pack("<I", len(payload))
        + b"\0\0\0\0"
        + bytes([0x20, 0, len(name_raw)])
        + name_raw
        + b"\0\0"
    )
    return bytes([len(rest), sum(rest) & 0xFF]) + rest + payload


class TrialLhaParserTests(unittest.TestCase):
    def test_level0_cp932_member_and_terminator(self):
        stream = level0_member("体験版.TXT", b"fixture") + b"\0"
        rows, end = parse_lha_level01(stream, 0)
        self.assertEqual([row["name"] for row in rows], ["体験版.TXT"])
        self.assertEqual(rows[0]["method"], "-lh0-")
        self.assertEqual(rows[0]["packed_size"], 7)
        self.assertEqual(end, len(stream))

    def test_header_checksum_mutation_is_rejected(self):
        stream = bytearray(level0_member("GAME.BAT", b"x") + b"\0")
        stream[1] ^= 1
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            parse_lha_level01(bytes(stream), 0)

    def test_level2_is_fail_closed(self):
        stream = bytearray(level0_member("GAME.BAT", b"x") + b"\0")
        stream[20] = 2
        header_size = stream[0]
        stream[1] = sum(stream[2 : 2 + header_size]) & 0xFF
        with self.assertRaisesRegex(ValueError, "unsupported LHA level 2"):
            parse_lha_level01(bytes(stream), 0)

    def test_member_basename_is_dos_path_insensitive(self):
        self.assertEqual(basename_cp932(r"GENSO\game.bat"), "GAME.BAT")
        self.assertEqual(basename_cp932("docs/体験版.txt"), "体験版.TXT")


if __name__ == "__main__":
    unittest.main()
