#!/usr/bin/env python3
"""Audit original V86 PIC dispatch and BIOS/EOI boundaries, without fitting time."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

OFFSETS = dict(special=16, auto_eoi=17, rotate_on_auto_eoi=18, single=19,
               request_issr=20, vector_base=21, irr=22, imr=23, imrr=24,
               isr=25, isrr=26, isr_ignore=27, active_irq=28)
MAIN = '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
ENGINE = '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1'


def active(service):
    return next((line for line in range(8) if service & (1 << line)), 8)


def controllers(row):
    items = row['pic']['controllers']
    assert len(items) == 2
    for item in items:
        raw = bytes.fromhex(item['raw'])
        assert len(raw) == 32
        assert all(item[name] == raw[offset] for name, offset in OFFSETS.items())
        assert item['imrr'] == (~item['imr'] & 255)
        assert item['isrr'] == ((~item['isr'] | item['isr_ignore']) & 255)
        assert item['active_irq'] == active(item['isr'])
        assert item['special'] == item['auto_eoi'] == item['rotate_on_auto_eoi'] == 0
    return items


def reduce(rows, meta, stage):
    """Return auditable projections; observation ordering is never elapsed time."""
    assert meta['complete'] and not meta['error'] and not meta['active'] and not meta['in_irq']
    assert len(rows) == meta['records']
    assert [row['ordinal'] for row in rows] == list(range(len(rows)))
    assert stage['complete'] and stage['observed_loops'] == stage['extent']
    assert stage['attested_prefix'] == 0 and stage['tail_expectation_pass'] is None
    assert not stage['gameover_guard_fired']
    assert all(action['unchanged_guest'] for action in stage['actions'])
    counts = Counter(row['kind'] for row in rows)
    assert counts['main-image-entry'] == counts['packet-start'] == counts['packet-end'] == 1
    vectors = Counter()
    dispatches, eois, bios = [], [], []
    pending = {}
    irq = None
    for index, row in enumerate(rows):
        master, slave = controllers(row)
        guard = row['pic']['cpu_dispatch']
        assert master['vector_base'] == 8 and slave['vector_base'] == 16
        assert master['isr_ignore'] == 128 and slave['isr_ignore'] == 0
        assert guard['cascade_irq'] == 7 and guard['ignore_cascade_in_service'] == 1
        assert guard['never_mark_cascade_in_service'] == 0
        assert not guard['nmi_active'] and not guard['nmi_pending']
        assert guard['decoder'] != guard['trap_decoder']
        kind = row['kind']
        if kind == 'cpu-irq-accept':
            vector = row['vector']
            assert row['interrupt_type'] == 0 and row['context']['flags'] & 512
            assert row['context']['flags'] & 0x20000, 'observed guest V86 acceptance'
            assert guard['irq_check']
            if vector < 16:
                assert master['isr'] & (1 << (vector-8))
            else:
                assert master['isr'] & 128 and slave['isr'] & (1 << (vector-16))
            vectors[vector] += 1
        elif kind == 'pic-dispatch-entry':
            assert 'dispatch' not in pending
            pending['dispatch'] = row
        elif kind == 'pic-dispatch-return':
            before = pending.pop('dispatch')
            p = before['pic']['controllers'][0]
            g = before['pic']['cpu_dispatch']
            # Compare only the native normal-primary domain. The captured
            # cascade workaround is active elsewhere in this same window.
            assert not p['isr'] & 128 and not (p['irr'] & ~p['imr'] & 128)
            enabled = bool(before['context']['flags'] & 512)
            allowed = enabled and bool(g['irq_check'])
            possible = p['irr'] & ~p['imr'] & ~p['isr'] & 255
            selected = next((line for line in range(active(p['isr']))
                             if possible & (1 << line)), 8) if allowed else 8
            accepts = [item for item in rows[before['ordinal']+1:index]
                       if item['kind'] == 'cpu-irq-accept']
            assert [item['vector'] for item in accepts] == ([] if selected == 8 else [selected+8])
            dispatches.append(dict(ordinal=before['ordinal'], requests=p['irr'], mask=p['imr'],
                                   service=p['isr'], enabled=allowed, selected=selected))
        elif kind == 'pic-write-entry':
            assert 'write' not in pending
            pending['write'] = row
        elif kind == 'pic-write-return':
            before = pending.pop('write')
            assert (before['port'], before['value']) == (row['port'], row['value'])
            port, value = row['port'], row['value']
            if port in (0, 8) and value & 0x20 and not value & 0x80:
                number = int(port == 8)
                old = before['pic']['controllers'][number]
                new = (master, slave)[number]
                line = (value & 7) if value & 0x40 else active(old['isr'])
                expected = old['isr'] & ~(1 << line) if line < 8 else old['isr']
                assert new['isr'] == expected
                assert (new['irr'], new['imr']) == (old['irr'], old['imr'])
                eois.append(dict(ordinal=before['ordinal'], controller=number, line=line,
                                 specific=bool(value & 0x40),
                                 requests=old['irr'], mask=old['imr'], service=old['isr'],
                                 after_service=new['isr'], after_active=new['active_irq']))
        elif kind == 'bios-irq-entry':
            assert irq is None and master['isr'] & 2
            irq = row
        elif kind == 'bios-irq-return':
            assert irq is not None and master['isr'] & 2 and not row['uart']['rx_ready']
            stores = [item for item in rows[irq['ordinal']+1:index]
                      if item['kind'] == 'bios-write-return']
            assert len(stores) == 1
            following = rows[index+1:index+3]
            assert [item['kind'] for item in following] == ['pic-dispatch-entry', 'pic-dispatch-return']
            # Find the guest EOI after the callback returns; a following
            # dispatch attempt does not clear the keyboard service bit.
            end = next(item for item in rows[index+1:]
                       if item['kind'] == 'pic-write-entry' and item['port'] == 0)
            assert end['value'] == 32 and end['pic']['controllers'][0]['isr'] & 2
            bios.append(dict(entry=irq['ordinal'], store=stores[0]['ordinal'],
                             returned=index, eoi=end['ordinal']))
            irq = None
    assert not pending and irq is None
    assert vectors[9] == len(bios) == counts['irq1-request'] == counts['rx-return']
    return dict(passed=True, records=len(rows), observed_loops=stage['observed_loops'],
                vectors=dict(sorted(vectors.items())), bios_boundaries=bios,
                normal_primary_dispatches=dispatches, eois=eois,
                entry_master_mask=rows[0]['pic']['controllers'][0]['imr'],
                stage_master_masks=sorted({row['pic']['controllers'][0]['imr'] for row in rows[1:]}),
                slave_masks=sorted({row['pic']['controllers'][1]['imr'] for row in rows}),
                cascade_in_service_observed=any(row['pic']['controllers'][0]['isr'] & 128 for row in rows),
                raw_clocks_are_audited_latency=False, original_timing_accepted=False,
                scope='Original candidate-local-attested MAIN, bounded first-stage window on one pinned emulator. '
                      'Dispatch projection excludes active cascade arbitration; EOI snapshots include both controllers. '
                      'No CPU scheduling, elapsed epoch, fixed latency, full campaign or hardware acceptance.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = args.capture
    load = lambda name: json.loads((base/name).read_text())
    receipt = load('receipt.json')
    assert receipt['complete'] and receipt['exit'] == 0 and not receipt['timeout']
    assert receipt['main_sha256'] == MAIN and receipt['emulator_sha256'] == ENGINE
    for batch in (receipt['source_files'], receipt['capsule'],
                  {str(base/name): digest for name, digest in receipt['files'].items()}):
        for name, digest in batch.items():
            with Path(name).open('rb') as source:
                assert hashlib.file_digest(source, 'sha256').hexdigest() == digest, name
    image = load('original-pic-image.json')
    assert image['passed'] and image['unchanged_context'] and image['module_size'] == 150114
    assert image['target_main_sha256'] == MAIN and image['entry_ip'] == 0
    assert image['entry_cs'] == image['load_segment']
    stream = (base/'keyboard-admission.jsonl').read_bytes()
    meta = load('keyboard-admission.json')
    assert hashlib.sha256(stream).hexdigest() == meta['stream_sha256']
    report = reduce([json.loads(line) for line in stream.splitlines()], meta, load('stage-input.json'))
    report['capture_receipt_sha256'] = hashlib.sha256((base/'receipt.json').read_bytes()).hexdigest()
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('ORIGINAL V86 PIC AUDIT PASS', report['records'], 'rows;', len(report['bios_boundaries']), 'BIOS/EOI pairs')


if __name__ == '__main__':
    main()
