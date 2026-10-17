"""Read sparse full fonts/video/RAM at original MAIN score-return boundaries.

The ordinary keyboard adapter supplies real device events. By default this
monitor reads only the frame counter between checkpoints. An explicit plan can
also stream complete DGROUP at the frame write of one declared input stage.
The separately pinned C++ observer retains actual loop samples and RNG calls.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import gdb
from th04_demo_video import VideoRam, SYMBOL_SIZES


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Monitor:
    def __init__(self, output, ram):
        self.output, self.ram = Path(output), ram
        self.profile = json.loads((self.output/'profile.json').read_text())
        self.plan = json.loads((self.output/'font-plan.json').read_text())
        self.wanted = {tuple(point) for point in self.plan['points']}
        self.observed = []
        self.current = self.terminal = self.error = None
        self.dialog_requested = self.continue_requested = self.quit_requested = False
        self.ui_point = None
        self.input_plan = None
        self.actor_stream = None
        if 'actor_dgroup' in self.plan:
            from th04_sparse_actor_gdb import ActorStream
            self.actor_stream = ActorStream(self)
        self.process = self.address('th04_demo_observer::process')
        self.load = self.address('th04_demo_observer::load_segment')
        self.video = VideoRam(gdb.selected_inferior().read_memory,
                              {name:self.address(name) for name in SYMBOL_SIZES})
        self.loader = Load(self)

    def address(self, name):
        return int(gdb.parse_and_eval("(void *)&'"+name+"'"))

    def number(self, offset, size):
        return int.from_bytes(self.ram.read_range(self.current.linear+offset,size)[0], 'little')

    def context(self):
        inferior = gdb.selected_inferior()
        return (self.ram.state(),
                bytes(inferior.read_memory(self.address('cpu_regs'),48)),
                bytes(inferior.read_memory(self.address('Segs'),136)))

    def finish(self):
        assert not self.error and not self.wanted and self.terminal is not None
        if self.input_plan is not None:self.input_plan.finish()
        if self.actor_stream is not None:self.actor_stream.finish()
        row = dict(complete=True, observations=self.observed,
                   terminal=self.terminal, natural_game_exit=False,
                   scope='Read-only completed score-return font/video/RAM samples. Ordinary keyboard input; no guest state assignments. Instantaneous display projection, not physical scanout or campaign equivalence.')
        (self.output/'sparse-fonts.json').write_text(json.dumps(row,indent=2)+'\n')
        gdb.write('TH04_SPARSE_FONTS_COMPLETE\n')


class Load(gdb.Breakpoint):
    def __init__(self, monitor):
        self.monitor = monitor
        super().__init__('*(unsigned int *)%d'%monitor.process,
                         type=gdb.BP_WATCHPOINT,internal=True)

    def stop(self):
        m=self.monitor
        try:
            assert m.ram.integer(m.process,4)==1 and m.current is None, 'unexpected MAIN generation'
            load=m.ram.integer(m.load,4);ds=load+m.profile['dgroup']
            m.current=SimpleNamespace(load=load,dgroup=ds,linear=ds*16,
                                      sequence=SimpleNamespace(frames=0))
            self.enabled=False
            m.score=Score(m)
            m.frame=Frame(m)
            if m.input_plan is not None:m.input_plan.bind()
            return False
        except Exception as error:
            m.error=repr(error);return True


class Frame(gdb.Breakpoint):
    def __init__(self, monitor):
        self.monitor=monitor;self.previous=0
        self.stage=monitor.number(0x5394,1) if monitor.number(0x538a,2)==0 else None
        linear=monitor.current.linear+0x538a
        host=monitor.ram.state()[0]+monitor.ram.physical(linear)
        super().__init__('*(unsigned short *)%d'%host,
                         type=gdb.BP_WATCHPOINT,internal=True)

    def stop(self):
        m=self.monitor
        try:
            frame=m.number(0x538a,2);stage=m.number(0x5394,1)
            # Loader/BSS writes precede the first real frame increment.
            if frame==0:
                self.previous=0;self.stage=stage;m.current.sequence.frames=0
                return False
            if self.stage is None:return False
            assert stage in (0,1,2) and frame==self.previous+1, (stage,frame,self.stage,self.previous)
            self.stage=stage;self.previous=frame;m.current.sequence.frames=frame
            if m.actor_stream is not None:m.actor_stream.observe(stage,frame)
            m.score.enabled=(stage,frame) in m.wanted
            if frame%1000==0:gdb.write('SPARSE_FRAME %d %d\n'%(stage,frame))
            for cue in m.plan['ui_cues']:
                if (stage,frame)==(cue['stage'],cue['frame']):
                    m.ui_point=cue
                    m.dialog_requested=cue['kind']=='dialogue'
                    m.continue_requested=cue['kind']=='continue'
                    return True
            return False
        except Exception as error:
            m.error=repr(error);return True


class Score(gdb.Breakpoint):
    def __init__(self, monitor):
        self.monitor=monitor
        self.linear=(monitor.current.load+0xaaf)*16+0x207
        host=monitor.ram.state()[0]+monitor.ram.physical(self.linear)
        super().__init__('*(unsigned char *)%d'%host,type=gdb.BP_WATCHPOINT,
                         wp_class=gdb.WP_READ,internal=True)
        self.enabled=False

    def stop(self):
        m=self.monitor
        try:
            before=m.context();state,regs,segs=before
            cs=int.from_bytes(segs[8:16],'little');ds=int.from_bytes(segs[24:32],'little')
            ip=int.from_bytes(regs[32:36],'little')&65535
            if (cs,ip)!=(m.current.load+0xaaf,0x207):return False
            assert ds==m.current.dgroup, 'score DGROUP'
            group,pages,_=m.ram.read_range(m.current.linear,65536)
            stage=group[0x5394];frame=int.from_bytes(group[0x538a:0x538c],'little');point=(stage,frame)
            assert point in m.wanted, 'undeclared score capture'
            video,mapping=m.video.capture(stage)
            font=m.video.read(m.video.symbols['vga']+312,528384)
            memory,ram_pages,_=m.ram.read_range(0,655360)
            assert group==memory[m.current.linear:m.current.linear+65536]
            assert before==m.context(), 'observation changed CPU context'
            stem='stage%d-%d'%(stage+1,frame);directory=m.output/'checkpoints';directory.mkdir(exist_ok=True)
            hashes={}
            for name,data in [('font',font),('video',video),('dgroup',group),('memory',memory)]:
                path=directory/(stem+'-'+name+'.bin.gz')
                with path.open('xb') as stream:stream.write(gzip.compress(data,compresslevel=1,mtime=0))
                hashes[name]=dict(sha256=digest(data),size=len(data),file_sha256=digest(path.read_bytes()))
            row=dict(stage=stage,frame=frame,stem=stem,load_segment=m.current.load,dgroup_segment=ds,
                     cs=cs,ip=ip,registers=regs.hex(),segments=segs.hex(),cpu_state=state,
                     opcode=m.ram.read_range(self.linear,16)[0].hex(),hashes=hashes,
                     video_mapping=mapping,dgroup_pages=pages,ram_pages=ram_pages,
                     lcg_calls=m.ram.integer(m.address('th04_demo_observer::lcg_count'),8),
                     ring_calls=m.ram.integer(m.address('th04_demo_observer::ring_count'),8),
                     unchanged_context=True)
            (directory/(stem+'.json')).write_text(json.dumps(row,indent=2)+'\n')
            m.observed.append(row);m.wanted.remove(point);self.enabled=False
            gdb.write('SPARSE_FONT_CHECKPOINT '+stem+'\n')
            if not m.wanted:
                m.terminal=dict(stage=stage,frame=frame,cs=cs,ip=ip)
                return True
            return False
        except Exception as error:
            m.error=repr(error);return True
