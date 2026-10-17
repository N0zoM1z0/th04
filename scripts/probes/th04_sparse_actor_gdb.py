"""Optional complete DGROUP stream at the original ordinary frame-write seam.

Only the declared input stage is streamed. Video, fonts and full conventional
RAM remain sparse. The wire uses the existing TH04OG1 XOR/header layout; its
stage and bounded extent are declared separately rather than assumed to be zero.
"""
import gzip
import hashlib
import json

from th04_demo_dgroup import HEADER


class ActorStream:
    def __init__(self, monitor):
        self.monitor = monitor
        self.stage = monitor.plan['actor_dgroup']['stage']
        self.extent = monitor.plan['actor_dgroup']['extent']
        self.count = self.previous = 0
        self.initial = self.context = None
        self.stream = None
        self.path = monitor.output / 'actor-dgroup.bin.gz'

    def initialize(self, stage):
        if stage != self.stage:
            return
        m = self.monitor
        assert self.initial is None and self.stream is None
        before = m.context()
        state, regs, segs = before
        assert (int.from_bytes(segs[8:16], 'little'),
                int.from_bytes(regs[32:36], 'little') & 65535,
                int.from_bytes(segs[24:32], 'little')) == (
                    m.current.load + m.profile['entries']['init_return']['segment'],
                    m.profile['entries']['init_return']['offset'], m.current.dgroup)
        group = m.ram.read_range(m.current.linear, 65536)[0]
        assert m.field('stage') == self.stage and m.field('frame') == 0
        assert before == m.context(), 'initial actor observation changed CPU'
        path = m.output / 'actor-init-dgroup.bin.gz'
        path.write_bytes(gzip.compress(group, compresslevel=1, mtime=0))
        self.initial = dict(stage=stage, frame=0, cpu_state=state,
                            registers=regs.hex(), segments=segs.hex(),
                            sha256=hashlib.sha256(group).hexdigest(),
                            file_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        self.stream = gzip.GzipFile(filename=str(self.path), mode='xb',
                                    compresslevel=1, mtime=0)
        self.stream.write(b'TH04OG1\n')
        self.save(False)

    def observe(self, stage, frame):
        if stage != self.stage:
            return
        m = self.monitor
        assert self.initial is not None and self.stream is not None
        assert frame == self.count + 1 and frame <= self.extent
        before = m.context()
        state, regs, segs = before
        boundary = m.profile['actor_boundary']
        cs = int.from_bytes(segs[8:16], 'little')
        ip = int.from_bytes(regs[32:36], 'little') & 65535
        ds = int.from_bytes(segs[24:32], 'little')
        assert (cs, ip, ds) == (m.current.load + boundary['segment'],
                                boundary['offset'], m.current.dgroup)
        assert int.from_bytes(regs[:2], 'little') == frame, 'frame-store AX'
        opcode = m.ram.read_range(cs * 16 + ip, 16)[0]
        assert opcode.hex() == boundary['opcode'], 'actor frame-store opcode'
        group = m.ram.read_range(m.current.linear, 65536)[0]
        assert m.field('stage') == stage and m.field('frame') == frame
        assert before == m.context(), 'actor observation changed CPU'
        # HostRam.state: memory base, CR0, CR4, CR3. No host pointer enters wire.
        context = (m.current.load, ds, *state[1:])
        if self.context is None:
            self.context = context
        assert context == self.context, 'actor load/paging context changed'
        header = HEADER.pack(1, frame, *context)
        current = int.from_bytes(group, 'little')
        self.stream.write(header)
        self.stream.write((current ^ self.previous).to_bytes(65536, 'little'))
        self.previous, self.count = current, frame
        if frame % 1000 == 0:
            self.stream.flush()
            self.save(False)

    def save(self, complete):
        row = dict(complete=complete, stage=self.stage, extent=self.extent,
                   records=self.count, initial=self.initial, context=self.context,
                   boundary=self.monitor.profile['actor_boundary'],
                   wire='TH04OG1 XOR DGROUP, <HHHHIII> process/frame/load/DS/CR0/CR4/CR3',
                   scope='Read-only original frame-store seam before mod counters/score. '
                         'Every record requires own CS/IP/DS/opcode/AX/frame and unchanged CPU; '
                         'no per-frame video/font/full-conventional-RAM capture or guest assignment.')
        if complete:
            row['stream_sha256'] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        (self.monitor.output / 'actor-dgroup.json').write_text(json.dumps(row, indent=2) + '\n')

    def finish(self):
        assert self.initial is not None and self.count == self.extent
        self.stream.close()
        self.save(True)
