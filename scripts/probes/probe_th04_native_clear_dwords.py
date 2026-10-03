#!/usr/bin/env python3
"""Replay CLEAR_DWORDS with independently seeded upper EAX bits.

This CPU diagnostic uses attested executable instructions and synthetic memory.
It does not emulate PC-98 graphics or accept a complete gameplay route.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_16
import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
from unicorn.x86_const import (
    UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_SS, UC_X86_REG_SP,
    UC_X86_REG_DI, UC_X86_REG_EAX, UC_X86_REG_EFLAGS,
)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402

COUNTS = (0x132, 0x200, 0x180, 0xB2C, 0xD0, 0x28, 0xA0, 0x640, 0xA8)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--expect-native-zero", action="store_true")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists() or not out.is_relative_to(ROOT / ".analysis"):
        parser.error("output must be a new private directory")
    target = ROOT / ".analysis/targets/th04/main.exe"
    native = args.build_dir.resolve() / "MAIN.EXE"
    manifest = json.loads((native.parent / "build.json").read_text())
    receipt = Path(manifest["products"]["main"]["build_receipt"])
    build = json.loads(receipt.read_text())
    map_path = receipt.parent / "source" / build["link"]["map"]
    assert target.stat().st_size == 156258
    assert sha(target) == "077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b"
    assert sha(native) == manifest["products"]["main"]["sha256"]
    assert sha(map_path) == build["link"]["map_sha256"]
    assert parse_mz(target.read_bytes()).valid and parse_mz(native.read_bytes()).valid
    entries = {}
    for line in map_path.read_text().splitlines():
        m = re.match(r"^\s*([\dA-Fa-f]{4}):([\dA-Fa-f]{4})\s+(?:idle\s+)?(.*)$", line)
        if m:
            entries[m[3]] = (int(m[1], 16), int(m[2], 16))
    nseg, noff = entries["CLEAR_DWORDS"]
    decoder = Cs(CS_ARCH_X86, CS_MODE_16)
    helpers = {}
    for kind, path, segment, offset in (
        ("target", target, 0x0AAF, 0x185E),
        ("native", native, nseg, noff),
    ):
        data = path.read_bytes()
        header = struct.unpack_from("<H", data, 8)[0] * 16
        start = header + segment * 16 + offset
        instructions = []
        for insn in decoder.disasm(data[start:start + 40], offset):
            instructions.append(insn)
            if insn.mnemonic == "ret":
                break
        assert instructions[-1].mnemonic == "ret" and instructions[-1].op_str == "4"
        size = sum(i.size for i in instructions)
        helpers[kind] = data[start:start + size]
    results = []
    for kind, code in helpers.items():
        for high in (0, 0x000E, 0xDEAD):
            for count in COUNTS:
                u = Uc(UC_ARCH_X86, UC_MODE_16)
                u.mem_map(0, 0x100000)
                u.mem_write(0x20000, code)
                u.mem_write(0x7E000, struct.pack("<HHH", 0x100, count, 0x2000))
                u.mem_write(0x81FFC, b"\xA5" * (count * 4 + 8))
                for reg, value in (
                    (UC_X86_REG_CS, 0x2000), (UC_X86_REG_DS, 0x8000),
                    (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xE000),
                    (UC_X86_REG_DI, 0x1357), (UC_X86_REG_EFLAGS, 2),
                    (UC_X86_REG_EAX, (high << 16) | 0xBEEF),
                ):
                    u.reg_write(reg, value)
                stopped = []

                def stop(vm, address, size, _):
                    if address == 0x20100:
                        stopped.append(True)
                        vm.emu_stop()

                u.hook_add(UC_HOOK_CODE, stop)
                u.emu_start(0x20000, 0x20101, count=count + 50)
                assert stopped and u.reg_read(UC_X86_REG_SP) == 0xE006
                assert u.reg_read(UC_X86_REG_DI) == 0x1357
                assert bytes(u.mem_read(0x81FFC, 4)) == b"\xA5" * 4
                assert bytes(u.mem_read(0x82000 + count * 4, 4)) == b"\xA5" * 4
                filled = bytes(u.mem_read(0x82000, count * 4))
                assert filled in (bytes(count * 4), struct.pack("<I", high << 16) * count)
                if kind == "target":
                    assert filled == struct.pack("<I", high << 16) * count
                if kind == "native" and args.expect_native_zero:
                    assert filled == bytes(count * 4)
                results.append(dict(artifact=kind,upper_eax=high,dwords=count,
                                    fill_dword=int.from_bytes(filled[:4], "little"),
                                    fill_sha256=hashlib.sha256(filled).hexdigest()))
    engine = Path(unicorn.unicorn._uc._name).resolve()
    report = dict(observed_utc=datetime.now(timezone.utc).isoformat(),
                  scope="bounded synthetic CPU control; no full-game or exact promotion",
                  target_sha256=sha(target),native_sha256=sha(native),map_sha256=sha(map_path),
                  script_sha256=sha(Path(__file__)),unicorn_version=unicorn.__version__,
                  unicorn_engine_sha256=sha(engine),
                  native_entry=[nseg,noff],target_entry=[0x0AAF,0x185E],
                  helper_bytes_equal=helpers["target"] == helpers["native"],
                  results=results)
    out.mkdir(parents=True)
    (out / "receipt.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(receipt=str(out / "receipt.json"),cases=len(results),
                         helper_bytes_equal=report["helper_bytes_equal"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
