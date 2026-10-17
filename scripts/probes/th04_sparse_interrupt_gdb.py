"""Read a stopped emulator's guest CPU/RAM on the collector deadline interrupt."""
import gzip,hashlib,json
import gdb

def install(monitor):
 def stopped(event):
  if getattr(event,'stop_signal',None)!='SIGINT':return
  m=monitor;row=dict(complete_capture=False,reason='collector deadline SIGINT',signal='SIGINT')
  try:
   before=m.context();state,regs,segs=before;cs=int.from_bytes(segs[8:16],'little');ds=int.from_bytes(segs[24:32],'little');ip=int.from_bytes(regs[32:36],'little')&65535
   memory,pages,_=m.ram.read_range(0,655360);opcode=m.ram.read_range(cs*16+ip,32)[0];assert before==m.context(),'deadline observation changed CPU'
   path=m.output/'interrupt-memory.bin.gz';path.write_bytes(gzip.compress(memory,compresslevel=1,mtime=0));row.update(cpu_state=state,registers=regs.hex(),segments=segs.hex(),cs=cs,ip=ip,ds=ds,opcode=opcode.hex(),memory_sha256=hashlib.sha256(memory).hexdigest(),memory_file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),memory_pages=pages,unchanged_context=True,process=m.ram.integer(m.process,4))
   if m.current is not None:row.update(load_segment=m.current.load,dgroup_segment=m.current.dgroup,stage=m.field('stage'),frame=m.field('frame'))
  except Exception as error:row['diagnostic_error']=repr(error)
  row['scope']='Read-only guest CPU/full640KiB RAM at a host deadline interrupt,not a normal game boundary or completed capture. No guest,clock,RNG or key assignment.'
  (m.output/'interrupt-diagnostic.json').write_text(json.dumps(row,indent=2)+'\n');m.error='collector deadline interrupt;diagnostic saved';gdb.write('TH04_DEADLINE_DIAGNOSTIC_SAVED\n')
 gdb.events.stop.connect(stopped)
 monitor.deadline_stop_handler=stopped
