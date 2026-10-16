"""Read-only code-fetch checkpoints around the original pre-Boss callback."""
import gzip,json,hashlib,os
from pathlib import Path
import gdb
TARGETS=[('std-transition',0x2454),('dialog-animate',0x2bfb),('dialog-run',0x2a7c),('player-update',0x5fcf)]
class Entry(gdb.Breakpoint):
 def __init__(self,monitor,index=0):
  self.monitor=monitor;self.index=index;self.label,self.offset=TARGETS[index]
  self.linear=(monitor.current.load+0xaaf)*16+self.offset
  self.host=monitor.ram.state()[0]+monitor.ram.physical(self.linear)
  super().__init__('*(unsigned char *)%d'%self.host,type=gdb.BP_WATCHPOINT,wp_class=gdb.WP_READ,internal=True)
 def stop(self):
  m=self.monitor
  try:
   registers=bytes(gdb.selected_inferior().read_memory(m.address('cpu_regs'),48));segments=bytes(gdb.selected_inferior().read_memory(m.address('Segs'),136));cs=int.from_bytes(segments[8:16],'little');ip=int.from_bytes(registers[32:36],'little')&65535
   if cs!=m.current.load+0xaaf or ip!=self.offset:raise ValueError('code-fetch checkpoint guest PC %04x:%04x expected %04x:%04x'%(cs,ip,m.current.load+0xaaf,self.offset))
   data,pages,state=m.ram.read_range(m.current.linear,65536);frame=int.from_bytes(data[0x538a:0x538c],'little');assert frame==m.dialog_frame
   folder=m.output/'dialog-checkpoints';folder.mkdir(exist_ok=True)
   (folder/(self.label+'-dgroup.bin')).write_bytes(data)
   (folder/(self.label+'-memory.bin.gz')).write_bytes(gzip.compress(m.ram.read_range(0,655360)[0],mtime=0))
   from th04_demo_video import VideoRam,LAYOUT,SYMBOL_SIZES
   layout=json.loads(Path(os.environ['TH04_DIALOG_VIDEO_LAYOUT']).read_text());assert layout['passed'] and layout['layout']==LAYOUT
   symbols={name:m.address(name) for name in SYMBOL_SIZES};assert len({symbols[name]-layout['symbols'][name]['address'] for name in SYMBOL_SIZES})==1
   block,mapping=VideoRam(gdb.selected_inferior().read_memory,symbols).capture(data[0x5394]);(folder/(self.label+'-video.bin.gz')).write_bytes(gzip.compress(block,mtime=0))
   assert registers==bytes(gdb.selected_inferior().read_memory(m.address('cpu_regs'),48)) and segments==bytes(gdb.selected_inferior().read_memory(m.address('Segs'),136))
   row=dict(schema_version=1,ordinal=self.index,label=self.label,frame=frame,load_segment=m.current.load,dgroup_segment=m.current.dgroup,cs=cs,ip=ip,watched_guest_linear=self.linear,watched_host=self.host,opcode=m.ram.read_range(self.linear,16)[0].hex(),cpu_regs=registers.hex(),segments=segments.hex(),dgroup_sha256=hashlib.sha256(data).hexdigest(),video_sha256=hashlib.sha256(block).hexdigest(),video_mapping=mapping,unchanged_context=True,key_det=int.from_bytes(data[0x3974:0x3976],'little'),player_pos=data[0x464e:0x4652].hex(),shot_time=data[0x4666])
   (folder/(self.label+'.json')).write_text(json.dumps(row,indent=2)+'\n');gdb.write('DIALOG_CHECKPOINT '+self.label+' '+str(row['key_det'])+'\n')
   self.enabled=False
   if self.index+1<len(TARGETS):m.dialog_entry_watch=Entry(m,self.index+1)
   return False
  except Exception as error:m.error=str(error);return True
