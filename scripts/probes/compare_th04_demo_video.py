#!/usr/bin/env python3
"""Compare complete raw DOS demo VRAM/palettes and programmed presentation state."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from capture_th04_dos_demos import sha
from compare_th04_dos_demos import require, load_capture
from compare_th04_demo_dgroup import BASELINE_PINS, PAIR_PINS
from th04_demo_video import records, regions, UPDATE_COUNT, BLOCK_SIZE, BOUNDARY, LAYOUT, SYMBOL_SIZES, OFFSETS, SIZES

SOURCE_NAMES = ('th04_demo_dgroup_stream.gdb', 'th04_demo_dgroup.py',
                'th04_demo_host_ram.py', 'th04_demo_video.py')


def read_side(directory, ordinary, consumer):
    receipt, _, diagnostic = load_capture(directory)
    parent, _, _ = load_capture(ordinary)
    for name in BASELINE_PINS:
        require(receipt[name] == parent[name], 'video/ordinary identity mismatch: '+name)
    require((directory/'raw.txt').read_bytes() == (ordinary/'raw.txt').read_bytes(),
            'video observer changes complete ordinary scalar/caller trace')
    stream = receipt['video_stream']
    require(stream['complete'], 'incomplete video producer')
    require(stream['consumer_source_sha256'] == {
        name: sha((consumer/name).read_bytes()) for name in SOURCE_NAMES}, 'executed video consumer identity')
    expected = {'video-stream.json'} | {f'video-demo-{n}.bin.gz' for n in range(1, receipt['demos']+1)}
    require(set(stream['files']) == expected, 'video file extent')
    for name, digest in stream['files'].items():
        require(sha((directory/name).read_bytes()) == digest, 'video file identity: '+name)
    layout_path = Path(stream['layout_receipt_path'])
    require(sha(layout_path.read_bytes()) == stream['layout_receipt_sha256'], 'video ABI receipt identity')
    layout = json.loads(layout_path.read_text())
    require(layout['passed'] and layout['layout'] == LAYOUT
            and layout['emulator_sha256'] == receipt['emulator_sha256']
            and layout['emulator_receipt_sha256'] == receipt['emulator_receipt_sha256']
            and {name: value['size'] for name, value in layout['symbols'].items()} == SYMBOL_SIZES,
            'video ABI/binary/ELF extent')
    metadata = json.loads((directory/'video-stream.json').read_text())
    require(metadata['schema_version'] == 1 and metadata['complete']
            and metadata['boundary'] == BOUNDARY and metadata['records_per_demo'] == UPDATE_COUNT
            and metadata['block_bytes'] == BLOCK_SIZE and metadata['layout'] == LAYOUT
            and set(metadata['processes']) == {str(n) for n in range(1, receipt['demos']+1)}
            and set(metadata['video_symbols']) == set(SYMBOL_SIZES), 'video metadata boundary/extent')
    require(len({metadata['video_symbols'][name]-row['address']
                 for name, row in layout['symbols'].items()}) == 1, 'video ELF runtime mapping')
    profile = json.loads((directory/'profile.json').read_text())
    for number, row in metadata['processes'].items():
        load = diagnostic['loads'][int(number)-1]['load_segment']
        require(row['frames'] == UPDATE_COUNT and row['load_segment'] == load
                and row['dgroup_segment'] == load+profile['dgroup'], 'video process extent')
        for key in ('logical_to_physical_maps', 'video_pointer_maps'):
            maps = row[key]
            require(maps and maps[0]['first_frame'] == 1, 'video initial mapping')
            previous = 0
            for mapping in maps:
                require(previous < mapping['first_frame'] <= UPDATE_COUNT, 'video mapping frame order')
                if key == 'video_pointer_maps':
                    base = mapping['backing_ram']
                    require(base > 0 and mapping['backing_bytes'] >= 0x44000
                            and mapping['cpu_page'] in (base+0x4000, base+0xc000)
                            and mapping['display_page'] in (base+0x4000, base+0xc000), 'video backing/page mapping')
                else:
                    require(mapping['pages'] and all(0 <= page < 16*1024*1024
                            and page % 4096 == 0 and not 0xa0000 <= page < 0x100000
                            for page in mapping['pages'].values()), 'video frame mapping outside conventional RAM')
                previous = mapping['first_frame']
    return receipt, profile, diagnostic


def iter_side(directory, number, profile, diagnostic):
    load = diagnostic['loads'][number-1]
    return records(directory/f'video-demo-{number}.bin.gz', number, load['load_segment'],
                   load['load_segment']+profile['dgroup'], [3, 0, 2, 1][number-1], load['cr0'], load['cr3'])


def summarize_pair(original, candidate, first_dump=None):
    rows, first, count, differing_frames = {}, None, 0, 0
    raw_gdc_differing_frames = 0
    for (frame, left), (other_frame, right) in zip(original, candidate, strict=True):
        require(frame == other_frame, 'paired video frame boundary')
        a, b = regions(left), regions(right)
        require(a.keys() == b.keys(), 'paired video region extent')
        changes = []
        for name in a:
            if name not in rows:
                rows[name] = dict(differing_frames=0, first_difference=None,
                                  original_hash=hashlib.sha256(), candidate_hash=hashlib.sha256(),
                                  original_values=set(), candidate_values=set(),
                                  original_nonzero_frames=0, candidate_nonzero_frames=0)
            row = rows[name]
            row['original_hash'].update(a[name])
            row['candidate_hash'].update(b[name])
            row['original_values'].add(sha(a[name]))
            row['candidate_values'].add(sha(b[name]))
            row['original_nonzero_frames'] += any(a[name])
            row['candidate_nonzero_frames'] += any(b[name])
            if a[name] != b[name]:
                changes.append(name)
                row['differing_frames'] += 1
                if row['first_difference'] is None:
                    indices = [i for i in range(len(a[name])) if a[name][i] != b[name][i]]
                    row['first_difference'] = dict(frame=frame, after_update=frame-1, differing_bytes=len(indices),
                        changes=[dict(offset=i, original=a[name][i], candidate=b[name][i]) for i in indices[:32]])
        at = OFFSETS['gdc']
        raw_gdc_differing_frames += left[at:at+SIZES['gdc']] != right[at:at+SIZES['gdc']]
        if changes:
            differing_frames += 1
            if first is None:
                first = dict(frame=frame, after_update=frame-1, regions=changes)
                if first_dump is not None:
                    for name, block in (('original', left), ('candidate', right)):
                        path = first_dump.with_name(first_dump.name+'-'+name+'.bin')
                        require(not path.exists(), 'fresh first-divergence dump path')
                        path.write_bytes(block)
                        first[name+'_dump'] = dict(path=str(path), sha256=sha(block))
        count += 1
    require(count == UPDATE_COUNT, 'incomplete paired video extent')
    for row in rows.values():
        row.update(passed=row['first_difference'] is None,
                   original_sha256=row.pop('original_hash').hexdigest(),
                   candidate_sha256=row.pop('candidate_hash').hexdigest(),
                   original_distinct_frames=len(row.pop('original_values')),
                   candidate_distinct_frames=len(row.pop('candidate_values')))
    return dict(passed=first is None, updates=count, differing_frames=differing_frames,
                first_difference=first, regions=rows, raw_gdc_differing_frames=raw_gdc_differing_frames)


def compare(original, candidate, original_full, candidate_full, original_consumer, candidate_consumer, dump_dir):
    a, ap, ad = read_side(original, original_full, original_consumer)
    b, bp, bd = read_side(candidate, candidate_full, candidate_consumer)
    for name in PAIR_PINS:
        require(a[name] == b[name], 'paired video reset/observer mismatch: '+name)
    require(a['video_stream']['gdb_sha256'] == b['video_stream']['gdb_sha256'], 'paired video debugger')
    require(a['role'] == 'original' and b['role'] == 'ordinary-reconstructed', 'video comparison roles')
    result = dict(passed=True, accepts_exact=False, boundary=BOUNDARY, block_bytes=BLOCK_SIZE,
                  scope='all two-page four-plane VRAM bytes, complete TRAM/palettes and programmed GDC presentation state',
                  raw_gdc_retained=True, excludes='GDC scan/raster/FIFO/drawing-clock internals; no full scanout/teardown/x64 acceptance',
                  original_receipt_sha256=sha((original/'receipt.json').read_bytes()),
                  candidate_receipt_sha256=sha((candidate/'receipt.json').read_bytes()), ordinary_controls_passed=True, demos={})
    for number in range(1, a['demos']+1):
        row = summarize_pair(iter_side(original, number, ap, ad), iter_side(candidate, number, bp, bd),
                             None if dump_dir is None else dump_dir/f'demo-{number}-first')
        result['demos'][str(number)] = row
        result['passed'] &= row['passed']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('original', 'candidate', 'original-full', 'candidate-full', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--original-consumer', type=Path, default=Path(__file__).parent)
    parser.add_argument('--candidate-consumer', type=Path, default=Path(__file__).parent)
    parser.add_argument('--first-dump-dir', type=Path)
    args = parser.parse_args()
    if args.first_dump_dir is not None:
        args.first_dump_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = compare(args.original, args.candidate, args.original_full, args.candidate_full,
                         args.original_consumer, args.candidate_consumer, args.first_dump_dir)
    except (ValueError, KeyError, OSError, TypeError, IndexError, EOFError) as error:
        result = dict(passed=False, accepts_exact=False, invalid_capture=str(error))
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
