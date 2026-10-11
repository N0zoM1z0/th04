#!/usr/bin/env python3
"""Verify complete original OP IRQ increments against independent raster phases.

Checks the base target/load/PIC/raw-counter/GDC gate, every counted IRQ before
its increment, and each armed host IRQ callback. Beam geometry predicts the
scheduled edge; actual CPU service latency is recorded separately, not fitted.
This is a bounded DOSBox-X Oracle, not a physical or native frontend verdict.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import verify_op_wait_clock as waits

ROOT = Path(__file__).resolve().parents[2]
require, sha, pic = waits.require, waits.sha, waits.pic


def raster(raw: bytes) -> tuple[float, float]:
    require(len(raw) == 540 and raw[535] == 0, '24-kHz raster extent / mode')
    lines, words, pitch, hs, vs, hfp, hbp, vfp, vbp = struct.unpack_from('<HHH6B', raw, 180)
    require(pitch == words and lines > 0 and words > 0, 'raster geometry')
    horizontal, vertical = words + hs + hfp + hbp, lines + vs + vfp + vbp
    line_ms = horizontal * 1000 / (21052600 // 8)
    period = vertical * line_ms
    require(abs(period - struct.unpack_from('<d', raw, 499)[0]) < 1e-12, 'raster period differs')
    # Pinned source explicitly casts the IRQ schedule delay to float.
    delay = struct.unpack('<f', struct.pack('<f', (lines + vfp) * line_ms + .0001))[0]
    return delay, period


def check_irqs(observation: dict) -> dict:
    rows = observation['rows']
    irqs = [r for r in rows if r['name'] == 'irq_before_increment']
    callbacks = [r for r in observation['timer_rows'] if r['kind'] == 'vsync_irq_event' and r['armed']]
    require(len(irqs) > 1 and len(irqs) == len(callbacks), 'complete armed IRQ / guest pairing')
    one = two = 0
    for row in rows:
        require(row['cadence_increment_hex'] == row['cadence_accumulator_hex'] == '0000',
                '24-kHz cadence skip state')
        if row['name'] == 'logo_wait_reset':
            one = 0
        require(waits.counters(row) == (one, two), 'complete IRQ counter progression')
        if row['name'] == 'irq_before_increment':
            require(row['ax'] == 0, 'IRQ increment register')
            one = (one + 1) & 65535
            two = (two + 1) & 65535
    require(two == len(irqs) == waits.counters(rows[-1])[1], 'terminal counted IRQ extent')
    planned, dispatched, serviced, latencies = [], [], [], []
    for guest, callback in zip(irqs, callbacks, strict=True):
        raw = bytes.fromhex(callback['gdc_clock_hex'])
        offset, period = raster(raw)
        frame_start = struct.unpack_from('<d', raw, 491)[0]
        due = frame_start + offset
        actual, service = pic(callback), pic(guest)
        # PIC may execute after a guest instruction/I/O overrun. It must not
        # fire before the source deadline or beyond this retrace's frame.
        require(due <= actual + 1e-8 and actual < frame_start + period,
                'IRQ callback outside scheduled retrace')
        require(actual <= service and service < frame_start + period, 'IRQ service outside retrace')
        blink = bytes(((callback['display_events'] // 32) & 3, callback['display_events'] % 32, 32))
        require(raw[196:199] == raw[428:431] == blink, 'IRQ snapshot / independent GDC phase')
        planned.append(due);dispatched.append(actual);serviced.append(service)
        latencies.append((service - actual) * guest['cycle_state']['CPU_CycleMax'])
    require(all(a < b for a, b in zip(planned, planned[1:])), 'IRQ source timeline order')
    require(len({round(x, 6) for x in latencies}) > 1, 'fixture lacks service-latency variation')
    return dict(counted_irqs=len(irqs), scheduled_edges_ms=planned,
                actual_callbacks_ms=dispatched, counter_instruction_ms=serviced,
                service_latency_cycles=latencies,
                callback_lateness_cycles=[(a-b)*rows[-1]['cycle_state']['CPU_CycleMax']
                                          for a,b in zip(dispatched,planned)],
                terminal_counters=waits.counters(rows[-1]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, action='append', required=True)
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--model-receipt', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    require(not output.exists() and output.is_relative_to(ROOT / '.analysis'), 'fresh private output')
    parent = json.loads(args.model_receipt.read_text());model = args.model_dir.resolve() / 'model'
    require(parent['passed'] and sha(model) == parent['model_program_sha256'] and
            sha(args.model_dir / 'model.cpp') == parent['model_source_sha256'], 'independent GDC model identity')
    output.mkdir(parents=True);captures=[]
    for path in args.capture:
        base = waits.verify(path.resolve(), output, model, irq_extension=True)
        observation = json.loads((path / 'startup-observation.json').read_text())
        irq = check_irqs(observation)
        negatives=[]
        for kind in ('missing-IRQ', 'counter-word', 'cadence-skip', 'blink-alias', 'frame-start'):
            changed = copy.deepcopy(observation)
            guest = next(r for r in changed['rows'] if r['name'] == 'irq_before_increment')
            callback = next(r for r in changed['timer_rows'] if r['kind'] == 'vsync_irq_event' and r['armed'])
            if kind == 'missing-IRQ':
                changed['rows'].remove(guest)
            elif kind == 'counter-word':
                guest['vsync_counts_hex'] = '00000100'
            elif kind == 'cadence-skip':
                guest['cadence_increment_hex'] = '0100'
            else:
                raw = bytearray.fromhex(callback['gdc_clock_hex'])
                if kind == 'blink-alias':raw[197] ^= 1
                else:struct.pack_into('<d', raw, 491, struct.unpack_from('<d', raw, 491)[0] + 1)
                callback['gdc_clock_hex'] = raw.hex()
            try:check_irqs(changed)
            except ValueError:negatives.append(kind)
            else:raise ValueError('IRQ mutation accepted: ' + kind)
        base.update(irq=irq,irq_negative_controls=negatives);captures.append(base)
    require(sorted(c['cycles'] for c in captures) == [24000,36000], 'complete CPU pair')
    report=dict(passed=True,source_sha256=sha(Path(__file__)),wait_reader_sha256=sha(Path(waits.__file__)),
                model_program_sha256=sha(model),captures=captures,scope=__doc__)
    (output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS complete IRQ / retrace phase:',[(c['cycles'],c['irq']['counted_irqs'],
        min(c['irq']['service_latency_cycles']),max(c['irq']['service_latency_cycles']))for c in captures])


if __name__ == '__main__':
    main()
