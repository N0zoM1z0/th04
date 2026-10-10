set pagination off
set confirm off
set disable-randomization off
set debuginfod enabled off
handle SIG33 nostop noprint pass
starti
python
import gdb
import gzip
import json
import os
import resource
import sys
from pathlib import Path

sys.path.insert(0, os.environ['TH04_DEMO_STREAM_SOURCE_DIR'])
from th04_demo_host_ram import HostRam
from th04_demo_dgroup import MAGIC, HEADER, UPDATE_COUNT, DGROUP_SIZE, BOUNDARY, FrameSequence
th04_video_mode = os.environ.get('TH04_DEMO_STREAM_KIND') == 'video'
th04_stream_prefix = 'video' if th04_video_mode else 'dgroup'
th04_stream_marker = 'TH04_VIDEO_STREAM' if th04_video_mode else 'TH04_DGROUP_STREAM'
th04_stream_block_size = DGROUP_SIZE
if th04_video_mode:
    from th04_demo_video import VideoRam, MAGIC, BLOCK_SIZE, LAYOUT, SYMBOL_SIZES
    th04_stream_block_size = BLOCK_SIZE

directory = Path(os.environ['TH04_DEMO_STREAM_DIR'])
profile = json.loads((directory / 'profile.json').read_text())
expected_processes = int(os.environ['TH04_DEMO_STOP_AFTER'])
inferior = gdb.selected_inferior()
resource.prlimit(inferior.pid, resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))

def address(name):
    return int(gdb.parse_and_eval("(unsigned long)&'"+name+"'"))

ram = HostRam(inferior.read_memory, {name: address(name) for name in ('MemBase', 'cpu', 'paging')})
if th04_video_mode:
    th04_video_layout = json.loads(Path(os.environ['TH04_DEMO_VIDEO_LAYOUT']).read_text())
    if not th04_video_layout['passed'] or th04_video_layout['layout'] != LAYOUT:
        raise ValueError('video layout identity')
    th04_video_symbols = {name: address(name) for name in SYMBOL_SIZES}
    th04_video_biases = {th04_video_symbols[name]-th04_video_layout['symbols'][name]['address'] for name in SYMBOL_SIZES}
    if len(th04_video_biases) != 1:
        raise ValueError('video ELF symbol mappings')
    th04_video_reader = VideoRam(inferior.read_memory, th04_video_symbols)
process_pointer = address('th04_demo_observer::process')
load_pointer = address('th04_demo_observer::load_segment')
active_pointer = address('th04_demo_observer::active')
captured = {}
current = None

class Frame(gdb.Breakpoint):
    def __init__(self, process, load):
        self.process, self.load, self.frames = process, load, 0
        self.dgroup = load+profile['dgroup']
        self.linear = self.dgroup*16
        self.host = ram.state()[0]+ram.physical(self.linear+profile['fields'][0][1])
        self.sequence = FrameSequence(ram.integer(self.host, 2))
        self.previous = 0
        self.raw = (directory / ('%s-demo-%d.bin.gz' % (th04_stream_prefix, process))).open('xb')
        self.stream = gzip.GzipFile(fileobj=self.raw, mode='wb', compresslevel=1, mtime=0, filename='')
        self.stream.write(MAGIC)
        self.maps = []
        self.last_pages = None
        self.video_maps = []
        self.last_video_map = None
        super().__init__('*(unsigned short *)%d' % self.host,
                         type=gdb.BP_WATCHPOINT, internal=True)

    def stop(self):
        if (not ram.integer(active_pointer, 1)
                or ram.integer(process_pointer, 4) != self.process):
            return False
        frame = ram.integer(self.host, 2)
        # C0 clears BSS a byte at a time; a reused 3996 can transiently be3840.
        if not self.sequence.observe(frame):
            return False
        if th04_video_mode:
            observed, pages, state = ram.read_range(self.linear+profile['fields'][0][1], 2)
        else:
            data, pages, state = ram.read_range(self.linear, DGROUP_SIZE)
            observed = data[profile['fields'][0][1]:profile['fields'][0][1]+2]
        if (int.from_bytes(observed, 'little') != frame
                or state[0]+ram.physical(self.linear+profile['fields'][0][1], state) != self.host):
            raise ValueError('stage-frame watch mapping changed')
        if th04_video_mode:
            stage_offset = next(offset for name, offset, size in profile['fields'] if name == 'stage')
            stage = ram.read_range(self.linear+stage_offset, 1)[0][0]
            data, th04_video_map = th04_video_reader.capture(stage)
            if th04_video_map != self.last_video_map:
                self.video_maps.append(dict(first_frame=frame, **th04_video_map))
                self.last_video_map = th04_video_map
        _, cr0, cr4, cr3 = state
        self.stream.write(HEADER.pack(self.process, frame, self.load, self.dgroup, cr0, cr4, cr3))
        value = int.from_bytes(data, 'little')
        self.stream.write((value ^ self.previous).to_bytes(th04_stream_block_size, 'little'))
        self.previous = value
        self.frames = frame
        if pages != self.last_pages:
            self.maps.append(dict(first_frame=frame, pages=pages))
            self.last_pages = pages
        if frame % 500 == 0 or frame == UPDATE_COUNT:
            self.stream.flush()
            gdb.write('%s %d %d\n' % (th04_stream_marker, self.process, frame))
        return False

    def close(self):
        self.stream.close()
        self.raw.close()
        captured[str(self.process)] = dict(frames=self.frames, load_segment=self.load,
            dgroup_segment=self.dgroup, logical_to_physical_maps=self.maps)
        if th04_video_mode:
            captured[str(self.process)]['video_pointer_maps'] = self.video_maps
        if self.frames != UPDATE_COUNT:
            raise ValueError('incomplete DGROUP process %d' % self.process)

class Load(gdb.Breakpoint):
    def __init__(self):
        super().__init__('*(unsigned int *)%d' % process_pointer,
                         type=gdb.BP_WATCHPOINT, internal=True)

    def stop(self):
        global current
        process = ram.integer(process_pointer, 4)
        if (process != (1 if current is None else current.process+1)
                or process > expected_processes):
            raise ValueError('DGROUP process order')
        if current is not None:
            current.enabled = False
            current.delete()
            current.close()
        load = ram.integer(load_pointer, 4)
        current = Frame(process, load)
        return False

Load()
end
continue
python
if current is not None:
    current.close()
if len(captured) != expected_processes:
    raise ValueError('incomplete DGROUP stream extent')
metadata = dict(schema_version=1, complete=True, boundary=BOUNDARY,
                records_per_demo=UPDATE_COUNT, block_bytes=th04_stream_block_size, processes=captured)
if th04_video_mode:
    metadata.update(layout=LAYOUT, video_symbols=th04_video_symbols)
else:
    metadata['dgroup_bytes'] = DGROUP_SIZE
(directory / (th04_stream_prefix+'-stream.json')).write_text(json.dumps(metadata, indent=2)+'\n')
gdb.write('%s_COMPLETE %d\n' % (th04_stream_marker, expected_processes))
end
quit
