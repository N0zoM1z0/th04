#!/usr/bin/env python3
"""Compare actual OP/Extra/dialog/Mugetsu actor controls with independent requests.

The original dialog producer executes at two loads with explicit graphics,
input, resource, sound and wait adapters. Native actor controls disable player
hit consumption and adapt the unlock bit. Cross-host BMP equality and repaint
invariance do not establish original full pixels, ordinary survival, Gengetsu,
audio, physical timing or full-route acceptance. All launches must be muted.
"""
import argparse
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from verify import source_manifest


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(frontend, original):
    producer = json.loads((original / 'receipt.json').read_text())
    assert producer['passed'] and producer['resource_cases'] == 512
    assert producer['loads'] == ['1000', '2000']
    assert producer['target_sha256'] == '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
    assert sha(original / 'resource-original.txt') == producer['resource_trace_sha256']
    resources = (original / 'resource-original.txt').read_text().splitlines()
    wanted = None
    for load in ('1000', '2000'):
        script = original / f'script-{load}-0.txt'
        record = next(row for row in producer['scripts'] if row['load'] == load and row['held'] == 0)
        assert sha(script) == record['trace_sha256']
        lines = script.read_text().splitlines()
        end = next(i for i, line in enumerate(lines) if line.startswith('END '))
        assert lines[end].split()[1] == '987'
        decoded = []
        for line in lines[:end]:
            fields = line.split()
            if fields[-1] != '-':
                fields[-1] = bytes.fromhex(fields[-1]).decode('ascii')
            decoded.append(' '.join(fields))
        assert wanted is None or wanted == decoded
        wanted = decoded
    assert len(wanted) == 699
    scenes = []
    for character, shot, shooting, paint in itertools.product(range(2), repeat=4):
        name = f'{character}-{shot}-{shooting}-{paint}'
        path = frontend / (name + '.txt')
        lines = path.read_text().splitlines()
        actual = [line.removeprefix('dialog ') for line in lines if line.startswith('dialog ')]
        assert actual == wanted, f'{name}: actual dialog requests differ from original'
        actual_resources = [line.split()[1:] for line in lines if line.startswith('resource ')]
        reference = resources[character * 256].split()
        assert reference[:2] == ['1', '13']
        expected_resources = [reference[i:i+4] for i in range(2, len(reference), 4)]
        assert actual_resources == expected_resources, f'{name}: actual resources differ from original'
        records = [list(map(int, line.split())) for line in lines if line[0].isdigit()]
        phases = [row[1] for i, row in enumerate(records) if not i or row[1] != records[i-1][1]]
        assert phases == [0, 1, 2, 3, 4, 5, 6, 7, 254, 255], f'{name}: lifecycle phases differ'
        assert records[0][0:3] == [11197, 0, 1]
        pending = lines[-1].split()
        assert pending[0] == 'pending' and int(pending[7]) == 987
        assert int(pending[2]) > 1000
        if shooting:
            assert int(pending[4]) > 0 and int(pending[5]) > 0 and int(pending[6]) == 227
        else:
            assert pending[4:7] == ['0', '0', '0']
        captures = sorted(frontend.glob(name + '-*.bmp'))
        assert len(captures) == 12
        scenes.append(dict(name=name, frames=int(pending[1]), battle_ticks=int(pending[2]),
                           dialog_ticks=int(pending[3]), hit_frames=int(pending[4]),
                           wing_frames=int(pending[5]), bomb_frames=int(pending[6])))
    files = {p.name: sha(p) for p in sorted(frontend.iterdir()) if p.is_file()}
    assert len(files) == 208
    for character, shot, shooting in itertools.product(range(2), repeat=3):
        prefix = f'{character}-{shot}-{shooting}-'
        for name, digest in files.items():
            if name.startswith(prefix + '0'):
                assert files[prefix + '1' + name[len(prefix)+1:]] == digest, 'repaint differs'
    return scenes, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('original-dir', 'linux-dir', 'ubsan-dir', 'output-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    linux_scenes, linux_files = validate(args.linux_dir, args.original_dir)
    ubsan_scenes, ubsan_files = validate(args.ubsan_dir, args.original_dir)
    assert linux_scenes == ubsan_scenes and linux_files == ubsan_files, 'native hosts differ'
    manifest = source_manifest(Path(__file__).resolve().parents[1])[0]
    receipt = dict(passed=True, source_manifest=manifest, scenes=linux_scenes,
                   files=linux_files, bmp_count=192, dialog_events=699,
                   original_producer_receipt_sha256=sha(args.original_dir / 'receipt.json'),
                   executed_hosts=['GNU8.4', 'optimized UBSan'],
                   utc=datetime.now(timezone.utc).isoformat(), scope=__doc__)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Mugetsu frontend: PASS 16 scenes/208 files/192 BMPs; original first-dialog/resource requests agree')


if __name__ == '__main__':
    main()
