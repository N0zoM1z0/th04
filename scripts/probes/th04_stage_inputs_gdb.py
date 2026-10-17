"""Queue ordinary keyboard edges one loop ahead; verify actual guest samples."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import gdb

from th04_stage_input_plan import parse_stage_input

sha = lambda value: hashlib.sha256(value).hexdigest()
KEYS = [(1, 'KBD_up'), (2, 'KBD_down'), (4, 'KBD_left'),
        (8, 'KBD_right'), (16, 'KBD_x'), (32, 'KBD_z')]


class LoopPoint(gdb.Breakpoint):
    def __init__(self, owner):
        self.owner = owner
        m = owner.monitor
        hook = next(h for h in m.profile['hooks'] if h[0] == 1)
        self.segment, self.offset = hook[1:]
        linear = (m.current.load + self.segment) * 16 + self.offset
        host = m.ram.state()[0] + m.ram.physical(linear)
        super().__init__('*(unsigned char *)%d' % host, type=gdb.BP_WATCHPOINT,
                         wp_class=gdb.WP_READ, internal=True)

    def stop(self):
        d = self.owner
        m = d.monitor
        try:
            regs = bytes(gdb.selected_inferior().read_memory(m.address('cpu_regs'), 48))
            segs = bytes(gdb.selected_inferior().read_memory(m.address('Segs'), 136))
            cs, ip = int.from_bytes(segs[8:16], 'little'), int.from_bytes(regs[32:36], 'little') & 65535
            if (cs, ip) != (m.current.load + self.segment, self.offset):
                return False
            return d.after_loop()
        except Exception as error:
            return d.fail(error)



class GameOverGuard(gdb.Breakpoint):
    def __init__(self, owner, point):
        self.owner,self.point=owner,point
        m=owner.monitor
        linear=(m.current.load+point['segment'])*16+point['offset']
        host=m.ram.state()[0]+m.ram.physical(linear)
        super().__init__('*(unsigned char *)%d'%host,type=gdb.BP_WATCHPOINT,
                         wp_class=gdb.WP_READ,internal=True)
        self.enabled=False
    def stop(self):
        d=self.owner;m=d.monitor
        regs=bytes(gdb.selected_inferior().read_memory(m.address('cpu_regs'),48))
        segs=bytes(gdb.selected_inferior().read_memory(m.address('Segs'),136))
        cs,ip=int.from_bytes(segs[8:16],'little'),int.from_bytes(regs[32:36],'little')&65535
        if (cs,ip)!=(m.current.load+self.point['segment'],self.point['offset']):return False
        self.enabled=False;d.guard_fired=True
        memory=m.ram.read_range(0,655360)[0]
        off,size=d.offsets['frame'];frame=int.from_bytes(memory[m.current.linear+off:m.current.linear+off+size],'little')
        path=m.output/'stage-input-gameover-memory.bin.gz'
        path.write_bytes(gzip.compress(memory,mtime=0,compresslevel=1))
        (m.output/'stage-input-gameover.json').write_text(json.dumps(dict(frame=frame,
            load_segment=m.current.load,dgroup_segment=m.current.dgroup,cpu_regs=regs.hex(),segments=segs.hex(),
            cs=cs,ip=ip,memory_sha256=sha(memory),scope='Actual own-MZ GameOver entry before blocking UI. This is a stopped incomplete route, not a timeout or a gameplay repair.'),indent=2)+'\n')
        m.error='actual Stage3 GameOver entry before configured completion at frame '+str(frame)
        d.save(False)
        return True

class InputPlan:
    def __init__(self, scope):
        self.scope = scope
        self.bound = False
        self.pending = []
        self.actions = []
        self.observed = 0
        self.held = None
        self.external = os.environ.get('TH04_STAGE_INPUT_EXTERNAL') == '1'
        self.path = Path(os.environ['TH04_STAGE_INPUT_PLAN'])
        raw = self.path.read_bytes()
        self.digest = sha(raw)
        self.version, self.stage, self.extent, self.inputs, self.expected = parse_stage_input(raw)
        self.keys = KEYS + ([(4096, 'KBD_esc')] if self.version == 2 else [])
        self.physical_readback_differences = []
        self.point = None
        self.guard = None
        self.guard_fired = False

    def bind(self, monitor):
        if self.bound or monitor is None or getattr(monitor, 'current', None) is None:
            return
        self.monitor = monitor
        self.offsets = {name: (off, size) for name, off, size in monitor.profile['fields']}
        self.stream = (monitor.output / 'stage-input-loops.jsonl').open('x')
        if self.external:
            profiles=json.loads(Path(os.environ['TH04_STAGE_BOUNDARY_PROFILES']).read_text())
            matches=[p for p in profiles.values() if p['dgroup']==monitor.profile['dgroup'] and p['signature']==monitor.profile['signature']]
            assert len(matches)==1 and matches[0]['stage3_input_sha256']==self.digest
            self.guard=GameOverGuard(self,matches[0]['stage3_gameover_guard'])
        self.bound = True
        if not self.external:
            self.point = LoopPoint(self)
        self.save(False)

    def after_loop(self):
        m = self.monitor
        group = m.ram.read_range(m.current.linear, 65536)[0]
        def number(name):
            off, size = self.offsets[name]
            return int.from_bytes(group[off:off + size], 'little')
        stage, frame, actual = number('stage'), number('frame'), number('input')
        if stage != self.stage:
            return False
        if self.guard is not None:self.guard.enabled=True
        assert frame == self.observed and frame < self.extent, 'input schedule observed stage/frame order'
        assert actual == self.expected[frame], 'input schedule actual loop sample differs at %d: %d != %d' % (frame, actual, self.expected[frame])
        if actual != self.inputs[frame]:
            self.physical_readback_differences.append(dict(frame=frame, physical=self.inputs[frame], actual=actual))
        self.stream.write(json.dumps(dict(stage=stage, frame=frame, actual=actual,
            expected=self.expected[frame], physical=self.inputs[frame], tick=self.scope['tick']())) + '\n')
        self.stream.flush()
        self.observed += 1
        if self.held is None:
            self.held = {name: False for _, name in self.keys}
            for action in self.scope['actions']:
                if action['key'] in self.held:
                    self.held[action['key']] = action['pressed']
            assert sum(bit for bit, name in self.keys if self.held[name]) == self.inputs[0], 'input schedule initial physical key ownership'
        if frame + 1 < self.extent:
            wanted = self.inputs[frame + 1]
            # Release old directions before pressing their replacements.
            self.pending = [(name, False, frame + 1) for bit, name in self.keys if self.held[name] and not wanted & bit]
            self.pending += [(name, True, frame + 1) for bit, name in self.keys if not self.held[name] and wanted & bit]
        return bool(self.pending)

    def flush(self):
        m = self.monitor
        clock = self.scope['clock']
        valid_clock = clock.is_valid()
        enabled = clock.enabled if valid_clock else False
        if valid_clock:clock.enabled = False
        try:
            for name, down, frame in self.pending:
                before = self.scope['snapshot']()
                tick = self.scope['tick']()
                memory = m.ram.read_range(0, 655360)[0]
                gdb.execute('call ((void (*)(int, bool))0x%x)(%d, %s)' %
                    (self.scope['function'], self.scope['keys'][name], 'true' if down else 'false'), to_string=True)
                assert tick == self.scope['tick']() and before == self.scope['snapshot']()
                assert memory == m.ram.read_range(0, 655360)[0], 'keyboard API changed conventional RAM'
                self.held[name] = down
                self.actions.append(dict(stage=self.stage, next_loop_frame=frame, key=name, pressed=down,
                    tick=tick, unchanged_guest=True, conventional_memory_sha256=sha(memory)))
            self.pending = []
            self.save(False)
        finally:
            if valid_clock:clock.enabled = enabled

    def fail(self, error):
        m = self.monitor
        memory = m.ram.read_range(0, 655360)[0]
        (m.output / 'stage-input-error-memory.bin.gz').write_bytes(gzip.compress(memory, mtime=0, compresslevel=1))
        registers = bytes(gdb.selected_inferior().read_memory(m.address('cpu_regs'), 48))
        segments = bytes(gdb.selected_inferior().read_memory(m.address('Segs'), 136))
        (m.output / 'stage-input-error.json').write_text(json.dumps(dict(error=repr(error), stage=self.stage,
            next_expected_frame=self.observed, memory_sha256=sha(memory),
            load_segment=m.current.load, cpu_regs=registers.hex(), segments=segments.hex(),
            cs=int.from_bytes(segments[8:16], 'little'), ip=int.from_bytes(registers[32:36], 'little') & 65535), indent=2) + '\n')
        m.error = 'stage input transport: ' + repr(error)
        return True

    def save(self, complete):
        (self.monitor.output / 'stage-input.json').write_text(json.dumps(dict(complete=complete,
            stage=self.stage, extent=self.extent, observed_loops=self.observed, plan_path=str(self.path),
            plan_version=self.version, physical_readback_differences=self.physical_readback_differences,
            plan_sha256=self.digest, actions=self.actions, external_loop_owner=self.external, gameover_guard_registered=int(self.guard is not None), gameover_guard_fired=self.guard_fired,
            scope='Actual ordinary KEYBOARD_AddKey device edges queued one observed loop ahead. Each actual latch strictly matches the frozen expected word. V2 keeps physical intent/readback differences explicit. Calls preserve CPU/context, tick and all 640 KiB conventional RAM; no gameplay/RNG/clock/key_det assignment.'), indent=2) + '\n')

    def checked_loop(self):
        try:return self.after_loop()
        except Exception as error:return self.fail(error)

    def finish(self):
        assert self.bound and not self.pending and self.observed == self.extent and not self.guard_fired
        if self.guard is not None:self.guard.enabled=False
        assert sha(self.path.read_bytes()) == self.digest
        self.stream.close()
        self.save(True)
