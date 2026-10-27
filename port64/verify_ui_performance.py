#!/usr/bin/env python3
"""Compare closed Ending/registration replays and no-death negative controls."""
import argparse
import hashlib
import json
from pathlib import Path

from verify_frame_pacing import percentiles, trace
from verify_host_window import row
from verify_background_results import natural_case, window_case
from verify_natural_routes import decode


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def equal_files(before,after,select=lambda p: True):
    old={str(p.relative_to(before)):sha(p) for p in before.rglob('*') if p.is_file() and select(p)}
    new={str(p.relative_to(after)):sha(p) for p in after.rglob('*') if p.is_file() and select(p)}
    assert old and old==new, [k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)]
    return dict(count=len(old),files=old)


def ui_case(folder):
    assert (folder/'controller-passed.txt').read_text().strip()=='exit 0'
    result=trace(folder/'trace/window.tsv')
    rows=[row(l) for l in (folder/'trace/window.tsv').read_text().splitlines() if l.startswith('R ')]
    actions={l.split('\t')[0]:list(map(int,l.split('\t')[1:])) for l in (folder/'actions.tsv').read_text().splitlines()}
    taps={}
    for name in ('cursor-right','cursor-down','cursor-left'):
        begin,end=actions[name]
        candidates=[r for r in rows if begin<r['seq']<=end and r['scene']=='registration']
        original=rows[begin-1]
        changed=next(r for r in candidates if (r['x'],r['y'])!=(original['x'],original['y']))
        held=next(r for r in candidates if r['held']&15)
        lag=changed['seq']-held['seq']
        assert 0<=lag<=2, (name,lag)
        taps[name]=lag
    begin,end=actions['cursor-right-hold']
    previous=rows[begin-1];moves=[]
    for r in rows:
        if begin<r['seq']<=end and r['scene']=='registration':
            if r['x']!=previous['x']:moves.append(r['seq'])
            previous=r
    assert len(moves)>=3
    result['cursor_tap_latency_refreshes']=taps
    result['held_cursor_move_intervals_refreshes']=[b-a for a,b in zip(moves,moves[1:])]
    sections=decode((folder/'saves/GENSOU.SCR').read_bytes())
    assert len(sections)==10 and all(int.from_bytes(s[2:4],'little')==sum(s[4:]) for s in sections)
    result['saved_checksums']=10
    assert any(r['scene']=='startup' for r in rows[actions['save'][0]:]), 'No fresh OP after save'
    return result


def contact(folder):
    assert (folder/'controller-passed.txt').read_text().strip()=='exit 0'
    rows=[l.split() for l in (folder/'route/state.txt').read_text().splitlines() if 'CHILD' not in l]
    assert len(rows)>1000
    return dict(samples=len(rows),misses=max(int(r[9]) for r in rows),
                respawn_samples=sum(int(r[12])>0 for r in rows),
                minimum_lives=min(int(r[6]) for r in rows))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--god-root',type=Path);a=p.parse_args()
    assert not a.output.exists();root=a.root;current=root/'release';god_root=a.god_root or current
    selected=lambda p:p.suffix=='.bin' or p.name in ('state.tsv','GENSOU.SCR')
    graphics=equal_files(root/'before-probe/checks',current/'probe/checks',selected)
    assert (current/'probe/checks/font-rows-passed.txt').read_text().startswith('65536 codes')
    registration=equal_files(root/'before-components/checks',current/'components/checks')
    costs={}
    for name,folder in [('before',root/'before-probe/checks'),('after',current/'probe/checks')]:
        samples=[l.split() for l in (folder/'costs.tsv').read_text().splitlines()[1:]]
        costs[name]={}
        for scene in sorted({s[0] for s in samples}):
            group=[s for s in samples if s[0]==scene]
            costs[name][scene]=dict(advance_ms=percentiles([int(s[2])/1e6 for s in group]),redraw_ms=percentiles([int(s[3])/1e6 for s in group]))
        io=[l.split() for l in (folder/'io.tsv').read_text().splitlines()[1:]]
        costs[name]['file_operations_ms']=percentiles([int(s[0])/1e6 for s in io])
    windows={name:ui_case(root/name) for name in ('before-registration','before-ending')}
    windows.update({name:ui_case(current/name) for name in ('registration','ending')})
    ordinary,god=contact(god_root/'ordinary-contact'),contact(god_root/'god-contact')
    assert ordinary['misses']>0 and ordinary['respawn_samples']>0
    assert god['misses']==god['respawn_samples']==0 and god['minimum_lives']>=6
    routes={name:natural_case(god_root/name,dict(rank=1,character=0,shot=0,extra=name=='god-extra',no_life_loss=True,invincible=True)) for name in ('god-normal','god-extra')}
    hook=window_case(god_root/'god-hook')
    result=dict(passed=True,graphics=graphics,registration=registration,costs=costs,windows=windows,
                ordinary_contact=ordinary,no_death_contact=god,no_death_routes=routes,hook=hook,
                scope='Actual Windows muted private windows plus explicit seeded/component controls. Eight graphics scripts bypass PMD measure waits only in the probe; real Ending window keeps its sound clock. No physical input/audio/display or DOS parity claim.')
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,graphics_files=graphics['count'],registration_files=registration['count'],ordinary_misses=ordinary['misses'],god_misses=god['misses'])))


if __name__=='__main__':main()
