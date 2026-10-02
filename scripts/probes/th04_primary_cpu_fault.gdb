set pagination off
set confirm off
set disable-randomization off
handle SIG33 nostop noprint pass
python
import os
import pathlib
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
        if not bool(gdb.parse_and_eval("cpu.pmode")):
            directory = pathlib.Path(os.environ["TH04_CPU_FAULT_DIR"])
            for name, start, size in (("code", cs * 16 + ip, 64),
                                      ("stack", ss * 16 + sp, 64), ("data", ds * 16, 65536)):
                if start + size <= 0xa0000:
                    data = bytes(gdb.selected_inferior().read_memory(base + start, size))
                    (directory / ("cpu-fault-%02d-%s.bin" % (self.count, name))).write_bytes(data)
        self.count += 1
        return False

Th04CpuFault("*CPU_Exception", internal=True)
gdb.write("TH04_CPU_OBSERVER_ARM primary-gdb\n")
end
run
