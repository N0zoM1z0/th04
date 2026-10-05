#!/usr/bin/env python3
"""Exercise compiled input latches and release/press waits with synthetic I/O.

Runs the complete relocated maintained MAIN and its real input/joystick/frame
functions. BIOS bitmap, modifier replies, controller ports and logical VSync
ticks are fixtures; this does not attest physical PC-98 cadence or Windows FPS.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct

import unicorn
from unicorn import UC_HOOK_CODE, UC_HOOK_INTR, UC_HOOK_INSN
from unicorn.x86_const import UC_X86_REG_AX, UC_X86_INS_IN

from probe_th04_native_planar_kernels import ROOT, LOAD, product, vm

# Independent BIOS-key-to-game-action fixtures; diagonals are separate bits.
KEYS = (
    (0x531, 0x04, 0x0001), (0x531, 0x20, 0x0002),
    (0x531, 0x08, 0x0004), (0x531, 0x10, 0x0008),
    (0x533, 0x01, 0x0008), (0x533, 0x04, 0x0400),
    (0x533, 0x08, 0x0002), (0x533, 0x10, 0x0800),
    (0x532, 0x40, 0x0004), (0x532, 0x04, 0x0100),
    (0x532, 0x08, 0x0001), (0x532, 0x10, 0x0200),
    (0x52F, 0x02, 0x0020), (0x52F, 0x04, 0x0010),
    (0x52C, 0x01, 0x4000), (0x52A, 0x01, 0x1000),
    (0x52D, 0x10, 0x2000), (0x530, 0x10, 0x0020),
)


def fixture(prod, entry, arguments, modifiers, joystick_present, joystick_bits):
    machine, run, put = vm(prod, entry, arguments)
    put("js_bexist", struct.pack("<H", joystick_present))
    put("js_stat", struct.pack("<H", 0xA55A))

    def interrupt(cpu, number, _):
        assert number == 0x18 and cpu.reg_read(UC_X86_REG_AX) >> 8 == 2
        cpu.reg_write(UC_X86_REG_AX, 0x200 | modifiers)

    def read_port(cpu, port, size, _):
        assert size == 1 and port in (0x188, 0x18A)
        return 0 if port == 0x188 else (~joystick_bits & 255)

    machine.hook_add(UC_HOOK_INTR, interrupt)
    machine.hook_add(UC_HOOK_INSN, read_port, None, 1, 0, UC_X86_INS_IN)

    def read(symbol, size):
        segment, offset = prod["entries"][symbol]
        return int.from_bytes(machine.mem_read((LOAD + segment) * 16 + offset, size), "little")

    return machine, run, put, read


def set_keys(machine, selected):
    bitmap = bytearray(10)
    for index in selected:
        address, mask, _ = KEYS[index]
        bitmap[address - 0x52A] |= mask
    machine.mem_write(0x52A, bytes(bitmap))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(ROOT / ".analysis"):
        parser.error("output must be a new private directory")
    prod = product(args.build_dir / "MAIN.EXE", args.build_dir / "build.json")
    results = []
    samples = [()] + [(index,) for index in range(len(KEYS))] + [tuple(range(len(KEYS)))]
    for selected in samples:
        expected_keys = 0
        for index in selected:
            expected_keys |= KEYS[index][2]
        for present, buttons in ((0, 0), (1, 0), (1, 0x21)):
            for reset in (False, True):
                for modifiers in (0, 1):
                    entry = "input_reset_sense()" if reset else "input_sense()"
                    machine, run, put, read = fixture(prod, entry, b"", modifiers, present, buttons)
                    put("_key_det", struct.pack("<H", 0x4000))
                    put("_shiftkey", bytes([1 - modifiers]))
                    set_keys(machine, selected)
                    instructions, ports = run()
                    expected = expected_keys | buttons | (0 if reset else 0x4000)
                    assert read("_key_det", 2) == expected
                    assert read("_shiftkey", 1) == modifiers
                    assert read("js_stat", 2) == (0 if reset else 0xA55A)
                    assert ports == ([[0x188, 1, 15], [0x18A, 1, 128], [0x188, 1, 14]] if present else [])
                    results.append(dict(kind="sense",keys=selected,joystick_present=present,
                                        joystick_bits=buttons,reset=reset,modifiers=modifiers,
                                        result_bits=expected,instructions=instructions))

    # The release duration is outside the timeout. Samples occur after a tick;
    # even an initially released key consumes one release tick before press.
    waits = ((3, 0, None), (3, 3, None), (3, 0, 2), (3, 3, 5),
             (1, 0, 3), (-1, 0, None), (-1, 5, None),
             (0, 0, 12015), (9999, 0, 10005), (10000, 0, 10001),
             (2, 0, 4), (1, 3, 5))
    frame_segment, frame_offset = prod["entries"]["frame_delay(int)"]
    frame_address = (LOAD + frame_segment) * 16 + frame_offset
    for timeout, held_until, press_at in waits:
        machine, run, put, read = fixture(prod, "input_wait_for_change(int)",
                                           struct.pack("<h", timeout), 0, 0, 0)
        ticks = [0]
        set_keys(machine, (12,) if held_until else ())

        def tick(cpu, address, size, _):
            if address == frame_address:
                ticks[0] += 1
                held = ticks[0] < held_until or (press_at is not None and ticks[0] >= press_at)
                set_keys(cpu, (12,) if held else ())
            # Independently supply a logical IRQ tick to the volatile word.
            # Execute the real frame-delay reset/compare/return instructions.
            if frame_address <= address < frame_address + 0x15:
                put("_vsync_Count1", struct.pack("<H", 1))

        machine.hook_add(UC_HOOK_CODE, tick)
        instructions, ports = run()
        # Reset samples before the tick and sense samples after it, ORing
        # their actions. Release therefore needs a complete clear interval.
        released_at = held_until + 1 if held_until else 1
        if timeout < 0:
            expected_ticks = released_at
        elif timeout in (0, 9999):
            expected_ticks = max(released_at + 1, press_at)
        else:
            deadline = released_at + timeout
            expected_ticks = min(deadline, max(released_at + 1, press_at)) if press_at else deadline
        assert ticks[0] == expected_ticks, (timeout, held_until, press_at, ticks[0], expected_ticks)
        assert not ports
        results.append(dict(kind="wait",timeout=timeout,held_until=held_until,press_at=press_at,
                            elapsed_ticks=ticks[0],instructions=instructions))

    engine = Path(unicorn.unicorn._uc._name).resolve()
    report = dict(observed_utc=datetime.now(timezone.utc).isoformat(),scope=__doc__,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  unicorn_version=unicorn.__version__,
                  unicorn_engine_sha256=hashlib.sha256(engine.read_bytes()).hexdigest(),
                  product_sha256=prod["exe_sha256"],map_sha256=prod["map_sha256"],
                  load_segment=LOAD,passed=True,results=results)
    output.mkdir(parents=True)
    (output / "receipt.json").write_text(json.dumps(report,indent=2) + "\n")
    print(json.dumps(dict(passed=True,cases=len(results),receipt=str(output / "receipt.json"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
