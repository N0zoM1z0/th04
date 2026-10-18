"""Audit the original IRQ1 monitor/BIOS/EOI/IRET path without fitting a delay."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts/probes'))
import pc98_keyboard_clock as clock
import reduce_th04_original_epoch as epoch
from pc98_keyboard_isr_cpu import check, identity


def audit(capture, read_data=None, hash_file=None):
    c = Path(capture)
    read_data = read_data or (lambda p: Path(p).read_bytes())
    hash_file = hash_file or clock.sha
    load = lambda name: json.loads(read_data(c/name))
    base = epoch.audit(c, read_data=read_data, hash_file=hash_file)
    meta = load('keyboard-isr.json')
    assert meta['passed']
    wire = read_data(c/'keyboard-isr.jsonl')
    assert hashlib.sha256(wire).hexdigest() == meta['stream_sha256']
    rows = [json.loads(line) for line in wire.splitlines()]
    assert len(rows) == meta['records'] and rows
    clocks = [json.loads(line) for line in read_data(c/'clock-events.jsonl').splitlines()]
    primary = [json.loads(line) for line in read_data(c/'keyboard-admission.jsonl').splitlines()]
    for row in rows:
        clock.audit_pic(row, meta['symbols'])
        assert 0 <= row['after_admission_ordinal'] < len(primary)
        linked = primary[row['after_admission_ordinal']]
        assert linked['ordinal'] == row['after_admission_ordinal']
        assert row['context']['ss'] == int.from_bytes(bytes.fromhex(row['context']['segments'])[16:24], 'little')
        assert row['context']['sp'] == int.from_bytes(bytes.fromhex(row['context']['registers'])[16:20], 'little') & 65535
        assert bool(row['stack'] is not None) == bool(row['context']['flags'] & 0x20000)
    ca, moments = clock.audit_rows(clocks, rows, meta['symbols']['_Z13TIMER_AddTickv'])
    time = {row['ordinal']: value for row, value in zip(rows, moments, strict=True)}
    groups = {}
    for row in rows:
        groups.setdefault(row['irq'], []).append(row)
    assert list(groups) == list(range(1, meta['interrupts']+1))
    assert len(groups) == len(base['receive_check_accept'])
    engine = identity()
    results = []
    negatives = []
    for number, group in groups.items():
        select = lambda kind: [row for row in group if row['kind'] == kind]
        one = lambda kind: _one(select(kind))
        accepted, entered = one('irq-accept'), one('irq-entry-return')
        before, after = one('bios-entry'), one('bios-return')
        monitor = [row for row in select('iret-entry') if row['role'] == 'monitor']
        monitor_returns = [row for row in select('iret-return') if row['role'] == 'monitor']
        tail_entries = [row for row in select('iret-entry') if row['role'] == 'bios-tail']
        tail_returns = [row for row in select('iret-return') if row['role'] == 'bios-tail']
        assert len(monitor) == len(monitor_returns) == len(tail_entries) == len(tail_returns) == 1
        returned = tail_returns[0]
        cs, ip = accepted['stub_cs'], accepted['stub_ip']
        assert cs == 0xf000
        assert accepted['vector'] == (ip.to_bytes(2, 'little')+cs.to_bytes(2, 'little')).hex()
        assert accepted['default_location'] == (cs << 16)|ip
        rom = bytes.fromhex(accepted['rom'])
        assert accepted['rom'] == accepted['default_rom']
        assert rom[:2] == bytes.fromhex('fe38') and rom[4:11] == bytes.fromhex('50b020e60058cf')
        assert not entered['context']['flags'] & 0x20000
        assert not monitor[0]['context']['flags'] & 0x20000
        assert monitor_returns[0]['context']['flags'] & 0x20000
        assert (monitor_returns[0]['context']['cs'], monitor_returns[0]['context']['ip']) == (cs, ip)
        assert (before['context']['cs'], before['context']['ip']) == (cs, ip+4)
        assert before['context'] == after['context'], 'BIOS callback changed guest CPU'
        assert returned['context'] == accepted['context'], 'IRQ1 did not restore interrupted CPU'
        reads = select('io-read-return')
        assert [row['port'] for row in reads] == [0x43, 0x41, 0x43]
        assert reads[0]['value'] & 2 and not reads[2]['value'] & 2
        scan = reads[1]['value']
        assert not reads[1]['uart']['rx_ready']
        expected = bytearray.fromhex(before['bios'])
        index, bit = (scan & 127)//8, 1 << (scan & 7)
        if scan & 128:
            expected[index] &= ~bit
        else:
            expected[index] |= bit
        assert expected.hex() == after['bios'], 'BIOS scan bitmap mutation'
        writes, written = select('pic-write-entry'), select('pic-write-return')
        assert len(writes) == len(written) == 1
        assert writes[0]['port'] == written[0]['port'] == 0
        assert writes[0]['value'] == written[0]['value'] == 0x20
        for row in group:
            if row['ordinal'] <= writes[0]['ordinal']:
                assert row['pic']['controllers'][0]['isr'] & 2
            elif row['ordinal'] >= written[0]['ordinal']:
                assert not row['pic']['controllers'][0]['isr'] & 2
        cpu = check(rom[4:11], after, returned)

        def cycles(a, b):
            value = (time[b['ordinal']]-time[a['ordinal']])*36000
            assert value >= 0
            return dict(numerator=value.numerator, denominator=value.denominator)

        results.append(dict(irq=number, scan=scan, rom_sha256=hashlib.sha256(rom[:11]).hexdigest(),
            monitor_iret_entry=monitor[0]['ordinal'], monitor_iret_return=monitor_returns[0]['ordinal'],
            bios_tail_iret_entry=tail_entries[0]['ordinal'], bios_tail_iret_return=returned['ordinal'],
            accept_to_bios_cycles=cycles(accepted, before), callback_cycles=cycles(before, after),
            bios_to_eoi_entry_cycles=cycles(after, writes[0]),
            eoi_write_cycles=cycles(writes[0], written[0]),
            eoi_return_to_iret_cycles=cycles(written[0], tail_entries[0]),
            tail_cycles=cycles(after, returned), full_irq_cycles=cycles(accepted, returned),
            cpu=cpu))
        if number == 1:
            tail = rom[4:11]
            controls = {
                'wrong-eoi-port': tail[:4]+bytes([0x20])+tail[5:],
                'wrong-eoi-value': tail[:2]+bytes([0x21])+tail[3:],
                'wrong-pop-register': tail[:5]+bytes([0x59])+tail[6:],
                'far-return-without-flags': tail[:6]+bytes([0xcb]),
            }
            for name, altered in controls.items():
                try:
                    check(altered, after, returned)
                except AssertionError:
                    negatives.append(name)
                else:
                    raise AssertionError('semantic ROM defect accepted: '+name)
            frame = bytearray.fromhex(after['stack'])
            frame[5] ^= 2
            try:
                check(tail, after, returned, frame=bytes(frame))
            except AssertionError:
                negatives.append('wrong-restored-if')
            else:
                raise AssertionError('incorrect interrupt frame accepted')
    assert len(negatives) == 5
    return dict(passed=True, interrupts=len(results), isr_records=len(rows), clock=ca,
        original_dispatch=base, independent_cpu=engine, results=results,
        semantic_rom_defects_rejected=negatives, current_product_changed=False,
        physical_timing_accepted=False, complete_campaign_accepted=False,
        scope='Original normal-boot first-eight Stage1 updates on one pinned DOSBox-X. '
              'Protected monitor entry/IRET, V86 BIOS callback, EOI and final IRET are separate. '
              'Independent real-mode CPU execution checks the standard seven-byte ROM tail; '
              'V86 protection/monitor implementation and physical instruction timing are outside that CPU projection. '
              'Audited emulator counter intervals are observations, not a fitted native IRQ delay, '
              'hardware cycle model, common boot epoch or complete-game acceptance.')


def _one(rows):
    assert len(rows) == 1
    return rows[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.capture)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('ORIGINAL IRQ SERVICE PASS', report['interrupts'], 'interrupts;',
          report['isr_records'], 'ISR records;', len(report['semantic_rom_defects_rejected']), 'semantic defects rejected')


if __name__ == '__main__':
    main()
