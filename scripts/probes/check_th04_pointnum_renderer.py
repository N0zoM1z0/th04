#!/usr/bin/env python3
"""Check the complete linked point-number renderer's operand and call contract.

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

SIZE = 0x9A
# Reviewed MAIN CIRCLE_TEXT(0AAF):1274..130D, including the terminal RET.
DATA_SITES = ((20, 'pointnums_alive', 0), (31, 'pointnum_first_yellow_alive', 0))
CALL_SITES = ((67, 'scroll'), (103, 'put'), (112, 'put'), (133, 'put'), (139, 'put'))
ORIGINAL_DATA = dict(pointnums_alive=0x3ED0, pointnum_first_yellow_alive=0x41F2)
SELF_WIDTH_SITE = 96
SELF_WIDTH_IMMEDIATE = 117
SPRITE_BYTES = 12*128


def owner_extent(map_text: str, wrapper: str, segment: int, entry: int) -> int:
    owners = []
    for line in map_text.splitlines():
        match = re.match(r'^\s*([0-9A-F]+):([0-9A-F]+)\s+([0-9A-F]+)\s+C=CODE\s+S=CIRCLE_TEXT\s+G=MAIN_01\s+M=(\S+)\s+ACBP=', line)
        if match and match[4].replace('\\', '/') == wrapper:
            owners.append((int(match[1], 16), int(match[2], 16), int(match[3], 16)))
    require(len(owners) == 1 and owners[0][:2] == (segment, entry),
            'unique complete renderer MAP owner')
    return owners[0][2]


def normalize(body: bytes, entry: int, callees: dict[str, int], data: dict[str, int]) -> bytes:
    require(len(body) == SIZE, 'complete renderer extent (including RET)')
    result = bytearray(body)
    for at, name, delta in DATA_SITES:
        require(struct.unpack_from('<H', body, at)[0] == data[name]+delta,
                f'renderer data binding: {name}+{delta}')
        result[at:at+2] = b'\0\0'
    for at, name in CALL_SITES:
        require(body[at-1] == 0xE8 and
                (entry+at+2+struct.unpack_from('<h', body, at)[0]) & 65535 == callees[name],
                'renderer near callee')
        result[at:at+2] = b'\0\0'
    require(body[SELF_WIDTH_SITE-3:SELF_WIDTH_SITE] == b'\x2e\x89\x0e' and
            struct.unpack_from('<H', body, SELF_WIDTH_SITE)[0] == entry+SELF_WIDTH_IMMEDIATE,
            'renderer self-modifying width immediate')
    result[SELF_WIDTH_SITE:SELF_WIDTH_SITE+2] = b'\0\0'
    return bytes(result)


def check(build: Path, map_path: Path) -> dict:
    target = next(t for t in tomllib.loads((ROOT/'config/targets.toml').read_text())['artifacts']
                  if t['id'] == 'th04-main')
    original = (ROOT/target['private_path']).read_bytes()
    require(len(original) == target['size'] and sha(original) == target['sha256']
            and parse_mz(original).valid, 'original target identity/format')
    original_body = original[0xD564:0xD564+SIZE]
    expected = normalize(original_body, 0x1274, dict(scroll=0x1120, put=0x130E), ORIGINAL_DATA)
    manifest = json.loads((build/'build.json').read_text())
    record = manifest['products']['main']
    main = (build/record['file']).read_bytes()
    require(len(main) == record['size'] and sha(main) == record['sha256']
            and parse_mz(main).valid, 'candidate identity/format')
    producer = Path(record['build_receipt'])
    receipt = json.loads(producer.read_text())
    require(sha(map_path.read_bytes()) == receipt['link']['map_sha256'], 'candidate MAP identity')
    symbols = map_symbols(map_path)
    segment, entry = symbols['POINTNUMS_RENDER']
    callees = {}
    for name, symbol in (('scroll', 'SCROLL_SUBPIXEL_Y_TO_VRAM_SEG1'), ('put', '@pointnum_put')):
        callee_segment, callees[name] = symbols[symbol]
        require(segment == callee_segment, 'renderer near-call segment')
    header = int.from_bytes(main[8:10], 'little')*16
    dgroup = int.from_bytes(main[header+1:header+3], 'little')
    data = {}
    for name in ORIGINAL_DATA:
        seg, off = symbols['_'+name]
        require(seg == dgroup, f'renderer DGROUP: {name}')
        data[name] = off
    extent = owner_extent(map_path.read_text(), receipt['body_only_wrappers']['src/main/pointnum/render.asm'], segment, entry)
    body = main[header+segment*16+entry:header+segment*16+entry+extent]
    sprite_seg, sprite_off = symbols['_sPOINTNUMS']
    require(sprite_seg == dgroup, 'renderer sprite DGROUP')
    original_header = int.from_bytes(original[8:10], 'little')*16
    original_sprites = original[original_header+0x2134*16+0x098A:original_header+0x2134*16+0x098A+SPRITE_BYTES]
    sprites = main[header+dgroup*16+sprite_off:header+dgroup*16+sprite_off+SPRITE_BYTES]
    require(len(sprites) == SPRITE_BYTES, 'complete renderer sprite extent')
    problems = []
    if sprites != original_sprites:
        problems.append('renderer digit/multiplier sprite-table differences')
    try:
        actual = normalize(body, entry, callees, data)
        differences = [i for i, (a, b) in enumerate(zip(expected, actual)) if a != b]
        if differences:
            problems.append(f'non-address instruction differences: {differences}')
    except (ValueError, AssertionError) as error:
        problems.append(str(error))
    return dict(passed=not problems, accepts_exact=False, problems=problems,
                extent_bytes=SIZE, sprite_bytes=SPRITE_BYTES,
                original_sprite_sha256=sha(original_sprites), candidate_sprite_sha256=sha(sprites), original_address='MAIN CIRCLE_TEXT(0AAF):1274',
                candidate_extent_bytes=extent,
                candidate_address=f'MAIN CIRCLE_TEXT({segment:04X}):{entry:04X}',
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
