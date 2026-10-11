#!/usr/bin/env python3
"""Compare relocated original MAIN/OP/MAINE and linked DOS VSYNC lifecycle instructions.

Explicit seeded state and mocked BIOS query responses permit an optional
interrupt during query service. This is an instruction diagnostic, not a
physical PC-98 or natural BIOS timing claim. No opcode is replaced.
"""

from pathlib import Path
import csv, json, struct, re, hashlib, itertools, sys, argparse
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
from capstone import Cs, CS_ARCH_X86, CS_MODE_16

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def original(artifact="op"):
    import tomllib

    targets = tomllib.loads((ROOT / "config/targets.toml").read_text())["artifacts"]
    record = next(x for x in targets if x["id"] == "th04-" + artifact)
    packed = ROOT / record["private_path"]
    raw = packed.read_bytes()
    assert len(raw) == record["size"] and sha(packed) == record["sha256"]
    assert parse_mz(raw).valid
    pins = dict(packed=sha(packed))
    if artifact == "main":
        b = raw[int.from_bytes(raw[8:10], "little") * 16 :]
        table = int.from_bytes(raw[24:26], "little")
        sites = []
        for i in range(int.from_bytes(raw[6:8], "little")):
            off, seg = struct.unpack_from("<HH", raw, table + 4 * i)
            sites.append(seg * 16 + off)
        assert len(sites) == 1136
        pins["payload"] = hashlib.sha256(b).hexdigest()
        layout = dict(
            start=0x236C,
            irq=0x23E0,
            dg=0x2134,
            count1=0x2AB2,
            count2=0x2AB4,
            proc=0x76E,
            inc=0x772,
            acc=0x2ABA,
            owner=0x774,
        )
    else:
        profiles = {
            "op": (
                "op-unlock-v1317",
                69028,
                "13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74",
                "84972ed592c6ecbac79fe880db94687522a8880e558bf4b084e92b7afbcf9417",
                804,
            ),
            "maine": (
                "maine-ending-v1291",
                62414,
                "7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c",
                "2ccd7840b883234247ef9892f1274d50d54763b440880c183ffff73246928007",
                559,
            ),
        }
        folder, size, pin, rel_pin, count = profiles[artifact]
        p = ROOT / ".analysis/port64" / folder / "decoded-original/payload.bin"
        b = p.read_bytes()
        assert len(b) == size and sha(p) == pin
        q = p.parent / "relocations.csv"
        assert sha(q) == rel_pin
        sites = [int(x["relative_linear"], 0) for x in csv.DictReader(q.open())]
        assert len(sites) == count
        receipt = json.loads((p.parent / "receipt.json").read_text())
        assert receipt["packed_target_sha256"] == sha(packed) and all(
            receipt["checks"].values()
        )
        pins.update(
            payload=sha(p),
            relocations=sha(q),
            decoded_receipt=sha(p.parent / "receipt.json"),
        )
        layout = (
            dict(
                start=0x2552,
                irq=0x25C6,
                dg=0xF34,
                count1=0x1AC6,
                count2=0x1AC8,
                proc=0x850,
                inc=0x854,
                acc=0x1ACE,
                owner=0x856,
            )
            if artifact == "op"
            else dict(
                start=0x2110,
                irq=0x2184,
                dg=0xE53,
                count1=0xEFA,
                count2=0xEFC,
                proc=0x3FC,
                inc=0x400,
                acc=0xF02,
                owner=0x402,
            )
        )
    irq = layout["irq"]
    # Guard the callback seed against the actual compared and called operands.
    assert (
        b[irq : irq + 7]
        == b"\x50\x1e\xb8" + struct.pack("<H", layout["dg"]) + b"\x8e\xd8"
    )
    assert (
        b[irq + 24 : irq + 29]
        == b"\x83\x3e" + struct.pack("<H", layout["proc"] + 2) + b"\x00"
    )
    assert b[irq + 38 : irq + 42] == b"\xff\x1e" + struct.pack("<H", layout["proc"])
    return dict(body=b, sites=sites, cs=0, artifact=artifact, pins=pins, **layout)


def candidate(exe, mp, source):
    b = exe.read_bytes()
    mz = parse_mz(b)
    assert mz.valid
    body = b[int.from_bytes(b[8:10], "little") * 16 :]
    text = mp.read_text()
    sites = []
    for i in range(int.from_bytes(b[6:8], "little")):
        a = int.from_bytes(b[24:26], "little") + 4 * i
        off, seg = struct.unpack_from("<HH", b, a)
        sites.append(seg * 16 + off)

    def public(n):
        matches = set(
            re.findall(
                r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?"
                + re.escape(n)
                + r"\s*$",
                text,
            )
        )
        assert len(matches) == 1, (n, matches)
        return tuple(int(x, 16) for x in matches.pop())

    cs, start = public("VSYNC_START")
    dg, c1 = public("_vsync_Count1")
    dg2, c2 = public("_vsync_Count2")
    dgp, proc = public("_vsync_Proc")
    assert dg == dg2 == dgp
    spans = re.findall(
        r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+([0-9A-F]{4})\s+C=CODE\b.*\bM=src\\shared\\hardware\\vsync_irq.asm\s",
        text,
    )
    spans = [tuple(int(x, 16) for x in row) for row in spans if int(row[2], 16)]
    assert len(spans) == 1
    seg, off, size = spans[0]
    linear = seg * 16 + off
    code = body[linear : linear + size]
    hits = [m.start() for m in re.finditer(re.escape(b"\x50\x1e\xb8"), code)]
    assert len(hits) == 1
    irq = linear + hits[0] - cs * 16
    assert 0 <= irq < 65536
    d = Cs(CS_ARCH_X86, CS_MODE_16)
    instructions = list(d.disasm(body[cs * 16 + irq : cs * 16 + irq + 40], irq))
    incs = [
        i
        for i in instructions
        if i.mnemonic == "mov"
        and re.fullmatch(r"ax, word ptr \[0x[0-9a-f]+\]", i.op_str)
    ]
    adds = [
        i
        for i in instructions
        if i.mnemonic == "add"
        and re.fullmatch(r"word ptr \[0x[0-9a-f]+\], ax", i.op_str)
    ]
    assert len(incs) == len(adds) == 1
    inc = int(re.search("0x([0-9a-f]+)", incs[0].op_str)[1], 16)
    acc = int(re.search("0x([0-9a-f]+)", adds[0].op_str)[1], 16)
    starts = list(d.disasm(body[cs * 16 + start : cs * 16 + irq], start))
    owners = [
        i
        for i in starts
        if i.mnemonic == "cmp"
        and re.fullmatch(r"byte ptr \[0x[0-9a-f]+\], 0", i.op_str)
    ]
    assert len(owners) == 1
    owner = int(re.search("0x([0-9a-f]+)", owners[0].op_str)[1], 16)
    return dict(
        body=body,
        sites=sites,
        cs=cs,
        start=start,
        irq=irq,
        dg=dg,
        count1=c1,
        count2=c2,
        proc=proc,
        inc=inc,
        acc=acc,
        owner=owner,
        pins={"exe": sha(exe), "map": sha(mp), "source": sha(source)},
    )


def execute(layout, load, feature, mode, phase, oldinc, inject):
    u = Uc(UC_ARCH_X86, UC_MODE_16)
    u.mem_map(0, 1048576)
    image = bytearray(layout["body"])
    for site in layout["sites"]:
        struct.pack_into(
            "<H", image, site, (struct.unpack_from("<H", image, site)[0] + load) & 65535
        )
    u.mem_write(load * 16, bytes(image))
    cs = load + layout["cs"]
    dg = load + layout["dg"]
    data = dg * 16
    for key, val in [("count1", 123), ("count2", 456), ("inc", oldinc), ("acc", phase)]:
        u.mem_write(data + layout[key], struct.pack("<H", val))
    u.mem_write(data + layout["proc"], b"\x00" * 4)
    u.mem_write(data + layout["owner"], b"\xfb")
    u.mem_write(0x45C, bytes([feature]))
    # Authored BIOS mock is outside every loaded product, never target code.
    bios_base = 0x90000
    assert load * 16 + len(image) < bios_base
    u.mem_write(bios_base, bytes.fromhex("fb90cf"))  # STI; NOP; IRET
    bios_pause = []
    bios_frames = []
    trace = []
    writes = []
    ports = []
    bios = []
    pending = []
    stop = 0x7000
    returned = []
    at_irq_return = []
    irq_return = None

    def code(emu, address, size, extra):
        if address == (cs * 16 + stop):
            returned.append(True)
            emu.emu_stop()
            return
        if irq_return is not None and address == irq_return:
            at_irq_return.append(True)
            emu.emu_stop()
            return
        if address == bios_base + 1 and inject and not bios_pause:
            bios_pause.append(True)
            emu.emu_stop()
            return
        trace.append(
            {
                "origin": "mock-bios"
                if bios_base <= address < bios_base + 3
                else "loaded-instructions",
                "cs": emu.reg_read(UC_X86_REG_CS),
                "ip": emu.reg_read(UC_X86_REG_IP),
                "bytes": bytes(emu.mem_read(address, size)).hex(),
            }
        )

    def interrupt(emu, number, extra):
        assert (
            number == 0x18
            and emu.reg_read(UC_X86_REG_AH) == 0x31
            and emu.reg_read(UC_X86_REG_CX) == 0
            and emu.reg_read(UC_X86_REG_DX) == 0
        )
        bios.append({"number": number, "pre_irq": state()})
        emu.reg_write(UC_X86_REG_AX, mode)
        emu.reg_write(UC_X86_REG_BH, 0)
        # UC_HOOK_INTR does not create the x86 INT frame: model it explicitly.
        flags = emu.reg_read(UC_X86_REG_EFLAGS) & 65535
        retcs = emu.reg_read(UC_X86_REG_CS)
        retip = emu.reg_read(UC_X86_REG_IP)
        sp = emu.reg_read(UC_X86_REG_SP)
        ss = emu.reg_read(UC_X86_REG_SS)
        bios_frames.append(
            dict(caller_cs=retcs, caller_ip=retip, sp=sp, ss=ss, flags=flags)
        )
        pending.append(True)
        emu.emu_stop()

    def out(emu, port, size, val, extra):
        ports.append([port, size, val])

    def write(emu, access, address, size, value, extra):
        if data <= address < data + 0x3000:
            writes.append({"offset": address - data, "size": size, "value": value})

    def state():
        return {
            "counts": [
                struct.unpack("<H", u.mem_read(data + layout[k], 2))[0]
                for k in ("count1", "count2")
            ],
            "increment": struct.unpack("<H", u.mem_read(data + layout["inc"], 2))[0],
            "accumulator": struct.unpack("<H", u.mem_read(data + layout["acc"], 2))[0],
        }

    u.hook_add(UC_HOOK_CODE, code)
    u.hook_add(UC_HOOK_INTR, interrupt)
    u.hook_add(UC_HOOK_INSN, out, None, 1, 0, UC_X86_INS_OUT)
    u.hook_add(UC_HOOK_MEM_WRITE, write)
    u.reg_write(UC_X86_REG_CS, cs)
    u.reg_write(UC_X86_REG_DS, dg)
    u.reg_write(UC_X86_REG_SS, 0x8000)
    u.reg_write(UC_X86_REG_SP, 0xFFE0)
    u.reg_write(UC_X86_REG_EFLAGS, 0x202)
    u.mem_write(0x8FFE0, struct.pack("<HH", stop, cs))
    u.emu_start(cs * 16 + layout["start"], 0, count=1000)
    interleaved = None
    if pending:
        assert len(bios_frames) == 1
        frame = bios_frames[0]
        u.mem_write(
            frame["ss"] * 16 + frame["sp"] - 6,
            struct.pack("<HHH", frame["caller_ip"], frame["caller_cs"], frame["flags"]),
        )
        u.reg_write(UC_X86_REG_SP, frame["sp"] - 6)
        u.reg_write(UC_X86_REG_EFLAGS, frame["flags"] & ~0x300)
        u.reg_write(UC_X86_REG_CS, 0x9000)
        u.reg_write(UC_X86_REG_IP, 0)
        u.emu_start(bios_base, 0, count=1000)
        if inject:
            assert bios_pause and not returned
            retcs = u.reg_read(UC_X86_REG_CS)
            retip = u.reg_read(UC_X86_REG_IP)
            flags = u.reg_read(UC_X86_REG_EFLAGS) & 65535
            sp = u.reg_read(UC_X86_REG_SP)
            ss = u.reg_read(UC_X86_REG_SS)
            assert retcs == 0x9000 and retip == 1 and flags & 0x200
            assert sp == bios_frames[0]["sp"] - 6
            u.mem_write(ss * 16 + sp - 6, struct.pack("<HHH", retip, retcs, flags))
            u.reg_write(UC_X86_REG_SP, sp - 6)
            u.reg_write(UC_X86_REG_EFLAGS, flags & ~0x300)
            u.reg_write(UC_X86_REG_CS, cs)
            irq_return = retcs * 16 + retip
            u.emu_start(cs * 16 + layout["irq"], 0, count=1000)
            assert at_irq_return and u.reg_read(UC_X86_REG_SP) == sp
            interleaved = state()
            irq_return = None
            u.emu_start(retcs * 16 + retip, 0, count=1000)
    assert returned and u.reg_read(UC_X86_REG_SP) == 0xFFE4
    after = state()
    start_trace = list(trace)
    start_writes = list(writes)
    start_ports = list(ports)
    trace.clear()
    ports.clear()
    writes.clear()
    returned.clear()
    u.reg_write(UC_X86_REG_CS, cs)
    u.reg_write(UC_X86_REG_SP, 0xFFE0)
    u.mem_write(0x8FFE0, struct.pack("<HHH", stop, cs, 0x202))
    u.reg_write(UC_X86_REG_EFLAGS, 2)
    u.emu_start(cs * 16 + layout["irq"], 0, count=1000)
    assert (
        returned
        and u.reg_read(UC_X86_REG_SP) == 0xFFE6
        and [x[0] for x in ports] == [0, 0x64]
    )
    return dict(
        load_segment=load,
        feature=feature,
        mode_bits=mode,
        phase=phase,
        old_increment=oldinc,
        query_irq=inject,
        after_start=after,
        after_irq=state(),
        interleaved=interleaved,
        bios_calls=bios,
        bios_frames=bios_frames,
        start_trace=start_trace,
        start_writes=start_writes,
        start_ports=start_ports,
        irq_trace=trace,
        irq_writes=writes,
        irq_ports=ports,
    )


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--original-artifact", choices=("op", "main", "maine"), default="op")
    a.add_argument("--candidate-exe", type=Path, required=True)
    a.add_argument("--candidate-map", type=Path, required=True)
    a.add_argument("--candidate-source", type=Path, required=True)
    a.add_argument("--output-dir", type=Path, required=True)
    args = a.parse_args()
    out = args.output_dir.resolve()
    assert not out.exists() and out.is_relative_to(ROOT / ".analysis")
    out.mkdir(parents=True)
    target = original(args.original_artifact)
    compiled = candidate(args.candidate_exe, args.candidate_map, args.candidate_source)
    rows = []
    mismatches = []
    for load, feature, mode, phase, oldinc in itertools.product(
        (0x10FC, 0x3333), (0, 0x40), (0, 12), (0, 12345, 65535), (0, 13311, 65535)
    ):
        for inject in (False, True) if feature else (False,):
            expected = execute(target, load, feature, mode, phase, oldinc, inject)
            actual = execute(compiled, load, feature, mode, phase, oldinc, inject)
            phase2 = (phase + oldinc) & 65535 if inject else phase
            increment = 13311 if feature and mode == 12 else 0
            counted = int(phase2 + increment < 65536)
            assert expected["after_start"] == dict(
                counts=[0, 0], increment=increment, accumulator=phase2
            )
            assert expected["after_irq"] == dict(
                counts=[counted, counted],
                increment=increment,
                accumulator=(phase2 + increment) & 65535,
            )
            keys = (
                "after_start",
                "after_irq",
                "interleaved",
                "bios_calls",
                "start_ports",
                "irq_ports",
            )
            ok = all(actual[k] == expected[k] for k in keys)
            row = dict(passed=ok, target=expected, candidate=actual)
            rows.append(row)
            if not ok:
                mismatches.append(len(rows) - 1)
    lib = Path(unicorn.__file__).parent / "lib/libunicorn.so"
    j = dict(
        passed=not mismatches,
        source_sha256=sha(Path(__file__)),
        target={k: v for k, v in target.items() if k not in ("body", "sites")},
        candidate={k: v for k, v in compiled.items() if k not in ("body", "sites")},
        unicorn_version=unicorn.__version__,
        unicorn_library_sha256=sha(lib),
        rows=rows,
        mismatches=mismatches,
        scope="Actual target and pinned TASM linked candidate instructions, seeded installed sentinel/callback disabled. Explicit BIOS AH31 input plus authored STI/NOP/IRET mock at9000:0000 outside loaded images; actual original/candidate IRQ nests with a separate IRET frame inside that service. Real BIOS/CRT wrapper code not executed. All opcode/write traces retained. Two relocated loads, extension absence/presence, mode0/C, three phases and three prior increments. Diagnostic semantic comparison; no natural BIOS/physical31kHz/frontend/exact acceptance.",
    )
    (out / "receipt.json").write_text(json.dumps(j, indent=2) + "\n")
    print("DOS LIFECYCLE", len(rows), "cases", len(mismatches), "mismatches")
    return 0 if j["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
