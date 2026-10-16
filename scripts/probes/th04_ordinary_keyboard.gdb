# Keyboard device input adapter; state observation remains read-only.
set pagination off
set language c++
set confirm off
set disable-randomization off
set debuginfod enabled off
handle SIG33 nostop noprint pass
starti
python
import gdb, json, os, re, hashlib
from pathlib import Path
import sys
sys.path.insert(0, os.environ['TH04_CLOCK_SOURCE_DIR'])
from th04_demo_host_ram import HostRam
out = Path(os.environ['TH04_CLOCK_INPUT_OUTPUT'])
header = Path(os.environ['TH04_CLOCK_KEYBOARD_HEADER']).read_text()
body = header.split('enum KBD_KEYS {', 1)[1].split('};', 1)[0]
names = re.findall('\\bKBD_[A-Za-z0-9_]+\\b', re.sub('/\\*.*?\\*/', '', body, flags=re.S))
assert len(names) == len(set(names))
keys = {name: i for i, name in enumerate(names)}
address = int(gdb.parse_and_eval('(void *)&PIC_Ticks'))
function = int(gdb.parse_and_eval("(void *)&'KEYBOARD_AddKey(KBD_KEYS, bool)'"))
regs = int(gdb.parse_and_eval('(void *)&cpu_regs'))
segments = int(gdb.parse_and_eval('(void *)&Segs'))
membaseptr = int(gdb.parse_and_eval('(void *)&MemBase'))
ram = HostRam(lambda address, size: gdb.selected_inferior().read_memory(address, size), {name: int(gdb.parse_and_eval('(void *)&' + name)) for name in ('MemBase', 'cpu', 'paging')})
actions = []
schedule = []
trace = out / 'raw.txt'
resident = None
seedwatch = None
todo = None
armed = False
held = False
found = None
dialog_frame = int(os.environ.get('TH04_ORDINARY_DIALOG_FRAME', 0))
continue_frame = int(os.environ.get('TH04_ORDINARY_CONTINUE_FRAME', 0))
active_dialog_frame = dialog_frame
waits = []
dialog_active = False
dialog_released = False
dialog_done = False
dialog_tick = None
enter_down = False
stall_ms = int(os.environ.get('TH04_ORDINARY_STALL_MS', 0))
last_progress_frame = 0
last_progress_tick = 0

def read(address, size):
    return bytes(gdb.selected_inferior().read_memory(address, size))

def tick():
    return int.from_bytes(read(address, 4), 'little')

def base():
    return int.from_bytes(read(membaseptr, 8), 'little')

def snapshot():
    return dict(conventional_sha256=hashlib.sha256(ram.read_range(0, 655360)[0]).hexdigest(), cpu_regs=read(regs, 48).hex(), segments=read(segments, 136).hex())

def save():
    record = dict(actions=actions, remaining=schedule, resident_linear=resident, found=found, requested_seed=64, pic_ticks_address=address, keyboard_function_address=function, keys=keys, scope='Original OP resident seed increment is observed, never written; keyboard API adapter only; no guest RAM/register/clock writes')
    if continue_frame:
        record['waits'] = waits
    (out / 'clock-input.json').write_text(json.dumps(record, indent=2) + '\n')

class Seed(gdb.Breakpoint):

    def __init__(self):
        super().__init__('*(unsigned int *)0x%x' % (base() + ram.physical(resident + 20)), type=gdb.BP_WATCHPOINT, wp_class=gdb.WP_WRITE, internal=True)

    def stop(self):
        global todo, armed
        value = int.from_bytes(read(base() + ram.physical(resident + 20), 4), 'little')
        if value == 64 and (not armed):
            todo = ('key', tick(), 'KBD_enter', True)
            armed = True
            return True
        assert value < 64 or armed, ('missed menu seed', value)
        return False

class Clock(gdb.Breakpoint):

    def __init__(self):
        super().__init__('*(unsigned int *)0x%x' % address, type=gdb.BP_WATCHPOINT, wp_class=gdb.WP_WRITE, internal=True)

    def stop(self):
        global resident, todo, held, found, dialog_released, dialog_done, last_progress_frame, last_progress_tick
        now = tick()
        if stall_ms and monitor is not None and monitor.current is not None:
            frame = monitor.current.sequence.frames
            if frame != last_progress_frame:
                last_progress_frame, last_progress_tick = frame, now
            elif frame > 0 and not dialog_active and now - last_progress_tick >= stall_ms:
                todo = ('diagnostic',)
                return True
        if dialog_active:
            current_frame = monitor.current.sequence.frames
            if current_frame > active_dialog_frame:
                if enter_down:
                    todo = ('key', now, 'KBD_enter', False)
                else:
                    todo = ('key', now, 'KBD_z', True)
                    dialog_done = True
                return True
            if not dialog_released and now - dialog_tick >= 100:
                todo = ('key', now, 'KBD_z', False)
                dialog_released = True
                return True
            if dialog_released and schedule and now >= schedule[0][0]:
                todo = ('key', *schedule.pop(0))
                return True
        if resident is None and now % 100 == 0 and base():
            try:
                memory = ram.read_range(0, 655360)[0]
            except ValueError:
                return False
            matches = []
            at = memory.find(b'HUMAConfig\x00')
            while at >= 0:
                if at % 16 == 0 and memory[at + 58:at + 60] == bytes([6, 0]) and (memory[at + 15] == 1):
                    matches.append(at)
                at = memory.find(b'HUMAConfig\x00', at + 1)
            if len(matches) == 1:
                resident = matches[0]
                found = dict(tick=now, bytes=memory[resident:resident + 256].hex(), memory_sha256=hashlib.sha256(memory).hexdigest())
                todo = ('arm',)
                return True
        loaded = trace.exists() and trace.stat().st_size > 1024
        if loaded and (not held):
            assert resident is not None, 'MAIN entered before guarded OP selection'
            todo = ('key', now, 'KBD_z', True)
            held = True
            return True
        if not loaded and schedule and (now >= schedule[0][0]):
            todo = ('key', *schedule.pop(0))
            if todo[2] == 'KBD_z':
                held = True
            return True
        return False
clock = Clock()
monitor = None
if os.environ.get('TH04_ORDINARY_DGROUP') == '1':
    from th04_ordinary_dgroup_gdb import Monitor
    monitor = Monitor(out, ram)
process_recorder = None
if os.environ.get('TH04_ORDINARY_PROCESS_EVENTS') == '1':
    from th04_ordinary_process_gdb import ProcessRecorder
    process_recorder = ProcessRecorder(out, ram, lambda name: int(gdb.parse_and_eval("(void *)&'" + name + "'")), read, tick, lambda: resident)
save()
while gdb.selected_inferior().pid:
    gdb.execute('continue')
    if not gdb.selected_inferior().pid:
        break
    if monitor is not None and monitor.error:
        raise ValueError(monitor.error)
    if process_recorder is not None and process_recorder.error:
        raise ValueError(process_recorder.error)
    if process_recorder is not None and process_recorder.at_entry():
        process_recorder.capture_event()
        if process_recorder.error:
            raise ValueError(process_recorder.error)
        continue
    if process_recorder is not None and process_recorder.transfer.at_entry():
        process_recorder.transfer.capture_transfer()
        continue
    if process_recorder is not None and process_recorder.entry_requested:
        process_recorder.entry_requested = None
        continue
    if monitor is not None and monitor.terminal is not None:
        before_flush = snapshot()
        before_tick = tick()
        trace_pointer = int(gdb.parse_and_eval("(void *)&'th04_demo_observer::trace'"))
        trace_file = int.from_bytes(read(trace_pointer,8), 'little')
        gdb.execute('call (int)fflush((void *)0x%x)' % trace_file, to_string=True)
        assert before_flush == snapshot() and before_tick == tick()
        monitor.finish()
        monitor = None
        if process_recorder is not None:
            process_recorder.finish('observed-main-prefix')
        gdb.execute('kill')
        break
    if monitor is not None and (monitor.dialog_requested or monitor.continue_requested):
        is_continue = monitor.continue_requested
        monitor.dialog_requested = False
        monitor.continue_requested = False
        active_dialog_frame = continue_frame if is_continue else dialog_frame
        dialog_active = True
        dialog_released = False
        dialog_done = False
        dialog_tick = tick()
        schedule = []
        if continue_frame:
            waits.append(dict(kind='continue' if is_continue else 'dialogue', frame=active_dialog_frame,
                              tick=dialog_tick, action_start=len(actions),
                              resident=ram.read_range(resident,80)[0].hex()))
        clock.enabled = True
        continue
    if todo is not None and todo[0] == 'diagnostic':
        registers, segment_data = read(regs,48), read(segments,136)
        cs = int.from_bytes(segment_data[8:16], 'little')
        ip = int.from_bytes(registers[32:36], 'little') & 65535
        linear = cs * 16 + ip
        opcode = ram.read_range(linear,64)[0].hex() if linear + 64 < 0xa0000 else None
        data = ram.read_range(monitor.current.linear,65536)[0]
        (out/'ordinary-stall-dgroup.bin').write_bytes(data)
        (out/'ordinary-stall.json').write_text(json.dumps(dict(complete_prefix=False,
            frame=last_progress_frame, tick=tick(), last_progress_tick=last_progress_tick,
            cs=cs, ip=ip, opcode=opcode, cpu_regs=registers.hex(), segments=segment_data.hex(),
            load_segment=monitor.current.load, dgroup_segment=monitor.current.dgroup,
            interpretation='Observed virtual no-frame progress; cause unclassified'),indent=2)+'\n')
        gdb.execute('kill')
        monitor = None
        break
    try:
        clock.enabled = False
        if seedwatch is not None:
            seedwatch.enabled = False
        if todo[0] == 'arm':
            seedwatch = Seed()
            save()
        else:
            _, due, name, down = todo
            before = tick()
            guest = snapshot()
            seed = int.from_bytes(read(base() + ram.physical(resident + 20), 4), 'little')
            gdb.execute('call ((void (*)(int, bool))0x%x)(%d, %s)' % (function, keys[name], 'true' if down else 'false'), to_string=True)
            assert before == tick() and guest == snapshot()
            action = dict(due=due, tick=before, key=name, pressed=down, resident_seed=seed, unchanged_guest=guest)
            if continue_frame:
                action.update(frame=monitor.current.sequence.frames if monitor.current else None,
                              resident=ram.read_range(resident,80)[0].hex())
            actions.append(action)
            if name == 'KBD_enter':
                enter_down = down
            if dialog_active and name == 'KBD_z' and not down:
                schedule = []
                for delta in range(500, 30001, 1000):
                    schedule.extend([(before + delta, 'KBD_enter', True),
                                     (before + delta + 120, 'KBD_enter', False)])
            if dialog_active and dialog_done:
                if continue_frame:
                    waits[-1].update(resumed_frame=monitor.current.sequence.frames, resumed_tick=before,
                                     action_end=len(actions), resident_after=action['resident'])
                dialog_active = False
                schedule = []
            save()
            if len(actions) == 1:
                schedule = [(before + 120, 'KBD_enter', False)]
                for delta in (1000, 2000):
                    schedule.extend([(before + delta, 'KBD_enter', True), (before + delta + 120, 'KBD_enter', False)])
                schedule.append((before + 2200, 'KBD_z', True))
                seedwatch.delete()
                seedwatch = None
        todo = None
        if held:
            if not dialog_frame and not stall_ms:
                clock.delete()
            else:
                clock.enabled = dialog_active or bool(stall_ms)
        else:
            clock.enabled = True
    except Exception as e:
        (out / 'clock-input-error.txt').write_text(repr(e) + '\n')
        gdb.execute('quit 91')
        break
if monitor is not None:
    monitor.finish()
if process_recorder is not None:
    process_recorder.finish('inferior-stopped')
end
