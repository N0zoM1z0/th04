#!/usr/bin/env python3
"""Build the flat TH04 ZUN launcher payload from explicit component inputs."""

from __future__ import annotations

import argparse
from pathlib import Path
import struct

NAMES = (b"-O", b"-I", b"-S", b"-M")
COPYRIGHT = b"comcstm (c)O.Morikawa 1996"
TIMESTAMP = 621381155
DIRECTORY_SIZE = 2 + 32 * 8 + 33 * 2 + 3


def word(value: int) -> bytes:
    if not 0 <= value <= 0xFFFF:
        raise ValueError(f"ZUN COM offset/length outside 16-bit range: {value}")
    return struct.pack("<H", value)


def directory(selector_size: int, component_sizes: tuple[int, ...]) -> bytes:
    if len(component_sizes) != len(NAMES) or any(size <= 0 for size in component_sizes):
        raise ValueError("ZUN directory requires four nonempty COM components")
    names = b"".join(name.ljust(8, b" ") for name in NAMES).ljust(32 * 8, b" ")
    first = 0x100 + selector_size + DIRECTORY_SIZE
    entries = [first]
    for size in component_sizes:
        entries.append(entries[-1] + size)
    table = b"".join(word(value) for value in entries)
    table += b"\0" * ((33 - len(entries)) * 2)
    mover_call = b"\xE8" + word(entries[-1] - first)
    result = word(len(NAMES)) + names + table + mover_call
    if len(result) != DIRECTORY_SIZE:
        raise AssertionError("ZUN directory size drift")
    return result


def flat_payload(
    usage: bytes, selector: bytes, components: tuple[bytes, ...],
    moveup: bytes, customization: bytes,
) -> tuple[bytes, dict[str, bytes]]:
    if len(components) != len(NAMES):
        raise ValueError("four ZUN components are required")
    if len(selector) != 223 or len(moveup) != 8 or len(customization) != 68:
        raise ValueError("launcher stub size drift")
    generated_directory = directory(len(selector), tuple(map(len, components)))
    inner = selector + generated_directory + b"".join(components) + moveup
    header_size = 3 + 2 + 2 + 2 + 4 + len(COPYRIGHT)
    usage_offset = 0x100 + header_size
    header = (
        b"\xE9" + word(header_size + len(usage) + len(inner) - 3)
        + word(usage_offset) + word(len(usage)) + word(len(inner))
        + struct.pack("<I", TIMESTAMP) + COPYRIGHT
    )
    if len(header) != header_size:
        raise AssertionError("COMCSTM header size drift")
    result = header + usage + inner + customization
    return result, {"header": header, "directory": generated_directory, "inner": inner}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("usage", "selector", "ongchk", "zuninit", "resident", "memchk", "moveup", "customization"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result, _parts = flat_payload(
        args.usage.read_bytes(), args.selector.read_bytes(),
        tuple(getattr(args, name).read_bytes() for name in ("ongchk", "zuninit", "resident", "memchk")),
        args.moveup.read_bytes(), args.customization.read_bytes(),
    )
    args.output.write_bytes(result)
    print(f"wrote {args.output}: {len(result)} flat bytes")


if __name__ == "__main__":
    main()
