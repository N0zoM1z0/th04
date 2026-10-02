set pagination off
set confirm off
set disable-randomization off
handle SIG33 nostop noprint pass
python
import os
import pathlib
import json
import gdb

debug = os.environ["TH04_CPU_DEBUG_FILE"]
gdb.execute('symbol-file "' + debug.replace('"', '\\"') + '"')

class Th04CpuFault(gdb.Breakpoint):
    count = 0

    def stop(self):
        vector = int(gdb.parse_and_eval("$rdi"))
        if vector not in (0, 6) or self.count >= 32:
            return False
        registers = gdb.parse_and_eval("cpu_regs")
        segments = gdb.parse_and_eval("Segs")
        word = lambda index: int(registers["regs"][index]["word"][0])
        segment = lambda index: int(segments["val"][index]) & 0xffff
        cs, ss, ds, es = (segment(index) for index in (1, 2, 3, 0))
        ip, sp = int(registers["ip"]["word"][0]), word(4)
        values = [cs, ip, ss, sp, ds, es, word(0), word(3), word(1), word(2),
                  word(6), word(7), word(5)]
        gdb.write("TH04_CPUFAULT %d %02X %s %08X\n" % (
            self.count, vector, " ".join("%04X" % v for v in values), int(registers["flags"])))
        base = int(gdb.parse_and_eval("MemBase"))
        vm86 = bool(int(registers["flags"]) & 0x20000)
        cr0 = int(gdb.parse_and_eval("cpu.cr0"))
        cr3 = int(gdb.parse_and_eval("paging.cr3"))
        # LTO discards the variable's DWARF location, but preserves its 120-byte
        # BSS object and complete type in this build-ID-pinned primary binary.
        memory = gdb.parse_and_eval("(MemoryBlock *)&'_ZL6memory.lto_priv.0'").dereference()
        if memory.type.sizeof != 120:
            raise ValueError("primary MemoryBlock layout changed")
        ram = int(memory["pages"]) * 4096
        alias = int(memory["mem_alias_pagemask_active"])
        inferior = gdb.selected_inferior()

        def physical_read(address, size):
            address = ((address >> 12) & alias) * 4096 + (address & 4095)
            if address + size > ram or (address < 0x100000 and address + size > 0xa0000):
                raise ValueError("snapshot physical range is not ordinary RAM")
            return bytes(inferior.read_memory(base + address, size))

        def physical_address(linear):
            if not cr0 & 0x80000000:
                return linear
            if int(gdb.parse_and_eval("cpu.cr4")) & 0x20:
                raise ValueError("PAE paging is outside this DOS observer")
            directory = int.from_bytes(physical_read((cr3 & 0xfffff000) + (linear >> 22) * 4, 4), "little")
            if not directory & 1:
                raise ValueError("snapshot directory entry is not present")
            if directory & 0x80:
                return (directory & 0xffc00000) + (linear & 0x3fffff)
            entry = int.from_bytes(physical_read((directory & 0xfffff000) + ((linear >> 12) & 1023) * 4, 4), "little")
            if not entry & 1:
                raise ValueError("snapshot page entry is not present")
            return (entry & 0xfffff000) + (linear & 4095)

        mappings = {}
        def linear_read(start, size):
            data = bytearray()
            while len(data) < size:
                linear = start + len(data)
                physical = physical_address(linear)
                length = min(size - len(data), 4096 - (linear & 4095))
                mappings["%05X" % (linear & ~4095)] = physical & ~4095
                data.extend(physical_read(physical, length))
            return data

        if not bool(gdb.parse_and_eval("cpu.pmode")) or vm86:
            directory = pathlib.Path(os.environ["TH04_CPU_FAULT_DIR"])
            try:
                for name, start, size in (("code", cs * 16 + ip, 64),
                                          ("stack", ss * 16 + sp, 64), ("data", ds * 16, 65536)):
                    if start + size <= 0xa0000:
                        data = linear_read(start, size)
                        (directory / ("cpu-fault-%02d-%s.bin" % (self.count, name))).write_bytes(data)
            except (gdb.error, ValueError) as error:
                gdb.write("TH04_CPUFAULT_SNAPSHOT_ERROR %d %s\n" % (self.count, error))
            metadata = dict(vm86=vm86, cr0=cr0, cr3=cr3, logical_to_physical_pages=mappings)
            (directory / ("cpu-fault-%02d-memory.json" % self.count)).write_text(json.dumps(metadata, indent=2) + "\n")
        self.count += 1
        return False

Th04CpuFault("*CPU_Exception", internal=True)
gdb.write("TH04_CPU_OBSERVER_ARM primary-gdb\n")
end
run
