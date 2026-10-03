#!/usr/bin/env python3
"""Compare native player movement with the pinned DOS player_move CPU body."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from datetime import datetime, timezone

import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_BP, UC_X86_REG_IP


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--runner')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = args.target.read_bytes()
    if len(data) != 156258 or sha(data) != '077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b':
        raise ValueError('MAIN target identity mismatch')
    header = struct.unpack_from('<H', data, 8)[0]*16
    if header != 6144 or struct.unpack_from('<H', data, 6)[0] != 1136:
        raise ValueError('MAIN header identity mismatch')
    engine = Uc(UC_ARCH_X86, UC_MODE_16)
    engine.mem_map(0, 0x110000)
    load = 0x2000
    engine.mem_write(load*16, data[header:])
    code_segment = load + 0x0aaf
    code_start = code_segment*16 + 0x5da8
    sentinel = code_segment*16 + 0xf000
    expected = []
    for high in range(16):
        for low in range(16):
            pressed = (high << 8) | low
            for reg,value in ((UC_X86_REG_CS,code_segment),(UC_X86_REG_DS,0x8000),
                              (UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xe000),(UC_X86_REG_BP,0xd000)):
                engine.reg_write(reg,value)
            engine.mem_write(0x7e000,struct.pack('<HH',0xf000,pressed))
            engine.mem_write(0x84656,bytes(4))
            engine.emu_start(code_start,sentinel,count=256)
            if engine.reg_read(UC_X86_REG_IP) != 0xf000 or engine.reg_read(UC_X86_REG_SP) != 0xe004:
                raise ValueError('original movement failed Pascal near return')
            vx,vy = struct.unpack('<hh',engine.mem_read(0x84656,4))
            expected.append(f'{pressed} {vx} {vy}')
    command = ([args.runner] if args.runner else []) + [str(args.exe.resolve()),'--movement-vectors']
    env = os.environ.copy(); env.setdefault('WINEDEBUG','-all')
    result = subprocess.run(command,capture_output=True,text=True,check=True,env=env)
    if result.stdout.strip().splitlines() != expected:
        raise ValueError('native movement differs from original DOS CPU')

    # Exhaustively check the independently generated mathematical constants
    # against maintained DOS data owners. This is source consistency, separate
    # from the target CPU evidence above; no table is extracted from an EXE.
    root = Path(__file__).resolve().parents[1]
    host = (root/'port64/motion_tables.hpp').read_text()
    host_sin = list(map(int,re.findall(r'-?\d+',host.split('sine_quarter{{')[1].split('}}')[0])))
    host_atan = list(map(int,re.findall(r'\d+',host.split('atan_ratio{{')[1].split('}}')[0])))
    dos = (root/'src/shared/math/trig_tables.asm').read_text()
    dos_sin = []
    for line in dos.splitlines():
        if line.strip().startswith('dw '): dos_sin += list(map(int,re.findall(r'-?\d+',line)))
    dos_atan = (root/'src/main/hardware/drawing_tables.asm').read_text().split('AtanTable8\tdb')[1].split(';')[0]
    dos_atan = list(map(int,re.findall(r'\d+',dos_atan.replace('db',''))))
    if host_sin != dos_sin[:65] or host_atan != dos_atan:
        raise ValueError('portable trig constants differ from maintained DOS owners')
    receipt = {
        'schema_version':1,'observed_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'passed':True,'target_sha256':sha(data),'native_sha256':sha(args.exe.read_bytes()),
        'body':{'artifact':'MAIN.EXE','load_segment':'2000','segment':'PLAYER_M_TEXT / main_01 0AAF',
                'offset':'5DA8','load_offset':'10898','file_offset':'12098','size':131},
        'cpu_cases':len(expected),'vectors_sha256':sha(('\n'.join(expected)+'\n').encode()),
        'unicorn_version':unicorn.__version__,
        'unicorn_engine_sha256':sha(Path(unicorn.unicorn._uc._name).read_bytes()),
        'trig_source_cases':len(host_sin)+len(host_atan),
        'limits':'Isolated movement primitive with initial zero velocity; full player_update death, shooting and PC-98 timing are outside this comparison.'
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'passed':True,'cpu_cases':len(expected),'receipt':str(args.output)}))


if __name__ == '__main__':
    main()
