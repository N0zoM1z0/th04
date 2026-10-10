#!/usr/bin/env python3
"""Read-only window trace and real X11 key-stream controls; audio stays muted.

Run the Linux controller under a private xvfb-run. The trace is an observer,
not an input/state injection interface. X11/SendInput observations establish OS
input/window behavior, not human keyboard, physical display or original timing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from verify import source_manifest, require_elf_x86_64

FIELDS = 'seq begin end deadline held shift focused before after scene program generation frame stage rank character shot x y bullets shots lives bombs misses invincibility audio_frames audio_opens audio_failed'.split()
PERIOD = 17730496

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def row(line):
    parts = line.split()
    if not parts or parts[0] != 'R':
        return None
    if len(parts) != len(FIELDS) + 1:
        raise ValueError('incomplete refresh trace')
    return {key: value if key == 'scene' else int(value) for key, value in zip(FIELDS, parts[1:])}

def latest(path):
    if not path.exists():
        return None
    with path.open('rb') as stream:
        stream.seek(max(0, path.stat().st_size - 16384))
        data = stream.read().decode('ascii')
        lines = data.splitlines()
    for line in reversed(lines if data.endswith('\n') else lines[:-1]):
        if line.startswith('R '):
            try:
                return row(line)
            except ValueError:
                continue
    return None

def assess(path, actions):
    lines = path.read_text().splitlines()
    assert lines[0] == f'TH04_WINDOW_TRACE 1 period_ns {PERIOD} catchup_limit 4 muted 1'
    rows = [row(line) for line in lines if line.startswith('R ')]
    presents = [list(map(int, line.split()[1:])) for line in lines if line.startswith('P ')]
    drops = [list(map(int, line.split()[1:])) for line in lines if line.startswith('D ')]
    ends = [list(map(int, line.split()[1:])) for line in lines if line.startswith('E ')]
    next_resync = {}
    sequence = 0
    for line in lines:
        if line.startswith('R '):
            sequence = int(line.split()[1])
        elif line.startswith('D '):
            now, discarded, slowdown = map(int, line.split()[1:])
            assert discarded > 0 and slowdown > 0
            next_resync[sequence + 1] = now + PERIOD * slowdown
    assert len(ends) == 1 and ends[0][:3] == [len(rows), len(presents), len(drops)]
    assert ends[0][4:] == [0, 0], 'muted device was opened/failed'
    assert [r['seq'] for r in rows] == list(range(1, len(rows) + 1))
    for i, r in enumerate(rows):
        assert r['begin'] <= r['end'] and r['before'] > 0 and r['after'] > 0
        assert r['audio_opens'] == 0 and r['audio_failed'] == 0
        if not r['focused']:
            assert r['held'] == 0 and r['shift'] == 0
        if i:
            previous = rows[i-1]
            assert r['begin'] >= previous['end'] and r['audio_frames'] >= previous['audio_frames']
            # A resync may replace the otherwise exact after-update deadline.
            expected = previous['deadline'] + PERIOD * previous['after']
            if r['deadline'] != expected:
                assert next_resync.get(r['seq']) == r['deadline'], 'unrecorded deadline change'
    assert presents and any(p[3] for p in presents)
    assert all(begin <= end and seq <= len(rows) for seq, begin, end, _ in presents)
    trials = {}
    for action in actions:
        selected = [r for r in rows if action['begin'] < r['seq'] <= action['end']]
        assert selected, action
        name = action['name']
        if name == 'background':
            selected = [r for r in selected if not r['focused']]
            assert len(selected) >= 3 and all(r['held'] == 0 and r['shift'] == 0 for r in selected)
        elif name in ('enter', 'keypad-enter', 'right', 'shift-left', 'shot'):
            mask = {'enter':0x1000, 'keypad-enter':0x1000, 'right':8, 'shift-left':4, 'shot':32}[name]
            selected = [r for r in selected if r['scene'] == 'main' and r['held'] & mask]
            assert len(selected) >= 3, (name, selected)
            if name == 'shift-left':
                assert all(r['shift'] for r in selected)
            if name in ('right', 'shift-left'):
                deltas = [b['x']-a['x'] for a, b in zip(selected, selected[1:]) if b['frame'] == a['frame']+1]
                assert deltas and all(d > 0 if name == 'right' else d < 0 for d in deltas)
                trials[name] = dict(samples=len(selected), deltas_q12_4=sorted(set(deltas)))
            elif name == 'shot':
                assert max(r['shots'] for r in selected) >= 2
        elif name == 'release':
            assert any(r['scene'] == 'main' and r['held'] == 0 and r['shots'] == 0 for r in selected)
        trials.setdefault(name, dict(samples=len(selected)))
    assert {'enter', 'keypad-enter', 'right', 'shift-left', 'shot', 'release', 'background'} <= trials.keys()
    assert max(abs(d) for d in trials['shift-left']['deltas_q12_4']) < min(trials['right']['deltas_q12_4'])
    def quantiles(values):
        values=sorted(values)
        return {str(p):values[min(len(values)-1, int((len(values)-1)*p/100))] for p in (50,95,99,100)}
    return dict(refreshes=len(rows),presents=len(presents),resyncs=len(drops),trials=trials,
                advance_ns=quantiles([r['end']-r['begin'] for r in rows]),
                presentation_ns=quantiles([p[2]-p[1] for p in presents]),audio_opens=0,
                limitations='Read-only trace adds observer I/O cost. CPU advance/render and host presentation are measured separately. No physical keyboard/display/audio or dense Lunatic/full route timing acceptance.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('exe','hdi','font','output'):
        parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    mf,source=source_manifest(root);out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    exe,hdi,font=[p.resolve() for p in (args.exe,args.hdi,args.font)]
    require_elf_x86_64(exe)
    assert sha(hdi)=='0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(font)=='41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    inputs={str(p):sha(p) for p in (exe,hdi,font)}
    saves=out/'saves';saves.mkdir();cfg=bytes([3,6,2,2,1,1,0,0,0,15])
    (out/'initial-MIKO.CFG').write_bytes(cfg);(saves/'MIKO.CFG').write_bytes(cfg)
    trace=out/'trace'/'window.tsv'
    command=[str(exe),'--hdi',str(hdi),'--font-bmp',str(font),'--save-dir',str(saves),'--title','--mute','--window-trace',str(trace.parent)]
    log=(out/'window.log').open('wb');process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
    held=[];actions=[];sink=None
    def x(*arguments):
        return subprocess.run(['xdotool',*arguments],check=True,capture_output=True,text=True).stdout.strip()
    def wait(predicate,timeout=45):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if process.poll() is not None:raise RuntimeError('window exited during observation')
            state=latest(trace)
            if state and predicate(state):return state
            time.sleep(.025)
        raise RuntimeError('window observation timeout')
    def sequence():return wait(lambda _:True)['seq']
    def action(name,keys,duration):
        start=sequence()
        for key in keys:x('keydown',key);held.append(key)
        time.sleep(duration)
        end=sequence()
        for key in reversed(keys):x('keyup',key);held.remove(key)
        actions.append(dict(name=name,keys=keys,begin=start,end=end));time.sleep(.06)
    try:
        wait(lambda _:True)
        windows=x('search','--onlyvisible','--pid',str(process.pid)).splitlines();assert len(windows)==1
        window=windows[0];x('windowfocus','--sync',window)
        # Natural muted startup; no frontend state writes or forced transitions.
        wait(lambda r:r['scene']=='menu')
        action('start',['Return'],.15);wait(lambda r:r['scene']=='character')
        action('marisa',['Right'],.15);action('character',['Return'],.15)
        wait(lambda r:r['scene']=='shot');action('shot-b',['Down'],.15);action('selection',['Return'],.15)
        wait(lambda r:r['scene']=='main' and r['frame']>=96)
        for name,keys,duration in [('enter',['Return'],.15),('keypad-enter',['KP_Enter'],.15),
                                  ('right',['Right'],.15),('shift-left',['Shift_L','Left'],.15),
                                  ('shot',['z'],.3),('release',[],.8)]:action(name,keys,duration)
        subprocess.run(['import','-window',window,str(out/'main.png')],check=True)
        sink=subprocess.Popen(['xmessage','-title','TH04 owned input focus control','-geometry','120x80+0+0','focus'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        deadline=time.monotonic()+5;sink_window=None
        while time.monotonic()<deadline:
            found=subprocess.run(['xdotool','search','--onlyvisible','--name','^TH04 owned input focus control$'],capture_output=True,text=True)
            if found.returncode==0:sink_window=found.stdout.splitlines()[-1];break
            time.sleep(.025)
        assert sink_window is not None;x('windowfocus','--sync',sink_window)
        wait(lambda r:not r['focused']);action('background',['Shift_L','Right'],.15)
        x('windowfocus','--sync',window);wait(lambda r:r['focused'])
        x('key','Escape');process.wait(timeout=15);assert process.returncode==0
        report=assess(trace,actions)
        assert (saves/'MIKO.CFG').read_bytes()==cfg
        for path,digest in inputs.items():assert sha(path)==digest
        assert source_manifest(root)[0]==mf
        receipt=dict(passed=True,source_manifest=mf,source_files=len(source),inputs=inputs,command=command,
                     display=os.environ.get('DISPLAY'),actions=actions,assessment=report,
                     trace_sha256=sha(trace),saves={p.name:sha(p) for p in saves.iterdir() if p.is_file()})
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(report),flush=True)
    finally:
        for key in reversed(held):subprocess.run(['xdotool','keyup',key],check=False)
        if sink is not None and sink.poll() is None:sink.terminate();sink.wait(timeout=5)
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        log.close()
        (out/'actions.json').write_text(json.dumps(actions,indent=2)+'\n')
if __name__=='__main__':main()
