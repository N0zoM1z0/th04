#!/usr/bin/env python3
"""Compare full ordinary actor pools with independent scalar timing controls."""
import argparse
import json
from pathlib import Path

from capture_th04_dos_demos import map_symbols, sha
from compare_th04_demo_dgroup import attest_pools, summarize_pair
from compare_th04_dos_demos import require
from compare_th04_dos_ordinary_prefix import compare, load
from th04_demo_dgroup import DGROUP_SIZE, UPDATE_COUNT
from th04_demo_globals import attest_fields
from th04_ordinary_dgroup import BOUNDARY, records


def scalar_control(capture, baseline, original, snapshot):
    control = load(baseline, original, snapshot)
    for key in ('role', 'main_sha256', 'map_sha256', 'initial_hdi_sha256',
                'emulator_sha256', 'debugger_sha256', 'font_sha256'):
        require(capture['receipt'][key] == control['receipt'][key], 'scalar baseline identity: ' + key)
    for key in ('end_after', 'dialog_at_frame', 'continue_at_frame', 'termination', 'natural_game_exit'):
        require(capture['receipt'].get(key) == control['receipt'].get(key),
                'scalar baseline contract: ' + key)
    require(capture['receipt']['files']['dosbox-x.conf'] == control['receipt']['files']['dosbox-x.conf'],
            'scalar baseline emulator configuration')
    require(capture['starting_files'] == control['starting_files'], 'scalar baseline files')
    timing = compare(control, capture)
    require(timing['passed'], 'DGROUP monitor changes scalar/RNG control: ' + str(timing))
    return timing


def read_side(directory, baseline, original, snapshot):
    capture = load(directory, original)
    timing = scalar_control(capture, baseline, original, snapshot)
    receipt = capture['receipt']
    require({'ordinary-dgroup.json', 'ordinary-dgroup.bin.gz'} <= receipt['files'].keys(),
            'missing pinned ordinary DGROUP stream')
    metadata = json.loads((directory / 'ordinary-dgroup.json').read_text())
    require(metadata['schema_version'] == 1 and metadata['complete'] and
            metadata['boundary'] == BOUNDARY and metadata['frames'] == UPDATE_COUNT and
            metadata['block_bytes'] == DGROUP_SIZE, 'ordinary DGROUP extent/boundary')
    profile = json.loads((directory / 'profile.json').read_text())
    row = next(line.split() for line in (directory / 'raw.txt').read_text().splitlines()
               if line.startswith('L '))
    module, cr0, cr3 = (int(x, 16) for x in row[2:5])
    dgroup = module + profile['dgroup']
    require(metadata['load_segment'] == module and metadata['dgroup_segment'] == dgroup,
            'ordinary DGROUP mapping identity')
    expected_pages = {str(page) for page in range(dgroup * 16 & ~4095,
                      ((dgroup * 16 + DGROUP_SIZE - 1) & ~4095) + 4096, 4096)}
    previous = 0
    require(metadata['mappings'] and metadata['mappings'][0]['first_frame'] == 1,
            'ordinary initial mapping')
    for mapping in metadata['mappings']:
        require(previous < mapping['first_frame'] <= UPDATE_COUNT and
                set(mapping['pages']) == expected_pages, 'ordinary mapping order/extent')
        require(all(isinstance(value, int) and value % 4096 == 0 and
                    0 <= value < 16 * 1024 * 1024 and not 0xa0000 <= value < 0x100000
                    for value in mapping['pages'].values()), 'ordinary physical RAM mapping')
        previous = mapping['first_frame']
    iterator = records(directory / 'ordinary-dgroup.bin.gz', module, dgroup,
                       profile['fields'], cr0, cr3)
    return capture, profile, iterator, timing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--original-baseline', required=True, type=Path)
    parser.add_argument('--candidate-baseline', required=True, type=Path)
    parser.add_argument('--baseline-sources', required=True, type=Path)
    parser.add_argument('--original-main', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    original = args.original_main.read_bytes()
    a, ap, ar, at = read_side(args.original, args.original_baseline, original, args.baseline_sources)
    b, bp, br, bt = read_side(args.candidate, args.candidate_baseline, original, args.baseline_sources)
    require(a['receipt']['role'] == 'original' and b['receipt']['role'] == 'candidate', 'ordinary pool roles')
    require(compare(a, b)['passed'], 'ordinary paired scalar/RNG mismatch')
    for key in ('emulator_sha256', 'debugger_sha256', 'adapter_sha256', 'walker_sha256', 'font_sha256'):
        require(a['receipt'][key] == b['receipt'][key], 'ordinary pool producer identity: ' + key)
    require(a['receipt']['files']['dosbox-x.conf'] == b['receipt']['files']['dosbox-x.conf'],
            'paired ordinary config')
    require(a['starting_files'] == b['starting_files'], 'paired ordinary starting files')
    symbols = map_symbols(Path(b['receipt']['map_path']))
    pools = attest_pools(a['receipt'], b['receipt'], symbols, bp['dgroup'])
    states, witnesses = attest_fields(original, Path(b['receipt']['main_path']).read_bytes(),
                                     symbols, bp['dgroup'])
    pools.extend(states)
    for name in ('input', 'shift_raw'):
        left = next(offset for field, offset, _ in ap['fields'] if field == name)
        right, width = next((offset, size) for field, offset, size in bp['fields'] if field == name)
        pools.append(('post_reset_' + name, left, right, 1, width))
    require(symbols['_stage_graze'][0] == symbols['_bullets'][0] == bp['dgroup'], 'ordinary graze ownership')
    result = summarize_pair(ar, br, 0x5a22, symbols['_bullets'][1], 0xbcbc,
                            symbols['_stage_graze'][1], pools)
    result['actor_pools_passed'] = all(result['pools'][name]['passed'] for name in
                                     ('shots', 'enemies', 'sparks', 'bullets', 'custom_entities',
                                      'circles', 'items', 'pointnums', 'gather_circles'))
    result['global_states_passed'] = all(result['pools'][name]['passed'] for name, *_ in states)
    result['post_reset_input_passed'] = all(result['pools'][name]['passed'] for name in
                                          ('post_reset_input', 'post_reset_shift_raw'))
    result.update(accepts_exact=False, boundary=BOUNDARY, scalar_controls=[at, bt],
                  scope='Nine complete ordinary pools, 22 state blocks and post-reset input; no pictures/Boss combat/full campaign acceptance',
                  extents=[dict(name=n, original=l, candidate=r, count=c, stride=s) for n, l, r, c, s in pools],
                  witnesses=witnesses,
                  receipt_sha256={str(d): sha((d / 'receipt.json').read_bytes()) for d in
                                  (args.original, args.candidate, args.original_baseline, args.candidate_baseline)})
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'], updates=result['updates'],
                         first_difference=result['first_difference'],
                         pools={name: row['passed'] for name, row in result['pools'].items()})))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
