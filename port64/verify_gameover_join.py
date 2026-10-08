#!/usr/bin/env python3
"""Live native Game Over clocks, frozen display, keyboard and Continue writes.

Actual OP selection and authored finite STD enemy contact drive ordinary MAIN.
Original Game Over/menu/fades execute at two loads with the captured starting
state and held input. Original TRAM and score-HUD stores then consume the
independently compared request stream. The last completed native indexed
display, palette, initial TRAM and CGROM are explicit graphics/input adapters;
this does not prove the original interrupted MAIN frame's physical display.
Life/bomb HUD, audio and DOS ranking I/O remain request adapters. Native host
writes are checked separately, including reopen and failure before reset.
Quit ends at the pending score-only MAINE owner, not a complete ordinary route.
"""

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import unicorn

from probe_assets import main_assets
from verify import source_manifest
from verify_gameover_render import Original as TextOriginal, SIZE, EXTENTS
from verify_gameover_scene import Original as SceneOriginal
from verify_player_bomb_pixels import read_exact


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_hashes(directory):
    return {p.relative_to(directory).as_posix(): sha(p.read_bytes())
            for p in sorted(directory.rglob('*')) if p.is_file()}


class Scene(SceneOriginal):
    def event(self, kind, *args, **kwargs):
        super().event(kind, *args, **kwargs)
        if kind == 11:
            self.hud.append((bytes(self.u.mem_read(0x84349, 8)),
                             bytes(self.u.mem_read(0x84351, 8))))

    def replay(self, values, keys):
        self.hud = []
        events = self.run_scene(values, keys)
        return events, list(self.hud)


class Graphics(TextOriginal):
    def body(self, u, address, size, unused):
        cs = u.reg_read(unicorn.x86_const.UC_X86_REG_CS)
        if cs - self.load == 0xaaf and 0x6ba2 <= address - cs * 16 < 0x6bd4:
            return  # Actual score_render, including its near return.
        super().body(u, address, size, unused)

    def seed_display(self, directory):
        self.reset()
        self.write(0x768, 'H', 0xa000)
        raw = (directory / 'initial.tram').read_bytes()
        assert len(raw) == 8000
        self.u.mem_write(0xa0000, raw[:4000])
        self.u.mem_write(0xa2000, raw[4000:])
        self.indices = np.frombuffer((directory / 'initial.indices').read_bytes(),
                                     dtype=np.uint8).reshape(400, 640)
        self.palette = np.frombuffer((directory / 'initial.pal').read_bytes(),
                                     dtype=np.uint8).reshape(16, 3)

    def score_hud(self, digits, hiscore):
        self.u.mem_write(0x84349, digits)
        self.u.mem_write(0x84351, hiscore)
        assert bytes(self.u.mem_read(0x81ece, 1)) == b'\0'  # Original initialized terminator.
        self.call(0xaaf, 0x6ba2)


def compare_rows(native, original, scene, out):
    for row, (x, y) in enumerate(itertools.zip_longest(native, original)):
        if x != y:
            (out / 'mismatch.json').write_text(json.dumps(
                dict(scene=scene, row=row, native=x, original=y), indent=2) + '\n')
            raise ValueError(f'Game Over {scene}: request/state row {row} differs')


def run_native(executable, hdi, font, out):
    command = [str(executable.resolve()), '--hdi', str(hdi.resolve()),
               '--font-bmp', str(font.resolve()), '--mute',
               '--gameover-checks', str(out / 'scenes')]
    digest = hashlib.sha256()
    size = 0
    with (out / 'native-stderr.txt').open('wb') as errors:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors)
        try:
            with gzip.open(out / 'native.gz', 'wb', compresslevel=6) as stream:
                while True:
                    block = process.stdout.read(1024 * 1024)
                    if not block:
                        break
                    size += len(block)
                    digest.update(block)
                    stream.write(block)
            assert process.wait(timeout=120) == 0, 'native frontend fixture failed'
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
    return command, digest.hexdigest(), size


def original_controls(target, font, gaiji, scenes, out, expected_records):
    names = sorted(p.parent.name for p in scenes.glob('*/initial.txt'))
    assert len(names) == 20, f'expected twenty real last-life scenes, got {len(names)}'
    slots = []
    for line in (scenes / 'snapshots.txt').read_text().splitlines():
        name, clock, tone = line.split()
        slots.append((name, int(clock), int(tone)))
    assert len(slots) == expected_records
    results = []
    first_trace = None
    first_states = None
    for load in (0x1000, 0x2000):
        scene = Scene(target, load)
        graphics = Graphics(target, load, font, gaiji)
        wanted = {}
        states = []
        for name in names:
            directory = scenes / name
            values = list(map(int, (directory / 'initial.txt').read_text().split()))
            keys = list(map(int, (directory / 'keys.txt').read_text().split()))
            actual = (directory / 'events.txt').read_text().splitlines()
            end = (directory / 'end.txt').read_text().strip()
            failed = end.startswith('FAILED ')
            # Host failure is outside the original score-I/O adapter. Run its
            # successful original continuation, compare the complete native
            # request prefix through the real attempted save, and independently
            # retain native fail-before-reset assertions in the frontend fixture.
            complete_keys = keys + [0] * (650 - len(keys))
            reference, hud = scene.replay(values, complete_keys)
            if failed:
                assert end == 'FAILED 114' and actual[-1].split()[1] == '7'
                compare_rows(actual, reference[1:1 + len(actual)], name, out)
            else:
                compare_rows(['BEGIN', *actual, end], reference, name, out)
            states.append(dict(scene=name, failed_writer=failed,
                               events=len(actual), trace_sha256=sha('\n'.join(reference).encode())))
            graphics.seed_display(directory)
            events = iter(actual)
            current = next(events, None)
            hud = iter(hud)
            tone = 100
            for slot_name, clock, native_tone in (s for s in slots if s[0] == name):
                while current is not None and int(current.split()[0]) <= clock:
                    words = current.split()
                    _, kind, x, y, value, attr = map(int, words[:6])
                    if kind in (0, 1):
                        graphics.command(f'{"G" if kind == 0 else "A"} {x} {y} {value} {attr} {words[6]}')
                    elif kind in (2, 3):
                        graphics.command('W' if kind == 2 else 'B')
                    elif kind == 4:
                        tone = value
                    elif kind == 11:
                        graphics.score_hud(*next(hud))
                    current = next(events, None)
                assert tone == native_tone, f'{name} clock{clock}: palette clock differs'
                wire = graphics.capture(tone)
                wanted[(slot_name, clock)] = wire
            if len(states) % 4 == 0:
                print(f'load{load:04x}: {len(states)} original scenes replayed', flush=True)
        records = []
        with gzip.open(out / 'original.gz', 'wb', compresslevel=6) if load == 0x1000 else gzip.open(out / 'original.gz', 'rb') as stream:
            with gzip.open(out / 'native.gz', 'rb') as native:
                for index, slot in enumerate(slots):
                    wire = wanted[slot[:2]]
                    actual = read_exact(native, SIZE)
                    if wire != actual:
                        at = next((i for i, (a, b) in enumerate(zip(wire, actual)) if a != b), min(len(wire), len(actual)))
                        (out / 'mismatch.json').write_text(json.dumps(
                            dict(record=index, scene=slot[0], clock=slot[1], byte=at,
                                 original=wire[at] if at < len(wire) else None,
                                 native=actual[at] if at < len(actual) else None), indent=2) + '\n')
                        raise ValueError(f'{slot[0]} clock{slot[1]}: complete display byte{at} differs')
                    records.append(dict(scene=slot[0], clock=slot[1], tone=slot[2], sha256=sha(wire)))
                    if load == 0x1000:
                        stream.write(wire)
                    else:
                        assert read_exact(stream, SIZE) == wire, 'display load metamorphism differs'
                assert not native.read(1), 'extra native display bytes'
            if load == 0x2000:
                assert not stream.read(1), 'extra original display bytes'
        if first_trace is not None:
            assert first_trace == records and first_states == states, 'scene load metamorphism differs'
        else:
            first_trace, first_states = records, states
        results.append(dict(load=load, calls=graphics.calls, tram_writes=graphics.writes))
        print(f'load{load:04x}: {len(states)} scenes, {len(records)} complete displays', flush=True)
    return first_trace, first_states, results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('target', 'hdi', 'font-bmp', 'exe', 'output-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--reference-dir', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest, source_files = source_manifest(root)
    out = args.output_dir.resolve()
    if out.exists():
        raise ValueError('use a fresh Game Over integration output directory')
    out.mkdir(parents=True)
    command, raw_hash, size = run_native(args.exe, args.hdi, args.font_bmp, out)
    assert size % SIZE == 0
    outputs = file_hashes(out / 'scenes')
    inputs = dict(target_sha256=sha(args.target.read_bytes()),
                  hdi_sha256=sha(args.hdi.read_bytes()), font_sha256=sha(args.font_bmp.read_bytes()))
    if args.reference_dir:
        proof = json.loads((args.reference_dir / 'receipt.json').read_text())
        assert proof['passed'] and proof['original_cpu_reexecuted']
        # Original observations are independent of candidate source revisions.
        # Bind their producer manifest and every scenario/host output rather
        # than assigning the current candidate digest to the old producer.
        producer = json.loads((args.reference_dir / 'source-manifest.json').read_text())
        assert proof['source_manifest'] == producer['sha256']
        assert proof['load_segments'] == [4096, 8192] and proof['scenes'] == 20
        assert proof['outputs'] == outputs
        assert all(proof[k] == v for k, v in inputs.items())
        assert sha((args.reference_dir / 'original.gz').read_bytes()) == proof['trace_gzip_sha256']
        assert raw_hash == proof['trace_raw_sha256']
        records, states, controls = proof['records'], proof['scene_controls'], proof['original_controls']
        with gzip.open(args.reference_dir / 'original.gz', 'rb') as reference, gzip.open(out / 'native.gz', 'rb') as native:
            for record in records:
                wire = read_exact(reference, SIZE)
                assert wire == read_exact(native, SIZE) and sha(wire) == record['sha256']
            assert not reference.read(1) and not native.read(1)
        trace = args.reference_dir / 'original.gz'
    else:
        gaiji = main_assets(args.hdi)['GAMEFT.BFT']
        records, states, controls = original_controls(args.target.read_bytes(), args.font_bmp,
                                                     gaiji, out / 'scenes', out, size // SIZE)
        trace = out / 'original.gz'
    assert source_manifest(root)[0] == manifest, 'source changed during integration controls'
    (out / 'source-manifest.json').write_text(json.dumps(dict(sha256=manifest, files=source_files), indent=2) + '\n')
    receipt = dict(passed=True, observed_utc=datetime.now(timezone.utc).isoformat(),
                   source_manifest=manifest, executable_sha256=sha(args.exe.read_bytes()),
                   **inputs, muted=True, command=command, scenes=len(states), snapshots=len(records),
                   compared_bytes=size, trace_raw_sha256=raw_hash, trace_gzip_sha256=sha(trace.read_bytes()),
                   native_gzip_sha256=sha((out / 'native.gz').read_bytes()), records=records,
                   outputs=outputs, scene_controls=states, original_controls=controls,
                   original_cpu_reexecuted=not bool(args.reference_dir), load_segments=[4096, 8192],
                   reference_dir=str(args.reference_dir) if args.reference_dir else None,
                   reference_producer_manifest=proof['source_manifest'] if args.reference_dir else None,
                   unicorn_version=unicorn.__version__,
                   unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
                   graphics_extents={f'{s:04x}:{lo:04x}..{hi:04x}': sha(args.target.read_bytes()[6144+s*16+lo:6144+s*16+hi])
                                     for s, lo, hi in (*EXTENTS, (0xaaf, 0x6ba2, 0x6bd4))}, scope=__doc__)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('passed', 'scenes', 'snapshots', 'compared_bytes')}))


if __name__ == '__main__':
    main()
