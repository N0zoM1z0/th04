"""Read live PC-98 font, raw video and DGROUP at declared unchanged boundaries.

TH04_FONT_PLAN names a checked-in or private JSON plan containing frames and
the independently attested font-layout path/hash. This observer performs reads
only. Its caller must include the plan, layout and this module in its capture
source closure and reject missing checkpoints before publishing a receipt.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import gdb

def install(scope):
    from th04_demo_video import VideoRam
    plan_path=Path(os.environ['TH04_FONT_PLAN']).resolve()
    plan_bytes=plan_path.read_bytes();plan=json.loads(plan_bytes)
    frames=plan['frames']
    if not frames or frames!=sorted(set(frames)) or any(type(f) is not int or not 1<=f<=65535 for f in frames):
        raise ValueError('font checkpoint frame plan')
    layout_path=Path(plan['layout_path']).resolve();layout_bytes=layout_path.read_bytes()
    if hashlib.sha256(layout_bytes).hexdigest()!=plan['layout_sha256']:raise ValueError('font layout identity')
    layout=json.loads(layout_bytes)
    if not layout['passed']:raise ValueError('font layout was not attested')
    offset=layout['layout']['font_offset'];size=layout['layout']['font_bytes']
    if (offset,size,layout['layout']['vga_size'])!=(312,528384,535896):raise ValueError('font layout extent')
    capture=VideoRam.capture
    def observed(self,stage):
        block,mapping=capture(self,stage);monitor=scope.get('monitor')
        if monitor is None or monitor.current is None:return block,mapping
        group=monitor.ram.read_range(monitor.current.linear,65536)[0]
        frame=int.from_bytes(group[0x538a:0x538c],'little')
        if frame not in frames:return block,mapping
        directory=monitor.output/'font-checkpoints';directory.mkdir(exist_ok=True);path=directory/str(frame)
        before=monitor.ram.state();inferior=gdb.selected_inferior()
        registers=bytes(inferior.read_memory(monitor.address('cpu_regs'),48))
        segments=bytes(inferior.read_memory(monitor.address('Segs'),136))
        font=self.read(self.symbols['vga']+offset,size)
        if (before!=monitor.ram.state() or registers!=bytes(inferior.read_memory(monitor.address('cpu_regs'),48))
                or segments!=bytes(inferior.read_memory(monitor.address('Segs'),136))):
            raise ValueError('font observation changed CPU context')
        for suffix,data in (('-font.bin.gz',font),('-video.bin.gz',block),('-dgroup.bin.gz',group)):
            destination=Path(str(path)+suffix)
            with destination.open('xb') as stream:stream.write(gzip.compress(data,mtime=0))
        digest=lambda data:hashlib.sha256(data).hexdigest()
        row=dict(frame=frame,load_segment=monitor.current.load,dgroup_segment=monitor.current.dgroup,
                 vga_address=self.symbols['vga'],font_offset=offset,font_bytes=size,font_sha256=digest(font),
                 video_sha256=digest(block),dgroup_sha256=digest(group),registers=registers.hex(),
                 segments=segments.hex(),cpu_state=before,unchanged_context=True,
                 layout_sha256=digest(layout_bytes),plan_sha256=digest(plan_bytes))
        with Path(str(path)+'.json').open('x') as stream:json.dump(row,stream,indent=2);stream.write('\n')
        gdb.write('FONT_CHECKPOINT '+str(frame)+'\n');return block,mapping
    VideoRam.capture=observed
