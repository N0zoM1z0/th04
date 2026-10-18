"""Observe keyboard API, UART, IRQ and actual BIOS stores without guest calls.

Software breakpoints consume no guest-observer hardware watchpoint slots.
The host mem_writeb hook is enabled only inside the pinned PC-98 IRQ callback.
The owner supplies output, ram, context(), admission_identity(), and a pinned
keyboard_admission plan. Wrap external inferior calls with begin/end_request;
GDB cannot install a FinishBreakpoint on its own dummy call frame.
"""
import hashlib,json
from fractions import Fraction
import gdb

class Admission:
    def __init__(self,m,symbols):
        assert m.plan['keyboard_admission']['engine_sha256']=='6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1','unsupported emulator ABI'
        self.m,self.symbols=m,symbols;self.active=False;self.complete=False;self.error=None
        self.ordinal=0;self.api=0;self.in_irq=False;self.packets=[];self.breakpoints=[]
        self.stream=(m.output/'keyboard-admission.jsonl').open('x');self.digest=hashlib.sha256()
        self.normal_bp=NormalPC98(self);self.rx_bp=Rx(self);self.irq_bp=Irq(self);self.handler_bp=Handler(self);self.store_bp=Store(self);self.send_bp=Send(self)
        self.breakpoints=[self.normal_bp,self.rx_bp,self.irq_bp,self.handler_bp,self.store_bp,self.send_bp]
        for bp in self.breakpoints:bp.enabled=False
        self.save(False)
    def moment(self):
        raw={n:int.from_bytes(bytes(gdb.selected_inferior().read_memory(self.symbols[n],8)),'little',signed=n!='PIC_Ticks') for n in ['PIC_Ticks','CPU_CycleMax','CPU_CycleLeft','CPU_Cycles']}
        assert raw['CPU_CycleMax']==36000
        q=Fraction(raw['PIC_Ticks']*36000+36000-raw['CPU_CycleLeft']-raw['CPU_Cycles'],36000)
        return dict(numerator=q.numerator,denominator=q.denominator,raw=raw)
    def uart(self):
        raw=bytes(gdb.selected_inferior().read_memory(self.symbols['_ZL29pc98_8251_keyboard_uart_state'],80))
        return dict(raw=raw.hex(),data=raw[0],mode=raw[8],valid=raw[12],rx_busy=raw[13],rx_ready=raw[14],recv_in=raw[72],recv_out=raw[73],next_byte=raw[40+raw[73]],io_delay_raw=raw[24:32].hex())
    def pic_state(self):
        read=lambda address,size:bytes(gdb.selected_inferior().read_memory(address,size))
        base=self.symbols['_ZL9pic_queue'];pointer=int.from_bytes(read(base+0x60008,8),'little');seen=set();entries=[]
        while pointer:
            assert base<=pointer<base+0x60000 and (pointer-base)%48==0 and pointer not in seen,'PIC queue link/layout'
            seen.add(pointer);raw=read(pointer,48)
            if int.from_bytes(raw[24:32],'little')==self.symbols['_Z12uart_rx_loadm']:
                entries.append(dict(slot=(pointer-base)//48,index_raw=raw[:16].hex(),value=int.from_bytes(raw[16:24],'little'),node_raw=raw.hex()))
            pointer=int.from_bytes(raw[32:40],'little')
        return dict(in_event_service=bool(read(self.symbols['_ZL14InEventService'],1)[0]),service_index_raw=read(self.symbols['_ZL7srv_lag'],16).hex(),uart_entries=entries,active_queue_nodes=len(seen))
    def context(self):
        state,regs,segs=self.m.context()
        return dict(cpu_state=state,registers=regs.hex(),segments=segs.hex(),cs=int.from_bytes(segs[8:16],'little'),ip=int.from_bytes(regs[32:40],'little')&65535,flags=int.from_bytes(regs[40:48],'little'))
    def event(self,kind,**extra):
        before=self.m.context();row=dict(ordinal=self.ordinal,kind=kind,time=self.moment(),context=self.context(),bios=self.m.ram.read_range(0x52a,10)[0].hex(),uart=self.uart(),pic=self.pic_state(),**self.m.admission_identity(),**extra)
        assert before==self.m.context(),'admission observation changed guest CPU'
        if kind in ['packet-start','packet-end','request-entry','request-return','internal-repeat-entry','internal-repeat-return']:
            row['keyboard_raw']=bytes(gdb.selected_inferior().read_memory(self.symbols['_ZL4keyb'],0x160)).hex()
        line=(json.dumps(row)+'\n').encode();self.stream.write(line.decode());self.stream.flush();self.digest.update(line);self.ordinal+=1
        if self.ordinal%128==0:self.save(False)
        return row
    def fail(self,error):
        self.error=repr(error);self.m.error='keyboard admission: '+repr(error)
        self.save(False);gdb.write('KEYBOARD_ADMISSION_ERROR '+repr(error)+'\n');return True
    def begin_request(self,key,pressed,source='unspecified'):
        if not self.active:return None
        assert not self.in_irq
        self.api+=1;before=self.m.context();memory=self.m.ram.read_range(0,655360)[0]
        time=self.event('request-entry',call=self.api,key=key,pressed=pressed,source=source,conventional_memory_sha256=hashlib.sha256(memory).hexdigest())['time']
        enabled=[(bp,bp.enabled) for bp in self.breakpoints]
        for bp,value in enabled:bp.enabled=False
        return self.api,before,memory,time,enabled
    def end_request(self,token):
        if token is None:return
        call,before,memory,time,enabled=token
        try:
            assert before==self.m.context() and memory==self.m.ram.read_range(0,655360)[0],'keyboard API changed guest state'
            assert Fraction(time['numerator'],time['denominator'])==Fraction(self.moment()['numerator'],self.moment()['denominator']),'keyboard API changed fractional PIC time'
            self.event('request-return',call=call,unchanged_guest=True)
        finally:
            for bp,value in enabled:bp.enabled=value
    def start(self,stage,frame):
        assert not self.active and not self.in_irq;self.active=True
        for bp in self.breakpoints:bp.enabled=bp is not self.store_bp
        self.packets.append(dict(stage=stage,start_frame=frame,start_ordinal=self.ordinal));self.event('packet-start');self.save(False)
    def stop(self,stage,frame):
        assert self.active and not self.in_irq;self.event('packet-end')
        self.packets[-1].update(end_stage=stage,end_frame=frame,end_ordinal=self.ordinal)
        self.active=False
        for bp in self.breakpoints:bp.enabled=False
        self.save(False)
    def update(self,stage,frame):
        wanted=any(stage==s and first<=frame<=last for s,first,last in self.m.plan['input_polls']['ranges'])
        if wanted and not self.active:self.start(stage,frame)
        elif self.active and not wanted:self.stop(stage,frame)
    def save(self,complete):
        self.stream.flush();report=dict(schema_version=1,complete=complete,error=self.error,records=self.ordinal,api_calls=self.api,active=self.active,in_irq=self.in_irq,packets=self.packets,symbols=self.symbols,stream_sha256=self.digest.hexdigest(),scope='Read-only host software breakpoints around real keyboard API calls,8251 RX/IRQ andactual mem_writeb BIOS stores inside the PC-98 IRQ handler. Guest CPU andRAM/time preservation is checked around API calls. Raw PIC counters andguest CPU mode are retained; normal-instruction andPIC callback contexts must be distinguished. No guest accessor,expected latch,time,phase orstate assignments.')
        (self.m.output/'keyboard-admission.json').write_text(json.dumps(report,indent=2)+'\n')
    def finish(self):
        assert not self.error and not self.in_irq
        if self.active:self.stop(-1,-1)
        self.save(True);self.stream.close();self.complete=True

class Point(gdb.Breakpoint):
    def __init__(self,p,symbol):self.p=p;super().__init__('*0x%x'%p.symbols[symbol],internal=True)
class Send(Point):
    def __init__(self,p):super().__init__(p,'_Z18pc98_keyboard_sendh')
    def stop(self):
        try:self.p.event('enqueue',scan_code=int(gdb.parse_and_eval('$rdi'))&255);return False
        except Exception as error:return self.p.fail(error)
class Rx(Point):
    def __init__(self,p):super().__init__(p,'_Z12uart_rx_loadm')
    def stop(self):
        try:self.p.event('rx-entry');RxReturn(self.p);return False
        except Exception as error:return self.p.fail(error)
class RxReturn(gdb.FinishBreakpoint):
    def __init__(self,p):self.p=p;super().__init__(gdb.newest_frame(),internal=True)
    def stop(self):
        try:self.p.event('rx-return');return False
        except Exception as error:return self.p.fail(error)
class Irq(Point):
    def __init__(self,p):super().__init__(p,'_Z15PIC_ActivateIRQm')
    def stop(self):
        try:
            if int(gdb.parse_and_eval('$rdi'))==1:self.p.event('irq1-request')
            return False
        except Exception as error:return self.p.fail(error)
class Handler(Point):
    def __init__(self,p):super().__init__(p,'_ZL17IRQ1_Handler_PC98v')
    def stop(self):
        p=self.p
        try:
            assert not p.in_irq;p.in_irq=True;p.event('bios-irq-entry');p.store_bp.enabled=True;HandlerReturn(p);return False
        except Exception as error:return p.fail(error)
class HandlerReturn(gdb.FinishBreakpoint):
    def __init__(self,p):self.p=p;super().__init__(gdb.newest_frame(),internal=True)
    def stop(self):
        p=self.p
        try:p.event('bios-irq-return');p.store_bp.enabled=False;p.in_irq=False;return False
        except Exception as error:return p.fail(error)
class Store(Point):
    def __init__(self,p):super().__init__(p,'_Z10mem_writebjh')
    def stop(self):
        p=self.p
        try:
            address=int(gdb.parse_and_eval('$rdi'));value=int(gdb.parse_and_eval('$rsi'))&255
            if 0x52a<=address<0x534:
                assert p.in_irq;p.event('bios-write-entry',address=address,value=value);StoreReturn(p,address,value)
            return False
        except Exception as error:return p.fail(error)
class StoreReturn(gdb.FinishBreakpoint):
    def __init__(self,p,address,value):self.p,self.address,self.value=p,address,value;super().__init__(gdb.newest_frame(),internal=True)
    def stop(self):
        p=self.p
        try:
            assert p.m.ram.read_range(self.address,1)[0]==bytes([self.value]);p.event('bios-write-return',address=self.address,value=self.value);return False
        except Exception as error:return p.fail(error)

class NormalPC98(Point):
    def __init__(self,p):super().__init__(p,'_Z20KEYBOARD_PC98_AddKey8KBD_KEYSb')
    def stop(self):
        p=self.p
        try:
            stack=[];frame=gdb.newest_frame()
            for i in range(5):
                if frame is None:break
                stack.append(dict(name=frame.name(),pc=int(frame.pc())));frame=frame.older()
            p.event('internal-repeat-entry',key=int(gdb.parse_and_eval('$rdi')),pressed=bool(int(gdb.parse_and_eval('$rsi'))&255),host_stack=stack)
            NormalReturn(p);return False
        except Exception as error:return p.fail(error)
class NormalReturn(gdb.FinishBreakpoint):
    def __init__(self,p):self.p=p;super().__init__(gdb.newest_frame(),internal=True)
    def stop(self):
        try:self.p.event('internal-repeat-return');return False
        except Exception as error:return self.p.fail(error)
