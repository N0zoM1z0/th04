#!/usr/bin/env python3
"""Capture bundled DOS demos through GAME.BAT with a read-only private emulator.

No input injection, guest patch, raster skipping or clock acceleration. Each
invocation starts from an independent original-data image and stops at the last
requested demo's terminal decision, before the exit fade/process replacement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import shutil
import subprocess
import sys
import time
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.pc98 import parse_mz
from prepare_th04_maine_diagnostic_hdi import Fat12, u16, u32
from probe_th04_pf_archive import ARCHIVES, parse_archive
from build_th04_cpu_fault_emulator import ARCHIVE_SHA256, COMMIT, PRIVATE


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# Widths and original offsets are target observations independently guarded by
# DemoPlay/gameplay_loop, score and initialization CPU Oracles (see focused note).
# Candidate offsets always come from the exact product's attested MAP.
FIELDS = [
    ('frame', '_stage_frame', 0x538a, 2),
    ('input', '_key_det', 0x3974, 2),
    ('shift_raw', '_shiftkey', 0x3976, 1),
    ('stage', '_stage_id', 0x5394, 1),
    ('score_digits', '_score', 0x4349, 8),
    ('score_delta', '_score_delta', 0x435a, 4),
    ('score_delta_frame', '_score_delta_frame', 0x435e, 4),
    ('lcg', '_random_seed', 0x3e2, 4),
    ('ring', '_randring', 0x3dcc, 256),
    ('ring_cursor', '_randring_p', 0x3ecc, 2),
    ('player_pos', '_player_pos', 0x464e, 4),
    ('power', '_power', 0x4664, 1),
    ('hit', '_player_is_hit', 0x4669, 1),
    ('invincibility', '_player_invincibility_time', 0x4662, 1),
    ('respawn', '_player_respawn_motion_time', 0x4663, 1),
    ('resident_pointer', '_resident', 0xba86, 4),
]
ORIGINAL_HOOKS = [(1, 0xaaf, 0xb7), (2, 0xaaf, 0x975), (3, 0, 0x2172),
                  (4, 0xaaf, 0x1180), (4, 0xaaf, 0x118e), (4, 0xaaf, 0x11a4),
                  (4, 0x13a9, 0x2c2), (4, 0x13a9, 0x2d0), (4, 0x13a9, 0x2e6)]


def map_symbols(path: Path) -> dict[str, tuple[int, int]]:
    result = {}
    for line in path.read_text().splitlines():
        match = re.match(r'^\s*([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+(?:idle\s+)?(\S.*)$', line)
        if match and ' C=' not in line:
            name = match[3].strip()
            pair = int(match[1], 16), int(match[2], 16)
            if name in result and result[name] != pair:
                raise ValueError(f'ambiguous MAP symbol: {name}')
            result[name] = pair
    return result


def profile(main: bytes, map_path: Path | None) -> dict:
    header = int.from_bytes(main[8:10], 'little')*16
    module = main[header:]
    dgroup = int.from_bytes(module[1:3], 'little')
    if module[:1] != b'\xba' or not parse_mz(main).valid:
        raise ValueError('unexpected MAIN entry/MZ')
    if map_path is None:
        hooks = ORIGINAL_HOOKS
        fields = [(name, offset, size) for name, _, offset, size in FIELDS]
    else:
        symbols = map_symbols(map_path)
        loop_segment, loop_offset = symbols['gameplay_loop()']
        demo_segment, demo_offset = symbols['demoplay()']
        # Exact natural producer's seams are decoded and opcode-guarded here.
        hooks = [(1, loop_segment, loop_offset+0x1f), (2, demo_segment, demo_offset+0x2c),
                 (3, *symbols['IRAND'])]
        hooks += [(4, *symbols[name]) for name in (
            'randring1_next16()', 'randring1_next16_and(unsigned int)',
            'randring1_next16_mod(unsigned int)', 'randring2_next16()',
            'randring2_next16_and(unsigned int)', 'randring2_next16_mod(unsigned int)')]
        fields = []
        for name, symbol, _, size in FIELDS:
            segment, offset = symbols[symbol]
            if segment != dgroup:
                raise ValueError(f'field outside MAIN DGROUP: {symbol}')
            fields.append((name, offset, size))
    boundary = hooks[0][1]*16+hooks[0][2]
    terminal = hooks[1][1]*16+hooks[1][2]
    key = fields[1][1]+1
    frame = fields[0][1]
    if (module[boundary:boundary+5] != b'\xf6\x06'+key.to_bytes(2, 'little')+b'\x10'
            or module[boundary-4:boundary-2] != b'\xff\x16'
            or module[terminal:terminal+6] != b'\x81\x3e'+frame.to_bytes(2, 'little')+b'\x9c\x0f'):
        raise ValueError('DemoPlay/gameplay boundary instruction drift')
    ring = fields[8][1].to_bytes(2, 'little')
    cursor = fields[9][1].to_bytes(2, 'little')
    expected_cursor_sites = []
    for _, segment, offset in hooks[3:]:
        at = segment*16+offset
        if module[at:at+12] != b'\x8b\x1e'+cursor+b'\x8b\x87'+ring+b'\xfe\x06'+cursor:
            raise ValueError('RNG ring accessor instruction/width drift')
        expected_cursor_sites.append(at+8)
    pattern = b'\xfe\x06'+cursor
    actual_cursor_sites = [i for i in range(len(module)) if module.startswith(pattern, i)]
    if sorted(expected_cursor_sites) != actual_cursor_sites:
        raise ValueError('ring cursor increments outside observed accessors')
    return dict(dgroup=dgroup, module_size=len(module), signature=module[:32].hex(),
                fields=fields, hooks=hooks, boundary='after-demo-before-update-v1',
                boundary_bytes=module[boundary-4:boundary+5].hex(),
                terminal_bytes=module[terminal:terminal+6].hex())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', action='store_true')
    parser.add_argument('--build-dir', type=Path, default=ROOT / '.analysis/build/th04-normal')
    parser.add_argument('--map', type=Path)
    parser.add_argument('--emulator-receipt', required=True, type=Path)
    parser.add_argument('--font-bmp', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--demos', type=int, choices=(1, 4), default=4)
    parser.add_argument('--cycles', type=int, default=24000, choices=(24000, 36000))
    parser.add_argument('--timeout', type=int, default=900)
    diagnostics = parser.add_mutually_exclusive_group()
    diagnostics.add_argument('--snapshot-frames', type=int, nargs='+',
                             help='read-only DGROUP watches; stops early, cannot pass completeness')
    diagnostics.add_argument('--dgroup-stream', action='store_true',
                             help='compressed DGROUP after every actor update; continues through all demos')
    diagnostics.add_argument('--video-stream', action='store_true',
                             help='full two-page PC-98 VRAM/palette/GDC stream at the same frame boundary')
    parser.add_argument('--video-layout', type=Path, help='attested host video layout receipt')
    args = parser.parse_args()
    os.nice(15)
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    # GDB needs additional virtual mappings for ELF symbols and Python. The
    # diagnostic script applies the ordinary 512 MiB limit to the inferior.
    address_space = (1536 if args.snapshot_frames or args.dgroup_stream or args.video_stream else 512)*1024*1024
    resource.setrlimit(resource.RLIMIT_AS, (address_space, address_space))
    output = args.output_dir.resolve()
    if output.exists() or not output.is_relative_to(ROOT / '.analysis/runtime/candidates'):
        parser.error('use a fresh private capture directory')
    if not args.original and args.map is None:
        parser.error('ordinary candidate requires its attested MAP')
    emulator_receipt = args.emulator_receipt.resolve()
    emulator = json.loads(emulator_receipt.read_text())
    binary = Path(emulator['binary']).resolve()
    observer = Path(__file__).with_name('th04_demo_observer.inl')
    if (not emulator_receipt.is_relative_to(PRIVATE) or not binary.is_relative_to(PRIVATE)
            or emulator['source_commit'] != COMMIT or emulator['source_archive_sha256'] != ARCHIVE_SHA256
            or emulator['observer_source_sha256'] != sha(observer.read_bytes())
            or emulator['binary_sha256'] != sha(binary.read_bytes())):
        raise ValueError('demo emulator identity drift')
    source = binary.parent.parent
    if (sha((source / 'src/cpu/core_normal.cpp').read_bytes()) != emulator['core_after_sha256']
            or sha((source / 'config.h').read_bytes()) != emulator['config_header_sha256']):
        raise ValueError('compiled emulator source/config identity drift')
    video_layout = None
    if args.video_stream:
        if args.video_layout is None:
            parser.error('video stream requires --video-layout')
        from th04_demo_video import LAYOUT, SYMBOL_SIZES
        video_layout = json.loads(args.video_layout.read_text())
        if (not video_layout['passed'] or video_layout['layout'] != LAYOUT
                or video_layout['emulator_sha256'] != emulator['binary_sha256']
                or video_layout['emulator_receipt_sha256'] != sha(emulator_receipt.read_bytes())
                or {name: row['size'] for name, row in video_layout['symbols'].items()} != SYMBOL_SIZES
                or any(sha(Path(path).read_bytes()) != digest
                       for path, digest in video_layout['source_inputs'].items())):
            raise ValueError('video ABI/source/ELF identity drift')
    targets = tomllib.loads((ROOT / 'config/targets.toml').read_text())['artifacts']
    products = {r['id'].removeprefix('th04-'): r for r in targets if r['id'].startswith('th04-')}
    for target in products.values():
        data = (ROOT / target['private_path']).read_bytes()
        if (len(data) != target['size'] or sha(data) != target['sha256'] or not parse_mz(data).valid):
            raise ValueError('original executable attestation failed')
    main_path = ROOT / products['main']['private_path'] if args.original else args.build_dir / 'MAIN.EXE'
    main_bytes = main_path.read_bytes()
    candidate_manifest = None
    if not args.original:
        candidate_manifest = json.loads((args.build_dir / 'build.json').read_text())
        if candidate_manifest.get('variant') != 'normal':
            raise ValueError('paired demo requires ordinary damage')
        receipt = json.loads(Path(candidate_manifest['products']['main']['build_receipt']).read_text())
        if sha(args.map.read_bytes()) != receipt['link']['map_sha256']:
            raise ValueError('MAP differs from MAIN producer')
    capture_profile = profile(main_bytes, None if args.original else args.map)
    output.mkdir(parents=True)
    # The preparation driver verifies all four selected originals/candidates and
    # copies the pinned HDI. It changes AUTOEXEC only, retaining assets and saves.
    command = [sys.executable, str(ROOT / 'scripts/prepare_product_hdi.py'), '--output-dir', str(output / 'prepared')]
    command += ['--original'] if args.original else ['--build-dir', str(args.build_dir.resolve())]
    subprocess.run(command, check=True, stdout=subprocess.PIPE)
    initial_image = (output / 'prepared/diagnostic.hdi').read_bytes()
    fs = Fat12(bytearray(initial_image))
    directory = fs.find_entry([fs.root], b'GENSO      ')
    offsets = [fs.cluster_offset(k) for k in fs.chain(u16(fs.image, directory+26))]
    entry = fs.find_entry(offsets, ARCHIVES['main']['fat_name'])
    archive = fs.file_bytes(u16(fs.image, entry+26), u32(fs.image, entry+28))
    if len(archive) != ARCHIVES['main']['size'] or sha(archive) != ARCHIVES['main']['sha256']:
        raise ValueError('pinned MAIN archive identity drift')
    _, assets = parse_archive(archive, 'main', ARCHIVES['main'])
    demos = {}
    for number in range(1, 5):
        name = f'DEMO{number}.REC'
        data = assets[name]
        if len(data) != 8000:
            raise ValueError('demo bank size')
        (output / name).write_bytes(data)
        demos[str(number)] = sha(data)
    starting_files = {}
    executed_products = {}
    for product, target in products.items():
        filename = {'main':'MAIN    EXE', 'op':'OP      EXE', 'maine':'MAINE   EXE', 'zun':'ZUN     COM'}[product]
        entry = fs.find_entry(offsets, filename.encode())
        data = fs.file_bytes(u16(fs.image, entry+26), u32(fs.image, entry+28))
        executed_products[product] = dict(size=len(data), sha256=sha(data))
    for name in (b'MIKO    CFG', b'GENSOU  SCR'):
        entry = fs.find_entry(offsets, name)
        data = fs.file_bytes(u16(fs.image, entry+26), u32(fs.image, entry+28))
        starting_files[name.decode()] = dict(size=len(data), sha256=sha(data), hex=data.hex())
    image = output / 'execution.hdi'
    image.write_bytes(initial_image)
    font = args.font_bmp.read_bytes()
    if font[:2] != b'BM':
        raise ValueError('font must be BMP')
    (output / 'FREECG98.BMP').write_bytes(font)
    runtime = tomllib.loads((ROOT / 'config/runtime.toml').read_text())
    conf_bytes = (ROOT / runtime['primary']['config']).read_bytes()
    if sha(conf_bytes) != runtime['primary']['config_sha256']:
        raise ValueError('base emulator config drift')
    conf_bytes = re.sub(rb'(?m)^cycles\s*=.*$', f'cycles = fixed {args.cycles}'.encode(), conf_bytes)
    conf_bytes = conf_bytes.replace(b'cputype = auto', b'cputype = pentium')
    config = output / 'dosbox-x.conf'
    config.write_bytes(conf_bytes)
    prof = output / 'observer-profile.txt'
    prof.write_text(f"{capture_profile['dgroup']:x} {capture_profile['module_size']:x}\n"
                    +capture_profile['signature']+'\n'+str(len(capture_profile['hooks']))+'\n'
                    +''.join(f'{kind} {segment:x} {offset:x}\n' for kind, segment, offset in capture_profile['hooks'])
                    +str(len(capture_profile['fields']))+'\n'
                    +''.join(f'{offset:x} {size}\n' for _, offset, size in capture_profile['fields']))
    (output / 'profile.json').write_text(json.dumps(capture_profile, indent=2)+'\n')
    env = os.environ.copy()
    env.update(SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
               TH04_DEMO_PROFILE=str(prof), TH04_DEMO_TRACE=str(output / 'raw.txt'),
               TH04_DEMO_STOP_AFTER=str(args.demos),
               XDG_CACHE_HOME=str(output / 'cache'), XDG_CONFIG_HOME=str(output / 'config'),
               XDG_DATA_HOME=str(output / 'data'))
    command = [str(binary), '-defaultconf', '-defaultmapper', '-conf', str(config),
               '-fastlaunch', '-nogui', '-nomenu', '-exit', '-c',
               f'imgmount 2 "{image}" -t hdd -fs none', '-c', 'boot -l c']
    snapshot_script = Path(__file__).with_name('th04_demo_snapshot.gdb')
    if args.snapshot_frames:
        if any(frame < 1 or frame >= 3996 for frame in args.snapshot_frames):
            parser.error('diagnostic frames must be inside the first demo')
        debugger = Path(shutil.which('gdb')).resolve()
        env.update(TH04_DEMO_SNAPSHOT_DIR=str(output),
                   TH04_DEMO_SNAPSHOT_FRAMES=','.join(map(str, args.snapshot_frames)))
        command = [str(debugger), '-nx', '-batch', '-x', str(snapshot_script), '--args', *command]
    stream_sources = None
    if args.dgroup_stream or args.video_stream:
        source_directory = Path(__file__).parent.resolve()
        stream_script = source_directory / 'th04_demo_dgroup_stream.gdb'
        source_names = ['th04_demo_dgroup_stream.gdb', 'th04_demo_dgroup.py', 'th04_demo_host_ram.py']
        if args.video_stream:
            source_names.append('th04_demo_video.py')
        stream_sources = {name: sha((source_directory / name).read_bytes()) for name in source_names}
        debugger = Path(shutil.which('gdb')).resolve()
        env.update(TH04_DEMO_STREAM_DIR=str(output),
                   TH04_DEMO_STREAM_SOURCE_DIR=str(source_directory))
        if args.video_stream:
            env.update(TH04_DEMO_STREAM_KIND='video', TH04_DEMO_VIDEO_LAYOUT=str(args.video_layout.resolve()))
        command = [str(debugger), '-nx', '-batch', '-x', str(stream_script), '--args', *command]
    start = time.monotonic()
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
    log = (output / 'boot.log').read_bytes()
    complete = (not timeout and code == 0 and
                f'TH04_DEMO_OBSERVER_COMPLETE {args.demos}\n'.encode() in log)
    record = dict(schema_version=1, capture_complete=complete, timeout=timeout, exit_code=code,
                  elapsed_seconds=time.monotonic()-start, command=command,
                  role='original' if args.original else 'ordinary-reconstructed', demos=args.demos,
                  cycles=args.cycles, canonicality='candidate-local-attested',
                  products=executed_products, starting_files=starting_files,
                  original_hdi_sha256=runtime['image']['sha256'], initial_hdi_sha256=sha(initial_image),
                  final_hdi_sha256=sha(image.read_bytes()), demo_sha256=demos,
                  archive_sha256=sha(archive), font_sha256=sha(font), config_sha256=sha(conf_bytes),
                  main_path=str(main_path.resolve()), main_sha256=sha(main_bytes),
                  map_sha256=None if args.original else sha(args.map.read_bytes()),
                  emulator_receipt_sha256=sha(emulator_receipt.read_bytes()),
                  emulator_sha256=sha(binary.read_bytes()), observer_source_sha256=sha(observer.read_bytes()),
                  profile_sha256=sha(prof.read_bytes()), profile_json_sha256=sha((output / 'profile.json').read_bytes()),
                  raw_sha256=sha((output / 'raw.txt').read_bytes()) if (output / 'raw.txt').exists() else None,
                  producer_manifest=candidate_manifest, scope=__doc__)
    record['resource_budget'] = dict(cpu_affinity=sorted(os.sched_getaffinity(0)), nice=15,
                                    address_space_bytes=512*1024*1024, serial_run=True)
    if args.snapshot_frames:
        record['diagnostic_snapshot'] = dict(frames=args.snapshot_frames,
            complete=all((output / f'snapshot-{frame}-dgroup.bin').is_file() for frame in args.snapshot_frames),
            gdb_sha256=sha(debugger.read_bytes()), script_sha256=sha(snapshot_script.read_bytes()),
            debugger_address_space_bytes=address_space,
            files={path.name: sha(path.read_bytes()) for path in sorted(output.glob('snapshot-*'))})
    if args.dgroup_stream or args.video_stream:
        prefix = 'video' if args.video_stream else 'dgroup'
        marker = 'TH04_VIDEO_STREAM' if args.video_stream else 'TH04_DGROUP_STREAM'
        metadata = output / (prefix+'-stream.json')
        stream_complete = (complete and metadata.is_file()
            and f'{marker}_COMPLETE {args.demos}\n'.encode() in log)
        record[prefix+'_stream'] = dict(complete=stream_complete,
            gdb_sha256=sha(debugger.read_bytes()), consumer_source_sha256=stream_sources,
            debugger_address_space_bytes=address_space,
            files={path.name: sha(path.read_bytes()) for path in sorted(output.glob(prefix+'-*'))})
        if args.video_stream:
            record['video_stream'].update(layout_receipt_path=str(args.video_layout.resolve()),
                                         layout_receipt_sha256=sha(args.video_layout.read_bytes()))
    (output / 'receipt.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(dict(capture_complete=complete, output=str(output), elapsed_seconds=record['elapsed_seconds'])))
    if args.dgroup_stream or args.video_stream:
        return 0 if record['video_stream' if args.video_stream else 'dgroup_stream']['complete'] else 1
    return 0 if complete or record.get('diagnostic_snapshot', {}).get('complete') else 1


if __name__ == '__main__':
    raise SystemExit(main())
