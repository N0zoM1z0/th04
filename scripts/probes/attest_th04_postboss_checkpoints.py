#!/usr/bin/env python3
"""Attest original player input before the blocking post-Boss dialogue.

The STD dialogue precedes player_update. The ordinary Boss departure instead
calls dialogue after that player prefix. Keep these two input owners distinct.
"""
from __future__ import annotations

import argparse
import gzip
import json
import struct
from pathlib import Path

from attest_th04_dialog_checkpoints import MAIN_SHA256, require, sha
from compare_th04_dos_ordinary_prefix import load, relocated_module
from th04_demo_video import BLOCK_SIZE

ENTRIES = (('player-update', 0x0aaf, 0x5fcf),
           ('dialog-animate', 0x0aaf, 0x2bfb),
           ('dialog-run', 0x0aaf, 0x2a7c),
           ('dialog-return', 0x13a9, 0xae19))


def attest_checkpoint(label, ordinal, relative_segment, offset, row, data,
                      memory, video, module, load_segment, frame):
    require(len(data) == 65536 and len(memory) == 655360 and len(video) == BLOCK_SIZE,
            'post-Boss complete checkpoint extents')
    require(row['label'] == label and row['ordinal'] == ordinal and
            row['frame'] == row['requested_frame'] == frame,
            'post-Boss label/order/frame')
    cs, ds = load_segment + relative_segment, load_segment + 0x2134
    require((row['load_segment'], row['dgroup_segment'], row['cs'], row['ip']) ==
            (load_segment, ds, cs, offset) and row['unchanged_context'] is True,
            'post-Boss actual code/data ownership')
    registers, segments = bytes.fromhex(row['cpu_regs']), bytes.fromhex(row['segments'])
    require(len(registers) == 48 and len(segments) == 136, 'post-Boss CPU context extent')
    require((int.from_bytes(registers[32:36], 'little') & 65535,
             int.from_bytes(segments[8:16], 'little'),
             int.from_bytes(segments[24:32], 'little')) == (offset, cs, ds),
            'post-Boss raw CPU CS:IP/DS')
    require(row['watched_guest_linear'] == cs * 16 + offset,
            'post-Boss code-fetch address')
    require(sha(data) == row['dgroup_sha256'] and sha(video) == row['video_sha256'] and
            memory[ds * 16:ds * 16 + 65536] == data,
            'post-Boss DGROUP/video/conventional memory')
    require(int.from_bytes(data[0x538a:0x538c], 'little') == frame and
            row['key_det'] == int.from_bytes(data[0x3974:0x3976], 'little') and
            data[0x53d9] == 255, 'post-Boss frame/input/defeated phase')
    code = module[relative_segment * 16 + offset:relative_segment * 16 + offset + 16]
    require(len(code) == 16 and bytes.fromhex(row['opcode']) == code and
            memory[cs * 16 + offset:cs * 16 + offset + 16] == code,
            'post-Boss executing target bytes')
    ss = int.from_bytes(segments[16:24], 'little')
    sp = int.from_bytes(registers[16:20], 'little') & 65535
    stack = memory[ss * 16 + sp:ss * 16 + sp + 16]
    require(len(stack) == 16 and bytes.fromhex(row['stack']) == stack,
            'post-Boss actual stack bytes')
    if label in ('player-update', 'dialog-run'):
        return_ip = 0x00f4 if label == 'player-update' else 0x2c1f
        site = 0x0aaf * 16 + return_ip
        call = module[site - 3:site]
        require(int.from_bytes(stack[:2], 'little') == return_ip and call[0] == 0xe8 and
                (return_ip + int.from_bytes(call[1:], 'little', signed=True)) & 65535 == offset and
                memory[cs * 16 + return_ip - 3:cs * 16 + return_ip] == call,
                'post-Boss near caller')
    if label == 'dialog-animate':
        require(struct.unpack_from('<HH', stack) == (0xae19, load_segment + 0x13a9),
                'post-Boss far caller return')
        site = 0x13a9 * 16 + 0xae19
        call = module[site - 5:site]
        require(call == b'\x9a' + struct.pack('<HH', 0x2bfb, load_segment + 0x0aaf) and
                memory[(load_segment + 0x13a9) * 16 + 0xae14:
                       (load_segment + 0x13a9) * 16 + 0xae19] == call,
                'post-Boss actual far dialogue call')
        bp = int.from_bytes(registers[20:24], 'little') & 65535
        parent = memory[ss * 16 + bp:ss * 16 + bp + 4]
        require(len(parent) == 4 and int.from_bytes(parent[2:], 'little') == 0x63fb,
                'post-Boss Orange/default caller frame')
        outer_bp = int.from_bytes(parent[:2], 'little')
        outer = memory[ss * 16 + outer_bp:ss * 16 + outer_bp + 6]
        require(outer_bp > bp and len(outer) == 6 and
                struct.unpack_from('<HH', outer, 2) == (0x0109, load_segment + 0x0aaf),
                'post-Boss actual main-loop caller frame')
        require(module[0x0aaf * 16 + 0x0105:0x0aaf * 16 + 0x0109] == bytes.fromhex('ff1ed0bc') and
                struct.unpack_from('<HH', data, 0xbcd0) == (0x6013, load_segment + 0x13a9),
                'post-Boss far callback after the player call')
        common = module[0x13a9 * 16 + 0x63f8:0x13a9 * 16 + 0x63fb]
        require(common[0] == 0xe8 and
                (0x63fb + int.from_bytes(common[1:], 'little', signed=True)) & 65535 == 0xacb3 and
                memory[(load_segment + 0x13a9) * 16 + 0x63f8:
                       (load_segment + 0x13a9) * 16 + 0x63fb] == common,
                'post-Boss shared defeat caller')
    if label != 'player-update':
        require(row['dialog_return'] == [load_segment + 0x13a9, 0xae19],
                'post-Boss recorded return owner')
    return dict(label=label, frame=frame, cs=cs, ip=offset, input=row['key_det'],
                shift=data[0x3976], invincibility=data[0x4662], shot_time=data[0x4666],
                player_position=data[0x464e:0x4652].hex())


def attest_player_order(observations, loop_input):
    require(len(observations) == 4 and
            [row['label'] for row in observations] == [row[0] for row in ENTRIES],
            'post-Boss execution order')
    player, animate, running, returned = observations
    require(player['input'] == loop_input, 'post-Boss player owns the earlier loop sample')
    require(player['invincibility'] == 191 and player['shot_time'] == 13 and
            all(row['invincibility'] == 190 and row['shot_time'] == 12
                for row in (animate, running, returned)), 'post-Boss executed player prefix')
    require(player['input'] == animate['input'] == running['input'] == 0x20 and
            returned['input'] == 0x2000, 'post-Boss distinct player/dialogue input samples')
    return {str(player['frame']): [player['input'], player['shift']]}


def attest_capture(directory: Path, main: bytes) -> dict:
    require(sha(main) == MAIN_SHA256, 'post-Boss pinned original MAIN')
    capture = load(directory, main)
    receipt = capture['receipt']
    frame = receipt.get('post_boss_dialog_at_frame')
    require(receipt['role'] == 'original' and type(frame) is int and frame == 9348 and
            receipt['continue_at_frame'] < frame < receipt['end_after'] - 1,
            'post-Boss original capture/cue')
    sources = {name: digest for name, digest in receipt['source_files'].items()
               if Path(name).name in ('capture.py', 'th04_ordinary_keyboard-font.gdb', 'postboss_watch.py')}
    require(len(sources) == 3, 'post-Boss observer source closure')
    terminal = json.loads((directory / 'ordinary-terminal.json').read_text())
    load_segment = terminal['load_segment']
    module = relocated_module(main, load_segment)
    observations, files = [], {}
    for ordinal, (label, segment, offset) in enumerate(ENTRIES):
        paths = [directory / 'postboss-checkpoints' / (label + suffix) for suffix in
                 ('.json', '-dgroup.bin', '-memory.bin.gz', '-video.bin.gz')]
        row = json.loads(paths[0].read_text())
        observations.append(attest_checkpoint(label, ordinal, segment, offset, row,
            paths[1].read_bytes(), gzip.decompress(paths[2].read_bytes()),
            gzip.decompress(paths[3].read_bytes()), module, load_segment, frame))
        files.update({str(path.relative_to(directory)): sha(path.read_bytes()) for path in paths})
        require(all(str(path.relative_to(directory)) in receipt['files'] and
                    files[str(path.relative_to(directory))] == receipt['files'][str(path.relative_to(directory))]
                    for path in paths), 'post-Boss receipt/checkpoint binding')
    player_inputs = attest_player_order(observations,
        int.from_bytes(bytes.fromhex(capture['rows'][frame]['input']), 'little'))
    return dict(passed=True, capture=str(directory.resolve()), frame=frame,
        capture_receipt_sha256=sha((directory / 'receipt.json').read_bytes()), target_sha256=MAIN_SHA256,
        reader_source_sha256=sha(Path(__file__).read_bytes()), observer_sources=sources,
        observations=observations, files=files,
        player_inputs=player_inputs,
        scope='Original Normal/ReimuA frame9348 player prefix precedes Boss departure dialogue. '
              'Actual code, raw CPU/stack, conventional/DGROUP memory and callback ownership bind Shot20h '
              'to player and later Enter2000h to dialogue return. No prefix rerun or gameplay input latch. '
              'This fixture does not accept whole pictures, all globals, physical timing, campaigns or exactness.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('capture', 'main', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    result = attest_capture(args.capture.resolve(), args.main.read_bytes())
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(passed=True, player_inputs=result['player_inputs'])))


if __name__ == '__main__':
    main()
