#!/usr/bin/env python3
"""Verify full DGROUP streams and compare complete demo actor/effect pools.

The shared boundary follows each actor update, before modulo counters and score
update. A full ordinary scalar/caller trace remains an independent timing
control. Uninterpreted DGROUP bytes are retained for further state owners;
only the explicitly listed pool/state fields are compared here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from capture_th04_dos_demos import map_symbols, sha
from compare_th04_dos_demos import load_capture, require
from inspect_th04_demo_snapshots import bullet
from th04_demo_dgroup import BOUNDARY, DGROUP_SIZE, UPDATE_COUNT, records

SOURCE_NAMES = ('th04_demo_dgroup_stream.gdb', 'th04_demo_dgroup.py', 'th04_demo_host_ram.py')
PAIR_PINS = ('demos', 'original_hdi_sha256', 'starting_files', 'demo_sha256', 'archive_sha256',
             'font_sha256', 'config_sha256', 'emulator_sha256', 'observer_source_sha256')
BASELINE_PINS = ('role', 'main_sha256', 'map_sha256', 'products', 'initial_hdi_sha256',
                 'profile_sha256', 'profile_json_sha256', *PAIR_PINS)
# Target-observed stage_state_init MAIN CIRCLE_TEXT(0AAF):73DB..74A5
# issues these nine clear_dwords calls. Retain every byte, including inactive
# records, padding and the enemy ES-relative script offset; no pointer masking.
POOLS = (
    ('shots', 0xb55e, 68, 18), ('enemies', 0x8a92, 32, 64),
    ('sparks', 0x53e2, 96, 16), ('bullets', 0x5a22, 440, 26),
    ('custom_entities', 0xb204, 32, 26), ('circles', 0x9594, 16, 10),
    ('items', 0xaf34, 32, 20), ('pointnums', 0x9634, 400, 16),
    ('gather_circles', 0x9292, 16, 42),
)


def attest_clear_calls(body, entry, clear, offsets):
    """Check actual PUSH destination/count and near CALL in the linked owner."""
    at = 0x57
    for (name, _, count, stride), offset in zip(POOLS, offsets, strict=True):
        require(body[at:at+3] == b'\x68'+offset.to_bytes(2, 'little'), f'{name} clear destination')
        at += 3
        dwords = count*stride//4
        operand = (b'\x6a'+bytes((dwords,))) if dwords < 128 else b'\x68'+dwords.to_bytes(2, 'little')
        require(body[at:at+len(operand)] == operand, f'{name} clear extent')
        at += len(operand)
        require(body[at:at+1] == b'\xe8' and len(body[at:at+3]) == 3
                and (entry+at+3+int.from_bytes(body[at+1:at+3], 'little', signed=True)) & 65535 == clear,
                f'{name} clear helper')
        at += 3


def attest_pools(original, candidate, symbols, dgroup):
    target = Path(original['main_path']).read_bytes()
    require(len(target) == 156258 and sha(target) == original['main_sha256'], 'pool target identity')
    raw = target[6144+0x11ecb:6144+0x11f96]
    require(sha(raw) == 'f41ff21e0254ae8050f35b00c514db046b74b4ae2b02538dd7856715a15dfed7',
            'pool boundary owner identity')
    attest_clear_calls(raw, 0x73db, 0x185e, [offset for _, offset, _, _ in POOLS])
    data = Path(candidate['main_path']).read_bytes()
    require(sha(data) == candidate['main_sha256'], 'pool candidate identity')
    header = int.from_bytes(data[8:10], 'little')*16
    segment, entry = symbols['_stage_state_init']
    clear_segment, clear = symbols['CLEAR_DWORDS']
    require(segment == clear_segment, 'pool clear helper segment')
    offsets = []
    for name, _, count, stride in POOLS:
        seg, offset = symbols['_'+name]
        require(seg == dgroup and offset+count*stride <= DGROUP_SIZE, f'{name} pool DGROUP extent')
        offsets.append(offset)
    body = data[header+segment*16+entry:header+segment*16+entry+0xcb]
    attest_clear_calls(body, entry, clear, offsets)
    return [(name, original_offset, offset, count, stride)
            for (name, original_offset, count, stride), offset in zip(POOLS, offsets, strict=True)]


def read_side(directory: Path, ordinary: Path, consumer: Path):
    receipt, _, diagnostic = load_capture(directory)
    parent, _, _ = load_capture(ordinary)
    for name in BASELINE_PINS:
        require(receipt[name] == parent[name], f'stream/ordinary identity mismatch: {name}')
    require((directory / 'raw.txt').read_bytes() == (ordinary / 'raw.txt').read_bytes(),
            'DGROUP observer changes complete ordinary scalar/caller trace')
    stream = receipt['dgroup_stream']
    require(stream['complete'], 'incomplete DGROUP producer')
    require(stream['consumer_source_sha256'] == {
        name: sha((consumer / name).read_bytes()) for name in SOURCE_NAMES},
        'DGROUP executed consumer source identity')
    expected = {'dgroup-stream.json'} | {f'dgroup-demo-{n}.bin.gz' for n in range(1, receipt['demos']+1)}
    require(set(stream['files']) == expected, 'DGROUP stream file extent')
    for name, digest in stream['files'].items():
        require(sha((directory / name).read_bytes()) == digest, f'DGROUP file identity: {name}')
    metadata = json.loads((directory / 'dgroup-stream.json').read_text())
    require(metadata['schema_version'] == 1 and metadata['complete']
            and metadata['boundary'] == BOUNDARY
            and metadata['records_per_demo'] == UPDATE_COUNT and metadata['dgroup_bytes'] == DGROUP_SIZE
            and set(metadata['processes']) == {str(n) for n in range(1, receipt['demos']+1)},
            'DGROUP metadata boundary/extent')
    profile = json.loads((directory / 'profile.json').read_text())
    for number, load in enumerate(diagnostic['loads'], 1):
        process = metadata['processes'][str(number)]
        dgroup = load['load_segment']+profile['dgroup']
        require(process['frames'] == UPDATE_COUNT and process['load_segment'] == load['load_segment']
                and process['dgroup_segment'] == dgroup, 'DGROUP process address/extent')
        maps = process['logical_to_physical_maps']
        require(maps and maps[0]['first_frame'] == 1, 'DGROUP mapping initial extent')
        previous = 0
        pages = {str(page) for page in range(dgroup*16 & ~4095,
                                            ((dgroup*16+DGROUP_SIZE-1) & ~4095)+4096, 4096)}
        for mapping in maps:
            require(previous < mapping['first_frame'] <= UPDATE_COUNT
                    and set(mapping['pages']) == pages, 'DGROUP page mapping extent/order')
            require(all(isinstance(page, int) and page % 4096 == 0 and 0 <= page < 16*1024*1024
                        and not 0xa0000 <= page < 0x100000 for page in mapping['pages'].values()),
                    'DGROUP physical mapping outside RAM')
            previous = mapping['first_frame']
    return receipt, profile, diagnostic


def iter_side(directory, number, profile, diagnostic):
    load = diagnostic['loads'][number-1]
    return records(directory / f'dgroup-demo-{number}.bin.gz', number, load['load_segment'],
                   load['load_segment']+profile['dgroup'], profile['fields'],
                   (directory / f'DEMO{number}.REC').read_bytes(), load['cr0'], load['cr3'])


def summarize_pair(original, candidate, original_offset, candidate_offset, graze_a, graze_b, pools=()):
    """Read every frame, even after a difference, and retain its bounded cause."""
    original_hash, candidate_hash = hashlib.sha256(), hashlib.sha256()
    count, differing_frames, first = 0, 0, None
    other = {name: dict(differing_frames=0, first_difference=None,
                       original_hash=hashlib.sha256(), candidate_hash=hashlib.sha256())
             for name, *_ in pools}
    coverage = {name: dict(original=set(), candidate=set(), original_nonzero=0, candidate_nonzero=0)
                for name, _, _, slots, stride in pools if slots*stride <= 32}
    for (frame, a), (other_frame, b) in zip(original, candidate, strict=True):
        require(frame == other_frame, 'paired DGROUP frame boundary mismatch')
        for name, left_offset, right_offset, slots, stride in pools:
            size = slots*stride
            left, right = a[left_offset:left_offset+size], b[right_offset:right_offset+size]
            require(len(left) == len(right) == size, f'{name} complete pool extent')
            row = other[name]
            row['original_hash'].update(left)
            row['candidate_hash'].update(right)
            if name in coverage:
                seen = coverage[name]
                seen['original'].add(bytes(left))
                seen['candidate'].add(bytes(right))
                seen['original_nonzero'] += any(left)
                seen['candidate_nonzero'] += any(right)
            if left != right:
                row['differing_frames'] += 1
                if row['first_difference'] is None:
                    indices = [i for i in range(size) if left[i] != right[i]]
                    row['first_difference'] = dict(frame=frame, after_update=frame-1,
                        differing_bytes=len(indices), changes=[dict(offset=i, slot=i//stride,
                        record_offset=i % stride, original=left[i], candidate=right[i]) for i in indices[:24]])
        x = a[original_offset:original_offset+440*26]
        y = b[candidate_offset:candidate_offset+440*26]
        require(len(x) == len(y) == 440*26, 'bullet pool extent')
        original_hash.update(x)
        candidate_hash.update(y)
        ga, gb = a[graze_a:graze_a+2], b[graze_b:graze_b+2]
        require(len(ga) == len(gb) == 2, 'graze extent')
        if x != y or ga != gb:
            differing_frames += 1
            if first is None:
                differences = []
                slots = 0
                for slot in range(440):
                    left, right = x[slot*26:(slot+1)*26], y[slot*26:(slot+1)*26]
                    if left != right:
                        slots += 1
                        if len(differences) < 12:
                            differences.append(dict(slot=slot, original=bullet(left), candidate=bullet(right),
                                changed_offsets=[i for i in range(26) if left[i] != right[i]]))
                first = dict(frame=frame, after_update=frame-1,
                             original_graze=int.from_bytes(ga, 'little'),
                             candidate_graze=int.from_bytes(gb, 'little'),
                             differing_slots=slots, bullets=differences)
        count += 1
    require(count == UPDATE_COUNT, 'incomplete paired actor extent')
    for name, _, _, slots, stride in pools:
        row = other[name]
        row.update(passed=row['first_difference'] is None, updates=count, bytes_per_frame=slots*stride,
                   original_pool_sha256=row.pop('original_hash').hexdigest(),
                   candidate_pool_sha256=row.pop('candidate_hash').hexdigest())
        if name in coverage:
            seen = coverage[name]
            row['coverage'] = dict(original_distinct_values=len(seen['original']),
                                   candidate_distinct_values=len(seen['candidate']),
                                   original_nonzero_frames=seen['original_nonzero'],
                                   candidate_nonzero_frames=seen['candidate_nonzero'])
    all_pools_passed = all(r['passed'] for r in other.values())
    return dict(passed=first is None and all_pools_passed, bullets_graze_passed=first is None,
                updates=count, differing_frames=differing_frames,
                original_pool_sha256=original_hash.hexdigest(), candidate_pool_sha256=candidate_hash.hexdigest(),
                first_difference=first, pools=other, all_pools_passed=all_pools_passed)


def compare(original: Path, candidate: Path, original_full: Path, candidate_full: Path,
            map_path: Path, original_consumer: Path, candidate_consumer: Path, global_states=False):
    a, ap, ad = read_side(original, original_full, original_consumer)
    b, bp, bd = read_side(candidate, candidate_full, candidate_consumer)
    for name in PAIR_PINS:
        require(a[name] == b[name], f'paired DGROUP reset/observer mismatch: {name}')
    require(a['dgroup_stream']['gdb_sha256'] == b['dgroup_stream']['gdb_sha256'],
            'paired debugger identity')
    require(a['role'] == 'original' and b['role'] == 'ordinary-reconstructed', 'DGROUP comparison roles')
    require(a['main_sha256'] == '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b',
            'original bullet offsets require pinned Japanese MAIN')
    require(sha(map_path.read_bytes()) == b['map_sha256'], 'DGROUP candidate MAP identity')
    symbols = map_symbols(map_path)
    require(symbols['_bullets'][0] == symbols['_stage_graze'][0] == bp['dgroup'],
            'bullet/graze symbols outside DGROUP')
    pool, graze = symbols['_bullets'][1], symbols['_stage_graze'][1]
    pools = attest_pools(a, b, symbols, bp['dgroup'])
    witnesses = []
    if global_states:
        from th04_demo_globals import attest_fields
        states, witnesses = attest_fields(Path(a['main_path']).read_bytes(),
                                         Path(b['main_path']).read_bytes(), symbols, bp['dgroup'])
        pools.extend(states)
    af, bf = ({name: (offset, size) for name, offset, size in profile['fields']}
              for profile in (ap, bp))
    for name in ('input', 'shift_raw'):
        require(af[name][1] == bf[name][1], 'post-reset input field width')
        pools.append(('post_reset_'+name, af[name][0], bf[name][0], 1, af[name][1]))
    result = dict(passed=True, accepts_exact=False, boundary=BOUNDARY,
        scope='nine complete raw actor/effect pools and stage graze after every bundled-demo actor update',
        pool_extents=[dict(name=name, original_dgroup_offset=left, candidate_dgroup_offset=right,
                           count=count, stride=stride) for name, left, right, count, stride in pools],
        original_receipt_sha256=sha((original / 'receipt.json').read_bytes()),
        candidate_receipt_sha256=sha((candidate / 'receipt.json').read_bytes()),
        ordinary_controls_passed=True, demos={})
    if global_states:
        result['scope'] += '; 22 pointer-free boss/midboss/player state blocks'
        result['global_instruction_witnesses'] = witnesses
        result['excluded_global_state'] = ['callback/code pointers', 'other global owners']
    for number in range(1, a['demos']+1):
        demo = summarize_pair(iter_side(original, number, ap, ad), iter_side(candidate, number, bp, bd),
                              0x5a22, pool, 0xbcbc, graze, pools)
        result['demos'][str(number)] = demo
        result['passed'] &= demo['passed'] and demo['all_pools_passed']
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('original', 'candidate', 'original-full', 'candidate-full', 'map', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--original-consumer', type=Path, default=Path(__file__).parent)
    parser.add_argument('--candidate-consumer', type=Path, default=Path(__file__).parent)
    parser.add_argument('--global-states', action='store_true', help='also attest and compare 22 scalar/structure owners')
    args = parser.parse_args()
    try:
        result = compare(args.original, args.candidate, args.original_full, args.candidate_full,
                         args.map, args.original_consumer, args.candidate_consumer, args.global_states)
    except (ValueError, KeyError, OSError, TypeError, IndexError, EOFError) as error:
        result = dict(passed=False, invalid_capture=str(error), accepts_exact=False)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
