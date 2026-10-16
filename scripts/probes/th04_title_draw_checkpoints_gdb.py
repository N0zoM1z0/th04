"""Observe actual original BB entry arguments; never reconstruct an earlier scroll.

Enable a read-only code-fetch watch only for updates declared by TH04_FONT_PLAN.
Each event binds CS:IP, argument registers, stack, DS scroll/frame and unchanged
CPU context. The paired after-update snapshot records zero-call frames too.
"""
import hashlib,json,os
from pathlib import Path
import gdb

class Entry(gdb.Breakpoint):
    def __init__(self,monitor,frames):
        self.monitor=monitor;self.frames=set(frames);self.counts={};self.seen={};self.digest=hashlib.sha256();self.events=0
        self.linear=(monitor.current.load+0xaaf)*16+0x15aa
        self.host=monitor.ram.state()[0]+monitor.ram.physical(self.linear)
        super().__init__('*(unsigned char *)%d'%self.host,type=gdb.BP_WATCHPOINT,wp_class=gdb.WP_READ,internal=True)
        self.enabled=False
    def stop(self):
        monitor=self.monitor
        try:
            before=monitor.ram.state();inferior=gdb.selected_inferior()
            regs=bytes(inferior.read_memory(monitor.address('cpu_regs'),48));segs=bytes(inferior.read_memory(monitor.address('Segs'),136))
            cs=int.from_bytes(segs[8:16],'little');ds=int.from_bytes(segs[24:32],'little');ss=int.from_bytes(segs[16:24],'little');ip=int.from_bytes(regs[32:36],'little')&65535
            if cs!=monitor.current.load+0xaaf or ip!=0x15aa or ds!=monitor.current.dgroup:raise ValueError('BB instruction-fetch context')
            read=lambda at,size:monitor.ram.read_range(monitor.current.linear+at,size)[0]
            stage_frame=int.from_bytes(read(0x538a,2),'little');frame=stage_frame+1
            if frame not in self.frames:raise ValueError('BB entry outside declared update')
            sp=int.from_bytes(regs[16:20],'little')&65535;stack=monitor.ram.read_range(ss*16+sp,16)[0]
            row=dict(frame=frame,stage_frame=stage_frame,load_segment=monitor.current.load,dgroup_segment=ds,cs=cs,ip=ip,opcode=monitor.ram.read_range(self.linear,16)[0].hex(),
                     left=int.from_bytes(regs[0:2],'little'),top=int.from_bytes(regs[8:10],'little'),sprite=int.from_bytes(regs[4:6],'little'),scroll_line=int.from_bytes(read(0x4278,2),'little'),
                     registers=regs.hex(),segments=segs.hex(),stack=stack.hex(),watched_guest_linear=self.linear,watched_host=self.host,unchanged_context=True)
            if before!=monitor.ram.state() or regs!=bytes(inferior.read_memory(monitor.address('cpu_regs'),48)) or segs!=bytes(inferior.read_memory(monitor.address('Segs'),136)):raise ValueError('BB observation changed context')
            encoded=(json.dumps(row,separators=(',',':'))+'\n').encode()
            with (monitor.output/'title-draws.jsonl').open('ab') as stream:stream.write(encoded)
            self.digest.update(encoded);self.events+=1;self.counts[frame]=self.counts.get(frame,0)+1
            return False
        except Exception as error:monitor.error=str(error);return True
    def boundary(self,frame):
        if frame in self.frames:
            self.seen[frame]=self.counts.get(frame,0)
            report=dict(frames=sorted(self.frames),observed=self.seen,events=self.events,jsonl_sha256=self.digest.hexdigest(),complete=set(self.seen)==self.frames)
            (self.monitor.output/'title-draws-summary.json').write_text(json.dumps(report,indent=2)+'\n')
        self.enabled=frame+1 in self.frames

def install(scope):
    from th04_demo_video import VideoRam
    plan=json.loads(Path(os.environ['TH04_FONT_PLAN']).read_text());frames=plan['frames'];capture=VideoRam.capture;watch=None
    def observed(self,stage):
        nonlocal watch
        block,mapping=capture(self,stage);monitor=scope.get('monitor')
        if monitor is None or monitor.current is None:return block,mapping
        if watch is None:watch=Entry(monitor,frames)
        frame=int.from_bytes(monitor.ram.read_range(monitor.current.linear+0x538a,2)[0],'little')
        watch.boundary(frame);return block,mapping
    VideoRam.capture=observed
