#!/usr/bin/env python3
"""Replay bounded MAIN initialization, backdrop addresses and slowdown policy.

Requires Capstone and Unicorn. This diagnostic executes original instructions
with synthetic state; it does not emulate PC-98 graphics or a complete route.
"""

import argparse
import unicorn
import sys
from pathlib import Path
import hashlib
import json
import re
import struct
from datetime import datetime, timezone
from capstone import Cs, CS_ARCH_X86, CS_MODE_16
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.x86_const import (
    UC_X86_REG_CS,
    UC_X86_REG_IP,
    UC_X86_REG_DS,
    UC_X86_REG_SS,
    UC_X86_REG_SP,
    UC_X86_REG_BP,
    UC_X86_REG_EFLAGS,
)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.pc98 import parse_mz  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    OUT = args.output_dir.resolve()
    if OUT.exists() or not OUT.is_relative_to(ROOT / ".analysis"):
        parser.error("output must be a new private directory")
    TARGET = ROOT / ".analysis/targets/th04/main.exe"
    NATIVE = args.build_dir.resolve() / "MAIN.EXE"
    MANIFEST = json.loads((NATIVE.parent / "build.json").read_text())
    RECEIPT = Path(MANIFEST["products"]["main"]["build_receipt"])
    R = json.loads(RECEIPT.read_text())
    MAP = RECEIPT.parent / "source" / R["link"]["map"]
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert (
        sha(TARGET)
        == "077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b"
        and TARGET.stat().st_size == 156258
    )
    assert (
        sha(NATIVE) == MANIFEST["products"]["main"]["sha256"]
        and sha(MAP) == R["link"]["map_sha256"]
    )
    assert parse_mz(TARGET.read_bytes()).valid and parse_mz(NATIVE.read_bytes()).valid
    OUT.mkdir(parents=True)
    c = Cs(CS_ARCH_X86, CS_MODE_16)
    entries = {}
    for line in MAP.read_text().splitlines():
        m = re.match(r"^\s*([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+(?:idle\s+)?(.*)$", line)
        if m:
            entries[m[3]] = tuple(int(m[x], 16) for x in (1, 2))

    def load(path):
        d = path.read_bytes()
        h = struct.unpack_from("<H", d, 8)[0] * 16
        return d[h:]

    modules = {"target": load(TARGET), "native": load(NATIVE)}

    def addr(name):
        seg, off = entries[name]
        return seg * 16 + off

    def vm(kind, entry):
        u = Uc(UC_ARCH_X86, UC_MODE_16)
        u.mem_map(0, 0x110000)
        u.mem_write(0x20000, modules[kind])
        u.reg_write(UC_X86_REG_CS, 0x2000 + (entry // 65536) * 4096)
        u.reg_write(UC_X86_REG_IP, entry % 65536)
        for reg, val in [
            (UC_X86_REG_DS, 0x8000),
            (UC_X86_REG_SS, 0x7000),
            (UC_X86_REG_SP, 0xE000),
            (UC_X86_REG_BP, 0xD000),
            (UC_X86_REG_EFLAGS, 2),
        ]:
            u.reg_write(reg, val)
        return u

    fields = {
        "target": {"previous": 0x3DBE, "current": 0x3DC4, "row": 0x3DC0},
        "native": {
            "previous": entries["_byte_250FE"][1],
            "current": entries["_byte_25104"][1],
            "row": entries["_word_25100"][1],
        },
    }
    semantic = {
        name: entries[s][1]
        for name, s in [
            ("previous", "_scroll_row_advance_previous"),
            ("current", "_scroll_row_advance_current"),
            ("row", "_tile_ring_scroll_row_prev"),
        ]
    }
    state_symbols = [
        "_byte_250FE",
        "_byte_25104",
        "_word_25100",
        "_scroll_row_advance_previous",
        "_scroll_row_advance_current",
        "_tile_ring_scroll_row_prev",
    ]
    assert len({entries[name][0] for name in state_symbols}) == 1
    state = []
    for kind, start, end in [
        ("target", 0xB1D6, 0xB208),
        (
            "native",
            addr("stage_runtime_init()") + 6,
            addr("stage_runtime_init()") + 0x38,
        ),
    ]:
        u = vm(kind, start)
        for name, offset in fields[kind].items():
            u.mem_write(
                0x80000 + offset, bytes.fromhex("FECA") if name == "row" else b"\xa5"
            )
        if kind == "native":
            for name, offset in semantic.items():
                u.mem_write(
                    0x80000 + offset,
                    bytes.fromhex("FECA") if name == "row" else b"\xa5",
                )
        stopped = []

        def stop(u, address, size, data):
            if address == 0x20000 + end:
                stopped.append(True)
                u.emu_stop()

        u.hook_add(UC_HOOK_CODE, stop)
        u.emu_start(0x20000 + start, 0x20000 + end + 1, count=100)
        assert stopped
        actual = {
            name: int.from_bytes(
                u.mem_read(0x80000 + offset, 2 if name == "row" else 1), "little"
            )
            for name, offset in fields[kind].items()
        }
        result = {
            "artifact": kind,
            "load_segment": "2000",
            "ds": "8000",
            "start_load_offset": hex(start),
            "stop_load_offset": hex(end),
            "driver_fields_after_init": actual,
        }
        if kind == "native":
            result["separate_semantic_fields_after_init"] = {
                name: int.from_bytes(
                    u.mem_read(0x80000 + offset, 2 if name == "row" else 1), "little"
                )
                for name, offset in semantic.items()
            }
        if kind == "target":
            assert actual == {"previous": 0, "current": 0, "row": 0}
        state.append(result)
    # Replay only the unchanged backdrop producer; ordinary RAM hooks measure its
    # addresses, not GRCG colors, PC-98 page selection or display-scroll effects.
    coverage = []
    for kind, entry in [
        ("target", 0xBEDA),
        ("native", addr("reimu_marisa_backdrop_colorfill()")),
    ]:
        u = vm(kind, entry)
        writes = set()
        stopped = []

        def mem(u, access, address, size, value, data):
            if 0xA8000 <= address < 0xA8000 + 32000:
                writes.update(range(address - 0xA8000, address - 0xA8000 + size))

        def stop(u, address, size, data):
            if address == 0x20000 + entry + 58:
                stopped.append(True)
                u.emu_stop()

        u.hook_add(UC_HOOK_MEM_WRITE, mem)
        u.hook_add(UC_HOOK_CODE, stop)
        u.emu_start(0x20000 + entry, 0x20000 + entry + 59, count=20000)
        assert stopped
        expected = {
            y * 80 + x
            for y in range(16, 384)
            for x in range(4, 52)
            if y < 72 or y >= 328 or x < 12 or x >= 44
        }
        assert writes == expected
        coverage.append(
            {
                "artifact": kind,
                "load_segment": "2000",
                "entry_load_offset": hex(entry),
                "write_bytes": len(writes),
                "top_16_playfield_rows_fully_written": all(
                    y * 80 + x in writes for y in range(16, 32) for x in range(4, 52)
                ),
            }
        )
    # Execute the threshold-control branch from each binary with explicit inputs.
    policies = {}
    for kind, entry in [("target", 0x1C8C8), ("native", addr("bullets_update()"))]:
        ins = list(c.disasm(modules[kind][entry : entry + 0x36B], entry))
        j = next(
            j
            for j, i in enumerate(ins)
            if i.mnemonic == "mov" and i.op_str == "di, 0x18"
        )
        seq = ins[j - 2 : j + 18]
        start = seq[0].address
        finish = ins[j + 18].address
        stores = [i for i in seq if i.mnemonic == "mov" and i.op_str.endswith(", 2")]
        assert len(stores) == 1

        def absolute(i):
            return int(re.search(r"\[(0x[0-9a-f]+)\]", i.op_str)[1], 16)

        offs = {
            "turbo": absolute(seq[0]),
            "perf": absolute(ins[j + 1]),
            "rank": absolute(ins[j + 4]),
            "parity": absolute(ins[j + 10]),
            "slowdown": absolute(stores[0]),
        }

        def outside(u, a, size, data):
            if not 0x20000 + start <= a < 0x20000 + finish:
                u.emu_stop()

        observed = []
        for turbo in [0, 1]:
            for rank in range(4):
                for perf in [0, 21]:
                    threshold = 24 + perf + 8 * rank
                    for count in [threshold - 1, threshold, threshold + 24]:
                        for parity in [0, 1]:
                            u = vm(kind, start)
                            for name, value in [
                                ("turbo", turbo),
                                ("rank", rank),
                                ("perf", perf),
                                ("parity", parity),
                            ]:
                                u.mem_write(0x80000 + offs[name], bytes([value]))
                            u.mem_write(0x80000 + offs["slowdown"], b"\x01\x00")
                            u.mem_write(0x70000 + 0xD000 - 2, struct.pack("<H", count))
                            u.hook_add(UC_HOOK_CODE, outside)
                            u.emu_start(0x20000 + start, 0x110000, count=100)
                            got = int.from_bytes(
                                u.mem_read(0x80000 + offs["slowdown"], 2), "little"
                            )
                            expected = (
                                2
                                if not turbo and count >= threshold and parity == 0
                                else 1
                            )
                            assert got == expected, (
                                kind,
                                turbo,
                                rank,
                                perf,
                                count,
                                parity,
                                got,
                                expected,
                            )
                            observed.append(got)
        policies[kind] = {
            "start_load_offset": hex(start),
            "ds_offsets": {k: hex(v) for k, v in offs.items()},
            "case_count": len(observed),
            "results": observed,
        }
    assert policies["target"]["results"] == policies["native"]["results"]
    result = {
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target_sha256": sha(TARGET),
        "native_sha256": sha(NATIVE),
        "map_sha256": sha(MAP),
        "unicorn_version": unicorn.__version__,
        "unicorn_engine_sha256": sha(Path(unicorn.unicorn._uc._name)),
        "native_state_symbols": {
            name: "%04X:%04X" % entries[name] for name in state_symbols
        },
        "unicorn_scope": "CPU-only isolated prefixes/producer; no PC-98 GRCG emulation, GDC timing, current user memory or full visual replay",
        "state_init": state,
        "backdrop_address_coverage": coverage,
        "slowdown_policy": policies,
        "confirmed_native_duplicate_state": any(
            fields["native"][name] != semantic[name] for name in semantic
        ),
        "native_driver_state_reset": all(
            value == 0 for value in state[1]["driver_fields_after_init"].values()
        ),
        "probe_sha256": sha(Path(__file__)),
        "module_handling": "Nonrelocated copies at load segment 2000; executed prefixes skip callees and contain no used relocation operands. Synthetic DS=8000 and SS=7000.",
        "top_stripe_root_cause": "Unconfirmed by this isolated diagnostic; inspect actual display-scroll and page state in a full original/native route.",
    }
    (OUT / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: result[k]
                for k in [
                    "state_init",
                    "backdrop_address_coverage",
                    "confirmed_native_duplicate_state",
                    "top_stripe_root_cause",
                ]
            }
        )
    )
    print("slowdown target/native cases", policies["target"]["case_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
