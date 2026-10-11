#!/usr/bin/env python3
"""Compare linked ordinary text writers with retained original MAIN execution."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct

from verify_dos_text_gaiji import (
    Machine, candidate, original, START, END, SEED,
    UC_X86_REG_BP, UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES,
    UC_X86_REG_DI, UC_X86_REG_SI, UC_X86_REG_SP, UC_X86_REG_SS, UC_X86_REG_EFLAGS,
)

ROOT = Path(__file__).resolve().parents[2]
ENTRIES = {"putca": (0x229e, 87), "putsa": (0x22f6, 114)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("incomplete original text transcript")
    return data


class TextMachine(Machine):
    def run(self, row, interrupt):
        kind, x, y, text, attribute, base = row
        cpu = self.cpu
        cpu.mem_write(self.load * 16, self.body)
        ds = self.load + self.layout["dg"]
        cpu.mem_write(ds * 16 + self.layout["textseg"], struct.pack("<H", base))
        raw = bytes.fromhex(text) if kind == "putsa" and text != "-" else b""
        # Give the far string its own RAM segment, beyond the loaded image
        # and below the return trampoline and stack. A dangling lead can
        # consume the first zero; the second zero ends the next iteration.
        assert self.load * 16 + len(self.body) <= 0x65000
        assert 0x65000 + len(raw) + 2 < 0x6f000
        cpu.mem_write(0x65000, raw + b"\0\0")
        cpu.mem_write(START, SEED)
        self.writes = bytearray()
        self.done = False
        cs, ip = self.layout[kind]
        for reg, value in ((UC_X86_REG_CS, self.load + cs), (UC_X86_REG_DS, ds),
                           (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xf000),
                           (UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1234),
                           (UC_X86_REG_DI, 0x5678), (UC_X86_REG_ES, 0x6789),
                           (UC_X86_REG_EFLAGS, 2 | (interrupt << 9))):
            cpu.reg_write(reg, value)
        arguments = (attribute, text, y, x) if kind == "putca" else (attribute, 0, 0x6500, y, x)
        stack = (0, 0x6f00, *(value & 65535 for value in arguments))
        cpu.mem_write(0x7f000, struct.pack("<" + "H" * len(stack), *stack))
        cpu.emu_start((self.load + cs) * 16 + ip, 0xfffff, count=100000000)
        assert self.done and cpu.reg_read(UC_X86_REG_SP) == 0xf000 + len(stack) * 2
        for reg, value in ((UC_X86_REG_BP, 0xabcd), (UC_X86_REG_SI, 0x1234),
                           (UC_X86_REG_DI, 0x5678), (UC_X86_REG_DS, ds)):
            assert cpu.reg_read(reg) == value, (reg, cpu.reg_read(reg), value)
        assert bool(cpu.reg_read(UC_X86_REG_EFLAGS) & 0x200) == bool(interrupt)
        return bytes(cpu.mem_read(START, END - START)), bytes(self.writes), cpu.reg_read(UC_X86_REG_ES)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", choices=("main", "op", "maine"), required=True)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--diagnostic", action="store_true")
    parser.add_argument("--alternate-bases-only", action="store_true")
    args = parser.parse_args()
    reference = original("main")
    reference.update(putca=(0, 0x229e), putsa=(0, 0x22f6), textseg=0x768)
    prior = json.loads((args.reference / "receipt.json").read_text())
    assert prior["passed"] and prior["original"] == reference["pins"]
    assert prior["entries"] == {"putca": "0000:229E", "putsa": "0000:22F6"}
    assert prior["nul_padding"] == 2 and prior["text_segment"] == "2134:0768"
    dependencies = {name: sha((ROOT / name).read_bytes()) for name in
                    ("scripts/runtime/verify_dos_text_gaiji.py",
                     "scripts/runtime/verify_dos_vsync_lifecycle.py", "scripts/lib/pc98.py")}
    assert prior["dos_producers"] == dependencies
    carrier = args.reference / "memory-original.bin.gz"
    assert sha(carrier.read_bytes()) == prior["files"][carrier.name]
    layout = candidate(args.exe, args.map)
    assert struct.unpack_from("<H", layout["body"], layout["dg"] * 16 + layout["textseg"])[0] == 0xa000
    mapping = args.map.read_text()
    selected = ("putca", "putsa") if args.artifact == "main" else ("putca",)
    for kind in selected:
        name = "TEXT_PUTCA" if kind == "putca" else "TEXT_PUTSA"
        hits = set(re.findall(r"(?m)^\s*([0-9A-F]{4}):([0-9A-F]{4})\s+"
                              r"(?:idle\s+)?" + name + r"\s*$", mapping))
        assert len(hits) == 1, (name, hits)
        layout[kind] = tuple(int(value, 16) for value in hits.pop())

    args.output.mkdir(parents=True, exist_ok=False)
    code = {}
    for kind in selected:
        start, length = ENTRIES[kind]
        expected = reference["body"][start:start + length]
        assert expected[19:21] == b"\x03\x3e" and expected[21:23] == b"\x68\x07"
        mapped = bytearray(expected)
        struct.pack_into("<H", mapped, 21, layout["textseg"])
        segment, offset = layout[kind]
        product_start = segment * 16 + offset
        assert not any(start <= site < start + length for site in reference["sites"])
        assert not any(product_start <= site < product_start + length for site in layout["sites"])
        actual = layout["body"][product_start:product_start + length]
        differences = [index for index, pair in enumerate(zip(mapped, actual)) if pair[0] != pair[1]]
        assert len(actual) == length
        assert not differences or args.diagnostic, (kind, differences)
        (args.output / (kind + "-original.bin")).write_bytes(expected)
        (args.output / (kind + "-mapped.bin")).write_bytes(mapped)
        (args.output / (kind + "-product.bin")).write_bytes(actual)
        code[kind] = dict(original_entry=[0, start], product_entry=list(layout[kind]),
                          length=length, mapped_operand=21, original_data_offset=0x768,
                          product_data_offset=layout["textseg"], differences=differences,
                          original_sha256=sha(expected), mapped_sha256=sha(mapped),
                          product_sha256=sha(actual))

    rows = prior["rows"]
    assert len(rows) == 840 and len(prior["controls"]) == 1680
    controls, differences = [], []
    with gzip.open(carrier, "rb") as stream:
        for load_index, load in enumerate((0x1000, 0x3333)):
            machine = TextMachine(layout, load)
            target = TextMachine(reference, load)
            with gzip.open(args.output / f"transcripts-{load:04x}.bin.gz", "wb", compresslevel=1) as output:
                for index, row in enumerate(rows):
                    saved = prior["controls"][load_index * len(rows) + index]
                    assert saved["load"] == f"{load:04x}" and saved["index"] == index
                    expected_memory = read(stream, END - START)
                    count = struct.unpack("<I", read(stream, 4))[0]
                    assert count == saved["write_bytes"] and count % 10 == 0
                    expected_writes = read(stream, count)
                    expected_es = struct.unpack("<H", read(stream, 2))[0]
                    assert sha(expected_memory) == saved["memory_sha256"]
                    assert sha(expected_writes) == saved["writes_sha256"] and expected_es == saved["es"]
                    if row[0] not in selected or (args.alternate_bases_only and row[5] == 0xa000):
                        continue
                    expected = (expected_memory, expected_writes, expected_es)
                    assert target.run(row, index & 1) == expected, ("original reference differs", load, index)
                    actual = machine.run(row, index & 1)
                    equal = expected == actual
                    if not equal:
                        detail = dict(load=f"{load:04x}", index=index,
                                      memory_bytes=sum(a != b for a, b in zip(expected[0], actual[0])),
                                      writes_equal=expected[1] == actual[1], es_equal=expected[2] == actual[2])
                        differences.append(detail)
                        assert args.diagnostic, detail
                    for result in (expected, actual):
                        for data in result[:2]:
                            output.write(struct.pack("<I", len(data)) + data)
                    controls.append(dict(load=f"{load:04x}", index=index, input=row, equal=equal,
                                         original=[sha(data) for data in expected[:2]],
                                         candidate=[sha(data) for data in actual[:2]],
                                         original_es=expected[2], candidate_es=actual[2]))
            print(args.artifact, f"{load:04x}", sum(c["load"] == f"{load:04x}" for c in controls),
                  "checked", flush=True)
        assert not stream.read(1)
    sources = ("src/shared/runtime/text_putca_large.asm", "src/main/hardware/text_putsa.asm",
               "src/shared/hardware/gaiji_text.cpp", "scripts/runtime/verify_dos_text_character.py")
    receipt = dict(passed=not differences and not any(c["differences"] for c in code.values()),
                   diagnostic=args.diagnostic, artifact=args.artifact, oracle_artifact="th04-main",
                   string_segment=0x6500, string_offset=0, nul_padding=2,
                   original=reference["pins"], candidate=layout["pins"], code=code, controls=controls,
                   differences=differences, reference_receipt_sha256=sha((args.reference / "receipt.json").read_bytes()),
                   original_carrier_sha256=sha(carrier.read_bytes()), dependencies=dependencies,
                   sources={name: sha((ROOT / name).read_bytes()) for name in sources},
                   files={p.name: sha(p.read_bytes()) for p in args.output.iterdir()})
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("DOS ordinary text", args.artifact, len(controls),
          "PASS" if receipt["passed"] else f"{len(differences)} controls differ", flush=True)


if __name__ == "__main__":
    main()
