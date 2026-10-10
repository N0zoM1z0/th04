#!/usr/bin/env python3
"""Check the standalone Stage4 midboss toggle against pinned MAIN DATA.

This is a bounded static state Oracle, not executable or unit exactness.
Reject a BSS owner even if its file backing happens to contain the right byte.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tomllib

from capture_th04_dos_demos import ROOT, map_symbols, sha
from compare_th04_dos_demos import require
from lib.pc98 import parse_mz


def data_byte(main: bytes, map_text: str, segment: int, offset: int) -> int:
    require(parse_mz(main).valid, 'invalid candidate MZ')
    header = int.from_bytes(main[8:10], 'little')*16
    require(segment == int.from_bytes(main[header+1:header+3], 'little'),
            'toggle symbol outside startup DGROUP')
    linear = segment*16+offset
    owners = re.findall(r'^\s*([0-9A-F]+)H\s+([0-9A-F]+)H\s+([0-9A-F]+)H\s+(\S+)\s+(\S+)\s*$',
                        map_text, re.M)
    require(sum(name == '_DATA' and cls == 'DATA' and int(length, 16) > 0
                and int(start, 16) <= linear <= int(stop, 16)
                for start, stop, length, name, cls in owners) == 1,
            'toggle must belong to initialized _DATA, not BSS')
    require(header+linear < len(main), 'toggle outside initialized load module')
    return main[header+linear]


def check(build_dir: Path, map_path: Path) -> dict:
    target = next(t for t in tomllib.loads((ROOT / 'config/targets.toml').read_text())['artifacts']
                  if t['id'] == 'th04-main')
    original = (ROOT / target['private_path']).read_bytes()
    require(len(original) == target['size'] and sha(original) == target['sha256']
            and parse_mz(original).valid, 'original target identity/format')
    header = int.from_bytes(original[8:10], 'little')*16
    dgroup = int.from_bytes(original[header+1:header+3], 'little')
    expected = original[header+dgroup*16+0x185e]
    # Pinned bounded pattern-stack references: increment, then parity test.
    require(original[0x16862:0x16866] == bytes.fromhex('fe065e18')
            and original[0x16883:0x16888] == bytes.fromhex('f6065e1801'),
            'original stack increment/parity ownership changed')
    manifest = json.loads((build_dir / 'build.json').read_text())
    record = manifest['products']['main']
    main = (build_dir / 'MAIN.EXE').read_bytes()
    require(sha(main) == record['sha256'] and len(main) == record['size'], 'candidate identity')
    producer = Path(record['build_receipt'])
    receipt = json.loads(producer.read_text())
    require(sha(map_path.read_bytes()) == receipt['link']['map_sha256'], 'candidate MAP identity')
    segment, offset = map_symbols(map_path)['_midboss4_aim_toggle']
    actual = data_byte(main, map_path.read_text(), segment, offset)
    return dict(passed=actual == expected, accepts_exact=False,
                original_sha256=sha(original), candidate_sha256=sha(main),
                map_sha256=sha(map_path.read_bytes()), producer_receipt_sha256=sha(producer.read_bytes()),
                original_address=f'MAIN DGROUP({dgroup:04X}):185E',
                candidate_address=f'MAIN DGROUP({segment:04X}):{offset:04X}',
                original_initial_value=expected, candidate_initial_value=actual)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--map', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(args.build_dir, args.map)
    except (ValueError, KeyError, OSError, TypeError, IndexError) as error:
        result = dict(passed=False, accepts_exact=False, error=str(error))
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
