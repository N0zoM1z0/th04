"""Read original MAIN's PIC/CPU admission state without guest accessor calls.

The existing recorder owns physical API calls, UART and BIOS observations.
These extra software breakpoints add controller state, CPU dispatch and EOI.
Raw clock counters remain raw; this module does not infer latency or phase.
"""
import hashlib,json
from pathlib import Path
import gdb

OFFSETS=dict(special=16,auto_eoi=17,rotate_on_auto_eoi=18,single=19,
             request_issr=20,vector_base=21,irr=22,imr=23,imrr=24,
             isr=25,isrr=26,isr_ignore=27,active_irq=28)

def install(m,symbols):
    p=m.admission;read=lambda address,size:bytes(gdb.selected_inferior().read_memory(address,size))
    old_pic=p.pic_state
    def observed_pic():
        result=old_pic();raw=read(symbols['_ZL4pics'],64)
        result['controllers']=[dict(raw=raw[i*32:(i+1)*32].hex(),
            **{name:raw[i*32+offset] for name,offset in OFFSETS.items()}) for i in range(2)]
        integer=lambda name,size=8:int.from_bytes(read(symbols[name],size),'little')
        result['cpu_dispatch']=dict(irq_check=integer('PIC_IRQCheck'),
            irq_check_pending=integer('PIC_IRQCheckPending'),
            nmi_active=integer('CPU_NMI_active',1),nmi_pending=integer('CPU_NMI_pending',1),
            decoder=integer('cpudecoder'),trap_decoder=symbols['_Z24CPU_Core_Normal_Trap_Runv'],
            cascade_irq=integer('master_cascade_irq',4),
            ignore_cascade_in_service=integer('ignore_cascade_in_service',1),
            never_mark_cascade_in_service=integer('never_mark_cascade_in_service',1))
        return result
    p.pic_state=observed_pic

    class Return(gdb.FinishBreakpoint):
        def __init__(self,kind,**extra):
            self.kind,self.extra=kind,extra
            super().__init__(gdb.newest_frame(),internal=True)
        def stop(self):
            try:p.event(self.kind,**self.extra);return False
            except Exception as error:return p.fail(error)
    class Point(gdb.Breakpoint):
        def __init__(self,name):super().__init__('*0x%x'%symbols[name],internal=True);self.enabled=False
    class Run(Point):
        def stop(self):
            try:
                state=p.pic_state();master=state['controllers'][0]
                if master['irr']&2 or master['isr']&2 or p.uart()['rx_ready']:
                    p.event('pic-dispatch-entry');Return('pic-dispatch-return')
                return False
            except Exception as error:return p.fail(error)
    class Accept(Point):
        def stop(self):
            try:
                vector=int(gdb.parse_and_eval('$rdi'));kind=int(gdb.parse_and_eval('$rsi'))
                if kind==0 and 8<=vector<24:
                    p.event('cpu-irq-accept',vector=vector,interrupt_type=kind)
                return False
            except Exception as error:return p.fail(error)
    class Io(Point):
        def stop(self):
            try:
                port=int(gdb.parse_and_eval('$rdi'));value=int(gdb.parse_and_eval('$rsi'))&255
                if port in (0,2,8,10):
                    p.event('pic-write-entry',port=port,value=value)
                    Return('pic-write-return',port=port,value=value)
                return False
            except Exception as error:return p.fail(error)
    p.breakpoints.extend([Run('_Z11PIC_runIRQsv'),Accept('_Z13CPU_Interruptmmj'),Io('_Z9IO_WriteBmh')])

    # The compiled observer identifies MAIN at its actual MZ entry CS:0000.
    # Bind the entire loaded module to the pinned Japanese target before using
    # any target-dependent state; no guest bytes or CPU state are assigned.
    from compare_th04_dos_demos import relocated_module
    target=Path(m.plan['pic_observer']['main_path']).read_bytes()
    assert hashlib.sha256(target).hexdigest()==m.plan['pic_observer']['main_sha256']
    before=m.context();expected=relocated_module(target,m.current.load)
    actual=m.ram.read_range(m.current.load*16,len(expected))[0]
    assert actual==expected,'complete original MAIN load-module attestation'
    assert before==m.context(),'module observation changed CPU context'
    _,regs,segs=before
    assert int.from_bytes(segs[8:16],'little')==m.current.load and int.from_bytes(regs[32:40],'little')&65535==0
    (m.output/'original-pic-image.json').write_text(json.dumps(dict(passed=True,
        target_main_sha256=hashlib.sha256(target).hexdigest(),load_segment=m.current.load,
        dgroup_segment=m.current.dgroup,module_size=len(actual),
        relocated_module_sha256=hashlib.sha256(actual).hexdigest(),
        entry_cs=m.current.load,entry_ip=0,cpu_state=before[0],registers=regs.hex(),segments=segs.hex(),
        unchanged_context=True,scope='Actual first MAIN entry;entire relocated load module equals the pinned target. Local candidate attestation,not pristine-dump provenance or semantic equivalence.'),indent=2)+'\n')
    p.event('main-image-entry',module_sha256=hashlib.sha256(actual).hexdigest())
