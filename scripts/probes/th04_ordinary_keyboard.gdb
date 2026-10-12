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

def read(address, size):
    return bytes(gdb.selected_inferior().read_memory(address, size))

def tick():
    return int.from_bytes(read(address, 4), 'little')

def base():
    return int.from_bytes(read(membaseptr, 8), 'little')

def snapshot():
    return dict(conventional_sha256=hashlib.sha256(ram.read_range(0, 655360)[0]).hexdigest(), cpu_regs=read(regs, 48).hex(), segments=read(segments, 136).hex())

def save():
    (out / 'clock-input.json').write_text(json.dumps(dict(actions=actions, remaining=schedule, resident_linear=resident, found=found, requested_seed=64, pic_ticks_address=address, keyboard_function_address=function, keys=keys, scope='Original OP resident seed increment is observed, never written; keyboard API adapter only; no guest RAM/register/clock writes'), indent=2) + '\n')

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
        global resident, todo, held, found
        now = tick()
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
save()
while gdb.selected_inferior().pid:
    gdb.execute('continue')
    if not gdb.selected_inferior().pid:
        break
    if monitor is not None and monitor.error:
        raise ValueError(monitor.error)
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
            actions.append(dict(due=due, tick=before, key=name, pressed=down, resident_seed=seed, unchanged_guest=guest))
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
            clock.delete()
        else:
            clock.enabled = True
    except Exception as e:
        (out / 'clock-input-error.txt').write_text(repr(e) + '\n')
        gdb.execute('quit 91')
        break
if monitor is not None:
    monitor.finish()
end
