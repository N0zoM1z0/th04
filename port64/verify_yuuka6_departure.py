#!/usr/bin/env python3
"""Original MAIN Final Stage departure through the nonreturning Ending entry.

Execute13A9:ACB3..AE86 at load2000, DS8000, stage_id5. All-clear9E06
is an explicit near-call observation adapter; end_game0AAF:0CC9 is the
nonreturning boundary. This checks call order/graze/clock/homing/palette,
not bonus math, MAINE execution, whole-route equality or DOS exactness.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

import unicorn
from unicorn.x86_const import (UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_SS,
    UC_X86_REG_SP, UC_X86_REG_BP, UC_X86_REG_IP, UC_X86_REG_EFLAGS)
from verify_transition import Original as Base
from verify import source_manifest

sha = lambda data: hashlib.sha256(data).hexdigest()

class Original(Base):
    def body(self, u, address, size, unused):
        cs = u.reg_read(UC_X86_REG_CS)
        ip = address - cs * 16
        if (cs, ip) == (0x33a9, 0x9e06):
            if self.reject:
                raise ValueError('injected all-clear callback rejection')
            self.events.append('6 0')
            sp = u.reg_read(UC_X86_REG_SP)
            off = struct.unpack('<H', u.mem_read(0x70000 + sp, 2))[0]
            u.reg_write(UC_X86_REG_SP, sp + 2)
            u.reg_write(UC_X86_REG_IP, off)
            return
        if (cs, ip) == (0x2aaf, 0xcc9):
            self.events.append('7 0')
            self.ending = True
            u.emu_stop()
            return
        super().body(u, address, size, unused)

    def execute(self, row):
        frame, graze, stage_graze, tone, changed, x, y = row
        self.seed_departure([frame, graze, stage_graze, 5, 53, 93,
                             tone, changed, x, y, 72, 0])
        self.write(0x5394, 'B', 5)
        self.events = []
        self.error = None
        self.ending = False
        u = self.u
        for reg, value in ((UC_X86_REG_CS, 0x33a9), (UC_X86_REG_DS, 0x8000),
                (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xe000),
                (UC_X86_REG_BP, 0xd000), (UC_X86_REG_EFLAGS, 2)):
            u.reg_write(reg, value)
        u.mem_write(0x7e000, struct.pack('<H', 0xf000))
        u.emu_start(0x33a90 + 0xacb3, 0x33a90 + 0xf000, count=200000)
        if self.error:
            raise RuntimeError('Final Stage original callback rejected') from self.error
        if not self.ending and (u.reg_read(UC_X86_REG_IP) != 0xf000 or
                               u.reg_read(UC_X86_REG_SP) != 0xe002):
            raise ValueError('Final Stage original return/stack differs')
        values = [self.read(0x53da, 'h')[0],
                  struct.unpack('<H', u.mem_read(0x90038, 2))[0],
                  self.read(0xbcbc, 'H')[0], self.read(0x3a4, 'h')[0],
                  self.read(0x5393, 'B')[0], *self.read(0x4642, '2h'),
                  int(self.ending)]
        if u.mem_read(0x90011, 1)[0] != 5 or u.mem_read(0x90013, 1)[0] != 53 or self.read(0x5392, 'B')[0] != 93:
            raise ValueError('Final Stage incorrectly advanced resident stage/quit')
        return 'F ' + ' '.join(map(str, values)) + '|' + '|'.join(self.events)

def fixtures():
    for frame, graze, stage_graze, tone, changed, xy in itertools.product(
            (-32768, -1, 0, 1, 63, 415, 416, 32767),
            (0, 65535), (0, 2, 65535), (0, 113), (0, 255),
            ((123, -456), (-15984, -15984))):
        yield [frame, graze, stage_graze, tone, changed, *xy]
    # Complete clock coverage with each call independently seeded from the
    # preceding departure's known state. Full live-route continuity is a
    # separate --stage6-screenshots check; these are bounded CPU calls.
    for graze, stage_graze in itertools.product((0, 65535), (2, 65535)):
        for frame in range(417):
            yield [frame, graze if not frame else (graze + stage_graze) & 65535,
                   stage_graze, 113 if not frame else 60, 0 if not frame else 1,
                   *([123, -456] if not frame else [-15984, -15984])]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('target', 'exe', 'output-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--runner')
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    manifest = source_manifest(root)[0]
    original = Original(args.target.read_bytes())
    original.reject = False
    rows = list(fixtures())
    expected = [original.execute(row) for row in rows]
    original.reject = True
    try:
        original.execute([0, 65535, 2, 113, 0, 123, -456])
    except RuntimeError as error:
        if not isinstance(error.__cause__, ValueError):
            raise
    else:
        raise ValueError('all-clear callback rejection swallowed')
    fixture = out / 'fixtures.txt'
    fixture.write_text('\n'.join(' '.join(map(str, row)) for row in rows) + '\n')
    trace = out / 'trace.txt'
    trace.write_text('\n'.join(expected) + '\n')
    env = os.environ.copy()
    env.setdefault('WINEDEBUG', '-all')
    command = ([args.runner] if args.runner else []) + [str(args.exe.resolve()), '--final-vectors', str(fixture)]
    actual = subprocess.run(command, check=True, capture_output=True, text=True, env=env).stdout.splitlines()
    if actual != expected:
        at = next((i for i, pair in enumerate(zip(actual, expected)) if pair[0] != pair[1]), min(len(actual), len(expected)))
        raise ValueError(f'Final Stage departure mismatch at row {at}: {rows[at]}')
    changed = list(actual)
    boundary = next(i for i, row in enumerate(rows) if row[0] == 416)
    changed[boundary] = changed[boundary].replace('|7 0', '|3 10')
    if changed == expected:
        raise ValueError('Ending-versus-fade negative control failed')
    if manifest != source_manifest(root)[0]:
        raise ValueError('source changed during Final Stage departure controls')
    receipt = dict(passed=True, cases=len(rows), original_cpu_reexecuted=True,
        callback_rejection_passed=True, ending_vs_fade_negative_passed=True,
        source_manifest_sha256=manifest, target_sha256=sha(original.target),
        native_sha256=sha(args.exe.read_bytes()), fixture_sha256=sha(fixture.read_bytes()),
        trace_sha256=sha(trace.read_bytes()), unicorn_version=unicorn.__version__,
        unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()),
        observed_utc=datetime.now(timezone.utc).isoformat(), scope=__doc__)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Yuuka6 Final Stage departure:', len(rows), 'PASS')

if __name__ == '__main__':
    main()
