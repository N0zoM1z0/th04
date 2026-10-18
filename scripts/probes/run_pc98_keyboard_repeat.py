#!/usr/bin/env python3
"""Run a held-key repeat Oracle on the pinned PC-98 emulator.

This uses internal DOS and an authored COM, not a TH04 image or V86 checkpoint.
All input enters through KEYBOARD_AddKey. No host keys or focus are used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time

ENGINE_SHA = '6e1a6e706d8b62aefa3204e30be5b77125fb4413d6891b5d10bd2701a6616ba1'
FONT_SHA = '41535bd7242c07d69ec5427584d31f068ca4eb996ca95246caed4e3573a494e6'
SYMBOLS = ['CPU_CycleLeft', 'CPU_CycleMax', 'CPU_Cycles', 'MemBase', 'PIC_Ticks',
           'Segs', 'cpu', 'cpu_regs', 'paging', '_Z12uart_rx_loadm',
           '_Z15KEYBOARD_AddKey8KBD_KEYSb', '_Z9IO_WriteBmh',
           '_ZL29pc98_8251_keyboard_uart_state', '_Z15PIC_ActivateIRQm']


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emulator', type=Path, required=True)
    parser.add_argument('--font-bmp', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    engine, font, out = args.emulator.resolve(), args.font_bmp.resolve(), args.output_dir.resolve()
    if sha(engine) != ENGINE_SHA or sha(font) != FONT_SHA:
        parser.error('emulator/font identity outside the attested Oracle contract')
    if out.exists():
        parser.error('output directory must be absent; retain prior failures')
    available = os.sched_getaffinity(0)
    os.sched_setaffinity(0, {1 if 1 in available else min(available)})
    os.nice(max(0, 19 - os.getpriority(os.PRIO_PROCESS, 0)))
    out.mkdir(parents=True)
    shutil.copy2(Path(__file__).resolve(), out/'launcher-source.py')
    here = Path(__file__).resolve().parent
    inputs = {str(Path(__file__).resolve()): sha(__file__), str(out/'launcher-source.py'): sha(out/'launcher-source.py')}
    for source, name in [(here/'fixtures/pc98_keyboard_repeat.asm', 'UART.ASM'),
                         (here/'fixtures/pc98_keyboard_uart.conf', 'dosbox-x.conf'),
                         (here/'pc98_keyboard_repeat_gdb.py', 'observe.py'),
                         (here/'th04_keyboard_admission_gdb.py', 'keyboard_admission_gdb.py'),
                         (here/'th04_demo_host_ram.py', 'th04_demo_host_ram.py')]:
        shutil.copy2(source, out/name)
        inputs[str(source)] = sha(source)
        inputs[str(out/name)] = sha(out/name)
    (out/'FREECG98.BMP').symlink_to(font)
    nasm = Path(shutil.which('nasm')).resolve()
    subprocess.run([str(nasm), '-f', 'bin', str(out/'UART.ASM'), '-o', str(out/'UART.COM')], check=True)
    SYMBOLS.extend(['_ZL17IRQ1_Handler_PC98v', '_Z10mem_writebjh', '_Z18pc98_keyboard_sendh', '_ZL9pic_queue', '_ZL14InEventService', '_ZL7srv_lag', '_Z20KEYBOARD_PC98_AddKey8KBD_KEYSb', '_ZL4keyb'])
    symbols = {}
    for line in subprocess.check_output(['nm', '-S', str(engine)], text=True).splitlines():
        cells = line.split()
        if len(cells) == 4 and cells[3] in SYMBOLS:
            symbols[cells[3]] = dict(address=int(cells[0], 16), size=int(cells[1], 16))
    if set(symbols) != set(SYMBOLS) or symbols['Segs']['size'] != 136 or symbols['cpu_regs']['size'] != 48:
        raise ValueError('pinned ELF symbol/layout contract differs')
    manifest = dict(engine=str(engine), engine_sha256=ENGINE_SHA, symbols=symbols,
                    keys=dict(KBD_z=30, KBD_enter=52), nasm_path=str(nasm), nasm_sha256=sha(nasm),
                    inputs={str(p): sha(p) for p in [out/'UART.ASM', out/'UART.COM',
                            out/'dosbox-x.conf', out/'th04_demo_host_ram.py', out/'keyboard_admission_gdb.py', font]})
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    observer = out/'observe.py'
    script = '\n'.join(['set debuginfod enabled off', 'set pagination off', 'set confirm off',
                        'set print thread-events off', 'set language c++', 'python', 'import sys',
                        'sys.path.insert(0,'+repr(str(out))+')',
                        'exec(compile(open('+repr(str(observer))+').read(),'+repr(str(observer))+
                        ',"exec"),{"__file__":'+repr(str(observer))+'})', 'end', 'quit', ''])
    (out/'observe.gdb').write_text(script)
    command = ['gdb', '-nx', '-batch', '-x', str(out/'observe.gdb'), '--args', str(engine),
               '-defaultconf', '-defaultmapper', '-conf', str(out/'dosbox-x.conf'),
               '-fastlaunch', '-nogui', '-nomenu', '-exit', '-c', 'mount c "'+str(out)+'"',
               '-c', 'c:', '-c', 'UART.COM', '-c', 'exit']

    def limit():
        resource.setrlimit(resource.RLIMIT_AS, (1536*1024*1024, 1536*1024*1024))

    start, timeout = time.monotonic(), False
    with (out/'gdb.log').open('xb') as log:
        process = subprocess.Popen(command, cwd=out, stdout=log, stderr=subprocess.STDOUT,
                                   env=dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
                                            XDG_CONFIG_HOME=str(out/'xdg'), PYTHONDONTWRITEBYTECODE='1'),
                                   preexec_fn=limit, start_new_session=True)
        try:
            code = process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            timeout = True
            if (out/'startup.json').exists():
                try:
                    os.kill(json.loads((out/'startup.json').read_text())['inferior_pid'], signal.SIGINT)
                except ProcessLookupError:
                    pass
            try:
                code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
    events = json.loads((out/'events.json').read_text()) if (out/'events.json').exists() else None
    passed = code == 0 and not timeout and events is not None and events['complete'] and events['error'] is None
    inputs.update({str(p): sha(p) for p in [out/'observe.py', out/'observe.gdb', out/'manifest.json']})
    receipt = dict(passed=passed, exit=code, timeout=timeout, elapsed=time.monotonic()-start,
                   command=command, engine_sha256=ENGINE_SHA, inputs=inputs,
                   events_sha256=sha(out/'events.json') if events is not None else None,
                   scope='Authored COM, internal DOS, normal PC-98 core, 36000 cycles/ms. Two external keyboard requests hold through two actual emulator repeats. API calls preserve guest CPU, 640KiB RAM and fractional time. Read-only UART/IRQ/BIOS observations include two held-key repeat cycles. Not TH04 V86 timing, physical hardware or cross-emulator acceptance. No game image is loaded or modified.')
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print('PC98 HELD REPEAT', passed, 'exit', code, 'timeout', timeout, flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
