"""Audit the pinned PIC tick transaction before interpreting keyboard time.

PIC_Ticks is written before the CPU budget is credited and queued indices are
normalized. A hardware watchpoint can stop between those stores. Raw counters
remain evidence; this reader derives the pending credit from observed host
instructions rather than accepting a supplied phase or clamping timestamps.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct

ENGINE_SHA = '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1'
OFFSETS = dict(tick_store_return=0x17, budget_credit=0x42, queue_credit=0x81)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def raw_time(row):
    value = row['time']
    raw = value['raw']
    assert raw['CPU_CycleMax'] == 36000
    expected = Fraction(raw['PIC_Ticks']*36000+36000-
                        raw['CPU_CycleLeft']-raw['CPU_Cycles'], 36000)
    assert expected == Fraction(value['numerator'], value['denominator'])
    return expected


def index80(raw):
    data = bytes.fromhex(raw)
    assert len(data) == 16
    mantissa = int.from_bytes(data[:8], 'little')
    word = int.from_bytes(data[8:10], 'little')
    exponent = word & 0x7fff
    assert exponent != 0x7fff
    value = Fraction(mantissa)*Fraction(2)**((exponent or 1)-16383-63)
    return -value if word & 0x8000 else value


def uart_indices(row):
    return {item['slot']: index80(item['index_raw'])
            for item in row['pic']['uart_entries']}


def audit_pic(row, symbols):
    """Require queue observations to agree with the attested 48-byte host nodes."""
    state = row['pic']
    assert 0 <= state['active_queue_nodes'] <= 8192
    index80(state['service_index_raw'])
    seen = set()
    base = symbols['_ZL9pic_queue']
    for item in state['uart_entries']:
        raw = bytes.fromhex(item['node_raw'])
        assert len(raw) == 48 and raw[:16].hex() == item['index_raw']
        assert int.from_bytes(raw[16:24], 'little') == item['value']
        assert int.from_bytes(raw[24:32], 'little') == symbols['_Z12uart_rx_loadm']
        assert 0 <= item['slot'] < 8192 and item['slot'] not in seen
        seen.add(item['slot'])
        pointer = int.from_bytes(raw[32:40], 'little')
        assert not pointer or (base <= pointer < base+0x60000 and (pointer-base)%48 == 0)
        index80(item['index_raw'])


def attest_timer(engine, symbols):
    """Check actual ELF operands at every instruction boundary used by the audit."""
    assert sha(engine) == ENGINE_SHA
    address = symbols['_Z13TIMER_AddTickv']['address']
    with Path(engine).open('rb') as stream:
        header = stream.read(64)
        assert header[:6] == b'\x7fELF\x02\x01'
        table = int.from_bytes(header[32:40], 'little')
        size = int.from_bytes(header[54:56], 'little')
        count = int.from_bytes(header[56:58], 'little')
        segments = []
        for i in range(count):
            stream.seek(table+i*size)
            kind, flags, offset, va, pa, filesz, memsz, align = struct.unpack('<IIQQQQQQ', stream.read(56))
            if kind == 1 and va <= address and address+0x81 <= va+filesz:
                segments.append(offset+address-va)
        assert len(segments) == 1
        stream.seek(segments[0])
        code = stream.read(0x81)
    assert code[0x10:0x13] == bytes.fromhex('488905')
    assert address+0x17+int.from_bytes(code[0x13:0x17], 'little', signed=True) == symbols['PIC_Ticks']['address']
    assert code[0x3b:0x3e] == bytes.fromhex('480105')
    assert address+0x42+int.from_bytes(code[0x3e:0x42], 'little', signed=True) == symbols['CPU_CycleLeft']['address']
    assert code[0x67:0x69] == bytes.fromhex('d9e8')  # FLD1
    assert code[0x70:0x76] == bytes.fromhex('db28d8e1db38')  # load/subtract/store index
    assert symbols['PIC_Ticks']['size'] == symbols['CPU_CycleLeft']['size'] == 8
    return dict(engine_sha256=ENGINE_SHA, timer_elf_address=address,
                observed_prefix_sha256=hashlib.sha256(code).hexdigest(), offsets=OFFSETS)


def audit_rows(clocks, admissions, timer):
    """Require complete timer transactions and derive each sample's clock phase."""
    assert clocks and [row['ordinal'] for row in clocks] == list(range(len(clocks)))
    assert [row['ordinal'] for row in admissions] == list(range(len(admissions)))
    assert clocks[0]['kind'] == 'clock-start' and clocks[-1]['kind'] == 'clock-end'
    states = [(False, False)]
    state = 'idle'
    credit = queue = False
    transactions = []
    current = []
    normalized_uart_entries = 0
    timeline = []
    for number, row in enumerate(clocks):
        kind = row['kind']
        if kind in ('clock-start', 'clock-end'):
            assert state == 'idle'
        elif kind == 'timer-entry':
            assert state == 'idle' and row['host_pc'] == timer
            state = 'entered'
            current = [row]
        elif kind == 'tick-store':
            assert state == 'entered' and row['host_pc'] == timer+OFFSETS['tick_store_return']
            assert row['time']['raw']['PIC_Ticks'] == current[0]['time']['raw']['PIC_Ticks']+1
            credit = queue = True
            state = 'stored'
            current.append(row)
        elif kind == 'budget-credit':
            assert state == 'stored' and row['host_pc'] == timer+OFFSETS['budget_credit']
            credit = False
            state = 'credited'
            current.append(row)
        elif kind == 'queue-credit':
            assert state == 'credited' and row['host_pc'] == timer+OFFSETS['queue_credit']
            before, after = uart_indices(current[-1]), uart_indices(row)
            assert before.keys() == after.keys()
            assert all(before[key]-after[key] == 1 for key in before)
            normalized_uart_entries += len(before)
            queue = False
            state = 'normalized'
            current.append(row)
        elif kind == 'timer-return':
            assert state == 'normalized' and row['host_pc'] == current[0]['return_pc']
            state = 'idle'
            current.append(row)
            values = [raw_time(item)-int(item['kind'] == 'tick-store') for item in current]
            assert all(value == values[0] for value in values), 'timer budget continuity'
            assert all(item['context'] == current[0]['context'] for item in current), 'timer changed guest CPU'
            transactions.append(current)
        else:
            raise AssertionError('unknown clock event: '+kind)
        assert row['time']['clock_audit']['records'] == number
        states.append((credit, queue))
        value = raw_time(row)-int(credit)
        proof = row['time']['clock_audit']
        assert (proof['tick_credit_pending'], proof['tick_queue_pending']) == (credit, queue)
        assert value == Fraction(proof['canonical_numerator'], proof['canonical_denominator'])
        timeline.append(((number+1, 0, number), raw_time(row), value))
    assert state == 'idle' and transactions
    corrected_samples = 0
    canonical = []
    for row in admissions:
        proof = row['time']['clock_audit']
        count = proof['records']
        assert 1 <= count <= len(clocks)
        credit, queue = states[count]
        assert (proof['tick_credit_pending'], proof['tick_queue_pending']) == (credit, queue)
        value = raw_time(row)-int(credit)
        assert value == Fraction(proof['canonical_numerator'], proof['canonical_denominator'])
        corrected_samples += int(credit)
        canonical.append(value)
        timeline.append(((count, 1, row['ordinal']), raw_time(row), value))
    timeline.sort()
    raw_regressions = sum(b[1] < a[1] for a, b in zip(timeline, timeline[1:]))
    canonical_regressions = sum(b[2] < a[2] for a, b in zip(timeline, timeline[1:]))
    assert canonical_regressions == 0, 'derived clock regressed'
    report = dict(passed=True, timer_transactions=len(transactions), clock_records=len(clocks),
        admission_records=len(admissions), admission_samples_with_pending_credit=corrected_samples,
        queue_entries_observed_minus_one=normalized_uart_entries,
        merged_raw_regressions=raw_regressions, merged_canonical_regressions=canonical_regressions,
        scope='Phase comes from complete observed timer instruction transactions, including actual PIC_Ticks hardware writes, CPU budget credit and queue index subtraction. No timestamp clamping, fitted phase or guest clock assignment. This decodes the pinned emulator boundary; it does not establish native game elapsed time or IRQ latency.')
    return report, canonical


def audit_capture(capture, read_stream=None):
    """Audit regular streams, or explicitly supplied exact archive bytes.

    The provider changes only stream reading. Source identities, real ELF
    operands, capture metadata and raw-stream digests remain required.
    """
    capture = Path(capture)
    if read_stream is None:
        read_stream = lambda path: path.read_bytes()
    receipt = json.loads((capture/'receipt.json').read_text())
    assert receipt['passed'] and receipt['exit'] == 0 and not receipt['timeout']
    for path, digest in receipt['inputs'].items():
        assert sha(path) == digest, path
    manifest = json.loads((capture/'manifest.json').read_text())
    binary = attest_timer(manifest['engine'], manifest['symbols'])
    clock_meta = json.loads((capture/'clock-events.json').read_text())
    assert clock_meta['passed'] and clock_meta['offsets'] == OFFSETS
    assert manifest['delivery_phase'] in ('tick-edge', 'tick-return')
    assert clock_meta['phase'] == manifest['delivery_phase']
    raw_clock = read_stream(capture/'clock-events.jsonl')
    assert hashlib.sha256(raw_clock).hexdigest() == clock_meta['stream_sha256']
    clocks = [json.loads(line) for line in raw_clock.splitlines()]
    meta = json.loads((capture/'keyboard-admission.json').read_text())
    assert meta['complete'] and not meta['error'] and not meta['active'] and not meta['in_irq']
    raw_admission = read_stream(capture/'keyboard-admission.jsonl')
    assert hashlib.sha256(raw_admission).hexdigest() == meta['stream_sha256']
    admissions = [json.loads(line) for line in raw_admission.splitlines()]
    assert len(clocks) == clock_meta['records'] and len(admissions) == meta['records']
    bias = json.loads((capture/'startup.json').read_text())['load_bias']
    assert clock_meta['timer_address'] == binary['timer_elf_address']+bias
    for name, item in manifest['symbols'].items():
        assert meta['symbols'][name] == item['address']+bias, name
    for row in clocks+admissions:
        audit_pic(row, meta['symbols'])
    report, canonical = audit_rows(clocks, admissions, clock_meta['timer_address'])
    expected_seam = 'tick-store' if manifest['delivery_phase'] == 'tick-edge' else 'timer-return'
    for row in admissions:
        if row['kind'] == 'request-entry':
            assert clocks[row['time']['clock_audit']['records']-1]['kind'] == expected_seam
    report.update(binary=binary, delivery_phase=manifest['delivery_phase'],
        clock_stream_sha256=clock_meta['stream_sha256'], admission_stream_sha256=meta['stream_sha256'])
    return report, canonical
