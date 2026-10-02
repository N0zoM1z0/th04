from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/probes"))
from inspect_th04_emulator_cpu_fault import decode_packets, locate, relocate
from inspect_th04_cpu_fault_trace import decode_lines


PACKET = "TH04_CPUFAULT 0 00 0913 011E 0913 FFFE 0913 F000 0001 0000 00FF 0000 0100 FFFE 091C 00007202"


class EmulatorCpuFaultTests(unittest.TestCase):
    def test_calibration_registers_and_raw_flags(self):
        fault, = decode_packets("LOG: harmless\n" + PACKET + "\n")
        self.assertEqual((fault["vector"], fault["ax"], fault["bx"], fault["dx"]), (0, 1, 0, 0))
        self.assertEqual(fault["raw_lazy_flags"], 0x7202)

    def test_incomplete_duplicate_and_wrong_vector_fail(self):
        for text in (PACKET.rsplit(" ", 1)[0], PACKET + "\n" + PACKET,
                     PACKET.replace("0 00", "1 00", 1),
                     PACKET.replace("0 00", "0 05", 1),
                     PACKET.replace("0913", "913", 1)):
            with self.subTest(text=text), self.assertRaises(ValueError):
                decode_packets(text)

    def test_loaded_code_requires_relocation_and_complete_snapshot_match(self):
        image = bytearray(192)
        struct.pack_into("<14H", image, 0, 0x5A4D, 192, 1, 1, 4, 0, 0xFFFF,
                         0, 0x80, 0, 0, 0, 28, 0)
        struct.pack_into("<2H", image, 28, 0x14, 0)
        image[64:] = bytes(range(128))
        struct.pack_into("<H", image, 64 + 0x14, 0x1234)
        loaded = relocate(bytes(image), 0x1000)
        self.assertEqual(loaded[0x14:0x16], bytes.fromhex("3422"))
        text = " 0000:0010 0060 C=CODE S=TEXT G=CODE M=owner.cpp\n 0000:0010 function()\n"
        fault = dict(cs=0x1000, ip=0x10)
        snapshot = loaded[0x10:0x50]
        owner = locate(fault, snapshot, bytes(image), text)
        self.assertEqual(owner["main_load_segment"], 0x1000)
        self.assertEqual(owner["nearest_public"]["name"], "function()")
        self.assertIsNone(locate(fault, bytes(image)[0x50:0x90], bytes(image), text))
        changed = bytearray(snapshot)
        changed[-1] ^= 1
        self.assertIsNone(locate(fault, bytes(changed), bytes(image), text))

    def test_guest_state_packet_requires_a_matching_exception(self):
        state = "Bochs port E9h: M1234 0002 0000 0100 0005 0008 00FF 0000 0000 0000"
        with self.assertRaises(ValueError):
            decode_lines(state, [])
        arm = "Bochs port E9h: A2000 10FC 0163"
        values = [0, 0x2000, 0x123, 0x1234, 0x100, 0x1234] + [0] * 31
        frame = "Bochs port E9h: F" + " ".join(f"{v:04X}" for v in values)
        result = decode_lines("\n".join((arm, frame, state)), [])
        self.assertEqual(result["faults"][0]["state"]["boss_statebyte0"], 255)
        for bad in (state.replace("M1234", "M1235"), state + "\n" + state):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                decode_lines("\n".join((arm, frame, bad)), [])
