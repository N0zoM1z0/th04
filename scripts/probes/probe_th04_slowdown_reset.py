#!/usr/bin/env python3
"""Execute the attested MAIN delay owner with synthetic VSync counts, no PC-98 timing claim."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

import unicorn
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_IP, UC_X86_REG_DS, UC_X86_REG_SS, UC_X86_REG_SP

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from lib.pc98 import parse_mz


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists() and args.output.resolve().is_relative_to(ROOT / '.analysis')
    target = ROOT / '.analysis/targets/th04/main.exe'
    raw = target.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert len(raw)==156258 and digest=='077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b'
    mz = parse_mz(raw)
    assert mz.valid
    start = 0xAAF2
    assert not any(start-1 <= r.linear < start+26 for r in mz.relocations)
    library = next(p for p in Path(unicorn.__file__).parent.rglob('libunicorn.so*') if p.is_file())

    def run(delay, ticks, skip_reset=False):
        vm = Uc(UC_ARCH_X86, UC_MODE_16)
        vm.mem_map(0, 0x110000)
        vm.mem_write(0x20000, mz.program_image)
        cs = 0x2AAF
        for reg, value in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,2),(UC_X86_REG_DS,0x8000),
                           (UC_X86_REG_SS,0x7000),(UC_X86_REG_SP,0xFF00)]:
            vm.reg_write(reg,value)
        vm.mem_write(0x7FF00,struct.pack('<H',0x100))
        vm.mem_write(0x82AB2,struct.pack('<H',ticks))
        vm.mem_write(0x85390,struct.pack('<H',delay))
        returned = False

        def hook(uc, address, size, data):
            nonlocal returned
            if address==cs*16+0x100:
                returned=True
                uc.emu_stop()
            elif skip_reset and address==cs*16+0x14:
                # Counterfactual control skips one instruction by PC, while
                # the target file and all loaded instruction bytes stay intact.
                uc.reg_write(UC_X86_REG_IP,0x1A)

        vm.hook_add(UC_HOOK_CODE,hook)
        vm.emu_start(cs*16+2,0x100000,count=200)
        after_ticks=struct.unpack('<H',bytes(vm.mem_read(0x82AB2,2)))[0]
        after_delay=struct.unpack('<H',bytes(vm.mem_read(0x85390,2)))[0]
        return dict(delay=delay,ticks=ticks,returned=returned,after_ticks=after_ticks,after_delay=after_delay)

    cases=[]
    for delay in (1,2,3):
        for ticks in (delay,delay+1):
            case=run(delay,ticks)
            assert case['returned'] and case['after_ticks']==0 and case['after_delay']==1
            cases.append(case)
    for delay,ticks in ((2,1),(3,2)):
        case=run(delay,ticks)
        assert not case['returned'] and case['after_ticks']==ticks and case['after_delay']==delay
        cases.append(case)
    negative=run(2,2,True)
    assert negative['returned'] and negative['after_delay']==2
    report=dict(passed=True,target_sha256=digest,canonicality='candidate-local-attested',
                artifact='th04-main',segment='SLOWDOWN_TEXT',relative_cs='0AAF',offset='0002',
                file_offset='C2F2',extent=26,load_segment='2000',ds='8000',
                module_sha256=hashlib.sha256(mz.program_image).hexdigest(),
                relocations=len(mz.relocations),unicorn_version=unicorn.__version__,
                engine_path=str(library),engine_sha256=hashlib.sha256(library.read_bytes()).hexdigest(),
                cases=cases,skip_store_control=negative,
                scope='Original instructions, synthetic counters/DS/stack; proves request reset and busy wait only, not a full game or physical timing.')
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(cases),skip_store_rejected=True)))


if __name__=='__main__':
    main()
