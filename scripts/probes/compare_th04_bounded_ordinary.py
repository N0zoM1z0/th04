#!/usr/bin/env python3
"""Compare observed ordinary prefixes ending at an actual after-update store."""
import argparse
import json
from pathlib import Path

from capture_th04_dos_demos import map_symbols, sha
from compare_th04_dos_demos import require
from compare_th04_dos_ordinary_prefix import load, compare
from compare_th04_demo_dgroup import POOLS, attest_pools, summarize_pair
from th04_demo_globals import attest_fields
from th04_ordinary_dgroup import records, BOUNDARY


def read_side(directory, original, source_snapshot=None):
    capture = load(directory, original, source_snapshot)
    receipt = capture['receipt']
    count = receipt['end_after']
    require(capture['bounded_terminal'] and receipt['natural_game_exit'] is False,
            'bounded prefix contract')
    profile = json.loads((directory / 'profile.json').read_text())
    metadata = json.loads((directory / 'ordinary-dgroup.json').read_text())
    terminal = capture['bounded_terminal']
    require(metadata['complete'] and metadata['boundary'] == BOUNDARY and
            metadata['frames'] == count and metadata['block_bytes'] == 65536 and
            metadata['load_segment'] == terminal['load_segment'] and
            metadata['dgroup_segment'] == terminal['dgroup_segment'], 'bounded DGROUP extent')
    base = metadata['dgroup_segment'] * 16
    pages = {str(page) for page in range(base & ~4095, ((base + 65535) & ~4095) + 4096, 4096)}
    mappings = metadata['mappings']
    require(mappings and mappings[0]['first_frame'] == 1, 'bounded initial page mapping')
    previous = 0
    for mapping in mappings:
        require(previous < mapping['first_frame'] <= count and set(mapping['pages']) == pages,
                'bounded page mapping extent/order')
        require(all(isinstance(value, int) and value % 4096 == 0 and
                    0 <= value < 16 * 1024 * 1024 and not 0xa0000 <= value < 0x100000
                    for value in mapping['pages'].values()), 'bounded physical RAM mapping')
        previous = mapping['first_frame']
    iterator = records(directory / 'ordinary-dgroup.bin.gz', terminal['load_segment'],
                       terminal['dgroup_segment'], profile['fields'], terminal['cr0'], terminal['cr3'], count)
    def verified():
        for frame, data in iterator:
            if frame == count:
                for name, offset, size in profile['fields']:
                    require(data[offset:offset + size].hex() == terminal['values'][name],
                            'terminal/DGROUP field identity: ' + name)
            yield frame, data
    return capture, profile, verified()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--original-main', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--source-snapshot', type=Path,
                        help='Frozen source fallback for immutable older capture identities')
    args = parser.parse_args()
    original = args.original_main.read_bytes()
    a, ap, ar = read_side(args.original, original, args.source_snapshot)
    b, bp, br = read_side(args.candidate, original, args.source_snapshot)
    require(a['receipt']['role'] == 'original' and b['receipt']['role'] == 'candidate', 'prefix roles')
    count = a['receipt']['end_after']
    require(count == b['receipt']['end_after'] and a['starting_files'] == b['starting_files'],
            'prefix reset/extent')
    for key in ('emulator_sha256', 'debugger_sha256', 'adapter_sha256', 'walker_sha256',
                'font_sha256', 'dialog_at_frame', 'continue_at_frame', 'post_boss_dialog_at_frame'):
        require(a['receipt'].get(key) == b['receipt'].get(key), 'prefix producer: ' + key)
    require(a['receipt']['files']['dosbox-x.conf'] == b['receipt']['files']['dosbox-x.conf'],
            'prefix emulator config')
    scalar = compare(a, b)
    symbols = map_symbols(Path(b['receipt']['map_path']))
    pools = attest_pools(a['receipt'], b['receipt'], symbols, bp['dgroup'])
    states, witnesses = attest_fields(original, Path(b['receipt']['main_path']).read_bytes(),
                                     symbols, bp['dgroup'])
    pools.extend(states)
    for name in ('input', 'shift_raw'):
        left, width = next((offset, size) for field, offset, size in ap['fields'] if field == name)
        right = next(offset for field, offset, _ in bp['fields'] if field == name)
        pools.append(('post_reset_' + name, left, right, 1, width))
    result = summarize_pair(ar, br, 0x5a22, symbols['_bullets'][1], 0xbcbc,
                            symbols['_stage_graze'][1], pools, expected_updates=count)
    result.update(scalar=scalar, scalar_passed=scalar['passed'],
                  actor_pools_passed=all(result['pools'][name]['passed'] for name, *_ in POOLS),
                  global_states_passed=all(result['pools'][name]['passed'] for name, *_ in states),
                  accepts_exact=False, natural_game_exit=False, boundary=BOUNDARY,
                  witnesses=witnesses, scope='Actual bounded ordinary actor/RNG/state extent; no natural game exit or complete campaign claim',
                  receipts={str(path): sha((path / 'receipt.json').read_bytes())
                            for path in (args.original, args.candidate)})
    result['passed'] &= scalar['passed']
    if a.get('continue_transition') or b.get('continue_transition'):
        require(a.get('continue_transition') == b.get('continue_transition'), 'paired Continue transition')
        result['continue_transition'] = a['continue_transition']
        result['continue_witnesses'] = [a['continue_witness'], b['continue_witness']]
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'], scalar_passed=scalar['passed'],
                         actor_pools_passed=result['actor_pools_passed'],
                         global_states_passed=result['global_states_passed'], updates=count,
                         scalar_difference=scalar['first_difference'],
                         changed={name: row['differing_frames'] for name, row in result['pools'].items()
                                  if not row['passed']})))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
