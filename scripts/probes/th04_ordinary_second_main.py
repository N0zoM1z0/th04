"""Admit actual generation-2 initialization and bounded after-update records."""
import json
from pathlib import Path

from capture_th04_dos_demos import sha
from compare_th04_dos_demos import require
from compare_th04_dos_ordinary_prefix import ordinary_profile, validate_bounded_terminal, compare
from compare_th04_demo_dgroup import summarize_pair, POOLS
from th04_ordinary_generation import split_generations, parse_trace
from th04_ordinary_dgroup import records, BOUNDARY


def load_second(directory, capture, original):
    receipt = capture['receipt']
    limit = receipt['restart_updates']
    require(type(limit) is int and 1 <= limit <= 3995, 'second MAIN frame extent')
    needed = {'raw-observer-all.txt', 'second-main/profile.json', 'second-main/raw.txt',
              'second-main/ordinary-terminal.json', 'second-main/ordinary-dgroup.json',
              'second-main/ordinary-dgroup.bin.gz', 'second-main-prefix.json'}
    require(needed <= receipt['files'].keys(), 'second MAIN pinned file set')
    full = (directory/'raw-observer-all.txt').read_bytes()
    first, second = split_generations(full)
    require(first == (directory/'raw.txt').read_bytes() and second == (directory/'second-main/raw.txt').read_bytes(),
            'second MAIN complete unmodified trace partition')
    main = Path(receipt['main_path']).read_bytes()
    map_path = Path(receipt['map_path']) if receipt['role'] == 'candidate' else None
    profile = ordinary_profile(main, original, map_path, limit)
    actual = json.loads((directory/'second-main/profile.json').read_text())
    if map_path is None:
        actual.pop('witnesses', None)
    require(actual == json.loads(json.dumps(profile)), 'second MAIN independently attested profile')
    parsed = parse_trace(second.decode(), main, profile, generation=2)
    require(not parsed['terminal'] and len(parsed['rows']) == limit and
            parsed['load_segment'] == capture['route']['entries'][-1]['load_segment'],
            'second MAIN real sample/generation extent')
    terminal = json.loads((directory/'second-main/ordinary-terminal.json').read_text())
    validate_bounded_terminal(terminal, main, profile, parsed['load_segment'], parsed['counts'])
    require(terminal['generation'] == 2, 'second MAIN terminal generation')
    end = json.loads((directory/'second-main-prefix.json').read_text())
    require(end['cpu_regs'] == terminal['cpu_regs'] and end['segments'] == terminal['segments'] and
            end['resident_hex'][:160] == terminal['resident'], 'second MAIN actual process/frame boundary')
    clock = capture['clock']
    followup = clock['second_main']
    start, stop = followup['action_start'], followup['action_end']
    actions = clock['actions'][start:stop]
    boundary = receipt.get('restart_shot_boundary', False)
    first_update = None
    if boundary:
        require('second-main/first-update.json' in receipt['files'], 'second MAIN pinned Shot boundary')
        first_update = json.loads((directory/'second-main/first-update.json').read_text())
        validate_bounded_terminal(first_update, main, dict(profile,end_after=1), parsed['load_segment'],
                                  dict(lcg=first_update['lcg_calls'],ring=first_update['ring_calls']))
        require(first_update['generation'] == 2 and followup['shot_boundary_frame'] == 1 and
                all(parsed['sample_counts'][0].get(name,0) <= first_update[key] <=
                    parsed['sample_counts'][1].get(name,0) for name,key in [('lcg','lcg_calls'),('ring','ring_calls')]),
                'second MAIN first-actor RNG/boundary extent')
    require(start == clock['restart']['action_end'] and stop == len(clock['actions']) and
            len(actions) in (1,2) and actions[-1]['key'] == 'KBD_z' and actions[-1]['pressed'] is True and
            actions[-1]['due'] == (followup['shot_boundary_tick'] if boundary else followup['tick'] + 200) and
            all(action['tick'] <= followup['prefix_tick'] and action['frame'] in ((None,0,1) if boundary else (None,0)) for action in actions),
            'second MAIN actual held Shot input')
    if boundary:
        validate_shot_boundary(actions[-1], followup, first_update)
    if clock['restart']['enter_down']:
        require(len(actions) == 2 and actions[0]['key'] == 'KBD_enter' and actions[0]['pressed'] is False and
                actions[0]['due'] == followup['tick'], 'second MAIN real Enter release')
    else:
        require(len(actions) == 1, 'second MAIN unexpected keys')
    metadata = json.loads((directory/'second-main/ordinary-dgroup.json').read_text())
    require(metadata['schema_version'] == 1 and metadata['complete'] is True and metadata['generation'] == 2 and
            metadata['frames'] == limit and metadata['block_bytes'] == 65536 and metadata['boundary'] == BOUNDARY and
            metadata['load_segment'] == parsed['load_segment'] and metadata['dgroup_segment'] == terminal['dgroup_segment'],
            'second MAIN complete DGROUP metadata')
    base = metadata['dgroup_segment'] * 16
    pages = {str(page) for page in range(base & ~4095, ((base + 65535) & ~4095) + 4096, 4096)}
    previous = 0
    require(metadata['mappings'] and metadata['mappings'][0]['first_frame'] == 1, 'second MAIN initial mapping')
    for mapping in metadata['mappings']:
        require(previous < mapping['first_frame'] <= limit and set(mapping['pages']) == pages and
                all(type(value) is int and value % 4096 == 0 and 0 <= value < 16 * 1024 * 1024 and
                    not 0xa0000 <= value < 0x100000 for value in mapping['pages'].values()), 'second MAIN RAM mapping')
        previous = mapping['first_frame']
    iterator = records(directory/'second-main/ordinary-dgroup.bin.gz', terminal['load_segment'],
                       terminal['dgroup_segment'], profile['fields'], terminal['cr0'], terminal['cr3'], limit, generation=2)
    def verified():
        for frame, data in iterator:
            if frame == 1 and first_update is not None:
                require(all(data[offset:offset+size].hex() == first_update['values'][name]
                            for name,offset,size in profile['fields']), 'second MAIN first-actor DGROUP agreement')
            if frame == limit:
                require(all(data[offset:offset+size].hex() == terminal['values'][name]
                            for name, offset, size in profile['fields']), 'second MAIN terminal/DGROUP field agreement')
            yield frame, data
    view = dict(fields=[name for name,_,_ in profile['fields']], rows=parsed['rows'], resident=parsed['resident'],
                events=parsed['events'], terminal_events=parsed['pending'], bounded_terminal=terminal)
    return view, verified()


def validate_shot_boundary(action, followup, first_update):
    require(action['frame'] == 1 and action['tick'] == action['due'] == followup['shot_boundary_tick'] and
            action['unchanged_guest']['cpu_regs'] == first_update['cpu_regs'] and
            action['unchanged_guest']['segments'] == first_update['segments'],
            'second MAIN Shot at actual actor boundary')


def compare_second(left_dir, right_dir, left, right, original, pools, symbols, states):
    a, ar = load_second(left_dir, left, original)
    b, br = load_second(right_dir, right, original)
    scalar = compare(a,b)
    terminal_differences = [name for name in a['fields'] if name != 'resident_pointer' and
                            a['bounded_terminal']['values'][name] != b['bounded_terminal']['values'][name]]
    result = summarize_pair(ar, br, 0x5a22, symbols['_bullets'][1], 0xbcbc, symbols['_stage_graze'][1],
                            pools, expected_updates=left['receipt']['restart_updates'])
    result.update(scalar=scalar, terminal_differences=terminal_differences,
                  actor_pools_passed=all(result['pools'][name]['passed'] for name,*_ in POOLS),
                  global_states_passed=all(result['pools'][name]['passed'] for name,*_ in states),
                  initial={role:dict(values=c['rows'][0],resident=c['resident'][0]) for role,c in [('original',a),('candidate',b)]},
                  terminal_resident_equal=a['bounded_terminal']['resident'] == b['bounded_terminal']['resident'],
                  generation=2, accepts_exact=False, natural_game_exit=False,
                  scope='Actual second MAIN initialization, consumed inputs, RNG, complete configured actor/state pools and terminal; no pixels, physical timing or campaign acceptance')
    result['passed'] &= scalar['passed'] and not terminal_differences and result['terminal_resident_equal']
    return result
