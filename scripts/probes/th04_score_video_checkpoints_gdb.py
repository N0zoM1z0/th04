"""Read complete original display/font/DGROUP after actual score return0AAF:0207."""
import gzip,hashlib,json,os
from pathlib import Path
import gdb

class Entry(gdb.Breakpoint):
    def __init__(self,monitor,plan,raw_capture):
        from th04_demo_video import VideoRam,SYMBOL_SIZES
        self.monitor=monitor;self.frames=set(plan['frames']);self.raw_capture=raw_capture
        self.plan_bytes=Path(os.environ['TH04_FONT_PLAN']).read_bytes();self.plan=plan
        self.video=VideoRam(gdb.selected_inferior().read_memory,{name:monitor.address(name) for name in SYMBOL_SIZES})
        self.linear=(monitor.current.load+0xaaf)*16+0x207
        self.host=monitor.ram.state()[0]+monitor.ram.physical(self.linear)
        super().__init__('*(unsigned char *)%d'%self.host,type=gdb.BP_WATCHPOINT,wp_class=gdb.WP_READ,internal=True)
        self.enabled=False
    def stop(self):
        monitor=self.monitor
        try:
            before=monitor.ram.state();inferior=gdb.selected_inferior()
            regs=bytes(inferior.read_memory(monitor.address('cpu_regs'),48));segs=bytes(inferior.read_memory(monitor.address('Segs'),136))
            cs=int.from_bytes(segs[8:16],'little');ds=int.from_bytes(segs[24:32],'little');ip=int.from_bytes(regs[32:36],'little')&65535
            if (cs,ip,ds)!=(monitor.current.load+0xaaf,0x207,monitor.current.dgroup):raise ValueError('score-return instruction-fetch context')
            group=monitor.ram.read_range(monitor.current.linear,65536)[0];frame=int.from_bytes(group[0x538a:0x538c],'little')
            if frame not in self.frames:raise ValueError('score video outside declared update')
            block,mapping=self.raw_capture(self.video,group[0x5394]);font=self.video.read(self.video.symbols['vga']+312,528384)
            if before!=monitor.ram.state() or regs!=bytes(inferior.read_memory(monitor.address('cpu_regs'),48)) or segs!=bytes(inferior.read_memory(monitor.address('Segs'),136)):raise ValueError('score video changed context')
            path=monitor.output/'post-score-checkpoints'/str(frame);path.parent.mkdir(exist_ok=True)
            for suffix,data in (('-font.bin.gz',font),('-video.bin.gz',block),('-dgroup.bin.gz',group)):
                with Path(str(path)+suffix).open('xb') as stream:stream.write(gzip.compress(data,mtime=0))
            digest=lambda data:hashlib.sha256(data).hexdigest();row=dict(frame=frame,load_segment=monitor.current.load,dgroup_segment=ds,cs=cs,ip=ip,opcode=monitor.ram.read_range(self.linear,16)[0].hex(),registers=regs.hex(),segments=segs.hex(),font_offset=312,font_bytes=len(font),font_sha256=digest(font),video_sha256=digest(block),dgroup_sha256=digest(group),plan_sha256=digest(self.plan_bytes),layout_sha256=self.plan['layout_sha256'],unchanged_context=True,video_mapping=mapping)
            with Path(str(path)+'.json').open('x') as stream:json.dump(row,stream,indent=2);stream.write('\n')
            self.enabled=False;gdb.write('SCORE_VIDEO_CHECKPOINT '+str(frame)+'\n');return False
        except Exception as error:monitor.error=str(error);return True

def install(scope):
    from th04_demo_video import VideoRam
    plan=json.loads(Path(os.environ['TH04_FONT_PLAN']).read_text());raw_capture=VideoRam.capture;watch=None
    def observed(self,stage):
        nonlocal watch
        block,mapping=raw_capture(self,stage);monitor=scope.get('monitor')
        if monitor is None or monitor.current is None:return block,mapping
        if watch is None:watch=Entry(monitor,plan,raw_capture)
        frame=int.from_bytes(monitor.ram.read_range(monitor.current.linear+0x538a,2)[0],'little');watch.enabled=frame in watch.frames
        return block,mapping
    VideoRam.capture=observed
