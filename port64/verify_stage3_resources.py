#!/usr/bin/env python3
"""Check original Stage3 setup requests and native Elly portrait composition.

The original BFNT/CDG/BB loaders are request adapters, not emulated file or VRAM
consumers. Independently decoded archive pixels check native asset selection and
palette composition; this is not a complete original-game screenshot Oracle.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
import subprocess
from pathlib import Path
import struct

from PIL import Image
import unicorn
from unicorn.x86_const import UC_X86_REG_CS, UC_X86_REG_SP
from probe_assets import main_assets
from verify_session import Original as Base
from verify import source_manifest


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Original(Base):
    def __init__(self, target):
        self.resources = []
        super().__init__(target)

    def body(self, u, address, size, unused):
        cs = u.reg_read(UC_X86_REG_CS)
        ip = address - cs * 16
        sp = u.reg_read(UC_X86_REG_SP)
        if (cs, ip) in ((0x2000, 0x2a74), (0x330e, 0x858), (0x33a9, 0xa518)):
            skip = 4 if cs != 0x33a9 else 2
            args = struct.unpack('<4H', u.mem_read(0x70000 + sp + skip, 8))
            off, seg = args[1:3] if cs == 0x330e else args[:2]
            raw = bytes(u.mem_read(seg * 16 + off, 24))
            name = raw.split(b'\0', 1)[0].decode('ascii')
            self.resources.append(dict(name=name, image=args[0] if cs == 0x330e else None,
                                       slot=args[3] if cs == 0x330e else None))
        super().body(u, address, size, unused)


def verify(hdi, frames, target, exe, runner, output):
    assets = main_assets(hdi)  # Independent Python FAT/PAR with archive identity.
    bft, bmt, faces = (assets[n] for n in ('ST02.BFT', 'ST02.BB2', 'BSS2.CD2'))
    for body, extent in ((bft, (32, 32, 0, 15)), (assets['ST02.BMT'], (64, 64, 0, 3)), (bmt, (64, 64, 0, 11))):
        if body[:5] != b'BFNT\x1a' or struct.unpack_from('<4H', body, 8) != extent:
            raise ValueError('Stage3 BFNT geometry changed')
    start = 32 + struct.unpack_from('<H', bmt, 28)[0]
    raw = bmt[start:start+48]
    palette = [tuple((raw[i+c] >> 4)*17 for c in (1, 2, 0)) for i in range(0, 48, 3)]
    if tuple(struct.unpack_from('<3H', faces)) != (2048, 128, 128) or faces[10:12] != b'\x04\x01':
        raise ValueError('Stage3 portrait geometry changed')
    original = Original(target.read_bytes())
    class Rejecting(Original):
        def body(self, u, address, size, unused):
            if address == 0x33a90 + 0xa6f6:
                raise ValueError('injected Stage3 setup rejection')
            super().body(u, address, size, unused)
    rejected = Rejecting(original.target)
    try:
        rejected.call_args(0xa6f6, far=True)
    except (RuntimeError, ValueError):
        if not isinstance(rejected.error, ValueError):
            raise
    else:
        raise ValueError('original resource callback rejection silently passed')
    setups = []
    for rank in range(5):
        original.resources = []
        # Reset DS from the pinned target, seed rank, then execute642C/A6F6.
        original.reset(); original.error = None; original.write(0x4348, 'B', rank)
        original.call_args(0x642c, far=True); original.call_args(0xa6f6, far=True)
        if original.error:
            raise RuntimeError('original Stage3 request adapter rejected') from original.error
        wanted = [dict(name='st02.bmt', image=None, slot=None),
                  dict(name='st02bk.cdg', image=0, slot=16),
                  dict(name='st02.bb', image=None, slot=None)]
        if original.resources != wanted:
            raise ValueError('original Stage3 resource requests differ')
        setups.append(dict(rank=rank, requests=list(original.resources)))
    inputs, expected = [], []
    for rank, marker in itertools.product(range(5), range(256)):
        original.reset(); original.error = None; original.resources = []
        actor = bytes((marker+i*73)&255 for i in range(22))
        hpbar, angle = marker*257-32768, marker^85
        original.u.mem_write(0x853b4, actor)
        original.write(0x46b2, 'B', 255); original.write(0x1ed0, 'h', hpbar)
        original.write(0x1ed2, 'B', angle); original.write(0x4348, 'B', rank)
        original.call_args(0x642c, far=True); original.call_args(0xa6f6, far=True)
        if original.error: raise RuntimeError('original retained Stage3 setup rejected') from original.error
        if original.read(0x46bc, '<3H') != (0x9fb,0x33a9,0x1d95):
            raise ValueError('Stage3 callback ownership changed')
        inputs.append(' '.join(map(str,(rank,*actor,255,hpbar,angle))))
        expected.append(' '.join((original.u.mem_read(0x853b4,22).hex(),
                        str(original.read(0x46b2,'B')[0]),str(original.read(0x1ed0,'h')[0]),str(original.read(0x1ed2,'B')[0]))))
    fixture = output.parent/'setup-fixtures.txt'; fixture.write_text('\n'.join(inputs)+'\n')
    env=os.environ.copy();env.setdefault('WINEDEBUG','-all')
    command=([runner] if runner else [])+[str(exe.resolve()),'--setup-vectors',str(fixture.resolve())]
    actual=subprocess.run(command,capture_output=True,text=True,check=True,env=env).stdout.splitlines()
    for i,(got,want) in enumerate(itertools.zip_longest(actual,expected)):
        if got != want: raise ValueError(f'retained Stage3 setup case{i} differs: {got} != {want}')
    trace=output.parent/'setup-trace.txt';trace.write_text('\n'.join(expected)+'\n')
    checks = []
    for rank in ('normal', 'lunatic'):
        for character in ('reimu', 'marisa'):
            for shooting in ('shot', 'idle'):
                path = frames / f'{rank}-{character}-{shooting}-7.bmp'
                with Image.open(path) as image:
                    image = image.convert('RGB'); checked = 0; used = set()
                    for y in range(128):
                        for x in range(128):
                            offset = (127-y)*16+x//8; mask = 0x80>>(x%8)
                            if not faces[16+offset]&mask: continue
                            color = sum(1<<p for p in range(4) if faces[16+(p+1)*2048+offset]&mask)
                            if image.getpixel((288+x,112+y)) != palette[color]:
                                raise ValueError(f'Elly asset/palette pixel differs: {path.name} {x},{y}')
                            checked += 1; used.add(color)
                    checks.append(dict(image=path.name,opaque_pixels=checked,palette_indices=sorted(used),bmp_sha256=sha(path.read_bytes())))
    names = ('ST02.BFT', 'ST02.BMT', 'ST02.MPN', 'ST02.MAP', 'ST02.STD',
             'ST02BK.CDG', 'ST02.BB', 'BSS2.CD2', '_DM02.TXT', '_DM12.TXT', 'ST02.BB1', 'ST02.BB2')
    return dict(passed=True, callback_rejection_passed=True, original_setups=setups, portrait_checks=checks,
                retained_midboss_setup_controls=len(inputs),native_sha256=sha(exe.read_bytes()),
                setup_fixture_sha256=sha(fixture.read_bytes()),setup_trace_sha256=sha(trace.read_bytes()),
                hdi_sha256=sha(hdi.read_bytes()), target_sha256=sha(target.read_bytes()),
                asset_sha256={n: sha(assets[n]) for n in names},
                scope='Actual MAIN13A9:A6F6..A7B4 resource requests across five rank seeds; 1280 retained 22-byte midboss setup/active/shared HP-bar and defeat-angle controls; independent archive geometry and Stage3 palette/Elly portrait0 pixels in eight native routes; pre-dialog BB2 supplies the active palette.',
                limits='Original BFNT/CDG/BB loader requests intercepted. Native composition checked against asset pixels, not original VRAM; no full Stage3 route, hardware timing, GUI pacing or DOS exact claim.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--hdi', type=Path, required=True)
    p.add_argument('--frames', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--exe', type=Path, required=True)
    p.add_argument('--runner')
    a = p.parse_args()
    manifest, _ = source_manifest(Path(__file__).resolve().parents[1])
    a.output.parent.mkdir(parents=True, exist_ok=True)
    receipt = verify(a.hdi, a.frames, a.target,a.exe,a.runner,a.output)
    after, _ = source_manifest(Path(__file__).resolve().parents[1])
    if manifest != after:
        raise ValueError('source changed during resource verification')
    receipt.update(source_manifest_sha256=manifest, observed_utc=datetime.now(timezone.utc).isoformat())
    receipt.update(unicorn_version=unicorn.__version__,
                   unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print('Stage3 resource requests and independent Elly portrait pixels: PASS')


if __name__ == '__main__':
    main()
