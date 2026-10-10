#!/usr/bin/env python3
"""Check the complete linked bullet invalidator's operand and call contract.

Address substitution is diagnostic only; this does not accept historical exactness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import struct
import tomllib

from capture_th04_dos_demos import ROOT, map_symbols, sha
from compare_th04_dos_demos import require
from lib.pc98 import parse_mz

SIZE = 0x96
# Reviewed MAIN TILE_TEXT(0AAF):1FA8..203D, including the terminal EVEN byte.
DATA_SITES = ((3, 'bullets', 0), (10, 'bullet_zap_active', 0),
              (17, 'bullet_clear_time', 0), (25, 'tile_invalidate_box', 0),
              (58, 'tile_invalidate_box', 0), (78, 'tile_invalidate_box', 0),
              (90, 'tile_invalidate_box', 0), (108, 'gather_circles', 0),
              (128, 'tile_invalidate_box', 0), (131, 'tile_invalidate_box', 2))
CALL_SITES = (44, 85, 99, 138)
ORIGINAL_DATA = dict(bullets=0x5A22, bullet_zap_active=0xBCB9,
                     bullet_clear_time=0xBCBA, tile_invalidate_box=0x4264,
                     gather_circles=0x9292)


def owner_extent(map_text: str, wrapper: str, segment: int, entry: int) -> int:
    owners = []
    for line in map_text.splitlines():
        match = re.match(r'^\s*([0-9A-F]+):([0-9A-F]+)\s+([0-9A-F]+)\s+C=CODE\s+S=TILE_TEXT\s+G=MAIN_01\s+M=(\S+)\s+ACBP=', line)
        if match and match[4].replace('\\', '/') == wrapper:
            owners.append((int(match[1], 16), int(match[2], 16), int(match[3], 16)))
    require(len(owners) == 1 and owners[0][:2] == (segment, entry),
            'unique complete invalidator MAP owner')
    return owners[0][2]


def normalize(body: bytes, entry: int, around: int, data: dict[str, int]) -> bytes:
    require(len(body) == SIZE, 'complete invalidator extent (including EVEN)')
    result = bytearray(body)
    for at, name, delta in DATA_SITES:
        require(struct.unpack_from('<H', body, at)[0] == data[name]+delta,
                f'invalidator data binding: {name}+{delta}')
        result[at:at+2] = b'\0\0'
    for at in CALL_SITES:
        require(body[at-1] == 0xE8 and
                (entry+at+2+struct.unpack_from('<h', body, at)[0]) & 65535 == around,
                'invalidator near Pascal callee')
        result[at:at+2] = b'\0\0'
    return bytes(result)


def check(build: Path, map_path: Path) -> dict:
    target = next(t for t in tomllib.loads((ROOT/'config/targets.toml').read_text())['artifacts']
                  if t['id'] == 'th04-main')
    original = (ROOT/target['private_path']).read_bytes()
    require(len(original) == target['size'] and sha(original) == target['sha256']
            and parse_mz(original).valid, 'original target identity/format')
    original_body = original[0xE298:0xE298+SIZE]
    expected = normalize(original_body, 0x1FA8, 0x0EE6, ORIGINAL_DATA)
    manifest = json.loads((build/'build.json').read_text())
    record = manifest['products']['main']
    main = (build/record['file']).read_bytes()
    require(len(main) == record['size'] and sha(main) == record['sha256']
            and parse_mz(main).valid, 'candidate identity/format')
    producer = Path(record['build_receipt'])
    receipt = json.loads(producer.read_text())
    require(sha(map_path.read_bytes()) == receipt['link']['map_sha256'], 'candidate MAP identity')
    symbols = map_symbols(map_path)
    segment, entry = symbols['bullets_and_gather_invalidate()']
    around_segment, around = symbols['TILES_INVALIDATE_AROUND']
    require(segment == around_segment, 'invalidator near-call segment')
    header = int.from_bytes(main[8:10], 'little')*16
    dgroup = int.from_bytes(main[header+1:header+3], 'little')
    data = {}
    for name in ORIGINAL_DATA:
        seg, off = symbols['_'+name]
        require(seg == dgroup, f'invalidator DGROUP: {name}')
        data[name] = off
    extent = owner_extent(map_path.read_text(), receipt['body_only_wrappers']['src/main/bullet/invalidate.asm'], segment, entry)
    body = main[header+segment*16+entry:header+segment*16+entry+extent]
    problems = []
    try:
        actual = normalize(body, entry, around, data)
        differences = [i for i, (a, b) in enumerate(zip(expected, actual)) if a != b]
        if differences:
            problems.append(f'non-address instruction differences: {differences}')
    except (ValueError, AssertionError) as error:
        problems.append(str(error))
    return dict(passed=not problems, accepts_exact=False, problems=problems,
                extent_bytes=SIZE, original_address='MAIN TILE_TEXT(0AAF):1FA8',
                candidate_extent_bytes=extent,
                candidate_address=f'MAIN TILE_TEXT({segment:04X}):{entry:04X}',
                original_sha256=sha(original), candidate_sha256=sha(main),
                original_body_sha256=sha(original_body), candidate_body_sha256=sha(body),
                map_sha256=sha(map_path.read_bytes()), producer_receipt_sha256=sha(producer.read_bytes()),
                scope='complete instruction contract with attested symbolic data/callee substitutions; no raw exact promotion')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--map', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = check(args.build_dir, args.map)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
