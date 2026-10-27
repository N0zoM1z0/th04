#!/usr/bin/env python3
"""Read closed Windows traces and compare independent renderer fixture outputs."""
import argparse
import hashlib
import json
from pathlib import Path

from verify_host_window import PERIOD, row


def percentiles(values):
    values = sorted(values)
    assert values
    return {str(p): values[min(len(values)-1, (len(values)-1)*p//100)]
            for p in (50, 95, 99, 100)}


def trace(path):
    lines = path.read_text().splitlines()
    rows = [row(line) for line in lines if line.startswith('R ')]
    presents = [list(map(int, line.split()[1:])) for line in lines if line.startswith('P ')]
    drops = [line for line in lines if line.startswith('D ')]
    ends = [list(map(int, line.split()[1:])) for line in lines if line.startswith('E ')]
    assert lines[0] == f'TH04_WINDOW_TRACE 3 period_ns {PERIOD} catchup_limit 4 muted 1'
    assert len(ends)==1 and ends[0][:3]==[len(rows),len(presents),len(drops)]
    assert ends[0][4:]==[0,0] and lines[-1].startswith('E ')
    assert [r['seq'] for r in rows]==list(range(1,len(rows)+1))
    assert all(r['begin']<=r['end'] and r['audio_opens']==r['audio_failed']==0 for r in rows)
    assert all(a['end']<=b['begin'] for a,b in zip(rows,rows[1:]))
    assert all(p[1]<=p[2] and p[0]<=len(rows) for p in presents)
    result = dict(refreshes=len(rows), presents=len(presents), resyncs=len(drops), audio_opens=0)
    result['presentation_interval_ms'] = percentiles(
        [(b[1]-a[1])/1e6 for a, b in zip(presents, presents[1:])])
    # Idle menu scenes repaint only on changes; their long gaps are expected.
    # Restrict this metric to MAIN and the normal one-refresh game cadence.
    main_intervals = [(b[1]-a[1])/1e6 for a,b in zip(presents,presents[1:])
                      if a[0] and b[0] and rows[a[0]-1]['scene']==rows[b[0]-1]['scene']=='main'
                      and rows[a[0]-1]['after']==rows[b[0]-1]['before']==1]
    if main_intervals:
        result['main_presentation_interval_ms'] = percentiles(main_intervals)
    result['deadline_lateness_ms'] = percentiles(
        [max(0, r['begin']-r['deadline'])/1e6 for r in rows])
    result['scene_update_ms'] = {
        scene: percentiles([(r['end']-r['begin'])/1e6 for r in rows if r['scene']==scene])
        for scene in sorted({r['scene'] for r in rows})}
    boundaries = []
    for a, b in zip(rows, rows[1:]):
        if a['scene'] != b['scene'] or (b['scene']=='main' and b['frame']==1 and a['frame']>1):
            boundaries.append(dict(seq=b['seq'], previous=a['scene'], scene=b['scene'],
                                   stage=b['stage'], frame=b['frame'],
                                   update_ms=(b['end']-b['begin'])/1e6))
    result['boundaries'] = boundaries
    result['trace_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def compare(before, after):
    def files(folder):
        return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in folder.rglob('*') if p.is_file()}
    old, new = files(before), files(after)
    assert old and old.keys()==new.keys(), 'Renderer fixture file sets differ'
    differences = [name for name in old if old[name]!=new[name]]
    assert not differences, differences
    return dict(files_equal=len(old), files=old,
                scope='Identical component inputs, complete output bytes; portable baseline comparison, not original DOS parity.')


def extra_route(folder):
    assert (folder/'controller-passed.txt').read_text().strip()=='exit 0'
    lines=(folder/'route/render-cost.tsv').read_text().splitlines()
    keys=lines[0].split()
    assert keys=='tick stage frame scene bullets turbo before after advance_ns repaint_ns'.split()
    samples=[{key: value if key=='scene' else int(value) for key,value in zip(keys,line.split())}
             for line in lines[1:]]
    result=(folder/'route/result.txt').read_text().split()
    result=dict(zip(result[::2],map(int,result[1::2])))
    assert result['fresh_op']==result['extra_visits']==result['registration_visits']==result['render_every']==1
    assert [s['tick'] for s in samples]==list(range(result['ticks']))
    states=[line.split() for line in (folder/'route/state.txt').read_text().splitlines()]
    main=[s for s in states if len(s)>14 and s[3]!='CHILD']
    handoff=next(int(b[0]) for a,b in zip(main,main[1:]) if int(a[14])==255 and int(b[14])==0)
    dense=[s for s in samples if s['tick']>=handoff and s['scene']=='main' and s['bullets']>=320]
    assert len(dense)>=100 and all(s['turbo']==1 for s in dense)
    return dict(ticks=len(samples), gengetsu_handoff_tick=handoff,
                maximum_bullets=max(s['bullets'] for s in samples), dense_samples=len(dense),
                dense_delay_factors=sorted({s['after'] for s in dense}),
                delay2_admissions=sum(s['after']==2 for s in samples),
                dense_advance_ms=percentiles([s['advance_ns']/1e6 for s in dense]),
                dense_warm_repaint_ms=percentiles([s['repaint_ns']/1e6 for s in dense]),
                cost_sha256=hashlib.sha256((folder/'route/render-cost.tsv').read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace', action='append', default=[], help='NAME=window.tsv')
    parser.add_argument('--before', type=Path)
    parser.add_argument('--after', type=Path)
    parser.add_argument('--extra-before', type=Path)
    parser.add_argument('--extra-after', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    report = {'traces': {name: trace(Path(path)) for name, path in
                         (item.split('=', 1) for item in args.trace)}}
    if args.before or args.after:
        assert args.before and args.after
        report['renderer'] = compare(args.before, args.after)
    if args.extra_before or args.extra_after:
        assert args.extra_before and args.extra_after
        old,new=extra_route(args.extra_before),extra_route(args.extra_after)
        assert old['dense_delay_factors']==[2] and new['dense_delay_factors']==[1]
        assert old['delay2_admissions']>10000 and 0<new['delay2_admissions']<=130
        report['extra'] = dict(before=old,after=new,
            scope='Full rendered ordinary Extra control with memory-only no-life-loss patch; diagnostic wall times include scheduling. Warm repaint is separate from update/audio; not continuous GDI/physical-display timing.')
    report['passed'] = True
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, traces=list(report['traces']),
                          renderer_files=report.get('renderer', {}).get('files_equal'))))


if __name__ == '__main__':
    main()
