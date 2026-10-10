"""Read-only host-RAM walker for the ELF-attested x86_64 DOS demo observer.

The callback reads inferior memory. It never calls an emulator guest accessor
or changes page-table accessed bits. CPUBlock/PagingBlock offsets are restricted
to the existing pinned observer's config.h (Bitu=uintptr_t).
"""
from __future__ import annotations


class HostRam:
    def __init__(self, read, symbols: dict[str, int]):
        self.read = read
        self.symbols = symbols

    def integer(self, pointer: int, size: int) -> int:
        data = bytes(self.read(pointer, size))
        if len(data) != size:
            raise ValueError('short host memory read')
        return int.from_bytes(data, 'little')

    def state(self) -> tuple[int, int, int, int]:
        return (self.integer(self.symbols['MemBase'], 8),
                self.integer(self.symbols['cpu']+16, 8),
                self.integer(self.symbols['cpu']+24, 8),
                self.integer(self.symbols['paging'], 8))

    def physical(self, linear: int, state=None) -> int:
        if not 0 <= linear < 0xa0000:
            raise ValueError('logical read outside conventional RAM')
        base, cr0, cr4, cr3 = self.state() if state is None else state
        if not cr0 & 0x80000000:
            return linear
        if cr4 & 0x20:
            raise ValueError('PAE outside observer contract')
        entry = self.integer(base+(cr3 & 0xfffff000)+(linear >> 22)*4, 4)
        if not entry & 1:
            raise ValueError('absent page directory')
        if entry & 0x80:
            return (entry & 0xffc00000)+(linear & 0x3fffff)
        entry = self.integer(base+(entry & 0xfffff000)+((linear >> 12)&1023)*4, 4)
        if not entry & 1:
            raise ValueError('absent page')
        return (entry & 0xfffff000)+(linear & 4095)

    def read_range(self, start: int, size: int):
        if size <= 0 or start < 0 or start+size > 0xa0000:
            raise ValueError('range outside conventional RAM')
        state = self.state()
        base = state[0]
        result = bytearray()
        pages = {}
        while len(result) < size:
            linear = start+len(result)
            physical = self.physical(linear, state)
            length = min(size-len(result), 4096-(linear & 4095))
            if not (0 <= physical and physical+length <= 16*1024*1024
                    and not (physical < 0x100000 and physical+length > 0xa0000)):
                raise ValueError('physical read outside ordinary RAM')
            pages[str(linear & ~4095)] = physical & ~4095
            data = bytes(self.read(base+physical, length))
            if len(data) != length:
                raise ValueError('short mapped memory read')
            result.extend(data)
        if len(result) != size:
            raise ValueError('short mapped memory read')
        return bytes(result), pages, state
