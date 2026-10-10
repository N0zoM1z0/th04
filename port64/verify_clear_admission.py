#!/usr/bin/env python3
"""Read-only actual admission replay and checksummed clear-mask counterexamples.

Requires a completed actual Normal route. All cloned traces are immutable hard
links; mutated scores/events are separate scratch files. No game is launched.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from verify_window_continue import decode, has_clear
from verify_window_extra import earned_normal


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def masked_score(raw, mask):
    section = bytearray(decode(raw)[1])
    section[174] = mask
    checksum = sum(section[4:])
    section[2:4] = checksum.to_bytes(2, 'little')
    key0, key1 = section[:2]
    section[195] = (section[195] - key0) & 255
    for i in range(194, 3, -1):
        rotate = ((section[i+1] >> 3) | (section[i+1] << 5)) & 255
        section[i] = (section[i] - key0 - (rotate ^ key1)) & 255
    result = raw[:196] + bytes(section) + raw[392:]
    assert decode(result)[1][174] == mask
    return result


def clone(source, output):
    output.mkdir()
    report = json.loads((source / 'receipt.json').read_text())
    for name in ('trace/window.tsv', 'restart/trace/window.tsv'):
        target = output / name
        target.parent.mkdir(parents=True)
        target.hardlink_to(source / name)
    shutil.copytree(source / 'saves', output / 'saves')
    shutil.copytree(source / 'physical-events', output / 'physical-events')
    return report


def reject(path):
    try:
        earned_normal(path)
    except AssertionError as error:
        return str(error)
    raise AssertionError('invalid admission fixture accepted')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--normal-route', type=Path, required=True)
    parser.add_argument('--rejected-route', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source, negative, out = [p.resolve() for p in
                              (args.normal_route, args.rejected_route, args.output)]
    out.mkdir(parents=True, exist_ok=False)
    pins = {str(p): sha(p) for p in
            [source / 'receipt.json', source / 'trace/window.tsv',
             source / 'restart/trace/window.tsv', source / 'saves/GENSOU.SCR',
             negative / 'receipt.json', negative / 'saves/GENSOU.SCR', Path(__file__)]}
    assert earned_normal(source)['passed']
    raw = (source / 'saves/GENSOU.SCR').read_bytes()
    assert has_clear(decode(raw)[1], 0)
    assert decode((negative / 'saves/GENSOU.SCR').read_bytes())[1][174] == 0x19
    negative_error = reject(negative)
    assert negative_error == 'Reimu A admission must be earned at Normal rank'
    results = []
    for label, mask in [('absent', 0), ('other-shot', 2),
                        ('initial-sentinel', 0x19), ('high-mask-with-bit0', 0x41)]:
        folder = out / label
        report = clone(source, folder)
        target = folder / 'saves/GENSOU.SCR'
        target.write_bytes(masked_score(raw, mask))
        report['files']['GENSOU.SCR'] = sha(target)
        for name in ('files_before', 'files_after'):
            report['restart'][name]['GENSOU.SCR'] = sha(target)
        (folder / 'receipt.json').write_text(json.dumps(report) + '\n')
        error = reject(folder)
        assert error == 'Reimu A admission must be earned at Normal rank'
        results.append(dict(name=label, mask=mask, checksum_valid=True,
                            rejected=True, error=error, score_sha256=sha(target)))
        shutil.rmtree(folder)
    folder = out / 'physical-sentinel'
    report = clone(source, folder)
    for event in report['physical_events']:
        if event['name'] == 'GENSOU.SCR':
            target = folder / 'physical-events' / event['snapshot']
            target.write_bytes(masked_score(target.read_bytes(), 0x19))
            event['sha256'] = sha(target)
    (folder / 'receipt.json').write_text(json.dumps(report) + '\n')
    error = reject(folder)
    results.append(dict(name='physical-sentinel', rejected=True,
                        checksum_valid=True, error=error))
    shutil.rmtree(folder)
    for path, digest in pins.items():
        assert sha(Path(path)) == digest
    receipt = dict(passed=True, pins=pins, actual_negative_error=negative_error,
                   controls=results, scope=__doc__,
                   reader_sha256=sha(Path(__file__).parent / 'verify_window_extra.py'),
                   mask_reader_sha256=sha(Path(__file__).parent / 'verify_window_continue.py'))
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Admission positive / actual sentinel route / five checksummed mutants PASS')


if __name__ == '__main__':
    main()
