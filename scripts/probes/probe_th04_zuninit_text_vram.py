#!/usr/bin/env python3
"""Replay ZUNINIT's target text writer on its seven embedded messages."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import unicorn
from unicorn import UC_ARCH_X86, UC_HOOK_MEM_WRITE, UC_MODE_16, Uc
from unicorn.x86_const import (
    UC_X86_REG_AX, UC_X86_REG_BX, UC_X86_REG_CS, UC_X86_REG_CX,
    UC_X86_REG_DI, UC_X86_REG_DS, UC_X86_REG_DX, UC_X86_REG_EFLAGS,
    UC_X86_REG_ES, UC_X86_REG_SP, UC_X86_REG_SS,
)


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/probes"))
from replay_th04_zun_source_only import PAYLOAD, PAYLOAD_SHA256  # noqa: E402

COMPONENT_START = 0x6F3
COMPONENT_SIZE = 0x475
COMPONENT_SHA256 = "692b1e056d907a9649bd1effa6e83239f71039d17de3569464067d0b42b7aa5e"
TEXT_RUNTIME_START = 0x1CF
TEXT_RUNTIME_END = 0x20A
TEXT_SHA256 = "0c5a90f8b85153d3c668f033651cddedbe2a635e2cfdcf8345e4ec5f8f8c6fb6"
STRINGS_START = 0x217
STRINGS_END = 0x30C
CS = 0x1000
CHAR_VRAM = 0xA0000
ATTR_VRAM = 0xA2000


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def messages(component: bytes) -> list[tuple[int, bytes]]:
    data = component[STRINGS_START - 0x100:STRINGS_END - 0x100]
    parts = data.split(b"$")
    if len(parts) != 8 or parts[-1] != b"" or any(len(part) != 34 for part in parts[:-1]):
        raise RuntimeError("ZUNINIT target text data partition drift")
    result = []
    position = STRINGS_START
    for part in parts[:-1]:
        result.append((position, part))
        position += len(part) + 1
    if position != STRINGS_END:
        raise RuntimeError("ZUNINIT target text data end drift")
    return result


def expected_writes(message: bytes, row_offset: int) -> list[tuple[int, int, int]]:
    chars = []
    for index in range(0, len(message), 2):
        pair = message[index:index + 2]
        try:
            euc = pair.decode("shift_jis").encode("euc_jp")
        except UnicodeError as exc:
            raise RuntimeError(f"target message pair is outside strict Shift-JIS: {pair.hex()}") from exc
        if len(euc) != 2 or not all(0xA1 <= byte <= 0xFE for byte in euc):
            raise RuntimeError(f"target message pair is outside JIS X 0208: {pair.hex()}")
        row, cell = euc[0] - 0x80, euc[1] - 0x80
        glyph_low = (cell << 8) | ((row - 0x20) & 0xFF)
        chars.append(glyph_low)
        chars.append(glyph_low | 0x8000)
    character_writes = [
        (CHAR_VRAM + row_offset + index * 2, 2, value)
        for index, value in enumerate(chars)
    ]
    attribute_writes = [
        (ATTR_VRAM + row_offset + index * 2, 2, 0x0041)
        for index in range(len(chars))
    ]
    return character_writes + attribute_writes


def replay(component: bytes, string_offset: int, message: bytes, row_offset: int) -> dict[str, object]:
    emulator = Uc(UC_ARCH_X86, UC_MODE_16)
    emulator.mem_map(CS << 4, 0x10000)
    emulator.mem_map(0x20000, 0x10000)
    emulator.mem_map(CHAR_VRAM, 0x4000)
    emulator.mem_write((CS << 4) + 0x100, component)
    emulator.reg_write(UC_X86_REG_CS, CS)
    emulator.reg_write(UC_X86_REG_DS, 0x2000)
    emulator.reg_write(UC_X86_REG_SS, 0x2000)
    emulator.reg_write(UC_X86_REG_SP, 0xFFFE)
    emulator.reg_write(UC_X86_REG_AX, row_offset)
    emulator.reg_write(UC_X86_REG_DX, string_offset)
    emulator.reg_write(UC_X86_REG_EFLAGS, 2)
    actual_writes: list[tuple[int, int, int]] = []

    def trace(_emulator: Uc, _access: int, address: int, size: int, value: int, _user: object) -> None:
        if CHAR_VRAM <= address < CHAR_VRAM + 0x4000:
            actual_writes.append((address, size, value))

    emulator.hook_add(UC_HOOK_MEM_WRITE, trace)
    emulator.emu_start((CS << 4) + TEXT_RUNTIME_START, (CS << 4) + TEXT_RUNTIME_END - 1)
    expected = expected_writes(message, row_offset)
    if actual_writes != expected:
        for index, (actual, wanted) in enumerate(zip(actual_writes, expected)):
            if actual != wanted:
                raise RuntimeError(f"message {string_offset:#x} VRAM write {index}: {actual} != {wanted}")
        raise RuntimeError(f"message {string_offset:#x} VRAM write count drift")
    if (
        emulator.reg_read(UC_X86_REG_BX) != string_offset + len(message)
        or emulator.reg_read(UC_X86_REG_CX) != 0
        or emulator.reg_read(UC_X86_REG_DX) != row_offset
        or emulator.reg_read(UC_X86_REG_DI) != row_offset + len(message) * 2
        or emulator.reg_read(UC_X86_REG_ES) != 0xA200
    ):
        raise RuntimeError(f"message {string_offset:#x} register end-state drift")
    span = len(message) * 2
    chars = bytes(emulator.mem_read(CHAR_VRAM + row_offset, span))
    attributes = bytes(emulator.mem_read(ATTR_VRAM + row_offset, span))
    if chars != b"".join(value.to_bytes(2, "little") for _, _, value in expected[:len(message)]):
        raise RuntimeError("character VRAM bytes differ from independent reference")
    if attributes != b"\x41\x00" * len(message):
        raise RuntimeError("attribute VRAM bytes differ from independent reference")
    trace_bytes = json.dumps(actual_writes, separators=(",", ":")).encode()
    return {
        "string_runtime_offset": f"0x{string_offset:X}",
        "row_vram_offset": f"0x{row_offset:X}",
        "message_sha256": sha(message),
        "shift_jis_pairs": len(message) // 2,
        "vram_write_count": len(actual_writes),
        "write_trace_sha256": sha(trace_bytes),
        "character_vram_sha256": sha(chars),
        "attribute_vram_sha256": sha(attributes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    private = (ROOT / ".analysis/reconstruction/probes").resolve()
    if output.exists() or output.parent != private:
        parser.error("output directory must be new directly below .analysis/reconstruction/probes")
    preflight = subprocess.run(
        [sys.executable, "scripts/preflight.py"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    )
    payload = PAYLOAD.read_bytes()
    if sha(payload) != PAYLOAD_SHA256:
        raise RuntimeError("decoded ZUN payload identity drift")
    component = payload[COMPONENT_START:COMPONENT_START + COMPONENT_SIZE]
    if len(component) != COMPONENT_SIZE or sha(component) != COMPONENT_SHA256:
        raise RuntimeError("ZUNINIT component identity drift")
    body = component[TEXT_RUNTIME_START - 0x100:TEXT_RUNTIME_END - 0x100]
    if len(body) != 0x3B or sha(body) != TEXT_SHA256 or body[-1] != 0xC3:
        raise RuntimeError("ZUNINIT text writer extent/identity drift")

    positions = (0x650, 0x6F0, 0x790)
    scenarios = [
        replay(component, offset, message, row)
        for offset, message in messages(component)
        for row in positions
    ]
    unicorn_binary = Path(unicorn.__file__).parent / "lib/libunicorn.so"
    if not unicorn_binary.is_file():
        raise RuntimeError("Unicorn binary path is unavailable")
    receipt = {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim": "ZUNINIT text writer renders its seven embedded Shift-JIS messages into PC-98 character/attribute VRAM",
        "target_payload_sha256": PAYLOAD_SHA256,
        "target_component_sha256": COMPONENT_SHA256,
        "target_extent": "th04-zun/com-payload/0x7C2+0x3B",
        "target_slice_sha256": TEXT_SHA256,
        "probe_source_sha256": sha(Path(__file__).read_bytes()),
        "emulator": {
            "name": "Unicorn x86 16-bit",
            "version": unicorn.__version__,
            "binary_sha256": sha(unicorn_binary.read_bytes()),
            "cs": "0x1000",
            "ds_ss": "0x2000",
            "initial_sp": "0xFFFE",
            "initial_eflags": "0x2",
            "initial_vram": "zero",
            "stop": "before RET at ZUNINIT runtime COM offset 0x209",
        },
        "reference": "strict shift_jis/euc_jp JIS row/cell, PC-98 two-word character plane, 0x0041 attribute plane",
        "python": sys.version.split()[0],
        "scenarios": scenarios,
        "preflight_stdout_sha256": sha(preflight.stdout.encode()),
        "limit": "Runtime behavior only; no original source, linked component, or exact byte acceptance follows.",
    }
    output.mkdir()
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"messages": len(scenarios), "pairs": sum(row["shift_jis_pairs"] for row in scenarios), "vram_writes": sum(row["vram_write_count"] for row in scenarios)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
