"""Observe the pinned timer transaction; never change guest or emulator clocks."""
import hashlib
import json
from fractions import Fraction
import gdb


class ClockAudit:
    def __init__(self, scope):
        self.scope = scope
        self.soft = scope['soft']
        self.original_moment = self.soft.moment
        self.records = []
        self.credit_pending = self.queue_pending = self.in_tick = False
        self.before_tick = None
        self.return_pc = None
        self.active = False
        self.stream = (scope['r']/'clock-events.jsonl').open('x')
        self.digest = hashlib.sha256()
        self.timer = scope['symbols']['_Z13TIMER_AddTickv']
        self.entry = TimerEntry(self)
        self.store = TickStore(self)
        self.credit = BudgetCredit(self)
        self.queue = QueueCredit(self)
        self.breakpoints = [self.entry, self.store, self.credit, self.queue]
        for bp in self.breakpoints:
            bp.enabled = False

    def moment(self):
        value = self.original_moment()
        q = Fraction(value['numerator'], value['denominator'])-int(self.credit_pending)
        value['clock_audit'] = dict(records=len(self.records),
            tick_credit_pending=self.credit_pending, tick_queue_pending=self.queue_pending,
            canonical_numerator=q.numerator, canonical_denominator=q.denominator)
        return value

    def record(self, kind, **extra):
        row = dict(ordinal=len(self.records), kind=kind, time=self.moment(),
            host_pc=int(gdb.parse_and_eval('$pc')), context=self.scope['context'](),
            pic=self.soft.pic_state(), **extra)
        line=(json.dumps(row)+'\n').encode()
        self.stream.write(line.decode()); self.stream.flush(); self.digest.update(line)
        self.records.append(row)

    def start(self):
        assert not self.active
        self.active=True
        for bp in self.breakpoints:bp.enabled=True
        self.record('clock-start')

    def finish(self):
        assert self.active and not self.in_tick
        self.record('clock-end')
        for bp in self.breakpoints:bp.enabled=False
        self.active=False
        self.stream.close()
        (self.scope['r']/'clock-events.json').write_text(json.dumps(dict(
            passed=True, records=len(self.records), stream_sha256=self.digest.hexdigest(),
            timer_address=self.timer, phase=self.scope['manifest']['delivery_phase'],
            offsets=dict(tick_store_return=0x17,budget_credit=0x42,queue_credit=0x81),
            scope='Actual entry, PIC_Ticks hardware write, CPU budget credit, queue normalization and return of the pinned TIMER_AddTick. Canonical time only removes the still-pending one-tick CPU budget credit; raw observations remain unchanged. No guest state or time assignments.'),indent=2)+'\n')

    def fail(self, error):
        return self.scope['fail'](error)


class TimerEntry(gdb.Breakpoint):
    def __init__(self, owner):
        self.o=owner
        super().__init__('*0x%x'%owner.timer,internal=True)
    def stop(self):
        o=self.o
        try:
            assert not o.in_tick and not o.credit_pending and not o.queue_pending
            o.in_tick=True
            o.before_tick=o.original_moment()['raw']['PIC_Ticks']
            o.return_pc=int.from_bytes(bytes(gdb.selected_inferior().read_memory(int(gdb.parse_and_eval('$rsp')),8)),'little')
            o.record('timer-entry',return_pc=o.return_pc)
            TimerReturn(o)
            return False
        except BaseException as error:return o.fail(error)


class TickStore(gdb.Breakpoint):
    def __init__(self, owner):
        self.o=owner
        super().__init__('*(unsigned long *)0x%x'%owner.scope['symbols']['PIC_Ticks'],
            type=gdb.BP_WATCHPOINT,wp_class=gdb.WP_WRITE,internal=True)
    def stop(self):
        o=self.o
        try:
            assert o.in_tick and int(gdb.parse_and_eval('$pc'))==o.timer+0x17
            assert o.original_moment()['raw']['PIC_Ticks']==o.before_tick+1
            o.credit_pending=o.queue_pending=True
            o.record('tick-store')
            return o.scope['manifest']['delivery_phase']=='tick-edge' and bool(o.scope['pending'])
        except BaseException as error:return o.fail(error)


class BudgetCredit(gdb.Breakpoint):
    def __init__(self, owner):
        self.o=owner
        super().__init__('*0x%x'%(owner.timer+0x42),internal=True)
    def stop(self):
        o=self.o
        try:
            assert o.in_tick and o.credit_pending and o.queue_pending
            o.credit_pending=False
            o.record('budget-credit')
            return False
        except BaseException as error:return o.fail(error)


class QueueCredit(gdb.Breakpoint):
    def __init__(self, owner):
        self.o=owner
        super().__init__('*0x%x'%(owner.timer+0x81),internal=True)
    def stop(self):
        o=self.o
        try:
            assert o.in_tick and not o.credit_pending and o.queue_pending
            o.queue_pending=False
            o.record('queue-credit')
            return False
        except BaseException as error:return o.fail(error)


class TimerReturn(gdb.FinishBreakpoint):
    def __init__(self, owner):
        self.o=owner
        super().__init__(gdb.newest_frame(),internal=True)
    def stop(self):
        o=self.o
        try:
            assert o.in_tick and not o.credit_pending and not o.queue_pending
            assert int(gdb.parse_and_eval('$pc'))==o.return_pc
            o.in_tick=False
            o.record('timer-return')
            return o.scope['manifest']['delivery_phase']=='tick-return' and bool(o.scope['pending'])
        except BaseException as error:return o.fail(error)
