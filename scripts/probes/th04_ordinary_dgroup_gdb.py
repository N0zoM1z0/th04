"""Read-only ordinary DGROUP monitor composed with the keyboard adapter."""
import gzip
import json
import os
from pathlib import Path

import gdb

from th04_demo_dgroup import DGROUP_SIZE, FrameSequence, HEADER, UPDATE_COUNT
from th04_ordinary_dgroup import BOUNDARY, MAGIC


class Monitor:
    def __init__(self, output, ram):
        self.output, self.ram = Path(output), ram
        self.profile = json.loads((self.output / 'profile.json').read_text())
        self.current = None
        self.error = None
        self.process = self.address('th04_demo_observer::process')
        self.load = self.address('th04_demo_observer::load_segment')
        self.active = self.address('th04_demo_observer::active')
        self.loader = Load(self)
        self.video = None
        if os.environ.get('TH04_ORDINARY_VIDEO') == '1':
            from th04_demo_video import VideoRam, LAYOUT, SYMBOL_SIZES
            layout = json.loads(Path(os.environ['TH04_ORDINARY_VIDEO_LAYOUT']).read_text())
            if not layout['passed'] or layout['layout'] != LAYOUT:
                raise ValueError('ordinary video layout')
            self.video_symbols = {name: self.address(name) for name in SYMBOL_SIZES}
            if len({self.video_symbols[name] - layout['symbols'][name]['address']
                    for name in SYMBOL_SIZES}) != 1:
                raise ValueError('ordinary video ELF mapping')
            self.video = VideoRam(gdb.selected_inferior().read_memory, self.video_symbols)

    def address(self, name):
        return int(gdb.parse_and_eval("(void *)&'" + name + "'"))

    def finish(self):
        if self.current is None:
            raise ValueError('no ordinary DGROUP process')
        self.current.stream.close()
        self.current.raw.close()
        if self.error or self.current.sequence.frames != UPDATE_COUNT:
            raise ValueError(self.error or 'incomplete ordinary DGROUP')
        record = dict(schema_version=1, complete=True, boundary=BOUNDARY,
                      frames=UPDATE_COUNT, block_bytes=DGROUP_SIZE,
                      load_segment=self.current.load, dgroup_segment=self.current.dgroup,
                      mappings=self.current.maps)
        (self.output / 'ordinary-dgroup.json').write_text(json.dumps(record, indent=2) + '\n')
        gdb.write('TH04_ORDINARY_DGROUP_COMPLETE\n')
        if self.video is not None:
            from th04_demo_video import BLOCK_SIZE, LAYOUT
            self.current.video_stream.close()
            self.current.video_raw.close()
            record.update(block_bytes=BLOCK_SIZE, layout=LAYOUT,
                          video_symbols=self.video_symbols, video_mappings=self.current.video_maps)
            (self.output / 'ordinary-video.json').write_text(json.dumps(record, indent=2) + '\n')
            gdb.write('TH04_ORDINARY_VIDEO_COMPLETE\n')


class Load(gdb.Breakpoint):
    def __init__(self, monitor):
        self.monitor = monitor
        super().__init__('*(unsigned int *)%d' % monitor.process,
                         type=gdb.BP_WATCHPOINT, internal=True)

    def stop(self):
        m = self.monitor
        if m.ram.integer(m.process, 4) != 1 or m.current is not None:
            m.error = 'unexpected ordinary MAIN process'
            return True
        m.current = Frame(m, m.ram.integer(m.load, 4))
        return False


class Frame(gdb.Breakpoint):
    def __init__(self, monitor, load):
        self.monitor, self.load = monitor, load
        self.dgroup = load + monitor.profile['dgroup']
        self.linear = self.dgroup * 16
        self.offset = monitor.profile['fields'][0][1]
        self.host = monitor.ram.state()[0] + monitor.ram.physical(self.linear + self.offset)
        self.sequence = FrameSequence(monitor.ram.integer(self.host, 2))
        self.previous = 0
        self.maps, self.last_pages = [], None
        self.raw = (monitor.output / 'ordinary-dgroup.bin.gz').open('xb')
        self.stream = gzip.GzipFile(fileobj=self.raw, mode='wb', compresslevel=1,
                                   mtime=0, filename='')
        self.stream.write(MAGIC)
        if monitor.video is not None:
            from th04_ordinary_video import MAGIC as VIDEO_MAGIC
            self.video_raw = (monitor.output / 'ordinary-video.bin.gz').open('xb')
            self.video_stream = gzip.GzipFile(fileobj=self.video_raw, mode='wb', compresslevel=1,
                                             mtime=0, filename='')
            self.video_stream.write(VIDEO_MAGIC)
            self.video_previous = 0
            self.video_maps, self.last_video_map = [], None
        super().__init__('*(unsigned short *)%d' % self.host,
                         type=gdb.BP_WATCHPOINT, internal=True)

    def stop(self):
        m = self.monitor
        try:
            if not m.ram.integer(m.active, 1):
                return False
            frame = m.ram.integer(self.host, 2)
            if not self.sequence.observe(frame):
                return False
            data, pages, state = m.ram.read_range(self.linear, DGROUP_SIZE)
            if (int.from_bytes(data[self.offset:self.offset + 2], 'little') != frame or
                    state[0] + m.ram.physical(self.linear + self.offset, state) != self.host):
                raise ValueError('ordinary frame mapping changed')
            _, cr0, cr4, cr3 = state
            self.stream.write(HEADER.pack(1, frame, self.load, self.dgroup, cr0, cr4, cr3))
            value = int.from_bytes(data, 'little')
            self.stream.write((value ^ self.previous).to_bytes(DGROUP_SIZE, 'little'))
            self.previous = value
            if m.video is not None:
                from th04_demo_video import BLOCK_SIZE
                stage = next(offset for name, offset, _ in m.profile['fields'] if name == 'stage')
                block, video_map = m.video.capture(data[stage])
                self.video_stream.write(HEADER.pack(1, frame, self.load, self.dgroup, cr0, cr4, cr3))
                value = int.from_bytes(block, 'little')
                self.video_stream.write((value ^ self.video_previous).to_bytes(BLOCK_SIZE, 'little'))
                self.video_previous = value
                if video_map != self.last_video_map:
                    self.video_maps.append(dict(first_frame=frame, **video_map))
                    self.last_video_map = video_map
            if pages != self.last_pages:
                self.maps.append(dict(first_frame=frame, pages=pages))
                self.last_pages = pages
            if frame % 500 == 0 or frame == UPDATE_COUNT:
                self.stream.flush()
                if m.video is not None:
                    self.video_stream.flush()
                gdb.write('TH04_ORDINARY_DGROUP %d\n' % frame)
            return False
        except Exception as error:
            m.error = str(error)
            return True
