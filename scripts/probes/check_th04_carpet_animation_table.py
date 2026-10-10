#!/usr/bin/env python3
"""Check all Stage 4 carpet lighting cells against the attested MAIN table.

This is a bounded data contract, not historical exact acceptance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib

from capture_th04_dos_demos import ROOT, map_symbols, sha
from check_th04_carpet_image_table import initialized_table
from compare_th04_dos_demos import require
from lib.pc98 import parse_mz

CELS = 8
COLUMNS = 24
EXTENT = CELS*COLUMNS


def compare_tables(original: bytes, candidate: bytes) -> dict:
    require(len(original) == len(candidate) == EXTENT, 'complete carpet animation extent')
    require(all(value in (0, 1, 2) for value in original), 'original animation state domain')
    differences = [dict(cel=index//COLUMNS, column=index % COLUMNS,
                        original=expected, candidate=actual)
                   for index, (expected, actual) in enumerate(zip(original, candidate))
                   if expected != actual]
    return dict(passed=not differences, extent_bytes=EXTENT,
                original_table_sha256=sha(original), candidate_table_sha256=sha(candidate),
                differing_cells=differences)


def check(build_dir: Path, map_path: Path) -> dict:
    target = next(t for t in tomllib.loads((ROOT/'config/targets.toml').read_text())['artifacts']
                  if t['id'] == 'th04-main')
    original = (ROOT/target['private_path']).read_bytes()
    require(len(original) == target['size'] and sha(original) == target['sha256']
            and parse_mz(original).valid, 'original target identity/format')
    header = int.from_bytes(original[8:10], 'little')*16
    require(int.from_bytes(original[header+1:header+3], 'little') == 0x2134,
            'original animation DGROUP')
    for address, instruction in ((0x3FAB, '81c69c19'), (0x4026, '80b99c1902')):
        raw = bytes.fromhex(instruction)
        at = header+0x0AAF*16+address
        require(original[at:at+len(raw)] == raw, 'original animation instruction ownership')
    at = header+0x2134*16+0x199C
    original_table = original[at:at+EXTENT]
    manifest = json.loads((build_dir/'build.json').read_text())
    record = manifest['products']['main']
    main = (build_dir/record['file']).read_bytes()
    require(len(main) == record['size'] and sha(main) == record['sha256'], 'candidate identity')
    producer = Path(record['build_receipt'])
    receipt = json.loads(producer.read_text())
    require(sha(map_path.read_bytes()) == receipt['link']['map_sha256'], 'candidate MAP identity')
    segment, offset = map_symbols(map_path)['_CARPET_LIGHTING_ANIM']
    table = initialized_table(main, map_path.read_text(), segment, offset, EXTENT)
    result = compare_tables(original_table, table)
    result.update(accepts_exact=False, original_sha256=sha(original), candidate_sha256=sha(main),
                  map_sha256=sha(map_path.read_bytes()), producer_receipt_sha256=sha(producer.read_bytes()),
                  original_address='MAIN DGROUP(2134):199C',
                  candidate_address=f'MAIN DGROUP({segment:04X}):{offset:04X}')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--map', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'fresh animation comparison output')
    result = check(args.build_dir, args.map)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
