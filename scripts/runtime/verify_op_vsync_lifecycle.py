#!/usr/bin/env python3
"""Execute original OP repeated START and one IRQ with nonzero cadence phase.

Twelve typed scenarios vary mode bits, phase and load segment. START and the
actual GDC-query helper run without opcode replacement. A BIOS AH31 response
and an installed hook sentinel are explicit inputs; no IRQ occurs inside START.
This is a bounded Unicorn diagnostic, not natural/physical 31-kHz validation.
"""

from pathlib import Path
import csv, struct, json, hashlib, sys
import unicorn
from unicorn import (
    Uc,
    UC_ARCH_X86,
    UC_MODE_16,
    UC_HOOK_CODE,
    UC_HOOK_INTR,
    UC_HOOK_INSN,
    UC_HOOK_MEM_WRITE,
)
from unicorn.x86_const import *


def main():
    root = Path(__file__).resolve().parents[2]
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    r = args.output_dir.resolve()
    assert not r.exists() and r.is_relative_to(root / ".analysis")
    r.mkdir(parents=True)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    p = root / ".analysis/port64/op-unlock-v1317/decoded-original/payload.bin"
    raw = p.read_bytes()
    # The callback lives in initialized DATA, away from the BSS counters.
    assert raw[0x25DE:0x25E3] == bytes.fromhex("833e520800")
    assert raw[0x25EC:0x25F0] == bytes.fromhex("ff1e5008")
    assert (
        len(raw) == 69028
        and sha(p) == "13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74"
    )
    rel = p.parent / "relocations.csv"
    assert (
        sha(rel) == "84972ed592c6ecbac79fe880db94687522a8880e558bf4b084e92b7afbcf9417"
    )
    sites = [int(x["relative_linear"], 0) for x in csv.DictReader(rel.open())]
    assert len(sites) == 804
    sys.path.insert(0, str(root / "scripts"))
    from lib.pc98 import parse_mz

    packed = root / ".analysis/targets/th04/op.exe"
    assert (
        packed.stat().st_size == 42290
        and sha(packed)
        == "8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f"
        and parse_mz(packed.read_bytes()).valid
    )
    decoded = json.loads((p.parent / "receipt.json").read_text())
    assert decoded["packed_target_sha256"] == sha(packed) and all(
        decoded["checks"].values()
    )
    output = r
    rows = []
    for load in (0x10FC, 0x3333):
        for mode in (0, 12):
            for phase in (0, 12345, 65535):
                u = Uc(UC_ARCH_X86, UC_MODE_16)
                u.mem_map(0, 1048576)
                image = bytearray(raw)
                for site in sites:
                    struct.pack_into(
                        "<H",
                        image,
                        site,
                        (struct.unpack_from("<H", image, site)[0] + load) & 65535,
                    )
                u.mem_write(load * 16, bytes(image))
                dg = load + 0xF34
                data = dg * 16
                u.mem_write(0x45C, bytes([0x40]))
                u.mem_write(data + 0x856, b"\xfb")
                u.mem_write(data + 0x1AC6, struct.pack("<HH", 1, 1))
                u.mem_write(data + 0x854, struct.pack("<H", phase))
                u.mem_write(data + 0x1ACE, struct.pack("<H", phase))
                u.mem_write(data + 0x850, b"\x00" * 4)
                trace = []
                writes = []
                bios = []
                ports = []
                stopped = []
                stop = 0x7000

                def code(emu, address, size, extra):
                    if address == load * 16 + stop:
                        stopped.append(True)
                        emu.emu_stop()
                        return
                    trace.append(
                        dict(
                            cs=emu.reg_read(UC_X86_REG_CS),
                            ip=emu.reg_read(UC_X86_REG_IP),
                            bytes=bytes(emu.mem_read(address, size)).hex(),
                        )
                    )

                def interrupt(emu, number, extra):
                    assert (
                        number == 0x18
                        and emu.reg_read(UC_X86_REG_AH) == 0x31
                        and emu.reg_read(UC_X86_REG_CX) == 0
                        and emu.reg_read(UC_X86_REG_DX) == 0
                    )
                    bios.append(number)
                    emu.reg_write(UC_X86_REG_AX, mode)
                    emu.reg_write(UC_X86_REG_BH, 0)

                def out(emu, port, size, value, extra):
                    ports.append((port, size, value))

                def write(emu, access, address, size, value, extra):
                    if data <= address < data + 0x2000:
                        writes.append(
                            dict(offset=address - data, size=size, value=value)
                        )

                u.hook_add(UC_HOOK_CODE, code)
                u.hook_add(UC_HOOK_INTR, interrupt)
                u.hook_add(UC_HOOK_INSN, out, None, 1, 0, UC_X86_INS_OUT)
                u.hook_add(UC_HOOK_MEM_WRITE, write)

                def execute(ip, irq=False):
                    u.reg_write(UC_X86_REG_CS, load)
                    u.reg_write(UC_X86_REG_DS, dg)
                    u.reg_write(UC_X86_REG_SS, 0x7000)
                    u.reg_write(UC_X86_REG_SP, 0xFFE0)
                    u.reg_write(UC_X86_REG_EFLAGS, 2)
                    u.mem_write(
                        0x7FFE0,
                        struct.pack("<HHH", stop, load, 2)
                        if irq
                        else struct.pack("<HH", stop, load),
                    )
                    stopped.clear()
                    u.emu_start(load * 16 + ip, 0, count=500)
                    assert stopped and u.reg_read(UC_X86_REG_SP) == 0xFFE0 + (
                        6 if irq else 4
                    )

                def state():
                    return dict(
                        counts=list(struct.unpack("<HH", u.mem_read(data + 0x1AC6, 4))),
                        increment=struct.unpack("<H", u.mem_read(data + 0x854, 2))[0],
                        accumulator=struct.unpack("<H", u.mem_read(data + 0x1ACE, 2))[
                            0
                        ],
                    )

                before = state()
                execute(0x2552)
                after = state()
                start_trace = list(trace)
                start_writes = list(writes)
                assert (
                    len(bios) == 1
                    and not ports
                    and after
                    == dict(
                        counts=[0, 0], increment=13311 if mode else 0, accumulator=phase
                    )
                )
                assert not any(
                    x["offset"] <= 0x1ACE < x["offset"] + x["size"] for x in writes
                )
                execute(0x25C6, irq=True)
                irq_state = state()
                value = phase + after["increment"]
                counted = int(value < 65536)
                assert irq_state == dict(
                    counts=[counted, counted],
                    increment=after["increment"],
                    accumulator=value & 65535,
                )
                assert [x[0] for x in ports] == [0, 0x64]
                rows.append(
                    dict(
                        load_segment=load,
                        dgroup=dg,
                        mode_bits=mode,
                        phase=phase,
                        before=before,
                        after_start=after,
                        after_irq=irq_state,
                        start_writes=start_writes,
                        start_trace=start_trace,
                        irq_trace=trace[len(start_trace) :],
                        bios_calls=bios,
                        irq_ports=ports,
                    )
                )
    lib = Path(unicorn.__file__).parent / "lib/libunicorn.so"
    assert lib.is_file()
    j = dict(
        passed=True,
        packed_target_sha256=sha(packed),
        decoded_receipt_sha256=sha(p.parent / "receipt.json"),
        canonicality="candidate-local-attested",
        payload_sha256=sha(p),
        relocations_sha256=sha(rel),
        unicorn_version=unicorn.__version__,
        unicorn_library_sha256=sha(lib),
        source_sha256=sha(Path(__file__)),
        rows=rows,
        scope="Actual complete original OP START0000:2552..25BB plus GDC query0000:15C2..1617 and IRQ0000:25C6 executed under Unicorn. Installed owner0xFB, explicitly seeded counter/cadence phase and typed BIOS AH31 responses0/C; IRQs absent during START, one explicit original IRQ afterward. Full payload relocated at10FC/3333. Target diagnostic, not natural31kHz/physical timing/exact acceptance. Direct START owns Count1/2 reset and increment selection, preserves accumulator; native v1398 phase-reset hypothesis falsified.",
    )
    (output / "receipt.json").write_text(json.dumps(j, indent=2) + "\n")
    print("ORIGINAL LIFECYCLE PASS", len(rows), flush=True)


if __name__ == "__main__":
    main()
