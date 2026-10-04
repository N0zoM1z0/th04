#!/usr/bin/env python3
"""Check original Stage2 setup requests and native Kurumi portrait composition.

The original BFNT/CDG/BB loaders are request adapters, not emulated file or VRAM
consumers. Independently decoded archive pixels check native asset selection and
palette composition; this is not a complete original-game screenshot Oracle.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
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


def verify(hdi, frames, target):
    assets = main_assets(hdi)  # Independent Python FAT/PAR with archive identity.
    bft, bmt, faces = (assets[n] for n in ('ST01.BFT', 'ST01.BMT', 'BSS1.CD2'))
    for body, extent in ((bft, (32, 32, 0, 17)), (bmt, (64, 64, 0, 15))):
        if body[:5] != b'BFNT\x1a' or struct.unpack_from('<4H', body, 8) != extent:
            raise ValueError('Stage2 BFNT geometry changed')
    start = 32 + struct.unpack_from('<H', bmt, 28)[0]
    raw = bmt[start:start+48]
    palette = [tuple((raw[i+c] >> 4)*17 for c in (1, 2, 0)) for i in range(0, 48, 3)]
    if tuple(struct.unpack_from('<3H', faces)) != (2048, 128, 128) or faces[10:12] != b'\x04\x01':
        raise ValueError('Stage2 portrait geometry changed')
    original = Original(target.read_bytes())
    class Rejecting(Original):
        def body(self, u, address, size, unused):
            if address == 0x33a90 + 0xa623:
                raise ValueError('injected Stage2 setup rejection')
            super().body(u, address, size, unused)
    rejected = Rejecting(original.target)
    try:
        rejected.call_args(0xa623, far=True)
    except (RuntimeError, ValueError):
        if not isinstance(rejected.error, ValueError):
            raise
    else:
        raise ValueError('original resource callback rejection silently passed')
    setups = []
    for rank in range(5):
        original.resources = []
        # Reset DS from the pinned target, seed rank, then execute642C/A623.
        original.reset(); original.error = None; original.write(0x4348, 'B', rank)
        original.call_args(0x642c, far=True); original.call_args(0xa623, far=True)
        if original.error:
            raise RuntimeError('original Stage2 request adapter rejected') from original.error
        wanted = [dict(name='st01.bmt', image=None, slot=None),
                  dict(name='st01bk.cdg', image=0, slot=16),
                  dict(name='st01.bb', image=None, slot=None)]
        if original.resources != wanted:
            raise ValueError('original Stage2 resource requests differ')
        setups.append(dict(rank=rank, requests=original.resources))
    checks = []
    for rank in ('normal', 'lunatic'):
        for character in ('reimu', 'marisa'):
            path = frames / f'{rank}-{character}-6.bmp'
            with Image.open(path) as image:
                image = image.convert('RGB')
                checked = 0
                used = set()
                for y in range(128):
                    for x in range(128):
                        offset = (127-y)*16 + x//8
                        mask = 0x80 >> (x % 8)
                        if not faces[16+offset] & mask:
                            continue
                        color = sum(1 << p for p in range(4) if faces[16+(p+1)*2048+offset] & mask)
                        if image.getpixel((288+x, 112+y)) != palette[color]:
                            raise ValueError(f'Kurumi asset/palette pixel differs: {path.name} {x},{y}')
                        checked += 1; used.add(color)
                checks.append(dict(image=path.name, opaque_pixels=checked, palette_indices=sorted(used),
                                   bmp_sha256=sha(path.read_bytes())))
    names = ('ST01.BFT', 'ST01.BMT', 'ST01.MPN', 'ST01.MAP', 'ST01.STD',
             'ST01BK.CDG', 'ST01.BB', 'BSS1.CD2', '_DM01.TXT', '_DM11.TXT')
    return dict(passed=True, callback_rejection_passed=True, original_setups=setups, portrait_checks=checks,
                hdi_sha256=sha(hdi.read_bytes()), target_sha256=sha(target.read_bytes()),
                asset_sha256={n: sha(assets[n]) for n in names},
                scope='Actual MAIN13A9:A623..A6F5 resource requests across five rank seeds; independent archive geometry and Stage2 palette/Kurumi portrait0 pixels in four native routes.',
                limits='Original BFNT/CDG/BB loader requests intercepted. Native composition checked against asset pixels, not original VRAM; no full Stage2 route, hardware timing, GUI pacing or DOS exact claim.')


def verify_battle_backdrop(hdi, frames):
    assets = main_assets(hdi)
    body, bmt = assets['ST01BK.CDG'], assets['ST01.BMT']
    plane, width, height = struct.unpack_from('<3H', body)
    if (plane, width, height, body[10], body[11], len(body)) != (5376, 384, 112, 1, 0, 21520):
        raise ValueError('Stage2 backdrop archive geometry changed')
    start = 32 + struct.unpack_from('<H', bmt, 28)[0]
    raw = bmt[start:start+48]
    palette = [tuple((raw[i+c] >> 4)*17 for c in (1, 2, 0)) for i in range(0, 48, 3)]
    # Original Kurumi entry sets color0 to96,0,0 at clock320; the
    # independent state CPU controls attest this before these phase2 frames.
    palette[0] = (102,0,0)
    checks = []
    for rank in ('normal', 'lunatic'):
        for character in ('reimu', 'marisa'):
            for shooting in ('shot', 'idle'):
                path = frames / f'{rank}-{character}-{shooting}-3.bmp'
                with Image.open(path) as image:
                    image = image.convert('RGB'); checked = 0
                    # At the first live spawnray checkpoint the lower eight
                    # picture side bands have no foreground actors. Decode original
                    # archive planes directly, including color-zero pixels.
                    for y in range(104, 112):
                        for x in itertools.chain(range(96),range(288,384)):
                            offset = (111-y)*48+x//8; mask = 0x80>>(x%8)
                            color = sum(1<<p for p in range(4) if body[16+p*5376+offset]&mask)
                            if image.getpixel((32+x,96+y)) != palette[color]:
                                raise ValueError(f'Kurumi opaque backdrop differs: {path.name} {x},{y}')
                            checked += 1
                    # Original TDW footprint extends to physical row399,
                    # beyond the ordinary playfield bottom383.
                    for y in itertools.chain(range(16,32) if shooting=='idle' else (),range(384,400)):
                        for x in range(32,416):
                            if image.getpixel((x,y)) != palette[0]:
                                raise ValueError(f'Kurumi colorfill differs: {path.name} {x},{y}')
                            checked += 1
                    checks.append(dict(image=path.name, checked_pixels=checked,bmp_sha256=sha(path.read_bytes())))
    return dict(checks=checks,checked_pixels=sum(c['checked_pixels'] for c in checks),scope='Selected unobstructed opaque-CDG lower-row side bands and TDW color0 side bands in eight natural native battle checkpoints; independent archive decode, not original VRAM.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--hdi', type=Path, required=True)
    p.add_argument('--frames', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--kurumi-frames', type=Path)
    a = p.parse_args()
    manifest, _ = source_manifest(Path(__file__).resolve().parents[1])
    receipt = verify(a.hdi, a.frames, a.target)
    if a.kurumi_frames:
        receipt['battle_backdrop'] = verify_battle_backdrop(a.hdi, a.kurumi_frames)
    after, _ = source_manifest(Path(__file__).resolve().parents[1])
    if manifest != after:
        raise ValueError('source changed during resource verification')
    receipt.update(source_manifest_sha256=manifest, observed_utc=datetime.now(timezone.utc).isoformat())
    receipt.update(unicorn_version=unicorn.__version__,
                   unicorn_engine_sha256=sha(Path(unicorn.unicorn._uc._name).read_bytes()))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print('Stage2 resource requests and 57,188 native portrait pixels: PASS')
    if a.kurumi_frames:
        print(f"Kurumi selected backdrop/colorfill pixels: {receipt['battle_backdrop']['checked_pixels']} PASS")


if __name__ == '__main__':
    main()
