#!/usr/bin/env python3
"""Validate complete muted window traces and reduce scheduling/route observations.

Read-only observer timings include instrumented host work and private display
cost. advance_ns excludes the separate advice/trace work after R end; deadline
lag includes lateness from the complete host loop. This reducer never accepts
original whole-route or physical performance.
"""
import argparse
import hashlib
import json
from pathlib import Path

from verify_host_window import PERIOD, row


def percentile(values, percentage):
    ordered = sorted(values)
    return ordered[min(len(ordered)-1, (len(ordered)-1)*percentage//100)]


def reduce(path):
    lines = path.read_text().splitlines()
    assert lines[0] in [f'TH04_WINDOW_TRACE {version} period_ns {PERIOD} catchup_limit 4 muted 1'
                       for version in (1, 2, 3)]
    version = int(lines[0].split()[1])
    width = {1: 29, 2: 38, 3: 40}[version]
    rows, presents, drops, ends = [], [], [], []
    next_deadline = None
    pending_resync = False
    previous_present_end = 0
    for line in lines[1:]:
        if line.startswith('#'):
            continue
        parts = line.split()
        assert parts, 'empty trace record'
        if parts[0] == 'R':
            assert len(parts) == width, 'header/body version mismatch'
            state = row(line)
            assert state['seq'] == len(rows) + 1
            assert state['begin'] >= state['deadline']
            assert state['begin'] <= state['end']
            assert state['before'] > 0 and state['after'] > 0
            assert state['audio_opens'] == state['audio_failed'] == 0
            if not state['focused']:
                assert state['held'] == state['shift'] == 0
            if rows:
                previous = rows[-1]
                assert state['begin'] >= previous['end']
                assert state['audio_frames'] >= previous['audio_frames']
                assert state['deadline'] == next_deadline, 'host deadline lost slowdown/resync'
            next_deadline = state['deadline'] + PERIOD * state['after']
            pending_resync = False
            rows.append(state)
        elif parts[0] == 'P':
            assert len(parts) == 5
            sequence, begin, end, updated = map(int, parts[1:])
            assert 0 <= sequence <= len(rows) and previous_present_end <= begin <= end
            assert updated in (0, 1)
            previous_present_end = end
            presents.append((sequence, begin, end, updated))
        elif parts[0] == 'D':
            assert len(parts) == 4 and rows
            now, discarded, slowdown = map(int, parts[1:])
            assert discarded > 0 and slowdown == rows[-1]['after']
            next_deadline = now + PERIOD * slowdown
            pending_resync = True
            drops.append((now, discarded, slowdown))
        elif parts[0] == 'E':
            assert len(parts) == 7 and rows
            ends.append(tuple(map(int, parts[1:])))
        else:
            raise ValueError('unknown trace record')
    assert rows and len(ends) == 1 and lines[-1].startswith('E ')
    assert ends[0][:3] == (len(rows), len(presents), len(drops))
    assert ends[0][3] >= rows[-1]['audio_frames'] and ends[0][4:] == (0, 0)
    main = [state for state in rows if state['scene'] == 'main']
    spans = []
    for state in main:
        identity = (state['generation'], state['stage'])
        if not spans or tuple(spans[-1]['identity']) != identity:
            spans.append(dict(identity=identity, first_refresh=state['seq'],
                              first_frame=state['frame'], refreshes=0,
                              max_bullets=0, slowdown2_refreshes=0))
        span = spans[-1]
        span['last_refresh'] = state['seq']
        span['last_frame'] = state['frame']
        span['last_misses'] = state['misses']
        span['last_lives'] = state['lives']
        span['refreshes'] += 1
        span['max_bullets'] = max(span['max_bullets'], state['bullets'])
        span['slowdown2_refreshes'] += state['after'] == 2
    advance = [state['end']-state['begin'] for state in rows]
    presentation = [end-begin for _, begin, end, updated in presents if updated]
    return dict(passed=True, trace_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                version=version, refreshes=len(rows), presents=len(presents),
                resyncs=len(drops), terminal_resync_without_following_refresh=pending_resync,
                observed_ns=rows[-1]['end']-rows[0]['begin'],
                deadline_lag_ns={p: percentile([state['begin']-state['deadline'] for state in rows], p)
                                 for p in (50, 95, 99, 100)},
                stages=spans, gameover_refreshes=sum(state['scene']=='gameover' for state in rows),
                advance_ns={p: percentile(advance, p) for p in (50, 95, 99, 100)},
                presentation_ns={p: percentile(presentation, p) for p in (50, 95, 99, 100)},
                audio_opens=0, scope=__doc__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'fresh reduction output required'
    result = reduce(args.trace)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('refreshes', 'presents', 'resyncs', 'audio_opens')}))


if __name__ == '__main__':
    main()
