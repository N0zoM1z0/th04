#!/usr/bin/env python3
"""Ordinary Extra OS route from a physically earned Normal save, fully muted.

Requires a passed Normal window/physical-restart receipt. No unlock, actor,
score, life, clock or transition injection. Live advice is read-only; ordinary
X11 keys drive gameplay, eight A glyphs, congratulations/verdict and fresh OP.
Private Xvfb is mandatory. Observer CPU/I-O cost is not timing acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from private_x11 import key_names, require_private_xvfb
from private_x11_keys import PrivateKeys
from verify import require_elf_x86_64
from verify_host_window import latest, row
from verify_window_continue import Writes, decode, entries, restart

ROOT = Path(__file__).resolve().parents[1]
FULL_NAME = bytes([0xaa] * 8).hex()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def earned_normal(path):
    """Reject logical-only, incomplete, mismatched or unearned admission files."""
    report = json.loads((path / 'receipt.json').read_text())
    if not report.get('passed') or report.get('stages') != list(range(6)):
        raise ValueError('a passed actual six-stage Normal window route is required')
    assert report['restart']['passed']
    assert report['restart']['files_before'] == report['restart']['files_after']
    assert sha(path / 'trace/window.tsv') == report['trace_sha256']
    lines = (path / 'trace/window.tsv').read_text().splitlines()
    rows = [row(line) for line in lines if line.startswith('R ')]
    ends = [list(map(int, line.split()[1:])) for line in lines if line.startswith('E ')]
    assert rows and rows[0]['scene'] == 'startup'
    assert (rows[-1]['scene'], rows[-1]['program']) == ('menu', 0)
    assert len(ends) == 1 and ends[0][0] == len(rows) and ends[0][4:] == [0, 0]
    assert {state['stage'] for state in rows if state['scene'] == 'main'} == set(range(6))
    assert not any(state['scene'] == 'gameover' for state in rows)
    assert all(state['audio_opens'] == state['audio_failed'] == 0 for state in rows)
    child = {(state['program'], state['generation'], state['scene']) for state in rows}
    assert (2, 3, 'maine') in child and (2, 3, 'registration') in child
    restarted = path / 'restart/trace/window.tsv'
    assert sha(restarted) == report['restart']['trace_sha256']
    restart_rows = [row(line) for line in restarted.read_text().splitlines() if line.startswith('R ')]
    assert any(state['scene'] == 'ranking' for state in restart_rows)
    assert all(state['generation'] == 1 and state['program'] == 0 for state in restart_rows)
    for event in report['physical_events']:
        assert event['mask'] & 0x80
        assert sha(path / 'physical-events' / event['snapshot']) == event['sha256']
    for name in ('GENSOU.SCR', 'MIKO.CFG'):
        assert sha(path / 'saves' / name) == report['files'][name]
        assert report['restart']['files_after'][name] == report['files'][name]
    sections = decode((path / 'saves/GENSOU.SCR').read_bytes())
    assert sections[1][174] & 1, 'Reimu A admission must be earned at Normal rank'
    assert (path / 'saves/MIKO.CFG').read_bytes() == bytes([1, 6, 2, 2, 1, 1, 0, 0, 0, 13])
    snapshots = [decode((path / 'physical-events' / event['snapshot']).read_bytes())
                 for event in report['physical_events'] if event['name'] == 'GENSOU.SCR']
    assert any(section[1][174] & 1 for section in snapshots)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('exe', 'hdi', 'font', 'normal-route', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--exe-sha256', required=True)
    parser.add_argument('--key-driver', choices=('xdotool', 'xtest'), default='xdotool')
    args = parser.parse_args()
    private_display = require_private_xvfb()
    exe, hdi, font, normal = [path.resolve() for path in
                              (args.exe, args.hdi, args.font, args.normal_route)]
    normal_report = earned_normal(normal)
    require_elf_x86_64(exe)
    assert sha(exe) == args.exe_sha256
    assert sha(hdi) == '0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(font) == '41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    pin_paths = [exe, hdi, font, Path(__file__), normal / 'receipt.json',
                 normal / 'saves/MIKO.CFG', normal / 'saves/GENSOU.SCR',
                 ROOT / 'port64/private_x11.py', ROOT / 'port64/verify_host_window.py',
                 ROOT / 'port64/verify_window_continue.py', ROOT / 'port64/private_x11_keys.py']
    pins = {str(path): sha(path) for path in pin_paths}
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    save = out / 'saves'
    save.mkdir()
    for name in ('MIKO.CFG', 'GENSOU.SCR'):
        shutil.copyfile(normal / 'saves' / name, save / name)
        shutil.copyfile(save / name, out / ('initial-' + name))
    initial = decode((save / 'GENSOU.SCR').read_bytes())
    trace = out / 'trace/window.tsv'
    command = [str(exe), '--hdi', str(hdi), '--font-bmp', str(font),
               '--save-dir', str(save), '--title', '--mute',
               '--window-trace', str(trace.parent), '--window-route-advice']
    log = (out / 'window.log').open('wb')
    actions = (out / 'actions.jsonl').open('w')
    writes = Writes(save, out / 'physical-events', trace)
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
    held = set()
    events = []
    scenes = set()
    last = 0
    started = time.monotonic()
    progress = 0
    registration_pulses = 0
    previous_registration_keys = set()
    passed = False
    error = None
    keyboard = None

    def x(*arguments):
        return subprocess.run(['xdotool', *arguments], check=True,
                              capture_output=True, text=True).stdout.strip()

    def wait(predicate, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            writes.pump()
            if process.poll() is not None:
                raise RuntimeError('owned Extra window exited during observation')
            state = latest(trace)
            if state and predicate(state):
                return state
            time.sleep(.001)
        raise RuntimeError('Extra observation timed out; owned process closes in finally')

    def keys(desired, state):
        desired = set(desired)
        if desired == held:
            return
        input_started_ns = time.monotonic_ns()
        if keyboard is not None:
            keyboard.set(desired)
        else:
            for key in sorted(held - desired):
                x('keyup', key)
            for key in sorted(desired - held):
                x('keydown', key)
        held.clear()
        held.update(desired)
        actions.write(json.dumps(dict(seq=state['seq'], scene=state['scene'],
                                     stage=state['stage'], frame=state['frame'],
                                     keys=sorted(desired), input_started_ns=input_started_ns,
                                     issued_ns=time.monotonic_ns())) + '\n')
        actions.flush()

    def press(key):
        keys({key}, wait(lambda _: True))
        time.sleep(.12)
        keys(set(), wait(lambda _: True))
        time.sleep(.04)

    try:
        if args.key_driver == 'xtest':
            keyboard = PrivateKeys()
            libraries = {str(Path(line.split()[-1]).resolve())
                         for line in Path('/proc/self/maps').read_text().splitlines()
                         if '/libX11.so' in line or '/libXtst.so' in line}
            assert libraries
            pins.update({path: sha(path) for path in libraries})
        wait(lambda _: True)
        windows = x('search', '--onlyvisible', '--pid', str(process.pid)).splitlines()
        assert len(windows) == 1
        window = windows[0]
        x('windowfocus', '--sync', window)
        wait(lambda state: state['scene'] == 'menu')
        assert (save / 'GENSOU.SCR').read_bytes() == (out / 'initial-GENSOU.SCR').read_bytes()
        press('Down')  # Actual OP admission chooses Extra, not a forced handoff.
        press('Return')
        wait(lambda state: state['scene'] == 'character')
        press('Return')
        wait(lambda state: state['scene'] == 'shot')
        press('Return')
        state = wait(lambda state: state['scene'] == 'main')
        assert (state['stage'], state['rank'], state['character'], state['shot']) == (6, 4, 0, 0)
        deadline = time.monotonic() + 1800
        while time.monotonic() < deadline:
            state = wait(lambda state: state['seq'] > last, timeout=15)
            last = state['seq']
            assert state['focused'] and state['audio_opens'] == state['audio_failed'] == 0
            scenes.add((state['program'], state['generation'], state['scene']))
            if state['program'] == 0 and state['generation'] > 2:
                keys(set(), state)
                if state['scene'] == 'menu':
                    break
            elif state['scene'] == 'gameover':
                raise RuntimeError('Extra reached Game Over; no-Continue clear rejected')
            elif state['scene'] == 'main':
                assert state['stage'] == 6 and state['rank'] == 4
                keys(key_names(state['advice_held'], state['advice_shift']), state)
            elif state['scene'] in ('dialog', 'maine', 'registration'):
                desired = {'z'} if state['seq'] % 20 >= 10 else set()
                if state['scene'] == 'registration':
                    if desired and not previous_registration_keys:
                        registration_pulses += 1
                    previous_registration_keys = desired
                keys(desired, state)
            else:
                keys(set(), state)
            if time.monotonic() - progress > 30:
                progress = time.monotonic()
                print(json.dumps(dict(elapsed=round(progress-started), seq=last,
                                      scene=state['scene'], frame=state['frame'],
                                      lives=state['lives'], misses=state['misses'],
                                      bombs=state['bombs'])), flush=True)
        else:
            raise RuntimeError('full Extra route watchdog expired')
        assert (2, 3, 'maine') in scenes and (2, 3, 'registration') in scenes
        final = (save / 'GENSOU.SCR').read_bytes()
        (out / 'final-GENSOU.SCR').write_bytes(final)
        sections = decode(final)
        assert sections[4][174] & 1, 'Extra Reimu A clear flag was not persisted'
        assert any(entry['name'] == FULL_NAME and entry['credits'] == 0
                   for entry in entries(sections[4])), 'complete eight-glyph name missing'
        assert all(sections[i][2:] == initial[i][2:] for i in range(10) if i != 4)
        assert sha(save / 'MIKO.CFG') == normal_report['files']['MIKO.CFG']
        subprocess.run(['import', '-window', window, str(out / 'fresh-op.png')], check=True)
        keys(set(), state)
        keys({'Escape'}, state)
        process.wait(timeout=15)
        keys(set(), state)
        assert process.returncode == 0
        writes.close()
        events = writes.records
        writes = None
        lines = trace.read_text().splitlines()
        rows = [row(line) for line in lines if line.startswith('R ')]
        ends = [list(map(int, line.split()[1:])) for line in lines if line.startswith('E ')]
        assert len(ends) == 1 and ends[0][0] == len(rows) and ends[0][4:] == [0, 0]
        assert all(state['audio_opens'] == state['audio_failed'] == 0 for state in rows)
        snapshots = [decode((out / 'physical-events' / event['snapshot']).read_bytes())
                     for event in events if event['name'] == 'GENSOU.SCR']
        assert any(section[4][174] & 1 and
                   any(entry['name'] == FULL_NAME and entry['credits'] == 0
                       for entry in entries(section[4])) for section in snapshots)
        result = dict(passed=True, private_display=private_display, key_driver=args.key_driver, pins=pins,
                      command=command, scenes=sorted(scenes), refreshes=len(rows),
                      registration_pulses=registration_pulses, full_name_gaiji=FULL_NAME,
                      physical_events=events, trace_sha256=sha(trace),
                      files={path.name: sha(path) for path in save.iterdir() if path.is_file()},
                      normal_receipt_sha256=sha(normal / 'receipt.json'), scope=__doc__)
        result['restart'] = restart(exe, hdi, font, save, out / 'restart')
        for path, digest in pins.items():
            assert sha(path) == digest
        (out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
        passed = True
        print('FULL EXTRA WINDOW + EIGHT-GLYPH NAME + PHYSICAL RESTART PASS', flush=True)
    except Exception as exception:
        error = str(exception)
        raise
    finally:
        if keyboard is not None:
            keyboard.close()
        else:
            for key in held:
                subprocess.run(['xdotool', 'keyup', key], check=False)
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if writes is not None:
            writes.close()
            events = writes.records
        log.close()
        actions.close()
        (out / 'physical-events.json').write_text(json.dumps(events, indent=2) + '\n')
        (out / 'terminal.json').write_text(json.dumps(dict(passed=passed, error=error, key_driver=args.key_driver,
                                                         pins=pins, command=command,
                                                         last_refresh=last,
                                                         elapsed=time.monotonic()-started), indent=2) + '\n')


if __name__ == '__main__':
    main()
