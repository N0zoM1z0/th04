#!/usr/bin/env python3
"""Attest the copied back page used by the original post-Boss dialogue suffix.

Complete original checkpoint ownership is checked independently of native RGB.
The copied playfield covers four planes at physical x32..415/y16..383. This
bounded page observation does not establish whole-game or exact reconstruction.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from attest_th04_postboss_checkpoints import attest_capture
from th04_demo_video import OFFSETS, SIZES

LABELS = ('player-update', 'dialog-animate', 'dialog-run', 'dialog-return')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def page_transition(checkpoints, completed_video):
    """Check real raw page observations; expose this layer for actual mutants."""
    require(set(checkpoints) == set(LABELS), 'dialogue page checkpoint labels')
    rows = {}
    for label in LABELS:
        video, group = checkpoints[label]
        require(len(video) == sum(SIZES.values()) and len(group) == 65536,
                'dialogue complete video/DGROUP extent')
        require(int.from_bytes(group[0x538a:0x538c], 'little') == 9348,
                'dialogue page frame')
        graphics = video[OFFSETS['graphics']:OFFSETS['graphics'] + SIZES['graphics']]
        modes = video[OFFSETS['modes']:OFFSETS['modes'] + SIZES['modes']]
        back, front = group[0x46fc:0x46fe]
        require(back in (0, 1) and front == 1 - back, 'dialogue page roles')

        def field(page):
            return b''.join(graphics[plane * 65536 + page * 32768 + y * 80 + 4:
                                     plane * 65536 + page * 32768 + y * 80 + 52]
                            for plane in range(4) for y in range(16, 384))

        rows[label] = dict(back=back, front=front, modes=list(modes),
                           back_field=field(back), front_field=field(front),
                           video_sha256=sha(video), dgroup_sha256=sha(group))
    require(len({(row['back'], row['front']) for row in rows.values()}) == 1,
            'dialogue page roles changed inside the blocked frame')
    before, after = rows['dialog-run'], rows['dialog-return']
    require(before['back_field'] == before['front_field'],
            'dialogue pre-script front/back copy')
    require(before['back_field'] == after['back_field'],
            'dialogue saved back page changed during script')
    changed = sum(a != b for a, b in zip(after['front_field'], after['back_field'], strict=True))
    require(changed > 0, 'dialogue front portrait writes missing')
    # pc98_gdc_vramop contains other flags; only bit0 selects the CPU page.
    require(after['modes'][0] & 1 == after['back'], 'dialogue return CPU back page')
    require(len(completed_video) == sum(SIZES.values()), 'resumed complete video extent')
    require(completed_video[OFFSETS['modes'] + 1] == after['back'],
            'resumed display does not select copied back page')
    return dict(rows={label: {key: sha(value) if key.endswith('_field') else value
                             for key, value in row.items()} for label, row in rows.items()},
                copied_playfield_bytes=70656, pre_run_pages_equal=True,
                back_unchanged_during_script=True, front_back_changed_bytes=changed,
                resumed_display_selects_copied_back=True)


def attest_pages(capture, target):
    witness = attest_capture(capture, target)
    checkpoints = {}
    for label in LABELS:
        stem = capture / 'postboss-checkpoints' / label
        metadata = json.loads(Path(str(stem) + '.json').read_text())
        video = gzip.decompress(Path(str(stem) + '-video.bin.gz').read_bytes())
        group = Path(str(stem) + '-dgroup.bin').read_bytes()
        require((sha(video), sha(group)) == (metadata['video_sha256'], metadata['dgroup_sha256']),
                'dialogue page content identity')
        checkpoints[label] = video, group
    stem = capture / 'post-score-checkpoints' / '9349'
    metadata = json.loads(Path(str(stem) + '.json').read_text())
    video = gzip.decompress(Path(str(stem) + '-video.bin.gz').read_bytes())
    group = gzip.decompress(Path(str(stem) + '-dgroup.bin.gz').read_bytes())
    require((sha(video), sha(group)) == (metadata['video_sha256'], metadata['dgroup_sha256']),
            'resumed page content identity')
    registers, segments = bytes.fromhex(metadata['registers']), bytes.fromhex(metadata['segments'])
    require(len(registers) == 48 and len(segments) == 136 and len(group) == 65536,
            'resumed raw CPU/DGROUP extent')
    require((int.from_bytes(registers[32:36], 'little') & 65535,
             int.from_bytes(segments[8:16], 'little'),
             int.from_bytes(segments[24:32], 'little')) ==
            (0x207, metadata['load_segment'] + 0xaaf, metadata['dgroup_segment']),
            'resumed score-return CS:IP/DS')
    require(metadata['frame'] == 9349 and metadata['unchanged_context'] and
            int.from_bytes(group[0x538a:0x538c], 'little') == 9349,
            'resumed page frame/read-only context')
    observations = page_transition(checkpoints, video)
    header = int.from_bytes(target[8:10], 'little') * 16
    code = target[header + 0xaaf * 16 + 0x2bfb:header + 0xaaf * 16 + 0x2c39]
    for offset, encoded in ((0x2c19, 'e80af9'), (0x2c1c, 'e85dfe'),
                            (0x2c29, 'baa600a0fc46ee'), (0x2c38, 'cb')):
        wanted = bytes.fromhex(encoded)
        require(code[offset - 0x2bfb:offset - 0x2bfb + len(wanted)] == wanted,
                'original dialogue copy/run/back-return code')
    return dict(passed=True, target_sha256=sha(target),
                capture_receipt_sha256=sha((capture / 'receipt.json').read_bytes()),
                witness_reader_sha256=witness['reader_source_sha256'],
                reader_sha256=sha(Path(__file__).read_bytes()),
                animate_extent=dict(artifact='th04-main', segment='0AAF', offset='2BFB',
                                    size=len(code), sha256=sha(code)),
                completed_video_sha256=sha(video), **observations,
                scope=__doc__ + ' Actual9348 CPU/stack/code/video ownership precedes the actual9349 score return. '
                      '0AAF:2C19 copies front to back before2C1C dialog_run;2C29 selects DS46FC back. '
                      'No target/native writes, pixel masks, clock fitting or historical exact promotion.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('capture', 'main', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    result = attest_pages(args.capture.resolve(), args.main.read_bytes())
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(passed=True, copied_bytes=result['copied_playfield_bytes'],
                         portrait_changed_bytes=result['front_back_changed_bytes'])))


if __name__ == '__main__':
    main()
