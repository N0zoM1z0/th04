#!/usr/bin/env python3
"""Execute attested DOS SMEM and graph-copy instructions with seeded RAM/I/O.

The DOS allocation replies and two VRAM banks are explicit component stimuli.
No original or compiled instruction is replaced. This checks function behavior,
not physical PC-98 timing or historical byte-exact acceptance.
"""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_INTR, UC_HOOK_INSN
from unicorn.x86_const import *

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/runtime"))
from verify_dos_vsync_lifecycle import original
from lib.pc98 import parse_mz

REGS = {
    "ax": UC_X86_REG_AX, "bx": UC_X86_REG_BX, "cx": UC_X86_REG_CX,
    "dx": UC_X86_REG_DX, "si": UC_X86_REG_SI, "di": UC_X86_REG_DI,
    "bp": UC_X86_REG_BP, "ds": UC_X86_REG_DS, "es": UC_X86_REG_ES,
}
OFFSETS = {
    "main": (0x21F4, 0x21DE, 0x77E, 0x2AC2, 0x2ABE, 0x784, None),
    "op": (0x248E, 0x2478, 0x860, 0x1AD6, 0x1AD2, 0x866, 0x156C),
    "maine": (0x209A, 0x2084, 0x40C, 0xF0A, 0xF06, 0x412, 0x11C2),
}
VRAM = ((0xA8000, 0x18000), (0xE0000, 0x8000))
MEMORY_STORE = None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retain(data):
    pin = hashlib.sha256(data).hexdigest()
    if MEMORY_STORE is not None:
        path = MEMORY_STORE / (pin + ".bin.gz")
        if not path.exists():
            path.write_bytes(gzip.compress(data, mtime=0))
    return pin


def target(artifact):
    x = original(artifact)
    get, release, base, end, top, reserve, graph = OFFSETS[artifact]
    body = x["body"]
    word = lambda value: struct.pack("<H", value)
    assert body[get:get + 5] == b"\x83\x3e" + word(base) + b"\x00"
    assert body[get + 25:get + 28] == b"\xa1" + word(end)
    assert body[get + 32:get + 36] == b"\x39\x1e" + word(top)
    assert body[get + 38:get + 42] == b"\x89\x1e" + word(end)
    assert body[get + 47:get + 53] == b"\xb8\xf8\xff\xca\x02\x00"
    assert body[release:release + 15] == (
        b"\x53\x8b\xdc\x36\x8b\x5f\x06\x89\x1e" + word(end) + b"\x5b\xca\x02\x00")
    functions = {"SMEM_WGET": (0, get), "SMEM_RELEASE": (0, release)}
    for row in csv.DictReader((ROOT / "config/th04_function_boundaries.csv").open()):
        if row["artifact"] == "th04-" + artifact and row["name"] in (
            "MEM_ASSIGN", "HMEM_ALLOC", "HMEM_FREE"
        ):
            functions[row["name"]] = (0, int(row["segment_offset"], 0))
    if graph is not None:
        functions["GRAPH_COPY_PAGE"] = (0, graph)
        assert body[graph:graph + 6] == b"\x33\xd2\x8b\x0e" + word({"op": 0x572, "maine": 0x11E}[artifact])
    x.update(functions=functions, data={"base": base, "end": end, "top": top,
             "reserve": reserve, "words": {"op": 0x572, "maine": 0x11E}.get(artifact)})
    return x


def linked(exe, mp, artifact):
    raw = exe.read_bytes()
    assert parse_mz(raw).valid
    body = raw[struct.unpack_from("<H", raw, 8)[0] * 16:]
    sites = []
    table = struct.unpack_from("<H", raw, 24)[0]
    for i in range(struct.unpack_from("<H", raw, 6)[0]):
        off, seg = struct.unpack_from("<HH", raw, table + 4 * i)
        sites.append(seg * 16 + off)
    text = mp.read_text()

    def public(name):
        hits = set(re.findall(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+(?:idle\s+)?"
                             + re.escape(name) + r"\s*$", text))
        assert len(hits) == 1, (name, hits)
        return tuple(int(v, 16) for v in hits.pop())

    names = ["MEM_ASSIGN", "HMEM_ALLOC", "HMEM_FREE", "GRAPH_COPY_PAGE"]
    for name in ("SMEM_WGET", "SMEM_RELEASE"):
        if re.search(r"\b" + name + r"\s*$", text, re.M):
            names.append(name)
    functions = {name: public(name) for name in names}
    dg, words = public("_graph_VramWords")
    reserve = None
    if re.search(r"\b_mem_Reserve\s*$", text, re.M):
        rdg, reserve = public("_mem_Reserve")
        assert rdg == dg
    return dict(body=body, sites=sites, dg=dg, functions=functions,
                data={"words": words, "reserve": reserve}, artifact=artifact,
                pins={"exe": digest(exe), "map": digest(mp)})


def product_map(receipt, artifact):
    directory = receipt.parent / "source/obj"
    if artifact != "main":
        directory /= "product"
    return directory / (artifact + "-native.map")


class Machine:
    def __init__(self, layout, load, dos=None):
        self.layout = layout
        self.load = load
        self.dg = load + layout["dg"]
        self.u = Uc(UC_ARCH_X86, UC_MODE_16)
        self.u.mem_map(0, 0x200000)
        body = bytearray(layout["body"])
        for site in layout["sites"]:
            struct.pack_into("<H", body, site,
                             (struct.unpack_from("<H", body, site)[0] + load) & 0xFFFF)
        self.u.mem_write(load * 16, bytes(body))
        self.done = False
        self.error = None
        self.io = []
        self.dos = dos
        self.services = []
        self.page = 0
        self.banks = None
        self.u.hook_add(UC_HOOK_CODE, self.guarded(self.code))
        self.u.hook_add(UC_HOOK_INTR, self.guarded(self.interrupt))
        self.u.hook_add(UC_HOOK_INSN, self.guarded(self.out), None, 1, 0, UC_X86_INS_OUT)

    def guarded(self, callback):
        # Old Unicorn ctypes callbacks can print and swallow exceptions.
        # Stop the guest and report them at the ordinary Python call boundary.
        def invoke(*args):
            try:
                callback(*args)
            except Exception as error:
                self.error = (type(error).__name__, str(error))
                self.u.emu_stop()
        return invoke

    def code(self, u, address, size, data):
        if address == 0xF0010:
            self.done = True
            u.emu_stop()

    def interrupt(self, u, number, data):
        assert number == 0x21 and self.dos is not None, (number, self.services)
        ax = u.reg_read(UC_X86_REG_AX)
        bx = u.reg_read(UC_X86_REG_BX)
        self.services.append({"ah": ax >> 8, "bx": bx})
        assert ax >> 8 == 0x48, hex(ax)
        flags = u.reg_read(UC_X86_REG_EFLAGS)
        if len(self.services) == 1:
            assert bx == 0xFFFF
            if self.dos.get("query_success"):
                u.reg_write(UC_X86_REG_AX, 0x6000)
                u.reg_write(UC_X86_REG_EFLAGS, flags & ~1)
            else:
                u.reg_write(UC_X86_REG_AX, 8)
                u.reg_write(UC_X86_REG_BX, self.dos["largest"])
                u.reg_write(UC_X86_REG_EFLAGS, flags | 1)
        else:
            assert len(self.services) == 2
            if self.dos.get("fail"):
                u.reg_write(UC_X86_REG_AX, 8)
                u.reg_write(UC_X86_REG_EFLAGS, flags | 1)
            else:
                u.reg_write(UC_X86_REG_AX, self.dos["base"])
                u.reg_write(UC_X86_REG_EFLAGS, flags & ~1)

    def out(self, u, port, size, value, data):
        self.io.append([port, size, value])
        assert size == 1 and port in (0x7C, 0xA6), (port, size, value)
        if port == 0xA6 and self.banks is not None:
            for i, (address, length) in enumerate(VRAM):
                self.banks[self.page][i] = bytes(u.mem_read(address, length))
            self.page = value & 1
            for i, (address, length) in enumerate(VRAM):
                u.mem_write(address, self.banks[self.page][i])

    def set_data(self, key, value):
        off = self.layout["data"][key]
        assert off is not None, key
        self.u.mem_write(self.dg * 16 + off, struct.pack("<H", value))

    def call(self, name, args=(), flags=0xAD7):
        u = self.u
        seed = dict(ax=0x1111, bx=0x1357, cx=0x2468, dx=0x369C,
                    si=0xABCD, di=0x9876, bp=0x1234, ds=self.dg, es=0x4444)
        for key, value in seed.items():
            u.reg_write(REGS[key], value)
        u.reg_write(UC_X86_REG_SS, 0x9000)
        u.reg_write(UC_X86_REG_SP, 0xFF00)
        u.reg_write(UC_X86_REG_EFLAGS, flags)
        frame = struct.pack("<HH", 0x10, 0xF000)
        frame += b"".join(struct.pack("<H", arg & 0xFFFF) for arg in reversed(args))
        u.mem_write(0x9FF00, frame)
        cs, ip = self.layout["functions"][name]
        u.reg_write(UC_X86_REG_CS, self.load + cs)
        u.reg_write(UC_X86_REG_IP, ip)
        self.done = False
        self.error = None
        u.emu_start((self.load + cs) * 16 + ip, 0x200000, count=1500000)
        assert self.error is None, (self.layout["artifact"], self.load, name, args, self.error)
        assert self.done, (name, hex(u.reg_read(UC_X86_REG_CS)), hex(u.reg_read(UC_X86_REG_IP)))
        assert u.reg_read(UC_X86_REG_SP) == 0xFF04 + 2 * len(args)
        regs = {key: u.reg_read(reg) for key, reg in REGS.items()}
        result = {"ax": regs["ax"], "carry": u.reg_read(UC_X86_REG_EFLAGS) & 1}
        if name == "SMEM_WGET":
            assert all(regs[k] == v for k, v in seed.items() if k != "ax"), regs
        if name == "SMEM_RELEASE":
            assert regs == seed, regs
            assert u.reg_read(UC_X86_REG_EFLAGS) & 0xFFFF == flags
        if name == "GRAPH_COPY_PAGE":
            assert all(regs[k] == seed[k] for k in ("bp", "si", "di", "ds")), regs
        return result

    def bind(self, base, paragraphs):
        self.call("MEM_ASSIGN", (base, paragraphs), flags=0x202)

    def end(self):
        return self.call("SMEM_WGET", (0,))["ax"]

    def begin_video(self):
        self.banks = [[bytes(((p * 71 + i * 53 + j * 13 + j // 97) & 255)
                             for j in range(length)) for i, (_, length) in enumerate(VRAM)]
                      for p in range(2)]
        for i, (address, _) in enumerate(VRAM):
            self.u.mem_write(address, self.banks[0][i])

    def picture(self):
        for i, (address, length) in enumerate(VRAM):
            self.banks[self.page][i] = bytes(self.u.mem_read(address, length))
        return [[retain(b) for b in page] for page in self.banks]


def allocator_controls(a, b, load):
    records = []
    counts = (0, 1, 15, 16, 17, 112, 113, 240, 241, 255, 256, 257, 0xFFF0, 0xFFF1, 0xFFFF)
    regions = ((0x7000, 0), (0x7000, 1), (0x7000, 16), (0x7000, 4096),
               (0xFFF8, 0), (0xFFF8, 7), (0xFFF0, 15), (0xFFFE, 1))
    for base, paragraphs in regions:
        for count in counts:
            machines = [Machine(x, load) for x in (a, b)]
            outputs = []
            for m in machines:
                m.bind(base, paragraphs)
                result = m.call("SMEM_WGET", (count,))
                result["end"] = m.end()
                outputs.append(result)
            assert outputs[0] == outputs[1], (base, paragraphs, count, outputs)
            records.append(dict(kind="get", base=base, paragraphs=paragraphs,
                                bytes=count, outputs=outputs))
    for rewind, flags in ((rewind, flags)
                         for rewind in (0, 0x6FFF, 0x7000, 0x7001, 0x7040, 0xFFF8, 0xFFFF)
                         for flags in (0x202, 0xED7)):
        outputs = []
        for x in (a, b):
            m = Machine(x, load)
            m.bind(0x7000, 0x40)
            m.call("SMEM_WGET", (32,))
            m.call("SMEM_RELEASE", (rewind,), flags=flags)
            outputs.append(m.call("SMEM_WGET", (0,)))
        assert outputs[0] == outputs[1], (rewind, outputs)
        records.append(dict(kind="release", rewind=rewind, flags=flags, outputs=outputs))
    sequence = (("SMEM_WGET", 512), ("HMEM_ALLOC", 32), ("HMEM_ALLOC", 31),
                ("SMEM_WGET", 1), ("HMEM_FREE", 0x7021), ("SMEM_WGET", 1),
                ("SMEM_RELEASE", 0x7000), ("HMEM_ALLOC", 63),
                ("SMEM_WGET", 1), ("HMEM_FREE", 0x7001), ("SMEM_WGET", 16))
    outputs = []
    for x in (a, b):
        m = Machine(x, load)
        m.bind(0x7000, 0x40)
        rows = []
        for name, arg in sequence:
            result = m.call(name, (arg,))
            rows.append(dict(name=name, arg=arg,
                             result=result if name == "SMEM_WGET" else
                             {"ax": result["ax"]} if name == "HMEM_ALLOC" else {}, end=m.end()))
        outputs.append(rows)
    assert outputs[0] == outputs[1], outputs
    records.append(dict(kind="shared-gap", outputs=outputs))
    outputs = []
    for x in (a, b):
        m = Machine(x, load)
        m.bind(0x7000, 0x100)
        sequence = (("SMEM_WGET", 17), ("SMEM_WGET", 32), ("SMEM_WGET", 255),
                    ("SMEM_RELEASE", 0x7004), ("SMEM_WGET", 16),
                    ("SMEM_RELEASE", 0x7002), ("SMEM_WGET", 256),
                    ("SMEM_RELEASE", 0x7000))
        rows = []
        for name, arg in sequence:
            r = m.call(name, (arg,))
            rows.append(dict(name=name, arg=arg, result=r if name == "SMEM_WGET" else {}, end=m.end()))
        outputs.append(rows)
    assert outputs[0] == outputs[1], outputs
    records.append(dict(kind="nested-workspaces", outputs=outputs))
    outputs = []
    for x in (a, b):
        m = Machine(x, load)
        m.bind(0x7000, 0x100)
        handles = [m.call("HMEM_ALLOC", (size,))["ax"] for size in (16, 8, 4)]
        workspace = m.call("SMEM_WGET", ((handles[2] - 1 - 0x7000) * 16,))
        m.call("HMEM_FREE", (handles[1],))
        reuse = m.call("HMEM_ALLOC", (6,))["ax"]
        blocked = m.call("SMEM_WGET", (1,))
        outputs.append(dict(handles=handles, workspace=workspace, reuse=reuse, blocked=blocked, end=m.end()))
    assert outputs[0] == outputs[1], outputs
    records.append(dict(kind="hole-reuse-with-full-workspace", outputs=outputs))
    for largest in (0, 1, 16, 255, 256, 257, 512, 4096):
        for reserve in (0, 1, 256, 65535):
            for fail in (False, True):
                dos = dict(largest=largest, base=0x7000, fail=fail)
                outputs = []
                for x in (a, b):
                    m = Machine(x, load, dos)
                    m.bind(0, 0)
                    m.set_data("reserve", reserve)
                    result = m.call("SMEM_WGET", (16,))
                    outputs.append(dict(result=result, services=m.services))
                assert outputs[0] == outputs[1], (dos, reserve, outputs)
                records.append(dict(kind="auto", dos=dos, reserve=reserve, outputs=outputs))
    for reserve in (0, 256, 65535):
        for fail in (False, True):
            dos = dict(largest=65535, base=0x7000, fail=fail, query_success=True)
            outputs = []
            for x in (a, b):
                m = Machine(x, load, dos)
                m.bind(0, 0)
                m.set_data("reserve", reserve)
                outputs.append(dict(result=m.call("SMEM_WGET", (16,)), services=m.services))
            assert outputs[0] == outputs[1], (dos, reserve, outputs)
            records.append(dict(kind="auto-query-success", dos=dos, reserve=reserve, outputs=outputs))
    return records


def graph_control(layout, load, words, destination, paragraphs, busy):
    m = Machine(layout, load)
    m.u.mem_write(0x70000, bytes([0xD3]) * 65536)
    m.bind(0x7000, paragraphs)
    if busy:
        assert m.call("HMEM_ALLOC", (busy,))["ax"]
    if "SMEM_WGET" in layout["functions"]:
        before = m.end()
    else:
        before = None
    m.set_data("words", words)
    m.begin_video()
    result = m.call("GRAPH_COPY_PAGE", (destination,), flags=0x202)
    picture = m.picture()
    io = m.io.copy()
    after = m.end() if before is not None else None
    return dict(ax=result["ax"], io=io, page=m.page, picture=picture,
                cursor=(before, after), scratch=retain(bytes(
                    m.u.mem_read(0x70000, min(words, 32768) * 2))),
                outside_vram=[retain(bytes(m.u.mem_read(address, 0x8000)))
                              for address in (0xC0000, 0xE8000)])


def main():
    global MEMORY_STORE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--old-build", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    MEMORY_STORE = args.output / "memory"
    MEMORY_STORE.mkdir(exist_ok=True)
    package = json.loads((args.build / "build.json").read_text())
    report = dict(scope="seeded DOS instructions; DF=0 for page copy; explicit INT21 allocation replies",
                  package_sha256=digest(args.build / "build.json"), source_fingerprint=package["source_fingerprint"], artifacts={})
    for artifact in ("main", "op", "maine"):
        product = package["products"][artifact]
        receipt = Path(product["build_receipt"])
        mp = product_map(receipt, artifact)
        assert mp.is_file(), mp
        a = target(artifact)
        b = linked(args.build / (artifact.upper() + ".EXE"), mp, artifact)
        assert b["pins"]["exe"] == product["sha256"]
        rows = []
        for load in (0x1000, 0x3333):
            rows.extend(dict(load=load, **row) for row in allocator_controls(a, b, load))
        graph_rows = []
        if artifact != "main":
            scenarios = [(words, destination, (words * 2 & 0xFFFF) // 16 + 2, 0)
                         for words in (0, 1, 7, 16, 16000, 0x7FFF, 0x8000, 0x8001, 0xFFFF)
                         for destination in (0, 1, 0xFFFE, 0xFFFF)]
            scenarios += [(16000, 0, 1999, 0), (16000, 1, 2000, 0),
                          (16000, 0, 2033, 32), (16000, 1, 2032, 32)]
            for load in (0x1000, 0x3333):
                for words, destination, paragraphs, busy in scenarios:
                    outputs = [graph_control(x, load, words, destination, paragraphs, busy) for x in (a, b)]
                    assert outputs[0] == outputs[1], (artifact, load, words, destination, paragraphs, busy, outputs)
                    graph_rows.append(dict(load=load, words=words, destination=destination,
                                           paragraphs=paragraphs, busy=busy, outputs=outputs))
        negatives = []
        old_baselines = []
        old_pins = None
        if artifact != "main" and args.old_build:
            old_package = json.loads((args.old_build / "build.json").read_text())
            old_product = old_package["products"][artifact]
            old_exe = args.old_build / old_product["file"]
            assert digest(old_exe) == old_product["sha256"]
            old_receipt = Path(old_product["build_receipt"])
            old_map = product_map(old_receipt, artifact)
            old = linked(old_exe, old_map, artifact)
            old_pins = dict(**old["pins"], build=digest(args.old_build / "build.json"),
                            source_fingerprint=old_package["source_fingerprint"])
            for load in (0x1000, 0x3333):
                for words in (1, 16000):
                    expected = graph_control(a, load, words, 1, 4096, 0)
                    actual = graph_control(old, load, words, 1, 4096, 0)
                    keys = ("ax", "io", "page", "picture")
                    assert all(actual[k] == expected[k] for k in keys), (artifact, load, words)
                    old_baselines.append(dict(load=load, words=words, paragraphs=4096,
                                               original=expected, old=actual))
                for words, paragraphs in ((0, 16), (16000, 2000)):
                    expected = graph_control(a, load, words, 1, paragraphs, 0)
                    actual = graph_control(old, load, words, 1, paragraphs, 0)
                    keys = ("ax", "io", "page", "picture")
                    differences = [k for k in keys if actual[k] != expected[k]]
                    assert differences, (artifact, load, words, actual)
                    negatives.append(dict(load=load, words=words, paragraphs=paragraphs,
                                          original=expected, old=actual, differences=differences))
        result = dict(original_pins=a["pins"], candidate_pins=b["pins"], allocator=rows,
                      page_copy=graph_rows, old_pins=old_pins, old_rejections=negatives,
                      old_baselines=old_baselines)
        with gzip.open(args.output / (artifact + "-controls.json.gz"), "wt") as f:
            json.dump(result, f, sort_keys=True)
        report["artifacts"][artifact] = dict(allocator_controls=len(rows), graph_controls=len(graph_rows),
                                             old_rejections=len(negatives),
                                             old_baselines=len(old_baselines),
                                             transcript_sha256=digest(args.output / (artifact + "-controls.json.gz")))
        print(artifact, report["artifacts"][artifact], flush=True)
    report["memory_blobs"] = {}
    for path in sorted(MEMORY_STORE.glob("*.bin.gz")):
        data = gzip.decompress(path.read_bytes())
        assert hashlib.sha256(data).hexdigest() == path.name[:-7]
        report["memory_blobs"][path.name] = dict(size=len(data), sha256=digest(path))
    report["verifier_sha256"] = digest(Path(__file__))
    (args.output / "receipt.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
