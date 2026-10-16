#!/usr/bin/env python3
"""Attest original player/Game Over/Continue instruction-fetch checkpoints."""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
from attest_th04_dialog_checkpoints import MAIN_SHA256, sha, require
from compare_th04_dos_ordinary_prefix import load, relocated_module
from th04_demo_video import BLOCK_SIZE

ENTRIES = (('player-entry', 0x5fcf), ('gameover-entry', 0x3a51),
           ('credit-applied', 0x3cde), ('gameover-return', 0x5fca),
           ('player-return', 0x00f4))

def attest_capture(directory: Path, main: bytes) -> dict:
    require(sha(main) == MAIN_SHA256, 'Continue pinned original MAIN')
    capture = load(directory, main)
    receipt = capture['receipt']
    frame = receipt.get('continue_at_frame')
    require(receipt['role'] == 'original' and type(frame) is int and frame > 0,
            'Continue original capture/cue')
    sources = receipt['source_files']
    require(any(name.endswith('continue_watch.py') for name in sources), 'Continue observer source closure')
    for name, digest in sources.items():
        require(sha(Path(name).read_bytes()) == digest, 'Continue source identity: ' + name)
    terminal = json.loads((directory/'ordinary-terminal.json').read_text())
    load_segment = terminal['load_segment']
    cs, ds = load_segment + 0xaaf, load_segment + 0x2134
    module = relocated_module(main, load_segment)
    rows, files = [], {}
    for ordinal, (label, offset) in enumerate(ENTRIES):
        folder = directory/'continue-checkpoints'
        paths = [folder/(label+suffix) for suffix in ('.json','-dgroup.bin','-memory.bin.gz','-video.bin.gz')]
        row = json.loads(paths[0].read_text())
        data, memory, video = paths[1].read_bytes(), gzip.decompress(paths[2].read_bytes()), gzip.decompress(paths[3].read_bytes())
        require(len(data) == 65536 and len(memory) == 655360 and len(video) == BLOCK_SIZE,
                'Continue complete checkpoint extents')
        require(row['ordinal'] == ordinal and row['label'] == label and row['frame'] == frame and
                row['load_segment'] == load_segment and row['dgroup_segment'] == ds and
                row['cs'] == cs and row['ip'] == offset and row['unchanged_context'] is True,
                'Continue checkpoint order/frame/segment/PC')
        registers, segments = bytes.fromhex(row['cpu_regs']), bytes.fromhex(row['segments'])
        require(len(registers) == 48 and len(segments) == 136 and
                int.from_bytes(registers[32:36], 'little') & 65535 == offset and
                int.from_bytes(segments[8:16], 'little') == cs and
                int.from_bytes(segments[24:32], 'little') == ds, 'Continue actual CPU context')
        require(memory[ds*16:ds*16+65536] == data and sha(data) == row['dgroup_sha256'] and
                sha(video) == row['video_sha256'], 'Continue memory/digests')
        site = 0xaaf*16+offset
        code = module[site:site+16]
        require(code == bytes.fromhex(row['opcode']) == memory[cs*16+offset:cs*16+offset+16],
                'Continue owned original instruction bytes')
        ss = int.from_bytes(segments[16:24], 'little')
        sp, bp = (int.from_bytes(registers[a:a+4], 'little') & 65535 for a in (16,20))
        word = lambda at: int.from_bytes(memory[ss*16+at:ss*16+at+2], 'little')
        if ordinal < 2:
            return_ip = (0x00f4, 0x5fca)[ordinal]
            require(word(sp) == return_ip, 'Continue entry caller stack')
            call = module[0xaaf*16+return_ip-3:0xaaf*16+return_ip]
            require(call[0] == 0xe8 and (return_ip+int.from_bytes(call[1:], 'little', signed=True)) & 65535 == offset,
                    'Continue entry direct target caller')
        elif ordinal == 2:
            require(word(bp+2) == 0x3b24 and module[site-4:site] == bytes.fromhex('fe064943'),
                    'Continue menu caller and actual increment')
        elif ordinal == 3:
            require(word(bp+2) == 0x610a and module[site-3:site] == bytes.fromhex('e887da'),
                    'Continue miss-helper frame and Game Over return')
        else:
            require(module[site-3:site] == bytes.fromhex('e8db5e'), 'Continue final player return call')
        key = int.from_bytes(data[0x3974:0x3976], 'little')
        require(int.from_bytes(data[0x538a:0x538c], 'little') == frame and key == row['key_det'],
                'Continue observed frame/input')
        rows.append(dict(label=label, frame=frame, cs=cs, ip=offset, input=key,
                         shift=data[0x3976], score_digits=data[0x4349:0x4351].hex(),
                         player_pos=data[0x464e:0x4652].hex(), shot_time=data[0x4666]))
        files.update({str(p.relative_to(directory)): sha(p.read_bytes()) for p in paths})
    require(rows[0]['input'] == int.from_bytes(bytes.fromhex(capture['rows'][frame]['input']), 'little'),
            'Continue outer-loop/player input agreement')
    require([bytes.fromhex(r['score_digits'])[0] for r in rows] == [0,0,1,1,1],
            'Continue actual score alias increment')
    return dict(passed=True, target_sha256=MAIN_SHA256, capture_receipt_sha256=sha((directory/'receipt.json').read_bytes()),
                reader_source_sha256=sha(Path(__file__).read_bytes()), source_files=sources, files=files,
                observations=rows, player_inputs={str(frame): [rows[0]['input'], rows[0]['shift']]},
                scope='Original code-fetch, caller, complete conventional memory and raw video observations. Player input is consumed before Game Over; later menu input belongs to the resumed suffix. No picture, UI timing, full route or exact acceptance.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('capture','main','output'):
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args()
    result = attest_capture(args.capture.resolve(), args.main.read_bytes())
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(passed=True, player_inputs=result['player_inputs'])))

if __name__ == '__main__':
    main()
