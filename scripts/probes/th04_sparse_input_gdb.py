"""Replay declared ordinary device edges one observed loop ahead.

This retains the v1462 transport contract while reading small fields between
edges. Full RAM/CPU/tick checks surround real KEYBOARD_AddKey calls. The target
stage's completed initialization enables loop and unexpected-GameOver watches.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path

import gdb

from th04_stage_input_plan import parse_stage_input

KEYS=[(1,'KBD_up'),(2,'KBD_down'),(4,'KBD_left'),(8,'KBD_right'),
      (16,'KBD_x'),(32,'KBD_z')]


class Fetch(gdb.Breakpoint):
    def __init__(self, owner, kind, point, enabled=False):
        self.owner,self.kind,self.point=owner,kind,point
        m=owner.monitor;linear=(m.current.load+point['segment'])*16+point['offset']
        self.linear=linear
        host=m.ram.state()[0]+m.ram.physical(linear)
        super().__init__('*(unsigned char *)%d'%host,type=gdb.BP_WATCHPOINT,
                         wp_class=gdb.WP_READ,internal=True)
        self.enabled=enabled

    def stop(self):
        d=self.owner;m=d.monitor
        try:
            _,regs,segs=m.context()
            cs=int.from_bytes(segs[8:16],'little');ip=int.from_bytes(regs[32:36],'little')&65535
            if (cs,ip)!=(m.current.load+self.point['segment'],self.point['offset']):return False
            assert int.from_bytes(segs[24:32],'little')==m.current.dgroup, 'input observer DGROUP'
            if self.kind=='init':
                stage=m.field('stage');frame=m.field('frame')
                d.initializations.append(dict(stage=stage,frame=frame,cs=cs,ip=ip,
                    registers=regs.hex(),segments=segs.hex(),opcode=m.ram.read_range(self.linear,16)[0].hex()))
                if stage==d.stage:
                    assert frame==0 and not d.active, 'input starts at own completed stage initialization'
                    if m.actor_stream is not None:m.actor_stream.initialize(stage)
                    self.enabled=False;d.active=True;d.loop.enabled=True;d.guard.enabled=True
                    d.save(False)
                return False
            if self.kind=='guard':
                self.enabled=False;d.guard_fired=True
                raise ValueError('actual unexpected GameOver entry at frame '+str(m.field('frame')))
            return d.after_loop()
        except Exception as error:
            return d.fail(error)


class SparseInput:
    def __init__(self, monitor, scope):
        self.monitor,self.scope=monitor,scope
        self.path=Path(os.environ['TH04_SPARSE_STAGE_INPUT'])
        raw=self.path.read_bytes();self.digest=hashlib.sha256(raw).hexdigest()
        self.version,self.stage,self.extent,self.inputs,self.expected=parse_stage_input(raw)
        self.keys=KEYS+([(4096,'KBD_esc')] if self.version==2 else [])
        self.physical_readback_differences=[]
        self.pending=[];self.actions=[];self.initializations=[]
        self.observed=0;self.active=False;self.bound=False;self.guard_fired=False;self.held=None

    def bind(self):
        m=self.monitor;assert m.current is not None and not self.bound
        profile=m.profile
        self.offsets={name:(off,size) for name,off,size in profile['fields']}
        self.stream=(m.output/'stage-input-loops.jsonl').open('x')
        hook=next(h for h in profile['hooks'] if h[0]==1)
        self.loop=Fetch(self,'loop',dict(segment=hook[1],offset=hook[2]))
        self.guard=Fetch(self,'guard',profile['stage3_gameover_guard'])
        self.entry=Fetch(self,'init',profile['entries']['init_return'],True)
        self.bound=True;self.save(False)

    def after_loop(self):
        m=self.monitor
        def number(name):
            off,size=self.offsets[name];return m.number(off,size)
        stage,frame,actual=number('stage'),number('frame'),number('input')
        assert self.active and stage==self.stage and frame==self.observed and frame<self.extent, 'input stage/frame order'
        assert actual==self.expected[frame], ('actual input differs',frame,actual,self.expected[frame])
        if actual!=self.inputs[frame]:
            self.physical_readback_differences.append(dict(frame=frame,physical=self.inputs[frame],actual=actual))
        self.stream.write(json.dumps(dict(stage=stage,frame=frame,actual=actual,
            expected=self.expected[frame],physical=self.inputs[frame],tick=self.scope['tick']()))+'\n');self.stream.flush()
        self.observed+=1
        if self.held is None:
            self.held={name:False for _,name in self.keys}
            for action in self.scope['actions']:
                if action['key'] in self.held:self.held[action['key']]=action['pressed']
            assert sum(bit for bit,name in self.keys if self.held[name])==self.inputs[0], 'initial physical keys'
        if frame+1<self.extent:
            wanted=self.inputs[frame+1]
            self.pending=[(name,False,frame+1) for bit,name in self.keys if self.held[name] and not wanted&bit]
            self.pending += [(name,True,frame+1) for bit,name in self.keys if not self.held[name] and wanted&bit]
        return bool(self.pending)

    def flush(self):
        m=self.monitor;clock=self.scope['clock'];valid=clock.is_valid();enabled=clock.enabled if valid else False
        if valid:clock.enabled=False
        try:
            for name,down,frame in self.pending:
                before=self.scope['snapshot']();tick=self.scope['tick']();memory=m.ram.read_range(0,655360)[0]
                gdb.execute('call ((void (*)(int, bool))0x%x)(%d, %s)'%
                    (self.scope['function'],self.scope['keys'][name],'true' if down else 'false'),to_string=True)
                assert tick==self.scope['tick']() and before==self.scope['snapshot']()
                assert memory==m.ram.read_range(0,655360)[0], 'keyboard call changed conventional RAM'
                self.held[name]=down;self.actions.append(dict(stage=self.stage,next_loop_frame=frame,
                    key=name,pressed=down,tick=tick,unchanged_guest=True,
                    conventional_memory_sha256=hashlib.sha256(memory).hexdigest()))
            self.pending=[];self.save(False)
        finally:
            if valid:clock.enabled=enabled

    def fail(self, error):
        m=self.monitor;memory=m.ram.read_range(0,655360)[0]
        (m.output/'stage-input-error-memory.bin.gz').write_bytes(gzip.compress(memory,compresslevel=1,mtime=0))
        (m.output/'stage-input-error.json').write_text(json.dumps(dict(error=repr(error),
            stage=self.stage,next_expected_loop=self.observed,context=[m.context()[0],m.context()[1].hex(),m.context()[2].hex()],
            memory_sha256=hashlib.sha256(memory).hexdigest()),indent=2)+'\n')
        m.error='sparse physical input: '+repr(error);self.save(False);return True

    def save(self, complete):
        row=dict(complete=complete,stage=self.stage,extent=self.extent,observed_loops=self.observed,
            plan_version=self.version,physical_readback_differences=self.physical_readback_differences,
            plan_sha256=self.digest,actions=self.actions,initializations=self.initializations,
            gameover_guard_registered=int(self.bound),gameover_guard_fired=self.guard_fired,
            scope='Actual keyboard API edges queued one observed loop ahead;each actual latch strictly matches its declared expectation. V2 keeps physical intent/readback differences explicit. Every call preserves CPU,tick and complete640KiB RAM. Own completed stage initialization activates loop/guard watches;no gameplay,RNG,clock or key_det assignment.')
        (self.monitor.output/'stage-input.json').write_text(json.dumps(row,indent=2)+'\n')

    def finish(self):
        assert self.bound and self.active and not self.pending and not self.guard_fired and self.observed==self.extent
        assert hashlib.sha256(self.path.read_bytes()).hexdigest()==self.digest
        self.loop.enabled=False;self.guard.enabled=False;self.stream.close();self.save(True)
