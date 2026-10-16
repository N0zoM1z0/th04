"""Record original BB calls over every interval following the first actor boundary.

Reuse the frozen entry observer; emit bounded progress summaries instead of
rewriting an expanding JSON object at every one of8000 update boundaries.
"""
import hashlib,json,os
from pathlib import Path
from th04_title_draw_checkpoints_gdb import Entry

class Stream(Entry):
    def boundary(self,frame):
        if frame in self.frames:self.seen[frame]=self.counts.get(frame,0)
        if frame%500==0 or frame==max(self.frames):
            report=dict(frames=sorted(self.frames),observed=self.seen,events=self.events,jsonl_sha256=self.digest.hexdigest(),complete=set(self.seen)==self.frames)
            (self.monitor.output/'title-draws-summary.json').write_text(json.dumps(report,indent=2)+'\n')
        self.enabled=frame+1 in self.frames

def install(scope):
    from th04_demo_video import VideoRam
    plan=json.loads(Path(os.environ['TH04_FONT_PLAN']).read_text());updates=plan['draw_updates']
    if type(updates) is not int or not 2<=updates<=65534:raise ValueError('title draw stream extent')
    capture=VideoRam.capture;watch=None
    def observed(self,stage):
        nonlocal watch
        block,mapping=capture(self,stage);monitor=scope.get('monitor')
        if monitor is None or monitor.current is None:return block,mapping
        frame=int.from_bytes(monitor.ram.read_range(monitor.current.linear+0x538a,2)[0],'little')
        if watch is None:
            if frame>1:raise ValueError('title draw stream attached too late')
            watch=Stream(monitor,range(2,updates+1))
        watch.boundary(frame);return block,mapping
    VideoRam.capture=observed
