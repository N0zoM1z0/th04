#!/usr/bin/env python3
"""Attest original pre-Boss instruction-fetch checkpoints and player input.

The ordinary loop sample precedes STD's blocking dialogue. It is a different
input boundary from the later player_update entry. This reader keeps both.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from compare_th04_dos_ordinary_prefix import load, relocated_module
from th04_demo_video import BLOCK_SIZE

MAIN_SHA256 = '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
ENTRIES = (('std-transition', 0x2454, 0x00ce, 'indirect'),
           ('dialog-animate', 0x2bfb, 0x2485, 'far'),
           ('dialog-run', 0x2a7c, 0x2c1f, 'near'),
           ('player-update', 0x5fcf, 0x00f4, 'near'))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(value, message):
    if not value:
        raise ValueError(message)

def attest_entry(label, offset, return_ip, kind, row, data, memory, video, module, load_segment, frame, fields):
    require(row['label'] == label and row['frame'] == frame, 'dialogue checkpoint label/frame')
    require(len(data) == 65536 and len(memory) == 655360 and len(video) == BLOCK_SIZE,
            'dialogue complete checkpoint extents')
    require(row['dgroup_sha256'] == sha(data) and row['video_sha256'] == sha(video), 'dialogue checkpoint digests')
    cs, ds = load_segment + 0xaaf, load_segment + 0x2134
    require(row['load_segment'] == load_segment and row['dgroup_segment'] == ds and
            row['cs'] == cs and row['ip'] == offset and row['unchanged_context'] is True,
            'dialogue checkpoint segment/PC ownership')
    registers, segments = bytes.fromhex(row['cpu_regs']), bytes.fromhex(row['segments'])
    require(len(registers) == 48 and len(segments) == 136, 'dialogue CPU context extent')
    require(int.from_bytes(registers[32:36], 'little') & 65535 == offset and
            int.from_bytes(segments[8:16], 'little') == cs and
            int.from_bytes(segments[24:32], 'little') == ds, 'dialogue actual CPU context')
    require(memory[ds*16:ds*16+65536] == data, 'dialogue conventional/DGROUP agreement')
    code = module[0xaaf*16+offset:0xaaf*16+offset+16]
    require(bytes.fromhex(row['opcode']) == code and memory[cs*16+offset:cs*16+offset+16] == code,
            'dialogue actual owned target opcode')
    ss, sp = int.from_bytes(segments[16:24], 'little'), int.from_bytes(registers[16:20], 'little') & 65535
    stack = memory[ss*16+sp:ss*16+sp+4]
    require(len(stack) == 4 and int.from_bytes(stack[:2], 'little') == return_ip, 'dialogue target caller return')
    site = 0xaaf*16 + return_ip
    if kind == 'indirect':
        require(module[site-4:site] == bytes.fromhex('ff168a42') and
                int.from_bytes(data[0x428a:0x428c], 'little') == offset, 'dialogue STD callback owner')
    else:
        call = module[site-3:site]
        require(len(call) == 3 and call[0] == 0xe8 and
                (return_ip + int.from_bytes(call[1:], 'little', signed=True)) & 65535 == offset,
                'dialogue direct target call')
        if kind == 'far':
            require(module[site-4] == 0x0e and int.from_bytes(stack[2:], 'little') == cs,
                    'dialogue far caller segment')
    values = {name: data[at:at+size].hex() for name, at, size in fields}
    require(int.from_bytes(bytes.fromhex(values['frame']), 'little') == frame and
            row['key_det'] == int.from_bytes(bytes.fromhex(values['input']), 'little'), 'dialogue observed input/frame')
    return dict(label=label, frame=frame, cs=cs, ip=offset, caller_return=return_ip,
                input=int.from_bytes(bytes.fromhex(values['input']), 'little'),
                shift=int(values['shift_raw'], 16), values=values)

def attest_capture(directory: Path, main: bytes, source_profile: Path) -> dict:
    require(sha(main) == MAIN_SHA256, 'dialogue pinned original MAIN')
    capture = load(directory, main)
    receipt = capture['receipt']
    require(receipt['role'] == 'original' and type(receipt.get('dialog_at_frame')) is int,
            'dialogue original capture/cue')
    sources = json.loads(source_profile.read_text())
    require(isinstance(sources, dict) and len(sources) >= 4, 'dialogue observer source closure')
    for name, digest in sources.items():
        require(sha(Path(name).read_bytes()) == digest, 'dialogue observer source identity: ' + name)
    require(receipt['adapter_sha256'] in sources.values() and
            any(name.endswith('dialog_watch.py') or name.endswith('th04_dialog_checkpoints_gdb.py') for name in sources),
            'dialogue observer/adapter binding')
    fields = json.loads((directory/'profile.json').read_text())['fields']
    terminal = json.loads((directory/'ordinary-terminal.json').read_text())
    load_segment, frame = terminal['load_segment'], receipt['dialog_at_frame']
    module = relocated_module(main, load_segment)
    rows, files = [], {}
    for label, offset, return_ip, kind in ENTRIES:
        folder = directory/'dialog-checkpoints'
        paths = [folder/(label+suffix) for suffix in ('.json','-dgroup.bin','-memory.bin.gz','-video.bin.gz')]
        row = json.loads(paths[0].read_text())
        rows.append(attest_entry(label, offset, return_ip, kind, row, paths[1].read_bytes(),
            gzip.decompress(paths[2].read_bytes()), gzip.decompress(paths[3].read_bytes()), module, load_segment, frame, fields))
        files.update({str(path.relative_to(directory)): sha(path.read_bytes()) for path in paths})
    require(rows[0]['values']['input'] == capture['rows'][frame]['input'], 'dialogue actual outer-loop sample')
    player = rows[-1]
    return dict(passed=True, capture=str(directory.resolve()), capture_receipt_sha256=sha((directory/'receipt.json').read_bytes()),
        target_sha256=MAIN_SHA256, reader_source_sha256=sha(Path(__file__).read_bytes()), source_profile_sha256=sha(source_profile.read_bytes()), source_files=sources,
        observations=rows, files=files, player_inputs={str(frame): [player['input'], player['shift']]},
        scope='Original instruction-fetch/caller/memory checkpoints. STD dialogue precedes player_update; loop and player inputs are separate. No complete picture, process, timing or exact promotion.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('capture','main','source-profile','output'):
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args()
    result = attest_capture(args.capture.resolve(), args.main.read_bytes(), args.source_profile.resolve())
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(passed=result['passed'], player_inputs=result['player_inputs'])))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
