#!/usr/bin/env python3
"""Read back incomplete DGROUP diagnostics against an independent complete demo.

Original pool ownership comes from the target-backed bullet/enemy CPU Oracles;
candidate addresses come from its attested MAP. This diagnoses actor differences
at the stage_frame write, before score update, and never accepts demo parity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from capture_th04_dos_demos import map_symbols, sha
from compare_th04_dos_demos import load_capture, require


def read_snapshots(directory: Path, full: Path, frames: list[int]):
    parent, _, diagnostic = load_capture(full)
    receipt = json.loads((directory / 'receipt.json').read_text())
    require(not receipt['capture_complete'] and not receipt['timeout']
            and receipt['exit_code'] == 0 and receipt['diagnostic_snapshot']['complete'],
            'diagnostic must be a successful early stop, not a complete demo')
    require(receipt['diagnostic_snapshot']['frames'] == frames, 'requested snapshot extent')
    for name in ('role', 'main_sha256', 'map_sha256', 'products', 'starting_files',
                 'demo_sha256', 'initial_hdi_sha256', 'font_sha256', 'config_sha256',
                 'emulator_sha256', 'observer_source_sha256', 'profile_json_sha256'):
        require(receipt[name] == parent[name], f'diagnostic/complete capture mismatch: {name}')
    raw = (directory / 'raw.txt').read_bytes()
    require(sha(raw) == receipt['raw_sha256'] and (full / 'raw.txt').read_bytes().startswith(raw),
            'diagnostic caller/frame prefix differs from complete ordinary replay')
    profile = json.loads((directory / 'profile.json').read_text())
    require(sha((directory / 'profile.json').read_bytes()) == receipt['profile_json_sha256'],
            'diagnostic profile identity')
    load = diagnostic['loads'][0]['load_segment']
    snapshots, hashes = {}, {}
    for frame in frames:
        path = directory / f'snapshot-{frame}-dgroup.bin'
        metadata_path = directory / f'snapshot-{frame}.json'
        data = path.read_bytes()
        metadata = json.loads(metadata_path.read_text())
        offset = profile['fields'][0][1]
        require(len(data) == 65536 and int.from_bytes(data[offset:offset+2], 'little') == frame,
                'snapshot frame/size mismatch')
        require(metadata['frame'] == frame and metadata['load_segment'] == load
                and metadata['dgroup_segment'] == load+profile['dgroup']
                and metadata['cr0'] == diagnostic['loads'][0]['cr0']
                and metadata['cr3'] == diagnostic['loads'][0]['cr3']
                and metadata['boundary'] == 'stage_frame write, before mod counters and score update',
                'snapshot address/boundary mismatch')
        for file in (path, metadata_path):
            hashes[file.name] = sha(file.read_bytes())
            if 'files' in receipt['diagnostic_snapshot']:
                require(hashes[file.name] == receipt['diagnostic_snapshot']['files'][file.name],
                        'snapshot producer hash mismatch')
        snapshots[frame] = data
    return receipt, snapshots, hashes


def bullet(data: bytes) -> dict:
    def word(offset):
        return int.from_bytes(data[offset:offset+2], 'little', signed=True)
    return dict(raw=data.hex(), flag=data[0], age=data[1],
                position=[word(2), word(4)], previous=[word(6), word(8)],
                velocity=[word(10), word(12)], group=data[14], speed=data[16],
                angle=data[17], spawn_flag=data[18], move_flag=data[19])


def inspect(original: Path, candidate: Path, original_full: Path, candidate_full: Path,
            map_path: Path, frames: list[int]) -> dict:
    a, ad, ah = read_snapshots(original, original_full, frames)
    b, bd, bh = read_snapshots(candidate, candidate_full, frames)
    require(a['role'] == 'original' and b['role'] == 'ordinary-reconstructed', 'diagnostic roles')
    require(a['main_sha256'] == '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b',
            'original actor offsets require the pinned Japanese MAIN')
    require(sha(map_path.read_bytes()) == b['map_sha256'], 'candidate MAP identity')
    symbols = map_symbols(map_path)
    pool = symbols['_bullets'][1]
    graze = symbols['_stage_graze'][1]
    main_bytes = Path(b['main_path']).read_bytes()
    header = int.from_bytes(main_bytes[8:10], 'little')*16
    dgroup = int.from_bytes(main_bytes[header+1:header+3], 'little')
    require(symbols['_bullets'][0] == symbols['_stage_graze'][0]
            == dgroup,
            'actor symbols outside DGROUP')
    rows = []
    for frame in frames:
        differences = []
        for slot in range(440):
            x = ad[frame][0x5a22+slot*26:0x5a22+(slot+1)*26]
            y = bd[frame][pool+slot*26:pool+(slot+1)*26]
            if x != y:
                differences.append(dict(slot=slot, original=bullet(x), candidate=bullet(y),
                                        changed_offsets=[j for j in range(26) if x[j] != y[j]]))
        rows.append(dict(frame=frame, original_graze=int.from_bytes(ad[frame][0xbcbc:0xbcbe], 'little'),
                         candidate_graze=int.from_bytes(bd[frame][graze:graze+2], 'little'),
                         differences=differences))
    return dict(diagnostic_readback_passed=True, accepts_demo_parity=False,
                boundary='stage_frame write, before mod counters and score update',
                original_receipt_sha256=sha((original / 'receipt.json').read_bytes()),
                candidate_receipt_sha256=sha((candidate / 'receipt.json').read_bytes()),
                original_snapshot_sha256=ah, candidate_snapshot_sha256=bh,
                candidate_map_sha256=sha(map_path.read_bytes()),
                original_pool='MAIN DGROUP:5A22, 440*26 bytes; graze DGROUP:BCBC',
                candidate_pool=f'MAIN DGROUP:{pool:04X}, 440*26 bytes; graze DGROUP:{graze:04X}',
                snapshots=rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('original', 'candidate', 'original-full', 'candidate-full', 'map', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--frames', nargs='+', type=int, required=True)
    args = parser.parse_args()
    try:
        result = inspect(args.original, args.candidate, args.original_full, args.candidate_full,
                         args.map, args.frames)
    except (ValueError, KeyError, OSError, TypeError, IndexError) as error:
        result = dict(diagnostic_readback_passed=False, accepts_demo_parity=False, error=str(error))
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'snapshots'}))
    return 0 if result['diagnostic_readback_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
