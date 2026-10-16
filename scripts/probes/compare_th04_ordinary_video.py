#!/usr/bin/env python3
"""Compare ordinary full VRAM/palettes with independent scalar controls."""
import argparse
import json
from pathlib import Path

from capture_th04_dos_demos import sha
from compare_th04_demo_video import summarize_pair
from compare_th04_bounded_ordinary import read_side as read_bounded_side
from compare_th04_dos_demos import require
from compare_th04_dos_ordinary_prefix import compare
from compare_th04_ordinary_pools import read_side, scalar_control
from th04_demo_dgroup import UPDATE_COUNT
from th04_demo_video import BLOCK_SIZE, LAYOUT, SYMBOL_SIZES
from th04_ordinary_dgroup import BOUNDARY
from th04_ordinary_video import records


def video_side(directory, baseline, original, snapshot):
    # Select by the pinned receipt, never by an unchecked caller-supplied count.
    receipt = json.loads((directory / 'receipt.json').read_text())
    if receipt.get('end_after') is None:
        capture, profile, _, control = read_side(directory, baseline, original, snapshot)
        count = UPDATE_COUNT
    else:
        capture, profile, _ = read_bounded_side(directory, original, snapshot)
        control = scalar_control(capture, baseline, original, snapshot)
        count = capture['receipt']['end_after']
    receipt = capture['receipt']
    require({'ordinary-video.json', 'ordinary-video.bin.gz'} <= receipt['files'].keys(),
            'missing pinned ordinary video stream')
    layout_path = Path(receipt['video_layout']['path'])
    require(sha(layout_path.read_bytes()) == receipt['video_layout']['sha256'], 'video layout identity')
    layout = json.loads(layout_path.read_text())
    require(layout['passed'] and layout['layout'] == LAYOUT and
            layout['emulator_sha256'] == receipt['emulator_sha256'] and
            layout['emulator_receipt_sha256'] == receipt['emulator_receipt_sha256'] and
            {name: row['size'] for name, row in layout['symbols'].items()} == SYMBOL_SIZES,
            'video ABI/binary/symbol widths')
    for path, digest in layout['source_inputs'].items():
        require(sha(Path(path).read_bytes()) == digest, 'video compiled source identity')
    metadata = json.loads((directory / 'ordinary-video.json').read_text())
    require(metadata['schema_version'] == 1 and metadata['complete'] and
            metadata['boundary'] == BOUNDARY and metadata['frames'] == count and
            metadata['block_bytes'] == BLOCK_SIZE and metadata['layout'] == LAYOUT,
            'ordinary video extent/boundary')
    require(set(metadata['video_symbols']) == set(SYMBOL_SIZES) and
            len({metadata['video_symbols'][name] - row['address']
                 for name, row in layout['symbols'].items()}) == 1, 'video runtime ELF mapping')
    mappings = metadata['video_mappings']
    require(mappings and mappings[0]['first_frame'] == 1, 'video initial backing mapping')
    previous = 0
    for mapping in mappings:
        base = mapping['backing_ram']
        require(previous < mapping['first_frame'] <= count and base > 0 and
                mapping['backing_bytes'] >= 0x44000 and
                mapping['cpu_page'] in (base + 0x4000, base + 0xc000) and
                mapping['display_page'] in (base + 0x4000, base + 0xc000), 'video backing/page extent')
        previous = mapping['first_frame']
    row = next(line.split() for line in (directory / 'raw.txt').read_text().splitlines()
               if line.startswith('L '))
    load, cr0, cr3 = (int(value, 16) for value in row[2:5])
    require(metadata['load_segment'] == load and metadata['dgroup_segment'] == load + profile['dgroup'],
            'video guest load identity')
    terminal = capture.get('bounded_terminal')
    if terminal:
        require((load, load + profile['dgroup'], cr0, cr3) ==
                tuple(terminal[key] for key in ('load_segment', 'dgroup_segment', 'cr0', 'cr3')),
                'video bounded terminal CPU identity')
    iterator = records(directory / 'ordinary-video.bin.gz', load, load + profile['dgroup'], cr0, cr3, count)
    return capture, iterator, control


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--original-baseline', required=True, type=Path)
    parser.add_argument('--candidate-baseline', required=True, type=Path)
    parser.add_argument('--baseline-sources', required=True, type=Path)
    parser.add_argument('--original-main', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--first-dump', type=Path)
    args = parser.parse_args()
    original = args.original_main.read_bytes()
    a, ar, at = video_side(args.original, args.original_baseline, original, args.baseline_sources)
    b, br, bt = video_side(args.candidate, args.candidate_baseline, original, args.baseline_sources)
    require(a['receipt']['role'] == 'original' and b['receipt']['role'] == 'candidate', 'video pair roles')
    require(compare(a, b)['passed'], 'video paired scalar/RNG control')
    for key in ('end_after', 'dialog_at_frame', 'continue_at_frame', 'post_boss_dialog_at_frame', 'termination', 'natural_game_exit'):
        require(a['receipt'].get(key) == b['receipt'].get(key), 'video paired contract: ' + key)
    for key in ('emulator_sha256', 'debugger_sha256', 'font_sha256', 'adapter_sha256', 'walker_sha256'):
        require(a['receipt'][key] == b['receipt'][key], 'video pair identity: ' + key)
    require(a['receipt']['files']['dosbox-x.conf'] == b['receipt']['files']['dosbox-x.conf'] and
            a['starting_files'] == b['starting_files'], 'video paired reset/configuration')
    require(a['receipt']['video_layout']['sha256'] == b['receipt']['video_layout']['sha256'],
            'video paired ABI receipt')
    result = summarize_pair(ar, br, args.first_dump, a['receipt'].get('end_after', UPDATE_COUNT))
    result.update(accepts_exact=False, boundary=BOUNDARY, scalar_controls=[at, bt],
                  block_bytes=BLOCK_SIZE, raw_gdc_retained=True,
                  natural_game_exit=False,
                  scope='Complete bounded ordinary two-page/four-plane VRAM, TRAM, palettes and configured GDC state; no raw raster/FIFO/scanout/defeat/campaign acceptance',
                  receipts={str(path): sha((path / 'receipt.json').read_bytes()) for path in
                            (args.original, args.candidate, args.original_baseline, args.candidate_baseline)})
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=result['passed'], updates=result['updates'],
                         first_difference=result['first_difference'],
                         raw_gdc_differing_frames=result['raw_gdc_differing_frames'],
                         differing_regions={name: row['differing_frames'] for name, row in
                                            result['regions'].items() if not row['passed']})))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
