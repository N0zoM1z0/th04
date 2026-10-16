"""Read actual guest software INT 21h requests and subsequent process activity."""
import hashlib
import gzip
import json
from pathlib import Path

import gdb

from th04_dos_process import resident_allocation, artifact_for_path, c_string, process_owner
from compare_th04_dos_demos import relocated_module


class ProcessRecorder(gdb.Breakpoint):
    def __init__(self, output, ram, address, read, tick, resident):
        self.output, self.ram = Path(output), ram
        self.address, self.read, self.tick, self.resident = address, read, tick, resident
        self.rows = []
        self.pending_exec = None
        self.error = None
        self.finished = False
        self.bound_artifact = None
        self.entry_records = []
        self.last_entry = None
        self.entry_requested = None
        self.handoff_requested = None
        self.targets = json.loads((self.output / 'process-targets.json').read_text())
        for row in self.targets.values():
            data = Path(row['path']).read_bytes()
            if hashlib.sha256(data).hexdigest() != row['sha256'] or len(data) != row['size']:
                raise ValueError('process target identity')
        if gdb.selected_frame().architecture().name() != 'i386:x86-64':
            raise ValueError('process observer requires pinned SysV AMD64 host ABI')
        self.regs, self.segments = address('cpu_regs'), address('Segs')
        self.kernel_disabled = address('dos_kernel_disabled')
        self.entry = address('CPU_Interrupt(unsigned long, unsigned long, unsigned int)')
        super().__init__('*%d' % self.entry, internal=True)
        self.silent = True
        self.transfer = Transfer(self)
        self.refresh_condition()

    def refresh_condition(self):
        condition = '($rdi == 33) && (($rsi & 1) != 0) && (*(unsigned char *)%d != 0)' % self.kernel_disabled
        if self.pending_exec is None or self.pending_exec.get('overlay'):
            condition += ' && (' + ' || '.join('*(unsigned char *)%d == %d' % (self.regs + 1, value)
                                               for value in (0, 0x31, 0x4b, 0x4c)) + ')'
        self.condition = condition

    def context(self):
        return dict(cpu_regs=self.read(self.regs, 48).hex(),
                    segments=self.read(self.segments, 136).hex(), tick=self.tick())

    def at_entry(self):
        return gdb.selected_frame().pc() == self.entry

    def capture_event(self):
        try:
            # Python stop callbacks can run before GDB applies .condition.
            # Filter the actual entry arguments before interpreting guest state.
            number, kind = (int(gdb.parse_and_eval('$' + name)) for name in ('rdi', 'rsi'))
            if number != 0x21 or not kind & 1 or self.read(self.kernel_disabled, 1) == b'\0':
                return False
            regs = self.read(self.regs, 48)
            ah = regs[1]
            if ah not in (0, 0x31, 0x4b, 0x4c) and self.pending_exec is None:
                return False
            context = self.context()
            segments = bytes.fromhex(context['segments'])
            cs = int.from_bytes(segments[8:16], 'little')
            ds = int.from_bytes(segments[24:32], 'little')
            oldeip = int(gdb.parse_and_eval('$rdx')) & 65535
            ip = (oldeip - 2) & 65535
            memory, _, state = self.ram.read_range(0, 655360)
            opcode = memory[cs * 16 + ip:cs * 16 + ip + 2]
            if opcode != b'\xcd\x21':
                (self.output / 'process-dispatch-error.json').write_text(json.dumps(dict(context=context,
                    cs=cs, oldeip=oldeip, ip=ip, opcode=opcode.hex(), state=state,
                    host_arguments=[int(gdb.parse_and_eval('$' + name)) for name in ('rdi','rsi','rdx')]),indent=2)+'\n')
                raise ValueError('process interrupt ABI/opcode boundary')
            owner = process_owner(memory, cs, ip)
            if owner and self.pending_exec and not self.pending_exec.get('overlay') and owner['environment_artifact'] == self.pending_exec['artifact']:
                self.record('environment-activity', context, owner=owner, cs=cs, ip=ip, opcode=opcode.hex(),
                            exec_sequence=self.pending_exec['sequence'], ax=int.from_bytes(regs[:2], 'little'))
                self.pending_exec = None
                self.refresh_condition()
            if ah in (0, 0x31, 0x4b, 0x4c):
                row = dict(owner=owner, cs=cs, ip=ip, opcode=opcode.hex(),
                           caller_artifact=self.bound_artifact,
                           caller_code_hex=memory[cs * 16 + ip:cs * 16 + ip + 96].hex(),
                           ax=int.from_bytes(regs[:2], 'little'), cr0=state[1], cr4=state[2], cr3=state[3])
                if ah == 0x4b:
                    dx = int.from_bytes(regs[8:10], 'little')
                    name = c_string(memory, ds * 16 + dx)
                    row.update(requested_path_hex=name.hex(), requested_artifact=artifact_for_path(name))
                    if regs[0] == 3:
                        es = int.from_bytes(segments[:8], 'little')
                        bx = int.from_bytes(regs[12:14], 'little')
                        block = memory[es * 16 + bx:es * 16 + bx + 4]
                        row.update(overlay_parameter_hex=block.hex(),
                                   overlay_load_segment=int.from_bytes(block[:2], 'little'),
                                   overlay_relocation_factor=int.from_bytes(block[2:], 'little'))
                event = self.record('exec-request' if ah == 0x4b else 'terminate-request', context, **row)
                if ah == 0x4b and regs[0] in (0, 3) and row['requested_artifact']:
                    self.pending_exec = dict(artifact=row['requested_artifact'], sequence=event['sequence'],
                                             overlay=regs[0] == 3, request=event)
                    if regs[0] == 3:
                        self.transfer.arm(event)
                    self.refresh_condition()
                    if self.bound_artifact == 'th04-main' and row['requested_artifact'] == 'th04-maine':
                        self.handoff_requested = event
            if context != self.context() or hashlib.sha256(memory).digest() != hashlib.sha256(self.ram.read_range(0, 655360)[0]).digest():
                raise ValueError('process observation changed guest context/RAM/tick')
            return False
        except Exception as error:
            self.error = str(error)
            (self.output / 'process-error.txt').write_text(self.error + '\n')
            return True

    def record(self, kind, context, **values):
        resident = self.resident()
        row = dict(sequence=len(self.rows), kind=kind, **context, **values,
                   resident_linear=resident,
                   resident_hex=None if resident is None else self.ram.read_range(resident, 256)[0].hex())
        if resident is not None:
            memory = self.ram.read_range(0, 655360)[0]
            anchor = values.get('owner') or (self.last_entry or {}).get('owner')
            if anchor is None:
                raise ValueError('resident allocation lacks observed program owner')
            row['resident_allocation'] = resident_allocation(memory, anchor['mcb_segment'], resident)
            name = 'process-memory-%04d.bin.gz' % row['sequence']
            with (self.output / name).open('xb') as stream:
                stream.write(gzip.compress(memory, mtime=0))
            row.update(memory_file=name,
                       memory_file_sha256=hashlib.sha256((self.output / name).read_bytes()).hexdigest(),
                       conventional_sha256=hashlib.sha256(memory).hexdigest())
        self.rows.append(row)
        with (self.output / 'process-events.jsonl').open('a') as stream:
            stream.write(json.dumps(row, sort_keys=True) + '\n')
        return row

    def finish(self, boundary):
        if self.finished:
            return
        self.finished = True
        (self.output / 'process-events.json').write_text(json.dumps(dict(schema_version=1,
            complete_capture=not self.error,
            complete_route=not self.error and boundary in ('fresh-op-menu', 'second-main-entry') and
                           [self.rows[i]['artifact'] for i in self.entry_records] ==
                           (['th04-main', 'th04-maine', 'th04-op', 'th04-main'] if
                            boundary == 'second-main-entry' else ['th04-main', 'th04-maine', 'th04-op']), boundary=boundary,
            events=len(self.rows), pending=self.pending_exec, error=self.error,
            entries=self.entry_records,
            scope='Booted guest DOS, with internal DOS kernel disabled: actual software INT21 requests and subsequent MCB/PSP-owned activity; requests alone are not successful exec or natural exit'), indent=2) + '\n')


class Transfer(gdb.Breakpoint):
    def __init__(self, recorder):
        self.recorder = recorder
        self.entry = recorder.address('CPU_JMP(bool, unsigned long, unsigned long, unsigned int)')
        super().__init__('*%d' % self.entry, internal=True)
        self.enabled = False
        self.silent = True
        self.expected = None

    def arm(self, request):
        r = self.recorder
        spec = r.targets[request['requested_artifact']]
        image = Path(spec['path']).read_bytes()
        load, factor = request['overlay_load_segment'], request['overlay_relocation_factor']
        if load != factor or not 0 < load < 0xa000:
            raise ValueError('overlay load/relocation contract')
        cs = factor + int.from_bytes(image[22:24], 'little')
        ip = int.from_bytes(image[20:22], 'little')
        self.expected = dict(artifact=request['requested_artifact'], request_sequence=request['sequence'],
                             load_segment=load, relocation_factor=factor, cs=cs, ip=ip,
                             image=image, relocated=relocated_module(image, factor))
        self.condition = '($rdi == 0) && ($rsi == %d) && ($rdx == %d)' % (cs, ip)
        self.enabled = True

    def at_entry(self):
        return self.enabled and gdb.selected_frame().pc() == self.entry

    def capture_transfer(self):
        expected, r = self.expected, self.recorder
        observed = r.ram.read_range(expected['load_segment'] * 16, len(expected['relocated']))[0]
        if observed != expected['relocated']:
            raise ValueError('overlay complete relocated image before transfer')
        self.enabled = False
        EntryReturn(r, expected)


class EntryReturn(gdb.FinishBreakpoint):
    def __init__(self, recorder, expected):
        self.recorder, self.expected = recorder, expected
        super().__init__(gdb.newest_frame(), internal=True)
        self.silent = True

    def stop(self):
        r, expected = self.recorder, self.expected
        try:
            context = r.context()
            segments, regs = bytes.fromhex(context['segments']), bytes.fromhex(context['cpu_regs'])
            cs, ip = int.from_bytes(segments[8:16], 'little'), int.from_bytes(regs[32:36], 'little') & 65535
            observed = r.ram.read_range(expected['load_segment'] * 16, len(expected['relocated']))[0]
            if (cs, ip) != (expected['cs'], expected['ip']) or observed != expected['relocated']:
                raise ValueError('actual overlay entry PC/complete image')
            memory = r.ram.read_range(0, 655360)[0]
            owner = process_owner(memory, cs, ip)
            if owner is None or owner['load_segment'] != expected['load_segment']:
                raise ValueError('overlay entry MCB/PSP ownership')
            name = 'process-entry-%04d.bin.gz' % len(r.rows)
            with (r.output / name).open('xb') as stream:
                stream.write(gzip.compress(observed, mtime=0))
            row = r.record('entry', context, artifact=expected['artifact'], owner=owner,
                           cs=cs, ip=ip, load_segment=expected['load_segment'],
                           relocation_factor=expected['relocation_factor'],
                           request_sequence=expected['request_sequence'],
                           file_sha256=hashlib.sha256(expected['image']).hexdigest(),
                           relocated_sha256=hashlib.sha256(observed).hexdigest(), image_bytes=len(observed),
                           ram_file=name, ram_file_sha256=hashlib.sha256((r.output / name).read_bytes()).hexdigest())
            if context != r.context() or memory != r.ram.read_range(0, 655360)[0]:
                raise ValueError('entry observation changed guest context/RAM/tick')
            r.bound_artifact = expected['artifact']
            r.entry_records.append(row['sequence'])
            r.last_entry = r.entry_requested = row
            r.pending_exec = None
            r.refresh_condition()
        except Exception as error:
            r.error = str(error)
            (r.output / 'process-error.txt').write_text(r.error + '\n')
        return True
