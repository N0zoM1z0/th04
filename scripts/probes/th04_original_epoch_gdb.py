"""Observe original timer transactions and delayed PIC check callbacks."""
import gdb
from clock_support import ClockAudit

def install(m,symbols):
    soft=m.admission
    read=lambda address,size:bytes(gdb.selected_inferior().read_memory(address,size))
    old_pic=soft.pic_state
    def observed_pic():
        result=old_pic();g=result['cpu_dispatch']
        g['irq_delay_ns']=int.from_bytes(read(symbols['PIC_irq_delay_ns'],8),'little')
        raw=read(symbols['PIC_IRQ_hax'],64)
        g['irq_hacks']=[int.from_bytes(raw[i:i+4],'little') for i in range(0,64,4)]
        return result
    soft.pic_state=observed_pic
    scope=dict(soft=soft,r=m.output,symbols=symbols,context=soft.context,
               manifest=dict(delivery_phase='observe'),pending=[],fail=soft.fail)
    clock=ClockAudit(scope);m.transaction_clock=clock;soft.moment=clock.moment
    soft.breakpoints.extend(clock.breakpoints)
    begin,end=soft.start,soft.stop
    def start(stage,frame):clock.start();begin(stage,frame)
    def stop(stage,frame):end(stage,frame);clock.finish()
    soft.start=start;soft.stop=stop
    class Returned(gdb.FinishBreakpoint):
        def __init__(self,kind):
            self.kind=kind;super().__init__(gdb.newest_frame(),internal=True)
        def stop(self):
            try:
                extra=dict(keyboard_raw=read(symbols['_ZL4keyb'],352).hex()) if self.kind=='keyboard-tick-return' else {}
                soft.event(self.kind,**extra);return False
            except Exception as error:return soft.fail(error)
    class Tick(gdb.Breakpoint):
        def stop(self):
            try:
                soft.event('keyboard-tick-entry',keyboard_raw=read(symbols['_ZL4keyb'],352).hex())
                Returned('keyboard-tick-return');return False
            except Exception as error:return soft.fail(error)
    class DelayedCheck(gdb.Breakpoint):
        def stop(self):
            try:
                state=soft.pic_state()['controllers'][0]
                if state['irr']&2 or state['isr']&2 or soft.uart()['rx_ready']:
                    soft.event('pic-check-entry',host_pc=int(gdb.parse_and_eval('$pc')))
                    Returned('pic-check-return')
                return False
            except Exception as error:return soft.fail(error)
    for cls,name in [(Tick,'_ZL20KEYBOARD_TickHandlerv'),(DelayedCheck,'_Z19PIC_IRQCheckDelayedm')]:
        bp=cls('*0x%x'%symbols[name],internal=True);bp.enabled=False;soft.breakpoints.append(bp)
