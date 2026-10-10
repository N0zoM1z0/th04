#!/usr/bin/env python3
"""Read-only complete natural Lunatic outcome, save/restart and slowdown checks.

No game launch or file mutation. Turbo0 acceptance requires natural >=320 and
>=400 slowdown2 samples. Turbo1 is a route-only control, never slowdown2 or
uninstrumented/physical performance acceptance. Shared host/observer costs remain.
"""
import argparse
import hashlib
import json
from pathlib import Path

from reduce_window_route import reduce
from verify_host_window import row
from verify_window_continue import decode, entries, has_clear


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def demand(condition, reason):
    if not condition:
        raise ValueError(reason)


def trace_rows(path):
    return [row(line) for line in path.read_text().splitlines() if line.startswith('R ')]


def verify(route, turbo, exe_sha256):
    demand(turbo in (0, 1), 'invalid requested Turbo')
    demand((route / 'receipt.json').is_file() and (route / 'terminal.json').is_file(),
           'complete route receipt and terminal required')
    report = json.loads((route / 'receipt.json').read_text())
    terminal = json.loads((route / 'terminal.json').read_text())
    demand(report['passed'] and terminal['passed'] and terminal['error'] is None,
           'successful terminal route required')
    demand(report['rank'] == 3 and terminal['rank'] == 3, 'Lunatic rank required')
    character, shot = report['character'], report['shot']
    demand(character in (0, 1) and shot in (0, 1), 'invalid character or shot')
    section = 3 + 5 * character
    demand(report['selected_section'] == section, 'wrong selected score section')
    command = report['command']
    demand('--mute' in command and '--window-route-advice' in command,
           'muted ordinary adaptive route required')
    exe = Path(command[0])
    demand(sha(exe) == exe_sha256 == report['pins'][str(exe)], 'program identity differs')
    for flag, expected in (
        ('--hdi', '0d5ea773a9e4f3e28f473b6deeedb6a7cdaccbb5b940a97983c4e3597dd4ebfd'),
        ('--font-bmp', '41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'),
    ):
        path = Path(command[command.index(flag) + 1])
        demand(sha(path) == expected == report['pins'][str(path)], 'original input identity differs')
    config = (route / 'initial-MIKO.CFG').read_bytes()
    demand(config == bytes([3, 6, 2, 2, 1, turbo, 0, 0, 0, 14 + turbo]),
           'physical Lunatic/Turbo configuration differs')
    demand((route / 'saves/MIKO.CFG').read_bytes() == config, 'configuration changed')
    demand(report.get('turbo', turbo) == terminal.get('turbo', turbo) == turbo,
           'declared Turbo differs from physical file')
    timing = reduce(route / 'trace/window.tsv')
    restart_timing = reduce(route / 'restart/trace/window.tsv')
    demand(timing['trace_sha256'] == report['trace_sha256'], 'route trace hash differs')
    demand(restart_timing['trace_sha256'] == report['restart']['trace_sha256'],
           'restart trace hash differs')
    rows = trace_rows(route / 'trace/window.tsv')
    main = [state for state in rows if state['scene'] == 'main']
    demand({state['stage'] for state in main} == set(range(6)), 'six stages required')
    demand(all((s['rank'], s['character'], s['shot'], s['program'], s['generation'], s['credits'])
               == (3, character, shot, 1, 2, 0) for s in main), 'MAIN identity/credit differs')
    demand(timing['gameover_refreshes'] == 0, 'Game Over rejects no-Continue route')
    scenes = {(s['program'], s['generation'], s['scene']) for s in rows}
    demand({(2, 3, 'maine'), (2, 3, 'registration'), (0, 4, 'menu')} <= scenes,
           'Ending/registration/fresh OP incomplete')
    demand(any(s['scene'] == 'registration' and s['held'] & 0x2000 for s in rows),
           'registration Escape absent from observed OS input')
    restarted = trace_rows(route / 'restart/trace/window.tsv')
    demand(any(s['scene'] == 'ranking' and s['program'] == 0 and s['generation'] == 1
               for s in restarted), 'independent fresh Scores reader absent')
    before = decode((route / 'op-initial-GENSOU.SCR').read_bytes())
    final = decode((route / 'final-GENSOU.SCR').read_bytes())
    demand((route / 'saves/GENSOU.SCR').read_bytes() == (route / 'final-GENSOU.SCR').read_bytes(),
           'final physical score differs')
    demand(has_clear(final[section], shot), 'true clear absent or unplayed sentinel')
    demand(all(before[i][2:] == final[i][2:] for i in range(10) if i != section),
           'unselected score payload/checksum changed')
    events = json.loads((route / 'physical-events.json').read_text())
    demand(events == report['physical_events'], 'physical events differ')
    clear_renames = []
    for event in events:
        path = route / 'physical-events' / event['snapshot']
        demand(event['mask'] == 0x80 and sha(path) == event['sha256'], 'rename snapshot differs')
        if event['name'] == 'GENSOU.SCR':
            observed = decode(path.read_bytes())
            demand(all(before[i][2:] == observed[i][2:] for i in range(10) if i != section),
                   'unselected rename payload/checksum changed')
            if has_clear(observed[section], shot):
                clear_renames.append(event)
        elif event['name'] == 'MIKO.CFG':
            demand(path.read_bytes() == config, 'renamed configuration differs')
        else:
            raise ValueError('unexpected physical file event')
    demand(clear_renames and clear_renames[-1]['sha256'] == sha(route / 'final-GENSOU.SCR'),
           'true clear absent at final physical rename')
    actual_files = {p.name: sha(p) for p in (route / 'saves').iterdir() if p.is_file()}
    demand(actual_files == report['files'] == report['restart']['files_before']
           == report['restart']['files_after'], 'save/restart identities differ')
    demand(set(actual_files) == {'MIKO.CFG', 'GENSOU.SCR'}
           and {p.name for p in (route / 'saves').iterdir()} == set(actual_files),
           'temporary or unexpected save artifact')
    density = timing['lunatic_density']
    if turbo == 0:
        for threshold in (320, 400):
            demand(density[threshold]['refreshes'] > 0
                   and density[threshold]['slowdown2_refreshes'] > 0,
                   f'natural dense slowdown2 absent at {threshold}')
    return dict(passed=True, dense_slowdown_accepted=turbo == 0, turbo=turbo,
                rank=3, character=character, shot=shot, selected_section=section,
                clear_mask=final[section][174], leaders=entries(final[section]),
                last_main=main[-1], clear_renames=clear_renames,
                route_schedule=timing, restart_schedule=restart_timing,
                producer_receipt_sha256=sha(route / 'receipt.json'),
                reader_sha256=sha(Path(__file__)), scope=__doc__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('route', type=Path)
    parser.add_argument('--expected-turbo', type=int, choices=(0, 1), default=0)
    parser.add_argument('--exe-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    demand(not args.output.exists(), 'fresh verdict output required')
    result = verify(args.route.resolve(), args.expected_turbo, args.exe_sha256)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('Natural route PASS; dense slowdown accepted:', result['dense_slowdown_accepted'])


if __name__ == '__main__':
    main()
