set pagination off
set confirm off
set disable-randomization off
set debuginfod enabled off
handle SIG33 nostop noprint pass
starti
python
import gdb
import json
import os
import resource
from pathlib import Path

directory = Path(os.environ['TH04_DEMO_SNAPSHOT_DIR'])
profile = json.loads((directory / 'profile.json').read_text())
requested = {int(x) for x in os.environ['TH04_DEMO_SNAPSHOT_FRAMES'].split(',')}
captured = set()
inferior = gdb.selected_inferior()
resource.prlimit(inferior.pid, resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))

# Host layout is restricted to this ELF-attested x86_64 observer: config.h
# defines Bitu as uintptr_t; CPUBlock starts cpl,mpl,cr0,cr4; PagingBlock starts
# cr3. Symbols remain in the stripped-debug ELF. No guest accessor/call is used.
def address(name):
    return int(gdb.parse_and_eval("(unsigned long)&'"+name+"'"))

def integer(pointer, size):
    return int.from_bytes(bytes(inferior.read_memory(pointer, size)), 'little')

def host_state():
    return (integer(address('MemBase'), 8), integer(address('cpu')+16, 8),
            integer(address('cpu')+24, 8), integer(address('paging'), 8))

def physical(linear):
    base, cr0, cr4, cr3 = host_state()
    if not cr0 & 0x80000000:
        return linear
    if cr4 & 0x20:
        raise ValueError('PAE outside snapshot observer')
    entry = integer(base+(cr3 & 0xfffff000)+(linear >> 22)*4, 4)
    if not entry & 1:
        raise ValueError('absent directory')
    if entry & 0x80:
        return (entry & 0xffc00000)+(linear & 0x3fffff)
    entry = integer(base+(entry & 0xfffff000)+((linear >> 12)&1023)*4, 4)
    if not entry & 1:
        raise ValueError('absent page')
    return (entry & 0xfffff000)+(linear & 4095)

def read_linear(start, size):
    base, _, _, _ = host_state()
    result = bytearray()
    pages = {}
    while len(result) < size:
        linear = start+len(result)
        page = physical(linear)
        length = min(size-len(result), 4096-(linear & 4095))
        if not (0 <= page and page+length <= 16*1024*1024
                and not (page < 0x100000 and page+length > 0xa0000)):
            raise ValueError('snapshot outside ordinary RAM')
        pages[str(linear & ~4095)] = page & ~4095
        result.extend(inferior.read_memory(base+page, length))
    return bytes(result), pages

class Frame(gdb.Breakpoint):
    def __init__(self, linear, load):
        self.linear, self.load = linear, load
        base = host_state()[0]
        self.host = base+physical(linear+profile['fields'][0][1])
        super().__init__('*(unsigned short *)%d' % self.host,
                         type=gdb.BP_WATCHPOINT, internal=True)

    def stop(self):
        frame = integer(self.host, 2)
        if frame not in requested or frame in captured:
            return False
        data, pages = read_linear(self.linear, 65536)
        if int.from_bytes(data[profile['fields'][0][1]:profile['fields'][0][1]+2], 'little') != frame:
            raise ValueError('frame watch mapping changed')
        (directory / ('snapshot-%d-dgroup.bin' % frame)).write_bytes(data)
        _, cr0, cr4, cr3 = host_state()
        metadata = dict(frame=frame, load_segment=self.load,
                        dgroup_segment=self.linear//16, cr0=cr0, cr4=cr4, cr3=cr3,
                        logical_to_physical_pages=pages,
                        boundary='stage_frame write, before mod counters and score update')
        (directory / ('snapshot-%d.json' % frame)).write_text(json.dumps(metadata, indent=2)+'\n')
        captured.add(frame)
        gdb.write('TH04_DEMO_SNAPSHOT %d\n' % frame)
        return captured == requested

class Load(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*(unsigned int *)&'th04_demo_observer::process'",
                         type=gdb.BP_WATCHPOINT, internal=True)

    def stop(self):
        process = integer(address('th04_demo_observer::process'), 4)
        if process == 1:
            load = integer(address('th04_demo_observer::load_segment'), 4)
            Frame((load+profile['dgroup'])*16, load)
            self.enabled = False
        return False

Load()
end
continue
kill
quit
