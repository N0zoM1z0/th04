#!/usr/bin/env python3
"""Capture ordinary Stage 1 with keyboard API input at the original OP seed tick.

Only MAIN is replaced. Original OP/MAINE/ZUN, legal configuration and assets
stay pinned. The adapter observes OP's resident counter, queues real keyboard
device events, and checks that guest RAM/registers/clock do not change during
each API call. It never assigns RNG or gameplay state.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import sys
import time
import tomllib
import tarfile

from capture_th04_dos_demos import ARCHIVE_SHA256, COMMIT, PRIVATE, ROOT, sha
from compare_th04_dos_ordinary_prefix import ordinary_profile
from lib.pc98 import parse_mz


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', action='store_true')
    parser.add_argument('--build-dir', type=Path)
    parser.add_argument('--map', type=Path)
    parser.add_argument('--emulator-receipt', required=True, type=Path)
    parser.add_argument('--font-bmp', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--dgroup-stream', action='store_true')
    parser.add_argument('--video-stream', action='store_true')
    parser.add_argument('--video-layout', type=Path)
    parser.add_argument('--end-after', type=int,
                        help='Stop at an observed after-update frame; bounded prefix, not natural game exit')
    parser.add_argument('--dialog-at-frame', type=int,
                        help='After this observed frame stalls, release Shot and send ordinary Enter pulses')
    parser.add_argument('--continue-at-frame', type=int,
                        help='Release Shot and operate the real Continue wait after this later observed frame')
    parser.add_argument('--quit-at-frame', type=int,
                        help='Release Shot, send ordinary Escape pulses, then observe MAINE and fresh OP menu')
    parser.add_argument('--restart-main', action='store_true',
                        help='After verified fresh OP menu, use ordinary keys to observe a second MAIN entry')
    parser.add_argument('--restart-updates', type=int,
                        help='Observe this many actual second-MAIN updates after restart (1..3995)')
    parser.add_argument('--restart-shot-boundary', action='store_true',
                        help='Send second-MAIN Shot at the first actual actor-update write instead of an entry delay')
    parser.add_argument('--restart-menu-boundary', action='store_true',
                        help='Confirm fresh OP at its actual counter store and repeat real Enter pulses until MAIN entry')
    parser.add_argument('--stall-diagnostic-ms', type=int,
                        help='Record actual guest PC/RAM after this much virtual no-frame progress')
    parser.add_argument('--all-products', action='store_true',
                        help='Install and attest a complete same-run four-product build and observe DOS4B00 entries')
    parser.add_argument('--process-events', action='store_true',
                        help='Observe actual guest INT21 requests and MCB/PSP process activity')
    parser.add_argument('--emulator-archive', type=Path, default=PRIVATE / 'dosbox-x-199aa35f.tar.gz')
    args = parser.parse_args()
    if args.video_stream:
        if args.video_layout is None:
            parser.error('video stream requires an attested --video-layout')
        args.dgroup_stream = True
    if args.end_after is not None:
        if not 1 <= args.end_after <= 65535:
            parser.error('--end-after must fit a nonzero stage-frame WORD')
        args.dgroup_stream = True
    if args.dialog_at_frame is not None and (args.end_after is None or
            not 1 <= args.dialog_at_frame < args.end_after):
        parser.error('dialog cue requires 1 <= frame < --end-after')
    if args.continue_at_frame is not None and (args.dialog_at_frame is None or
            not args.dialog_at_frame < args.continue_at_frame < args.end_after):
        parser.error('Continue cue requires dialog frame < Continue frame < --end-after')
    if args.quit_at_frame is not None and (not args.process_events or args.continue_at_frame is not None or
            args.dialog_at_frame is None or not args.dialog_at_frame < args.quit_at_frame < args.end_after):
        parser.error('Quit route requires process events, no Continue cue, and dialog < Quit < end-after')
    if args.stall_diagnostic_ms is not None and (args.end_after is None or args.stall_diagnostic_ms < 1000):
        parser.error('stall diagnostics require a bounded prefix and at least1000 virtual milliseconds')
    if args.restart_main and args.quit_at_frame is None:
        parser.error('Restart requires a configured Quit route')
    if args.restart_updates is not None and (not args.restart_main or args.video_stream or
            not 1 <= args.restart_updates <= 3995):
        parser.error('Restart updates require restart, no video, and 1..3995 updates')
    if args.restart_shot_boundary and (args.restart_updates is None or args.restart_updates < 2):
        parser.error('Boundary Shot requires at least two second-MAIN updates')
    if args.all_products and not args.process_events:
        parser.error('Four-product surface requires process events')
    if args.restart_menu_boundary and (not args.all_products or not args.restart_main):
        parser.error('Boundary menu requires an all-product restart route')
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(ROOT / '.analysis/runtime/candidates'):
        parser.error('use a fresh private capture directory')
    if not args.original and (args.build_dir is None or args.map is None):
        parser.error('candidate requires its frozen build directory and MAP')
    os.nice(19)
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    resource.setrlimit(resource.RLIMIT_AS, (1536 * 1024 * 1024, 1536 * 1024 * 1024))
    emulator_path = args.emulator_receipt.resolve()
    emulator = json.loads(emulator_path.read_text())
    binary = Path(emulator['binary']).resolve()
    observer = Path(__file__).with_name('th04_demo_observer.inl')
    if (not emulator_path.is_relative_to(PRIVATE) or not binary.is_relative_to(PRIVATE)
            or emulator['source_commit'] != COMMIT or emulator['source_archive_sha256'] != ARCHIVE_SHA256
            or emulator['binary_sha256'] != sha(binary.read_bytes())
            or emulator['observer_source_sha256'] != sha(observer.read_bytes())):
        raise ValueError('observer emulator identity drift')
    source = binary.parent.parent
    if (sha((source / 'src/cpu/core_normal.cpp').read_bytes()) != emulator['core_after_sha256']
            or sha((source / 'config.h').read_bytes()) != emulator['config_header_sha256']):
        raise ValueError('compiled observer source/config drift')
    process_inputs = {}
    if args.process_events:
        elf = binary.read_bytes()[:20]
        if elf[:6] != b'\x7fELF\x02\x01' or int.from_bytes(elf[18:20], 'little') != 62:
            raise ValueError('process observer host ELF/ABI')
        if sha(args.emulator_archive.read_bytes()) != ARCHIVE_SHA256:
            raise ValueError('process observer pinned archive')
        with tarfile.open(args.emulator_archive) as archive:
            for name in ('src/cpu/cpu.cpp', 'include/cpu.h'):
                data = (source / name).read_bytes()
                if archive.extractfile(source.name + '/' + name).read() != data:
                    raise ValueError('process observer CPU source identity')
                process_inputs[str(source / name)] = sha(data)
    targets = tomllib.loads((ROOT / 'config/targets.toml').read_text())['artifacts']
    products = {target['id'].removeprefix('th04-'): target for target in targets
                if target['id'].startswith('th04-')}
    for target in products.values():
        data = (ROOT / target['private_path']).read_bytes()
        if len(data) != target['size'] or sha(data) != target['sha256'] or not parse_mz(data).valid:
            raise ValueError('original executable attestation failed')
    original = (ROOT / products['main']['private_path']).read_bytes()
    main_path = ROOT / products['main']['private_path'] if args.original else args.build_dir / 'MAIN.EXE'
    main_bytes = main_path.read_bytes()
    manifest = None
    if not args.original:
        manifest = json.loads((args.build_dir / 'build.json').read_text())
        product = manifest['products']['main']
        producer = json.loads(Path(product['build_receipt']).read_text())
        if (manifest.get('variant') != 'normal' or len(main_bytes) != product['size']
                or sha(main_bytes) != product['sha256']
                or not parse_mz(main_bytes).valid
                or sha(args.map.read_bytes()) != producer['link']['map_sha256']):
            raise ValueError('ordinary MAIN producer/MAP drift')
    surface = None
    if args.all_products and not args.original:
        from th04_product_surface import attest_surface
        surface = attest_surface(args.build_dir.resolve())
    capture_profile = ordinary_profile(main_bytes, original, None if args.original else args.map)
    if args.end_after is not None:
        from capture_th04_dos_demos import profile as demo_profile
        guarded = demo_profile(main_bytes, None if args.original else args.map)
        capture_profile['hooks'][1] = guarded['hooks'][1]
        capture_profile['boundary'] = 'ordinary-bounded-after-update-v2'
        capture_profile['terminal_bytes'] = guarded['terminal_bytes']
        capture_profile['end_after'] = args.end_after
    output.mkdir(parents=True)
    if args.process_events:
        process_targets = {'th04-' + name: dict(path=str((ROOT / row['private_path']).resolve()),
                           size=row['size'], sha256=row['sha256']) for name, row in products.items()}
        process_targets['th04-main'] = dict(path=str(main_path.resolve()), size=len(main_bytes), sha256=sha(main_bytes))
        if surface is not None:
            process_targets = surface['products']
        (output / 'process-targets.json').write_text(json.dumps(process_targets, indent=2) + '\n')
    if args.all_products:
        from th04_product_surface import op_counter_profile
        if surface is None:
            surface = dict(schema_version=1, origin='pinned-original', products=process_targets)
        (output/'product-surface.json').write_text(json.dumps(surface,indent=2)+'\n')
        op = Path(process_targets['th04-op']['path']).read_bytes()
        op_map = None if args.original else Path(surface['op_map_path'])
        (output/'op-counter-profile.json').write_text(json.dumps(op_counter_profile(op,op_map),indent=2)+'\n')
    prepare = [sys.executable, str(ROOT / 'scripts/prepare_product_hdi.py'), '--output-dir',
               str(output / 'prepared'), '--products', *(['main','op','maine','zun'] if args.all_products else ['main']), '--rank', '1', '--lives', '6', '--bombs', '0']
    prepare += ['--original'] if args.original else ['--build-dir', str(args.build_dir.resolve())]
    with (output / 'prepare.log').open('wb') as stream:
        subprocess.run(prepare, check=True, stdout=stream, stderr=subprocess.STDOUT)
    initial_image = (output / 'prepared/diagnostic.hdi').read_bytes()
    image = output / 'execution.hdi'
    image.write_bytes(initial_image)
    font = args.font_bmp.read_bytes()
    if font[:2] != b'BM':
        raise ValueError('font must be BMP')
    (output / 'FREECG98.BMP').write_bytes(font)
    runtime = tomllib.loads((ROOT / 'config/runtime.toml').read_text())
    config_bytes = (ROOT / runtime['primary']['config']).read_bytes()
    if sha(config_bytes) != runtime['primary']['config_sha256']:
        raise ValueError('base emulator config drift')
    config_bytes = re.sub(rb'(?m)^cycles\s*=.*$', b'cycles = fixed 24000', config_bytes)
    config_bytes = config_bytes.replace(b'cputype = auto', b'cputype = pentium')
    config = output / 'dosbox-x.conf'
    config.write_bytes(config_bytes)
    profile_path = output / 'observer-profile.txt'
    profile_path.write_text(f"{capture_profile['dgroup']:x} {capture_profile['module_size']:x}\n"
                            + capture_profile['signature'] + '\n' + str(len(capture_profile['hooks'])) + '\n'
                            + ''.join(f'{kind} {segment:x} {offset:x}\n'
                                      for kind, segment, offset in capture_profile['hooks'])
                            + str(len(capture_profile['fields'])) + '\n'
                            + ''.join(f'{offset:x} {size}\n' for _, offset, size in capture_profile['fields']))
    (output / 'profile.json').write_text(json.dumps(capture_profile, indent=2) + '\n')
    debugger = Path(shutil.which('gdb')).resolve()
    adapter = Path(__file__).with_name('th04_ordinary_keyboard.gdb')
    walker = Path(__file__).with_name('th04_demo_host_ram.py')
    env = dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               TH04_DEMO_PROFILE=str(profile_path), TH04_DEMO_TRACE=str(output / 'raw.txt'),
               TH04_DEMO_STOP_AFTER='1', TH04_CLOCK_INPUT_OUTPUT=str(output),
               TH04_CLOCK_KEYBOARD_HEADER=str(source / 'include/keyboard.h'),
               TH04_CLOCK_SOURCE_DIR=str(adapter.parent),
               XDG_CACHE_HOME=str(output / 'cache'), XDG_CONFIG_HOME=str(output / 'config'),
               XDG_DATA_HOME=str(output / 'data'))
    command = [str(debugger), '-nx', '-batch', '-x', str(adapter), '--args', str(binary),
               '-defaultconf', '-defaultmapper', '-conf', str(config), '-fastlaunch', '-nogui',
               '-nomenu', '-exit', '-c', f'imgmount 2 "{image}" -t hdd -fs none', '-c', 'boot -l c']
    stream_sources = []
    if args.process_events:
        env['TH04_ORDINARY_PROCESS_EVENTS'] = '1'
    if args.all_products:
        env['TH04_ORDINARY_ALL_PRODUCTS'] = '1'
    if args.end_after is not None:
        env['TH04_ORDINARY_END_AFTER'] = str(args.end_after)
    if args.dialog_at_frame is not None:
        env['TH04_ORDINARY_DIALOG_FRAME'] = str(args.dialog_at_frame)
    if args.continue_at_frame is not None:
        env['TH04_ORDINARY_CONTINUE_FRAME'] = str(args.continue_at_frame)
    if args.quit_at_frame is not None:
        env['TH04_ORDINARY_QUIT_FRAME'] = str(args.quit_at_frame)
    if args.restart_main:
        env['TH04_ORDINARY_RESTART_MAIN'] = '1'
    if args.restart_updates is not None:
        env['TH04_ORDINARY_RESTART_UPDATES'] = str(args.restart_updates)
    if args.restart_shot_boundary:
        env['TH04_ORDINARY_RESTART_SHOT_BOUNDARY'] = '1'
    if args.restart_menu_boundary:
        env['TH04_ORDINARY_RESTART_MENU_BOUNDARY'] = '1'
    if args.stall_diagnostic_ms is not None:
        env['TH04_ORDINARY_STALL_MS'] = str(args.stall_diagnostic_ms)
    if args.dgroup_stream:
        env['TH04_ORDINARY_DGROUP'] = '1'
        stream_sources = [adapter.with_name(name) for name in
                          ('th04_ordinary_dgroup.py', 'th04_ordinary_dgroup_gdb.py', 'th04_demo_dgroup.py')]
    if args.video_stream:
        from th04_demo_video import LAYOUT, SYMBOL_SIZES
        layout = json.loads(args.video_layout.read_text())
        if (not layout['passed'] or layout['layout'] != LAYOUT or
                layout['emulator_sha256'] != emulator['binary_sha256'] or
                layout['emulator_receipt_sha256'] != sha(emulator_path.read_bytes()) or
                {name: row['size'] for name, row in layout['symbols'].items()} != SYMBOL_SIZES or
                any(sha(Path(path).read_bytes()) != digest for path, digest in layout['source_inputs'].items())):
            raise ValueError('ordinary video ABI/source/binary drift')
        env.update(TH04_ORDINARY_VIDEO='1', TH04_ORDINARY_VIDEO_LAYOUT=str(args.video_layout.resolve()))
        stream_sources += [adapter.with_name(name) for name in ('th04_demo_video.py', 'th04_ordinary_video.py')]
    if args.process_events:
        stream_sources += [adapter.with_name(name) for name in ('th04_dos_process.py', 'th04_ordinary_process_gdb.py', 'th04_ordinary_generation.py', 'th04_product_surface.py')]
    started = time.monotonic()
    timeout = False
    with (output / 'boot.log').open('wb') as stream:
        child = subprocess.Popen(command, cwd=output, env=env, stdout=stream,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = child.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timeout = True
            os.killpg(child.pid, signal.SIGTERM)
            try:
                code = child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                code = child.wait()
    complete = (not timeout and code == 0 and b'TH04_DEMO_OBSERVER_COMPLETE 1\n'
                in (output / 'boot.log').read_bytes() and not (output / 'clock-input-error.txt').exists())
    if args.end_after is not None:
        complete = (not timeout and code == 0 and b'TH04_ORDINARY_PREFIX_COMPLETE\n'
                    in (output / 'boot.log').read_bytes() and not (output / 'clock-input-error.txt').exists())
    if args.quit_at_frame is not None:
        complete = complete and b'TH04_ORDINARY_ROUTE_COMPLETE\n' in (output / 'boot.log').read_bytes()
    names = ['profile.json', 'observer-profile.txt', 'dosbox-x.conf', 'boot.log', 'raw.txt', 'clock-input.json']
    if args.dgroup_stream:
        complete = complete and b'TH04_ORDINARY_DGROUP_COMPLETE\n' in (output / 'boot.log').read_bytes()
        names += ['ordinary-dgroup.bin.gz', 'ordinary-dgroup.json']
    if args.video_stream:
        complete = complete and b'TH04_ORDINARY_VIDEO_COMPLETE\n' in (output / 'boot.log').read_bytes()
        names += ['ordinary-video.bin.gz', 'ordinary-video.json']
    if args.end_after is not None:
        names += ['ordinary-terminal.json']
    if args.stall_diagnostic_ms is not None:
        names += ['ordinary-stall.json', 'ordinary-stall-dgroup.bin']
    if args.process_events:
        names += ['process-events.json', 'process-events.jsonl', 'process-targets.json']
        names += sorted(path.name for pattern in ('process-entry-*.bin.gz', 'process-memory-*.bin.gz')
                        for path in output.glob(pattern))
        complete = complete and (output / 'process-events.json').is_file() and not (output / 'process-error.txt').exists()
    if args.quit_at_frame is not None:
        names += ['main-handoff.json', 'handoff-dgroup.bin', 'fresh-op-menu.json']
    if args.restart_updates is not None and complete:
        from th04_ordinary_generation import split_generations
        full = (output / 'raw.txt').read_bytes()
        first, second = split_generations(full)
        (output / 'raw.txt').rename(output / 'raw-observer-all.txt')
        (output / 'raw.txt').write_bytes(first)
        (output / 'second-main/raw.txt').write_bytes(second)
        names += ['raw-observer-all.txt', 'second-main/profile.json', 'second-main/raw.txt',
                  'second-main/ordinary-dgroup.json', 'second-main/ordinary-dgroup.bin.gz',
                  'second-main/ordinary-terminal.json', 'second-main-prefix.json']
        complete = complete and b'TH04_ORDINARY_SECOND_MAIN_COMPLETE\n' in (output / 'boot.log').read_bytes()
    if args.restart_shot_boundary and complete:
        names += ['second-main/first-update.json']
    if args.all_products:
        names += ['product-surface.json','op-counter-profile.json','initial-op-menu.json']
    for name in ('route-diagnostic.json','route-diagnostic-memory.bin.gz'):
        if (output/name).exists():
            names.append(name)
    receipt = dict(schema_version=1, complete=complete, timeout=timeout, exit=code,
                   role='original' if args.original else 'candidate', elapsed=time.monotonic() - started,
                   command=command, main_path=str(main_path.resolve()), main_sha256=sha(main_bytes),
                   map_path=None if args.original else str(args.map.resolve()),
                   map_sha256=None if args.original else sha(args.map.read_bytes()), producer_manifest=manifest,
                   initial_hdi_sha256=sha(initial_image), final_hdi_sha256=sha(image.read_bytes()),
                   emulator_receipt_sha256=sha(emulator_path.read_bytes()), emulator_sha256=sha(binary.read_bytes()),
                   font_sha256=sha(font), debugger_sha256=sha(debugger.read_bytes()),
                   adapter_sha256=sha(adapter.read_bytes()), walker_sha256=sha(walker.read_bytes()),
                   source_files={str(path): sha(path.read_bytes()) for path in
                                 (Path(__file__), adapter, walker, source / 'include/keyboard.h',
                                  source / 'include/regs.h', source / 'src/hardware/keyboard.cpp', *stream_sources)},
                   files={name: sha((output / name).read_bytes()) for name in names if (output / name).exists()},
                   resource_budget=dict(cpu_affinity=sorted(os.sched_getaffinity(0)), nice=os.nice(0),
                                        address_space_bytes=1536 * 1024 * 1024),
                   scope=__doc__)
    if args.end_after is not None:
        receipt.update(end_after=args.end_after, termination='observed-after-update-prefix',
                       natural_game_exit=False)
    if args.dialog_at_frame is not None:
        receipt['dialog_at_frame'] = args.dialog_at_frame
    if args.continue_at_frame is not None:
        receipt['continue_at_frame'] = args.continue_at_frame
    if args.quit_at_frame is not None:
        receipt.update(quit_at_frame=args.quit_at_frame, restart_main=args.restart_main, termination='observed-second-main-prefix' if args.restart_updates else 'observed-second-main-entry' if args.restart_main else 'observed-fresh-op-menu',
                       natural_game_exit=False)
        metadata = output / 'ordinary-dgroup.json'
        if metadata.is_file():
            receipt['main_frames'] = json.loads(metadata.read_text())['frames']
    if args.restart_updates is not None:
        receipt['restart_updates'] = args.restart_updates
        receipt['restart_shot_boundary'] = args.restart_shot_boundary
    if args.video_stream:
        receipt['video_layout'] = dict(path=str(args.video_layout.resolve()),
                                       sha256=sha(args.video_layout.read_bytes()))
    if args.process_events:
        receipt.update(process_events=True, resident_ownership=True, process_host_inputs=process_inputs)
    if args.all_products:
        receipt['all_products'] = True
        receipt['restart_menu_boundary'] = args.restart_menu_boundary
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(complete=complete, output=str(output))))
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
