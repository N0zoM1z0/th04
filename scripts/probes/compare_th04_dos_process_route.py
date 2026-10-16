#!/usr/bin/env python3
"""Compare real Quit/MAINE/fresh-OP overlays and their bounded MAIN prefix."""
import argparse
import json
from pathlib import Path

from capture_th04_dos_demos import Fat12, map_symbols, sha, u16, u32
from compare_th04_demo_dgroup import POOLS, attest_pools, summarize_pair
from compare_th04_dos_demos import require
from compare_th04_dos_ordinary_prefix import compare, load
from th04_demo_globals import attest_fields
from th04_dos_route import decode_score_sections
from th04_ordinary_dgroup import BOUNDARY, records


def read_side(directory, original, snapshot=None):
    capture = load(directory, original, snapshot)
    require('route' in capture, 'process route contract required')
    count = capture['route']['completed_updates']
    profile = json.loads((directory / 'profile.json').read_text())
    terminal = capture['route_prefix_terminal']
    metadata = json.loads((directory / 'ordinary-dgroup.json').read_text())
    require({'ordinary-dgroup.json', 'ordinary-dgroup.bin.gz'} <= capture['receipt']['files'].keys() and
            metadata['schema_version'] == 1 and metadata['complete'] is True and
            metadata['frames'] == count and metadata['block_bytes'] == 65536 and
            metadata['boundary'] == BOUNDARY and metadata['load_segment'] == terminal['load_segment'] and
            metadata['dgroup_segment'] == terminal['dgroup_segment'], 'route complete DGROUP prefix metadata')
    base = metadata['dgroup_segment'] * 16
    pages = {str(page) for page in range(base & ~4095, ((base + 65535) & ~4095) + 4096, 4096)}
    mappings, previous = metadata['mappings'], 0
    require(mappings and mappings[0]['first_frame'] == 1, 'route initial DGROUP mapping')
    for mapping in mappings:
        require(previous < mapping['first_frame'] <= count and set(mapping['pages']) == pages and
                all(type(value) is int and value % 4096 == 0 and 0 <= value < 16 * 1024 * 1024 and
                    not 0xa0000 <= value < 0x100000 for value in mapping['pages'].values()),
                'route mapped RAM extent/order')
        previous = mapping['first_frame']
    iterator = records(directory / 'ordinary-dgroup.bin.gz', terminal['load_segment'], terminal['dgroup_segment'],
                       profile['fields'], terminal['cr0'], terminal['cr3'], count)
    def verified():
        for frame, data in iterator:
            if frame == count:
                for name, offset, size in profile['fields']:
                    require(data[offset:offset + size].hex() == terminal['values'][name],
                            'route terminal/DGROUP field identity: ' + name)
            yield frame, data
    return capture, profile, verified()


def game_file(image, name):
    fs = Fat12(bytearray(image))
    entry = fs.find_entry([fs.root], b'GENSO      ')
    directory = [fs.cluster_offset(k) for k in fs.chain(u16(fs.image, entry + 26))]
    entry = fs.find_entry(directory, name)
    return fs.file_bytes(u16(fs.image, entry + 26), u32(fs.image, entry + 28))


def file_state(directory):
    initial, final = ((directory / name).read_bytes() for name in ('prepared/diagnostic.hdi', 'execution.hdi'))
    states = {}
    for name in (b'MIKO    CFG', b'GENSOU  SCR'):
        a, b = (game_file(image, name) for image in (initial, final))
        states[name.decode()] = dict(initial_sha256=sha(a), final_sha256=sha(b), changed=a != b,
                                     initial_hex=a.hex(), final_hex=b.hex())
        if name == b'GENSOU  SCR':
            before, after = decode_score_sections(a), decode_score_sections(b)
            states[name.decode()].update(checksum_bits=16, sections=10,
                decoded_sections=[sha(section) for section in after],
                changed_decoded_sections=[i for i in range(10) if before[i] != after[i]])
    return states


def compare_route(original_dir, candidate_dir, original, source_snapshot=None):
    a, ap, ar = read_side(original_dir, original, source_snapshot)
    b, bp, br = read_side(candidate_dir, original, source_snapshot)
    require(a['receipt']['role'] == 'original' and b['receipt']['role'] == 'candidate', 'route pair roles')
    for key in ('end_after', 'dialog_at_frame', 'quit_at_frame', 'main_frames', 'termination',
                'natural_game_exit', 'emulator_sha256', 'emulator_receipt_sha256', 'debugger_sha256',
                'adapter_sha256', 'walker_sha256', 'font_sha256', 'process_host_inputs', 'source_files'):
        require(a['receipt'].get(key) == b['receipt'].get(key), 'route pair identity/contract: ' + key)
    require(a['receipt']['files']['dosbox-x.conf'] == b['receipt']['files']['dosbox-x.conf'] and
            a['starting_files'] == b['starting_files'], 'route paired reset/configuration')
    scalar = compare(a, b)
    require(scalar['passed'], 'route admitted scalar/RNG comparison: ' + str(scalar))
    require(a['terminal_events'] == b['terminal_events'], 'route unfinished update RNG events')
    symbols = map_symbols(Path(b['receipt']['map_path']))
    pools = attest_pools(a['receipt'], b['receipt'], symbols, bp['dgroup'])
    states, witnesses = attest_fields(original, Path(b['receipt']['main_path']).read_bytes(), symbols, bp['dgroup'])
    pools.extend(states)
    for name in ('input', 'shift_raw'):
        left, width = next((offset, size) for field, offset, size in ap['fields'] if field == name)
        right = next(offset for field, offset, _ in bp['fields'] if field == name)
        pools.append(('post_reset_' + name, left, right, 1, width))
    count = a['route']['completed_updates']
    result = summarize_pair(ar, br, 0x5a22, symbols['_bullets'][1], 0xbcbc,
                            symbols['_stage_graze'][1], pools, expected_updates=count)
    residents = {}
    for label, left, right in [('main_handoff', a['route']['handoff'], b['route']['handoff']),
                               *[(name, a['route']['entries'][i], b['route']['entries'][i])
                                 for i, name in ((1, 'maine_entry'), (2, 'op_entry'))],
                               ('fresh_op_menu', a['route']['menu'], b['route']['menu'])]:
        x, y = bytes.fromhex(left['resident_hex']), bytes.fromhex(right['resident_hex'])
        residents[label] = dict(passed=x == y, original_sha256=sha(x), candidate_sha256=sha(y),
                                differing_offsets=[i for i, (u, v) in enumerate(zip(x, y)) if u != v])
    af, bf = file_state(original_dir), file_state(candidate_dir)
    file_results = {name: dict(original=af[name], candidate=bf[name],
                              raw_equal=af[name]['final_hex'] == bf[name]['final_hex']) for name in af}
    file_results['GENSOU  SCR']['decoded_equal'] = af['GENSOU  SCR']['decoded_sections'] == bf['GENSOU  SCR']['decoded_sections']
    result.update(accepts_exact=False, natural_game_exit=False, scalar=scalar,
                  actor_pools_passed=all(result['pools'][name]['passed'] for name, *_ in POOLS),
                  global_states_passed=all(result['pools'][name]['passed'] for name, *_ in states),
                  route_entries_verified=True, resident_checkpoints=residents, files=file_results,
                  completed_updates=count, pre_update_samples=len(a['rows']), incomplete_update=count,
                  witnesses=witnesses, executed_artifacts=['th04-main', 'th04-maine', 'th04-op'],
                  scope='Actual MAIN Quit -> original MAINE -> fresh original OP menu, full entry images and resident use; MAIN-only reconstruction, no resident allocation-owner MCB, complete campaign, native, UI-frame or physical timing acceptance',
                  receipts={str(path): sha((path / 'receipt.json').read_bytes()) for path in (original_dir, candidate_dir)})
    result['passed'] &= all(row['passed'] for row in residents.values()) and all(row['raw_equal'] for row in file_results.values())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--original-main', required=True, type=Path)
    parser.add_argument('--source-snapshot', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = compare_route(args.original, args.candidate, args.original_main.read_bytes(), args.source_snapshot)
    except (ValueError, KeyError, OSError, TypeError, IndexError, EOFError) as error:
        result = dict(passed=False, accepts_exact=False, invalid_capture=str(error))
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key in
                     ('passed', 'invalid_capture', 'completed_updates', 'pre_update_samples',
                      'route_entries_verified', 'actor_pools_passed', 'global_states_passed')}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
