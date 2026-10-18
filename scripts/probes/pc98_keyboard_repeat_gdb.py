"""Observe two external requests and two normal repeat calls with independent BIOS write watches."""
import hashlib,json,traceback
from fractions import Fraction
from pathlib import Path
import gdb
from th04_demo_host_ram import HostRam
r=Path(__file__).resolve().parent;manifest=json.loads((r/'manifest.json').read_text());symbols={k:v['address'] for k,v in manifest['symbols'].items()};inferior=gdb.selected_inferior()
gdb.execute('starti')
load_bias=int(gdb.parse_and_eval('(unsigned long)&MemBase'))-symbols['MemBase']
symbols={name:address+load_bias for name,address in symbols.items()}
(r/'startup.json').write_text(json.dumps(dict(inferior_pid=gdb.selected_inferior().pid,load_bias=load_bias,symbols=symbols),indent=2)+'\n')
read=lambda p,n:bytes(inferior.read_memory(p,n));ram=HostRam(read,symbols);events=[];active=False;complete=False;error=None;markers=[];api_count=0;watchers=[];pending=[]
def integer(name,signed=False):return int.from_bytes(read(symbols[name],8),'little',signed=signed)
def time():
 raw={k:integer(k,k!='PIC_Ticks') for k in ['PIC_Ticks','CPU_CycleMax','CPU_CycleLeft','CPU_Cycles']};assert raw['CPU_CycleMax']==36000
 q=Fraction(raw['PIC_Ticks']*raw['CPU_CycleMax']+raw['CPU_CycleMax']-raw['CPU_CycleLeft']-raw['CPU_Cycles'],raw['CPU_CycleMax'])
 return dict(numerator=q.numerator,denominator=q.denominator,raw=raw)
def context():
 regs=read(symbols['cpu_regs'],48);segs=read(symbols['Segs'],136)
 return dict(registers=regs.hex(),segments=segs.hex(),cs=int.from_bytes(segs[8:16],'little'),ip=int.from_bytes(regs[32:40],'little')&65535,flags=int.from_bytes(regs[40:48],'little'),cpu_state=ram.state())
def uart():
 raw=read(symbols['_ZL29pc98_8251_keyboard_uart_state'],80)
 return dict(raw=raw.hex(),data=raw[0],mode=raw[8],valid=raw[12],rx_busy=raw[13],rx_ready=raw[14],recv_in=raw[72],recv_out=raw[73],next_byte=raw[40+raw[73]],io_delay_raw=raw[24:32].hex())
def bios():return ram.read_range(0x52a,10)[0].hex()
def save():
 (r/'events.json').write_text(json.dumps(dict(complete=complete,error=error,runtime_load_bias=load_bias,markers=markers,api_count=api_count,events=events,scope='Authored internal-DOS PC-98 guest,not TH04 or a resumed original checkpoint. Only original KEYBOARD_AddKey calls inject input;guest BIOS matrix is read,never assigned. Actual UART event,IRQ and BIOS writes are observed,including two held-key repeat cycles. Guest CPU mode/vector/ROM image must be kept separate from original V86 game timing.'),indent=2)+'\n')
def event(kind,**extra):events.append(dict(kind=kind,time=time(),context=context(),bios=bios(),uart=uart(),**extra));save()
def fail(exc):
 global error
 error=repr(exc);detail=dict(kind='observer-error',error=error,traceback=traceback.format_exc())
 try:detail.update(context=context(),uart=uart(),bios=bios())
 except BaseException:pass
 events.append(detail);save();return True
def inject(key,pressed):
 global api_count
 before_ctx=context();before_time=time();before_mem=ram.read_range(0,655360)[0];before_uart=uart()
 token=soft.begin_request(manifest['keys'][key],pressed)
 gdb.execute('call ((void (*)(int, bool))0x%x)(%d, %s)'%(symbols['_Z15KEYBOARD_AddKey8KBD_KEYSb'],manifest['keys'][key],'true' if pressed else 'false'),to_string=True)
 soft.end_request(token)
 after_ctx=context();after_time=time();after_mem=ram.read_range(0,655360)[0]
 assert before_ctx==after_ctx and before_mem==after_mem,'input call changed guest CPU/RAM'
 assert Fraction(before_time['numerator'],before_time['denominator'])==Fraction(after_time['numerator'],after_time['denominator']),'input call advanced emulated time'
 api_count+=1;event('request',key=key,pressed=pressed,before_time=before_time,before_uart=before_uart,unchanged_guest=True,conventional_memory_sha256=hashlib.sha256(before_mem).hexdigest())
class BiosWrite(gdb.Breakpoint):
 def __init__(self,address,label):
  self.label=label;super().__init__('*(unsigned char *)0x%x'%address,type=gdb.BP_WATCHPOINT,wp_class=gdb.WP_WRITE,internal=True)
 def stop(self):
  try:
   if active:event('bios-write',cell=self.label)
   return False
  except BaseException as exc:return fail(exc)
class RxFinish(gdb.FinishBreakpoint):
 def __init__(self):super().__init__(gdb.newest_frame(),internal=True)
 def stop(self):
  try:event('rx-return');return False
  except BaseException as exc:return fail(exc)
class Rx(gdb.Breakpoint):
 def stop(self):
  try:
   if active:event('rx-entry');RxFinish()
   return False
  except BaseException as exc:return fail(exc)
class Irq(gdb.Breakpoint):
 def stop(self):
  try:
   if active and int(gdb.parse_and_eval('$rdi'))==1:event('irq1-request')
   return False
  except BaseException as exc:return fail(exc)
class Marker(gdb.Breakpoint):
 def stop(self):
  global active,complete
  try:
   if int(gdb.parse_and_eval('$rdi'))!=0xe9:return False
   value=int(gdb.parse_and_eval('$rsi'))&255
   if not 0xa0<=value<=0xa6:return False
   assert value==0xa0+len(markers),'guest marker order'
   if value==0xa0:
    ctx=context();assert not ctx['cpu_state'][1]&0x80000000,'micro fixture paging mode changed'
    assert ram.read_range(ctx['cs']*16+0x100,len((r/'UART.COM').read_bytes()))[0]==(r/'UART.COM').read_bytes(),'actual guest COM image differs'
    state=uart();event('startup-state',initial_uart=state);assert not state['rx_busy'] and not state['rx_ready'] and state['recv_in']==state['recv_out'],'keyboard startup queue not drained'
    active=True;rx.enabled=True;irq.enabled=True;soft.start(0,0)
    base=ram.state()[0]
    watchers.extend([BiosWrite(base+ram.physical(0x52f),'shot'),BiosWrite(base+ram.physical(0x52d),'enter')])
    event('micro-image',sha256=hashlib.sha256((r/'UART.COM').read_bytes()).hexdigest(),irq9_vector=ram.read_range(0x24,4)[0].hex())
   markers.append(value);event('marker',value=value)
   matrix=bytes.fromhex(bios());shot=bool(matrix[5]&2);enter=bool(matrix[3]&16)
   if value==0xa0:assert not shot and not enter;pending.append(('KBD_z',True))
   elif value==0xa1:assert shot and not enter
   elif value==0xa2:assert not shot and not enter and api_count==1
   elif value==0xa3:assert shot and not enter and api_count==1
   elif value==0xa4:assert not shot and not enter and api_count==1
   elif value==0xa5:assert shot and not enter and api_count==1;pending.append(('KBD_z',False))
   elif value==0xa6:
    assert not shot and not enter and api_count==2
    soft.finish();assert not soft.error;complete=True;active=False;rx.enabled=False;irq.enabled=False
    for watcher in watchers:watcher.enabled=False
    self.enabled=False;save()
   return bool(pending) or complete
  except BaseException as exc:return fail(exc)
from keyboard_admission_gdb import Admission
class Adapter:
 output=r;error=None
 plan={'input_polls':{'ranges':[[0,0,0]]},'keyboard_admission':{'engine_sha256':manifest['engine_sha256']}}
 ram=ram
 def context(self):return ram.state(),read(symbols['cpu_regs'],48),read(symbols['Segs'],136)
 def admission_identity(self):return dict(stage=0,frame=0,load_segment=None,dgroup_segment=None)
soft=Admission(Adapter(),symbols)
rx=Rx('*0x%x'%symbols['_Z12uart_rx_loadm'],internal=True);rx.enabled=False
irq=Irq('*0x%x'%symbols['_Z15PIC_ActivateIRQm'],internal=True);irq.enabled=False
marker=Marker('*0x%x'%symbols['_Z9IO_WriteBmh'],internal=True)
try:
 while True:
  gdb.execute('continue')
  if soft.error:error=soft.error
  if error or complete:break
  if not pending:break
  tasks=list(pending);pending.clear()
  enabled=[(bp,bp.enabled) for bp in [marker,rx,irq,*watchers]]
  for bp,value in enabled:bp.enabled=False
  try:
   for key,pressed in tasks:inject(key,pressed)
  finally:
   for bp,value in enabled:bp.enabled=value
 if complete and not error:gdb.execute('continue')
except BaseException as execution_error:fail(execution_error)
if not complete and error is None:
 try:
  ctx=context();linear=ctx['cs']*16+ctx['ip'];window=ram.read_range(max(0,linear-16),64)[0].hex() if linear+64<0xa0000 else None
  event('incomplete-stop',instruction_window=window,uart_state=uart())
 except BaseException as diagnostic_error:events.append(dict(kind='incomplete-diagnostic-error',error=repr(diagnostic_error)))
save()
if not complete or error:gdb.execute('quit 1')
