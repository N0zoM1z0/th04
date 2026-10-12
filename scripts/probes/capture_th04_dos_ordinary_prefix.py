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
    args = parser.parse_args()
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
    capture_profile = ordinary_profile(main_bytes, original, None if args.original else args.map)
    output.mkdir(parents=True)
    prepare = [sys.executable, str(ROOT / 'scripts/prepare_product_hdi.py'), '--output-dir',
               str(output / 'prepared'), '--products', 'main', '--rank', '1', '--lives', '6', '--bombs', '0']
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
    names = ['profile.json', 'observer-profile.txt', 'dosbox-x.conf', 'boot.log', 'raw.txt', 'clock-input.json']
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
                                  source / 'include/regs.h', source / 'src/hardware/keyboard.cpp')},
                   files={name: sha((output / name).read_bytes()) for name in names if (output / name).exists()},
                   resource_budget=dict(cpu_affinity=sorted(os.sched_getaffinity(0)), nice=os.nice(0),
                                        address_space_bytes=1536 * 1024 * 1024),
                   scope=__doc__)
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(complete=complete, output=str(output))))
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
