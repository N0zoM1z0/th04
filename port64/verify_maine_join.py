#!/usr/bin/env python3
"""Original CPU controls for MAIN's Ending transfer and MAINE audio/palette ABI.

Release/exec, VSync and audio device consumers are explicit adapters. Resident
copies, end metadata, counters, fade loops, palette arithmetic and sound-mode
branches execute original instructions. These bounded controls do not emulate
DOS process replacement, physical audio or a complete game.
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
from unicorn.x86_const import *
from verify_score import Original as MainBase
from verify_cutscene import Original as MaineBase
from verify import source_manifest

sha = lambda data: hashlib.sha256(data).hexdigest()
FIELDS = ((0x1868, 0x26), (0x2398, 0x28), (0x239a, 0x2a),
          (0x239c, 0x2c), (0x239e, 0x2e), (0x1b5e, 0x34), (0x1b60, 0x36))
RELEASES = {(0x2aaf, 0x6aab): ('text', False), (0x330e, 0x9ae): ('cdg', True),
            (0x33a9, 0xa544): ('boss', True), (0x2aaf, 0x242e): ('dialog', False),
            (0x2aaf, 0x5499): ('player', False), (0x2aaf, 0xcae): ('std', False),
            (0x2aaf, 0xecb): ('map', False), (0x2000, 0x2748): ('super', True),
            (0x2000, 0x1d4a): ('graphics', True), (0x2000, 0x2254): ('text-clear', True),
            (0x2000, 0x1a5a): ('gaiji', True), (0x330e, 0x53e): ('game-exit', True)}

def return_to_caller(u, args=0, far=True):
    sp = u.reg_read(UC_X86_REG_SP)
    values = struct.unpack('<HH' if far else '<H', u.mem_read(0x70000+sp, 4 if far else 2))
    u.reg_write(UC_X86_REG_SP, sp+(4 if far else 2)+args)
    if far:
        u.reg_write(UC_X86_REG_CS, values[1])
    u.reg_write(UC_X86_REG_IP, values[0])

class Main(MainBase):
    def hook(self, u, address, size, unused):
        try:
            self.control(u, address)
        except Exception as error:
            self.error = error
            u.emu_stop()

    def control(self, u, address):
        cs = u.reg_read(UC_X86_REG_CS)
        ip = address-cs*16
        sp = u.reg_read(UC_X86_REG_SP)
        key = (cs, ip)
        if (cs == 0x2aaf and (0x3cee <= ip < 0x3db1 or 0xcc9 <= ip < 0xd1f or 0x158 <= ip < 0x174)
                or cs == 0x2000 and 0x666 <= ip < 0x6a2):
            return
        if key in RELEASES:
            name, far = RELEASES[key]
            self.calls.append(name)
            assert self.published() == self.expected
            return_to_caller(u, far=far)
        elif key == (0x2000, 0x41b4):
            assert bytes(u.mem_read(0x9001d, 8)) == self.digits
            assert u.mem_read(0x90026, 2) == b'\xa5\xa5'
            assert struct.unpack('<H', u.mem_read(0x70000+sp+4, 2))[0] == self.ems
            self.calls.append('ems')
            return_to_caller(u, 2)
        elif key == (0x330e, 0x2fc):
            assert struct.unpack('<H', u.mem_read(0x70000+sp+4, 2))[0] == 0x204
            self.calls.append('song-fade4')
            assert tuple(u.mem_read(0x90025, 1))+tuple(u.mem_read(0x90030, 1)) == ((49, 254) if self.bad else (48, 255))
            return_to_caller(u, 2)
        elif key == (0x2000, 0x2462):
            self.ticks += 1
            return_to_caller(u)
        elif key == (0x2000, 0x1f04):
            self.fade.append(f'{self.ticks} {self.read(0x3a4, "H")[0]}')
            return_to_caller(u)
        elif key == (0x2000, 0xa375):
            pointers = struct.unpack('<6H', u.mem_read(0x70000+sp+4, 12))
            assert pointers[:2] == pointers[2:4] and pointers[4:] == (0, 0)
            assert bytes(u.mem_read(pointers[1]*16+pointers[0], 6)) == b'maine\0'
            self.calls.append('execl')
            u.reg_write(UC_X86_REG_AX, 0xffff)
            return_to_caller(u)  # Explicit execl FAILURE return/stack control.
        else:
            raise ValueError(f'unexpected original MAIN consumer {cs:04X}:{ip:04X}')

    def published(self):
        r = bytes(self.u.mem_read(0x90000, 256))
        return [r[0x30], r[0x25], *[struct.unpack_from('<H', r, b)[0] for a, b in FIELDS],
                *struct.unpack_from('<II', r, 0x40), *r[0x1d:0x25], self.read(0x435a, 'I')[0]]

    def handoff(self, values, ems):
        bad, *data = values
        counts, slow, total, pending, digits = data[:7], data[7], data[8], data[9], data[10:]
        self.reset()
        self.error = None; self.calls = []; self.fade = []; self.ticks = 0
        self.ems = ems; self.bad = bad; self.digits = bytes(digits)
        self.expected = [254 if bad else 255, 49 if bad else 48, *counts, slow, total, *digits, pending]
        self.u.mem_write(0x90000, b'\xa5'*256)
        self.write(0xba86, 'HH', 0, 0x9000)
        self.write(0x539e, 'H', ems)
        self.write(0x3e2, 'I', 0x12345678)
        self.write(0x435a, 'I', pending)
        self.u.mem_write(0x84349, self.digits)
        for (a, b), value in zip(FIELDS, counts):
            self.write(a, 'H', value)
        self.write(0x1860, 'II', slow, total)
        self.call_args(0xcf4 if bad else 0xcc9, far=True, cs=0x2aaf)
        if self.error:
            raise RuntimeError('MAIN handoff adapter rejected') from self.error
        assert self.published() == self.expected
        assert self.read(0x3e2, 'I')[0] == 0x12345678
        assert self.calls == ['song-fade4']+(['ems'] if ems else [])+[v[0] for v in RELEASES.values()]+['execl']
        assert self.ticks == 273 and self.fade[-1] == '273 0'
        return ' '.join(map(str, self.published()))

    def counter(self, values):
        slow, total, refreshes, threshold = values
        self.reset(); self.error = None
        self.write(0x1860, 'II', slow, total); self.write(0x2ab2, 'H', refreshes); self.write(0x5390, 'H', threshold)
        for reg, value in ((UC_X86_REG_CS, 0x2aaf), (UC_X86_REG_DS, 0x8000), (UC_X86_REG_EFLAGS, 2)):
            self.u.reg_write(reg, value)
        self.u.emu_start(0x2aaf0+0x158, 0x2aaf0+0x174, count=20)
        if self.error:
            raise RuntimeError('MAIN counter adapter rejected') from self.error
        assert self.u.reg_read(UC_X86_REG_IP) == 0x174
        return ' '.join(map(str, self.read(0x1860, 'II')))

class Maine(MaineBase):
    def body(self, u, address):
        cs = u.reg_read(UC_X86_REG_CS); ip = address-cs*16; relative = cs-self.load
        if cs == self.entry_cs and ip == 0xff00:
            self.done = True; u.emu_stop(); return
        if (self.mode == 'palette' and relative == 0 and 0x19ec <= ip < 0x1a55
                or self.mode == 'sound' and relative == 0xcc7 and 0x3d6 <= ip < 0x405):
            return
        if self.mode == 'sound' and (relative, ip) == (0xcc7, 0x33):
            sp = u.reg_read(UC_X86_REG_SP)
            self.fallbacks.append(struct.unpack('<H', u.mem_read(0x70000+sp+4, 2))[0])
            return_to_caller(u, 2); return
        raise ValueError(f'unexpected original MAINE consumer {relative:04X}:{ip:04X}')

    def port(self, u, port, size, value, unused):
        if self.mode == 'palette' and size == 1 and port in (0xa8, 0xac, 0xaa, 0xae):
            self.outputs.append((port, value)); return
        self.error = ValueError('unexpected original palette port'); u.emu_stop()

    def interrupt(self, u, number, unused):
        try:
            assert self.mode == 'sound'
            assert number == (0x61 if self.sound_mode == 3 else 0x60)
            if self.sound_mode == 3:
                assert u.reg_read(UC_X86_REG_DX) == 0xc0
            else:
                assert u.reg_read(UC_X86_REG_AX) >> 8 == 5
            u.reg_write(UC_X86_REG_AX, next(self.samples)); self.polls += 1
        except Exception as error:
            self.error = error; u.emu_stop()

    def invoke(self, mode, cs, ip, args=()):
        self.mode = mode; self.entry_cs = self.load+cs; self.done = False; self.error = None
        self.outputs = []; self.fallbacks = []; self.polls = 0
        for reg, value in ((UC_X86_REG_CS, self.entry_cs), (UC_X86_REG_DS, self.ds),
                           (UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0xff00),
                           (UC_X86_REG_BP, 0), (UC_X86_REG_EFLAGS, 2)):
            self.u.reg_write(reg, value)
        self.u.mem_write(0x7ff00, struct.pack('<'+'H'*(2+len(args)), 0xff00, self.entry_cs, *args))
        self.u.emu_start(self.entry_cs*16+ip, 0x10ffff, count=10000)
        if self.error:
            raise RuntimeError('MAINE sound/palette adapter rejected') from self.error
        assert self.done and self.u.reg_read(UC_X86_REG_SP) == 0xff04+len(args)*2

def run(args, *options):
    env = os.environ.copy(); env.setdefault('WINEDEBUG', '-all')
    return subprocess.check_output(([args.runner] if args.runner else [])+[str(args.exe.resolve()), *map(str, options)],
                                   env=env, text=True).splitlines()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('target', 'maine', 'decoded', 'exe', 'output-dir'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--runner'); args = p.parse_args()
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    manifest, _ = source_manifest(Path(__file__).resolve().parents[1])
    original = Main(args.target.read_bytes())
    handoffs = []
    for bad, marker in itertools.product((0, 1), (0, 1, 255, 32767, 32768, 65535)):
        counts = [(marker+i*977)&65535 for i in range(7)]
        for pending in (0, 195552, 0xffffffff):
            handoffs.append([bad, *counts, (marker*65537)&0xffffffff, (0xffffffff-marker)&0xffffffff,
                             pending, *[(marker+i*71)&255 for i in range(8)]])
    path = out/'handoff-fixtures.txt'; path.write_text(''.join(' '.join(map(str, r))+'\n' for r in handoffs))
    expected = [original.handoff(r, 0) for r in handoffs]
    assert expected == [original.handoff(r, 0x1234) for r in handoffs]
    (out/'handoff-trace.txt').write_text('\n'.join(expected)+'\n')
    assert run(args, '--handoff', path) == expected
    assert run(args, '--fade') == original.fade
    (out/'fade-trace.txt').write_text('\n'.join(original.fade)+'\n')
    counters = list(itertools.product((0, 1, 0xffffffff), (0, 1, 0xffffffff),
                                      (0, 1, 2, 3, 32767, 32768, 65535), (0, 1, 2, 3, 32768, 65535)))
    path = out/'frame-fixtures.txt'; path.write_text(''.join(' '.join(map(str, r))+'\n' for r in counters))
    frame_reference = [original.counter(r) for r in counters]
    (out/'frame-trace.txt').write_text('\n'.join(frame_reference)+'\n')
    assert run(args, '--frames', path) == frame_reference
    sound_cases = palette_cases = 0
    for load in (0x1000, 0x2000):
        maine = Maine(args.maine, args.decoded, load)
        maine.u.hook_add(unicorn.UC_HOOK_INTR, maine.interrupt)
        for tone in (-32768, -1, 0, 1, 60, 94, 100, 106, 199, 200, 201, 32767):
            palette = bytes((i*73+29)&255 for i in range(48))
            maine.write(0x132, 'h', tone); maine.write(0x164, 'H', 0)
            maine.u.mem_write(maine.ds*16+0xeca, palette)
            maine.invoke('palette', 0, 0x19ec)
            t = max(0, min(200, tone)); outputs = []
            for index in range(16):
                outputs.append((0xa8, index))
                for channel, port in enumerate((0xac, 0xaa, 0xae)):
                    nibble = palette[index*3+channel] >> 4
                    value = nibble*t//100 if t <= 100 else 15-(15-nibble)*(200-t)//100
                    outputs.append((port, value))
            assert maine.outputs == outputs
            palette_cases += 1
        for mode, fallback, goal in itertools.product((0, 1, 2, 3), (0, 1, 4, 999, 65535), (0, 3, 65535)):
            maine.sound_mode = mode; maine.samples = iter((0, max(0, goal-1), goal))
            maine.write(0x5a1, 'B', mode)
            maine.invoke('sound', 0xcc7, 0x3d6, (fallback, goal))
            assert maine.fallbacks == ([fallback] if mode == 0 else [])
            assert maine.polls == (0 if mode == 0 else 1 if goal == 0 else 3)
            sound_cases += 1
    final_manifest, _ = source_manifest(Path(__file__).resolve().parents[1]); assert manifest == final_manifest
    receipt = dict(passed=True, observed_utc=datetime.now(timezone.utc).isoformat(), source_manifest_sha256=manifest,
                   main_sha256=sha(original.target), maine_sha256=sha(args.maine.read_bytes()),
                   exe_sha256=sha(args.exe.read_bytes()), handoff_cases=len(handoffs)*2,
                   frame_counter_cases=len(counters), main_fade_refreshes=273,
                   main_fade_palette_calls=len(original.fade), sound_cases=sound_cases, palette_cases=palette_cases,
                   handoff_lines_sha256=sha(('\n'.join(expected)+'\n').encode()),
                   scope='Bounded original instructions with explicit release/execl-failure, VSync and audio-device adapters. Native MAIN-to-MAINE publication/lifetime; no full DOS process execution, physical palette capture, music synthesis or complete-game claim.')
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n'); print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
