"""Read IRQ1 entry, BIOS I/O and guest EOI/IRET state on the pinned engine."""
import hashlib
import json
from pathlib import Path
import gdb


def install(m, symbols):
    p = m.admission
    read = lambda address, size: bytes(gdb.selected_inferior().read_memory(address, size))
    stream = (m.output/'keyboard-isr.jsonl').open('x')
    digest = hashlib.sha256()
    state = dict(sequence=0, irq=None, callback=False, records=0)

    def memory(address, size):
        if address+size <= 0xa0000:
            return m.ram.read_range(address, size)[0]
        # The conventional-RAM walker deliberately excludes ROM/device pages.
        # Read only the F000 ROM window, preserving paging and recording maps.
        assert 0xf0000 <= address < address+size <= 0x100000
        base, cr0, cr4, cr3 = m.ram.state()
        assert not cr4 & 0x20, 'PAE outside ROM observer contract'
        result = bytearray()
        while len(result) < size:
            linear = address+len(result)
            physical = linear
            if cr0 & 0x80000000:
                entry = int.from_bytes(read(base+(cr3 & 0xfffff000)+(linear >> 22)*4, 4), 'little')
                assert entry & 1
                if entry & 0x80:
                    physical = (entry & 0xffc00000)+(linear & 0x3fffff)
                else:
                    entry = int.from_bytes(read(base+(entry & 0xfffff000)+((linear >> 12)&1023)*4, 4), 'little')
                    assert entry & 1
                    physical = (entry & 0xfffff000)+(linear & 4095)
            length = min(size-len(result), 4096-(linear & 4095))
            assert (0xf0000 <= physical and physical+length <= 0x100000) or (0x100000 <= physical and physical+length <= 0x1000000)
            result.extend(read(base+physical, length))
        return bytes(result)

    def record(kind, **extra):
        before = m.context()
        context = p.context()
        regs, segs = bytes.fromhex(context['registers']), bytes.fromhex(context['segments'])
        ss = int.from_bytes(segs[16:24], 'little')
        sp = int.from_bytes(regs[16:20], 'little') & 65535
        context.update(ss=ss, sp=sp)
        row = dict(ordinal=state['records'], kind=kind, irq=state['irq'],
                   after_admission_ordinal=p.ordinal-1, time=p.moment(), context=context,
                   bios=memory(0x52a, 16).hex(), uart=p.uart(), pic=p.pic_state(),
                   stack=memory(ss*16+sp, 16).hex() if context['flags'] & 0x20000 else None,
                   stack_scope='V86 real-segment frame only; protected monitor stack excluded', **extra)
        assert m.context() == before, 'ISR observation changed guest context'
        data = (json.dumps(row, separators=(',', ':'))+'\n').encode()
        stream.write(data.decode()); stream.flush(); digest.update(data)
        state['records'] += 1

    class Returned(gdb.FinishBreakpoint):
        def __init__(self, kind, **extra):
            self.kind, self.extra = kind, extra
            super().__init__(gdb.newest_frame(), internal=True)

        def stop(self):
            try:
                if self.kind == 'io-read-return':
                    self.extra['value'] = int(gdb.parse_and_eval('$rax')) & 255
                record(self.kind, **self.extra)
                if self.kind == 'iret-return' and self.extra['role'] == 'bios-tail':
                    state['irq'] = None
                    iret.enabled = False
                return False
            except Exception as error:
                return p.fail(error)

    class Read(gdb.Breakpoint):
        def stop(self):
            try:
                port = int(gdb.parse_and_eval('$rdi'))
                if state['callback'] and port in (0x41, 0x43):
                    record('io-read-entry', port=port)
                    Returned('io-read-return', port=port)
                return False
            except Exception as error:
                return p.fail(error)

    class Iret(gdb.Breakpoint):
        def stop(self):
            try:
                if state['irq'] is not None:
                    context = p.context()
                    role = 'bios-tail' if context['cs'] == 0xf000 and context['flags'] & 0x20000 else 'monitor'
                    record('iret-entry', role=role, use32=bool(int(gdb.parse_and_eval('$rdi'))),
                           old_eip=int(gdb.parse_and_eval('$rsi')) & 0xffffffff)
                    Returned('iret-return', role=role)
                return False
            except Exception as error:
                return p.fail(error)

    io = Read('*0x%x'%symbols['_Z8IO_ReadBm'], internal=True)
    iret = Iret('*0x%x'%symbols['_Z8CPU_IRETbj'], internal=True)
    io.enabled = iret.enabled = False
    old_event = p.event

    def observed(kind, **extra):
        original_row = old_event(kind, **extra)
        if kind == 'cpu-irq-accept' and extra.get('vector') == 9:
            assert state['irq'] is None
            state['sequence'] += 1
            state['irq'] = state['sequence']
            vector = memory(9*4, 4)
            ip, cs = int.from_bytes(vector[:2], 'little'), int.from_bytes(vector[2:], 'little')
            location = int.from_bytes(read(symbols['BIOS_DEFAULT_IRQ1_LOCATION'], 8), 'little')
            record('irq-accept', vector=vector.hex(), stub_cs=cs, stub_ip=ip,
                   rom=memory(cs*16+ip, 32).hex(), default_location=location,
                   default_rom=memory((location >> 16)*16+(location & 65535), 32).hex())
            Returned('irq-entry-return')
            iret.enabled = True
        elif kind == 'bios-irq-entry':
            assert state['irq'] is not None and not state['callback']
            state['callback'] = True
            io.enabled = True
            record('bios-entry')
        elif kind == 'bios-irq-return':
            assert state['callback']
            record('bios-return')
            state['callback'] = False
            io.enabled = False
        elif kind in ('pic-write-entry', 'pic-write-return') and state['irq'] is not None:
            record(kind, **extra)

        return original_row

    p.event = observed
    old_finish = p.finish

    def finish(*args, **kwargs):
        assert state['irq'] is None and not state['callback']
        stream.close()
        (m.output/'keyboard-isr.json').write_text(json.dumps(dict(
            passed=True, records=state['records'], interrupts=state['sequence'],
            stream_sha256=digest.hexdigest(), symbols=symbols,
            scope='Read-only IRQ1 ROM/stack/BIOS I/O/EOI/IRET observations. '
                  'Original MAIN and emulator identities remain bound by the parent capture. '
                  'No guest PC, memory, flags, elapsed time or expected latch assignments. '
                  'One emulator family; physical CPU timing and complete campaign remain open.'), indent=2)+'\n')
        return old_finish(*args, **kwargs)

    p.finish = finish
