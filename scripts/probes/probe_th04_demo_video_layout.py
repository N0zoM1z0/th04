#!/usr/bin/env python3
"""Attest the retained emulator's host video ABI with a small compiler probe."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import tarfile

from capture_th04_dos_demos import sha, ROOT
from build_th04_cpu_fault_emulator import ARCHIVE_SHA256, COMMIT
from compare_th04_dos_demos import require
from th04_demo_video import LAYOUT, SYMBOL_SIZES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emulator-receipt', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    require(not out.exists() and out.is_relative_to(ROOT/'.analysis'), 'fresh private video layout directory')
    os.nice(15)
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    emulator = json.loads(args.emulator_receipt.read_text())
    binary = Path(emulator['binary'])
    compiler = Path(emulator['compilers']['g++']['path'])
    source = binary.parent.parent
    require(emulator['source_commit'] == COMMIT and emulator['source_archive_sha256'] == ARCHIVE_SHA256
            and sha(args.archive.read_bytes()) == ARCHIVE_SHA256, 'pinned emulator archive')
    require(sha(binary.read_bytes()) == emulator['binary_sha256'], 'retained emulator binary')
    require(sha(compiler.read_bytes()) == emulator['compilers']['g++']['sha256'], 'retained emulator compiler')
    require(sha((source/'config.h').read_bytes()) == emulator['config_header_sha256'], 'compiled emulator config')
    out.mkdir(parents=True)
    code = '#include "dosbox.h"\n#include "vga.h"\n#include "mem.h"\n#include "pc98_gdc.h"\n#include <cstdio>\n#include <cstddef>\nint main(){\n'
    code += 'printf("{\\\"vga_size\\\":%zu,\\\"vga_mem_linear\\\":%zu,\\\"vga_mem_size\\\":%zu,\\\"gdc_size\\\":%zu",sizeof(VGA_Type),offsetof(VGA_Type,mem)+offsetof(VGA_Memory,linear),offsetof(VGA_Type,mem)+offsetof(VGA_Memory,memsize),sizeof(PC98_GDC_state));\n'
    for name in LAYOUT:
        if name not in ('vga_size', 'vga_mem_linear', 'vga_mem_size', 'gdc_size'):
            code += f'printf(",\\\"{name}\\\":%zu",offsetof(PC98_GDC_state,{name}));\n'
    code += 'puts("}");}\n'
    cpp = out/'layout.cpp'
    cpp.write_text(code)
    command = [str(compiler), '-std=gnu++14', '-O2', '-msse', '-DHAVE_CONFIG_H',
               '-D_XOPEN_SOURCE=700', '-D_POSIX_C_SOURCE=200809L', '-I.', '-Iinclude',
               '-MMD', '-MF', str(out/'layout.d'), str(cpp), '-o', str(out/'layout-probe')]
    compiled = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (out/'compile.log').write_text(compiled.stdout+compiled.stderr)
    require(compiled.returncode == 0, 'video ABI compilation')
    raw = subprocess.check_output([str(out/'layout-probe')])
    (out/'layout.json').write_bytes(raw)
    layout = json.loads(raw)
    require(layout == LAYOUT, 'host video ABI differs from reader')
    dependencies = shlex.split((out/'layout.d').read_text().partition(':')[2].replace('\\\n', ''))
    inputs = {str(source/'config.h'): emulator['config_header_sha256']}
    names = set()
    for name in dependencies:
        path = Path(name)
        path = path if path.is_absolute() else source/path
        if path != cpp and path != source/'config.h':
            require(path.is_relative_to(source), 'unexpected host probe dependency')
            names.add(str(path.relative_to(source)))
    names.update(('src/hardware/vga_memory.cpp', 'src/hardware/vga_draw.cpp',
                  'src/hardware/vga_pc98_dac.cpp', 'src/hardware/vga_pc98_gdc.cpp'))
    with tarfile.open(args.archive) as archive:
        for name in sorted(names):
            data = (source/name).read_bytes()
            require(archive.extractfile(source.name+'/'+name).read() == data,
                    'emulator video source differs from archive: '+name)
            inputs[str(source/name)] = sha(data)
    nm = subprocess.check_output(['nm', '-S', '--defined-only', str(binary)], text=True)
    (out/'symbols.txt').write_text(nm)
    symbols = {}
    for line in nm.splitlines():
        columns = line.split()
        if len(columns) == 4 and columns[3] in SYMBOL_SIZES:
            require(int(columns[1], 16) == SYMBOL_SIZES[columns[3]], 'ELF video symbol width')
            symbols[columns[3]] = dict(address=int(columns[0], 16), size=int(columns[1], 16))
    require(set(symbols) == set(SYMBOL_SIZES), 'ELF video symbol extent')
    receipt = dict(schema_version=1, passed=True, accepts_exact=False, layout=layout, symbols=symbols,
                   emulator_sha256=emulator['binary_sha256'], emulator_receipt_sha256=sha(args.emulator_receipt.read_bytes()),
                   source_archive_sha256=ARCHIVE_SHA256, compiler_sha256=sha(compiler.read_bytes()),
                   source_inputs=inputs, command=command, probe_source_sha256=sha(cpp.read_bytes()),
                   probe_binary_sha256=sha((out/'layout-probe').read_bytes()), layout_sha256=sha(raw),
                   nm_sha256=sha(nm.encode()), scope='compiler-observed host layout and pinned ELF widths; no emulator/game rebuild')
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(passed=True, sources=len(inputs), symbols=len(symbols), layout=layout)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
