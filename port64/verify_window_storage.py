#!/usr/bin/env python3
"""Muted actual SDL/X11 setup, corrupt-file recovery and physical restart.

Fresh private saves only. No gameplay/unlock/state injection. Starting file
fixtures are declared separately; ordinary OS keys and WM_DELETE_WINDOW drive
the product. Input is restricted to a checked private Xvfb, never the host.
"""
import argparse
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import time

from private_x11 import require_private_xvfb
from private_x11_keys import PrivateKeys
from reduce_window_route import reduce
from verify import require_elf_x86_64
from verify_host_window import latest
from verify_window_continue import Writes, decode

ROOT = Path(__file__).resolve().parents[1]
PENDING = bytes.fromhex('ff030201010100000007')
SELECTED = bytes.fromhex('0103020201010000000a')
TAIL = b'TH04_HOST_STORAGE_TAIL\x00'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ClientData(C.Union):
    _fields_ = [('b', C.c_char * 20), ('s', C.c_short * 10), ('l', C.c_long * 5)]


class ClientMessage(C.Structure):
    _fields_ = [('type', C.c_int), ('serial', C.c_ulong), ('send_event', C.c_int),
                ('display', C.c_void_p), ('window', C.c_ulong),
                ('message_type', C.c_ulong), ('format', C.c_int), ('data', ClientData)]


class Event(C.Union):
    _fields_ = [('client', ClientMessage), ('pad', C.c_long * 24)]


def close_window(keyboard, window):
    """Ordinary X11 window-manager close protocol on the checked private server."""
    assert C.sizeof(C.c_void_p) == 8 and C.sizeof(ClientMessage) == 96
    assert C.sizeof(Event) == 192
    lib = keyboard.xlib
    lib.XInternAtom.argtypes = [C.c_void_p, C.c_char_p, C.c_int]
    lib.XInternAtom.restype = C.c_ulong
    lib.XSendEvent.argtypes = [C.c_void_p, C.c_ulong, C.c_int, C.c_long, C.POINTER(Event)]
    lib.XSendEvent.restype = C.c_int
    event = Event()
    event.client.type = 33  # ClientMessage in the local X11 ABI.
    event.client.send_event = 1
    event.client.display = keyboard.display
    event.client.window = int(window)
    event.client.message_type = lib.XInternAtom(keyboard.display, b'WM_PROTOCOLS', 0)
    event.client.format = 32
    event.client.data.l[0] = lib.XInternAtom(keyboard.display, b'WM_DELETE_WINDOW', 0)
    assert lib.XSendEvent(keyboard.display, int(window), 0, 0, C.byref(event))
    lib.XSync(keyboard.display, 0)


def files(save):
    return {p.name: sha(p) for p in save.iterdir() if p.is_file()}


def score_valid(raw, template):
    sections = decode(raw[:1960])
    assert all(s[174] == 0x19 for s in sections), 'recovered file must remain unplayed'
    assert all(s[2:] == template[i][2:] for i, s in enumerate(sections))


def trial(exe, hdi, font, base, name, cfg, score, needs_setup,
          score_repair, expected_exit, template, interrupt=False):
    out = base / name
    out.mkdir()
    save = out / 'saves'
    save.mkdir()
    for filename, data in [('MIKO.CFG', cfg), ('GENSOU.SCR', score)]:
        if data is not None:
            (save / filename).write_bytes(data)
            (out / ('initial-' + filename)).write_bytes(data)
    trace = out / 'trace/window.tsv'
    writes = Writes(save, out / 'physical-events', trace)
    keyboard = PrivateKeys()
    command = [str(exe), '--hdi', str(hdi), '--font-bmp', str(font),
               '--save-dir', str(save), '--title', '--mute',
               '--window-trace', str(trace.parent)]
    log = (out / 'window.log').open('wb')
    process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
    actions = []
    started = time.monotonic()
    passed = False
    error = None
    window = None
    events = []

    def wait(predicate, timeout=90):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            writes.pump()
            if process.poll() is not None:
                raise RuntimeError('owned storage window exited before observation')
            state = latest(trace)
            if state:
                assert state['audio_opens'] == state['audio_failed'] == 0
                if predicate(state):
                    return state
            time.sleep(.003)
        raise RuntimeError('storage observation timeout')

    def keys(desired, state):
        if set(desired) != keyboard.held:
            keyboard.set(desired)
            actions.append(dict(seq=state['seq'], scene=state['scene'],
                                keys=sorted(desired), issued_ns=time.monotonic_ns()))

    try:
        state = wait(lambda _: True)
        windows = subprocess.check_output(['xdotool', 'search', '--onlyvisible',
                                           '--pid', str(process.pid)], text=True).splitlines()
        assert len(windows) == 1
        window = windows[0]
        subprocess.run(['xdotool', 'windowfocus', '--sync', window], check=True)
        if needs_setup:
            state = wait(lambda s: s['scene'] == 'setup')
            assert (save / 'MIKO.CFG').read_bytes() == PENDING
            assert files(save).get('GENSOU.SCR') == (hashlib.sha256(score).hexdigest() if score is not None else None)
            (out / 'pending-MIKO.CFG').write_bytes((save / 'MIKO.CFG').read_bytes())
            if interrupt:
                close_window(keyboard, window)
                process.wait(timeout=15)
                assert process.returncode == 0
                assert (save / 'MIKO.CFG').read_bytes() == PENDING
                assert not (save / 'GENSOU.SCR').exists()
            else:
                deadline = time.monotonic() + 90
                last = 0
                while time.monotonic() < deadline:
                    state = wait(lambda s: s['seq'] > last)
                    last = state['seq']
                    if state['scene'] != 'setup':
                        keys(set(), state)
                        break
                    keys({'z'} if state['seq'] % 20 >= 10 else set(), state)
                else:
                    raise RuntimeError('ordinary setup confirmation did not finish')
        if not interrupt:
            state = wait(lambda s: s['scene'] == 'menu')
            keys(set(), state)
            assert (save / 'MIKO.CFG').read_bytes() == (PENDING if needs_setup else cfg)
            actual = (save / 'GENSOU.SCR').read_bytes()
            if score_repair:
                assert len(actual) == 1960
                score_valid(actual, template)
            else:
                assert actual == score, 'valid score/tail changed during OP reading'
            (out / 'menu-GENSOU.SCR').write_bytes(actual)
            (out / 'menu-MIKO.CFG').write_bytes((save / 'MIKO.CFG').read_bytes())
            before = files(save)
            keys({'Escape'}, state)
            process.wait(timeout=15)
            assert process.returncode == 0
            keyboard.set(set())
            assert (save / 'MIKO.CFG').read_bytes() == expected_exit
            assert sha(save / 'GENSOU.SCR') == before['GENSOU.SCR']
        writes.close()
        events = writes.records
        writes = None
        schedule = reduce(trace)
        assert all(span['refreshes'] == 0 for span in schedule['stages'])  # No MAIN entry.
        lines = trace.read_text().splitlines()
        assert not any(line.split()[10] in ('main', 'character', 'shot', 'gameover')
                       for line in lines if line.startswith('R '))
        if not interrupt:
            assert lines[-2].startswith(('P ', 'R '))
        expected_score_events = score_repair and not interrupt
        assert bool([e for e in events if e['name'] == 'GENSOU.SCR']) == expected_score_events
        for event in events:
            snapshot = out / 'physical-events' / event['snapshot']
            assert sha(snapshot) == event['sha256'] and event['mask'] & 0x80
            if event['name'] == 'GENSOU.SCR':
                score_valid(snapshot.read_bytes(), template)
        assert not any(p.name.startswith(('.score-pending-', '.config-pending-')) for p in save.iterdir())
        result = dict(passed=True, name=name, command=command, interrupted_setup=interrupt,
                      setup_required=needs_setup, score_repaired=expected_score_events,
                      initial_config_sha256=hashlib.sha256(cfg).hexdigest() if cfg is not None else None,
                      initial_score_sha256=hashlib.sha256(score).hexdigest() if score is not None else None,
                      actions=actions, physical_events=events, files=files(save), schedule=schedule,
                      elapsed=time.monotonic()-started, scope=__doc__)
        (out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
        passed = True
        print(name, schedule['refreshes'], 'PASS', flush=True)
        return result
    except Exception as exception:
        error = str(exception)
        raise
    finally:
        keyboard.close()
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
        (out / 'physical-events.json').write_text(json.dumps(events, indent=2) + '\n')
        (out / 'terminal.json').write_text(json.dumps(dict(passed=passed, error=error,
                                                         returncode=process.returncode), indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('exe', 'hdi', 'font', 'score-template', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--exe-sha256', required=True)
    parser.add_argument('--score-sha256', required=True)
    args = parser.parse_args()
    display = require_private_xvfb()
    exe, hdi, font, source = [p.resolve() for p in
                              (args.exe, args.hdi, args.font, args.score_template)]
    require_elf_x86_64(exe)
    assert sha(exe) == args.exe_sha256 and sha(source) == args.score_sha256
    assert sha(hdi) == '0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'
    assert sha(font) == '41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
    pins = {str(p): sha(p) for p in [exe, hdi, font, source, Path(__file__),
                                    ROOT / 'port64/verify_window_continue.py',
                                    ROOT / 'port64/private_x11.py', ROOT / 'port64/private_x11_keys.py',
                                    ROOT / 'port64/reduce_window_route.py', ROOT / 'port64/verify_host_window.py']}
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    template = decode(source.read_bytes())
    assert len(source.read_bytes()) == 1960 and all(s[174] == 0x19 for s in template)
    records = []
    run = lambda name, cfg, score, setup, repair, exit_cfg, interrupt=False: records.append(
        trial(exe, hdi, font, out, name, cfg, score, setup, repair, exit_cfg, template, interrupt))
    run('missing-close-setup', None, None, True, True, PENDING, True)
    pending = (out / 'missing-close-setup/saves/MIKO.CFG').read_bytes()
    run('pending-restart-complete', pending, None, True, True, SELECTED)
    raw = source.read_bytes()
    run('short-config-empty-score', SELECTED[:7], b'', True, True, SELECTED)
    run('bad-config-short-score', SELECTED[:-1] + b'\xff', raw[:1959], True, True, SELECTED)
    unsafe = bytes([254,3,2,2,1,1,0,0,0,7])
    bad_first = bytearray(raw + TAIL); bad_first[2] ^= 1
    run('unsafe-rank-bad-first', unsafe, bytes(bad_first), True, True, SELECTED)
    unsafe_bool = bytes([1,3,2,2,1,255,0,0,0,8])
    bad_last = bytearray(raw + TAIL); bad_last[9*196+2] ^= 1
    run('unsafe-bool-bad-last', unsafe_bool, bytes(bad_last), True, True, SELECTED)
    live = SELECTED[:6] + bytes.fromhex('a5127e') + SELECTED[9:] + TAIL
    run('valid-records-tail', live, raw + TAIL, False, False, SELECTED + TAIL)
    ranges = bytes([2,0,255,255,255,1,0xa5,0x12,0x7e,0]) + TAIL
    corrected = bytes([2,3,2,0,0,1,0,0,0,8]) + TAIL
    run('valid-corrected-ranges', ranges, raw, False, False, corrected)
    # Separate fresh score/config reader processes after the physical exit saves.
    for original in records[1:3]:
        folder = out / original['name'] / 'saves'
        run(original['name'] + '-restart', (folder / 'MIKO.CFG').read_bytes(),
            (folder / 'GENSOU.SCR').read_bytes(), False, False, SELECTED)
    for path, digest in pins.items():
        assert sha(Path(path)) == digest
    (out / 'receipt.json').write_text(json.dumps(dict(passed=True, private_display=display,
                                                    pins=pins, cases=records, scope=__doc__), indent=2) + '\n')
    print('ACTUAL HOST STORAGE/SETUP/RECOVERY/RESTART PASS', flush=True)


if __name__ == '__main__':
    main()
