#!/usr/bin/env python3
"""Compare a bounded native ordinary MAIN component with original DOS.

The caller supplies the recorded seed/options/assets and actual consumed inputs.
This does not accept natural native OP timing, other globals, pictures, blocking
scene timing, complete process routes, or historical executable bytes.
--frontend drives the real dialogue owner with separately declared release/Enter
controls and checks actual gameplay input; --updates names the bounded extent.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import islice
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from verify import require_elf_x86_64, source_manifest
from verify_demo_state import TARGET_SHA256, little, require, sha
from verify_demo_pools import compare_demo

UPDATES = 3996
FIELDS = ('frame', 'input', 'shift_raw', 'stage', 'score_digits', 'score_delta',
          'score_delta_frame', 'lcg', 'ring', 'ring_cursor', 'player_pos', 'power',
          'hit', 'invincibility', 'respawn', 'lives', 'bombs', 'misses', 'bombs_used',
          'lcg_calls', 'ring_calls')


def parse_native(raw: bytes, updates: int = UPDATES) -> list[dict]:
    require(0 < updates <= 65535, 'ordinary configured extent')
    lines = raw.decode('ascii').splitlines()
    require(len(lines) == updates + 2 and
            lines[0] == f'TH04_ORDINARY_STATE 1 {updates}', 'ordinary trace extent/header')
    result = []
    previous = (0, 0)
    for frame, line in enumerate(lines[1:]):
        c = line.split()
        require(len(c) == 23 and int(c[0]) == frame, 'ordinary scalar field/frame order')
        require(c[1] == ('P' if frame == updates else 'I'), 'ordinary prefix decision')
        require(len(c[5]) == 16 and len(c[9]) == 512 and
                bytes.fromhex(c[5]).hex() == c[5] and
                bytes.fromhex(c[9]).hex() == c[9], 'ordinary byte-field extent')
        counts = int(c[21]), int(c[22])
        require((frame != 0 or counts == (0, 0)) and
                all(old <= new < 2**64 for old, new in zip(previous, counts)),
                'ordinary post-initialization RNG counts')
        previous = counts
        row = dict(frame=little(c[0], 2), input=little(c[2], 2), shift_raw=little(c[3], 1),
                   stage=little(c[4], 1), score_digits=c[5], score_delta=little(c[6], 4),
                   score_delta_frame=little(c[7], 4), lcg=little(c[8], 4), ring=c[9],
                   ring_cursor=little(c[10], 2),
                   player_pos=little(c[11], 2, True) + little(c[12], 2, True),
                   power=little(c[13], 1), hit=little(c[14], 1),
                   invincibility=little(c[15], 1), respawn=little(c[16], 1),
                   lives=int(c[17]), bombs=int(c[18]), misses=int(c[19]),
                   bombs_used=int(c[20]), lcg_calls=counts[0], ring_calls=counts[1])
        require(all(0 <= row[k] <= 255 for k in ('lives', 'bombs', 'misses', 'bombs_used')),
                'ordinary resident byte width')
        result.append(row)
    return result


def compare_scalar(capture: dict, profile: dict, native: list[dict]) -> dict:
    require(len(native) > 1 and len(capture['rows']) >= len(native),
            'ordinary paired boundary extent')
    counts = Counter()
    differences = []
    for frame, row in enumerate(native):
        resident = bytes.fromhex(capture['resident'][frame])
        require(len(resident) >= 74 and resident[:11] == b'HUMAConfig\0',
                'ordinary resident identity/extent')
        if frame == 0:
            require(resident[48:51] == bytes((0x37, 0, 0)),
                    'ordinary initial run/miss/Bomb layout')
        if frame:
            for index, _ in capture['events'][frame]:
                kind = profile['hooks'][index][0]
                require(kind in (3, 4), 'ordinary RNG event owner')
                counts['lcg_calls' if kind == 3 else 'ring_calls'] += 1
        original = capture['rows'][frame] | dict(lives=resident[11], bombs=resident[13],
            misses=resident[49], bombs_used=resident[50],
            lcg_calls=counts['lcg_calls'], ring_calls=counts['ring_calls'])
        changed = {k: dict(original=original[k], native=row[k]) for k in FIELDS
                   if original[k] != row[k]}
        if changed:
            differences.append(dict(frame=frame, fields=changed))
    return dict(passed=not differences, fields=list(FIELDS), boundaries=len(native),
                differing_boundaries=len(differences), differences=differences)


def compare_consumed(capture: dict, raw: bytes, updates: int, player_inputs: dict | None = None) -> dict:
    lines = raw.decode('ascii').splitlines()
    require(len(lines) == updates, 'ordinary consumed input extent')
    differences = []
    for frame, line in enumerate(lines):
        columns = line.split()
        require(len(columns) == 3 and int(columns[0]) == frame, 'ordinary consumed input frame order')
        _, keys, shift = map(int, columns)
        require(0 <= keys <= 65535 and shift in (0, 1), 'ordinary consumed input width')
        original = capture['rows'][frame]
        expected = (int.from_bytes(bytes.fromhex(original['input']), 'little'), int(original['shift_raw'], 16))
        if player_inputs is not None and str(frame) in player_inputs:
            expected = tuple(player_inputs[str(frame)])
        if (keys, shift) != expected:
            differences.append(dict(frame=frame, original=list(expected), native=[keys, shift]))
    return dict(passed=not differences, updates=updates, differences=differences)


def compare_owners(capture: dict, raw: bytes, updates: int) -> dict:
    fields = (('boss', 24), ('boss_statebyte', 16), ('boss_hitbox_radius', 4), ('boss_phase_timed_out', 1))
    lines = raw.decode('ascii').splitlines()
    require(len(lines) == updates + 1, 'ordinary Boss owner extent')
    differences = []
    for frame, line in enumerate(lines):
        columns = line.split()
        require(len(columns) == 2 and int(columns[0]) == frame, 'ordinary Boss owner frame order')
        data = bytes.fromhex(columns[1])
        require(len(data) == 45 and data.hex() == columns[1], 'ordinary Boss owner wire extent')
        cursor = 0
        changed = {}
        for name, size in fields:
            native = data[cursor:cursor + size].hex()
            original = capture['rows'][frame][name]
            if native != original:
                changed[name] = dict(original=original, native=native)
            cursor += size
        if changed:
            differences.append(dict(frame=frame, fields=changed))
    return dict(passed=not differences, fields=[name for name, _ in fields], boundaries=len(lines),
                differing_boundaries=len(differences), differences=differences)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('dos-root', 'original', 'exe', 'output-dir'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--updates', type=int, default=UPDATES)
    parser.add_argument('--frontend', action='store_true')
    parser.add_argument('--dialog-observer-profile', type=Path)
    args = parser.parse_args()
    require(0 < args.updates <= 65535, 'ordinary requested extent')
    root = Path(__file__).resolve().parents[1]
    dos = args.dos_root.resolve()
    sys.path.insert(0, str(dos / 'scripts/probes'))
    from compare_th04_dos_ordinary_prefix import load
    from compare_th04_dos_process_route import game_file
    from capture_th04_dos_demos import ARCHIVES, parse_archive
    from compare_th04_demo_dgroup import attest_clear_calls
    from th04_ordinary_dgroup import records

    original = args.original.resolve()
    target = (dos / '.analysis/targets/th04/main.exe').read_bytes()
    require(sha(target) == TARGET_SHA256, 'ordinary pinned target')
    capture = load(original, target)
    require(capture['receipt']['role'] == 'original' and
            len(capture['rows']) > args.updates, 'ordinary original capture extent/role')
    owner = target[6144 + 0x11ecb:6144 + 0x11f96]
    require(sha(owner) == 'f41ff21e0254ae8050f35b00c514db046b74b4ae2b02538dd7856715a15dfed7',
            'ordinary pool-clear owner')
    attest_clear_calls(owner, 0x73db, 0x185e,
                       [0xb55e, 0x8a92, 0x53e2, 0x5a22, 0xb204, 0x9594, 0xaf34, 0x9634, 0x9292])
    manifest, sources = source_manifest(root)
    require_elf_x86_64(args.exe)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    inputs = output / 'inputs'
    (inputs / 'save').mkdir(parents=True)
    for fat, name in (('MIKO    CFG', 'MIKO.CFG'), ('GENSOU  SCR', 'save/GENSOU.SCR')):
        (inputs / name).write_bytes(bytes.fromhex(capture['starting_files'][fat]))
    image = (original / 'prepared/diagnostic.hdi').read_bytes()
    _, assets = parse_archive(game_file(image, ARCHIVES['main']['fat_name']), 'main', ARCHIVES['main'])
    for name in ('ST00.STD', 'ST00.MAP'):
        (inputs / name).write_bytes(assets[name])
    resident = bytes.fromhex(capture['resident'][0])
    require(resident[17] == 0 and resident[18] in b'01' and resident[25] < 2,
            'ordinary stage/character/shot start')
    seed = int.from_bytes(resident[20:24], 'little')
    plan = [f'{seed} {args.updates} {resident[18] - 48} {resident[25]}']
    for frame, row in enumerate(capture['rows'][:args.updates + 1]):
        require(int.from_bytes(bytes.fromhex(row['frame']), 'little') == frame,
                'ordinary original input frame order')
        plan.append(f'{frame} {int.from_bytes(bytes.fromhex(row["input"]), "little")} '
                    f'{int(row["shift_raw"], 16)}')
    (inputs / 'inputs.txt').write_text('\n'.join(plan) + '\n')
    raw_path = output / 'pools.bin'
    command = [str(args.exe.resolve()), str(inputs), str(raw_path)]
    if args.frontend:
        font = original / 'FREECG98.BMP'
        require(sha(font.read_bytes()) == capture['receipt']['font_sha256'], 'ordinary font identity')
        (inputs/'save/MIKO.CFG').write_bytes((inputs/'MIKO.CFG').read_bytes())
        (inputs/'save/ordinary-inputs.txt').write_bytes((inputs/'inputs.txt').read_bytes())
        frontend = output/'frontend'
        raw_path = frontend/'pools.bin'
        command = [str(args.exe.resolve()), '--hdi', str(original/'prepared/diagnostic.hdi'),
                   '--font-bmp', str(font), '--save-dir', str(inputs/'save'),
                   '--ordinary-trace-checks', str(frontend), '--mute']
    starting_inputs = {str(p.relative_to(inputs)): sha(p.read_bytes()) for p in inputs.rglob("*") if p.is_file()}
    run = subprocess.run(command, capture_output=True, timeout=120,
                         env=dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'))
    (output / 'stdout.txt').write_bytes(run.stdout)
    (output / 'stderr.txt').write_bytes(run.stderr)
    run.check_returncode()
    state_raw = (frontend/'state.txt').read_bytes() if args.frontend else run.stdout
    (output / 'state.txt').write_bytes(state_raw)
    witness = None
    if args.frontend:
        blocked_frames = set()
        for line in (frontend/'blocks.txt').read_text().splitlines():
            columns = line.split()
            require(len(columns) == 6, 'ordinary blocking input record width')
            frame = int(columns[0])
            require(0 <= frame < args.updates, 'ordinary blocking frame extent')
            blocked_frames.add(frame)
        if blocked_frames:
            from attest_th04_dialog_checkpoints import attest_capture
            profile_path = args.dialog_observer_profile or original/'dialog-checkpoint-sources.json'
            require(profile_path.is_file(), 'blocking dialogue requires original player-entry evidence')
            witness = attest_capture(original, target, profile_path.resolve())
            require(blocked_frames == {int(k) for k in witness['player_inputs']},
                    'ordinary blocking/player-entry evidence coverage')
            (output/'player-input-witness.json').write_text(json.dumps(witness, indent=2)+'\n')
    player_inputs = dict(witness['player_inputs']) if witness else {}
    continue_witness = None
    continue_blocks = dict(passed=True, frames=[], rows=0)
    if args.frontend:
        go_path = frontend/'gameover-blocks.txt'
        go_rows = [list(map(int, line.split())) for line in go_path.read_text().splitlines()] if go_path.is_file() else []
        require(all(len(row) == 11 for row in go_rows), 'ordinary Game Over record width')
        go_frames = {row[0] for row in go_rows}
        cue = capture['receipt'].get('continue_at_frame', 0)
        require(go_frames == ({cue} if 0 < cue < args.updates else set()),
                'ordinary Continue capture/trace coverage')
        if go_frames:
            from attest_th04_continue_checkpoints import attest_capture as attest_continue
            continue_witness = attest_continue(original, target)
            require(go_frames == {int(k) for k in continue_witness['player_inputs']} and
                    not go_frames.intersection(map(int, player_inputs)), 'ordinary Continue player witness coverage')
            for index, row in enumerate(go_rows):
                frame, attempt, before, after, host, completed, polled, consumed_key, lives, misses, credit = row
                require(frame == cue and attempt == index and
                        consumed_key == continue_witness['player_inputs'][str(frame)][0],
                        'ordinary suspended player sample/order')
                require(completed == frame + (index == len(go_rows)-1), 'ordinary Game Over frame freeze/resume')
            require(go_rows[0][2] == -1 and go_rows[-1][3] == -1 and len(go_rows) > 1 and
                    go_rows[-1][-1] == 1, 'ordinary Game Over actual entry/Continue return')
            player_inputs.update(continue_witness['player_inputs'])
            continue_blocks = dict(passed=True, frames=sorted(go_frames), rows=len(go_rows),
                                   policy='Actual player-prefix sample is retained while release/Enter UI polls resume its suffix.')
            (output/'continue-input-witness.json').write_text(json.dumps(continue_witness, indent=2)+'\n')
    consumed = compare_consumed(capture, (frontend/'consumed.txt').read_bytes(), args.updates,
        player_inputs) if args.frontend else dict(passed=True, adapter='direct update arguments')
    physical_files = dict(passed=True, scope='not configured')
    if continue_witness:
        from compare_th04_dos_process_route import decode_score_sections
        image = (original/'execution.hdi').read_bytes()
        files = {}
        for fat, name in ((b'MIKO    CFG', 'MIKO.CFG'), (b'GENSOU  SCR', 'GENSOU.SCR')):
            a, b = game_file(image, fat), (inputs/'save'/name).read_bytes()
            initial = bytes.fromhex(capture['starting_files'][fat.decode()])
            row = dict(passed=a == b, original_sha256=sha(a), native_sha256=sha(b),
                       initial_sha256=sha(initial), original_changed=a != initial, native_changed=b != initial)
            if name == 'GENSOU.SCR':
                decoded_a, decoded_b = decode_score_sections(a), decode_score_sections(b)
                decoded_initial = decode_score_sections(initial)
                row.update(decoded_equal=decoded_a == decoded_b, checksum_bits=16,
                           sections=len(decoded_a), changed_decoded_sections=[i for i in range(10) if decoded_a[i] != decoded_initial[i]])
            files[name] = row
        physical_files = dict(passed=all(row['passed'] for row in files.values()), files=files,
                              scope='Complete bounded CFG/SCR bytes, decoded score sections and checksums; the recorded configured Turbo Continue writes its ranked entry before resetting the live score.')
    owners = compare_owners(capture, (frontend/'owners.txt').read_bytes(), args.updates) if args.frontend else dict(passed=True, scope='not configured')
    profile = json.loads((original / 'profile.json').read_text())
    scalar = compare_scalar(capture, profile, parse_native(state_raw, args.updates))
    terminal = json.loads((original / 'ordinary-terminal.json').read_text())
    iterator = records(original / 'ordinary-dgroup.bin.gz', terminal['load_segment'],
        terminal['dgroup_segment'], profile['fields'], terminal['cr0'], terminal['cr3'],
        terminal['frame'])
    with raw_path.open('rb') as stream:
        require(stream.read(8) == b'TH04OP1\n', 'ordinary pool protocol')
        pools = compare_demo(islice(iterator, args.updates), stream, 0, args.updates)
        require(stream.read(1) == b'', 'ordinary pool trailing bytes')
    for _ in iterator:
        pass  # Finish the complete original stream, including CRC/metadata checks.
    raw_hash = hashlib.sha256()
    packed = output / 'pools.bin.gz'
    with raw_path.open('rb') as src, packed.open('xb') as dst:
        with gzip.GzipFile(filename='', fileobj=dst, mode='wb', mtime=0) as archive:
            while chunk := src.read(1024 * 1024):
                raw_hash.update(chunk)
                archive.write(chunk)
    restored_hash = hashlib.sha256()
    with gzip.open(packed, 'rb') as archive:
        while chunk := archive.read(1024 * 1024):
            restored_hash.update(chunk)
    require(restored_hash.digest() == raw_hash.digest(), 'ordinary pool retention readback')
    raw_path.unlink()
    require(source_manifest(root)[0] == manifest, 'ordinary native source drift')
    report = dict(passed=scalar['passed'] and pools['passed'] and consumed['passed'] and owners['passed'] and physical_files['passed'], accepts_exact=False,
        natural_game_exit=False, updates=args.updates, scalar=scalar, actor_pools=pools,
        command=command, frontend=args.frontend, consumed_input=consumed,
        player_input_boundary=[w['scope'] for w in (witness, continue_witness) if w],
        continue_blocks=continue_blocks, physical_files=physical_files, starting_inputs=starting_inputs, boss_owners=owners, source_manifest_sha256=manifest, source_files=sources,
        executable_sha256=sha(args.exe.read_bytes()), original_receipt_sha256=sha((original/'receipt.json').read_bytes()),
        input_files={str(p.relative_to(inputs)):sha(p.read_bytes()) for p in inputs.rglob('*') if p.is_file()},
        pools_raw_sha256=raw_hash.hexdigest(), pools_gzip_sha256=sha(packed.read_bytes()),
        scope=__doc__)
    (output / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=report['passed'], scalar=scalar['passed'], pools=pools['passed'])))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
