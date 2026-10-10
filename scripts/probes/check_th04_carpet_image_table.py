#!/usr/bin/env python3
"""Compare the initialized Stage 4 carpet table with the pinned MAIN owner.

This checks a bounded data contract, not historical exact acceptance.
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

EXTENT = 3*24*2


def initialized_table(main: bytes, map_text: str, segment: int, offset: int) -> bytes:
    require(parse_mz(main).valid, 'candidate MZ integrity')
    header = int.from_bytes(main[8:10], 'little')*16
    require(segment == int.from_bytes(main[header+1:header+3], 'little'), 'table DGROUP')
    linear = segment*16+offset
    owners = re.findall(r'^\s*([0-9A-F]+)H\s+([0-9A-F]+)H\s+([0-9A-F]+)H\s+(\S+)\s+(\S+)\s*$',
                        map_text, re.M)
    require(sum(name == '_DATA' and cls == 'DATA' and int(length, 16) > 0
                and int(start, 16) <= linear and linear+EXTENT-1 <= int(stop, 16)
                for start, stop, length, name, cls in owners) == 1, 'complete initialized DATA table')
    # A relocation would change a supposed VRAM offset when DOS loads MAIN.
    relocations = int.from_bytes(main[6:8], 'little')
    relocation_table = int.from_bytes(main[24:26], 'little')
    for at in range(relocation_table, relocation_table+relocations*4, 4):
        off, seg = struct.unpack_from('<HH', main, at)
        site = seg*16+off
        require(site+2 <= linear or site >= linear+EXTENT, 'relocation overlaps carpet table')
    data = main[header+linear:header+linear+EXTENT]
    require(len(data) == EXTENT, 'initialized table file extent')
    return data


def compare_tables(original: bytes, candidate: bytes) -> dict:
    require(len(original) == len(candidate) == EXTENT, 'carpet table extent')
    differences = []
    for level in range(3):
        for column in range(24):
            at = (level*24+column)*2
            expected, actual = (int.from_bytes(data[at:at+2], 'little')
                                for data in (original, candidate))
            if expected != actual:
                differences.append(dict(level=level, column=column,
                                        original=expected, candidate=actual))
    return dict(passed=not differences, extent_bytes=EXTENT,
                original_table_sha256=sha(original), candidate_table_sha256=sha(candidate),
                differing_words=differences)


def check(build_dir: Path, map_path: Path) -> dict:
    target = next(t for t in tomllib.loads((ROOT/'config/targets.toml').read_text())['artifacts']
                  if t['id'] == 'th04-main')
    original = (ROOT/target['private_path']).read_bytes()
    require(len(original) == target['size'] and sha(original) == target['sha256']
            and parse_mz(original).valid, 'original target identity/format')
    header = int.from_bytes(original[8:10], 'little')*16
    dgroup = int.from_bytes(original[header+1:header+3], 'little')
    require(dgroup == 0x2134, 'original DGROUP')
    # Actual STAGES_TEXT(0AAF) callers reference this table and tile_ring.
    for address, instruction in ((0x3fb6, '050c19'), (0x3fcb, '8985404d'),
                                 (0x403d, '8b870c19'), (0x4079, '8b840c19')):
        raw = bytes.fromhex(instruction)
        at = header+0x0aaf*16+address
        require(original[at:at+len(raw)] == raw, 'original carpet instruction ownership')
    table = original[header+dgroup*16+0x190c:header+dgroup*16+0x190c+EXTENT]
    manifest = json.loads((build_dir/'build.json').read_text())
    record = manifest['products']['main']
    main = (build_dir/'MAIN.EXE').read_bytes()
    require(len(main) == record['size'] and sha(main) == record['sha256'], 'candidate identity')
    producer = Path(record['build_receipt'])
    receipt = json.loads(producer.read_text())
    require(sha(map_path.read_bytes()) == receipt['link']['map_sha256'], 'candidate MAP identity')
    segment, offset = map_symbols(map_path)['_CARPET_TILE_IMAGE_VOS']
    result = compare_tables(table, initialized_table(main, map_path.read_text(), segment, offset))
    result.update(accepts_exact=False, original_sha256=sha(original), candidate_sha256=sha(main),
                  map_sha256=sha(map_path.read_bytes()), producer_receipt_sha256=sha(producer.read_bytes()),
                  original_address='MAIN DGROUP(2134):190C',
                  candidate_address=f'MAIN DGROUP({segment:04X}):{offset:04X}')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--map', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'fresh table comparison output')
    result = check(args.build_dir, args.map)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
